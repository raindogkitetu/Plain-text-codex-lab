#!/usr/bin/env python3
"""Recommend Villain posting windows without posting or mutating DBs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
HISTORY_PATH = ROOT / "data" / "villain_post_history.json"
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
CANDIDATES_PATH = ROOT / "data" / "villain_generated_candidates.json"
REPORT_PATH = ROOT / "reports" / "villain_post_time_optimizer.md"
JST = ZoneInfo("Asia/Tokyo")

WEEKDAY_WINDOWS = [
    "07:00-08:30",
    "12:00-13:00",
    "19:00-22:30",
    "23:00-23:59",
]
WEEKEND_WINDOWS = [
    "09:00-11:00",
    "19:00-23:00",
    "23:00-23:59",
]
TYPE_BIAS = {
    "COMMUNITY_INFO": ["23:00-23:59", "19:00-22:30", "19:00-23:00"],
    "POSTER_SUMMARY": ["23:00-23:59", "19:00-22:30", "19:00-23:00"],
    "CULTURE_OBSERVER": ["23:00-23:59", "19:00-22:30", "19:00-23:00"],
    "ABOUT_WORDING": ["19:00-22:30", "19:00-23:00"],
    "IMAGE_POST": ["19:00-22:30", "19:00-23:00", "09:00-11:00"],
    "ANNOUNCEMENT": ["12:00-13:00", "19:00-22:30", "19:00-23:00"],
}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def now_jst() -> datetime:
    return datetime.now(timezone.utc).astimezone(JST)


def windows_for_day(is_weekend: bool) -> list[str]:
    return WEEKEND_WINDOWS if is_weekend else WEEKDAY_WINDOWS


def recommend_windows(post_type: str, is_weekend: bool) -> tuple[list[str], str]:
    base = windows_for_day(is_weekend)
    bias = TYPE_BIAS.get(post_type, [])
    prioritized = [window for window in bias if window in base]
    remaining = [window for window in base if window not in prioritized]
    recommendation = prioritized + remaining
    if post_type in TYPE_BIAS:
        reason = f"{post_type} は {', '.join(prioritized or base)} を優先。"
    else:
        reason = "固定時間帯ルールをそのまま適用。"
    return recommendation, reason


def queue_items(queue_db: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "source": "queue",
            "item_id": item.get("queue_id", ""),
            "post_type": item.get("post_type", "UNKNOWN"),
            "status": item.get("status", ""),
            "role": item.get("candidate_role", ""),
        }
        for item in queue_db.get("queue", [])
    ]


def candidate_items(candidate_db: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "source": "candidate",
            "item_id": candidate.get("candidate_id", ""),
            "post_type": candidate.get("category", "UNKNOWN"),
            "status": candidate.get("status", "generated"),
            "role": "generated_candidate",
        }
        for candidate in candidate_db.get("candidates", [])
    ]


def history_summary(history_db: dict[str, Any]) -> dict[str, Any]:
    history = history_db.get("history", [])
    return {
        "history_count": len(history),
        "learning_mode": "fixed_rules_only" if not history else "history_aware_future_ready",
    }


def build_rows(items: list[dict[str, Any]], is_weekend: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        windows, reason = recommend_windows(item["post_type"], is_weekend)
        rows.append(
            {
                **item,
                "recommended_windows_jst": windows,
                "primary_window_jst": windows[0] if windows else "",
                "recommendation_reason": reason,
            }
        )
    return rows


def write_report(rows: list[dict[str, Any]], history: dict[str, Any], current_jst: datetime) -> None:
    day_kind = "weekend" if current_jst.weekday() >= 5 else "weekday"
    lines = [
        "# Villain Post Time Optimizer",
        "",
        f"- Generated at JST: `{current_jst.isoformat()}`",
        "- status: `DRY_RUN_ONLY`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        "- DB mutation: `NOT_EXECUTED`",
        f"- day_kind: `{day_kind}`",
        f"- history_count: `{history.get('history_count')}`",
        f"- learning_mode: `{history.get('learning_mode')}`",
        "- live_x_learning: `23:00 community/culture priority from 2026-05-15 GET-only analysis`",
        "",
        "## Base Windows JST",
        "",
        f"- weekday: `{', '.join(WEEKDAY_WINDOWS)}`",
        f"- weekend: `{', '.join(WEEKEND_WINDOWS)}`",
        "",
        "## Recommended Items",
        "",
    ]
    if not rows:
        lines.append("- none")
    for row in rows:
        lines.extend(
            [
                f"### `{row.get('item_id')}`",
                "",
                f"- source: `{row.get('source')}`",
                f"- post_type: `{row.get('post_type')}`",
                f"- status: `{row.get('status')}`",
                f"- role: `{row.get('role')}`",
                f"- primary_window_jst: `{row.get('primary_window_jst')}`",
                f"- recommended_windows_jst: `{', '.join(row.get('recommended_windows_jst', []))}`",
                f"- recommendation_reason: {row.get('recommendation_reason')}",
                "",
            ]
        )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    history_db = read_json(HISTORY_PATH)
    queue_db = read_json(QUEUE_PATH)
    candidate_db = read_json(CANDIDATES_PATH)
    current = now_jst()
    is_weekend = current.weekday() >= 5
    rows = build_rows(queue_items(queue_db) + candidate_items(candidate_db), is_weekend)
    write_report(rows, history_summary(history_db), current)
    print("status=DRY_RUN_ONLY")
    print("db_mutation=NOT_EXECUTED")
    print(f"recommendations={len(rows)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
