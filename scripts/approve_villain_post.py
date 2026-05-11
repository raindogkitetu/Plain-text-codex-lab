#!/usr/bin/env python3
"""Apply a human approval marker to a Villain dry-run payload.

This is an approval gate only. It never logs in to X, never authenticates with
an API, never uploads media, never publishes, and never schedules a post.
Dry-run safety remains active, so postable judgment stays false while
dry_run_only is true.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
X_CONFIG_PATH = ROOT / "data" / "x_api_config.json"
REQUIRED_CONFIRM_TEXT = "POST_APPROVED"


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Mark a Villain dry-run payload as human-approved."
    )
    parser.add_argument("--payload-id", required=True)
    parser.add_argument("--confirm", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.confirm != REQUIRED_CONFIRM_TEXT:
        raise SystemExit("Approval failed: confirmation text must exactly match POST_APPROVED")

    payload_db = read_json(PAYLOADS_PATH)
    x_config = read_json(X_CONFIG_PATH)
    connection = x_config.get("connection", {})
    guard = x_config.get("posting_guard", {})
    payloads = payload_db.get("payloads", [])
    target = next(
        (payload for payload in payloads if payload.get("payload_id") == args.payload_id),
        None,
    )

    if target is None:
        raise SystemExit(f"Approval failed: payload not found: {args.payload_id}")

    approval = target.setdefault("approval", {})
    safety = target.setdefault("safety", {})

    if approval.get("manual_approval_required") is not True:
        raise SystemExit("Approval failed: manual_approval_required must be true")

    approval["human_confirm_received"] = True
    approval["human_confirm_text"] = REQUIRED_CONFIRM_TEXT
    approval["daisho_approval_status"] = "approved"
    approval["approval_status"] = "human_approved"
    approval["approved_for_live_post"] = False
    approval["approval_not_postable_reason"] = (
        "Human approval is recorded separately from postability; write_action_kill_switch, dry_run_only, and live_post_blocked keep this payload non-postable."
    )
    approval["approved_at"] = datetime.now(timezone.utc).isoformat()

    safety["dry_run_only"] = connection.get("dry_run_only", True)
    safety["api_connected"] = connection.get("api_connected", False)
    safety["write_action_kill_switch"] = guard.get("write_action_kill_switch", True)
    safety["live_post_blocked"] = True
    safety["auto_post_enabled"] = guard.get("auto_post_enabled", False)
    safety["postable_judgment"] = False
    safety["blocked_reason"] = (
        "Human approval recorded, but kill switch/dry-run/live-post blocking keeps postable_judgment false."
    )

    payload_db["status"] = "dry_run_only"
    payload_db["posting_execution_allowed"] = False
    payload_db["api_connection_allowed"] = False

    write_json(PAYLOADS_PATH, payload_db)
    print(f"approved dry-run payload {args.payload_id}; live posting remains blocked")


if __name__ == "__main__":
    main()
