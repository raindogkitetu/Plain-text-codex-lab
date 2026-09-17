#!/bin/bash
set -euo pipefail

LAB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$LAB_ROOT"

SUBJECT='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4'
ROOM='mb-sonnet-2-discovery'
REG_REQUEST='register-raindog-writer-acf7b45a0344e497'
TECH_ROOT="$HOME/FLOP-safe/technocore-chat"
CONTACT_LOG='data/sonnet_failover_contacts.json'
MAX_NEW_CONTACTS="${MAX_NEW_CONTACTS:-2}"

if [ ! -f "$TECH_ROOT/scripts/sign.py" ]; then
  echo 'SAFE_STOP=SIGNER_NOT_FOUND'
  exit 2
fi

python3 - <<'PY'
import json, os
p='data/sonnet_failover_contacts.json'
items=[]
for src in ['data/sonnet_direct_fallback_post.json','data/sonnet_direct_fallback_post_2.json']:
    try:
        x=json.load(open(src))
        if x.get('game_id'):
            items.append({'game_id':x['game_id'],'target_did':x.get('target_did'),'request_id':x.get('request_id'),'posted_at':x.get('posted_at'),'source':src})
    except Exception:
        pass
try:
    old=json.load(open(p))
    if isinstance(old,list): items += old
except Exception:
    pass
seen=set(); out=[]
for x in items:
    g=x.get('game_id')
    if g and g not in seen:
        seen.add(g); out.append(x)
os.makedirs('data',exist_ok=True)
json.dump(out,open(p,'w'),indent=2); open(p,'a').write('\n')
PY

get_receipt_status() {
  node -e 'const fs=require("fs");try{const x=JSON.parse(fs.readFileSync("data/sonnet_receipt_live_watch_state.json","utf8"));process.stdout.write(x.status||"UNKNOWN")}catch{process.stdout.write("UNKNOWN")}'
}

get_direct_count() {
  node -e 'const fs=require("fs");try{const x=JSON.parse(fs.readFileSync("data/sonnet_discovery_subject_watch.json","utf8"));process.stdout.write(String((x.direct_roster_or_invite||[]).length))}catch{process.stdout.write("0")}'
}

precheck() {
  local rs dc
  rs="$(get_receipt_status)"
  dc="$(get_direct_count)"
  echo "PRECHECK_RECEIPT_STATUS=$rs"
  echo "PRECHECK_DIRECT_COUNT=$dc"
  if [ "$rs" = 'ACCEPTED' ] || [ "$rs" = 'REFUSED' ]; then
    echo "ACTIONABLE_RECEIPT_STATUS=$rs"
    return 10
  fi
  if [ "$dc" != '0' ]; then
    echo 'ACTIONABLE_DIRECT_PATH=1'
    node -e 'const x=require("./data/sonnet_discovery_subject_watch.json");console.log(JSON.stringify(x.latest_direct_roster_or_invite||null,null,2))'
    return 11
  fi
  return 0
}

select_candidate() {
  node scripts/sonnet_candidate_live.mjs >/tmp/sonnet-candidate-live.out
  cat /tmp/sonnet-candidate-live.out >&2
  node - <<'NODE'
const fs=require('fs');
const x=JSON.parse(fs.readFileSync('data/sonnet_candidate_live.json','utf8'));
const contacts=JSON.parse(fs.readFileSync('data/sonnet_failover_contacts.json','utf8'));
const used=new Set((contacts||[]).map(v=>String(v.game_id||'').toLowerCase()));
const subject='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const now=Date.now();
if ((x.errors||[]).length) process.exit(20);
for (const c of (x.candidates||[])) {
  const g=String(c?.game_id||'').toLowerCase();
  if (!g || used.has(g) || !c.read_ok || !c.setup_accepted || c.word_posts!==0 || (c.errors||[]).length) continue;
  const sigs=[...(c.recruitment_signals||[])].reverse();
  const s=sigs.find(v=>v && v.from && v.from!==subject && /seat|open|recruit|roster|join|writer|slot|member|available/i.test(String(v.text||'')));
  if (!s) continue;
  const ts=Date.parse(s.ts||0);
  if (!Number.isFinite(ts) || now-ts>120*60*1000) continue;
  process.stdout.write(JSON.stringify({game_id:g,room:c.room,score:c.score,target_did:s.from,signal_ts:s.ts,signal_seq:s.seq}));
  process.exit(0);
}
process.exit(21);
NODE
}

load_seed() {
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
    exit 3
  fi
  echo "KEYCHAIN_LAYOUT=$KEYCHAIN_LAYOUT"
  local got
  got="$(cd "$TECH_ROOT" && SIGN_SEED="$SEED" uv run scripts/sign.py did)"
  if [ "$got" != "$SUBJECT" ]; then
    unset SEED
    echo 'SAFE_STOP=DID_MISMATCH'
    exit 4
  fi
}

post_candidate() {
  local selected="$1"
  if ! node -e 'JSON.parse(process.argv[1])' "$selected" >/dev/null 2>&1; then
    echo 'SAFE_STOP=SELECTED_JSON_INVALID'
    return 12
  fi
  export SELECTED_JSON="$selected"
  local game target score signal_ts req receipt msg nonce signed sign_did sig enc tmp code
  game="$(node -e 'const x=JSON.parse(process.env.SELECTED_JSON);process.stdout.write(x.game_id)')"
  target="$(node -e 'const x=JSON.parse(process.env.SELECTED_JSON);process.stdout.write(x.target_did)')"
  score="$(node -e 'const x=JSON.parse(process.env.SELECTED_JSON);process.stdout.write(String(x.score))')"
  signal_ts="$(node -e 'const x=JSON.parse(process.env.SELECTED_JSON);process.stdout.write(String(x.signal_ts||""))')"
  receipt="$(get_receipt_status)"
  req="raindog-${game}-chain-$(date +%s)"
  export SUBJECT REG_REQUEST game target receipt req
  msg="$(python3 - <<'PY'
import json, os
print(json.dumps({
  'type':'sonnet.note.v1','contest_id':'sonnet-2','game_id':os.environ['game'],
  'target_did':os.environ['target'],'request_id':os.environ['req'],
  'text':('raindog writer DID '+os.environ['SUBJECT']+' requests the next eligible open writer seat for '+os.environ['game']+'. '
          'Registration request '+os.environ['REG_REQUEST']+' is already signed and posted; current locally verified receipt state is '+os.environ['receipt']+'. '
          'Please target this raindog DID with a direct seat offer or exact official roster proposal when eligible. I will not sign a conflicting roster.')
},separators=(',',':')))
PY
)"
  load_seed
  nonce="$(python3 -c 'import time; print(time.time_ns())')"
  signed="$(cd "$TECH_ROOT" && SIGN_SEED="$SEED" uv run scripts/sign.py say "$ROOM" "$nonce" "$msg")"
  unset SEED
  sign_did="${signed%%$'\n'*}"
  sig="${signed#*$'\n'}"
  unset signed
  if [ "$sign_did" != "$SUBJECT" ] || [ -z "$sig" ]; then
    unset sig
    echo 'SAFE_STOP=SIGN_OUTPUT_INVALID'
    exit 5
  fi
  enc="$(python3 - "$msg" <<'PY'
import sys, urllib.parse
print(urllib.parse.quote(sys.argv[1],safe=''))
PY
)"
  tmp="$(mktemp /tmp/raindog-sonnet-chain.XXXXXX)"
  code="$(curl --connect-timeout 10 --max-time 20 -sS -o "$tmp" -w '%{http_code}' "https://technocore.chat/r/${ROOM}/say-signed/${sign_did}/${sig}/${nonce}/${enc}")"
  unset sig enc msg
  echo "CHAIN_TEAM=$game"
  echo "CHAIN_SCORE=$score"
  echo "CHAIN_TARGET=$target"
  echo "CHAIN_HTTP=$code"
  cat "$tmp"; echo
  rm -f "$tmp"
  if [ "$code" != '200' ]; then
    echo 'SAFE_STOP=POST_FAILED'
    exit 6
  fi
  export game target score signal_ts req receipt
  python3 - <<'PY'
import json, os, datetime
p='data/sonnet_failover_contacts.json'
try: items=json.load(open(p))
except Exception: items=[]
items.append({'game_id':os.environ['game'],'target_did':os.environ['target'],'request_id':os.environ['req'],'posted_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'score':int(os.environ['score']),'signal_ts':os.environ['signal_ts'],'receipt_status_before_post':os.environ['receipt'],'http':200,'source':'chain'})
json.dump(items,open(p,'w'),indent=2); open(p,'a').write('\n')
PY
}

watch_both() {
  node scripts/sonnet_receipt_live_watch.mjs > data/sonnet_chain_receipt.log 2>&1 &
  local rpid=$!
  node scripts/sonnet_discovery_subject_watch.mjs > data/sonnet_chain_discovery.log 2>&1 || true
  wait "$rpid" || true
}

for ((i=1;i<=MAX_NEW_CONTACTS;i++)); do
  if ! precheck; then
    break
  fi
  selected="$(select_candidate)" || {
    echo 'SAFE_STOP=NO_NEXT_ACTIONABLE_FALLBACK'
    break
  }
  if ! node -e 'JSON.parse(process.argv[1])' "$selected" >/dev/null 2>&1; then
    echo 'SAFE_STOP=SELECTED_JSON_INVALID'
    break
  fi
  echo "CHAIN_SELECTED_JSON=$selected"
  post_candidate "$selected"
  echo "CHAIN_WATCH_ROUND=$i"
  watch_both
  rs="$(get_receipt_status)"
  dc="$(get_direct_count)"
  echo "ROUND_${i}_RECEIPT_STATUS=$rs"
  echo "ROUND_${i}_DIRECT_COUNT=$dc"
  if [ "$rs" = 'ACCEPTED' ] || [ "$rs" = 'REFUSED' ] || [ "$dc" != '0' ]; then
    break
  fi
done

echo 'FINAL_CHAIN_SUMMARY_BEGIN'
node - <<'NODE'
const fs=require('fs');
let d={},r={},contacts=[];
try{d=JSON.parse(fs.readFileSync('data/sonnet_discovery_subject_watch.json','utf8'))}catch{}
try{r=JSON.parse(fs.readFileSync('data/sonnet_receipt_live_watch_state.json','utf8'))}catch{}
try{contacts=JSON.parse(fs.readFileSync('data/sonnet_failover_contacts.json','utf8'))}catch{}
console.log(JSON.stringify({
  contacts:contacts.map(x=>({game_id:x.game_id,target_did:x.target_did,request_id:x.request_id,posted_at:x.posted_at,http:x.http})),
  discovery_checked_at:d.checked_at||null,
  read_ok:!!d.read_ok,
  direct_roster_or_invite:(d.direct_roster_or_invite||[]).length,
  latest_direct_roster_or_invite:d.latest_direct_roster_or_invite||null,
  discovery_errors:d.errors||[],
  writer_receipt_status:r.status||'UNKNOWN',
  writer_receipt:r.receipt||null,
  writer_receipt_checked_at:r.checked_at||null
},null,2));
NODE
echo 'FINAL_CHAIN_SUMMARY_END'
