# Villain Auto Maintenance v1

- Generated at JST: `2026-05-22T03:00:04+09:00`
- status: `SUCCESS`
- job_time: `03:00`
- posting executed: `NO`
- media upload executed: `NO`
- tweet creation executed: `NO`

## JSON Sanity

- status: `PASSED`
- checked_count: `58`

## Recent Media History

- cooldown_days: `7`
- entries: `12`

## Agent Handoff

- status: `FAILED`
- command: `python3 scripts/agent_handoff_runner.py`
- returncode: `2`
- posting executed: `NO`
- upload executed: `NO`
- tweet creation executed: `NO`
- reports_updated: `reports/agent_handoff_status.md, reports/villain_quality_review_summary.md`

## Candidate Refill

- status: `SKIPPED`
- reason: `ready_stream_count_sufficient`
- min_ready_stream_candidates: `5`
- ready_count_before: `5`
- ready_count_after: `5`
- added_count: `0`
- added_ids: `none`
- posting executed: `NO`
- upload executed: `NO`
- tweet creation executed: `NO`

## Pilot Refresh

- status: `SUCCESS`
- command: `python3 scripts/auto_post_pilot.py --mode LIMITED_LIVE_EXECUTION`
- returncode: `0`
- posting executed: `NO`
- upload executed: `NO`
- tweet creation executed: `NO`

## Projects Mirror Sync

- status: `SKIPPED`
- reason: `already_in_projects_or_missing_mirror`
- target: ``
- copied_files: `0`
- copied_dirs: `none`
- posting executed: `NO`
- upload executed: `NO`
- tweet creation executed: `NO`

## ChatGPT Bridge Prompt Refresh

- status: `SUCCESS`
- command: `python3 scripts/chatgpt_bridge_prompt_builder.py`
- returncode: `0`
- posting executed: `NO`
- upload executed: `NO`
- tweet creation executed: `NO`

### Bridge Prompt Output

- `bridge_prompt_hash=47af7da285831be821a99534905a03691685dfb5d2e1c61c2efbf6b31b4ca025`
- `wrote reports/chatgpt_bridge_prompt.md`
- `wrote data/chatgpt_bridge_exchange.json`
- `posting_executed=NO`
- `upload_media=NOT_EXECUTED`
- `create_tweet=NOT_EXECUTED`

### Pilot Refresh Output

- `status=LIMITED_LIVE_EXECUTION_READY`
- `mode=LIMITED_LIVE_EXECUTION`
- `pilot_items=1`
- `live_posting=NOT_EXECUTED`
- `x_api_write=NOT_USED`
- `upload_media=NOT_EXECUTED`
- `create_tweet=NOT_EXECUTED`
- `wrote data/villain_auto_post_pilot.json`
- `wrote reports/villain_auto_post_pilot.md`

### Handoff Errors

- `/Library/Developer/CommandLineTools/usr/bin/python3: can't open file '/Users/raindog/Projects/villain-auto-posting/scripts/agent_handoff_runner.py': [Errno 2] No such file or directory`
