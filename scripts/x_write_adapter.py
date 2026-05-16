#!/usr/bin/env python3
"""Execute one supervised X post from the Villain execution manifest.

Default behavior is validation only. The adapter can write to X only when all
of these are true:
- --mode LIMITED_LIVE_EXECUTION
- --execute-one is provided
- data/villain_auto_post_pilot.json is also in LIMITED_LIVE_EXECUTION mode
- the selected manifest item passes all hard gates

Credentials may be read from .env only for the final execute path, and are never
printed, measured, or written to output files.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import mimetypes
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from required_token_layer import MANDATORY_FOOTER, normalize_mandatory_tokens, verification_summary


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
PILOT_PATH = ROOT / "data" / "villain_auto_post_pilot.json"
MANUAL_RESULTS_PATH = ROOT / "data" / "manual_post_results.json"
RESULT_PATH = ROOT / "data" / "villain_x_write_adapter.json"
REPORT_PATH = ROOT / "reports" / "villain_x_write_adapter.md"

MEDIA_UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
CREATE_TWEET_URL = "https://api.twitter.com/2/tweets"
USERNAME = "raindog_kitetu"
JST = ZoneInfo("Asia/Tokyo")
VALID_MODES = {"DRY_RUN", "LIVE_PILOT", "LIMITED_LIVE_EXECUTION"}
REQUIRED_KEYS = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]
MAX_POSTS_PER_DAY = 5
COOLDOWN_BETWEEN_POSTS_MINUTES = 120


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


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def percent_encode(value: str) -> str:
    return urllib.parse.quote(value, safe="~")


def oauth_header(method: str, url: str, query: dict[str, str], env: dict[str, str]) -> str:
    oauth_params = {
        "oauth_consumer_key": env["X_API_KEY"],
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": env["X_ACCESS_TOKEN"],
        "oauth_version": "1.0",
    }
    signing_params = {**query, **oauth_params}
    normalized = "&".join(
        f"{percent_encode(key)}={percent_encode(value)}"
        for key, value in sorted(signing_params.items())
    )
    base_string = "&".join([method.upper(), percent_encode(url), percent_encode(normalized)])
    signing_key = f"{percent_encode(env['X_API_SECRET'])}&{percent_encode(env['X_ACCESS_TOKEN_SECRET'])}"
    digest = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    oauth_params["oauth_signature"] = base64.b64encode(digest).decode("ascii")
    return "OAuth " + ", ".join(
        f'{percent_encode(key)}="{percent_encode(value)}"'
        for key, value in sorted(oauth_params.items())
    )


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


def latest_post_at(manual_db: dict[str, Any]) -> datetime | None:
    posted: list[datetime] = []
    for item in manual_db.get("manual_post_results", []):
        if not item.get("post_url"):
            continue
        parsed = parse_jst(item.get("post_datetime_jst", ""))
        if parsed:
            posted.append(parsed)
    return max(posted) if posted else None


def select_manifest_item(pilot: dict[str, Any], execution_id: str) -> dict[str, Any]:
    items = pilot.get("execution_manifest", [])
    if execution_id:
        for item in items:
            if item.get("execution_id") == execution_id:
                return item
        return {}
    for item in items:
        if item.get("ready_for_limited_live_execution") is True:
            return item
    return {}


def pilot_item_for_manifest(pilot: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    source_id = manifest.get("source_id")
    slot = manifest.get("slot")
    for item in pilot.get("pilot_plan", []):
        if item.get("source_id") == source_id and item.get("slot") == slot:
            return item
    return {}


def manual_texts_and_images(manual_db: dict[str, Any]) -> tuple[set[str], set[str]]:
    texts: set[str] = set()
    images: set[str] = set()
    for item in manual_db.get("manual_post_results", []):
        text = item.get("post_text", "")
        if text:
            texts.add(text.strip())
        notes = item.get("manual_notes", "")
        for line in notes.splitlines():
            if line.startswith("image_used="):
                images.add(line.split("=", 1)[1].strip())
    return texts, images


def execution_blockers(mode: str, pilot: dict[str, Any], manifest: dict[str, Any], item: dict[str, Any], manual_db: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if mode != "LIMITED_LIVE_EXECUTION":
        blockers.append("mode_not_limited_live_execution")
    if pilot.get("mode") != "LIMITED_LIVE_EXECUTION":
        blockers.append("pilot_plan_not_limited_live_execution")
    if not manifest:
        blockers.append("execution_manifest_item_not_found")
    if manifest and manifest.get("ready_for_limited_live_execution") is not True:
        blockers.append("manifest_not_ready")
    if not item:
        blockers.append("pilot_item_not_found")
        return blockers

    text = normalize_mandatory_tokens(item.get("text", ""))
    token_check = verification_summary(text)
    if token_check.get("valid_after") is not True:
        blockers.append("required_tokens_not_verified")
    if item.get("required_tokens_verified") is not True:
        blockers.append("pilot_item_required_tokens_false")
    if item.get("risk") == "high":
        blockers.append("risk_high")
    if item.get("eligible") is not True:
        blockers.append("pilot_item_not_eligible")
    for blocker in item.get("blockers", []):
        if blocker in {"already_posted", "same_image_cooldown", "repeated_topic_penalty", "risk_high", "required_tokens_not_verified"}:
            blockers.append(blocker)

    posted_texts, posted_images = manual_texts_and_images(manual_db)
    if text.strip() in posted_texts:
        blockers.append("already_posted")
    image = item.get("image", {})
    image_path = image.get("absolute_path") or image.get("file_path", "")
    if image_path and image_path in posted_images:
        blockers.append("same_image_cooldown")

    posts_today = today_post_count(manual_db)
    if posts_today >= MAX_POSTS_PER_DAY:
        blockers.append("max_posts_per_day_reached")
    latest = latest_post_at(manual_db)
    if latest:
        next_allowed = latest + timedelta(minutes=COOLDOWN_BETWEEN_POSTS_MINUTES)
        if datetime.now(JST) < next_allowed:
            blockers.append("cooldown_between_posts_active")
    return sorted(set(blockers))


def upload_media(env: dict[str, str], image_path: Path) -> str:
    content_type = mimetypes.guess_type(str(image_path))[0] or "application/octet-stream"
    boundary = f"----villain{secrets.token_hex(12)}"
    media_bytes = image_path.read_bytes()
    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="media"; filename="{image_path.name}"\r\n'.encode(),
            f"Content-Type: {content_type}\r\n\r\n".encode(),
            media_bytes,
            f"\r\n--{boundary}--\r\n".encode(),
        ]
    )
    request = urllib.request.Request(
        MEDIA_UPLOAD_URL,
        data=body,
        headers={
            "Authorization": oauth_header("POST", MEDIA_UPLOAD_URL, {}, env),
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "villain-limited-live-adapter/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    media_id = data.get("media_id_string")
    if not media_id:
        raise RuntimeError("media upload response missing media_id_string")
    return media_id


def create_tweet(env: dict[str, str], text: str, media_id: str = "") -> dict[str, Any]:
    payload: dict[str, Any] = {"text": text}
    if media_id:
        payload["media"] = {"media_ids": [media_id]}
    request = urllib.request.Request(
        CREATE_TWEET_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": oauth_header("POST", CREATE_TWEET_URL, {}, env),
            "Content-Type": "application/json",
            "User-Agent": "villain-limited-live-adapter/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def write_report(result: dict[str, Any]) -> None:
    lines = [
        "# Villain X Write Adapter v1",
        "",
        f"- Generated at JST: `{result.get('generated_at_jst')}`",
        f"- status: `{result.get('status')}`",
        f"- mode: `{result.get('mode')}`",
        f"- execution_id: `{result.get('execution_id', '')}`",
        f"- live_posting: `{result.get('live_posting')}`",
        f"- upload_media: `{result.get('upload_media')}`",
        f"- create_tweet: `{result.get('create_tweet')}`",
        "- credentials_displayed: `false`",
        "- credential_lengths_displayed: `false`",
        "- credential_partials_displayed: `false`",
        "",
        "## Result",
        "",
        f"- tweet_id: `{result.get('tweet_id', '')}`",
        f"- url: `{result.get('url', '')}`",
        f"- posted_at: `{result.get('posted_at', '')}`",
        f"- media_used: `{result.get('media_used', '')}`",
        f"- no_retry_unless_manual: `{str(result.get('no_retry_unless_manual', True)).lower()}`",
        "",
        "## Gates",
        "",
    ]
    blockers = result.get("blockers", [])
    if blockers:
        lines.extend(f"- blocker: `{blocker}`" for blocker in blockers)
    else:
        lines.append("- blockers: `none`")
    lines.extend(["", "## Text", "", "```text", result.get("text", ""), "```", ""])
    if result.get("error"):
        lines.extend(["## Error", "", f"- `{result.get('error')}`", ""])
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def build_result(args: argparse.Namespace) -> dict[str, Any]:
    pilot = read_json(PILOT_PATH)
    manual_db = read_json(MANUAL_RESULTS_PATH)
    manifest = select_manifest_item(pilot, args.execution_id)
    item = pilot_item_for_manifest(pilot, manifest) if manifest else {}
    text = normalize_mandatory_tokens(item.get("text", "")) if item else ""
    image = item.get("image", {}) if item else {}
    image_path = image.get("absolute_path") or image.get("file_path", "")
    if image_path and not str(image_path).startswith("/"):
        image_path = str(ROOT / image_path)
    blockers = execution_blockers(args.mode, pilot, manifest, item, manual_db)

    result: dict[str, Any] = {
        "db_name": "Villain X Write Adapter Result",
        "version": "1.0.0",
        "generated_at_jst": now_jst(),
        "mode": args.mode,
        "execution_id": manifest.get("execution_id", "") if manifest else args.execution_id,
        "status": "BLOCKED" if blockers else ("READY_TO_EXECUTE_ONE" if args.execute_one else "READY_NOT_EXECUTED"),
        "live_posting": "NOT_EXECUTED",
        "upload_media": "NOT_EXECUTED",
        "create_tweet": "NOT_EXECUTED",
        "tweet_id": "",
        "url": "",
        "posted_at": "",
        "media_used": image_path,
        "text": text,
        "blockers": blockers,
        "error": "",
        "no_retry_unless_manual": True,
        "safety": {
            "max_posts_per_day": MAX_POSTS_PER_DAY,
            "cooldown_between_posts_minutes": COOLDOWN_BETWEEN_POSTS_MINUTES,
            "required_tokens_verified": verification_summary(text).get("valid_after") is True if text else False,
            "api_key_output_allowed": False,
            "env_output_allowed": False,
            "unlimited_posting_allowed": False,
        },
    }
    if blockers or not args.execute_one:
        return result

    env = parse_env(ENV_PATH)
    missing = [key for key in REQUIRED_KEYS if not env.get(key)]
    if missing:
        result["status"] = "FAILED"
        result["error"] = "required credential environment variable missing"
        return result

    try:
        media_id = ""
        if image_path:
            resolved = Path(image_path)
            if not resolved.exists():
                raise RuntimeError("selected image path does not exist")
            media_id = upload_media(env, resolved)
            result["upload_media"] = "EXECUTED_ONCE"
        tweet = create_tweet(env, text, media_id)
        tweet_id = tweet.get("data", {}).get("id", "")
        if not tweet_id:
            raise RuntimeError("create tweet response missing tweet id")
        result["tweet_id"] = tweet_id
        result["url"] = f"https://x.com/{USERNAME}/status/{tweet_id}"
        result["posted_at"] = now_jst()
        result["status"] = "SUCCESS"
        result["live_posting"] = "EXECUTED_ONCE"
        result["create_tweet"] = "EXECUTED_ONCE"
    except urllib.error.HTTPError as error:
        result["status"] = "FAILED"
        result["error"] = f"HTTP {error.code}"
    except Exception as error:  # noqa: BLE001 - keep result sanitized and non-retrying.
        result["status"] = "FAILED"
        result["error"] = str(error)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Supervised X write adapter for one Villain execution manifest item.")
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="DRY_RUN")
    parser.add_argument("--execution-id", default="", help="Optional execution_manifest execution_id. Defaults to first ready item.")
    parser.add_argument("--execute-one", action="store_true", help="Actually execute one post. Only works in LIMITED_LIVE_EXECUTION.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_result(args)
    write_json(RESULT_PATH, result)
    write_report(result)
    print(f"status={result.get('status')}")
    print(f"mode={result.get('mode')}")
    print(f"execution_id={result.get('execution_id')}")
    print(f"live_posting={result.get('live_posting')}")
    print(f"upload_media={result.get('upload_media')}")
    print(f"create_tweet={result.get('create_tweet')}")
    print(f"wrote {RESULT_PATH.relative_to(ROOT)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    if result.get("status") == "SUCCESS":
        print(f"url={result.get('url')}")


if __name__ == "__main__":
    main()
