#!/usr/bin/env python3
"""Validate and ingest a pasted ChatGPT bridge decision.

The decision source is data/chatgpt_to_codex_handoff.json. This script does
not post, upload media, create tweets, or generate tracking codes.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
CHATGPT_INBOX = ROOT / "data" / "chatgpt_to_codex_handoff.json"
BRIDGE_EXCHANGE = ROOT / "data" / "chatgpt_bridge_exchange.json"
TRAJECTORY_PATH = ROOT / "data" / "agent_handoff_trajectory.json"
HANDOFF_REPORT = ROOT / "reports" / "agent_handoff_status.md"
BRIDGE_PROMPT = ROOT / "reports" / "chatgpt_bridge_prompt.md"
JST = ZoneInfo("Asia/Tokyo")
INBOX_SCHEMA_VERSION = "handoff.chatgpt_to_codex.v1"
DECISION_SCHEMA_VERSION = "handoff.chatgpt_decision.v1"
EXCHANGE_SCHEMA_VERSION = "handoff.chatgpt_bridge_exchange.v1"
TRAJECTORY_SCHEMA_VERSION = "handoff.trajectory.v1"


def now_jst() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def explicit_human_post_approval(inbox: dict[str, Any]) -> bool:
    approval = inbox.get("explicit_human_post_approval", {})
    if not isinstance(approval, dict):
        return False
    return approval.get("approved") is True and approval.get("scope") == "posting_execution"


def decision_payload(inbox: dict[str, Any]) -> dict[str, Any]:
    if "chatgpt_review_decision" in inbox:
        return inbox
    return inbox.get("chatgpt_decision", {})


def has_tracking_code_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key == "tracking_code":
                return True
            if has_tracking_code_key(nested):
                return True
    if isinstance(value, list):
        return any(has_tracking_code_key(item) for item in value)
    return False


def validate_decision(inbox: dict[str, Any]) -> tuple[str, list[str]]:
    errors: list[str] = []
    payload = decision_payload(inbox)
    schema_version = payload.get("schema_version") or inbox.get("schema_version")
    if schema_version not in {INBOX_SCHEMA_VERSION, DECISION_SCHEMA_VERSION}:
        errors.append(f"invalid_schema_version:{schema_version}")
    decision = payload.get("chatgpt_review_decision", {})
    if not isinstance(decision, dict) or not decision.get("decision"):
        errors.append("missing_chatgpt_review_decision")
    safe_to_post = payload.get("safe_to_post", inbox.get("safe_to_post", False))
    if safe_to_post is True and not explicit_human_post_approval(inbox):
        errors.append("safe_to_post_true_without_explicit_human_approval")
    posting_status = payload.get("posting_execution_status", inbox.get("posting_execution_status", "BLOCKED"))
    if posting_status != "BLOCKED" and not explicit_human_post_approval(inbox):
        errors.append("posting_execution_status_not_blocked_without_explicit_human_approval")
    if has_tracking_code_key(payload):
        errors.append("tracking_code_field_detected")
    status = "ACCEPTED" if not errors else "REJECTED"
    return status, errors


def append_trajectory(generated_at: str, status: str, errors: list[str], inbox: dict[str, Any]) -> None:
    db = read_json(
        TRAJECTORY_PATH,
        {
            "db_name": "Agent Handoff Trajectory",
            "events": [],
            "schema_version": TRAJECTORY_SCHEMA_VERSION,
            "version": "1.0.0",
        },
    )
    events = db.setdefault("events", [])
    events.append(
        {
            "at_jst": generated_at,
            "decision": decision_payload(inbox).get("chatgpt_review_decision", {}).get("decision", ""),
            "event_type": "chatgpt_bridge_decision_ingested",
            "ingestion_errors": errors,
            "ingestion_status": status,
            "posting_executed": False,
            "safe_to_post": False,
            "tweet_creation_executed": False,
            "upload_media_executed": False,
        }
    )
    db["event_count"] = len(events)
    db["last_event_at_jst"] = generated_at
    write_json(TRAJECTORY_PATH, db)


def update_bridge_exchange(generated_at: str, status: str, errors: list[str]) -> None:
    exchange = read_json(
        BRIDGE_EXCHANGE,
        {
            "db_name": "ChatGPT Bridge Exchange",
            "schema_version": EXCHANGE_SCHEMA_VERSION,
            "version": "1.0.0",
        },
    )
    exchange.update(
        {
            "last_chatgpt_response_errors": errors,
            "last_chatgpt_response_ingested_at_jst": generated_at,
            "last_chatgpt_response_status": status,
            "posting_executed": False,
            "safe_to_post": False,
            "tweet_creation_executed": False,
            "upload_media_executed": False,
        }
    )
    write_json(BRIDGE_EXCHANGE, exchange)


def update_report(generated_at: str, status: str, errors: list[str]) -> None:
    section = [
        "",
        "## ChatGPT Bridge",
        "",
        f"- bridge prompt: `{BRIDGE_PROMPT.relative_to(ROOT)}`",
        f"- last ingestion at JST: `{generated_at}`",
        f"- last_chatgpt_response_status: `{status}`",
        f"- ingestion_errors: `{errors if errors else 'none'}`",
        "- safe_to_post: `false`",
        "- posting_execution_status: `BLOCKED`",
        "- posting executed: `NO`",
        "- upload executed: `NO`",
        "- tweet creation executed: `NO`",
        "",
    ]
    existing = HANDOFF_REPORT.read_text(encoding="utf-8") if HANDOFF_REPORT.exists() else "# Agent Handoff Status\n"
    marker = "\n## ChatGPT Bridge\n"
    if marker in existing:
        existing = existing.split(marker)[0].rstrip() + "\n"
    HANDOFF_REPORT.parent.mkdir(parents=True, exist_ok=True)
    HANDOFF_REPORT.write_text(existing.rstrip() + "\n" + "\n".join(section), encoding="utf-8")


def main() -> None:
    generated_at = now_jst()
    inbox = read_json(CHATGPT_INBOX, {})
    status, errors = validate_decision(inbox)
    append_trajectory(generated_at, status, errors, inbox)
    update_bridge_exchange(generated_at, status, errors)
    update_report(generated_at, status, errors)
    print(f"last_chatgpt_response_status={status}")
    print(f"errors={errors if errors else 'none'}")
    print("posting_executed=NO")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
