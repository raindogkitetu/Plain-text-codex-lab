# Villain Post Outcome Logger v1

- Generated at JST: `2026-05-22T16:18:59+09:00`
- status: `LOCAL_OUTCOME_LOGGING_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- action: `inserted`
- outcomes: `15`

## Latest Outcome

- tweet_id: `2057473911550521382`
- url: https://x.com/raindog_kitetu/status/2057473911550521382
- candidate_id: `vln-stream-20260519-stock-003`
- passcode: `GQ2UB`
- posted_at_jst: `2026-05-21T23:49:41+09:00`
- image_hash: `c08bd7a3905ae1a98aa927b96794a1690eefe2dc3535c25d17ca9f476821daa4`
- topic_cluster: `culture_observer_apparel_context`
- archetype_primary: `community_artifact`
- novelty_score: `74`
- culture_observer_score: `40`
- metrics_1h: `{'captured_at_jst': '', 'impressions': None, 'likes': None, 'reposts': None, 'replies': None, 'bookmarks': None, 'profile_clicks': None, 'repost_reuse': None}`
- metrics_24h: `{'captured_at_jst': '', 'impressions': None, 'likes': None, 'reposts': None, 'replies': None, 'bookmarks': None, 'profile_clicks': None, 'repost_reuse': None}`
- manual_review.keep: `True`
- manual_review.delete_reason: ``
- felt_native: `True`
- felt_ad_like: `False`
- manual_review.notes: `User confirmed the second Villain post. Text was adjusted after Chappy Ora-stance review to avoid poetic/formal tone.`
- updated_at_jst: `2026-05-21T23:52:25+09:00`
- update_history_count: `1`

```text
服が前に出すぎると、
だいたい広告っぽくなる。

ちょい見えで止めとくくらいが、
いちばん残る。

#着て稼ぐ #villain $PPP @0xmavillain GQ2UB
```

## Three-Post Operation Prep

- 1日3本運用では、各投稿をこのoutcome DBに即時記録する。
- 1h metricsで初速、24h metricsで後残りを分けて見る。
- 完全放置BOTではなく、人間レビューで keep/delete_reason と felt_native/felt_ad_like を更新する。
- community_artifact / culture_observer / anti_ad の比率を日次で見る。
