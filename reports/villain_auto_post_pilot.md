# Villain Auto Post Pilot v1

- Generated at JST: `2026-05-17T00:50:32+09:00`
- version: `1.3.0`
- status: `LIMITED_LIVE_EXECUTION_READY`
- mode: `LIMITED_LIVE_EXECUTION`
- live posting by this script: `NOT_EXECUTED`
- X API write by this script: `NOT_USED`
- upload_media by this script: `NOT_EXECUTED`
- create_tweet by this script: `NOT_EXECUTED`
- execution_enabled: `true`
- source_mode: `generated_candidates_fallback`
- target_post_count: `3` / `3-5`

## Pilot Policy

- 完全放置BOTではなく、人間監督前提のlimited live運用。
- DRY_RUNでは計画生成のみ。LIVE_PILOTでは実弾候補をarmする。
- LIMITED_LIVE_EXECUTIONでは、上限内の実行manifestを作る。
- このスクリプト実行中にX API writeは呼ばない。投稿adapterは別レイヤー。
- risk high / 重複 / 明らかな低品質 / novelty低すぎ は止める。
- required_tokens_verified=true をhard gateにする。
- max_posts_per_dayとcooldown_between_postsを必ず見る。
- post_after_publish_review / manual_override_allowed / delete_if_needed を前提にする。
- remixabilityをscoringに入れ、画像がコミュニティ素材化する確率を見る。
- image_readyを優先するが、pilotではtext-only枠も警告付きで許可可能。
- note本文は作らない。各投稿に軽いnote_seedだけ残す。

## OpenAI Policy Alignment

- 人間の制御を残す: `post_after_publish_review`, `manual_override_allowed`, `delete_if_needed`。
- プライバシーを尊重し、APIキー/.env/機微情報は出力しない。
- スパム、欺瞞、なりすまし、無制限投稿を避ける。
- high risk / repeated / same image / token未検証は止める。

## Live Pilot Limits

- max_posts_per_day: `5`
- posts_already_recorded_today: `0`
- remaining_posts_today: `5`
- cooldown_between_posts_minutes: `120`
- limited_live_execution_mode_enabled: `true`
- posting_adapter_in_this_script: `false`

## Warnings

- `candidate_stream_empty_using_generated_candidates_fallback`
- `live_pilot_using_generated_candidates_fallback_until_stream_is_populated`
- `limited_live_execution_manifest_only_no_x_write_adapter_called`

## Today's Pilot Plan

### 1. `morning` / `culture_observer`

- source: `generated_candidates` / `vln-gen-20260516-003`
- score: `110`
- risk: `low`
- passcode: `J1M5V`
- passcode_exists_in_db: `true`
- novelty: `66`
- raw_novelty: `70`
- remixability: `100`
- remixability_signals: `community_reposting_probability, cropability, identity_badge_feel, image_stands_alone, one_sentence_complete, screenshot_friendly, someone_else_can_say_it`
- saturation_flags: `repeated_structure`
- pilot_score: `314`
- image_ready: `true`
- image: `villain_post_images/生成画像1.png`
- required_tokens_valid_after: `true`
- required_tokens_verified: `true`
- mandatory_footer_order: `#着て稼ぐ #villain $PPP @0xmavillain`
- planned_publish_after_jst: `2026-05-17T08:00+09:00`
- post_after_publish_review: `true`
- manual_override_allowed: `true`
- delete_if_needed: `true`
- expected_type: `residual_growth_or_profile_pull`
- fallback_action: `hold_for_daytime_or_rewrite_lighter`
- reason: 勝ち人格のculture_observerを優先。説明する人ではなく、現場を見て短く残す人に寄せる。
- execution_gate_required_tokens: `true`
- execution_gate_same_image_cooldown_ok: `true`
- execution_gate_repeated_topic_ok: `true`

#### note_seed

- why_posted: 勝ち人格のculture_observerを優先。説明する人ではなく、現場を見て短く残す人に寄せる。
- expected_reaction: `residual_growth_or_profile_pull`
- human_observation_pending: `true`
- lesson_for_later: Record actual X reaction after posting; do not draft note yet.

```text
話題になる服って、
だいたい服だけじゃない。

誰が着て、
どこで集まってるかまで含めて、
少し残る。

#着て稼ぐ #villain $PPP @0xmavillain J1M5V
```

### 2. `daytime` / `community_info`

- source: `generated_candidates` / `vln-gen-20260516-001`
- score: `103`
- risk: `low`
- passcode: `F3X7M`
- passcode_exists_in_db: `true`
- novelty: `70`
- raw_novelty: `70`
- remixability: `100`
- remixability_signals: `community_reposting_probability, cropability, identity_badge_feel, image_stands_alone, one_sentence_complete, screenshot_friendly, someone_else_can_say_it`
- saturation_flags: `none`
- pilot_score: `321`
- image_ready: `true`
- image: `villain_post_images/20260514集会.png`
- required_tokens_valid_after: `true`
- required_tokens_verified: `true`
- mandatory_footer_order: `#着て稼ぐ #villain $PPP @0xmavillain`
- planned_publish_after_jst: `2026-05-17T13:00+09:00`
- post_after_publish_review: `true`
- manual_override_allowed: `true`
- delete_if_needed: `true`
- expected_type: `community_resonance`
- fallback_action: `hold_for_night_if_context_is_too_heavy`
- reason: 実データで最強だったcommunity_info型。集会/現場感を短く置き、説明ではなく文化の動きを見せる。
- execution_gate_required_tokens: `true`
- execution_gate_same_image_cooldown_ok: `true`
- execution_gate_repeated_topic_ok: `true`

#### note_seed

- why_posted: 実データで最強だったcommunity_info型。集会/現場感を短く置き、説明ではなく文化の動きを見せる。
- expected_reaction: `community_resonance`
- human_observation_pending: `true`
- lesson_for_later: Record actual X reaction after posting; do not draft note yet.

```text
昨日の集会、
まだ少し残ってる。

説明より、
人が集まってる事実の方が強い。

$villainは、
そこがちょっと変。

#着て稼ぐ #villain $PPP @0xmavillain F3X7M
```

### 3. `night` / `poster_summary`

- source: `generated_candidates` / `vln-gen-20260516-002`
- score: `96`
- risk: `low`
- passcode: `H9J6L`
- passcode_exists_in_db: `true`
- novelty: `43`
- raw_novelty: `57`
- remixability: `65`
- remixability_signals: `identity_badge_feel, one_sentence_complete, screenshot_friendly, someone_else_can_say_it`
- saturation_flags: `repeated_phrase, repeated_structure`
- pilot_score: `236`
- image_ready: `false`
- image: ``
- required_tokens_valid_after: `true`
- required_tokens_verified: `true`
- mandatory_footer_order: `#着て稼ぐ #villain $PPP @0xmavillain`
- planned_publish_after_jst: `2026-05-17T20:00+09:00`
- post_after_publish_review: `true`
- manual_override_allowed: `true`
- delete_if_needed: `true`
- expected_type: `residual_growth`
- fallback_action: `fallback_to_poster_summary_image_ready`
- reason: poster_summaryは平均130.5 impressions。文化の違和感を一行目に置き、画像で止める。
- execution_gate_required_tokens: `true`
- execution_gate_same_image_cooldown_ok: `true`
- execution_gate_repeated_topic_ok: `true`
- warnings: `image_not_ready_text_only_possible, primary_category_prefers_image`

#### note_seed

- why_posted: poster_summaryは平均130.5 impressions。文化の違和感を一行目に置き、画像で止める。
- expected_reaction: `residual_growth`
- human_observation_pending: `true`
- lesson_for_later: Record actual X reaction after posting; do not draft note yet.

```text
気づくと、
また$villainの話になってる。

服の話だけなら、
たぶんここまで残らない。

#着て稼ぐ #villain $PPP @0xmavillain H9J6L
```

## Execution Manifest

- `vln-exec-morning-vln-gen-20260516-003`
  - passcode: `J1M5V`
  - ready_for_limited_live_execution: `true`
  - planned_publish_after_jst: `2026-05-17T08:00+09:00`
  - x_api_write_called_by_this_script: `false`
  - upload_media_called_by_this_script: `false`
  - create_tweet_called_by_this_script: `false`
- `vln-exec-daytime-vln-gen-20260516-001`
  - passcode: `F3X7M`
  - ready_for_limited_live_execution: `true`
  - planned_publish_after_jst: `2026-05-17T13:00+09:00`
  - x_api_write_called_by_this_script: `false`
  - upload_media_called_by_this_script: `false`
  - create_tweet_called_by_this_script: `false`
- `vln-exec-night-vln-gen-20260516-002`
  - passcode: `H9J6L`
  - ready_for_limited_live_execution: `true`
  - planned_publish_after_jst: `2026-05-17T20:00+09:00`
  - x_api_write_called_by_this_script: `false`
  - upload_media_called_by_this_script: `false`
  - create_tweet_called_by_this_script: `false`

## 24h Learning

- 投稿後24hで `residual_growth`, `profile_clicks`, `repost_reuse`, `remixability` を見る。
- 画像が抜粋再投稿された場合は `repost_reuse=true` として残す。
- profile_clicksだけでなく、画像単体の二次拡散を学習対象にする。

## Execution Boundary

このスクリプトは選定、arm、execution manifest作成まで。X API write adapterは呼ばない。

- LIVE_PILOT modeでも無制限投稿は禁止。
- LIMITED_LIVE_EXECUTION modeでも、このスクリプト単体では投稿しない。
- risk highは禁止。
- 同一画像連投は禁止。
- 既投稿再投稿は禁止。
- APIキー/.env出力は禁止。
- 人間の後追い確認、削除、修正を前提にする。
- note本文、note構成、note投稿準備はしない。

## RealityGuard

- この実行では投稿実行なし。
- この実行ではcreate_tweetなし。
- この実行ではupload_mediaなし。
- この実行ではX API writeなし。
- 無制限投稿なし。
- mode: `LIMITED_LIVE_EXECUTION`。
