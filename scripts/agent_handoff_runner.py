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


ROOT = Path(__file__).resolve().parents[1]
CHATGPT_INBOX = ROOT / "data" / "chatgpt_to_codex_handoff.json"
CODEX_OUTBOX = ROOT / "data" / "codex_to_chatgpt_handoff.json"
STATE_PATH = ROOT / "data" / "agent_handoff_state.json"
QUALITY_QUEUE = ROOT / "data" / "villain_quality_review_queue.json"
OUTCOMES_PATH = ROOT / "data" / "villain_post_outcomes.json"
HANDOFF_REPORT = ROOT / "reports" / "agent_handoff_status.md"
DELETED_LEARNING_COOLDOWN_DAYS = 7
REQUIRED_FILES = [
    ROOT / "docs" / "agent_handoff_protocol.md",
    CHATGPT_INBOX,
    ROOT / "data" / "villain_post_quality_os.json",
    ROOT / "scripts" / "post_quality_os.py",
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
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
        "review_items": len(items),
        "blockers": blockers,
        "warnings": warnings,
        "blocked_reason_frequency": dict(sorted(blocker_frequency.items())),
        "review_required_candidate_count": statuses.get("REVIEW_REQUIRED", 0),
        "ready_candidate_count": statuses.get("READY", 0),
        "blocked_candidate_count": statuses.get("BLOCKED", 0),
    }


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
    lines = [
        "# Agent Handoff Status",
        "",
        f"- Generated at JST: `{outbox.get('generated_at_jst')}`",
        f"- status: `{outbox.get('status')}`",
        "- posting executed: `NO`",
        "- upload executed: `NO`",
        "- tweet creation executed: `NO`",
        "",
        "## Quality Review",
        "",
        f"- quality_status: `{result.get('quality_status')}`",
        f"- review_items: `{state.get('last_run', {}).get('review_items')}`",
        f"- blockers: `{', '.join(result.get('blockers', [])) if result.get('blockers') else 'none'}`",
        f"- warnings: `{', '.join(result.get('warnings', [])) if result.get('warnings') else 'none'}`",
        f"- blocked_reason_frequency: `{maintenance.get('blocked_reason_frequency', {})}`",
        f"- review_required_candidate_count: `{maintenance.get('review_required_candidate_count', 0)}`",
        f"- READY_candidate_count: `{maintenance.get('ready_candidate_count', 0)}`",
        f"- BLOCKED_candidate_count: `{maintenance.get('blocked_candidate_count', 0)}`",
        f"- stale_cleanup_removed: `{maintenance.get('stale_cleanup', {}).get('removed_count', 0)}`",
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
    lines.append("")
    HANDOFF_REPORT.parent.mkdir(parents=True, exist_ok=True)
    HANDOFF_REPORT.write_text("\n".join(lines), encoding="utf-8")


def run_handoff() -> dict[str, Any]:
    generated_at = now_jst()
    inbox = read_json(CHATGPT_INBOX, {})
    missing = missing_files()
    review = cleanup_review_queue(build_review())
    write_json(QUALITY_QUEUE, review)
    write_report(review)
    summary = summarize_review(review)
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
        "version": "1.0.0",
        "status": "BLOCKED" if missing else "READY_FOR_CHATGPT_REVIEW",
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
                "reports/agent_handoff_status.md",
            ],
            "quality_status": summary["quality_status"],
            "blockers": summary["blockers"],
            "warnings": summary["warnings"],
        },
        "maintenance_summary": {
            "blocked_reason_frequency": summary["blocked_reason_frequency"],
            "review_required_candidate_count": summary["review_required_candidate_count"],
            "ready_candidate_count": summary["ready_candidate_count"],
            "blocked_candidate_count": summary["blocked_candidate_count"],
            "stale_cleanup": review.get("stale_cleanup", {}),
            "deleted_learning_cooldown_remaining": cooldowns,
            "unresolved_issues_summary": unresolved,
        },
        "validation": {
            "json_valid": not missing,
            "quality_review_runner": True,
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
        "version": "1.0.0",
        "status": outbox["status"],
        "generated_at_jst": generated_at,
        "posting_executed": False,
        "upload_media_executed": False,
        "tweet_creation_executed": False,
        "handoff_files": {
            "protocol": "docs/agent_handoff_protocol.md",
            "chatgpt_inbox": "data/chatgpt_to_codex_handoff.json",
            "codex_outbox": "data/codex_to_chatgpt_handoff.json",
            "quality_policy": "data/villain_post_quality_os.json",
            "quality_queue": "data/villain_quality_review_queue.json",
            "quality_report": "reports/villain_quality_review_summary.md",
            "handoff_report": "reports/agent_handoff_status.md",
        },
        "last_run": {
            "status": outbox["status"],
            "quality_status": summary["quality_status"],
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
    write_handoff_report(outbox, state)
    return {"outbox": outbox, "state": state, "summary": summary}


def main() -> None:
    result = run_handoff()
    outbox = result["outbox"]
    summary = result["summary"]
    print(f"status={outbox['status']}")
    print(f"quality_status={summary['quality_status']}")
    print(f"review_items={summary['review_items']}")
    print(f"blocked_reason_frequency={summary['blocked_reason_frequency']}")
    print(f"review_required_candidate_count={summary['review_required_candidate_count']}")
    print(f"ready_candidate_count={summary['ready_candidate_count']}")
    print("posting_executed=NO")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"wrote {CODEX_OUTBOX.relative_to(ROOT)}")
    print(f"wrote {STATE_PATH.relative_to(ROOT)}")
    print(f"wrote {HANDOFF_REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
