# Villain Auto Post Pilot v1

- Generated at JST: `2026-05-16T11:13:08+09:00`
- version: `1.2.0`
- status: `LIMITED_LIVE_PILOT_READY`
- mode: `LIVE_PILOT`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- execution_enabled: `true`
- source_mode: `generated_candidates_fallback`
- target_post_count: `3` / `3-5`

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

- `candidate_stream_empty_using_generated_candidates_fallback`
- `live_pilot_using_generated_candidates_fallback_until_stream_is_populated`

## Today's Pilot Plan

### 1. `morning` / `culture_observer`

- source: `generated_candidates` / `vln-gen-20260515-003`
- score: `110`
- risk: `low`
- novelty: `66`
- raw_novelty: `70`
- saturation_flags: `repeated_structure`
- pilot_score: `214`
- image_ready: `true`
- image: `villain_post_images/生成画像1.png`
- planned_publish_after_jst: `2026-05-16T13:13+09:00`
- post_after_publish_review: `true`
- manual_override_allowed: `true`
- delete_if_needed: `true`
- expected_type: `residual_growth_or_profile_pull`
- fallback_action: `hold_for_daytime_or_rewrite_lighter`
- reason: 勝ち人格のculture_observerを優先。説明する人ではなく、現場を見て短く残す人に寄せる。

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

#着て稼ぐ #villain @0xmavillain R2J9T
```

### 2. `daytime` / `community_info`

- source: `generated_candidates` / `vln-gen-20260515-001`
- score: `103`
- risk: `low`
- novelty: `70`
- raw_novelty: `70`
- saturation_flags: `none`
- pilot_score: `221`
- image_ready: `true`
- image: `villain_post_images/20260514集会.png`
- planned_publish_after_jst: `2026-05-16T15:13+09:00`
- post_after_publish_review: `true`
- manual_override_allowed: `true`
- delete_if_needed: `true`
- expected_type: `community_resonance`
- fallback_action: `hold_for_night_if_context_is_too_heavy`
- reason: 実データで最強だったcommunity_info型。集会/現場感を短く置き、説明ではなく文化の動きを見せる。

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

#着て稼ぐ #villain @0xmavillain R2J9T
```

### 3. `night` / `poster_summary`

- source: `generated_candidates` / `vln-gen-20260515-002`
- score: `96`
- risk: `low`
- novelty: `43`
- raw_novelty: `57`
- saturation_flags: `repeated_phrase, repeated_structure`
- pilot_score: `171`
- image_ready: `false`
- image: ``
- planned_publish_after_jst: `2026-05-16T20:00+09:00`
- post_after_publish_review: `true`
- manual_override_allowed: `true`
- delete_if_needed: `true`
- expected_type: `residual_growth`
- fallback_action: `fallback_to_poster_summary_image_ready`
- reason: poster_summaryは平均130.5 impressions。文化の違和感を一行目に置き、画像で止める。
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

#着て稼ぐ #villain @0xmavillain R2J9T
```

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
