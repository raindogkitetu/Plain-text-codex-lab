#!/usr/bin/env python3
"""Context and topic-image mismatch gates for Villain posting.

This module is local analysis only. It never calls X APIs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_DATA_PATH = ROOT / "data" / "villain_context_mismatch_gate.json"

REALITY_CONTEXT_TERMS = [
    "昨日",
    "今日",
    "明日",
    "今夜",
    "今朝",
    "さっき",
    "集会",
    "現場",
    "イベント",
    "発表",
    "リリース",
    "開催",
    "会場",
]

TEMPORAL_TERMS = ["昨日", "今日", "明日", "今夜", "今朝", "さっき"]
REALITY_EVENT_TERMS = ["集会", "現場", "イベント", "発表", "リリース", "開催", "会場"]

TOPIC_GROUPS = {
    "gathering_event": ["集会", "現場", "イベント", "開催", "会場", "集ま", "人が集ま"],
    "announcement": ["発表", "リリース", "公開", "告知"],
    "temporal_claim": ["昨日", "今日", "明日", "今夜", "今朝", "さっき"],
}

IMAGE_TOPIC_TERMS = {
    "gathering_event": ["集会", "現場", "イベント", "会場", "meeting", "community", "gather", "crowd", "group"],
    "announcement": ["発表", "リリース", "公開", "告知", "release", "announce"],
}


def first_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def matched_terms(text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if term and term in text]


def context_terms(text: str) -> list[str]:
    return matched_terms(text, REALITY_CONTEXT_TERMS)


def temporal_reality_terms(text: str) -> dict[str, list[str]]:
    temporal = matched_terms(text, TEMPORAL_TERMS)
    events = matched_terms(text, REALITY_EVENT_TERMS)
    return {"temporal_terms": temporal, "event_terms": events}


def has_temporal_reality_claim(text: str) -> bool:
    terms = temporal_reality_terms(text)
    return bool(terms["temporal_terms"] and terms["event_terms"])


def topic_groups_for_text(text: str) -> list[str]:
    groups: list[str] = []
    for group, terms in TOPIC_GROUPS.items():
        if matched_terms(text, terms):
            groups.append(group)
    return groups


def image_metadata_text(image: dict[str, Any]) -> str:
    values = []
    for key in ("file_path", "absolute_path", "image_type", "reason", "prompt_family", "composition", "layout"):
        value = image.get(key)
        if value:
            values.append(str(value))
    return " ".join(values).lower()


def context_evidence_verified(candidate: dict[str, Any]) -> bool:
    evidence = candidate.get("context_evidence", {})
    review = candidate.get("review", {})
    return bool(
        evidence.get("verified")
        or evidence.get("source_file")
        or candidate.get("manual_context_approved")
        or review.get("explicit_context_approval")
    )


def context_gate_blockers(candidate: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    text = candidate.get("text", "")
    terms = context_terms(text)
    temporal_reality = temporal_reality_terms(text)
    verified = context_evidence_verified(candidate)
    blockers: list[str] = []
    if has_temporal_reality_claim(text) and not verified:
        blockers.append("temporal_context_unverified")
    return blockers, {
        "terms": terms,
        **temporal_reality,
        "context_evidence_verified": verified,
        "requires_evidence": has_temporal_reality_claim(text),
    }


def topic_image_pairing_blockers(text: str, image: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    groups = topic_groups_for_text(text)
    metadata = image_metadata_text(image)
    blockers: list[str] = []
    checks: dict[str, Any] = {"topic_groups": groups, "image_metadata": metadata[:240], "matched_image_terms": {}}
    if not groups:
        return blockers, checks
    if image.get("ready") is not True:
        blockers.append("topic_image_pairing_unverified")
        return blockers, checks
    for group in groups:
        expected = IMAGE_TOPIC_TERMS.get(group, [])
        if not expected:
            continue
        matched = [term for term in expected if term.lower() in metadata]
        checks["matched_image_terms"][group] = matched
        if not matched:
            blockers.append("topic_image_pairing_mismatch")
    return sorted(set(blockers)), checks


def deleted_records(outcomes_db: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        record
        for record in outcomes_db.get("outcomes", [])
        if record.get("human_review", {}).get("keep") is False
    ]


def deleted_learning_blockers(
    candidate: dict[str, Any],
    image: dict[str, Any],
    outcomes_db: dict[str, Any],
) -> tuple[list[str], list[dict[str, Any]]]:
    blockers: list[str] = []
    matches: list[dict[str, Any]] = []
    source_id = candidate.get("source_id", "")
    text = candidate.get("text", "")
    line = first_line(text)
    groups = set(topic_groups_for_text(text))
    image_path = image.get("absolute_path") or image.get("file_path", "")
    prompt_family = image.get("prompt_family", "")

    for record in deleted_records(outcomes_db):
        reasons: list[str] = []
        if source_id and source_id == record.get("candidate_id"):
            reasons.append("deleted_candidate_blacklist")
        if image_path and image_path in {record.get("image_used"), record.get("image_used", "").replace(str(ROOT), "/Users/raindog/Projects/villain-auto-posting")}:
            reasons.append("deleted_image_cooldown")
        if prompt_family and prompt_family == record.get("prompt_family"):
            reasons.append("deleted_prompt_family_cooldown")
        if line and line == first_line(record.get("text", "")):
            reasons.append("deleted_text_near_match")
        if groups and record.get("topic_cluster") == "community_gathering_signal" and "gathering_event" in groups:
            reasons.append("deleted_topic_context_cooldown")
        if reasons:
            blockers.extend(reasons)
            matches.append(
                {
                    "tweet_id": record.get("tweet_id", ""),
                    "execution_id": record.get("execution_id", ""),
                    "candidate_id": record.get("candidate_id", ""),
                    "image_used": record.get("image_used", ""),
                    "prompt_family": record.get("prompt_family", ""),
                    "topic_cluster": record.get("topic_cluster", ""),
                    "delete_reason": record.get("human_review", {}).get("delete_reason", ""),
                    "reasons": sorted(set(reasons)),
                }
            )
    return sorted(set(blockers)), matches


def write_gate_report(data: dict[str, Any]) -> None:
    REPORT_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
