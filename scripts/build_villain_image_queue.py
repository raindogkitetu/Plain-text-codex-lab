#!/usr/bin/env python3
"""Build a Villain image candidate queue from creative output.

This script only reads local files and writes JSON/Markdown. It does not
generate images, read .env, upload media, create tweets, or call X API write
actions.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
CREATIVE_RULES_PATH = ROOT / "data" / "villain_creative_rules.json"
CREATIVE_REPORT_PATH = ROOT / "reports" / "villain_creative_output.md"
QUEUE_PATH = ROOT / "data" / "villain_image_queue.json"
REPORT_PATH = ROOT / "reports" / "villain_image_candidates.md"

MAX_CANDIDATES_PER_POST = 3
STATUS_VALUES = ["generated", "review_needed", "approved", "rejected"]


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def extract_recommended_mode(report_text: str) -> str:
    match = re.search(r"## 1\. 推奨モード\s+- `([^`]+)`", report_text)
    return match.group(1) if match else "OBSERVER_MODE"


def prompt_for_mode(mode: str, caption: str, mode_rules: dict) -> str:
    composition = mode_rules.get("composition", {})
    return (
        "Cyberpunk anime style, cinematic Villain visual, hooded figure, teal and pink neon, "
        "rainy city atmosphere, no AI face close-up, no cheap neon, no overly NFT-like look. "
        f"Mode {mode}; subject {composition.get('subject_ratio')}; background {composition.get('background_ratio')}; "
        f"viewpoint {composition.get('viewpoint')}; color {composition.get('color_temperature')}; "
        f"rain {'yes' if composition.get('rain') else 'no'}. "
        f"Caption reference: {caption!r}."
    )


def candidate_modes(recommended_mode: str) -> list[str]:
    modes = [recommended_mode, "POSTER_MODE", "STREET_MODE", "OBSERVER_MODE", "BRIGHT_MODE"]
    unique: list[str] = []
    for mode in modes:
        if mode not in unique:
            unique.append(mode)
    return unique[:MAX_CANDIDATES_PER_POST]


def build_queue(payload: dict, creative_rules: dict, recommended_mode: str, generated_at: str) -> list[dict]:
    source_post_id = payload.get("payload_id", "")
    caption = payload.get("caption", "")
    available_modes = creative_rules.get("available_modes", {})
    queue = []
    for index, mode in enumerate(candidate_modes(recommended_mode), start=1):
        mode_rules = available_modes.get(mode, {})
        queue.append(
            {
                "queue_id": f"vln-imgq-{source_post_id}-{index:03d}",
                "source_post_id": source_post_id,
                "image_mode": mode,
                "prompt": prompt_for_mode(mode, caption, mode_rules),
                "image_status": "review_needed",
                "selected_for_post": False,
                "human_review_status": "review_needed",
                "notes": "候補生成のみ。画像生成、media upload、API投稿は未実行。",
                "created_at": generated_at,
            }
        )
    return queue


def write_report(queue_db: dict) -> None:
    lines = [
        "# Villain Image Candidates",
        "",
        f"- Generated at: `{queue_db.get('generated_at', '')}`",
        f"- status: `{queue_db.get('status', 'BLOCKED')}`",
        f"- source_post_id: `{queue_db.get('source_post_id', '')}`",
        f"- candidate_count: `{queue_db.get('candidate_count', 0)}`",
        "- image generation: `NOT EXECUTED`",
        "- upload_media: `NOT EXECUTED`",
        "- create_tweet: `NOT EXECUTED`",
        "- X API write: `NOT USED`",
        "",
        "## Candidates",
        "",
    ]
    for item in queue_db.get("queue", []):
        lines.extend(
            [
                f"### `{item.get('queue_id', '')}`",
                "",
                f"- image_mode: `{item.get('image_mode', '')}`",
                f"- image_status: `{item.get('image_status', '')}`",
                f"- selected_for_post: `{item.get('selected_for_post', False)}`",
                f"- human_review_status: `{item.get('human_review_status', '')}`",
                f"- notes: {item.get('notes', '')}",
                "",
                "```text",
                item.get("prompt", ""),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Human Selection",
            "",
            "- 画像を採用する場合は、人間が1件だけ `selected_for_post=true` にする。",
            "- 現段階では全候補 `review_needed` のまま。",
            "- BLOCKED維持。画像生成、upload_media、create_tweetは実行しない。",
            "",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    payload_db = read_json(PAYLOADS_PATH)
    creative_rules = read_json(CREATIVE_RULES_PATH)
    creative_report = read_text(CREATIVE_REPORT_PATH)
    payloads = payload_db.get("payloads", [])
    payload = payloads[0] if payloads else {}
    generated_at = datetime.now(timezone.utc).isoformat()
    recommended_mode = extract_recommended_mode(creative_report)
    queue = build_queue(payload, creative_rules, recommended_mode, generated_at)
    queue_db = {
        "db_name": "Villain Image Queue",
        "version": "1.0.0",
        "status": "BLOCKED",
        "max_candidates_per_post": MAX_CANDIDATES_PER_POST,
        "allowed_status_values": STATUS_VALUES,
        "source_post_id": payload.get("payload_id", ""),
        "recommended_mode": recommended_mode,
        "candidate_count": len(queue),
        "generated_at": generated_at,
        "safety": {
            "image_generation_executed": False,
            "upload_media_executed": False,
            "create_tweet_executed": False,
            "x_api_write_used": False,
        },
        "queue": queue,
    }
    write_json(QUEUE_PATH, queue_db)
    write_report(queue_db)
    print(f"wrote image queue to {QUEUE_PATH.relative_to(ROOT)}")
    print(f"wrote image candidates report to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
