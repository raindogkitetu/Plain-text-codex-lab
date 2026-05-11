#!/usr/bin/env python3
"""Build a human-readable Villain pre-post safety check report.

This script is read/report only. It does not read .env, connect to X, upload
media, publish posts, schedule posts, or change posting flags.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_PATH = ROOT / "data" / "villain_dry_run_validation.json"
X_CONFIG_PATH = ROOT / "data" / "x_api_config.json"
REPORT_PATH = ROOT / "reports" / "villain_pre_post_check.md"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def bool_text(value: object) -> str:
    return "true" if value is True else "false"


def final_judgment(validation: dict, x_config: dict) -> str:
    guard = x_config.get("posting_guard", {})
    connection = x_config.get("connection", {})

    if guard.get("write_action_kill_switch") is True:
        return "BLOCKED"
    if connection.get("dry_run_only") is True:
        return "READY_DRY_RUN_ONLY"
    if validation.get("global_postable_judgment") is True:
        return "READY"
    return "BLOCKED"


def render_payload(result: dict) -> str:
    approval = result.get("approval", {})
    double_check = result.get("required_double_check", {})
    failures = result.get("failures", [])
    blockers = result.get("blockers", [])
    lines = [
        f"## Payload `{result.get('payload_id', '')}`",
        "",
        f"- `source_queue_id`: `{result.get('source_queue_id', '')}`",
        f"- dry-run validator: `{result.get('validation_status', 'unknown')}`",
        f"- caption characters: `{result.get('caption_characters', 0)}` / `{result.get('max_caption_characters', 0)}`",
        f"- manual approval received: `{bool_text(approval.get('human_confirm_received'))}`",
        f"- approved_for_live_post: `{bool_text(approval.get('approved_for_live_post'))}`",
        f"- approval is not postability: `{bool_text(approval.get('approval_is_not_postability'))}`",
        f"- postable_judgment: `{bool_text(result.get('postable_judgment'))}`",
        "",
        "### Double Check",
        "",
        f"- first check / dry-run validator OK: `{bool_text(double_check.get('first_check_dry_run_validator'))}`",
        f"- second check / manual approval OK: `{bool_text(double_check.get('second_check_manual_approval'))}`",
        f"- final check / kill switch false: `{bool_text(double_check.get('final_check_kill_switch_false'))}`",
        "",
        "### Failures",
        "",
    ]
    lines.extend(f"- {failure}" for failure in failures) if failures else lines.append("- none")
    lines.extend(["", "### Blockers", ""])
    lines.extend(f"- {blocker}" for blocker in blockers) if blockers else lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    validation = read_json(VALIDATION_PATH)
    x_config = read_json(X_CONFIG_PATH)
    guard = x_config.get("posting_guard", {})
    connection = x_config.get("connection", {})
    results = validation.get("results", [])
    generated_at = datetime.now(timezone.utc).isoformat()
    judgment = final_judgment(validation, x_config)

    lines = [
        "# Villain Pre-Post Safety Check",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Final judgment: `{judgment}`",
        "- Live posting: `DISABLED`",
        "- X API write actions: `NOT USED`",
        "",
        "## Summary",
        "",
        f"- dry-run validation status: `{validation.get('status', 'missing')}`",
        f"- payload count: `{validation.get('payload_count', 0)}`",
        f"- validator passed: `{validation.get('passed_count', 0)}`",
        f"- validator failed: `{validation.get('failed_count', 0)}`",
        f"- postable count: `{validation.get('postable_count', 0)}`",
        f"- global postable judgment: `{bool_text(validation.get('global_postable_judgment'))}`",
        "",
        "## Gates",
        "",
        f"- `manual_approval_required`: `{bool_text(guard.get('manual_approval_required'))}`",
        f"- `write_action_kill_switch`: `{bool_text(guard.get('write_action_kill_switch'))}`",
        f"- `auto_post_enabled`: `{bool_text(guard.get('auto_post_enabled'))}`",
        f"- `dry_run_only`: `{bool_text(connection.get('dry_run_only'))}`",
        f"- `api_connected`: `{bool_text(connection.get('api_connected'))}`",
        "",
        "## Meaning",
        "",
        "- `dry-run validator pass` means the draft can be inspected safely.",
        "- `manual approval received` means a human approval marker exists.",
        "- `postable_judgment=false` means it is still not allowed to post.",
        "- `write_action_kill_switch=true` keeps the final judgment BLOCKED.",
        "",
    ]

    if results:
        lines.extend(render_payload(result) for result in results)
    else:
        lines.extend(["## Payloads", "", "No validation results found.", ""])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote pre-post check report to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
