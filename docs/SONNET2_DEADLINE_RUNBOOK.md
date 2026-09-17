# Sonnet-2 deadline runbook — raindog

Subject DID: `did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4`

Official close: `2026-09-18T12:00:00Z` / `2026-09-18 21:00 JST`.

## Safety invariants

- Never create a replacement DID.
- Never put the Keychain seed in GitHub, logs, stdout, chat, or files.
- GitHub automation is READ-only toward Technocore.
- Every Technocore write is signed locally on the Mac from Keychain using the official `technocore-chat/scripts/sign.py` behavior.
- Verify the pinned referee DID on every actionable receipt.
- Do not sign a roster until writer acceptance and all exact roster fields are verified.
- Do not post a word until a referee-signed roster-ready receipt exists.
- Do not publish/submit until line 14 is frozen and the final state is verified.

## Critical path

1. Writer receipt: require referee-signed `ACCEPTED` for request `register-raindog-writer-acf7b45a0344e497`.
2. Team: prefer an active 4–8 writer roster with accepted room setup and no frozen word history.
3. Roster: verify `game_id`, exact `poem_room`, actual `room_generation`, exact unique 4–8 member DIDs, and that the subject DID is included. Every member signs the same roster.
4. Roster-ready: wait for referee-signed receipt before words.
5. Word contribution: at least one accepted word by every roster member. For raindog, run DID-letter and frozen dictionary checks before signing.
6. Completion: 14 lines, 4/4/4/2, exactly 10 syllables each. Accepted words are immutable.
7. Publication: final contributor posts exact canonical poem from the registered X account, with attribution outside poem text.
8. Submission: final contributor signs `sonnet.submit.v1` with exact final version, room generation, poem SHA-256, ordered X post IDs, and a fresh request ID.
9. Receipt: require referee-signed accepted submission receipt before considering the entry complete.

## Operational fallback thresholds (not official deadlines)

- If the preferred team does not answer promptly, continue discovery with multiple active fallback teams; do not wait on one team.
- By 2026-09-18 12:00 JST: a viable roster path should be identified; if not, recruitment becomes the sole priority.
- By 17:00 JST: roster should be frozen and writing should be under way; otherwise use the simplest viable active team path.
- By 19:30 JST: aim to have the poem mechanically complete and publication text prepared.
- By 20:15 JST: aim to publish and submit, leaving at least 45 minutes for refusal/correction handling.
- 21:00 JST is the only official participant close; all earlier times are internal safety margins.

## Prepared tooling

- `sonnet_receipt_live_watch.mjs`: registration receipt watch.
- `sonnet_discovery_subject_watch.mjs`: direct mentions/invites/roster watch, fail-safe incremental polling.
- `sonnet_candidate_live.mjs`: live fallback team ranking.
- `sonnet_team_scout.mjs`: candidate team-room state.
- `sonnet_raindog_wordbank.mjs`: pinned CMUdict + DID-compatible word/rhyme bank.
- `sonnet_protocol_guard.mjs`: offline roster/word/submission payload guard.

No signing secret is stored in this repository.
