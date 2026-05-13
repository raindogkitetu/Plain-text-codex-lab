# Villain Post Selector v1

- status: `REPORT_ONLY`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- safe_post_status: `BLOCK`

## Inputs

- `reports/villain_post_stock_v1.md`
- `reports/villain_post_stock_v2.md`
- `reports/villain_x_current_analysis.md`
- `reports/villain_boss_attention_os.md`
- `reports/villain_learning_analysis.md`
- `reports/villain_scroll_stop_analysis.md`
- `reports/villain_image_type_analysis.md`

## Selection Logic

優先:

1. boss_attention_score
2. lifestyle / community / apparel_focus
3. scroll_stopが強い1行目
4. 19:00-22:30に合う投稿
5. ボスが拾いやすい現場感

回避:

- 同カテゴリ連投
- 同じ空気感の連投
- 直近弱かった `quote_visual` / 詩的すぎる投稿
- `old/new mining machineの結果！` 型の反復
- `quote_visual` 単独
- 画像だけに頼る poster_summary

## 1. 今日の推奨投稿TOP3

### TOP 1

- stock: `v2 Stock 1`
- post_title: `気づくと、こればっか着てる`
- category: `boss_attention`, `lifestyle`, `apparel_focus`, `poster_summary`
- recommended_image_type: `poster_summary / apparel_focus collage`
- recommended_time_window: `19:00-22:30`
- ooguri反応期待値: `92/100`
- selector_rank: `S`

#### social_post_text

```text
気づくと、
こればっか着てる。

説明しづらいけど、
“なんか合う”。

$villain

@0xmavillain C14QB
```

#### reason

- X現状分析で一番強かったのが `届いた〜！` 系の生活感 + 画像。
- ボス反応OSでは現場感/Apparel x 人を最優先カテゴリに設定。
- `poster_summary` 単独ではなく、日常Apparel文脈がある。
- 直近弱かった `quote_visual` の抽象ポエムから離れている。
- 疲れている日でも出しやすい短さ。

### TOP 2

- stock: `v2 Stock 4`
- post_title: `集まると、少し見える`
- category: `community`, `boss_attention`, `poster_summary`
- recommended_image_type: `community summary / gathering collage`
- recommended_time_window: `19:00-22:30`
- ooguri反応期待値: `90/100`
- selector_rank: `S`

#### social_post_text

```text
集まると、
少し見える。

これは服だけじゃなくて、
たぶん動き。

$villain

@0xmavillain C14QB
```

#### reason

- ボスに拾われやすいのは一般バズよりコミュニティ波及。
- 集会まとめ画像は保存性と文化拡張の両方がある。
- ただし集会/コミュニティ文脈が今日ある時だけ使う。
- 今日その文脈が薄いならTOP 1を優先。

### TOP 3

- stock: `v2 Stock 10`
- post_title: `コミュニティが服を動かしてる`
- category: `community`, `boss_attention`, `apparel_focus`, `poster_summary`
- recommended_image_type: `community + apparel summary`
- recommended_time_window: `18:00-22:30`
- ooguri反応期待値: `89/100`
- selector_rank: `S`

#### social_post_text

```text
服が先か、
人が先か。

Villain見てると、
たまに分からなくなる。

$villain

@0xmavillain C14QB
```

#### reason

- Apparelとコミュニティを両方入れられる。
- ボスが補足しやすい余白がある。
- TOP 2より少し思想寄りなので、疲れている日はTOP 1の方が安全。

## 2. 推奨画像タイプ

今日の第一候補:

- `poster_summary / apparel_focus collage`

条件:

- 広告っぽすぎない
- 日常の中で `$villain` を着ている
- 複数コマでも情報量を増やしすぎない
- 画像内コピーは短くする
- 逆さ三角マークは使わない

## 3. 推奨時間

第一候補:

- `19:00-22:30`

理由:

- Apparel/日常/ボス反応狙いは夜が合いやすい。
- X現状分析でも19時台は強い投稿がある。

代替:

- `07:00-08:30`

使う条件:

- 軽い日常投稿として出す時。
- 画像の情報量が少ない時。

## 4. do_not_use_today

- `quote_visual` 単独
- `強いより、残る` 系の短文だけ投稿
- `old/new mining machineの結果！` 型
- 説明系explainerの連投
- ボスに媚びて見える投稿
- 画像内コピーが強すぎて本文が負ける投稿
- 画像権利/表記確認が済んでいない画像

## 5. 疲れてる日でも迷わない運用

### 30秒判断

1. 画像があるか
2. Apparelか日常感があるか
3. ボスが拾える余白があるか
4. quote_visual単独ではないか
5. 19:00-22:30に出せるか

全部OKならTOP 1。

### 今日の最短投稿

```text
気づくと、
こればっか着てる。

説明しづらいけど、
“なんか合う”。

$villain

@0xmavillain C14QB
```

### 疲れてる日の禁止

- 新しく深いことを言おうとしない
- 画像の意味を説明しない
- ボス向けに寄せすぎない
- 迷ったら投稿しない

## Final Selector Result

- today_recommendation: `v2 Stock 1`
- reason: `生活感 + apparel_focus + poster_summary + boss_attention_score 92`
- manual_post_only: `true`
- API_post_ready: `false`
- safe_post_status: `BLOCK`
