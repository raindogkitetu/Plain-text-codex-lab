#!/usr/bin/env python3
"""Score Villain persona alignment for queue and generated candidates.

Report-only analysis. This script does not mutate JSON DBs, read .env, call X
API, upload media, create tweets, or execute posting.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_PATH = ROOT / "data" / "villain_generated_candidates.json"
QUEUE_PATH = ROOT / "data" / "villain_post_queue.json"
REPORT_PATH = ROOT / "reports" / "villain_persona_scorer.md"

NG_PATTERNS = {
    "financial_advice": ["投資", "買え", "今すぐ買う", "必ず上がる"],
    "guaranteed_profit": ["必ず稼げる", "確定利益", "利益保証", " guaranteed profit "],
    "personal_attack": ["お前", "雑魚", "無能"],
    "excessive_defamation": ["詐欺師", "死ね", "消えろ"],
    "false_certainty": ["絶対", "確実に", "100%"],
}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def nonempty_lines(text: str) -> int:
    return len([line for line in text.splitlines() if line.strip()])


def contains_any(text: str, words: list[str]) -> bool:
    lowered = text.lower()
    return any(word.lower() in lowered for word in words)


def ng_hits(text: str) -> list[str]:
    hits: list[str] = []
    for key, words in NG_PATTERNS.items():
        if contains_any(text, words):
            hits.append(key)
    return hits


def score_text(text: str, source: str, item_id: str, post_type: str, image_hint: str) -> dict[str, Any]:
    components: dict[str, dict[str, Any]] = {}
    hits = ng_hits(text)

    poison_ok = contains_any(text, ["強い", "普通じゃない", "刺さる", "ちょっと強い", "残ってる"])
    components["villain_poison"] = {
        "score": 18 if poison_ok else 9,
        "reason": "少し毒のある引っかかりがある。" if poison_ok else "毒は控えめ。",
    }

    irony_ok = contains_any(text, ["普通", "まあ言いそう", "そっち", "でも今日はそこがいい"])
    components["irony"] = {
        "score": 14 if irony_ok else 7,
        "reason": "皮肉やズレの感覚がある。" if irony_ok else "皮肉は弱め。",
    }

    short_power_ok = len(text) <= 220 and nonempty_lines(text) <= 9
    components["short_sentence_power"] = {
        "score": 18 if short_power_ok else 10,
        "reason": "短文の圧が出ている。" if short_power_ok else "少し長くなっている。",
    }

    insider_ok = not contains_any(text, ["知ってる人だけ", "古参なら分かる", "身内"])
    components["not_too_insider"] = {
        "score": 12 if insider_ok else 4,
        "reason": "内輪ノリに閉じすぎていない。" if insider_ok else "内輪感が強い。",
    }

    avoids_investment = "financial_advice" not in hits and "guaranteed_profit" not in hits
    components["avoid_investment_advice"] = {
        "score": 14 if avoids_investment else 0,
        "reason": "金融助言っぽさを避けている。" if avoids_investment else "金融助言または利益保証に寄る。",
    }

    no_excess_hype = not contains_any(text, ["爆益", "やばい", "乗り遅れる", "急げ"])
    components["not_too_hyped"] = {
        "score": 12 if no_excess_hype else 4,
        "reason": "煽りすぎていない。" if no_excess_hype else "煽りが強い。",
    }

    visual_fit_ok = bool(image_hint) or post_type in {"ABOUT_WORDING", "SILENT_DOMINANCE", "SELF_RESPECT"}
    components["image_fit"] = {
        "score": 12 if visual_fit_ok else 6,
        "reason": "画像投稿との相性がある。" if visual_fit_ok else "画像連携は弱め。",
    }

    community_operator_ok = post_type in {"COMMUNITY_INFO", "CULTURE_OBSERVER"} or contains_any(
        text, ["集会", "集ま", "会話", "人が", "誰が着て"]
    )
    components["community_operator"] = {
        "score": 10 if community_operator_ok else 0,
        "reason": "実データで強い現場/コミュニティ運用人格がある。" if community_operator_ok else "現場感は薄い。",
    }

    culture_observer_ok = post_type in {"POSTER_SUMMARY", "CULTURE_OBSERVER"} or contains_any(
        text, ["気づくと", "話題", "残る", "文化", "服だけじゃない"]
    )
    components["culture_observer"] = {
        "score": 10 if culture_observer_ok else 0,
        "reason": "説明より文化の違和感を短く残している。" if culture_observer_ok else "文化観測の強さは控えめ。",
    }

    plain_ai_record = contains_any(text, ["old mining machineの結果", "new mining machineの結果"])
    components["plain_ai_record_penalty"] = {
        "score": -12 if plain_ai_record else 0,
        "reason": "単なる結果報告は直近実データで弱い。" if plain_ai_record else "単純なAI実録連投ではない。",
    }

    total = sum(component["score"] for component in components.values())
    penalties = 0
    if "personal_attack" in hits:
        penalties += 25
    if "excessive_defamation" in hits:
        penalties += 35
    if "false_certainty" in hits:
        penalties += 15
    persona_score = max(0, min(100, total - penalties))

    improvement: list[str] = []
    if persona_score < 80:
        if not poison_ok:
            improvement.append("冒頭にもう半歩だけ引っかかりを置く。")
        if not irony_ok:
            improvement.append("真面目に回収せず、少しズレた一言を残す。")
        if not short_power_ok:
            improvement.append("1行削って短文の圧を戻す。")
        if hits:
            improvement.append("NG要素を外してVillainの余白へ戻す。")
    if not improvement:
        improvement.append("現状で十分。次は画像との温度合わせを見る。")

    return {
        "source": source,
        "item_id": item_id,
        "post_type": post_type,
        "persona_score": persona_score,
        "components": components,
        "ng_hits": hits,
        "improvement_suggestions": improvement,
        "text": text,
    }


def candidate_rows(db: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        score_text(
            candidate.get("text", ""),
            "candidate",
            candidate.get("candidate_id", ""),
            candidate.get("category", "UNKNOWN"),
            candidate.get("image_hint", ""),
        )
        for candidate in db.get("candidates", [])
    ]


def queue_rows(db: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        score_text(
            item.get("text", ""),
            "queue",
            item.get("queue_id", ""),
            item.get("post_type", "UNKNOWN"),
            item.get("image", {}).get("poster_concept", ""),
        )
        for item in db.get("queue", [])
    ]


def write_report(rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Villain Persona Scorer",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "- status: `DRY_RUN_ONLY`",
        "- DB mutation: `NOT_EXECUTED`",
        "- live posting: `NOT_EXECUTED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        f"- scored_items: `{len(rows)}`",
        "",
        "## NG Elements",
        "",
        "- 金融助言",
        "- 確定利益表現",
        "- 個人攻撃",
        "- 過度な誹謗中傷",
        "- 虚偽の断定",
        "",
        "## Scores",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"### `{row.get('item_id')}`",
                "",
                f"- source: `{row.get('source')}`",
                f"- post_type: `{row.get('post_type')}`",
                f"- persona_score: `{row.get('persona_score')}`",
                f"- ng_hits: `{', '.join(row.get('ng_hits', [])) if row.get('ng_hits') else 'none'}`",
                "",
                "#### Components",
                "",
            ]
        )
        for key, component in row.get("components", {}).items():
            lines.append(f"- {key}: `{component.get('score')}` / {component.get('reason')}")
        lines.extend(["", "#### Improvement", ""])
        for item in row.get("improvement_suggestions", []):
            lines.append(f"- {item}")
        lines.extend(["", "```text", row.get("text", ""), "```", ""])
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    candidates_db = read_json(CANDIDATES_PATH)
    queue_db = read_json(QUEUE_PATH)
    rows = candidate_rows(candidates_db) + queue_rows(queue_db)
    write_report(rows)
    print("status=DRY_RUN_ONLY")
    print("db_mutation=NOT_EXECUTED")
    print(f"scored_items={len(rows)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
