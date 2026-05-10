# Villain Final Safety Check

- Generated at: `2026-05-10T13:27:18.980061+00:00`
- Overall judgment: `BLOCKED`
- Live posting: `not allowed`
- Payload count: `1`
- Queue count: `1`
- History count: `0`
- Status file loaded: `true`

This report is read-only. It does not log in to X, authenticate with an API, upload media, publish posts, schedule posts, or change any safety flags.

## Required Conditions For Future Posting

- `auto_post_enabled` must be true.
- `manual_approval_required` must remain true.
- `dry_run_only` must be false.
- `api_connected` must be true.
- Queue item must be approved.
- Image must be ready.
- Final caption must be ready.
- Prohibited content check must be pass.
- Human confirmation must exactly match POST_APPROVED.
- Live post function must exist and pass a separate review.

## Global BLOCKED Reasons

- auto_post_enabled is false
- dry_run_only is true
- api_connected is false
- posting_execution_allowed is false
- external_api_integration_allowed is false
- x_login_operation_allowed is false
- X credentials are not configured; only environment variable names are present
- no live post function exists

## Payload `vln-dryrun-20260510-001`

- Final judgment: `BLOCKED`
- `source_queue_id`: `vln-queue-20260510-001`
- `status`: `dry_run_preview_ready`
- `post_type`: `ABOUT_WORDING`
- `approved_for_live_post`: `true`
- `human_confirm_received`: `true`
- `dry_run_only`: `true`
- `api_connected`: `false`
- `live_post_blocked`: `true`
- `auto_post_enabled`: `false`
- `postable_judgment`: `false`

### BLOCKED Reasons

- auto_post_enabled is false
- dry_run_only is true
- api_connected is false
- posting_execution_allowed is false
- external_api_integration_allowed is false
- x_login_operation_allowed is false
- X credentials are not configured; only environment variable names are present
- no live post function exists
- image_path is null
- image_attached is not pass
- passcode_confirmed is not pass
- live_post_blocked is true
- postable_judgment is false
