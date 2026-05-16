# Villain Required Token Layer v1

- Generated at JST: `2026-05-16T11:20:35+09:00`
- status: `active_local_validation`
- live posting: `NOT_EXECUTED`
- X API write: `NOT_USED`
- upload_media: `NOT_EXECUTED`
- create_tweet: `NOT_EXECUTED`
- mandatory_footer_order: `#着て稼ぐ #villain $PPP @0xmavillain`

## Rule

- 投稿文生成後にmandatory_tokensを検証する。
- 欠けているtokenはfinal text末尾に必ず追加する。
- 重複tokenは1つに整理する。
- token orderは `#着て稼ぐ #villain $PPP @0xmavillain` に固定する。
- mandatory tokenは短文化、自然文最適化、novelty調整で削除しない。

## Integration

- candidate generation: `scripts/generate_villain_candidates.py`
- daily selection: `data/villain_daily_selection.json` final_text gate
- auto_post_pilot: `scripts/auto_post_pilot.py` plan item token verification

## Scan Summary

- files_with_text_findings: `5`
- ppp_missing_findings: `8`

## Missing `$PPP` Findings

- `data/manual_post_results.json` / `manual_post_results[0].post_text`
  - preview: ABOUTの文章、ちょっと強い。 /  / Love $villain, / and wear it daily... /  / 毎日着ろって。 /  / 普通そんなこと言わない。 /  / でもVillainなら、 / まあ言いそう。 /  / #着て稼ぐ #villain @0xmavillain M5Q1C
- `data/manual_post_results.json` / `manual_post_results[1].post_text`
  - preview: 誰かに見せるため、 / だけじゃない服がある。 /  / 自分の側に戻る感じ。 /  / 今日はそれでいい。 /  / #着て稼ぐ #villain @0xmavillain R2J9T
- `data/manual_post_results.json` / `manual_post_results[2].post_text`
  - preview: 強い服って、 / 大声じゃない方がいい。 /  / 黙ってても、 / ちょっと残るやつ。 /  / Villainはそっち。 /  / #着て稼ぐ #villain @0xmavillain R2J9T
- `data/manual_post_results.json` / `manual_post_results[3].post_text`
  - preview: 説明より、 / 着てる人の方が早い。 /  / しかも少しずつ、 / 集まってる。 /  / $villainは、 / そこがちょっと変。 /  / #着て稼ぐ #villain @0xmavillain R2J9T
- `data/villain_dry_run_payloads.json` / `payloads[0].caption`
  - preview: ABOUTの文章、ちょっと強い。 /  / Love $villain, / and wear it daily... /  / 毎日着ろって。 /  / 普通そんなこと言わない。 /  / でもVillainなら、 / まあ言いそう。 /  / #着て稼ぐ #villain @0xmavillain M5Q1C
- `data/villain_post_metrics.json` / `records[0].text`
  - preview: ABOUTの文章、ちょっと強い。 /  / Love $villain, / and wear it daily... /  / 毎日着ろって。 /  / 普通そんなこと言わない。 /  / でもVillainなら、 / まあ言いそう。 /  / #着て稼ぐ #villain @0xmavillain M5Q1C
- `data/villain_post_queue.json` / `queue[0].text`
  - preview: ABOUTの文章、ちょっと強い。 /  / Love $villain, / and wear it daily... /  / 毎日着ろって / 普通にすごいこと言ってる。 /  / でもVillainなら / まあ言いそう。 /  / #着て稼ぐ #villain @0xmavillain M5Q1C
- `data/villain_post_template.json` / `filled_example.post_body.final_text`
  - preview: Web3の入口は、難しくなくていい。 /  / まず着る。 / 次に投稿する。 / そして、仲間が増える。 /  / Villainはその順番で動く。 /  / #着て稼ぐ #villain @0xmavillain P3L6B

## All Token Findings

### `data/manual_post_results.json`
- `manual_post_results[0].post_text`
  - missing_before: `$PPP`
  - duplicates_before: `none`
  - changed_by_normalizer: `true`
- `manual_post_results[1].post_text`
  - missing_before: `$PPP`
  - duplicates_before: `none`
  - changed_by_normalizer: `true`
- `manual_post_results[2].post_text`
  - missing_before: `$PPP`
  - duplicates_before: `none`
  - changed_by_normalizer: `true`
- `manual_post_results[3].post_text`
  - missing_before: `$PPP`
  - duplicates_before: `none`
  - changed_by_normalizer: `true`
### `data/villain_dry_run_payloads.json`
- `payloads[0].caption`
  - missing_before: `$PPP`
  - duplicates_before: `none`
  - changed_by_normalizer: `true`
### `data/villain_post_metrics.json`
- `records[0].text`
  - missing_before: `$PPP`
  - duplicates_before: `none`
  - changed_by_normalizer: `true`
### `data/villain_post_queue.json`
- `queue[0].text`
  - missing_before: `$PPP`
  - duplicates_before: `none`
  - changed_by_normalizer: `true`
### `data/villain_post_template.json`
- `filled_example.post_body.final_text`
  - missing_before: `$PPP`
  - duplicates_before: `none`
  - changed_by_normalizer: `true`
