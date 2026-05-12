# Villain Post Analysis

- Generated at: `2026-05-12T12:32:45.982132+00:00`
- status: `ANALYSIS_ONLY`
- live posting: `NOT EXECUTED`
- X API write: `NOT USED`
- upload_media: `NOT EXECUTED`
- create_tweet: `NOT EXECUTED`
- metrics source: `manual_or_read_only_later`

## vln-post-20260512-api-001

- post_url: https://x.com/raindog_kitetu/status/2054095791770538063
- posted_at: `2026-05-12T07:06:14.918224+00:00`
- post_type: `ABOUT_WORDING`
- tone_type: `rough_note_mode`
- image_type: `OBSERVER_MODE`
- image_used: `true`
- impressions: `manual_pending`
- likes: `manual_pending`
- reposts: `manual_pending`
- replies: `manual_pending`
- bookmarks: `manual_pending`
- engagement_rate: `manual_pending`
- text_length: `133`
- line_breaks: `12`
- villain_score: `95`
- quality_score: `100`
- risk: `high`
- already_posted: `true`

### Text

```text
ABOUTの文章、ちょっと強い。

Love $villain,
and wear it daily...

毎日着ろって。

普通そんなこと言わない。

でもVillainなら、
まあ言いそう。

#着て稼ぐ #villain @0xmavillain M5Q1C
```

### Result Summary

数値は未入力。初回API画像投稿として、ABOUT文言の引っかかりを短文で置いた投稿。

### Why It Worked Hypothesis

- ABOUTの文言をそのまま説明せず、最初の違和感から入っている。
- Love $villain / wear it daily を引用軸にして、新規にも入口がある。
- 画像付きで、Villainの空気を本文だけに背負わせていない。

### Why It Failed Hypothesis

- 数値未確認のため失敗要因は未確定。
- 文脈を知らない読者には、ABOUT文言の強さが少し伝わりにくい可能性がある。
- Passcode確認がDB上では未確認のため、運用リスクとして残る。

### Next Improvement

- 24時間後または任意タイミングでインプレッション/いいね/返信/保存を手入力する。
- 反応が弱い場合は、ABOUT文言の引用をもう少し前に出す。
- 反応が良い場合は、ABOUT_WORDING型を週1候補として残す。
