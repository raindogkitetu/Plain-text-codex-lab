#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const ROOM='mb-sonnet-2-registration';
const CONTEST='sonnet-2';
const REQUEST_ID='register-raindog-writer-acf7b45a0344e497';
const SUBJECT_DID='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const REFEREE_DID='did:key:z6MkowHQwsx9xr84WbWN3YCnKutyBnBXkT1ChKY4uEAAMzte';
const EXPECTED_TEXT='{"type":"sonnet.register.v1","contest_id":"sonnet-2","role":"writer","x_account_url":"https://x.com/raindog_kitetu","request_id":"register-raindog-writer-acf7b45a0344e497"}';
const OUT='data/sonnet_postretry_readcheck.json';
const MONITOR='data/sonnet_receipt_monitor_state.json';
const B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const IDX=new Map([...B58].map((c,i)=>[c,i]));

function b58decode(raw){let n=0n;for(const ch of raw){const d=IDX.get(ch);if(d==null)throw new Error('bad base58');n=n*58n+BigInt(d)}let hex=n.toString(16);if(hex.length%2)hex='0'+hex;let body=hex?Buffer.from(hex,'hex'):Buffer.alloc(0);const lead=raw.length-raw.replace(/^1+/,'').length;if(lead)body=Buffer.concat([Buffer.alloc(lead),body]);return body}
function pub(did){const d=b58decode(did.slice('did:key:z'.length));if(d.length!==34||d[0]!==0xed||d[1]!==0x01)throw new Error('not ed25519');return crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),d.subarray(2)]),format:'der',type:'spki'})}
function verify(m,did){try{return !!m&&m.from===did&&m.nonce!=null&&typeof m.text==='string'&&!!m.sig&&crypto.verify(null,Buffer.from(`${ROOM}|${m.nonce}|${m.text}`,'utf8'),pub(did),Buffer.from(m.sig,'base64url'))}catch{return false}}
function deep(o,keys){if(!o||typeof o!=='object')return null;for(const k of keys)if(o[k]!=null)return o[k];for(const v of Object.values(o))if(v&&typeof v==='object'){const x=deep(v,keys);if(x!=null)return x}return null}
function inspect(messages,s){for(const m of messages){if(!s.registration_message_found&&m?.from===SUBJECT_DID&&m?.text===EXPECTED_TEXT&&verify(m,SUBJECT_DID)){s.registration_message_found=true;s.registration_seq=Number(m.seq||0)||null;s.registration_ts=m.ts||null;s.registration_signature_verified=true}if(!s.receipt&&m?.from===REFEREE_DID&&verify(m,REFEREE_DID)){let p;try{p=JSON.parse(m.text)}catch{continue}if(p?.type!=='sonnet.receipt.v1'||(p?.contest_id&&p.contest_id!==CONTEST)||String(deep(p,['request_id'])||'')!==REQUEST_ID)continue;const pd=deep(p,['participant_did','sender_did','did']);if(pd&&String(pd)!==SUBJECT_DID)continue;const raw=String(deep(p,['status','decision'])||'unknown').toLowerCase();const decision=raw==='accepted'?'ACCEPTED':((raw==='rejected'||raw==='refused')?'REFUSED':raw.toUpperCase());s.receipt={seq:Number(m.seq||0)||null,ts:m.ts||null,decision,reason:deep(p,['reason','reason_code','error'])??null,participant_did:pd??null,referee_did:REFEREE_DID,signature_verified:true}}}}
async function getText(url,ms=15000){const c=new AbortController(),t=setTimeout(()=>c.abort(),ms);try{const r=await fetch(url,{headers:{'user-agent':'raindog-sonnet-postretry-readcheck/1.1','cache-control':'no-cache'},signal:c.signal});if(!r.ok)throw new Error(`HTTP ${r.status}`);return await r.text()}finally{clearTimeout(t)}}

let previous={};try{previous=JSON.parse(fs.readFileSync(MONITOR,'utf8'))}catch{}
let cursor=Number(previous.cursor||0);
const s={schema_version:1,checked_at:new Date().toISOString(),room:ROOM,contest:CONTEST,request_id:REQUEST_ID,subject_did:SUBJECT_DID,referee_did:REFEREE_DID,start_cursor:cursor,registration_message_found:false,registration_seq:null,registration_ts:null,registration_signature_verified:false,receipt:null,export_scanned:false,incremental_read_succeeded:false,history_gap:null,last_seq:cursor,technocore_write_count:0};
try{const raw=await getText(`https://technocore.chat/r/${ROOM}/export?n=${Date.now()}`,10000);s.export_scanned=true;inspect(raw.split(/\r?\n/).filter(Boolean).map(x=>{try{return JSON.parse(x)}catch{return null}}).filter(Boolean),s)}catch(e){s.export_error=`${e?.name||'Error'}:${e?.message||String(e)}`}
if(!s.receipt||!s.registration_message_found){for(let i=0;i<40;i++){let v;try{v=JSON.parse(await getText(`https://technocore.chat/r/${ROOM}?format=json&since=${cursor}&limit=200&wait=0&n=${Date.now()}`,15000));s.incremental_read_succeeded=true}catch(e){s.read_error=`${e?.name||'Error'}:${e?.message||String(e)}`;break}const first=v.first_seq==null?null:Number(v.first_seq),last=Number(v.last_seq||cursor);s.last_seq=Math.max(s.last_seq,last);if(first!=null&&first>cursor+1){s.history_gap={from_cursor:cursor,first_retained_seq:first};cursor=first-1;continue}const msgs=Array.isArray(v.messages)?v.messages:[];inspect(msgs,s);if(s.receipt&&s.registration_message_found)break;if(last<=cursor)break;cursor=last;if(msgs.length<200)break}}
s.status=s.receipt?.decision||'PENDING_NO_VERIFIED_RECEIPT';
fs.mkdirSync('data',{recursive:true});fs.writeFileSync(OUT,JSON.stringify(s,null,2)+'\n');console.log(JSON.stringify(s,null,2));