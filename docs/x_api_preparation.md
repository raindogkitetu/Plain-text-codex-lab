# X API Preparation

This document describes preparation only. It does not enable live posting.

Current status:
- X API credentials are not stored in this repository.
- X login is not allowed.
- External API authentication is not allowed.
- Live posting is blocked.
- `dry_run_only` is `true`.
- `auto_post_enabled` remains `false`.
- `manual_approval_required` remains `true`.

Configuration file:
- `data/x_api_config.json`

Allowed now:
- Validate config shape.
- Prepare a payload preview from an approved queue item.
- Show a dry-run preview.

Blocked now:
- X login.
- API authentication.
- Tweet creation.
- Media upload.
- Live publish.
- Live scheduling.

Future production requirements:
- `auto_post_enabled` must be explicitly set to `true` by the operator.
- `manual_approval_required` must remain `true`.
- API connection must be verified outside this preparation step.
- `dry_run_only` must be explicitly set to `false`.
- Queue item status must be `approved`.
- Human confirmation text must exactly match `POST_APPROVED`.
- Image must be ready.
- Final caption must be ready.
- Prohibited content check must be `pass`.

Human approval rule:
- No post can move toward live posting without explicit Daisho approval.
- The required confirmation text is `POST_APPROVED`.

Safety note:
- This preparation step contains no credentials, no login flow, no API call, and no posting function.
