#!/usr/bin/env python3
"""Build a manual posting plan for Villain dry-run payloads.

This script only creates a human-readable checklist. It does not read .env,
connect to X, upload media, publish posts, schedule posts, or change posting
flags.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
VALIDATION_PATH = ROOT / "data" / "villain_dry_run_validation.json"
X_CONFIG_PATH = ROOT / "data" / "x_api_config.json"
PRE_POST_REPORT_PATH = ROOT / "reports" / "villain_pre_post_check.md"
REPORT_PATH = ROOT / "reports" / "villain_manual_post_plan.md"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def bool_text(value: object) -> str:
    return "true" if value is True else "false"


def final_status(validation: dict, x_config: dict) -> str:
    guard = x_config.get("posting_guard", {})
    connection = x_config.get("connection", {})
    if guard.get("write_action_kill_switch") is True:
        return "BLOCKED"
    if connection.get("dry_run_only") is True:
        return "READY_DRY_RUN_ONLY"
    if validation.get("global_postable_judgment") is True:
        return "READY"
    return "BLOCKED"


def validation_for_payload(validation: dict, payload_id: str) -> dict:
    for result in validation.get("results", []):
        if result.get("payload_id") == payload_id:
            return result
    return {}


def checklist_lines(kill_switch: bool) -> list[str]:
    return [
        "- [ ] 本文確認",
        "- [ ] 禁止語・誤字確認",
        "- [ ] 投稿先アカウント確認",
        "- [ ] 画像有無確認",
        "- [ ] 予約投稿ではない確認",
        f"- [ ] kill switch true の間は投稿不可: `{bool_text(kill_switch)}`",
    ]


def render_payload(payload: dict, validation_result: dict, final: str, kill_switch: bool) -> str:
    approval = payload.get("approval", {})
    safety = payload.get("safety", {})
    checks = payload.get("checks_snapshot", {})
    caption = payload.get("caption", "")
    blockers = validation_result.get("blockers", [])
    failures = validation_result.get("failures", [])

    lines = [
        f"## Manual Plan For `{payload.get('payload_id', '')}`",
        "",
        f"- FINAL_STATUS: `{final}`",
        f"- post_type: `{payload.get('post_type', '')}`",
        f"- source_queue_id: `{payload.get('source_queue_id', '')}`",
        f"- dry-run validator: `{validation_result.get('validation_status', 'missing')}`",
        f"- manual approval: `{bool_text(approval.get('human_confirm_received'))}`",
        f"- approved_for_live_post: `{bool_text(approval.get('approved_for_live_post'))}`",
        f"- write_action_kill_switch: `{bool_text(kill_switch)}`",
        f"- postable_judgment: `{bool_text(safety.get('postable_judgment'))}`",
        f"- image_path: `{payload.get('image_path') or 'missing'}`",
        f"- image check: `{checks.get('image_attached', 'unchecked')}`",
        f"- passcode check: `{checks.get('passcode_confirmed', 'unchecked')}`",
        "",
        "### 投稿候補本文",
        "",
        "```text",
        caption,
        "```",
        "",
        "### 人間チェックリスト",
        "",
    ]
    lines.extend(checklist_lines(kill_switch))
    lines.extend(["", "### BLOCK / 注意点", ""])
    if failures or blockers:
        lines.extend(f"- {item}" for item in failures + blockers)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "### 手動運用メモ",
            "",
            "- このレポートは投稿実行ではない。",
            "- kill switch が true の間は、手動投稿も不可として扱う。",
            "- 画像、投稿先、本文を人間が確認するまで先へ進めない。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    payload_db = read_json(PAYLOADS_PATH)
    validation = read_json(VALIDATION_PATH)
    x_config = read_json(X_CONFIG_PATH)
    guard = x_config.get("posting_guard", {})
    connection = x_config.get("connection", {})
    payloads = payload_db.get("payloads", [])
    generated_at = datetime.now(timezone.utc).isoformat()
    kill_switch = guard.get("write_action_kill_switch") is True
    final = final_status(validation, x_config)

    lines = [
        "# Villain Manual Post Plan",
        "",
        f"- Generated at: `{generated_at}`",
        f"- FINAL_STATUS: `{final}`",
        "- Live posting: `DISABLED`",
        "- X API write actions: `NOT USED`",
        "- This is a manual checklist only.",
        "",
        "## Current Gates",
        "",
        f"- `manual_approval_required`: `{bool_text(guard.get('manual_approval_required'))}`",
        f"- `approved_for_live_post`: `false`",
        f"- `write_action_kill_switch`: `{bool_text(kill_switch)}`",
        f"- `dry_run_only`: `{bool_text(connection.get('dry_run_only'))}`",
        f"- `auto_post_enabled`: `{bool_text(guard.get('auto_post_enabled'))}`",
        f"- `api_connected`: `{bool_text(connection.get('api_connected'))}`",
        f"- pre-post check report: `{'exists' if PRE_POST_REPORT_PATH.exists() else 'missing'}`",
        "",
    ]

    if payloads:
        for payload in payloads:
            result = validation_for_payload(validation, payload.get("payload_id", ""))
            lines.append(render_payload(payload, result, final, kill_switch))
    else:
        lines.extend(["## Manual Plan", "", "No dry-run payloads found.", ""])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote manual post plan to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
