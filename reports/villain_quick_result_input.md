# Villain Quick Result Input

- Generated at JST: `2026-05-13T16:29:37.071045+09:00`
- status: `REPORT_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- DB mutation: `NOT_EXECUTED`
- baseline_impressions: `60`
- posted_slot_count: `1`

## Slot 1

- candidate_id: `vln-gen-20260512-001`
- post_url: `https://x.com/raindog_kitetu/status/2054095791770538063`
- post_datetime_jst: `2026-05-12T16:06:14.669000+09:00`
- hours_since_post: `24.4h`
- baseline_comparison: `pending_vs_baseline_60`
- result_status: `manual_metrics_pending`

### 30 Second Input Template

```text
candidate_id: vln-gen-20260512-001
post_url: https://x.com/raindog_kitetu/status/2054095791770538063
post_datetime_jst: 2026-05-12T16:06:14.669000+09:00
impressions: 
likes: 
reposts: 
replies: 
bookmarks: 
profile_visits: 
follows: 
manual_notes: usual average impressions around 60
this post weaker than baseline
poetic tone may be too soft
persona_fit: medium
```

### Quick Judgment

- weak: impressions < 60
- normal: 60 <= impressions < 100
- strong: impressions >= 100
- 24h未満なら `wait_for_24h_metrics` を優先
