#!/usr/bin/env python3
"""Generate the final Villain safety check report.

This script is read/report only. It does not log in to X, authenticate with an
API, upload media, publish posts, schedule posts, or change safety flags.
At the current preparation stage every payload is intentionally BLOCKED.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
X_CONFIG_PATH = ROOT / "data" / "x_api_config.json"
AUTO_PLAN_PATH = ROOT / "data" / "villain_auto_post_plan.json"
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
HISTORY_PATH = ROOT / "data" / "villain_post_history.json"
STATUS_PATH = ROOT / "status.json"
REPORT_PATH = ROOT / "reports" / "villain_final_safety_check.md"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def credential_envs_only(credentials: dict) -> bool:
    if not credentials:
        return False
    return all(isinstance(value, str) and value.startswith("X_") for value in credentials.values())


def live_function_exists() -> bool:
    # This repository stage intentionally has no live posting function.
    return False


def global_blockers(x_config: dict, auto_plan: dict) -> list[str]:
    connection = x_config.get("connection", {})
    guard = x_config.get("posting_guard", {})
    credentials = x_config.get("credentials", {})
    policy = auto_plan.get("global_policy", {})
    blockers: list[str] = []

    if guard.get("auto_post_enabled") is False or policy.get("auto_post_enabled") is False:
        blockers.append("auto_post_enabled is false")
    if connection.get("dry_run_only") is True:
        blockers.append("dry_run_only is true")
    if connection.get("api_connected") is False:
        blockers.append("api_connected is false")
    if guard.get("manual_approval_required") is not True:
        blockers.append("manual_approval_required is not true")
    if policy.get("posting_execution_allowed") is False:
        blockers.append("posting_execution_allowed is false")
    if policy.get("external_api_integration_allowed") is False:
        blockers.append("external_api_integration_allowed is false")
    if policy.get("x_login_operation_allowed") is False:
        blockers.append("x_login_operation_allowed is false")
    if credential_envs_only(credentials):
        blockers.append("X credentials are not configured; only environment variable names are present")
    if not live_function_exists():
        blockers.append("no live post function exists")

    return blockers


def payload_blockers(payload: dict, x_config: dict, auto_plan: dict) -> list[str]:
    blockers = global_blockers(x_config, auto_plan)
    approval = payload.get("approval", {})
    checks = payload.get("checks_snapshot", {})
    safety = payload.get("safety", {})

    if payload.get("status") != "dry_run_preview_ready":
        blockers.append("payload status is not dry_run_preview_ready")
    if not payload.get("image_path"):
        blockers.append("image_path is null")
    if checks.get("image_attached") != "pass":
        blockers.append("image_attached is not pass")
    if checks.get("passcode_confirmed") != "pass":
        blockers.append("passcode_confirmed is not pass")
    if checks.get("prohibited_content_check") != "pass":
        blockers.append("prohibited_content_check is not pass")
    if checks.get("skip_day_policy") is True:
        blockers.append("skip_day_policy is true")
    if approval.get("human_confirm_received") is not True:
        blockers.append("human_confirm_received is not true")
    if approval.get("approved_for_live_post") is not True:
        blockers.append("approved_for_live_post is not true")
    if safety.get("live_post_blocked") is True:
        blockers.append("live_post_blocked is true")
    if safety.get("postable_judgment") is not True:
        blockers.append("postable_judgment is false")

    return blockers


def render_payload(payload: dict, blockers: list[str]) -> str:
    approval = payload.get("approval", {})
    safety = payload.get("safety", {})
    lines = [
        f"## Payload `{payload.get('payload_id', '')}`",
        "",
        "- Final judgment: `BLOCKED`",
        f"- `source_queue_id`: `{payload.get('source_queue_id', '')}`",
        f"- `status`: `{payload.get('status', '')}`",
        f"- `post_type`: `{payload.get('post_type', '')}`",
        f"- `approved_for_live_post`: `{bool_text(approval.get('approved_for_live_post', False))}`",
        f"- `human_confirm_received`: `{bool_text(approval.get('human_confirm_received', False))}`",
        f"- `dry_run_only`: `{bool_text(safety.get('dry_run_only', True))}`",
        f"- `api_connected`: `{bool_text(safety.get('api_connected', False))}`",
        f"- `live_post_blocked`: `{bool_text(safety.get('live_post_blocked', True))}`",
        f"- `auto_post_enabled`: `{bool_text(safety.get('auto_post_enabled', False))}`",
        f"- `postable_judgment`: `{bool_text(safety.get('postable_judgment', False))}`",
        "",
        "### BLOCKED Reasons",
        "",
    ]
    lines.extend(f"- {blocker}" for blocker in blockers)
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    x_config = read_json(X_CONFIG_PATH)
    auto_plan = read_json(AUTO_PLAN_PATH)
    payload_db = read_json(PAYLOADS_PATH)
    queue_db = read_json(QUEUE_PATH)
    history_db = read_json(HISTORY_PATH)
    status_db = read_json(STATUS_PATH)
    generated_at = datetime.now(timezone.utc).isoformat()

    payloads = payload_db.get("payloads", [])
    queue_count = len(queue_db.get("queue", []))
    history_count = len(history_db.get("history", []))
    global_reasons = global_blockers(x_config, auto_plan)

    lines = [
        "# Villain Final Safety Check",
        "",
        f"- Generated at: `{generated_at}`",
        "- Overall judgment: `BLOCKED`",
        "- Live posting: `not allowed`",
        f"- Payload count: `{len(payloads)}`",
        f"- Queue count: `{queue_count}`",
        f"- History count: `{history_count}`",
        f"- Status file loaded: `{bool_text(bool(status_db))}`",
        "",
        "This report is read-only. It does not log in to X, authenticate with an API, upload media, publish posts, schedule posts, or change any safety flags.",
        "",
        "## Required Conditions For Future Posting",
        "",
        "- `auto_post_enabled` must be true.",
        "- `manual_approval_required` must remain true.",
        "- `dry_run_only` must be false.",
        "- `api_connected` must be true.",
        "- Queue item must be approved.",
        "- Image must be ready.",
        "- Final caption must be ready.",
        "- Prohibited content check must be pass.",
        "- Human confirmation must exactly match POST_APPROVED.",
        "- Live post function must exist and pass a separate review.",
        "",
        "## Global BLOCKED Reasons",
        "",
    ]
    lines.extend(f"- {reason}" for reason in global_reasons)
    lines.append("")

    if not payloads:
        lines.extend(["## Payloads", "", "No dry-run payloads found.", ""])
    else:
        for payload in payloads:
            lines.append(render_payload(payload, payload_blockers(payload, x_config, auto_plan)))

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote final safety check report to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
