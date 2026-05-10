# X API Preflight Check

- Generated at: `2026-05-10T13:35:36.005240+00:00`
- preflight_status: `NOT_READY`
- live posting: `DISABLED`

## Reasons

- credentials not configured
- dry_run_only is true
- api_connected is false
- live post function missing by design
- auto_post_enabled is false

## Checklist

- [x] data/x_api_config.json exists: `PASS`
- [x] credentials are env-var names only: `PASS`
- [x] actual credential values are not stored: `PASS`
- [x] api_connected is false: `PASS`
- [x] dry_run_only is true: `PASS`
- [x] auto_post_enabled is false: `PASS`
- [x] manual_approval_required is true: `PASS`
- [x] live_post_blocked is true: `PASS`
- [x] no live post function exists: `PASS`
- [x] no upload_media function exists: `PASS`
- [x] no create_tweet function exists: `PASS`

## Forbidden Function Scan

- `x_login` exists: `false`
- `api_authenticate` exists: `false`
- `create_tweet` exists: `false`
- `upload_media` exists: `false`
- `publish_post` exists: `false`
- `schedule_live_post` exists: `false`

## Safety Note

This preflight reads configuration keys and scans local script text only.
It does not read environment variable values, log in to X, authenticate with an API, upload media, publish posts, or schedule posts.
