# Daily Schedule

## 2026-05-09

- 06:00 villain-auto-generator
- 06:30 morning_schedule.sh -> claude-journal / villain / note
- 09:00 minara 市場スクリーニング
- 11:30 schedule-manager-note OnDemand=true
- 14:30 afternoon_schedule.sh -> villain
- 14:30 villain-auto-generator duplicate
- 17:00 minara 市場スクリーニング
- 18:00 evening_schedule.sh -> villain
- 18:00 villain-auto-generator duplicate

## Current Problem

Claude side rarely completes the full daily timetable reliably.

## Test Plan

Phase 1: Codex reads and records schedule only.
Phase 2: Codex monitors whether each task ran.
Phase 3: Codex reports missed tasks.
Phase 4: One-day Codex-only test after monitoring works.
