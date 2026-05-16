# Villain Post Outcome Logger v1

- Generated at JST: `2026-05-16T21:07:01+09:00`
- status: `LOCAL_OUTCOME_LOGGING_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- action: `no_changes`
- outcomes: `1`

## Latest Outcome

- tweet_id: `2055613495119585536`
- url: https://x.com/raindog_kitetu/status/2055613495119585536
- candidate_id: `vln-gen-20260516-003`
- passcode: `R2J9T`
- posted_at_jst: `2026-05-16T20:37:03+09:00`
- image_hash: `bd1e9c5bbb7c8887d71327cde08be78acf2b5e21cd2355698fcd60eb0c62c4a6`
- topic_cluster: `culture_observer_apparel_context`
- archetype_primary: `community_artifact`
- novelty_score: `66`
- culture_observer_score: `40`
- metrics_1h: `{'captured_at_jst': '2026-05-16T20:46:48+09:00', 'impressions': None, 'likes': 0, 'reposts': 0, 'replies': 0, 'profile_clicks': None, 'repost_reuse': None, 'bookmarks': 0}`
- metrics_24h: `{'captured_at_jst': '', 'impressions': None, 'likes': None, 'reposts': None, 'replies': None, 'profile_clicks': None, 'repost_reuse': None, 'bookmarks': None}`
- manual_review.keep: `pending`
- manual_review.delete_reason: ``
- felt_native: `True`
- felt_ad_like: `False`
- manual_review.notes: `Normalize pending keep state.`
- updated_at_jst: `2026-05-16T20:50:02+09:00`
- update_history_count: `3`

```text
話題になる服って、
だいたい服だけじゃない。

誰が着て、
どこで集まってるかまで含めて、
少し残る。

#着て稼ぐ #villain $PPP @0xmavillain R2J9T
```

## Three-Post Operation Prep

- 1日3本運用では、各投稿をこのoutcome DBに即時記録する。
- 1h metricsで初速、24h metricsで後残りを分けて見る。
- 完全放置BOTではなく、人間レビューで keep/delete_reason と felt_native/felt_ad_like を更新する。
- community_artifact / culture_observer / anti_ad の比率を日次で見る。
