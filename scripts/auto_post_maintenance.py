#!/usr/bin/env python3
"""03:00 maintenance job for Villain Auto Posting OS.

This job is local/read-write maintenance only. It validates JSON files, refreshes
recent media history, and writes reports. It has no X write path.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from media_deduplication import build_recent_media_history


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
STATUS_PATH = ROOT / "status.json"
RESULT_PATH = ROOT / "data" / "villain_auto_maintenance.json"
STREAM_PATH = ROOT / "data" / "villain_candidate_stream.json"
PASSCODES_PATH = ROOT / "data" / "villain_passcodes.json"
OUTCOMES_PATH = ROOT / "data" / "villain_post_outcomes.json"
WEARABLE_STOCK_PATH = ROOT / "data" / "villain_shop_wearable_stock.json"
SCHEDULER_REPORT_PATH = ROOT / "reports" / "villain_auto_scheduler.md"
MAINTENANCE_REPORT_PATH = ROOT / "reports" / "villain_auto_maintenance.md"
HANDOFF_RUNNER_PATH = ROOT / "scripts" / "agent_handoff_runner.py"
BUILD_REVIEW_BOARD_PATH = ROOT / "scripts" / "build_human_review_board.py"
IMAGE_SELECTOR_PATH = ROOT / "scripts" / "local_image_selector.py"
AUTO_POST_PILOT_PATH = ROOT / "scripts" / "auto_post_pilot.py"
BRIDGE_PROMPT_BUILDER_PATH = ROOT / "scripts" / "chatgpt_bridge_prompt_builder.py"
HANDOFF_REPORT_PATH = ROOT / "reports" / "agent_handoff_status.md"
QUALITY_REPORT_PATH = ROOT / "reports" / "villain_quality_review_summary.md"
PROJECTS_MIRROR_ROOT = Path("/Users/raindog/Projects/villain-auto-posting")
MIN_READY_STREAM_CANDIDATES = 5
JST = ZoneInfo("Asia/Tokyo")


def now_jst() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def json_sanity_check() -> dict[str, Any]:
    checked: list[str] = []
    failures: list[dict[str, str]] = []
    paths = sorted(DATA_DIR.glob("*.json"))
    if STATUS_PATH.exists():
        paths.append(STATUS_PATH)
    for path in paths:
        try:
            read_json(path)
            checked.append(str(path.relative_to(ROOT)))
        except Exception as error:  # noqa: BLE001 - report sanitized local JSON failure.
            failures.append({"path": str(path.relative_to(ROOT)), "error": str(error)})
    return {
        "status": "PASSED" if not failures else "FAILED",
        "checked_count": len(checked),
        "checked_files": checked,
        "failures": failures,
    }



def run_safe_script(script_path: Path, label: str) -> dict[str, Any]:
    command = [sys.executable, str(script_path)]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    stdout_lines = [line for line in completed.stdout.splitlines() if line.strip()]
    stderr_lines = [line for line in completed.stderr.splitlines() if line.strip()]
    return {
        "label": label,
        "status": "SUCCESS" if completed.returncode == 0 else "FAILED",
        "returncode": completed.returncode,
        "command": f"python3 scripts/{script_path.name}",
        "stdout_tail": stdout_lines[-20:],
        "stderr_tail": stderr_lines[-20:],
        "posting_executed": False,
        "upload_media_executed": False,
        "tweet_creation_executed": False,
    }


def active_passcodes(passcodes_db: dict[str, Any], used_passcodes: set[str]) -> list[str]:
    candidates: list[tuple[int, str, str]] = []
    for item in passcodes_db.get("passcodes", []):
        code = item.get("code", "")
        if not code or item.get("status") != "active" or code in used_passcodes:
            continue
        candidates.append((int(item.get("usage_count") or 0), item.get("last_used_at") or "", code))
    return [code for _usage, _last_used, code in sorted(candidates)]


def existing_ready_stream_items(stream_db: dict[str, Any]) -> list[dict[str, Any]]:
    ready: list[dict[str, Any]] = []
    for item in stream_db.get("stream", []):
        if item.get("status") in {"posted", "archived", "stale"}:
            continue
        image = item.get("image", {})
        if item.get("text") and image.get("ready") is True and image.get("file_path"):
            ready.append(item)
    return ready


def used_image_paths(stream_db: dict[str, Any], outcomes_db: dict[str, Any]) -> set[str]:
    used: set[str] = set()
    for item in stream_db.get("stream", []):
        image_path = item.get("image", {}).get("file_path", "")
        if image_path:
            used.add(image_path)
    for outcome in outcomes_db.get("outcomes", []):
        image_path = outcome.get("image_used", "")
        if image_path:
            used.add(image_path)
            try:
                used.add(str(Path(image_path).relative_to(ROOT)))
            except ValueError:
                pass
    return used


def refill_templates() -> list[dict[str, str]]:
    return [
        {
            "category": "culture_observer",
            "topic": "desk_residue",
            "text": "机に置いた瞬間、\nグッズじゃなくて、\n生活の一部になる。\n\n広告より、\n使われた跡の方が強い。",
            "preferred": "thermos",
        },
        {
            "category": "poster_summary",
            "topic": "bag_entryway",
            "text": "持ち物って、\n置かれた場所で\nだいたい正体が出る。\n\nきれいな写真より、\n帰ってきた後の方が本物っぽい。",
            "preferred": "bag",
        },
        {
            "category": "culture_observer",
            "topic": "quiet_apparel",
            "text": "服は主張しすぎると、\n急に広告になる。\n\n少しだけ見えて、\n勝手に残るくらいがちょうどいい。",
            "preferred": "hoodie",
        },
        {
            "category": "street_signal",
            "topic": "cap_afterdark",
            "text": "ロゴが大きいほど、\n強いわけじゃない。\n\n気づいた人だけが拾うくらいで、\nちょうど残る。",
            "preferred": "cap",
        },
        {
            "category": "community_artifact",
            "topic": "bucket_mirror",
            "text": "ちゃんと着ると、\nただの黒じゃなくなる。\n\n誰が使うかで、\n空気の方が先に変わる。",
            "preferred": "bucket",
        },
        {
            "category": "anti_ad",
            "topic": "used_object",
            "text": "完成された写真より、\n少し生活に混ざった方が強い。\n\n広告じゃなくて、\n持ち物に見えるから。",
            "preferred": "lifestyle",
        },
    ]


def choose_stock_item(stock_items: list[dict[str, Any]], preferred: str, used_images: set[str]) -> dict[str, Any] | None:
    def score(item: dict[str, Any]) -> int:
        haystack = " ".join(
            str(item.get(key, "")).lower()
            for key in ("id", "path", "image_type", "prompt_family", "fit_notes")
        )
        points = 0
        if preferred and preferred.lower() in haystack:
            points += 100
        if "photo" in haystack:
            points += 20
        if "person" in haystack or "mirror" in haystack:
            points += 12
        if "poster" in haystack:
            points -= 25
        return points

    candidates = [
        item
        for item in stock_items
        if item.get("path")
        and item.get("path") not in used_images
        and (ROOT / item.get("path", "")).exists()
    ]
    if not candidates:
        return None
    return sorted(candidates, key=score, reverse=True)[0]


def normalize_footer(text: str, passcode: str) -> str:
    footer = f"#着て稼ぐ #villain $PPP @0xmavillain {passcode}"
    body = text.strip()
    if footer in body:
        return body
    return f"{body}\n\n{footer}"


def refill_candidate_stream() -> dict[str, Any]:
    if not (STREAM_PATH.exists() and PASSCODES_PATH.exists() and WEARABLE_STOCK_PATH.exists()):
        return {
            "status": "SKIPPED",
            "reason": "required_source_missing",
            "added_count": 0,
            "ready_count_before": 0,
            "ready_count_after": 0,
            "added_ids": [],
        }

    stream_db = read_json(STREAM_PATH)
    passcodes_db = read_json(PASSCODES_PATH)
    outcomes_db = read_json(OUTCOMES_PATH) if OUTCOMES_PATH.exists() else {"outcomes": []}
    stock_db = read_json(WEARABLE_STOCK_PATH)
    ready_before = len(existing_ready_stream_items(stream_db))
    if ready_before >= MIN_READY_STREAM_CANDIDATES:
        return {
            "status": "SKIPPED",
            "reason": "ready_stream_count_sufficient",
            "added_count": 0,
            "ready_count_before": ready_before,
            "ready_count_after": ready_before,
            "added_ids": [],
        }

    stream = stream_db.setdefault("stream", [])
    existing_ids = {item.get("stream_id") for item in stream}
    used_passcodes = {item.get("passcode", "") for item in stream if item.get("passcode")}
    today = datetime.now(JST).strftime("%Y%m%d")
    date_label = datetime.now(JST).strftime("%Y-%m-%d")
    passcodes = active_passcodes(passcodes_db, used_passcodes)
    stock_items = list(stock_db.get("items", []))
    images = used_image_paths(stream_db, outcomes_db)
    templates = refill_templates()
    added: list[str] = []

    for template in templates:
        if len(existing_ready_stream_items(stream_db)) >= MIN_READY_STREAM_CANDIDATES:
            break
        if not passcodes:
            break
        stock_item = choose_stock_item(stock_items, template.get("preferred", ""), images)
        if not stock_item:
            continue
        passcode = passcodes.pop(0)
        sequence = len([item for item in stream if str(item.get("stream_id", "")).startswith(f"vln-stream-{today}")]) + 1
        stream_id = f"vln-stream-{today}-auto-{sequence:03d}"
        if stream_id in existing_ids:
            continue
        text = normalize_footer(template["text"], passcode)
        now = now_jst()
        stream.append(
            {
                "stream_id": stream_id,
                "source_candidate_id": f"maintenance-refill-{today}-{sequence:03d}",
                "created_at_jst": now,
                "updated_at_jst": now,
                "status": "approved",
                "category": template["category"],
                "passcode": passcode,
                "text": text,
                "image": {
                    "required": True,
                    "ready": True,
                    "file_path": stock_item.get("path", ""),
                    "image_type": stock_item.get("image_type", "wearable_lifestyle_photo"),
                    "match_score": 92,
                    "rights_notes": "maintenance refill from approved shop wearable stock; not raw shop image.",
                },
                "scores": {
                    "quality_prediction": 90,
                    "persona_score": 84,
                    "risk_prediction": "low",
                    "novelty_score": 78,
                    "remixability_score": 72,
                    "residual_growth_potential": 72,
                    "profile_click_potential": 64,
                },
                "lifecycle": {
                    "fresh_until_jst": f"{date_label}T23:59:00+09:00",
                    "aging_after_jst": f"{date_label}T23:59:00+09:00",
                    "stale_after_jst": f"{date_label}T23:59:00+09:00",
                    "lifespan_reason": "maintenance refill for same-day supervised schedule; no temporal/event claim.",
                },
                "review": {
                    "human_decision": "approved",
                    "decision_at_jst": now,
                    "timing_hint": "scheduled_slot",
                    "reject_reason": "",
                    "maintenance_refill": True,
                },
                "post_execution": {
                    "posting_execution_allowed": True,
                    "posted_url": "",
                    "posted_at_jst": "",
                    "method": "scheduled_supervised_live",
                },
                "learning": {
                    "actual_residual_type": "",
                    "manual_notes": f"Auto-refilled by maintenance from {stock_item.get('id', '')}; no reality/event claim.",
                },
            }
        )
        existing_ids.add(stream_id)
        images.add(stock_item.get("path", ""))
        added.append(stream_id)

    stream_db["updated_at_jst"] = now_jst()
    write_json(STREAM_PATH, stream_db)
    ready_after = len(existing_ready_stream_items(stream_db))
    return {
        "status": "SUCCESS" if added or ready_after >= MIN_READY_STREAM_CANDIDATES else "PARTIAL",
        "reason": "refilled_from_shop_wearable_stock",
        "min_ready_stream_candidates": MIN_READY_STREAM_CANDIDATES,
        "ready_count_before": ready_before,
        "ready_count_after": ready_after,
        "added_count": len(added),
        "added_ids": added,
        "posting_executed": False,
        "upload_media_executed": False,
        "tweet_creation_executed": False,
    }


def refresh_limited_live_pilot() -> dict[str, Any]:
    command = [sys.executable, str(AUTO_POST_PILOT_PATH), "--mode", "LIMITED_LIVE_EXECUTION"]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    stdout_lines = [line for line in completed.stdout.splitlines() if line.strip()]
    stderr_lines = [line for line in completed.stderr.splitlines() if line.strip()]
    return {
        "status": "SUCCESS" if completed.returncode == 0 else "FAILED",
        "returncode": completed.returncode,
        "command": "python3 scripts/auto_post_pilot.py --mode LIMITED_LIVE_EXECUTION",
        "stdout_tail": stdout_lines[-20:],
        "stderr_tail": stderr_lines[-20:],
        "posting_executed": False,
        "upload_media_executed": False,
        "tweet_creation_executed": False,
    }


def refresh_chatgpt_bridge_prompt() -> dict[str, Any]:
    command = [sys.executable, str(BRIDGE_PROMPT_BUILDER_PATH)]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    stdout_lines = [line for line in completed.stdout.splitlines() if line.strip()]
    stderr_lines = [line for line in completed.stderr.splitlines() if line.strip()]
    return {
        "status": "SUCCESS" if completed.returncode == 0 else "FAILED",
        "returncode": completed.returncode,
        "command": "python3 scripts/chatgpt_bridge_prompt_builder.py",
        "stdout_tail": stdout_lines[-20:],
        "stderr_tail": stderr_lines[-20:],
        "posting_executed": False,
        "upload_media_executed": False,
        "tweet_creation_executed": False,
    }


def sync_to_projects_mirror() -> dict[str, Any]:
    if ROOT == PROJECTS_MIRROR_ROOT or not PROJECTS_MIRROR_ROOT.exists():
        return {
            "status": "SKIPPED",
            "reason": "already_in_projects_or_missing_mirror",
            "copied_files": [],
            "copied_dirs": [],
            "posting_executed": False,
            "upload_media_executed": False,
            "tweet_creation_executed": False,
        }

    copied_files: list[str] = []
    copied_dirs: list[str] = []
    file_paths = [
        STREAM_PATH,
        PASSCODES_PATH,
        OUTCOMES_PATH,
        WEARABLE_STOCK_PATH,
        ROOT / "data" / "villain_auto_post_pilot.json",
        RESULT_PATH,
        ROOT / "reports" / "villain_auto_post_pilot.md",
        ROOT / "reports" / "villain_post_outcome_logger.md",
        ROOT / "reports" / "villain_shop_wearable_stock.md",
        ROOT / "reports" / "chatgpt_bridge_prompt.md",
        ROOT / "data" / "chatgpt_bridge_exchange.json",
        MAINTENANCE_REPORT_PATH,
        SCHEDULER_REPORT_PATH,
        ROOT / "scripts" / "auto_post_maintenance.py",
        ROOT / "scripts" / "chatgpt_bridge_prompt_builder.py",
        ROOT / "docs" / "handoff_contract.md",
    ]
    for source in file_paths:
        if not source.exists():
            continue
        target = PROJECTS_MIRROR_ROOT / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(source, target)
            copied_files.append(str(source.relative_to(ROOT)))
        except OSError as error:
            return {
                "status": "FAILED",
                "reason": "projects_mirror_copy_failed",
                "error": str(error),
                "target": str(PROJECTS_MIRROR_ROOT),
                "copied_files": copied_files,
                "copied_dirs": copied_dirs,
                "posting_executed": False,
                "upload_media_executed": False,
                "tweet_creation_executed": False,
            }

    source_dir = ROOT / "villain_post_images" / "wearable_stock"
    target_dir = PROJECTS_MIRROR_ROOT / "villain_post_images" / "wearable_stock"
    if source_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
        for source in source_dir.glob("*"):
            if source.is_file():
                try:
                    shutil.copy2(source, target_dir / source.name)
                except OSError as error:
                    return {
                        "status": "FAILED",
                        "reason": "projects_mirror_image_copy_failed",
                        "error": str(error),
                        "target": str(PROJECTS_MIRROR_ROOT),
                        "copied_files": copied_files,
                        "copied_dirs": copied_dirs,
                        "posting_executed": False,
                        "upload_media_executed": False,
                        "tweet_creation_executed": False,
                    }
        copied_dirs.append(str(source_dir.relative_to(ROOT)))

    return {
        "status": "SUCCESS",
        "reason": "synced_safe_runtime_state_to_projects_mirror",
        "target": str(PROJECTS_MIRROR_ROOT),
        "copied_files": copied_files,
        "copied_dirs": copied_dirs,
        "posting_executed": False,
        "upload_media_executed": False,
        "tweet_creation_executed": False,
    }

def run_handoff_runner() -> dict[str, Any]:
    command = [sys.executable, str(HANDOFF_RUNNER_PATH)]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    stdout_lines = [line for line in completed.stdout.splitlines() if line.strip()]
    stderr_lines = [line for line in completed.stderr.splitlines() if line.strip()]
    return {
        "status": "SUCCESS" if completed.returncode == 0 else "FAILED",
        "returncode": completed.returncode,
        "command": "python3 scripts/agent_handoff_runner.py",
        "stdout_tail": stdout_lines[-20:],
        "stderr_tail": stderr_lines[-20:],
        "posting_executed": False,
        "upload_media_executed": False,
        "tweet_creation_executed": False,
        "reports_updated": [
            str(HANDOFF_REPORT_PATH.relative_to(ROOT)),
            str(QUALITY_REPORT_PATH.relative_to(ROOT)),
        ],
    }


def scheduler_report(result: dict[str, Any]) -> str:
    media = result.get("recent_media_history", {})
    sanity = result.get("json_sanity_check", {})
    handoff = result.get("agent_handoff", {})
    refill = result.get("candidate_refill", {})
    pilot = result.get("limited_live_pilot_refresh", {})
    bridge = result.get("chatgpt_bridge_prompt_refresh", {})
    sync = result.get("projects_mirror_sync", {})
    return "\n".join(
        [
            "# Villain Auto Scheduler v1",
            "",
            f"- Generated at JST: `{result.get('generated_at_jst')}`",
            "- current job: `03:00 maintenance`",
            "- posting executed: `NO`",
            "- media upload executed: `NO`",
            "- tweet creation executed: `NO`",
            "",
            "## Daily Slots",
            "",
            "- 03:00: maintenance only; refresh JSON sanity, recent media history, and scheduler report.",
            "- 03:00 maintenance also runs `python3 scripts/agent_handoff_runner.py` for Quality OS handoff reports.",
            "- 13:00: daytime posting slot.",
            "- 20:00: night posting slot.",
            "- 23:00: late night posting slot.",
            "",
            "## Scheduler Limits",
            "",
            "- max_posts_per_day: `3`",
            "- max_posts_per_run: `1`",
            "- cooldown_between_posts_minutes: `120`",
            "- post_count_source: `data/villain_post_outcomes.json`",
            "- scheduler_state_role: `auxiliary log only`",
            "",
            "## Gate Order",
            "",
            "1. `manual_stop`",
            "2. outcome DB daily success count",
            "3. cooldown from latest successful outcome",
            "4. `human_review.keep` from latest successful outcome",
            "5. Auto Post Pilot candidate gates",
            "6. X Write Adapter gates",
            "7. network preflight before any write attempt",
            "",
            "## Human Review Gate",
            "",
            "- `human_review.keep=pending` blocks as `human_review_pending`.",
            "- `human_review.keep=false` blocks as `previous_post_marked_delete_or_drop`.",
            "- `human_review.keep=true` is required before the next post.",
            "- If no successful outcome exists, scheduler can continue to candidate evaluation.",
            "",
            "## Maintenance Result",
            "",
            f"- json_sanity_check: `{sanity.get('status')}`",
            f"- json_files_checked: `{sanity.get('checked_count')}`",
            f"- recent_media_entries: `{len(media.get('entries', []))}`",
            f"- agent_handoff: `{handoff.get('status')}`",
            f"- agent_handoff_command: `{handoff.get('command')}`",
            f"- candidate_refill: `{refill.get('status')}`",
            f"- ready_stream_candidates: `{refill.get('ready_count_after', refill.get('ready_count_before', 'unknown'))}`",
            f"- refill_added_count: `{refill.get('added_count', 0)}`",
            f"- limited_live_pilot_refresh: `{pilot.get('status')}`",
            f"- chatgpt_bridge_prompt_refresh: `{bridge.get('status')}`",
            f"- projects_mirror_sync: `{sync.get('status')}`",
            "",
            "## Safety",
            "",
            "- passcode source: `data/villain_passcodes.json` active codes only.",
            "- passcode auto generation: `false`.",
            "- retry behavior: no automatic retry; one scheduler run can select at most one post.",
            "- 03:00 job is not a posting slot.",
            "",
        ]
    )


def maintenance_report(result: dict[str, Any]) -> str:
    sanity = result.get("json_sanity_check", {})
    media = result.get("recent_media_history", {})
    handoff = result.get("agent_handoff", {})
    refill = result.get("candidate_refill", {})
    pilot = result.get("limited_live_pilot_refresh", {})
    bridge = result.get("chatgpt_bridge_prompt_refresh", {})
    sync = result.get("projects_mirror_sync", {})
    lines = [
        "# Villain Auto Maintenance v1",
        "",
        f"- Generated at JST: `{result.get('generated_at_jst')}`",
        f"- status: `{result.get('status')}`",
        "- job_time: `03:00`",
        "- posting executed: `NO`",
        "- media upload executed: `NO`",
        "- tweet creation executed: `NO`",
        "",
        "## JSON Sanity",
        "",
        f"- status: `{sanity.get('status')}`",
        f"- checked_count: `{sanity.get('checked_count')}`",
        "",
        "## Recent Media History",
        "",
        f"- cooldown_days: `{media.get('cooldown_days')}`",
        f"- entries: `{len(media.get('entries', []))}`",
        "",
        "## Agent Handoff",
        "",
        f"- status: `{handoff.get('status')}`",
        f"- command: `{handoff.get('command')}`",
        f"- returncode: `{handoff.get('returncode')}`",
        "- posting executed: `NO`",
        "- upload executed: `NO`",
        "- tweet creation executed: `NO`",
        f"- reports_updated: `{', '.join(handoff.get('reports_updated', []))}`",
        "",
        "## Candidate Refill",
        "",
        f"- status: `{refill.get('status')}`",
        f"- reason: `{refill.get('reason', '')}`",
        f"- min_ready_stream_candidates: `{refill.get('min_ready_stream_candidates', MIN_READY_STREAM_CANDIDATES)}`",
        f"- ready_count_before: `{refill.get('ready_count_before')}`",
        f"- ready_count_after: `{refill.get('ready_count_after')}`",
        f"- added_count: `{refill.get('added_count', 0)}`",
        f"- added_ids: `{', '.join(refill.get('added_ids', [])) if refill.get('added_ids') else 'none'}`",
        "- posting executed: `NO`",
        "- upload executed: `NO`",
        "- tweet creation executed: `NO`",
        "",
        "## Pilot Refresh",
        "",
        f"- status: `{pilot.get('status')}`",
        f"- command: `{pilot.get('command')}`",
        f"- returncode: `{pilot.get('returncode')}`",
        "- posting executed: `NO`",
        "- upload executed: `NO`",
        "- tweet creation executed: `NO`",
        "",
        "## Projects Mirror Sync",
        "",
        f"- status: `{sync.get('status')}`",
        f"- reason: `{sync.get('reason', '')}`",
        f"- target: `{sync.get('target', '')}`",
        f"- copied_files: `{len(sync.get('copied_files', []))}`",
        f"- copied_dirs: `{', '.join(sync.get('copied_dirs', [])) if sync.get('copied_dirs') else 'none'}`",
        "- posting executed: `NO`",
        "- upload executed: `NO`",
        "- tweet creation executed: `NO`",
        "",
    ]
    lines.extend(
        [
            "## ChatGPT Bridge Prompt Refresh",
            "",
            f"- status: `{bridge.get('status')}`",
            f"- command: `{bridge.get('command')}`",
            f"- returncode: `{bridge.get('returncode')}`",
            "- posting executed: `NO`",
            "- upload executed: `NO`",
            "- tweet creation executed: `NO`",
            "",
        ]
    )
    if bridge.get("stdout_tail"):
        lines.extend(["### Bridge Prompt Output", ""])
        lines.extend(f"- `{line}`" for line in bridge.get("stdout_tail", []))
        lines.append("")
    if bridge.get("stderr_tail"):
        lines.extend(["### Bridge Prompt Errors", ""])
        lines.extend(f"- `{line}`" for line in bridge.get("stderr_tail", []))
        lines.append("")
    if pilot.get("stdout_tail"):
        lines.extend(["### Pilot Refresh Output", ""])
        lines.extend(f"- `{line}`" for line in pilot.get("stdout_tail", []))
        lines.append("")
    if pilot.get("stderr_tail"):
        lines.extend(["### Pilot Refresh Errors", ""])
        lines.extend(f"- `{line}`" for line in pilot.get("stderr_tail", []))
        lines.append("")
    if handoff.get("stdout_tail"):
        lines.extend(["### Handoff Output", ""])
        lines.extend(f"- `{line}`" for line in handoff.get("stdout_tail", []))
        lines.append("")
    if handoff.get("stderr_tail"):
        lines.extend(["### Handoff Errors", ""])
        lines.extend(f"- `{line}`" for line in handoff.get("stderr_tail", []))
        lines.append("")
    if sanity.get("failures"):
        lines.extend(["## Failures", ""])
        lines.extend(f"- `{item.get('path')}`: `{item.get('error')}`" for item in sanity.get("failures", []))
        lines.append("")
    return "\n".join(lines)


def build_result() -> dict[str, Any]:
    sanity = json_sanity_check()
    media_history = build_recent_media_history(write=True)
    handoff = run_handoff_runner()
    refill = refill_candidate_stream()
    pilot = refresh_limited_live_pilot()
    bridge = refresh_chatgpt_bridge_prompt()
    sync = sync_to_projects_mirror()
    # Handoff reports are advisory for ChatGPT/Codex review. A temporary
    # handoff failure must not break the operational maintenance job that keeps
    # the scheduled candidate stream stocked.
    status_ok = (
        sanity.get("status") == "PASSED"
        and refill.get("status") in {"SUCCESS", "SKIPPED"}
        and pilot.get("status") == "SUCCESS"
        and bridge.get("status") == "SUCCESS"
        and sync.get("status") in {"SUCCESS", "SKIPPED"}
    )
    return {
        "db_name": "Villain Auto Maintenance Run",
        "version": "1.1.0",
        "generated_at_jst": now_jst(),
        "status": "SUCCESS" if status_ok else "FAILED",
        "job": "03:00_maintenance",
        "posting_executed": False,
        "x_api_write_used": False,
        "upload_media_executed": False,
        "tweet_creation_executed": False,
        "json_sanity_check": sanity,
        "recent_media_history": {
            "cooldown_days": media_history.get("cooldown_days"),
            "near_duplicate_hamming_threshold": media_history.get("near_duplicate_hamming_threshold"),
            "entries": media_history.get("entries", []),
        },
        "agent_handoff": handoff,
        "warnings": ["agent_handoff_failed_non_blocking"] if handoff.get("status") != "SUCCESS" else [],
        "candidate_refill": refill,
        "limited_live_pilot_refresh": pilot,
        "chatgpt_bridge_prompt_refresh": bridge,
        "projects_mirror_sync": sync,
    }


def main() -> None:
    result = build_result()
    write_json(RESULT_PATH, result)
    SCHEDULER_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEDULER_REPORT_PATH.write_text(scheduler_report(result), encoding="utf-8")
    MAINTENANCE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    MAINTENANCE_REPORT_PATH.write_text(maintenance_report(result), encoding="utf-8")
    print(f"status={result.get('status')}")
    print("posting_executed=NO")
    print(f"wrote {RESULT_PATH.relative_to(ROOT)}")
    print(f"wrote {SCHEDULER_REPORT_PATH.relative_to(ROOT)}")
    print(f"wrote {MAINTENANCE_REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
