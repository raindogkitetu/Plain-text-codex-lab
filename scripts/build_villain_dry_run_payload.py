#!/usr/bin/env python3
"""Build Villain dry-run preview payloads from the local post queue.

This script never logs in to X, never authenticates with an API, never uploads
media, and never publishes or schedules a post. It only reads JSON files and
writes a local dry-run preview JSON file.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
CONFIG_PATH = ROOT / "data" / "x_api_config.json"
OUTPUT_PATH = ROOT / "data" / "villain_dry_run_payloads.json"

ALLOWED_QUEUE_STATUSES = {"waiting_for_image", "approved"}


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def require_safe_config(config: dict) -> None:
    connection = config.get("connection", {})
    guard = config.get("posting_guard", {})

    required = {
        "api_connected": connection.get("api_connected") is False,
        "dry_run_only": connection.get("dry_run_only") is True,
        "auto_post_enabled": guard.get("auto_post_enabled") is False,
        "manual_approval_required": guard.get("manual_approval_required") is True,
        "block_if_dry_run_only": guard.get("block_if_dry_run_only") is True,
        "write_action_kill_switch": guard.get("write_action_kill_switch") is True,
    }

    failed = [name for name, ok in required.items() if not ok]
    if failed:
        raise SystemExit(f"Unsafe X API dry-run config: {', '.join(failed)}")


def build_payload(queue_item: dict, config: dict, index: int, created_at: str) -> dict:
    date_part = created_at[:10].replace("-", "")
    image = queue_item.get("image", {})
    approval = queue_item.get("approval", {})
    checks = queue_item.get("checks", {})
    connection = config.get("connection", {})
    guard = config.get("posting_guard", {})

    image_path = image.get("file_path_or_url") or None
    approved_for_live_post = (
        queue_item.get("status") == "approved"
        and checks.get("image_attached") == "pass"
        and checks.get("passcode_confirmed") == "pass"
        and checks.get("prohibited_content_check") == "pass"
        and checks.get("skip_day_policy") is False
        and checks.get("daisho_approval") == "approved"
        and guard.get("write_action_kill_switch") is False
        and connection.get("dry_run_only") is False
        and guard.get("auto_post_enabled") is True
    )

    return {
        "payload_id": f"vln-dryrun-{date_part}-{index:03d}",
        "source_queue_id": queue_item.get("queue_id", ""),
        "status": "dry_run_preview_ready",
        "post_type": queue_item.get("post_type", ""),
        "queue_status": queue_item.get("status", ""),
        "candidate_role": queue_item.get("candidate_role", ""),
        "caption": queue_item.get("text", ""),
        "image_path": image_path,
        "image": {
            "required": image.get("required", True),
            "ready": bool(image_path),
            "status": image.get("status", "waiting_for_image"),
            "poster_concept": image.get("poster_concept", ""),
            "rights_notes": image.get("rights_notes", ""),
        },
        "approval": {
            "manual_approval_required": approval.get("manual_approval_required", True),
            "human_confirm_text_required": guard.get(
                "require_human_confirm_text", "POST_APPROVED"
            ),
            "daisho_approval_status": checks.get("daisho_approval", "unchecked"),
            "approved_for_live_post": approved_for_live_post,
        },
        "checks_snapshot": {
            "source_url_confirmed": checks.get("source_url_confirmed", "unchecked"),
            "image_attached": checks.get("image_attached", "unchecked"),
            "passcode_confirmed": checks.get("passcode_confirmed", "unchecked"),
            "prohibited_content_check": checks.get(
                "prohibited_content_check", "unchecked"
            ),
            "skip_day_policy": checks.get("skip_day_policy", False),
        },
        "safety": {
            "dry_run_only": connection.get("dry_run_only", True),
            "api_connected": connection.get("api_connected", False),
            "write_action_kill_switch": guard.get("write_action_kill_switch", True),
            "live_post_blocked": True,
            "auto_post_enabled": guard.get("auto_post_enabled", False),
            "postable_judgment": False,
            "blocked_reason": "Dry-run preview only. No X login, API auth, media upload, publish, or scheduling is performed.",
        },
        "created_at": created_at,
    }


def main() -> None:
    config = read_json(CONFIG_PATH)
    require_safe_config(config)
    queue_db = read_json(QUEUE_PATH)
    created_at = datetime.now(timezone.utc).isoformat()

    candidates = [
        item
        for item in queue_db.get("queue", [])
        if item.get("status") in ALLOWED_QUEUE_STATUSES
    ]

    payloads = [
        build_payload(item, config, index, created_at)
        for index, item in enumerate(candidates, start=1)
    ]

    output = {
        "db_name": "Villain Dry Run Payload DB",
        "version": "0.1.0",
        "status": "dry_run_only",
        "source_queue_path": "data/villain_post_queue.json",
        "x_api_config_path": "data/x_api_config.json",
        "posting_execution_allowed": False,
        "api_connection_allowed": False,
        "payload_count": len(payloads),
        "generated_at": created_at,
        "payloads": payloads,
    }

    write_json(OUTPUT_PATH, output)
    print(f"wrote {len(payloads)} dry-run payload(s) to {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
