#!/usr/bin/env python3
"""Analyze Villain post metrics without live posting or X API write actions.

This script reads local JSON only, updates derived analysis fields, and writes
a Markdown report. It does not read .env, call X API, upload media, or create
posts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "data" / "villain_post_metrics.json"
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
REPORT_PATH = ROOT / "reports" / "villain_post_analysis.md"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def nonempty_line_count(text: str) -> int:
    return len([line for line in text.splitlines() if line.strip()])


def engagement_rate(record: dict[str, Any]) -> float | None:
    impressions = record.get("impressions")
    if not isinstance(impressions, (int, float)) or impressions <= 0:
        return None
    total = 0
    for key in ("likes", "reposts", "replies", "bookmarks"):
        value = record.get(key)
        if isinstance(value, (int, float)):
            total += value
    return round(total / impressions, 4)


def queue_by_id(queue_db: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item.get("queue_id", ""): item
        for item in queue_db.get("queue", [])
        if item.get("queue_id")
    }


def payload_by_id(payload_db: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        payload.get("payload_id", ""): payload
        for payload in payload_db.get("payloads", [])
        if payload.get("payload_id")
    }


def derive_villain_score(record: dict[str, Any], queue_item: dict[str, Any]) -> int:
    text = record.get("text", "")
    score = 0
    if "Villain" in text or "$villain" in text or "#villain" in text:
        score += 25
    if "#着て稼ぐ" in text:
        score += 20
    if record.get("post_type") in {"ABOUT_WORDING", "APPAREL", "STORE", "THE_POOL"}:
        score += 20
    if record.get("tone_type") == "rough_note_mode":
        score += 20
    if queue_item.get("scoring", {}).get("recommendation") == "do_not_repost":
        score += 0
    else:
        score += 10
    if record.get("image_used"):
        score += 10
    return min(score, 100)


def update_records(metrics_db: dict[str, Any], queue_db: dict[str, Any], payload_db: dict[str, Any]) -> None:
    queue_items = queue_by_id(queue_db)
    payloads = payload_by_id(payload_db)
    now = datetime.now(timezone.utc).isoformat()

    for record in metrics_db.get("records", []):
        text = record.get("text", "")
        queue_item = queue_items.get(record.get("source_queue_id", ""), {})
        payload = payloads.get(record.get("source_payload_id", ""), {})
        scoring = queue_item.get("scoring", {})

        record["text_length"] = len(text)
        record["line_breaks"] = max(len(text.splitlines()) - 1, 0)
        record["nonempty_lines"] = nonempty_line_count(text)
        record["engagement_rate"] = engagement_rate(record)
        record["quality_score"] = scoring.get("score")
        record["risk"] = scoring.get("risk_level")
        record["villain_score"] = derive_villain_score(record, queue_item)
        record["analysis_status"] = "hypothesis_only" if record.get("metrics_status") == "manual_pending" else "metrics_available"
        record["already_posted"] = bool(payload.get("posted_url") or payload.get("api_image_posted"))
        record["analysis_updated_at"] = now

    metrics_db["updated_at"] = now


def fmt(value: Any) -> str:
    if value is None:
        return "`manual_pending`"
    if isinstance(value, bool):
        return f"`{str(value).lower()}`"
    return f"`{value}`"


def write_report(metrics_db: dict[str, Any]) -> None:
    lines = [
        "# Villain Post Analysis",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "- status: `ANALYSIS_ONLY`",
        "- live posting: `NOT EXECUTED`",
        "- X API write: `NOT USED`",
        "- upload_media: `NOT EXECUTED`",
        "- create_tweet: `NOT EXECUTED`",
        "- metrics source: `manual_or_read_only_later`",
        "",
    ]

    for record in metrics_db.get("records", []):
        lines.extend(
            [
                f"## {record.get('post_id', '')}",
                "",
                f"- post_url: {record.get('post_url', '')}",
                f"- posted_at: `{record.get('posted_at', '')}`",
                f"- post_type: `{record.get('post_type', '')}`",
                f"- tone_type: `{record.get('tone_type', '')}`",
                f"- image_type: `{record.get('image_type', '')}`",
                f"- image_used: {fmt(record.get('image_used'))}",
                f"- impressions: {fmt(record.get('impressions'))}",
                f"- likes: {fmt(record.get('likes'))}",
                f"- reposts: {fmt(record.get('reposts'))}",
                f"- replies: {fmt(record.get('replies'))}",
                f"- bookmarks: {fmt(record.get('bookmarks'))}",
                f"- engagement_rate: {fmt(record.get('engagement_rate'))}",
                f"- text_length: `{record.get('text_length')}`",
                f"- line_breaks: `{record.get('line_breaks')}`",
                f"- villain_score: `{record.get('villain_score')}`",
                f"- quality_score: `{record.get('quality_score')}`",
                f"- risk: `{record.get('risk')}`",
                f"- already_posted: {fmt(record.get('already_posted'))}",
                "",
                "### Text",
                "",
                "```text",
                record.get("text", ""),
                "```",
                "",
                "### Result Summary",
                "",
                record.get("result_summary", ""),
                "",
                "### Why It Worked Hypothesis",
                "",
            ]
        )
        for item in record.get("why_it_worked_hypothesis", []):
            lines.append(f"- {item}")
        lines.extend(["", "### Why It Failed Hypothesis", ""])
        for item in record.get("why_it_failed_hypothesis", []):
            lines.append(f"- {item}")
        lines.extend(["", "### Next Improvement", ""])
        for item in record.get("next_improvement", []):
            lines.append(f"- {item}")
        lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    metrics_db = read_json(METRICS_PATH)
    queue_db = read_json(QUEUE_PATH)
    payload_db = read_json(PAYLOADS_PATH)
    update_records(metrics_db, queue_db, payload_db)
    write_json(METRICS_PATH, metrics_db)
    write_report(metrics_db)
    print(f"analysis_status=ANALYSIS_ONLY")
    print(f"records={len(metrics_db.get('records', []))}")
    print(f"wrote {METRICS_PATH.relative_to(ROOT)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
