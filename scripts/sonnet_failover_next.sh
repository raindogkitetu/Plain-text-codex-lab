#!/bin/bash
set -euo pipefail

LAB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$LAB_ROOT"

SUBJECT='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4'
ROOM='mb-sonnet-2-discovery'
REG_REQUEST='register-raindog-writer-acf7b45a0344e497'
PREV_MARKER='data/sonnet_direct_fallback_post.json'
MARKER='data/sonnet_direct_fallback_post_2.json'
WATCH='data/sonnet_discovery_subject_watch.json'

if [ -f "$MARKER" ]; then
  echo 'SAFE_STOP=SECOND_FALLBACK_ALREADY_POSTED'
  cat "$MARKER"
  exit 0
fi

if [ ! -f "$WATCH" ]; then
  echo 'SAFE_STOP=NO_DISCOVERY_WATCH_STATE'
  exit 2
fi

WATCH_OK="$(node -e 'const x=require("./data/sonnet_discovery_subject_watch.json");process.stdout.write(String(!!x.read_ok))')"
DIRECT_COUNT="$(node -e 'const x=require("./data/sonnet_discovery_subject_watch.json");process.stdout.write(String((x.direct_roster_or_invite||[]).length))')"
WATCH_ERRORS="$(node -e 'const x=require("./data/sonnet_discovery_subject_watch.json");process.stdout.write(String((x.errors||[]).length))')"
WATCH_AGE="$(node -e 'const x=require("./data/sonnet_discovery_subject_watch.json");const t=Date.parse(x.checked_at||0);process.stdout.write(String(Number.isFinite(t)?Math.floor((Date.now()-t)/60000):9999))')"

printf 'WATCH_OK=%s\nDIRECT_COUNT=%s\nWATCH_ERRORS=%s\nWATCH_AGE_MIN=%s\n' "$WATCH_OK" "$DIRECT_COUNT" "$WATCH_ERRORS" "$WATCH_AGE"

if [ "$WATCH_OK" != 'true' ] || [ "$WATCH_ERRORS" != '0' ] || [ "$WATCH_AGE" -gt 20 ]; then
  echo 'SAFE_STOP=DISCOVERY_WATCH_NOT_FRESH_CLEAN'
  exit 3
fi

if [ "$DIRECT_COUNT" != '0' ]; then
  echo 'SAFE_STOP=DIRECT_PATH_ALREADY_EXISTS'
  node -e 'const x=require("./data/sonnet_discovery_subject_watch.json");console.log(JSON.stringify(x.latest_direct_roster_or_invite||null,null,2))'
  exit 0
fi

PREV_GAME=''
if [ -f "$PREV_MARKER" ]; then
  PREV_GAME="$(node -e 'const x=require("./data/sonnet_direct_fallback_post.json");process.stdout.write(x.game_id||"")')"
fi

echo "PREVIOUS_TEAM=$PREV_GAME"

node scripts/sonnet_candidate_live.mjs

SELECTED_JSON="$(node - <<'NODE'
const fs=require('fs');
const x=JSON.parse(fs.readFileSync('data/sonnet_candidate_live.json','utf8'));
const prev=process.env.PREV_GAME||'';
const subject=process.env.SUBJECT;
if ((x.errors||[]).length) process.exit(10);
const now=Date.now();
for (const c of (x.candidates||[])) {
  if (!c || c.game_id===prev || !c.read_ok || !c.setup_accepted || c.word_posts!==0 || (c.errors||[]).length) continue;
  const sigs=[...(c.recruitment_signals||[])].reverse();
  const s=sigs.find(v=>v && v.from && v.from!==subject && /seat|open|recruit|roster|join|writer|slot|member/i.test(String(v.text||'')));
  if (!s) continue;
  const age=Date.parse(s.ts||0);
  if (!Number.isFinite(age) || now-age > 90*60*1000) continue;
  process.stdout.write(JSON.stringify({game_id:c.game_id,room:c.room,score:c.score,target_did:s.from,signal_ts:s.ts,signal_seq:s.seq,setup_accepted:c.setup_accepted,word_posts:c.word_posts,read_ok:c.read_ok}));
  process.exit(0);
}
process.exit(11);
NODE
)" || {
  echo 'SAFE_STOP=NO_NEXT_ACTIONABLE_FALLBACK'
  exit 4
}

export SELECTED_JSON
TOP="$(node -e 'const x=JSON.parse(process.env.SELECTED_JSON);process.stdout.write(x.game_id)')"
TARGET="$(node -e 'const x=JSON.parse(process.env.SELECTED_JSON);process.stdout.write(x.target_did)')"
SCORE="$(node -e 'const x=JSON.parse(process.env.SELECTED_JSON);process.stdout.write(String(x.score))')"
SIGNAL_TS="$(node -e 'const x=JSON.parse(process.env.SELECTED_JSON);process.stdout.write(String(x.signal_ts||""))')"

printf 'SELECTED_TEAM=%s\nSELECTED_SCORE=%s\nTARGET=%s\nSIGNAL_TS=%s\n' "$TOP" "$SCORE" "$TARGET" "$SIGNAL_TS"

RECEIPT_STATUS="$(node -e 'const fs=require("fs");try{const x=JSON.parse(fs.readFileSync("data/sonnet_receipt_live_watch_state.json","utf8"));process.stdout.write(x.status||"UNKNOWN")}catch{process.stdout.write("UNKNOWN")}')"

TECH_ROOT="$HOME/FLOP-safe/technocore-chat"
if [ ! -f "$TECH_ROOT/scripts/sign.py" ]; then
  echo 'SAFE_STOP=SIGNER_NOT_FOUND'
  exit 5
fi

REQ="raindog-${TOP}-direct2-$(date +%s)"
export SUBJECT TOP TARGET REQ RECEIPT_STATUS REG_REQUEST
MSG="$(python3 - <<'PY'
import json, os
print(json.dumps({
  'type':'sonnet.note.v1',
  'contest_id':'sonnet-2',
  'game_id':os.environ['TOP'],
  'target_did':os.environ['TARGET'],
  'request_id':os.environ['REQ'],
  'text':(
    'raindog writer DID '+os.environ['SUBJECT']+
    ' requests the next eligible open writer seat for '+os.environ['TOP']+'. '
    'Registration request '+os.environ['REG_REQUEST']+
    ' is already signed and posted; current locally verified receipt state is '+os.environ['RECEIPT_STATUS']+'. '
    'Please target this raindog DID with a direct seat offer or exact official roster proposal when eligible. '
    'I will not sign a conflicting roster.'
  )
},separators=(',',':')))
PY
)"

cd "$TECH_ROOT"
SEED=''
KEYCHAIN_LAYOUT=''
if SEED="$(security find-generic-password -s 'FLOP Technocore DID seed' -a "$USER" -w 2>/dev/null)"; then
  KEYCHAIN_LAYOUT='service-seed/account-user'
elif SEED="$(security find-generic-password -s "$USER" -a 'FLOP Technocore DID seed' -w 2>/dev/null)"; then
  KEYCHAIN_LAYOUT='service-user/account-seed'
elif SEED="$(security find-generic-password -s 'FLOP Technocore DID seed' -w 2>/dev/null)"; then
  KEYCHAIN_LAYOUT='service-seed/any-account'
else
  echo 'SAFE_STOP=KEYCHAIN_SEED_NOT_FOUND'
  exit 6
fi

echo "KEYCHAIN_LAYOUT=$KEYCHAIN_LAYOUT"
GOT_DID="$(SIGN_SEED="$SEED" uv run scripts/sign.py did)"
if [ "$GOT_DID" != "$SUBJECT" ]; then
  unset SEED
  echo 'SAFE_STOP=DID_MISMATCH'
  exit 7
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
  exit 8
fi

ENC="$(python3 - "$MSG" <<'PY'
import sys, urllib.parse
print(urllib.parse.quote(sys.argv[1], safe=''))
PY
)"
TMP="$(mktemp /tmp/raindog-sonnet-direct2.XXXXXX)"
CODE="$(curl --connect-timeout 10 --max-time 20 -sS -o "$TMP" -w '%{http_code}' "https://technocore.chat/r/${ROOM}/say-signed/${SIGN_DID}/${SIG}/${NONCE}/${ENC}")"
unset SIG ENC MSG
printf 'SECOND_FALLBACK_HTTP=%s\n' "$CODE"
cat "$TMP"; printf '\n'; rm -f "$TMP"

if [ "$CODE" != '200' ]; then
  echo 'SAFE_STOP=POST_FAILED'
  exit 9
fi

cd "$LAB_ROOT"
export TOP TARGET REQ RECEIPT_STATUS SCORE SIGNAL_TS
python3 - <<'PY'
import json, os, datetime
with open('data/sonnet_direct_fallback_post_2.json','w') as f:
    json.dump({
      'posted_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'game_id':os.environ['TOP'],
      'target_did':os.environ['TARGET'],
      'request_id':os.environ['REQ'],
      'receipt_status_before_post':os.environ['RECEIPT_STATUS'],
      'score':int(os.environ['SCORE']),
      'signal_ts':os.environ['SIGNAL_TS'],
      'http':200
    },f,indent=2); f.write('\n')
PY

echo 'SECOND_POST_OK=1'
echo 'WATCHING=DISCOVERY_AND_WRITER_RECEIPT'
node scripts/sonnet_receipt_live_watch.mjs > data/sonnet_receipt_after_failover.log 2>&1 &
RPID=$!
node scripts/sonnet_discovery_subject_watch.mjs
wait "$RPID" || true

echo 'FINAL_SUMMARY_BEGIN'
node - <<'NODE'
const fs=require('fs');
const d=JSON.parse(fs.readFileSync('data/sonnet_discovery_subject_watch.json','utf8'));
let r={status:'UNKNOWN',receipt:null,checked_at:null};
try{const x=JSON.parse(fs.readFileSync('data/sonnet_receipt_live_watch_state.json','utf8'));r={status:x.status,receipt:x.receipt,checked_at:x.checked_at}}catch{}
console.log(JSON.stringify({
  discovery_checked_at:d.checked_at,
  read_ok:d.read_ok,
  direct_roster_or_invite:(d.direct_roster_or_invite||[]).length,
  latest_direct_roster_or_invite:d.latest_direct_roster_or_invite||null,
  discovery_errors:d.errors||[],
  writer_receipt_status:r.status,
  writer_receipt:r.receipt,
  writer_receipt_checked_at:r.checked_at
},null,2));
NODE
echo 'FINAL_SUMMARY_END'
