#!/usr/bin/env python3
"""Dry-run safe post executor for Villain.

This script only evaluates whether a post would be safe to execute. It never
uploads media, creates tweets, calls X API write endpoints, reads .env, or
executes live posting.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
GENERATED_PATH = ROOT / "data" / "villain_generated_candidates.json"
METRICS_PATH = ROOT / "data" / "villain_post_metrics.json"
X_API_CONFIG_PATH = ROOT / "data" / "x_api_config.json"
FINAL_REVIEW_PATH = ROOT / "reports" / "villain_final_review.md"
REPORT_PATH = ROOT / "reports" / "villain_safe_post_executor.md"
APPROVED_STATUS = "APPROVE_TO_POST"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def queue_by_id(queue_db: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item.get("queue_id", ""): item
        for item in queue_db.get("queue", [])
        if item.get("queue_id")
    }


def generated_by_id(generated_db: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        candidate.get("candidate_id", ""): candidate
        for candidate in generated_db.get("candidates", [])
        if candidate.get("candidate_id")
    }


def metrics_by_queue_id(metrics_db: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        record.get("source_queue_id", ""): record
        for record in metrics_db.get("records", [])
        if record.get("source_queue_id")
    }


def parse_final_review_targets(report_text: str) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in report_text.splitlines():
        match = re.match(r"^## `([^`]+)`", line)
        if match:
            if current:
                targets.append(current)
            current = {"queue_id": match.group(1)}
            continue
        if current is None:
            continue
        field = re.match(r"^- ([a-zA-Z0-9_]+): `?([^`]+)`?", line)
        if field:
            key, value = field.group(1), field.group(2).strip()
            current[key] = value
    if current:
        targets.append(current)
    return [target for target in targets if target.get("final_review_status") == APPROVED_STATUS]


def selected_image_path(queue_item: dict[str, Any], final_target: dict[str, Any]) -> str:
    image = queue_item.get("image", {})
    for value in (
        image.get("selected_image_path"),
        image.get("selected_image"),
        image.get("file_path_or_url"),
        queue_item.get("selected_image_path"),
        final_target.get("selected_image"),
    ):
        if value:
            return value
    return ""


def boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return False


def text_preview(text: str, limit: int = 180) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def evaluate_target(
    final_target: dict[str, Any],
    queue_items: dict[str, dict[str, Any]],
    generated_candidates: dict[str, dict[str, Any]],
    metric_records: dict[str, dict[str, Any]],
    x_api_config: dict[str, Any],
) -> dict[str, Any]:
    queue_id = final_target.get("queue_id", "")
    queue_item = queue_items.get(queue_id, {})
    candidate_id = final_target.get("candidate_id", "") or queue_item.get("source_generated_candidate_id", "")
    candidate = generated_candidates.get(candidate_id, {})
    metrics_record = metric_records.get(queue_id, {})
    image_path = selected_image_path(queue_item, final_target)
    risk = (
        candidate.get("risk_prediction")
        or queue_item.get("scoring", {}).get("risk_level")
        or metrics_record.get("risk")
        or final_target.get("risk")
    )
    already_posted = bool(
        metrics_record.get("already_posted")
        or metrics_record.get("post_url")
        or queue_item.get("post_execution", {}).get("posted_url")
    )
    failed_conditions: list[str] = []

    human_confirmed = boolish(queue_item.get("approval", {}).get("human_confirmed")) or boolish(
        queue_item.get("approval", {}).get("approved_by_human")
    )
    approved_for_live_post = boolish(queue_item.get("approval", {}).get("approved_for_live_post"))
    write_action_kill_switch = boolish(
        x_api_config.get("posting_guard", {}).get("write_action_kill_switch", True)
    )
    passcode_ok = boolish(queue_item.get("passcode", {}).get("confirmed")) or (
        queue_item.get("checks", {}).get("passcode_confirmed") == "pass"
    )
    selected_image_exists = bool(image_path) and Path(image_path).exists()

    if not queue_item:
        failed_conditions.append("queue_item_not_found")
    if not human_confirmed:
        failed_conditions.append("human_confirmed_false")
    if not approved_for_live_post:
        failed_conditions.append("approved_for_live_post_false")
    if write_action_kill_switch:
        failed_conditions.append("write_action_kill_switch_true")
    if not passcode_ok:
        failed_conditions.append("passcode_ok_false")
    if not selected_image_exists:
        failed_conditions.append("selected_image_exists_false")
    if already_posted:
        failed_conditions.append("already_posted_true")
    if risk == "high":
        failed_conditions.append("risk_high")

    safe_post_status = "SAFE_TO_POST" if not failed_conditions else "BLOCK"
    text = queue_item.get("text") or candidate.get("text") or final_target.get("text_preview", "")
    return {
        "queue_id": queue_id,
        "candidate_id": candidate_id,
        "text_preview": text_preview(text),
        "selected_image": image_path,
        "safe_post_status": safe_post_status,
        "failed_conditions": failed_conditions,
        "would_execute_actions": [
            "upload_media(image_path)",
            "create_tweet(text)",
        ],
        "conditions": {
            "human_confirmed": human_confirmed,
            "approved_for_live_post": approved_for_live_post,
            "write_action_kill_switch": write_action_kill_switch,
            "passcode_ok": passcode_ok,
            "selected_image_exists": selected_image_exists,
            "already_posted": already_posted,
            "risk": risk,
        },
    }


def write_report(results: list[dict[str, Any]]) -> None:
    lines = [
        "# Villain Safe Post Executor",
        "",
        f"- Generated at: `{now_iso()}`",
        "- status: `DRY_RUN_ONLY`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        "- would_execute_actions: `DISPLAY_ONLY`",
        f"- targets_with_final_review_approve: `{len(results)}`",
        "",
    ]
    if not results:
        lines.extend(
            [
                "## No Executor Targets",
                "",
                "- safe_post_status: `BLOCK`",
                "- failed_conditions: `no_final_review_approve_targets`",
                "",
            ]
        )
    for result in results:
        lines.extend(
            [
                f"## `{result.get('queue_id')}`",
                "",
                f"- candidate_id: `{result.get('candidate_id')}`",
                f"- selected_image: `{result.get('selected_image')}`",
                f"- safe_post_status: `{result.get('safe_post_status')}`",
                f"- failed_conditions: `{', '.join(result.get('failed_conditions', [])) if result.get('failed_conditions') else 'none'}`",
                "",
                "### Conditions",
                "",
            ]
        )
        for key, value in result.get("conditions", {}).items():
            lines.append(f"- {key}: `{value}`")
        lines.extend(
            [
                "",
                "### Would Execute Actions",
                "",
            ]
        )
        for action in result.get("would_execute_actions", []):
            lines.append(f"- `{action}`")
        lines.extend(
            [
                "",
                "### Text Preview",
                "",
                "```text",
                result.get("text_preview", ""),
                "```",
                "",
            ]
        )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    queue_db = read_json(QUEUE_PATH)
    generated_db = read_json(GENERATED_PATH)
    metrics_db = read_json(METRICS_PATH)
    x_api_config = read_json(X_API_CONFIG_PATH)
    final_targets = parse_final_review_targets(read_text(FINAL_REVIEW_PATH))
    queue_items = queue_by_id(queue_db)
    generated_candidates = generated_by_id(generated_db)
    metric_records = metrics_by_queue_id(metrics_db)
    results = [
        evaluate_target(target, queue_items, generated_candidates, metric_records, x_api_config)
        for target in final_targets
    ]
    write_report(results)
    print("status=DRY_RUN_ONLY")
    print("live_posting=NOT_EXECUTED")
    print("x_api_write=NOT_USED")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"targets={len(results)}")
    print(f"safe_to_post={sum(1 for result in results if result.get('safe_post_status') == 'SAFE_TO_POST')}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
