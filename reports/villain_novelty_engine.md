# Villain Novelty Engine v1

- Generated at JST: `2026-05-16`
- status: `DESIGN_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- commit: `NOT_EXECUTED`
- design DB: `data/villain_novelty_engine.json`

## 1. Concept

Novelty Engine は、「伸びそう」ではなく「見たことない」を定量化するためのレイヤー。

現在のVillain OSは、quality / residual / selection が強くなっている。これは安定した勝ち筋を作る。一方で、同じ黒パーカー、同じ夜景、同じ背中、同じ短文観測が続くと、完成度は高くてもタイムライン上では既視感になる。

Novelty は奇抜さそのものではない。

定義:

> 過去のVillain投稿・画像・文体・人格パターンからどれだけズレていて、それでもVillain文脈として読めるか。

つまり「ランダム」ではなく、「Villainらしいのに見たことない」こと。

## 2. Novelty Score

`novelty_score` は以下の8要素で見る。

| component | weight | meaning |
|---|---:|---|
| `visual_novelty` | 16 | 見た目が過去画像と違うか |
| `context_novelty` | 14 | 文脈が違うか。店、机、移動、集会後など |
| `persona_novelty` | 12 | いつもの観測者から少しズレているか |
| `location_novelty` | 10 | 夜の街以外の場所があるか |
| `composition_novelty` | 12 | 背中・コラージュ・中央配置から外れているか |
| `texture_novelty` | 10 | 汚れ、手ブレ、紙、布、机など質感があるか |
| `lifestyle_residue` | 14 | 生活痕が残っているか |
| `unpredictability` | 12 | 次に何が来るか予測しにくいか |

高Noveltyの目安:

- `80+`: 今日の主力候補にしてよい
- `65-79`: selectionで補正をかける価値あり
- `50-64`: qualityが高いなら使えるが、既視感に注意
- `<50`: 伸びそうでも擦り感が強い

## 3. Saturation Detection

### same_black_hoodie

黒パーカー/黒T/背中ロゴが連続している状態。

penalty: `-12`

対策:

- 服を主役から外す。
- 机、レシート、手元、スマホ画面、集会後の残骸を主役にする。
- 服は「写り込む」程度にする。

### same_city_night

夜景、ネオン、雨の街、背中の繰り返し。

penalty: `-10`

対策:

- 朝の光
- 室内
- コンビニ袋
- 作業机
- カフェのレシート
- 移動中の手元

### same_back_view

後ろ姿構図の連続。

penalty: `-10`

対策:

- 顔を出さずに手元へ寄る。
- 椅子、机、袖、帽子、紙、空のカップを使う。
- 人物が主役ではなく、痕跡が主役の画像にする。

### repeated_phrase

`説明より`, `気づくと`, `残る`, `ちょっと変` などの頻出フック。

penalty: `-12`

対策:

- 一文だけにする。
- 会話ログ風にする。
- 途中で切る。
- 断定せず、メモのように残す。

### repeated_structure

短文観測 + 逆説 + footer の繰り返し。

penalty: `-8`

対策:

- 1行投稿
- 箇条書き未満の断片
- 写真に本文を寄せる
- 日付/場所/残骸から入る

## 4. Lifestyle Residue

生活痕とは、完成された広告ではなく「そこに人がいた」証拠。

Villainが後残り型になりやすいなら、画像も「完成品」より「痕跡」の方が刺さる可能性がある。

生活痕シグナル:

| signal | score | use |
|---|---:|---|
| 手ブレ | 8 | 綺麗すぎない現場感 |
| 汚れ | 8 | 新品広告から離れる |
| レシート | 7 | 生活の具体物 |
| 作業机 | 8 | build/参加/日常の接続 |
| coffee | 6 | 既存の宇宙人コーヒー文脈とも接続 |
| discord | 8 | コミュニティの裏側。ただし個人情報は出さない |
| 集会後 | 10 | community_infoとresidualに強い |
| unfinished feeling | 9 | まだ動いている感じ |

画像テーマ例:

- 集会後の机に残ったカップとステッカー
- レシートの横に畳まれた黒T
- Discordを開いたPCと飲みかけのcoffee
- 作業机の端に置かれた帽子
- コンビニ袋から少し見えるVillain
- 片付け途中の集会メモ
- 着た後の袖、椅子、空のカップ

本文例の方向:

```text
まだ片付いてない。

でも、こういう方が残る。
```

```text
服より先に、
机がVillainになってた。
```

```text
集会のあとって、
少しだけ物が強い。
```

## 5. Ad Feel Penalty

「完成度が高い」が「広告感」に変わると、Villain人格から遠くなる。

| flag | penalty | reason |
|---|---:|---|
| `overpolished` | -12 | 完成されすぎて人の痕跡がない |
| `too_clean` | -10 | 生活が消えている |
| `too_symmetric` | -8 | ポスター広告に見える |
| `generic_ai_visual` | -14 | AI夜景・人物・ロゴの既視感 |
| `catalog_product_shot` | -10 | 服単体紹介に戻る |

広告感を下げる方法:

- 構図を少し崩す。
- 物を少し切る。
- 人を中央に置かない。
- 光を綺麗にしすぎない。
- コピーを言い切りすぎない。
- ロゴを主役にしすぎない。

## 6. Novelty Rotation

### image novelty

72h以内に避ける:

- 同じ画像ファイル
- 黒パーカー背中
- 雨のネオン夜景
- 同じコラージュグリッド

増やす:

- desk residue
- receipt
- coffee
- after gathering
- partial object
- unfinished composition

### wording novelty

2投稿ごとに避ける:

- `説明より`
- `気づくと`
- `残る`
- `ちょっと変`

増やす:

- 一文断片
- ログ風
- 聞こえた一言
- 未完成メモ
- 短い矛盾

例:

```text
これ、広告じゃなくて残骸。
```

```text
今日のVillain、
机の上にいた。
```

```text
きれいに撮ると、
少し嘘になる。
```

### persona novelty

3投稿ごとに人格をずらす。

| persona | role |
|---|---|
| `culture_observer` | 文化の違和感を見る |
| `community_operator` | 集まりや動きを残す |
| `quiet_apparel_witness` | 服を説明せず生活に置く |
| `afterparty_recorder` | 集会後の痕跡を拾う |
| `desk_side_builder` | 作業机・制作・参加の気配を見る |
| `anti_ad_copywriter` | 広告っぽさを壊す |

## 7. Remixability

今回の重要観測:

ボス側アカウントが、鬼徹の投稿画像を抜粋して再投稿していた。

これは「投稿がRTされた」ではなく、「画像そのものが拾われた」状態。つまり、投稿全体ではなく、画像・一文・空気がコミュニティ素材として再利用され始めている。

流れ:

```text
投稿
↓
画像がコミュニティ素材化
↓
他人が再利用
↓
二次拡散
↓
インプ加速
```

ここで起きているのは、単なるブランド投稿の拡散ではなく `remixability`。

定義:

> 投稿全体ではなく、画像・一文・空気が他人に拾われ、再投稿・切り抜き・引用・スクショで二次拡散されやすい度合い。

重要なのは、完成された広告として見られることではない。

他人が「これ、自分たちの空気として使える」と感じること。

### Remixability Score

`remixability_score` は以下で見る。

| component | weight | meaning |
|---|---:|---|
| `quoteability` | 16 | 引用しやすいか |
| `reusable_visual` | 18 | 画像だけで再利用できるか |
| `community_reposting_probability` | 18 | コミュニティ内で再投稿されそうか |
| `identity_attachment` | 16 | 見た人が自分のidentityとして持てるか |
| `phrase_portability` | 14 | 一文だけ抜いても成立するか |
| `screenshot_reuse_fit` | 10 | スクショで文脈が壊れにくいか |
| `cropability` | 8 | 切り抜いても強いか |

強いシグナル:

- 一文で成立する
- 画像だけでも空気がある
- “自分も言いたくなる”
- スクショ再利用しやすい
- 引用しやすい
- 切り抜きやすい
- 他人が自分の言葉として使いやすい

減点:

- 広告として完成しすぎている
- 鬼徹個人に閉じすぎている
- 長い背景説明が必要
- ロゴや導線が強すぎて、素材ではなく広告に見える

### Current Case

今回のケースは、`brand_post` ではなく `community_culture_material` に近い。

観測:

- 画像単体でも成立している
- 一文だけでも空気が伝わる
- 他人が自分の言葉として使いやすい
- culture / identity の素材になり始めている
- 二次拡散がインプ加速に接続しうる

次の打ち手:

- 完成された広告画像より、拾いやすい画像を増やす。
- 画像内コピーは短く、切り抜きに耐える一文にする。
- 投稿文は説明しすぎず、画像が再利用される余白を残す。
- `poster_summary` と `culture_observer` は、`remixability_score` をselectionで見る。
- 「人が言いたくなる一文」を、画像側にも本文側にも置く。

## 8. Integration

### Image Strategy

追加候補:

- 各画像に `novelty_tags` を持たせる。
- `ad_feel_risk` を持たせる。
- `remixability_tags` を持たせる。
- `reusable_visual` と `cropability` を画像ごとに見る。
- `same_image_cooldown` と接続する。

### Candidate Stream

stream item の `scores` に追加する。

```json
{
  "scores": {
    "novelty_score": null,
    "remixability_score": null,
    "visual_novelty": null,
    "context_novelty": null,
    "persona_novelty": null,
    "quoteability": null,
    "reusable_visual": null,
    "community_reposting_probability": null,
    "identity_attachment": null,
    "phrase_portability": null,
    "lifestyle_residue_score": null,
    "ad_feel_risk": null
  },
  "novelty": {
    "saturation_flags": [],
    "lifestyle_residue_signals": [],
    "rotation_hint": "",
    "why_it_feels_new": ""
  },
  "remixability": {
    "remixability_signals": [],
    "reuse_surface": "",
    "why_others_can_pick_it_up": "",
    "recommended_format": ""
  }
}
```

### Daily Selection

Daily Selectionに以下を追加する候補。

- `novelty_score`
- `remixability_score`
- `saturation_penalty`
- `same_image_cooldown`
- `same_persona_decay`
- `lifestyle_residue_bonus`
- `reusable_visual_bonus`
- `quoteability_bonus`

考え方:

- qualityが高くてもnoveltyが低い候補は、主力slotから外す。
- noveltyが高く、riskが低い候補は、多少qualityが低くてもテスト枠に入れる。
- remixabilityが高い候補は、広告感が多少低くても実戦テスト枠に入れる。
- 画像が拾われやすい候補は、profile_clickだけでなく二次拡散を評価する。

### Residual Learning

24h後に、以下を見たい。

- noveltyが高い投稿はimpressionsの後伸びがあるか。
- lifestyle_residueはprofile_clicksに効くか。
- remixabilityが高い画像は、引用/再投稿/スクショ再利用に繋がるか。
- 画像単体の二次利用が、投稿本体の遅延impressionsを押し上げるか。
- generic_ai_visualは初速だけで止まるか。
- anti_ad_copyは保存/返信/プロフィール誘導に効くか。

### Generated Candidates

seed生成時に、毎回1本は `novelty_test` を混ぜる。
また、毎回1本は `remixability_test` として「拾いやすい一文/画像」を混ぜる。

例:

- `after_gathering_residue`
- `desk_side_villain`
- `receipt_lifestyle`
- `unfinished_postcard`
- `anti_clean_visual`
- `one_line_repost_material`
- `croppable_identity_image`
- `community_screenshot_phrase`

## 9. Novelty Test Slots

1日3-5本のうち、最低1本はNovelty Testにする。
加えて、最低1本はRemixability Testにする。

推奨:

- morning: lifestyle residue light
- daytime: desk/receipt/coffee
- night: anti-ad culture observer
- late_night: after gathering / unfinished feeling
- remix slot: one sentence + reusable visual + low explanation density

ただし、late_nightの主力を毎回noveltyにしない。23時台は勝ち枠でもあるため、NoveltyとResidualのバランスを見る。

## 10. Current Saturation Hypothesis

飽和し始めている可能性:

- 黒パーカー
- 都市夜景
- 後ろ姿
- poster collage
- `説明より` 系の観測フック
- `残る` 系の結論
- きれいにまとまったAI visual

次の打ち手:

- 服を主役から外す。
- 人物を主役から外す。
- 夜景を減らす。
- 完成画像より生活痕を使う。
- 1本は「少し汚いが本物っぽい」候補を混ぜる。
- 1本は「他人が拾える素材」候補を混ぜる。

## 11. Why Novelty Can Beat Quality

Qualityは、安心して読める状態を作る。

でもタイムラインでは、安心して読めるものほど通過される瞬間がある。特に同じ黒、同じ夜景、同じ背中、同じ短文構造が続くと、読者は内容を見る前に「見たことある」と判断する。

Noveltyが強い瞬間は、その自動判定を止める。

「これは何だ」
「いつものVillainだけど、少し違う」
「広告じゃなくて、何か残ってる」

この違和感が、scroll stopになる。

Villain人格はもともと、完璧な広告より「少し変な観測」に強い。だから完成度だけを上げ続けると、むしろ人格が薄くなる。生活痕、未完成感、場所のズレ、言葉の崩れが入ると、Villainの「現場を見て、短く残す人」という芯が戻る。

結論: Noveltyはqualityの代替ではない。qualityが作った型を、飽和する前にずらすためのエンジン。見たことないのにVillainだと分かる、その瞬間だけqualityより強くなる。

## 12. RealityGuard

- 投稿実行なし。
- create_tweetなし。
- upload_mediaなし。
- X API writeなし。
- commitなし。
- このOSは設計のみ。
