#!/usr/bin/env python3
"""Build a human-only manual post pack from selected Villain candidates."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SELECTION_PATH = ROOT / "reports" / "villain_manual_test_selection.md"
REPORT_PATH = ROOT / "reports" / "villain_manual_post_pack.md"

HUMAN_CHECKLIST = [
    "本文に誤字がない",
    "金融助言に見えない",
    "誰か個人を攻撃していない",
    "Villainらしさがある",
    "画像が必要な場合は画像を確認済み",
]

DO_NOT_POST_IF = [
    "利益保証に見える",
    "特定個人/団体への攻撃に見える",
    "文脈なしで炎上しそう",
    "画像権利が不明",
]


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def parse_selection(report: str) -> list[dict[str, Any]]:
    posts: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_text = False
    text_lines: list[str] = []

    for line in report.splitlines():
        heading = re.match(r"^### `([^`]+)`", line)
        if heading:
            if current:
                current["final_text"] = "\n".join(text_lines).strip()
                posts.append(current)
            current = {"candidate_id": heading.group(1)}
            in_text = False
            text_lines = []
            continue
        if current is None:
            continue
        if line.strip() == "```text":
            in_text = True
            text_lines = []
            continue
        if line.strip() == "```" and in_text:
            in_text = False
            current["final_text"] = "\n".join(text_lines).strip()
            continue
        if in_text:
            text_lines.append(line)
            continue
        field = re.match(r"^- ([a-zA-Z0-9_]+): `([^`]*)`", line)
        if field:
            current[field.group(1)] = field.group(2)

    if current:
        current["final_text"] = current.get("final_text", "\n".join(text_lines).strip())
        posts.append(current)

    return [post for post in posts if post.get("candidate_id", "").startswith("vln-gen-")]


def image_status_for(post: dict[str, Any]) -> str:
    post_type = post.get("post_type", "")
    if post_type in {"ABOUT_WORDING", "SILENT_DOMINANCE", "SELF_RESPECT"}:
        return "image_required_human_check"
    return "image_optional_human_check"


def write_report(posts: list[dict[str, Any]]) -> None:
    lines = [
        "# Villain Manual Post Pack",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "- status: `DRY_RUN_ONLY`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        "- DB mutation: `NOT_EXECUTED`",
        f"- post_pack_count: `{len(posts)}`",
        "",
    ]
    if not posts:
        lines.append("- no manual test candidates found")
    for index, post in enumerate(posts, 1):
        lines.extend(
            [
                f"## Post {index}",
                "",
                f"- post_number: `{index}`",
                f"- candidate_id: `{post.get('candidate_id', '')}`",
                f"- post_type: `{post.get('post_type', '')}`",
                f"- image_status: `{image_status_for(post)}`",
                f"- recommended_time_window: `{post.get('recommended_time_window', '')}`",
                f"- quality_score: `{post.get('quality_score', '')}`",
                f"- persona_score: `{post.get('persona_score', '')}`",
                f"- risk: `{post.get('risk', '')}`",
                "",
                "### final_text",
                "",
                "```text",
                post.get("final_text", ""),
                "```",
                "",
                "### human_checklist",
                "",
            ]
        )
        for item in HUMAN_CHECKLIST:
            lines.append(f"- [ ] {item}")
        lines.extend(["", "### do_not_post_if", ""])
        for item in DO_NOT_POST_IF:
            lines.append(f"- {item}")
        lines.append("")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    posts = parse_selection(read_text(SELECTION_PATH))
    write_report(posts)
    print("status=DRY_RUN_ONLY")
    print("live_posting=NOT_EXECUTED")
    print("x_api_write=NOT_USED")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"post_pack_count={len(posts)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
