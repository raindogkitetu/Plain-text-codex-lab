#!/usr/bin/env python3
"""Recommend Villain candidates for queue review without mutating the queue.

This is a dry-run only orchestration report. It reads generated candidates,
scoring rules, and the existing queue, then writes a Markdown decision report.
It does not add queue items, read .env, call X API, upload media, or create
posts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GENERATED_PATH = ROOT / "data" / "villain_generated_candidates.json"
SCORING_RULES_PATH = ROOT / "data" / "villain_post_scoring_rules.json"
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
REPORT_PATH = ROOT / "reports" / "villain_queue_decisions.md"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def existing_texts(queue_db: dict[str, Any]) -> set[str]:
    return {
        item.get("text", "").strip()
        for item in queue_db.get("queue", [])
        if item.get("text", "").strip()
    }


def candidate_decision(candidate: dict[str, Any], threshold: int, existing: set[str]) -> dict[str, Any]:
    quality_score = candidate.get("quality_prediction", 0)
    risk = candidate.get("risk_prediction", "unknown")
    text = candidate.get("text", "").strip()
    already_posted = bool(candidate.get("already_posted"))
    duplicate_text = text in existing
    reasons: list[str] = []

    if quality_score < threshold:
        reasons.append(f"quality_score_below_{threshold}")
    if risk == "high":
        reasons.append("risk_high")
    if already_posted:
        reasons.append("already_posted")
    if duplicate_text:
        reasons.append("duplicate_with_existing_queue")
    if not text:
        reasons.append("empty_text")

    queue_add_allowed = not reasons
    if queue_add_allowed:
        reasons.append("quality_score_passed_and_risk_low_enough")

    return {
        "candidate_id": candidate.get("candidate_id", ""),
        "category": candidate.get("category", ""),
        "quality_score": quality_score,
        "risk": risk,
        "already_posted": already_posted,
        "duplicate_text": duplicate_text,
        "queue_add_allowed": queue_add_allowed,
        "recommendation_reason": ", ".join(reasons),
        "text": text,
        "image_hint": candidate.get("image_hint", ""),
    }


def rank(decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        decisions,
        key=lambda item: (
            item.get("queue_add_allowed") is True,
            item.get("risk") == "low",
            item.get("quality_score", 0),
        ),
        reverse=True,
    )


def write_report(
    generated_db: dict[str, Any],
    scoring_rules: dict[str, Any],
    decisions: list[dict[str, Any]],
    recommended: list[dict[str, Any]],
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    threshold = scoring_rules.get("selection_policy", {}).get("recommended_threshold", 80)
    lines = [
        "# Villain Queue Decisions",
        "",
        f"- Generated at: `{now}`",
        "- status: `DRY_RUN_ONLY`",
        "- queue mutation: `NOT_EXECUTED`",
        "- queue auto add: `DISABLED`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        f"- source_run_id: `{generated_db.get('run_id', '')}`",
        f"- quality_threshold: `{threshold}`",
        "- max recommended queue candidates: `2`",
        "",
        "## Recommended Queue Candidates",
        "",
    ]

    if not recommended:
        lines.append("- none")
    for item in recommended:
        lines.extend(
            [
                f"### `{item.get('candidate_id')}`",
                "",
                f"- category: `{item.get('category')}`",
                f"- quality_score: `{item.get('quality_score')}`",
                f"- risk: `{item.get('risk')}`",
                f"- queue_add_allowed: `{str(item.get('queue_add_allowed')).lower()}`",
                f"- recommendation_reason: {item.get('recommendation_reason')}",
                f"- image_hint: {item.get('image_hint')}",
                "",
                "```text",
                item.get("text", ""),
                "```",
                "",
            ]
        )

    lines.extend(["## All Decisions", ""])
    for item in decisions:
        lines.extend(
            [
                f"- `{item.get('candidate_id')}`: queue_add_allowed=`{str(item.get('queue_add_allowed')).lower()}`, "
                f"quality_score=`{item.get('quality_score')}`, risk=`{item.get('risk')}`, "
                f"reason={item.get('recommendation_reason')}",
            ]
        )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    generated_db = read_json(GENERATED_PATH)
    scoring_rules = read_json(SCORING_RULES_PATH)
    queue_db = read_json(QUEUE_PATH)
    threshold = scoring_rules.get("selection_policy", {}).get("recommended_threshold", 80)
    existing = existing_texts(queue_db)

    decisions = [
        candidate_decision(candidate, threshold, existing)
        for candidate in generated_db.get("candidates", [])
    ]
    ranked = rank(decisions)
    recommended = [item for item in ranked if item.get("queue_add_allowed")][:2]
    write_report(generated_db, scoring_rules, decisions, recommended)

    print("status=DRY_RUN_ONLY")
    print("queue_mutation=NOT_EXECUTED")
    print(f"decisions={len(decisions)}")
    print(f"recommended={len(recommended)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
