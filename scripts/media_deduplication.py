#!/usr/bin/env python3
"""Media reuse guard for Villain posting.

This module is read/local-file only. It computes stable image hashes, builds a
recent successful media history, and returns blockers for near-duplicate media.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

try:
    from PIL import Image
except Exception:  # pragma: no cover - runtime environment guard.
    Image = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
OUTCOMES_PATH = ROOT / "data" / "villain_post_outcomes.json"
HISTORY_PATH = ROOT / "data" / "recent_media_history.json"
JST = ZoneInfo("Asia/Tokyo")
MEDIA_REUSE_COOLDOWN_DAYS = 7
NEAR_DUPLICATE_HAMMING_THRESHOLD = 8


def now_jst() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_jst(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=JST)
    return parsed.astimezone(JST)


def normalize_path(path_text: str) -> str:
    if not path_text:
        return ""
    path_text = path_text.replace("/Users/raindog/Documents/New project", str(ROOT))
    path_text = path_text.replace("/Users/raindog/Projects/villain-auto-posting", str(ROOT))
    path = Path(path_text)
    if not path.is_absolute():
        path = ROOT / path
    return str(path)


def sha256_file(path_text: str) -> str:
    path = Path(normalize_path(path_text))
    if not path.exists() or not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def perceptual_hash(path_text: str) -> str:
    """Return a 64-bit difference hash as 16 hex chars."""
    if Image is None:
        return ""
    path = Path(normalize_path(path_text))
    if not path.exists() or not path.is_file():
        return ""
    try:
        with Image.open(path) as image:
            image = image.convert("L").resize((9, 8))
            pixels = list(image.getdata())
    except Exception:
        return ""
    bits: list[str] = []
    for row in range(8):
        offset = row * 9
        for col in range(8):
            bits.append("1" if pixels[offset + col] > pixels[offset + col + 1] else "0")
    return f"{int(''.join(bits), 2):016x}"


def hamming_distance(left: str, right: str) -> int | None:
    if not left or not right:
        return None
    try:
        return bin(int(left, 16) ^ int(right, 16)).count("1")
    except ValueError:
        return None


def prompt_family_for(image: dict[str, Any] | None, path_text: str = "") -> str:
    image = image or {}
    values = [
        image.get("prompt_family", ""),
        image.get("composition", ""),
        image.get("layout", ""),
        image.get("image_type", ""),
        image.get("reason", ""),
        Path(normalize_path(path_text or image.get("absolute_path") or image.get("file_path", ""))).stem,
    ]
    joined = " ".join(str(value).lower() for value in values if value)
    joined = re.sub(r"\d{6,}|\b\d+\b", "", joined)
    joined = re.sub(r"[^a-z0-9ぁ-んァ-ン一-龥]+", "_", joined).strip("_")
    return joined[:80]


def media_signature(image: dict[str, Any] | None) -> dict[str, Any]:
    image = image or {}
    path = normalize_path(image.get("absolute_path") or image.get("file_path", ""))
    return {
        "path": path,
        "sha256": sha256_file(path),
        "perceptual_hash": perceptual_hash(path),
        "prompt_family": prompt_family_for(image, path),
        "composition": image.get("composition", ""),
        "layout": image.get("layout", ""),
        "image_type": image.get("image_type", ""),
    }


def outcome_entry(record: dict[str, Any]) -> dict[str, Any]:
    image_path = normalize_path(record.get("image_used", ""))
    return {
        "tweet_id": record.get("tweet_id", ""),
        "url": record.get("url", ""),
        "posted_at_jst": record.get("posted_at_jst", ""),
        "candidate_id": record.get("candidate_id", ""),
        "execution_id": record.get("execution_id", ""),
        "passcode": record.get("passcode", ""),
        "image_used": image_path,
        "sha256": record.get("image_hash") or sha256_file(image_path),
        "perceptual_hash": record.get("perceptual_hash") or perceptual_hash(image_path),
        "prompt_family": record.get("prompt_family") or prompt_family_for({}, image_path),
        "composition": record.get("composition", ""),
        "layout": record.get("layout", ""),
    }


def build_recent_media_history(
    outcomes: dict[str, Any] | None = None,
    *,
    cooldown_days: int = MEDIA_REUSE_COOLDOWN_DAYS,
    write: bool = True,
) -> dict[str, Any]:
    outcomes = outcomes if outcomes is not None else read_json(OUTCOMES_PATH, {})
    cutoff = datetime.now(JST) - timedelta(days=cooldown_days)
    entries: list[dict[str, Any]] = []
    for record in outcomes.get("outcomes", []):
        if not record.get("tweet_id") or not record.get("url") or not record.get("image_used"):
            continue
        if record.get("status") != "SUCCESS":
            continue
        posted = parse_jst(record.get("posted_at_jst", ""))
        if posted and posted < cutoff:
            continue
        entries.append(outcome_entry(record))
    history = {
        "db_name": "Villain Recent Media History",
        "version": "1.0.0",
        "generated_at_jst": now_jst(),
        "cooldown_days": cooldown_days,
        "near_duplicate_hamming_threshold": NEAR_DUPLICATE_HAMMING_THRESHOLD,
        "policy": {
            "allow_reuse_after_cooldown": True,
            "block_same_file": True,
            "block_same_sha256": True,
            "block_near_duplicate_perceptual_hash": True,
            "block_same_prompt_family_within_cooldown": True,
        },
        "entries": entries,
    }
    if write:
        write_json(HISTORY_PATH, history)
    return history


def media_reuse_check(image: dict[str, Any] | None, history: dict[str, Any] | None = None) -> dict[str, Any]:
    signature = media_signature(image)
    history = history if history is not None else build_recent_media_history(write=True)
    blockers: list[str] = []
    matches: list[dict[str, Any]] = []
    for entry in history.get("entries", []):
        reasons: list[str] = []
        if signature["path"] and signature["path"] == normalize_path(entry.get("image_used", "")):
            reasons.append("same_media_path")
        if signature["sha256"] and signature["sha256"] == entry.get("sha256"):
            reasons.append("same_media_sha256")
        distance = hamming_distance(signature.get("perceptual_hash", ""), entry.get("perceptual_hash", ""))
        if distance is not None and distance <= int(history.get("near_duplicate_hamming_threshold", NEAR_DUPLICATE_HAMMING_THRESHOLD)):
            reasons.append("near_duplicate_media_phash")
        if signature.get("prompt_family") and signature.get("prompt_family") == entry.get("prompt_family"):
            reasons.append("same_prompt_family_cooldown")
        if reasons:
            blockers.extend(reasons)
            matches.append(
                {
                    "tweet_id": entry.get("tweet_id", ""),
                    "url": entry.get("url", ""),
                    "posted_at_jst": entry.get("posted_at_jst", ""),
                    "image_used": entry.get("image_used", ""),
                    "hamming_distance": distance,
                    "reasons": sorted(set(reasons)),
                }
            )
    return {
        "signature": signature,
        "blockers": sorted(set(blockers)),
        "matches": matches[:5],
        "cooldown_days": history.get("cooldown_days", MEDIA_REUSE_COOLDOWN_DAYS),
    }


def main() -> None:
    history = build_recent_media_history(write=True)
    print("status=SUCCESS")
    print(f"entries={len(history.get('entries', []))}")
    print(f"wrote {HISTORY_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
