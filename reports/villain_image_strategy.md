# Villain Image Strategy

## Purpose
READY text must not reuse weak or mismatched image context.

## Current issue
READY candidates exist, but some still point to risky images such as:
- villain_post_images/20260514集会.png

## Rules
1. Do not use images tied to deleted/keep=false posts.
2. Do not use event-like images unless the text has verified context evidence.
3. If image metadata is thin, mark as REVIEW_REQUIRED.
4. Prefer neutral lifestyle / apparel / street observation images for abstract text.
5. Avoid “集会 / 現場 / イベント” visual context unless explicitly grounded.

## Recommended next step
For vln-gen-20260516-002:
- keep text
- replace image
- do not use 20260514集会.png
- choose neutral apparel/street image
- if no image fits, mark text-only as fallback review option
