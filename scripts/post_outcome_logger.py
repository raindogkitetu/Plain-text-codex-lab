#!/usr/bin/env python3
"""Log Villain post outcomes for learning without posting or X write calls."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from required_token_layer import extract_passcode
from media_deduplication import perceptual_hash, prompt_family_for


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "data" / "villain_x_write_adapter.json"
PILOT_PATH = ROOT / "data" / "villain_auto_post_pilot.json"
OUTCOME_PATH = ROOT / "data" / "villain_post_outcomes.json"
REPORT_PATH = ROOT / "reports" / "villain_post_outcome_logger.md"

JST = ZoneInfo("Asia/Tokyo")
ARCHETYPES = [
    "culture_observer",
    "street_signal",
    "meme_fragment",
    "anti_ad",
    "quiet_flex",
    "community_artifact",
]


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


def image_hash(path_text: str) -> str:
    if not path_text:
        return ""
    path = Path(path_text)
    if not path.exists():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def first_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def find_pilot_item(pilot: dict[str, Any], execution_id: str) -> dict[str, Any]:
    manifest = {}
    for item in pilot.get("execution_manifest", []):
        if item.get("execution_id") == execution_id:
            manifest = item
            break
    source_id = manifest.get("source_id")
    slot = manifest.get("slot")
    for item in pilot.get("pilot_plan", []):
        if item.get("source_id") == source_id and item.get("slot") == slot:
            return item
    return {}


def infer_topic_cluster(text: str, item: dict[str, Any]) -> str:
    category = item.get("category", "")
    joined = f"{text}\n{item.get('reason', '')}"
    if category == "culture_observer" or any(word in joined for word in ("誰が着て", "話題になる服", "服だけじゃない")):
        return "culture_observer_apparel_context"
    if category == "community_info" or any(word in joined for word in ("集会", "集ま", "人が")):
        return "community_gathering_signal"
    if category == "poster_summary":
        return "poster_summary_residual"
    return category or "unknown"


def archetype_scores(text: str, item: dict[str, Any]) -> dict[str, int]:
    category = item.get("category", "")
    image = item.get("image", {})
    remix = item.get("remixability", {})
    signals = set(remix.get("signals", []))
    line = first_line(text)
    scores = {
        "culture_observer": 40 if category == "culture_observer" else 15,
        "street_signal": 20 if image.get("ready") else 8,
        "meme_fragment": 15 if len(line) <= 24 else 6,
        "anti_ad": 18 if "広告" in text or "服だけじゃない" in text else 8,
        "quiet_flex": 12 if any(word in text for word in ("強い", "残る", "話題")) else 6,
        "community_artifact": 35 if "image_stands_alone" in signals or category == "community_info" else 12,
    }
    if "someone_else_can_say_it" in signals:
        scores["meme_fragment"] += 10
        scores["community_artifact"] += 8
    if "identity_badge_feel" in signals:
        scores["quiet_flex"] += 8
        scores["community_artifact"] += 10
    if "community_reposting_probability" in signals:
        scores["community_artifact"] += 12
    return scores


def primary_archetype(scores: dict[str, int]) -> str:
    return max(scores, key=lambda key: scores[key]) if scores else "unknown"


def empty_metrics() -> dict[str, Any]:
    return {
        "captured_at_jst": "",
        "impressions": None,
        "likes": None,
        "reposts": None,
        "replies": None,
        "bookmarks": None,
        "profile_clicks": None,
        "repost_reuse": None,
    }


def build_record(adapter: dict[str, Any], pilot: dict[str, Any]) -> dict[str, Any]:
    item = find_pilot_item(pilot, adapter.get("execution_id", ""))
    text = adapter.get("text", "")
    image_path = adapter.get("media_used", "")
    image = item.get("image", {})
    passcode = adapter.get("passcode") or item.get("passcode") or extract_passcode(text)
    scores = archetype_scores(text, item)
    return {
        "tweet_id": adapter.get("tweet_id", ""),
        "url": adapter.get("url", ""),
        "posted_at_jst": adapter.get("posted_at", ""),
        "status": "SUCCESS",
        "candidate_id": item.get("source_id", ""),
        "execution_id": adapter.get("execution_id", ""),
        "passcode": passcode,
        "image_used": image_path,
        "image_hash": image_hash(image_path),
        "perceptual_hash": perceptual_hash(image_path),
        "prompt_family": prompt_family_for(image, image_path),
        "composition": image.get("composition", ""),
        "layout": image.get("layout", ""),
        "topic_cluster": infer_topic_cluster(text, item),
        "archetype": {
            "primary": primary_archetype(scores),
            "scores": scores,
            "labels": ARCHETYPES,
        },
        "scores": {
            "novelty_score": item.get("novelty_score"),
            "remixability_score": item.get("remixability_score"),
            "culture_observer_score": scores.get("culture_observer"),
            "quality_score": item.get("score"),
        },
        "metrics_1h": empty_metrics(),
        "metrics_24h": empty_metrics(),
        "human_review": {
            "keep": "pending",
            "delete_reason": "",
            "felt_native": None,
            "felt_ad_like": None,
            "notes": "",
        },
        "learning_flags": {
            "required_tokens_verified": item.get("required_tokens_verified"),
            "risk": item.get("risk"),
            "remixability_signals": item.get("remixability", {}).get("signals", []),
            "saturation_flags": item.get("saturation_flags", []),
            "post_publish_learning_focus": item.get("post_publish_learning_plan", {}).get("learning_focus", []),
        },
        "text": text,
        "logged_at_jst": now_jst(),
        "updated_at_jst": now_jst(),
        "update_history": [],
    }


def upsert_record(db: dict[str, Any], record: dict[str, Any]) -> tuple[dict[str, Any], str]:
    tweet_id = record.get("tweet_id", "")
    records = db.setdefault("outcomes", [])
    for index, existing in enumerate(records):
        if existing.get("tweet_id") == tweet_id:
            records[index] = {**existing, **record}
            return db, "updated"
    records.append(record)
    return db, "inserted"


def parse_optional_bool(value: str) -> bool | None:
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    if normalized in {"null", "none", "pending", ""}:
        return None
    raise argparse.ArgumentTypeError("expected true, false, null, or pending")


def parse_keep(value: str) -> bool | str:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    if normalized == "pending":
        return "pending"
    raise argparse.ArgumentTypeError("expected true, false, or pending")


def ensure_metrics_shape(record: dict[str, Any]) -> None:
    for key in ("metrics_1h", "metrics_24h"):
        metrics = record.setdefault(key, {})
        for metric_key, default in empty_metrics().items():
            metrics.setdefault(metric_key, default)
    review = record.setdefault("human_review", {})
    review.setdefault("keep", "pending")
    review.setdefault("delete_reason", "")
    review.setdefault("felt_native", None)
    review.setdefault("felt_ad_like", None)
    review.setdefault("notes", "")
    record.setdefault("update_history", [])


def find_outcome_index(db: dict[str, Any], tweet_id: str, candidate_id: str) -> int:
    for index, record in enumerate(db.get("outcomes", [])):
        if tweet_id and record.get("tweet_id") == tweet_id:
            return index
        if candidate_id and record.get("candidate_id") == candidate_id:
            return index
    return -1


def update_metric_group(record: dict[str, Any], group: str, args: argparse.Namespace, changed: dict[str, Any]) -> None:
    metrics = record.setdefault(group, empty_metrics())
    prefix = "metrics_1h" if group == "metrics_1h" else "metrics_24h"
    fields = {
        "impressions": getattr(args, f"{prefix}_impressions"),
        "likes": getattr(args, f"{prefix}_likes"),
        "reposts": getattr(args, f"{prefix}_reposts"),
        "replies": getattr(args, f"{prefix}_replies"),
        "bookmarks": getattr(args, f"{prefix}_bookmarks"),
        "profile_clicks": getattr(args, f"{prefix}_profile_clicks"),
        "repost_reuse": getattr(args, f"{prefix}_repost_reuse"),
    }
    group_changed = False
    for field, value in fields.items():
        if value is None:
            continue
        old_value = metrics.get(field)
        if old_value == value:
            continue
        metrics[field] = value
        changed[f"{group}.{field}"] = {"old": old_value, "new": value}
        group_changed = True
    captured_at = getattr(args, f"{prefix}_captured_at")
    if captured_at:
        old_value = metrics.get("captured_at_jst", "")
        metrics["captured_at_jst"] = captured_at
        changed[f"{group}.captured_at_jst"] = {"old": old_value, "new": captured_at}
    elif group_changed and not metrics.get("captured_at_jst"):
        metrics["captured_at_jst"] = now_jst()
        changed[f"{group}.captured_at_jst"] = {"old": "", "new": metrics["captured_at_jst"]}


def update_manual_review(record: dict[str, Any], args: argparse.Namespace, changed: dict[str, Any]) -> None:
    review = record.setdefault("human_review", {})
    updates = {
        "keep": args.manual_keep,
        "delete_reason": args.delete_reason,
        "felt_native": args.felt_native,
        "felt_ad_like": args.felt_ad_like,
        "notes": args.notes,
    }
    for field, value in updates.items():
        if value is None and field not in {"felt_native", "felt_ad_like", "keep"}:
            continue
        if field in {"felt_native", "felt_ad_like", "keep"} and not getattr(args, f"{field}_provided", False):
            continue
        old_value = review.get(field)
        if old_value == value:
            continue
        review[field] = value
        changed[f"human_review.{field}"] = {"old": old_value, "new": value}


def update_existing_outcome(args: argparse.Namespace) -> tuple[dict[str, Any], str]:
    db = read_json(OUTCOME_PATH)
    index = find_outcome_index(db, args.tweet_id, args.candidate_id)
    if index < 0:
        raise SystemExit("target outcome not found")
    record = db["outcomes"][index]
    ensure_metrics_shape(record)
    changed: dict[str, Any] = {}
    update_metric_group(record, "metrics_1h", args, changed)
    update_metric_group(record, "metrics_24h", args, changed)
    update_manual_review(record, args, changed)
    if changed:
        timestamp = now_jst()
        record["updated_at_jst"] = timestamp
        record.setdefault("update_history", []).append(
            {
                "updated_at_jst": timestamp,
                "source": "post_outcome_logger_update",
                "changes": changed,
            }
        )
        db["outcomes"][index] = record
        db["updated_at_jst"] = timestamp
        db["last_action"] = "updated_outcome"
        db["last_updated_tweet_id"] = record.get("tweet_id", "")
    else:
        db["last_action"] = "no_changes"
        db["last_updated_tweet_id"] = record.get("tweet_id", "")
    return db, db["last_action"]


def build_db(adapter: dict[str, Any], pilot: dict[str, Any], existing: dict[str, Any]) -> tuple[dict[str, Any], str]:
    db = existing or {
        "db_name": "Villain Post Outcomes",
        "version": "1.0.0",
        "status": "local_outcome_logging_only",
        "purpose": "実投稿後のtweet_id、画像、archetype、1h/24h metrics、人間レビューを学習用に保存する。投稿・X API writeは行わない。",
        "safety": {
            "live_posting_allowed": False,
            "x_api_write_allowed": False,
            "upload_media_allowed": False,
            "create_tweet_allowed": False,
            "commit_performed": False,
        },
        "archetype_labels": ARCHETYPES,
        "outcomes": [],
    }
    record = build_record(adapter, pilot)
    db, action = upsert_record(db, record)
    db["updated_at_jst"] = now_jst()
    return db, action


def write_report(db: dict[str, Any], action: str) -> None:
    lines = [
        "# Villain Post Outcome Logger v1",
        "",
        f"- Generated at JST: `{now_jst()}`",
        "- status: `LOCAL_OUTCOME_LOGGING_ONLY`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        f"- action: `{action}`",
        f"- outcomes: `{len(db.get('outcomes', []))}`",
        "",
        "## Latest Outcome",
        "",
    ]
    latest = {}
    last_updated = db.get("last_updated_tweet_id", "")
    for outcome in db.get("outcomes", []):
        if last_updated and outcome.get("tweet_id") == last_updated:
            latest = outcome
            break
    if not latest:
        latest = db.get("outcomes", [])[-1] if db.get("outcomes") else {}
    if latest:
        metrics_1h = latest.get("metrics_1h", {})
        metrics_24h = latest.get("metrics_24h", {})
        lines.extend(
            [
                f"- tweet_id: `{latest.get('tweet_id')}`",
                f"- url: {latest.get('url')}",
                f"- candidate_id: `{latest.get('candidate_id')}`",
                f"- passcode: `{latest.get('passcode', '')}`",
                f"- posted_at_jst: `{latest.get('posted_at_jst')}`",
                f"- image_hash: `{latest.get('image_hash')}`",
                f"- topic_cluster: `{latest.get('topic_cluster')}`",
                f"- archetype_primary: `{latest.get('archetype', {}).get('primary')}`",
                f"- novelty_score: `{latest.get('scores', {}).get('novelty_score')}`",
                f"- culture_observer_score: `{latest.get('scores', {}).get('culture_observer_score')}`",
                f"- metrics_1h: `{metrics_1h}`",
                f"- metrics_24h: `{metrics_24h}`",
                f"- manual_review.keep: `{latest.get('human_review', {}).get('keep')}`",
                f"- manual_review.delete_reason: `{latest.get('human_review', {}).get('delete_reason')}`",
                f"- felt_native: `{latest.get('human_review', {}).get('felt_native')}`",
                f"- felt_ad_like: `{latest.get('human_review', {}).get('felt_ad_like')}`",
                f"- manual_review.notes: `{latest.get('human_review', {}).get('notes')}`",
                f"- updated_at_jst: `{latest.get('updated_at_jst', '')}`",
                f"- update_history_count: `{len(latest.get('update_history', []))}`",
                "",
                "```text",
                latest.get("text", ""),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Three-Post Operation Prep",
            "",
            "- 1日3本運用では、各投稿をこのoutcome DBに即時記録する。",
            "- 1h metricsで初速、24h metricsで後残りを分けて見る。",
            "- 完全放置BOTではなく、人間レビューで keep/delete_reason と felt_native/felt_ad_like を更新する。",
            "- community_artifact / culture_observer / anti_ad の比率を日次で見る。",
            "",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Log or update Villain post outcomes without X write calls.")
    subparsers = parser.add_subparsers(dest="command")

    log_parser = subparsers.add_parser("log", help="Log latest successful X write adapter result.")
    log_parser.add_argument("--source", default="adapter", choices=["adapter"], help="Outcome source.")

    update_parser = subparsers.add_parser("update", help="Update metrics and manual review for an existing outcome.")
    update_parser.add_argument("--tweet-id", default="")
    update_parser.add_argument("--candidate-id", default="")
    for prefix in ("metrics-1h", "metrics-24h"):
        update_parser.add_argument(f"--{prefix}-captured-at", default="")
        update_parser.add_argument(f"--{prefix}-impressions", type=int)
        update_parser.add_argument(f"--{prefix}-likes", type=int)
        update_parser.add_argument(f"--{prefix}-reposts", type=int)
        update_parser.add_argument(f"--{prefix}-replies", type=int)
        update_parser.add_argument(f"--{prefix}-bookmarks", type=int)
        update_parser.add_argument(f"--{prefix}-profile-clicks", type=int)
        update_parser.add_argument(f"--{prefix}-repost-reuse", type=parse_optional_bool)
    update_parser.add_argument("--manual-keep", type=parse_keep)
    update_parser.add_argument("--delete-reason")
    update_parser.add_argument("--felt-native", type=parse_optional_bool)
    update_parser.add_argument("--felt-ad-like", type=parse_optional_bool)
    update_parser.add_argument("--notes")

    args = parser.parse_args()
    if args.command is None:
        args.command = "log"
    argv = set(sys.argv[1:])
    args.keep_provided = "--manual-keep" in argv
    args.felt_native_provided = "--felt-native" in argv
    args.felt_ad_like_provided = "--felt-ad-like" in argv
    return args


def main() -> None:
    args = parse_args()
    if args.command == "update":
        db, action = update_existing_outcome(args)
        tweet_id = db.get("last_updated_tweet_id", "")
    else:
        adapter = read_json(ADAPTER_PATH)
        if adapter.get("status") != "SUCCESS" or not adapter.get("tweet_id"):
            raise SystemExit("latest adapter result is not a successful posted tweet")
        pilot = read_json(PILOT_PATH)
        existing = read_json(OUTCOME_PATH)
        db, action = build_db(adapter, pilot, existing)
        tweet_id = adapter.get("tweet_id")
    write_json(OUTCOME_PATH, db)
    write_report(db, action)
    print("status=LOCAL_OUTCOME_LOGGING_ONLY")
    print("live_posting=NOT_EXECUTED")
    print("x_api_write=NOT_USED")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"action={action}")
    print(f"tweet_id={tweet_id}")
    print(f"wrote {OUTCOME_PATH.relative_to(ROOT)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
