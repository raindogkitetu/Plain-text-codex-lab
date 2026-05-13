#!/usr/bin/env python3
"""Score Villain image types for scroll-stop fit.

Report-only. This script reads manual results, manual post pack, candidates,
and queue data, then writes a Markdown analysis. It does not mutate JSON DBs,
post to X, call X API write endpoints, upload media, create tweets, or read
.env.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = ROOT / "data" / "manual_post_results.json"
CANDIDATES_PATH = ROOT / "data" / "villain_generated_candidates.json"
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
PACK_PATH = ROOT / "reports" / "villain_manual_post_pack.md"
REPORT_PATH = ROOT / "reports" / "villain_image_type_analysis.md"

IMAGE_TYPES = (
    "poster_summary",
    "quote_visual",
    "apparel_focus",
    "character_visual",
    "community_info",
    "meme",
    "unknown",
)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def parse_manual_pack(markdown: str) -> dict[str, dict[str, str]]:
    pack: dict[str, dict[str, str]] = {}
    sections = re.split(r"\n## Post\s+\d+\n", markdown)
    for section in sections[1:]:
        candidate = re.search(r"- candidate_id: `([^`]+)`", section)
        if not candidate:
            continue
        candidate_id = candidate.group(1)
        image_status = re.search(r"- image_status: `([^`]+)`", section)
        recommended_time = re.search(r"- recommended_time_window: `([^`]+)`", section)
        final_text = re.search(r"### final_text\n\n```text\n(.*?)\n```", section, re.DOTALL)
        pack[candidate_id] = {
            "image_status": image_status.group(1) if image_status else "unknown",
            "recommended_time_window": recommended_time.group(1) if recommended_time else "unknown",
            "final_text": final_text.group(1) if final_text else "",
        }
    return pack


def classify_image_type(image_hint: str, text: str, post_type: str) -> str:
    source = f"{image_hint}\n{text}\n{post_type}".lower()
    if "poster_mode" in source or "ポスター" in source or "中央" in source:
        return "poster_summary"
    if "quote" in source or "言葉" in source or "about" in source or "コピー" in source:
        return "quote_visual"
    if "apparel" in source or "服" in source or "質感" in source or "store" in source:
        return "apparel_focus"
    if "observer_mode" in source or "street_mode" in source or "フード" in source or "人物" in source:
        return "character_visual"
    if "community" in source or "コミュニティ" in source or "仕組み" in source or "pool" in source:
        return "community_info"
    if "meme" in source or "ネタ" in source:
        return "meme"
    return "unknown"


def learning_by_candidate(results_db: dict[str, Any]) -> dict[str, dict[str, Any]]:
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
            "image_used": bool(item.get("image_used")),
            "post_url": item.get("post_url", ""),
            "manual_notes": item.get("manual_notes", ""),
            "weak_patterns": weak_patterns,
            "persona_fit": future.get("persona_fit", "unreviewed"),
        }
    return learning


def collect_candidates(
    candidates_db: dict[str, Any],
    queue_db: dict[str, Any],
    pack: dict[str, dict[str, str]],
    learning: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()

    for item in candidates_db.get("candidates", []):
        candidate_id = item.get("candidate_id", "")
        if not candidate_id:
            continue
        seen.add(candidate_id)
        pack_item = pack.get(candidate_id, {})
        text = pack_item.get("final_text") or item.get("text", "")
        image_hint = item.get("image_hint", "")
        post_type = item.get("category", "")
        items.append(
            {
                "source": "generated_candidates",
                "candidate_id": candidate_id,
                "queue_id": "",
                "post_type": post_type,
                "text": text,
                "image_hint": image_hint,
                "image_status": pack_item.get("image_status", "image_required_human_check"),
                "recommended_time_window": pack_item.get("recommended_time_window", "unknown"),
                "quality_score": item.get("quality_prediction"),
                "risk": item.get("risk_prediction", "unknown"),
                "learning": learning.get(candidate_id, {}),
            }
        )

    for item in queue_db.get("queue", []):
        queue_id = item.get("queue_id", "")
        if queue_id in seen:
            continue
        image = item.get("image", {})
        text = item.get("text", "")
        image_hint = image.get("poster_concept", "")
        post_type = item.get("post_type", "")
        items.append(
            {
                "source": "post_queue",
                "candidate_id": item.get("candidate_id", ""),
                "queue_id": queue_id,
                "post_type": post_type,
                "text": text,
                "image_hint": image_hint,
                "image_status": image.get("status", "image_required_human_check"),
                "recommended_time_window": "unknown",
                "quality_score": item.get("scoring", {}).get("score"),
                "risk": item.get("scoring", {}).get("risk_level", "unknown"),
                "learning": learning.get(item.get("candidate_id", ""), {}),
            }
        )

    return items


def score_axis(image_type: str, text: str, image_hint: str, weak_patterns: list[str]) -> dict[str, dict[str, Any]]:
    text_len = len(text.replace("\n", ""))
    has_image_hint = bool(image_hint)
    has_brand = any(word in f"{text}\n{image_hint}" for word in ("Villain", "villain", "$villain", "着て稼ぐ"))
    has_text_match = any(word in image_hint for word in ("着て稼ぐ", "$villain", "ABOUT", "服", "ポスター"))

    axes = {
        "scroll_stop_power": 12,
        "readability_on_timeline": 12 if text_len <= 130 else 8,
        "poster_strength": 8,
        "visual_clarity": 10 if has_image_hint else 5,
        "brand_fit": 12 if has_brand else 6,
        "text_image_match": 12 if has_text_match else 6,
        "saveability": 10,
    }

    if image_type == "poster_summary":
        axes["scroll_stop_power"] += 8
        axes["poster_strength"] += 12
        axes["saveability"] += 6
    elif image_type == "quote_visual":
        axes["readability_on_timeline"] += 5
        axes["text_image_match"] += 5
    elif image_type == "apparel_focus":
        axes["brand_fit"] += 4
        axes["visual_clarity"] += 4
    elif image_type == "character_visual":
        axes["scroll_stop_power"] += 4
        axes["brand_fit"] += 2
    elif image_type == "community_info":
        axes["saveability"] += 8
        axes["readability_on_timeline"] -= 4
    elif image_type == "meme":
        axes["scroll_stop_power"] += 6
        axes["brand_fit"] -= 3

    if "poetic_tone_too_soft" in weak_patterns:
        axes["scroll_stop_power"] -= 8
        axes["text_image_match"] -= 4
    if "low_scroll_stop_power" in weak_patterns:
        axes["scroll_stop_power"] -= 10
        axes["poster_strength"] -= 3
    if "villainness_too_low" in weak_patterns:
        axes["brand_fit"] -= 8
        axes["saveability"] -= 4

    return {
        name: {
            "score": max(0, min(20, score)),
            "reason": axis_reason(name, image_type, has_image_hint, has_brand, has_text_match),
        }
        for name, score in axes.items()
    }


def axis_reason(name: str, image_type: str, has_image_hint: bool, has_brand: bool, has_text_match: bool) -> str:
    if name == "poster_strength":
        return "poster_summary は初期仮説として強めに評価。"
    if name == "visual_clarity":
        return "image_hint があるか、人間が画像を確認できる状態か。"
    if name == "brand_fit":
        return f"brand_term_detected={has_brand}"
    if name == "text_image_match":
        return f"image_hint_matches_text={has_text_match}"
    return f"image_type={image_type}"


def score_candidate(item: dict[str, Any]) -> dict[str, Any]:
    learning = item.get("learning", {})
    weak_patterns = learning.get("weak_patterns", [])
    image_type = classify_image_type(item.get("image_hint", ""), item.get("text", ""), item.get("post_type", ""))
    axes = score_axis(image_type, item.get("text", ""), item.get("image_hint", ""), weak_patterns)
    score = min(100, sum(axis["score"] for axis in axes.values()))
    human_check_required = item.get("image_status") in {
        "",
        "image_required_human_check",
        "waiting_for_image",
        "unchecked",
    }
    return {
        **item,
        "image_type": image_type,
        "image_stop_score": score,
        "axes": axes,
        "image_required_human_check": human_check_required,
        "recommendation": recommendation(image_type, score, weak_patterns, human_check_required, item.get("risk")),
    }


def recommendation(image_type: str, score: int, weak_patterns: list[str], human_check: bool, risk: str) -> str:
    if risk == "high":
        return "画像相性は高くても、risk=high のため通常投稿テストからは外す。"
    if "poetic_tone_too_soft" in weak_patterns:
        return "画像は強めのポスター寄りで補強。本文の柔らかさを画で止める。"
    if image_type == "poster_summary" and score >= 85:
        return "次テスト優先。ポスター系の強さ仮説を検証する。"
    if human_check:
        return "画像権利と見え方を人間確認してから判断。"
    return "候補として保持。本文との一致をさらに見る。"


def best_type_hypothesis(scored: list[dict[str, Any]]) -> str:
    if not scored:
        return "waiting_for_candidates"
    averages: dict[str, list[int]] = {image_type: [] for image_type in IMAGE_TYPES}
    for item in scored:
        averages.setdefault(item["image_type"], []).append(item["image_stop_score"])
    ranked = sorted(
        ((image_type, sum(scores) / len(scores)) for image_type, scores in averages.items() if scores),
        key=lambda pair: pair[1],
        reverse=True,
    )
    if not ranked:
        return "waiting_for_candidates"
    return f"{ranked[0][0]} ({ranked[0][1]:.1f})"


def write_report(scored: list[dict[str, Any]]) -> None:
    ranked = sorted(scored, key=lambda item: item["image_stop_score"], reverse=True)
    best = best_type_hypothesis(ranked)
    next_test = next((item for item in ranked if item["image_type"] == "poster_summary"), ranked[0] if ranked else None)

    lines = [
        "# Villain Image Type Analysis",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "- status: `REPORT_ONLY`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        "- DB mutation: `NOT_EXECUTED`",
        "- image_required_human_check: `REQUIRED`",
        "",
        "## Summary",
        "",
        f"- best_image_type_hypothesis: `{best}`",
        "- image_type_recommendations: `poster_summary を優先テスト。quote_visual / apparel_focus は本文が強い時だけ採用。`",
        f"- next_test_recommendation: `{next_test.get('candidate_id') or next_test.get('queue_id') if next_test else 'waiting_for_candidates'}`",
        "",
        "## Candidate Image Fit",
        "",
    ]

    for item in ranked:
        identifier = item.get("candidate_id") or item.get("queue_id")
        lines.extend(
            [
                f"### {identifier}",
                "",
                f"- source: `{item.get('source')}`",
                f"- post_type: `{item.get('post_type')}`",
                f"- image_type: `{item.get('image_type')}`",
                f"- image_stop_score: `{item.get('image_stop_score')}`",
                f"- image_status: `{item.get('image_status')}`",
                f"- image_required_human_check: `{item.get('image_required_human_check')}`",
                f"- recommended_time_window: `{item.get('recommended_time_window')}`",
                f"- quality_score: `{item.get('quality_score')}`",
                f"- risk: `{item.get('risk')}`",
                f"- recommendation: `{item.get('recommendation')}`",
                "",
                "#### image_hint",
                "",
                "```text",
                item.get("image_hint", ""),
                "```",
                "",
                "#### text",
                "",
                "```text",
                item.get("text", ""),
                "```",
                "",
                "#### axes",
                "",
            ]
        )
        for axis, value in item.get("axes", {}).items():
            lines.append(f"- {axis}: `{value.get('score')}` - {value.get('reason')}")
        lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    results_db = read_json(RESULTS_PATH)
    candidates_db = read_json(CANDIDATES_PATH)
    queue_db = read_json(QUEUE_PATH)
    pack = parse_manual_pack(read_text(PACK_PATH))
    learning = learning_by_candidate(results_db)
    candidates = collect_candidates(candidates_db, queue_db, pack, learning)
    scored = [score_candidate(item) for item in candidates if item.get("text")]
    write_report(scored)
    print(f"scored_candidates={len(scored)}")
    print("live_posting=NOT_EXECUTED")
    print("x_api_write=NOT_USED")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
