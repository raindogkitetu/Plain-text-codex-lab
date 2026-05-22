# Villain Image Strategy OS v1

- status: `DRY_RUN_ONLY`
- read_only: `true`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- queue mutation: `NOT_EXECUTED`
- source report: `reports/villain_x_current_analysis.md`
- source learning DB: `data/manual_post_results.json`
- strategy DB: `data/villain_image_strategy.json`

## Why This Exists

直近X実データでは、画像あり投稿が画像なし投稿より明確に強い。

- image_yes: count `7`, avg impressions `98.6`, max `201`
- image_no: count `13`, avg impressions `23.8`, max `49`
- strongest post: community_info `昨日の集会、` with image, `201` impressions
- strong category cluster: `community_info`, `poster_summary`, `culture_observer`
- weak pattern: imageなしの `observer_ai_record` 連投、服単体の `apparel_focus`

結論: 次フェーズでは、画像を「添える」ではなく、投稿カテゴリごとに選ぶ。主力は community / poster / culture 画像。

## Image Inventory

| file | size | primary type | secondary types | priority | best use |
|---|---:|---|---|---|---|
| `villain_post_images/20260514集会.png` | 1122x1402 | community | poster, culture, meme | S | 集会・スペース・コミュニティの動きを短く残す |
| `villain_post_images/cf8fcb9d-0176-43ae-a9a8-0a727eb23625.png` | 1402x1122 | poster | culture, apparel, community | S | 日常・街・着用者の空気を使う poster_summary |
| `villain_post_images/生成画像1.png` | 1024x1536 | poster | culture, apparel | S | `$VILLAINは日常だ` 系の短い文化観測 |
| `villain_post_images/0f4d2062-6e30-4a09-aea6-9fee9f0fe69d.png` | 1254x1254 | meme | poster, observer | B | 強い一言の単発投稿 |
| `villain_post_images/0a9d78af-455a-4778-a98d-c4bcc7081f41.png` | 1254x1254 | meme | poster, observer, apparel | B | 保存される標語系。夜帯に少量 |
| `villain_post_images/villain_observer_001.png` | 1536x1024 | observer | poster, culture | C | observer系の補助。主力にはしない |

## Category Match Table

| post category | preferred image types | avoid | rule |
|---|---|---|---|
| `community_info` | community, poster, culture | observer, unknown | 集会、会話、現場感が見える画像を優先。本文は説明せず短く置く |
| `poster_summary` | poster, culture, community | unknown | 画像のコピー/構図で止め、本文は一言の違和感にする |
| `culture_observer` | culture, community, poster | unknown | 服そのものではなく、誰がどこでどう残しているかを見る |
| `apparel_focus` | culture, poster, apparel | apparel-only | 服単体紹介で終わらせない。着用者・場所・会話に接続する |
| `observer_ai_record` | culture, observer | no-image streak | 単純なold/new mining machine結果報告なら生成しない |

## Next Image Candidates

1. `villain_post_images/20260514集会.png`
   - category: `community_info`
   - slot: `23:00-23:59`
   - reason: 実データ最強投稿と同じ、集会/現場感/画像ありの型。

2. `villain_post_images/cf8fcb9d-0176-43ae-a9a8-0a727eb23625.png`
   - category: `poster_summary`
   - slot: `23:00-23:59`
   - reason: poster_summary平均 `130.5` impressions の勝ち型に合う。日常・街・着用者の空気がある。

3. `villain_post_images/生成画像1.png`
   - category: `culture_observer`
   - slot: `23:00-23:59`
   - reason: 服単体ではなく、日常に入り込んだ違和感を置ける。

## No-Image Reduction Rule

原則:

- `community_info`, `poster_summary`, `culture_observer` は画像ありで候補化する。
- 画像候補がない `community_info` は優先度を下げる。
- 画像なし `observer_ai_record` は連投しない。
- `apparel_focus` は、画像があっても服単体紹介なら主力にしない。

画像なしを許可する例外:

- 返信や会話文脈で画像が邪魔になる。
- 速報性が高く、画像確認待ちで文脈が古くなる。
- 本文単体で強い一文があり、画像が説明しすぎる。

## Operational Direction

今のVillain人格は、服を説明する人より「現場を見て短く残す人」が強い。

画像戦略もそこに合わせる。

- 増やす: 集会、会話、街、カフェ、夜道、複数人、着用者の空気
- 減らす: 画像なし観測ログ、服単体紹介、old/new mining machineの単純結果報告
- 維持: 23時台の community/culture/poster 投稿
- 注意: meme画像は強いが、連投すると広告感・煽り感が勝つ

## Review Status

- local image inventory: `6` files
- strategy JSON added: `data/villain_image_strategy.json`
- report added: `reports/villain_image_strategy.md`
- X API write code added: `NO`
- create_tweet code added: `NO`
- upload_media code added: `NO`
- posting execution added: `NO`
