#!/usr/bin/env python3
"""Analyze recent raindog_kitetu X posts with read-only requests.

Report-only. This script reads local .env values but never prints credentials,
lengths, or partials. It performs GET-only X API requests, writes a Markdown
analysis, and never posts, uploads media, creates tweets, or calls write APIs.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
REPORT_PATH = ROOT / "reports" / "villain_x_current_analysis.md"
JST = ZoneInfo("Asia/Tokyo")

VERIFY_URL = "https://api.twitter.com/1.1/account/verify_credentials.json"
TWEETS_URL_TEMPLATE = "https://api.twitter.com/2/users/{user_id}/tweets"
REQUIRED_KEYS = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]

VILLAIN_TERMS = ("villain", "0xmavillain", "着て稼ぐ", "$villain", "VILLAIN", "Villain")
CORE_CATEGORIES = ("community_info", "poster_summary", "apparel_focus", "observer_ai_record")


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def percent_encode(value: str) -> str:
    return urllib.parse.quote(value, safe="~")


def oauth_header(method: str, url: str, query: dict[str, str], env: dict[str, str]) -> str:
    oauth_params = {
        "oauth_consumer_key": env["X_API_KEY"],
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": env["X_ACCESS_TOKEN"],
        "oauth_version": "1.0",
    }
    signing_params = {**query, **oauth_params}
    normalized = "&".join(
        f"{percent_encode(key)}={percent_encode(value)}"
        for key, value in sorted(signing_params.items())
    )
    base_string = "&".join([method.upper(), percent_encode(url), percent_encode(normalized)])
    signing_key = (
        f"{percent_encode(env['X_API_SECRET'])}&"
        f"{percent_encode(env['X_ACCESS_TOKEN_SECRET'])}"
    )
    digest = hmac.new(
        signing_key.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha1,
    ).digest()
    oauth_params["oauth_signature"] = base64.b64encode(digest).decode("ascii")
    return "OAuth " + ", ".join(
        f'{percent_encode(key)}="{percent_encode(value)}"'
        for key, value in sorted(oauth_params.items())
    )


def get_json(url: str, query: dict[str, str], env: dict[str, str]) -> tuple[bool, int, dict[str, Any]]:
    full_url = url + "?" + urllib.parse.urlencode(query)
    request = urllib.request.Request(
        full_url,
        headers={
            "Authorization": oauth_header("GET", url, query, env),
            "User-Agent": "villain-x-current-analysis/0.1",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            body = response.read().decode("utf-8")
            return True, response.status, json.loads(body)
    except urllib.error.HTTPError as error:
        try:
            body = json.loads(error.read().decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = {"error": f"HTTP {error.code}"}
        return False, error.code, body
    except urllib.error.URLError:
        return False, 0, {"error": "network or connection error"}


def profile(env: dict[str, str]) -> tuple[bool, str, str]:
    query = {"include_entities": "false", "skip_status": "true"}
    ok, status, data = get_json(VERIFY_URL, query, env)
    if not ok:
        return False, "", f"profile_check_failed_http_{status}"
    return True, str(data.get("id_str", "")), data.get("screen_name", "")


def fetch_recent_tweets(env: dict[str, str], user_id: str) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    base_url = TWEETS_URL_TEMPLATE.format(user_id=user_id)
    common = {
        "max_results": "30",
        "tweet.fields": "created_at,public_metrics,non_public_metrics,organic_metrics,attachments",
        "expansions": "attachments.media_keys",
        "media.fields": "type,url,preview_image_url,width,height,alt_text",
        "exclude": "retweets",
    }
    ok, status, data = get_json(base_url, common, env)
    if ok:
        return "private_metrics_available", data.get("data", []), data

    fallback = {
        **common,
        "tweet.fields": "created_at,public_metrics,attachments",
    }
    ok, status, data = get_json(base_url, fallback, env)
    if ok:
        return "public_metrics_only", data.get("data", []), data
    return f"fetch_failed_http_{status}", [], data


def is_villain_related(tweet: dict[str, Any]) -> bool:
    text = tweet.get("text", "")
    return any(term.lower() in text.lower() for term in VILLAIN_TERMS)


def impression_count(tweet: dict[str, Any]) -> int | None:
    for key in ("non_public_metrics", "organic_metrics"):
        metrics = tweet.get(key, {})
        value = metrics.get("impression_count")
        if isinstance(value, int):
            return value
    return None


def public_engagement(tweet: dict[str, Any]) -> int:
    metrics = tweet.get("public_metrics", {})
    return (
        metrics.get("like_count", 0)
        + metrics.get("reply_count", 0) * 2
        + metrics.get("retweet_count", 0) * 3
        + metrics.get("quote_count", 0) * 3
    )


def first_available_metric(tweet: dict[str, Any], key: str) -> int | None:
    for metric_group in ("public_metrics", "non_public_metrics", "organic_metrics"):
        metrics = tweet.get(metric_group, {})
        value = metrics.get(key)
        if isinstance(value, int):
            return value
    return None


def metric_value(tweet: dict[str, Any], key: str) -> int:
    value = first_available_metric(tweet, key)
    return value if isinstance(value, int) else 0


def first_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def parsed_created_at(created_at: str) -> datetime | None:
    try:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError:
        return None


def age_hours(created_at: str) -> float | None:
    dt = parsed_created_at(created_at)
    if not dt:
        return None
    return (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds() / 3600


def hour_window(created_at: str) -> str:
    dt = parsed_created_at(created_at)
    if not dt:
        return "unknown"
    hour = dt.astimezone(JST).hour
    if 7 <= hour < 9:
        return "07:00-08:30"
    if 12 <= hour < 13:
        return "12:00-13:00"
    if 19 <= hour < 23:
        return "19:00-22:30"
    if hour == 23:
        return "23:00-23:59"
    return f"{hour:02d}:00-other"


def infer_image_type(tweet: dict[str, Any], media_by_key: dict[str, dict[str, Any]]) -> str:
    text = tweet.get("text", "").lower()
    first = first_line(tweet.get("text", "")).lower()
    media_keys = tweet.get("attachments", {}).get("media_keys", [])
    alt_text = " ".join(media_by_key.get(key, {}).get("alt_text", "") or "" for key in media_keys).lower()
    joined = f"{text}\n{alt_text}"
    compact_text = re.sub(r"\s+", "", text)
    if first.startswith("@"):
        return "reply_text"
    if "mining machine" in joined or "の結果" in joined:
        return "observer_ai_record"
    if "届いた" in joined or "到着" in joined:
        return "apparel_focus"
    if len(compact_text) <= 90 and any(word in joined for word in ("強そう", "残る", "静かな", "薄い")):
        return "quote_visual"
    if any(word in joined for word in ("集会", "コミュニティ", "community", "space", "まとめ")):
        return "community_info"
    if any(word in joined for word in ("設計", "理由", "実装", "dao", "参入障壁", "ホルダー", "特典")):
        return "explainer_poster"
    if any(word in joined for word in ("quote", "言葉", "強そう", "残る")):
        return "quote_visual"
    if any(word in joined for word in ("服", "apparel", "wear", "daily")):
        return "apparel_focus"
    if any(word in joined for word in ("poster", "ポスター", "着て稼ぐ", "$villain")):
        return "poster_summary"
    if media_keys:
        return "image_unknown"
    return "text_only"


def enrich(tweets: list[dict[str, Any]], raw: dict[str, Any]) -> list[dict[str, Any]]:
    media = raw.get("includes", {}).get("media", [])
    media_by_key = {item.get("media_key", ""): item for item in media}
    enriched = []
    for tweet in tweets:
        enriched.append(
            {
                **tweet,
                "impressions": impression_count(tweet),
                "engagement_proxy": public_engagement(tweet),
                "likes": metric_value(tweet, "like_count"),
                "reposts": metric_value(tweet, "retweet_count"),
                "replies": metric_value(tweet, "reply_count"),
                "quotes": metric_value(tweet, "quote_count"),
                "bookmarks": metric_value(tweet, "bookmark_count"),
                "profile_clicks": metric_value(tweet, "user_profile_clicks"),
                "url_link_clicks": metric_value(tweet, "url_link_clicks"),
                "media_count": len(tweet.get("attachments", {}).get("media_keys", [])),
                "first_line": first_line(tweet.get("text", "")),
                "time_window": hour_window(tweet.get("created_at", "")),
                "age_hours": age_hours(tweet.get("created_at", "")),
                "image_type": infer_image_type(tweet, media_by_key),
                "villain_related": is_villain_related(tweet),
            }
        )
    return enriched


def sort_key(tweet: dict[str, Any]) -> int:
    impressions = tweet.get("impressions")
    if isinstance(impressions, int):
        return impressions
    return tweet.get("engagement_proxy", 0)


def summarize_patterns(tweets: list[dict[str, Any]]) -> dict[str, Any]:
    top = sorted(tweets, key=sort_key, reverse=True)[:10]
    mature = [tweet for tweet in tweets if (tweet.get("age_hours") or 0) >= 24]
    low = sorted(mature or tweets, key=sort_key)[:10]
    top_images = Counter(tweet.get("image_type") for tweet in top)
    low_images = Counter(tweet.get("image_type") for tweet in low)
    top_times = Counter(tweet.get("time_window") for tweet in top)
    top_first_lines = [tweet.get("first_line", "") for tweet in top[:5]]
    weak_first_lines = [tweet.get("first_line", "") for tweet in low[:5]]
    return {
        "top_images": top_images,
        "low_images": low_images,
        "top_times": top_times,
        "top_first_lines": top_first_lines,
        "weak_first_lines": weak_first_lines,
    }


def metric_label(tweet: dict[str, Any]) -> str:
    if isinstance(tweet.get("impressions"), int):
        return f"impressions={tweet['impressions']}"
    return f"engagement_proxy={tweet.get('engagement_proxy', 0)}"


def maturity_label(tweet: dict[str, Any]) -> str:
    age = tweet.get("age_hours")
    if not isinstance(age, (int, float)):
        return "age_unknown"
    if age < 24:
        return f"immature_metrics_{age:.1f}h"
    return f"mature_{age:.1f}h"


def tweet_url(username: str, tweet: dict[str, Any]) -> str:
    return f"https://x.com/{username}/status/{tweet.get('id')}"


def category_summary(tweets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for category in sorted({tweet.get("image_type") or "unknown" for tweet in tweets} | set(CORE_CATEGORIES)):
        items = [tweet for tweet in tweets if (tweet.get("image_type") or "unknown") == category]
        if not items:
            continue
        impressions = [tweet.get("impressions") for tweet in items if isinstance(tweet.get("impressions"), int)]
        top = max(items, key=sort_key)
        rows.append(
            {
                "category": category,
                "count": len(items),
                "average_impressions": round(sum(impressions) / len(impressions), 1) if impressions else None,
                "max_impressions": max(impressions) if impressions else None,
                "top_first_line": top.get("first_line", ""),
            }
        )
    return sorted(rows, key=lambda row: row.get("average_impressions") or -1, reverse=True)


def media_summary(tweets: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summary = {}
    for label, has_media in (("image_yes", True), ("image_no", False)):
        items = [tweet for tweet in tweets if bool(tweet.get("media_count")) == has_media]
        impressions = [tweet.get("impressions") for tweet in items if isinstance(tweet.get("impressions"), int)]
        summary[label] = {
            "count": len(items),
            "average_impressions": round(sum(impressions) / len(impressions), 1) if impressions else None,
            "max_impressions": max(impressions) if impressions else None,
        }
    return summary


def time_summary(tweets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for window in sorted({tweet.get("time_window") or "unknown" for tweet in tweets}):
        items = [tweet for tweet in tweets if (tweet.get("time_window") or "unknown") == window]
        impressions = [tweet.get("impressions") for tweet in items if isinstance(tweet.get("impressions"), int)]
        top = max(items, key=sort_key)
        rows.append(
            {
                "window": window,
                "count": len(items),
                "average_impressions": round(sum(impressions) / len(impressions), 1) if impressions else None,
                "max_impressions": max(impressions) if impressions else None,
                "top_first_line": top.get("first_line", ""),
            }
        )
    return sorted(rows, key=lambda row: row.get("average_impressions") or -1, reverse=True)


def conclusion_lines(
    category_rows: list[dict[str, Any]],
    media: dict[str, dict[str, Any]],
    time_rows: list[dict[str, Any]],
) -> list[str]:
    top_categories = [row for row in category_rows if row.get("average_impressions") is not None]
    strongest = top_categories[0] if top_categories else {}
    weakest = top_categories[-1] if top_categories else {}
    category_by_name = {row.get("category"): row for row in top_categories}
    image_yes = media.get("image_yes", {})
    image_no = media.get("image_no", {})
    time_with_impressions = [row for row in time_rows if row.get("average_impressions") is not None]
    strongest_time = time_with_impressions[0] if time_with_impressions else {}
    lines = []
    if strongest:
        lines.append(
            f"- strongest_category: `{strongest.get('category')}` / avg_impressions=`{strongest.get('average_impressions')}` / max=`{strongest.get('max_impressions')}`"
        )
    for category in CORE_CATEGORIES:
        row = category_by_name.get(category)
        if row:
            lines.append(
                f"- core_category_{category}: avg_impressions=`{row.get('average_impressions')}` / max=`{row.get('max_impressions')}` / count=`{row.get('count')}`"
            )
    if weakest and weakest != strongest:
        lines.append(
            f"- weakest_category: `{weakest.get('category')}` / avg_impressions=`{weakest.get('average_impressions')}` / max=`{weakest.get('max_impressions')}`"
        )
    if image_yes.get("average_impressions") is not None and image_no.get("average_impressions") is not None:
        image_direction = "image_attached_stronger" if image_yes["average_impressions"] >= image_no["average_impressions"] else "image_less_stronger"
        lines.append(
            f"- media_direction: `{image_direction}` / image_yes_avg=`{image_yes.get('average_impressions')}` / image_no_avg=`{image_no.get('average_impressions')}`"
        )
    if strongest_time:
        lines.append(
            f"- strongest_time_window_by_avg_impressions: `{strongest_time.get('window')}` / avg_impressions=`{strongest_time.get('average_impressions')}` / max=`{strongest_time.get('max_impressions')}`"
        )
    if strongest.get("category") in {"community_info", "poster_summary"}:
        lines.append("- operating_mode: `community/culture observation is currently stronger than clothing-only introduction`")
    elif strongest.get("category") == "apparel_focus":
        lines.append("- operating_mode: `apparel focus is leading in this run; validate against community/culture posts before scaling`")
    observer = category_by_name.get("observer_ai_record")
    apparel = category_by_name.get("apparel_focus")
    if observer and (observer.get("average_impressions") or 0) < 40:
        lines.append("- reduce_pattern: `plain old/new mining machine result reports need a story or community context before posting repeatedly`")
    if apparel and strongest and apparel.get("category") != strongest.get("category"):
        lines.append("- apparel_focus_note: `clothing-only posts are not the lead category in this run`")
    return lines


def analysis_state(mode: str, tweets: list[dict[str, Any]], analyzed: list[dict[str, Any]]) -> tuple[str, str]:
    if mode.startswith("fetch_failed"):
        return "FAILED", mode
    if not tweets:
        return "FAILED", "zero_tweets_fetched"
    if not analyzed:
        return "PARTIAL", "no_villain_related_tweets_found"
    if mode == "public_metrics_only":
        return "PARTIAL", "private_metrics_unavailable_public_metrics_only"
    return "SUCCESS", "analysis_completed"


def write_failure_report(status: str, reason: str, extra_lines: list[str] | None = None) -> None:
    lines = [
        "# Villain X Current Analysis",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        f"- status: `{status}`",
        "- mode: `DRY_RUN_ONLY`",
        "- read_only: `true`",
        f"- reason: `{reason}`",
        "- live posting: `NOT_EXECUTED`",
        "- X_API_WRITE: `NOT_USED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        "- credentials_displayed: `false`",
    ]
    if extra_lines:
        lines.extend(extra_lines)
    lines.extend(
        [
            "",
            "## RealityGuard",
            "",
            "- GET-only read analysis.",
            "- No post was created.",
            "- No media was uploaded.",
            "- No write API was called.",
            "- No DB file was mutated.",
            "",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def write_report(username: str, mode: str, tweets: list[dict[str, Any]]) -> str:
    villain_tweets = [tweet for tweet in tweets if tweet.get("villain_related")]
    analyzed = villain_tweets or tweets
    status, reason = analysis_state(mode, tweets, villain_tweets)
    if status == "FAILED":
        write_failure_report(status, reason, [f"- fetched_tweets: `{len(tweets)}`"])
        return status
    top = sorted(analyzed, key=sort_key, reverse=True)[:10]
    mature = [tweet for tweet in analyzed if (tweet.get("age_hours") or 0) >= 24]
    low = sorted(mature or analyzed, key=sort_key)[:10]
    patterns = summarize_patterns(analyzed)
    category_rows = category_summary(analyzed)
    media = media_summary(analyzed)
    time_rows = time_summary(analyzed)
    impressions_available = any(isinstance(tweet.get("impressions"), int) for tweet in analyzed)

    lines = [
        "# Villain X Current Analysis",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        f"- status: `{status}`",
        "- mode: `DRY_RUN_ONLY`",
        "- read_only: `true`",
        f"- reason: `{reason}`",
        "- account: `@raindog_kitetu`",
        f"- fetched_tweets: `{len(tweets)}`",
        f"- villain_related_analyzed: `{len(villain_tweets)}`",
        f"- metrics_mode: `{mode}`",
        f"- impressions_available: `{str(impressions_available).lower()}`",
        "- live posting: `NOT_EXECUTED`",
        "- X_API_WRITE: `NOT_USED`",
        "- X API write: `NOT_USED`",
        "- upload_media: `NOT_EXECUTED`",
        "- create_tweet: `NOT_EXECUTED`",
        "- credentials_displayed: `false`",
        "",
    ]
    if not impressions_available:
        lines.extend(
            [
                "> Note: X API did not return impression_count in this run. Rankings below use public engagement proxy until manual/X analytics impressions are entered.",
                "",
            ]
        )

    lines.extend(["## 1. 高インプレ投稿TOP10", ""])
    for index, tweet in enumerate(top, 1):
        lines.extend(
            [
                f"{index}. [{tweet.get('id')}]({tweet_url(username, tweet)}) - `{metric_label(tweet)}` / likes=`{tweet.get('likes')}` / reposts=`{tweet.get('reposts')}` / replies=`{tweet.get('replies')}` / bookmarks=`{tweet.get('bookmarks')}` / profile_clicks=`{tweet.get('profile_clicks')}` / `{maturity_label(tweet)}` / image_type=`{tweet.get('image_type')}` / media_count=`{tweet.get('media_count')}` / time=`{tweet.get('time_window')}`",
                f"   - first_line: `{tweet.get('first_line')}`",
            ]
        )

    lines.extend(["", "## 2. 低インプレ投稿TOP10", ""])
    for index, tweet in enumerate(low, 1):
        lines.extend(
            [
                f"{index}. [{tweet.get('id')}]({tweet_url(username, tweet)}) - `{metric_label(tweet)}` / likes=`{tweet.get('likes')}` / reposts=`{tweet.get('reposts')}` / replies=`{tweet.get('replies')}` / bookmarks=`{tweet.get('bookmarks')}` / profile_clicks=`{tweet.get('profile_clicks')}` / `{maturity_label(tweet)}` / image_type=`{tweet.get('image_type')}` / media_count=`{tweet.get('media_count')}` / time=`{tweet.get('time_window')}`",
                f"   - first_line: `{tweet.get('first_line')}`",
            ]
        )

    lines.extend(
        [
            "",
            "## 3. 共通特徴",
            "",
            f"- strong_image_types: `{dict(patterns['top_images'])}`",
            f"- weak_image_types: `{dict(patterns['low_images'])}`",
            f"- strong_time_windows: `{dict(patterns['top_times'])}`",
            "",
            "## 4. カテゴリ比較",
            "",
            "| category | count | avg impressions | max impressions | top first line |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in category_rows:
        lines.append(
            f"| `{row.get('category')}` | {row.get('count')} | {row.get('average_impressions')} | {row.get('max_impressions')} | `{row.get('top_first_line')}` |"
        )
    lines.extend(
        [
            "",
            "## 5. 画像あり/なし",
            "",
        ]
    )
    for label, values in media.items():
        lines.append(
            f"- {label}: count=`{values.get('count')}` / avg_impressions=`{values.get('average_impressions')}` / max_impressions=`{values.get('max_impressions')}`"
        )

    lines.extend(["", "## 6. 強い1行目パターン", ""])
    for line in patterns["top_first_lines"]:
        lines.append(f"- `{line}`")

    lines.extend(["", "## 7. 強い時間帯", ""])
    for window, count in patterns["top_times"].most_common():
        lines.append(f"- `{window}`: {count}")

    lines.extend(["", "## 8. 時間帯比較", ""])
    lines.extend(["| window | count | avg impressions | max impressions | top first line |", "| --- | ---: | ---: | ---: | --- |"])
    for row in time_rows:
        lines.append(
            f"| `{row.get('window')}` | {row.get('count')} | {row.get('average_impressions')} | {row.get('max_impressions')} | `{row.get('top_first_line')}` |"
        )

    lines.extend(["", "## 9. 弱い投稿パターン", ""])
    for line in patterns["weak_first_lines"]:
        lines.append(f"- `{line}`")
    lines.extend(
        [
            "",
            "## 10. データ生成結論",
            "",
        ]
    )
    lines.extend(conclusion_lines(category_rows, media, time_rows))
    lines.extend(
        [
            "",
            "## RealityGuard",
            "",
            "- GET-only read analysis.",
            "- No post was created.",
            "- No media was uploaded.",
            "- No write API was called.",
            "- No DB file was mutated.",
            "",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return status


def main() -> None:
    env = parse_env(ENV_PATH)
    missing = [key for key in REQUIRED_KEYS if not env.get(key)]
    if missing:
        write_failure_report("FAILED", "required environment variable missing")
        print("analysis failed; required env missing")
        return
    ok, user_id, username_or_reason = profile(env)
    if not ok:
        write_failure_report("FAILED", username_or_reason)
        print("analysis failed; profile lookup failed")
        return
    mode, tweets, raw = fetch_recent_tweets(env, user_id)
    enriched = enrich(tweets, raw)
    status = write_report(username_or_reason or "raindog_kitetu", mode, enriched)
    print(f"status={status}")
    print(f"fetched_tweets={len(tweets)}")
    print(f"metrics_mode={mode}")
    print("dry_run_only=true")
    print("live_posting=NOT_EXECUTED")
    print("x_api_write=NOT_USED")
    print("upload_media=NOT_EXECUTED")
    print("create_tweet=NOT_EXECUTED")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
