#!/usr/bin/env python3
"""Execute one approved Villain image post, then restore the kill switch.

This script reads local .env values but never prints credentials, lengths, or
partials. It performs exactly one media upload and one tweet creation only when
the final readiness report is READY.
"""

from __future__ import annotations

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
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
X_CONFIG_PATH = ROOT / "data" / "x_api_config.json"
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
IMAGE_QUEUE_PATH = ROOT / "data" / "villain_image_queue.json"
FINAL_CHECK_REPORT_PATH = ROOT / "reports" / "villain_api_final_check.md"
RUN_LOG_PATH = ROOT / "reports" / "villain_run_log.md"
FINAL_REPORT_PATH = ROOT / "reports" / "villain_api_live_post_result.md"

MEDIA_UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
CREATE_TWEET_URL = "https://api.twitter.com/2/tweets"
REQUIRED_KEYS = [
    "X_API_KEY",
    "X_API_SECRET",
    "X_ACCESS_TOKEN",
    "X_ACCESS_TOKEN_SECRET",
]


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    signing_key = (
        f"{percent_encode(env['X_API_SECRET'])}&"
        f"{percent_encode(env['X_ACCESS_TOKEN_SECRET'])}"
    )
    digest = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    oauth_params["oauth_signature"] = base64.b64encode(digest).decode("ascii")
    return "OAuth " + ", ".join(
        f'{percent_encode(key)}="{percent_encode(value)}"'
        for key, value in sorted(oauth_params.items())
    )


def selected_image(queue_db: dict) -> dict:
    selected = [item for item in queue_db.get("queue", []) if item.get("selected_for_post") is True]
    if len(selected) != 1:
        raise RuntimeError("expected exactly one selected image")
    return selected[0]


def final_ready() -> bool:
    text = FINAL_CHECK_REPORT_PATH.read_text(encoding="utf-8")
    return "- readiness: `READY`" in text


def restore_kill_switch() -> None:
    config = read_json(X_CONFIG_PATH)
    config.setdefault("posting_guard", {})["write_action_kill_switch"] = True
    write_json(X_CONFIG_PATH, config)


def upload_media(env: dict[str, str], image_path: Path) -> str:
    content_type = mimetypes.guess_type(str(image_path))[0] or "application/octet-stream"
    boundary = f"----villain{secrets.token_hex(12)}"
    media_bytes = image_path.read_bytes()
    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            b'Content-Disposition: form-data; name="media"; filename="villain_observer_001.png"\r\n',
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
            "User-Agent": "villain-post-os-image-post/0.1",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    media_id = data.get("media_id_string")
    if not media_id:
        raise RuntimeError("media upload response missing media_id_string")
    return media_id


def create_tweet(env: dict[str, str], text: str, media_id: str) -> dict:
    payload = json.dumps(
        {"text": text, "media": {"media_ids": [media_id]}},
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        CREATE_TWEET_URL,
        data=payload,
        headers={
            "Authorization": oauth_header("POST", CREATE_TWEET_URL, {}, env),
            "Content-Type": "application/json",
            "User-Agent": "villain-post-os-image-post/0.1",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def write_result_report(success: bool, tweet_id: str, url: str, reason: str) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    status = "SUCCESS" if success else "FAILED"
    lines = [
        "# Villain API Live Post Result",
        "",
        f"- Generated at: `{generated_at}`",
        f"- status: `{status}`",
        f"- tweet_id: `{tweet_id}`",
        f"- post_url: `{url}`",
        "- upload_media: `EXECUTED_ONCE`" if success else "- upload_media: `FAILED_OR_NOT_COMPLETED`",
        "- create_tweet: `EXECUTED_ONCE`" if success else "- create_tweet: `FAILED_OR_NOT_COMPLETED`",
        "- credentials_displayed: `false`",
        "- credential_lengths_displayed: `false`",
        "- credential_partials_displayed: `false`",
        "- write_action_kill_switch_after: `true`",
        "",
        "## Result",
        "",
        f"- {reason}",
        "",
    ]
    FINAL_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def append_run_log(url: str) -> None:
    entry = "\n".join(
        [
            "",
            "## 2026-05-12 First API Image Post",
            "",
            "- result: `API image post success`",
            f"- post_url: `{url}`",
            "- upload_media: `EXECUTED_ONCE`",
            "- create_tweet: `EXECUTED_ONCE`",
            "- write_action_kill_switch restored: `true`",
            "",
        ]
    )
    with RUN_LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(entry)


def main() -> None:
    env = parse_env(ENV_PATH)
    missing = [key for key in REQUIRED_KEYS if not env.get(key)]
    if missing:
        restore_kill_switch()
        raise SystemExit("required credential environment variable missing")
    if not final_ready():
        restore_kill_switch()
        raise SystemExit("final readiness report is not READY")

    payload_db = read_json(PAYLOADS_PATH)
    queue_db = read_json(IMAGE_QUEUE_PATH)
    payload = payload_db["payloads"][0]
    image = selected_image(queue_db)
    image_path = Path(image["image_path"])
    if not image_path.exists():
        restore_kill_switch()
        raise SystemExit("selected image path does not exist")

    success = False
    tweet_id = ""
    url = ""
    reason = ""
    try:
        media_id = upload_media(env, image_path)
        tweet = create_tweet(env, payload["caption"], media_id)
        tweet_id = tweet.get("data", {}).get("id", "")
        if not tweet_id:
            raise RuntimeError("create tweet response missing tweet id")
        url = f"https://x.com/raindog_kitetu/status/{tweet_id}"
        payload["posted_url"] = url
        payload["api_image_posted"] = True
        payload["api_image_posted_at"] = datetime.now(timezone.utc).isoformat()
        write_json(PAYLOADS_PATH, payload_db)
        success = True
        reason = "one image post created successfully"
        append_run_log(url)
    except urllib.error.HTTPError as error:
        reason = f"HTTP {error.code}"
        raise
    finally:
        restore_kill_switch()
        write_result_report(success, tweet_id, url, reason or "post failed")
        print("api image post attempt complete; credentials were not printed")
        if success:
            print(url)


if __name__ == "__main__":
    main()
