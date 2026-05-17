#!/usr/bin/env python3
"""Run the repo-local ChatGPT -> Codex handoff loop without posting."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from post_quality_os import build_review, write_report


ROOT = Path(__file__).resolve().parents[1]
CHATGPT_INBOX = ROOT / "data" / "chatgpt_to_codex_handoff.json"
CODEX_OUTBOX = ROOT / "data" / "codex_to_chatgpt_handoff.json"
STATE_PATH = ROOT / "data" / "agent_handoff_state.json"
QUALITY_QUEUE = ROOT / "data" / "villain_quality_review_queue.json"
HANDOFF_REPORT = ROOT / "reports" / "agent_handoff_status.md"
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
    return {
        "quality_status": review.get("status", ""),
        "review_items": len(items),
        "blockers": blockers,
        "warnings": warnings,
    }


def write_handoff_report(outbox: dict[str, Any], state: dict[str, Any]) -> None:
    result = outbox.get("implementation_result", {})
    validation = outbox.get("validation", {})
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
    issues = outbox.get("unresolved_issues", [])
    lines.extend([f"- {issue}" for issue in issues] or ["- none"])
    lines.extend(["", "## Next Actions", ""])
    actions = outbox.get("next_actions", [])
    lines.extend([f"- {action}" for action in actions] or ["- none"])
    lines.append("")
    HANDOFF_REPORT.parent.mkdir(parents=True, exist_ok=True)
    HANDOFF_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    generated_at = now_jst()
    inbox = read_json(CHATGPT_INBOX, {})
    missing = missing_files()
    review = build_review()
    write_json(QUALITY_QUEUE, review)
    write_report(review)
    summary = summarize_review(review)
    unresolved = list(inbox.get("open_questions_for_codex", []))
    if missing:
        unresolved.append("Required handoff files missing: " + ", ".join(missing))

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
            "unresolved_issues": unresolved,
        },
    }
    write_json(CODEX_OUTBOX, outbox)
    write_json(STATE_PATH, state)
    write_handoff_report(outbox, state)
    print(f"status={outbox['status']}")
    print(f"quality_status={summary['quality_status']}")
    print(f"review_items={summary['review_items']}")
    print("posting_executed=NO")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"wrote {CODEX_OUTBOX.relative_to(ROOT)}")
    print(f"wrote {STATE_PATH.relative_to(ROOT)}")
    print(f"wrote {HANDOFF_REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
