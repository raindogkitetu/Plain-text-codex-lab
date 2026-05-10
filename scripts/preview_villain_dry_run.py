#!/usr/bin/env python3
"""Render Villain dry-run payloads into a human-readable Markdown report.

This script is report-only. It does not log in to X, authenticate with an API,
upload media, publish posts, schedule posts, or change any safety flags.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
REPORT_PATH = ROOT / "reports" / "villain_dry_run_preview.md"


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def nullable_text(value: object) -> str:
    return "null" if value is None else str(value)


def collect_blockers(payload: dict) -> list[str]:
    blockers: list[str] = []
    safety = payload.get("safety", {})
    approval = payload.get("approval", {})
    checks = payload.get("checks_snapshot", {})

    if safety.get("dry_run_only") is True:
        blockers.append("dry_run_only is true")
    if safety.get("api_connected") is False:
        blockers.append("api_connected is false")
    if not payload.get("image_path"):
        blockers.append("image_path is null")
    if (
        approval.get("manual_approval_required") is True
        and approval.get("human_confirm_received") is not True
    ):
        blockers.append("manual approval is required")
    if approval.get("daisho_approval_status") != "approved":
        blockers.append("daisho approval is not approved")
    if checks.get("image_attached") != "pass":
        blockers.append("image_attached is not pass")
    if checks.get("passcode_confirmed") != "pass":
        blockers.append("passcode_confirmed is not pass")
    if checks.get("prohibited_content_check") != "pass":
        blockers.append("prohibited_content_check is not pass")
    if checks.get("skip_day_policy") is True:
        blockers.append("skip_day_policy is true")
    if safety.get("live_post_blocked") is True:
        blockers.append("live_post_blocked is true")
    if safety.get("postable_judgment") is False:
        blockers.append("postable_judgment is false")

    return blockers


def collect_next_actions(payload: dict) -> list[str]:
    actions: list[str] = []
    approval = payload.get("approval", {})
    checks = payload.get("checks_snapshot", {})

    if not payload.get("image_path"):
        actions.append("Attach an image or poster and confirm its source/rights.")
    if checks.get("passcode_confirmed") != "pass":
        actions.append("Confirm the Passcode in the final footer.")
    if approval.get("daisho_approval_status") != "approved":
        actions.append("Get explicit Daisho approval with POST_APPROVED.")
    if approval.get("approved_for_live_post") is True:
        actions.append("Approval marker is recorded. Keep dry-run blocking active.")
    if checks.get("prohibited_content_check") != "pass":
        actions.append("Resolve prohibited content check before any approval.")
    if not actions:
        actions.append("Keep in dry-run until live-posting is explicitly enabled.")
    return actions


def render_payload(payload: dict, index: int) -> str:
    approval = payload.get("approval", {})
    safety = payload.get("safety", {})
    blockers = collect_blockers(payload)
    actions = collect_next_actions(payload)

    lines = [
        f"## Payload {index}: `{payload.get('payload_id', '')}`",
        "",
        f"- `payload_id`: `{payload.get('payload_id', '')}`",
        f"- `source_queue_id`: `{payload.get('source_queue_id', '')}`",
        f"- `status`: `{payload.get('status', '')}`",
        f"- `post_type`: `{payload.get('post_type', '')}`",
        f"- `image_path`: `{nullable_text(payload.get('image_path'))}`",
        "- `postable`: `false`",
        "",
        "### Caption",
        "",
        "```text",
        payload.get("caption", ""),
        "```",
        "",
        "### Approval",
        "",
        f"- `manual_approval_required`: `{bool_text(approval.get('manual_approval_required', True))}`",
        f"- `human_confirm_text_required`: `{approval.get('human_confirm_text_required', 'POST_APPROVED')}`",
        f"- `human_confirm_received`: `{bool_text(approval.get('human_confirm_received', False))}`",
        f"- `daisho_approval_status`: `{approval.get('daisho_approval_status', 'unchecked')}`",
        f"- `approved_for_live_post`: `{bool_text(approval.get('approved_for_live_post', False))}`",
        f"- `approved_at`: `{nullable_text(approval.get('approved_at'))}`",
        "",
        "### Safety",
        "",
        f"- `dry_run_only`: `{bool_text(safety.get('dry_run_only', True))}`",
        f"- `api_connected`: `{bool_text(safety.get('api_connected', False))}`",
        f"- `live_post_blocked`: `{bool_text(safety.get('live_post_blocked', True))}`",
        f"- `auto_post_enabled`: `{bool_text(safety.get('auto_post_enabled', False))}`",
        f"- `postable_judgment`: `{bool_text(safety.get('postable_judgment', False))}`",
        "",
        "### 投稿不可理由",
        "",
    ]

    lines.extend(f"- {blocker}" for blocker in blockers)
    lines.extend(["", "### 次に必要な作業", ""])
    lines.extend(f"- {action}" for action in actions)
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    payload_db = read_json(PAYLOADS_PATH)
    payloads = payload_db.get("payloads", [])
    generated_at = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Villain Dry Run Preview",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Source: `{PAYLOADS_PATH.relative_to(ROOT)}`",
        f"- Payload count: `{len(payloads)}`",
        "- Live posting: `blocked`",
        "- Postable judgment: `false`",
        "",
        "> This report is preview-only. It does not log in to X, authenticate with an API, upload media, publish posts, or schedule posts.",
        "",
    ]

    if not payloads:
        lines.extend(["No dry-run payloads found.", ""])
    else:
        for index, payload in enumerate(payloads, start=1):
            lines.append(render_payload(payload, index))

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote dry-run preview report to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
