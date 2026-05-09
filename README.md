# Plain-text-codex-lab

AI-assisted repair and monitoring workspace.

## Current Goals

- Whisper auto monitoring
- Proposal-before-test workflow
- Playwright validation
- AI status sharing
- Automated recovery scripts

## Environment

- macOS
- GitHub connected
- Codex enabled
- Claude assisted workflow

## Rules

1. Verify implementation before proposing changes
2. Run tests before destructive operations
3. Separate assumptions from verified facts
4. Use Playwright for actual UI verification
5. Report execution results clearly

## Planned Components

- status.json
- whisper-monitor.sh
- auto-recovery
- log summarizer
- watchdog scripts

## Status

Project initialized successfully.

## Villain Patrol Replacement Test

Use `data/villain_test_plan.json` to test whether Codex can act as a
read-only replacement operator for the Villain patrol workflow when Claude is
unavailable.

Operational rules:

1. Confirm the Git working tree before editing any DB files.
2. Load the Villain DB files under `data/` and verify JSON structure first.
3. Treat official site, official X, X search, Whitepaper, NFT, Token, and
   Apparel as separate test targets.
4. Record success only when the checked URL, timestamp, evidence, and scope are
   clear.
5. Do not auto-post, call external APIs without approval, connect wallets,
   purchase items, or delete DB records.
6. Append to logs or memory only after confirming the intended entry with the
   operator.

## Villain Posting Operations DB

Use the Villain posting DB files to generate draft-only Villain post ideas from
the flow: Whitepaper philosophy -> today's topic -> Villain-style post.

Supporting file:

- `data/villain_post_rules.json`: source policy, post structure, prohibited
  content, and quality checklist.
- `data/villain_passcodes.json`: public passcode rotation DB.
- `data/villain_post_knowledge.json`: Whitepaper interpretation, Villain voice,
  implicit rules from observed posts, and archetypes.
- `data/villain_post_template.json`: one draft-only posting record template.
- `data/villain_posting_operations.json`: broader idea/review/published queue
  DB from the first posting operations pass.
- `data/villain_sources.json`: official URLs, social links, NFT references,
  existing post examples, and screenshot evidence registry.

Posting rules:

1. Keep auto-posting disabled.
2. Store official URL evidence before moving a post into review.
3. Separate official-confirmed facts, unverified items, and opinion.
4. Do not write investment advice, purchase prompts, wallet actions, or
   unsupported claims.
5. Every draft needs a hook, short lines, an image or poster concept, and the
   final footer: `#着て稼ぐ #villain @0xmavillain {PASSCODE}`.
6. If X, Instagram, TikTok, LINE, or OpenSea pages cannot be read, register the
   URL and mark the content as manual-check required instead of guessing.
7. Show pre-post checks as a checklist:
   `□ 元ネタURL確認`, `□ 画像/ポスター添付`, `□ パスコード確認`.
8. If fact checks are complete and the checklist has no issue, the draft may be
   judged `投稿可能`. Only incomplete fact checks force `完成扱い不可`.
9. After manual posting, append the post URL and first metrics to the published
   record instead of overwriting evidence.
