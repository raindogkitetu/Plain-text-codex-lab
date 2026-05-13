# Villain Post Stock v1

- status: `REPORT_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- safe_post_status: `BLOCK`
- categories: `boss_attention`, `poster_summary`, `apparel_focus`, `lifestyle`

## Stock 1

- post_title: `気づくと、こればっか着てる`
- categories: `boss_attention`, `poster_summary`, `apparel_focus`, `lifestyle`
- recommended_time_window: `19:00-22:30`
- boss_attention_score: `90/100`
- test_priority: `high`

### social_post_text

```text
気づくと、
こればっか着てる。

説明しづらいけど、
“なんか合う”。

$villain

@0xmavillain C14QB
```

### image_copy

```text
$VILLAINは、日常だ。

気づくと、こればっか着てる。
```

### hypothesis

`apparel_focus + poster_summary + 日常の一言` は、抽象的な quote 投稿よりボス反応を取りやすい。

## Stock 2

- post_title: `届いたより、馴染んだ`
- categories: `boss_attention`, `apparel_focus`, `lifestyle`
- recommended_time_window: `19:00-22:30`
- boss_attention_score: `86/100`
- test_priority: `high`

### social_post_text

```text
届いた時より、
馴染んできた時の方が強い。

こういう服、
たぶん残る。

$villain

@0xmavillain C14QB
```

### image_copy

```text
届いたより、馴染んだ。
```

### hypothesis

「届いた〜！」系の強さを、到着報告ではなく日常化した文脈で再現できるかを見る。

## Stock 3

- post_title: `普通に着てるのが一番Villain`
- categories: `boss_attention`, `poster_summary`, `apparel_focus`, `lifestyle`
- recommended_time_window: `07:00-08:30`
- boss_attention_score: `84/100`
- test_priority: `medium_high`

### social_post_text

```text
特別な日じゃなくて、
普通の日に着てる。

その方が、
なんかVillainっぽい。

$villain

@0xmavillain C14QB
```

### image_copy

```text
普通の日に、$villain。
```

### hypothesis

Villainをイベント化せず、生活の中に置いた方がコミュニティ文化として拾われやすい。

## Use Notes

- 画像は poster_summary 寄り、ただし広告感を出しすぎない。
- `$villain` 表記を本文では統一する。
- 画像内の `$VILLAIN` 大文字表記は、使用前に許容するか確認。
- 逆さ三角マークは使わない。
- パスコードは実投稿前にローテーション確認。
- 実投稿は手動のみ。

## Do Not Post If

- 画像権利が不明。
- 画像内コピーが利益保証に見える。
- ボスに媚びている感じが出る。
- 投稿文を足しすぎて説明臭くなる。
- X API write / create_tweet / upload_media が必要になる。
