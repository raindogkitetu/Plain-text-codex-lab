#!/usr/bin/env python3
"""Select the next single Villain manual test candidate.

Report-only. This script merges quality, persona, scroll-stop, image type,
risk, time-window, and manual posting history. It does not mutate JSON DBs,
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
MANUAL_SELECTION_PATH = ROOT / "reports" / "villain_manual_test_selection.md"
SCROLL_STOP_PATH = ROOT / "reports" / "villain_scroll_stop_analysis.md"
IMAGE_TYPE_PATH = ROOT / "reports" / "villain_image_type_analysis.md"
TIME_OPTIMIZER_PATH = ROOT / "reports" / "villain_post_time_optimizer.md"
RESULTS_PATH = ROOT / "data" / "manual_post_results.json"
REPORT_PATH = ROOT / "reports" / "villain_unified_test_selection.md"


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_manual_selection(markdown: str) -> dict[str, dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    sections = re.split(r"\n### `([^`]+)`\n", markdown)
    for index in range(1, len(sections), 2):
        candidate_id = sections[index]
        section = sections[index + 1]
        if "candidate_id:" not in section:
            continue
        text_match = re.search(r"```text\n(.*?)\n```", section, re.DOTALL)
        candidates[candidate_id] = {
            "candidate_id": candidate_id,
            "queue_id": field(section, "queue_id"),
            "post_type": field(section, "post_type"),
            "quality_score": number_field(section, "quality_score"),
            "persona_score": number_field(section, "persona_score"),
            "risk": field(section, "risk") or "unknown",
            "recommended_time_window": field(section, "recommended_time_window"),
            "suggested_final_text": text_match.group(1) if text_match else "",
        }
    return candidates


def parse_scroll_stop(markdown: str) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    sections = re.split(r"\n### ([^\n`]+)\n", markdown)
    for index in range(1, len(sections), 2):
        candidate_id = sections[index].strip()
        section = sections[index + 1]
        values[candidate_id] = {
            "scroll_stop_score": number_field(section, "scroll_stop_score"),
            "scroll_recommended_improvement": field(section, "recommended_improvement"),
        }
    return values


def parse_image_type(markdown: str) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    sections = re.split(r"\n### ([^\n`]+)\n", markdown)
    for index in range(1, len(sections), 2):
        candidate_id = sections[index].strip()
        section = sections[index + 1]
        values[candidate_id] = {
            "image_type": field(section, "image_type") or "unknown",
            "image_stop_score": number_field(section, "image_stop_score"),
            "image_status": field(section, "image_status") or "unknown",
            "image_recommendation": field(section, "recommendation"),
        }
    return values


def parse_time_optimizer(markdown: str) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    sections = re.split(r"\n### `([^`]+)`\n", markdown)
    for index in range(1, len(sections), 2):
        candidate_id = sections[index]
        section = sections[index + 1]
        values[candidate_id] = {
            "primary_window_jst": field(section, "primary_window_jst"),
            "recommended_windows_jst": field(section, "recommended_windows_jst"),
            "time_reason": bare_field(section, "recommendation_reason"),
        }
    return values


def field(section: str, name: str) -> str:
    match = re.search(rf"- {re.escape(name)}: `([^`]*)`", section)
    return match.group(1) if match else ""


def bare_field(section: str, name: str) -> str:
    match = re.search(rf"- {re.escape(name)}: (.+)", section)
    return match.group(1).strip() if match else ""


def number_field(section: str, name: str) -> int:
    value = field(section, name)
    try:
        return int(value)
    except ValueError:
        return 0


def posted_candidate_ids(results_db: dict[str, Any]) -> set[str]:
    posted: set[str] = set()
    for item in results_db.get("manual_post_results", []):
        if item.get("post_datetime_jst") or item.get("post_url"):
            candidate_id = item.get("candidate_id")
            if candidate_id:
                posted.add(candidate_id)
    return posted


def risk_safety_score(risk: str) -> int:
    if risk == "low":
        return 100
    if risk == "medium":
        return 70
    if risk == "high":
        return 0
    return 50


def clamp_score(value: float) -> int:
    return max(0, min(100, round(value)))


def combine_candidates(
    manual: dict[str, dict[str, Any]],
    scroll: dict[str, dict[str, Any]],
    image: dict[str, dict[str, Any]],
    time_data: dict[str, dict[str, Any]],
    posted: set[str],
) -> list[dict[str, Any]]:
    combined: list[dict[str, Any]] = []
    for candidate_id, item in manual.items():
        risk = item.get("risk", "unknown")
        is_posted = candidate_id in posted
        scroll_score = scroll.get(candidate_id, {}).get("scroll_stop_score", 0)
        image_score = image.get(candidate_id, {}).get("image_stop_score", 0)
        quality = item.get("quality_score", 0)
        persona = item.get("persona_score", 0)
        unified = clamp_score(
            quality * 0.20
            + persona * 0.20
            + scroll_score * 0.25
            + image_score * 0.25
            + risk_safety_score(risk) * 0.10
        )
        excluded_reasons: list[str] = []
        if is_posted:
            excluded_reasons.append("already_posted")
        if risk == "high":
            excluded_reasons.append("high_risk")
        combined.append(
            {
                **item,
                **scroll.get(candidate_id, {}),
                **image.get(candidate_id, {}),
                **time_data.get(candidate_id, {}),
                "already_posted": is_posted,
                "risk_safety_score": risk_safety_score(risk),
                "unified_test_score": unified,
                "excluded": bool(excluded_reasons),
                "excluded_reasons": excluded_reasons,
            }
        )
    return combined


def select_next(candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    eligible = [item for item in candidates if not item.get("excluded")]
    if not eligible:
        return None
    return sorted(eligible, key=lambda item: item["unified_test_score"], reverse=True)[0]


def reason_for_selection(item: dict[str, Any] | None) -> str:
    if not item:
        return "eligible_candidate_not_found"
    return (
        f"quality={item.get('quality_score')}, persona={item.get('persona_score')}, "
        f"scroll_stop={item.get('scroll_stop_score')}, image_stop={item.get('image_stop_score')}, "
        f"risk={item.get('risk')} を統合。poster_summary 仮説と未投稿条件を優先。"
    )


def checklist() -> list[str]:
    return [
        "本文に誤字がない",
        "金融助言に見えない",
        "誰か個人を攻撃していない",
        "画像権利と見え方を確認済み",
        "ポスター系画像が本文を食いすぎていない",
        "投稿先アカウントを確認済み",
    ]


def do_not_post_if() -> list[str]:
    return [
        "利益保証に見える",
        "特定個人/団体への攻撃に見える",
        "画像権利が不明",
        "本文より画像コピーの方が強すぎる",
        "文脈なしで炎上しそう",
    ]


def write_report(candidates: list[dict[str, Any]], selected: dict[str, Any] | None) -> None:
    lines = [
        "# Villain Unified Test Selection",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "- status: `REPORT_ONLY`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        "- DB mutation: `NOT_EXECUTED`",
        "- scoring_weights: `quality 20 / persona 20 / scroll_stop 25 / image_stop 25 / risk_safety 10`",
        "",
        "## Next Manual Test Post",
        "",
        f"- next_manual_test_post: `{selected.get('candidate_id') if selected else None}`",
        f"- unified_test_score: `{selected.get('unified_test_score') if selected else None}`",
        f"- reason: `{reason_for_selection(selected)}`",
        f"- recommended_image_type: `{selected.get('image_type') if selected else None}`",
        f"- recommended_time_window: `{selected.get('primary_window_jst') or selected.get('recommended_time_window') if selected else None}`",
        "",
        "### suggested_final_text",
        "",
        "```text",
        selected.get("suggested_final_text", "") if selected else "",
        "```",
        "",
        "### human_checklist",
        "",
    ]
    for item in checklist():
        lines.append(f"- [ ] {item}")
    lines.extend(["", "### do_not_post_if", ""])
    for item in do_not_post_if():
        lines.append(f"- {item}")
    lines.extend(["", "## Candidate Scores", ""])

    for item in sorted(candidates, key=lambda candidate: candidate["unified_test_score"], reverse=True):
        lines.extend(
            [
                f"### {item.get('candidate_id')}",
                "",
                f"- unified_test_score: `{item.get('unified_test_score')}`",
                f"- quality_score: `{item.get('quality_score')}`",
                f"- persona_score: `{item.get('persona_score')}`",
                f"- scroll_stop_score: `{item.get('scroll_stop_score')}`",
                f"- image_stop_score: `{item.get('image_stop_score')}`",
                f"- risk: `{item.get('risk')}`",
                f"- risk_safety_score: `{item.get('risk_safety_score')}`",
                f"- image_type: `{item.get('image_type')}`",
                f"- recommended_time_window: `{item.get('primary_window_jst') or item.get('recommended_time_window')}`",
                f"- already_posted: `{item.get('already_posted')}`",
                f"- excluded: `{item.get('excluded')}`",
                f"- excluded_reasons: `{', '.join(item.get('excluded_reasons') or []) or 'none'}`",
                "",
            ]
        )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    manual = parse_manual_selection(read_text(MANUAL_SELECTION_PATH))
    scroll = parse_scroll_stop(read_text(SCROLL_STOP_PATH))
    image = parse_image_type(read_text(IMAGE_TYPE_PATH))
    time_data = parse_time_optimizer(read_text(TIME_OPTIMIZER_PATH))
    posted = posted_candidate_ids(read_json(RESULTS_PATH))
    candidates = combine_candidates(manual, scroll, image, time_data, posted)
    selected = select_next(candidates)
    write_report(candidates, selected)
    print(f"candidate_count={len(candidates)}")
    print(f"next_manual_test_post={selected.get('candidate_id') if selected else None}")
    print("live_posting=NOT_EXECUTED")
    print("x_api_write=NOT_USED")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
