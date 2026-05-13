#!/usr/bin/env python3
"""Build a manual post test report from result templates.

This logger is intentionally read/report oriented for setup. It does not post,
call X API write endpoints, upload media, create tweets, or read .env.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = ROOT / "data" / "manual_post_results.json"
REPORT_PATH = ROOT / "reports" / "villain_manual_post_test.md"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def metric_value(value: Any) -> str:
    return "pending" if value is None or value == "" else str(value)


def write_report(results_db: dict[str, Any]) -> None:
    results = results_db.get("manual_post_results", [])
    lines = [
        "# Villain Manual Post Test",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "- status: `MANUAL_RESULT_LOGGING_ONLY`",
        "- live posting: `NOT_EXECUTED`",
        "- auto posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        f"- template_slots: `{len(results)}`",
        "",
        "## How To Use",
        "",
        "- 手動投稿後に post_datetime_jst と各数値を手入力する。",
        "- 数値が未確認なら null のまま残す。",
        "- good_pattern / weak_pattern / persona_fit は future learning 用に短く記録する。",
        "- このレポートとDBは記録用であり、投稿実行機能ではない。",
        "",
        "## Result Slots",
        "",
    ]
    for result in results:
        learning = result.get("future_learning", {})
        lines.extend(
            [
                f"### Slot {result.get('slot')}",
                "",
                f"- candidate_id: `{result.get('candidate_id', '')}`",
                f"- post_datetime_jst: `{metric_value(result.get('post_datetime_jst'))}`",
                f"- image_used: `{result.get('image_used')}`",
                f"- impressions: `{metric_value(result.get('impressions'))}`",
                f"- likes: `{metric_value(result.get('likes'))}`",
                f"- reposts: `{metric_value(result.get('reposts'))}`",
                f"- replies: `{metric_value(result.get('replies'))}`",
                f"- bookmarks: `{metric_value(result.get('bookmarks'))}`",
                f"- profile_visits: `{metric_value(result.get('profile_visits'))}`",
                f"- follows: `{metric_value(result.get('follows'))}`",
                f"- manual_notes: `{metric_value(result.get('manual_notes'))}`",
                f"- good_pattern: `{metric_value(learning.get('good_pattern'))}`",
                f"- weak_pattern: `{metric_value(learning.get('weak_pattern'))}`",
                f"- persona_fit: `{learning.get('persona_fit', 'unreviewed')}`",
                "",
                "```text",
                result.get("post_text", ""),
                "```",
                "",
            ]
        )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    results_db = read_json(RESULTS_PATH)
    write_report(results_db)
    print("status=MANUAL_RESULT_LOGGING_ONLY")
    print("live_posting=NOT_EXECUTED")
    print("x_api_write=NOT_USED")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"slots={len(results_db.get('manual_post_results', []))}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
