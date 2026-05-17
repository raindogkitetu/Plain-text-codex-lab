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
]

images = []

if IMAGE_DIR.exists():
    for p in sorted(IMAGE_DIR.glob("*")):
        if not p.is_file():
            continue

        if p.name in BLOCKED:
            continue

        score = 0

        lower = p.name.lower()

        for hint in SAFE_HINTS:
            if hint in lower:
                score += 1

        images.append({
            "name": p.name,
            "path": str(p),
            "score": score,
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
        lines.append(f"- path: `{item['path']}`")
        lines.append("")

OUT.write_text("\n".join(lines), encoding="utf-8")

print(f"wrote: {OUT}")
print(f"safe images: {len(images)}")
print("posting executed: NO")
print("upload executed: NO")
print("tweet creation executed: NO")
