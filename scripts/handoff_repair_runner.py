#!/usr/bin/env python3
"""Execute review-only repair actions from the handoff layer.

This layer rehabilitates candidates for review. It never approves posting and
never calls upload/create tweet paths.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
REPAIR_RESULT_PATH = ROOT / "data" / "villain_repair_execution.json"
REPAIRED_CANDIDATES_PATH = ROOT / "data" / "villain_repaired_candidates.json"
CONTEXT_EVIDENCE_REQUESTS_PATH = ROOT / "data" / "villain_context_evidence_requests.json"
REPAIR_QUALITY_ANALYTICS_PATH = ROOT / "data" / "villain_repair_quality_analytics.json"
IMAGE_STRATEGY_PATH = ROOT / "data" / "villain_image_strategy.json"
RECENT_MEDIA_HISTORY_PATH = ROOT / "data" / "recent_media_history.json"
OUTCOMES_PATH = ROOT / "data" / "villain_post_outcomes.json"
QUALITY_POLICY_PATH = ROOT / "data" / "villain_post_quality_os.json"
TRAJECTORY_PATH = ROOT / "data" / "agent_handoff_trajectory.json"
JST = ZoneInfo("Asia/Tokyo")

REPAIR_SCHEMA_VERSION = "handoff.repair_execution.v1"
REPAIRED_CANDIDATES_SCHEMA_VERSION = "handoff.repaired_candidates.v1"
CONTEXT_EVIDENCE_SCHEMA_VERSION = "handoff.context_evidence_requests.v1"
REPAIR_QUALITY_SCHEMA_VERSION = "handoff.repair_quality_analytics.v1"
TRAJECTORY_SCHEMA_VERSION = "handoff.trajectory.v1"
BANNED_IMAGE_NAMES = {"20260514集会.png"}
TEMPORAL_EVENT_PATTERNS = [
    r"昨日の集会、?\n?",
    r"今日の集会、?\n?",
    r"明日の集会、?\n?",
    r"昨日のイベント、?\n?",
    r"今日のイベント、?\n?",
    r"明日のイベント、?\n?",
    r"さっきの発表、?\n?",
    r"現場で、?\n?",
    r"どこで集まってるかまで含めて、?\n?",
]


def now_jst() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def compact_lines(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    compact: list[str] = []
    previous_blank = False
    for line in lines:
        blank = not line.strip()
        if blank and previous_blank:
            continue
        compact.append(line)
        previous_blank = blank
    return "\n".join(compact).strip() + "\n"


def strip_temporal_claims(text: str) -> tuple[str, list[str]]:
    repaired = text.replace("誰が着て、\nどこで集まってるかまで含めて、", "誰が着て、\nどう残るかまで含めて、")
    removed: list[str] = []
    for pattern in TEMPORAL_EVENT_PATTERNS:
        updated = re.sub(pattern, "", repaired)
        if updated != repaired:
            removed.append(pattern)
            repaired = updated
    repaired = repaired.replace("人が集まってる事実の方が強い。", "人が着て残る空気の方が強い。")
    return compact_lines(repaired), removed


def safe_image_candidates() -> list[dict[str, Any]]:
    image_db = read_json(IMAGE_STRATEGY_PATH, {})
    candidates: list[dict[str, Any]] = []
    for item in image_db.get("next_image_recommendations", []):
        file_path = item.get("file", "")
        if not file_path or Path(file_path).name in BANNED_IMAGE_NAMES:
            continue
        abs_path = ROOT / file_path
        if abs_path.exists():
            candidates.append({**item, "absolute_path": str(abs_path)})
    for item in image_db.get("local_image_inventory", []):
        file_path = item.get("file", "")
        if not file_path or Path(file_path).name in BANNED_IMAGE_NAMES:
            continue
        abs_path = ROOT / file_path
        if abs_path.exists():
            candidates.append(
                {
                    "file": file_path,
                    "absolute_path": str(abs_path),
                    "category": item.get("primary_type", ""),
                    "rank": 20 if item.get("priority") == "S" else 60,
                    "reason": item.get("best_use", ""),
                    "recommended_for_categories": item.get("recommended_for_categories", []),
                }
            )
    return sorted(candidates, key=lambda item: item.get("rank", 99))


def choose_replacement_image(item: dict[str, Any]) -> dict[str, Any]:
    category = item.get("category", "")
    for image in safe_image_candidates():
        recommended = [str(value).lower() for value in image.get("recommended_for_categories", [])]
        if category and category.lower() in recommended:
            return image
    candidates = safe_image_candidates()
    return candidates[0] if candidates else {}


def evidence_request_for(item: dict[str, Any], action: dict[str, Any], generated_at: str) -> dict[str, Any]:
    return {
        "candidate_id": item.get("candidate_id", ""),
        "context_terms": item.get("context_terms", []),
        "created_at_jst": generated_at,
        "evidence_status": "REQUESTED",
        "execution_id": item.get("execution_id", ""),
        "question": "この投稿は何を見て言っているのか？",
        "reason": action.get("reason", ""),
        "required_before_review": True,
        "source_file_required": True,
    }


def by_execution_id(review: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item.get("execution_id", ""): item for item in review.get("review_items", [])}


def original_for_repaired(repaired: dict[str, Any], review_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return review_by_id.get(repaired.get("original_execution_id", ""), {})


def diff_summary(original: dict[str, Any], repaired: dict[str, Any]) -> dict[str, Any]:
    original_lines = [line.strip() for line in original.get("text", "").splitlines() if line.strip()]
    repaired_lines = [line.strip() for line in repaired.get("text", "").splitlines() if line.strip()]
    removed = [line for line in original_lines if line not in repaired_lines]
    added = [line for line in repaired_lines if line not in original_lines]
    original_image = original.get("image", "")
    repaired_image = repaired.get("image", {}).get("file_path", "") or repaired.get("image", {}).get("absolute_path", "")
    return {
        "added_lines": added,
        "image_changed": bool(original_image and repaired_image and repaired_image not in original_image),
        "original_image": original_image,
        "removed_lines": removed,
        "repaired_image": repaired_image,
        "text_changed": original.get("text", "").strip() != repaired.get("text", "").strip(),
    }


def evaluate_repaired_candidate(repaired: dict[str, Any], original: dict[str, Any]) -> dict[str, Any]:
    from post_quality_os import evaluate_candidate  # local import avoids coupling during module load.

    outcomes = read_json(OUTCOMES_PATH, {})
    policy = read_json(QUALITY_POLICY_PATH, {})
    recent_media = read_json(RECENT_MEDIA_HISTORY_PATH, {})
    candidate = {
        "candidate_id": repaired.get("candidate_id", ""),
        "category": original.get("category", "culture_observer"),
        "execution_id": repaired.get("original_execution_id", ""),
        "image": repaired.get("image", {}),
        "passcode": repaired.get("passcode", ""),
        "slot": original.get("slot", ""),
        "text": repaired.get("text", ""),
    }
    quality = evaluate_candidate(candidate, outcomes, policy)
    blockers = quality.get("blockers", [])
    warnings = quality.get("warnings", [])
    repair_quality_warnings: list[str] = []
    repaired_image_path = str(candidate.get("image", {}).get("absolute_path") or candidate.get("image", {}).get("file_path", ""))
    repaired_image_name = Path(repaired_image_path).name if repaired_image_path else ""
    for entry in recent_media.get("entries", []):
        entry_image = str(entry.get("image_used", ""))
        if repaired_image_name and Path(entry_image).name == repaired_image_name:
            repair_quality_warnings.append("replacement_image_recently_used")
            break
    score = 72
    score += int(quality.get("native_tone_score", 0) * 0.12)
    score += int(quality.get("persona_fit", 0) * 0.1)
    score -= len(blockers) * 18
    score -= len(warnings) * 7
    score -= len(repair_quality_warnings) * 14
    if quality.get("topic_image_fit", {}).get("status") == "OK":
        score += 8
    score = max(0, min(100, score))
    if blockers:
        risk = "high"
    elif warnings or repair_quality_warnings:
        risk = "medium"
    else:
        risk = "low"
    confidence = max(0, min(100, score - (15 if risk == "medium" else 30 if risk == "high" else 0)))
    return {
        "quality_review": quality,
        "repair_confidence": confidence,
        "repair_quality_warnings": sorted(set(repair_quality_warnings)),
        "repair_quality_score": score,
        "repair_regression_risk": risk,
    }


def reviewer_feedback_linkage(original: dict[str, Any], repaired: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedback_status": "PENDING_REVIEWER_FEEDBACK",
        "human_approved_for_posting": False,
        "original_candidate_id": original.get("candidate_id", ""),
        "original_execution_id": repaired.get("original_execution_id", ""),
        "review_queue_source": "data/villain_quality_review_queue.json",
        "reviewer_prompt": "Does this repaired candidate feel natural, grounded, non-ad-like, and image-text matched?",
    }


def repair_failure_clusters(repair_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: Counter[tuple[str, str]] = Counter()
    for item in repair_results:
        status = item.get("repair_status", "")
        action_type = item.get("repair_action", {}).get("type", "")
        grouped[(status, action_type)] += 1
    return [
        {
            "cluster": f"{status}:{action_type}",
            "count": count,
            "recurring": count >= 2,
        }
        for (status, action_type), count in sorted(grouped.items())
    ]


def repair_quality_analytics(
    generated_at: str,
    repair_results: list[dict[str, Any]],
    repaired_candidates: list[dict[str, Any]],
    review_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    evaluated_candidates: list[dict[str, Any]] = []
    risk_frequency: Counter[str] = Counter()
    confidence_values: list[int] = []
    quality_values: list[int] = []

    for candidate in repaired_candidates:
        original = original_for_repaired(candidate, review_by_id)
        evaluation = evaluate_repaired_candidate(candidate, original)
        diff = diff_summary(original, candidate)
        feedback = reviewer_feedback_linkage(original, candidate)
        quality_score = int(evaluation["repair_quality_score"])
        confidence = int(evaluation["repair_confidence"])
        regression_risk = evaluation["repair_regression_risk"]
        candidate.update(
            {
                "human_approved_for_posting": False,
                "repair_confidence": confidence,
                "repair_quality_score": quality_score,
                "repair_quality_warnings": evaluation.get("repair_quality_warnings", []),
                "repair_regression_risk": regression_risk,
                "repaired_vs_original_diff": diff,
                "reviewer_feedback_linkage": feedback,
                "safe_to_post": False,
            }
        )
        evaluated_candidates.append(
            {
                "candidate_id": candidate.get("candidate_id", ""),
                "original_candidate_id": candidate.get("original_candidate_id", ""),
                "original_execution_id": candidate.get("original_execution_id", ""),
                "quality_review_after_repair": evaluation["quality_review"],
                "repair_confidence": confidence,
                "repair_quality_warnings": evaluation.get("repair_quality_warnings", []),
                "repair_quality_score": quality_score,
                "repair_regression_risk": regression_risk,
                "repaired_vs_original_diff": diff,
                "reviewer_feedback_linkage": feedback,
                "safe_to_post": False,
            }
        )
        risk_frequency[regression_risk] += 1
        confidence_values.append(confidence)
        quality_values.append(quality_score)

    status_frequency = Counter(item.get("repair_status", "") for item in repair_results)
    action_frequency = Counter(item.get("repair_action", {}).get("type", "") for item in repair_results)
    analytics = {
        "db_name": "Villain Repair Quality Analytics",
        "generated_at_jst": generated_at,
        "posting_executed": False,
        "repair_outcome_analytics": {
            "archive_count": status_frequency.get("ARCHIVED_FROM_REVIEW", 0),
            "blocked_no_replacement_image_count": status_frequency.get("BLOCKED_NO_REPLACEMENT_IMAGE", 0),
            "context_evidence_request_count": action_frequency.get("context_evidence_required", 0),
            "image_replacement_attempt_count": action_frequency.get("image_replacement_required", 0),
            "repair_action_frequency": dict(sorted(action_frequency.items())),
            "repair_status_frequency": dict(sorted(status_frequency.items())),
            "repaired_for_review_count": status_frequency.get("REPAIRED_FOR_REVIEW_ONLY", 0),
        },
        "repair_quality_summary": {
            "average_repair_confidence": round(sum(confidence_values) / len(confidence_values), 1)
            if confidence_values
            else 0,
            "average_repair_quality_score": round(sum(quality_values) / len(quality_values), 1)
            if quality_values
            else 0,
            "evaluated_repaired_candidate_count": len(evaluated_candidates),
            "repair_regression_risk_frequency": dict(sorted(risk_frequency.items())),
            "safe_to_post": False,
        },
        "repaired_candidate_evaluations": evaluated_candidates,
        "recurring_repair_failure_clusters": repair_failure_clusters(repair_results),
        "safe_to_post": False,
        "schema_version": REPAIR_QUALITY_SCHEMA_VERSION,
        "tweet_creation_executed": False,
        "upload_media_executed": False,
        "version": "1.0.0",
    }
    return analytics


def previous_attempts() -> dict[str, int]:
    db = read_json(REPAIR_RESULT_PATH, {})
    attempts: dict[str, int] = {}
    for item in db.get("repair_results", []):
        key = item.get("execution_id", "")
        if key:
            attempts[key] = max(attempts.get(key, 0), int(item.get("repair_attempt", 0)))
    return attempts


def stable_repair_id(candidate_id: str, execution_id: str, attempt: int) -> str:
    suffix = re.sub(r"[^A-Za-z0-9]+", "-", execution_id).strip("-").lower()
    if suffix.startswith("vln-exec-"):
        suffix = suffix[len("vln-exec-") :]
    return f"{candidate_id}-repair-{suffix}-{attempt}"


def run_repair_execution(
    repair_actions: list[dict[str, Any]],
    review: dict[str, Any],
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or now_jst()
    review_by_id = by_execution_id(review)
    attempts = previous_attempts()
    repair_results: list[dict[str, Any]] = []
    repaired_candidates: list[dict[str, Any]] = []
    evidence_requests: list[dict[str, Any]] = []

    for action_record in repair_actions:
        execution_id = action_record.get("execution_id", "")
        item = review_by_id.get(execution_id, {})
        action = action_record.get("repair_action", {})
        action_type = action.get("type", "none")
        attempt = attempts.get(execution_id, 0) + 1
        result = {
            "candidate_id": action_record.get("candidate_id", ""),
            "created_at_jst": generated_at,
            "execution_id": execution_id,
            "original_blockers": action_record.get("blockers", []),
            "repair_action": action,
            "repair_attempt": attempt,
            "repair_status": "SKIPPED",
            "safe_to_post": False,
        }

        if action_type == "archive_or_drop":
            if "temporal_context_unverified" in action_record.get("blockers", []):
                evidence_requests.append(evidence_request_for(item, action, generated_at))
            result["repair_status"] = "ARCHIVED_FROM_REVIEW"
            result["reason"] = "Deleted-near pattern should not be rehabilitated automatically."
        elif action_type in {"image_replacement_required", "context_evidence_required"}:
            stripped_text, removed_patterns = strip_temporal_claims(item.get("text", ""))
            replacement = choose_replacement_image(item)
            if action_type == "context_evidence_required":
                evidence_requests.append(evidence_request_for(item, action, generated_at))
            if replacement:
                repaired_id = stable_repair_id(action_record.get("candidate_id", ""), execution_id, attempt)
                repaired_candidate = {
                    "candidate_id": repaired_id,
                    "created_at_jst": generated_at,
                    "human_approved_for_posting": False,
                    "image": {
                        "absolute_path": replacement.get("absolute_path", ""),
                        "file_path": replacement.get("file", ""),
                        "reason": replacement.get("reason", ""),
                        "ready": True,
                    },
                    "original_candidate_id": action_record.get("candidate_id", ""),
                    "original_execution_id": execution_id,
                    "passcode": item.get("passcode", ""),
                    "repair_attempt": attempt,
                    "repair_status": "REPAIRED_FOR_REVIEW_ONLY",
                    "safe_to_post": False,
                    "text": stripped_text,
                }
                repaired_candidates.append(repaired_candidate)
                result["repair_status"] = "REPAIRED_FOR_REVIEW_ONLY"
                result["repaired_candidate_id"] = repaired_id
                result["replacement_image"] = replacement.get("file", "")
                result["temporal_patterns_removed"] = removed_patterns
            else:
                result["repair_status"] = "BLOCKED_NO_REPLACEMENT_IMAGE"
        else:
            result["reason"] = "No executable repair action."
        repair_results.append(result)

    quality_analytics = repair_quality_analytics(generated_at, repair_results, repaired_candidates, review_by_id)

    result_db = {
        "db_name": "Villain Repair Execution",
        "generated_at_jst": generated_at,
        "posting_executed": False,
        "repair_quality_summary": quality_analytics.get("repair_quality_summary", {}),
        "repair_results": repair_results,
        "schema_version": REPAIR_SCHEMA_VERSION,
        "safe_to_post": False,
        "tweet_creation_executed": False,
        "upload_media_executed": False,
        "version": "1.0.0",
    }
    repaired_db = {
        "db_name": "Villain Repaired Candidates",
        "generated_at_jst": generated_at,
        "repaired_candidates": repaired_candidates,
        "schema_version": REPAIRED_CANDIDATES_SCHEMA_VERSION,
        "safe_to_post": False,
        "version": "1.0.0",
    }
    evidence_db = {
        "context_evidence_requests": evidence_requests,
        "db_name": "Villain Context Evidence Requests",
        "generated_at_jst": generated_at,
        "schema_version": CONTEXT_EVIDENCE_SCHEMA_VERSION,
        "safe_to_post": False,
        "version": "1.0.0",
    }
    write_json(REPAIR_RESULT_PATH, result_db)
    write_json(REPAIRED_CANDIDATES_PATH, repaired_db)
    write_json(CONTEXT_EVIDENCE_REQUESTS_PATH, evidence_db)
    write_json(REPAIR_QUALITY_ANALYTICS_PATH, quality_analytics)
    append_repair_trajectory(generated_at, repair_results, repaired_candidates)
    return {
        "context_evidence_request_count": len(evidence_requests),
        "recurring_repair_failure_clusters": quality_analytics.get("recurring_repair_failure_clusters", []),
        "repair_quality_summary": quality_analytics.get("repair_quality_summary", {}),
        "repair_result_count": len(repair_results),
        "repair_status_frequency": dict(sorted(Counter(item["repair_status"] for item in repair_results).items())),
        "repaired_candidate_count": len(repaired_candidates),
        "safe_to_post": False,
    }


def append_repair_trajectory(
    generated_at: str,
    repair_results: list[dict[str, Any]],
    repaired_candidates: list[dict[str, Any]],
) -> None:
    db = read_json(
        TRAJECTORY_PATH,
        {
            "db_name": "Agent Handoff Trajectory",
            "events": [],
            "schema_version": TRAJECTORY_SCHEMA_VERSION,
            "version": "1.0.0",
        },
    )
    events = db.setdefault("events", [])
    events.append(
        {
            "at_jst": generated_at,
            "event_type": "repair_execution_cycle",
            "posting_executed": False,
            "repair_result_count": len(repair_results),
            "repair_status_frequency": dict(sorted(Counter(item["repair_status"] for item in repair_results).items())),
            "repaired_candidate_count": len(repaired_candidates),
            "safe_to_post": False,
            "tweet_creation_executed": False,
            "upload_media_executed": False,
        }
    )
    db["event_count"] = len(events)
    db["last_event_at_jst"] = generated_at
    write_json(TRAJECTORY_PATH, db)


def main() -> None:
    outbox = read_json(ROOT / "data" / "codex_to_chatgpt_handoff.json", {})
    review = read_json(ROOT / "data" / "villain_quality_review_queue.json", {})
    result = run_repair_execution(outbox.get("repair_actions", []), review)
    print(f"repair_result_count={result['repair_result_count']}")
    print(f"repaired_candidate_count={result['repaired_candidate_count']}")
    print("posting_executed=NO")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")


if __name__ == "__main__":
    main()
