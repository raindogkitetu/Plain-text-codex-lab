# Villain API Post Readiness

- Generated at: `2026-05-12T06:07:32.848311+00:00`
- Overall API post readiness: `BLOCKED`
- FINAL_STATUS source: `BLOCKED`
- X API write actions: `NOT USED`
- create_tweet: `NOT EXECUTED`
- upload_media: `NOT EXECUTED`
- `.env` read: `NO`

## Rule Summary

- target status: `READY_FOR_API_POST`
- default status: `BLOCKED`
- api_write_allowed_now: `false`
- create_tweet_allowed_now: `false`
- target account: `@raindog_kitetu`

## Payload `vln-dryrun-20260510-001`

- API readiness: `BLOCKED`
- dry-run validator: `pass`
- caption characters: `131`
- recorded post URL: `https://x.com/raindog_kitetu/status/2054075449144467770?s=20`

### Caption

```text
ABOUTの文章、ちょっと強い。

Love $villain,
and wear it daily...

毎日着ろって
普通にすごいこと言ってる。

でもVillainなら
まあ言いそう。

#着て稼ぐ #villain @0xmavillain M5Q1C
```

### Conditions

- `approved_for_live_post`: `fail` (actual `False`, required `True`)
- `write_action_kill_switch`: `fail` (actual `True`, required `False`)
- `final_status`: `fail` (actual `BLOCKED`, required `READY_FOR_API_POST`)
- `postable_count`: `fail` (actual `0`, required `> 0`)
- `target_account_confirmed`: `fail` (actual `False`, required `True`)
- `caption_present`: `pass` (actual `True`, required `True`)
- `post_url_not_recorded`: `fail` (actual `False`, required `True`)
- `api_final_human_confirmed`: `fail` (actual `False`, required `True`)

### API Post BLOCKED Reasons

- approved_for_live_post
- write_action_kill_switch
- final_status
- postable_count
- target_account_confirmed
- post_url_not_recorded
- api_final_human_confirmed
