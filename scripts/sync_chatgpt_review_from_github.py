#!/usr/bin/env python3
"""Sync GitHub-hosted ChatGPT review state into the local repo.

This is a review-only bridge consumer. It fetches the latest GitHub review bot
commit and copies only safe handoff/report files into the local workspace.

It never posts, uploads media, creates tweets, or generates tracking codes.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
JST = ZoneInfo("Asia/Tokyo")
RESULT_PATH = ROOT / "data" / "chatgpt_review_sync.json"
REPORT_PATH = ROOT / "reports" / "chatgpt_review_sync.md"
DEFAULT_REMOTE = "origin"
DEFAULT_BRANCH = "main"

SYNC_FILES = [
    "data/chatgpt_to_codex_handoff.json",
    "data/chatgpt_bridge_exchange.json",
    "data/agent_handoff_trajectory.json",
    "reports/agent_handoff_status.md",
    "reports/chatgpt_bridge_prompt.md",
    "reports/chatgpt_github_review_bot.md",
]


def now_jst() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_git(args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


def remote_ref(remote: str, branch: str) -> str:
    return f"{remote}/{branch}"


def fetch(remote: str, branch: str) -> dict[str, Any]:
    completed = run_git(["fetch", remote, branch])
    return {
        "returncode": completed.returncode,
        "status": "SUCCESS" if completed.returncode == 0 else "FAILED",
        "stderr_tail": completed.stderr.splitlines()[-20:],
        "stdout_tail": completed.stdout.splitlines()[-20:],
    }


def git_show(ref: str, path: str) -> tuple[bool, str, str]:
    completed = run_git(["show", f"{ref}:{path}"])
    if completed.returncode != 0:
        return False, "", completed.stderr.strip()
    return True, completed.stdout, ""


def has_key(value: Any, target: str) -> bool:
    if isinstance(value, dict):
        return any(key == target or has_key(nested, target) for key, nested in value.items())
    if isinstance(value, list):
        return any(has_key(item, target) for item in value)
    return False


def validate_synced_invariants() -> list[str]:
    errors: list[str] = []
    inbox = read_json(ROOT / "data" / "chatgpt_to_codex_handoff.json", {})
    exchange = read_json(ROOT / "data" / "chatgpt_bridge_exchange.json", {})
    if inbox.get("safe_to_post") is not False:
        errors.append("chatgpt_to_codex.safe_to_post_not_false")
    if inbox.get("posting_execution_status") != "BLOCKED":
        errors.append("chatgpt_to_codex.posting_execution_status_not_blocked")
    if has_key(inbox, "tracking_code"):
        errors.append("chatgpt_to_codex.tracking_code_key_detected")
    for key in ("posting_executed", "upload_media_executed", "tweet_creation_executed"):
        value = exchange.get(key)
        if value not in {False, None}:
            errors.append(f"chatgpt_bridge_exchange.{key}_not_false")
    return errors


def sync_files(ref: str, dry_run: bool) -> dict[str, Any]:
    updated: list[str] = []
    unchanged: list[str] = []
    missing: list[dict[str, str]] = []
    for path in SYNC_FILES:
        ok, remote_content, error = git_show(ref, path)
        if not ok:
            missing.append({"path": path, "error": error})
            continue
        local_path = ROOT / path
        local_content = local_path.read_text(encoding="utf-8") if local_path.exists() else ""
        if local_content == remote_content:
            unchanged.append(path)
            continue
        updated.append(path)
        if not dry_run:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_text(remote_content, encoding="utf-8")
    return {
        "missing": missing,
        "unchanged": unchanged,
        "updated": updated,
    }


def build_report(result: dict[str, Any]) -> str:
    sync = result.get("sync", {})
    fetch_result = result.get("fetch", {})
    lines = [
        "# ChatGPT Review Sync",
        "",
        f"- generated_at_jst: `{result.get('generated_at_jst')}`",
        f"- status: `{result.get('status')}`",
        f"- remote_ref: `{result.get('remote_ref')}`",
        f"- dry_run: `{result.get('dry_run')}`",
        f"- fetch_status: `{fetch_result.get('status')}`",
        f"- updated_files: `{len(sync.get('updated', []))}`",
        f"- unchanged_files: `{len(sync.get('unchanged', []))}`",
        f"- missing_files: `{len(sync.get('missing', []))}`",
        f"- invariant_errors: `{result.get('invariant_errors') or 'none'}`",
        "- safe_to_post: `false`",
        "- posting_execution_status: `BLOCKED`",
        "- posting executed: `NO`",
        "- upload executed: `NO`",
        "- tweet creation executed: `NO`",
        "",
        "## Updated Files",
        "",
    ]
    lines.extend(f"- `{path}`" for path in sync.get("updated", []))
    if not sync.get("updated"):
        lines.append("- none")
    lines.extend(["", "## Missing Files", ""])
    lines.extend(f"- `{item.get('path')}`: `{item.get('error')}`" for item in sync.get("missing", []))
    if not sync.get("missing"):
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> int:
    generated_at = now_jst()
    ref = remote_ref(args.remote, args.branch)
    fetch_result = {"status": "SKIPPED", "returncode": 0, "stdout_tail": [], "stderr_tail": []}
    if not args.no_fetch:
        fetch_result = fetch(args.remote, args.branch)
    sync = sync_files(ref, args.dry_run)
    invariant_errors = [] if args.dry_run else validate_synced_invariants()
    status = "SUCCESS"
    if fetch_result.get("status") == "FAILED" or sync.get("missing") or invariant_errors:
        status = "FAILED"
    if args.dry_run and status == "SUCCESS":
        status = "DRY_RUN"
    result = {
        "db_name": "ChatGPT Review Sync",
        "dry_run": args.dry_run,
        "fetch": fetch_result,
        "generated_at_jst": generated_at,
        "invariant_errors": invariant_errors,
        "posting_executed": False,
        "remote_ref": ref,
        "safe_to_post": False,
        "schema_version": "handoff.chatgpt_review_sync.v1",
        "status": status,
        "sync": sync,
        "tweet_creation_executed": False,
        "upload_media_executed": False,
        "version": "1.0.0",
    }
    if not args.dry_run:
        write_json(RESULT_PATH, result)
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(build_report(result), encoding="utf-8")
    print(f"status={status}")
    print(f"updated_files={len(sync.get('updated', []))}")
    print("posting_executed=NO")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    return 0 if status in {"SUCCESS", "DRY_RUN"} else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync GitHub-hosted ChatGPT review state.")
    parser.add_argument("--remote", default=DEFAULT_REMOTE)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-fetch", action="store_true")
    return parser.parse_args()


def main() -> None:
    raise SystemExit(run(parse_args()))


if __name__ == "__main__":
    main()
