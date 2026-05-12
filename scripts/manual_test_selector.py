#!/usr/bin/env python3
"""Select Villain manual-test candidates from existing dry-run artifacts."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_PATH = ROOT / "data" / "villain_generated_candidates.json"
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
QUALITY_REPORT_PATH = ROOT / "reports" / "villain_post_quality_scores.md"
PERSONA_REPORT_PATH = ROOT / "reports" / "villain_persona_scorer.md"
TIME_REPORT_PATH = ROOT / "reports" / "villain_post_time_optimizer.md"
SAFE_REPORT_PATH = ROOT / "reports" / "villain_safe_post_executor.md"
REPORT_PATH = ROOT / "reports" / "villain_manual_test_selection.md"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def parse_section_values(report: str, score_key: str) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    current = ""
    for line in report.splitlines():
        heading = re.match(r"^### `([^`]+)`", line)
        if heading:
            current = heading.group(1)
            values.setdefault(current, {})
            continue
        if not current:
            continue
        score_match = re.match(rf"^- {re.escape(score_key)}: `([^`]+)`", line)
        if score_match:
            raw = score_match.group(1)
            values[current][score_key] = int(raw.split()[0])
        risk_match = re.match(r"^- risk: `([^`]+)`", line)
        if risk_match:
            values[current]["risk"] = risk_match.group(1)
        window_match = re.match(r"^- primary_window_jst: `([^`]+)`", line)
        if window_match:
            values[current]["recommended_time_window"] = window_match.group(1)
    return values


def parse_safe_status(report: str) -> str:
    match = re.search(r"^- safe_post_status: `([^`]+)`", report, re.MULTILINE)
    return match.group(1) if match else "BLOCK"


def candidates_from_db(db: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": candidate.get("candidate_id", ""),
            "queue_id": "",
            "post_type": candidate.get("category", "UNKNOWN"),
            "text": candidate.get("text", ""),
            "quality_score": candidate.get("quality_prediction"),
            "risk": candidate.get("risk_prediction", "unknown"),
        }
        for candidate in db.get("candidates", [])
    ]


def queue_from_db(db: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": "",
            "queue_id": item.get("queue_id", ""),
            "post_type": item.get("post_type", "UNKNOWN"),
            "text": item.get("text", ""),
            "quality_score": item.get("scoring", {}).get("score"),
            "risk": item.get("scoring", {}).get("risk_level", "unknown"),
        }
        for item in db.get("queue", [])
    ]


def enrich_items(
    items: list[dict[str, Any]],
    quality_scores: dict[str, dict[str, Any]],
    persona_scores: dict[str, dict[str, Any]],
    time_scores: dict[str, dict[str, Any]],
    safe_status: str,
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for item in items:
        item_id = item.get("candidate_id") or item.get("queue_id")
        quality = quality_scores.get(item_id, {})
        persona = persona_scores.get(item_id, {})
        timing = time_scores.get(item_id, {})
        enriched.append(
            {
                **item,
                "quality_score": item.get("quality_score") or quality.get("score"),
                "risk": item.get("risk") if item.get("risk") != "unknown" else quality.get("risk", "unknown"),
                "persona_score": persona.get("persona_score"),
                "recommended_time_window": timing.get("recommended_time_window", ""),
                "safe_post_status": safe_status,
            }
        )
    return enriched


def rank_key(item: dict[str, Any]) -> tuple[int, int, int, int]:
    risk_rank = {"low": 2, "medium": 1}.get(item.get("risk"), 0)
    time_rank = 1 if item.get("recommended_time_window") else 0
    return (
        item.get("quality_score") or 0,
        item.get("persona_score") or 0,
        risk_rank,
        time_rank,
    )


def qualifies(item: dict[str, Any]) -> bool:
    return (
        (item.get("quality_score") or 0) >= 80
        and (item.get("persona_score") or 0) >= 80
        and item.get("risk") in {"low", "medium"}
        and item.get("safe_post_status") == "BLOCK"
    )


def manual_next_action(item: dict[str, Any]) -> str:
    window = item.get("recommended_time_window") or "推奨時間未確定"
    return f"{window} を目安に、人間レビュー用の画像・最終文面を確認。投稿はまだしない。"


def write_report(selected: list[dict[str, Any]], excluded: list[dict[str, Any]], safe_status: str) -> None:
    lines = [
        "# Villain Manual Test Selection",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "- status: `DRY_RUN_ONLY`",
        "- DB mutation: `NOT_EXECUTED`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        f"- inherited_safe_post_status: `{safe_status}`",
        f"- manual_test_candidates_count: `{len(selected)}`",
        "",
        "## manual_test_candidates",
        "",
    ]
    if not selected:
        lines.append("- none")
    for item in selected:
        lines.extend(
            [
                f"### `{item.get('candidate_id') or item.get('queue_id')}`",
                "",
                f"- candidate_id: `{item.get('candidate_id')}`",
                f"- queue_id: `{item.get('queue_id')}`",
                f"- post_type: `{item.get('post_type')}`",
                f"- quality_score: `{item.get('quality_score')}`",
                f"- persona_score: `{item.get('persona_score')}`",
                f"- risk: `{item.get('risk')}`",
                f"- recommended_time_window: `{item.get('recommended_time_window')}`",
                f"- manual_next_action: {manual_next_action(item)}",
                "",
                "```text",
                item.get("text", ""),
                "```",
                "",
            ]
        )
    lines.extend(["## excluded_candidates", ""])
    if not excluded:
        lines.append("- none")
    for item in excluded:
        lines.append(
            f"- `{item.get('candidate_id') or item.get('queue_id')}`: "
            f"quality={item.get('quality_score')}, persona={item.get('persona_score')}, "
            f"risk={item.get('risk')}, safe_post_status={item.get('safe_post_status')}"
        )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    candidates_db = read_json(CANDIDATES_PATH)
    queue_db = read_json(QUEUE_PATH)
    quality_scores = parse_section_values(read_text(QUALITY_REPORT_PATH), "score")
    persona_scores = parse_section_values(read_text(PERSONA_REPORT_PATH), "persona_score")
    time_scores = parse_section_values(read_text(TIME_REPORT_PATH), "persona_score")
    safe_status = parse_safe_status(read_text(SAFE_REPORT_PATH))
    items = enrich_items(
        candidates_from_db(candidates_db) + queue_from_db(queue_db),
        quality_scores,
        persona_scores,
        time_scores,
        safe_status,
    )
    selected = sorted([item for item in items if qualifies(item)], key=rank_key, reverse=True)[:5]
    excluded = [item for item in items if item not in selected]
    write_report(selected, excluded, safe_status)
    print("status=DRY_RUN_ONLY")
    print("db_mutation=NOT_EXECUTED")
    print(f"selected={len(selected)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
