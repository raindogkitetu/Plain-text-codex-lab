#!/usr/bin/env python3
"""Whitelist-only commit/push helper for Villain OS handoff state.

Default mode is dry-run. This script stages only safe supervisory handoff files,
validates hard invariants, and optionally creates a local commit or pushes it.
It never posts, uploads media, creates tweets, or generates tracking codes.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMMIT_MESSAGE = "chore: publish villain handoff state"

WHITELIST = [
    "docs/cold_start_bootstrap.md",
    "docs/current_villain_os_state.md",
    "docs/handoff_contract.md",
    "docs/agent_handoff_protocol.md",
    "data/codex_to_chatgpt_handoff.json",
    "data/chatgpt_to_codex_handoff.json",
    "data/chatgpt_bridge_exchange.json",
    "data/agent_handoff_state.json",
    "data/agent_handoff_trajectory.json",
    "data/villain_quality_review_queue.json",
    "data/villain_repair_execution.json",
    "data/villain_repaired_candidates.json",
    "data/villain_context_evidence_requests.json",
    "data/villain_repair_quality_analytics.json",
    "reports/agent_handoff_status.md",
    "reports/villain_quality_review_summary.md",
    "reports/chatgpt_bridge_prompt.md",
    "scripts/agent_handoff_runner.py",
    "scripts/chatgpt_bridge_prompt_builder.py",
    "scripts/chatgpt_decision_ingestor.py",
    "scripts/handoff_commit_push.py",
    "scripts/handoff_repair_runner.py",
    "scripts/post_quality_os.py",
    "scripts/auto_post_maintenance.py",
]

FORBIDDEN_EXACT = {
    ".DS_Store",
    "AGENTS.md",
    "data/villain_passcodes.json",
}
FORBIDDEN_PREFIXES = (
    "assets/",
    "logs/",
    "space_recordings/",
    "villain_post_images/",
)
JSON_INVARIANT_FILES = [
    "data/codex_to_chatgpt_handoff.json",
    "data/chatgpt_to_codex_handoff.json",
    "data/chatgpt_bridge_exchange.json",
    "data/agent_handoff_state.json",
    "data/villain_quality_review_queue.json",
    "data/villain_repair_execution.json",
    "data/villain_repaired_candidates.json",
    "data/villain_repair_quality_analytics.json",
]


def run_git(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


def rel(path: str) -> str:
    return path.strip().rstrip("/")


def porcelain_entries() -> list[dict[str, str]]:
    completed = run_git(["status", "--porcelain=v1", "-z"])
    raw = completed.stdout.split("\0")
    entries: list[dict[str, str]] = []
    index = 0
    while index < len(raw):
        item = raw[index]
        index += 1
        if not item:
            continue
        status = item[:2]
        path = item[3:]
        if status.startswith("R") or status.startswith("C"):
            if index < len(raw):
                path = raw[index]
                index += 1
        entries.append({"path": rel(path), "status": status})
    return entries


def is_forbidden(path: str, allow_passcodes: bool = False) -> bool:
    path = rel(path)
    exact = FORBIDDEN_EXACT - ({"data/villain_passcodes.json"} if allow_passcodes else set())
    return path in exact or any(path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)


def read_json(path: str) -> Any:
    with (ROOT / path).open("r", encoding="utf-8") as file:
        return json.load(file)


def find_values(data: Any, key: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(data, dict):
        for item_key, value in data.items():
            if item_key == key:
                found.append(value)
            found.extend(find_values(value, key))
    elif isinstance(data, list):
        for value in data:
            found.extend(find_values(value, key))
    return found


def has_key(data: Any, key: str) -> bool:
    if isinstance(data, dict):
        return any(item_key == key or has_key(value, key) for item_key, value in data.items())
    if isinstance(data, list):
        return any(has_key(value, key) for value in data)
    return False


def bool_false_or_missing(value: Any) -> bool:
    return value is False or value is None


def validate_invariants() -> tuple[bool, list[str]]:
    errors: list[str] = []
    for path in JSON_INVARIANT_FILES:
        full_path = ROOT / path
        if not full_path.exists():
            errors.append(f"missing_json:{path}")
            continue
        try:
            data = read_json(path)
        except Exception as error:  # noqa: BLE001 - sanitized local validation error.
            errors.append(f"invalid_json:{path}:{error}")
            continue

        for value in find_values(data, "safe_to_post"):
            if value is not False:
                errors.append(f"safe_to_post_not_false:{path}:{value}")
        for value in find_values(data, "posting_execution_status"):
            if value != "BLOCKED":
                errors.append(f"posting_execution_status_not_blocked:{path}:{value}")
        for key in ("posting_executed", "upload_media_executed", "tweet_creation_executed"):
            for value in find_values(data, key):
                if not bool_false_or_missing(value):
                    errors.append(f"{key}_not_false:{path}:{value}")
        if has_key(data, "tracking_code"):
            errors.append(f"tracking_code_key_detected:{path}")

    generated_markers = [
        "generate_tracking_code",
        "tracking_code =",
        "tracking_code:",
    ]
    script_targets = [
        "scripts/agent_handoff_runner.py",
        "scripts/chatgpt_bridge_prompt_builder.py",
        "scripts/chatgpt_decision_ingestor.py",
        "scripts/handoff_repair_runner.py",
        "scripts/post_quality_os.py",
        "scripts/auto_post_maintenance.py",
    ]
    for path in script_targets:
        full_path = ROOT / path
        if not full_path.exists():
            continue
        text = full_path.read_text(encoding="utf-8")
        for marker in generated_markers:
            if marker in text:
                errors.append(f"tracking_code_generation_marker:{path}:{marker}")
    return not errors, errors


def dirty_diff_summary(entries: list[dict[str, str]], allow_passcodes: bool) -> dict[str, Any]:
    whitelist = set(WHITELIST)
    changed = [entry["path"] for entry in entries]
    return {
        "changed_files": changed,
        "forbidden_dirty_files": [path for path in changed if is_forbidden(path, allow_passcodes)],
        "non_whitelisted_dirty_files": [path for path in changed if path not in whitelist],
        "whitelisted_dirty_files": [path for path in changed if path in whitelist],
    }


def staged_files() -> list[str]:
    completed = run_git(["diff", "--cached", "--name-only"])
    return [rel(line) for line in completed.stdout.splitlines() if line.strip()]


def guard_preexisting_staged(allow_passcodes: bool) -> tuple[bool, list[str]]:
    staged = staged_files()
    forbidden = [path for path in staged if is_forbidden(path, allow_passcodes)]
    non_whitelist = [path for path in staged if path not in WHITELIST]
    errors = [f"forbidden_already_staged:{path}" for path in forbidden]
    errors.extend(f"non_whitelisted_already_staged:{path}" for path in non_whitelist if path not in forbidden)
    return not errors, errors


def whitelist_paths_to_stage() -> list[str]:
    paths: list[str] = []
    for path in WHITELIST:
        if (ROOT / path).exists():
            paths.append(path)
    return paths


def stage_whitelist(paths: list[str]) -> None:
    if paths:
        # Some handoff JSON/report files are intentionally ignored during normal
        # development. In this helper, the whitelist is the safety boundary, so
        # force-add only these explicitly listed supervisory files.
        run_git(["add", "-f", "--", *paths])


def commit(message: str) -> str:
    completed = run_git(["commit", "-m", message])
    return completed.stdout.strip()


def push() -> str:
    completed = run_git(["push"])
    return completed.stdout.strip() or completed.stderr.strip()


def build_result(args: argparse.Namespace) -> dict[str, Any]:
    entries = porcelain_entries()
    invariant_ok, invariant_errors = validate_invariants()
    staged_ok, staged_errors = guard_preexisting_staged(args.allow_passcodes)
    paths_to_stage = whitelist_paths_to_stage()
    summary = dirty_diff_summary(entries, args.allow_passcodes)
    result: dict[str, Any] = {
        "commit_created": False,
        "dirty_diff_summary": summary,
        "dry_run": args.dry_run or not args.commit,
        "forbidden_path_guard": {
            "allow_passcodes": args.allow_passcodes,
            "errors": staged_errors,
            "ok": staged_ok,
        },
        "invariant_validation": {
            "errors": invariant_errors,
            "ok": invariant_ok,
        },
        "message": args.message,
        "posting_executed": False,
        "push_executed": False,
        "safe_to_post": False,
        "stage_candidates": paths_to_stage,
        "tweet_creation_executed": False,
        "upload_media_executed": False,
    }

    if not invariant_ok or not staged_ok:
        result["status"] = "BLOCKED"
        return result

    if args.dry_run or not args.commit:
        result["status"] = "DRY_RUN"
        return result

    stage_whitelist(paths_to_stage)
    result["staged_files_after_add"] = staged_files()
    commit_output = commit(args.message)
    result["commit_created"] = True
    result["commit_output"] = commit_output
    result["status"] = "COMMITTED"

    if args.push:
        result["push_output"] = push()
        result["push_executed"] = True
        result["status"] = "PUSHED"
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Whitelist-only Villain OS handoff commit/push helper.")
    parser.add_argument("--commit", action="store_true", help="Create a local commit after validation.")
    parser.add_argument("--push", action="store_true", help="Push after commit. Requires --commit.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and summarize without staging or committing.")
    parser.add_argument("--message", default=DEFAULT_COMMIT_MESSAGE, help="Commit message for --commit.")
    parser.add_argument(
        "--allow-passcodes",
        action="store_true",
        help="Allow preexisting passcode dirty state. Passcodes are still not staged by default whitelist.",
    )
    args = parser.parse_args()
    if args.push and not args.commit:
        parser.error("--push requires --commit")
    if not args.commit:
        args.dry_run = True
    return args


def main() -> None:
    args = parse_args()
    result = build_result(args)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    print("posting_executed=NO")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    if result.get("status") == "BLOCKED":
        sys.exit(1)


if __name__ == "__main__":
    main()
