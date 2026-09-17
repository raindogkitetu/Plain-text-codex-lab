#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

INTERVAL="${INTERVAL:-90}"
MAX_ROUNDS="${MAX_ROUNDS:-40}"

for ((i=1;i<=MAX_ROUNDS;i++)); do
  echo "WATCH_ROUND=$i"
  node scripts/sonnet_gate_check.mjs > data/sonnet_gate_check_live.json
  node - <<'NODE'
const fs=require('fs');
const x=JSON.parse(fs.readFileSync('data/sonnet_gate_check_live.json','utf8'));
console.log(JSON.stringify({
  checked_at:x.checked_at,
  gate:x.gate,
  writer_receipt_status:x.writer_receipt_status,
  writer_receipt:x.writer_receipt,
  registration_export_ok:x.registration_export_ok,
  registration_read_errors:x.registration_read_errors,
  rules_export_ok:x.rules_export_ok,
  rules_read_errors:x.rules_read_errors,
  direct_roster_or_invite:x.direct_roster_or_invite,
  latest_direct_roster_or_invite:x.latest_direct_roster_or_invite
},null,2));
NODE
  GATE="$(node -e 'const x=require("./data/sonnet_gate_check_live.json");process.stdout.write(x.gate||"")')"
  if [ "$GATE" != 'WAIT_WRITER_ACCEPTED' ]; then
    echo "WATCH_STOP_GATE=$GATE"
    exit 0
  fi
  if [ "$i" -lt "$MAX_ROUNDS" ]; then
    sleep "$INTERVAL"
  fi
done

echo 'WATCH_STOP_GATE=TIMEBOX_EXHAUSTED'
