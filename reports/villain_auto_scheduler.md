# Villain Auto Scheduler v1

- Generated at JST: `2026-05-17T00:56:37+09:00`
- status: `SUCCESS_POSTED_ONCE`
- mode: `LIVE_PILOT`
- live posting: `EXECUTED_ONCE`
- upload_media: `EXECUTED_ONCE`
- create_tweet: `EXECUTED_ONCE`
- no_retry_unless_manual: `true`

## Scheduler Limits

- max_posts_per_day: `3`
- cooldown_between_posts_minutes: `120`
- max_posts_per_run: `1`
- posts_counted_today: `0`

## Stop

- Stop by setting `manual_stop` to `true` in `data/villain_auto_scheduler.json`.
- launchd登録後なら `launchctl unload ~/Library/LaunchAgents/com.raindog.villain-auto-scheduler.plist` でも止める。

## Selected Manifest

- execution_id: `vln-exec-morning-vln-gen-20260516-003`
- source_id: `vln-gen-20260516-003`
- slot: `morning`
- passcode: `J1M5V`
- ready_for_limited_live_execution: `true`

## Adapter Check

- status: `SUCCESS`
- mode: `LIMITED_LIVE_EXECUTION`
- live_posting: `EXECUTED_ONCE`
- upload_media: `EXECUTED_ONCE`
- create_tweet: `EXECUTED_ONCE`
- required_tokens_verified: `true`
- passcode_verified: `true`
- blockers: `none`

## Network Preflight

- status: `PASSED`
- request_sent: `false`
- upload_media_called: `false`
- create_tweet_called: `false`
- api.twitter.com: dns_resolved=`true`
- upload.twitter.com: dns_resolved=`true`

## Sandbox Finding

- Codex sandbox can fail DNS resolution for `api.twitter.com` and `upload.twitter.com` before any X API request is sent.
- When DNS preflight fails, scheduler returns `NETWORK_PREFLIGHT_FAILED` before `upload_media` or `create_tweet`.
- In that state, passcode usage and outcome success records must not be updated.
- Real posting should run only from a network-enabled local environment.

## Commands

- DRY_RUN: `python3 scripts/auto_post_scheduler.py --mode DRY_RUN`
- LIVE_PILOT check: `python3 scripts/auto_post_scheduler.py --mode LIVE_PILOT`
- LIMITED_LIVE_EXECUTION equivalent check: `python3 scripts/auto_post_scheduler.py --mode LIMITED_LIVE_EXECUTION_CHECK`
- Future one-post execution requires both config `allow_write_execution=true` and CLI `--execute-one`.
