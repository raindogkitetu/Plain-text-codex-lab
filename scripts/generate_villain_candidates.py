#!/usr/bin/env python3
"""Generate Villain post candidates in dry-run mode only.

The script creates up to three candidate drafts and predicts quality using the
local scoring rule weights. It does not add candidates to the queue, read .env,
call X API, upload media, or create posts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "villain_generated_candidates.json"
SCORING_RULES_PATH = ROOT / "data" / "villain_post_scoring_rules.json"
REPORT_PATH = ROOT / "reports" / "villain_generated_candidates.md"

PASSCODE = "R2J9T"
FOOTER = f"#着て稼ぐ #villain @0xmavillain {PASSCODE}"
MAX_CANDIDATES = 3


SEEDS: list[dict[str, str]] = [
    {
        "category": "ABOUT_WORDING",
        "text": "ABOUTの言葉、\nまだ残ってる。\n\n毎日着ろって、\nやっぱり普通じゃない。\n\nでも今日はそこがいい。\n\n" + FOOTER,
        "image_hint": "OBSERVER_MODE: 雨のネオン街、遠景の看板に『着て稼ぐ』、フード人物は後ろ姿、人物30%/背景70%。",
        "why_this_might_work": "ABOUT文言の違和感を説明せず、引っかかりだけで置けている。",
    },
    {
        "category": "SILENT_DOMINANCE",
        "text": "強い服って、\n大声じゃない方がいい。\n\n黙ってても、\nちょっと残るやつ。\n\nVillainはそっち。\n\n" + FOOTER,
        "image_hint": "POSTER_MODE: 暗い路地、中央にフードの背中、強い陰影、文字は『着て稼ぐ』と『$villain』まで。",
        "why_this_might_work": "煽らずに強さを出し、Villainの静かな熱量へ寄せている。",
    },
    {
        "category": "SELF_RESPECT",
        "text": "誰かに見せるため、\nだけじゃない服がある。\n\n自分の側に戻る感じ。\n\n今日はそれでいい。\n\n" + FOOTER,
        "image_hint": "STREET_MODE: 店の外、雨上がり、顔を見せない人物、服の質感と街の余白を優先。",
        "why_this_might_work": "説明より体験感を残し、新規にも読めるが綺麗に回収しすぎない。",
    },
    {
        "category": "EMOTIONAL_DAMAGE",
        "text": "刺さる言葉って、\nたまに雑に来る。\n\nLove $villain.\n\nそれだけで、\nちょっと逃げ場ない。\n\n" + FOOTER,
        "image_hint": "OBSERVER_MODE: ネオン看板の反射、孤独な後ろ姿、英字コピーは小さく『Love $villain』。",
        "why_this_might_work": "感情の引っかかりを短く置き、深く説明しない。",
    },
    {
        "category": "RELATIONSHIP_POWER",
        "text": "服から始まって、\n誰かに届くことがある。\n\nそれくらいの距離が、\n今のVillainには合う。\n\n" + FOOTER,
        "image_hint": "BRIGHT_MODE: 店先の光、2人分の影だけ、顔なし、明るすぎないティールとピンク。",
        "why_this_might_work": "関係性を押しつけず、人へ戻る感覚だけを残している。",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def nonempty_lines(text: str) -> int:
    return len([line for line in text.splitlines() if line.strip()])


def has_thin_post_risk(text: str) -> bool:
    body = text.replace(FOOTER, "").strip()
    return len(body) < 35 or nonempty_lines(body) < 3


def predict_quality(text: str, category: str, image_hint: str, rules: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    weights = rules.get("weights", {})
    components: dict[str, Any] = {}

    first_line = text.splitlines()[0].strip() if text else ""
    components["hook_strength"] = {
        "score": weights.get("hook_strength", 15) if first_line else 0,
        "reason": "冒頭に短い引っかかりがある。" if first_line else "冒頭が空。",
    }

    rough_words = ["ちょっと", "普通", "今日は", "それでいい", "そっち", "残る"]
    raindog_ok = any(word in text for word in rough_words)
    components["raindog_voice"] = {
        "score": weights.get("raindog_voice", 20) if raindog_ok else 10,
        "reason": "ぽろっとした距離感がある。" if raindog_ok else "少し整いすぎ。",
    }

    villain_ok = "Villain" in text or "$villain" in text or "#villain" in text
    components["villain_context"] = {
        "score": weights.get("villain_context", 15) if villain_ok else 0,
        "reason": "Villain文脈が本文またはfooterにある。" if villain_ok else "Villain文脈が薄い。",
    }

    compact_ok = len(text) <= 220 and nonempty_lines(text) <= 9
    components["brevity_and_spacing"] = {
        "score": weights.get("brevity_and_spacing", 10) if compact_ok else 5,
        "reason": "短文改行で長すぎない。" if compact_ok else "少し長い。",
    }

    new_reader_ok = category in {"ABOUT_WORDING", "SELF_RESPECT", "RELATIONSHIP_POWER"}
    components["new_reader_clarity"] = {
        "score": weights.get("new_reader_clarity", 10) if new_reader_ok else 7,
        "reason": "初見にも入口がある。" if new_reader_ok else "内輪寄りだが読める。",
    }

    note_ok = category in {"ABOUT_WORDING", "SELF_RESPECT", "EMOTIONAL_DAMAGE"}
    components["save_or_note_potential"] = {
        "score": weights.get("save_or_note_potential", 10) if note_ok else 7,
        "reason": "note化できる種がある。" if note_ok else "短文単体向き。",
    }

    visual_ok = bool(image_hint)
    components["visual_fit"] = {
        "score": weights.get("visual_fit", 10) if visual_ok else 0,
        "reason": "画像の方向性が明確。" if visual_ok else "画像案がない。",
    }

    unsafe_words = ["必ず稼げる", "保証", "爆益", "買え", "急げ"]
    safety_ok = not any(word in text for word in unsafe_words) and not has_thin_post_risk(text)
    components["safety"] = {
        "score": weights.get("safety", 10) if safety_ok else 4,
        "reason": "過度な煽り・利益保証・薄さを避けている。" if safety_ok else "薄い投稿または禁止寄り表現のリスク。",
    }

    total = sum(component["score"] for component in components.values())
    return total, components


def build_candidate(index: int, seed: dict[str, str], rules: dict[str, Any], generated_at: str) -> dict[str, Any]:
    score, components = predict_quality(seed["text"], seed["category"], seed["image_hint"], rules)
    minimum = rules.get("selection_policy", {}).get("recommended_threshold", 80)
    villain_score = min(100, score + (5 if "着て稼ぐ" in seed["text"] else 0))
    return {
        "candidate_id": f"vln-gen-{generated_at[:10].replace('-', '')}-{index:03d}",
        "status": "generated",
        "dry_run_only": true_literal(),
        "queue_add_allowed": score >= minimum,
        "queue_add_blocked_reason": "" if score >= minimum else "quality_prediction_below_80",
        "category": seed["category"],
        "text": seed["text"],
        "image_hint": seed["image_hint"],
        "villain_score": villain_score,
        "quality_prediction": score,
        "quality_threshold": minimum,
        "quality_components": components,
        "risk_prediction": "low" if score >= minimum else "medium",
        "why_this_might_work": seed["why_this_might_work"],
        "generated_at": generated_at,
    }


def true_literal() -> bool:
    return True


def write_report(db: dict[str, Any]) -> None:
    lines = [
        "# Villain Generated Candidates",
        "",
        f"- Generated at: `{db.get('generated_at')}`",
        "- status: `DRY_RUN_ONLY`",
        "- live posting: `NOT EXECUTED`",
        "- X API write: `NOT USED`",
        "- upload_media: `NOT EXECUTED`",
        "- create_tweet: `NOT EXECUTED`",
        "- queue auto add: `DISABLED`",
        f"- max candidates: `{db.get('generation_policy', {}).get('max_candidates_per_run')}`",
        "",
    ]

    for candidate in db.get("candidates", []):
        lines.extend(
            [
                f"## {candidate.get('candidate_id')}",
                "",
                f"- category: `{candidate.get('category')}`",
                f"- villain_score: `{candidate.get('villain_score')}`",
                f"- quality_prediction: `{candidate.get('quality_prediction')}`",
                f"- queue_add_allowed: `{str(candidate.get('queue_add_allowed')).lower()}`",
                f"- risk_prediction: `{candidate.get('risk_prediction')}`",
                f"- why_this_might_work: {candidate.get('why_this_might_work')}",
                f"- image_hint: {candidate.get('image_hint')}",
                "",
                "```text",
                candidate.get("text", ""),
                "```",
                "",
            ]
        )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rules = read_json(SCORING_RULES_PATH)
    now = datetime.now(timezone.utc).isoformat()
    selected = SEEDS[:MAX_CANDIDATES]
    db = {
        "db_name": "Villain Generated Candidates DB",
        "version": "1.0.0",
        "status": "dry_run_only",
        "purpose": "投稿候補を最大3本だけ生成し、quality scoringと連携してqueue投入可否を判定する。実投稿・X API write・media uploadは行わない。",
        "safety": {
            "live_posting_allowed": False,
            "x_api_write_allowed": False,
            "upload_media_allowed": False,
            "create_tweet_allowed": False,
            "env_read_allowed": False,
            "queue_auto_add_allowed": False,
        },
        "generation_policy": {
            "max_candidates_per_run": MAX_CANDIDATES,
            "categories": [
                "ABOUT_WORDING",
                "EMOTIONAL_DAMAGE",
                "SILENT_DOMINANCE",
                "RELATIONSHIP_POWER",
                "SELF_RESPECT",
            ],
            "style_constraints": [
                "説明しすぎ禁止",
                "長文禁止",
                "鬼徹っぽさ維持",
                "一言の強さ優先",
                "薄い投稿禁止",
            ],
            "quality_gate": {
                "connected_to": "data/villain_post_scoring_rules.json",
                "minimum_score_for_queue_add": rules.get("selection_policy", {}).get("recommended_threshold", 80),
                "score_below_threshold_queue_add_allowed": False,
            },
        },
        "run_id": f"vln-gen-run-{now[:10].replace('-', '')}",
        "generated_at": now,
        "candidates": [build_candidate(index, seed, rules, now) for index, seed in enumerate(selected, 1)],
    }
    write_json(OUTPUT_PATH, db)
    write_report(db)
    print("status=DRY_RUN_ONLY")
    print(f"candidates={len(db['candidates'])}")
    print("live_posting=NOT_EXECUTED")
    print("x_api_write=NOT_USED")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
