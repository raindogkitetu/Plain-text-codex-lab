# Villain Candidate Stream OS v1

- Generated at JST: `2026-05-15`
- status: `DESIGN_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- commit: `NOT_EXECUTED`
- design DB: `data/villain_candidate_stream.json`

## 1. Concept

Candidate Stream は、投稿候補を「毎回ゼロから考える」状態から、「常に候補が流れていて、その中から選ぶ」状態へ変えるための候補在庫レイヤー。

既存構造との役割分担:

| layer | role |
|---|---|
| `generated_candidates` | 候補を作る |
| `candidate_stream` | 候補を5-15本保持し、鮮度・カテゴリ・画像・スコアで管理する |
| `queue` | 投稿直前の承認・安全チェック・手動投稿用 |
| `scoring/persona/image strategy` | stream item に評価値を付与する |
| `manual_post_results/residual learning` | 実績をstream設計とscoringへ戻す |

重要: stream は投稿実行権限を持たない。`approved` は「人間が投稿候補として採用可にした」という意味で、X投稿許可ではない。

## 2. Target State

- 常時 `5-15` 投稿候補を保持する。
- 主力カテゴリは `culture_observer`, `poster_summary`, `community_info`。
- 人間の作業は `approve`, `reject`, `timing` に寄せる。
- 投稿密度は `1日3-5本` を目標にする。
- 画像付き候補を優先する。
- 初速だけでなく、24h residual learning を次のstream補充に戻す。

## 3. Candidate Statuses

| status | meaning | human action |
|---|---|---|
| `fresh` | 生成直後。レビュー前または軽い確認のみ | approve / reject / hold |
| `approved` | 投稿候補として採用可。投稿実行許可ではない | timing指定、queue候補化 |
| `aging` | 寿命が近い。文脈確認が必要 | 今日使う / リライト / staleへ |
| `stale` | 文脈が古い。通常投稿から外す | リライト / archived |
| `archived` | 学習用に残すが選択対象外 | 参照のみ |
| `posted` | 人間が実投稿済み。URLと実績を記録 | 24h学習へ |

## 4. Lifespan Rules

| category | fresh | aging | stale | rule |
|---|---:|---:|---:|---|
| `culture_observer` | 12h | 24h | 36h | 今日の空気に寄るため短命。古くなると観測ではなく後出しになる |
| `poster_summary` | 24h | 72h | 120h | 画像とコピーが主役なので中寿命。日常/文化系なら数日使える |
| `community_info` | 12h | 36h | 72h | 集会・イベント文脈は鮮度が重要。日付入り画像は特に短命 |
| `explainer` | 72h | 168h | 336h | 設計説明は長寿命。ただし主力密度にはしない |
| `apparel_focus` | 24h | 72h | 120h | 服単体では弱い。culture/poster/community接続がない場合は早めに落とす |

寿命の思想:

- `culture_observer`: 空気を切るので短命。
- `poster_summary`: 画像で止めるので中寿命。
- `explainer`: 文脈が変わりにくいので長寿命。

## 5. Stream Management Policy

Queueではなくstreamとして管理する理由:

- queue は投稿直前の安全チェックに向く。
- stream は候補の鮮度、在庫、カテゴリバランス、画像準備状況を見るのに向く。
- queueに全部入れると「投稿待ち」の圧が強くなり、rejectやagingの判断がしづらい。
- streamなら候補を気軽に増やし、古くなったら落とせる。

基本方針:

- 生成器は毎回上書きではなく、streamへappendする設計に拡張する。
- stream item は `quality_prediction`, `persona_score`, `risk_prediction`, `image_ready`, `lifespan` を持つ。
- `approved` でも投稿実行はしない。
- `posted` になったら `manual_post_results` と `residual_learning` へ接続する。

## 6. Daily Operation For 3-5 Posts

### Morning: candidate generation

目的: その日の候補在庫を作る。

- active stream count を確認。
- `stream_count_low` なら5本以上補充。
- `category_bias` があれば不足カテゴリを優先。
- 画像戦略からS/A画像に合う候補を作る。
- 朝は `poster_summary` と `explainer` を多めに作ってもよい。

目標:

- active candidates: `8-12`
- image-ready candidates: `3+`
- approved-ready candidates: `3+`

### Midday: review

目的: 人間の判断を小さくする。

- freshから3-5本を見て、`approved`, `reject`, `hold` に分ける。
- 画像ありを優先。
- culture_observerは今日中に使うか捨てる。
- 23時候補、昼候補、返信/軽量候補を分ける。

目標:

- approved candidates: `3-5`
- 夜の主力: `1-2`
- 日中の軽量: `1-2`

### Evening/Night: posting selection

目的: 作るのではなく選ぶ。

- 18:00-22:30: poster_summary / apparel connected to culture
- 23:00-23:59: community_info / culture_observer / image-backed posts
- 投稿後はURLを記録し、24h residual analysisへ送る。

注意:

- 投稿実行は人間だけ。
- Codexは投稿文・画像候補・比較・記録まで。
- `create_tweet`, `upload_media`, X API write は禁止のまま。

## 7. Shortage Detection

### stream_count_low

条件:

```text
active_candidates < 5
```

対応:

- 朝生成で5本以上補充。
- `culture_observer`, `poster_summary`, `community_info` を最低1本ずつ入れる。

### category_bias

条件:

```text
one_primary_category_share > 0.6
or any primary category count == 0
```

対応:

- 不足カテゴリを優先生成。
- `apparel_focus` が増えすぎたら、culture/community接続があるものだけ残す。

### image_shortage

条件:

```text
image_ready_candidates < 3
or image_ready_ratio < 0.5
```

対応:

- `data/villain_image_strategy.json` のS画像を優先接続。
- `poster_summary`, `community_info`, `culture_observer` は原則画像あり。

### approved_shortage

条件:

```text
approved_candidates < 3
```

対応:

- 昼レビューでfreshから3本以上approvedに送る。
- risk low + image ready + persona high を優先。

## 8. Image Strategy Connection

Stream item は画像状態を持つ。

```json
{
  "image": {
    "required": true,
    "ready": true,
    "file_path": "villain_post_images/cf8fcb9d-0176-43ae-a9a8-0a727eb23625.png",
    "image_type": "poster",
    "match_score": 95,
    "rights_notes": "local generated asset; human final check required"
  }
}
```

優先順位:

1. `image_ready=true`
2. category と image_type が一致
3. `poster/culture/community` のS画像
4. risk low
5. persona score high

現在の画像接続:

| image | best categories | stream priority |
|---|---|---|
| `villain_post_images/20260514集会.png` | community_info, poster_summary | S |
| `villain_post_images/cf8fcb9d-0176-43ae-a9a8-0a727eb23625.png` | poster_summary, culture_observer, community_info | S |
| `villain_post_images/生成画像1.png` | poster_summary, culture_observer | S |
| `villain_post_images/0f4d2062-6e30-4a09-aea6-9fee9f0fe69d.png` | culture_observer | B |
| `villain_post_images/0a9d78af-455a-4778-a98d-c4bcc7081f41.png` | culture_observer | B |
| `villain_post_images/villain_observer_001.png` | culture_observer | C |

## 9. Stream Item Fields

`data/villain_candidate_stream.json` に設計済み。

主要フィールド:

- `stream_id`
- `source_candidate_id`
- `status`
- `category`
- `text`
- `image.required`
- `image.ready`
- `image.file_path`
- `scores.quality_prediction`
- `scores.persona_score`
- `scores.residual_growth_potential`
- `scores.profile_click_potential`
- `lifecycle.fresh_until_jst`
- `lifecycle.aging_after_jst`
- `lifecycle.stale_after_jst`
- `review.human_decision`
- `review.timing_hint`
- `post_execution.posting_execution_allowed=false`

## 10. Script Evolution Plan

Current:

- `scripts/generate_villain_candidates.py` creates max 3 candidates.
- `data/villain_generated_candidates.json` is a latest-run output.
- scoring/persona/image tools evaluate candidates or queue items.

Next design:

1. Add stream append mode.
   - Generated candidates are appended to `data/villain_candidate_stream.json`.
   - Duplicate text/candidate detection prevents repeated ideas.

2. Add lifecycle update.
   - A read/design script can mark fresh -> aging -> stale based on category lifespan.

3. Add shortage detector.
   - Report `stream_count_low`, `category_bias`, `image_shortage`, `approved_shortage`.

4. Add stream report.
   - `reports/villain_candidate_stream.md` becomes the daily inventory dashboard.

5. Keep queue separate.
   - Only human-approved candidates move toward queue/checklist.

## 11. Daily Stream Dashboard Draft

```md
## Stream Snapshot

- active candidates:
- fresh:
- approved:
- aging:
- stale:
- image_ready:
- stream_count_low:
- category_bias:
- image_shortage:

## Recommended Today

1. 23:00 main:
2. evening backup:
3. daytime light:

## Needs Generation

- culture_observer:
- poster_summary:
- community_info:
- image-ready:
```

## 12. Why Stream Raises Posting Density

Stream化すると投稿密度が上がる理由は、判断のボトルネックが変わるから。

今は「何を投稿するか」を毎回ゼロから考えている。これは品質は上がるが、投稿のたびに発想、文体調整、画像選定、安全確認、タイミング判断が全部一列に並ぶ。1本ごとの認知コストが高い。

Stream化すると、候補生成と投稿判断が分離される。

- 朝は作るだけ。
- 昼は選ぶだけ。
- 夜は出すだけ。

この分離で、人間は毎回「新しく考える」のではなく「今ある候補から選ぶ」状態になる。候補が5-15本あれば、今日の空気に合うものを拾えるし、合わないものはaging/staleに落とせる。

さらに、画像付き候補をstream内で優先できるため、実データで強い `poster_summary + image`, `community_info + image`, `culture_observer + image` を自然に多く出せる。

結論: stream化は、投稿品質を落として量を増やす仕組みではない。品質判断を前倒しして、投稿時の負荷を下げる仕組み。だから1日3-5本に増やしても、Villain人格と画像戦略を崩しにくい。

## 13. RealityGuard

- 投稿実行なし。
- create_tweetなし。
- upload_mediaなし。
- X API writeなし。
- stream DBは設計状態。
- commitなし。
