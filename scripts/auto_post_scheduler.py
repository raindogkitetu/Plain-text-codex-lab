#!/usr/bin/env python3
"""Supervised scheduler wrapper for Villain live pilot posting.

The scheduler is intentionally thin. It prepares a fresh pilot plan, validates
one execution candidate through the write adapter, and only posts when both the
config and CLI explicitly allow one execution. It never retries automatically.
"""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "villain_auto_scheduler.json"
STATE_PATH = ROOT / "data" / "villain_auto_scheduler_state.json"
PILOT_PATH = ROOT / "data" / "villain_auto_post_pilot.json"
ADAPTER_PATH = ROOT / "data" / "villain_x_write_adapter.json"
PASSCODES_PATH = ROOT / "data" / "villain_passcodes.json"
MANUAL_RESULTS_PATH = ROOT / "data" / "manual_post_results.json"
OUTCOMES_PATH = ROOT / "data" / "villain_post_outcomes.json"
REPORT_PATH = ROOT / "reports" / "villain_auto_scheduler.md"
LOG_PATH = ROOT / "logs" / "villain_auto_scheduler.log"
X_PREFLIGHT_HOSTS = ["api.twitter.com", "upload.twitter.com"]

JST = ZoneInfo("Asia/Tokyo")
VALID_MODES = {"DRY_RUN", "LIVE_PILOT", "LIMITED_LIVE_EXECUTION_CHECK"}
DEFAULT_CONFIG = {
    "db_name": "Villain Auto Scheduler",
    "version": "1.0.0",
    "status": "configured",
    "manual_stop": False,
    "mode": "LIVE_PILOT",
    "max_posts_per_day": 3,
    "cooldown_between_posts_minutes": 120,
    "max_posts_per_run": 1,
    "allow_write_execution": False,
    "no_retry_unless_manual": True,
    "passcode_canonical_source": "data/villain_passcodes.json",
    "passcode_auto_generation_allowed": False,
    "required_tokens": ["#着て稼ぐ", "#villain", "$PPP", "@0xmavillain"],
    "hard_blocks": [
        "manual_stop",
        "max_posts_per_day_reached",
        "cooldown_active",
        "risk_high",
        "already_posted",
        "same_image_cooldown",
        "repeated_topic_penalty",
        "required_tokens_not_verified",
        "passcode_missing",
        "passcode_not_in_db",
        "human_review_pending",
        "previous_post_marked_delete_or_drop",
    ],
    "paths": {
        "state": "data/villain_auto_scheduler_state.json",
        "log": "logs/villain_auto_scheduler.log",
        "report": "reports/villain_auto_scheduler.md",
        "launchd_plist": "launchd/com.raindog.villain-auto-scheduler.plist",
    },
}


def now_jst() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def today_jst() -> str:
    return datetime.now(JST).date().isoformat()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_log(entry: dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


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


def run_local(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip().splitlines(),
        "stderr": completed.stderr.strip().splitlines(),
    }


def network_preflight(hosts: list[str]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for host in hosts:
        try:
            socket.getaddrinfo(host, 443)
            results.append({"host": host, "dns_resolved": True, "error": ""})
        except socket.gaierror as error:
            results.append({"host": host, "dns_resolved": False, "error": str(error)})
    return {
        "status": "PASSED" if all(item["dns_resolved"] for item in results) else "FAILED",
        "hosts": results,
        "request_sent": False,
        "upload_media_called": False,
        "create_tweet_called": False,
    }


def manual_posts_today() -> int:
    manual_db = read_json(MANUAL_RESULTS_PATH, {})
    count = 0
    today = datetime.now(JST).date()
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


def is_effective_success_outcome(record: dict[str, Any]) -> bool:
    if not is_success_outcome(record):
        return False
    review = record.get("human_review", {})
    if review.get("keep") is False:
        return False
    if record.get("effective_post") is False or record.get("x_deleted_by_human") is True:
        return False
    return True


def success_outcomes(outcomes_db: dict[str, Any]) -> list[dict[str, Any]]:
    return [record for record in outcomes_db.get("outcomes", []) if is_effective_success_outcome(record)]


def outcome_successes_today(outcomes_db: dict[str, Any]) -> int:
    today = today_jst()
    return sum(1 for record in success_outcomes(outcomes_db) if str(record.get("posted_at_jst", "")).startswith(today))


def latest_success_outcome(outcomes_db: dict[str, Any]) -> dict[str, Any]:
    records = []
    for record in success_outcomes(outcomes_db):
        posted = parse_jst(record.get("posted_at_jst", ""))
        if posted:
            records.append((posted, record))
    if not records:
        return {}
    return max(records, key=lambda item: item[0])[1]


def latest_success_at(outcomes_db: dict[str, Any]) -> datetime | None:
    latest = latest_success_outcome(outcomes_db)
    return parse_jst(latest.get("posted_at_jst", "")) if latest else None


def human_review_blocker(outcomes_db: dict[str, Any]) -> str:
    latest = latest_success_outcome(outcomes_db)
    if not latest:
        return ""
    keep = latest.get("human_review", {}).get("keep", "pending")
    if keep == "pending":
        return "human_review_pending"
    if keep is False:
        return "previous_post_marked_delete_or_drop"
    return ""


def scheduler_blockers(config: dict[str, Any], outcomes_db: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if config.get("manual_stop") is True:
        blockers.append("manual_stop")

    max_posts = int(config.get("max_posts_per_day", 3))
    posts_today = outcome_successes_today(outcomes_db)
    if posts_today >= max_posts:
        blockers.append("max_posts_per_day_reached")

    latest = latest_success_at(outcomes_db)
    if latest:
        cooldown = timedelta(minutes=int(config.get("cooldown_between_posts_minutes", 120)))
        if datetime.now(JST) < latest + cooldown:
            blockers.append("cooldown_active")
    review_blocker = human_review_blocker(outcomes_db)
    if review_blocker:
        blockers.append(review_blocker)
    return blockers


def first_ready_manifest(pilot: dict[str, Any]) -> dict[str, Any]:
    for item in pilot.get("execution_manifest", []):
        if item.get("ready_for_limited_live_execution") is True:
            return item
    return {}


def first_manifest(pilot: dict[str, Any]) -> dict[str, Any]:
    for item in pilot.get("execution_manifest", []):
        return item
    return {}


def update_passcode_usage(passcode: str, adapter: dict[str, Any]) -> None:
    if not passcode:
        return
    db = read_json(PASSCODES_PATH, {})
    today = today_jst()
    for item in db.get("passcodes", []):
        if item.get("code") == passcode:
            item["usage_count"] = int(item.get("usage_count", 0)) + 1
            item["last_used_at"] = today
            item["last_used_context"] = "auto_scheduler_x_post"
            break
    db.setdefault("usage_log", []).append(
        {
            "date": today,
            "passcode": passcode,
            "post_type": "AUTO_SCHEDULER_X_POST",
            "draft_only": False,
            "actually_posted": True,
            "source": "auto_scheduler",
            "tweet_id": adapter.get("tweet_id", ""),
            "url": adapter.get("url", ""),
            "execution_id": adapter.get("execution_id", ""),
        }
    )
    write_json(PASSCODES_PATH, db)


def write_report(result: dict[str, Any]) -> None:
    selected = result.get("selected_manifest", {})
    adapter = result.get("adapter_result", {})
    lines = [
        "# Villain Auto Scheduler v1",
        "",
        f"- Generated at JST: `{result.get('generated_at_jst')}`",
        f"- status: `{result.get('status')}`",
        f"- mode: `{result.get('mode')}`",
        f"- live posting: `{result.get('live_posting')}`",
        f"- upload_media: `{result.get('upload_media')}`",
        f"- create_tweet: `{result.get('create_tweet')}`",
        f"- no_retry_unless_manual: `{str(result.get('no_retry_unless_manual', True)).lower()}`",
        "",
        "## Scheduler Limits",
        "",
        f"- max_posts_per_day: `{result.get('limits', {}).get('max_posts_per_day')}`",
        f"- cooldown_between_posts_minutes: `{result.get('limits', {}).get('cooldown_between_posts_minutes')}`",
        f"- max_posts_per_run: `{result.get('limits', {}).get('max_posts_per_run')}`",
        f"- posts_counted_today: `{result.get('limits', {}).get('posts_counted_today')}`",
        f"- post_count_source: `{result.get('limits', {}).get('post_count_source')}`",
        "",
        "## Daily Slots",
        "",
        "- 03:00: maintenance only; no posting.",
        "- 13:00: daytime posting slot.",
        "- 20:00: night posting slot.",
        "- 23:00: late night posting slot.",
        "",
        "## Gate Order",
        "",
        "1. `manual_stop`",
        "2. outcome DB daily success count",
        "3. cooldown from latest successful outcome",
        "4. `human_review.keep` from latest successful outcome",
        "5. Auto Post Pilot candidate gates",
        "6. X Write Adapter gates",
        "7. network preflight before any write attempt",
        "",
        "## Human Review Gate",
        "",
        f"- latest_success_tweet_id: `{result.get('human_review_gate', {}).get('latest_tweet_id', '')}`",
        f"- latest_success_posted_at_jst: `{result.get('human_review_gate', {}).get('latest_posted_at_jst', '')}`",
        f"- latest_success_keep: `{result.get('human_review_gate', {}).get('latest_keep', '')}`",
        "- `pending` blocks as `human_review_pending`.",
        "- `false` blocks as `previous_post_marked_delete_or_drop`.",
        "- `true` is required before the next post.",
        "",
        "## Stop",
        "",
        "- Stop by setting `manual_stop` to `true` in `data/villain_auto_scheduler.json`.",
        "- launchd登録後なら `launchctl unload ~/Library/LaunchAgents/com.raindog.villain-auto-scheduler.plist` でも止める。",
        "",
        "## Selected Manifest",
        "",
    ]
    if selected:
        lines.extend(
            [
                f"- execution_id: `{selected.get('execution_id', '')}`",
                f"- source_id: `{selected.get('source_id', '')}`",
                f"- slot: `{selected.get('slot', '')}`",
                f"- passcode: `{selected.get('passcode', '')}`",
                f"- ready_for_limited_live_execution: `{str(selected.get('ready_for_limited_live_execution')).lower()}`",
            ]
        )
    else:
        lines.append("- none")
    lines.extend(["", "## Adapter Check", ""])
    if adapter:
        lines.extend(
            [
                f"- status: `{adapter.get('status', '')}`",
                f"- mode: `{adapter.get('mode', '')}`",
                f"- live_posting: `{adapter.get('live_posting', '')}`",
                f"- upload_media: `{adapter.get('upload_media', '')}`",
                f"- create_tweet: `{adapter.get('create_tweet', '')}`",
                f"- required_tokens_verified: `{str(adapter.get('required_tokens_verified', False)).lower()}`",
                f"- passcode_verified: `{str(adapter.get('passcode_verified', False)).lower()}`",
                f"- blockers: `{', '.join(adapter.get('blockers', [])) if adapter.get('blockers') else 'none'}`",
            ]
        )
    else:
        lines.append("- not run")
    preflight = result.get("network_preflight", {})
    lines.extend(["", "## Network Preflight", ""])
    if preflight:
        lines.extend(
            [
                f"- status: `{preflight.get('status', '')}`",
                "- request_sent: `false`",
                "- upload_media_called: `false`",
                "- create_tweet_called: `false`",
            ]
        )
        for item in preflight.get("hosts", []):
            lines.append(
                f"- {item.get('host')}: dns_resolved=`{str(item.get('dns_resolved')).lower()}`"
            )
    else:
        lines.append("- not run")
    lines.extend(
        [
            "",
            "## Sandbox Finding",
            "",
            "- Codex sandbox can fail DNS resolution for `api.twitter.com` and `upload.twitter.com` before any X API request is sent.",
            "- When DNS preflight fails, scheduler returns `NETWORK_PREFLIGHT_FAILED` before `upload_media` or `create_tweet`.",
            "- In that state, passcode usage and outcome success records must not be updated.",
            "- Real posting should run only from a network-enabled local environment.",
        ]
    )
    lines.extend(["", "## Commands", ""])
    lines.extend(
        [
            "- DRY_RUN: `python3 scripts/auto_post_scheduler.py --mode DRY_RUN`",
            "- LIVE_PILOT check: `python3 scripts/auto_post_scheduler.py --mode LIVE_PILOT`",
            "- LIMITED_LIVE_EXECUTION equivalent check: `python3 scripts/auto_post_scheduler.py --mode LIMITED_LIVE_EXECUTION_CHECK`",
            "- Future one-post execution requires both config `allow_write_execution=true` and CLI `--execute-one`.",
            "",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def build_result(args: argparse.Namespace) -> dict[str, Any]:
    config = read_json(CONFIG_PATH, DEFAULT_CONFIG)
    state = read_json(STATE_PATH, {"successful_posts": [], "last_run_at_jst": ""})
    outcomes_db = read_json(OUTCOMES_PATH, {})
    mode = args.mode
    generated_at = now_jst()
    base_blockers = scheduler_blockers(config, outcomes_db)
    latest_success = latest_success_outcome(outcomes_db)
    result: dict[str, Any] = {
        "db_name": "Villain Auto Scheduler Run",
        "version": "1.0.0",
        "generated_at_jst": generated_at,
        "mode": mode,
        "status": "BLOCKED" if base_blockers else "CHECK_READY",
        "live_posting": "NOT_EXECUTED",
        "upload_media": "NOT_EXECUTED",
        "create_tweet": "NOT_EXECUTED",
        "no_retry_unless_manual": True,
        "blockers": base_blockers,
        "selected_manifest": {},
        "adapter_result": {},
        "network_preflight": {},
        "commands": [],
        "limits": {
            "max_posts_per_day": int(config.get("max_posts_per_day", 3)),
            "cooldown_between_posts_minutes": int(config.get("cooldown_between_posts_minutes", 120)),
            "max_posts_per_run": int(config.get("max_posts_per_run", 1)),
            "posts_counted_today": outcome_successes_today(outcomes_db),
            "post_count_source": "data/villain_post_outcomes.json",
        },
        "human_review_gate": {
            "source": "latest_success_outcome",
            "latest_tweet_id": latest_success.get("tweet_id", ""),
            "latest_posted_at_jst": latest_success.get("posted_at_jst", ""),
            "latest_keep": latest_success.get("human_review", {}).get("keep", "") if latest_success else "",
            "required_to_continue": True,
        },
        "safety": {
            "passcode_canonical_source": "data/villain_passcodes.json",
            "passcode_auto_generation_allowed": False,
            "api_key_output_allowed": False,
            "env_output_allowed": False,
        },
    }
    if base_blockers:
        return result

    plan_mode = "DRY_RUN" if mode == "DRY_RUN" else "LIMITED_LIVE_EXECUTION"
    plan_run = run_local([sys.executable, "scripts/auto_post_pilot.py", "--mode", plan_mode])
    result["commands"].append(plan_run)
    if plan_run["returncode"] != 0:
        result["status"] = "FAILED_PLAN"
        result["blockers"].append("auto_post_pilot_failed")
        return result

    pilot = read_json(PILOT_PATH, {})
    selected = first_manifest(pilot) if mode == "DRY_RUN" else first_ready_manifest(pilot)
    result["selected_manifest"] = selected
    if not selected:
        result["status"] = "BLOCKED"
        result["blockers"].append("no_manifest" if mode == "DRY_RUN" else "no_ready_manifest")
        return result

    adapter_mode = "DRY_RUN" if mode == "DRY_RUN" else "LIMITED_LIVE_EXECUTION"
    adapter_command = [sys.executable, "scripts/x_write_adapter.py", "--mode", adapter_mode, "--execution-id", selected.get("execution_id", "")]
    may_write = (
        mode == "LIVE_PILOT"
        and args.execute_one
        and config.get("allow_write_execution") is True
        and int(config.get("max_posts_per_run", 1)) == 1
    )
    adapter_run = run_local(adapter_command)
    result["commands"].append(adapter_run)
    adapter = read_json(ADAPTER_PATH, {})
    result["adapter_result"] = adapter
    result["live_posting"] = adapter.get("live_posting", "NOT_EXECUTED")
    result["upload_media"] = adapter.get("upload_media", "NOT_EXECUTED")
    result["create_tweet"] = adapter.get("create_tweet", "NOT_EXECUTED")

    if adapter_run["returncode"] != 0:
        result["status"] = "FAILED_ADAPTER"
        result["blockers"].append("x_write_adapter_failed")
        return result
    if may_write and adapter.get("blockers"):
        result["status"] = "BLOCKED"
        result["blockers"].extend(adapter.get("blockers", []))
        return result
    if may_write and adapter.get("status") not in {"READY_NOT_EXECUTED", "READY_TO_EXECUTE_ONE"}:
        result["status"] = "WRITE_NOT_SUCCESSFUL_NO_RETRY"
        result["blockers"].append("adapter_not_ready")
        return result
    if may_write:
        preflight = network_preflight(X_PREFLIGHT_HOSTS)
        result["network_preflight"] = preflight
        if preflight.get("status") != "PASSED":
            result["status"] = "NETWORK_PREFLIGHT_FAILED"
            result["blockers"].append("network_preflight_failed")
            state["last_run_at_jst"] = generated_at
            state["last_status"] = result["status"]
            state["last_selected_execution_id"] = selected.get("execution_id", "")
            write_json(STATE_PATH, state)
            return result

        execute_command = [*adapter_command, "--execute-one"]
        execute_run = run_local(execute_command)
        result["commands"].append(execute_run)
        adapter = read_json(ADAPTER_PATH, {})
        result["adapter_result"] = adapter
        result["live_posting"] = adapter.get("live_posting", "NOT_EXECUTED")
        result["upload_media"] = adapter.get("upload_media", "NOT_EXECUTED")
        result["create_tweet"] = adapter.get("create_tweet", "NOT_EXECUTED")
        if execute_run["returncode"] != 0:
            result["status"] = "FAILED_ADAPTER"
            result["blockers"].append("x_write_adapter_failed")
            return result
    if adapter.get("status") == "SUCCESS":
        passcode = adapter.get("passcode", "")
        update_passcode_usage(passcode, adapter)
        logger_run = run_local([sys.executable, "scripts/post_outcome_logger.py", "log"])
        result["commands"].append(logger_run)
        state.setdefault("successful_posts", []).append(
            {
                "posted_at_jst": adapter.get("posted_at", ""),
                "tweet_id": adapter.get("tweet_id", ""),
                "url": adapter.get("url", ""),
                "execution_id": adapter.get("execution_id", ""),
                "passcode": passcode,
            }
        )
        result["status"] = "SUCCESS_POSTED_ONCE"
    elif may_write:
        result["status"] = "WRITE_NOT_SUCCESSFUL_NO_RETRY"
    else:
        result["status"] = "READY_NOT_EXECUTED" if adapter.get("status") in {"READY_NOT_EXECUTED", "READY_TO_EXECUTE_ONE"} else "CHECK_COMPLETE"

    state["last_run_at_jst"] = generated_at
    state["last_status"] = result["status"]
    state["last_selected_execution_id"] = selected.get("execution_id", "")
    write_json(STATE_PATH, state)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Supervised Villain auto post scheduler.")
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="DRY_RUN")
    parser.add_argument("--execute-one", action="store_true", help="Allow one post only when config also enables write execution.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not CONFIG_PATH.exists():
        write_json(CONFIG_PATH, DEFAULT_CONFIG)
    result = build_result(args)
    append_log(result)
    write_json(
        STATE_PATH,
        {
            **read_json(STATE_PATH, {}),
            "last_run_at_jst": result["generated_at_jst"],
            "last_status": result["status"],
            "last_selected_execution_id": result.get("selected_manifest", {}).get("execution_id", ""),
        },
    )
    write_report(result)
    print(f"status={result.get('status')}")
    print(f"mode={result.get('mode')}")
    print(f"live_posting={result.get('live_posting')}")
    print(f"upload_media={result.get('upload_media')}")
    print(f"create_tweet={result.get('create_tweet')}")
    print(f"selected_execution_id={result.get('selected_manifest', {}).get('execution_id', '')}")
    print(f"wrote {STATE_PATH.relative_to(ROOT)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    print(f"logged {LOG_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
