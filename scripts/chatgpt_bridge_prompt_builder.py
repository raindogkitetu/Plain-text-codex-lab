#!/usr/bin/env python3
"""Build the ChatGPT bridge prompt from repo-local handoff artifacts.

This script only reads review artifacts and writes a prompt/report for ChatGPT.
It never posts, uploads media, creates tweets, or generates tracking codes.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
CODEX_OUTBOX = ROOT / "data" / "codex_to_chatgpt_handoff.json"
HANDOFF_STATE = ROOT / "data" / "agent_handoff_state.json"
QUALITY_QUEUE = ROOT / "data" / "villain_quality_review_queue.json"
HANDOFF_REPORT = ROOT / "reports" / "agent_handoff_status.md"
QUALITY_REPORT = ROOT / "reports" / "villain_quality_review_summary.md"
BRIDGE_PROMPT = ROOT / "reports" / "chatgpt_bridge_prompt.md"
BRIDGE_EXCHANGE = ROOT / "data" / "chatgpt_bridge_exchange.json"
JST = ZoneInfo("Asia/Tokyo")
SCHEMA_VERSION = "handoff.chatgpt_bridge_exchange.v1"

INPUT_FILES = [
    CODEX_OUTBOX,
    HANDOFF_STATE,
    QUALITY_QUEUE,
    HANDOFF_REPORT,
    QUALITY_REPORT,
]

EXPECTED_RESPONSE_SCHEMA = {
    "schema_version": "handoff.chatgpt_decision.v1",
    "safe_to_post": False,
    "posting_execution_status": "BLOCKED",
    "chatgpt_review_decision": {
        "decision": "REVIEW_READY_NOT_POST_READY | BLOCKED | REQUEST_REPAIR | REQUEST_REFILL",
        "approved_for_review": [],
        "not_approved_for_posting": [],
        "must_remain_blocked": [],
        "repair_candidates": [],
        "image_replacement_required": [],
        "context_evidence_required": [],
        "archive_or_drop_candidates": [],
        "refill_required": False,
        "next_codex_actions": [],
        "policy_clarification": [],
    },
}


def now_jst() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fenced(label: str, body: str, language: str = "") -> str:
    info = f" {language}" if language else ""
    return f"## {label}\n\n```{info}\n{body.strip()}\n```\n"


def content_bundle() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): read_text(path) for path in INPUT_FILES}


def bridge_hash(bundle: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for name in sorted(bundle):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bundle[name].encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def build_prompt(generated_at: str, bundle: dict[str, str], prompt_hash: str) -> str:
    outbox = read_json(CODEX_OUTBOX, {})
    state = read_json(HANDOFF_STATE, {})
    queue = read_json(QUALITY_QUEUE, {})
    lines = [
        "# ChatGPT Bridge Prompt",
        "",
        "You are ChatGPT reviewing the Villain Auto Posting OS handoff from Codex.",
        "Return only JSON matching the expected response schema. Do not ask Codex to post.",
        "",
        "## Safety Invariants",
        "",
        "- safe_to_post=false",
        "- posting_execution_status=BLOCKED",
        "- no upload_media",
        "- no create_tweet",
        "- no tracking_code generation",
        "- human approval required before any posting path",
        "- passcodes must come only from active values in data/villain_passcodes.json",
        "",
        "## Current Summary",
        "",
        f"- generated_at_jst: `{generated_at}`",
        f"- bridge_prompt_hash: `{prompt_hash}`",
        f"- codex_outbox_status: `{outbox.get('status', '')}`",
        f"- review_state: `{outbox.get('review_state_machine', {}).get('current_state', '')}`",
        f"- queue_health_status: `{queue.get('queue_health_status', '')}`",
        f"- review_board_status: `{queue.get('review_board_status', '')}`",
        f"- posting_execution_status: `{queue.get('posting_execution_status', '')}`",
        f"- safe_to_review: `{str(queue.get('safe_to_review', False)).lower()}`",
        f"- safe_to_post: `{str(queue.get('safe_to_post', False)).lower()}`",
        f"- state_last_run: `{state.get('last_run', {})}`",
        "",
        "## Task For ChatGPT",
        "",
        "1. Decide whether current candidates should stay in review, be repaired, be refilled, or remain blocked.",
        "2. Keep READY as review-ready only, not post-ready.",
        "3. Keep `safe_to_post=false` and `posting_execution_status=BLOCKED` unless a separate explicit human approval artifact exists.",
        "4. Return only decision JSON. No prose outside JSON.",
        "",
        fenced("Expected Response Schema", json.dumps(EXPECTED_RESPONSE_SCHEMA, ensure_ascii=False, indent=2), "json"),
    ]
    for name in sorted(bundle):
        language = "json" if name.endswith(".json") else "markdown"
        lines.append(fenced(name, bundle[name], language))
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    generated_at = now_jst()
    bundle = content_bundle()
    prompt_hash = bridge_hash(bundle)
    prompt = build_prompt(generated_at, bundle, prompt_hash)
    BRIDGE_PROMPT.parent.mkdir(parents=True, exist_ok=True)
    BRIDGE_PROMPT.write_text(prompt, encoding="utf-8")
    exchange = {
        "bridge_prompt_hash": prompt_hash,
        "db_name": "ChatGPT Bridge Exchange",
        "expected_response_schema": EXPECTED_RESPONSE_SCHEMA,
        "generated_at_jst": generated_at,
        "input_files": sorted(bundle),
        "last_chatgpt_response_status": "PENDING",
        "posting_executed": False,
        "safe_to_post": False,
        "schema_version": SCHEMA_VERSION,
        "tweet_creation_executed": False,
        "upload_media_executed": False,
        "version": "1.0.0",
    }
    write_json(BRIDGE_EXCHANGE, exchange)
    print(f"bridge_prompt_hash={prompt_hash}")
    print(f"wrote {BRIDGE_PROMPT.relative_to(ROOT)}")
    print(f"wrote {BRIDGE_EXCHANGE.relative_to(ROOT)}")
    print("posting_executed=NO")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")


if __name__ == "__main__":
    main()
