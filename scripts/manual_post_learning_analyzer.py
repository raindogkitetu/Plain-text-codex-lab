#!/usr/bin/env python3
"""Analyze manual Villain post results when data is available.

Report-only. This script does not mutate JSON DBs, post to X, call X API write
endpoints, upload media, create tweets, or read .env.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = ROOT / "data" / "manual_post_results.json"
REPORT_PATH = ROOT / "reports" / "villain_learning_analysis.md"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def has_post_result(item: dict[str, Any]) -> bool:
    return bool(item.get("post_datetime_jst"))


def engagement_score(item: dict[str, Any]) -> int:
    total = 0
    for key, weight in {
        "likes": 1,
        "reposts": 3,
        "replies": 2,
        "bookmarks": 3,
        "profile_visits": 1,
        "follows": 5,
    }.items():
        value = item.get(key)
        if isinstance(value, int):
            total += value * weight
    return total


def time_window(value: str) -> str:
    if not value or "T" not in value:
        return "unknown"
    try:
        hour = int(value.split("T", 1)[1].split(":", 1)[0])
    except (ValueError, IndexError):
        return "unknown"
    if 7 <= hour < 9:
        return "07:00-08:30"
    if 12 <= hour < 13:
        return "12:00-13:00"
    if 19 <= hour < 23:
        return "19:00-22:30"
    return "other"


def analyze(results: list[dict[str, Any]]) -> dict[str, Any]:
    posted = [item for item in results if has_post_result(item)]
    if not posted:
        return {
            "analysis_status": "waiting_for_manual_posts",
            "strongest_post": None,
            "weakest_post": None,
            "best_time_window": None,
            "best_post_type": None,
            "persona_fit_summary": "waiting_for_manual_posts",
            "good_pattern": [],
            "weak_pattern": [],
        }

    ranked = sorted(posted, key=engagement_score, reverse=True)
    time_counts = Counter(time_window(item.get("post_datetime_jst", "")) for item in posted)
    persona_counts = Counter(item.get("future_learning", {}).get("persona_fit", "unreviewed") for item in posted)
    good_patterns = [
        item.get("future_learning", {}).get("good_pattern", "")
        for item in posted
        if item.get("future_learning", {}).get("good_pattern")
    ]
    weak_patterns = [
        item.get("future_learning", {}).get("weak_pattern", "")
        for item in posted
        if item.get("future_learning", {}).get("weak_pattern")
    ]
    return {
        "analysis_status": "ready",
        "strongest_post": ranked[0].get("candidate_id"),
        "weakest_post": ranked[-1].get("candidate_id"),
        "best_time_window": time_counts.most_common(1)[0][0] if time_counts else None,
        "best_post_type": "manual_type_pending",
        "persona_fit_summary": dict(persona_counts),
        "good_pattern": good_patterns,
        "weak_pattern": weak_patterns,
    }


def write_report(results_db: dict[str, Any], analysis: dict[str, Any]) -> None:
    lines = [
        "# Villain Learning Analysis",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "- status: `REPORT_ONLY`",
        "- live posting: `NOT_EXECUTED`",
        "- auto posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        "- DB mutation: `NOT_EXECUTED`",
        f"- analysis_status: `{analysis.get('analysis_status')}`",
        "",
        "## Summary",
        "",
        f"- strongest_post: `{analysis.get('strongest_post')}`",
        f"- weakest_post: `{analysis.get('weakest_post')}`",
        f"- best_time_window: `{analysis.get('best_time_window')}`",
        f"- best_post_type: `{analysis.get('best_post_type')}`",
        f"- persona_fit_summary: `{analysis.get('persona_fit_summary')}`",
        "",
        "## good_pattern",
        "",
    ]
    good_patterns = analysis.get("good_pattern") or []
    if not good_patterns:
        lines.append("- waiting_for_manual_posts")
    for item in good_patterns:
        lines.append(f"- {item}")
    lines.extend(["", "## weak_pattern", ""])
    weak_patterns = analysis.get("weak_pattern") or []
    if not weak_patterns:
        lines.append("- waiting_for_manual_posts")
    for item in weak_patterns:
        lines.append(f"- {item}")
    lines.extend(["", "## Slots", ""])
    for item in results_db.get("manual_post_results", []):
        lines.extend(
            [
                f"### Slot {item.get('slot')}",
                "",
                f"- candidate_id: `{item.get('candidate_id', '')}`",
                f"- posted: `{has_post_result(item)}`",
                f"- engagement_score: `{engagement_score(item)}`",
                f"- post_datetime_jst: `{item.get('post_datetime_jst', '') or 'pending'}`",
                "",
            ]
        )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    results_db = read_json(RESULTS_PATH)
    analysis = analyze(results_db.get("manual_post_results", []))
    write_report(results_db, analysis)
    print(f"analysis_status={analysis.get('analysis_status')}")
    print("live_posting=NOT_EXECUTED")
    print("x_api_write=NOT_USED")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
