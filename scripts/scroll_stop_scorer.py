#!/usr/bin/env python3
"""Score Villain posts for timeline scroll-stop power.

Report-only. This script reads candidates, queue, and manual result learning,
then writes a Markdown analysis. It does not mutate JSON DBs, post to X, call X
API write endpoints, upload media, create tweets, or read .env.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_PATH = ROOT / "data" / "villain_generated_candidates.json"
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
RESULTS_PATH = ROOT / "data" / "manual_post_results.json"
REPORT_PATH = ROOT / "reports" / "villain_scroll_stop_analysis.md"

WEAK_PATTERN_PENALTIES = {
    "poetic_tone_too_soft": 10,
    "low_scroll_stop_power": 15,
    "villainness_too_low": 12,
}

GENERIC_WORDS = ("今日はそれでいい", "残ってる", "ちょっと", "感じ")
VILLAIN_WORDS = ("Villain", "villain", "$villain", "着て稼ぐ", "普通じゃない", "強い", "毎日着ろ")
TENSION_WORDS = ("でも", "普通", "言わない", "じゃない", "なのに", "違和感", "強い")
EMOTIONAL_WORDS = ("強い", "痛い", "残る", "戻る", "黙って", "普通じゃない", "毎日着ろ")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def text_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def first_line_score(text: str) -> tuple[int, str]:
    lines = text_lines(text)
    if not lines:
        return 0, "冒頭行が空。"
    first = lines[0]
    score = 8
    if len(first) <= 18:
        score += 4
    if any(word in first for word in ("ABOUT", "強い", "服", "誰か", "毎日", "普通")):
        score += 4
    if first.endswith(("。", "？", "?", "。")):
        score += 2
    return min(score, 16), f"first_line=`{first}`"


def component_score(text: str, image_hint: str, weak_patterns: list[str]) -> dict[str, dict[str, Any]]:
    lines = text_lines(text)
    body_len = len(text.replace("\n", ""))
    hook, hook_reason = first_line_score(text)
    emotional = 12 if any(word in text for word in EMOTIONAL_WORDS) else 5
    tension = 12 if any(word in text for word in TENSION_WORDS) else 4
    curiosity = 10 if len(lines) >= 4 and any(word in text for word in ("でも", "普通", "なぜ", "言わない")) else 5
    shortness = 12 if body_len <= 130 else 8 if body_len <= 180 else 4
    visual = 10 if image_hint else 5
    villainness = 14 if any(word in text for word in VILLAIN_WORDS) else 5
    memorability = 12 if any(word in text for word in ("毎日着ろ", "普通そんなこと言わない", "Villainなら")) else 6

    if "villainness_too_low" in weak_patterns:
        villainness = max(0, villainness - 6)
    if "poetic_tone_too_soft" in weak_patterns:
        emotional = max(0, emotional - 4)
        memorability = max(0, memorability - 3)
    if "low_scroll_stop_power" in weak_patterns:
        hook = max(0, hook - 5)
        curiosity = max(0, curiosity - 4)

    return {
        "first_line_hook": {"score": hook, "reason": hook_reason},
        "emotional_trigger": {"score": emotional, "reason": "感情語/違和感語の有無。"},
        "contradiction_or_tension": {"score": tension, "reason": "普通さとのズレ、否定、反転の有無。"},
        "curiosity_gap": {"score": curiosity, "reason": "続きを読ませる余白の有無。"},
        "shortness": {"score": shortness, "reason": f"text_length={body_len}"},
        "visual_match": {"score": visual, "reason": "image_hint または画像投稿文脈の有無。"},
        "villainness": {"score": villainness, "reason": "Villain固有語と強さの有無。"},
        "memorability": {"score": memorability, "reason": "一言で残る文の有無。"},
    }


def penalty_score(text: str, weak_patterns: list[str]) -> tuple[int, list[str]]:
    penalties: list[tuple[str, int]] = []
    for pattern in weak_patterns:
        if pattern in WEAK_PATTERN_PENALTIES:
            penalties.append((pattern, WEAK_PATTERN_PENALTIES[pattern]))
    if any(word in text for word in GENERIC_WORDS):
        penalties.append(("generic_message", 5))
    if len(text.replace("\n", "")) > 180:
        penalties.append(("explanation_too_long", 8))
    if not any(word in text for word in ("普通", "でも", "強い", "毎日着ろ", "Villain")):
        penalties.append(("scroll_past_risk", 7))
    return sum(value for _, value in penalties), [name for name, _ in penalties]


def manual_learning_by_candidate(results_db: dict[str, Any]) -> dict[str, dict[str, Any]]:
    learning: dict[str, dict[str, Any]] = {}
    for item in results_db.get("manual_post_results", []):
        candidate_id = item.get("candidate_id")
        if not candidate_id:
            continue
        future = item.get("future_learning", {})
        weak = future.get("weak_pattern", [])
        if isinstance(weak, str):
            weak_patterns = [weak] if weak else []
        else:
            weak_patterns = [str(value) for value in weak]
        learning[candidate_id] = {
            "weak_patterns": weak_patterns,
            "persona_fit": future.get("persona_fit", "unreviewed"),
            "manual_notes": item.get("manual_notes", ""),
            "post_url": item.get("post_url", ""),
        }
    return learning


def collect_posts(
    candidates_db: dict[str, Any], queue_db: dict[str, Any], results_db: dict[str, Any]
) -> list[dict[str, Any]]:
    learning = manual_learning_by_candidate(results_db)
    posts: list[dict[str, Any]] = []
    seen: set[str] = set()

    for item in candidates_db.get("candidates", []):
        candidate_id = item.get("candidate_id", "")
        if not candidate_id:
            continue
        seen.add(candidate_id)
        posts.append(
            {
                "source": "generated_candidates",
                "candidate_id": candidate_id,
                "queue_id": "",
                "post_type": item.get("category", ""),
                "text": item.get("text", ""),
                "image_hint": item.get("image_hint", ""),
                "quality_score": item.get("quality_prediction"),
                "risk": item.get("risk_prediction", "unknown"),
                "learning": learning.get(candidate_id, {}),
            }
        )

    for item in queue_db.get("queue", []):
        candidate_id = item.get("candidate_id") or item.get("queue_id", "")
        queue_id = item.get("queue_id", "")
        post_key = candidate_id or queue_id
        if post_key in seen:
            continue
        seen.add(post_key)
        posts.append(
            {
                "source": "post_queue",
                "candidate_id": candidate_id,
                "queue_id": queue_id,
                "post_type": item.get("post_type", ""),
                "text": item.get("text", ""),
                "image_hint": item.get("image", {}).get("poster_concept", ""),
                "quality_score": item.get("scoring", {}).get("score"),
                "risk": item.get("scoring", {}).get("risk_level", "unknown"),
                "learning": learning.get(candidate_id, {}),
            }
        )

    return posts


def score_post(post: dict[str, Any]) -> dict[str, Any]:
    weak_patterns = post.get("learning", {}).get("weak_patterns", [])
    components = component_score(post.get("text", ""), post.get("image_hint", ""), weak_patterns)
    base_score = sum(part["score"] for part in components.values())
    penalty, penalty_reasons = penalty_score(post.get("text", ""), weak_patterns)
    final_score = max(0, min(100, base_score - penalty))
    return {
        **post,
        "scroll_stop_score": final_score,
        "components": components,
        "penalty": penalty,
        "penalty_reasons": penalty_reasons,
        "recommended_improvement": recommended_improvement(final_score, penalty_reasons, components),
    }


def recommended_improvement(score: int, penalties: list[str], components: dict[str, dict[str, Any]]) -> str:
    if "poetic_tone_too_soft" in penalties:
        return "詩的な余韻より、最初の一行に少し硬い違和感を置く。"
    if "low_scroll_stop_power" in penalties:
        return "冒頭をさらに短くして、普通ではない言葉を先頭に出す。"
    if "villainness_too_low" in penalties:
        return "Villain固有の強さを一語だけ足す。説明は増やさない。"
    weakest_component = min(components.items(), key=lambda item: item[1]["score"])[0]
    if score >= 80:
        return "この方向で可。重くしすぎず、冒頭だけ少し尖らせる余地あり。"
    return f"{weakest_component} を補強。意味の説明ではなく、止まる言葉を増やす。"


def write_report(scored_posts: list[dict[str, Any]]) -> None:
    ranked = sorted(scored_posts, key=lambda item: item["scroll_stop_score"], reverse=True)
    strongest = ranked[0] if ranked else None
    weakest = ranked[-1] if ranked else None

    lines = [
        "# Villain Scroll Stop Analysis",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "- status: `REPORT_ONLY`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        "- DB mutation: `NOT_EXECUTED`",
        "- learning_source: `data/manual_post_results.json`",
        "",
        "## Summary",
        "",
        f"- strongest_scroll_stop_post: `{strongest.get('candidate_id') if strongest else None}`",
        f"- weakest_scroll_stop_post: `{weakest.get('candidate_id') if weakest else None}`",
        f"- recommended_improvement: `{weakest.get('recommended_improvement') if weakest else 'waiting_for_candidates'}`",
        "",
        "## Score Per Candidate",
        "",
    ]

    for item in ranked:
        lines.extend(
            [
                f"### {item.get('candidate_id') or item.get('queue_id')}",
                "",
                f"- source: `{item.get('source')}`",
                f"- post_type: `{item.get('post_type')}`",
                f"- scroll_stop_score: `{item.get('scroll_stop_score')}`",
                f"- quality_score: `{item.get('quality_score')}`",
                f"- risk: `{item.get('risk')}`",
                f"- penalty: `{item.get('penalty')}`",
                f"- penalty_reasons: `{', '.join(item.get('penalty_reasons') or []) or 'none'}`",
                f"- recommended_improvement: `{item.get('recommended_improvement')}`",
                "",
                "```text",
                item.get("text", ""),
                "```",
                "",
                "#### Components",
                "",
            ]
        )
        for name, component in item.get("components", {}).items():
            lines.append(f"- {name}: `{component.get('score')}` - {component.get('reason')}")
        lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    candidates_db = read_json(CANDIDATES_PATH)
    queue_db = read_json(QUEUE_PATH)
    results_db = read_json(RESULTS_PATH)
    posts = collect_posts(candidates_db, queue_db, results_db)
    scored_posts = [score_post(post) for post in posts if post.get("text")]
    write_report(scored_posts)
    print(f"scored_posts={len(scored_posts)}")
    print("live_posting=NOT_EXECUTED")
    print("x_api_write=NOT_USED")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
