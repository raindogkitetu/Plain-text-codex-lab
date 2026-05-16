# Villain Auto Post Pilot v1

- Generated at JST: `2026-05-16T11:09:35+09:00`
- version: `1.2.0`
- status: `LIVE_PILOT_BLOCKED`
- mode: `LIVE_PILOT`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- execution_enabled: `true`
- source_mode: `candidate_stream_empty_live_blocked`
- target_post_count: `0` / `3-5`

## Pilot Policy

- 完全放置ではなく、人間監督前提のlimited live pilot。
- DRY_RUNでは計画生成のみ。LIVE_PILOTでは上限内の実弾候補をarmする。
- このスクリプト実行中にX API writeは呼ばない。実投稿アダプタは別レイヤー。
- risk high / 重複 / 明らかな低品質 / novelty低すぎ は止める。
- max_posts_per_dayとcooldown_between_postsを必ず見る。
- post_after_publish_review / manual_override_allowed / delete_if_needed を前提にする。
- image_readyを優先するが、pilotではtext-only枠も警告付きで許可可能。
- note本文は作らない。各投稿に軽いnote_seedだけ残す。

## Live Pilot Limits

- max_posts_per_day: `5`
- posts_already_recorded_today: `0`
- remaining_posts_today: `5`
- cooldown_between_posts_minutes: `120`

## Warnings

- `pilot_plan_below_target_minimum`
- `no_image_ready_items`
- `live_pilot_requires_nonempty_candidate_stream`

## Today's Pilot Plan

- No eligible pilot items.

## Execution Boundary

このスクリプトは選定とarmまで。X API write adapterは呼ばない。

- LIVE_PILOT modeでも無制限投稿は禁止。
- risk highは禁止。
- 同一画像連投は禁止。
- 既投稿再投稿は禁止。
- 人間の後追い確認、削除、修正を前提にする。
- note本文、note構成、note投稿準備はしない。

## RealityGuard

- この実行では投稿実行なし。
- この実行ではcreate_tweetなし。
- この実行ではupload_mediaなし。
- この実行ではX API writeなし。
- 無制限投稿なし。
- mode: `LIVE_PILOT`。
