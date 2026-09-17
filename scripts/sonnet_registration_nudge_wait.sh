#!/bin/bash
set -euo pipefail

LAB_ROOT="$HOME/Plain-text-codex-lab"
INTERVAL="${INTERVAL:-30}"
MAX_ROUNDS="${MAX_ROUNDS:-120}"
NUDGE_SCRIPT="${NUDGE_SCRIPT:-/tmp/sonnet_registration_nudge_once.sh}"

cd "$LAB_ROOT"

if [ ! -f "$NUDGE_SCRIPT" ]; then
  echo "SAFE_STOP=NUDGE_SCRIPT_NOT_FOUND"
  exit 2
fi

for ((i=1;i<=MAX_ROUNDS;i++)); do
  echo "WAIT_ROUND=$i"
  if node scripts/sonnet_gate_check.mjs > /tmp/sonnet-gate-wait.json 2>/tmp/sonnet-gate-wait.err; then
    GATE="$(node -e 'const x=require("/tmp/sonnet-gate-wait.json");process.stdout.write(x.gate||"")')"
    STATUS="$(node -e 'const x=require("/tmp/sonnet-gate-wait.json");process.stdout.write(x.writer_receipt_status||"")')"
    DIRECT="$(node -e 'const x=require("/tmp/sonnet-gate-wait.json");process.stdout.write(String(x.direct_roster_or_invite||0))')"
    REG_OK="$(node -e 'const x=require("/tmp/sonnet-gate-wait.json");process.stdout.write(String(!!x.registration_export_ok))')"
    echo "GATE=$GATE"
    echo "WRITER_RECEIPT_STATUS=$STATUS"
    echo "REGISTRATION_EXPORT_OK=$REG_OK"
    echo "DIRECT_COUNT=$DIRECT"

    case "$GATE" in
      READY_TO_VERIFY_ROSTER)
        echo "SAFE_STOP=ALREADY_READY_TO_VERIFY_ROSTER"
        exit 0
        ;;
      REGISTRATION_REFUSED)
        echo "SAFE_STOP=REGISTRATION_REFUSED"
        exit 0
        ;;
      WAIT_WRITER_ACCEPTED)
        if [ "$REG_OK" = "true" ] && [ "$STATUS" = "PENDING_NO_VERIFIED_RECEIPT" ] && [ "$DIRECT" != "0" ]; then
          echo "HEALTHY_PENDING_CONFIRMED=1"
          bash "$NUDGE_SCRIPT"
          exit $?
        fi
        ;;
    esac
  else
    echo "GATE_CHECK_ERROR=$(tr '\n' ' ' < /tmp/sonnet-gate-wait.err | tail -c 500)"
  fi

  sleep "$INTERVAL"
done

echo "SAFE_STOP=HEALTHY_GATE_NOT_REACHED"
exit 0
