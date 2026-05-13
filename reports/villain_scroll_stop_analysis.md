# Villain Scroll Stop Analysis

- Generated at: `2026-05-13T07:08:56.108468+00:00`
- status: `REPORT_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- DB mutation: `NOT_EXECUTED`
- learning_source: `data/manual_post_results.json`

## Summary

- strongest_scroll_stop_post: `vln-queue-20260510-001`
- weakest_scroll_stop_post: `vln-gen-20260512-001`
- recommended_improvement: `詩的な余韻より、最初の一行に少し硬い違和感を置く。`

## Score Per Candidate

### vln-queue-20260510-001

- source: `post_queue`
- post_type: `ABOUT_WORDING`
- scroll_stop_score: `93`
- quality_score: `100`
- risk: `high`
- penalty: `5`
- penalty_reasons: `generic_message`
- recommended_improvement: `この方向で可。重くしすぎず、冒頭だけ少し尖らせる余地あり。`

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

#### Components

- first_line_hook: `16` - first_line=`ABOUTの文章、ちょっと強い。`
- emotional_trigger: `12` - 感情語/違和感語の有無。
- contradiction_or_tension: `12` - 普通さとのズレ、否定、反転の有無。
- curiosity_gap: `10` - 続きを読ませる余白の有無。
- shortness: `12` - text_length=120
- visual_match: `10` - image_hint または画像投稿文脈の有無。
- villainness: `14` - Villain固有語と強さの有無。
- memorability: `12` - 一言で残る文の有無。

### vln-gen-20260512-002

- source: `generated_candidates`
- post_type: `SILENT_DOMINANCE`
- scroll_stop_score: `82`
- quality_score: `94`
- risk: `low`
- penalty: `5`
- penalty_reasons: `generic_message`
- recommended_improvement: `この方向で可。重くしすぎず、冒頭だけ少し尖らせる余地あり。`

```text
強い服って、
大声じゃない方がいい。

黙ってても、
ちょっと残るやつ。

Villainはそっち。

#着て稼ぐ #villain @0xmavillain R2J9T
```

#### Components

- first_line_hook: `16` - first_line=`強い服って、`
- emotional_trigger: `12` - 感情語/違和感語の有無。
- contradiction_or_tension: `12` - 普通さとのズレ、否定、反転の有無。
- curiosity_gap: `5` - 続きを読ませる余白の有無。
- shortness: `12` - text_length=77
- visual_match: `10` - image_hint または画像投稿文脈の有無。
- villainness: `14` - Villain固有語と強さの有無。
- memorability: `6` - 一言で残る文の有無。

### vln-gen-20260512-003

- source: `generated_candidates`
- post_type: `SELF_RESPECT`
- scroll_stop_score: `75`
- quality_score: `100`
- risk: `low`
- penalty: `12`
- penalty_reasons: `generic_message, scroll_past_risk`
- recommended_improvement: `curiosity_gap を補強。意味の説明ではなく、止まる言葉を増やす。`

```text
誰かに見せるため、
だけじゃない服がある。

自分の側に戻る感じ。

今日はそれでいい。

#着て稼ぐ #villain @0xmavillain R2J9T
```

#### Components

- first_line_hook: `16` - first_line=`誰かに見せるため、`
- emotional_trigger: `12` - 感情語/違和感語の有無。
- contradiction_or_tension: `12` - 普通さとのズレ、否定、反転の有無。
- curiosity_gap: `5` - 続きを読ませる余白の有無。
- shortness: `12` - text_length=72
- visual_match: `10` - image_hint または画像投稿文脈の有無。
- villainness: `14` - Villain固有語と強さの有無。
- memorability: `6` - 一言で残る文の有無。

### vln-gen-20260512-001

- source: `generated_candidates`
- post_type: `ABOUT_WORDING`
- scroll_stop_score: `34`
- quality_score: `100`
- risk: `low`
- penalty: `42`
- penalty_reasons: `poetic_tone_too_soft, low_scroll_stop_power, villainness_too_low, generic_message`
- recommended_improvement: `詩的な余韻より、最初の一行に少し硬い違和感を置く。`

```text
ABOUTの言葉、
まだ残ってる。

毎日着ろって、
やっぱり普通じゃない。

でも今日はそこがいい。

#着て稼ぐ #villain @0xmavillain R2J9T
```

#### Components

- first_line_hook: `11` - first_line=`ABOUTの言葉、`
- emotional_trigger: `8` - 感情語/違和感語の有無。
- contradiction_or_tension: `12` - 普通さとのズレ、否定、反転の有無。
- curiosity_gap: `6` - 続きを読ませる余白の有無。
- shortness: `12` - text_length=78
- visual_match: `10` - image_hint または画像投稿文脈の有無。
- villainness: `8` - Villain固有語と強さの有無。
- memorability: `9` - 一言で残る文の有無。
