# Villain Auto Scheduler v1

- Generated at JST: `2026-05-22T23:00:03+09:00`
- status: `BLOCKED`
- mode: `LIVE_PILOT`
- live posting: `NOT_EXECUTED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- no_retry_unless_manual: `true`

## Scheduler Limits

- max_posts_per_day: `3`
- cooldown_between_posts_minutes: `120`
- max_posts_per_run: `1`
- posts_counted_today: `0`
- post_count_source: `data/villain_post_outcomes.json`

## Daily Slots

- 03:00: maintenance only; no posting.
- 13:00: daytime posting slot.
- 20:00: night posting slot.
- 23:00: late night posting slot.

## Gate Order

1. `manual_stop`
2. outcome DB daily success count
3. cooldown from latest successful outcome
4. `human_review.keep` from latest successful outcome
5. Auto Post Pilot candidate gates
6. X Write Adapter gates
7. network preflight before any write attempt

## Human Review Gate

- latest_success_tweet_id: `2057473911550521382`
- latest_success_posted_at_jst: `2026-05-21T23:49:41+09:00`
- latest_success_keep: `True`
- `pending` blocks as `human_review_pending`.
- `false` blocks as `previous_post_marked_delete_or_drop`.
- `true` is required before the next post.

## Stop

- Stop by setting `manual_stop` to `true` in `data/villain_auto_scheduler.json`.
- launchd登録後なら `launchctl unload ~/Library/LaunchAgents/com.raindog.villain-auto-scheduler.plist` でも止める。

## Selected Manifest

- none

## Adapter Check

- not run

## Network Preflight

- not run

## Sandbox Finding

- Codex sandbox can fail DNS resolution for `api.twitter.com` and `upload.twitter.com` before any X API request is sent.
- When DNS preflight fails, scheduler returns `NETWORK_PREFLIGHT_FAILED` before `upload_media` or `create_tweet`.
- In that state, passcode usage and outcome success records must not be updated.
- Real posting should run only from a network-enabled local environment.

## Runtime Context

- root: `/Users/raindog/Projects/villain-auto-posting`
- python: `/Library/Developer/CommandLineTools/usr/bin/python3`
- codex_credit_visible_to_scheduler: `false`
- codex_credit_controls_launchd: `false`
- network_preflight_controls_posting: `true`
- running_from_launchd_target_root: `true`

## Diagnosis

- none

## Commands

- DRY_RUN: `python3 scripts/auto_post_scheduler.py --mode DRY_RUN`
- LIVE_PILOT check: `python3 scripts/auto_post_scheduler.py --mode LIVE_PILOT`
- LIMITED_LIVE_EXECUTION equivalent check: `python3 scripts/auto_post_scheduler.py --mode LIMITED_LIVE_EXECUTION_CHECK`
- Future one-post execution requires both config `allow_write_execution=true` and CLI `--execute-one`.
