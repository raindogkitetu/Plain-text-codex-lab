#!/usr/bin/env python3
"""Select image candidates for Villain queue items in dry-run mode.

The script reads queue items, generated candidates, and local image files, then
writes a selection report. It does not mutate the queue, upload media, create
tweets, call X API, read .env, or execute posting.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
GENERATED_PATH = ROOT / "data" / "villain_generated_candidates.json"
IMAGE_DIR = ROOT / "villain_post_images"
REPORT_PATH = ROOT / "reports" / "villain_image_selection.md"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def image_files() -> list[Path]:
    if not IMAGE_DIR.exists():
        return []
    return sorted(
        path for path in IMAGE_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def normalize(text: str) -> str:
    return "".join(ch.lower() for ch in text if ch.isalnum())


def infer_image_mode(path: Path) -> str:
    name = path.name.lower()
    if "observer" in name:
        return "OBSERVER_MODE"
    if "poster" in name:
        return "POSTER_MODE"
    if "street" in name:
        return "STREET_MODE"
    if "bright" in name:
        return "BRIGHT_MODE"
    return "UNKNOWN_MODE"


def candidate_for_queue(item: dict[str, Any], generated_db: dict[str, Any]) -> dict[str, Any]:
    source_id = item.get("source_generated_candidate_id")
    candidates = generated_db.get("candidates", [])
    if source_id:
        for candidate in candidates:
            if candidate.get("candidate_id") == source_id:
                return candidate

    post_type = item.get("post_type", "")
    for candidate in candidates:
        if candidate.get("category") == post_type:
            return candidate

    item_text = normalize(item.get("text", ""))
    best: dict[str, Any] = {}
    best_score = 0
    for candidate in candidates:
        cand_text = normalize(candidate.get("text", ""))
        shared = len(set(item_text) & set(cand_text))
        if shared > best_score:
            best = candidate
            best_score = shared
    return best


def image_score(image_path: Path, item: dict[str, Any], candidate: dict[str, Any]) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    mode = infer_image_mode(image_path)
    hint = candidate.get("image_hint", "") + " " + item.get("image", {}).get("poster_concept", "")
    category = candidate.get("category") or item.get("post_type", "")
    name = image_path.name.lower()

    if mode != "UNKNOWN_MODE" and mode in hint:
        score += 40
        reasons.append(f"mode_match:{mode}")
    if category == "ABOUT_WORDING" and "observer" in name:
        score += 25
        reasons.append("about_wording_observer_fit")
    if category == "SILENT_DOMINANCE" and "poster" in name:
        score += 25
        reasons.append("silent_dominance_poster_fit")
    if category == "SELF_RESPECT" and ("street" in name or "observer" in name):
        score += 20
        reasons.append("self_respect_street_or_observer_fit")
    if "villain" in name:
        score += 15
        reasons.append("villain_filename_signal")
    if not reasons:
        reasons.append("generic_local_image_candidate")
    return score, reasons


def build_selection(item: dict[str, Any], generated_db: dict[str, Any], images: list[Path]) -> dict[str, Any]:
    candidate = candidate_for_queue(item, generated_db)
    scored_images = []
    for path in images:
        score, reasons = image_score(path, item, candidate)
        scored_images.append(
            {
                "path": str(path),
                "image_mode": infer_image_mode(path),
                "score": score,
                "reasons": reasons,
            }
        )
    scored_images.sort(key=lambda image: image["score"], reverse=True)
    selected = scored_images[0] if scored_images else None
    return {
        "queue_id": item.get("queue_id", ""),
        "candidate_id": candidate.get("candidate_id", item.get("source_generated_candidate_id", "")),
        "category": candidate.get("category", item.get("post_type", "")),
        "queue_status": item.get("status", ""),
        "image_hint": candidate.get("image_hint", item.get("image", {}).get("poster_concept", "")),
        "image_candidates": scored_images[:3],
        "selected_image": selected.get("path") if selected else "",
        "selected_image_path": selected.get("path") if selected else "",
        "image_selected": bool(selected),
        "next_status_if_applied": "ready_for_human_post_review" if selected else "waiting_for_image",
        "selection_reason": ", ".join(selected.get("reasons", [])) if selected else "no_local_image_candidates_found",
    }


def write_report(selections: list[dict[str, Any]], total_images: int) -> None:
    now = datetime.now(timezone.utc).isoformat()
    lines = [
        "# Villain Image Selection",
        "",
        f"- Generated at: `{now}`",
        "- status: `DRY_RUN_ONLY`",
        "- queue mutation: `NOT_EXECUTED`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        f"- local_image_candidates_found: `{total_images}`",
        "",
    ]
    if not selections:
        lines.append("- no waiting_for_image queue items")
    for selection in selections:
        lines.extend(
            [
                f"## `{selection.get('queue_id')}`",
                "",
                f"- candidate_id: `{selection.get('candidate_id')}`",
                f"- category: `{selection.get('category')}`",
                f"- queue_status: `{selection.get('queue_status')}`",
                f"- image_selected: `{str(selection.get('image_selected')).lower()}`",
                f"- selected_image: `{selection.get('selected_image')}`",
                f"- next_status_if_applied: `{selection.get('next_status_if_applied')}`",
                f"- selection_reason: {selection.get('selection_reason')}",
                f"- image_hint: {selection.get('image_hint')}",
                "",
                "### Image Candidates",
                "",
            ]
        )
        candidates = selection.get("image_candidates", [])
        if not candidates:
            lines.append("- none")
        for image in candidates:
            lines.append(
                f"- `{image.get('path')}` score=`{image.get('score')}` mode=`{image.get('image_mode')}` "
                f"reasons=`{', '.join(image.get('reasons', []))}`"
            )
        lines.append("")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    queue_db = read_json(QUEUE_PATH)
    generated_db = read_json(GENERATED_PATH)
    images = image_files()
    waiting_items = [
        item for item in queue_db.get("queue", [])
        if item.get("status") == "waiting_for_image"
    ]
    selections = [build_selection(item, generated_db, images) for item in waiting_items]
    write_report(selections, len(images))
    print("status=DRY_RUN_ONLY")
    print("queue_mutation=NOT_EXECUTED")
    print(f"waiting_for_image={len(waiting_items)}")
    print(f"image_candidates_found={len(images)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
