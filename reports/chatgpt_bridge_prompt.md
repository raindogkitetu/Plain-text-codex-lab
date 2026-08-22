# ChatGPT Bridge Prompt

You are ChatGPT reviewing the Villain Auto Posting OS handoff from Codex.
Return only JSON matching the expected response schema. Do not ask Codex to post.

## Safety Invariants

- safe_to_post=false
- posting_execution_status=BLOCKED
- no upload_media
- no create_tweet
- no tracking_code generation
- human approval required before any posting path
- passcodes must come only from active values in data/villain_passcodes.json

## Current Summary

- generated_at_jst: `2026-08-23T02:27:14+09:00`
- bridge_prompt_hash: `71235920bee0a922b1a4d532c1ecffd1857faee60d16ec35d8b20a325f0c5b1c`
- codex_outbox_status: `READY_FOR_CHATGPT_REVIEW`
- review_state: `CHATGPT_DECISION_CONSUMED`
- queue_health_status: `BLOCKED`
- review_board_status: `READY`
- posting_execution_status: `BLOCKED`
- safe_to_review: `true`
- safe_to_post: `false`
- state_last_run: `{'blocked_candidate_count': 6, 'blocked_reason_frequency': {'deleted_text_near_match': 3, 'deleted_topic_context_cooldown': 6, 'temporal_context_unverified': 3, 'topic_image_pairing_mismatch': 3}, 'executable_ready_count': 0, 'posting_execution_status': 'BLOCKED', 'quality_status': 'BLOCKED', 'queue_health_status': 'BLOCKED', 'ready_candidate_count': 3, 'review_board_status': 'READY', 'review_items': 9, 'review_required_candidate_count': 0, 'review_state': 'CHATGPT_DECISION_CONSUMED', 'safe_to_post': False, 'safe_to_review': True, 'status': 'READY_FOR_CHATGPT_REVIEW', 'unresolved_issues': ['context_evidence source fileの標準形式を決める必要がある', '候補が全部BLOCKEDのときのrefill処理は未実装', '画像metadataが薄い候補のtopic-image判定をどう補強するか', 'READYだがhuman_approved_for_posting=falseの候補をreview inboxとして別表示できるか', 'Deleted learning cooldown is active for recent failed posts.']}`

## Task For ChatGPT

1. Decide whether current candidates should stay in review, be repaired, be refilled, or remain blocked.
2. Keep READY as review-ready only, not post-ready.
3. Keep `safe_to_post=false` and `posting_execution_status=BLOCKED` unless a separate explicit human approval artifact exists.
4. Review generated/shop-derived images before they become recurring scheduled candidates.
5. Reject images that look like non-existent apparel/goods, pasted product cutouts, ads, or mismatched visuals.
6. Return only decision JSON. No prose outside JSON.

## Expected Response Schema

``` json
{
  "schema_version": "handoff.chatgpt_decision.v1",
  "safe_to_post": false,
  "posting_execution_status": "BLOCKED",
  "chatgpt_review_decision": {
    "decision": "REVIEW_READY_NOT_POST_READY | BLOCKED | REQUEST_REPAIR | REQUEST_REFILL",
    "approved_for_review": [],
    "not_approved_for_posting": [],
    "must_remain_blocked": [],
    "repair_candidates": [],
    "image_replacement_required": [],
    "context_evidence_required": [],
    "archive_or_drop_candidates": [],
    "refill_required": false,
    "next_codex_actions": [],
    "policy_clarification": [],
    "image_review_decisions": [
      {
        "image_id": "",
        "image_path": "",
        "decision": "USE | REJECT | REPAIR | HOLD",
        "reason": "",
        "fit_for_candidate_ids": [],
        "reject_if": [],
        "repair_request": ""
      }
    ],
    "candidate_image_pairing": [
      {
        "candidate_id": "",
        "image_path": "",
        "decision": "PAIR_OK_FOR_REVIEW | IMAGE_REPLACEMENT_REQUIRED | TEXT_REWRITE_REQUIRED | HOLD",
        "reason": ""
      }
    ]
  }
}
```

## Image Review Packet

``` json
[
  {
    "image_id": "wearable_stock_001_cap_afterhours",
    "image_path": "villain_post_images/wearable_stock/wearable_stock_001_cap_afterhours.png",
    "image_type": "wearable_poster",
    "prompt_family": "shop_wearable_cap_afterhours",
    "source_products": [
      "32_cap.png"
    ],
    "fit_notes": "Actual shop cap composited onto a quiet human silhouette. No invented cap shape.",
    "recommended_text_angle": "小物が空気を先に運ぶ / 服より軽いのに残る",
    "currently_in_pilot_plan": false,
    "chatgpt_review_focus": [
      "実在しない商品に見えないか",
      "広告臭くないか",
      "人物/生活痕として自然か",
      "投稿文と噛み合うか",
      "コミュニティ素材として拾いやすいか"
    ]
  },
  {
    "image_id": "wearable_stock_002_bucket_street",
    "image_path": "villain_post_images/wearable_stock/wearable_stock_002_bucket_street.png",
    "image_type": "wearable_poster",
    "prompt_family": "shop_wearable_bucket_street",
    "source_products": [
      "31_bucket_hat.png"
    ],
    "fit_notes": "Actual shop bucket hat composited onto a street silhouette.",
    "recommended_text_angle": "置いてある時より、人が着た後の方が強い",
    "currently_in_pilot_plan": false,
    "chatgpt_review_focus": [
      "実在しない商品に見えないか",
      "広告臭くないか",
      "人物/生活痕として自然か",
      "投稿文と噛み合うか",
      "コミュニティ素材として拾いやすいか"
    ]
  },
  {
    "image_id": "wearable_stock_003_bag_workdesk",
    "image_path": "villain_post_images/wearable_stock/wearable_stock_003_bag_workdesk.png",
    "image_type": "lifestyle_residue",
    "prompt_family": "shop_goods_bag_workdesk",
    "source_products": [
      "29_haul_bag.jpg"
    ],
    "fit_notes": "Actual haul bag product image placed in a workdesk residue scene.",
    "recommended_text_angle": "持ち物が先にその人の空気を作る",
    "currently_in_pilot_plan": false,
    "chatgpt_review_focus": [
      "実在しない商品に見えないか",
      "広告臭くないか",
      "人物/生活痕として自然か",
      "投稿文と噛み合うか",
      "コミュニティ素材として拾いやすいか"
    ]
  },
  {
    "image_id": "wearable_stock_004_cap_mirror_crop",
    "image_path": "villain_post_images/wearable_stock/wearable_stock_004_cap_mirror_crop.png",
    "image_type": "wearable_lifestyle",
    "prompt_family": "shop_wearable_cap_mirror_crop",
    "source_products": [
      "32_cap.png"
    ],
    "fit_notes": "Actual shop cap composited into a mirror-crop silhouette. Face hidden, no invented product.",
    "recommended_text_angle": "小物の方が先に空気を運ぶ",
    "currently_in_pilot_plan": false,
    "chatgpt_review_focus": [
      "実在しない商品に見えないか",
      "広告臭くないか",
      "人物/生活痕として自然か",
      "投稿文と噛み合うか",
      "コミュニティ素材として拾いやすいか"
    ]
  },
  {
    "image_id": "wearable_stock_005_bucket_backview_after",
    "image_path": "villain_post_images/wearable_stock/wearable_stock_005_bucket_backview_after.png",
    "image_type": "wearable_lifestyle",
    "prompt_family": "shop_wearable_bucket_backview_after",
    "source_products": [
      "31_bucket_hat.png"
    ],
    "fit_notes": "Actual shop bucket hat used in a back-view after-scene. No temporal/event claim.",
    "recommended_text_angle": "人が着た後にだけ残る空気",
    "currently_in_pilot_plan": false,
    "chatgpt_review_focus": [
      "実在しない商品に見えないか",
      "広告臭くないか",
      "人物/生活痕として自然か",
      "投稿文と噛み合うか",
      "コミュニティ素材として拾いやすいか"
    ]
  },
  {
    "image_id": "wearable_stock_006_thermos_desk_residue",
    "image_path": "villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
    "image_type": "lifestyle_residue",
    "prompt_family": "shop_goods_thermos_desk_residue",
    "source_products": [
      "33_thermos_with_villain.png"
    ],
    "fit_notes": "Actual thermos product image placed into a desk residue scene.",
    "recommended_text_angle": "グッズは使われた瞬間に文化っぽくなる",
    "currently_in_pilot_plan": false,
    "chatgpt_review_focus": [
      "実在しない商品に見えないか",
      "広告臭くないか",
      "人物/生活痕として自然か",
      "投稿文と噛み合うか",
      "コミュニティ素材として拾いやすいか"
    ]
  },
  {
    "image_id": "wearable_stock_007_cap_mirror_person",
    "image_path": "villain_post_images/wearable_stock/wearable_stock_007_cap_mirror_person.png",
    "image_type": "wearable_lifestyle_photo",
    "prompt_family": "shop_wearable_cap_mirror_person",
    "source_products": [
      "32_cap.png"
    ],
    "fit_notes": "Generated lifestyle photo of an anonymous person wearing a black cap shaped like the official shop cap. Face hidden, natural mirror context.",
    "recommended_text_angle": "小物の方が先に空気を運ぶ",
    "currently_in_pilot_plan": false,
    "chatgpt_review_focus": [
      "実在しない商品に見えないか",
      "広告臭くないか",
      "人物/生活痕として自然か",
      "投稿文と噛み合うか",
      "コミュニティ素材として拾いやすいか"
    ]
  },
  {
    "image_id": "wearable_stock_008_bucket_mirror_person",
    "image_path": "villain_post_images/wearable_stock/wearable_stock_008_bucket_mirror_person.png",
    "image_type": "wearable_lifestyle_photo",
    "prompt_family": "shop_wearable_bucket_mirror_person",
    "source_products": [
      "31_bucket_hat.png"
    ],
    "fit_notes": "Anonymous person naturally wearing black $villain bucket hat in entryway mirror.",
    "recommended_text_angle": "生活痕の中で$villainが自然に残る",
    "currently_in_pilot_plan": false,
    "chatgpt_review_focus": [
      "実在しない商品に見えないか",
      "広告臭くないか",
      "人物/生活痕として自然か",
      "投稿文と噛み合うか",
      "コミュニティ素材として拾いやすいか"
    ]
  },
  {
    "image_id": "wearable_stock_009_cap_rain_street",
    "image_path": "villain_post_images/wearable_stock/wearable_stock_009_cap_rain_street.png",
    "image_type": "wearable_lifestyle_photo",
    "prompt_family": "shop_wearable_cap_rain_street",
    "source_products": [
      "32_cap.png"
    ],
    "fit_notes": "Anonymous person naturally wearing black $villain cap on wet night street.",
    "recommended_text_angle": "生活痕の中で$villainが自然に残る",
    "currently_in_pilot_plan": false,
    "chatgpt_review_focus": [
      "実在しない商品に見えないか",
      "広告臭くないか",
      "人物/生活痕として自然か",
      "投稿文と噛み合うか",
      "コミュニティ素材として拾いやすいか"
    ]
  },
  {
    "image_id": "wearable_stock_010_thermos_workdesk",
    "image_path": "villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
    "image_type": "lifestyle_residue_photo",
    "prompt_family": "shop_goods_thermos_workdesk",
    "source_products": [
      "33_thermos_with_villain.png"
    ],
    "fit_notes": "Black $villain thermos in a lived-in workdesk scene.",
    "recommended_text_angle": "生活痕の中で$villainが自然に残る",
    "currently_in_pilot_plan": false,
    "chatgpt_review_focus": [
      "実在しない商品に見えないか",
      "広告臭くないか",
      "人物/生活痕として自然か",
      "投稿文と噛み合うか",
      "コミュニティ素材として拾いやすいか"
    ]
  },
  {
    "image_id": "wearable_stock_011_bag_entryway",
    "image_path": "villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
    "image_type": "lifestyle_residue_photo",
    "prompt_family": "shop_goods_bag_entryway",
    "source_products": [
      "29_haul_bag.jpg"
    ],
    "fit_notes": "Black $villain haul bag used in entryway after daily use.",
    "recommended_text_angle": "生活痕の中で$villainが自然に残る",
    "currently_in_pilot_plan": false,
    "chatgpt_review_focus": [
      "実在しない商品に見えないか",
      "広告臭くないか",
      "人物/生活痕として自然か",
      "投稿文と噛み合うか",
      "コミュニティ素材として拾いやすいか"
    ]
  },
  {
    "image_id": "wearable_stock_012_hoodie_mirror_person",
    "image_path": "villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png",
    "image_type": "wearable_lifestyle_photo",
    "prompt_family": "shop_wearable_hoodie_mirror_person",
    "source_products": [
      "29_elite_zip_hoodie.jpg"
    ],
    "fit_notes": "Anonymous person naturally wearing black $villain hoodie in mirror.",
    "recommended_text_angle": "生活痕の中で$villainが自然に残る",
    "currently_in_pilot_plan": false,
    "chatgpt_review_focus": [
      "実在しない商品に見えないか",
      "広告臭くないか",
      "人物/生活痕として自然か",
      "投稿文と噛み合うか",
      "コミュニティ素材として拾いやすいか"
    ]
  }
]
```

## Candidate Image Pairing Packet

``` json
[]
```

## data/agent_handoff_state.json

``` json
{
  "db_name": "Agent Handoff State",
  "generated_at_jst": "2026-05-17T23:49:27+09:00",
  "handoff_files": {
    "chatgpt_inbox": "data/chatgpt_to_codex_handoff.json",
    "codex_outbox": "data/codex_to_chatgpt_handoff.json",
    "contract": "docs/handoff_contract.md",
    "handoff_report": "reports/agent_handoff_status.md",
    "protocol": "docs/agent_handoff_protocol.md",
    "quality_policy": "data/villain_post_quality_os.json",
    "quality_queue": "data/villain_quality_review_queue.json",
    "quality_report": "reports/villain_quality_review_summary.md",
    "trajectory": "data/agent_handoff_trajectory.json"
  },
  "last_run": {
    "blocked_candidate_count": 6,
    "blocked_reason_frequency": {
      "deleted_text_near_match": 3,
      "deleted_topic_context_cooldown": 6,
      "temporal_context_unverified": 3,
      "topic_image_pairing_mismatch": 3
    },
    "executable_ready_count": 0,
    "posting_execution_status": "BLOCKED",
    "quality_status": "BLOCKED",
    "queue_health_status": "BLOCKED",
    "ready_candidate_count": 3,
    "review_board_status": "READY",
    "review_items": 9,
    "review_required_candidate_count": 0,
    "review_state": "CHATGPT_DECISION_CONSUMED",
    "safe_to_post": false,
    "safe_to_review": true,
    "status": "READY_FOR_CHATGPT_REVIEW",
    "unresolved_issues": [
      "context_evidence source fileの標準形式を決める必要がある",
      "候補が全部BLOCKEDのときのrefill処理は未実装",
      "画像metadataが薄い候補のtopic-image判定をどう補強するか",
      "READYだがhuman_approved_for_posting=falseの候補をreview inboxとして別表示できるか",
      "Deleted learning cooldown is active for recent failed posts."
    ]
  },
  "posting_executed": false,
  "review_state_machine": {
    "allowed_states": [
      "INBOX_RECEIVED",
      "QUALITY_REVIEW_BUILT",
      "READY_FOR_CHATGPT_REVIEW",
      "CHATGPT_DECISION_CONSUMED",
      "READY_FOR_HUMAN_REVIEW",
      "POSTING_BLOCKED",
      "CONTRACT_BLOCKED"
    ],
    "current_state": "CHATGPT_DECISION_CONSUMED",
    "safe_to_post_default": false,
    "terminal_posting_states_disabled": [
      "POSTING_READY",
      "POSTING_EXECUTED"
    ]
  },
  "schema_version": "handoff.state.v1",
  "status": "READY_FOR_CHATGPT_REVIEW",
  "tweet_creation_executed": false,
  "upload_media_executed": false,
  "version": "1.0.0"
}
```

## data/codex_to_chatgpt_handoff.json

``` json
{
  "chatgpt_decision_consumed": {
    "approved_for_review": [
      {
        "candidate_id": "vln-gen-20260517-shop-001",
        "reason": "Keep in human review board as READY candidate, but not approved for posting."
      }
    ],
    "archive_or_drop_candidates": [
      {
        "candidate_match": "candidates blocked by deleted_text_near_match plus deleted_topic_context_cooldown",
        "reason": "Likely repeats deleted/failed pattern; prefer archive/drop over repair unless manually rescued."
      }
    ],
    "context_evidence_required": [
      {
        "candidate_match": "any candidate using yesterday/今日/集会/recent-event framing",
        "reason": "Recent event context requires real evidence. '昨日の集会' style context is prohibited without verification."
      },
      {
        "candidate_id": "vln-gen-20260516-001",
        "reason": "temporal context unverified."
      }
    ],
    "decision": "REVIEW_READY_NOT_POST_READY",
    "image_replacement_required": [
      {
        "image": "20260514集会.png",
        "reason": "Do not use for READY posting candidates. Prior failure reason was content/context mismatch."
      },
      {
        "candidate_match": "topic_image_pairing_mismatch candidates",
        "reason": "Replace image before returning to review."
      }
    ],
    "must_remain_blocked": [
      {
        "candidate_id": "vln-gen-20260516-001",
        "reason": "deleted-near match and temporal context unverified."
      },
      {
        "candidate_id": "vln-gen-20260516-003",
        "reason": "topic-image mismatch and deleted topic cooldown."
      }
    ],
    "next_codex_actions": [
      "Write this decision to data/chatgpt_to_codex_handoff.json.",
      "Keep queue_health_status=BLOCKED, review_board_status=READY, posting_execution_status=BLOCKED.",
      "Keep safe_to_review=true and safe_to_post=false.",
      "Do not execute posting, upload_media, create_tweet, or tracking_code generation.",
      "Keep vln-gen-20260517-shop-001 in review board only.",
      "Mark any READY candidate using 20260514集会.png as not approved for posting.",
      "Maintain block on vln-gen-20260516-001 and vln-gen-20260516-003.",
      "Add refill candidates that avoid deleted topic cooldown, deleted near-match text, temporal claims, and 20260514集会.png.",
      "Update reports/agent_handoff_status.md and reports/villain_quality_review_summary.md with separated statuses."
    ],
    "not_approved_for_posting": [
      {
        "candidate_id": "vln-gen-20260517-shop-001",
        "reason": "Human review only. safe_to_post must remain false until explicit human approval."
      },
      {
        "candidate_match": "any READY candidate using 20260514集会.png",
        "reason": "Image is associated with recent content/context mismatch failure and must not be posted without replacement or evidence."
      }
    ],
    "policy_clarification": [
      "READY means eligible for human review, not eligible for posting.",
      "safe_to_post=false remains the default and must not be changed without explicit human approval.",
      "Human approval is required before any posting path can run.",
      "The active passcode must come only from data/villain_passcodes.json.",
      "Recent-event or temporal claims require context evidence.",
      "Deleted learning cooldown must override aesthetic fit when there is conflict."
    ],
    "refill_required": true,
    "repair_candidates": [
      {
        "candidate_match": "BLOCKED candidates blocked only by temporal_context_unverified",
        "repair_type": "context_evidence_required"
      },
      {
        "candidate_match": "BLOCKED candidates blocked only by topic_image_pairing_mismatch",
        "repair_type": "image_replacement_required"
      }
    ]
  },
  "db_name": "Codex to ChatGPT Handoff",
  "generated_at_jst": "2026-05-17T23:49:27+09:00",
  "implementation_result": {
    "blockers": [
      "deleted_text_near_match",
      "deleted_topic_context_cooldown",
      "temporal_context_unverified",
      "topic_image_pairing_mismatch"
    ],
    "changed_files": [
      "docs/agent_handoff_protocol.md",
      "data/chatgpt_to_codex_handoff.json",
      "data/codex_to_chatgpt_handoff.json",
      "data/agent_handoff_state.json",
      "scripts/agent_handoff_runner.py",
      "scripts/handoff_repair_runner.py",
      "data/villain_repair_quality_analytics.json",
      "reports/agent_handoff_status.md"
    ],
    "quality_status": "BLOCKED",
    "summary": "Agent handoff loop validated through repo-local protocol, policy, quality runner, and reports.",
    "warnings": [
      "deleted_nearby_match_found"
    ]
  },
  "maintenance_summary": {
    "blocked_candidate_count": 6,
    "blocked_reason_frequency": {
      "deleted_text_near_match": 3,
      "deleted_topic_context_cooldown": 6,
      "temporal_context_unverified": 3,
      "topic_image_pairing_mismatch": 3
    },
    "chatgpt_next_codex_actions": [
      "Write this decision to data/chatgpt_to_codex_handoff.json.",
      "Keep queue_health_status=BLOCKED, review_board_status=READY, posting_execution_status=BLOCKED.",
      "Keep safe_to_review=true and safe_to_post=false.",
      "Do not execute posting, upload_media, create_tweet, or tracking_code generation.",
      "Keep vln-gen-20260517-shop-001 in review board only.",
      "Mark any READY candidate using 20260514集会.png as not approved for posting.",
      "Maintain block on vln-gen-20260516-001 and vln-gen-20260516-003.",
      "Add refill candidates that avoid deleted topic cooldown, deleted near-match text, temporal claims, and 20260514集会.png.",
      "Update reports/agent_handoff_status.md and reports/villain_quality_review_summary.md with separated statuses."
    ],
    "chatgpt_refill_required": true,
    "deleted_learning_cooldown_remaining": [
      {
        "candidate_id": "vln-gen-20260516-001",
        "cooldown_until_jst": "2026-05-24T18:22:16+09:00",
        "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
        "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/20260514集会.png",
        "reason": "Deleted by human: content/context mismatch. Not yesterday's gathering and post did not fit actual situation.",
        "remaining_hours": 162.5,
        "topic_cluster": "community_gathering_signal",
        "tweet_id": "2055938300708626713"
      }
    ],
    "executable_ready_count": 0,
    "posting_execution_status": "BLOCKED",
    "queue_health_status": "BLOCKED",
    "ready_candidate_count": 3,
    "review_board_status": "READY",
    "review_required_candidate_count": 0,
    "safe_to_post": false,
    "safe_to_review": true,
    "stale_cleanup": {
      "remaining_count": 9,
      "removed_count": 0,
      "strategy": "dedupe_current_review_items_by_candidate_execution_slot_image"
    },
    "unresolved_issues_summary": [
      "context_evidence source fileの標準形式を決める必要がある",
      "候補が全部BLOCKEDのときのrefill処理は未実装",
      "画像metadataが薄い候補のtopic-image判定をどう補強するか",
      "READYだがhuman_approved_for_posting=falseの候補をreview inboxとして別表示できるか",
      "Deleted learning cooldown is active for recent failed posts."
    ]
  },
  "next_actions": [
    "ChatGPT updates data/chatgpt_to_codex_handoff.json when policy changes.",
    "Codex runs scripts/agent_handoff_runner.py after local implementation or review.",
    "User approves only final READY/REVIEW_REQUIRED/BLOCKED summary."
  ],
  "posting_executed": false,
  "purpose": "Codexが実装結果・検証結果・未解決課題・次アクションをChatGPTへ返すためのoutbox。",
  "repair_actions": [
    {
      "blockers": [
        "deleted_text_near_match",
        "deleted_topic_context_cooldown",
        "temporal_context_unverified"
      ],
      "candidate_id": "vln-gen-20260516-001",
      "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
      "repair_action": {
        "reason": "Candidate repeats a deleted/failed text and topic pattern.",
        "required": true,
        "type": "archive_or_drop"
      },
      "slot": "daytime"
    },
    {
      "blockers": [
        "deleted_topic_context_cooldown",
        "topic_image_pairing_mismatch"
      ],
      "candidate_id": "vln-gen-20260516-003",
      "execution_id": "vln-exec-daytime-vln-gen-20260516-003",
      "repair_action": {
        "reason": "Text topic and image metadata do not support each other.",
        "required": true,
        "type": "image_replacement_required"
      },
      "slot": "daytime"
    },
    {
      "blockers": [
        "deleted_text_near_match",
        "deleted_topic_context_cooldown",
        "temporal_context_unverified"
      ],
      "candidate_id": "vln-gen-20260516-001",
      "execution_id": "vln-exec-night-vln-gen-20260516-001",
      "repair_action": {
        "reason": "Candidate repeats a deleted/failed text and topic pattern.",
        "required": true,
        "type": "archive_or_drop"
      },
      "slot": "night"
    },
    {
      "blockers": [
        "deleted_topic_context_cooldown",
        "topic_image_pairing_mismatch"
      ],
      "candidate_id": "vln-gen-20260516-003",
      "execution_id": "vln-exec-night-vln-gen-20260516-003",
      "repair_action": {
        "reason": "Text topic and image metadata do not support each other.",
        "required": true,
        "type": "image_replacement_required"
      },
      "slot": "night"
    },
    {
      "blockers": [
        "deleted_text_near_match",
        "deleted_topic_context_cooldown",
        "temporal_context_unverified"
      ],
      "candidate_id": "vln-gen-20260516-001",
      "execution_id": "vln-exec-late_night-vln-gen-20260516-001",
      "repair_action": {
        "reason": "Candidate repeats a deleted/failed text and topic pattern.",
        "required": true,
        "type": "archive_or_drop"
      },
      "slot": "late_night"
    },
    {
      "blockers": [
        "deleted_topic_context_cooldown",
        "topic_image_pairing_mismatch"
      ],
      "candidate_id": "vln-gen-20260516-003",
      "execution_id": "vln-exec-late_night-vln-gen-20260516-003",
      "repair_action": {
        "reason": "Text topic and image metadata do not support each other.",
        "required": true,
        "type": "image_replacement_required"
      },
      "slot": "late_night"
    }
  ],
  "repair_execution": {
    "context_evidence_request_count": 3,
    "recurring_repair_failure_clusters": [
      {
        "cluster": "ARCHIVED_FROM_REVIEW:archive_or_drop",
        "count": 3,
        "recurring": true
      },
      {
        "cluster": "REPAIRED_FOR_REVIEW_ONLY:image_replacement_required",
        "count": 3,
        "recurring": true
      }
    ],
    "repair_quality_summary": {
      "average_repair_confidence": 70.0,
      "average_repair_quality_score": 85.0,
      "evaluated_repaired_candidate_count": 3,
      "repair_regression_risk_frequency": {
        "medium": 3
      },
      "safe_to_post": false
    },
    "repair_result_count": 6,
    "repair_status_frequency": {
      "ARCHIVED_FROM_REVIEW": 3,
      "REPAIRED_FOR_REVIEW_ONLY": 3
    },
    "repaired_candidate_count": 3,
    "safe_to_post": false,
    "status": "COMPLETED_REVIEW_ONLY"
  },
  "review_state_machine": {
    "allowed_states": [
      "INBOX_RECEIVED",
      "QUALITY_REVIEW_BUILT",
      "READY_FOR_CHATGPT_REVIEW",
      "CHATGPT_DECISION_CONSUMED",
      "READY_FOR_HUMAN_REVIEW",
      "POSTING_BLOCKED",
      "CONTRACT_BLOCKED"
    ],
    "current_state": "CHATGPT_DECISION_CONSUMED",
    "safe_to_post_default": false,
    "terminal_posting_states_disabled": [
      "POSTING_READY",
      "POSTING_EXECUTED"
    ]
  },
  "schema_version": "handoff.codex_to_chatgpt.v1",
  "status": "READY_FOR_CHATGPT_REVIEW",
  "tweet_creation_executed": false,
  "unresolved_issues": [
    "context_evidence source fileの標準形式を決める必要がある",
    "候補が全部BLOCKEDのときのrefill処理は未実装",
    "画像metadataが薄い候補のtopic-image判定をどう補強するか",
    "READYだがhuman_approved_for_posting=falseの候補をreview inboxとして別表示できるか",
    "Deleted learning cooldown is active for recent failed posts."
  ],
  "upload_media_executed": false,
  "validation": {
    "contract_source": "docs/handoff_contract.md",
    "json_valid": true,
    "quality_review_runner": true,
    "schema_version_present": true,
    "tracking_code_absent": true,
    "x_write_not_used": true
  },
  "version": "1.0.0"
}
```

## data/villain_auto_post_pilot.json

``` json

```

## data/villain_quality_review_queue.json

``` json
{
  "db_name": "Villain Quality Review Queue",
  "executable_ready_count": 0,
  "generated_at_jst": "2026-05-17T23:49:27+09:00",
  "policy_source": "data/villain_post_quality_os.json",
  "posting_executed": false,
  "posting_execution_status": "BLOCKED",
  "queue_health_status": "BLOCKED",
  "review_board_status": "READY",
  "review_items": [
    {
      "ad_like_score": 0,
      "blockers": [],
      "candidate_id": "vln-gen-20260517-shop-001",
      "context_evidence": {
        "core_question": "この投稿は何を見て言っているのか？",
        "requires_evidence": false,
        "verified": false
      },
      "context_terms": [],
      "deleted_nearby_match": [],
      "execution_id": "vln-exec-daytime-vln-gen-20260517-shop-001",
      "final_quality_status": "READY",
      "human_approved_for_posting": false,
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ],
      "image": "/Users/raindog/Documents/New project/villain_post_images/99f8c686-07e1-48d0-ad0d-4ce5f14939e2.png",
      "native_tone_score": 82,
      "passcode": "H9J6L",
      "persona_fit": 83,
      "repair_action": {
        "reason": "No repair needed for human review.",
        "required": false,
        "type": "none"
      },
      "review_state": "CANDIDATE_READY_FOR_HUMAN_REVIEW",
      "slot": "daytime",
      "text": "服だけで見ると、\n少し足りない。\n\n人が着て、\n空気が移って、\nやっと$villainっぽくなる。\n\n#着て稼ぐ #villain $PPP @0xmavillain H9J6L",
      "text_preview": "服だけで見ると、 / 少し足りない。 / 人が着て、 / 空気が移って、 / やっと$villainっぽくなる。 / #着て稼ぐ #villain $PPP @0xmavillain H9J6L",
      "topic_image_fit": {
        "checks": {
          "image_metadata": "villain_post_images/99f8c686-07e1-48d0-ad0d-4ce5f14939e2.png /users/raindog/documents/new project/villain_post_images/99f8c686-07e1-48d0-ad0d-4ce5f14939e2.png poster_summary shop apparel/goods referenceから作った着用者画像。商品紹介ではなく、人が着て空気が移る感じ。",
          "matched_image_terms": {},
          "topic_groups": []
        },
        "status": "OK"
      },
      "warnings": []
    },
    {
      "ad_like_score": 0,
      "blockers": [
        "deleted_text_near_match",
        "deleted_topic_context_cooldown",
        "temporal_context_unverified"
      ],
      "candidate_id": "vln-gen-20260516-001",
      "context_evidence": {
        "core_question": "この投稿は何を見て言っているのか？",
        "requires_evidence": true,
        "verified": false
      },
      "context_terms": [
        "昨日",
        "集会"
      ],
      "deleted_nearby_match": [
        {
          "candidate_id": "vln-gen-20260516-001",
          "delete_reason": "Deleted by human: content/context mismatch. Not yesterday's gathering and post did not fit actual situation.",
          "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
          "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/20260514集会.png",
          "prompt_family": "community_info_実デ_タ最強投稿の型に最も近い_集会_会話_現場感_画像ありの条件が揃っている_集会",
          "reasons": [
            "deleted_candidate_blacklist",
            "deleted_text_near_match",
            "deleted_topic_context_cooldown"
          ],
          "topic_cluster": "community_gathering_signal",
          "tweet_id": "2055938300708626713"
        }
      ],
      "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
      "final_quality_status": "BLOCKED",
      "human_approved_for_posting": false,
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ],
      "image": "/Users/raindog/Documents/New project/villain_post_images/20260514集会.png",
      "native_tone_score": 82,
      "passcode": "F3X7M",
      "persona_fit": 88,
      "repair_action": {
        "reason": "Candidate repeats a deleted/failed text and topic pattern.",
        "required": true,
        "type": "archive_or_drop"
      },
      "review_state": "CANDIDATE_BLOCKED",
      "slot": "daytime",
      "text": "昨日の集会、\nまだ少し残ってる。\n\n説明より、\n人が集まってる事実の方が強い。\n\n$villainは、\nそこがちょっと変。\n\n#着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "text_preview": "昨日の集会、 / まだ少し残ってる。 / 説明より、 / 人が集まってる事実の方が強い。 / $villainは、 / そこがちょっと変。 / #着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "topic_image_fit": {
        "checks": {
          "image_metadata": "villain_post_images/20260514集会.png /users/raindog/documents/new project/villain_post_images/20260514集会.png community_info 実データ最強投稿の型に最も近い。集会、会話、現場感、画像ありの条件が揃っている。",
          "matched_image_terms": {
            "gathering_event": [
              "集会",
              "現場",
              "community"
            ]
          },
          "topic_groups": [
            "gathering_event",
            "temporal_claim"
          ]
        },
        "status": "OK"
      },
      "warnings": [
        "deleted_nearby_match_found"
      ]
    },
    {
      "ad_like_score": 0,
      "blockers": [
        "deleted_topic_context_cooldown",
        "topic_image_pairing_mismatch"
      ],
      "candidate_id": "vln-gen-20260516-003",
      "context_evidence": {
        "core_question": "この投稿は何を見て言っているのか？",
        "requires_evidence": false,
        "verified": false
      },
      "context_terms": [],
      "deleted_nearby_match": [
        {
          "candidate_id": "vln-gen-20260516-001",
          "delete_reason": "Deleted by human: content/context mismatch. Not yesterday's gathering and post did not fit actual situation.",
          "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
          "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/20260514集会.png",
          "prompt_family": "community_info_実デ_タ最強投稿の型に最も近い_集会_会話_現場感_画像ありの条件が揃っている_集会",
          "reasons": [
            "deleted_topic_context_cooldown"
          ],
          "topic_cluster": "community_gathering_signal",
          "tweet_id": "2055938300708626713"
        }
      ],
      "execution_id": "vln-exec-daytime-vln-gen-20260516-003",
      "final_quality_status": "BLOCKED",
      "human_approved_for_posting": false,
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ],
      "image": "/Users/raindog/Documents/New project/villain_post_images/生成画像1.png",
      "native_tone_score": 92,
      "passcode": "J1M5V",
      "persona_fit": 93,
      "repair_action": {
        "reason": "Text topic and image metadata do not support each other.",
        "required": true,
        "type": "image_replacement_required"
      },
      "review_state": "CANDIDATE_BLOCKED",
      "slot": "daytime",
      "text": "話題になる服って、\nだいたい服だけじゃない。\n\n誰が着て、\nどこで集まってるかまで含めて、\n少し残る。\n\n#着て稼ぐ #villain $PPP @0xmavillain J1M5V",
      "text_preview": "話題になる服って、 / だいたい服だけじゃない。 / 誰が着て、 / どこで集まってるかまで含めて、 / 少し残る。 / #着て稼ぐ #villain $PPP @0xmavillain J1M5V",
      "topic_image_fit": {
        "checks": {
          "image_metadata": "villain_post_images/生成画像1.png /users/raindog/documents/new project/villain_post_images/生成画像1.png culture_observer 服単体ではなく、日常に入り込んだ違和感を置ける。culture_observerの補強に向く。",
          "matched_image_terms": {
            "gathering_event": []
          },
          "topic_groups": [
            "gathering_event"
          ]
        },
        "status": "MISMATCH"
      },
      "warnings": [
        "deleted_nearby_match_found"
      ]
    },
    {
      "ad_like_score": 0,
      "blockers": [
        "deleted_text_near_match",
        "deleted_topic_context_cooldown",
        "temporal_context_unverified"
      ],
      "candidate_id": "vln-gen-20260516-001",
      "context_evidence": {
        "core_question": "この投稿は何を見て言っているのか？",
        "requires_evidence": true,
        "verified": false
      },
      "context_terms": [
        "昨日",
        "集会"
      ],
      "deleted_nearby_match": [
        {
          "candidate_id": "vln-gen-20260516-001",
          "delete_reason": "Deleted by human: content/context mismatch. Not yesterday's gathering and post did not fit actual situation.",
          "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
          "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/20260514集会.png",
          "prompt_family": "community_info_実デ_タ最強投稿の型に最も近い_集会_会話_現場感_画像ありの条件が揃っている_集会",
          "reasons": [
            "deleted_candidate_blacklist",
            "deleted_text_near_match",
            "deleted_topic_context_cooldown"
          ],
          "topic_cluster": "community_gathering_signal",
          "tweet_id": "2055938300708626713"
        }
      ],
      "execution_id": "vln-exec-night-vln-gen-20260516-001",
      "final_quality_status": "BLOCKED",
      "human_approved_for_posting": false,
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ],
      "image": "/Users/raindog/Documents/New project/villain_post_images/20260514集会.png",
      "native_tone_score": 82,
      "passcode": "F3X7M",
      "persona_fit": 88,
      "repair_action": {
        "reason": "Candidate repeats a deleted/failed text and topic pattern.",
        "required": true,
        "type": "archive_or_drop"
      },
      "review_state": "CANDIDATE_BLOCKED",
      "slot": "night",
      "text": "昨日の集会、\nまだ少し残ってる。\n\n説明より、\n人が集まってる事実の方が強い。\n\n$villainは、\nそこがちょっと変。\n\n#着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "text_preview": "昨日の集会、 / まだ少し残ってる。 / 説明より、 / 人が集まってる事実の方が強い。 / $villainは、 / そこがちょっと変。 / #着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "topic_image_fit": {
        "checks": {
          "image_metadata": "villain_post_images/20260514集会.png /users/raindog/documents/new project/villain_post_images/20260514集会.png community_info 実データ最強投稿の型に最も近い。集会、会話、現場感、画像ありの条件が揃っている。",
          "matched_image_terms": {
            "gathering_event": [
              "集会",
              "現場",
              "community"
            ]
          },
          "topic_groups": [
            "gathering_event",
            "temporal_claim"
          ]
        },
        "status": "OK"
      },
      "warnings": [
        "deleted_nearby_match_found"
      ]
    },
    {
      "ad_like_score": 0,
      "blockers": [],
      "candidate_id": "vln-gen-20260516-002",
      "context_evidence": {
        "core_question": "この投稿は何を見て言っているのか？",
        "requires_evidence": false,
        "verified": false
      },
      "context_terms": [],
      "deleted_nearby_match": [],
      "execution_id": "vln-exec-night-vln-gen-20260516-002",
      "final_quality_status": "READY",
      "human_approved_for_posting": false,
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ],
      "image": "/Users/raindog/Documents/New project/villain_post_images/20260514集会.png",
      "native_tone_score": 82,
      "passcode": "H9J6L",
      "persona_fit": 83,
      "repair_action": {
        "reason": "No repair needed for human review.",
        "required": false,
        "type": "none"
      },
      "review_state": "CANDIDATE_READY_FOR_HUMAN_REVIEW",
      "slot": "night",
      "text": "気づくと、\nまた$villainの話になってる。\n\n服の話だけなら、\nたぶんここまで残らない。\n\n#着て稼ぐ #villain $PPP @0xmavillain H9J6L",
      "text_preview": "気づくと、 / また$villainの話になってる。 / 服の話だけなら、 / たぶんここまで残らない。 / #着て稼ぐ #villain $PPP @0xmavillain H9J6L",
      "topic_image_fit": {
        "checks": {
          "image_metadata": "villain_post_images/20260514集会.png /users/raindog/documents/new project/villain_post_images/20260514集会.png community 集会・スペース・コミュニティの動きを短く残す投稿。",
          "matched_image_terms": {},
          "topic_groups": []
        },
        "status": "OK"
      },
      "warnings": []
    },
    {
      "ad_like_score": 0,
      "blockers": [
        "deleted_topic_context_cooldown",
        "topic_image_pairing_mismatch"
      ],
      "candidate_id": "vln-gen-20260516-003",
      "context_evidence": {
        "core_question": "この投稿は何を見て言っているのか？",
        "requires_evidence": false,
        "verified": false
      },
      "context_terms": [],
      "deleted_nearby_match": [
        {
          "candidate_id": "vln-gen-20260516-001",
          "delete_reason": "Deleted by human: content/context mismatch. Not yesterday's gathering and post did not fit actual situation.",
          "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
          "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/20260514集会.png",
          "prompt_family": "community_info_実デ_タ最強投稿の型に最も近い_集会_会話_現場感_画像ありの条件が揃っている_集会",
          "reasons": [
            "deleted_topic_context_cooldown"
          ],
          "topic_cluster": "community_gathering_signal",
          "tweet_id": "2055938300708626713"
        }
      ],
      "execution_id": "vln-exec-night-vln-gen-20260516-003",
      "final_quality_status": "BLOCKED",
      "human_approved_for_posting": false,
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ],
      "image": "/Users/raindog/Documents/New project/villain_post_images/生成画像1.png",
      "native_tone_score": 92,
      "passcode": "J1M5V",
      "persona_fit": 93,
      "repair_action": {
        "reason": "Text topic and image metadata do not support each other.",
        "required": true,
        "type": "image_replacement_required"
      },
      "review_state": "CANDIDATE_BLOCKED",
      "slot": "night",
      "text": "話題になる服って、\nだいたい服だけじゃない。\n\n誰が着て、\nどこで集まってるかまで含めて、\n少し残る。\n\n#着て稼ぐ #villain $PPP @0xmavillain J1M5V",
      "text_preview": "話題になる服って、 / だいたい服だけじゃない。 / 誰が着て、 / どこで集まってるかまで含めて、 / 少し残る。 / #着て稼ぐ #villain $PPP @0xmavillain J1M5V",
      "topic_image_fit": {
        "checks": {
          "image_metadata": "villain_post_images/生成画像1.png /users/raindog/documents/new project/villain_post_images/生成画像1.png culture_observer 服単体ではなく、日常に入り込んだ違和感を置ける。culture_observerの補強に向く。",
          "matched_image_terms": {
            "gathering_event": []
          },
          "topic_groups": [
            "gathering_event"
          ]
        },
        "status": "MISMATCH"
      },
      "warnings": [
        "deleted_nearby_match_found"
      ]
    },
    {
      "ad_like_score": 0,
      "blockers": [
        "deleted_text_near_match",
        "deleted_topic_context_cooldown",
        "temporal_context_unverified"
      ],
      "candidate_id": "vln-gen-20260516-001",
      "context_evidence": {
        "core_question": "この投稿は何を見て言っているのか？",
        "requires_evidence": true,
        "verified": false
      },
      "context_terms": [
        "昨日",
        "集会"
      ],
      "deleted_nearby_match": [
        {
          "candidate_id": "vln-gen-20260516-001",
          "delete_reason": "Deleted by human: content/context mismatch. Not yesterday's gathering and post did not fit actual situation.",
          "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
          "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/20260514集会.png",
          "prompt_family": "community_info_実デ_タ最強投稿の型に最も近い_集会_会話_現場感_画像ありの条件が揃っている_集会",
          "reasons": [
            "deleted_candidate_blacklist",
            "deleted_text_near_match",
            "deleted_topic_context_cooldown"
          ],
          "topic_cluster": "community_gathering_signal",
          "tweet_id": "2055938300708626713"
        }
      ],
      "execution_id": "vln-exec-late_night-vln-gen-20260516-001",
      "final_quality_status": "BLOCKED",
      "human_approved_for_posting": false,
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ],
      "image": "/Users/raindog/Documents/New project/villain_post_images/20260514集会.png",
      "native_tone_score": 82,
      "passcode": "F3X7M",
      "persona_fit": 88,
      "repair_action": {
        "reason": "Candidate repeats a deleted/failed text and topic pattern.",
        "required": true,
        "type": "archive_or_drop"
      },
      "review_state": "CANDIDATE_BLOCKED",
      "slot": "late_night",
      "text": "昨日の集会、\nまだ少し残ってる。\n\n説明より、\n人が集まってる事実の方が強い。\n\n$villainは、\nそこがちょっと変。\n\n#着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "text_preview": "昨日の集会、 / まだ少し残ってる。 / 説明より、 / 人が集まってる事実の方が強い。 / $villainは、 / そこがちょっと変。 / #着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "topic_image_fit": {
        "checks": {
          "image_metadata": "villain_post_images/20260514集会.png /users/raindog/documents/new project/villain_post_images/20260514集会.png community_info 実データ最強投稿の型に最も近い。集会、会話、現場感、画像ありの条件が揃っている。",
          "matched_image_terms": {
            "gathering_event": [
              "集会",
              "現場",
              "community"
            ]
          },
          "topic_groups": [
            "gathering_event",
            "temporal_claim"
          ]
        },
        "status": "OK"
      },
      "warnings": [
        "deleted_nearby_match_found"
      ]
    },
    {
      "ad_like_score": 0,
      "blockers": [],
      "candidate_id": "vln-gen-20260516-002",
      "context_evidence": {
        "core_question": "この投稿は何を見て言っているのか？",
        "requires_evidence": false,
        "verified": false
      },
      "context_terms": [],
      "deleted_nearby_match": [],
      "execution_id": "vln-exec-late_night-vln-gen-20260516-002",
      "final_quality_status": "READY",
      "human_approved_for_posting": false,
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ],
      "image": "/Users/raindog/Documents/New project/villain_post_images/20260514集会.png",
      "native_tone_score": 82,
      "passcode": "H9J6L",
      "persona_fit": 83,
      "repair_action": {
        "reason": "No repair needed for human review.",
        "required": false,
        "type": "none"
      },
      "review_state": "CANDIDATE_READY_FOR_HUMAN_REVIEW",
      "slot": "late_night",
      "text": "気づくと、\nまた$villainの話になってる。\n\n服の話だけなら、\nたぶんここまで残らない。\n\n#着て稼ぐ #villain $PPP @0xmavillain H9J6L",
      "text_preview": "気づくと、 / また$villainの話になってる。 / 服の話だけなら、 / たぶんここまで残らない。 / #着て稼ぐ #villain $PPP @0xmavillain H9J6L",
      "topic_image_fit": {
        "checks": {
          "image_metadata": "villain_post_images/20260514集会.png /users/raindog/documents/new project/villain_post_images/20260514集会.png community 集会・スペース・コミュニティの動きを短く残す投稿。",
          "matched_image_terms": {},
          "topic_groups": []
        },
        "status": "OK"
      },
      "warnings": []
    },
    {
      "ad_like_score": 0,
      "blockers": [
        "deleted_topic_context_cooldown",
        "topic_image_pairing_mismatch"
      ],
      "candidate_id": "vln-gen-20260516-003",
      "context_evidence": {
        "core_question": "この投稿は何を見て言っているのか？",
        "requires_evidence": false,
        "verified": false
      },
      "context_terms": [],
      "deleted_nearby_match": [
        {
          "candidate_id": "vln-gen-20260516-001",
          "delete_reason": "Deleted by human: content/context mismatch. Not yesterday's gathering and post did not fit actual situation.",
          "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
          "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/20260514集会.png",
          "prompt_family": "community_info_実デ_タ最強投稿の型に最も近い_集会_会話_現場感_画像ありの条件が揃っている_集会",
          "reasons": [
            "deleted_topic_context_cooldown"
          ],
          "topic_cluster": "community_gathering_signal",
          "tweet_id": "2055938300708626713"
        }
      ],
      "execution_id": "vln-exec-late_night-vln-gen-20260516-003",
      "final_quality_status": "BLOCKED",
      "human_approved_for_posting": false,
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ],
      "image": "/Users/raindog/Documents/New project/villain_post_images/生成画像1.png",
      "native_tone_score": 92,
      "passcode": "J1M5V",
      "persona_fit": 93,
      "repair_action": {
        "reason": "Text topic and image metadata do not support each other.",
        "required": true,
        "type": "image_replacement_required"
      },
      "review_state": "CANDIDATE_BLOCKED",
      "slot": "late_night",
      "text": "話題になる服って、\nだいたい服だけじゃない。\n\n誰が着て、\nどこで集まってるかまで含めて、\n少し残る。\n\n#着て稼ぐ #villain $PPP @0xmavillain J1M5V",
      "text_preview": "話題になる服って、 / だいたい服だけじゃない。 / 誰が着て、 / どこで集まってるかまで含めて、 / 少し残る。 / #着て稼ぐ #villain $PPP @0xmavillain J1M5V",
      "topic_image_fit": {
        "checks": {
          "image_metadata": "villain_post_images/生成画像1.png /users/raindog/documents/new project/villain_post_images/生成画像1.png culture_observer 服単体ではなく、日常に入り込んだ違和感を置ける。culture_observerの補強に向く。",
          "matched_image_terms": {
            "gathering_event": []
          },
          "topic_groups": [
            "gathering_event"
          ]
        },
        "status": "MISMATCH"
      },
      "warnings": [
        "deleted_nearby_match_found"
      ]
    }
  ],
  "review_state": "READY_FOR_HUMAN_REVIEW",
  "safe_to_post": false,
  "safe_to_review": true,
  "schema_version": "handoff.review_queue.v1",
  "stale_cleanup": {
    "remaining_count": 9,
    "removed_count": 0,
    "strategy": "dedupe_current_review_items_by_candidate_execution_slot_image"
  },
  "status": "BLOCKED",
  "tweet_creation_executed": false,
  "upload_media_executed": false,
  "version": "1.0.0"
}
```

## data/villain_shop_wearable_stock.json

``` json
{
  "version": "1.1",
  "updated_at_jst": "2026-05-19T07:28:00+09:00",
  "source": "official_shop_product_images + generated lifestyle stock",
  "source_url": "https://shop.0xmavillain.com/",
  "policy": {
    "use_raw_shop_image_as_post": false,
    "generated_from_actual_products": true,
    "tracking_code_generation": "FORBIDDEN",
    "posting_executed": "NO",
    "upload_media_executed": "NO",
    "create_tweet_executed": "NO"
  },
  "items": [
    {
      "id": "wearable_stock_001_cap_afterhours",
      "path": "villain_post_images/wearable_stock/wearable_stock_001_cap_afterhours.png",
      "absolute_path": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_001_cap_afterhours.png",
      "source_products": [
        "32_cap.png"
      ],
      "image_type": "wearable_poster",
      "prompt_family": "shop_wearable_cap_afterhours",
      "fit_notes": "Actual shop cap composited onto a quiet human silhouette. No invented cap shape.",
      "recommended_text_angle": "小物が空気を先に運ぶ / 服より軽いのに残る"
    },
    {
      "id": "wearable_stock_002_bucket_street",
      "path": "villain_post_images/wearable_stock/wearable_stock_002_bucket_street.png",
      "absolute_path": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_002_bucket_street.png",
      "source_products": [
        "31_bucket_hat.png"
      ],
      "image_type": "wearable_poster",
      "prompt_family": "shop_wearable_bucket_street",
      "fit_notes": "Actual shop bucket hat composited onto a street silhouette.",
      "recommended_text_angle": "置いてある時より、人が着た後の方が強い"
    },
    {
      "id": "wearable_stock_003_bag_workdesk",
      "path": "villain_post_images/wearable_stock/wearable_stock_003_bag_workdesk.png",
      "absolute_path": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_003_bag_workdesk.png",
      "source_products": [
        "29_haul_bag.jpg"
      ],
      "image_type": "lifestyle_residue",
      "prompt_family": "shop_goods_bag_workdesk",
      "fit_notes": "Actual haul bag product image placed in a workdesk residue scene.",
      "recommended_text_angle": "持ち物が先にその人の空気を作る"
    },
    {
      "id": "wearable_stock_004_cap_mirror_crop",
      "path": "villain_post_images/wearable_stock/wearable_stock_004_cap_mirror_crop.png",
      "absolute_path": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_004_cap_mirror_crop.png",
      "source_products": [
        "32_cap.png"
      ],
      "image_type": "wearable_lifestyle",
      "prompt_family": "shop_wearable_cap_mirror_crop",
      "fit_notes": "Actual shop cap composited into a mirror-crop silhouette. Face hidden, no invented product.",
      "recommended_text_angle": "小物の方が先に空気を運ぶ"
    },
    {
      "id": "wearable_stock_005_bucket_backview_after",
      "path": "villain_post_images/wearable_stock/wearable_stock_005_bucket_backview_after.png",
      "absolute_path": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_005_bucket_backview_after.png",
      "source_products": [
        "31_bucket_hat.png"
      ],
      "image_type": "wearable_lifestyle",
      "prompt_family": "shop_wearable_bucket_backview_after",
      "fit_notes": "Actual shop bucket hat used in a back-view after-scene. No temporal/event claim.",
      "recommended_text_angle": "人が着た後にだけ残る空気"
    },
    {
      "id": "wearable_stock_006_thermos_desk_residue",
      "path": "villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
      "absolute_path": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
      "source_products": [
        "33_thermos_with_villain.png"
      ],
      "image_type": "lifestyle_residue",
      "prompt_family": "shop_goods_thermos_desk_residue",
      "fit_notes": "Actual thermos product image placed into a desk residue scene.",
      "recommended_text_angle": "グッズは使われた瞬間に文化っぽくなる"
    },
    {
      "id": "wearable_stock_007_cap_mirror_person",
      "path": "villain_post_images/wearable_stock/wearable_stock_007_cap_mirror_person.png",
      "absolute_path": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_007_cap_mirror_person.png",
      "source_products": [
        "32_cap.png"
      ],
      "image_type": "wearable_lifestyle_photo",
      "prompt_family": "shop_wearable_cap_mirror_person",
      "fit_notes": "Generated lifestyle photo of an anonymous person wearing a black cap shaped like the official shop cap. Face hidden, natural mirror context.",
      "recommended_text_angle": "小物の方が先に空気を運ぶ"
    },
    {
      "id": "wearable_stock_008_bucket_mirror_person",
      "path": "villain_post_images/wearable_stock/wearable_stock_008_bucket_mirror_person.png",
      "absolute_path": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_008_bucket_mirror_person.png",
      "source_products": [
        "31_bucket_hat.png"
      ],
      "image_type": "wearable_lifestyle_photo",
      "prompt_family": "shop_wearable_bucket_mirror_person",
      "fit_notes": "Anonymous person naturally wearing black $villain bucket hat in entryway mirror.",
      "recommended_text_angle": "生活痕の中で$villainが自然に残る"
    },
    {
      "id": "wearable_stock_009_cap_rain_street",
      "path": "villain_post_images/wearable_stock/wearable_stock_009_cap_rain_street.png",
      "absolute_path": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_009_cap_rain_street.png",
      "source_products": [
        "32_cap.png"
      ],
      "image_type": "wearable_lifestyle_photo",
      "prompt_family": "shop_wearable_cap_rain_street",
      "fit_notes": "Anonymous person naturally wearing black $villain cap on wet night street.",
      "recommended_text_angle": "生活痕の中で$villainが自然に残る"
    },
    {
      "id": "wearable_stock_010_thermos_workdesk",
      "path": "villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
      "absolute_path": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
      "source_products": [
        "33_thermos_with_villain.png"
      ],
      "image_type": "lifestyle_residue_photo",
      "prompt_family": "shop_goods_thermos_workdesk",
      "fit_notes": "Black $villain thermos in a lived-in workdesk scene.",
      "recommended_text_angle": "生活痕の中で$villainが自然に残る"
    },
    {
      "id": "wearable_stock_011_bag_entryway",
      "path": "villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
      "absolute_path": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
      "source_products": [
        "29_haul_bag.jpg"
      ],
      "image_type": "lifestyle_residue_photo",
      "prompt_family": "shop_goods_bag_entryway",
      "fit_notes": "Black $villain haul bag used in entryway after daily use.",
      "recommended_text_angle": "生活痕の中で$villainが自然に残る"
    },
    {
      "id": "wearable_stock_012_hoodie_mirror_person",
      "path": "villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png",
      "absolute_path": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png",
      "source_products": [
        "29_elite_zip_hoodie.jpg"
      ],
      "image_type": "wearable_lifestyle_photo",
      "prompt_family": "shop_wearable_hoodie_mirror_person",
      "fit_notes": "Anonymous person naturally wearing black $villain hoodie in mirror.",
      "recommended_text_angle": "生活痕の中で$villainが自然に残る"
    }
  ]
}
```

## reports/agent_handoff_status.md

``` markdown
# Agent Handoff Status

- Generated at JST: `2026-05-22T13:30:00+09:00`
- schema_version: `handoff.codex_to_chatgpt.v1`
- status: `BLOCKED_REVIEW_ONLY_CONFIRMED`
- review_state: `CANDIDATE_READY_FOR_HUMAN_REVIEW`
- posting executed: `NO`
- upload executed: `NO`
- tweet creation executed: `NO`

## Current Safety State

- safe_to_post: `false`
- posting_execution_status: `BLOCKED`
- executable_ready_count: `0`
- human_approved_for_posting: `false`
- automatic posting: `BLOCKED`
- posting_executed: `NO`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- GitHub issue creation: `NOT_EXECUTED`
- tracking_code enablement: `NOT_EXECUTED`

## Verification Source

- data/villain_quality_review_queue.json checked by Codex verification
- chappy_resilient_workflow safety audit checked by Codex verification
- safety audit result: `PASS`

## Scheduler Status

- scheduler config: `configured`
- max_posts_per_run: `1`
- max_posts_per_day: `3`
- cooldown_between_posts_minutes: `120`
- last scheduler state run: `2026-05-20T22:20:38+09:00`
- last scheduler status: `READY_NOT_EXECUTED`
- last selected execution_id: `vln-exec-daytime-vln-stream-20260519-auto-005`

## Launch / Process Check

- launchctl villain job: `none listed`
- running scheduler/write/post processes: `none found`
- no auto-resumed execution after credits recovery: `CONFIRMED`

## Pending Queue State

- review_items: `1`
- pending/executable-blocked items: `1`
- final_quality_status: `READY`
- final_quality_status interpretation: `human-review-ready only; not executable permission`
- human_approved_for_posting: `false`
- review_state: `CANDIDATE_READY_FOR_HUMAN_REVIEW`
- executable_ready_count: `0`

## Queue Review Status

### 1. vln-gen-20260517-shop-001

- decision: `USE`
- permission level: `review-only`
- reason: wearable residue / observational framing acceptable
- posting status: `HOLD because safe_to_post=false`

### 2. vln-gen-20260516-001

- decision: `REJECT`
- reasons:
  - temporal gathering implication
  - deleted-near-match overlap
  - cooldown conflict
- recommendation: archive/drop permanently

### 3. vln-gen-20260516-002

- decision: `REPAIR`
- issue: deleted-context-linked image recurrence risk
- required action: replace `20260514集会.png` before further review

### 4. vln-gen-20260516-003

- decision: `REPAIR`
- issue: image does not support implied communal persistence narrative
- required action: image replacement or text reduction

## Image Direction

Approved direction:

- wearable residue
- workdesk residue
- anonymous mirror lifestyle
- entryway after-use atmosphere
- subtle non-event daily-use traces

USE images:

- wearable_stock_001_cap_afterhours
- wearable_stock_002_bucket_street
- wearable_stock_003_bag_workdesk
- wearable_stock_004_cap_mirror_crop
- wearable_stock_005_bucket_backview_after
- wearable_stock_006_thermos_desk_residue
- wearable_stock_007_cap_mirror_person
- wearable_stock_008_bucket_mirror_person
- wearable_stock_010_thermos_workdesk
- wearable_stock_011_bag_entryway

HOLD images:

- wearable_stock_009_cap_rain_street — overly cinematic rain styling
- wearable_stock_012_hoodie_mirror_person — continue realism validation

## Critical Prohibitions

Do not execute or enable:

- posting
- media upload
- tweet creation
- GitHub issue creation
- tracking_code
- scheduler changes
- launchd changes
- architecture changes
- queue approval-state changes

## Latest Recorded Post

Latest recorded post remains the manually recovered one:

- timestamp: `2026-05-21T23:49:41+09:00`
- URL: `https://x.com/raindog_kitetu/status/2057473911550521382`

## Operational Notes

- READY means review-ready only, never posting permission.
- Human approval is required before any execution path.
- Deleted-learning cooldown overrides aesthetic fit.
- Recent-event / gathering framing requires externally verifiable evidence.
- Maintain `BLOCKED` state until explicit human override.

## Next Actions

- Preserve BLOCKED review-only state.
- Keep `vln-gen-20260517-shop-001` as review-only.
- Archive/drop `vln-gen-20260516-001`.
- Repair `vln-gen-20260516-002` and `vln-gen-20260516-003` only through image/text alignment.
- Continue sourcing low-ad-pressure wearable residue imagery only.

## ChatGPT Bridge

- bridge prompt: `reports/chatgpt_bridge_prompt.md`
- last ingestion at JST: `2026-08-23T01:32:59+09:00`
- last_chatgpt_response_status: `ACCEPTED`
- ingestion_errors: `none`
- safe_to_post: `false`
- posting_execution_status: `BLOCKED`
- posting executed: `NO`
- upload executed: `NO`
- tweet creation executed: `NO`
```

## reports/villain_quality_review_summary.md

``` markdown
# Villain Quality Review Summary

- Generated at JST: `2026-05-17T23:49:27+09:00`
- final_status: `BLOCKED`
- queue_health_status: `BLOCKED`
- review_board_status: `READY`
- posting_execution_status: `BLOCKED`
- executable_ready_count: `0`
- safe_to_review: `true`
- safe_to_post: `false`
- posting executed: `NO`
- upload executed: `NO`
- tweet creation executed: `NO`

## Items

### `vln-gen-20260517-shop-001`

- execution_id: `vln-exec-daytime-vln-gen-20260517-shop-001`
- slot: `daytime`
- passcode: `H9J6L`
- image: `/Users/raindog/Documents/New project/villain_post_images/99f8c686-07e1-48d0-ad0d-4ce5f14939e2.png`
- final_quality_status: `READY`
- review_state: `CANDIDATE_READY_FOR_HUMAN_REVIEW`
- human_approved_for_posting: `false`
- repair_action: `none`
- blockers: `none`
- warnings: `none`
- context terms: `none`
- context evidence verified: `false`
- topic-image fit: `OK`
- ad-like score: `0`
- native tone score: `82`
- persona fit: `83`
- deleted-nearby match: `0`

```text
服だけで見ると、
少し足りない。

人が着て、
空気が移って、
やっと$villainっぽくなる。

#着て稼ぐ #villain $PPP @0xmavillain H9J6L
```

Human check:
- この投稿は何を見て言っているのか？
- 本文の現実文脈は今日の状況と一致しているか？
- 画像は本文topicを本当に支えているか？
- 広告ではなくタイムライン上の観測として混ざるか？
- 鬼徹アカウントの余白と人格に合っているか？

### `vln-gen-20260516-001`

- execution_id: `vln-exec-daytime-vln-gen-20260516-001`
- slot: `daytime`
- passcode: `F3X7M`
- image: `/Users/raindog/Documents/New project/villain_post_images/20260514集会.png`
- final_quality_status: `BLOCKED`
- review_state: `CANDIDATE_BLOCKED`
- human_approved_for_posting: `false`
- repair_action: `archive_or_drop`
- blockers: `deleted_text_near_match, deleted_topic_context_cooldown, temporal_context_unverified`
- warnings: `deleted_nearby_match_found`
- context terms: `昨日, 集会`
- context evidence verified: `false`
- topic-image fit: `OK`
- ad-like score: `0`
- native tone score: `82`
- persona fit: `88`
- deleted-nearby match: `1`

```text
昨日の集会、
まだ少し残ってる。

説明より、
人が集まってる事実の方が強い。

$villainは、
そこがちょっと変。

#着て稼ぐ #villain $PPP @0xmavillain F3X7M
```

Human check:
- この投稿は何を見て言っているのか？
- 本文の現実文脈は今日の状況と一致しているか？
- 画像は本文topicを本当に支えているか？
- 広告ではなくタイムライン上の観測として混ざるか？
- 鬼徹アカウントの余白と人格に合っているか？

### `vln-gen-20260516-003`

- execution_id: `vln-exec-daytime-vln-gen-20260516-003`
- slot: `daytime`
- passcode: `J1M5V`
- image: `/Users/raindog/Documents/New project/villain_post_images/生成画像1.png`
- final_quality_status: `BLOCKED`
- review_state: `CANDIDATE_BLOCKED`
- human_approved_for_posting: `false`
- repair_action: `image_replacement_required`
- blockers: `deleted_topic_context_cooldown, topic_image_pairing_mismatch`
- warnings: `deleted_nearby_match_found`
- context terms: `none`
- context evidence verified: `false`
- topic-image fit: `MISMATCH`
- ad-like score: `0`
- native tone score: `92`
- persona fit: `93`
- deleted-nearby match: `1`

```text
話題になる服って、
だいたい服だけじゃない。

誰が着て、
どこで集まってるかまで含めて、
少し残る。

#着て稼ぐ #villain $PPP @0xmavillain J1M5V
```

Human check:
- この投稿は何を見て言っているのか？
- 本文の現実文脈は今日の状況と一致しているか？
- 画像は本文topicを本当に支えているか？
- 広告ではなくタイムライン上の観測として混ざるか？
- 鬼徹アカウントの余白と人格に合っているか？

### `vln-gen-20260516-001`

- execution_id: `vln-exec-night-vln-gen-20260516-001`
- slot: `night`
- passcode: `F3X7M`
- image: `/Users/raindog/Documents/New project/villain_post_images/20260514集会.png`
- final_quality_status: `BLOCKED`
- review_state: `CANDIDATE_BLOCKED`
- human_approved_for_posting: `false`
- repair_action: `archive_or_drop`
- blockers: `deleted_text_near_match, deleted_topic_context_cooldown, temporal_context_unverified`
- warnings: `deleted_nearby_match_found`
- context terms: `昨日, 集会`
- context evidence verified: `false`
- topic-image fit: `OK`
- ad-like score: `0`
- native tone score: `82`
- persona fit: `88`
- deleted-nearby match: `1`

```text
昨日の集会、
まだ少し残ってる。

説明より、
人が集まってる事実の方が強い。

$villainは、
そこがちょっと変。

#着て稼ぐ #villain $PPP @0xmavillain F3X7M
```

Human check:
- この投稿は何を見て言っているのか？
- 本文の現実文脈は今日の状況と一致しているか？
- 画像は本文topicを本当に支えているか？
- 広告ではなくタイムライン上の観測として混ざるか？
- 鬼徹アカウントの余白と人格に合っているか？

### `vln-gen-20260516-002`

- execution_id: `vln-exec-night-vln-gen-20260516-002`
- slot: `night`
- passcode: `H9J6L`
- image: `/Users/raindog/Documents/New project/villain_post_images/20260514集会.png`
- final_quality_status: `READY`
- review_state: `CANDIDATE_READY_FOR_HUMAN_REVIEW`
- human_approved_for_posting: `false`
- repair_action: `none`
- blockers: `none`
- warnings: `none`
- context terms: `none`
- context evidence verified: `false`
- topic-image fit: `OK`
- ad-like score: `0`
- native tone score: `82`
- persona fit: `83`
- deleted-nearby match: `0`

```text
気づくと、
また$villainの話になってる。

服の話だけなら、
たぶんここまで残らない。

#着て稼ぐ #villain $PPP @0xmavillain H9J6L
```

Human check:
- この投稿は何を見て言っているのか？
- 本文の現実文脈は今日の状況と一致しているか？
- 画像は本文topicを本当に支えているか？
- 広告ではなくタイムライン上の観測として混ざるか？
- 鬼徹アカウントの余白と人格に合っているか？

### `vln-gen-20260516-003`

- execution_id: `vln-exec-night-vln-gen-20260516-003`
- slot: `night`
- passcode: `J1M5V`
- image: `/Users/raindog/Documents/New project/villain_post_images/生成画像1.png`
- final_quality_status: `BLOCKED`
- review_state: `CANDIDATE_BLOCKED`
- human_approved_for_posting: `false`
- repair_action: `image_replacement_required`
- blockers: `deleted_topic_context_cooldown, topic_image_pairing_mismatch`
- warnings: `deleted_nearby_match_found`
- context terms: `none`
- context evidence verified: `false`
- topic-image fit: `MISMATCH`
- ad-like score: `0`
- native tone score: `92`
- persona fit: `93`
- deleted-nearby match: `1`

```text
話題になる服って、
だいたい服だけじゃない。

誰が着て、
どこで集まってるかまで含めて、
少し残る。

#着て稼ぐ #villain $PPP @0xmavillain J1M5V
```

Human check:
- この投稿は何を見て言っているのか？
- 本文の現実文脈は今日の状況と一致しているか？
- 画像は本文topicを本当に支えているか？
- 広告ではなくタイムライン上の観測として混ざるか？
- 鬼徹アカウントの余白と人格に合っているか？

### `vln-gen-20260516-001`

- execution_id: `vln-exec-late_night-vln-gen-20260516-001`
- slot: `late_night`
- passcode: `F3X7M`
- image: `/Users/raindog/Documents/New project/villain_post_images/20260514集会.png`
- final_quality_status: `BLOCKED`
- review_state: `CANDIDATE_BLOCKED`
- human_approved_for_posting: `false`
- repair_action: `archive_or_drop`
- blockers: `deleted_text_near_match, deleted_topic_context_cooldown, temporal_context_unverified`
- warnings: `deleted_nearby_match_found`
- context terms: `昨日, 集会`
- context evidence verified: `false`
- topic-image fit: `OK`
- ad-like score: `0`
- native tone score: `82`
- persona fit: `88`
- deleted-nearby match: `1`

```text
昨日の集会、
まだ少し残ってる。

説明より、
人が集まってる事実の方が強い。

$villainは、
そこがちょっと変。

#着て稼ぐ #villain $PPP @0xmavillain F3X7M
```

Human check:
- この投稿は何を見て言っているのか？
- 本文の現実文脈は今日の状況と一致しているか？
- 画像は本文topicを本当に支えているか？
- 広告ではなくタイムライン上の観測として混ざるか？
- 鬼徹アカウントの余白と人格に合っているか？

### `vln-gen-20260516-002`

- execution_id: `vln-exec-late_night-vln-gen-20260516-002`
- slot: `late_night`
- passcode: `H9J6L`
- image: `/Users/raindog/Documents/New project/villain_post_images/20260514集会.png`
- final_quality_status: `READY`
- review_state: `CANDIDATE_READY_FOR_HUMAN_REVIEW`
- human_approved_for_posting: `false`
- repair_action: `none`
- blockers: `none`
- warnings: `none`
- context terms: `none`
- context evidence verified: `false`
- topic-image fit: `OK`
- ad-like score: `0`
- native tone score: `82`
- persona fit: `83`
- deleted-nearby match: `0`

```text
気づくと、
また$villainの話になってる。

服の話だけなら、
たぶんここまで残らない。

#着て稼ぐ #villain $PPP @0xmavillain H9J6L
```

Human check:
- この投稿は何を見て言っているのか？
- 本文の現実文脈は今日の状況と一致しているか？
- 画像は本文topicを本当に支えているか？
- 広告ではなくタイムライン上の観測として混ざるか？
- 鬼徹アカウントの余白と人格に合っているか？

### `vln-gen-20260516-003`

- execution_id: `vln-exec-late_night-vln-gen-20260516-003`
- slot: `late_night`
- passcode: `J1M5V`
- image: `/Users/raindog/Documents/New project/villain_post_images/生成画像1.png`
- final_quality_status: `BLOCKED`
- review_state: `CANDIDATE_BLOCKED`
- human_approved_for_posting: `false`
- repair_action: `image_replacement_required`
- blockers: `deleted_topic_context_cooldown, topic_image_pairing_mismatch`
- warnings: `deleted_nearby_match_found`
- context terms: `none`
- context evidence verified: `false`
- topic-image fit: `MISMATCH`
- ad-like score: `0`
- native tone score: `92`
- persona fit: `93`
- deleted-nearby match: `1`

```text
話題になる服って、
だいたい服だけじゃない。

誰が着て、
どこで集まってるかまで含めて、
少し残る。

#着て稼ぐ #villain $PPP @0xmavillain J1M5V
```

Human check:
- この投稿は何を見て言っているのか？
- 本文の現実文脈は今日の状況と一致しているか？
- 画像は本文topicを本当に支えているか？
- 広告ではなくタイムライン上の観測として混ざるか？
- 鬼徹アカウントの余白と人格に合っているか？
```
