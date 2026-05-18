# Agent Handoff Status

- Generated at JST: `2026-05-17T23:49:27+09:00`
- schema_version: `handoff.codex_to_chatgpt.v1`
- status: `READY_FOR_CHATGPT_REVIEW`
- review_state: `CHATGPT_DECISION_CONSUMED`
- posting executed: `NO`
- upload executed: `NO`
- tweet creation executed: `NO`

## Quality Review

- quality_status: `BLOCKED`
- queue_health_status: `BLOCKED`
- review_board_status: `READY`
- posting_execution_status: `BLOCKED`
- executable_ready_count: `0`
- safe_to_review: `true`
- safe_to_post: `false`
- review_items: `9`
- blockers: `deleted_text_near_match, deleted_topic_context_cooldown, temporal_context_unverified, topic_image_pairing_mismatch`
- warnings: `deleted_nearby_match_found`
- blocked_reason_frequency: `{'deleted_text_near_match': 3, 'deleted_topic_context_cooldown': 6, 'temporal_context_unverified': 3, 'topic_image_pairing_mismatch': 3}`
- review_required_candidate_count: `0`
- READY_candidate_count: `3`
- BLOCKED_candidate_count: `6`
- stale_cleanup_removed: `0`

## ChatGPT Decision

- decision: `REVIEW_READY_NOT_POST_READY`
- approved_for_review: `1`
- not_approved_for_posting: `2`
- must_remain_blocked: `2`
- refill_required: `true`
- repair_actions: `6`
- repair_execution_status: `COMPLETED_REVIEW_ONLY`
- repaired_candidate_count: `3`
- context_evidence_request_count: `3`
- average_repair_quality_score: `85.0`
- average_repair_confidence: `70.0`
- repair_regression_risk_frequency: `{'medium': 3}`
- recurring_repair_failure_clusters: `2`

## Deleted Learning Cooldown

- `2055938300708626713` candidate `vln-gen-20260516-001`: `162.5`h remaining until `2026-05-24T18:22:16+09:00`

## Validation

- json_valid: `True`
- quality_review_runner: `True`
- tracking_code_absent: `True`
- x_write_not_used: `True`

## Unresolved Issues

- context_evidence source fileの標準形式を決める必要がある
- 候補が全部BLOCKEDのときのrefill処理は未実装
- 画像metadataが薄い候補のtopic-image判定をどう補強するか
- READYだがhuman_approved_for_posting=falseの候補をreview inboxとして別表示できるか
- Deleted learning cooldown is active for recent failed posts.

## Next Actions

- ChatGPT updates data/chatgpt_to_codex_handoff.json when policy changes.
- Codex runs scripts/agent_handoff_runner.py after local implementation or review.
- User approves only final READY/REVIEW_REQUIRED/BLOCKED summary.

## GitHub Handoff

- ChatGPT can read this contract and the JSON handoff files through the GitHub connector after commit/push.
- Codex should only publish handoff/review/report files for this loop; posting artifacts stay gated.

## ChatGPT Bridge

- bridge prompt: `reports/chatgpt_bridge_prompt.md`
- last ingestion at JST: `2026-05-17T23:52:43+09:00`
- last_chatgpt_response_status: `ACCEPTED`
- ingestion_errors: `none`
- safe_to_post: `false`
- posting_execution_status: `BLOCKED`
- posting executed: `NO`
- upload executed: `NO`
- tweet creation executed: `NO`
