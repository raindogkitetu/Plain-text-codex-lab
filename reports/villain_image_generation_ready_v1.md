# Villain Image Generation Ready v1

- status: `REPORT_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- safe_post_status: `BLOCK`
- inputs: `villain_image_batch_plan_v1.md`, `villain_image_post_mapping_v1.md`, `villain_post_stock_v2.md`

## Quality Conditions

- `$villain` 表記を統一する。
- 逆さ三角マークは禁止。
- スマホ縮小でも文字が読める。
- 情報量を増やしすぎない。
- “広告感”より“生活感”。
- ooguriが拾いやすい現場感を入れる。
- AIっぽさを軽減する。
- poster_summary寄りにする。

## S Rank

### Image 1

- image_id: `vln-img-batch-001`
- linked_post_title: `気づくと、こればっか着てる`
- exact_image_copy: `$villainは、日常だ。 / 気づくと、こればっか着てる。`
- recommended_filename: `villain_lifestyle_daily_wear_001.png`
- image_series: `lifestyle_series`, `poster_summary_series`
- ready_to_generate: `true`
- linked_post_ready: `true`

#### final_visual_prompt_jp

```text
日本の都会の日常で、黒いstreetwearの$villainを着た人たち。4コマのposter_summary collage。駅ホーム、夜道、カフェ、コンビニ前。人物は20〜40代、男女混在、後ろ姿や横顔中心。広告感ではなく、実際に着て生活している雰囲気。文字は少なめで、スマホ縮小でも読める大きさ。「$villainは、日常だ。」「気づくと、こればっか着てる。」だけを入れる。黒、ネオン緑、少しピンク。AIっぽさを減らし、写真っぽく、現場感を出す。逆さ三角マークは入れない。
```

#### final_visual_prompt_en

```text
Realistic Japanese urban everyday-life poster-summary collage for $villain streetwear. Four panels: train station platform, night street, small cafe, convenience store front. People aged 20-40, mixed gender, ordinary but atmospheric, wearing black $villain hoodies, T-shirts, and caps. Mostly back views and side profiles. Not an advertisement, more like real people wearing it in daily life. Minimal readable text, large enough for mobile: "$villainは、日常だ。" and "気づくと、こればっか着てる。" Black palette with neon green and a little pink. Reduce AI look, make it grounded, photographic, and lived-in. Do not include any inverted triangle mark.
```

#### negative_prompt

```text
inverted triangle mark, NFT style, space background, cyber fantasy, glossy advertisement, luxury fashion ad, too much text, unreadable logo, face close-up, AI-looking hands, distorted typography, fake brand marks, profit guarantee, investment language
```

### Image 2

- image_id: `vln-img-batch-002`
- linked_post_title: `集まると、少し見える`
- exact_image_copy: `集まると、見える。`
- recommended_filename: `villain_community_gathering_001.png`
- image_series: `community_series`, `poster_summary_series`
- ready_to_generate: `true`
- linked_post_ready: `conditional`

#### final_visual_prompt_jp

```text
$villainを着た少人数のコミュニティが、夜の街角やカフェ外で自然に集まっているposter_summary画像。複数コマ、スマホを見る手元、背中、横顔、街灯、会話の気配。説明図ではなく現場スナップ風。文字は「集まると、見える。」だけ。スマホ縮小でも読める大きさ。黒い服、ネオン緑、少しピンク。ボスが拾いやすい文化感、コミュニティが動いている感じ。逆さ三角マークは入れない。
```

#### final_visual_prompt_en

```text
Poster-summary collage of a small $villain community gathering in a realistic Japanese city at night. Multiple panels: people in black $villain streetwear meeting near a cafe, hands holding phones, back views, side profiles, quiet conversations under street lights. Not an infographic, more like candid documentary snapshots. Minimal readable text: "集まると、見える。". Black clothing, neon green accents, a little pink, grounded community culture, something ooguri could naturally pick up. No inverted triangle mark.
```

#### negative_prompt

```text
inverted triangle mark, crowd festival, fake conference stage, crypto hype, NFT art, too many diagrams, excessive text, faces too perfect, luxury ad, aggressive slogans, profit language
```

### Image 3

- image_id: `vln-img-batch-003`
- linked_post_title: `コミュニティが服を動かしてる`
- exact_image_copy: `服が、人を動かす。`
- recommended_filename: `villain_community_apparel_motion_001.png`
- image_series: `community_series`, `lifestyle_series`, `poster_summary_series`
- ready_to_generate: `true`
- linked_post_ready: `conditional`

#### final_visual_prompt_jp

```text
黒い$villain streetwearを着た人が、1人から2人、そして小さな集まりになっていくposter_summary collage。駅前、細い路地、カフェの外、夜の歩道。後ろ姿中心で、服の$villainロゴは自然に読める。文字は「服が、人を動かす。」のみ。スマホ縮小でも読めるように大きめ。広告ではなく、文化が街で動いている感じ。AIっぽい顔や手を避ける。逆さ三角マークは禁止。
```

#### final_visual_prompt_en

```text
Realistic poster-summary collage showing $villain apparel bringing people together. Panels progress from one person walking alone, to two people meeting, to a small group outside a cafe. Japanese city, station area, narrow street, night sidewalk. Mostly back views, subtle readable $villain logos on black streetwear. Minimal mobile-readable text: "服が、人を動かす。". Not an ad, more like culture moving through the city. Avoid AI-looking faces and hands. No inverted triangle mark.
```

#### negative_prompt

```text
inverted triangle mark, corporate advertisement, giant crowd, futuristic space city, NFT look, excessive neon, unreadable text, face close-up, influencer pose, profit guarantee
```

## A Rank

### Image 4

- image_id: `vln-img-batch-004`
- linked_post_title: `届いたより、馴染んだ`
- exact_image_copy: `届いたより、馴染んだ。`
- recommended_filename: `villain_lifestyle_familiar_001.png`
- image_series: `lifestyle_series`, `quiet_strength_series`
- ready_to_generate: `true`
- linked_post_ready: `true`

#### final_visual_prompt_jp

```text
何度か着た後の黒い$villainパーカーやTシャツ。新品感ではなく、少し馴染んだ質感。部屋の椅子、駅のベンチ、帰り道、カフェの椅子に自然に置かれた服。1〜3コマ。文字は「届いたより、馴染んだ。」だけで、スマホ縮小でも読める大きさ。静かでリアル、生活に入っている感じ。広告感なし。逆さ三角マークは禁止。
```

#### final_visual_prompt_en

```text
Quiet realistic lifestyle image of black $villain hoodie and T-shirt after being worn several times. Not new-product photography; slightly lived-in fabric texture. One to three panels: on a chair at home, station bench, evening walk, cafe chair. Minimal mobile-readable text: "届いたより、馴染んだ。". Calm, grounded, everyday, not commercial. No inverted triangle mark.
```

#### negative_prompt

```text
inverted triangle mark, product catalog, glossy ad, perfect model pose, excessive branding, NFT style, too much text, dirty clothing, luxury fashion editorial
```

### Image 5

- image_id: `vln-img-batch-005`
- linked_post_title: `説明より、着てる人`
- exact_image_copy: `説明より、着てる人。`
- recommended_filename: `villain_people_wearing_001.png`
- image_series: `lifestyle_series`, `community_series`
- ready_to_generate: `true`
- linked_post_ready: `true`

#### final_visual_prompt_jp

```text
$villainを着ている2〜4人の小さな群像。街角、駅前、カフェ外。後ろ姿と横顔中心。服の$villainロゴは自然に見える。説明より着ている人を見せる。文字は「説明より、着てる人。」だけで、スマホ縮小でも読める。広告感なし、普通だけど雰囲気がある人たち。AIっぽさを避ける。逆さ三角マークは禁止。
```

#### final_visual_prompt_en

```text
Small group of 2-4 ordinary but atmospheric people wearing black $villain streetwear in a Japanese city. Street corner, station area, outside a cafe. Mostly back views and side profiles. Logos visible naturally, not staged. Minimal mobile-readable text: "説明より、着てる人。". Documentary-like, everyday, no ad feel. Reduce AI look. No inverted triangle mark.
```

#### negative_prompt

```text
inverted triangle mark, fashion campaign, influencer posing, face close-up, perfect models, crypto hype, NFT style, too much text, unreadable logos
```

### Image 6

- image_id: `vln-img-batch-006`
- linked_post_title: `普通の日に、$villain`
- exact_image_copy: `普通の日に、$villain。`
- recommended_filename: `villain_lifestyle_normal_day_001.png`
- image_series: `lifestyle_series`
- ready_to_generate: `true`
- linked_post_ready: `true`

#### final_visual_prompt_jp

```text
普通の朝、駅改札、コンビニ、カフェの窓際。黒い$villain Tシャツやパーカーを自然に着ている人物。顔は見せすぎず、後ろ姿や横顔。文字は「普通の日に、$villain。」だけで、スマホ縮小でも読める。明るすぎず、日常の静かな空気。広告感なし。逆さ三角マークは禁止。
```

#### final_visual_prompt_en

```text
Normal morning in urban Japan: station gate, convenience store, cafe window. A person naturally wearing black $villain T-shirt or hoodie. Mostly back view or side profile, not posing. Minimal mobile-readable text: "普通の日に、$villain。". Quiet everyday atmosphere, not too bright, realistic, no ad feel. No inverted triangle mark.
```

#### negative_prompt

```text
inverted triangle mark, glossy commercial, luxury styling, NFT aesthetic, too much neon, face close-up, unreadable text, profit language
```

## Ready Order

1. `vln-img-batch-001` / `villain_lifestyle_daily_wear_001.png`
2. `vln-img-batch-002` / `villain_community_gathering_001.png`
3. `vln-img-batch-003` / `villain_community_apparel_motion_001.png`
4. `vln-img-batch-004` / `villain_lifestyle_familiar_001.png`
5. `vln-img-batch-005` / `villain_people_wearing_001.png`
6. `vln-img-batch-006` / `villain_lifestyle_normal_day_001.png`

## Final

- generation_ready_count: `6`
- S_rank_ready_count: `3`
- A_rank_ready_count: `3`
- manual_post_only: `true`
- API_post_ready: `false`
- safe_post_status: `BLOCK`
