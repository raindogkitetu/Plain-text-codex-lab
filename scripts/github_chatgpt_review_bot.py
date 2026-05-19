#!/usr/bin/env python3
"""Run the GitHub-hosted ChatGPT review bridge.

This script is intentionally review-only. It reads the bridge prompt, asks the
OpenAI API for a decision JSON, validates hard invariants, and writes the
decision into data/chatgpt_to_codex_handoff.json for the normal ingestor.

It never posts, uploads media, creates tweets, or generates tracking codes.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_PROMPT = ROOT / "reports" / "chatgpt_bridge_prompt.md"
CHATGPT_INBOX = ROOT / "data" / "chatgpt_to_codex_handoff.json"
BRIDGE_EXCHANGE = ROOT / "data" / "chatgpt_bridge_exchange.json"
BOT_REPORT = ROOT / "reports" / "chatgpt_github_review_bot.md"
JST = ZoneInfo("Asia/Tokyo")

DECISION_SCHEMA_VERSION = "handoff.chatgpt_decision.v1"
INBOX_SCHEMA_VERSION = "handoff.chatgpt_to_codex.v1"
EXCHANGE_SCHEMA_VERSION = "handoff.chatgpt_bridge_exchange.v1"
DEFAULT_MODEL = "gpt-5.4-mini"

SYSTEM_PROMPT = """You are the ChatGPT Review Agent for Villain Auto Posting OS.
Return JSON only. Do not approve posting. Do not create GitHub issues. Do not
ask for media upload or tweet creation. Keep safe_to_post=false and
posting_execution_status=BLOCKED. Never generate tracking_code or passcodes."""


def now_jst() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def has_key(value: Any, target: str) -> bool:
    if isinstance(value, dict):
        return any(key == target or has_key(nested, target) for key, nested in value.items())
    if isinstance(value, list):
        return any(has_key(item, target) for item in value)
    return False


def extract_output_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    chunks: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                chunks.append(text)
    if chunks:
        return "\n".join(chunks)
    choices = response.get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            return content
    raise ValueError("openai_response_missing_text")


def parse_json_text(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = [line for line in stripped.splitlines() if not line.strip().startswith("```")]
        stripped = "\n".join(lines).strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        parsed = json.loads(stripped[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("decision_json_not_object")
    return parsed


def normalize_decision(decision: dict[str, Any], generated_at: str, model: str) -> dict[str, Any]:
    decision.setdefault("schema_version", DECISION_SCHEMA_VERSION)
    decision["safe_to_post"] = False
    decision["posting_execution_status"] = "BLOCKED"
    decision["posting_execution_allowed"] = False
    decision["posting_performed"] = False
    decision["upload_media_performed"] = False
    decision["create_tweet_performed"] = False
    decision["github_issue_created"] = False
    decision["generated_by"] = "github_chatgpt_review_bot"
    decision["generated_at_jst"] = generated_at
    decision["model"] = model
    if "chatgpt_review_decision" not in decision:
        decision["chatgpt_review_decision"] = {
            "decision": decision.get("decision", "REVIEW_ONLY_DECISION"),
            "next_codex_actions": [],
        }
    return decision


def validate_decision(decision: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if decision.get("schema_version") != DECISION_SCHEMA_VERSION:
        errors.append(f"invalid_schema_version:{decision.get('schema_version')}")
    if decision.get("safe_to_post") is not False:
        errors.append("safe_to_post_not_false")
    if decision.get("posting_execution_status") != "BLOCKED":
        errors.append("posting_execution_status_not_blocked")
    if decision.get("posting_execution_allowed") is not False:
        errors.append("posting_execution_allowed_not_false")
    if decision.get("posting_performed") is not False:
        errors.append("posting_performed_not_false")
    if decision.get("upload_media_performed") is not False:
        errors.append("upload_media_performed_not_false")
    if decision.get("create_tweet_performed") is not False:
        errors.append("create_tweet_performed_not_false")
    if has_key(decision, "tracking_code"):
        errors.append("tracking_code_key_detected")
    if not isinstance(decision.get("chatgpt_review_decision"), dict):
        errors.append("missing_chatgpt_review_decision")
    return errors


def call_openai(prompt: str, model: str, timeout: int) -> dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY_missing")
    body = {
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "model": model,
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed OpenAI API endpoint.
        return json.loads(response.read().decode("utf-8"))


def write_inbox(decision: dict[str, Any]) -> None:
    inbox = {
        "chatgpt_review_decision": decision.get("chatgpt_review_decision", {}),
        "decision_payload": decision,
        "posting_execution_status": "BLOCKED",
        "safe_to_post": False,
        "schema_version": INBOX_SCHEMA_VERSION,
        "source": "github_chatgpt_review_bot",
    }
    write_json(CHATGPT_INBOX, inbox)


def update_exchange(generated_at: str, status: str, model: str, errors: list[str]) -> None:
    exchange = read_json(
        BRIDGE_EXCHANGE,
        {
            "db_name": "ChatGPT Bridge Exchange",
            "schema_version": EXCHANGE_SCHEMA_VERSION,
            "version": "1.0.0",
        },
    )
    exchange.update(
        {
            "github_review_bot": {
                "errors": errors,
                "last_run_at_jst": generated_at,
                "model": model,
                "status": status,
            },
            "last_chatgpt_response_errors": errors,
            "last_chatgpt_response_ingested_at_jst": generated_at,
            "last_chatgpt_response_status": status,
            "posting_executed": False,
            "safe_to_post": False,
            "tweet_creation_executed": False,
            "upload_media_executed": False,
        }
    )
    write_json(BRIDGE_EXCHANGE, exchange)


def update_report(generated_at: str, status: str, model: str, errors: list[str]) -> None:
    lines = [
        "# ChatGPT GitHub Review Bot",
        "",
        f"- last_run_at_jst: `{generated_at}`",
        f"- status: `{status}`",
        f"- model: `{model}`",
        f"- errors: `{errors if errors else 'none'}`",
        "- safe_to_post: `false`",
        "- posting_execution_status: `BLOCKED`",
        "- posting executed: `NO`",
        "- upload executed: `NO`",
        "- tweet creation executed: `NO`",
        "",
        "This bot only writes review decisions for Codex. It does not post, upload media, create tweets, generate tracking codes, or create GitHub issues.",
        "",
    ]
    BOT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    BOT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    generated_at = now_jst()
    model = args.model or os.environ.get("OPENAI_MODEL") or DEFAULT_MODEL
    prompt = read_text(BRIDGE_PROMPT)
    if not prompt:
        errors = ["bridge_prompt_missing"]
        update_exchange(generated_at, "FAILED", model, errors)
        update_report(generated_at, "FAILED", model, errors)
        print("status=FAILED")
        print(f"errors={errors}")
        return 1
    if args.dry_run:
        update_exchange(generated_at, "DRY_RUN", model, [])
        update_report(generated_at, "DRY_RUN", model, [])
        print("status=DRY_RUN")
        print("posting_executed=NO")
        print("upload_media=NOT_EXECUTED")
        print("create_tweet=NOT_EXECUTED")
        return 0

    try:
        response = call_openai(prompt, model, args.timeout)
        raw_text = extract_output_text(response)
        decision = normalize_decision(parse_json_text(raw_text), generated_at, model)
        errors = validate_decision(decision)
    except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        errors = [f"review_bot_error:{type(error).__name__}:{error}"]
        update_exchange(generated_at, "FAILED", model, errors)
        update_report(generated_at, "FAILED", model, errors)
        print("status=FAILED")
        print(f"errors={errors}")
        print("posting_executed=NO")
        print("upload_media=NOT_EXECUTED")
        print("create_tweet=NOT_EXECUTED")
        return 1

    if errors:
        update_exchange(generated_at, "REJECTED", model, errors)
        update_report(generated_at, "REJECTED", model, errors)
        print("status=REJECTED")
        print(f"errors={errors}")
        print("posting_executed=NO")
        print("upload_media=NOT_EXECUTED")
        print("create_tweet=NOT_EXECUTED")
        return 1

    write_inbox(decision)
    update_exchange(generated_at, "ACCEPTED", model, [])
    update_report(generated_at, "ACCEPTED", model, [])
    print("status=ACCEPTED")
    print("wrote data/chatgpt_to_codex_handoff.json")
    print("posting_executed=NO")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    time.sleep(0)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run GitHub-hosted ChatGPT review bridge.")
    parser.add_argument("--dry-run", action="store_true", help="Validate local files without calling OpenAI.")
    parser.add_argument("--model", default="", help="OpenAI model. Defaults to OPENAI_MODEL or a repo default.")
    parser.add_argument("--timeout", type=int, default=90, help="OpenAI request timeout in seconds.")
    return parser.parse_args()


def main() -> None:
    raise SystemExit(run(parse_args()))


if __name__ == "__main__":
    main()
