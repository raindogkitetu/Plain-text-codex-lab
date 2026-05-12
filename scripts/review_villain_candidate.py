#!/usr/bin/env python3
"""Approve or reject generated Villain candidates without posting.

Default execution is dry-run/report only. The queue is mutated only when the
explicit command is `approve <candidate_id>`. Reject records review metadata on
the generated candidate and never adds it to the queue.

This script does not read .env, call X API, upload media, create tweets, or
execute any live posting action.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GENERATED_PATH = ROOT / "data" / "villain_generated_candidates.json"
SCORING_RULES_PATH = ROOT / "data" / "villain_post_scoring_rules.json"
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
DECISIONS_PATH = ROOT / "reports" / "villain_queue_decisions.md"
REPORT_PATH = ROOT / "reports" / "villain_review_actions.md"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def generated_by_id(generated_db: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        candidate.get("candidate_id", ""): candidate
        for candidate in generated_db.get("candidates", [])
        if candidate.get("candidate_id")
    }


def queue_ids(queue_db: dict[str, Any]) -> set[str]:
    return {
        item.get("source_generated_candidate_id", "")
        for item in queue_db.get("queue", [])
        if item.get("source_generated_candidate_id")
    }


def candidate_known_to_decision_report(candidate_id: str) -> bool:
    if not DECISIONS_PATH.exists():
        return False
    return candidate_id in DECISIONS_PATH.read_text(encoding="utf-8")


def passcode_from_text(text: str) -> str:
    tail = text.strip().split()[-1] if text.strip() else ""
    return tail if tail and tail.isalnum() else ""


def first_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def approve_blockers(candidate: dict[str, Any], queue_db: dict[str, Any], threshold: int) -> list[str]:
    blockers: list[str] = []
    candidate_id = candidate.get("candidate_id", "")
    quality = candidate.get("quality_prediction", 0)
    risk = candidate.get("risk_prediction", "unknown")

    if quality < threshold:
        blockers.append(f"quality_score_below_{threshold}")
    if risk == "high":
        blockers.append("risk_high")
    if candidate.get("already_posted"):
        blockers.append("already_posted")
    if candidate.get("review", {}).get("rejected"):
        blockers.append("candidate_already_rejected")
    if candidate_id in queue_ids(queue_db):
        blockers.append("candidate_already_in_queue")
    if not candidate.get("text", "").strip():
        blockers.append("empty_text")
    if not candidate_known_to_decision_report(candidate_id):
        blockers.append("missing_from_queue_decision_report")
    if candidate.get("queue_add_allowed") is not True:
        blockers.append("candidate_queue_add_allowed_false")
    return blockers


def build_queue_item(candidate: dict[str, Any], approved_by: str, approved_at: str) -> dict[str, Any]:
    candidate_id = candidate.get("candidate_id", "")
    text = candidate.get("text", "")
    passcode = passcode_from_text(text)
    return {
        "queue_id": f"vln-queue-{candidate_id}",
        "source_generated_candidate_id": candidate_id,
        "created_at": approved_at,
        "updated_at": approved_at,
        "status": "waiting_for_image",
        "post_type": candidate.get("category", ""),
        "candidate_role": "review_approved",
        "is_today_main_candidate": False,
        "rough_first_reaction": first_line(text),
        "text": text,
        "fixed_footer": "#着て稼ぐ #villain @0xmavillain {PASSCODE}",
        "passcode": {
            "code": passcode,
            "confirmed": False,
            "usage_log_recorded": False,
        },
        "source_urls": [],
        "image": {
            "required": True,
            "status": "waiting_for_image",
            "file_path_or_url": "",
            "poster_concept": candidate.get("image_hint", ""),
            "source_asset": "",
            "rights_notes": "画像未添付。実投稿前に素材元と使用可否を確認する。",
        },
        "checks": {
            "source_url_confirmed": "unchecked",
            "image_attached": "unchecked",
            "passcode_confirmed": "unchecked",
            "prohibited_content_check": "unchecked",
            "skip_day_policy": False,
            "daisho_approval": "unchecked",
        },
        "approval": {
            "manual_approval_required": True,
            "approved_by": approved_by,
            "approved_at": approved_at,
            "approval_comment": "Generated candidate approved for queue review only. Posting remains blocked.",
            "approved_by_human": True,
        },
        "rejection": {
            "rejected_by": "",
            "rejected_at": "",
            "reason": "",
        },
        "skip": {
            "skipped": False,
            "reason": "",
            "note_seed_only": "",
        },
        "post_execution": {
            "posting_execution_allowed": False,
            "posted_url": "",
            "posted_at": "",
            "posted_by": "",
            "method": "manual_only",
        },
        "review_safety": {
            "dry_run_only": True,
            "live_posting_allowed": False,
            "x_api_write_allowed": False,
            "upload_media_allowed": False,
            "create_tweet_allowed": False,
        },
        "quality_snapshot": {
            "quality_prediction": candidate.get("quality_prediction"),
            "villain_score": candidate.get("villain_score"),
            "risk_prediction": candidate.get("risk_prediction"),
        },
    }


def apply_approve(
    generated_db: dict[str, Any],
    queue_db: dict[str, Any],
    candidate_id: str,
    approved_by: str,
    threshold: int,
) -> tuple[str, list[str]]:
    candidates = generated_by_id(generated_db)
    candidate = candidates.get(candidate_id)
    if not candidate:
        return "BLOCKED", ["candidate_not_found"]

    blockers = approve_blockers(candidate, queue_db, threshold)
    if blockers:
        return "BLOCKED", blockers

    approved_at = now_iso()
    queue_db.setdefault("queue", []).append(build_queue_item(candidate, approved_by, approved_at))
    queue_db["updated_at"] = approved_at
    candidate["review"] = {
        "approved_by_human": True,
        "approved_at": approved_at,
        "approved_by": approved_by,
        "queue_added": True,
        "queue_status": "waiting_for_image",
    }
    write_json(QUEUE_PATH, queue_db)
    write_json(GENERATED_PATH, generated_db)
    return "APPROVED_FOR_QUEUE_ONLY", []


def apply_reject(
    generated_db: dict[str, Any],
    candidate_id: str,
    rejected_by: str,
    reason: str,
) -> tuple[str, list[str]]:
    candidates = generated_by_id(generated_db)
    candidate = candidates.get(candidate_id)
    if not candidate:
        return "BLOCKED", ["candidate_not_found"]

    rejected_at = now_iso()
    candidate["review"] = {
        "rejected": True,
        "rejected_at": rejected_at,
        "rejected_by": rejected_by,
        "rejected_reason": reason,
        "queue_added": False,
    }
    write_json(GENERATED_PATH, generated_db)
    return "REJECTED_NO_QUEUE_MUTATION", []


def build_dry_run_actions(generated_db: dict[str, Any], queue_db: dict[str, Any], threshold: int) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for candidate in generated_db.get("candidates", []):
        blockers = approve_blockers(candidate, queue_db, threshold)
        actions.append(
            {
                "candidate_id": candidate.get("candidate_id", ""),
                "category": candidate.get("category", ""),
                "quality_score": candidate.get("quality_prediction"),
                "risk": candidate.get("risk_prediction"),
                "approve_allowed": not blockers,
                "approve_blockers": blockers,
                "reject_allowed": True,
                "text": candidate.get("text", ""),
            }
        )
    return actions


def write_report(
    action: str,
    candidate_id: str,
    result: str,
    blockers: list[str],
    dry_run_actions: list[dict[str, Any]],
) -> None:
    lines = [
        "# Villain Review Actions",
        "",
        f"- Generated at: `{now_iso()}`",
        "- status: `DRY_RUN_ONLY`",
        f"- requested_action: `{action}`",
        f"- requested_candidate_id: `{candidate_id}`",
        f"- result: `{result}`",
        f"- blockers: `{', '.join(blockers) if blockers else 'none'}`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        "- queue mutation rule: `APPROVE_ONLY`",
        "",
        "## Candidate Review Matrix",
        "",
    ]
    for item in dry_run_actions:
        lines.extend(
            [
                f"### `{item.get('candidate_id')}`",
                "",
                f"- category: `{item.get('category')}`",
                f"- quality_score: `{item.get('quality_score')}`",
                f"- risk: `{item.get('risk')}`",
                f"- approve_allowed: `{str(item.get('approve_allowed')).lower()}`",
                f"- approve_blockers: `{', '.join(item.get('approve_blockers', [])) if item.get('approve_blockers') else 'none'}`",
                f"- reject_allowed: `{str(item.get('reject_allowed')).lower()}`",
                "",
            ]
        )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review generated Villain candidate.")
    parser.add_argument("action", nargs="?", choices=["approve", "reject", "dry-run"], default="dry-run")
    parser.add_argument("candidate_id", nargs="?", default="")
    parser.add_argument("--by", default="human")
    parser.add_argument("--reason", default="manual_reject")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generated_db = read_json(GENERATED_PATH)
    scoring_rules = read_json(SCORING_RULES_PATH)
    queue_db = read_json(QUEUE_PATH)
    threshold = scoring_rules.get("selection_policy", {}).get("recommended_threshold", 80)
    result = "DRY_RUN_ONLY"
    blockers: list[str] = []

    if args.action == "approve":
        result, blockers = apply_approve(generated_db, queue_db, args.candidate_id, args.by, threshold)
        generated_db = read_json(GENERATED_PATH)
        queue_db = read_json(QUEUE_PATH)
    elif args.action == "reject":
        result, blockers = apply_reject(generated_db, args.candidate_id, args.by, args.reason)
        generated_db = read_json(GENERATED_PATH)

    dry_run_actions = build_dry_run_actions(generated_db, queue_db, threshold)
    write_report(args.action, args.candidate_id, result, blockers, dry_run_actions)

    print(f"status={result}")
    print("live_posting=NOT_EXECUTED")
    print("x_api_write=NOT_USED")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
