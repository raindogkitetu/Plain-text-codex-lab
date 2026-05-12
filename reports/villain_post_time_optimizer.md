# Villain Post Time Optimizer

- Generated at JST: `2026-05-12T23:06:26.616261+09:00`
- status: `DRY_RUN_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- DB mutation: `NOT_EXECUTED`
- day_kind: `weekday`
- history_count: `0`
- learning_mode: `fixed_rules_only`

## Base Windows JST

- weekday: `07:00-08:30, 12:00-13:00, 19:00-22:30`
- weekend: `09:00-11:00, 19:00-23:00`

## Recommended Items

### `vln-queue-20260510-001`

- source: `queue`
- post_type: `ABOUT_WORDING`
- status: `waiting_for_image`
- role: `main`
- primary_window_jst: `19:00-22:30`
- recommended_windows_jst: `19:00-22:30, 07:00-08:30, 12:00-13:00`
- recommendation_reason: ABOUT_WORDING は 19:00-22:30 を優先。

### `vln-gen-20260512-001`

- source: `candidate`
- post_type: `ABOUT_WORDING`
- status: `generated`
- role: `generated_candidate`
- primary_window_jst: `19:00-22:30`
- recommended_windows_jst: `19:00-22:30, 07:00-08:30, 12:00-13:00`
- recommendation_reason: ABOUT_WORDING は 19:00-22:30 を優先。

### `vln-gen-20260512-002`

- source: `candidate`
- post_type: `SILENT_DOMINANCE`
- status: `generated`
- role: `generated_candidate`
- primary_window_jst: `07:00-08:30`
- recommended_windows_jst: `07:00-08:30, 12:00-13:00, 19:00-22:30`
- recommendation_reason: 固定時間帯ルールをそのまま適用。

### `vln-gen-20260512-003`

- source: `candidate`
- post_type: `SELF_RESPECT`
- status: `generated`
- role: `generated_candidate`
- primary_window_jst: `07:00-08:30`
- recommended_windows_jst: `07:00-08:30, 12:00-13:00, 19:00-22:30`
- recommendation_reason: 固定時間帯ルールをそのまま適用。
