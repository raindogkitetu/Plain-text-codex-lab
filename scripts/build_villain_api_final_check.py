#!/usr/bin/env python3
"""Build the final API image post readiness dry-run report.

This script is read/report only. It does not read .env, upload media, create
tweets, call X API write actions, or change posting flags.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
IMAGE_QUEUE_PATH = ROOT / "data" / "villain_image_queue.json"
API_RULES_PATH = ROOT / "data" / "villain_api_post_rules.json"
IMAGE_RULES_PATH = ROOT / "data" / "villain_image_post_rules.json"
REPORT_PATH = ROOT / "reports" / "villain_api_final_check.md"

PLACEHOLDER_IMAGE_PATH = "PLACEHOLDER_IMAGE_PATH_REQUIRES_HUMAN_REPLACEMENT"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def bool_text(value: object) -> str:
    return "true" if value is True else "false"


def selected_images(queue_db: dict) -> list[dict]:
    return [
        item
        for item in queue_db.get("queue", [])
        if item.get("selected_for_post") is True
    ]


def final_status(image_rules: dict) -> str:
    # This phase is readiness-only. Until an explicit unlock happens, stay BLOCKED.
    return "BLOCKED"


def build_checks(
    payload: dict,
    selected: list[dict],
    api_rules: dict,
    image_rules: dict,
) -> list[dict]:
    selected_image = selected[0] if len(selected) == 1 else {}
    approval = payload.get("approval", {})
    safety = payload.get("safety", {})
    api_manual = api_rules.get("manual_state", {})
    image_manual = image_rules.get("manual_state", {})
    image_path = selected_image.get("image_path") or image_manual.get("image_file_path") or PLACEHOLDER_IMAGE_PATH
    placeholder_used = image_path == PLACEHOLDER_IMAGE_PATH
    status = final_status(image_rules)

    return [
        {
            "id": "selected_image_exists",
            "ok": len(selected) == 1 and selected_image.get("image_status") == "approved",
            "actual": f"{len(selected)} selected; status {selected_image.get('image_status', 'missing')}",
            "required": "exactly 1 selected approved image",
        },
        {
            "id": "target_account_confirmed",
            "ok": api_manual.get("target_account") == "@raindog_kitetu"
            and api_manual.get("target_account_confirmed") is True,
            "actual": f"{api_manual.get('target_account', '')}; confirmed {api_manual.get('target_account_confirmed', False)}",
            "required": "@raindog_kitetu confirmed true",
        },
        {
            "id": "image_path_exists",
            "ok": bool(image_path),
            "actual": image_path,
            "required": "image path or placeholder",
        },
        {
            "id": "image_path_not_placeholder",
            "ok": not placeholder_used,
            "actual": "placeholder" if placeholder_used else "real path",
            "required": "real image path before upload",
        },
        {
            "id": "media_upload_ready",
            "ok": image_manual.get("media_upload_ready") is True,
            "actual": image_manual.get("media_upload_ready", False),
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
            "ok": safety.get("write_action_kill_switch") is False,
            "actual": safety.get("write_action_kill_switch", True),
            "required": False,
        },
        {
            "id": "api_final_human_confirmed",
            "ok": api_manual.get("api_final_human_confirmed") is True
            and image_manual.get("api_final_human_confirmed") is True,
            "actual": api_manual.get("api_final_human_confirmed", False)
            and image_manual.get("api_final_human_confirmed", False),
            "required": True,
        },
        {
            "id": "final_status",
            "ok": status == image_rules.get("target_status", "READY_FOR_API_IMAGE_POST"),
            "actual": status,
            "required": image_rules.get("target_status", "READY_FOR_API_IMAGE_POST"),
        },
    ]


def main() -> None:
    payload_db = read_json(PAYLOADS_PATH)
    queue_db = read_json(IMAGE_QUEUE_PATH)
    api_rules = read_json(API_RULES_PATH)
    image_rules = read_json(IMAGE_RULES_PATH)
    payloads = payload_db.get("payloads", [])
    payload = payloads[0] if payloads else {}
    selected = selected_images(queue_db)
    selected_image = selected[0] if len(selected) == 1 else {}
    image_path = (
        selected_image.get("image_path")
        or image_rules.get("manual_state", {}).get("image_file_path")
        or PLACEHOLDER_IMAGE_PATH
    )
    checks = build_checks(payload, selected, api_rules, image_rules)
    blockers = [check["id"] for check in checks if not check["ok"]]
    status = "READY" if not blockers else "BLOCKED"
    generated_at = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Villain API Final Check",
        "",
        f"- Generated at: `{generated_at}`",
        f"- readiness: `{status}`",
        "- phase: `dry-run only`",
        "- create_tweet: `NOT EXECUTED`",
        "- upload_media: `NOT EXECUTED`",
        "- X API write: `NOT USED`",
        "- `.env` read: `NO`",
        "",
        "## Target",
        "",
        "- target account: `@raindog_kitetu`",
        f"- selected image queue_id: `{selected_image.get('queue_id', 'missing')}`",
        f"- selected image mode: `{selected_image.get('image_mode', 'missing')}`",
        f"- planned image path: `{image_path}`",
        "",
        "## 投稿予定本文",
        "",
        "```text",
        payload.get("caption", ""),
        "```",
        "",
        "## 実行予定 create_tweet payload",
        "",
        "```json",
        json.dumps(
            {
                "text": payload.get("caption", ""),
                "media": {
                    "image_path": image_path,
                    "upload_media_not_executed": True,
                },
                "target_account": "@raindog_kitetu",
                "dry_run_only": True,
            },
            ensure_ascii=False,
            indent=2,
        ),
        "```",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        lines.append(
            f"- `{check['id']}`: `{'pass' if check['ok'] else 'fail'}` "
            f"(actual `{check['actual']}`, required `{check['required']}`)"
        )
    lines.extend(["", "## 未達理由", ""])
    lines.extend(f"- {blocker}" for blocker in blockers) if blockers else lines.append("- none")
    lines.extend(
        [
            "",
            "## Rollback Plan",
            "",
            "- If any live-post step is accidentally prepared, stop before execution.",
            "- Keep `write_action_kill_switch=true`.",
            "- Keep `approved_for_live_post=false` until a separate explicit unlock.",
            "- Do not call upload_media or create_tweet.",
            "- If a payload file is generated by mistake, mark it invalidated and do not post.",
            "",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote API final check report to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
