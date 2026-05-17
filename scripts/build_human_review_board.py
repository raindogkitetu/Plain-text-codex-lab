from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent

READY_REPORT = ROOT / "reports/villain_ready_candidates.md"
IMAGE_REPORT = ROOT / "reports/villain_image_recommendations.md"
OUT = ROOT / "reports/villain_human_review_board_runtime.md"

def read_text(path):
    if not path.exists():
        return f"[missing] {path.name}"
    return path.read_text(encoding="utf-8")

ready_text = read_text(READY_REPORT)
image_text = read_text(IMAGE_REPORT)

lines = []

lines.append("# Villain Human Review Board")
lines.append("")

lines.append("## READY Candidates")
lines.append("")
lines.append("```text")
lines.append(ready_text[:8000])
lines.append("```")
lines.append("")

lines.append("## Image Recommendations")
lines.append("")
lines.append("```text")
lines.append(image_text[:8000])
lines.append("```")
lines.append("")

lines.append("## Human Decision")
lines.append("")
lines.append("- keep: true | false | pending")
lines.append("- approve_to_post: true | false")
lines.append("- reviewer_notes")
lines.append("")

lines.append("## Safety")
lines.append("")
lines.append("- posting executed: NO")
lines.append("- upload executed: NO")
lines.append("- tweet creation executed: NO")

OUT.write_text("\n".join(lines), encoding="utf-8")

print(f"wrote: {OUT}")
print("posting executed: NO")
print("upload executed: NO")
print("tweet creation executed: NO")
