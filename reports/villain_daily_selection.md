# Villain Daily Selection OS v1

- Generated at JST: `2026-05-16`
- status: `DESIGN_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- commit: `NOT_EXECUTED`
- design DB: `data/villain_daily_selection.json`

## 1. Concept

Daily Selection OS は、Candidate Stream から「今日の朝・昼・夜・深夜に出すならどれか」を選ぶための選定レイヤー。

役割は投稿生成ではなく、候補在庫の中から slot に合う候補を選ぶこと。

| layer | role |
|---|---|
| Candidate Stream | 候補を5-15本保持する |
| Residual Learning | 24hで残る型を評価する |
| Image Strategy | 画像適性とimage_readyを判断する |
| Scoring / Persona | 品質・安全性・人格一致を評価する |
| Daily Selection | 今日のslotに割り当てる |

重要: Daily Selection は投稿実行をしない。`selected` は「人間が確認する今日候補」であり、投稿許可ではない。

## 2. Selection Conditions

Daily Selection は以下の条件で候補を採点する。

| condition | purpose |
|---|---|
| `current_trend_fit` | 今日の空気に合うか。便乗ではなく温度合わせ |
| `residual_type` | 24hで残る型か、profile_pull型か |
| `image_ready` | 画像付きで出せるか。現在の勝ち筋に直結 |
| `category_balance` | 1日内でカテゴリが偏りすぎないか |
| `freshness_decay` | 候補が古くなりすぎていないか |
| `time_window_fit` | 朝/昼/夜/深夜のslotに合うか |
| `persona_rotation` | 鬼徹人格が単調になっていないか |

補助条件:

- `quality_prediction`
- `persona_score`
- `risk_prediction`
- `image.match_score`
- `residual_growth_potential`
- `profile_click_potential`

## 3. Selection Score

設計上の重み:

| factor | weight |
|---|---:|
| `current_trend_fit` | 12 |
| `residual_type` | 14 |
| `image_ready` | 16 |
| `category_balance` | 10 |
| `freshness_decay` | 12 |
| `time_window_fit` | 14 |
| `persona_rotation` | 10 |
| `quality_prediction` | 8 |
| `risk_safety` | 14 |

思想:

- 画像readyは強め。
- late_nightは `residual_growth` と `profile_pull` を優先。
- リスクがある候補は高スコアでも落とす。
- current trend は「寄せる」が「乗りすぎない」。

## 4. Slot Definitions

1日3-5投稿を前提に、4つの基本slotを持つ。

| slot | time window JST | target | best categories |
|---|---|---:|---|
| `morning` | `07:00-09:00` | 1 | `poster_summary`, `explainer`, `apparel_focus` |
| `daytime` | `12:00-15:00` | 1 | `explainer`, `poster_summary`, `community_info` |
| `night` | `18:00-22:30` | 1 | `poster_summary`, `culture_observer`, `community_info` |
| `late_night` | `23:00-23:59` | 1 | `community_info`, `culture_observer`, `poster_summary` |

5本目を出す場合:

- reply/contextual軽量投稿
- aging候補の救済
- community_infoの追記
- 画像なしでも本文が強い短文

ただし5本目は主力ではなく、密度調整枠。

## 5. Slot Fit By Category

### culture_observer

向くslot:

- `night`
- `late_night`

理由:

- 今日の空気に寄るため、夜の文脈確認後が強い。
- 24h residual/profile_pullを狙うなら23時台と相性がよい。
- 朝に出すと重さや違和感が少し浮くことがある。

### poster_summary

向くslot:

- `morning`
- `night`
- `late_night`

理由:

- 画像で止められるため幅が広い。
- 日常/街/着用者の画像なら朝でも機能する。
- 23時台は実データ上の勝ち枠。

### community_info

向くslot:

- `daytime`
- `night`
- `late_night`

理由:

- 集会・イベント・現場感は文脈が必要。
- 直近勝ち投稿は `23:00-23:59` で強かった。
- 日付/イベント入り画像は鮮度が重要。

### explainer

向くslot:

- `morning`
- `daytime`

理由:

- 長寿命で、今日の空気に左右されにくい。
- 日中の初見入口として使いやすい。
- 夜の主力枠を奪いすぎない方がよい。

## 6. Residual Type Priority

| residual_type | priority | best slots | note |
|---|---:|---|---|
| `residual_growth` | high | `night`, `late_night` | 後残り型の主力 |
| `profile_pull` | high | `night`, `late_night` | 説明しない型の価値を見る |
| `community_resonance` | high | `daytime`, `late_night` | 会話・返信・repostに期待 |
| `instant_reaction` | medium | `morning`, `daytime` | 軽量枠。主力にはしない |
| `silent_failure` | blocked | none | そのまま出さない |

現在の仮説:

- `culture_observer + poster_summary + image` は `residual_growth` または `profile_pull` 候補。
- `community_info + image` は `community_resonance` と `residual_growth` の両方を狙える。
- `explainer` は即時理解型だが、人格を薄くしないため日中に限定する。

## 7. Anti-Overuse Rules

### repeated_topic_penalty

条件:

```text
same topic or first-line pattern used within 48h
```

penalty: `-12`

理由: 同じ観測を擦ると、文化観測ではなくテンプレに見える。

### same_image_cooldown

条件:

```text
same image file used within 72h
```

penalty: `-14`

理由: S画像でも連投すると既視感が出る。画像は勝ち筋だが、擦ると広告感が強くなる。

### same_persona_decay

条件:

```text
same persona/category selected 3 times in a row
```

penalty: `-10`

理由: `culture_observer` だけに寄ると、鬼徹人格が静かすぎて単調になる。たまに `community_info` や `explainer` を挟む。

### same_time_slot_repetition

条件:

```text
same category selected in same slot for 2 consecutive days
```

penalty: `-6`

理由: 23時台優位は使う。ただし毎日同じ見え方にしない。

## 8. Daily Output Template

`reports/villain_daily_selection.md` は、将来的に同じファイル内へ当日選定結果を追記できる。

```md
## Daily Selection: YYYY-MM-DD

- selection_run_at_jst: ``
- source_stream_count: ``
- image_ready_count: ``
- approved_count: ``
- warnings: ``

### Selected Slots

| slot | time | stream_id | category | image_ready | residual_type | score | reason |
|---|---|---|---|---:|---|---:|---|
| morning | 07:00-09:00 |  |  |  |  |  |  |
| daytime | 12:00-15:00 |  |  |  |  |  |  |
| night | 18:00-22:30 |  |  |  |  |  |  |
| late_night | 23:00-23:59 |  |  |  |  |  |  |

### Backups

| rank | stream_id | category | best_slot | reason |
|---:|---|---|---|---|

### Do Not Use Today

| stream_id | reason |
|---|---|

### RealityGuard

- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
```

## 9. Data Output Design

`data/villain_daily_selection.json` に設計済み。

主要フィールド:

- `selection_policy`
- `selection_score_weights`
- `slot_definitions`
- `anti_overuse_rules`
- `residual_type_priority`
- `category_rotation_targets`
- `daily_selection_output_template`

将来の当日出力は以下の形にする。

```json
{
  "date_jst": "2026-05-16",
  "selection_run_at_jst": "",
  "source_stream_count": 0,
  "selected_slots": {
    "morning": null,
    "daytime": null,
    "night": null,
    "late_night": null
  },
  "backup_candidates": [],
  "warnings": [],
  "posting_execution_allowed": false
}
```

## 10. Selection Flow

1. Load candidate stream.
2. Exclude `posted`, `archived`, hard `stale`, high risk.
3. Apply freshness decay.
4. Apply image readiness bonus.
5. Apply residual type bonus.
6. Apply slot fit.
7. Apply anti-overuse penalties.
8. Enforce category balance.
9. Pick one candidate per slot.
10. Output report only.

No posting. No media upload. No X write.

## 11. Category Balance

1日4本の基本mix:

| category | count |
|---|---:|
| `culture_observer` | 1 |
| `poster_summary` | 1 |
| `community_info` | 1 |
| `explainer_or_apparel_connected` | 1 |

ルール:

- primary categoriesは1日最低2種類使う。
- 同じprimary categoryは1日2本まで。
- `apparel_focus` は単体で出さず、poster/culture/community接続がある場合だけ選ぶ。
- `explainer` は密度維持には使うが、夜の主力人格にはしない。

## 12. Current Known Signals

既存学習からの初期値:

- `poster_summary`: avg impressions `130.5`
- `community_info`: avg impressions `128.0`, max `201`
- image_yes: avg impressions `98.6`
- image_no: avg impressions `23.8`
- strongest_window: `23:00-23:59`
- winning voice: `現場を見て、短く残す人`

初期方針:

- late_night は `community_info`, `culture_observer`, `poster_summary` の画像ready候補を優先。
- morning/daytime は重すぎない `poster_summary` or `explainer`。
- night は文化観測の主力候補。
- same image の72h cooldownを守る。

## 13. Why Selection Layer Preserves Density And Persona

Selection layer があると、投稿密度と人格維持が両立しやすくなる。

理由は、量を増やす判断と、人格を守る判断を同じ場所で扱えるから。

Candidate Stream だけだと、候補は溜まるが「今日どれを出すか」はまだ人間の気分に残る。Residual Learning だけだと、後残り型は分かるが、朝昼夜の配置までは決まらない。Image Strategy だけだと、画像の強さは分かるが、同じ画像を擦りすぎる危険がある。

Daily Selection はその間に入って、以下を同時に見る。

- 今日のslotに合うか
- 画像は使えるか
- 後残り型か
- 同じ話題を擦っていないか
- 同じ人格に寄りすぎていないか
- カテゴリが偏っていないか

これにより、人間は毎回ゼロから悩まず「今日の朝はこれ、夜はこれ」と選べる。一方で、同じ画像・同じ観測・同じ人格を連投することを抑えられる。

結論: Selection layer は、投稿量を増やすための自動化ではなく、Villain人格を崩さずに投稿判断を軽くするための編集レイヤー。これがあると、1日3-5本に増やしても、`現場を見て、短く残す人` という芯を維持しやすい。

## 14. RealityGuard

- 投稿実行なし。
- create_tweetなし。
- upload_mediaなし。
- X API writeなし。
- commitなし。
- このOSは設計のみ。
