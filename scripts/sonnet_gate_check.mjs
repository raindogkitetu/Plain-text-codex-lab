#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const REG_ROOM='mb-sonnet-2-registration';
const RULES_ROOM='d-sonnet-2-rules';
const CONTEST='sonnet-2';
const REQUEST_ID='register-raindog-writer-acf7b45a0344e497';
const SUBJECT_DID='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const REFEREE_DID='did:key:z6MkowHQwsx9xr84WbWN3YCnKutyBnBXkT1ChKY4uEAAMzte';
const B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const IDX=new Map([...B58].map((c,i)=>[c,i]));

function b58decode(raw){let n=0n;for(const ch of raw){const d=IDX.get(ch);if(d==null)throw new Error('bad base58');n=n*58n+BigInt(d)}let hex=n.toString(16);if(hex.length%2)hex='0'+hex;let body=hex?Buffer.from(hex,'hex'):Buffer.alloc(0);const lead=raw.length-raw.replace(/^1+/,'').length;if(lead)body=Buffer.concat([Buffer.alloc(lead),body]);return body}
function pub(did){const d=b58decode(did.slice('did:key:z'.length));if(d.length!==34||d[0]!==0xed||d[1]!==0x01)throw new Error('not ed25519');return crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),d.subarray(2)]),format:'der',type:'spki'})}
function verify(m,did,room){try{return !!m&&m.from===did&&m.nonce!=null&&typeof m.text==='string'&&!!m.sig&&crypto.verify(null,Buffer.from(`${room}|${m.nonce}|${m.text}`,'utf8'),pub(did),Buffer.from(m.sig,'base64url'))}catch{return false}}
function J(s){try{return JSON.parse(s)}catch{return null}}
function deep(o,keys){if(!o||typeof o!=='object')return null;for(const k of keys)if(o[k]!=null)return o[k];for(const v of Object.values(o)){if(v&&typeof v==='object'){const x=deep(v,keys);if(x!=null)return x}}return null}
function sleep(ms){return new Promise(r=>setTimeout(r,ms))}
async function getText(url,ms=45000){const c=new AbortController(),t=setTimeout(()=>c.abort(),ms);try{const r=await fetch(url,{headers:{'user-agent':'raindog-sonnet-gate-check/1.0','cache-control':'no-cache'},signal:c.signal});if(!r.ok)throw new Error(`HTTP ${r.status}`);return await r.text()}finally{clearTimeout(t)}}
async function fetchExport(room, attempts=5){const errors=[];for(let i=1;i<=attempts;i++){try{return {ok:true,text:await getText(`https://technocore.chat/r/${room}/export?n=${Date.now()}-${i}`),errors}}catch(e){errors.push(`${e?.name||'Error'}:${e?.message||String(e)}`);if(i<attempts)await sleep(Math.min(8000,1500*i))}}return {ok:false,text:'',errors}}

function findReceipt(messages){for(const m of messages){if(!verify(m,REFEREE_DID,REG_ROOM))continue;const p=J(m.text);if(p?.type!=='sonnet.receipt.v1')continue;if(p?.contest_id&&p.contest_id!==CONTEST)continue;if(String(deep(p,['request_id'])||'')!==REQUEST_ID)continue;const pd=deep(p,['participant_did','sender_did','did']);if(pd&&String(pd)!==SUBJECT_DID)continue;const raw=String(deep(p,['status','decision'])||'unknown').toLowerCase();const decision=raw==='accepted'?'ACCEPTED':((raw==='rejected'||raw==='refused')?'REFUSED':raw.toUpperCase());return {seq:Number(m.seq||0)||null,ts:m.ts||null,decision,reason:deep(p,['reason','reason_code','error'])??null,participant_did:pd??null,referee_did:REFEREE_DID,signature_verified:true}}
return null}

const reg=await fetchExport(REG_ROOM,5);
let receipt=null;
if(reg.ok){const msgs=reg.text.split(/\r?\n/).filter(Boolean).map(J).filter(Boolean);receipt=findReceipt(msgs)}

const rules=await fetchExport(RULES_ROOM,4);
const ruleMentions=[];
if(rules.ok){for(const m of rules.text.split(/\r?\n/).filter(Boolean).map(J).filter(Boolean)){if(!verify(m,REFEREE_DID,RULES_ROOM))continue;if(typeof m.text==='string'&&(m.text.includes(SUBJECT_DID)||m.text.includes(REQUEST_ID)))ruleMentions.push({seq:Number(m.seq||0)||null,ts:m.ts||null,text:m.text.slice(0,2000)})}}

let directCount=0, latestDirect=null, discoveryCheckedAt=null;
try{const d=JSON.parse(fs.readFileSync('data/sonnet_discovery_subject_watch.json','utf8'));directCount=(d.direct_roster_or_invite||[]).length;latestDirect=d.latest_direct_roster_or_invite||null;discoveryCheckedAt=d.checked_at||null}catch{}

const writerStatus=receipt?.decision || (reg.ok?'PENDING_NO_VERIFIED_RECEIPT':'UNVERIFIED_NETWORK_INCOMPLETE');
let gate='WAIT_WRITER_ACCEPTED';
if(writerStatus==='ACCEPTED'&&directCount>0)gate='READY_TO_VERIFY_ROSTER';
else if(writerStatus==='REFUSED')gate='REGISTRATION_REFUSED';
else if(!reg.ok)gate='NETWORK_RECOVERY_NEEDED';
else if(directCount===0)gate='WAIT_DIRECT_ROSTER';

const out={
  checked_at:new Date().toISOString(),
  gate,
  writer_receipt_status:writerStatus,
  writer_receipt:receipt,
  registration_export_ok:reg.ok,
  registration_read_errors:reg.errors,
  rules_export_ok:rules.ok,
  rules_read_errors:rules.errors,
  verified_rules_mentions:ruleMentions,
  direct_roster_or_invite:directCount,
  latest_direct_roster_or_invite:latestDirect,
  discovery_checked_at:discoveryCheckedAt,
  technocore_write_count:0
};
fs.mkdirSync('data',{recursive:true});
fs.writeFileSync('data/sonnet_gate_check.json',JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out,null,2));
