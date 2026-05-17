#!/usr/bin/env python3
"""03:00 maintenance job for Villain Auto Posting OS.

This job is local/read-write maintenance only. It validates JSON files, refreshes
recent media history, and writes reports. It has no X write path.
"""

from __future__ import annotations

import json
import subprocess
import sys
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
HANDOFF_RUNNER_PATH = ROOT / "scripts" / "agent_handoff_runner.py"
BUILD_REVIEW_BOARD_PATH = ROOT / "scripts" / "build_human_review_board.py"
IMAGE_SELECTOR_PATH = ROOT / "scripts" / "local_image_selector.py"
HANDOFF_REPORT_PATH = ROOT / "reports" / "agent_handoff_status.md"
QUALITY_REPORT_PATH = ROOT / "reports" / "villain_quality_review_summary.md"
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



def run_safe_script(script_path: Path, label: str) -> dict[str, Any]:
    command = [sys.executable, str(script_path)]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    stdout_lines = [line for line in completed.stdout.splitlines() if line.strip()]
    stderr_lines = [line for line in completed.stderr.splitlines() if line.strip()]
    return {
        "label": label,
        "status": "SUCCESS" if completed.returncode == 0 else "FAILED",
        "returncode": completed.returncode,
        "command": f"python3 scripts/{script_path.name}",
        "stdout_tail": stdout_lines[-20:],
        "stderr_tail": stderr_lines[-20:],
        "posting_executed": False,
        "upload_media_executed": False,
        "tweet_creation_executed": False,
    }

def run_handoff_runner() -> dict[str, Any]:
    command = [sys.executable, str(HANDOFF_RUNNER_PATH)]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    stdout_lines = [line for line in completed.stdout.splitlines() if line.strip()]
    stderr_lines = [line for line in completed.stderr.splitlines() if line.strip()]
    return {
        "status": "SUCCESS" if completed.returncode == 0 else "FAILED",
        "returncode": completed.returncode,
        "command": "python3 scripts/agent_handoff_runner.py",
        "stdout_tail": stdout_lines[-20:],
        "stderr_tail": stderr_lines[-20:],
        "posting_executed": False,
        "upload_media_executed": False,
        "tweet_creation_executed": False,
        "reports_updated": [
            str(HANDOFF_REPORT_PATH.relative_to(ROOT)),
            str(QUALITY_REPORT_PATH.relative_to(ROOT)),
        ],
    }


def scheduler_report(result: dict[str, Any]) -> str:
    media = result.get("recent_media_history", {})
    sanity = result.get("json_sanity_check", {})
    handoff = result.get("agent_handoff", {})
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
            "- 03:00 maintenance also runs `python3 scripts/agent_handoff_runner.py` for Quality OS handoff reports.",
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
            f"- agent_handoff: `{handoff.get('status')}`",
            f"- agent_handoff_command: `{handoff.get('command')}`",
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
    handoff = result.get("agent_handoff", {})
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
        "## Agent Handoff",
        "",
        f"- status: `{handoff.get('status')}`",
        f"- command: `{handoff.get('command')}`",
        f"- returncode: `{handoff.get('returncode')}`",
        "- posting executed: `NO`",
        "- upload executed: `NO`",
        "- tweet creation executed: `NO`",
        f"- reports_updated: `{', '.join(handoff.get('reports_updated', []))}`",
        "",
    ]
    if handoff.get("stdout_tail"):
        lines.extend(["### Handoff Output", ""])
        lines.extend(f"- `{line}`" for line in handoff.get("stdout_tail", []))
        lines.append("")
    if handoff.get("stderr_tail"):
        lines.extend(["### Handoff Errors", ""])
        lines.extend(f"- `{line}`" for line in handoff.get("stderr_tail", []))
        lines.append("")
    if sanity.get("failures"):
        lines.extend(["## Failures", ""])
        lines.extend(f"- `{item.get('path')}`: `{item.get('error')}`" for item in sanity.get("failures", []))
        lines.append("")
    return "\n".join(lines)


def build_result() -> dict[str, Any]:
    sanity = json_sanity_check()
    media_history = build_recent_media_history(write=True)
    handoff = run_handoff_runner()
    return {
        "db_name": "Villain Auto Maintenance Run",
        "version": "1.0.0",
        "generated_at_jst": now_jst(),
        "status": "SUCCESS" if sanity.get("status") == "PASSED" and handoff.get("status") == "SUCCESS" else "FAILED",
        "job": "03:00_maintenance",
        "posting_executed": False,
        "x_api_write_used": False,
        "json_sanity_check": sanity,
        "recent_media_history": {
            "cooldown_days": media_history.get("cooldown_days"),
            "near_duplicate_hamming_threshold": media_history.get("near_duplicate_hamming_threshold"),
            "entries": media_history.get("entries", []),
        },
        "agent_handoff": handoff,
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
