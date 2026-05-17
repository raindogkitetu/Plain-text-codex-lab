# Villain Context Mismatch Gate v1

- status: `implemented`
- posting executed: `NO`
- upload executed: `NO`
- tweet creation executed: `NO`

## Trigger

- tweet_id: `2055938300708626713`
- url: `https://x.com/raindog_kitetu/status/2055938300708626713`
- human_review.keep: `false`
- deletion: user deleted on X
- reason: `content/context mismatch`
- felt_native: `false`
- felt_ad_like: `true`

## Failure

The post used a real-world time/event claim:

- `昨日`
- `集会`

The system treated a previously strong `community_info` pattern as reusable, but the claim was not grounded in a current event source or explicit human approval. This made the post factually and socially misaligned even though the image and category looked strong on paper.

## New Hard Gates

1. `context_evidence_missing`
   - Blocks text containing reality-context terms such as `昨日`, `今日`, `明日`, `集会`, `現場`, `イベント`, `発表` unless a source file or explicit context approval exists.

2. `topic_image_pairing_mismatch`
   - Blocks when text topic and image metadata do not match.
   - Example: a gathering/community claim paired with a generic apparel/culture image.

3. Deleted-learning blockers
   - `deleted_candidate_blacklist`
   - `deleted_image_cooldown`
   - `deleted_prompt_family_cooldown`
   - `deleted_text_near_match`
   - `deleted_topic_context_cooldown`

## Current Block Result

`vln-gen-20260516-001` is now blocked by:

- `context_evidence_missing`
- `deleted_candidate_blacklist`
- `deleted_text_near_match`
- `deleted_topic_context_cooldown`
- media reuse blockers

Nearby gathering-topic candidates are also blocked when they inherit the deleted post's topic context without new evidence.

## Learning Rule

Strong community language is not enough. Any post that implies a real event or time sequence must be grounded by a current context source or human approval before it can reach live execution.
