# Villain Image Type Analysis

- Generated at: `2026-05-13T07:13:21.321946+00:00`
- status: `REPORT_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- DB mutation: `NOT_EXECUTED`
- image_required_human_check: `REQUIRED`

## Summary

- best_image_type_hypothesis: `poster_summary (100.0)`
- image_type_recommendations: `poster_summary を優先テスト。quote_visual / apparel_focus は本文が強い時だけ採用。`
- next_test_recommendation: `vln-gen-20260512-002`

## Candidate Image Fit

### vln-gen-20260512-002

- source: `generated_candidates`
- post_type: `SILENT_DOMINANCE`
- image_type: `poster_summary`
- image_stop_score: `100`
- image_status: `image_required_human_check`
- image_required_human_check: `True`
- recommended_time_window: `07:00-08:30`
- quality_score: `94`
- risk: `low`
- recommendation: `次テスト優先。ポスター系の強さ仮説を検証する。`

#### image_hint

```text
POSTER_MODE: 暗い路地、中央にフードの背中、強い陰影、文字は『着て稼ぐ』と『$villain』まで。
```

#### text

```text
強い服って、
大声じゃない方がいい。

黙ってても、
ちょっと残るやつ。

Villainはそっち。

#着て稼ぐ #villain @0xmavillain R2J9T
```

#### axes

- scroll_stop_power: `20` - image_type=poster_summary
- readability_on_timeline: `12` - image_type=poster_summary
- poster_strength: `20` - poster_summary は初期仮説として強めに評価。
- visual_clarity: `10` - image_hint があるか、人間が画像を確認できる状態か。
- brand_fit: `12` - brand_term_detected=True
- text_image_match: `12` - image_hint_matches_text=True
- saveability: `16` - image_type=poster_summary

### vln-queue-20260510-001

- source: `post_queue`
- post_type: `ABOUT_WORDING`
- image_type: `poster_summary`
- image_stop_score: `100`
- image_status: `waiting_for_image`
- image_required_human_check: `True`
- recommended_time_window: `unknown`
- quality_score: `100`
- risk: `high`
- recommendation: `画像相性は高くても、risk=high のため通常投稿テストからは外す。`

#### image_hint

```text
Shop ABOUT文言とApparelの空気が分かる画像またはポスター
```

#### text

```text
ABOUTの文章、ちょっと強い。

Love $villain,
and wear it daily...

毎日着ろって
普通にすごいこと言ってる。

でもVillainなら
まあ言いそう。

#着て稼ぐ #villain @0xmavillain M5Q1C
```

#### axes

- scroll_stop_power: `20` - image_type=poster_summary
- readability_on_timeline: `12` - image_type=poster_summary
- poster_strength: `20` - poster_summary は初期仮説として強めに評価。
- visual_clarity: `10` - image_hint があるか、人間が画像を確認できる状態か。
- brand_fit: `12` - brand_term_detected=True
- text_image_match: `12` - image_hint_matches_text=True
- saveability: `16` - image_type=poster_summary

### vln-gen-20260512-003

- source: `generated_candidates`
- post_type: `SELF_RESPECT`
- image_type: `apparel_focus`
- image_stop_score: `84`
- image_status: `image_required_human_check`
- image_required_human_check: `True`
- recommended_time_window: `07:00-08:30`
- quality_score: `100`
- risk: `low`
- recommendation: `画像権利と見え方を人間確認してから判断。`

#### image_hint

```text
STREET_MODE: 店の外、雨上がり、顔を見せない人物、服の質感と街の余白を優先。
```

#### text

```text
誰かに見せるため、
だけじゃない服がある。

自分の側に戻る感じ。

今日はそれでいい。

#着て稼ぐ #villain @0xmavillain R2J9T
```

#### axes

- scroll_stop_power: `12` - image_type=apparel_focus
- readability_on_timeline: `12` - image_type=apparel_focus
- poster_strength: `8` - poster_summary は初期仮説として強めに評価。
- visual_clarity: `14` - image_hint があるか、人間が画像を確認できる状態か。
- brand_fit: `16` - brand_term_detected=True
- text_image_match: `12` - image_hint_matches_text=True
- saveability: `10` - image_type=apparel_focus

### vln-gen-20260512-001

- source: `generated_candidates`
- post_type: `ABOUT_WORDING`
- image_type: `quote_visual`
- image_stop_score: `55`
- image_status: `image_required_human_check`
- image_required_human_check: `True`
- recommended_time_window: `19:00-22:30`
- quality_score: `100`
- risk: `low`
- recommendation: `画像は強めのポスター寄りで補強。本文の柔らかさを画で止める。`

#### image_hint

```text
OBSERVER_MODE: 雨のネオン街、遠景の看板に『着て稼ぐ』、フード人物は後ろ姿、人物30%/背景70%。
```

#### text

```text
ABOUTの言葉、
まだ残ってる。

毎日着ろって、
やっぱり普通じゃない。

でも今日はそこがいい。

#着て稼ぐ #villain @0xmavillain R2J9T
```

#### axes

- scroll_stop_power: `0` - image_type=quote_visual
- readability_on_timeline: `17` - image_type=quote_visual
- poster_strength: `5` - poster_summary は初期仮説として強めに評価。
- visual_clarity: `10` - image_hint があるか、人間が画像を確認できる状態か。
- brand_fit: `4` - brand_term_detected=True
- text_image_match: `13` - image_hint_matches_text=True
- saveability: `6` - image_type=quote_visual
