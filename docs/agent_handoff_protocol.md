# Agent Handoff Protocol

This repository uses files as the handoff layer between ChatGPT, Codex, and the user.

## Purpose

ChatGPT and Codex do not need to hold an autonomous hidden conversation. Instead:

- ChatGPT writes policy, product judgment, and review criteria into repo files.
- Codex reads those files, implements local changes, runs safe verification, and writes results back to reports.
- The user sees the final review summary and approves or blocks live execution.

## Handoff Files

### ChatGPT Writes

- `docs/agent_handoff_protocol.md`
  - shared workflow
  - unresolved issues
  - next actions
- `data/chatgpt_to_codex_handoff.json`
  - current strategy brief
  - policy changes requested by ChatGPT
  - acceptance criteria for Codex
- `data/villain_post_quality_os.json`
  - gate definitions
  - blocker names
  - scoring thresholds
  - known failure patterns

### Codex Writes

- `data/codex_to_chatgpt_handoff.json`
  - implementation result
  - validation results
  - unresolved issues
  - safe next action
- `reports/villain_quality_review_summary.md`
  - current candidate quality review
  - blockers
  - warnings
  - why approved or why blocked
  - safe next action
- `reports/agent_handoff_status.md`
  - latest handoff health
  - whether policy, runner, reports, and review queue are aligned
- implementation files under `scripts/`, `data/`, `reports/`, and `launchd/` when requested by the user

## Required Loop

1. Read ChatGPT brief from `data/chatgpt_to_codex_handoff.json`.
2. Read policy from `data/villain_post_quality_os.json`.
3. Read latest candidates from `data/villain_auto_post_pilot.json`.
4. Read previous outcomes from `data/villain_post_outcomes.json`.
5. Run local quality evaluation only.
6. Write `data/villain_quality_review_queue.json`.
7. Write `reports/villain_quality_review_summary.md`.
8. Write Codex result to `data/codex_to_chatgpt_handoff.json`.
9. Write handoff status to `reports/agent_handoff_status.md`.
10. Do not post, upload media, or create tweets.
11. Leave unresolved issues in the handoff files or the quality review report.

## Runner

Use:

```bash
python3 scripts/agent_handoff_runner.py
```

The runner is local only. It does not call X APIs and does not invoke live scheduler execution.

It should:

1. Validate required handoff files exist.
2. Read latest candidates from `data/villain_auto_post_pilot.json`.
2. Run `scripts/post_quality_os.py` logic by importing it, not by posting.
3. Emit `posting_executed=false`, `upload_media_executed=false`, and `tweet_creation_executed=false`.
4. Record unresolved issues and next actions for the next agent pass.

## Quality Review Decision States

- `READY`
  - no hard blockers
  - review score above threshold
  - no unresolved real-world context
- `REVIEW_REQUIRED`
  - no hard blockers, but ad-like/native/persona score needs human read
- `BLOCKED`
  - at least one hard blocker exists
  - candidate must not reach live execution

## Current Known Failure

- tweet_id: `2055938300708626713`
- failure: content/context mismatch
- cause: a real-world claim about `昨日の集会` was posted without current-context evidence
- result: user deleted the post on X
- policy response:
  - temporal reality claims require evidence
  - gathering/event topic near this failure is cooled down
  - the candidate/image/topic pairing is treated as a negative example

## Unresolved Issues

- Define the exact source-file format for context evidence.
- Decide whether a human approval should expire after one slot or one day.
- Add richer image metadata for product/apparel assets so topic-image pairing can be less brittle.
- Build a queue refill step that creates fresh candidates when every current candidate is blocked.
- Decide when Codex may auto-open a PR versus only prepare a local commit.

## Next Actions

- Run `python3 scripts/agent_handoff_runner.py` after ChatGPT updates policy.
- Run `python3 scripts/post_quality_os.py` before any live scheduler execution.
- If the report says `BLOCKED`, do not run the scheduler.
- If the report says `REVIEW_REQUIRED`, ask for human approval.
- If the report says `READY`, live execution may still require scheduler cooldown, passcode, media deduplication, and max-post gates.
