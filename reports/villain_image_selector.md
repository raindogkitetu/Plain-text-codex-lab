# Villain Image Selector

## Purpose
Select images that naturally support READY text.

## Problem
READY candidates can still point to weak or risky images.

## Rules
1. Do not use images from keep=false or deleted posts.
2. Do not use event/meeting images without context evidence.
3. Prefer neutral apparel, street, lifestyle, and observation images.
4. If image metadata is thin, mark REVIEW_REQUIRED.
5. If no fitting image exists, recommend text-only fallback review.

## Inputs
- READY candidate text
- image path
- image metadata
- prompt_family
- previous outcome history
- deleted learning cooldown
- topic-image fit score

## Outputs
- selected_image
- image_status: READY | REVIEW_REQUIRED | BLOCKED
- image_blockers
- image_warnings
- recommendation

## Next implementation
Create a local image selector that ranks images for each READY candidate without posting.
