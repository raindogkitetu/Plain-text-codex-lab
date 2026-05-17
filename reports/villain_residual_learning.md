# Villain Residual Learning OS v1

- Generated at JST: `2026-05-15`
- status: `DESIGN_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- commit: `NOT_EXECUTED`
- scope: residual growth learning for manual Villain posts

## 1. Why This OS Exists

Villain投稿は、初速だけで強弱を決めると誤判定しやすい。

特に `culture_observer`, `poster_summary`, `説明しない観測型` は、投稿直後の反応よりも、24時間後に「じわっと残ったか」を見る必要がある。

現在の勝ち筋は以下。

- `community_info`: avg impressions `128.0`, max `201`
- `poster_summary`: avg impressions `130.5`, max `134`
- image_yes: avg impressions `98.6`
- image_no: avg impressions `23.8`
- strongest time window: `23:00-23:59`
- winning voice: `現場を見て、短く残す人`

Residual Learning OS は、これを初速評価から24h評価へ拡張する。

## 2. Proposed Data Structure

`data/manual_post_results.json` の各 `manual_post_results[]` に、以下のフィールドを追加する案。

```json
{
  "initial_metrics": {
    "recorded_at_jst": "",
    "age_minutes": null,
    "impressions": null,
    "likes": null,
    "reposts": null,
    "replies": null,
    "bookmarks": null,
    "profile_clicks": null
  },
  "24h_metrics": {
    "recorded_at_jst": "",
    "age_hours": null,
    "impressions": null,
    "likes": null,
    "reposts": null,
    "replies": null,
    "bookmarks": null,
    "profile_clicks": null
  },
  "residual_learning": {
    "residual_growth_rate": null,
    "profile_click_retention": null,
    "delayed_engagement": null,
    "residual_type": "",
    "classification_reason": "",
    "feature_tags": []
  }
}
```

既存の `impressions`, `likes`, `reposts`, `replies`, `bookmarks`, `profile_visits` は最終値または手入力用として残す。時間差分析は `initial_metrics` と `24h_metrics` に寄せる。

## 3. Metric Definitions

### residual_growth_rate

24hでどれだけ後伸びしたか。

```text
residual_growth_rate =
  (24h_metrics.impressions - initial_metrics.impressions)
  / max(initial_metrics.impressions, 1)
```

目安:

- `>= 1.00`: 24hで初速の2倍以上。後残り型が強い
- `0.40 - 0.99`: 後伸びあり
- `0.10 - 0.39`: 少し伸びるが初速依存
- `< 0.10`: ほぼ初速型

### profile_click_retention

プロフィール誘導が24hでも残ったか。

```text
profile_click_retention =
  24h_metrics.profile_clicks / max(initial_metrics.profile_clicks, 1)
```

初速が0で24hが1以上なら、`delayed_profile_pull=true` として別途評価する。

### delayed_engagement

いいね以外の遅延反応を含めた後残りスコア。

```text
delayed_engagement =
  (24h.likes - initial.likes)
  + 2 * (24h.replies - initial.replies)
  + 3 * (24h.reposts - initial.reposts)
  + 2 * (24h.profile_clicks - initial.profile_clicks)
```

`profile_clicks` はVillain文脈では重めに扱う。説明しない観測型は、いいねより「誰だこれ」と見に行く反応が重要。

## 4. Residual Type Classification

### instant_reaction

初速で反応が出て、その後ほぼ増えない。

- residual_growth_rate `< 0.10`
- delayed_engagement `<= 1`
- profile_click_retention `< 1.2`

向いている型: meme, 強い単発コピー, 話題便乗。

### residual_growth

24hでimpressionsがじわじわ伸びる。

- residual_growth_rate `>= 0.40`
- 24h impressions が baseline に近づく、または超える
- repostなしでも views が増える

向いている型: culture_observer, poster_summary, community_info。

### profile_pull

impressionsより profile_clicks が強い。

- 24h profile_clicks `>= 2`
- または delayed_profile_pull `true`
- profile_clicks / impressions が過去平均より高い

向いている型: 説明しない観測型、謎を残す短文、画像で世界観を見せる投稿。

### community_resonance

返信・repost・引用・会話の種が出る。

- replies `>= 2`
- reposts `>= 1`
- delayed_engagement のうち replies/reposts が主成分

向いている型: community_info, event recap, gathering image。

### silent_failure

初速も24hも伸びず、プロフィール誘導もない。

- 24h impressions が baseline の半分未満
- profile_clicks `0`
- delayed_engagement `0`

主な原因候補: 抽象度が高すぎる、画像が説明しすぎる、服単体紹介、文が詩に寄りすぎる。

## 5. Feature Extraction For Residual Posts

各投稿に以下の特徴タグを持たせる。

```json
{
  "residual_features": {
    "post_category": "culture_observer",
    "image_type": "poster",
    "image_secondary_types": ["culture", "apparel", "community"],
    "posted_hour_jst": 23,
    "time_window": "23:00-23:59",
    "text_line_count": 9,
    "text_char_count": 88,
    "explanation_density": 0.18,
    "observation_density": 0.82,
    "has_direct_cta": false,
    "has_question": false,
    "has_community_signal": true,
    "has_apparel_signal": true
  }
}
```

### explanation_density

説明語の比率。低いほど「説明しない観測型」。

説明語例:

- 理由
- つまり
- だから
- とは
- 仕組み
- 設計
- 条件
- 詳しく

今回の投稿は、説明語が少ないため `explanation_density` は低めに判定する。

### observation_density

観測語・現場語の比率。

観測語例:

- 見る
- 着てる人
- 集まってる
- 残る
- 変
- 気づくと
- 話になってる

今回の投稿は `着てる人`, `集まってる`, `ちょっと変` があり、観測密度は高い。

## 6. 24h Analysis Report Template

24時間後の分析は、このレポートに追記するか、同じ構造で別セクションを追加する。

```md
## 24h Check: 2055294832743182612

- checked_at_jst: ``
- age_hours: ``
- source: `GET/read only`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`

### Metrics

| metric | initial | 24h | delta |
|---|---:|---:|---:|
| impressions |  |  |  |
| likes |  |  |  |
| reposts |  |  |  |
| replies |  |  |  |
| profile_clicks |  |  |  |

### Residual Scores

- residual_growth_rate: ``
- profile_click_retention: ``
- delayed_engagement: ``
- residual_type: ``

### Comparison Against Previous Winner

Previous winner:

- first_line: `昨日の集会、`
- category: `community_info`
- impressions: `201`
- likes: `17`
- reposts: `2`
- replies: `3`
- profile_clicks: `1`

Current post:

- first_line: `説明より、`
- category: `culture_observer + poster_summary + image`
- image: `villain_post_images/cf8fcb9d-0176-43ae-a9a8-0a727eb23625.png`
- time_window: `23:00-23:59`

### Judgment

- time delayed growth:
- profile pull:
- culture observer durability:
- poster summary image continuity:
- explanation-less residual effect:
- final type: `instant_reaction | residual_growth | profile_pull | community_resonance | silent_failure`
```

## 7. Scoring Integration Policy

`data/villain_post_scoring_rules.json` には、将来的に以下を追加する。

```json
{
  "residual_learning_weights": {
    "residual_growth_potential": 10,
    "profile_click_potential": 8,
    "delayed_engagement_potential": 6,
    "instant_reaction_penalty_when_overoptimized": -5
  }
}
```

反映方針:

- `residual_growth` 判定が2回以上出たカテゴリは、次回候補で優先度を上げる。
- `profile_pull` 判定が出た文体は、impressionsが中程度でも残す。
- `silent_failure` が出た場合は、画像・文体・時間帯を分解して原因を見る。カテゴリごと捨てない。
- 初速の likes だけで判断しない。
- profile_clicks は、Villain人格における「入口を開けた反応」として重く扱う。

## 8. Current Post Tracking Target

Target post:

- URL: `https://x.com/raindog_kitetu/status/2055294832743182612?s=20`
- candidate_id: `vln-gen-20260515-final-culture-observer-poster-summary`
- post_datetime_jst: `2026-05-15T23:34:09+09:00`
- post_type: `culture_observer + poster_summary + image`
- image_used: `true`
- image_file: `villain_post_images/cf8fcb9d-0176-43ae-a9a8-0a727eb23625.png`
- test_focus: `24h residual growth`

Text:

```text
説明より、
着てる人の方が早い。

しかも少しずつ、
集まってる。

$villainは、
そこがちょっと変。

#着て稼ぐ #villain @0xmavillain R2J9T
```

Feature hypothesis:

- `culture_observer`: strong
- `poster_summary_plus_image`: strong
- `explanation_density`: low
- `observation_density`: high
- `profile_pull_potential`: medium-high
- `community_resonance_potential`: medium
- expected residual_type: `residual_growth` or `profile_pull`

## 9. Why Villain Persona Tends To Be Residual

Villain人格は、即時に分かりやすい広告文より、少し引っかかる観測に寄っている。

「説明より、着てる人の方が早い。」は、その場で大きな反応を取りに行く文ではない。むしろ、画像を見た後に「たしかに何か動いてる」と遅れて理解される文。

この人格は、以下の理由で後残り型になりやすい。

1. 断定より観測が多い  
   読者に解釈の余白を渡すので、即いいねよりも後から見返す・プロフィールを見る反応に寄りやすい。

2. 商品説明ではなく文化の気配を出す  
   服の機能を説明しないため、購買導線は弱く見えるが、世界観への入口は残る。

3. 画像と本文の役割が分かれている  
   画像が「何があるか」を見せ、本文が「なぜ少し変なのか」を残す。読解が一拍遅れる分、24hで評価した方が正しい。

4. コミュニティ文脈は遅れて伝播する  
   集会、着用者、街、会話の気配は、タイムラインで一瞬に消費されるより、関係者や周辺層にじわっと届く。

5. Villainの強さは「大声」ではなく「残る違和感」  
   瞬間最大風速ではなく、見た人の中に小さく残る方が人格に合っている。

結論: Villain人格は、強いCTAやトレンド便乗で瞬間反応を取りに行くより、`culture_observer + poster_summary + image + low explanation density` で24hの残り方を見る方が学習精度が高い。

## 10. RealityGuard

- 投稿実行なし。
- X API writeなし。
- create_tweetなし。
- upload_mediaなし。
- このレポートは設計のみ。
- scoringやDBへの本反映は24h実測後に行う。
