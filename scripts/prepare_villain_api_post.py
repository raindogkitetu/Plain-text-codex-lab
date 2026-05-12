#!/usr/bin/env python3
"""Prepare a Villain API post readiness report without posting.

This script does not read .env, connect to X, call write APIs, create tweets,
upload media, publish posts, or change posting flags.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "data" / "villain_api_post_rules.json"
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
VALIDATION_PATH = ROOT / "data" / "villain_dry_run_validation.json"
X_CONFIG_PATH = ROOT / "data" / "x_api_config.json"
UNLOCK_REPORT_PATH = ROOT / "reports" / "villain_unlock_status.md"
MANUAL_POST_REPORT_PATH = ROOT / "reports" / "villain_live_manual_post_ready.md"
REPORT_PATH = ROOT / "reports" / "villain_api_post_readiness.md"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def bool_text(value: object) -> str:
    return "true" if value is True else "false"


def read_unlock_status() -> str:
    text = read_text(UNLOCK_REPORT_PATH)
    match = re.search(r"- Overall unlock status: `([^`]+)`", text)
    return match.group(1) if match else "BLOCKED"


def recorded_post_url() -> str:
    text = read_text(MANUAL_POST_REPORT_PATH)
    match = re.search(r"- 投稿URL: `([^`]+)`", text)
    return match.group(1) if match else ""


def validation_for_payload(validation: dict, payload_id: str) -> dict:
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
    post_url: str,
) -> dict:
    approval = payload.get("approval", {})
    guard = x_config.get("posting_guard", {})
    caption = payload.get("caption", "")
    manual_state = rules.get("manual_state", {})
    validation_result = validation_for_payload(validation, payload.get("payload_id", ""))

    checks = [
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
            "id": "final_status",
            "ok": final_status == rules.get("target_status", "READY_FOR_API_POST"),
            "actual": final_status,
            "required": rules.get("target_status", "READY_FOR_API_POST"),
        },
        {
            "id": "postable_count",
            "ok": validation.get("postable_count", 0) > 0,
            "actual": validation.get("postable_count", 0),
            "required": "> 0",
        },
        {
            "id": "target_account_confirmed",
            "ok": manual_state.get("target_account_confirmed") is True,
            "actual": manual_state.get("target_account_confirmed", False),
            "required": True,
        },
        {
            "id": "caption_present",
            "ok": isinstance(caption, str) and bool(caption.strip()),
            "actual": isinstance(caption, str) and bool(caption.strip()),
            "required": True,
        },
        {
            "id": "post_url_not_recorded",
            "ok": not bool(post_url),
            "actual": not bool(post_url),
            "required": True,
        },
        {
            "id": "api_final_human_confirmed",
            "ok": manual_state.get("api_final_human_confirmed") is True,
            "actual": manual_state.get("api_final_human_confirmed", False),
            "required": True,
        },
    ]

    status = rules.get("target_status", "READY_FOR_API_POST") if all(check["ok"] for check in checks) else "BLOCKED"
    blockers = [check["id"] for check in checks if not check["ok"]]

    return {
        "payload_id": payload.get("payload_id", ""),
        "status": status,
        "validation_status": validation_result.get("validation_status", "missing"),
        "caption": caption,
        "caption_characters": len(caption) if isinstance(caption, str) else 0,
        "post_url_recorded": post_url,
        "checks": checks,
        "blockers": blockers,
    }


def render_payload(result: dict) -> str:
    lines = [
        f"## Payload `{result.get('payload_id', '')}`",
        "",
        f"- API readiness: `{result.get('status', 'BLOCKED')}`",
        f"- dry-run validator: `{result.get('validation_status', 'missing')}`",
        f"- caption characters: `{result.get('caption_characters', 0)}`",
        f"- recorded post URL: `{result.get('post_url_recorded') or 'none'}`",
        "",
        "### Caption",
        "",
        "```text",
        result.get("caption", ""),
        "```",
        "",
        "### Conditions",
        "",
    ]
    for check in result.get("checks", []):
        lines.append(
            f"- `{check['id']}`: `{'pass' if check['ok'] else 'fail'}` "
            f"(actual `{check['actual']}`, required `{check['required']}`)"
        )
    lines.extend(["", "### API Post BLOCKED Reasons", ""])
    blockers = result.get("blockers", [])
    lines.extend(f"- {blocker}" for blocker in blockers) if blockers else lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    rules = read_json(RULES_PATH)
    payload_db = read_json(PAYLOADS_PATH)
    validation = read_json(VALIDATION_PATH)
    x_config = read_json(X_CONFIG_PATH)
    payloads = payload_db.get("payloads", [])
    final_status = read_unlock_status()
    post_url = recorded_post_url()
    generated_at = datetime.now(timezone.utc).isoformat()
    results = [
        evaluate_payload(payload, rules, validation, x_config, final_status, post_url)
        for payload in payloads
    ]
    overall_status = (
        rules.get("target_status", "READY_FOR_API_POST")
        if results and any(result["status"] == rules.get("target_status", "READY_FOR_API_POST") for result in results)
        else "BLOCKED"
    )

    lines = [
        "# Villain API Post Readiness",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Overall API post readiness: `{overall_status}`",
        f"- FINAL_STATUS source: `{final_status}`",
        "- X API write actions: `NOT USED`",
        "- create_tweet: `NOT EXECUTED`",
        "- upload_media: `NOT EXECUTED`",
        "- `.env` read: `NO`",
        "",
        "## Rule Summary",
        "",
        f"- target status: `{rules.get('target_status', 'READY_FOR_API_POST')}`",
        f"- default status: `{rules.get('default_status', 'BLOCKED')}`",
        f"- api_write_allowed_now: `{bool_text(rules.get('api_write_allowed_now'))}`",
        f"- create_tweet_allowed_now: `{bool_text(rules.get('create_tweet_allowed_now'))}`",
        f"- target account: `{rules.get('manual_state', {}).get('target_account', '')}`",
        "",
    ]

    if results:
        lines.extend(render_payload(result) for result in results)
    else:
        lines.extend(["## Payloads", "", "No payloads found.", ""])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote API post readiness report to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
