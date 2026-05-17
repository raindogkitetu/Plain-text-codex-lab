#!/usr/bin/env python3
"""03:00 maintenance job for Villain Auto Posting OS.

This job is local/read-write maintenance only. It validates JSON files, refreshes
recent media history, and writes reports. It has no X write path.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from media_deduplication import build_recent_media_history


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
STATUS_PATH = ROOT / "status.json"
RESULT_PATH = ROOT / "data" / "villain_auto_maintenance.json"
SCHEDULER_REPORT_PATH = ROOT / "reports" / "villain_auto_scheduler.md"
MAINTENANCE_REPORT_PATH = ROOT / "reports" / "villain_auto_maintenance.md"
JST = ZoneInfo("Asia/Tokyo")


def now_jst() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def json_sanity_check() -> dict[str, Any]:
    checked: list[str] = []
    failures: list[dict[str, str]] = []
    paths = sorted(DATA_DIR.glob("*.json"))
    if STATUS_PATH.exists():
        paths.append(STATUS_PATH)
    for path in paths:
        try:
            read_json(path)
            checked.append(str(path.relative_to(ROOT)))
        except Exception as error:  # noqa: BLE001 - report sanitized local JSON failure.
            failures.append({"path": str(path.relative_to(ROOT)), "error": str(error)})
    return {
        "status": "PASSED" if not failures else "FAILED",
        "checked_count": len(checked),
        "checked_files": checked,
        "failures": failures,
    }


def scheduler_report(result: dict[str, Any]) -> str:
    media = result.get("recent_media_history", {})
    sanity = result.get("json_sanity_check", {})
    return "\n".join(
        [
            "# Villain Auto Scheduler v1",
            "",
            f"- Generated at JST: `{result.get('generated_at_jst')}`",
            "- current job: `03:00 maintenance`",
            "- posting executed: `NO`",
            "- media upload executed: `NO`",
            "- tweet creation executed: `NO`",
            "",
            "## Daily Slots",
            "",
            "- 03:00: maintenance only; refresh JSON sanity, recent media history, and scheduler report.",
            "- 13:00: daytime posting slot.",
            "- 20:00: night posting slot.",
            "- 23:00: late night posting slot.",
            "",
            "## Scheduler Limits",
            "",
            "- max_posts_per_day: `3`",
            "- max_posts_per_run: `1`",
            "- cooldown_between_posts_minutes: `120`",
            "- post_count_source: `data/villain_post_outcomes.json`",
            "- scheduler_state_role: `auxiliary log only`",
            "",
            "## Gate Order",
            "",
            "1. `manual_stop`",
            "2. outcome DB daily success count",
            "3. cooldown from latest successful outcome",
            "4. `human_review.keep` from latest successful outcome",
            "5. Auto Post Pilot candidate gates",
            "6. X Write Adapter gates",
            "7. network preflight before any write attempt",
            "",
            "## Human Review Gate",
            "",
            "- `human_review.keep=pending` blocks as `human_review_pending`.",
            "- `human_review.keep=false` blocks as `previous_post_marked_delete_or_drop`.",
            "- `human_review.keep=true` is required before the next post.",
            "- If no successful outcome exists, scheduler can continue to candidate evaluation.",
            "",
            "## Maintenance Result",
            "",
            f"- json_sanity_check: `{sanity.get('status')}`",
            f"- json_files_checked: `{sanity.get('checked_count')}`",
            f"- recent_media_entries: `{len(media.get('entries', []))}`",
            "",
            "## Safety",
            "",
            "- passcode source: `data/villain_passcodes.json` active codes only.",
            "- passcode auto generation: `false`.",
            "- retry behavior: no automatic retry; one scheduler run can select at most one post.",
            "- 03:00 job is not a posting slot.",
            "",
        ]
    )


def maintenance_report(result: dict[str, Any]) -> str:
    sanity = result.get("json_sanity_check", {})
    media = result.get("recent_media_history", {})
    lines = [
        "# Villain Auto Maintenance v1",
        "",
        f"- Generated at JST: `{result.get('generated_at_jst')}`",
        f"- status: `{result.get('status')}`",
        "- job_time: `03:00`",
        "- posting executed: `NO`",
        "- media upload executed: `NO`",
        "- tweet creation executed: `NO`",
        "",
        "## JSON Sanity",
        "",
        f"- status: `{sanity.get('status')}`",
        f"- checked_count: `{sanity.get('checked_count')}`",
        "",
        "## Recent Media History",
        "",
        f"- cooldown_days: `{media.get('cooldown_days')}`",
        f"- entries: `{len(media.get('entries', []))}`",
        "",
    ]
    if sanity.get("failures"):
        lines.extend(["## Failures", ""])
        lines.extend(f"- `{item.get('path')}`: `{item.get('error')}`" for item in sanity.get("failures", []))
        lines.append("")
    return "\n".join(lines)


def build_result() -> dict[str, Any]:
    sanity = json_sanity_check()
    media_history = build_recent_media_history(write=True)
    return {
        "db_name": "Villain Auto Maintenance Run",
        "version": "1.0.0",
        "generated_at_jst": now_jst(),
        "status": "SUCCESS" if sanity.get("status") == "PASSED" else "FAILED",
        "job": "03:00_maintenance",
        "posting_executed": False,
        "x_api_write_used": False,
        "json_sanity_check": sanity,
        "recent_media_history": {
            "cooldown_days": media_history.get("cooldown_days"),
            "near_duplicate_hamming_threshold": media_history.get("near_duplicate_hamming_threshold"),
            "entries": media_history.get("entries", []),
        },
    }


def main() -> None:
    result = build_result()
    write_json(RESULT_PATH, result)
    SCHEDULER_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEDULER_REPORT_PATH.write_text(scheduler_report(result), encoding="utf-8")
    MAINTENANCE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    MAINTENANCE_REPORT_PATH.write_text(maintenance_report(result), encoding="utf-8")
    print(f"status={result.get('status')}")
    print("posting_executed=NO")
    print(f"wrote {RESULT_PATH.relative_to(ROOT)}")
    print(f"wrote {SCHEDULER_REPORT_PATH.relative_to(ROOT)}")
    print(f"wrote {MAINTENANCE_REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
