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


def prompt_for_mode(mode: str, caption: str) -> str:
    base = (
        "Cyberpunk anime style, rainy neon street at night, teal and pink color palette, "
        "dark cinematic atmosphere, hooded solitary figure, no close-up face, no cheap neon, "
        "no overly NFT-like collectible look, high-detail environmental storytelling."
    )
    if mode == "POSTER_MODE":
        return (
            f"{base} Movie poster composition, centered silhouette, strong brand mood, "
            "high contrast, optional short English text inspired by 'wear it daily', "
            "clean typography, dramatic lighting."
        )
    return (
        f"{base} Wide angle back view, lonely observer in a neon city, subject 30 percent "
        "and world 70 percent, quiet tension, cinematic rain reflections, inspired by the caption: "
        f"{caption!r}."
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


def write_prompt_report(payload: dict, rules: dict, mode: str, prompts: dict, generated_at: str) -> None:
    lines = [
        "# Villain Image Prompt",
        "",
        f"- Generated at: `{generated_at}`",
        f"- payload_id: `{payload.get('payload_id', '')}`",
        f"- recommended_mode: `{mode}`",
        "- image generation executed: `NO`",
        "- media upload executed: `NO`",
        "",
        "## Source Caption",
        "",
        "```text",
        payload.get("caption", ""),
        "```",
        "",
        "## OBSERVER_MODE Prompt",
        "",
        "```text",
        prompts["OBSERVER_MODE"],
        "```",
        "",
        "## POSTER_MODE Prompt",
        "",
        "```text",
        prompts["POSTER_MODE"],
        "```",
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
        "",
    ]
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
    payload_db = read_json(PAYLOADS_PATH)
    x_config = read_json(X_CONFIG_PATH)
    api_rules = read_json(API_RULES_PATH)
    payloads = payload_db.get("payloads", [])
    payload = payloads[0] if payloads else {}
    caption = payload.get("caption", "")
    generated_at = datetime.now(timezone.utc).isoformat()
    mode = recommended_mode(caption)
    prompts = {
        "OBSERVER_MODE": prompt_for_mode("OBSERVER_MODE", caption),
        "POSTER_MODE": prompt_for_mode("POSTER_MODE", caption),
    }
    plan = evaluate_image_plan(payload, rules, x_config, api_rules, bool(prompts.get(mode)))

    write_prompt_report(payload, rules, mode, prompts, generated_at)
    write_plan_report(payload, mode, plan, generated_at)
    print(f"wrote image prompt report to {PROMPT_REPORT_PATH.relative_to(ROOT)}")
    print(f"wrote image API post plan to {PLAN_REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
