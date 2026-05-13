# Villain Next Post Ready

- status: `REPORT_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- safe_post_status: `BLOCK`
- post_method: `manual_only`

## 1. Recommended Image

- file_name: `cf8fcb9d-0176-43ae-a9a8-0a727eb23625.png`
- path: `villain_post_images/cf8fcb9d-0176-43ae-a9a8-0a727eb23625.png`
- image_type: `poster_summary`
- fit: `high`

理由:

- 複数カットのまとめ画像で、タイムライン上で止まりやすい。
- Apparelが日常に入っている感じが出ている。
- 人物が顔アップではなく、生活/街/服の文脈になっている。
- ボスが拾いやすい「文化が実物になっている」方向。
- 投稿本文の「こればっか着てる」と画像の反復カットが合う。

注意:

- 画像内表記は `$VILLAIN` 大文字。運用上 `$villain` 統一を厳密に守るなら、画像修正版を推奨。
- `$villain` 下の逆さ三角マークは目立つ形では使われていないが、左下/服ロゴ周辺のブランド意匠は投稿前に人間確認する。
- 画像内文字は読みやすいが、情報量は多め。本文は短くする。

## 2. Post Text

```text
気づくと、
こればっか着てる。

説明しづらいけど、
“なんか合う”。

$villain

@0xmavillain
```

## 3. Recommended Time

- primary: `19:00-22:30`
- secondary: `07:00-08:30`

理由:

- 現場感/日常感のある画像は夜の方が見られやすい仮説。
- 朝に出す場合は軽い日常投稿として扱う。

## 4. boss_attention_score

- score: `88/100`

内訳:

- 現場感: `25/25`
- 日常感: `20/20`
- Villain文化拡張: `18/20`
- 画像の止まり: `18/20`
- ボスが拾う余白: `7/15`

減点:

- 画像内表記が `$VILLAIN` 大文字で、指定の `$villain` 統一とは完全一致しない。
- 画像内情報量が多く、本文側で説明しすぎると弱くなる。

## 5. Hypothesis

`apparel_focus + poster_summary + 日常の一言` は、抽象的な `quote_visual` よりボス反応を取りやすい。

検証したいこと:

- Apparelが「思想」ではなく「日常」になっている投稿は拾われやすいか。
- `届いた〜！` 系の強さを、日常着用文脈で再現できるか。
- 画像の情報量が多い場合、本文を短くした方が反応が出るか。

## 6. Pre-post Checklist

- [ ] 画像内表記 `$VILLAIN` を許容するか確認
- [ ] `$villain` 統一が必要なら画像を修正/再生成
- [ ] 画像権利・生成元・使用可否を確認
- [ ] 画像内コピーが利益保証に見えない
- [ ] 投稿本文に金融助言がない
- [ ] 誰か個人/団体への攻撃に見えない
- [ ] 投稿先アカウントを確認
- [ ] 手動投稿のみで実施
- [ ] 投稿後、24h後に quick input へ結果記録

## 7. do_not_post_if

- `$villain` 表記統一が必須で、画像修正がまだの場合
- 画像権利が不明な場合
- 画像内ロゴ/意匠が意図と違う場合
- 投稿本文を足しすぎて説明臭くなった場合
- 利益保証や投資助言に見える場合
- ボスに媚びている感じが出た場合

## Final Judgment

- ready_for_manual_post: `conditional`
- condition: `画像内 $VILLAIN 大文字表記を許容するなら手動投稿候補。厳密に $villain 統一するなら画像修正後。`
- API_post_ready: `false`
- safe_post_status: `BLOCK`
