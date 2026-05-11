# X API Setup Manual

## Current Status

- preflight_status: `NOT_READY`
- live posting: `DISABLED`
- final safety: `BLOCKED`
- auto_post_enabled: `false`
- dry_run_only: `true`
- api_connected: `false`
- manual_approval_required: `true`

This manual is for a future setup phase only. Do not connect X API yet.

## `.env.example`

`.env.example` defines the environment variable names that may be needed later.
It intentionally contains no values.

Required names:

```env
X_API_KEY=
X_API_SECRET=
X_ACCESS_TOKEN=
X_ACCESS_TOKEN_SECRET=
X_BEARER_TOKEN=
```

Rules:

- Do not commit real credentials.
- Do not put token, secret, or API key values into repository files.
- Do not create `.env` until a future approved setup phase.
- Keep `.env` local only if it is created later.

## Future Connection Order

1. Create X developer account.
2. Obtain credentials.
3. Create local `.env`.
4. Run preflight.
5. Run final safety check.
6. Run dry-run confirmation.
7. Complete manual approval.
8. Enable API connection.
9. Still keep posting `BLOCKED` until explicit unlock.

## Safety Checks Before Any Connection

- Confirm `auto_post_enabled` is still `false`.
- Confirm `dry_run_only` is still `true`.
- Confirm `manual_approval_required` is still `true`.
- Confirm `final safety` is still `BLOCKED`.
- Confirm no live post function exists.
- Confirm no upload media function exists.
- Confirm no create tweet function exists.
- Confirm `.env` is not committed.
- Confirm `.env.example` contains names only.

## Connection Preflight Checklist

- [ ] X developer account exists.
- [ ] Credentials obtained outside the repository.
- [ ] Local `.env` created only after explicit approval.
- [ ] `python3 scripts/x_api_preflight_check.py` has been run.
- [ ] `python3 scripts/final_villain_safety_check.py` has been run.
- [ ] `python3 scripts/build_villain_dashboard.py` shows `live posting: DISABLED`.
- [ ] Queue item is approved.
- [ ] Image is ready.
- [ ] Caption is final.
- [ ] Human confirmation text is exactly `POST_APPROVED`.
- [ ] Explicit unlock phase has been approved.

## Forbidden In Current Phase

- X login.
- API connection.
- Adding token, secret, or API key values.
- Creating `.env`.
- Setting `auto_post_enabled` to `true`.
- Setting `dry_run_only` to `false`.
- Live posting.
