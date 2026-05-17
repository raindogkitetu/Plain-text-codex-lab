# Villain Novelty Engine

## Purpose
Reduce repeated or near-duplicate Villain posts.

## Current failure patterns
- deleted_text_near_match
- deleted_topic_context_cooldown

## Goals
1. Avoid semantic repetition.
2. Avoid repeating emotional cadence.
3. Avoid repeating recent structure openings.
4. Avoid recently deleted themes.
5. Increase perceived spontaneity.

## Detection ideas
- ngram overlap
- embedding similarity
- opening phrase cooldown
- repeated hashtag rhythm
- repeated sentence cadence
- deleted-post semantic distance

## Soft rules
- Similarity should lower candidate priority.
- Near-match should trigger REVIEW_REQUIRED.
- Deleted-near-match should BLOCK.

## Candidate diversification
Prefer variation across:
- observation
- apparel
- loneliness
- city texture
- late-night mood
- humor
- contradiction
- emotional restraint

## Future direction
Generate candidates from:
- different narrative angle
- different emotional temperature
- different sentence length
- different image category

## Safety boundary
Novelty engine must never:
- auto post
- call upload_media
- call create_tweet
