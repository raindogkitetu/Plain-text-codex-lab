#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path.cwd()

IMAGE_DIR = ROOT / "villain_post_images"
OUT = ROOT / "reports" / "villain_image_recommendations.md"

BLOCKED = {
    "20260514集会.png",
}

SAFE_HINTS = [
    "street",
    "apparel",
    "night",
    "city",
    "walk",
    "shadow",
    "observer",
]

TEXT_HINT_MAP = {
    "服": ["apparel", "shirt", "hoodie", "wear", "observer"],
    "着": ["apparel", "shirt", "hoodie", "wear", "observer"],
    "街": ["street", "city", "night", "walk"],
    "夜": ["night", "shadow", "city"],
    "残": ["shadow", "night", "observer"],
    "話": ["observer", "street", "apparel"],
}

RISKY_IMAGE_TERMS = [
    "集会",
    "event",
    "meeting",
    "crowd",
]

def text_image_fit_score(candidate_text: str, image_name: str) -> tuple[int, list[str], list[str]]:
    lower = image_name.lower()
    score = 0
    warnings = []
    blockers = []

    for risky in RISKY_IMAGE_TERMS:
        if risky in image_name or risky in lower:
            blockers.append("risky_event_image")

    matched = False
    for text_hint, image_hints in TEXT_HINT_MAP.items():
        if text_hint in candidate_text:
            for image_hint in image_hints:
                if image_hint in lower:
                    score += 2
                    matched = True

    for hint in SAFE_HINTS:
        if hint in lower:
            score += 1

    if not matched:
        warnings.append("thin_text_image_match")

    return score, warnings, blockers


def load_ready_candidate_text() -> str:
    ready_path = ROOT / "reports" / "villain_ready_candidates.md"
    if not ready_path.exists():
        return ""
    return ready_path.read_text(encoding="utf-8")


READY_TEXT = load_ready_candidate_text()

images = []

if IMAGE_DIR.exists():
    for p in sorted(IMAGE_DIR.glob("*")):
        if not p.is_file():
            continue

        if p.name in BLOCKED:
            continue

        score, warnings, blockers = text_image_fit_score(READY_TEXT, p.name)

        status = "READY"
        if blockers:
            status = "BLOCKED"
        elif score < 2 or warnings:
            status = "REVIEW_REQUIRED"

        images.append({
            "name": p.name,
            "path": str(p),
            "score": score,
            "status": status,
            "warnings": warnings,
            "blockers": blockers,
        })

images.sort(key=lambda x: x["score"], reverse=True)

lines = []
lines.append("# Villain Image Recommendations")
lines.append("")

if not images:
    lines.append("No safe images found.")
else:
    for idx, item in enumerate(images[:20], 1):
        lines.append(f"## {idx}. {item['name']}")
        lines.append(f"- score: {item['score']}")
        lines.append(f"- status: `{item.get('status', '')}`")
        lines.append(f"- warnings: `{item.get('warnings', [])}`")
        lines.append(f"- blockers: `{item.get('blockers', [])}`")
        lines.append(f"- path: `{item['path']}`")
        lines.append("")

OUT.write_text("\n".join(lines), encoding="utf-8")

print(f"wrote: {OUT}")
print(f"safe images: {len(images)}")
print("posting executed: NO")
print("upload executed: NO")
print("tweet creation executed: NO")
