#!/usr/bin/env python3
"""Score Villain post queue candidates without posting.

This script reads local JSON files, adds scoring metadata to the post queue,
and writes a Markdown report. It does not read .env, upload media, create
tweets, or call X API write actions.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
RULES_PATH = ROOT / "data" / "villain_post_scoring_rules.json"
REPORT_PATH = ROOT / "reports" / "villain_post_quality_scores.md"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def payload_by_queue_id(payload_db: dict) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for payload in payload_db.get("payloads", []):
        source = payload.get("source_queue_id")
        if source:
            result[source] = payload
    return result


def line_count(text: str) -> int:
    return len([line for line in text.splitlines() if line.strip()])


def score_candidate(item: dict, payload: dict, rules: dict) -> dict:
    text = payload.get("caption") or item.get("text", "")
    checks = item.get("checks", {})
    image = item.get("image", {})
    weights = rules.get("weights", {})
    components: dict[str, dict] = {}

    hook_ok = bool(text.splitlines()[0].strip()) if text else False
    components["hook_strength"] = {
        "score": weights.get("hook_strength", 15) if hook_ok else 0,
        "reason": "冒頭に引っかかりがある。" if hook_ok else "冒頭フックが弱い。",
    }

    raindog_ok = any(word in text for word in ["ちょっと", "普通", "まあ言いそう", "言わない"])
    components["raindog_voice"] = {
        "score": weights.get("raindog_voice", 20) if raindog_ok else 10,
        "reason": "ぽろっとした違和感と言い切りすぎない余白がある。" if raindog_ok else "やや説明寄り。",
    }

    villain_ok = "$villain" in text or "#villain" in text or "Villain" in text
    components["villain_context"] = {
        "score": weights.get("villain_context", 15) if villain_ok else 5,
        "reason": "Villain文脈が本文とフッターに入っている。" if villain_ok else "Villain文脈が薄い。",
    }

    compact_ok = len(text) <= 280 and line_count(text) <= 10
    components["brevity_and_spacing"] = {
        "score": weights.get("brevity_and_spacing", 10) if compact_ok else 6,
        "reason": "短文改行で読みやすい。" if compact_ok else "やや長い。",
    }

    new_reader_ok = "Love $villain" in text or "wear it daily" in text
    components["new_reader_clarity"] = {
        "score": weights.get("new_reader_clarity", 10) if new_reader_ok else 6,
        "reason": "ABOUT文言があり、新規にも取っかかりがある。" if new_reader_ok else "初見には文脈不足。",
    }

    note_ok = "ABOUT" in text or "普通" in text
    components["save_or_note_potential"] = {
        "score": weights.get("save_or_note_potential", 10) if note_ok else 5,
        "reason": "ABOUT文言の解釈としてnote化しやすい。" if note_ok else "深掘り余地は限定的。",
    }

    visual_ok = bool(payload.get("image_path")) or image.get("status") in {"approved", "attached"}
    components["visual_fit"] = {
        "score": weights.get("visual_fit", 10) if visual_ok else 4,
        "reason": "画像付き投稿実績/画像導線がある。" if visual_ok else "画像添付が未確定。",
    }

    prohibited_ok = checks.get("prohibited_content_check") == "pass"
    source_ok = checks.get("source_url_confirmed") == "pass"
    components["safety"] = {
        "score": weights.get("safety", 10) if prohibited_ok and source_ok else 4,
        "reason": "禁止事項と元ネタ確認は通過。" if prohibited_ok and source_ok else "安全チェックに未達あり。",
    }

    total = sum(component["score"] for component in components.values())
    risk_factors: list[str] = []
    if payload.get("posted_url") or payload.get("api_image_posted"):
        risk_factors.append("already_posted")
    if not payload.get("image_path") and image.get("status") not in {"approved", "attached"}:
        risk_factors.append("image_missing")
    if item.get("passcode", {}).get("confirmed") is not True:
        risk_factors.append("passcode_unconfirmed")
    if checks.get("source_url_confirmed") != "pass":
        risk_factors.append("source_unchecked")
    if checks.get("prohibited_content_check") != "pass":
        risk_factors.append("prohibited_content_unchecked_or_fail")

    if "already_posted" in risk_factors:
        risk_level = "high"
    elif risk_factors:
        risk_level = "medium"
    else:
        risk_level = "low"

    recommendation = "do_not_repost" if "already_posted" in risk_factors else (
        "candidate" if total >= rules.get("selection_policy", {}).get("recommended_threshold", 80) else "hold"
    )

    reasons = [
        components["hook_strength"]["reason"],
        components["raindog_voice"]["reason"],
        components["villain_context"]["reason"],
    ]
    if risk_factors:
        reasons.append(f"risk factors: {', '.join(risk_factors)}")

    return {
        "version": "1.0.0",
        "score": total,
        "max_score": rules.get("max_score", 100),
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "recommendation": recommendation,
        "reason": " / ".join(reasons),
        "components": components,
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


def write_report(queue_db: dict, rules: dict) -> None:
    lines = [
        "# Villain Post Quality Scores",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "- status: `SCORING_ONLY`",
        "- live posting: `NOT EXECUTED`",
        "- upload_media: `NOT EXECUTED`",
        "- create_tweet: `NOT EXECUTED`",
        "- X API write: `NOT USED`",
        "",
        "## Selection Policy",
        "",
        f"- recommended_threshold: `{rules.get('selection_policy', {}).get('recommended_threshold', 80)}`",
        f"- do_not_repost_if_already_posted: `{rules.get('selection_policy', {}).get('do_not_repost_if_already_posted', True)}`",
        f"- scoring_does_not_unlock_posting: `{rules.get('selection_policy', {}).get('scoring_does_not_unlock_posting', True)}`",
        "",
        "## Queue Scores",
        "",
    ]
    for item in queue_db.get("queue", []):
        scoring = item.get("scoring", {})
        lines.extend(
            [
                f"### `{item.get('queue_id', '')}`",
                "",
                f"- score: `{scoring.get('score', 0)}` / `{scoring.get('max_score', 100)}`",
                f"- risk: `{scoring.get('risk_level', '')}`",
                f"- recommendation: `{scoring.get('recommendation', '')}`",
                f"- reason: {scoring.get('reason', '')}",
                "",
            ]
        )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    queue_db = read_json(QUEUE_PATH)
    payload_db = read_json(PAYLOADS_PATH)
    rules = read_json(RULES_PATH)
    payloads = payload_by_queue_id(payload_db)
    for item in queue_db.get("queue", []):
        payload = payloads.get(item.get("queue_id", ""), {})
        item["scoring"] = score_candidate(item, payload, rules)
    queue_db["scoring_status"] = "SCORING_ONLY"
    queue_db["scoring_updated_at"] = datetime.now(timezone.utc).isoformat()
    write_json(QUEUE_PATH, queue_db)
    write_report(queue_db, rules)
    print(f"wrote scoring to {QUEUE_PATH.relative_to(ROOT)}")
    print(f"wrote scoring report to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
