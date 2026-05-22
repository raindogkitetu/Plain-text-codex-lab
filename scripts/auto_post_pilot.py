#!/usr/bin/env python3
"""Build a Villain limited live pilot/execution plan.

Pilot v1 supports DRY_RUN, LIVE_PILOT, and LIMITED_LIVE_EXECUTION planning
modes. It reads local candidate/strategy JSON, chooses up to 3 supervised posting
candidates, and writes a report. This script does not contain an X API write
adapter; live modes arm a limited execution manifest only after hard gates pass.
It never performs unlimited posting. It also stores only lightweight note seeds,
not note drafts.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from required_token_layer import (
    MANDATORY_FOOTER,
    extract_passcode,
    normalize_mandatory_tokens,
    passcode_exists,
    verification_summary,
)
from media_deduplication import (
    MEDIA_REUSE_COOLDOWN_DAYS,
    build_recent_media_history,
    media_reuse_check,
)
from context_mismatch_gate import (
    context_gate_blockers,
    deleted_learning_blockers,
    topic_image_pairing_blockers,
    write_gate_report,
)
from post_quality_os import evaluate_candidate


ROOT = Path(__file__).resolve().parents[1]
STREAM_PATH = ROOT / "data" / "villain_candidate_stream.json"
DAILY_SELECTION_PATH = ROOT / "data" / "villain_daily_selection.json"
NOVELTY_PATH = ROOT / "data" / "villain_novelty_engine.json"
IMAGE_STRATEGY_PATH = ROOT / "data" / "villain_image_strategy.json"
SCORING_RULES_PATH = ROOT / "data" / "villain_post_scoring_rules.json"
GENERATED_PATH = ROOT / "data" / "villain_generated_candidates.json"
MANUAL_RESULTS_PATH = ROOT / "data" / "manual_post_results.json"
OUTCOMES_PATH = ROOT / "data" / "villain_post_outcomes.json"
OUTPUT_PATH = ROOT / "data" / "villain_auto_post_pilot.json"
REPORT_PATH = ROOT / "reports" / "villain_auto_post_pilot.md"
MEDIA_HISTORY_PATH = ROOT / "data" / "recent_media_history.json"
QUALITY_POLICY_PATH = ROOT / "data" / "villain_post_quality_os.json"

JST = ZoneInfo("Asia/Tokyo")
PILOT_VERSION = "1.3.0"
TARGET_MIN = 3
TARGET_MAX = 3
MAX_POSTS_PER_DAY = 3
COOLDOWN_BETWEEN_POSTS_MINUTES = 120
MIN_NOVELTY_FOR_PILOT = 40
VALID_MODES = {"DRY_RUN", "LIVE_PILOT", "LIMITED_LIVE_EXECUTION", "PLAN_ONLY"}

CATEGORY_ALIASES = {
    "COMMUNITY_INFO": "community_info",
    "POSTER_SUMMARY": "poster_summary",
    "CULTURE_OBSERVER": "culture_observer",
    "ABOUT_WORDING": "about_wording",
    "SILENT_DOMINANCE": "silent_dominance",
    "EMOTIONAL_DAMAGE": "culture_observer",
    "RELATIONSHIP_POWER": "culture_observer",
}

SLOT_ORDER = ["daytime", "night", "late_night"]
SLOT_EXPECTED_TYPE = {
    "morning": "instant_reaction_or_light_residual",
    "daytime": "profile_pull_or_explainer",
    "night": "residual_growth",
    "late_night": "residual_growth_or_community_resonance",
}
SLOT_FALLBACK = {
    "morning": "hold_for_daytime_or_rewrite_lighter",
    "daytime": "hold_for_night_if_context_is_too_heavy",
    "night": "fallback_to_poster_summary_image_ready",
    "late_night": "fallback_to_best_image_ready_culture_or_community",
}

LIVE_PILOT_MODES = {"LIVE_PILOT"}
LIVE_EXECUTION_MODES = {"LIMITED_LIVE_EXECUTION"}
LIVE_MODES = LIVE_PILOT_MODES | LIVE_EXECUTION_MODES


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def now_jst() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def normalize_category(category: str) -> str:
    if not category:
        return "unknown"
    return CATEGORY_ALIASES.get(category, category.lower())


def first_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def compact_preview(text: str, limit: int = 120) -> str:
    compact = " / ".join(line.strip() for line in text.splitlines() if line.strip())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def manual_texts_and_images(manual_db: dict[str, Any]) -> tuple[set[str], set[str], set[str]]:
    posted_texts: set[str] = set()
    first_lines: set[str] = set()
    image_paths: set[str] = set()
    for item in manual_db.get("manual_post_results", []):
        if item.get("post_url"):
            text = item.get("post_text", "")
            if text:
                posted_texts.add(text.strip())
                line = first_line(text)
                if line:
                    first_lines.add(line)
        notes = item.get("manual_notes", "")
        match = re.search(r"image_used=([^\n]+)", notes)
        if match:
            image_paths.add(match.group(1).strip())
    return posted_texts, first_lines, image_paths


def parse_jst(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=JST)
    return parsed.astimezone(JST)


def today_post_count(manual_db: dict[str, Any]) -> int:
    today = datetime.now(JST).date()
    count = 0
    for item in manual_db.get("manual_post_results", []):
        if not item.get("post_url"):
            continue
        posted_at = parse_jst(item.get("post_datetime_jst", ""))
        if posted_at and posted_at.date() == today:
            count += 1
    return count


def is_success_outcome(record: dict[str, Any]) -> bool:
    return (
        bool(record.get("tweet_id"))
        and bool(record.get("url"))
        and bool(record.get("posted_at_jst"))
        and record.get("status") == "SUCCESS"
    )


def outcome_successes_today(outcomes_db: dict[str, Any]) -> int:
    today = datetime.now(JST).date()
    count = 0
    for record in outcomes_db.get("outcomes", []):
        if not is_success_outcome(record):
            continue
        posted_at = parse_jst(record.get("posted_at_jst", ""))
        if posted_at and posted_at.date() == today:
            count += 1
    return count


def next_slot_time(slot: str, already_planned: int) -> str:
    now = datetime.now(JST)
    slot_hours = {
        "morning": 8,
        "daytime": 13,
        "night": 20,
        "late_night": 23,
    }
    planned = now.replace(hour=slot_hours.get(slot, now.hour), minute=0, second=0, microsecond=0)
    if planned <= now:
        planned = now + timedelta(minutes=COOLDOWN_BETWEEN_POSTS_MINUTES * max(already_planned, 1))
    return planned.isoformat(timespec="minutes")


def planned_datetime_for_slot(slot: str, already_planned: int) -> datetime:
    now = datetime.now(JST)
    slot_hours = {
        "morning": 8,
        "daytime": 13,
        "night": 20,
        "late_night": 23,
    }
    planned = now.replace(hour=slot_hours.get(slot, now.hour), minute=0, second=0, microsecond=0)
    if planned <= now:
        planned = now + timedelta(minutes=COOLDOWN_BETWEEN_POSTS_MINUTES * max(already_planned, 1))
    return planned


def assign_publish_times(items: list[dict[str, Any]]) -> None:
    previous: datetime | None = None
    for index, item in enumerate(items):
        planned = planned_datetime_for_slot(item.get("slot", "night"), index)
        if previous is not None:
            minimum = previous + timedelta(minutes=COOLDOWN_BETWEEN_POSTS_MINUTES)
            if planned < minimum:
                planned = minimum
        item["planned_publish_after_jst"] = planned.isoformat(timespec="minutes")
        previous = planned


def image_recommendations_by_category(image_db: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for item in image_db.get("next_image_recommendations", []):
        category = normalize_category(item.get("category", ""))
        result.setdefault(category, []).append(item)
    for image in image_db.get("local_image_inventory", []):
        for category in image.get("recommended_for_categories", []):
            result.setdefault(normalize_category(category), []).append(
                {
                    "file": image.get("file", ""),
                    "category": normalize_category(category),
                    "rank": 10 if image.get("priority") == "S" else 50,
                    "reason": image.get("best_use", ""),
                    "image_type": image.get("primary_type", ""),
                    "priority": image.get("priority", ""),
                }
            )
    return result


def choose_image(
    category: str,
    image_hint: str,
    image_by_category: dict[str, list[dict[str, Any]]],
    used_images: set[str],
) -> dict[str, Any]:
    candidates = list(image_by_category.get(category, []))
    if not candidates and category == "culture_observer":
        candidates = list(image_by_category.get("poster_summary", []))
    if not candidates and category == "apparel_focus":
        candidates = list(image_by_category.get("poster_summary", []))
    candidates = sorted(candidates, key=lambda item: item.get("rank", 99))
    for item in candidates:
        file_path = item.get("file", "")
        if not file_path:
            continue
        abs_path = ROOT / file_path
        if str(abs_path) in used_images or file_path in used_images:
            continue
        if abs_path.exists():
            return {
                "ready": True,
                "file_path": file_path,
                "absolute_path": str(abs_path),
                "image_type": item.get("image_type") or category,
                "reason": item.get("reason") or image_hint,
            }
    return {
        "ready": False,
        "file_path": "",
        "absolute_path": "",
        "image_type": "",
        "reason": image_hint or "no_image_ready_candidate",
    }


def generated_candidates(generated_db: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for candidate in generated_db.get("candidates", []):
        category = normalize_category(candidate.get("category", ""))
        passcode = candidate.get("passcode") or extract_passcode(candidate.get("text", ""))
        normalized_text = normalize_mandatory_tokens(candidate.get("text", ""), passcode=passcode or None)
        items.append(
            {
                "source": "generated_candidates",
                "source_id": candidate.get("candidate_id", ""),
                "status": "fresh",
                "daily_selection_selected": True,
                "category": category,
                "passcode": passcode,
                "text": normalized_text,
                "token_verification": verification_summary(normalized_text),
                "image_hint": candidate.get("image_hint", ""),
                "score": candidate.get("quality_prediction", 0),
                "risk": candidate.get("risk_prediction", "medium"),
                "novelty_score": None,
                "remixability_score": None,
                "already_posted": False,
                "why": candidate.get("why_this_might_work", ""),
            }
        )
    return items


def stream_candidates(stream_db: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in stream_db.get("stream", []):
        status = item.get("status", "")
        if status in {"posted", "archived", "stale"}:
            continue
        scores = item.get("scores", {})
        image = item.get("image", {})
        passcode = item.get("passcode") or extract_passcode(item.get("text", ""))
        normalized_text = normalize_mandatory_tokens(item.get("text", ""), passcode=passcode or None)
        items.append(
            {
                "source": "candidate_stream",
                "source_id": item.get("stream_id", ""),
                "status": status or "fresh",
                "daily_selection_selected": item.get("review", {}).get("human_decision") in {"approved", "timing"}
                or status in {"fresh", "approved", "aging"},
                "category": normalize_category(item.get("category", "")),
                "passcode": passcode,
                "text": normalized_text,
                "token_verification": verification_summary(normalized_text),
                "image_hint": image.get("rights_notes", ""),
                "image": image,
                "score": scores.get("quality_prediction") or 80,
                "risk": scores.get("risk_prediction") or "medium",
                "novelty_score": scores.get("novelty_score"),
                "remixability_score": scores.get("remixability_score"),
                "already_posted": bool(item.get("post_execution", {}).get("posted_url")),
                "why": item.get("learning", {}).get("manual_notes", ""),
            }
        )
    return items


def novelty_floor(candidate: dict[str, Any], novelty_db: dict[str, Any]) -> int:
    explicit = candidate.get("novelty_score")
    if isinstance(explicit, (int, float)):
        return int(explicit)
    category = candidate.get("category")
    text = candidate.get("text", "")
    score = 62
    if category in {"culture_observer", "community_info"}:
        score += 8
    if any(word in text for word in ("机", "レシート", "coffee", "集会のあと", "片付", "残骸")):
        score += 12
    if any(word in first_line(text) for word in ("説明より", "気づくと", "残る")):
        score -= 5
    if novelty_db.get("status") == "design_only":
        score += 0
    return max(0, min(100, score))


def novelty_saturation_flags(candidate: dict[str, Any], image: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    text = candidate.get("text", "")
    image_text = ""
    if image.get("ready"):
        image_text = " ".join(str(image.get(key, "")) for key in ("file_path", "image_type", "reason")).lower()
    joined = f"{text}\n{image_text}".lower()
    if "hoodie" in joined or "パーカー" in joined or "black" in joined or "黒" in joined:
        flags.append("same_black_hoodie")
    if any(word in joined for word in ("night", "夜", "neon", "ネオン", "city", "街", "rain", "雨")):
        flags.append("same_city_night")
    if any(word in joined for word in ("back view", "背中", "後ろ姿")):
        flags.append("same_back_view")
    if any(word in first_line(text) for word in ("説明より", "気づくと", "残る", "ちょっと変")):
        flags.append("repeated_phrase")
    nonempty_lines = [line for line in text.splitlines() if line.strip()]
    if 5 <= len(nonempty_lines) <= 9 and any(word in text for word in ("でも", "だいたい", "たぶん")):
        flags.append("repeated_structure")
    if any(word in joined for word in ("overpolished", "too clean", "too_symmetric", "generic_ai_visual")):
        flags.append("overpolished")
    return flags


def novelty_penalty(flags: list[str]) -> int:
    penalties = {
        "same_black_hoodie": 8,
        "same_city_night": 8,
        "same_back_view": 8,
        "repeated_phrase": 10,
        "repeated_structure": 4,
        "overpolished": 10,
    }
    return sum(penalties.get(flag, 0) for flag in flags)


def remixability_score(candidate: dict[str, Any], image: dict[str, Any], novelty_db: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    explicit = candidate.get("remixability_score")
    if isinstance(explicit, (int, float)):
        return int(explicit), {"source": "candidate_score", "signals": [], "components": {}}

    text = candidate.get("text", "")
    category = candidate.get("category", "")
    line = first_line(text)
    image_ready = image.get("ready") is True
    weights = novelty_db.get("remixability_score_weights", {})
    components: dict[str, int] = {}
    signals: list[str] = []

    quoteable = bool(line) and len(line) <= 24
    components["quoteability"] = weights.get("quoteability", 16) if quoteable else 6
    if quoteable:
        signals.append("one_sentence_complete")

    reusable_visual = image_ready and category in {"community_info", "poster_summary", "culture_observer"}
    components["reusable_visual"] = weights.get("reusable_visual", 18) if reusable_visual else (8 if image_ready else 0)
    if reusable_visual:
        signals.append("image_stands_alone")

    community_repost = category in {"community_info", "culture_observer"} or any(
        word in text for word in ("集会", "集ま", "誰が着て", "人が")
    )
    components["community_reposting_probability"] = weights.get("community_reposting_probability", 18) if community_repost else 7
    if community_repost:
        signals.append("community_reposting_probability")

    identity = any(word in text for word in ("$villain", "Villain", "#villain")) and category in {
        "community_info",
        "poster_summary",
        "culture_observer",
    }
    components["identity_attachment"] = weights.get("identity_attachment", 16) if identity else 8
    if identity:
        signals.append("identity_badge_feel")

    nonempty_lines = [item for item in text.splitlines() if item.strip()]
    portable = 3 <= len(nonempty_lines) <= 9 and len(text) <= 240
    components["phrase_portability"] = weights.get("phrase_portability", 14) if portable else 6
    if portable:
        signals.append("someone_else_can_say_it")

    screenshot_fit = image_ready or quoteable
    components["screenshot_reuse_fit"] = weights.get("screenshot_reuse_fit", 10) if screenshot_fit else 4
    if screenshot_fit:
        signals.append("screenshot_friendly")

    cropable = image_ready and image.get("file_path")
    components["cropability"] = weights.get("cropability", 8) if cropable else 2
    if cropable:
        signals.append("cropability")

    penalty = 0
    joined = f"{text}\n{image.get('reason', '')}".lower()
    if any(word in joined for word in ("overpolished", "too clean", "too_symmetric", "generic_ai_visual")):
        penalty += 10
    if len(text) > 260:
        penalty += 8

    score = max(0, min(100, sum(components.values()) - penalty))
    return score, {"source": "computed", "signals": sorted(set(signals)), "components": components, "penalty": penalty}


def repeated_topic(candidate: dict[str, Any], posted_first_lines: set[str]) -> bool:
    line = first_line(candidate.get("text", ""))
    if not line:
        return False
    if line in posted_first_lines:
        return True
    repeated_fragments = ("説明より", "気づくと", "残る", "ちょっと変")
    return any(fragment in line and any(fragment in posted for posted in posted_first_lines) for fragment in repeated_fragments)


def slot_fit(candidate: dict[str, Any], slot: str, daily_db: dict[str, Any]) -> int:
    category = candidate.get("category", "")
    best = daily_db.get("slot_definitions", {}).get(slot, {}).get("best_categories", [])
    best = [normalize_category(item) for item in best]
    if category in best:
        return 14
    if slot in {"night", "late_night"} and category in {"culture_observer", "poster_summary", "community_info"}:
        return 10
    if slot in {"morning", "daytime"} and category in {"explainer", "poster_summary", "about_wording"}:
        return 10
    return 4


def expected_type_for(category: str, slot: str) -> str:
    if category == "community_info":
        return "community_resonance" if slot in {"daytime", "late_night"} else "residual_growth"
    if category == "culture_observer":
        return "residual_growth_or_profile_pull"
    if category == "poster_summary":
        return "residual_growth"
    if category in {"explainer", "about_wording"}:
        return "instant_reaction_or_profile_pull"
    return SLOT_EXPECTED_TYPE.get(slot, "pilot_test")


def note_seed_for(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "why_posted": item.get("reason", ""),
        "expected_reaction": item.get("expected_type", "pilot_learning"),
        "human_observation_pending": True,
        "lesson_for_later": "Record actual X reaction after posting; do not draft note yet.",
    }


def eligibility(
    candidate: dict[str, Any],
    image: dict[str, Any],
    novelty_score: int,
    mode: str,
    posted_texts: set[str],
    posted_first_lines: set[str],
    used_images: set[str],
    media_history: dict[str, Any],
    outcomes_db: dict[str, Any],
) -> tuple[bool, list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []
    text = candidate.get("text", "").strip()
    risk = candidate.get("risk", "medium")
    score = int(candidate.get("score") or 0)
    image_ready = image.get("ready") is True
    same_image = image.get("absolute_path") in used_images or image.get("file_path") in used_images
    media_reuse = media_reuse_check(image, media_history) if image.get("ready") else {"blockers": [], "matches": []}
    context_blockers, _context_check = context_gate_blockers(candidate)
    pairing_blockers, _pairing_check = topic_image_pairing_blockers(text, image)
    deleted_blockers, _deleted_matches = deleted_learning_blockers(candidate, image, outcomes_db)
    repeated = repeated_topic(candidate, posted_first_lines)
    required_tokens_verified = candidate.get("token_verification", {}).get("valid_after") is True
    passcode = candidate.get("passcode") or extract_passcode(text)

    if not candidate.get("daily_selection_selected", False):
        blockers.append("daily_selection_selected_false")
    if not required_tokens_verified:
        blockers.append("required_tokens_not_verified")
    if not passcode:
        blockers.append("passcode_missing")
    elif not passcode_exists(passcode):
        blockers.append("passcode_not_in_db")
    if score < 80:
        blockers.append("score_below_80")
    if risk == "high":
        blockers.append("risk_high")
    if candidate.get("already_posted") or text in posted_texts:
        blockers.append("already_posted")
    if repeated:
        blockers.append("repeated_topic_penalty")
    if same_image:
        blockers.append("same_image_cooldown")
    for blocker in media_reuse.get("blockers", []):
        if blocker in {
            "same_media_path",
            "same_media_sha256",
            "near_duplicate_media_phash",
            "same_prompt_family_cooldown",
        }:
                blockers.append(blocker)
    blockers.extend(context_blockers)
    blockers.extend(blocker for blocker in pairing_blockers if blocker == "topic_image_pairing_mismatch")
    blockers.extend(
        blocker
        for blocker in deleted_blockers
        if blocker in {"deleted_topic_context_cooldown", "deleted_text_near_match"}
    )
    if novelty_score < MIN_NOVELTY_FOR_PILOT:
        blockers.append("novelty_too_low")
    if not image_ready:
        warnings.append("image_not_ready_text_only_possible")
        if candidate.get("category") in {"community_info", "poster_summary", "culture_observer"}:
            warnings.append("primary_category_prefers_image")
    if len(text) > 260:
        warnings.append("text_long_for_pilot")
    if media_reuse.get("matches"):
        warnings.append("recent_media_reuse_match_found")
    if context_blockers:
        warnings.append("reality_context_requires_evidence")
    if pairing_blockers:
        warnings.append("topic_image_pairing_requires_review")
    if deleted_blockers:
        warnings.append("near_deleted_or_dropped_post")
    return not blockers, blockers, warnings


def build_plan(mode: str) -> dict[str, Any]:
    if mode == "PLAN_ONLY":
        mode = "DRY_RUN"
    stream_db = read_json(STREAM_PATH)
    daily_db = read_json(DAILY_SELECTION_PATH)
    novelty_db = read_json(NOVELTY_PATH)
    image_db = read_json(IMAGE_STRATEGY_PATH)
    scoring_db = read_json(SCORING_RULES_PATH)
    quality_policy = read_json(QUALITY_POLICY_PATH)
    generated_db = read_json(GENERATED_PATH)
    manual_db = read_json(MANUAL_RESULTS_PATH)
    outcomes_db = read_json(OUTCOMES_PATH)
    posted_texts, posted_first_lines, posted_images = manual_texts_and_images(manual_db)
    media_history = build_recent_media_history(write=True)
    posts_today = outcome_successes_today(outcomes_db)
    remaining_today = max(0, MAX_POSTS_PER_DAY - posts_today)
    image_by_category = image_recommendations_by_category(image_db)

    raw_candidates = stream_candidates(stream_db)
    source_mode = "candidate_stream"
    if not raw_candidates:
        raw_candidates = generated_candidates(generated_db)
        source_mode = "generated_candidates_fallback"

    used_images = set(posted_images)
    selected_ids: set[str] = set()
    pilot_items: list[dict[str, Any]] = []
    rejected_items: list[dict[str, Any]] = []

    for slot in SLOT_ORDER:
        slot_options: list[dict[str, Any]] = []
        for candidate in raw_candidates:
            if candidate.get("source_id") in selected_ids:
                continue
            category = candidate.get("category", "unknown")
            image = candidate.get("image") or choose_image(
                category,
                candidate.get("image_hint", ""),
                image_by_category,
                used_images,
            )
            if image.get("file_path") and not image.get("absolute_path"):
                image["absolute_path"] = str(ROOT / image["file_path"])
                image["ready"] = Path(image["absolute_path"]).exists()
            novelty_score = novelty_floor(candidate, novelty_db)
            saturation_flags = novelty_saturation_flags(candidate, image)
            adjusted_novelty = max(0, novelty_score - novelty_penalty(saturation_flags))
            remix_score, remix = remixability_score(candidate, image, novelty_db)
            passcode = candidate.get("passcode") or extract_passcode(candidate.get("text", ""))
            normalized_text = normalize_mandatory_tokens(candidate.get("text", ""), passcode=passcode or None)
            ok, blockers, warnings = eligibility(
                candidate,
                image,
                adjusted_novelty,
                mode,
                posted_texts,
                posted_first_lines,
                used_images,
                media_history,
                outcomes_db,
            )
            media_reuse = media_reuse_check(image, media_history) if image.get("ready") else {"signature": {}, "blockers": [], "matches": []}
            context_blockers, context_check = context_gate_blockers({**candidate, "text": normalized_text})
            pairing_blockers, pairing_check = topic_image_pairing_blockers(normalized_text, image)
            deleted_blockers, deleted_matches = deleted_learning_blockers({**candidate, "text": normalized_text}, image, outcomes_db)
            fit = slot_fit(candidate, slot, daily_db)
            pilot_score = int(candidate.get("score") or 0) + adjusted_novelty + fit
            pilot_score += remix_score
            if image.get("ready"):
                pilot_score += 16
            if candidate.get("risk") == "low":
                pilot_score += 10
            if candidate.get("category") in {"culture_observer", "poster_summary", "community_info"}:
                pilot_score += 8
            option = {
                "slot": slot,
                "source": candidate.get("source"),
                "source_id": candidate.get("source_id"),
                "category": category,
                "passcode": passcode,
                "text": normalized_text,
                "text_preview": compact_preview(normalized_text),
                "token_verification": {
                    "required_layer": "Required Token Layer v1",
                    "mandatory_footer_order": MANDATORY_FOOTER,
                    **verification_summary(normalized_text),
                },
                "image": image,
                "score": int(candidate.get("score") or 0),
                "risk": candidate.get("risk", "medium"),
                "novelty_score": adjusted_novelty,
                "raw_novelty_score": novelty_score,
                "remixability_score": remix_score,
                "remixability": remix,
                "media_deduplication": media_reuse,
                "context_mismatch_gate": {
                    "blockers": sorted(set(context_blockers + pairing_blockers)),
                    "context_check": context_check,
                    "pairing_check": pairing_check,
                },
                "deleted_learning_gate": {
                    "blockers": deleted_blockers,
                    "matches": deleted_matches,
                },
                "saturation_flags": saturation_flags,
                "pilot_score": pilot_score,
                "eligible": ok,
                "blockers": blockers,
                "warnings": warnings,
                "reason": candidate.get("why") or "fits pilot density test",
                "expected_type": expected_type_for(category, slot),
                "fallback_action": SLOT_FALLBACK.get(slot, "hold_for_human_review"),
            }
            quality_review = evaluate_candidate(option, outcomes_db, quality_policy)
            option["quality_review"] = quality_review
            if quality_review.get("blockers"):
                option["blockers"] = sorted(set(option["blockers"] + quality_review.get("blockers", [])))
                option["eligible"] = False
                ok = False
            if quality_review.get("warnings"):
                option["warnings"] = sorted(set(option["warnings"] + quality_review.get("warnings", [])))
            if ok:
                slot_options.append(option)
            else:
                rejected_items.append(option)
        if slot_options:
            chosen = sorted(slot_options, key=lambda item: item["pilot_score"], reverse=True)[0]
            selected_ids.add(chosen["source_id"])
            if chosen.get("image", {}).get("file_path"):
                used_images.add(chosen["image"]["file_path"])
                used_images.add(chosen["image"].get("absolute_path", ""))
            pilot_items.append(chosen)

    # If fewer than the target minimum are available, add eligible backups from
    # the remaining pool regardless of slot fit. This keeps pilot mode from
    # stopping too early while still respecting hard blockers.
    if len(pilot_items) < TARGET_MIN:
        for candidate in raw_candidates:
            if candidate.get("source_id") in selected_ids:
                continue
            category = candidate.get("category", "unknown")
            image = candidate.get("image") or choose_image(category, candidate.get("image_hint", ""), image_by_category, used_images)
            novelty_score = novelty_floor(candidate, novelty_db)
            saturation_flags = novelty_saturation_flags(candidate, image)
            adjusted_novelty = max(0, novelty_score - novelty_penalty(saturation_flags))
            remix_score, remix = remixability_score(candidate, image, novelty_db)
            ok, blockers, warnings = eligibility(candidate, image, adjusted_novelty, mode, posted_texts, posted_first_lines, used_images, media_history, outcomes_db)
            if not ok:
                continue
            media_reuse = media_reuse_check(image, media_history) if image.get("ready") else {"signature": {}, "blockers": [], "matches": []}
            slot = "daytime"
            passcode = candidate.get("passcode") or extract_passcode(candidate.get("text", ""))
            normalized_text = normalize_mandatory_tokens(candidate.get("text", ""), passcode=passcode or None)
            context_blockers, context_check = context_gate_blockers({**candidate, "text": normalized_text})
            pairing_blockers, pairing_check = topic_image_pairing_blockers(normalized_text, image)
            deleted_blockers, deleted_matches = deleted_learning_blockers({**candidate, "text": normalized_text}, image, outcomes_db)
            pilot_items.append(
                {
                    "slot": slot,
                    "source": candidate.get("source"),
                    "source_id": candidate.get("source_id"),
                    "category": category,
                    "passcode": passcode,
                    "text": normalized_text,
                    "text_preview": compact_preview(normalized_text),
                    "token_verification": {
                        "required_layer": "Required Token Layer v1",
                        "mandatory_footer_order": MANDATORY_FOOTER,
                        **verification_summary(normalized_text),
                    },
                    "image": image,
                    "score": int(candidate.get("score") or 0),
                    "risk": candidate.get("risk", "medium"),
                    "novelty_score": adjusted_novelty,
                    "raw_novelty_score": novelty_score,
                    "remixability_score": remix_score,
                    "remixability": remix,
                    "media_deduplication": media_reuse,
                    "context_mismatch_gate": {
                        "blockers": sorted(set(context_blockers + pairing_blockers)),
                        "context_check": context_check,
                        "pairing_check": pairing_check,
                    },
                    "deleted_learning_gate": {
                        "blockers": deleted_blockers,
                        "matches": deleted_matches,
                    },
                    "saturation_flags": saturation_flags,
                    "pilot_score": int(candidate.get("score") or 0) + adjusted_novelty + remix_score,
                    "eligible": True,
                    "blockers": blockers,
                    "warnings": warnings + ["backup_slot_selected_due_to_low_plan_count"],
                    "reason": candidate.get("why") or "backup selected to keep pilot density",
                    "expected_type": expected_type_for(category, slot),
                    "fallback_action": "hold_for_human_review",
                }
            )
            quality_review = evaluate_candidate(pilot_items[-1], outcomes_db, quality_policy)
            pilot_items[-1]["quality_review"] = quality_review
            if quality_review.get("blockers"):
                pilot_items[-1]["blockers"] = sorted(set(pilot_items[-1]["blockers"] + quality_review.get("blockers", [])))
                pilot_items[-1]["eligible"] = False
                rejected_items.append(pilot_items.pop())
                continue
            if quality_review.get("warnings"):
                pilot_items[-1]["warnings"] = sorted(set(pilot_items[-1]["warnings"] + quality_review.get("warnings", [])))
            selected_ids.add(candidate.get("source_id"))
            if len(pilot_items) >= TARGET_MIN:
                break

    pilot_items = pilot_items[: min(TARGET_MAX, remaining_today if mode in LIVE_MODES else TARGET_MAX)]
    assign_publish_times(pilot_items)
    for item in pilot_items:
        item["post_after_publish_review"] = True
        item["manual_override_allowed"] = True
        item["delete_if_needed"] = True
        item["required_tokens_verified"] = item.get("token_verification", {}).get("valid_after") is True
        item["execution_gate"] = {
            "max_posts_per_day_ok": remaining_today > 0,
            "cooldown_between_posts_minutes": COOLDOWN_BETWEEN_POSTS_MINUTES,
            "risk_not_high": item.get("risk") != "high",
            "already_posted_false": "already_posted" not in item.get("blockers", []),
            "same_image_cooldown_ok": "same_image_cooldown" not in item.get("blockers", []),
            "media_reuse_cooldown_ok": not any(
                blocker in item.get("blockers", [])
                for blocker in (
                    "same_media_path",
                    "same_media_sha256",
                    "near_duplicate_media_phash",
                    "same_prompt_family_cooldown",
                )
            ),
            "context_evidence_ok": "temporal_context_unverified" not in item.get("blockers", []),
            "topic_image_pairing_ok": "topic_image_pairing_mismatch" not in item.get("blockers", [])
            and "topic_image_pairing_unverified" not in item.get("blockers", []),
            "deleted_learning_ok": not any(
                blocker in item.get("blockers", [])
                for blocker in (
                    "deleted_candidate_blacklist",
                    "deleted_image_cooldown",
                    "deleted_prompt_family_cooldown",
                    "deleted_text_near_match",
                    "deleted_topic_context_cooldown",
                )
            ),
            "repeated_topic_penalty_ok": "repeated_topic_penalty" not in item.get("blockers", []),
            "required_tokens_verified": item["required_tokens_verified"],
        }
        item["post_publish_learning_plan"] = {
            "analysis_after_hours": 24,
            "metrics": ["impressions", "likes", "reposts", "replies", "profile_clicks"],
            "learning_focus": ["residual_growth", "profile_clicks", "repost_reuse", "remixability"],
        }
        item["note_seed"] = note_seed_for(item)

    if mode in LIVE_EXECUTION_MODES and remaining_today <= 0:
        status = "LIMITED_LIVE_EXECUTION_BLOCKED"
    elif mode in LIVE_EXECUTION_MODES and len(pilot_items) >= 1:
        status = "LIMITED_LIVE_EXECUTION_READY"
    elif mode in LIVE_EXECUTION_MODES:
        status = "LIMITED_LIVE_EXECUTION_BLOCKED"
    elif mode in LIVE_PILOT_MODES and remaining_today <= 0:
        status = "LIVE_PILOT_BLOCKED"
    elif mode in LIVE_PILOT_MODES and len(pilot_items) >= 1:
        status = "LIMITED_LIVE_PILOT_READY"
    elif mode in LIVE_PILOT_MODES:
        status = "LIVE_PILOT_BLOCKED"
    else:
        status = "PLAN_READY" if len(pilot_items) >= TARGET_MIN else "PARTIAL_PLAN"
    warnings = []
    if source_mode == "generated_candidates_fallback":
        warnings.append("candidate_stream_empty_using_generated_candidates_fallback")
    if len(pilot_items) < TARGET_MIN:
        warnings.append("pilot_plan_below_target_minimum")
    if not any(item.get("image", {}).get("ready") for item in pilot_items):
        warnings.append("no_image_ready_items")
    if mode in LIVE_MODES and source_mode == "generated_candidates_fallback":
        warnings.append("live_pilot_using_generated_candidates_fallback_until_stream_is_populated")
    if mode in LIVE_MODES and remaining_today <= 0:
        warnings.append("max_posts_per_day_reached")
    if mode in LIVE_EXECUTION_MODES:
        warnings.append("limited_live_execution_manifest_only_no_x_write_adapter_called")

    gate_report = {
        "db_name": "Villain Context Mismatch Gate",
        "version": "1.0.0",
        "generated_at_jst": now_jst(),
        "reality_context_terms": [
            "昨日",
            "今日",
            "明日",
            "集会",
            "現場",
            "イベント",
            "発表",
        ],
        "policy": {
            "context_evidence_required": True,
            "topic_image_pairing_required": True,
            "deleted_keep_false_nearby_candidates_blocked": True,
            "x_api_write_allowed": False,
        },
        "deleted_or_dropped_sources": [
            {
                "tweet_id": record.get("tweet_id", ""),
                "execution_id": record.get("execution_id", ""),
                "candidate_id": record.get("candidate_id", ""),
                "image_used": record.get("image_used", ""),
                "prompt_family": record.get("prompt_family", ""),
                "topic_cluster": record.get("topic_cluster", ""),
                "delete_reason": record.get("human_review", {}).get("delete_reason", ""),
            }
            for record in outcomes_db.get("outcomes", [])
            if record.get("human_review", {}).get("keep") is False
        ],
        "selected_items": [
            {
                "source_id": item.get("source_id", ""),
                "blockers": item.get("blockers", []),
                "context_mismatch_gate": item.get("context_mismatch_gate", {}),
                "deleted_learning_gate": item.get("deleted_learning_gate", {}),
            }
            for item in pilot_items
        ],
        "rejected_preview": [
            {
                "source_id": item.get("source_id", ""),
                "blockers": item.get("blockers", []),
                "context_mismatch_gate": item.get("context_mismatch_gate", {}),
                "deleted_learning_gate": item.get("deleted_learning_gate", {}),
            }
            for item in rejected_items[:10]
        ],
    }
    write_gate_report(gate_report)

    return {
        "db_name": "Villain Auto Post Pilot Plan",
        "version": PILOT_VERSION,
        "status": status,
        "mode": mode,
        "generated_at_jst": now_jst(),
        "source_mode": source_mode,
        "target_post_count": {
            "min": TARGET_MIN,
            "max": TARGET_MAX,
            "actual": len(pilot_items),
        },
        "live_pilot_limits": {
            "max_posts_per_day": MAX_POSTS_PER_DAY,
            "posts_already_recorded_today": posts_today,
            "remaining_posts_today": remaining_today,
            "cooldown_between_posts_minutes": COOLDOWN_BETWEEN_POSTS_MINUTES,
        },
        "limited_live_execution": {
            "mode_enabled": mode in LIVE_EXECUTION_MODES,
            "live_execution_mode": "LIMITED_LIVE_EXECUTION",
            "execution_scope": "supervised_limited_posting_manifest",
            "posting_adapter_in_this_script": False,
            "requires_human_supervision": True,
            "max_posts_per_day": MAX_POSTS_PER_DAY,
            "cooldown_between_posts_minutes": COOLDOWN_BETWEEN_POSTS_MINUTES,
            "manual_safety": {
                "delete_if_needed": True,
                "manual_override_allowed": True,
                "post_after_publish_review": True,
            },
            "hard_blocks": [
                "risk_high",
                "already_posted",
                "same_image_cooldown",
                "same_media_path",
                "same_media_sha256",
                "near_duplicate_media_phash",
                "same_prompt_family_cooldown",
                "temporal_context_unverified",
                "topic_image_pairing_mismatch",
                "topic_image_pairing_unverified",
                "deleted_candidate_blacklist",
                "deleted_image_cooldown",
                "deleted_prompt_family_cooldown",
                "deleted_text_near_match",
                "deleted_topic_context_cooldown",
                "repeated_topic_penalty",
                "required_tokens_not_verified",
                "passcode_missing",
                "passcode_not_in_db",
                "max_posts_per_day_reached",
            ],
        },
        "safety": {
            "live_posting_allowed": mode in LIVE_MODES,
            "x_api_write_allowed_by_this_script": False,
            "upload_media_allowed_by_this_script": False,
            "create_tweet_allowed_by_this_script": False,
            "x_write_adapter_allowed_in_limited_live_execution": mode in LIVE_EXECUTION_MODES,
            "auto_posting_allowed": False,
            "would_execute_actions": [],
            "api_key_output_allowed": False,
            "env_output_allowed": False,
        },
        "pilot_policy": {
            "human_supervision_required_after_post": True,
            "post_after_publish_review": True,
            "manual_override_allowed": True,
            "delete_if_needed": True,
            "note_creation_enabled": False,
            "note_seed_only": True,
            "execution_enabled": mode in LIVE_MODES,
            "execution_enablement_requires_separate_design": mode not in LIVE_EXECUTION_MODES,
            "density_priority": "slightly_higher_than_overcautious_blocking",
            "policy_alignment": {
                "human_control": True,
                "privacy_respect": True,
                "no_spam_or_deception": True,
                "no_sensitive_personal_data_output": True,
                "source": "OpenAI usage policies effective 2025-10-29",
            },
            "hard_blocks": [
                "risk_high",
                "already_posted",
                "repeated_topic_penalty",
                "same_image_cooldown",
                "same_media_path",
                "same_media_sha256",
                "near_duplicate_media_phash",
                "same_prompt_family_cooldown",
                "temporal_context_unverified",
                "topic_image_pairing_mismatch",
                "topic_image_pairing_unverified",
                "deleted_candidate_blacklist",
                "deleted_image_cooldown",
                "deleted_prompt_family_cooldown",
                "deleted_text_near_match",
                "deleted_topic_context_cooldown",
                "required_tokens_not_verified",
                "passcode_missing",
                "passcode_not_in_db",
                "novelty_too_low",
                "score_below_80",
                "max_posts_per_day_reached",
            ],
        },
        "inputs": {
            "candidate_stream": str(STREAM_PATH.relative_to(ROOT)),
            "daily_selection": str(DAILY_SELECTION_PATH.relative_to(ROOT)),
            "novelty_engine": str(NOVELTY_PATH.relative_to(ROOT)),
            "image_strategy": str(IMAGE_STRATEGY_PATH.relative_to(ROOT)),
            "scoring_rules": str(SCORING_RULES_PATH.relative_to(ROOT)),
            "generated_candidates": str(GENERATED_PATH.relative_to(ROOT)),
            "manual_results": str(MANUAL_RESULTS_PATH.relative_to(ROOT)),
            "outcomes": str(OUTCOMES_PATH.relative_to(ROOT)),
            "recent_media_history": str(MEDIA_HISTORY_PATH.relative_to(ROOT)),
            "safe_post_executor": "scripts/safe_post_executor.py",
            "x_write_adapter": "scripts/x_write_adapter.py",
        },
        "warnings": warnings,
        "execution_manifest": [
            {
                "execution_id": f"vln-exec-{item.get('slot')}-{item.get('source_id')}",
                "slot": item.get("slot"),
                "source_id": item.get("source_id"),
                "passcode": item.get("passcode"),
                "planned_publish_after_jst": item.get("planned_publish_after_jst"),
                "ready_for_limited_live_execution": mode in LIVE_EXECUTION_MODES
                and item.get("eligible") is True
                and item.get("required_tokens_verified") is True,
                "media_reuse_cooldown_ok": item.get("execution_gate", {}).get("media_reuse_cooldown_ok", False),
                "manual_review_after_publish": True,
                "delete_if_needed": True,
                "x_api_write_called_by_this_script": False,
                "upload_media_called_by_this_script": False,
                "create_tweet_called_by_this_script": False,
            }
            for item in pilot_items
        ],
        "pilot_plan": pilot_items,
        "rejected_or_blocked_count": len(rejected_items),
        "rejected_or_blocked_preview": rejected_items[:10],
    }


def write_report(plan: dict[str, Any]) -> None:
    mode = plan.get("mode", "DRY_RUN")
    policy = plan.get("pilot_policy", {})
    limits = plan.get("live_pilot_limits", {})
    execution = plan.get("limited_live_execution", {})
    lines = [
        "# Villain Auto Post Pilot v1",
        "",
        f"- Generated at JST: `{plan.get('generated_at_jst')}`",
        f"- version: `{plan.get('version')}`",
        f"- status: `{plan.get('status')}`",
        f"- mode: `{mode}`",
        "- live posting by this script: `NOT_EXECUTED`",
        "- X API write by this script: `NOT_USED`",
        "- upload_media by this script: `NOT_EXECUTED`",
        "- create_tweet by this script: `NOT_EXECUTED`",
        f"- execution_enabled: `{str(policy.get('execution_enabled', False)).lower()}`",
        f"- source_mode: `{plan.get('source_mode')}`",
        f"- target_post_count: `{plan.get('target_post_count', {}).get('actual')}` / `{TARGET_MIN}-{TARGET_MAX}`",
        "",
        "## Pilot Policy",
        "",
        "- 完全放置BOTではなく、人間監督前提のlimited live運用。",
        "- DRY_RUNでは計画生成のみ。LIVE_PILOTでは実弾候補をarmする。",
        "- LIMITED_LIVE_EXECUTIONでは、上限内の実行manifestを作る。",
        "- このスクリプト実行中にX API writeは呼ばない。投稿adapterは別レイヤー。",
        "- risk high / 重複 / 明らかな低品質 / novelty低すぎ は止める。",
        "- required_tokens_verified=true をhard gateにする。",
        "- max_posts_per_dayとcooldown_between_postsを必ず見る。",
        "- post_after_publish_review / manual_override_allowed / delete_if_needed を前提にする。",
        "- remixabilityをscoringに入れ、画像がコミュニティ素材化する確率を見る。",
        "- image_readyを優先するが、pilotではtext-only枠も警告付きで許可可能。",
        f"- media reuse cooldownは `{MEDIA_REUSE_COOLDOWN_DAYS}` 日。phash/sha256/path/prompt familyで近似重複を止める。",
        "- note本文は作らない。各投稿に軽いnote_seedだけ残す。",
        "",
        "## OpenAI Policy Alignment",
        "",
        "- 人間の制御を残す: `post_after_publish_review`, `manual_override_allowed`, `delete_if_needed`。",
        "- プライバシーを尊重し、APIキー/.env/機微情報は出力しない。",
        "- スパム、欺瞞、なりすまし、無制限投稿を避ける。",
        "- high risk / repeated / same image / token未検証は止める。",
        "- 直近7日以内の同一/近似画像、同一構図、同一prompt familyは止める。",
        "- 昨日/今日/明日/集会/現場/イベント/発表など現実文脈語は、根拠ファイルまたは明示承認なしでは止める。",
        "- keep=false の投稿に近い candidate/image/prompt_family/topic は次候補から除外する。",
        "",
        "## Live Pilot Limits",
        "",
        f"- max_posts_per_day: `{limits.get('max_posts_per_day')}`",
        f"- posts_already_recorded_today: `{limits.get('posts_already_recorded_today')}`",
        f"- remaining_posts_today: `{limits.get('remaining_posts_today')}`",
        f"- cooldown_between_posts_minutes: `{limits.get('cooldown_between_posts_minutes')}`",
        f"- limited_live_execution_mode_enabled: `{str(execution.get('mode_enabled', False)).lower()}`",
        f"- posting_adapter_in_this_script: `{str(execution.get('posting_adapter_in_this_script', False)).lower()}`",
        "",
    ]
    if plan.get("warnings"):
        lines.extend(["## Warnings", ""])
        lines.extend(f"- `{warning}`" for warning in plan.get("warnings", []))
        lines.append("")

    lines.extend(["## Today's Pilot Plan", ""])
    if not plan.get("pilot_plan"):
        lines.extend(["- No eligible pilot items.", ""])
    for index, item in enumerate(plan.get("pilot_plan", []), 1):
        image = item.get("image", {})
        lines.extend(
            [
                f"### {index}. `{item.get('slot')}` / `{item.get('category')}`",
                "",
                f"- source: `{item.get('source')}` / `{item.get('source_id')}`",
                f"- score: `{item.get('score')}`",
                f"- risk: `{item.get('risk')}`",
                f"- passcode: `{item.get('passcode', '')}`",
                f"- passcode_exists_in_db: `{str(item.get('token_verification', {}).get('passcode_exists_in_db', False)).lower()}`",
                f"- novelty: `{item.get('novelty_score')}`",
                f"- raw_novelty: `{item.get('raw_novelty_score')}`",
                f"- remixability: `{item.get('remixability_score')}`",
                f"- remixability_signals: `{', '.join(item.get('remixability', {}).get('signals', [])) if item.get('remixability', {}).get('signals') else 'none'}`",
                f"- saturation_flags: `{', '.join(item.get('saturation_flags', [])) if item.get('saturation_flags') else 'none'}`",
                f"- pilot_score: `{item.get('pilot_score')}`",
                f"- image_ready: `{str(image.get('ready')).lower()}`",
                f"- image: `{image.get('file_path', '')}`",
                f"- media_dedup_blockers: `{', '.join(item.get('media_deduplication', {}).get('blockers', [])) if item.get('media_deduplication', {}).get('blockers') else 'none'}`",
                f"- media_dedup_matches: `{len(item.get('media_deduplication', {}).get('matches', []))}`",
                f"- context_gate_blockers: `{', '.join(item.get('context_mismatch_gate', {}).get('blockers', [])) if item.get('context_mismatch_gate', {}).get('blockers') else 'none'}`",
                f"- deleted_learning_blockers: `{', '.join(item.get('deleted_learning_gate', {}).get('blockers', [])) if item.get('deleted_learning_gate', {}).get('blockers') else 'none'}`",
                f"- quality_status: `{item.get('quality_review', {}).get('final_quality_status', 'not_run')}`",
                f"- quality_blockers: `{', '.join(item.get('quality_review', {}).get('blockers', [])) if item.get('quality_review', {}).get('blockers') else 'none'}`",
                f"- quality_warnings: `{', '.join(item.get('quality_review', {}).get('warnings', [])) if item.get('quality_review', {}).get('warnings') else 'none'}`",
                f"- required_tokens_valid_after: `{str(item.get('token_verification', {}).get('valid_after')).lower()}`",
                f"- required_tokens_verified: `{str(item.get('required_tokens_verified', False)).lower()}`",
                f"- mandatory_footer_order: `{item.get('token_verification', {}).get('mandatory_footer_order', MANDATORY_FOOTER)}`",
                f"- planned_publish_after_jst: `{item.get('planned_publish_after_jst', '')}`",
                f"- post_after_publish_review: `{str(item.get('post_after_publish_review', False)).lower()}`",
                f"- manual_override_allowed: `{str(item.get('manual_override_allowed', False)).lower()}`",
                f"- delete_if_needed: `{str(item.get('delete_if_needed', False)).lower()}`",
                f"- expected_type: `{item.get('expected_type')}`",
                f"- fallback_action: `{item.get('fallback_action')}`",
                f"- reason: {item.get('reason')}",
            ]
        )
        gate = item.get("execution_gate", {})
        lines.extend(
            [
                f"- execution_gate_required_tokens: `{str(gate.get('required_tokens_verified', False)).lower()}`",
                f"- execution_gate_same_image_cooldown_ok: `{str(gate.get('same_image_cooldown_ok', False)).lower()}`",
                f"- execution_gate_media_reuse_cooldown_ok: `{str(gate.get('media_reuse_cooldown_ok', False)).lower()}`",
                f"- execution_gate_context_evidence_ok: `{str(gate.get('context_evidence_ok', False)).lower()}`",
                f"- execution_gate_topic_image_pairing_ok: `{str(gate.get('topic_image_pairing_ok', False)).lower()}`",
                f"- execution_gate_deleted_learning_ok: `{str(gate.get('deleted_learning_ok', False)).lower()}`",
                f"- execution_gate_repeated_topic_ok: `{str(gate.get('repeated_topic_penalty_ok', False)).lower()}`",
            ]
        )
        if item.get("warnings"):
            lines.append(f"- warnings: `{', '.join(item.get('warnings', []))}`")
        note_seed = item.get("note_seed", {})
        lines.extend(
            [
                "",
                "#### note_seed",
                "",
                f"- why_posted: {note_seed.get('why_posted', '')}",
                f"- expected_reaction: `{note_seed.get('expected_reaction', '')}`",
                f"- human_observation_pending: `{str(note_seed.get('human_observation_pending', True)).lower()}`",
                f"- lesson_for_later: {note_seed.get('lesson_for_later', '')}",
            ]
        )
        lines.extend(["", "```text", item.get("text", ""), "```", ""])

    lines.extend(["## Execution Manifest", ""])
    if not plan.get("execution_manifest"):
        lines.extend(["- No execution manifest items.", ""])
    for item in plan.get("execution_manifest", []):
        lines.extend(
            [
                f"- `{item.get('execution_id')}`",
                f"  - passcode: `{item.get('passcode', '')}`",
                f"  - ready_for_limited_live_execution: `{str(item.get('ready_for_limited_live_execution')).lower()}`",
                f"  - planned_publish_after_jst: `{item.get('planned_publish_after_jst')}`",
                "  - x_api_write_called_by_this_script: `false`",
                "  - upload_media_called_by_this_script: `false`",
                "  - create_tweet_called_by_this_script: `false`",
            ]
        )
    lines.append("")

    lines.extend(
        [
            "## 24h Learning",
            "",
            "- 投稿後24hで `residual_growth`, `profile_clicks`, `repost_reuse`, `remixability` を見る。",
            "- 画像が抜粋再投稿された場合は `repost_reuse=true` として残す。",
            "- profile_clicksだけでなく、画像単体の二次拡散を学習対象にする。",
            "",
        ]
    )

    lines.extend(
        [
            "## Execution Boundary",
            "",
            "このスクリプトは選定、arm、execution manifest作成まで。X API write adapterは呼ばない。",
            "",
            "- LIVE_PILOT modeでも無制限投稿は禁止。",
            "- LIMITED_LIVE_EXECUTION modeでも、このスクリプト単体では投稿しない。",
            "- risk highは禁止。",
            "- 同一画像連投は禁止。",
            "- 既投稿再投稿は禁止。",
            "- APIキー/.env出力は禁止。",
            "- 人間の後追い確認、削除、修正を前提にする。",
            "- note本文、note構成、note投稿準備はしない。",
            "",
            "## RealityGuard",
            "",
            "- この実行では投稿実行なし。",
            "- この実行ではcreate_tweetなし。",
            "- この実行ではupload_mediaなし。",
            "- この実行ではX API writeなし。",
            "- 無制限投稿なし。",
            f"- mode: `{mode}`。",
            "",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a supervised Villain auto-post pilot plan.")
    parser.add_argument(
        "--mode",
        choices=sorted(VALID_MODES),
        default="DRY_RUN",
        help=(
            "DRY_RUN builds a plan; LIVE_PILOT arms candidates; "
            "LIMITED_LIVE_EXECUTION writes a supervised execution manifest without calling X API write."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mode = args.mode
    plan = build_plan(mode)
    write_json(OUTPUT_PATH, plan)
    write_report(plan)
    print(f"status={plan.get('status')}")
    print(f"mode={plan.get('mode')}")
    print(f"pilot_items={len(plan.get('pilot_plan', []))}")
    print("live_posting=NOT_EXECUTED")
    print("x_api_write=NOT_USED")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
