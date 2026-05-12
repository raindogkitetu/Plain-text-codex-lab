# Villain E2E Dry Run

- Generated at: `2026-05-12T13:31:48+00:00`
- status: `DRY_RUN_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- queue mutation scope: `DRY_RUN_APPROVE_AND_IMAGE_SELECTION_ONLY`

## Selected Candidate

- candidate_id: `vln-gen-20260512-001`
- category: `ABOUT_WORDING`
- quality_score: `100`
- villain_score: `100`
- risk: `low`
- already_posted: `false`
- selection_reason: `quality_score >= 80, risk != high, already_posted != true`

```text
ABOUTの言葉、
まだ残ってる。

毎日着ろって、
やっぱり普通じゃない。

でも今日はそこがいい。

#着て稼ぐ #villain @0xmavillain R2J9T
```

## Queue State Transition

- approve_flow_result: `APPROVED_FOR_QUEUE_ONLY`
- queue_id: `vln-queue-vln-gen-20260512-001`
- transition_1: `generated_candidate -> queue`
- queue_status_after_approve: `waiting_for_image`
- transition_2: `waiting_for_image -> ready_for_human_post_review`
- queue_status_after_image_selection: `ready_for_human_post_review`
- posting_execution_allowed: `false`

## Image Selection

- image_selected: `true`
- selected_image: `/Users/raindog/Documents/New project/villain_post_images/villain_observer_001.png`
- selected_image_path: `/Users/raindog/Documents/New project/villain_post_images/villain_observer_001.png`
- selection_reason: `mode_match:OBSERVER_MODE, about_wording_observer_fit, villain_filename_signal`
- next_status: `ready_for_human_post_review`

## Final Review

- final_review_result: `APPROVE_TO_POST`
- human_review_ready: `true`
- block_reason: `none`
- duplicate_signal: `false`
- image_selected: `true`
- quality_score: `100`
- risk: `low`

## Safety Confirmation

- live投稿: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- .env読み込み: `NOT_USED`
- 実投稿処理: `NOT_EXECUTED`
