# Villain Local Image Ranking

## Purpose
Rank local images against READY candidates before any posting flow.

## Goal
Choose images that naturally fit the text while avoiding risky context.

## Inputs
- READY candidate text
- image path
- image metadata
- deleted learning history
- previous post outcomes
- topic-image fit score
- novelty score

## Ranking factors
1. topic-image alignment
2. emotional consistency
3. apparel/street relevance
4. deleted-post distance
5. recent image reuse cooldown
6. metadata confidence
7. visual neutrality

## Penalties
- deleted image reuse
- event/meeting imagery
- mismatch with abstract text
- low metadata confidence
- repeated image cadence

## Outputs
- ranked image list
- selected image
- fit score
- blocker list
- warning list
- fallback recommendation

## Future implementation
Create a local ranking runner that:
- scans villain_post_images/
- scores candidate/image pairs
- outputs READY image recommendations
- never posts
- never calls upload_media
- never calls create_tweet
