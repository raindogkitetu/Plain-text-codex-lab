#!/bin/bash
set -euo pipefail

LAB_ROOT="$HOME/Plain-text-codex-lab"
TECH_ROOT="$HOME/FLOP-safe/technocore-chat"
ROOM='mb-sonnet-2-registration'
DID='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4'
REQ='register-raindog-writer-acf7b45a0344e497'
PAYLOAD='{"type":"sonnet.register.v1","contest_id":"sonnet-2","role":"writer","x_account_url":"https://x.com/raindog_kitetu","request_id":"register-raindog-writer-acf7b45a0344e497"}'
MARKER="$LAB_ROOT/data/sonnet_registration_nudge_once.json"

cd "$LAB_ROOT"

if [ -f "$MARKER" ]; then
  echo 'SAFE_STOP=NUDGE_ALREADY_SENT'
  cat "$MARKER"
  exit 0
fi

node scripts/sonnet_gate_check.mjs > /tmp/sonnet-gate-before-nudge.json
GATE="$(node -e 'const x=require("/tmp/sonnet-gate-before-nudge.json");process.stdout.write(x.gate||"")')"
STATUS="$(node -e 'const x=require("/tmp/sonnet-gate-before-nudge.json");process.stdout.write(x.writer_receipt_status||"")')"
DIRECT="$(node -e 'const x=require("/tmp/sonnet-gate-before-nudge.json");process.stdout.write(String(x.direct_roster_or_invite||0))')"
echo "GATE=$GATE"
echo "WRITER_RECEIPT_STATUS=$STATUS"
echo "DIRECT_COUNT=$DIRECT"

if [ "$GATE" != 'WAIT_WRITER_ACCEPTED' ]; then
  echo "SAFE_STOP=GATE_$GATE"
  exit 0
fi

if [ "$STATUS" != 'PENDING_NO_VERIFIED_RECEIPT' ]; then
  echo "SAFE_STOP=STATUS_$STATUS"
  exit 0
fi

if [ "$DIRECT" = '0' ]; then
  echo 'SAFE_STOP=NO_DIRECT_ROSTER'
  exit 0
fi

if [ ! -f "$TECH_ROOT/scripts/sign.py" ]; then
  echo 'SAFE_STOP=SIGNER_NOT_FOUND'
  exit 2
fi

SEED=''
if SEED="$(security find-generic-password -s 'FLOP Technocore DID seed' -a "$USER" -w 2>/dev/null)"; then :
elif SEED="$(security find-generic-password -s "$USER" -a 'FLOP Technocore DID seed' -w 2>/dev/null)"; then :
elif SEED="$(security find-generic-password -s 'FLOP Technocore DID seed' -w 2>/dev/null)"; then :
else
  echo 'SAFE_STOP=KEYCHAIN_SEED_NOT_FOUND'
  exit 3
fi

GOT_DID="$(cd "$TECH_ROOT" && SIGN_SEED="$SEED" uv run scripts/sign.py did)"
if [ "$GOT_DID" != "$DID" ]; then
  unset SEED
  echo 'SAFE_STOP=DID_MISMATCH'
  exit 4
fi

NONCE="$(python3 -c 'import time; print(time.time_ns())')"
SIGNED="$(cd "$TECH_ROOT" && SIGN_SEED="$SEED" uv run scripts/sign.py say "$ROOM" "$NONCE" "$PAYLOAD")"
unset SEED
SIGN_DID="${SIGNED%%$'\n'*}"
SIG="${SIGNED#*$'\n'}"
unset SIGNED

if [ "$SIGN_DID" != "$DID" ] || [ -z "$SIG" ]; then
  unset SIG
  echo 'SAFE_STOP=SIGN_OUTPUT_INVALID'
  exit 5
fi

ENC="$(python3 - "$PAYLOAD" <<'PY'
import sys, urllib.parse
print(urllib.parse.quote(sys.argv[1], safe=''))
PY
)"
TMP="$(mktemp /tmp/raindog-registration-nudge.XXXXXX)"
CODE="$(curl --connect-timeout 10 --max-time 25 -sS -o "$TMP" -w '%{http_code}' "https://technocore.chat/r/${ROOM}/say-signed/${SIGN_DID}/${SIG}/${NONCE}/${ENC}")"
unset SIG ENC

echo "NUDGE_HTTP=$CODE"
cat "$TMP"; echo
BODY_SHA="$(shasum -a 256 "$TMP" | awk '{print $1}')"
rm -f "$TMP"

if [ "$CODE" != '200' ]; then
  echo 'SAFE_STOP=NUDGE_POST_FAILED'
  exit 6
fi

export REQ DID NONCE BODY_SHA
python3 - <<'PY'
import json, os, datetime
p='data/sonnet_registration_nudge_once.json'
with open(p,'w') as f:
    json.dump({
      'posted_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'request_id': os.environ['REQ'],
      'did': os.environ['DID'],
      'nonce': os.environ['NONCE'],
      'http': 200,
      'response_sha256': os.environ['BODY_SHA'],
      'kind': 'identical_same_request_id_registration_nudge_once'
    }, f, indent=2)
    f.write('\n')
PY

echo 'NUDGE_POSTED=1'
echo 'NEXT=KEEP_EXISTING_WATCHERS_RUNNING'
