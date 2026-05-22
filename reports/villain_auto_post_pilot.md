# Villain Auto Post Pilot v1

- Generated at JST: `2026-05-22T23:00:03+09:00`
- version: `1.3.0`
- status: `LIMITED_LIVE_EXECUTION_BLOCKED`
- mode: `LIMITED_LIVE_EXECUTION`
- live posting by this script: `NOT_EXECUTED`
- X API write by this script: `NOT_USED`
- upload_media by this script: `NOT_EXECUTED`
- create_tweet by this script: `NOT_EXECUTED`
- execution_enabled: `true`
- source_mode: `candidate_stream`
- target_post_count: `0` / `3-3`

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
- media reuse cooldownは `7` 日。phash/sha256/path/prompt familyで近似重複を止める。
- note本文は作らない。各投稿に軽いnote_seedだけ残す。

## OpenAI Policy Alignment

- 人間の制御を残す: `post_after_publish_review`, `manual_override_allowed`, `delete_if_needed`。
- プライバシーを尊重し、APIキー/.env/機微情報は出力しない。
- スパム、欺瞞、なりすまし、無制限投稿を避ける。
- high risk / repeated / same image / token未検証は止める。
- 直近7日以内の同一/近似画像、同一構図、同一prompt familyは止める。
- 昨日/今日/明日/集会/現場/イベント/発表など現実文脈語は、根拠ファイルまたは明示承認なしでは止める。
- keep=false の投稿に近い candidate/image/prompt_family/topic は次候補から除外する。

## Live Pilot Limits

- max_posts_per_day: `3`
- posts_already_recorded_today: `2`
- remaining_posts_today: `1`
- cooldown_between_posts_minutes: `120`
- limited_live_execution_mode_enabled: `true`
- posting_adapter_in_this_script: `false`

## Warnings

- `pilot_plan_below_target_minimum`
- `no_image_ready_items`
- `limited_live_execution_manifest_only_no_x_write_adapter_called`

## Today's Pilot Plan

- No eligible pilot items.

## Execution Manifest

- No execution manifest items.


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
