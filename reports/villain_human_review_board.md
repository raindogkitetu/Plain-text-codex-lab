# Villain Human Review Board

## Purpose
Provide one place for human review before any post execution.

## Review sections

### READY candidates
Candidates that passed Quality OS and image selector.

### REVIEW_REQUIRED candidates
Candidates that are not blocked, but need human judgment.

### BLOCKED candidates
Shown only as summary counts, not as posting options.

## Required fields
- candidate_id
- execution_id
- passcode
- text
- image path
- image fit score
- quality status
- image status
- warnings
- blockers
- suggested action

## Human decision fields
- keep: true | false | pending
- approve_to_post: true | false
- reason
- notes

## Safety rules
- Board must never post.
- Board must never call upload_media.
- Board must never call create_tweet.
- approve_to_post only changes review state.
- scheduler/adapter still enforce final gates.

## Future implementation
Generate this board from:
- reports/villain_ready_candidates.md
- reports/villain_image_recommendations.md
- data/villain_quality_review_queue.json
- data/villain_post_outcomes.json
