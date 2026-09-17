#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

INTERVAL="${INTERVAL:-90}"
MAX_ROUNDS="${MAX_ROUNDS:-320}"
OUT='data/sonnet_overnight_watch_latest.json'
LOG='data/sonnet_overnight_watch.log'

: > "$LOG"

for ((i=1;i<=MAX_ROUNDS;i++)); do
  TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "[$TS] WATCH_ROUND=$i" | tee -a "$LOG"

  if node scripts/sonnet_gate_check.mjs > "$OUT.tmp" 2>>"$LOG"; then
    mv "$OUT.tmp" "$OUT"
  else
    rm -f "$OUT.tmp"
    echo "[$TS] GATE_CHECK_EXEC_ERROR=1" | tee -a "$LOG"
    if [ "$i" -lt "$MAX_ROUNDS" ]; then sleep "$INTERVAL"; fi
    continue
  fi

  node - <<'NODE' | tee -a "$LOG"
const fs=require('fs');
const x=JSON.parse(fs.readFileSync('data/sonnet_overnight_watch_latest.json','utf8'));
console.log(JSON.stringify({
  checked_at:x.checked_at,
  gate:x.gate,
  writer_receipt_status:x.writer_receipt_status,
  registration_export_ok:x.registration_export_ok,
  direct_roster_or_invite:x.direct_roster_or_invite,
  registration_read_errors:x.registration_read_errors,
  rules_read_errors:x.rules_read_errors
}));
NODE

  GATE="$(node -e 'const x=require("./data/sonnet_overnight_watch_latest.json");process.stdout.write(x.gate||"")')"

  case "$GATE" in
    READY_TO_VERIFY_ROSTER)
      echo "WATCH_STOP_GATE=READY_TO_VERIFY_ROSTER" | tee -a "$LOG"
      printf '\a\a\a'
      exit 0
      ;;
    REGISTRATION_REFUSED)
      echo "WATCH_STOP_GATE=REGISTRATION_REFUSED" | tee -a "$LOG"
      printf '\a\a\a'
      exit 0
      ;;
    WAIT_WRITER_ACCEPTED)
      ;;
    NETWORK_RECOVERY_NEEDED)
      echo "NETWORK_TRANSIENT=1; continuing watch" | tee -a "$LOG"
      ;;
    *)
      echo "NONTERMINAL_GATE=$GATE; continuing watch" | tee -a "$LOG"
      ;;
  esac

  if [ "$i" -lt "$MAX_ROUNDS" ]; then
    sleep "$INTERVAL"
  fi
done

echo 'WATCH_STOP_GATE=TIMEBOX_EXHAUSTED' | tee -a "$LOG"
