#!/bin/bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
INTERVAL="${INTERVAL:-180}"
DEADLINE_EPOCH="$(python3 - <<'PY'
import datetime
print(int(datetime.datetime(2026,9,18,12,0,0,tzinfo=datetime.timezone.utc).timestamp()))
PY
)"

while true; do
  now="$(date +%s)"
  if [ "$now" -ge "$DEADLINE_EPOCH" ]; then
    echo 'FINAL_GATE=DEADLINE_REACHED'
    break
  fi

  node scripts/sonnet_gate_check.mjs > /tmp/sonnet_gate_check.out 2>&1 || true
  cat /tmp/sonnet_gate_check.out

  if [ ! -f data/sonnet_gate_check.json ]; then
    echo 'GATE_WAIT=NO_STATE_FILE'
    sleep "$INTERVAL"
    continue
  fi

  GATE="$(node -e 'const x=require("./data/sonnet_gate_check.json");process.stdout.write(String(x.gate||"UNKNOWN"))')"
  STATUS="$(node -e 'const x=require("./data/sonnet_gate_check.json");process.stdout.write(String(x.writer_receipt_status||"UNKNOWN"))')"
  DIRECT="$(node -e 'const x=require("./data/sonnet_gate_check.json");process.stdout.write(String(x.direct_roster_or_invite||0))')"
  REGOK="$(node -e 'const x=require("./data/sonnet_gate_check.json");process.stdout.write(String(!!x.registration_export_ok))')"

  echo "GATE=$GATE"
  echo "WRITER_RECEIPT_STATUS=$STATUS"
  echo "DIRECT_ROSTER_COUNT=$DIRECT"
  echo "REGISTRATION_EXPORT_OK=$REGOK"

  case "$GATE" in
    READY_TO_VERIFY_ROSTER|REGISTRATION_REFUSED)
      printf '\a'
      echo "FINAL_GATE=$GATE"
      break
      ;;
    NETWORK_RECOVERY_NEEDED)
      echo "GATE_WAIT=NETWORK_RETRY_IN_${INTERVAL}s"
      ;;
    WAIT_WRITER_ACCEPTED|WAIT_DIRECT_ROSTER)
      echo "GATE_WAIT=RECHECK_IN_${INTERVAL}s"
      ;;
    *)
      echo "GATE_WAIT=UNKNOWN_STATE_RECHECK_IN_${INTERVAL}s"
      ;;
  esac

  sleep "$INTERVAL"
done
