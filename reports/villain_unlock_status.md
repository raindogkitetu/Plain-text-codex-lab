# Villain Posting Unlock Status

- Generated at: `2026-05-12T05:34:44.280981+00:00`
- Overall unlock status: `BLOCKED`
- FINAL_STATUS source: `BLOCKED`
- Live posting: `DISABLED`
- X API write actions: `NOT USED`

## Rule Summary

- unlock target: `READY_FOR_MANUAL_POST`
- default status: `BLOCKED`
- all conditions required: `true`
- target account confirmed: `false`

## Payload `vln-dryrun-20260510-001`

- unlock status: `BLOCKED`
- dry-run validator: `pass`

### Conditions

- `manual_approval`: `pass` (actual `True`, required `True`)
- `approved_for_live_post`: `fail` (actual `False`, required `True`)
- `write_action_kill_switch`: `fail` (actual `True`, required `False`)
- `validator_passed_count`: `pass` (actual `1`, required `> 0`)
- `postable_count`: `fail` (actual `0`, required `> 0`)
- `final_status`: `fail` (actual `BLOCKED`, required `!= BLOCKED`)
- `caption_present`: `pass` (actual `True`, required `True`)
- `target_account_confirmed`: `fail` (actual `False`, required `True`)

### BLOCKED Reasons

- approved_for_live_post
- write_action_kill_switch
- postable_count
- final_status
- target_account_confirmed
