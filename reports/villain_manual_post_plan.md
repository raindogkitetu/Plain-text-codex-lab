# Villain Manual Post Plan

- Generated at: `2026-05-11T14:00:03.527347+00:00`
- FINAL_STATUS: `BLOCKED`
- Live posting: `DISABLED`
- X API write actions: `NOT USED`
- This is a manual checklist only.

## Current Gates

- `manual_approval_required`: `true`
- `approved_for_live_post`: `false`
- `write_action_kill_switch`: `true`
- `dry_run_only`: `true`
- `auto_post_enabled`: `false`
- `api_connected`: `false`
- pre-post check report: `exists`

## Manual Plan For `vln-dryrun-20260510-001`

- FINAL_STATUS: `BLOCKED`
- post_type: `ABOUT_WORDING`
- source_queue_id: `vln-queue-20260510-001`
- dry-run validator: `pass`
- manual approval: `true`
- approved_for_live_post: `false`
- write_action_kill_switch: `true`
- postable_judgment: `false`
- image_path: `missing`
- image check: `unchecked`
- passcode check: `unchecked`

### 投稿候補本文

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

### 人間チェックリスト

- [ ] 本文確認
- [ ] 禁止語・誤字確認
- [ ] 投稿先アカウント確認
- [ ] 画像有無確認
- [ ] 予約投稿ではない確認
- [ ] kill switch true の間は投稿不可: `true`

### BLOCK / 注意点

- write_action_kill_switch is true

### 手動運用メモ

- このレポートは投稿実行ではない。
- kill switch が true の間は、手動投稿も不可として扱う。
- 画像、投稿先、本文を人間が確認するまで先へ進めない。
