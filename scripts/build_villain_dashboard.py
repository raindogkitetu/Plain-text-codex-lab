#!/usr/bin/env python3
"""Build the Villain posting OS status dashboard.

This script is read/report only. It does not log in to X, authenticate with an
API, upload media, publish posts, or change posting flags.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
X_CONFIG_PATH = ROOT / "data" / "x_api_config.json"
AUTO_PLAN_PATH = ROOT / "data" / "villain_auto_post_plan.json"
HISTORY_PATH = ROOT / "data" / "villain_post_history.json"
FINAL_SAFETY_REPORT_PATH = ROOT / "reports" / "villain_final_safety_check.md"
PREFLIGHT_REPORT_PATH = ROOT / "reports" / "x_api_preflight_check.md"
QUEUE_PREVIEW_REPORT_PATH = ROOT / "reports" / "villain_queue_preview.md"
DASHBOARD_PATH = ROOT / "reports" / "villain_dashboard.md"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def count_payloads(payloads: list[dict], key_path: tuple[str, ...], expected: object) -> int:
    count = 0
    for payload in payloads:
        current: object = payload
        for key in key_path:
            if not isinstance(current, dict):
                current = None
                break
            current = current.get(key)
        if current == expected:
            count += 1
    return count


def queue_summary(queue: list[dict]) -> dict:
    waiting_for_image = sum(
        1 for item in queue if item.get("status") == "waiting_for_image"
    )
    approved = sum(1 for item in queue if item.get("status") == "approved")
    missing_image = sum(
        1 for item in queue if not item.get("image", {}).get("file_path_or_url")
    )
    blocked = sum(
        1
        for item in queue
        if item.get("status") != "approved"
        or not item.get("image", {}).get("file_path_or_url")
        or item.get("checks", {}).get("passcode_confirmed") != "pass"
    )
    return {
        "waiting_for_image": waiting_for_image,
        "approved": approved,
        "missing_image": missing_image,
        "blocked": blocked,
        "preview_exists": QUEUE_PREVIEW_REPORT_PATH.exists(),
    }


def final_safety_status() -> str:
    if not FINAL_SAFETY_REPORT_PATH.exists():
        return "BLOCKED"
    text = FINAL_SAFETY_REPORT_PATH.read_text(encoding="utf-8")
    if "Overall judgment: `BLOCKED`" in text:
        return "BLOCKED"
    return "UNKNOWN"


def preflight_status() -> str:
    if not PREFLIGHT_REPORT_PATH.exists():
        return "NOT_READY"
    text = PREFLIGHT_REPORT_PATH.read_text(encoding="utf-8")
    if "preflight_status: `NOT_READY`" in text:
        return "NOT_READY"
    return "UNKNOWN"


def next_actions(payloads: list[dict], queue_count: int) -> list[str]:
    actions = []
    if queue_count == 0:
        actions.append("Generate a queue draft before dry-run preview.")
    if any(not payload.get("image_path") for payload in payloads):
        actions.append("Attach image/poster and confirm source rights.")
    if any(
        payload.get("checks_snapshot", {}).get("passcode_confirmed") != "pass"
        for payload in payloads
    ):
        actions.append("Confirm Passcode in the final footer.")
    if any(
        payload.get("safety", {}).get("dry_run_only") is True for payload in payloads
    ):
        actions.append("Keep dry-run blocking active until an explicit future enable phase.")
    actions.append("Do not connect X API or add credentials in this phase.")
    return actions


def main() -> None:
    queue_db = read_json(QUEUE_PATH)
    payload_db = read_json(PAYLOADS_PATH)
    x_config = read_json(X_CONFIG_PATH)
    auto_plan = read_json(AUTO_PLAN_PATH)
    history_db = read_json(HISTORY_PATH)

    queue = queue_db.get("queue", [])
    payloads = payload_db.get("payloads", [])
    connection = x_config.get("connection", {})
    guard = x_config.get("posting_guard", {})
    policy = auto_plan.get("global_policy", {})

    approved_count = count_payloads(
        payloads, ("approval", "human_confirm_received"), True
    )
    blocked_count = len(payloads)
    postable_count = count_payloads(payloads, ("safety", "postable_judgment"), True)
    queue_counts = queue_summary(queue)
    live_posting = "DISABLED"
    final_status = final_safety_status()
    x_preflight_status = preflight_status()
    generated_at = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Villain Posting OS Dashboard",
        "",
        f"- Generated at: `{generated_at}`",
        f"- live posting: `{live_posting}`",
        f"- final safety: `{final_status}`",
        f"- x api preflight: `{x_preflight_status}`",
        "",
        "## Core Status",
        "",
        f"- `auto_post_enabled`: `{bool_text(guard.get('auto_post_enabled', False))}`",
        f"- `manual_approval_required`: `{bool_text(guard.get('manual_approval_required', True))}`",
        f"- `dry_run_only`: `{bool_text(connection.get('dry_run_only', True))}`",
        f"- `api_connected`: `{bool_text(connection.get('api_connected', False))}`",
        f"- `live_post_blocked`: `{bool_text(any(payload.get('safety', {}).get('live_post_blocked', True) for payload in payloads) or True)}`",
        f"- `postable_judgment`: `{bool_text(postable_count > 0)}`",
        f"- `posting_execution_allowed`: `{bool_text(policy.get('posting_execution_allowed', False))}`",
        "",
        "## Counts",
        "",
        f"- Queue items: `{len(queue)}`",
        f"- Queue waiting_for_image: `{queue_counts['waiting_for_image']}`",
        f"- Queue approved: `{queue_counts['approved']}`",
        f"- Queue missing image: `{queue_counts['missing_image']}`",
        f"- Queue blocked: `{queue_counts['blocked']}`",
        f"- Queue preview report: `{'exists' if queue_counts['preview_exists'] else 'missing'}`",
        f"- Dry-run payloads: `{len(payloads)}`",
        f"- Human-approved payloads: `{approved_count}`",
        f"- BLOCKED payloads: `{blocked_count}`",
        f"- History records: `{len(history_db.get('history', []))}`",
        "",
        "## X API",
        "",
        f"- `preflight_status`: `{x_preflight_status}`",
        f"- `api_connected`: `{bool_text(connection.get('api_connected', False))}`",
        f"- `login_required`: `{bool_text(connection.get('login_required', False))}`",
        f"- `dry_run_only`: `{bool_text(connection.get('dry_run_only', True))}`",
        "- Credentials: `environment variable names only`",
        "- Live API actions: `blocked`",
        "",
        "## Queue",
        "",
    ]

    if not queue:
        lines.append("- No queue items.")
    else:
        for item in queue:
            lines.append(
                f"- `{item.get('queue_id', '')}`: status `{item.get('status', '')}`, type `{item.get('post_type', '')}`"
            )

    lines.extend(["", "## Dry Run Payloads", ""])
    if not payloads:
        lines.append("- No dry-run payloads.")
    else:
        for payload in payloads:
            lines.append(
                f"- `{payload.get('payload_id', '')}`: status `{payload.get('status', '')}`, approved `{bool_text(payload.get('approval', {}).get('human_confirm_received', False))}`, postable `false`"
            )

    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in next_actions(payloads, len(queue)))
    lines.extend(
        [
            "",
            "## Safety Note",
            "",
            "This dashboard is read-only. It does not log in to X, authenticate with an API, upload media, publish posts, or change posting flags.",
            "",
        ]
    )

    DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote dashboard report to {DASHBOARD_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
