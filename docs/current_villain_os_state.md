# Current Villain OS State

Last updated: 2026-05-17

## Current Architecture

candidate generation
→ quality gates
→ deleted learning
→ novelty engine
→ image strategy
→ local image selector
→ text-image fit scoring
→ READY / REVIEW_REQUIRED / BLOCKED
→ human review board
→ scheduler final gates
→ optional posting execution

## Current Runtime Flow

03:00 maintenance:
- agent handoff runner
- local image selector
- human review board builder
- review summaries
- cleanup
- NO posting

Posting slots:
- 13:00
- 20:00
- 23:00

## Hard Safety Rules

- tracking_code generation forbidden
- passcode source of truth:
  data/villain_passcodes.json
- max_posts_per_run = 1
- cooldown = 120 minutes
- review required before next post
- deleted learning enforced
- image reuse cooldown enforced
- upload_media not called during maintenance
- create_tweet not called during maintenance

## Quality OS

Hard blockers:
- temporal_context_unverified
- topic_image_pairing_mismatch
- deleted_topic_context_cooldown
- deleted_text_near_match

Soft review:
- ad_like_review_required
- native_tone_review_required
- persona_fit_review_required

## Current Review System

Generated reports:
- villain_ready_candidates.md
- villain_image_recommendations.md
- villain_human_review_board_runtime.md

## Current State

System state:
- stable
- review-first
- human-supervised
- non-autonomous posting

Current safety:
- posting disabled by review gates unless approved
- maintenance separated from posting
- runtime artifacts mostly ignored from git

## Next Priorities

1. text-image fit scoring refinement
2. novelty scoring refinement
3. deleted-learning expansion
4. reviewer history learning
5. human review UI
6. local image ranking improvements
7. scheduler-review board integration refinement

## Important Notes

This OS is now:
- human-review-first
- safety layered
- recovery capable
- git synchronized
- maintenance automated

The system should prioritize:
"natural existence in timeline"
over
"aggressive growth optimization"
