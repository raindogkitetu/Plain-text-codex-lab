# Chappy Replacement Request: 2057684471256879127

- updated_at_jst: `2026-05-22T14:41:46+09:00`
- status: `WAITING_FOR_CHAPPY_NEW_IMAGE_DIRECTION`
- safe_to_post: `false`
- posting_execution_status: `BLOCKED`
- executable_ready_count: `0`
- posting executed: `NO`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`

## User Judgment

- The first two wearer-photo candidates are rejected before Chappy review.
- Reason: they look too close to the previous wearable posts. If users think it is the same post, the replacement fails.
- Chappy should prefer a fresh image direction, not another ordinary mirror/street wearable photo.

## Contact Sheet

![replacement contact sheet](/Users/raindog/Projects/villain-auto-posting/reports/chappy_replacement_2057684471256879127_contact_sheet.jpg)

## Rejected Before Chappy Review

- `wearable_stock_007_cap_mirror_person`: too visually similar to previous post family
- `wearable_stock_008_bucket_mirror_person`: too visually similar to previous post family

## Remaining Stock Candidates

### 1. wearable_stock_005_bucket_backview_after

- path: `/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_005_bucket_backview_after.png`
- type: `wearable_lifestyle`
- notes: Actual shop bucket hat used in a back-view after-scene. No temporal/event claim.
- angle: 人が着た後にだけ残る空気

### 2. wearable_stock_004_cap_mirror_crop

- path: `/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_004_cap_mirror_crop.png`
- type: `wearable_lifestyle`
- notes: Actual shop cap composited into a mirror-crop silhouette. Face hidden, no invented product.
- angle: 小物の方が先に空気を運ぶ

### 3. wearable_stock_001_cap_afterhours

- path: `/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_001_cap_afterhours.png`
- type: `wearable_poster`
- notes: Actual shop cap composited onto a quiet human silhouette. No invented cap shape.
- angle: 小物が空気を先に運ぶ / 服より軽いのに残る

### 4. wearable_stock_002_bucket_street

- path: `/Users/raindog/Projects/villain-auto-posting/villain_post_images/wearable_stock/wearable_stock_002_bucket_street.png`
- type: `wearable_poster`
- notes: Actual shop bucket hat composited onto a street silhouette.
- angle: 置いてある時より、人が着た後の方が強い


## オラ好みの画像ルール

Chappy should judge this as **オラ好みの画像**.

Must have:

- 日本語の大きい見出しが読める
- キャラ、マスコット、人物、AI相棒など一目で記憶に残る主役がいる
- ポスター調または図解ポスター調で、情報が整理されている
- 黒ベースに黄色/白など強いコントラスト、または明るいポップ配色
- タイムラインで同じ投稿に見えない新鮮さ
- 投稿本文を読まなくても何か始まった感が伝わる

Avoid:

- 普通の着用写真だけ
- 前回と同じようなミラー/ストリート/背中構図
- 英語ラベル中心で日本語ユーザーに伝わりにくい画像
- 暗すぎて情報が見えない雰囲気画像
- 商品カタログっぽい並べ方

## Preferred New Direction

- pop poster or infographic-poster composition with a clear character hook
- large readable Japanese headline, not English labels
- one memorable mascot/person/AI character visible at feed size
- black/yellow or strong contrast palette inspired by user reference, but still Villain-compatible
- looks like a new chapter, not another product photo

## Chappy Return JSON Only

```json
{
  "approved_image_id": "",
  "approved_image_path": "",
  "avoid_text_angles": [],
  "best_text_angle": "",
  "decision": "APPROVE_ONE | NEED_NEW_IMAGE | REJECT_ALL | HOLD",
  "new_image_brief_if_needed": "",
  "posting_permission_granted": false,
  "visual_reason": ""
}
```
