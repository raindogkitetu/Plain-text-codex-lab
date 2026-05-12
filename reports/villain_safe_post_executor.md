# Villain Safe Post Executor

- Generated at: `2026-05-12T14:01:29.816048+00:00`
- version: `2.0.0`
- status: `DRY_RUN_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- would_execute_actions: `DISPLAY_ONLY`
- targets_with_final_review_approve: `1`
- live unlock rule: `ALL_CONDITIONS_REQUIRED`

## `vln-queue-vln-gen-20260512-001`

- candidate_id: `vln-gen-20260512-001`
- selected_image: `/Users/raindog/Documents/New project/villain_post_images/villain_observer_001.png`
- safe_post_status: `BLOCK`
- failed_conditions: `queue_item_not_found, human_confirmed_false, approved_for_live_post_false, write_action_kill_switch_true, dry_run_only_true, passcode_ok_false`

### Conditions

- human_confirmed: `False`
- approved_for_live_post: `False`
- write_action_kill_switch: `True`
- passcode_ok: `False`
- dry_run_only: `True`
- auto_post_enabled: `False`
- manual_confirmation_mode: `True`
- selected_image_exists: `True`
- already_posted: `False`
- risk: `low`

### Required Live Post Checklist

- human_confirmed == true: `False`
- approved_for_live_post == true: `False`
- write_action_kill_switch == false: `False`
- passcode_ok == true: `False`
- DRY_RUN_ONLY == false: `False`
- auto_post == false or manual confirmation mode: `True`
- selected_image_exists == true: `True`
- already_posted == false: `True`
- risk != high: `True`

### Would Execute Actions

- `upload_media(image_path)`
- `create_tweet(text)`

### Text Preview

```text
ABOUTの言葉、
まだ残ってる。

毎日着ろって、
やっぱり普通じゃない。

でも今日はそこがいい。

#着て稼ぐ #villain @0xmavillain R2J9T
```
