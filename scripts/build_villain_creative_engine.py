#!/usr/bin/env python3
"""Build Villain Creative Engine output from a draft caption.

This script only reads local JSON files and writes a Markdown report. It does
not read .env, generate images, upload media, create tweets, or call X API
write actions.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
CREATIVE_RULES_PATH = ROOT / "data" / "villain_creative_rules.json"
IMAGE_TEXT_RULES_PATH = ROOT / "data" / "villain_image_text_rules.json"
REPORT_PATH = ROOT / "reports" / "villain_creative_output.md"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def choose_mode(caption: str) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if "ABOUT" in caption or "Love $villain" in caption:
        reasons.append("ABOUT文言への引っかかりが核なので、説明より観測者の余白が合う。")
        reasons.append("本文が静かな違和感で進むため、派手な中央ポスターより遠景が自然。")
        return "OBSERVER_MODE", reasons
    if "服" in caption or "wear" in caption.lower():
        reasons.append("服や着る行為が軸なので、日常と街に寄せる。")
        return "STREET_MODE", reasons
    if "入口" in caption or "はじめ" in caption:
        reasons.append("新規向けの入口投稿なので、暗すぎない明るさを残す。")
        return "BRIGHT_MODE", reasons
    reasons.append("象徴コピーを強く見せる余地があるため、ポスター構図が合う。")
    return "POSTER_MODE", reasons


def copy_recommendation(mode: str, text_rules: dict) -> dict:
    if mode == "BRIGHT_MODE":
        return {
            "primary": "コピーなし",
            "secondary": "$villain",
            "reason": "入口向けは情報量を抑え、あとから安全に文字を足せる余白を優先する。",
        }
    return {
        "primary": "着て稼ぐ",
        "secondary": "$villain",
        "reason": text_rules.get("symbolic_phrase", {}).get(
            "meaning",
            "コミュニティの合言葉として扱う。",
        ),
    }


def build_prompt(mode: str, caption: str, composition: dict, copy: dict, with_text: bool) -> str:
    base = (
        "Cyberpunk anime style, cinematic Villain community visual, dark neon city, "
        "hooded figure, rain reflections, teal and pink palette, no AI face close-up, "
        "no cheap neon, no overly NFT-like collectible look, film still quality."
    )
    composition_text = (
        f"Composition: subject {composition.get('subject_ratio')}, background {composition.get('background_ratio')}, "
        f"viewpoint {composition.get('viewpoint')}, color temperature {composition.get('color_temperature')}, "
        f"rain {'yes' if composition.get('rain') else 'no'}."
    )
    if with_text and copy.get("primary") != "コピーなし":
        text = (
            f"Add image text with primary copy {copy.get('primary')!r} and secondary copy {copy.get('secondary')!r}; "
            "maximum two text elements; show it as a community slogan, not a profit promise."
        )
    elif with_text:
        text = f"Use only a small {copy.get('secondary')!r} signature if needed; otherwise leave text minimal."
    else:
        text = "No readable text, no slogan, no logo text; leave clean negative space for later typography."
    return f"{base} {composition_text} Inspired by caption: {caption!r}. {text}"


def main() -> None:
    payload_db = read_json(PAYLOADS_PATH)
    creative_rules = read_json(CREATIVE_RULES_PATH)
    text_rules = read_json(IMAGE_TEXT_RULES_PATH)
    payloads = payload_db.get("payloads", [])
    payload = payloads[0] if payloads else {}
    caption = payload.get("caption", "")
    mode, reasons = choose_mode(caption)
    mode_rules = creative_rules.get("available_modes", {}).get(mode, {})
    composition = mode_rules.get("composition", {})
    copy = copy_recommendation(mode, text_rules)
    generated_at = datetime.now(timezone.utc).isoformat()
    prompt_with_text = build_prompt(mode, caption, composition, copy, True)
    prompt_without_text = build_prompt(mode, caption, composition, copy, False)

    lines = [
        "# Villain Creative Engine v1",
        "",
        f"- Generated at: `{generated_at}`",
        f"- payload_id: `{payload.get('payload_id', '')}`",
        "- status: `BLOCKED`",
        "- create_tweet: `NOT EXECUTED`",
        "- upload_media: `NOT EXECUTED`",
        "- X API write: `NOT USED`",
        "- `.env` read: `NO`",
        "",
        "## Input Caption",
        "",
        "```text",
        caption,
        "```",
        "",
        "## 1. 推奨モード",
        "",
        f"- `{mode}`",
        "",
        "## 2. 推奨理由",
        "",
    ]
    lines.extend(f"- {reason}" for reason in reasons)
    lines.extend(
        [
            "",
            "## 3. 推奨構図",
            "",
            f"- 人物比率: `{composition.get('subject_ratio', '')}`",
            f"- 背景比率: `{composition.get('background_ratio', '')}`",
            f"- 視点: `{composition.get('viewpoint', '')}`",
            f"- 色温度: `{composition.get('color_temperature', '')}`",
            f"- 雨有無: `{'あり' if composition.get('rain') else 'なし'}`",
            "",
            "## 4. 推奨コピー",
            "",
            f"- primary: `{copy.get('primary')}`",
            f"- secondary: `{copy.get('secondary')}`",
            f"- reason: {copy.get('reason')}",
            "",
            "## 5. 画像生成プロンプト",
            "",
            "### 文字入り版",
            "",
            "```text",
            prompt_with_text,
            "```",
            "",
            "### 文字なし版",
            "",
            "```text",
            prompt_without_text,
            "```",
            "",
            "## 6. NG項目",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in creative_rules.get("ng_items", []))
    lines.extend(
        [
            "",
            "## Available Modes",
            "",
        ]
    )
    for available_mode in ["OBSERVER_MODE", "POSTER_MODE", "BRIGHT_MODE", "STREET_MODE"]:
        mode_data = creative_rules.get("available_modes", {}).get(available_mode, {})
        lines.append(f"- `{available_mode}`: {mode_data.get('copy_strategy', '')}")
    lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote creative output report to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
