#!/usr/bin/env python3
"""Render the Villain post queue into a human-readable Markdown report.

This script is read/report only. It does not log in to X, authenticate with an
API, upload media, publish posts, create .env files, or change posting flags.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
REPORT_PATH = ROOT / "reports" / "villain_queue_preview.md"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def nullable_text(value: object) -> str:
    return "null" if value in (None, "") else str(value)


def caption_exists(item: dict) -> bool:
    return bool(item.get("text", "").strip())


def approval_state(item: dict) -> str:
    checks = item.get("checks", {})
    approval = item.get("approval", {})
    if item.get("status") == "approved":
        return "approved"
    if checks.get("daisho_approval") == "approved" or approval.get("approved_by"):
        return "approved_marker_present"
    return checks.get("daisho_approval", "unchecked")


def is_blocked(item: dict) -> bool:
    checks = item.get("checks", {})
    image = item.get("image", {})
    post_execution = item.get("post_execution", {})
    return any(
        [
            item.get("status") in {"waiting_for_image", "rejected", "skipped"},
            not image.get("file_path_or_url"),
            checks.get("image_attached") != "pass",
            checks.get("passcode_confirmed") != "pass",
            checks.get("prohibited_content_check") != "pass",
            checks.get("skip_day_policy") is True,
            checks.get("daisho_approval") != "approved",
            post_execution.get("posting_execution_allowed") is False,
        ]
    )


def next_actions_for_item(item: dict) -> list[str]:
    actions: list[str] = []
    checks = item.get("checks", {})
    image = item.get("image", {})

    if not image.get("file_path_or_url"):
        actions.append("Attach image/poster and confirm source rights.")
    if checks.get("passcode_confirmed") != "pass":
        actions.append("Confirm Passcode.")
    if checks.get("daisho_approval") != "approved":
        actions.append("Wait for explicit Daisho approval.")
    if checks.get("prohibited_content_check") != "pass":
        actions.append("Resolve prohibited content check.")
    if not actions:
        actions.append("Keep blocked until final safety allows a future phase.")
    return actions


def main() -> None:
    queue_db = read_json(QUEUE_PATH)
    queue = queue_db.get("queue", [])
    status_counts = Counter(item.get("status", "unknown") for item in queue)
    missing_image_items = [
        item for item in queue if not item.get("image", {}).get("file_path_or_url")
    ]
    blocked_count = sum(1 for item in queue if is_blocked(item))
    generated_at = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Villain Queue Preview",
        "",
        f"- Generated at: `{generated_at}`",
        "- live posting: `DISABLED`",
        "- report mode: `read_only`",
        "",
        "## Summary",
        "",
        f"- total queue items: `{len(queue)}`",
        f"- waiting_for_image count: `{status_counts.get('waiting_for_image', 0)}`",
        f"- approved count: `{status_counts.get('approved', 0)}`",
        f"- blocked count: `{blocked_count}`",
        "",
        "## Status Counts",
        "",
    ]

    if status_counts:
        for status, count in sorted(status_counts.items()):
            lines.append(f"- `{status}`: `{count}`")
    else:
        lines.append("- No queue statuses.")

    lines.extend(["", "## Queue Item List", ""])
    if not queue:
        lines.append("- No queue items.")
    else:
        lines.append(
            "| queue_id | post_type | status | image_path | caption | approval | blocked |"
        )
        lines.append(
            "|---|---|---|---|---|---|---|"
        )
        for item in queue:
            image_path = item.get("image", {}).get("file_path_or_url")
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{item.get('queue_id', '')}`",
                        f"`{item.get('post_type', '')}`",
                        f"`{item.get('status', '')}`",
                        f"`{nullable_text(image_path)}`",
                        f"`{bool_text(caption_exists(item))}`",
                        f"`{approval_state(item)}`",
                        f"`{bool_text(is_blocked(item))}`",
                    ]
                )
                + " |"
            )

    lines.extend(["", "## Missing Image Items", ""])
    if not missing_image_items:
        lines.append("- None.")
    else:
        for item in missing_image_items:
            lines.append(
                f"- `{item.get('queue_id', '')}` needs image/poster: {item.get('image', {}).get('poster_concept', '')}"
            )

    lines.extend(["", "## Next Actions", ""])
    if not queue:
        lines.append("- Generate a queue draft.")
    else:
        for item in queue:
            lines.append(f"### `{item.get('queue_id', '')}`")
            lines.extend(f"- {action}" for action in next_actions_for_item(item))

    lines.extend(
        [
            "",
            "## Safety Note",
            "",
            "This queue preview is read-only. It does not log in to X, connect an API, add credentials, create .env, upload media, or publish posts.",
            "",
        ]
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote queue preview report to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
