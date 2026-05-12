#!/usr/bin/env python3
"""Build the Villain posting unlock status report.

This script only reads local JSON/report files and writes a Markdown status
report. It does not read .env, connect to X, call write APIs, or publish posts.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "data" / "villain_post_unlock_rules.json"
VALIDATION_PATH = ROOT / "data" / "villain_dry_run_validation.json"
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
X_CONFIG_PATH = ROOT / "data" / "x_api_config.json"
PRE_POST_REPORT_PATH = ROOT / "reports" / "villain_pre_post_check.md"
REPORT_PATH = ROOT / "reports" / "villain_unlock_status.md"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def bool_text(value: object) -> str:
    return "true" if value is True else "false"


def read_pre_post_final_status() -> str:
    if not PRE_POST_REPORT_PATH.exists():
        return "BLOCKED"
    text = PRE_POST_REPORT_PATH.read_text(encoding="utf-8")
    match = re.search(r"- Final judgment: `([^`]+)`", text)
    return match.group(1) if match else "BLOCKED"


def validation_result_for(validation: dict, payload_id: str) -> dict:
    for result in validation.get("results", []):
        if result.get("payload_id") == payload_id:
            return result
    return {}


def evaluate_payload(
    payload: dict,
    rules: dict,
    validation: dict,
    x_config: dict,
    final_status: str,
) -> dict:
    approval = payload.get("approval", {})
    guard = x_config.get("posting_guard", {})
    caption = payload.get("caption", "")
    manual_state = rules.get("manual_state", {})
    validation_result = validation_result_for(validation, payload.get("payload_id", ""))

    checks = [
        {
            "id": "manual_approval",
            "ok": approval.get("human_confirm_received") is True,
            "actual": approval.get("human_confirm_received", False),
            "required": True,
        },
        {
            "id": "approved_for_live_post",
            "ok": approval.get("approved_for_live_post") is True,
            "actual": approval.get("approved_for_live_post", False),
            "required": True,
        },
        {
            "id": "write_action_kill_switch",
            "ok": guard.get("write_action_kill_switch") is False,
            "actual": guard.get("write_action_kill_switch", True),
            "required": False,
        },
        {
            "id": "validator_passed_count",
            "ok": validation.get("passed_count", 0) > 0,
            "actual": validation.get("passed_count", 0),
            "required": "> 0",
        },
        {
            "id": "postable_count",
            "ok": validation.get("postable_count", 0) > 0,
            "actual": validation.get("postable_count", 0),
            "required": "> 0",
        },
        {
            "id": "final_status",
            "ok": final_status != "BLOCKED",
            "actual": final_status,
            "required": "!= BLOCKED",
        },
        {
            "id": "caption_present",
            "ok": isinstance(caption, str) and bool(caption.strip()),
            "actual": isinstance(caption, str) and bool(caption.strip()),
            "required": True,
        },
        {
            "id": "target_account_confirmed",
            "ok": manual_state.get("target_account_confirmed") is True,
            "actual": manual_state.get("target_account_confirmed", False),
            "required": True,
        },
    ]

    status = "READY_FOR_MANUAL_POST" if all(check["ok"] for check in checks) else "BLOCKED"
    blockers = [check["id"] for check in checks if not check["ok"]]

    return {
        "payload_id": payload.get("payload_id", ""),
        "status": status,
        "validation_status": validation_result.get("validation_status", "missing"),
        "checks": checks,
        "blockers": blockers,
    }


def render_payload(result: dict) -> str:
    lines = [
        f"## Payload `{result.get('payload_id', '')}`",
        "",
        f"- unlock status: `{result.get('status', 'BLOCKED')}`",
        f"- dry-run validator: `{result.get('validation_status', 'missing')}`",
        "",
        "### Conditions",
        "",
    ]
    for check in result.get("checks", []):
        lines.append(
            f"- `{check['id']}`: `{'pass' if check['ok'] else 'fail'}` "
            f"(actual `{check['actual']}`, required `{check['required']}`)"
        )
    lines.extend(["", "### BLOCKED Reasons", ""])
    blockers = result.get("blockers", [])
    lines.extend(f"- {blocker}" for blocker in blockers) if blockers else lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    rules = read_json(RULES_PATH)
    validation = read_json(VALIDATION_PATH)
    payload_db = read_json(PAYLOADS_PATH)
    x_config = read_json(X_CONFIG_PATH)
    final_status = read_pre_post_final_status()
    payloads = payload_db.get("payloads", [])
    generated_at = datetime.now(timezone.utc).isoformat()
    results = [
        evaluate_payload(payload, rules, validation, x_config, final_status)
        for payload in payloads
    ]
    overall_status = (
        "READY_FOR_MANUAL_POST"
        if results and any(result["status"] == "READY_FOR_MANUAL_POST" for result in results)
        else "BLOCKED"
    )

    lines = [
        "# Villain Posting Unlock Status",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Overall unlock status: `{overall_status}`",
        f"- FINAL_STATUS source: `{final_status}`",
        "- Live posting: `DISABLED`",
        "- X API write actions: `NOT USED`",
        "",
        "## Rule Summary",
        "",
        f"- unlock target: `{rules.get('unlock_target_status', 'READY_FOR_MANUAL_POST')}`",
        f"- default status: `{rules.get('default_status', 'BLOCKED')}`",
        f"- all conditions required: `{bool_text(rules.get('all_conditions_required'))}`",
        f"- target account confirmed: `{bool_text(rules.get('manual_state', {}).get('target_account_confirmed'))}`",
        "",
    ]

    if results:
        lines.extend(render_payload(result) for result in results)
    else:
        lines.extend(["## Payloads", "", "No payloads found.", ""])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote unlock status report to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
