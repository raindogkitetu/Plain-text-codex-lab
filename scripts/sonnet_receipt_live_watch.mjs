#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const ROOM='mb-sonnet-2-registration';
const CONTEST='sonnet-2';
const REQUEST_ID='register-raindog-writer-acf7b45a0344e497';
const SUBJECT_DID='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const REFEREE_DID='did:key:z6MkowHQwsx9xr84WbWN3YCnKutyBnBXkT1ChKY4uEAAMzte';
const DEADLINE_MS=Date.parse('2026-09-18T12:00:00.000Z');
const WATCH_MS=4*60*1000+20*1000;
const OUT='data/sonnet_receipt_live_watch_state.json';
const POST='data/sonnet_postretry_readcheck.json';
const MON='data/sonnet_receipt_monitor_state.json';
const B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const IDX=new Map([...B58].map((c,i)=>[c,i]));

function load(path){try{return JSON.parse(fs.readFileSync(path,'utf8'))}catch{return null}}
function save(state){fs.mkdirSync('data',{recursive:true});fs.writeFileSync(OUT,JSON.stringify(state,null,2)+'\n')}
function b58decode(raw){let n=0n;for(const ch of raw){const d=IDX.get(ch);if(d==null)throw new Error('bad base58');n=n*58n+BigInt(d)}let hex=n.toString(16);if(hex.length%2)hex='0'+hex;let body=hex?Buffer.from(hex,'hex'):Buffer.alloc(0);const lead=raw.length-raw.replace(/^1+/,'').length;if(lead)body=Buffer.concat([Buffer.alloc(lead),body]);return body}
function pub(did){const d=b58decode(did.slice('did:key:z'.length));if(d.length!==34||d[0]!==0xed||d[1]!==0x01)throw new Error('not ed25519');return crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),d.subarray(2)]),format:'der',type:'spki'})}
function verify(m){try{return !!m&&m.from===REFEREE_DID&&m.nonce!=null&&typeof m.text==='string'&&!!m.sig&&crypto.verify(null,Buffer.from(`${ROOM}|${m.nonce}|${m.text}`,'utf8'),pub(REFEREE_DID),Buffer.from(m.sig,'base64url'))}catch{return false}}
function deep(o,keys){if(!o||typeof o!=='object')return null;for(const k of keys)if(o[k]!=null)return o[k];for(const v of Object.values(o)){if(v&&typeof v==='object'){const x=deep(v,keys);if(x!=null)return x}}return null}
function receiptFrom(messages){for(const m of messages){if(!verify(m))continue;let p;try{p=JSON.parse(m.text)}catch{continue}if(p?.type!=='sonnet.receipt.v1')continue;if(p?.contest_id&&p.contest_id!==CONTEST)continue;if(String(deep(p,['request_id'])||'')!==REQUEST_ID)continue;const pd=deep(p,['participant_did','sender_did','did']);if(pd&&String(pd)!==SUBJECT_DID)continue;const raw=String(deep(p,['status','decision'])||'unknown').toLowerCase();const decision=raw==='accepted'?'ACCEPTED':((raw==='rejected'||raw==='refused')?'REFUSED':raw.toUpperCase());return {seq:Number(m.seq||0)||null,ts:m.ts||null,decision,reason:deep(p,['reason','reason_code','error'])??null,participant_did:pd??null,referee_did:REFEREE_DID,signature_verified:true}}return null}
async function getJson(url,ms=15000){const c=new AbortController();const t=setTimeout(()=>c.abort(),ms);try{const r=await fetch(url,{headers:{'user-agent':'raindog-sonnet-live-watch/1.1','cache-control':'no-cache'},signal:c.signal});if(!r.ok)throw new Error(`HTTP ${r.status}`);return await r.json()}finally{clearTimeout(t)}}
async function getText(url,ms=30000){const c=new AbortController();const t=setTimeout(()=>c.abort(),ms);try{const r=await fetch(url,{headers:{'user-agent':'raindog-sonnet-live-watch/1.1','cache-control':'no-cache'},signal:c.signal});if(!r.ok)throw new Error(`HTTP ${r.status}`);return await r.text()}finally{clearTimeout(t)}}

const old=load(OUT)||{};
const post=load(POST)||{};
const mon=load(MON)||{};
let cursor=Math.max(Number(old.cursor||0),Number(post.last_seq||0),Number(mon.cursor||0),3317809);
const started=Date.now();
const stopAt=Math.min(started+WATCH_MS,DEADLINE_MS);
let state={schema_version:2,contest:CONTEST,request_id:REQUEST_ID,subject_did:SUBJECT_DID,referee_did:REFEREE_DID,room:ROOM,started_at:new Date(started).toISOString(),checked_at:new Date().toISOString(),cursor,status:old.status==='ACCEPTED'||old.status==='REFUSED'?old.status:'WATCHING',terminal:old.terminal===true,receipt:old.receipt||null,coverage_gaps:Array.isArray(old.coverage_gaps)?old.coverage_gaps:[],read_errors:[],technocore_write_count:0};
if(state.terminal){save(state);console.log(JSON.stringify(state,null,2));process.exit(0)}

for(let attempt=0;attempt<2&&!state.receipt;attempt++){
  try{
    const raw=await getText(`https://technocore.chat/r/${ROOM}/export?n=${Date.now()}-${attempt}`,25000);
    const msgs=raw.split(/\r?\n/).filter(Boolean).map(x=>{try{return JSON.parse(x)}catch{return null}}).filter(Boolean);
    const rec=receiptFrom(msgs);if(rec)state.receipt=rec;
  }catch(e){state.read_errors.push(`export_${attempt+1}:${e?.name||'Error'}:${e?.message||String(e)}`)}
}

while(!state.receipt&&Date.now()<stopAt){
  try{
    const v=await getJson(`https://technocore.chat/r/${ROOM}?format=json&since=${cursor}&limit=200&wait=10&n=${Date.now()}`,20000);
    const first=v.first_seq==null?null:Number(v.first_seq);
    const last=Number(v.last_seq||cursor);
    if(first!=null&&first>cursor+1){state.coverage_gaps.push({from_cursor:cursor,first_retained_seq:first,observed_at:new Date().toISOString()});cursor=first-1;continue}
    const msgs=Array.isArray(v.messages)?v.messages:[];
    const rec=receiptFrom(msgs);if(rec){state.receipt=rec;break}
    if(last>cursor)cursor=last;
  }catch(e){state.read_errors.push(`${new Date().toISOString()}:${e?.name||'Error'}:${e?.message||String(e)}`);await new Promise(r=>setTimeout(r,1500))}
  if(state.read_errors.length>20)state.read_errors=state.read_errors.slice(-20);
  state.cursor=cursor;state.checked_at=new Date().toISOString();
}

state.cursor=cursor;
state.checked_at=new Date().toISOString();
if(state.receipt){state.status=state.receipt.decision;state.terminal=['ACCEPTED','REFUSED'].includes(state.receipt.decision)}
else if(Date.now()>=DEADLINE_MS){state.status='DEADLINE_NO_VERIFIED_RECEIPT';state.terminal=false}
else state.status='PENDING_NO_VERIFIED_RECEIPT';
save(state);
console.log(JSON.stringify(state,null,2));
