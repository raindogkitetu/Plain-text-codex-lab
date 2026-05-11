#!/usr/bin/env python3
"""Validate Villain dry-run payloads without performing any live action."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
X_CONFIG_PATH = ROOT / "data" / "x_api_config.json"
AUTO_PLAN_PATH = ROOT / "data" / "villain_auto_post_plan.json"
OUTPUT_PATH = ROOT / "data" / "villain_dry_run_validation.json"

MAX_CAPTION_CHARACTERS = 25000


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def check_payload(payload: dict, x_config: dict, auto_plan: dict) -> dict:
    connection = x_config.get("connection", {})
    guard = x_config.get("posting_guard", {})
    policy = auto_plan.get("global_policy", {})
    approval = payload.get("approval", {})
    safety = payload.get("safety", {})
    caption = payload.get("caption", "")
    failures: list[str] = []
    blockers: list[str] = []

    if not isinstance(caption, str) or not caption.strip():
        failures.append("caption is empty")
    if isinstance(caption, str) and len(caption) > MAX_CAPTION_CHARACTERS:
        failures.append("caption exceeds max character limit")

    if guard.get("auto_post_enabled") is not False:
        failures.append("auto_post_enabled is not false")
    if connection.get("dry_run_only") is not True:
        failures.append("dry_run_only is not true")
    if connection.get("api_connected") is not False:
        failures.append("api_connected is not false")
    if safety.get("live_post_blocked") is not True:
        failures.append("live_post_blocked is not true")
    if policy.get("posting_execution_allowed") is not False:
        failures.append("posting_execution_allowed is not false")
    if policy.get("external_api_integration_allowed") is not False:
        failures.append("external_api_integration_allowed is not false")

    if guard.get("write_action_kill_switch") is True:
        blockers.append("write_action_kill_switch is true")
    if approval.get("human_confirm_received") is not True:
        blockers.append("human approval is missing")
    if safety.get("postable_judgment") is not False:
        failures.append("postable_judgment is not false")
    if approval.get("approved_for_live_post") is not False:
        failures.append("approved_for_live_post is not false")

    validation_passed = not failures
    postable_judgment = False

    return {
        "payload_id": payload.get("payload_id", ""),
        "source_queue_id": payload.get("source_queue_id", ""),
        "validation_status": "pass" if validation_passed else "fail",
        "postable_judgment": postable_judgment,
        "caption_characters": len(caption) if isinstance(caption, str) else 0,
        "max_caption_characters": MAX_CAPTION_CHARACTERS,
        "failures": failures,
        "blockers": blockers,
        "approval": {
            "human_confirm_received": approval.get("human_confirm_received", False),
            "approved_for_live_post": approval.get("approved_for_live_post", False),
            "approval_is_not_postability": True,
        },
        "required_double_check": {
            "first_check_dry_run_validator": validation_passed,
            "second_check_manual_approval": approval.get("human_confirm_received") is True,
            "final_check_kill_switch_false": guard.get("write_action_kill_switch") is False,
        },
    }


def main() -> None:
    payload_db = read_json(PAYLOADS_PATH)
    x_config = read_json(X_CONFIG_PATH)
    auto_plan = read_json(AUTO_PLAN_PATH)
    payloads = payload_db.get("payloads", [])
    generated_at = datetime.now(timezone.utc).isoformat()
    results = [check_payload(payload, x_config, auto_plan) for payload in payloads]

    output = {
        "db_name": "Villain Dry Run Validation",
        "version": "0.1.0",
        "status": "validated_blocked",
        "generated_at": generated_at,
        "source_payload_path": "data/villain_dry_run_payloads.json",
        "payload_count": len(results),
        "passed_count": sum(1 for result in results if result["validation_status"] == "pass"),
        "failed_count": sum(1 for result in results if result["validation_status"] == "fail"),
        "postable_count": 0,
        "global_postable_judgment": False,
        "results": results,
    }

    write_json(OUTPUT_PATH, output)
    print(f"wrote dry-run validation to {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
