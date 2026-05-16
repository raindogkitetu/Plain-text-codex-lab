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

from required_token_layer import MANDATORY_FOOTER, normalize_mandatory_tokens, verification_summary


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "villain_generated_candidates.json"
SCORING_RULES_PATH = ROOT / "data" / "villain_post_scoring_rules.json"
REPORT_PATH = ROOT / "reports" / "villain_generated_candidates.md"

PASSCODE = "R2J9T"
FOOTER = f"{MANDATORY_FOOTER} {PASSCODE}"
MAX_CANDIDATES = 3


SEEDS: list[dict[str, str]] = [
    {
        "category": "COMMUNITY_INFO",
        "text": "昨日の集会、\nまだ少し残ってる。\n\n説明より、\n人が集まってる事実の方が強い。\n\n$villainは、\nそこがちょっと変。\n\n" + FOOTER,
        "image_hint": "COMMUNITY_MODE: 夜の街角やカフェ外、$villainを着た少人数の集まり。会話の気配、スマホを見る手元、背中、横顔。文字は少なめ。",
        "why_this_might_work": "実データで最強だったcommunity_info型。集会/現場感を短く置き、説明ではなく文化の動きを見せる。",
    },
    {
        "category": "POSTER_SUMMARY",
        "text": "気づくと、\nまた$villainの話になってる。\n\n服の話だけなら、\nたぶんここまで残らない。\n\n" + FOOTER,
        "image_hint": "POSTER_SUMMARY: $villainを着た人たちの日常コラージュ。駅、夜道、カフェ、コンビニ前。文化が街に残っている感じ。",
        "why_this_might_work": "poster_summaryは平均130.5 impressions。文化の違和感を一行目に置き、画像で止める。",
    },
    {
        "category": "CULTURE_OBSERVER",
        "text": "話題になる服って、\nだいたい服だけじゃない。\n\n誰が着て、\nどこで集まってるかまで含めて、\n少し残る。\n\n" + FOOTER,
        "image_hint": "CULTURE_OBSERVER: 2〜4人の$villain着用者。広告感なし。会話、視線、街灯、現場の余白。文字は短く。",
        "why_this_might_work": "勝ち人格のculture_observerを優先。説明する人ではなく、現場を見て短く残す人に寄せる。",
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

    new_reader_ok = category in {
        "ABOUT_WORDING",
        "SELF_RESPECT",
        "RELATIONSHIP_POWER",
        "COMMUNITY_INFO",
        "POSTER_SUMMARY",
        "CULTURE_OBSERVER",
    }
    components["new_reader_clarity"] = {
        "score": weights.get("new_reader_clarity", 10) if new_reader_ok else 7,
        "reason": "初見にも入口がある。" if new_reader_ok else "内輪寄りだが読める。",
    }

    note_ok = category in {
        "ABOUT_WORDING",
        "SELF_RESPECT",
        "EMOTIONAL_DAMAGE",
        "COMMUNITY_INFO",
        "POSTER_SUMMARY",
        "CULTURE_OBSERVER",
    }
    components["save_or_note_potential"] = {
        "score": weights.get("save_or_note_potential", 10) if note_ok else 7,
        "reason": "note化できる種がある。" if note_ok else "短文単体向き。",
    }

    visual_ok = bool(image_hint)
    components["visual_fit"] = {
        "score": weights.get("visual_fit", 10) if visual_ok else 0,
        "reason": "画像の方向性が明確。" if visual_ok else "画像案がない。",
    }

    community_ok = category in {"COMMUNITY_INFO", "CULTURE_OBSERVER"} or any(
        word in text for word in ["集会", "集ま", "会話", "人が", "誰が着て"]
    )
    components["community_context"] = {
        "score": weights.get("community_context", 0) if community_ok else 0,
        "reason": "実データで強いコミュニティ/現場感がある。" if community_ok else "コミュニティ文脈は薄い。",
    }

    culture_ok = category in {"POSTER_SUMMARY", "CULTURE_OBSERVER"} or any(
        word in text for word in ["気づくと", "話題", "残る", "文化"]
    )
    components["culture_observation"] = {
        "score": weights.get("culture_observation", 0) if culture_ok else 0,
        "reason": "文化の違和感を短く観測している。" if culture_ok else "文化観測の引っかかりは弱い。",
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
    normalized_text = normalize_mandatory_tokens(seed["text"])
    token_check = verification_summary(seed["text"])
    score, components = predict_quality(normalized_text, seed["category"], seed["image_hint"], rules)
    minimum = rules.get("selection_policy", {}).get("recommended_threshold", 80)
    villain_score = min(100, score + (5 if "着て稼ぐ" in normalized_text else 0))
    return {
        "candidate_id": f"vln-gen-{generated_at[:10].replace('-', '')}-{index:03d}",
        "status": "generated",
        "dry_run_only": true_literal(),
        "queue_add_allowed": score >= minimum,
        "queue_add_blocked_reason": "" if score >= minimum else "quality_prediction_below_80",
        "category": seed["category"],
        "text": normalized_text,
        "token_verification": {
            "required_layer": "Required Token Layer v1",
            "mandatory_footer_order": MANDATORY_FOOTER,
            "missing_before": token_check["missing_before"],
            "duplicates_before": token_check["duplicates_before"],
            "normalized": token_check["changed"],
            "valid_after": token_check["valid_after"],
        },
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
                f"- required_tokens_valid_after: `{str(candidate.get('token_verification', {}).get('valid_after')).lower()}`",
                f"- mandatory_footer_order: `{candidate.get('token_verification', {}).get('mandatory_footer_order')}`",
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
                "COMMUNITY_INFO",
                "POSTER_SUMMARY",
                "CULTURE_OBSERVER",
                "ABOUT_WORDING",
                "SILENT_DOMINANCE",
            ],
            "style_constraints": [
                "説明しすぎ禁止",
                "長文禁止",
                "鬼徹っぽさ維持",
                "一言の強さ優先",
                "薄い投稿禁止",
                "old/new mining machine の単なる結果報告を避ける",
                "服単体紹介だけで終わらせない",
                "画像付き前提で文化/現場感を置く",
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
