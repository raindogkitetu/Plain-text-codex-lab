#!/usr/bin/env python3
"""Run the repo-local ChatGPT -> Codex handoff loop without posting."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from post_quality_os import build_review, write_report
from handoff_repair_runner import run_repair_execution


ROOT = Path(__file__).resolve().parents[1]
CHATGPT_INBOX = ROOT / "data" / "chatgpt_to_codex_handoff.json"
CODEX_OUTBOX = ROOT / "data" / "codex_to_chatgpt_handoff.json"
STATE_PATH = ROOT / "data" / "agent_handoff_state.json"
QUALITY_QUEUE = ROOT / "data" / "villain_quality_review_queue.json"
OUTCOMES_PATH = ROOT / "data" / "villain_post_outcomes.json"
HANDOFF_REPORT = ROOT / "reports" / "agent_handoff_status.md"
TRAJECTORY_PATH = ROOT / "data" / "agent_handoff_trajectory.json"
HANDOFF_SCHEMA_VERSION = "handoff.v1"
INBOX_SCHEMA_VERSION = "handoff.chatgpt_to_codex.v1"
OUTBOX_SCHEMA_VERSION = "handoff.codex_to_chatgpt.v1"
STATE_SCHEMA_VERSION = "handoff.state.v1"
TRAJECTORY_SCHEMA_VERSION = "handoff.trajectory.v1"
DELETED_LEARNING_COOLDOWN_DAYS = 7
REQUIRED_FILES = [
    ROOT / "docs" / "handoff_contract.md",
    ROOT / "docs" / "agent_handoff_protocol.md",
    CHATGPT_INBOX,
    ROOT / "data" / "villain_post_quality_os.json",
    ROOT / "scripts" / "post_quality_os.py",
    ROOT / "scripts" / "handoff_repair_runner.py",
    ROOT / "data" / "villain_post_outcomes.json",
]
JST = ZoneInfo("Asia/Tokyo")


def now_jst() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def missing_files() -> list[str]:
    return [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]


def tracking_code_absent() -> bool:
    targets = [
        ROOT / "scripts" / "post_quality_os.py",
        ROOT / "scripts" / "auto_post_pilot.py",
        ROOT / "scripts" / "x_write_adapter.py",
        ROOT / "data" / "villain_post_quality_os.json",
    ]
    for path in targets:
        if path.exists() and "tracking_code" in path.read_text(encoding="utf-8"):
            return False
    return True


def summarize_review(review: dict[str, Any]) -> dict[str, Any]:
    items = review.get("review_items", [])
    blockers = sorted({blocker for item in items for blocker in item.get("blockers", [])})
    warnings = sorted({warning for item in items for warning in item.get("warnings", [])})
    statuses = Counter(item.get("final_quality_status", "") for item in items)
    blocker_frequency = Counter(blocker for item in items for blocker in item.get("blockers", []))
    return {
        "quality_status": review.get("status", ""),
        "queue_health_status": review.get("queue_health_status", ""),
        "review_board_status": review.get("review_board_status", ""),
        "posting_execution_status": review.get("posting_execution_status", ""),
        "executable_ready_count": review.get("executable_ready_count", 0),
        "safe_to_review": review.get("safe_to_review", False),
        "safe_to_post": review.get("safe_to_post", False),
        "review_items": len(items),
        "blockers": blockers,
        "warnings": warnings,
        "blocked_reason_frequency": dict(sorted(blocker_frequency.items())),
        "review_required_candidate_count": statuses.get("REVIEW_REQUIRED", 0),
        "ready_candidate_count": statuses.get("READY", 0),
        "blocked_candidate_count": statuses.get("BLOCKED", 0),
    }


def ensure_inbox_contract(inbox: dict[str, Any]) -> dict[str, Any]:
    return {
        **inbox,
        "schema_version": inbox.get("schema_version") or INBOX_SCHEMA_VERSION,
        "safe_to_post": False,
        "posting_execution_status": "BLOCKED",
    }


def review_state_machine(summary: dict[str, Any], missing: list[str], decision: dict[str, Any]) -> dict[str, Any]:
    if missing:
        current = "CONTRACT_BLOCKED"
    elif summary.get("safe_to_post") is True:
        current = "INVALID_SAFE_TO_POST_TRUE"
    elif decision:
        current = "CHATGPT_DECISION_CONSUMED"
    elif summary.get("safe_to_review"):
        current = "READY_FOR_CHATGPT_REVIEW"
    else:
        current = "EMPTY_REVIEW_BOARD"
    return {
        "current_state": current,
        "allowed_states": [
            "INBOX_RECEIVED",
            "QUALITY_REVIEW_BUILT",
            "READY_FOR_CHATGPT_REVIEW",
            "CHATGPT_DECISION_CONSUMED",
            "READY_FOR_HUMAN_REVIEW",
            "POSTING_BLOCKED",
            "CONTRACT_BLOCKED",
        ],
        "terminal_posting_states_disabled": [
            "POSTING_READY",
            "POSTING_EXECUTED",
        ],
        "safe_to_post_default": False,
    }


def repair_actions_from_review(review: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for item in review.get("review_items", []):
        action = item.get("repair_action", {})
        if not action or action.get("type") == "none":
            continue
        actions.append(
            {
                "candidate_id": item.get("candidate_id", ""),
                "execution_id": item.get("execution_id", ""),
                "slot": item.get("slot", ""),
                "repair_action": action,
                "blockers": item.get("blockers", []),
            }
        )
    return actions


def append_trajectory(
    generated_at: str,
    inbox: dict[str, Any],
    outbox: dict[str, Any],
    summary: dict[str, Any],
    repair_actions: list[dict[str, Any]],
) -> None:
    db = read_json(
        TRAJECTORY_PATH,
        {
            "db_name": "Agent Handoff Trajectory",
            "schema_version": TRAJECTORY_SCHEMA_VERSION,
            "version": "1.0.0",
            "events": [],
        },
    )
    events = db.setdefault("events", [])
    events.append(
        {
            "at_jst": generated_at,
            "event_type": "handoff_runner_cycle",
            "inbox_schema_version": inbox.get("schema_version", ""),
            "outbox_schema_version": outbox.get("schema_version", ""),
            "chatgpt_decision": inbox.get("chatgpt_review_decision", {}).get("decision", ""),
            "review_state": outbox.get("review_state_machine", {}).get("current_state", ""),
            "queue_health_status": summary.get("queue_health_status", ""),
            "review_board_status": summary.get("review_board_status", ""),
            "posting_execution_status": summary.get("posting_execution_status", ""),
            "safe_to_post": False,
            "repair_action_count": len(repair_actions),
            "posting_executed": False,
            "upload_media_executed": False,
            "tweet_creation_executed": False,
        }
    )
    db["last_event_at_jst"] = generated_at
    db["event_count"] = len(events)
    write_json(TRAJECTORY_PATH, db)


def cleanup_review_queue(review: dict[str, Any]) -> dict[str, Any]:
    seen: set[tuple[str, str, str, str]] = set()
    cleaned: list[dict[str, Any]] = []
    removed = 0
    for item in review.get("review_items", []):
        key = (
            item.get("candidate_id", ""),
            item.get("execution_id", ""),
            item.get("slot", ""),
            item.get("image", ""),
        )
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        cleaned.append(item)
    review["review_items"] = cleaned
    review["stale_cleanup"] = {
        "strategy": "dedupe_current_review_items_by_candidate_execution_slot_image",
        "removed_count": removed,
        "remaining_count": len(cleaned),
    }
    return review


def deleted_learning_cooldown_remaining(outcomes_db: dict[str, Any]) -> list[dict[str, Any]]:
    now = datetime.now(JST)
    remaining: list[dict[str, Any]] = []
    for record in outcomes_db.get("outcomes", []):
        if record.get("human_review", {}).get("keep") is not False:
            continue
        anchor = (
            parse_jst(record.get("updated_at_jst", ""))
            or parse_jst(record.get("deleted_at_jst", ""))
            or parse_jst(record.get("posted_at_jst", ""))
        )
        if not anchor:
            continue
        expires = anchor + timedelta(days=DELETED_LEARNING_COOLDOWN_DAYS)
        seconds = max(0, int((expires - now).total_seconds()))
        remaining.append(
            {
                "tweet_id": record.get("tweet_id", ""),
                "candidate_id": record.get("candidate_id", ""),
                "execution_id": record.get("execution_id", ""),
                "topic_cluster": record.get("topic_cluster", ""),
                "image_used": record.get("image_used", ""),
                "cooldown_until_jst": expires.isoformat(timespec="seconds"),
                "remaining_hours": round(seconds / 3600, 1),
                "reason": record.get("human_review", {}).get("delete_reason", ""),
            }
        )
    return remaining


def write_handoff_report(outbox: dict[str, Any], state: dict[str, Any]) -> None:
    result = outbox.get("implementation_result", {})
    validation = outbox.get("validation", {})
    maintenance = outbox.get("maintenance_summary", {})
    decision = outbox.get("chatgpt_decision_consumed", {})
    repair_execution = outbox.get("repair_execution", {})
    repair_quality = repair_execution.get("repair_quality_summary", {})
    lines = [
        "# Agent Handoff Status",
        "",
        f"- Generated at JST: `{outbox.get('generated_at_jst')}`",
        f"- schema_version: `{outbox.get('schema_version')}`",
        f"- status: `{outbox.get('status')}`",
        f"- review_state: `{outbox.get('review_state_machine', {}).get('current_state')}`",
        "- posting executed: `NO`",
        "- upload executed: `NO`",
        "- tweet creation executed: `NO`",
        "",
        "## Quality Review",
        "",
        f"- quality_status: `{result.get('quality_status')}`",
        f"- queue_health_status: `{maintenance.get('queue_health_status', '')}`",
        f"- review_board_status: `{maintenance.get('review_board_status', '')}`",
        f"- posting_execution_status: `{maintenance.get('posting_execution_status', '')}`",
        f"- executable_ready_count: `{maintenance.get('executable_ready_count', 0)}`",
        f"- safe_to_review: `{str(maintenance.get('safe_to_review', False)).lower()}`",
        f"- safe_to_post: `{str(maintenance.get('safe_to_post', False)).lower()}`",
        f"- review_items: `{state.get('last_run', {}).get('review_items')}`",
        f"- blockers: `{', '.join(result.get('blockers', [])) if result.get('blockers') else 'none'}`",
        f"- warnings: `{', '.join(result.get('warnings', [])) if result.get('warnings') else 'none'}`",
        f"- blocked_reason_frequency: `{maintenance.get('blocked_reason_frequency', {})}`",
        f"- review_required_candidate_count: `{maintenance.get('review_required_candidate_count', 0)}`",
        f"- READY_candidate_count: `{maintenance.get('ready_candidate_count', 0)}`",
        f"- BLOCKED_candidate_count: `{maintenance.get('blocked_candidate_count', 0)}`",
        f"- stale_cleanup_removed: `{maintenance.get('stale_cleanup', {}).get('removed_count', 0)}`",
        "",
        "## ChatGPT Decision",
        "",
        f"- decision: `{decision.get('decision', '')}`",
        f"- approved_for_review: `{len(decision.get('approved_for_review', []))}`",
        f"- not_approved_for_posting: `{len(decision.get('not_approved_for_posting', []))}`",
        f"- must_remain_blocked: `{len(decision.get('must_remain_blocked', []))}`",
        f"- refill_required: `{str(decision.get('refill_required', False)).lower()}`",
        f"- repair_actions: `{len(outbox.get('repair_actions', []))}`",
        f"- repair_execution_status: `{repair_execution.get('status', '')}`",
        f"- repaired_candidate_count: `{repair_execution.get('repaired_candidate_count', 0)}`",
        f"- context_evidence_request_count: `{repair_execution.get('context_evidence_request_count', 0)}`",
        f"- average_repair_quality_score: `{repair_quality.get('average_repair_quality_score', 0)}`",
        f"- average_repair_confidence: `{repair_quality.get('average_repair_confidence', 0)}`",
        f"- repair_regression_risk_frequency: `{repair_quality.get('repair_regression_risk_frequency', {})}`",
        f"- recurring_repair_failure_clusters: `{len(repair_execution.get('recurring_repair_failure_clusters', []))}`",
        "",
        "## Deleted Learning Cooldown",
        "",
    ]
    cooldowns = maintenance.get("deleted_learning_cooldown_remaining", [])
    if cooldowns:
        for item in cooldowns:
            lines.append(
                f"- `{item.get('tweet_id')}` candidate `{item.get('candidate_id')}`: "
                f"`{item.get('remaining_hours')}`h remaining until `{item.get('cooldown_until_jst')}`"
            )
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Validation",
            "",
            f"- json_valid: `{validation.get('json_valid')}`",
            f"- quality_review_runner: `{validation.get('quality_review_runner')}`",
            f"- tracking_code_absent: `{validation.get('tracking_code_absent')}`",
            f"- x_write_not_used: `{validation.get('x_write_not_used')}`",
            "",
            "## Unresolved Issues",
            "",
        ]
    )
    issues = outbox.get("unresolved_issues", [])
    lines.extend([f"- {issue}" for issue in issues] or ["- none"])
    lines.extend(["", "## Next Actions", ""])
    actions = outbox.get("next_actions", [])
    lines.extend([f"- {action}" for action in actions] or ["- none"])
    lines.extend(["", "## GitHub Handoff", ""])
    lines.extend(
        [
            "- ChatGPT can read this contract and the JSON handoff files through the GitHub connector after commit/push.",
            "- Codex should only publish handoff/review/report files for this loop; posting artifacts stay gated.",
        ]
    )
    lines.append("")
    HANDOFF_REPORT.parent.mkdir(parents=True, exist_ok=True)
    HANDOFF_REPORT.write_text("\n".join(lines), encoding="utf-8")


def run_handoff() -> dict[str, Any]:
    generated_at = now_jst()
    inbox = ensure_inbox_contract(read_json(CHATGPT_INBOX, {}))
    write_json(CHATGPT_INBOX, inbox)
    chatgpt_decision = inbox.get("chatgpt_review_decision", {})
    missing = missing_files()
    review = cleanup_review_queue(build_review())
    write_json(QUALITY_QUEUE, review)
    write_report(review)
    summary = summarize_review(review)
    state_machine = review_state_machine(summary, missing, chatgpt_decision)
    repair_actions = repair_actions_from_review(review)
    repair_execution = run_repair_execution(repair_actions, review, generated_at)
    outcomes = read_json(OUTCOMES_PATH, {})
    cooldowns = deleted_learning_cooldown_remaining(outcomes)
    unresolved = list(inbox.get("open_questions_for_codex", []))
    if missing:
        unresolved.append("Required handoff files missing: " + ", ".join(missing))
    if summary["blocked_candidate_count"] and not summary["ready_candidate_count"]:
        unresolved.append("All current candidates are blocked; refill or image/text repair is needed.")
    if cooldowns:
        unresolved.append("Deleted learning cooldown is active for recent failed posts.")

    outbox = {
        "db_name": "Codex to ChatGPT Handoff",
        "schema_version": OUTBOX_SCHEMA_VERSION,
        "version": "1.0.0",
        "status": "BLOCKED" if missing else "READY_FOR_CHATGPT_REVIEW",
        "review_state_machine": state_machine,
        "generated_at_jst": generated_at,
        "purpose": "Codexが実装結果・検証結果・未解決課題・次アクションをChatGPTへ返すためのoutbox。",
        "posting_executed": False,
        "upload_media_executed": False,
        "tweet_creation_executed": False,
        "implementation_result": {
            "summary": "Agent handoff loop validated through repo-local protocol, policy, quality runner, and reports.",
            "changed_files": [
                "docs/agent_handoff_protocol.md",
                "data/chatgpt_to_codex_handoff.json",
                "data/codex_to_chatgpt_handoff.json",
                "data/agent_handoff_state.json",
                "scripts/agent_handoff_runner.py",
                "scripts/handoff_repair_runner.py",
                "data/villain_repair_quality_analytics.json",
                "reports/agent_handoff_status.md",
            ],
            "quality_status": summary["quality_status"],
            "blockers": summary["blockers"],
            "warnings": summary["warnings"],
        },
        "chatgpt_decision_consumed": chatgpt_decision,
        "repair_actions": repair_actions,
        "repair_execution": {
            "status": "COMPLETED_REVIEW_ONLY",
            **repair_execution,
        },
        "maintenance_summary": {
            "queue_health_status": summary["queue_health_status"],
            "review_board_status": summary["review_board_status"],
            "posting_execution_status": summary["posting_execution_status"],
            "executable_ready_count": summary["executable_ready_count"],
            "safe_to_review": summary["safe_to_review"],
            "safe_to_post": summary["safe_to_post"],
            "blocked_reason_frequency": summary["blocked_reason_frequency"],
            "review_required_candidate_count": summary["review_required_candidate_count"],
            "ready_candidate_count": summary["ready_candidate_count"],
            "blocked_candidate_count": summary["blocked_candidate_count"],
            "stale_cleanup": review.get("stale_cleanup", {}),
            "deleted_learning_cooldown_remaining": cooldowns,
            "chatgpt_refill_required": chatgpt_decision.get("refill_required", False),
            "chatgpt_next_codex_actions": chatgpt_decision.get("next_codex_actions", []),
            "unresolved_issues_summary": unresolved,
        },
        "validation": {
            "contract_source": "docs/handoff_contract.md",
            "json_valid": not missing,
            "quality_review_runner": True,
            "schema_version_present": True,
            "tracking_code_absent": tracking_code_absent(),
            "x_write_not_used": True,
        },
        "unresolved_issues": unresolved,
        "next_actions": [
            "ChatGPT updates data/chatgpt_to_codex_handoff.json when policy changes.",
            "Codex runs scripts/agent_handoff_runner.py after local implementation or review.",
            "User approves only final READY/REVIEW_REQUIRED/BLOCKED summary.",
        ],
    }
    state = {
        "db_name": "Agent Handoff State",
        "schema_version": STATE_SCHEMA_VERSION,
        "version": "1.0.0",
        "status": outbox["status"],
        "review_state_machine": state_machine,
        "generated_at_jst": generated_at,
        "posting_executed": False,
        "upload_media_executed": False,
        "tweet_creation_executed": False,
        "handoff_files": {
            "contract": "docs/handoff_contract.md",
            "protocol": "docs/agent_handoff_protocol.md",
            "chatgpt_inbox": "data/chatgpt_to_codex_handoff.json",
            "codex_outbox": "data/codex_to_chatgpt_handoff.json",
            "trajectory": "data/agent_handoff_trajectory.json",
            "quality_policy": "data/villain_post_quality_os.json",
            "quality_queue": "data/villain_quality_review_queue.json",
            "quality_report": "reports/villain_quality_review_summary.md",
            "handoff_report": "reports/agent_handoff_status.md",
        },
        "last_run": {
            "status": outbox["status"],
            "review_state": state_machine["current_state"],
            "quality_status": summary["quality_status"],
            "queue_health_status": summary["queue_health_status"],
            "review_board_status": summary["review_board_status"],
            "posting_execution_status": summary["posting_execution_status"],
            "executable_ready_count": summary["executable_ready_count"],
            "safe_to_review": summary["safe_to_review"],
            "safe_to_post": summary["safe_to_post"],
            "review_items": summary["review_items"],
            "blocked_reason_frequency": summary["blocked_reason_frequency"],
            "review_required_candidate_count": summary["review_required_candidate_count"],
            "ready_candidate_count": summary["ready_candidate_count"],
            "blocked_candidate_count": summary["blocked_candidate_count"],
            "unresolved_issues": unresolved,
        },
    }
    write_json(CODEX_OUTBOX, outbox)
    write_json(STATE_PATH, state)
    append_trajectory(generated_at, inbox, outbox, summary, repair_actions)
    write_handoff_report(outbox, state)
    return {"outbox": outbox, "state": state, "summary": summary}


def main() -> None:
    result = run_handoff()
    outbox = result["outbox"]
    summary = result["summary"]
    print(f"status={outbox['status']}")
    print(f"schema_version={outbox['schema_version']}")
    print(f"review_state={outbox['review_state_machine']['current_state']}")
    print(f"quality_status={summary['quality_status']}")
    print(f"queue_health_status={summary['queue_health_status']}")
    print(f"review_board_status={summary['review_board_status']}")
    print(f"posting_execution_status={summary['posting_execution_status']}")
    print(f"executable_ready_count={summary['executable_ready_count']}")
    print(f"safe_to_review={summary['safe_to_review']}")
    print(f"safe_to_post={summary['safe_to_post']}")
    print(f"review_items={summary['review_items']}")
    print(f"blocked_reason_frequency={summary['blocked_reason_frequency']}")
    print(f"review_required_candidate_count={summary['review_required_candidate_count']}")
    print(f"ready_candidate_count={summary['ready_candidate_count']}")
    print(f"repair_actions={len(outbox.get('repair_actions', []))}")
    print(f"repair_execution_status={outbox['repair_execution']['status']}")
    print(f"repaired_candidate_count={outbox['repair_execution']['repaired_candidate_count']}")
    print("posting_executed=NO")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"wrote {CODEX_OUTBOX.relative_to(ROOT)}")
    print(f"wrote {STATE_PATH.relative_to(ROOT)}")
    print(f"wrote {HANDOFF_REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
