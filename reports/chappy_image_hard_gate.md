# Chappy Image Hard Gate

- updated_at_jst: `2026-05-22T14:26:00+09:00`
- status: `ENFORCED`
- live_posting: `NOT_EXECUTED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`

## Rule

Any post with an image path must have explicit Chappy image approval for that exact image before the X write adapter can execute.

Required approval fields:

```json
{
  "source": "chappy",
  "decision": "APPROVE_ONE",
  "approved_image_path": "/absolute/or/matching/path.png",
  "posting_permission_granted": false
}
```

Chappy image approval is visual approval only. It never grants posting permission by itself.

## Verified Block

The deleted replacement candidate was tested with `--execute-one`.

- status: `BLOCKED`
- blocker: `chappy_image_approval_missing`
- live_posting: `NOT_EXECUTED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`

## Current Replacement

- deleted_tweet_id: `2057684471256879127`
- request_json: `data/chappy_replacement_2057684471256879127_request.json`
- request_report: `reports/chappy_replacement_2057684471256879127_request.md`
- current_state: `WAITING_FOR_CHAPPY_IMAGE_DECISION`
- safe_to_post: `false`
- posting_execution_status: `BLOCKED`
- executable_ready_count: `0`
