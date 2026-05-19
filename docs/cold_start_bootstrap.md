# Cold Start Bootstrap

## 1. System Identity

- System: Villain Auto Posting OS
- Architecture: review-first architecture
- Operating model: human-supervised system
- Pipeline: repair-governed review pipeline
- Purpose: recover the current Villain OS state with minimal conversational context.

## 2. Core Safety Invariants

- `safe_to_post=false`
- `posting_execution_status=BLOCKED`
- human approval required before any posting path
- no automatic `upload_media`
- no automatic `create_tweet`
- no `tracking_code` generation
- passcodes must come only from active entries in `data/villain_passcodes.json`
- `AGENTS.md` is runtime-local and excluded from normal commits unless explicitly requested.

## 3. Current Active Subsystems

- maintenance separation
- handoff protocol
- review queue
- deleted learning
- novelty engine
- repair execution layer
- repair quality intelligence
- trajectory logging
- ChatGPT bridge
- decision ingestor
- GitHub ChatGPT review bot

## 4. Current Schemas

- `handoff.chatgpt_to_codex.v1`
- `handoff.codex_to_chatgpt.v1`
- `handoff.review_queue.v1`
- `handoff.state.v1`
- `handoff.trajectory.v1`
- `handoff.repair_execution.v1`
- `handoff.repaired_candidates.v1`
- `handoff.context_evidence_requests.v1`
- `handoff.repair_quality_analytics.v1`
- `handoff.chatgpt_bridge_exchange.v1`

## 5. Read-First Files

Read these before making changes:

1. `docs/cold_start_bootstrap.md`
2. `docs/current_villain_os_state.md`
3. `docs/handoff_contract.md`
4. `docs/agent_handoff_protocol.md`
5. `reports/agent_handoff_status.md`
6. `reports/chatgpt_bridge_prompt.md`
7. `reports/chatgpt_github_review_bot.md`
8. `reports/villain_quality_review_summary.md`
9. `data/agent_handoff_state.json`
10. `data/agent_handoff_trajectory.json`
11. `data/villain_quality_review_queue.json`
12. `data/codex_to_chatgpt_handoff.json`
13. `data/chatgpt_to_codex_handoff.json`

## 6. Current Known Risks

- temporal context hallucination
- topic-image mismatch
- deleted-near repetition
- recent media reuse
- repair regression risk
- over-trusting `READY` as post-ready instead of review-ready
- accidental reintroduction of `tracking_code`
- accidental posting from maintenance or bridge workflows

## 7. Current Operational Status

- posting executed: NO
- upload executed: NO
- tweet creation executed: NO
- safe_to_post=false
- posting_execution_status=BLOCKED
- review_board_status=READY
- queue_health_status=BLOCKED
- executable_ready_count=0
- GitHub review bot may update review JSON only; it must not approve posting.

## 8. Next Pending Implementation

- repair regression analytics refinement
- reviewer learning
- repair outcome clustering
- memory compression strategy
- context evidence source-file standard
- refill flow for blocked/expired review boards
- image metadata enrichment for topic-image pairing

## 9. Cold-Start Recovery Procedure

1. Read this bootstrap file.
2. Read `docs/handoff_contract.md`.
3. Read `docs/agent_handoff_protocol.md`.
4. Inspect `reports/agent_handoff_status.md`.
5. Inspect `reports/villain_quality_review_summary.md`.
6. Inspect `reports/chatgpt_bridge_prompt.md` if ChatGPT bridge state matters.
7. Inspect `reports/chatgpt_github_review_bot.md` if GitHub review automation is active.
8. Inspect latest trajectory in `data/agent_handoff_trajectory.json`.
9. Inspect latest state in `data/agent_handoff_state.json`.
10. Validate safety invariants:
   - `safe_to_post=false`
   - `posting_execution_status=BLOCKED`
   - `upload_media` not executed
   - `create_tweet` not executed
   - no `tracking_code` generation
11. Continue from the latest review state.

## 10. Default Commands

Review-only runner:

```bash
python3 scripts/agent_handoff_runner.py
```

ChatGPT bridge prompt builder:

```bash
python3 scripts/chatgpt_bridge_prompt_builder.py
```

ChatGPT decision ingestor:

```bash
python3 scripts/chatgpt_decision_ingestor.py
```

GitHub ChatGPT review bot dry-run:

```bash
python3 scripts/github_chatgpt_review_bot.py --dry-run
```

Handoff-only publication dry-run:

```bash
python3 scripts/handoff_commit_push.py --dry-run
```

Local handoff-only commit:

```bash
python3 scripts/handoff_commit_push.py --commit --message "chore: publish villain handoff state"
```

Handoff-only push after commit:

```bash
python3 scripts/handoff_commit_push.py --commit --push --message "chore: publish villain handoff state"
```

Validation:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/codex_pycache python3 -m py_compile scripts/agent_handoff_runner.py scripts/handoff_repair_runner.py scripts/chatgpt_bridge_prompt_builder.py scripts/chatgpt_decision_ingestor.py scripts/github_chatgpt_review_bot.py scripts/handoff_commit_push.py
jq empty data/*.json status.json
```

## 11. Forbidden During Cold Start

- do not post
- do not upload media
- do not create tweets
- do not run scheduler with `--execute-one`
- do not generate or mutate passcodes
- do not generate `tracking_code`
- do not commit `AGENTS.md` unless explicitly requested

## 12. Recovery Summary

Villain OS is currently a review-first, human-supervised, repair-governed posting system. New sessions should continue from repository state, not conversational memory. The active goal is to improve review, repair, bridge, and learning quality while keeping posting disabled until explicit human approval.
