# Next Session

## Current State

- latest commit: `c0b039a`
- preflight_status: `NOT_READY`
- final safety: `BLOCKED`
- live posting: `DISABLED`
- auto_post_enabled: `false`
- dry_run_only: `true`
- api_connected: `false`
- manual approval required: `true`

## Next Candidates

- queue UX
- caption quality
- image_ready flow
- x api setup manual
- .env.example

## X API Environment Template

- `.env.example` exists.
- It contains X API environment variable names only.
- Values must stay empty until a future approved setup phase.
- Do not create `.env` in this repository.

## X API Setup Manual

- `docs/x_api_setup_manual.md` exists.
- It documents the future connection order.
- Current phase remains NOT_READY / DISABLED / BLOCKED.
- Do not connect X API or create `.env` yet.

## Guardrails

- No live posting.
- No X login.
- No API connection.
- No credentials in repository.
