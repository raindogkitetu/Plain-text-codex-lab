# Villain Next Manual Test Plan

- status: `REPORT_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- DB mutation: `NOT_EXECUTED`
- safe_post_status: `BLOCK`

## Test Hypothesis

`poster_summary` 画像は、`quote_visual` よりスクロール停止力が高い。

## Next Test

- candidate_id: `vln-gen-20260512-002`
- image_type: `poster_summary`
- post_method: `manual_only`
- baseline_impressions: `60`
- success_condition: `impressions >= 60`
- better_condition: `impressions >= 100`
- recommended_time_window: `07:00-08:30` または `19:00-22:30`

## Recommended Text

```text
“強そう”って、だいたい浅い。
残るのは、静かな方。
```

## Why This Test

- Unified Test Selector の次候補が `vln-gen-20260512-002`
- Image Type Scorer で `poster_summary` が最有力仮説
- Slot1 の弱点は `poetic_tone_too_soft` / `low_scroll_stop_power` / `villainness_too_low`
- 今回は短く、硬く、止まる一文を優先する

## Human Checklist

- [ ] poster_summary 画像を人間が確認
- [ ] 画像の権利・使用可否を確認
- [ ] 本文が金融助言に見えない
- [ ] 画像内コピーが利益保証に見えない
- [ ] 投稿先アカウントを確認
- [ ] 手動投稿のみで実施

## Do Not Post If

- 利益保証に見える
- 画像権利が不明
- 画像コピーが本文より強すぎる
- 特定個人/団体への攻撃に見える
- 文脈なしで炎上しそう

## Result Fields To Fill Later

- post_url:
- posted_at_jst:
- impressions:
- likes:
- reposts:
- replies:
- bookmarks:
- profile_visits:
- follows:
- manual_notes:
- good_pattern:
- weak_pattern:
- persona_fit:
