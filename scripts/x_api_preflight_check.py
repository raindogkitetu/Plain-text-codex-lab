#!/usr/bin/env python3
"""Generate an X API preflight checklist report.

This script is read/report only. It checks configured environment variable
names, never reads environment variable values, never logs in, never
authenticates, and never posts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
X_CONFIG_PATH = ROOT / "data" / "x_api_config.json"
REPORT_PATH = ROOT / "reports" / "x_api_preflight_check.md"
SCRIPTS_DIR = ROOT / "scripts"

FORBIDDEN_FUNCTION_NAMES = [
    "x_login",
    "api_authenticate",
    "create_tweet",
    "upload_media",
    "publish_post",
    "schedule_live_post",
]


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def pass_text(value: bool) -> str:
    return "PASS" if value else "FAIL"


def credentials_are_env_names_only(credentials: dict) -> bool:
    expected = {
        "api_key_env",
        "api_secret_env",
        "access_token_env",
        "access_token_secret_env",
        "bearer_token_env",
    }
    if set(credentials.keys()) != expected:
        return False
    return all(isinstance(value, str) and value.startswith("X_") for value in credentials.values())


def forbidden_function_exists(function_name: str) -> bool:
    pattern = f"def {function_name}("
    if not SCRIPTS_DIR.exists():
        return False
    return any(
        pattern in path.read_text(encoding="utf-8")
        for path in SCRIPTS_DIR.glob("*.py")
    )


def main() -> None:
    config = read_json(X_CONFIG_PATH)
    credentials = config.get("credentials", {})
    connection = config.get("connection", {})
    guard = config.get("posting_guard", {})
    generated_at = datetime.now(timezone.utc).isoformat()

    function_checks = {
        name: forbidden_function_exists(name) for name in FORBIDDEN_FUNCTION_NAMES
    }
    env_names_only = credentials_are_env_names_only(credentials)

    checks = [
        ("data/x_api_config.json exists", X_CONFIG_PATH.exists()),
        ("credentials are env-var names only", env_names_only),
        ("actual credential values are not stored", env_names_only),
        ("api_connected is false", connection.get("api_connected") is False),
        ("dry_run_only is true", connection.get("dry_run_only") is True),
        ("auto_post_enabled is false", guard.get("auto_post_enabled") is False),
        ("manual_approval_required is true", guard.get("manual_approval_required") is True),
        ("live_post_blocked is true", guard.get("block_if_dry_run_only") is True),
        ("no live post function exists", not any(function_checks.values())),
        ("no upload_media function exists", not function_checks["upload_media"]),
        ("no create_tweet function exists", not function_checks["create_tweet"]),
    ]

    reasons = [
        "credentials not configured",
        "dry_run_only is true",
        "api_connected is false",
        "live post function missing by design",
        "auto_post_enabled is false",
    ]

    lines = [
        "# X API Preflight Check",
        "",
        f"- Generated at: `{generated_at}`",
        "- preflight_status: `NOT_READY`",
        "- live posting: `DISABLED`",
        "",
        "## Reasons",
        "",
    ]
    lines.extend(f"- {reason}" for reason in reasons)
    lines.extend(["", "## Checklist", ""])
    lines.extend(
        f"- [{'x' if passed else ' '}] {label}: `{pass_text(passed)}`"
        for label, passed in checks
    )
    lines.extend(["", "## Forbidden Function Scan", ""])
    lines.extend(
        f"- `{name}` exists: `{bool_text(exists)}`"
        for name, exists in function_checks.items()
    )
    lines.extend(
        [
            "",
            "## Safety Note",
            "",
            "This preflight reads configuration keys and scans local script text only.",
            "It does not read environment variable values, log in to X, authenticate with an API, upload media, publish posts, or schedule posts.",
            "",
        ]
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote X API preflight report to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
