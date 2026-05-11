# Villain Pre-Post Safety Check

- Generated at: `2026-05-11T13:55:06.473355+00:00`
- Final judgment: `BLOCKED`
- Live posting: `DISABLED`
- X API write actions: `NOT USED`

## Summary

- dry-run validation status: `validated_blocked`
- payload count: `1`
- validator passed: `1`
- validator failed: `0`
- postable count: `0`
- global postable judgment: `false`

## Gates

- `manual_approval_required`: `true`
- `write_action_kill_switch`: `true`
- `auto_post_enabled`: `false`
- `dry_run_only`: `true`
- `api_connected`: `false`

## Meaning

- `dry-run validator pass` means the draft can be inspected safely.
- `manual approval received` means a human approval marker exists.
- `postable_judgment=false` means it is still not allowed to post.
- `write_action_kill_switch=true` keeps the final judgment BLOCKED.

## Payload `vln-dryrun-20260510-001`

- `source_queue_id`: `vln-queue-20260510-001`
- dry-run validator: `pass`
- caption characters: `131` / `25000`
- manual approval received: `true`
- approved_for_live_post: `false`
- approval is not postability: `true`
- postable_judgment: `false`

### Double Check

- first check / dry-run validator OK: `true`
- second check / manual approval OK: `true`
- final check / kill switch false: `false`

### Failures

- none

### Blockers

- write_action_kill_switch is true
