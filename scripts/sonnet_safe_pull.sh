#!/bin/bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

FILES=(
  data/sonnet_discovery_subject_watch.json
  data/sonnet_receipt_live_watch_state.json
)

TMP="$(mktemp -d /tmp/sonnet-safe-pull.XXXXXX)"
cleanup(){ rm -rf "$TMP"; }
trap cleanup EXIT

PRESERVED=()
for f in "${FILES[@]}"; do
  if [ -f "$f" ]; then
    mkdir -p "$TMP/$(dirname "$f")"
    cp "$f" "$TMP/$f"
    PRESERVED+=("$f")
  fi
done

for f in "${PRESERVED[@]}"; do
  if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    git restore --staged --worktree -- "$f"
  fi
done

git pull --ff-only

for f in "${PRESERVED[@]}"; do
  mkdir -p "$(dirname "$f")"
  cp "$TMP/$f" "$f"
done

echo 'SAFE_PULL_OK=1'
printf 'PRESERVED=%s\n' "${PRESERVED[*]:-none}"
