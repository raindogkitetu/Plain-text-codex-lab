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

- generated_at_jst: `2026-05-22T03:00:04+09:00`
- bridge_prompt_hash: `47af7da285831be821a99534905a03691685dfb5d2e1c61c2efbf6b31b4ca025`
- codex_outbox_status: ``
- review_state: ``
- queue_health_status: ``
- review_board_status: ``
- posting_execution_status: ``
- safe_to_review: `false`
- safe_to_post: `false`
- state_last_run: `{}`

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
    "currently_in_pilot_plan": true,
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
[
  {
    "candidate_id": "vln-stream-20260519-auto-005",
    "execution_id": "vln-exec-daytime-vln-stream-20260519-auto-005",
    "slot": "daytime",
    "passcode": "H9J6L",
    "text": "持ち物って、\n置かれた場所で\nだいたい正体が出る。\n\nきれいな写真より、\n帰ってきた後の方が本物っぽい。\n\n#着て稼ぐ #villain $PPP @0xmavillain H9J6L",
    "image_path": "villain_post_images/wearable_stock/wearable_stock_003_bag_workdesk.png",
    "image_type": "lifestyle_residue",
    "quality_status": "READY",
    "blockers": [],
    "warnings": [],
    "required_tokens_verified": true,
    "risk": "low"
  }
]
```

## data/agent_handoff_state.json

``` json

```

## data/codex_to_chatgpt_handoff.json

``` json

```

## data/villain_auto_post_pilot.json

``` json
{
  "db_name": "Villain Auto Post Pilot Plan",
  "version": "1.3.0",
  "status": "LIMITED_LIVE_EXECUTION_READY",
  "mode": "LIMITED_LIVE_EXECUTION",
  "generated_at_jst": "2026-05-22T03:00:04+09:00",
  "source_mode": "candidate_stream",
  "target_post_count": {
    "min": 3,
    "max": 3,
    "actual": 1
  },
  "live_pilot_limits": {
    "max_posts_per_day": 3,
    "posts_already_recorded_today": 0,
    "remaining_posts_today": 3,
    "cooldown_between_posts_minutes": 120
  },
  "limited_live_execution": {
    "mode_enabled": true,
    "live_execution_mode": "LIMITED_LIVE_EXECUTION",
    "execution_scope": "supervised_limited_posting_manifest",
    "posting_adapter_in_this_script": false,
    "requires_human_supervision": true,
    "max_posts_per_day": 3,
    "cooldown_between_posts_minutes": 120,
    "manual_safety": {
      "delete_if_needed": true,
      "manual_override_allowed": true,
      "post_after_publish_review": true
    },
    "hard_blocks": [
      "risk_high",
      "already_posted",
      "same_image_cooldown",
      "same_media_path",
      "same_media_sha256",
      "near_duplicate_media_phash",
      "same_prompt_family_cooldown",
      "temporal_context_unverified",
      "topic_image_pairing_mismatch",
      "topic_image_pairing_unverified",
      "deleted_candidate_blacklist",
      "deleted_image_cooldown",
      "deleted_prompt_family_cooldown",
      "deleted_text_near_match",
      "deleted_topic_context_cooldown",
      "repeated_topic_penalty",
      "required_tokens_not_verified",
      "passcode_missing",
      "passcode_not_in_db",
      "max_posts_per_day_reached"
    ]
  },
  "safety": {
    "live_posting_allowed": true,
    "x_api_write_allowed_by_this_script": false,
    "upload_media_allowed_by_this_script": false,
    "create_tweet_allowed_by_this_script": false,
    "x_write_adapter_allowed_in_limited_live_execution": true,
    "auto_posting_allowed": false,
    "would_execute_actions": [],
    "api_key_output_allowed": false,
    "env_output_allowed": false
  },
  "pilot_policy": {
    "human_supervision_required_after_post": true,
    "post_after_publish_review": true,
    "manual_override_allowed": true,
    "delete_if_needed": true,
    "note_creation_enabled": false,
    "note_seed_only": true,
    "execution_enabled": true,
    "execution_enablement_requires_separate_design": false,
    "density_priority": "slightly_higher_than_overcautious_blocking",
    "policy_alignment": {
      "human_control": true,
      "privacy_respect": true,
      "no_spam_or_deception": true,
      "no_sensitive_personal_data_output": true,
      "source": "OpenAI usage policies effective 2025-10-29"
    },
    "hard_blocks": [
      "risk_high",
      "already_posted",
      "repeated_topic_penalty",
      "same_image_cooldown",
      "same_media_path",
      "same_media_sha256",
      "near_duplicate_media_phash",
      "same_prompt_family_cooldown",
      "temporal_context_unverified",
      "topic_image_pairing_mismatch",
      "topic_image_pairing_unverified",
      "deleted_candidate_blacklist",
      "deleted_image_cooldown",
      "deleted_prompt_family_cooldown",
      "deleted_text_near_match",
      "deleted_topic_context_cooldown",
      "required_tokens_not_verified",
      "passcode_missing",
      "passcode_not_in_db",
      "novelty_too_low",
      "score_below_80",
      "max_posts_per_day_reached"
    ]
  },
  "inputs": {
    "candidate_stream": "data/villain_candidate_stream.json",
    "daily_selection": "data/villain_daily_selection.json",
    "novelty_engine": "data/villain_novelty_engine.json",
    "image_strategy": "data/villain_image_strategy.json",
    "scoring_rules": "data/villain_post_scoring_rules.json",
    "generated_candidates": "data/villain_generated_candidates.json",
    "manual_results": "data/manual_post_results.json",
    "outcomes": "data/villain_post_outcomes.json",
    "recent_media_history": "data/recent_media_history.json",
    "safe_post_executor": "scripts/safe_post_executor.py",
    "x_write_adapter": "scripts/x_write_adapter.py"
  },
  "warnings": [
    "pilot_plan_below_target_minimum",
    "limited_live_execution_manifest_only_no_x_write_adapter_called"
  ],
  "execution_manifest": [
    {
      "execution_id": "vln-exec-daytime-vln-stream-20260519-auto-005",
      "slot": "daytime",
      "source_id": "vln-stream-20260519-auto-005",
      "passcode": "H9J6L",
      "planned_publish_after_jst": "2026-05-22T13:00+09:00",
      "ready_for_limited_live_execution": true,
      "media_reuse_cooldown_ok": true,
      "manual_review_after_publish": true,
      "delete_if_needed": true,
      "x_api_write_called_by_this_script": false,
      "upload_media_called_by_this_script": false,
      "create_tweet_called_by_this_script": false
    }
  ],
  "pilot_plan": [
    {
      "slot": "daytime",
      "source": "candidate_stream",
      "source_id": "vln-stream-20260519-auto-005",
      "category": "poster_summary",
      "passcode": "H9J6L",
      "text": "持ち物って、\n置かれた場所で\nだいたい正体が出る。\n\nきれいな写真より、\n帰ってきた後の方が本物っぽい。\n\n#着て稼ぐ #villain $PPP @0xmavillain H9J6L",
      "text_preview": "持ち物って、 / 置かれた場所で / だいたい正体が出る。 / きれいな写真より、 / 帰ってきた後の方が本物っぽい。 / #着て稼ぐ #villain $PPP @0xmavillain H9J6L",
      "token_verification": {
        "required_layer": "Required Token Layer v1",
        "mandatory_footer_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "missing_before": [],
        "duplicates_before": [],
        "changed": false,
        "before_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "after_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "final_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "passcode": "H9J6L",
        "passcode_exists_in_db": true,
        "valid_after": true
      },
      "image": {
        "required": true,
        "ready": true,
        "file_path": "villain_post_images/wearable_stock/wearable_stock_003_bag_workdesk.png",
        "image_type": "lifestyle_residue",
        "match_score": 92,
        "rights_notes": "maintenance refill from approved shop wearable stock; not raw shop image.",
        "absolute_path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_003_bag_workdesk.png"
      },
      "score": 90,
      "risk": "low",
      "novelty_score": 74,
      "raw_novelty_score": 78,
      "remixability_score": 72,
      "remixability": {
        "source": "candidate_score",
        "signals": [],
        "components": {}
      },
      "media_deduplication": {
        "signature": {
          "path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_003_bag_workdesk.png",
          "sha256": "5e2b6a199e9ba18f149d24337d510a7d56f1e314cf4f2178127709d37ccfc28f",
          "perceptual_hash": "0000681f97c76b31",
          "prompt_family": "lifestyle_residue_wearable_stock_003_bag_workdesk",
          "composition": "",
          "layout": "",
          "image_type": "lifestyle_residue"
        },
        "blockers": [],
        "matches": [],
        "cooldown_days": 7
      },
      "context_mismatch_gate": {
        "blockers": [],
        "context_check": {
          "terms": [],
          "temporal_terms": [],
          "event_terms": [],
          "context_evidence_verified": false,
          "requires_evidence": false
        },
        "pairing_check": {
          "topic_groups": [],
          "image_metadata": "villain_post_images/wearable_stock/wearable_stock_003_bag_workdesk.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_003_bag_workdesk.png lifestyle_residue",
          "matched_image_terms": {}
        }
      },
      "deleted_learning_gate": {
        "blockers": [],
        "matches": []
      },
      "saturation_flags": [
        "repeated_structure"
      ],
      "pilot_score": 284,
      "eligible": true,
      "blockers": [],
      "warnings": [],
      "reason": "Auto-refilled by maintenance from wearable_stock_003_bag_workdesk; no reality/event claim.",
      "expected_type": "residual_growth",
      "fallback_action": "hold_for_night_if_context_is_too_heavy",
      "quality_review": {
        "candidate_id": "vln-stream-20260519-auto-005",
        "execution_id": "",
        "slot": "daytime",
        "passcode": "H9J6L",
        "image": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_003_bag_workdesk.png",
        "text": "持ち物って、\n置かれた場所で\nだいたい正体が出る。\n\nきれいな写真より、\n帰ってきた後の方が本物っぽい。\n\n#着て稼ぐ #villain $PPP @0xmavillain H9J6L",
        "text_preview": "持ち物って、 / 置かれた場所で / だいたい正体が出る。 / きれいな写真より、 / 帰ってきた後の方が本物っぽい。 / #着て稼ぐ #villain $PPP @0xmavillain H9J6L",
        "final_quality_status": "READY",
        "blockers": [],
        "warnings": [],
        "context_terms": [],
        "context_evidence": {
          "verified": false,
          "requires_evidence": false,
          "core_question": "この投稿は何を見て言っているのか？"
        },
        "topic_image_fit": {
          "status": "OK",
          "checks": {
            "topic_groups": [],
            "image_metadata": "villain_post_images/wearable_stock/wearable_stock_003_bag_workdesk.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_003_bag_workdesk.png lifestyle_residue",
            "matched_image_terms": {}
          }
        },
        "ad_like_score": 0,
        "native_tone_score": 77,
        "persona_fit": 78,
        "deleted_nearby_match": [],
        "human_check_checklist": [
          "この投稿は何を見て言っているのか？",
          "本文の現実文脈は今日の状況と一致しているか？",
          "画像は本文topicを本当に支えているか？",
          "広告ではなくタイムライン上の観測として混ざるか？",
          "鬼徹アカウントの余白と人格に合っているか？"
        ]
      },
      "planned_publish_after_jst": "2026-05-22T13:00+09:00",
      "post_after_publish_review": true,
      "manual_override_allowed": true,
      "delete_if_needed": true,
      "required_tokens_verified": true,
      "execution_gate": {
        "max_posts_per_day_ok": true,
        "cooldown_between_posts_minutes": 120,
        "risk_not_high": true,
        "already_posted_false": true,
        "same_image_cooldown_ok": true,
        "media_reuse_cooldown_ok": true,
        "context_evidence_ok": true,
        "topic_image_pairing_ok": true,
        "deleted_learning_ok": true,
        "repeated_topic_penalty_ok": true,
        "required_tokens_verified": true
      },
      "post_publish_learning_plan": {
        "analysis_after_hours": 24,
        "metrics": [
          "impressions",
          "likes",
          "reposts",
          "replies",
          "profile_clicks"
        ],
        "learning_focus": [
          "residual_growth",
          "profile_clicks",
          "repost_reuse",
          "remixability"
        ]
      },
      "note_seed": {
        "why_posted": "Auto-refilled by maintenance from wearable_stock_003_bag_workdesk; no reality/event claim.",
        "expected_reaction": "residual_growth",
        "human_observation_pending": true,
        "lesson_for_later": "Record actual X reaction after posting; do not draft note yet."
      }
    }
  ],
  "rejected_or_blocked_count": 12,
  "rejected_or_blocked_preview": [
    {
      "slot": "daytime",
      "source": "candidate_stream",
      "source_id": "vln-stream-20260519-stock-001",
      "category": "culture_observer",
      "passcode": "C14QB",
      "text": "机に置いた瞬間、\nグッズじゃなくて、\n生活の一部になる。\n\n広告より、\n使われた跡の方が強い。\n\n#着て稼ぐ #villain $PPP @0xmavillain C14QB",
      "text_preview": "机に置いた瞬間、 / グッズじゃなくて、 / 生活の一部になる。 / 広告より、 / 使われた跡の方が強い。 / #着て稼ぐ #villain $PPP @0xmavillain C14QB",
      "token_verification": {
        "required_layer": "Required Token Layer v1",
        "mandatory_footer_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "missing_before": [],
        "duplicates_before": [],
        "changed": false,
        "before_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "after_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "final_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "passcode": "C14QB",
        "passcode_exists_in_db": true,
        "valid_after": true
      },
      "image": {
        "required": true,
        "ready": true,
        "file_path": "villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
        "image_type": "lifestyle_residue_photo",
        "match_score": 94,
        "rights_notes": "公式ショップ実物グッズを参照した生活痕/着用画像。商品画像そのままではない。",
        "absolute_path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png"
      },
      "score": 92,
      "risk": "low",
      "novelty_score": 80,
      "raw_novelty_score": 80,
      "remixability_score": 74,
      "remixability": {
        "source": "candidate_score",
        "signals": [],
        "components": {}
      },
      "media_deduplication": {
        "signature": {
          "path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
          "sha256": "536ed31d6942711bf8ef87c8d6c2c9ee189732bb5df6615fd4d8ffdd77aa5fc2",
          "perceptual_hash": "1f19113034302030",
          "prompt_family": "lifestyle_residue_photo_wearable_stock_010_thermos_workdesk",
          "composition": "",
          "layout": "",
          "image_type": "lifestyle_residue_photo"
        },
        "blockers": [
          "near_duplicate_media_phash",
          "same_media_path",
          "same_media_sha256",
          "same_prompt_family_cooldown"
        ],
        "matches": [
          {
            "tweet_id": "2056897607105192401",
            "url": "https://x.com/raindog_kitetu/status/2056897607105192401",
            "posted_at_jst": "2026-05-20T09:31:48+09:00",
            "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
            "hamming_distance": 0,
            "reasons": [
              "near_duplicate_media_phash",
              "same_media_path",
              "same_media_sha256",
              "same_prompt_family_cooldown"
            ]
          }
        ],
        "cooldown_days": 7
      },
      "context_mismatch_gate": {
        "blockers": [],
        "context_check": {
          "terms": [],
          "temporal_terms": [],
          "event_terms": [],
          "context_evidence_verified": false,
          "requires_evidence": false
        },
        "pairing_check": {
          "topic_groups": [],
          "image_metadata": "villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png lifestyle_residue_photo",
          "matched_image_terms": {}
        }
      },
      "deleted_learning_gate": {
        "blockers": [],
        "matches": []
      },
      "saturation_flags": [],
      "pilot_score": 284,
      "eligible": false,
      "blockers": [
        "near_duplicate_media_phash",
        "same_media_path",
        "same_media_sha256",
        "same_prompt_family_cooldown"
      ],
      "warnings": [
        "recent_media_reuse_match_found"
      ],
      "reason": "Thermos desk residue. No temporal/event claim.",
      "expected_type": "residual_growth_or_profile_pull",
      "fallback_action": "hold_for_night_if_context_is_too_heavy",
      "quality_review": {
        "candidate_id": "vln-stream-20260519-stock-001",
        "execution_id": "",
        "slot": "daytime",
        "passcode": "C14QB",
        "image": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
        "text": "机に置いた瞬間、\nグッズじゃなくて、\n生活の一部になる。\n\n広告より、\n使われた跡の方が強い。\n\n#着て稼ぐ #villain $PPP @0xmavillain C14QB",
        "text_preview": "机に置いた瞬間、 / グッズじゃなくて、 / 生活の一部になる。 / 広告より、 / 使われた跡の方が強い。 / #着て稼ぐ #villain $PPP @0xmavillain C14QB",
        "final_quality_status": "READY",
        "blockers": [],
        "warnings": [],
        "context_terms": [],
        "context_evidence": {
          "verified": false,
          "requires_evidence": false,
          "core_question": "この投稿は何を見て言っているのか？"
        },
        "topic_image_fit": {
          "status": "OK",
          "checks": {
            "topic_groups": [],
            "image_metadata": "villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png lifestyle_residue_photo",
            "matched_image_terms": {}
          }
        },
        "ad_like_score": 0,
        "native_tone_score": 72,
        "persona_fit": 78,
        "deleted_nearby_match": [],
        "human_check_checklist": [
          "この投稿は何を見て言っているのか？",
          "本文の現実文脈は今日の状況と一致しているか？",
          "画像は本文topicを本当に支えているか？",
          "広告ではなくタイムライン上の観測として混ざるか？",
          "鬼徹アカウントの余白と人格に合っているか？"
        ]
      }
    },
    {
      "slot": "daytime",
      "source": "candidate_stream",
      "source_id": "vln-stream-20260519-stock-002",
      "category": "poster_summary",
      "passcode": "DKLS8",
      "text": "持ち物って、\n置かれた場所で\nだいたい正体が出る。\n\nきれいな写真より、\n帰ってきた後の方が本物っぽい。\n\n#着て稼ぐ #villain $PPP @0xmavillain DKLS8",
      "text_preview": "持ち物って、 / 置かれた場所で / だいたい正体が出る。 / きれいな写真より、 / 帰ってきた後の方が本物っぽい。 / #着て稼ぐ #villain $PPP @0xmavillain DKLS8",
      "token_verification": {
        "required_layer": "Required Token Layer v1",
        "mandatory_footer_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "missing_before": [],
        "duplicates_before": [],
        "changed": false,
        "before_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "after_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "final_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "passcode": "DKLS8",
        "passcode_exists_in_db": true,
        "valid_after": true
      },
      "image": {
        "required": true,
        "ready": true,
        "file_path": "villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
        "image_type": "lifestyle_residue_photo",
        "match_score": 94,
        "rights_notes": "公式ショップ実物グッズを参照した生活痕/着用画像。商品画像そのままではない。",
        "absolute_path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png"
      },
      "score": 92,
      "risk": "low",
      "novelty_score": 76,
      "raw_novelty_score": 80,
      "remixability_score": 74,
      "remixability": {
        "source": "candidate_score",
        "signals": [],
        "components": {}
      },
      "media_deduplication": {
        "signature": {
          "path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
          "sha256": "4de3bef0230faf0c5c6a5888df83ad45c6ce5afe921dceca4da165df5e4c2ad0",
          "perceptual_hash": "c3c7819168602021",
          "prompt_family": "lifestyle_residue_photo_wearable_stock_011_bag_entryway",
          "composition": "",
          "layout": "",
          "image_type": "lifestyle_residue_photo"
        },
        "blockers": [
          "near_duplicate_media_phash",
          "same_media_path",
          "same_media_sha256",
          "same_prompt_family_cooldown"
        ],
        "matches": [
          {
            "tweet_id": "2056736652442353980",
            "url": "https://x.com/raindog_kitetu/status/2056736652442353980",
            "posted_at_jst": "2026-05-19T23:00:05+09:00",
            "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
            "hamming_distance": 0,
            "reasons": [
              "near_duplicate_media_phash",
              "same_media_path",
              "same_media_sha256",
              "same_prompt_family_cooldown"
            ]
          }
        ],
        "cooldown_days": 7
      },
      "context_mismatch_gate": {
        "blockers": [],
        "context_check": {
          "terms": [],
          "temporal_terms": [],
          "event_terms": [],
          "context_evidence_verified": false,
          "requires_evidence": false
        },
        "pairing_check": {
          "topic_groups": [],
          "image_metadata": "villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png lifestyle_residue_photo",
          "matched_image_terms": {}
        }
      },
      "deleted_learning_gate": {
        "blockers": [],
        "matches": []
      },
      "saturation_flags": [
        "repeated_structure"
      ],
      "pilot_score": 290,
      "eligible": false,
      "blockers": [
        "near_duplicate_media_phash",
        "same_media_path",
        "same_media_sha256",
        "same_prompt_family_cooldown"
      ],
      "warnings": [
        "recent_media_reuse_match_found"
      ],
      "reason": "Bag entryway residue. No temporal/event claim.",
      "expected_type": "residual_growth",
      "fallback_action": "hold_for_night_if_context_is_too_heavy",
      "quality_review": {
        "candidate_id": "vln-stream-20260519-stock-002",
        "execution_id": "",
        "slot": "daytime",
        "passcode": "DKLS8",
        "image": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
        "text": "持ち物って、\n置かれた場所で\nだいたい正体が出る。\n\nきれいな写真より、\n帰ってきた後の方が本物っぽい。\n\n#着て稼ぐ #villain $PPP @0xmavillain DKLS8",
        "text_preview": "持ち物って、 / 置かれた場所で / だいたい正体が出る。 / きれいな写真より、 / 帰ってきた後の方が本物っぽい。 / #着て稼ぐ #villain $PPP @0xmavillain DKLS8",
        "final_quality_status": "READY",
        "blockers": [],
        "warnings": [],
        "context_terms": [],
        "context_evidence": {
          "verified": false,
          "requires_evidence": false,
          "core_question": "この投稿は何を見て言っているのか？"
        },
        "topic_image_fit": {
          "status": "OK",
          "checks": {
            "topic_groups": [],
            "image_metadata": "villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png lifestyle_residue_photo",
            "matched_image_terms": {}
          }
        },
        "ad_like_score": 0,
        "native_tone_score": 77,
        "persona_fit": 78,
        "deleted_nearby_match": [],
        "human_check_checklist": [
          "この投稿は何を見て言っているのか？",
          "本文の現実文脈は今日の状況と一致しているか？",
          "画像は本文topicを本当に支えているか？",
          "広告ではなくタイムライン上の観測として混ざるか？",
          "鬼徹アカウントの余白と人格に合っているか？"
        ]
      }
    },
    {
      "slot": "daytime",
      "source": "candidate_stream",
      "source_id": "vln-stream-20260519-stock-003",
      "category": "culture_observer",
      "passcode": "GQ2UB",
      "text": "服は主張しすぎると、\n急に広告になる。\n\n少しだけ見えて、\n勝手に残るくらいがちょうどいい。\n\n#着て稼ぐ #villain $PPP @0xmavillain GQ2UB",
      "text_preview": "服は主張しすぎると、 / 急に広告になる。 / 少しだけ見えて、 / 勝手に残るくらいがちょうどいい。 / #着て稼ぐ #villain $PPP @0xmavillain GQ2UB",
      "token_verification": {
        "required_layer": "Required Token Layer v1",
        "mandatory_footer_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "missing_before": [],
        "duplicates_before": [],
        "changed": false,
        "before_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "after_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "final_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "passcode": "GQ2UB",
        "passcode_exists_in_db": true,
        "valid_after": true
      },
      "image": {
        "required": true,
        "ready": true,
        "file_path": "villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png",
        "image_type": "wearable_lifestyle_photo",
        "match_score": 94,
        "rights_notes": "公式ショップ実物グッズを参照した生活痕/着用画像。商品画像そのままではない。",
        "absolute_path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png"
      },
      "score": 92,
      "risk": "low",
      "novelty_score": 72,
      "raw_novelty_score": 80,
      "remixability_score": 74,
      "remixability": {
        "source": "candidate_score",
        "signals": [],
        "components": {}
      },
      "media_deduplication": {
        "signature": {
          "path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png",
          "sha256": "c08bd7a3905ae1a98aa927b96794a1690eefe2dc3535c25d17ca9f476821daa4",
          "perceptual_hash": "263228e4d8c8b8f8",
          "prompt_family": "wearable_lifestyle_photo_wearable_stock_012_hoodie_mirror_person",
          "composition": "",
          "layout": "",
          "image_type": "wearable_lifestyle_photo"
        },
        "blockers": [
          "near_duplicate_media_phash",
          "same_media_path",
          "same_media_sha256"
        ],
        "matches": [
          {
            "tweet_id": "2057473911550521382",
            "url": "https://x.com/raindog_kitetu/status/2057473911550521382",
            "posted_at_jst": "2026-05-21T23:49:41+09:00",
            "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png",
            "hamming_distance": 0,
            "reasons": [
              "near_duplicate_media_phash",
              "same_media_path",
              "same_media_sha256"
            ]
          }
        ],
        "cooldown_days": 7
      },
      "context_mismatch_gate": {
        "blockers": [],
        "context_check": {
          "terms": [],
          "temporal_terms": [],
          "event_terms": [],
          "context_evidence_verified": false,
          "requires_evidence": false
        },
        "pairing_check": {
          "topic_groups": [],
          "image_metadata": "villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png wearable_lifestyle_photo",
          "matched_image_terms": {}
        }
      },
      "deleted_learning_gate": {
        "blockers": [],
        "matches": []
      },
      "saturation_flags": [
        "same_black_hoodie"
      ],
      "pilot_score": 276,
      "eligible": false,
      "blockers": [
        "near_duplicate_media_phash",
        "same_media_path",
        "same_media_sha256"
      ],
      "warnings": [
        "recent_media_reuse_match_found"
      ],
      "reason": "Hoodie mirror person. No temporal/event claim.",
      "expected_type": "residual_growth_or_profile_pull",
      "fallback_action": "hold_for_night_if_context_is_too_heavy",
      "quality_review": {
        "candidate_id": "vln-stream-20260519-stock-003",
        "execution_id": "",
        "slot": "daytime",
        "passcode": "GQ2UB",
        "image": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png",
        "text": "服は主張しすぎると、\n急に広告になる。\n\n少しだけ見えて、\n勝手に残るくらいがちょうどいい。\n\n#着て稼ぐ #villain $PPP @0xmavillain GQ2UB",
        "text_preview": "服は主張しすぎると、 / 急に広告になる。 / 少しだけ見えて、 / 勝手に残るくらいがちょうどいい。 / #着て稼ぐ #villain $PPP @0xmavillain GQ2UB",
        "final_quality_status": "READY",
        "blockers": [],
        "warnings": [],
        "context_terms": [],
        "context_evidence": {
          "verified": false,
          "requires_evidence": false,
          "core_question": "この投稿は何を見て言っているのか？"
        },
        "topic_image_fit": {
          "status": "OK",
          "checks": {
            "topic_groups": [],
            "image_metadata": "villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png wearable_lifestyle_photo",
            "matched_image_terms": {}
          }
        },
        "ad_like_score": 0,
        "native_tone_score": 82,
        "persona_fit": 83,
        "deleted_nearby_match": [],
        "human_check_checklist": [
          "この投稿は何を見て言っているのか？",
          "本文の現実文脈は今日の状況と一致しているか？",
          "画像は本文topicを本当に支えているか？",
          "広告ではなくタイムライン上の観測として混ざるか？",
          "鬼徹アカウントの余白と人格に合っているか？"
        ]
      }
    },
    {
      "slot": "daytime",
      "source": "candidate_stream",
      "source_id": "vln-stream-20260519-auto-004",
      "category": "culture_observer",
      "passcode": "F3X7M",
      "text": "机に置いた瞬間、\nグッズじゃなくて、\n生活の一部になる。\n\n広告より、\n使われた跡の方が強い。\n\n#着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "text_preview": "机に置いた瞬間、 / グッズじゃなくて、 / 生活の一部になる。 / 広告より、 / 使われた跡の方が強い。 / #着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "token_verification": {
        "required_layer": "Required Token Layer v1",
        "mandatory_footer_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "missing_before": [],
        "duplicates_before": [],
        "changed": false,
        "before_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "after_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "final_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "passcode": "F3X7M",
        "passcode_exists_in_db": true,
        "valid_after": true
      },
      "image": {
        "required": true,
        "ready": true,
        "file_path": "villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
        "image_type": "lifestyle_residue",
        "match_score": 92,
        "rights_notes": "maintenance refill from approved shop wearable stock; not raw shop image.",
        "absolute_path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png"
      },
      "score": 90,
      "risk": "low",
      "novelty_score": 78,
      "raw_novelty_score": 78,
      "remixability_score": 72,
      "remixability": {
        "source": "candidate_score",
        "signals": [],
        "components": {}
      },
      "media_deduplication": {
        "signature": {
          "path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
          "sha256": "9257441a33698225b81a8439603a5f1402dbfff677bc1ed4199c8f4cbfde7715",
          "perceptual_hash": "0000c013c3c90d17",
          "prompt_family": "lifestyle_residue_wearable_stock_006_thermos_desk_residue",
          "composition": "",
          "layout": "",
          "image_type": "lifestyle_residue"
        },
        "blockers": [
          "near_duplicate_media_phash",
          "same_media_path",
          "same_media_sha256",
          "same_prompt_family_cooldown"
        ],
        "matches": [
          {
            "tweet_id": "2057067435744997644",
            "url": "https://x.com/raindog_kitetu/status/2057067435744997644",
            "posted_at_jst": "2026-05-20T20:54:30+09:00",
            "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
            "hamming_distance": 0,
            "reasons": [
              "near_duplicate_media_phash",
              "same_media_path",
              "same_media_sha256",
              "same_prompt_family_cooldown"
            ]
          }
        ],
        "cooldown_days": 7
      },
      "context_mismatch_gate": {
        "blockers": [],
        "context_check": {
          "terms": [],
          "temporal_terms": [],
          "event_terms": [],
          "context_evidence_verified": false,
          "requires_evidence": false
        },
        "pairing_check": {
          "topic_groups": [],
          "image_metadata": "villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png lifestyle_residue",
          "matched_image_terms": {}
        }
      },
      "deleted_learning_gate": {
        "blockers": [
          "deleted_candidate_blacklist"
        ],
        "matches": [
          {
            "tweet_id": "2057067435744997644",
            "execution_id": "vln-exec-daytime-vln-stream-20260519-auto-004",
            "candidate_id": "vln-stream-20260519-auto-004",
            "image_used": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
            "prompt_family": "lifestyle_residue_wearable_stock_006_thermos_desk_residue",
            "topic_cluster": "culture_observer_apparel_context",
            "delete_reason": "Deleted by human: image quality was terrible; flat product composite did not fit account quality bar.",
            "reasons": [
              "deleted_candidate_blacklist"
            ]
          }
        ]
      },
      "saturation_flags": [],
      "pilot_score": 278,
      "eligible": false,
      "blockers": [
        "near_duplicate_media_phash",
        "same_media_path",
        "same_media_sha256",
        "same_prompt_family_cooldown"
      ],
      "warnings": [
        "deleted_nearby_match_found",
        "near_deleted_or_dropped_post",
        "recent_media_reuse_match_found"
      ],
      "reason": "Auto-refilled by maintenance from wearable_stock_006_thermos_desk_residue; no reality/event claim.",
      "expected_type": "residual_growth_or_profile_pull",
      "fallback_action": "hold_for_night_if_context_is_too_heavy",
      "quality_review": {
        "candidate_id": "vln-stream-20260519-auto-004",
        "execution_id": "",
        "slot": "daytime",
        "passcode": "F3X7M",
        "image": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
        "text": "机に置いた瞬間、\nグッズじゃなくて、\n生活の一部になる。\n\n広告より、\n使われた跡の方が強い。\n\n#着て稼ぐ #villain $PPP @0xmavillain F3X7M",
        "text_preview": "机に置いた瞬間、 / グッズじゃなくて、 / 生活の一部になる。 / 広告より、 / 使われた跡の方が強い。 / #着て稼ぐ #villain $PPP @0xmavillain F3X7M",
        "final_quality_status": "REVIEW_REQUIRED",
        "blockers": [],
        "warnings": [
          "deleted_nearby_match_found"
        ],
        "context_terms": [],
        "context_evidence": {
          "verified": false,
          "requires_evidence": false,
          "core_question": "この投稿は何を見て言っているのか？"
        },
        "topic_image_fit": {
          "status": "OK",
          "checks": {
            "topic_groups": [],
            "image_metadata": "villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png lifestyle_residue",
            "matched_image_terms": {}
          }
        },
        "ad_like_score": 0,
        "native_tone_score": 72,
        "persona_fit": 78,
        "deleted_nearby_match": [
          {
            "tweet_id": "2057067435744997644",
            "execution_id": "vln-exec-daytime-vln-stream-20260519-auto-004",
            "candidate_id": "vln-stream-20260519-auto-004",
            "image_used": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
            "prompt_family": "lifestyle_residue_wearable_stock_006_thermos_desk_residue",
            "topic_cluster": "culture_observer_apparel_context",
            "delete_reason": "Deleted by human: image quality was terrible; flat product composite did not fit account quality bar.",
            "reasons": [
              "deleted_candidate_blacklist"
            ]
          }
        ],
        "human_check_checklist": [
          "この投稿は何を見て言っているのか？",
          "本文の現実文脈は今日の状況と一致しているか？",
          "画像は本文topicを本当に支えているか？",
          "広告ではなくタイムライン上の観測として混ざるか？",
          "鬼徹アカウントの余白と人格に合っているか？"
        ]
      }
    },
    {
      "slot": "night",
      "source": "candidate_stream",
      "source_id": "vln-stream-20260519-stock-001",
      "category": "culture_observer",
      "passcode": "C14QB",
      "text": "机に置いた瞬間、\nグッズじゃなくて、\n生活の一部になる。\n\n広告より、\n使われた跡の方が強い。\n\n#着て稼ぐ #villain $PPP @0xmavillain C14QB",
      "text_preview": "机に置いた瞬間、 / グッズじゃなくて、 / 生活の一部になる。 / 広告より、 / 使われた跡の方が強い。 / #着て稼ぐ #villain $PPP @0xmavillain C14QB",
      "token_verification": {
        "required_layer": "Required Token Layer v1",
        "mandatory_footer_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "missing_before": [],
        "duplicates_before": [],
        "changed": false,
        "before_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "after_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "final_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "passcode": "C14QB",
        "passcode_exists_in_db": true,
        "valid_after": true
      },
      "image": {
        "required": true,
        "ready": true,
        "file_path": "villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
        "image_type": "lifestyle_residue_photo",
        "match_score": 94,
        "rights_notes": "公式ショップ実物グッズを参照した生活痕/着用画像。商品画像そのままではない。",
        "absolute_path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png"
      },
      "score": 92,
      "risk": "low",
      "novelty_score": 80,
      "raw_novelty_score": 80,
      "remixability_score": 74,
      "remixability": {
        "source": "candidate_score",
        "signals": [],
        "components": {}
      },
      "media_deduplication": {
        "signature": {
          "path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
          "sha256": "536ed31d6942711bf8ef87c8d6c2c9ee189732bb5df6615fd4d8ffdd77aa5fc2",
          "perceptual_hash": "1f19113034302030",
          "prompt_family": "lifestyle_residue_photo_wearable_stock_010_thermos_workdesk",
          "composition": "",
          "layout": "",
          "image_type": "lifestyle_residue_photo"
        },
        "blockers": [
          "near_duplicate_media_phash",
          "same_media_path",
          "same_media_sha256",
          "same_prompt_family_cooldown"
        ],
        "matches": [
          {
            "tweet_id": "2056897607105192401",
            "url": "https://x.com/raindog_kitetu/status/2056897607105192401",
            "posted_at_jst": "2026-05-20T09:31:48+09:00",
            "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
            "hamming_distance": 0,
            "reasons": [
              "near_duplicate_media_phash",
              "same_media_path",
              "same_media_sha256",
              "same_prompt_family_cooldown"
            ]
          }
        ],
        "cooldown_days": 7
      },
      "context_mismatch_gate": {
        "blockers": [],
        "context_check": {
          "terms": [],
          "temporal_terms": [],
          "event_terms": [],
          "context_evidence_verified": false,
          "requires_evidence": false
        },
        "pairing_check": {
          "topic_groups": [],
          "image_metadata": "villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png lifestyle_residue_photo",
          "matched_image_terms": {}
        }
      },
      "deleted_learning_gate": {
        "blockers": [],
        "matches": []
      },
      "saturation_flags": [],
      "pilot_score": 294,
      "eligible": false,
      "blockers": [
        "near_duplicate_media_phash",
        "same_media_path",
        "same_media_sha256",
        "same_prompt_family_cooldown"
      ],
      "warnings": [
        "recent_media_reuse_match_found"
      ],
      "reason": "Thermos desk residue. No temporal/event claim.",
      "expected_type": "residual_growth_or_profile_pull",
      "fallback_action": "fallback_to_poster_summary_image_ready",
      "quality_review": {
        "candidate_id": "vln-stream-20260519-stock-001",
        "execution_id": "",
        "slot": "night",
        "passcode": "C14QB",
        "image": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
        "text": "机に置いた瞬間、\nグッズじゃなくて、\n生活の一部になる。\n\n広告より、\n使われた跡の方が強い。\n\n#着て稼ぐ #villain $PPP @0xmavillain C14QB",
        "text_preview": "机に置いた瞬間、 / グッズじゃなくて、 / 生活の一部になる。 / 広告より、 / 使われた跡の方が強い。 / #着て稼ぐ #villain $PPP @0xmavillain C14QB",
        "final_quality_status": "READY",
        "blockers": [],
        "warnings": [],
        "context_terms": [],
        "context_evidence": {
          "verified": false,
          "requires_evidence": false,
          "core_question": "この投稿は何を見て言っているのか？"
        },
        "topic_image_fit": {
          "status": "OK",
          "checks": {
            "topic_groups": [],
            "image_metadata": "villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png lifestyle_residue_photo",
            "matched_image_terms": {}
          }
        },
        "ad_like_score": 0,
        "native_tone_score": 72,
        "persona_fit": 78,
        "deleted_nearby_match": [],
        "human_check_checklist": [
          "この投稿は何を見て言っているのか？",
          "本文の現実文脈は今日の状況と一致しているか？",
          "画像は本文topicを本当に支えているか？",
          "広告ではなくタイムライン上の観測として混ざるか？",
          "鬼徹アカウントの余白と人格に合っているか？"
        ]
      }
    },
    {
      "slot": "night",
      "source": "candidate_stream",
      "source_id": "vln-stream-20260519-stock-002",
      "category": "poster_summary",
      "passcode": "DKLS8",
      "text": "持ち物って、\n置かれた場所で\nだいたい正体が出る。\n\nきれいな写真より、\n帰ってきた後の方が本物っぽい。\n\n#着て稼ぐ #villain $PPP @0xmavillain DKLS8",
      "text_preview": "持ち物って、 / 置かれた場所で / だいたい正体が出る。 / きれいな写真より、 / 帰ってきた後の方が本物っぽい。 / #着て稼ぐ #villain $PPP @0xmavillain DKLS8",
      "token_verification": {
        "required_layer": "Required Token Layer v1",
        "mandatory_footer_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "missing_before": [],
        "duplicates_before": [],
        "changed": false,
        "before_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "after_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "final_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "passcode": "DKLS8",
        "passcode_exists_in_db": true,
        "valid_after": true
      },
      "image": {
        "required": true,
        "ready": true,
        "file_path": "villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
        "image_type": "lifestyle_residue_photo",
        "match_score": 94,
        "rights_notes": "公式ショップ実物グッズを参照した生活痕/着用画像。商品画像そのままではない。",
        "absolute_path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png"
      },
      "score": 92,
      "risk": "low",
      "novelty_score": 76,
      "raw_novelty_score": 80,
      "remixability_score": 74,
      "remixability": {
        "source": "candidate_score",
        "signals": [],
        "components": {}
      },
      "media_deduplication": {
        "signature": {
          "path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
          "sha256": "4de3bef0230faf0c5c6a5888df83ad45c6ce5afe921dceca4da165df5e4c2ad0",
          "perceptual_hash": "c3c7819168602021",
          "prompt_family": "lifestyle_residue_photo_wearable_stock_011_bag_entryway",
          "composition": "",
          "layout": "",
          "image_type": "lifestyle_residue_photo"
        },
        "blockers": [
          "near_duplicate_media_phash",
          "same_media_path",
          "same_media_sha256",
          "same_prompt_family_cooldown"
        ],
        "matches": [
          {
            "tweet_id": "2056736652442353980",
            "url": "https://x.com/raindog_kitetu/status/2056736652442353980",
            "posted_at_jst": "2026-05-19T23:00:05+09:00",
            "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
            "hamming_distance": 0,
            "reasons": [
              "near_duplicate_media_phash",
              "same_media_path",
              "same_media_sha256",
              "same_prompt_family_cooldown"
            ]
          }
        ],
        "cooldown_days": 7
      },
      "context_mismatch_gate": {
        "blockers": [],
        "context_check": {
          "terms": [],
          "temporal_terms": [],
          "event_terms": [],
          "context_evidence_verified": false,
          "requires_evidence": false
        },
        "pairing_check": {
          "topic_groups": [],
          "image_metadata": "villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png lifestyle_residue_photo",
          "matched_image_terms": {}
        }
      },
      "deleted_learning_gate": {
        "blockers": [],
        "matches": []
      },
      "saturation_flags": [
        "repeated_structure"
      ],
      "pilot_score": 290,
      "eligible": false,
      "blockers": [
        "near_duplicate_media_phash",
        "same_media_path",
        "same_media_sha256",
        "same_prompt_family_cooldown"
      ],
      "warnings": [
        "recent_media_reuse_match_found"
      ],
      "reason": "Bag entryway residue. No temporal/event claim.",
      "expected_type": "residual_growth",
      "fallback_action": "fallback_to_poster_summary_image_ready",
      "quality_review": {
        "candidate_id": "vln-stream-20260519-stock-002",
        "execution_id": "",
        "slot": "night",
        "passcode": "DKLS8",
        "image": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
        "text": "持ち物って、\n置かれた場所で\nだいたい正体が出る。\n\nきれいな写真より、\n帰ってきた後の方が本物っぽい。\n\n#着て稼ぐ #villain $PPP @0xmavillain DKLS8",
        "text_preview": "持ち物って、 / 置かれた場所で / だいたい正体が出る。 / きれいな写真より、 / 帰ってきた後の方が本物っぽい。 / #着て稼ぐ #villain $PPP @0xmavillain DKLS8",
        "final_quality_status": "READY",
        "blockers": [],
        "warnings": [],
        "context_terms": [],
        "context_evidence": {
          "verified": false,
          "requires_evidence": false,
          "core_question": "この投稿は何を見て言っているのか？"
        },
        "topic_image_fit": {
          "status": "OK",
          "checks": {
            "topic_groups": [],
            "image_metadata": "villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png lifestyle_residue_photo",
            "matched_image_terms": {}
          }
        },
        "ad_like_score": 0,
        "native_tone_score": 77,
        "persona_fit": 78,
        "deleted_nearby_match": [],
        "human_check_checklist": [
          "この投稿は何を見て言っているのか？",
          "本文の現実文脈は今日の状況と一致しているか？",
          "画像は本文topicを本当に支えているか？",
          "広告ではなくタイムライン上の観測として混ざるか？",
          "鬼徹アカウントの余白と人格に合っているか？"
        ]
      }
    },
    {
      "slot": "night",
      "source": "candidate_stream",
      "source_id": "vln-stream-20260519-stock-003",
      "category": "culture_observer",
      "passcode": "GQ2UB",
      "text": "服は主張しすぎると、\n急に広告になる。\n\n少しだけ見えて、\n勝手に残るくらいがちょうどいい。\n\n#着て稼ぐ #villain $PPP @0xmavillain GQ2UB",
      "text_preview": "服は主張しすぎると、 / 急に広告になる。 / 少しだけ見えて、 / 勝手に残るくらいがちょうどいい。 / #着て稼ぐ #villain $PPP @0xmavillain GQ2UB",
      "token_verification": {
        "required_layer": "Required Token Layer v1",
        "mandatory_footer_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "missing_before": [],
        "duplicates_before": [],
        "changed": false,
        "before_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "after_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "final_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "passcode": "GQ2UB",
        "passcode_exists_in_db": true,
        "valid_after": true
      },
      "image": {
        "required": true,
        "ready": true,
        "file_path": "villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png",
        "image_type": "wearable_lifestyle_photo",
        "match_score": 94,
        "rights_notes": "公式ショップ実物グッズを参照した生活痕/着用画像。商品画像そのままではない。",
        "absolute_path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png"
      },
      "score": 92,
      "risk": "low",
      "novelty_score": 72,
      "raw_novelty_score": 80,
      "remixability_score": 74,
      "remixability": {
        "source": "candidate_score",
        "signals": [],
        "components": {}
      },
      "media_deduplication": {
        "signature": {
          "path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png",
          "sha256": "c08bd7a3905ae1a98aa927b96794a1690eefe2dc3535c25d17ca9f476821daa4",
          "perceptual_hash": "263228e4d8c8b8f8",
          "prompt_family": "wearable_lifestyle_photo_wearable_stock_012_hoodie_mirror_person",
          "composition": "",
          "layout": "",
          "image_type": "wearable_lifestyle_photo"
        },
        "blockers": [
          "near_duplicate_media_phash",
          "same_media_path",
          "same_media_sha256"
        ],
        "matches": [
          {
            "tweet_id": "2057473911550521382",
            "url": "https://x.com/raindog_kitetu/status/2057473911550521382",
            "posted_at_jst": "2026-05-21T23:49:41+09:00",
            "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png",
            "hamming_distance": 0,
            "reasons": [
              "near_duplicate_media_phash",
              "same_media_path",
              "same_media_sha256"
            ]
          }
        ],
        "cooldown_days": 7
      },
      "context_mismatch_gate": {
        "blockers": [],
        "context_check": {
          "terms": [],
          "temporal_terms": [],
          "event_terms": [],
          "context_evidence_verified": false,
          "requires_evidence": false
        },
        "pairing_check": {
          "topic_groups": [],
          "image_metadata": "villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png wearable_lifestyle_photo",
          "matched_image_terms": {}
        }
      },
      "deleted_learning_gate": {
        "blockers": [],
        "matches": []
      },
      "saturation_flags": [
        "same_black_hoodie"
      ],
      "pilot_score": 286,
      "eligible": false,
      "blockers": [
        "near_duplicate_media_phash",
        "same_media_path",
        "same_media_sha256"
      ],
      "warnings": [
        "recent_media_reuse_match_found"
      ],
      "reason": "Hoodie mirror person. No temporal/event claim.",
      "expected_type": "residual_growth_or_profile_pull",
      "fallback_action": "fallback_to_poster_summary_image_ready",
      "quality_review": {
        "candidate_id": "vln-stream-20260519-stock-003",
        "execution_id": "",
        "slot": "night",
        "passcode": "GQ2UB",
        "image": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png",
        "text": "服は主張しすぎると、\n急に広告になる。\n\n少しだけ見えて、\n勝手に残るくらいがちょうどいい。\n\n#着て稼ぐ #villain $PPP @0xmavillain GQ2UB",
        "text_preview": "服は主張しすぎると、 / 急に広告になる。 / 少しだけ見えて、 / 勝手に残るくらいがちょうどいい。 / #着て稼ぐ #villain $PPP @0xmavillain GQ2UB",
        "final_quality_status": "READY",
        "blockers": [],
        "warnings": [],
        "context_terms": [],
        "context_evidence": {
          "verified": false,
          "requires_evidence": false,
          "core_question": "この投稿は何を見て言っているのか？"
        },
        "topic_image_fit": {
          "status": "OK",
          "checks": {
            "topic_groups": [],
            "image_metadata": "villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_012_hoodie_mirror_person.png wearable_lifestyle_photo",
            "matched_image_terms": {}
          }
        },
        "ad_like_score": 0,
        "native_tone_score": 82,
        "persona_fit": 83,
        "deleted_nearby_match": [],
        "human_check_checklist": [
          "この投稿は何を見て言っているのか？",
          "本文の現実文脈は今日の状況と一致しているか？",
          "画像は本文topicを本当に支えているか？",
          "広告ではなくタイムライン上の観測として混ざるか？",
          "鬼徹アカウントの余白と人格に合っているか？"
        ]
      }
    },
    {
      "slot": "night",
      "source": "candidate_stream",
      "source_id": "vln-stream-20260519-auto-004",
      "category": "culture_observer",
      "passcode": "F3X7M",
      "text": "机に置いた瞬間、\nグッズじゃなくて、\n生活の一部になる。\n\n広告より、\n使われた跡の方が強い。\n\n#着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "text_preview": "机に置いた瞬間、 / グッズじゃなくて、 / 生活の一部になる。 / 広告より、 / 使われた跡の方が強い。 / #着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "token_verification": {
        "required_layer": "Required Token Layer v1",
        "mandatory_footer_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "missing_before": [],
        "duplicates_before": [],
        "changed": false,
        "before_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "after_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "final_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "passcode": "F3X7M",
        "passcode_exists_in_db": true,
        "valid_after": true
      },
      "image": {
        "required": true,
        "ready": true,
        "file_path": "villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
        "image_type": "lifestyle_residue",
        "match_score": 92,
        "rights_notes": "maintenance refill from approved shop wearable stock; not raw shop image.",
        "absolute_path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png"
      },
      "score": 90,
      "risk": "low",
      "novelty_score": 78,
      "raw_novelty_score": 78,
      "remixability_score": 72,
      "remixability": {
        "source": "candidate_score",
        "signals": [],
        "components": {}
      },
      "media_deduplication": {
        "signature": {
          "path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
          "sha256": "9257441a33698225b81a8439603a5f1402dbfff677bc1ed4199c8f4cbfde7715",
          "perceptual_hash": "0000c013c3c90d17",
          "prompt_family": "lifestyle_residue_wearable_stock_006_thermos_desk_residue",
          "composition": "",
          "layout": "",
          "image_type": "lifestyle_residue"
        },
        "blockers": [
          "near_duplicate_media_phash",
          "same_media_path",
          "same_media_sha256",
          "same_prompt_family_cooldown"
        ],
        "matches": [
          {
            "tweet_id": "2057067435744997644",
            "url": "https://x.com/raindog_kitetu/status/2057067435744997644",
            "posted_at_jst": "2026-05-20T20:54:30+09:00",
            "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
            "hamming_distance": 0,
            "reasons": [
              "near_duplicate_media_phash",
              "same_media_path",
              "same_media_sha256",
              "same_prompt_family_cooldown"
            ]
          }
        ],
        "cooldown_days": 7
      },
      "context_mismatch_gate": {
        "blockers": [],
        "context_check": {
          "terms": [],
          "temporal_terms": [],
          "event_terms": [],
          "context_evidence_verified": false,
          "requires_evidence": false
        },
        "pairing_check": {
          "topic_groups": [],
          "image_metadata": "villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png lifestyle_residue",
          "matched_image_terms": {}
        }
      },
      "deleted_learning_gate": {
        "blockers": [
          "deleted_candidate_blacklist"
        ],
        "matches": [
          {
            "tweet_id": "2057067435744997644",
            "execution_id": "vln-exec-daytime-vln-stream-20260519-auto-004",
            "candidate_id": "vln-stream-20260519-auto-004",
            "image_used": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
            "prompt_family": "lifestyle_residue_wearable_stock_006_thermos_desk_residue",
            "topic_cluster": "culture_observer_apparel_context",
            "delete_reason": "Deleted by human: image quality was terrible; flat product composite did not fit account quality bar.",
            "reasons": [
              "deleted_candidate_blacklist"
            ]
          }
        ]
      },
      "saturation_flags": [],
      "pilot_score": 288,
      "eligible": false,
      "blockers": [
        "near_duplicate_media_phash",
        "same_media_path",
        "same_media_sha256",
        "same_prompt_family_cooldown"
      ],
      "warnings": [
        "deleted_nearby_match_found",
        "near_deleted_or_dropped_post",
        "recent_media_reuse_match_found"
      ],
      "reason": "Auto-refilled by maintenance from wearable_stock_006_thermos_desk_residue; no reality/event claim.",
      "expected_type": "residual_growth_or_profile_pull",
      "fallback_action": "fallback_to_poster_summary_image_ready",
      "quality_review": {
        "candidate_id": "vln-stream-20260519-auto-004",
        "execution_id": "",
        "slot": "night",
        "passcode": "F3X7M",
        "image": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
        "text": "机に置いた瞬間、\nグッズじゃなくて、\n生活の一部になる。\n\n広告より、\n使われた跡の方が強い。\n\n#着て稼ぐ #villain $PPP @0xmavillain F3X7M",
        "text_preview": "机に置いた瞬間、 / グッズじゃなくて、 / 生活の一部になる。 / 広告より、 / 使われた跡の方が強い。 / #着て稼ぐ #villain $PPP @0xmavillain F3X7M",
        "final_quality_status": "REVIEW_REQUIRED",
        "blockers": [],
        "warnings": [
          "deleted_nearby_match_found"
        ],
        "context_terms": [],
        "context_evidence": {
          "verified": false,
          "requires_evidence": false,
          "core_question": "この投稿は何を見て言っているのか？"
        },
        "topic_image_fit": {
          "status": "OK",
          "checks": {
            "topic_groups": [],
            "image_metadata": "villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png lifestyle_residue",
            "matched_image_terms": {}
          }
        },
        "ad_like_score": 0,
        "native_tone_score": 72,
        "persona_fit": 78,
        "deleted_nearby_match": [
          {
            "tweet_id": "2057067435744997644",
            "execution_id": "vln-exec-daytime-vln-stream-20260519-auto-004",
            "candidate_id": "vln-stream-20260519-auto-004",
            "image_used": "/Users/raindog/Documents/New project/villain_post_images/wearable_stock/wearable_stock_006_thermos_desk_residue.png",
            "prompt_family": "lifestyle_residue_wearable_stock_006_thermos_desk_residue",
            "topic_cluster": "culture_observer_apparel_context",
            "delete_reason": "Deleted by human: image quality was terrible; flat product composite did not fit account quality bar.",
            "reasons": [
              "deleted_candidate_blacklist"
            ]
          }
        ],
        "human_check_checklist": [
          "この投稿は何を見て言っているのか？",
          "本文の現実文脈は今日の状況と一致しているか？",
          "画像は本文topicを本当に支えているか？",
          "広告ではなくタイムライン上の観測として混ざるか？",
          "鬼徹アカウントの余白と人格に合っているか？"
        ]
      }
    },
    {
      "slot": "late_night",
      "source": "candidate_stream",
      "source_id": "vln-stream-20260519-stock-001",
      "category": "culture_observer",
      "passcode": "C14QB",
      "text": "机に置いた瞬間、\nグッズじゃなくて、\n生活の一部になる。\n\n広告より、\n使われた跡の方が強い。\n\n#着て稼ぐ #villain $PPP @0xmavillain C14QB",
      "text_preview": "机に置いた瞬間、 / グッズじゃなくて、 / 生活の一部になる。 / 広告より、 / 使われた跡の方が強い。 / #着て稼ぐ #villain $PPP @0xmavillain C14QB",
      "token_verification": {
        "required_layer": "Required Token Layer v1",
        "mandatory_footer_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "missing_before": [],
        "duplicates_before": [],
        "changed": false,
        "before_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "after_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "final_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "passcode": "C14QB",
        "passcode_exists_in_db": true,
        "valid_after": true
      },
      "image": {
        "required": true,
        "ready": true,
        "file_path": "villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
        "image_type": "lifestyle_residue_photo",
        "match_score": 94,
        "rights_notes": "公式ショップ実物グッズを参照した生活痕/着用画像。商品画像そのままではない。",
        "absolute_path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png"
      },
      "score": 92,
      "risk": "low",
      "novelty_score": 80,
      "raw_novelty_score": 80,
      "remixability_score": 74,
      "remixability": {
        "source": "candidate_score",
        "signals": [],
        "components": {}
      },
      "media_deduplication": {
        "signature": {
          "path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
          "sha256": "536ed31d6942711bf8ef87c8d6c2c9ee189732bb5df6615fd4d8ffdd77aa5fc2",
          "perceptual_hash": "1f19113034302030",
          "prompt_family": "lifestyle_residue_photo_wearable_stock_010_thermos_workdesk",
          "composition": "",
          "layout": "",
          "image_type": "lifestyle_residue_photo"
        },
        "blockers": [
          "near_duplicate_media_phash",
          "same_media_path",
          "same_media_sha256",
          "same_prompt_family_cooldown"
        ],
        "matches": [
          {
            "tweet_id": "2056897607105192401",
            "url": "https://x.com/raindog_kitetu/status/2056897607105192401",
            "posted_at_jst": "2026-05-20T09:31:48+09:00",
            "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
            "hamming_distance": 0,
            "reasons": [
              "near_duplicate_media_phash",
              "same_media_path",
              "same_media_sha256",
              "same_prompt_family_cooldown"
            ]
          }
        ],
        "cooldown_days": 7
      },
      "context_mismatch_gate": {
        "blockers": [],
        "context_check": {
          "terms": [],
          "temporal_terms": [],
          "event_terms": [],
          "context_evidence_verified": false,
          "requires_evidence": false
        },
        "pairing_check": {
          "topic_groups": [],
          "image_metadata": "villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png lifestyle_residue_photo",
          "matched_image_terms": {}
        }
      },
      "deleted_learning_gate": {
        "blockers": [],
        "matches": []
      },
      "saturation_flags": [],
      "pilot_score": 294,
      "eligible": false,
      "blockers": [
        "near_duplicate_media_phash",
        "same_media_path",
        "same_media_sha256",
        "same_prompt_family_cooldown"
      ],
      "warnings": [
        "recent_media_reuse_match_found"
      ],
      "reason": "Thermos desk residue. No temporal/event claim.",
      "expected_type": "residual_growth_or_profile_pull",
      "fallback_action": "fallback_to_best_image_ready_culture_or_community",
      "quality_review": {
        "candidate_id": "vln-stream-20260519-stock-001",
        "execution_id": "",
        "slot": "late_night",
        "passcode": "C14QB",
        "image": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png",
        "text": "机に置いた瞬間、\nグッズじゃなくて、\n生活の一部になる。\n\n広告より、\n使われた跡の方が強い。\n\n#着て稼ぐ #villain $PPP @0xmavillain C14QB",
        "text_preview": "机に置いた瞬間、 / グッズじゃなくて、 / 生活の一部になる。 / 広告より、 / 使われた跡の方が強い。 / #着て稼ぐ #villain $PPP @0xmavillain C14QB",
        "final_quality_status": "READY",
        "blockers": [],
        "warnings": [],
        "context_terms": [],
        "context_evidence": {
          "verified": false,
          "requires_evidence": false,
          "core_question": "この投稿は何を見て言っているのか？"
        },
        "topic_image_fit": {
          "status": "OK",
          "checks": {
            "topic_groups": [],
            "image_metadata": "villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_010_thermos_workdesk.png lifestyle_residue_photo",
            "matched_image_terms": {}
          }
        },
        "ad_like_score": 0,
        "native_tone_score": 72,
        "persona_fit": 78,
        "deleted_nearby_match": [],
        "human_check_checklist": [
          "この投稿は何を見て言っているのか？",
          "本文の現実文脈は今日の状況と一致しているか？",
          "画像は本文topicを本当に支えているか？",
          "広告ではなくタイムライン上の観測として混ざるか？",
          "鬼徹アカウントの余白と人格に合っているか？"
        ]
      }
    },
    {
      "slot": "late_night",
      "source": "candidate_stream",
      "source_id": "vln-stream-20260519-stock-002",
      "category": "poster_summary",
      "passcode": "DKLS8",
      "text": "持ち物って、\n置かれた場所で\nだいたい正体が出る。\n\nきれいな写真より、\n帰ってきた後の方が本物っぽい。\n\n#着て稼ぐ #villain $PPP @0xmavillain DKLS8",
      "text_preview": "持ち物って、 / 置かれた場所で / だいたい正体が出る。 / きれいな写真より、 / 帰ってきた後の方が本物っぽい。 / #着て稼ぐ #villain $PPP @0xmavillain DKLS8",
      "token_verification": {
        "required_layer": "Required Token Layer v1",
        "mandatory_footer_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "missing_before": [],
        "duplicates_before": [],
        "changed": false,
        "before_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "after_counts": {
          "#着て稼ぐ": 1,
          "#villain": 1,
          "$PPP": 1,
          "@0xmavillain": 1
        },
        "final_order": "#着て稼ぐ #villain $PPP @0xmavillain",
        "passcode": "DKLS8",
        "passcode_exists_in_db": true,
        "valid_after": true
      },
      "image": {
        "required": true,
        "ready": true,
        "file_path": "villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
        "image_type": "lifestyle_residue_photo",
        "match_score": 94,
        "rights_notes": "公式ショップ実物グッズを参照した生活痕/着用画像。商品画像そのままではない。",
        "absolute_path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png"
      },
      "score": 92,
      "risk": "low",
      "novelty_score": 76,
      "raw_novelty_score": 80,
      "remixability_score": 74,
      "remixability": {
        "source": "candidate_score",
        "signals": [],
        "components": {}
      },
      "media_deduplication": {
        "signature": {
          "path": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
          "sha256": "4de3bef0230faf0c5c6a5888df83ad45c6ce5afe921dceca4da165df5e4c2ad0",
          "perceptual_hash": "c3c7819168602021",
          "prompt_family": "lifestyle_residue_photo_wearable_stock_011_bag_entryway",
          "composition": "",
          "layout": "",
          "image_type": "lifestyle_residue_photo"
        },
        "blockers": [
          "near_duplicate_media_phash",
          "same_media_path",
          "same_media_sha256",
          "same_prompt_family_cooldown"
        ],
        "matches": [
          {
            "tweet_id": "2056736652442353980",
            "url": "https://x.com/raindog_kitetu/status/2056736652442353980",
            "posted_at_jst": "2026-05-19T23:00:05+09:00",
            "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
            "hamming_distance": 0,
            "reasons": [
              "near_duplicate_media_phash",
              "same_media_path",
              "same_media_sha256",
              "same_prompt_family_cooldown"
            ]
          }
        ],
        "cooldown_days": 7
      },
      "context_mismatch_gate": {
        "blockers": [],
        "context_check": {
          "terms": [],
          "temporal_terms": [],
          "event_terms": [],
          "context_evidence_verified": false,
          "requires_evidence": false
        },
        "pairing_check": {
          "topic_groups": [],
          "image_metadata": "villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png lifestyle_residue_photo",
          "matched_image_terms": {}
        }
      },
      "deleted_learning_gate": {
        "blockers": [],
        "matches": []
      },
      "saturation_flags": [
        "repeated_structure"
      ],
      "pilot_score": 290,
      "eligible": false,
      "blockers": [
        "near_duplicate_media_phash",
        "same_media_path",
        "same_media_sha256",
        "same_prompt_family_cooldown"
      ],
      "warnings": [
        "recent_media_reuse_match_found"
      ],
      "reason": "Bag entryway residue. No temporal/event claim.",
      "expected_type": "residual_growth",
      "fallback_action": "fallback_to_best_image_ready_culture_or_community",
      "quality_review": {
        "candidate_id": "vln-stream-20260519-stock-002",
        "execution_id": "",
        "slot": "late_night",
        "passcode": "DKLS8",
        "image": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png",
        "text": "持ち物って、\n置かれた場所で\nだいたい正体が出る。\n\nきれいな写真より、\n帰ってきた後の方が本物っぽい。\n\n#着て稼ぐ #villain $PPP @0xmavillain DKLS8",
        "text_preview": "持ち物って、 / 置かれた場所で / だいたい正体が出る。 / きれいな写真より、 / 帰ってきた後の方が本物っぽい。 / #着て稼ぐ #villain $PPP @0xmavillain DKLS8",
        "final_quality_status": "READY",
        "blockers": [],
        "warnings": [],
        "context_terms": [],
        "context_evidence": {
          "verified": false,
          "requires_evidence": false,
          "core_question": "この投稿は何を見て言っているのか？"
        },
        "topic_image_fit": {
          "status": "OK",
          "checks": {
            "topic_groups": [],
            "image_metadata": "villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png /users/raindog/projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_011_bag_entryway.png lifestyle_residue_photo",
            "matched_image_terms": {}
          }
        },
        "ad_like_score": 0,
        "native_tone_score": 77,
        "persona_fit": 78,
        "deleted_nearby_match": [],
        "human_check_checklist": [
          "この投稿は何を見て言っているのか？",
          "本文の現実文脈は今日の状況と一致しているか？",
          "画像は本文topicを本当に支えているか？",
          "広告ではなくタイムライン上の観測として混ざるか？",
          "鬼徹アカウントの余白と人格に合っているか？"
        ]
      }
    }
  ]
}
```

## data/villain_quality_review_queue.json

``` json
{
  "db_name": "Villain Quality Review Queue",
  "version": "1.0.0",
  "generated_at_jst": "2026-05-17T18:22:22+09:00",
  "status": "BLOCKED",
  "posting_executed": false,
  "upload_media_executed": false,
  "tweet_creation_executed": false,
  "policy_source": "data/villain_post_quality_os.json",
  "review_items": [
    {
      "candidate_id": "vln-gen-20260516-001",
      "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
      "slot": "daytime",
      "passcode": "F3X7M",
      "image": "/Users/raindog/Documents/New project/villain_post_images/20260514集会.png",
      "text": "昨日の集会、\nまだ少し残ってる。\n\n説明より、\n人が集まってる事実の方が強い。\n\n$villainは、\nそこがちょっと変。\n\n#着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "text_preview": "昨日の集会、 / まだ少し残ってる。 / 説明より、 / 人が集まってる事実の方が強い。 / $villainは、 / そこがちょっと変。 / #着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "final_quality_status": "BLOCKED",
      "blockers": [
        "deleted_text_near_match",
        "deleted_topic_context_cooldown",
        "temporal_context_unverified"
      ],
      "warnings": [
        "deleted_nearby_match_found"
      ],
      "context_terms": [
        "昨日",
        "集会"
      ],
      "context_evidence": {
        "verified": false,
        "requires_evidence": true,
        "core_question": "この投稿は何を見て言っているのか？"
      },
      "topic_image_fit": {
        "status": "OK",
        "checks": {
          "topic_groups": [
            "gathering_event",
            "temporal_claim"
          ],
          "image_metadata": "villain_post_images/20260514集会.png /users/raindog/documents/new project/villain_post_images/20260514集会.png community_info 実データ最強投稿の型に最も近い。集会、会話、現場感、画像ありの条件が揃っている。",
          "matched_image_terms": {
            "gathering_event": [
              "集会",
              "現場",
              "community"
            ]
          }
        }
      },
      "ad_like_score": 0,
      "native_tone_score": 82,
      "persona_fit": 88,
      "deleted_nearby_match": [
        {
          "tweet_id": "2055938300708626713",
          "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
          "candidate_id": "vln-gen-20260516-001",
          "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/20260514集会.png",
          "prompt_family": "community_info_実デ_タ最強投稿の型に最も近い_集会_会話_現場感_画像ありの条件が揃っている_集会",
          "topic_cluster": "community_gathering_signal",
          "delete_reason": "Deleted by human: content/context mismatch. Not yesterday's gathering and post did not fit actual situation.",
          "reasons": [
            "deleted_candidate_blacklist",
            "deleted_text_near_match",
            "deleted_topic_context_cooldown"
          ]
        }
      ],
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ]
    },
    {
      "candidate_id": "vln-gen-20260516-002",
      "execution_id": "vln-exec-daytime-vln-gen-20260516-002",
      "slot": "daytime",
      "passcode": "H9J6L",
      "image": "/Users/raindog/Documents/New project/villain_post_images/20260514集会.png",
      "text": "気づくと、\nまた$villainの話になってる。\n\n服の話だけなら、\nたぶんここまで残らない。\n\n#着て稼ぐ #villain $PPP @0xmavillain H9J6L",
      "text_preview": "気づくと、 / また$villainの話になってる。 / 服の話だけなら、 / たぶんここまで残らない。 / #着て稼ぐ #villain $PPP @0xmavillain H9J6L",
      "final_quality_status": "READY",
      "blockers": [],
      "warnings": [],
      "context_terms": [],
      "context_evidence": {
        "verified": false,
        "requires_evidence": false,
        "core_question": "この投稿は何を見て言っているのか？"
      },
      "topic_image_fit": {
        "status": "OK",
        "checks": {
          "topic_groups": [],
          "image_metadata": "villain_post_images/20260514集会.png /users/raindog/documents/new project/villain_post_images/20260514集会.png community 集会・スペース・コミュニティの動きを短く残す投稿。",
          "matched_image_terms": {}
        }
      },
      "ad_like_score": 0,
      "native_tone_score": 82,
      "persona_fit": 83,
      "deleted_nearby_match": [],
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ]
    },
    {
      "candidate_id": "vln-gen-20260516-003",
      "execution_id": "vln-exec-daytime-vln-gen-20260516-003",
      "slot": "daytime",
      "passcode": "J1M5V",
      "image": "/Users/raindog/Documents/New project/villain_post_images/生成画像1.png",
      "text": "話題になる服って、\nだいたい服だけじゃない。\n\n誰が着て、\nどこで集まってるかまで含めて、\n少し残る。\n\n#着て稼ぐ #villain $PPP @0xmavillain J1M5V",
      "text_preview": "話題になる服って、 / だいたい服だけじゃない。 / 誰が着て、 / どこで集まってるかまで含めて、 / 少し残る。 / #着て稼ぐ #villain $PPP @0xmavillain J1M5V",
      "final_quality_status": "BLOCKED",
      "blockers": [
        "deleted_topic_context_cooldown",
        "topic_image_pairing_mismatch"
      ],
      "warnings": [
        "deleted_nearby_match_found"
      ],
      "context_terms": [],
      "context_evidence": {
        "verified": false,
        "requires_evidence": false,
        "core_question": "この投稿は何を見て言っているのか？"
      },
      "topic_image_fit": {
        "status": "MISMATCH",
        "checks": {
          "topic_groups": [
            "gathering_event"
          ],
          "image_metadata": "villain_post_images/生成画像1.png /users/raindog/documents/new project/villain_post_images/生成画像1.png culture_observer 服単体ではなく、日常に入り込んだ違和感を置ける。culture_observerの補強に向く。",
          "matched_image_terms": {
            "gathering_event": []
          }
        }
      },
      "ad_like_score": 0,
      "native_tone_score": 92,
      "persona_fit": 93,
      "deleted_nearby_match": [
        {
          "tweet_id": "2055938300708626713",
          "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
          "candidate_id": "vln-gen-20260516-001",
          "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/20260514集会.png",
          "prompt_family": "community_info_実デ_タ最強投稿の型に最も近い_集会_会話_現場感_画像ありの条件が揃っている_集会",
          "topic_cluster": "community_gathering_signal",
          "delete_reason": "Deleted by human: content/context mismatch. Not yesterday's gathering and post did not fit actual situation.",
          "reasons": [
            "deleted_topic_context_cooldown"
          ]
        }
      ],
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ]
    },
    {
      "candidate_id": "vln-gen-20260516-001",
      "execution_id": "vln-exec-night-vln-gen-20260516-001",
      "slot": "night",
      "passcode": "F3X7M",
      "image": "/Users/raindog/Documents/New project/villain_post_images/20260514集会.png",
      "text": "昨日の集会、\nまだ少し残ってる。\n\n説明より、\n人が集まってる事実の方が強い。\n\n$villainは、\nそこがちょっと変。\n\n#着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "text_preview": "昨日の集会、 / まだ少し残ってる。 / 説明より、 / 人が集まってる事実の方が強い。 / $villainは、 / そこがちょっと変。 / #着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "final_quality_status": "BLOCKED",
      "blockers": [
        "deleted_text_near_match",
        "deleted_topic_context_cooldown",
        "temporal_context_unverified"
      ],
      "warnings": [
        "deleted_nearby_match_found"
      ],
      "context_terms": [
        "昨日",
        "集会"
      ],
      "context_evidence": {
        "verified": false,
        "requires_evidence": true,
        "core_question": "この投稿は何を見て言っているのか？"
      },
      "topic_image_fit": {
        "status": "OK",
        "checks": {
          "topic_groups": [
            "gathering_event",
            "temporal_claim"
          ],
          "image_metadata": "villain_post_images/20260514集会.png /users/raindog/documents/new project/villain_post_images/20260514集会.png community_info 実データ最強投稿の型に最も近い。集会、会話、現場感、画像ありの条件が揃っている。",
          "matched_image_terms": {
            "gathering_event": [
              "集会",
              "現場",
              "community"
            ]
          }
        }
      },
      "ad_like_score": 0,
      "native_tone_score": 82,
      "persona_fit": 88,
      "deleted_nearby_match": [
        {
          "tweet_id": "2055938300708626713",
          "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
          "candidate_id": "vln-gen-20260516-001",
          "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/20260514集会.png",
          "prompt_family": "community_info_実デ_タ最強投稿の型に最も近い_集会_会話_現場感_画像ありの条件が揃っている_集会",
          "topic_cluster": "community_gathering_signal",
          "delete_reason": "Deleted by human: content/context mismatch. Not yesterday's gathering and post did not fit actual situation.",
          "reasons": [
            "deleted_candidate_blacklist",
            "deleted_text_near_match",
            "deleted_topic_context_cooldown"
          ]
        }
      ],
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ]
    },
    {
      "candidate_id": "vln-gen-20260516-002",
      "execution_id": "vln-exec-night-vln-gen-20260516-002",
      "slot": "night",
      "passcode": "H9J6L",
      "image": "/Users/raindog/Documents/New project/villain_post_images/20260514集会.png",
      "text": "気づくと、\nまた$villainの話になってる。\n\n服の話だけなら、\nたぶんここまで残らない。\n\n#着て稼ぐ #villain $PPP @0xmavillain H9J6L",
      "text_preview": "気づくと、 / また$villainの話になってる。 / 服の話だけなら、 / たぶんここまで残らない。 / #着て稼ぐ #villain $PPP @0xmavillain H9J6L",
      "final_quality_status": "READY",
      "blockers": [],
      "warnings": [],
      "context_terms": [],
      "context_evidence": {
        "verified": false,
        "requires_evidence": false,
        "core_question": "この投稿は何を見て言っているのか？"
      },
      "topic_image_fit": {
        "status": "OK",
        "checks": {
          "topic_groups": [],
          "image_metadata": "villain_post_images/20260514集会.png /users/raindog/documents/new project/villain_post_images/20260514集会.png community 集会・スペース・コミュニティの動きを短く残す投稿。",
          "matched_image_terms": {}
        }
      },
      "ad_like_score": 0,
      "native_tone_score": 82,
      "persona_fit": 83,
      "deleted_nearby_match": [],
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ]
    },
    {
      "candidate_id": "vln-gen-20260516-003",
      "execution_id": "vln-exec-night-vln-gen-20260516-003",
      "slot": "night",
      "passcode": "J1M5V",
      "image": "/Users/raindog/Documents/New project/villain_post_images/生成画像1.png",
      "text": "話題になる服って、\nだいたい服だけじゃない。\n\n誰が着て、\nどこで集まってるかまで含めて、\n少し残る。\n\n#着て稼ぐ #villain $PPP @0xmavillain J1M5V",
      "text_preview": "話題になる服って、 / だいたい服だけじゃない。 / 誰が着て、 / どこで集まってるかまで含めて、 / 少し残る。 / #着て稼ぐ #villain $PPP @0xmavillain J1M5V",
      "final_quality_status": "BLOCKED",
      "blockers": [
        "deleted_topic_context_cooldown",
        "topic_image_pairing_mismatch"
      ],
      "warnings": [
        "deleted_nearby_match_found"
      ],
      "context_terms": [],
      "context_evidence": {
        "verified": false,
        "requires_evidence": false,
        "core_question": "この投稿は何を見て言っているのか？"
      },
      "topic_image_fit": {
        "status": "MISMATCH",
        "checks": {
          "topic_groups": [
            "gathering_event"
          ],
          "image_metadata": "villain_post_images/生成画像1.png /users/raindog/documents/new project/villain_post_images/生成画像1.png culture_observer 服単体ではなく、日常に入り込んだ違和感を置ける。culture_observerの補強に向く。",
          "matched_image_terms": {
            "gathering_event": []
          }
        }
      },
      "ad_like_score": 0,
      "native_tone_score": 92,
      "persona_fit": 93,
      "deleted_nearby_match": [
        {
          "tweet_id": "2055938300708626713",
          "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
          "candidate_id": "vln-gen-20260516-001",
          "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/20260514集会.png",
          "prompt_family": "community_info_実デ_タ最強投稿の型に最も近い_集会_会話_現場感_画像ありの条件が揃っている_集会",
          "topic_cluster": "community_gathering_signal",
          "delete_reason": "Deleted by human: content/context mismatch. Not yesterday's gathering and post did not fit actual situation.",
          "reasons": [
            "deleted_topic_context_cooldown"
          ]
        }
      ],
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ]
    },
    {
      "candidate_id": "vln-gen-20260516-001",
      "execution_id": "vln-exec-late_night-vln-gen-20260516-001",
      "slot": "late_night",
      "passcode": "F3X7M",
      "image": "/Users/raindog/Documents/New project/villain_post_images/20260514集会.png",
      "text": "昨日の集会、\nまだ少し残ってる。\n\n説明より、\n人が集まってる事実の方が強い。\n\n$villainは、\nそこがちょっと変。\n\n#着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "text_preview": "昨日の集会、 / まだ少し残ってる。 / 説明より、 / 人が集まってる事実の方が強い。 / $villainは、 / そこがちょっと変。 / #着て稼ぐ #villain $PPP @0xmavillain F3X7M",
      "final_quality_status": "BLOCKED",
      "blockers": [
        "deleted_text_near_match",
        "deleted_topic_context_cooldown",
        "temporal_context_unverified"
      ],
      "warnings": [
        "deleted_nearby_match_found"
      ],
      "context_terms": [
        "昨日",
        "集会"
      ],
      "context_evidence": {
        "verified": false,
        "requires_evidence": true,
        "core_question": "この投稿は何を見て言っているのか？"
      },
      "topic_image_fit": {
        "status": "OK",
        "checks": {
          "topic_groups": [
            "gathering_event",
            "temporal_claim"
          ],
          "image_metadata": "villain_post_images/20260514集会.png /users/raindog/documents/new project/villain_post_images/20260514集会.png community_info 実データ最強投稿の型に最も近い。集会、会話、現場感、画像ありの条件が揃っている。",
          "matched_image_terms": {
            "gathering_event": [
              "集会",
              "現場",
              "community"
            ]
          }
        }
      },
      "ad_like_score": 0,
      "native_tone_score": 82,
      "persona_fit": 88,
      "deleted_nearby_match": [
        {
          "tweet_id": "2055938300708626713",
          "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
          "candidate_id": "vln-gen-20260516-001",
          "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/20260514集会.png",
          "prompt_family": "community_info_実デ_タ最強投稿の型に最も近い_集会_会話_現場感_画像ありの条件が揃っている_集会",
          "topic_cluster": "community_gathering_signal",
          "delete_reason": "Deleted by human: content/context mismatch. Not yesterday's gathering and post did not fit actual situation.",
          "reasons": [
            "deleted_candidate_blacklist",
            "deleted_text_near_match",
            "deleted_topic_context_cooldown"
          ]
        }
      ],
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ]
    },
    {
      "candidate_id": "vln-gen-20260516-002",
      "execution_id": "vln-exec-late_night-vln-gen-20260516-002",
      "slot": "late_night",
      "passcode": "H9J6L",
      "image": "/Users/raindog/Documents/New project/villain_post_images/20260514集会.png",
      "text": "気づくと、\nまた$villainの話になってる。\n\n服の話だけなら、\nたぶんここまで残らない。\n\n#着て稼ぐ #villain $PPP @0xmavillain H9J6L",
      "text_preview": "気づくと、 / また$villainの話になってる。 / 服の話だけなら、 / たぶんここまで残らない。 / #着て稼ぐ #villain $PPP @0xmavillain H9J6L",
      "final_quality_status": "READY",
      "blockers": [],
      "warnings": [],
      "context_terms": [],
      "context_evidence": {
        "verified": false,
        "requires_evidence": false,
        "core_question": "この投稿は何を見て言っているのか？"
      },
      "topic_image_fit": {
        "status": "OK",
        "checks": {
          "topic_groups": [],
          "image_metadata": "villain_post_images/20260514集会.png /users/raindog/documents/new project/villain_post_images/20260514集会.png community 集会・スペース・コミュニティの動きを短く残す投稿。",
          "matched_image_terms": {}
        }
      },
      "ad_like_score": 0,
      "native_tone_score": 82,
      "persona_fit": 83,
      "deleted_nearby_match": [],
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ]
    },
    {
      "candidate_id": "vln-gen-20260516-003",
      "execution_id": "vln-exec-late_night-vln-gen-20260516-003",
      "slot": "late_night",
      "passcode": "J1M5V",
      "image": "/Users/raindog/Documents/New project/villain_post_images/生成画像1.png",
      "text": "話題になる服って、\nだいたい服だけじゃない。\n\n誰が着て、\nどこで集まってるかまで含めて、\n少し残る。\n\n#着て稼ぐ #villain $PPP @0xmavillain J1M5V",
      "text_preview": "話題になる服って、 / だいたい服だけじゃない。 / 誰が着て、 / どこで集まってるかまで含めて、 / 少し残る。 / #着て稼ぐ #villain $PPP @0xmavillain J1M5V",
      "final_quality_status": "BLOCKED",
      "blockers": [
        "deleted_topic_context_cooldown",
        "topic_image_pairing_mismatch"
      ],
      "warnings": [
        "deleted_nearby_match_found"
      ],
      "context_terms": [],
      "context_evidence": {
        "verified": false,
        "requires_evidence": false,
        "core_question": "この投稿は何を見て言っているのか？"
      },
      "topic_image_fit": {
        "status": "MISMATCH",
        "checks": {
          "topic_groups": [
            "gathering_event"
          ],
          "image_metadata": "villain_post_images/生成画像1.png /users/raindog/documents/new project/villain_post_images/生成画像1.png culture_observer 服単体ではなく、日常に入り込んだ違和感を置ける。culture_observerの補強に向く。",
          "matched_image_terms": {
            "gathering_event": []
          }
        }
      },
      "ad_like_score": 0,
      "native_tone_score": 92,
      "persona_fit": 93,
      "deleted_nearby_match": [
        {
          "tweet_id": "2055938300708626713",
          "execution_id": "vln-exec-daytime-vln-gen-20260516-001",
          "candidate_id": "vln-gen-20260516-001",
          "image_used": "/Users/raindog/Projects/villain-auto-posting/villain_post_images/20260514集会.png",
          "prompt_family": "community_info_実デ_タ最強投稿の型に最も近い_集会_会話_現場感_画像ありの条件が揃っている_集会",
          "topic_cluster": "community_gathering_signal",
          "delete_reason": "Deleted by human: content/context mismatch. Not yesterday's gathering and post did not fit actual situation.",
          "reasons": [
            "deleted_topic_context_cooldown"
          ]
        }
      ],
      "human_check_checklist": [
        "この投稿は何を見て言っているのか？",
        "本文の現実文脈は今日の状況と一致しているか？",
        "画像は本文topicを本当に支えているか？",
        "広告ではなくタイムライン上の観測として混ざるか？",
        "鬼徹アカウントの余白と人格に合っているか？"
      ]
    }
  ]
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

- Generated at JST: `2026-05-19T21:55:39+09:00`
- schema_version: `handoff.codex_to_chatgpt.v1`
- status: `READY_FOR_CHATGPT_REVIEW`
- review_state: `CHATGPT_DECISION_CONSUMED`
- posting executed: `NO`
- upload executed: `NO`
- tweet creation executed: `NO`

## Quality Review

- quality_status: `READY`
- queue_health_status: `CLEAR`
- review_board_status: `READY`
- posting_execution_status: `BLOCKED`
- executable_ready_count: `0`
- safe_to_review: `true`
- safe_to_post: `false`
- review_items: `2`
- blockers: `none`
- warnings: `none`
- blocked_reason_frequency: `{}`
- review_required_candidate_count: `0`
- READY_candidate_count: `2`
- BLOCKED_candidate_count: `0`
- stale_cleanup_removed: `0`

## ChatGPT Decision

- decision: `CONSTANT_REVIEW_ENABLED`
- approved_for_review: `0`
- not_approved_for_posting: `0`
- must_remain_blocked: `0`
- refill_required: `false`
- repair_actions: `0`
- repair_execution_status: `COMPLETED_REVIEW_ONLY`
- repaired_candidate_count: `0`
- context_evidence_request_count: `0`
- average_repair_quality_score: `0`
- average_repair_confidence: `0`
- repair_regression_risk_frequency: `{}`
- recurring_repair_failure_clusters: `0`

## Deleted Learning Cooldown

- `2055938300708626713` candidate `vln-gen-20260516-001`: `116.4`h remaining until `2026-05-24T18:22:16+09:00`

## Validation

- json_valid: `True`
- quality_review_runner: `True`
- tracking_code_absent: `True`
- x_write_not_used: `True`

## Unresolved Issues

- Deleted learning cooldown is active for recent failed posts.

## Next Actions

- ChatGPT updates data/chatgpt_to_codex_handoff.json when policy changes.
- Codex runs scripts/agent_handoff_runner.py after local implementation or review.
- User approves only final READY/REVIEW_REQUIRED/BLOCKED summary.

## GitHub Handoff

- ChatGPT can read this contract and the JSON handoff files through the GitHub connector after commit/push.
- Codex should only publish handoff/review/report files for this loop; posting artifacts stay gated.

## ChatGPT Bridge

- bridge prompt: `reports/chatgpt_bridge_prompt.md`
- last ingestion at JST: `2026-05-21T00:50:33+09:00`
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

- Generated at JST: `2026-05-17T18:22:22+09:00`
- final_status: `BLOCKED`
- posting executed: `NO`
- upload executed: `NO`
- tweet creation executed: `NO`

## Items

### `vln-gen-20260516-001`

- execution_id: `vln-exec-daytime-vln-gen-20260516-001`
- slot: `daytime`
- passcode: `F3X7M`
- image: `/Users/raindog/Documents/New project/villain_post_images/20260514集会.png`
- final_quality_status: `BLOCKED`
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

- execution_id: `vln-exec-daytime-vln-gen-20260516-002`
- slot: `daytime`
- passcode: `H9J6L`
- image: `/Users/raindog/Documents/New project/villain_post_images/20260514集会.png`
- final_quality_status: `READY`
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

- execution_id: `vln-exec-daytime-vln-gen-20260516-003`
- slot: `daytime`
- passcode: `J1M5V`
- image: `/Users/raindog/Documents/New project/villain_post_images/生成画像1.png`
- final_quality_status: `BLOCKED`
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
