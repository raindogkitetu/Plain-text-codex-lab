#!/usr/bin/env python3
"""Validate and normalize Villain mandatory posting tokens.

Required Token Layer v1 is read/write only for local JSON and reports. It does
not call X, upload media, create tweets, read .env, or unlock posting.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "villain_required_tokens.json"
REPORT_PATH = ROOT / "reports" / "villain_required_tokens.md"
JST = ZoneInfo("Asia/Tokyo")

MANDATORY_TOKENS = ["#着て稼ぐ", "#villain", "$PPP", "@0xmavillain"]
MANDATORY_FOOTER = " ".join(MANDATORY_TOKENS)
TEXT_KEYS = {"text", "post_text", "caption", "final_text", "draft_text", "tweet_text", "social_post_text"}


def now_jst() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def token_counts(text: str) -> dict[str, int]:
    words = text.split()
    return {token: words.count(token) for token in MANDATORY_TOKENS}


def missing_tokens(text: str) -> list[str]:
    counts = token_counts(text)
    return [token for token in MANDATORY_TOKENS if counts.get(token, 0) == 0]


def duplicate_tokens(text: str) -> list[str]:
    counts = token_counts(text)
    return [token for token in MANDATORY_TOKENS if counts.get(token, 0) > 1]


def normalize_mandatory_tokens(text: str) -> str:
    """Return text with mandatory tokens deduped and appended in fixed order."""

    footer_suffixes: list[str] = []
    body_lines: list[str] = []
    for line in text.strip().splitlines():
        words = line.split()
        if not words:
            body_lines.append("")
            continue

        has_mandatory = any(word in MANDATORY_TOKENS for word in words)
        remaining = [word for word in words if word not in MANDATORY_TOKENS]
        if has_mandatory:
            passcode_like = remaining and all(word.isalnum() and 4 <= len(word) <= 8 for word in remaining)
            if passcode_like:
                footer_suffixes.extend(word for word in remaining if word not in footer_suffixes)
                continue
            if remaining:
                body_lines.append(" ".join(remaining))
            continue

        body_lines.append(line.rstrip())

    while body_lines and not body_lines[-1].strip():
        body_lines.pop()

    footer = MANDATORY_FOOTER
    if footer_suffixes:
        footer = f"{footer} {' '.join(footer_suffixes)}"

    body = "\n".join(body_lines).strip()
    if body:
        return f"{body}\n\n{footer}"
    return footer


def verify_text(text: str) -> dict[str, Any]:
    normalized = normalize_mandatory_tokens(text)
    before_counts = token_counts(text)
    after_counts = token_counts(normalized)
    return {
        "missing_before": missing_tokens(text),
        "duplicates_before": duplicate_tokens(text),
        "changed": normalized != text,
        "before_counts": before_counts,
        "after_counts": after_counts,
        "final_order": MANDATORY_FOOTER,
        "valid_after": not missing_tokens(normalized) and not duplicate_tokens(normalized),
        "normalized_text": normalized,
    }


def verification_summary(text: str) -> dict[str, Any]:
    check = verify_text(text)
    return {
        "required_layer": "Required Token Layer v1",
        "mandatory_footer_order": MANDATORY_FOOTER,
        "missing_before": check["missing_before"],
        "duplicates_before": check["duplicates_before"],
        "changed": check["changed"],
        "before_counts": check["before_counts"],
        "after_counts": check["after_counts"],
        "final_order": check["final_order"],
        "valid_after": check["valid_after"],
    }


def iter_text_fields(value: Any, path: str = "") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if key in TEXT_KEYS and isinstance(child, str) and child.strip():
                check = verify_text(child)
                if check["missing_before"] or check["duplicates_before"] or check["changed"]:
                    findings.append(
                        {
                            "json_path": child_path,
                            "missing_before": check["missing_before"],
                            "duplicates_before": check["duplicates_before"],
                            "changed": check["changed"],
                            "preview": child.replace("\n", " / ")[:180],
                            "normalized_preview": check["normalized_text"].replace("\n", " / ")[:180],
                        }
                    )
            findings.extend(iter_text_fields(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(iter_text_fields(child, f"{path}[{index}]"))
    return findings


def scan_data_files() -> list[dict[str, Any]]:
    scan_results: list[dict[str, Any]] = []
    for path in sorted((ROOT / "data").glob("*.json")):
        try:
            data = read_json(path)
        except json.JSONDecodeError as exc:
            scan_results.append(
                {
                    "file": str(path.relative_to(ROOT)),
                    "json_error": str(exc),
                    "findings": [],
                }
            )
            continue
        findings = iter_text_fields(data)
        if findings:
            scan_results.append({"file": str(path.relative_to(ROOT)), "findings": findings})
    return scan_results


def build_config(scan_results: list[dict[str, Any]]) -> dict[str, Any]:
    missing_ppp = [
        {
            "file": item["file"],
            "json_path": finding["json_path"],
            "preview": finding["preview"],
        }
        for item in scan_results
        for finding in item.get("findings", [])
        if "$PPP" in finding.get("missing_before", [])
    ]
    return {
        "db_name": "Villain Required Token Layer",
        "version": "1.0.0",
        "status": "active_local_validation",
        "updated_at_jst": now_jst(),
        "purpose": "投稿文生成後のfinal textで必須導線トークンを検証し、欠落時は固定順で追加する。",
        "mandatory_tokens": MANDATORY_TOKENS,
        "mandatory_footer_order": MANDATORY_FOOTER,
        "policy": {
            "run_after_text_generation": True,
            "run_before_auto_post_pilot_output": True,
            "dedupe_tokens": True,
            "preserve_existing_passcode_suffix": True,
            "never_remove_for_brevity_or_novelty": True,
            "posting_execution_allowed": False,
            "x_api_write_allowed": False,
            "upload_media_allowed": False,
            "create_tweet_allowed": False,
        },
        "integration_points": {
            "candidate_generation": "scripts/generate_villain_candidates.py normalizes every candidate text before scoring/output.",
            "daily_selection": "data/villain_daily_selection.json treats required_token_layer as a non-optional final_text gate.",
            "auto_post_pilot": "scripts/auto_post_pilot.py normalizes plan item text and records token_verification.",
        },
        "scan_summary": {
            "files_with_text_findings": len(scan_results),
            "ppp_missing_findings": len(missing_ppp),
        },
        "ppp_missing_candidates": missing_ppp,
    }


def write_report(config: dict[str, Any], scan_results: list[dict[str, Any]]) -> None:
    lines = [
        "# Villain Required Token Layer v1",
        "",
        f"- Generated at JST: `{config.get('updated_at_jst')}`",
        "- status: `active_local_validation`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        f"- mandatory_footer_order: `{config.get('mandatory_footer_order')}`",
        "",
        "## Rule",
        "",
        "- 投稿文生成後にmandatory_tokensを検証する。",
        "- 欠けているtokenはfinal text末尾に必ず追加する。",
        "- 重複tokenは1つに整理する。",
        "- token orderは `#着て稼ぐ #villain $PPP @0xmavillain` に固定する。",
        "- mandatory tokenは短文化、自然文最適化、novelty調整で削除しない。",
        "",
        "## Integration",
        "",
        "- candidate generation: `scripts/generate_villain_candidates.py`",
        "- daily selection: `data/villain_daily_selection.json` final_text gate",
        "- auto_post_pilot: `scripts/auto_post_pilot.py` plan item token verification",
        "",
        "## Scan Summary",
        "",
        f"- files_with_text_findings: `{config.get('scan_summary', {}).get('files_with_text_findings')}`",
        f"- ppp_missing_findings: `{config.get('scan_summary', {}).get('ppp_missing_findings')}`",
        "",
        "## Missing `$PPP` Findings",
        "",
    ]
    missing_ppp = config.get("ppp_missing_candidates", [])
    if not missing_ppp:
        lines.append("- None")
    for item in missing_ppp:
        lines.extend(
            [
                f"- `{item.get('file')}` / `{item.get('json_path')}`",
                f"  - preview: {item.get('preview')}",
            ]
        )

    lines.extend(["", "## All Token Findings", ""])
    if not scan_results:
        lines.append("- None")
    for item in scan_results:
        lines.append(f"### `{item.get('file')}`")
        if item.get("json_error"):
            lines.append(f"- json_error: `{item.get('json_error')}`")
            continue
        for finding in item.get("findings", []):
            lines.extend(
                [
                    f"- `{finding.get('json_path')}`",
                    f"  - missing_before: `{', '.join(finding.get('missing_before', [])) or 'none'}`",
                    f"  - duplicates_before: `{', '.join(finding.get('duplicates_before', [])) or 'none'}`",
                    f"  - changed_by_normalizer: `{str(finding.get('changed')).lower()}`",
                ]
            )
    lines.append("")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan Villain text fields for mandatory token compliance.")
    parser.add_argument("--write-config", action="store_true", help="Write data/villain_required_tokens.json.")
    args = parser.parse_args()
    scan_results = scan_data_files()
    config = build_config(scan_results)
    if args.write_config:
        write_json(CONFIG_PATH, config)
    write_report(config, scan_results)
    print("status=REQUIRED_TOKEN_SCAN_COMPLETE")
    print(f"mandatory_footer_order={MANDATORY_FOOTER}")
    print(f"ppp_missing_findings={config['scan_summary']['ppp_missing_findings']}")
    print("live_posting=NOT_EXECUTED")
    print("x_api_write=NOT_USED")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    if args.write_config:
        print(f"wrote {CONFIG_PATH.relative_to(ROOT)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
