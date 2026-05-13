# Villain Image Post Mapping v1

- status: `REPORT_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- safe_post_status: `BLOCK`
- inputs: `villain_post_stock_v1.md`, `villain_post_stock_v2.md`

## Series

- lifestyle_series: 日常・街・駅・カフェ・コンビニ・夜道
- community_series: 集会・複数人・Discord/Spaces後の空気・まとめ画像
- quiet_strength_series: 強さを叫ばず、残る感じ
- poster_summary_series: 複数コマ・短いコピー・保存されるまとめ

## S Rank Mapping

### S1. 気づくと、こればっか着てる

- source: `v2 Stock 1 / v1 Stock 1`
- series: `lifestyle_series`, `poster_summary_series`
- recommended_image_theme: `日常の中で$villainを着ている複数コマ`
- recommended_image_copy: `$VILLAINは、日常だ。 / 気づくと、こればっか着てる。`
- recommended_composition: `4コマ collage。駅ホーム、カフェ、夜道、コンビニ前。後ろ姿多め。黒streetwear。`
- recommended_file_name: `villain_lifestyle_daily_wear_001.png`
- ready_to_generate: `true`
- ready_to_post: `conditional`
- condition: `画像内表記と権利確認後。本文では $villain 表記に統一。`

### S2. 届いたより、馴染んだ

- source: `v2 Stock 2 / v1 Stock 2`
- series: `lifestyle_series`, `quiet_strength_series`
- recommended_image_theme: `新品感ではなく、何度か着た後の日常`
- recommended_image_copy: `届いたより、馴染んだ。`
- recommended_composition: `1〜3コマ。部屋の椅子、駅、帰り道。服のシワや使用感を少し残す。`
- recommended_file_name: `villain_lifestyle_familiar_001.png`
- ready_to_generate: `true`
- ready_to_post: `false`
- condition: `画像未生成。生成後に権利・表記確認。`

### S3. 集まると、少し見える

- source: `v2 Stock 4`
- series: `community_series`, `poster_summary_series`
- recommended_image_theme: `集会/コミュニティの動きが見えるまとめ画像`
- recommended_image_copy: `集まると、見える。`
- recommended_composition: `複数人の背中、スマホ画面、街角、会話している手元。説明図ではなく現場スナップ風。`
- recommended_file_name: `villain_community_gathering_001.png`
- ready_to_generate: `true`
- ready_to_post: `false`
- condition: `当日の集会/コミュニティ文脈がある時だけ使用。`

### S4. コミュニティが服を動かしてる

- source: `v2 Stock 10`
- series: `community_series`, `lifestyle_series`, `poster_summary_series`
- recommended_image_theme: `服を着た人が街で合流していく感じ`
- recommended_image_copy: `服が、人を動かす。`
- recommended_composition: `3〜5コマ。1人→2人→小さな集まり。駅前、路地、カフェ外。`
- recommended_file_name: `villain_community_apparel_motion_001.png`
- ready_to_generate: `true`
- ready_to_post: `false`
- condition: `コミュニティ文脈が薄い日は使わない。`

## A Rank Mapping

### A1. 普通の日に、$villain

- source: `v2 Stock 3 / v1 Stock 3`
- series: `lifestyle_series`
- recommended_image_theme: `普通の日の街歩き`
- recommended_image_copy: `普通の日に、$villain。`
- recommended_composition: `駅改札、朝のコンビニ、カフェの窓際。顔は見せすぎない。`
- recommended_file_name: `villain_lifestyle_normal_day_001.png`
- ready_to_generate: `true`
- ready_to_post: `false`
- condition: `朝投稿向き。画像未生成。`

### A2. 説明より、着てる人

- source: `v2 Stock 5`
- series: `lifestyle_series`, `community_series`
- recommended_image_theme: `着用者が主役の小さな群像`
- recommended_image_copy: `説明より、着てる人。`
- recommended_composition: `2〜4人。後ろ姿/横顔。服のロゴは見えるが広告っぽくしない。`
- recommended_file_name: `villain_people_wearing_001.png`
- ready_to_generate: `true`
- ready_to_post: `false`
- condition: `人物のAI感が出たらNG。`

### A3. 店っぽいけど、普通の店じゃない

- source: `v2 Stock 6`
- series: `lifestyle_series`, `poster_summary_series`
- recommended_image_theme: `ショップ/入口/街の違和感`
- recommended_image_copy: `普通の店じゃない。`
- recommended_composition: `店外観、看板、服を持つ手元、夜の通り。`
- recommended_file_name: `villain_store_not_normal_001.png`
- ready_to_generate: `true`
- ready_to_post: `false`
- condition: `公式店舗/実店舗と誤認される表現は避ける。`

### A4. ABOUTの文章、まだ強い

- source: `v2 Stock 9`
- series: `poster_summary_series`, `quiet_strength_series`
- recommended_image_theme: `ABOUT文言と日常Apparelの接続`
- recommended_image_copy: `毎日着ろって。`
- recommended_composition: `1枚目に短いコピー、他コマに着用者。白黒寄り、強すぎない。`
- recommended_file_name: `villain_about_daily_001.png`
- ready_to_generate: `true`
- ready_to_post: `false`
- condition: `詩的に寄せすぎず、硬い違和感を残す。`

## B Rank Mapping

### B1. AIが変なところで止まった

- source: `v2 Stock 7`
- series: `poster_summary_series`, `quiet_strength_series`
- recommended_image_theme: `AI実録を事件化するミニポスター`
- recommended_image_copy: `そこ拾うんだ。`
- recommended_composition: `スクリーンショット風だが本物UIを模倣しすぎない。黒背景、短い一言、手元。`
- recommended_file_name: `villain_ai_record_weird_point_001.png`
- ready_to_generate: `true`
- ready_to_post: `false`
- condition: `mining machine結果の反復に見えるなら使わない。`

### B2. 強いより、残る

- source: `v2 Stock 8`
- series: `quiet_strength_series`
- recommended_image_theme: `静かな強さ`
- recommended_image_copy: `強いより、残る方。`
- recommended_composition: `1人の後ろ姿。夜道。コピーは小さめ。余白多め。`
- recommended_file_name: `villain_quiet_strength_001.png`
- ready_to_generate: `true`
- ready_to_post: `false`
- condition: `quote_visual単独なので優先度低。本文が弱い日は使わない。`

## Existing Image Candidate

### cf8fcb9d-0176-43ae-a9a8-0a727eb23625.png

- mapped_to: `S1. 気づくと、こればっか着てる`
- series: `lifestyle_series`, `poster_summary_series`
- ready_to_post: `conditional`
- reason: `日常の複数コマ、Apparel着用、生活感が揃っている。`
- caution: `画像内表記が $VILLAIN 大文字。$villain統一が必須なら修正。`

## Generation Priority

1. `villain_lifestyle_daily_wear_001.png`
2. `villain_community_gathering_001.png`
3. `villain_community_apparel_motion_001.png`
4. `villain_lifestyle_familiar_001.png`
5. `villain_people_wearing_001.png`

## Do Not Generate

- NFT感が強い画像
- 宇宙/サイバーに寄りすぎた画像
- 逆さ三角マーク入り画像
- ロゴが読めない画像
- 顔アップ中心のAI感が強い画像
- 広告バナーのように見える画像
- 長文コピー入り画像

## Final

- next_post_image_set: `S1. 気づくと、こればっか着てる + cf8fcb9d-0176-43ae-a9a8-0a727eb23625.png`
- manual_post_only: `true`
- API_post_ready: `false`
- safe_post_status: `BLOCK`
