#!/usr/bin/env python3
"""Build final human review report for Villain posts without posting.

The script reviews queue items whose status is ready_for_human_post_review and
outputs a Markdown report. It does not mutate queue data, read .env, call X API,
upload media, create tweets, or execute any live posting action.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
GENERATED_PATH = ROOT / "data" / "villain_generated_candidates.json"
METRICS_PATH = ROOT / "data" / "villain_post_metrics.json"
REPORT_PATH = ROOT / "reports" / "villain_final_review.md"
TARGET_STATUS = "ready_for_human_post_review"
QUALITY_THRESHOLD = 80


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def text_preview(text: str, limit: int = 180) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def selected_image_path(item: dict[str, Any]) -> str:
    image = item.get("image", {})
    for key in ("selected_image_path", "selected_image", "file_path_or_url"):
        value = item.get(key) or image.get(key)
        if value:
            return value
    return ""


def duplicate_signal(item: dict[str, Any], metrics_record: dict[str, Any]) -> bool:
    if metrics_record.get("already_posted"):
        return True
    if metrics_record.get("post_url"):
        return True
    execution = item.get("post_execution", {})
    return bool(execution.get("posted_url"))


def build_review_item(
    item: dict[str, Any],
    generated_candidates: dict[str, dict[str, Any]],
    metrics_records: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    candidate_id = item.get("source_generated_candidate_id", "")
    candidate = generated_candidates.get(candidate_id, {})
    metrics_record = metrics_records.get(item.get("queue_id", ""), {})
    scoring = item.get("scoring", {})
    quality_score = candidate.get("quality_prediction", scoring.get("score"))
    villain_score = candidate.get("villain_score", metrics_record.get("villain_score"))
    risk = candidate.get("risk_prediction", scoring.get("risk_level", metrics_record.get("risk")))
    selected_image = selected_image_path(item)
    image_selected = bool(selected_image)
    already_posted = bool(metrics_record.get("already_posted") or item.get("post_execution", {}).get("posted_url"))
    is_duplicate = duplicate_signal(item, metrics_record)
    block_reasons: list[str] = []

    if risk == "high":
        block_reasons.append("risk_high")
    if already_posted:
        block_reasons.append("already_posted")
    if not image_selected:
        block_reasons.append("image_selected_false")
    if quality_score is None:
        block_reasons.append("quality_score_missing")
    elif quality_score < QUALITY_THRESHOLD:
        block_reasons.append(f"score_below_{QUALITY_THRESHOLD}")

    final_review_status = "BLOCK" if block_reasons else "APPROVE_TO_POST"
    recommendation = final_review_status
    final_reason = ", ".join(block_reasons) if block_reasons else "all_final_review_conditions_passed"

    return {
        "candidate_id": candidate_id,
        "queue_id": item.get("queue_id", ""),
        "text_preview": text_preview(item.get("text", "")),
        "selected_image": selected_image,
        "quality_score": quality_score,
        "villain_score": villain_score,
        "risk": risk,
        "already_posted": already_posted,
        "duplicate_signal": is_duplicate,
        "image_selected": image_selected,
        "recommendation": recommendation,
        "final_reason": final_reason,
        "human_review_ready": final_review_status == "APPROVE_TO_POST",
        "final_review_status": final_review_status,
    }


def write_report(review_items: list[dict[str, Any]], total_targets: int) -> None:
    lines = [
        "# Villain Final Review",
        "",
        f"- Generated at: `{now_iso()}`",
        "- status: `DRY_RUN_ONLY`",
        "- queue mutation: `NOT_EXECUTED`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        f"- target_status: `{TARGET_STATUS}`",
        f"- target_count: `{total_targets}`",
        f"- human_review_ready_count: `{sum(1 for item in review_items if item.get('human_review_ready'))}`",
        "",
    ]
    if not review_items:
        lines.extend(
            [
                "## No Review Targets",
                "",
                f"- final_review_status: `BLOCK`",
                f"- final_reason: no queue items with status `{TARGET_STATUS}`",
                "",
            ]
        )
    for item in review_items:
        lines.extend(
            [
                f"## `{item.get('queue_id')}`",
                "",
                f"- candidate_id: `{item.get('candidate_id')}`",
                f"- selected_image: `{item.get('selected_image')}`",
                f"- quality_score: `{item.get('quality_score')}`",
                f"- villain_score: `{item.get('villain_score')}`",
                f"- risk: `{item.get('risk')}`",
                f"- already_posted: `{str(item.get('already_posted')).lower()}`",
                f"- duplicate_signal: `{str(item.get('duplicate_signal')).lower()}`",
                f"- image_selected: `{str(item.get('image_selected')).lower()}`",
                f"- recommendation: `{item.get('recommendation')}`",
                f"- human_review_ready: `{str(item.get('human_review_ready')).lower()}`",
                f"- final_review_status: `{item.get('final_review_status')}`",
                f"- final_reason: {item.get('final_reason')}",
                "",
                "### Text Preview",
                "",
                "```text",
                item.get("text_preview", ""),
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
    generated_candidates = generated_by_id(generated_db)
    metrics_records = metrics_by_queue_id(metrics_db)
    targets = [
        item for item in queue_db.get("queue", [])
        if item.get("status") == TARGET_STATUS
    ]
    review_items = [
        build_review_item(item, generated_candidates, metrics_records)
        for item in targets
    ]
    write_report(review_items, len(targets))
    print("status=DRY_RUN_ONLY")
    print("queue_mutation=NOT_EXECUTED")
    print(f"target_status={TARGET_STATUS}")
    print(f"target_count={len(targets)}")
    print(f"human_review_ready_count={sum(1 for item in review_items if item.get('human_review_ready'))}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
