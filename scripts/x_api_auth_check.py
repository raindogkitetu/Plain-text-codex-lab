#!/usr/bin/env python3
"""Check X API authentication without performing any posting action.

This script reads local .env values but never prints credentials, lengths, or
partial values. It calls only a read-only self-check endpoint.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
REPORT_PATH = ROOT / "reports" / "x_api_auth_check.md"

REQUIRED_KEYS = [
    "X_API_KEY",
    "X_API_SECRET",
    "X_ACCESS_TOKEN",
    "X_ACCESS_TOKEN_SECRET",
]

VERIFY_URL = "https://api.twitter.com/1.1/account/verify_credentials.json"


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
    base_string = "&".join(
        [
            method.upper(),
            percent_encode(url),
            percent_encode(normalized),
        ]
    )
    signing_key = (
        f"{percent_encode(env['X_API_SECRET'])}&"
        f"{percent_encode(env['X_ACCESS_TOKEN_SECRET'])}"
    )
    digest = hmac.new(
        signing_key.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha1,
    ).digest()
    oauth_params["oauth_signature"] = base64.b64encode(digest).decode("ascii")
    return "OAuth " + ", ".join(
        f'{percent_encode(key)}="{percent_encode(value)}"'
        for key, value in sorted(oauth_params.items())
    )


def auth_check(env: dict[str, str]) -> tuple[bool, str]:
    missing = [key for key in REQUIRED_KEYS if not env.get(key)]
    if missing:
        return False, "required environment variable missing"

    query = {"include_entities": "false", "skip_status": "true"}
    url = VERIFY_URL + "?" + urllib.parse.urlencode(query)
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": oauth_header("GET", VERIFY_URL, query, env),
            "User-Agent": "villain-post-os-auth-check/0.1",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            if 200 <= response.status < 300:
                return True, "read-only credential verification succeeded"
            return False, f"unexpected HTTP status {response.status}"
    except urllib.error.HTTPError as error:
        return False, f"HTTP {error.code}"
    except urllib.error.URLError:
        return False, "network or connection error"


def write_report(success: bool, reason: str) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    status = "SUCCESS" if success else "FAILED"
    lines = [
        "# X API Auth Check",
        "",
        f"- Generated at: `{generated_at}`",
        f"- auth_status: `{status}`",
        "- live posting: `DISABLED`",
        "- api_mode: `read_only_auth_check`",
        "- credentials_displayed: `false`",
        "- credential_lengths_displayed: `false`",
        "- credential_partials_displayed: `false`",
        "",
        "## Result",
        "",
        f"- {reason}",
        "",
        "## Safety",
        "",
        "- No post was created.",
        "- No media was uploaded.",
        "- No delete/update/follow/like/reply/repost/DM action was performed.",
        "- `auto_post_enabled` remains `false`.",
        "- `dry_run_only` remains `true`.",
        "- `live_post_blocked` remains `true`.",
        "",
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    env = parse_env(ENV_PATH)
    success, reason = auth_check(env)
    write_report(success, reason)
    print("auth check complete; report written without credential output")


if __name__ == "__main__":
    main()
