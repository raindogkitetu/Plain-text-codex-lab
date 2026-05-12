#!/usr/bin/env python3
"""Build image prompt and image API post plan reports without posting.

This script does not read .env, generate images, upload media, call X API write
actions, create tweets, or change posting flags.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "data" / "villain_image_post_rules.json"
TEXT_RULES_PATH = ROOT / "data" / "villain_image_text_rules.json"
PAYLOADS_PATH = ROOT / "data" / "villain_dry_run_payloads.json"
X_CONFIG_PATH = ROOT / "data" / "x_api_config.json"
API_RULES_PATH = ROOT / "data" / "villain_api_post_rules.json"
PROMPT_REPORT_PATH = ROOT / "reports" / "villain_image_prompt.md"
PLAN_REPORT_PATH = ROOT / "reports" / "villain_image_api_post_plan.md"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def bool_text(value: object) -> str:
    return "true" if value is True else "false"


def text_instruction_for_mode(mode: str, text_rules: dict) -> str:
    default_set = text_rules.get("default_copy_set", ["着て稼ぐ", "$villain"])
    max_text = text_rules.get("layout_rules", {}).get("max_text_elements", 2)
    ng = ", ".join(text_rules.get("ng_expressions", []))
    if mode == "POSTER_MODE":
        placement = text_rules.get("layout_rules", {}).get("poster_mode", {})
    else:
        placement = text_rules.get("layout_rules", {}).get("observer_mode", {})
    return (
        f"Include image text as the main visual copy: {default_set[0]!r} plus {default_set[1]!r}. "
        f"Use no more than {max_text} text elements. Place the primary copy at "
        f"{placement.get('primary_copy_position', 'natural scene placement')}; place $villain as "
        f"{placement.get('secondary_copy_position', 'small signature')}. Treat '着て稼ぐ' as a community slogan, "
        "not as financial advice or a profit promise. Avoid these expressions: "
        f"{ng}."
    )


def prompt_for_mode(mode: str, caption: str, text_rules: dict, with_text: bool) -> str:
    base = (
        "Cyberpunk anime style, rainy neon street at night, teal and pink color palette, "
        "dark cinematic atmosphere, hooded solitary figure, no close-up face, no cheap neon, "
        "no overly NFT-like collectible look, high-detail environmental storytelling."
    )
    text_instruction = text_instruction_for_mode(mode, text_rules) if with_text else (
        "No readable text, no logo text, no slogan text; leave clean negative space for later typography."
    )
    if mode == "POSTER_MODE":
        return (
            f"{base} Movie poster composition, centered silhouette, strong brand mood, "
            f"high contrast, clean typography space, dramatic lighting. {text_instruction}"
        )
    return (
        f"{base} Wide angle back view, lonely observer in a neon city, subject 30 percent "
        "and world 70 percent, quiet tension, cinematic rain reflections, inspired by the caption: "
        f"{caption!r}. {text_instruction}"
    )


def recommended_mode(caption: str) -> str:
    if "ABOUT" in caption or "Love $villain" in caption:
        return "OBSERVER_MODE"
    return "POSTER_MODE"


def evaluate_image_plan(payload: dict, rules: dict, x_config: dict, api_rules: dict, prompt_present: bool) -> dict:
    approval = payload.get("approval", {})
    guard = x_config.get("posting_guard", {})
    caption = payload.get("caption", "")
    manual_state = rules.get("manual_state", {})
    api_manual_state = api_rules.get("manual_state", {})
    image_file_path = manual_state.get("image_file_path") or payload.get("image_path")

    checks = [
        {
            "id": "caption_present",
            "ok": isinstance(caption, str) and bool(caption.strip()),
            "actual": isinstance(caption, str) and bool(caption.strip()),
            "required": True,
        },
        {
            "id": "image_prompt_present",
            "ok": prompt_present,
            "actual": prompt_present,
            "required": True,
        },
        {
            "id": "image_file_present",
            "ok": bool(image_file_path),
            "actual": bool(image_file_path),
            "required": True,
        },
        {
            "id": "image_size_confirmed",
            "ok": manual_state.get("image_size_confirmed") is True,
            "actual": manual_state.get("image_size_confirmed", False),
            "required": True,
        },
        {
            "id": "image_rights_confirmed",
            "ok": manual_state.get("image_rights_confirmed") is True,
            "actual": manual_state.get("image_rights_confirmed", False),
            "required": True,
        },
        {
            "id": "media_upload_ready",
            "ok": manual_state.get("media_upload_ready") is True,
            "actual": manual_state.get("media_upload_ready", False),
            "required": True,
        },
        {
            "id": "approved_for_live_post",
            "ok": approval.get("approved_for_live_post") is True,
            "actual": approval.get("approved_for_live_post", False),
            "required": True,
        },
        {
            "id": "write_action_kill_switch",
            "ok": guard.get("write_action_kill_switch") is False,
            "actual": guard.get("write_action_kill_switch", True),
            "required": False,
        },
        {
            "id": "api_final_human_confirmed",
            "ok": api_manual_state.get("api_final_human_confirmed") is True
            and manual_state.get("api_final_human_confirmed") is True,
            "actual": api_manual_state.get("api_final_human_confirmed", False)
            and manual_state.get("api_final_human_confirmed", False),
            "required": True,
        },
        {
            "id": "final_status",
            "ok": False,
            "actual": "BLOCKED",
            "required": rules.get("target_status", "READY_FOR_API_IMAGE_POST"),
        },
    ]

    return {
        "status": rules.get("target_status", "READY_FOR_API_IMAGE_POST")
        if all(check["ok"] for check in checks)
        else "BLOCKED",
        "checks": checks,
        "blockers": [check["id"] for check in checks if not check["ok"]],
        "image_file_path": image_file_path,
    }


def text_risk_assessment(text_rules: dict) -> list[str]:
    return [
        "risk_level: medium",
        "「着て稼ぐ」は強い言葉なので、利益保証ではなくコミュニティの合言葉として見せる。",
        "金融広告に見える数値・利回り・保証表現は入れない。",
        "画像内文字は原則2要素までにして、煽りではなく象徴コピーとして扱う。",
        f"NG expressions: {', '.join(text_rules.get('ng_expressions', []))}",
    ]


def write_prompt_report(
    payload: dict,
    rules: dict,
    text_rules: dict,
    mode: str,
    prompts: dict,
    generated_at: str,
) -> None:
    lines = [
        "# Villain Image Prompt",
        "",
        f"- Generated at: `{generated_at}`",
        f"- payload_id: `{payload.get('payload_id', '')}`",
        f"- recommended_mode: `{mode}`",
        "- image generation executed: `NO`",
        "- media upload executed: `NO`",
        "- primary symbolic copy: `着て稼ぐ`",
        "- default image copy set: `着て稼ぐ + $villain`",
        "",
        "## Source Caption",
        "",
        "```text",
        payload.get("caption", ""),
        "```",
        "",
        "## OBSERVER_MODE Prompt With Text",
        "",
        "```text",
        prompts["OBSERVER_MODE_WITH_TEXT"],
        "```",
        "",
        "## OBSERVER_MODE Prompt Without Text",
        "",
        "```text",
        prompts["OBSERVER_MODE_NO_TEXT"],
        "```",
        "",
        "## POSTER_MODE Prompt With Text",
        "",
        "```text",
        prompts["POSTER_MODE_WITH_TEXT"],
        "```",
        "",
        "## POSTER_MODE Prompt Without Text",
        "",
        "```text",
        prompts["POSTER_MODE_NO_TEXT"],
        "```",
        "",
        "## Image Text Rules",
        "",
        f"- copy priority: `{', '.join(text_rules.get('copy_priority', []))}`",
        f"- max text elements: `{text_rules.get('layout_rules', {}).get('max_text_elements', 2)}`",
        "- basic set: `着て稼ぐ + $villain`",
        "- POSTER_MODE: `着て稼ぐ` を大きく中央または上部に配置。",
        "- OBSERVER_MODE: `着て稼ぐ` を遠景看板や背中の文字として自然に配置。",
        "- `$villain` はロゴ、署名、ネオン看板として併記。",
        "",
        "## Text Risk Assessment",
        "",
    ]
    lines.extend(f"- {item}" for item in text_risk_assessment(text_rules))
    lines.extend(
        [
            "",
        "## Daisho Preferences",
        "",
        f"- prefer: `{', '.join(rules.get('daisho_preferences', {}).get('prefer', []))}`",
        f"- avoid: `{', '.join(rules.get('daisho_preferences', {}).get('avoid', []))}`",
        "",
        "## Recommendation",
        "",
        "- この本文はABOUT文言への引っかかりが核なので、説明ポスターより観測者の余白が合う。",
        "- 推奨は `OBSERVER_MODE`。人物を大きくしすぎず、街と空気を主役にする。",
        "- 文字入り版では `着て稼ぐ + $villain` を主軸にする。",
        "- 文字なし版は後から人間が安全なタイポグラフィを載せるための予備案として扱う。",
        "",
        ]
    )
    PROMPT_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def write_plan_report(payload: dict, mode: str, plan: dict, generated_at: str) -> None:
    lines = [
        "# Villain Image API Post Plan",
        "",
        f"- Generated at: `{generated_at}`",
        f"- payload_id: `{payload.get('payload_id', '')}`",
        f"- image_mode: `{mode}`",
        f"- image API post status: `{plan['status']}`",
        "- X API write actions: `NOT USED`",
        "- upload_media: `NOT EXECUTED`",
        "- create_tweet: `NOT EXECUTED`",
        "- `.env` read: `NO`",
        "",
        "## Image File State",
        "",
        f"- image_file_path: `{plan.get('image_file_path') or 'missing'}`",
        "",
        "## Required Conditions",
        "",
    ]
    for check in plan["checks"]:
        lines.append(
            f"- `{check['id']}`: `{'pass' if check['ok'] else 'fail'}` "
            f"(actual `{check['actual']}`, required `{check['required']}`)"
        )
    lines.extend(["", "## BLOCKED Reasons", ""])
    lines.extend(f"- {blocker}" for blocker in plan["blockers"]) if plan["blockers"] else lines.append("- none")
    lines.extend(
        [
            "",
            "## Safety Note",
            "",
            "- 現段階では画像生成、media upload、create_tweet、実投稿は行わない。",
            "- `write_action_kill_switch=true` と `approved_for_live_post=false` を維持する。",
            "",
        ]
    )
    PLAN_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rules = read_json(RULES_PATH)
    text_rules = read_json(TEXT_RULES_PATH)
    payload_db = read_json(PAYLOADS_PATH)
    x_config = read_json(X_CONFIG_PATH)
    api_rules = read_json(API_RULES_PATH)
    payloads = payload_db.get("payloads", [])
    payload = payloads[0] if payloads else {}
    caption = payload.get("caption", "")
    generated_at = datetime.now(timezone.utc).isoformat()
    mode = recommended_mode(caption)
    prompts = {
        "OBSERVER_MODE_WITH_TEXT": prompt_for_mode("OBSERVER_MODE", caption, text_rules, True),
        "OBSERVER_MODE_NO_TEXT": prompt_for_mode("OBSERVER_MODE", caption, text_rules, False),
        "POSTER_MODE_WITH_TEXT": prompt_for_mode("POSTER_MODE", caption, text_rules, True),
        "POSTER_MODE_NO_TEXT": prompt_for_mode("POSTER_MODE", caption, text_rules, False),
    }
    plan = evaluate_image_plan(
        payload,
        rules,
        x_config,
        api_rules,
        bool(prompts.get(f"{mode}_WITH_TEXT")) and bool(prompts.get(f"{mode}_NO_TEXT")),
    )

    write_prompt_report(payload, rules, text_rules, mode, prompts, generated_at)
    write_plan_report(payload, mode, plan, generated_at)
    print(f"wrote image prompt report to {PROMPT_REPORT_PATH.relative_to(ROOT)}")
    print(f"wrote image API post plan to {PLAN_REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
