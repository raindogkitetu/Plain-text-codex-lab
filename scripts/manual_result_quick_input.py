#!/usr/bin/env python3
"""Build a quick manual result input template for Villain posts.

Report-only. This script reads manual_post_results.json and writes a Markdown
template. It does not mutate JSON DBs, post to X, call X API write endpoints,
upload media, create tweets, or read .env.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = ROOT / "data" / "manual_post_results.json"
REPORT_PATH = ROOT / "reports" / "villain_quick_result_input.md"
JST = ZoneInfo("Asia/Tokyo")
BASELINE_IMPRESSIONS = 60


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def is_posted(item: dict[str, Any]) -> bool:
    return bool(item.get("post_url") or item.get("post_datetime_jst"))


def hours_since_post(item: dict[str, Any], now: datetime) -> float | None:
    posted_at = parse_datetime(item.get("post_datetime_jst", ""))
    if posted_at is None:
        return None
    if posted_at.tzinfo is None:
        posted_at = posted_at.replace(tzinfo=JST)
    return (now - posted_at.astimezone(JST)).total_seconds() / 3600


def metric_status(item: dict[str, Any], now: datetime) -> str:
    elapsed = hours_since_post(item, now)
    if elapsed is not None and elapsed < 24:
        return "wait_for_24h_metrics"
    impressions = item.get("impressions")
    if not isinstance(impressions, int):
        return "manual_metrics_pending"
    if impressions < BASELINE_IMPRESSIONS:
        return "weak"
    if impressions < 100:
        return "normal"
    return "strong"


def baseline_comparison(item: dict[str, Any]) -> str:
    impressions = item.get("impressions")
    if not isinstance(impressions, int):
        return "pending_vs_baseline_60"
    delta = impressions - BASELINE_IMPRESSIONS
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta}_vs_baseline_60"


def value_or_blank(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def write_report(results_db: dict[str, Any]) -> None:
    now = datetime.now(JST)
    posted_items = [item for item in results_db.get("manual_post_results", []) if is_posted(item)]

    lines = [
        "# Villain Quick Result Input",
        "",
        f"- Generated at JST: `{now.isoformat()}`",
        "- status: `REPORT_ONLY`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        "- DB mutation: `NOT_EXECUTED`",
        f"- baseline_impressions: `{BASELINE_IMPRESSIONS}`",
        f"- posted_slot_count: `{len(posted_items)}`",
        "",
    ]

    if not posted_items:
        lines.extend(
            [
                "## Status",
                "",
                "- result_status: `waiting_for_manual_posts`",
                "- next_action: `手動投稿後に post_url / post_datetime_jst / metrics を記録する`",
                "",
            ]
        )

    for item in posted_items:
        future = item.get("future_learning", {})
        elapsed = hours_since_post(item, now)
        elapsed_label = "unknown" if elapsed is None else f"{elapsed:.1f}h"
        lines.extend(
            [
                f"## Slot {item.get('slot')}",
                "",
                f"- candidate_id: `{item.get('candidate_id', '')}`",
                f"- post_url: `{item.get('post_url', '')}`",
                f"- post_datetime_jst: `{item.get('post_datetime_jst', '')}`",
                f"- hours_since_post: `{elapsed_label}`",
                f"- baseline_comparison: `{baseline_comparison(item)}`",
                f"- result_status: `{metric_status(item, now)}`",
                "",
                "### 30 Second Input Template",
                "",
                "```text",
                f"candidate_id: {item.get('candidate_id', '')}",
                f"post_url: {item.get('post_url', '')}",
                f"post_datetime_jst: {item.get('post_datetime_jst', '')}",
                f"impressions: {value_or_blank(item.get('impressions'))}",
                f"likes: {value_or_blank(item.get('likes'))}",
                f"reposts: {value_or_blank(item.get('reposts'))}",
                f"replies: {value_or_blank(item.get('replies'))}",
                f"bookmarks: {value_or_blank(item.get('bookmarks'))}",
                f"profile_visits: {value_or_blank(item.get('profile_visits'))}",
                f"follows: {value_or_blank(item.get('follows'))}",
                f"manual_notes: {item.get('manual_notes', '')}",
                f"persona_fit: {future.get('persona_fit', 'unreviewed')}",
                "```",
                "",
                "### Quick Judgment",
                "",
                "- weak: impressions < 60",
                "- normal: 60 <= impressions < 100",
                "- strong: impressions >= 100",
                "- 24h未満なら `wait_for_24h_metrics` を優先",
                "",
            ]
        )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    results_db = read_json(RESULTS_PATH)
    write_report(results_db)
    print("live_posting=NOT_EXECUTED")
    print("x_api_write=NOT_USED")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
