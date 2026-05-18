#!/usr/bin/env python3
"""Evaluate Villain post quality gates without posting.

Quality OS is a naturalness/context-grounding layer. It separates hard blockers
from subjective review-required signals and never calls X write APIs.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from context_mismatch_gate import (
    context_gate_blockers,
    deleted_learning_blockers,
    topic_image_pairing_blockers,
)


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "data" / "villain_post_quality_os.json"
PILOT_PATH = ROOT / "data" / "villain_auto_post_pilot.json"
OUTCOMES_PATH = ROOT / "data" / "villain_post_outcomes.json"
QUEUE_PATH = ROOT / "data" / "villain_quality_review_queue.json"
REPORT_PATH = ROOT / "reports" / "villain_quality_review_summary.md"
OS_REPORT_PATH = ROOT / "reports" / "villain_post_quality_os.md"
JST = ZoneInfo("Asia/Tokyo")

HARD_BLOCKERS = {
    "temporal_context_unverified",
    "topic_image_pairing_mismatch",
    "deleted_topic_context_cooldown",
    "deleted_text_near_match",
}

AD_LIKE_TERMS = [
    "買って",
    "購入",
    "販売",
    "セール",
    "限定",
    "今すぐ",
    "公式",
    "おすすめ",
    "稼げる",
    "絶対",
    "必須",
]

NATIVE_TONE_POSITIVE = ["気づくと", "たぶん", "少し", "変", "残る", "空気", "話題", "だいたい"]
PERSONA_TERMS = ["$villain", "#villain", "鬼徹", "着て稼ぐ", "服だけじゃない", "集ま", "残る"]


def now_jst() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def compact_text(text: str, limit: int = 180) -> str:
    compact = " / ".join(line.strip() for line in text.splitlines() if line.strip())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def ad_like_score(text: str, image: dict[str, Any]) -> int:
    score = 0
    score += sum(12 for term in AD_LIKE_TERMS if term in text)
    if text.count("#") >= 4:
        score += 10
    if "!" in text or "！" in text:
        score += 8
    image_words = " ".join(str(image.get(key, "")) for key in ("reason", "image_type", "prompt_family")).lower()
    if any(word in image_words for word in ("product", "clean", "overpolished", "generic_ai_visual")):
        score += 14
    return min(score, 100)


def native_tone_score(text: str) -> int:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    score = 62
    score += sum(5 for term in NATIVE_TONE_POSITIVE if term in text)
    if 3 <= len(lines) <= 9:
        score += 10
    if len(text) > 260:
        score -= 16
    if sum(1 for term in AD_LIKE_TERMS if term in text) >= 2:
        score -= 18
    if text.count("。") >= 8:
        score -= 8
    return max(0, min(score, 100))


def persona_fit_score(text: str, category: str) -> int:
    score = 58
    score += sum(5 for term in PERSONA_TERMS if term in text)
    if category in {"culture_observer", "poster_summary", "community_info"}:
        score += 10
    if "稼げる" in text or "絶対" in text:
        score -= 16
    return max(0, min(score, 100))


def review_status(blockers: list[str], warnings: list[str]) -> str:
    if blockers:
        return "BLOCKED"
    if warnings:
        return "REVIEW_REQUIRED"
    return "READY"


def explicit_human_approved(candidate: dict[str, Any]) -> bool:
    review = candidate.get("review", {})
    manual_review = candidate.get("manual_review", {})
    return bool(
        candidate.get("human_approved_for_posting") is True
        or candidate.get("explicit_human_approved") is True
        or review.get("human_decision") == "approved"
        or manual_review.get("keep") is True and manual_review.get("approve_for_posting") is True
    )


def repair_action_for(blockers: list[str], warnings: list[str]) -> dict[str, Any]:
    blocker_set = set(blockers)
    if "deleted_text_near_match" in blocker_set and "deleted_topic_context_cooldown" in blocker_set:
        return {
            "type": "archive_or_drop",
            "required": True,
            "reason": "Candidate repeats a deleted/failed text and topic pattern.",
        }
    if "temporal_context_unverified" in blocker_set:
        return {
            "type": "context_evidence_required",
            "required": True,
            "reason": "Temporal or real-event claim needs evidence before review can continue.",
        }
    if "topic_image_pairing_mismatch" in blocker_set:
        return {
            "type": "image_replacement_required",
            "required": True,
            "reason": "Text topic and image metadata do not support each other.",
        }
    if warnings:
        return {
            "type": "human_review_required",
            "required": True,
            "reason": "Subjective quality signal needs review before any later approval.",
        }
    return {
        "type": "none",
        "required": False,
        "reason": "No repair needed for human review.",
    }


def item_review_state(status: str, human_approved: bool) -> str:
    if status == "BLOCKED":
        return "CANDIDATE_BLOCKED"
    if status == "REVIEW_REQUIRED":
        return "CANDIDATE_REVIEW_REQUIRED"
    if status == "READY" and human_approved:
        return "CANDIDATE_APPROVED_FOR_POSTING"
    if status == "READY":
        return "CANDIDATE_READY_FOR_HUMAN_REVIEW"
    return "CANDIDATE_UNKNOWN"


def evaluate_candidate(candidate: dict[str, Any], outcomes_db: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    text = candidate.get("text", "")
    image = candidate.get("image", {})
    context_blockers, context_check = context_gate_blockers(candidate)
    pairing_blockers, pairing_check = topic_image_pairing_blockers(text, image)
    deleted_blockers, deleted_matches = deleted_learning_blockers(candidate, image, outcomes_db)

    hard_blockers = []
    hard_blockers.extend(context_blockers)
    hard_blockers.extend(blocker for blocker in pairing_blockers if blocker == "topic_image_pairing_mismatch")
    hard_blockers.extend(blocker for blocker in deleted_blockers if blocker in HARD_BLOCKERS)
    hard_blockers = sorted(set(hard_blockers))

    ad_score = ad_like_score(text, image)
    native_score = native_tone_score(text)
    persona_score = persona_fit_score(text, candidate.get("category", ""))
    warnings: list[str] = []
    review_policy = policy.get("review_required_policy", {})
    if ad_score >= int(review_policy.get("ad_like_detection", {}).get("review_threshold", 55)):
        warnings.append("ad_like_review_required")
    if native_score < int(review_policy.get("native_tone_check", {}).get("review_below", 65)):
        warnings.append("native_tone_review_required")
    if persona_score < int(review_policy.get("persona_consistency_check", {}).get("review_below", 65)):
        warnings.append("persona_fit_review_required")
    if pairing_blockers and "topic_image_pairing_mismatch" not in pairing_blockers:
        warnings.extend(pairing_blockers)
    if deleted_matches:
        warnings.append("deleted_nearby_match_found")
    warnings = sorted(set(warnings))

    status = review_status(hard_blockers, warnings)
    human_approved = explicit_human_approved(candidate)
    return {
        "candidate_id": candidate.get("source_id") or candidate.get("candidate_id", ""),
        "execution_id": candidate.get("execution_id", ""),
        "slot": candidate.get("slot", ""),
        "passcode": candidate.get("passcode", ""),
        "image": image.get("absolute_path") or image.get("file_path", ""),
        "text": text,
        "text_preview": compact_text(text),
        "final_quality_status": status,
        "review_state": item_review_state(status, human_approved),
        "human_approved_for_posting": human_approved,
        "repair_action": repair_action_for(hard_blockers, warnings),
        "blockers": hard_blockers,
        "warnings": warnings,
        "context_terms": context_check.get("terms", []),
        "context_evidence": {
            "verified": context_check.get("context_evidence_verified", False),
            "requires_evidence": context_check.get("requires_evidence", False),
            "core_question": policy.get("context_evidence", {}).get("core_question", ""),
        },
        "topic_image_fit": {
            "status": "MISMATCH" if "topic_image_pairing_mismatch" in pairing_blockers else "OK",
            "checks": pairing_check,
        },
        "ad_like_score": ad_score,
        "native_tone_score": native_score,
        "persona_fit": persona_score,
        "deleted_nearby_match": deleted_matches,
        "human_check_checklist": [
            "この投稿は何を見て言っているのか？",
            "本文の現実文脈は今日の状況と一致しているか？",
            "画像は本文topicを本当に支えているか？",
            "広告ではなくタイムライン上の観測として混ざるか？",
            "鬼徹アカウントの余白と人格に合っているか？",
        ],
    }


def candidate_items(pilot: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    manifest_by_source = {
        (item.get("source_id"), item.get("slot")): item
        for item in pilot.get("execution_manifest", [])
    }
    for item in pilot.get("pilot_plan", []):
        manifest = manifest_by_source.get((item.get("source_id"), item.get("slot")), {})
        items.append({**item, "execution_id": manifest.get("execution_id", "")})
    for item in pilot.get("rejected_or_blocked_preview", []):
        items.append({**item, "execution_id": f"vln-exec-{item.get('slot')}-{item.get('source_id')}"})
    return items


def build_review() -> dict[str, Any]:
    policy = read_json(POLICY_PATH)
    pilot = read_json(PILOT_PATH)
    outcomes = read_json(OUTCOMES_PATH)
    reviews = [evaluate_candidate(item, outcomes, policy) for item in candidate_items(pilot)]
    status = "READY"
    if any(item["final_quality_status"] == "BLOCKED" for item in reviews):
        status = "BLOCKED"
    elif any(item["final_quality_status"] == "REVIEW_REQUIRED" for item in reviews):
        status = "REVIEW_REQUIRED"
    queue_health_status = "BLOCKED" if any(item["final_quality_status"] == "BLOCKED" for item in reviews) else "CLEAR"
    review_board_status = "READY" if reviews else "EMPTY"
    executable_ready_count = sum(
        1
        for item in reviews
        if item["final_quality_status"] == "READY" and item.get("human_approved_for_posting") is True
    )
    posting_execution_status = "READY" if executable_ready_count > 0 else "BLOCKED"
    return {
        "db_name": "Villain Quality Review Queue",
        "schema_version": "handoff.review_queue.v1",
        "version": "1.0.0",
        "generated_at_jst": now_jst(),
        "status": status,
        "review_state": "READY_FOR_HUMAN_REVIEW" if reviews else "EMPTY_REVIEW_BOARD",
        "queue_health_status": queue_health_status,
        "review_board_status": review_board_status,
        "posting_execution_status": posting_execution_status,
        "executable_ready_count": executable_ready_count,
        "safe_to_review": bool(reviews),
        "safe_to_post": False,
        "posting_executed": False,
        "upload_media_executed": False,
        "tweet_creation_executed": False,
        "policy_source": str(POLICY_PATH.relative_to(ROOT)),
        "review_items": reviews,
    }


def write_report(review: dict[str, Any]) -> None:
    lines = [
        "# Villain Quality Review Summary",
        "",
        f"- Generated at JST: `{review.get('generated_at_jst')}`",
        f"- final_status: `{review.get('status')}`",
        f"- queue_health_status: `{review.get('queue_health_status')}`",
        f"- review_board_status: `{review.get('review_board_status')}`",
        f"- posting_execution_status: `{review.get('posting_execution_status')}`",
        f"- executable_ready_count: `{review.get('executable_ready_count')}`",
        f"- safe_to_review: `{str(review.get('safe_to_review')).lower()}`",
        f"- safe_to_post: `{str(review.get('safe_to_post')).lower()}`",
        "- posting executed: `NO`",
        "- upload executed: `NO`",
        "- tweet creation executed: `NO`",
        "",
        "## Items",
        "",
    ]
    if not review.get("review_items"):
        lines.append("- No candidates to review.")
    for item in review.get("review_items", []):
        lines.extend(
            [
                f"### `{item.get('candidate_id')}`",
                "",
                f"- execution_id: `{item.get('execution_id')}`",
                f"- slot: `{item.get('slot')}`",
                f"- passcode: `{item.get('passcode')}`",
                f"- image: `{item.get('image')}`",
                f"- final_quality_status: `{item.get('final_quality_status')}`",
                f"- review_state: `{item.get('review_state')}`",
                f"- human_approved_for_posting: `{str(item.get('human_approved_for_posting')).lower()}`",
                f"- repair_action: `{item.get('repair_action', {}).get('type')}`",
                f"- blockers: `{', '.join(item.get('blockers', [])) if item.get('blockers') else 'none'}`",
                f"- warnings: `{', '.join(item.get('warnings', [])) if item.get('warnings') else 'none'}`",
                f"- context terms: `{', '.join(item.get('context_terms', [])) if item.get('context_terms') else 'none'}`",
                f"- context evidence verified: `{str(item.get('context_evidence', {}).get('verified')).lower()}`",
                f"- topic-image fit: `{item.get('topic_image_fit', {}).get('status')}`",
                f"- ad-like score: `{item.get('ad_like_score')}`",
                f"- native tone score: `{item.get('native_tone_score')}`",
                f"- persona fit: `{item.get('persona_fit')}`",
                f"- deleted-nearby match: `{len(item.get('deleted_nearby_match', []))}`",
                "",
                "```text",
                item.get("text", ""),
                "```",
                "",
                "Human check:",
            ]
        )
        lines.extend(f"- {check}" for check in item.get("human_check_checklist", []))
        lines.append("")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    os_lines = [
        "# Villain Post Quality OS",
        "",
        "- role: `naturalness_and_context_grounding_gate`",
        "- hard blockers: `temporal_context_unverified`, `topic_image_pairing_mismatch`, `deleted_topic_context_cooldown`, `deleted_text_near_match`",
        "- review_required only: `ad_like_review_required`, `native_tone_review_required`, `persona_fit_review_required`",
        "- posting executed: `NO`",
        "- upload executed: `NO`",
        "- tweet creation executed: `NO`",
        "",
        "## Principle",
        "",
        "スコアより先に、この投稿は何を見て言っているのかを確認する。現実に接地していない言葉は止める。",
        "",
    ]
    OS_REPORT_PATH.write_text("\n".join(os_lines), encoding="utf-8")


def main() -> None:
    review = build_review()
    write_json(QUEUE_PATH, review)
    write_report(review)
    print(f"status={review.get('status')}")
    print(f"review_items={len(review.get('review_items', []))}")
    print("posting_executed=NO")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"wrote {QUEUE_PATH.relative_to(ROOT)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Villain post quality review without posting.")
    parser.parse_args()
    main()
