#!/bin/bash
set -euo pipefail

LAB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$LAB_ROOT"

SUBJECT='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4'
ROOM='mb-sonnet-2-discovery'
REG_REQUEST='register-raindog-writer-acf7b45a0344e497'
MARKER='data/sonnet_direct_fallback_post.json'

if [ -f "$MARKER" ]; then
  echo 'SAFE_STOP=FALLBACK_ALREADY_POSTED'
  cat "$MARKER"
  exit 0
fi

node scripts/sonnet_candidate_live.mjs

TOP="$(node -e 'const fs=require("fs");const x=JSON.parse(fs.readFileSync("data/sonnet_candidate_live.json","utf8"));process.stdout.write(x.top3?.[0]?.game_id||"")')"
DIRECT="$(node -e 'const fs=require("fs");const x=JSON.parse(fs.readFileSync("data/sonnet_candidate_live.json","utf8"));process.stdout.write(String(!!x.top3?.[0]?.direct_to_subject))')"
SETUP="$(node -e 'const fs=require("fs");const x=JSON.parse(fs.readFileSync("data/sonnet_candidate_live.json","utf8"));process.stdout.write(String(!!x.candidates?.[0]?.setup_accepted))')"
READ_OK="$(node -e 'const fs=require("fs");const x=JSON.parse(fs.readFileSync("data/sonnet_candidate_live.json","utf8"));process.stdout.write(String(!!x.candidates?.[0]?.read_ok))')"
WORDS="$(node -e 'const fs=require("fs");const x=JSON.parse(fs.readFileSync("data/sonnet_candidate_live.json","utf8"));process.stdout.write(String(x.candidates?.[0]?.word_posts??-1))')"
TARGET="$(node -e 'const fs=require("fs");const x=JSON.parse(fs.readFileSync("data/sonnet_candidate_live.json","utf8"));process.stdout.write(x.candidates?.[0]?.latest_recruitment?.from||"")')"
CANDIDATE_ERRORS="$(node -e 'const fs=require("fs");const x=JSON.parse(fs.readFileSync("data/sonnet_candidate_live.json","utf8"));process.stdout.write(String((x.candidates?.[0]?.errors||[]).length))')"
GLOBAL_ERRORS="$(node -e 'const fs=require("fs");const x=JSON.parse(fs.readFileSync("data/sonnet_candidate_live.json","utf8"));process.stdout.write(String((x.errors||[]).length))')"
RECEIPT_STATUS="$(node -e 'const fs=require("fs");try{const x=JSON.parse(fs.readFileSync("data/sonnet_receipt_live_watch_state.json","utf8"));process.stdout.write(x.status||"UNKNOWN")}catch{process.stdout.write("UNKNOWN")}')"

printf 'TOP=%s\nDIRECT_TO_RAINDOG=%s\nSETUP_ACCEPTED=%s\nREAD_OK=%s\nWORD_POSTS=%s\nCANDIDATE_ERRORS=%s\nGLOBAL_ERRORS=%s\nRECEIPT_STATUS=%s\nTARGET=%s\n' "$TOP" "$DIRECT" "$SETUP" "$READ_OK" "$WORDS" "$CANDIDATE_ERRORS" "$GLOBAL_ERRORS" "$RECEIPT_STATUS" "$TARGET"

if [ "$DIRECT" = 'true' ]; then
  echo 'SAFE_STOP=DIRECT_PATH_ALREADY_EXISTS'
  exit 0
fi

if [ -z "$TOP" ] || [ "$SETUP" != 'true' ] || [ "$READ_OK" != 'true' ] || [ "$WORDS" != '0' ] || [ "$CANDIDATE_ERRORS" != '0' ] || [ "$GLOBAL_ERRORS" != '0' ] || [ -z "$TARGET" ]; then
  echo 'SAFE_STOP=NO_ACTIONABLE_VERIFIED_FALLBACK'
  exit 2
fi

TECH_ROOT="$HOME/FLOP-safe/technocore-chat"
if [ ! -f "$TECH_ROOT/scripts/sign.py" ]; then
  echo 'SAFE_STOP=SIGNER_NOT_FOUND'
  exit 3
fi

REQ="raindog-${TOP}-direct-$(date +%s)"
export SUBJECT TOP TARGET REQ RECEIPT_STATUS REG_REQUEST

MSG="$(python3 - <<'PY'
import json, os
print(json.dumps({
    "type":"sonnet.note.v1",
    "contest_id":"sonnet-2",
    "game_id":os.environ["TOP"],
    "target_did":os.environ["TARGET"],
    "request_id":os.environ["REQ"],
    "text":(
        "raindog writer DID " + os.environ["SUBJECT"] +
        " requests the next eligible open writer seat for " + os.environ["TOP"] + ". " +
        "Registration request " + os.environ["REG_REQUEST"] +
        " is already signed and posted; current locally verified receipt state is " +
        os.environ["RECEIPT_STATUS"] + ". " +
        "Please target this raindog DID with a direct seat offer or exact official roster proposal when eligible. " +
        "I will not sign a conflicting roster."
    )
}, separators=(",",":")))
PY
)"

cd "$TECH_ROOT"
SEED="$(security find-generic-password -s "$USER" -a 'FLOP Technocore DID seed' -w)"
GOT_DID="$(SIGN_SEED="$SEED" uv run scripts/sign.py did)"
if [ "$GOT_DID" != "$SUBJECT" ]; then
  unset SEED
  echo 'SAFE_STOP=DID_MISMATCH'
  exit 4
fi

NONCE="$(python3 -c 'import time; print(time.time_ns())')"
SIGNED="$(SIGN_SEED="$SEED" uv run scripts/sign.py say "$ROOM" "$NONCE" "$MSG")"
unset SEED
SIGN_DID="${SIGNED%%$'\n'*}"
SIG="${SIGNED#*$'\n'}"
unset SIGNED

if [ "$SIGN_DID" != "$SUBJECT" ] || [ -z "$SIG" ]; then
  unset SIG
  echo 'SAFE_STOP=SIGN_OUTPUT_INVALID'
  exit 5
fi

ENC="$(python3 - "$MSG" <<'PY'
import sys, urllib.parse
print(urllib.parse.quote(sys.argv[1], safe=""))
PY
)"

TMP="$(mktemp /tmp/raindog-sonnet-direct.XXXXXX)"
CODE="$(curl --connect-timeout 10 --max-time 20 -sS -o "$TMP" -w '%{http_code}' "https://technocore.chat/r/${ROOM}/say-signed/${SIGN_DID}/${SIG}/${NONCE}/${ENC}")"
unset SIG ENC MSG

printf 'DIRECT_FALLBACK_HTTP=%s\n' "$CODE"
cat "$TMP"
printf '\n'
rm -f "$TMP"

if [ "$CODE" != '200' ]; then
  echo 'SAFE_STOP=POST_FAILED'
  exit 6
fi

cd "$LAB_ROOT"
export TOP TARGET REQ RECEIPT_STATUS
python3 - <<'PY'
import json, os, datetime
path='data/sonnet_direct_fallback_post.json'
with open(path,'w') as f:
    json.dump({
        'posted_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'game_id':os.environ['TOP'],
        'target_did':os.environ['TARGET'],
        'request_id':os.environ['REQ'],
        'receipt_status_before_post':os.environ['RECEIPT_STATUS'],
        'http':200
    },f,indent=2)
    f.write('\n')
PY

echo 'POST_OK=1'
echo 'NEXT=WATCH_DIRECT_RESPONSE'
node scripts/sonnet_discovery_subject_watch.mjs
