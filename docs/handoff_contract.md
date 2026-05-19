# Handoff Contract

This contract stabilizes the Codex ↔ ChatGPT review exchange for the Villain Auto Posting OS.

## Scope

- This interface is for review, quality judgment, repair planning, and GitHub-visible handoff only.
- It must not execute posting, upload media, create tweets, or generate tracking codes.
- `safe_to_post` defaults to `false` in every handoff cycle.
- Passcodes must come only from active entries in `data/villain_passcodes.json`.
- `AGENTS.md` is runtime-local and excluded from normal handoff commits unless explicitly requested.

## Transport

The canonical exchange surface is repository files:

- ChatGPT inbox: `data/chatgpt_to_codex_handoff.json`
- Codex outbox: `data/codex_to_chatgpt_handoff.json`
- Shared state: `data/agent_handoff_state.json`
- Trajectory log: `data/agent_handoff_trajectory.json`
- Repair execution log: `data/villain_repair_execution.json`
- Repaired review-only candidates: `data/villain_repaired_candidates.json`
- Context evidence requests: `data/villain_context_evidence_requests.json`
- Repair quality analytics: `data/villain_repair_quality_analytics.json`
- ChatGPT bridge exchange: `data/chatgpt_bridge_exchange.json`
- Review queue: `data/villain_quality_review_queue.json`
- Human-readable reports:
  - `reports/agent_handoff_status.md`
  - `reports/villain_quality_review_summary.md`
  - `reports/chatgpt_bridge_prompt.md`

For ChatGPT GitHub connector use, Codex must commit and push only the handoff/review/report files that are safe to publish. Local-only media, logs, secrets, `.env`, `.DS_Store`, `AGENTS.md`, `villain_post_images/`, `assets/`, and `space_recordings/` remain outside normal handoff commits.

## Schema Versions

Every handoff JSON must include `schema_version`.

- `data/chatgpt_to_codex_handoff.json`: `handoff.chatgpt_to_codex.v1`
- `data/codex_to_chatgpt_handoff.json`: `handoff.codex_to_chatgpt.v1`
- `data/agent_handoff_state.json`: `handoff.state.v1`
- `data/agent_handoff_trajectory.json`: `handoff.trajectory.v1`
- `data/villain_quality_review_queue.json`: `handoff.review_queue.v1`
- `data/villain_repair_execution.json`: `handoff.repair_execution.v1`
- `data/villain_repaired_candidates.json`: `handoff.repaired_candidates.v1`
- `data/villain_context_evidence_requests.json`: `handoff.context_evidence_requests.v1`
- `data/villain_repair_quality_analytics.json`: `handoff.repair_quality_analytics.v1`
- `data/chatgpt_bridge_exchange.json`: `handoff.chatgpt_bridge_exchange.v1`

JSON serialization must be deterministic. The runner writes generated handoff JSON with stable key ordering.

## Review State Machine

Allowed states:

- `INBOX_RECEIVED`
- `QUALITY_REVIEW_BUILT`
- `READY_FOR_CHATGPT_REVIEW`
- `CHATGPT_DECISION_CONSUMED`
- `READY_FOR_HUMAN_REVIEW`
- `POSTING_BLOCKED`
- `CONTRACT_BLOCKED`

Disabled posting terminal states:

- `POSTING_READY`
- `POSTING_EXECUTED`

`READY` means eligible for review. It does not mean eligible for posting.

## Status Separation

- `queue_health_status`: `BLOCKED` if any candidate remains blocked.
- `review_board_status`: `READY` if review items exist.
- `posting_execution_status`: `BLOCKED` unless an item is explicitly human-approved.
- `executable_ready_count`: count of READY items with explicit human approval.
- `safe_to_review`: true when review items exist.
- `safe_to_post`: always false by default.

## Repair Actions

Each review item may include `repair_action`.

Allowed repair action types:

- `none`
- `context_evidence_required`
- `image_replacement_required`
- `human_review_required`
- `archive_or_drop`

Repair actions are advisory for review/refill. They must not unlock posting.

## Repair Execution

The repair execution layer consumes `repair_actions` and writes review-only outputs.

Supported behavior:

- `archive_or_drop`: marks the candidate as not worth automatic repair.
- `image_replacement_required`: creates a review-only repaired candidate with a safer replacement image.
- `context_evidence_required`: creates a context evidence request and may strip temporal/event wording for a repaired review candidate.
- temporal claim stripping removes real-event phrases such as `昨日の集会` from repaired review candidates.

Repair execution invariants:

- repaired candidates are not human-approved
- repaired candidates have `safe_to_post=false`
- repaired candidates do not enter live posting automatically
- evidence requests ask what the post is grounded in before review can continue

## Repair Quality Intelligence

The repair quality layer evaluates repaired candidates after repair execution, still for review only.

It records:

- `repair_quality_score`: heuristic quality score after repair, based on Quality OS review output.
- `repair_regression_risk`: `low`, `medium`, or `high` risk that repair reintroduced blockers or weak review signals.
- `repair_confidence`: confidence that the repair is worth human review, never approval for posting.
- `reviewer_feedback_linkage`: pointer back to the original candidate and pending human feedback.
- `repaired_vs_original_diff`: concise text and image change summary.
- `repair_outcome_analytics`: aggregate status/action counts for the current repair cycle.
- `recurring_repair_failure_clusters`: repeated repair failure patterns that should influence future refill/repair decisions.

Repair quality intelligence must preserve these invariants:

- repaired candidates remain `human_approved_for_posting=false`
- repaired candidates remain `safe_to_post=false`
- regression analysis may downgrade review confidence but must never upgrade to posting approval
- reviewer feedback is linked for later learning, not automatic execution

## ChatGPT Bridge

The bridge removes manual file gathering from the user.

Codex responsibilities:

- build `reports/chatgpt_bridge_prompt.md` from the latest outbox, state, review queue, and reports
- write `data/chatgpt_bridge_exchange.json` with the prompt hash, input files, and expected response schema
- validate the ChatGPT decision after it is pasted or synced into `data/chatgpt_to_codex_handoff.json`
- append bridge ingestion events to `data/agent_handoff_trajectory.json`

ChatGPT responsibilities:

- read the bridge prompt
- return only decision JSON
- keep `safe_to_post=false`
- keep `posting_execution_status=BLOCKED`
- request review, repair, refill, or blocking decisions only

Bridge invariants:

- the bridge does not call upload or tweet creation code
- the bridge does not run scheduler execution
- the bridge does not generate tracking codes
- `safe_to_post=true` is rejected unless a separate explicit human approval artifact exists
- the human reviews the final decision summary, not the raw file gathering

### Image Review Bridge

Codex must include an image review packet in `reports/chatgpt_bridge_prompt.md` whenever generated/shop-derived images are available.

Image review packet fields:

- `image_id`
- `image_path`
- `image_type`
- `prompt_family`
- `source_products`
- `fit_notes`
- `recommended_text_angle`
- `currently_in_pilot_plan`
- `chatgpt_review_focus`

ChatGPT decision fields for image review:

- `image_review_decisions`
- `candidate_image_pairing`

Allowed image decisions:

- `USE`: suitable for review-board candidates.
- `REJECT`: do not use; likely nonexistent product, ad-like, mismatched, or otherwise unsafe for natural posting.
- `REPAIR`: usable direction, but needs regeneration or image replacement.
- `HOLD`: keep as stock but do not attach to scheduled candidates yet.

Allowed candidate-image pairing decisions:

- `PAIR_OK_FOR_REVIEW`
- `IMAGE_REPLACEMENT_REQUIRED`
- `TEXT_REWRITE_REQUIRED`
- `HOLD`

Image bridge invariants:

- `USE` means review-ready only; it does not approve posting.
- `REJECT` must remove the image from automatic candidate pairing or mark it as blocked.
- generated images must not invent apparel or goods that do not exist in the official shop references.
- Codex may generate and stock images, but ChatGPT should judge naturalness, product fidelity, ad-likeness, and text-image fit.
- posting/upload/tweet creation remain disabled in bridge workflows.

## Handoff-Only Commit/Push Mode

`scripts/handoff_commit_push.py` provides a whitelist-only Git publication path for supervisory state.

Default behavior:

- dry-run unless `--commit` is explicitly passed
- never push unless `--push` is explicitly passed
- validate invariants before staging
- stage only whitelisted handoff/review/report files
- block if forbidden or non-whitelisted files are already staged

Forbidden from normal handoff publication:

- `AGENTS.md`
- `.DS_Store`
- `assets/`
- `logs/`
- `space_recordings/`
- `villain_post_images/`
- `data/villain_passcodes.json` unless an explicit passcode-specific review path is used

Commit/push invariants:

- `safe_to_post=false`
- `posting_execution_status=BLOCKED`
- `posting_executed=false`
- `upload_media_executed=false`
- `tweet_creation_executed=false`
- no `tracking_code` key in handoff JSON
- no tracking-code generation markers in handoff scripts

## Trajectory Log

`data/agent_handoff_trajectory.json` records a compact append-only scaffold of handoff cycles:

- timestamp
- inbox/outbox schema versions
- ChatGPT decision
- review state
- separated statuses
- repair action count
- repaired candidate count
- repair status frequency
- posting/upload/tweet flags, always false for this workflow

This is not analytics for X performance. It is only the audit trail of Codex ↔ ChatGPT review exchange.

## Safety Invariants

- `posting_executed=false`
- `upload_media_executed=false`
- `tweet_creation_executed=false`
- `safe_to_post=false`
- no tracking code generation
- no X write adapter execution
- no scheduler `--execute-one`
