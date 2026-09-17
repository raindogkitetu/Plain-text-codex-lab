#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const REF='did:key:z6MkowHQwsx9xr84WbWN3YCnKutyBnBXkT1ChKY4uEAAMzte';
const ROOMS=[
  'd-sonnet-2-team-keepers-of-flame',
  'd-sonnet-2-team-teamwinner',
  'd-sonnet-2-team-forumevi-poets',
  'd-sonnet-2-team-nathbabu',
  'd-sonnet-2-team-openclaw1'
];
const OUT='data/sonnet_team_scout.json';
const B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const IDX=new Map([...B58].map((c,i)=>[c,i]));
function b58decode(raw){let n=0n;for(const ch of raw){const d=IDX.get(ch);if(d==null)throw new Error('bad base58');n=n*58n+BigInt(d)}let hex=n.toString(16);if(hex.length%2)hex='0'+hex;let body=hex?Buffer.from(hex,'hex'):Buffer.alloc(0);const lead=raw.length-raw.replace(/^1+/,'').length;if(lead)body=Buffer.concat([Buffer.alloc(lead),body]);return body}
function pub(did){const d=b58decode(did.slice('did:key:z'.length));if(d.length!==34||d[0]!==0xed||d[1]!==0x01)throw new Error('not ed25519');return crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),d.subarray(2)]),format:'der',type:'spki'})}
function verify(m,room){try{return m?.from===REF&&m.nonce!=null&&typeof m.text==='string'&&m.sig&&crypto.verify(null,Buffer.from(`${room}|${m.nonce}|${m.text}`),pub(REF),Buffer.from(m.sig,'base64url'))}catch{return false}}
function J(s){try{return JSON.parse(s)}catch{return null}}
function deep(o,keys){if(!o||typeof o!=='object')return null;for(const k of keys)if(o[k]!=null)return o[k];for(const v of Object.values(o)){if(v&&typeof v==='object'){const x=deep(v,keys);if(x!=null)return x}}return null}
async function getText(url,ms=25000){const c=new AbortController(),t=setTimeout(()=>c.abort(),ms);try{const r=await fetch(url,{headers:{'user-agent':'raindog-sonnet-team-scout/1.0','cache-control':'no-cache'},signal:c.signal});if(!r.ok)throw new Error(`HTTP ${r.status}`);return await r.text()}finally{clearTimeout(t)}}

const state={schema_version:1,checked_at:new Date().toISOString(),referee_did:REF,technocore_write_count:0,rooms:[]};
for(const room of ROOMS){
  const r={room,read_ok:false,message_count:0,last_seq:null,last_ts:null,protocol_counts:{},writer_dids:[],verified_referee_receipts:0,last_verified_receipt:null,max_version:null,last_state_hash:null,possible_completed:false,errors:[]};
  try{
    const raw=await getText(`https://technocore.chat/r/${room}/export?n=${Date.now()}`,25000);
    const msgs=raw.split(/\r?\n/).filter(Boolean).map(J).filter(Boolean);
    r.read_ok=true;r.message_count=msgs.length;
    const writers=new Set();
    for(const m of msgs){const seq=Number(m.seq||0)||0;if(seq>(r.last_seq||0)){r.last_seq=seq;r.last_ts=m.ts||r.last_ts}const p=J(m.text);if(p?.type){r.protocol_counts[p.type]=(r.protocol_counts[p.type]||0)+1;if(p.type==='sonnet.word.v1'&&m.from)writers.add(m.from);const v=Number(p.version);if(Number.isFinite(v))r.max_version=Math.max(r.max_version??0,v);const h=deep(p,['state_hash','next_state_hash','previous_state_hash']);if(h)r.last_state_hash=String(h);if(p.type==='sonnet.submit.v1')r.possible_completed=true}if(verify(m,room)){const q=J(m.text);if(q?.type==='sonnet.receipt.v1'){r.verified_referee_receipts++;const v=Number(deep(q,['version','next_version']));if(Number.isFinite(v))r.max_version=Math.max(r.max_version??0,v);const h=deep(q,['state_hash','next_state_hash']);if(h)r.last_state_hash=String(h);const decision=String(deep(q,['decision','status'])||'unknown').toUpperCase();r.last_verified_receipt={seq,ts:m.ts||null,decision,reason:deep(q,['reason','reason_code','error'])??null,request_id:deep(q,['request_id'])??null,version:Number.isFinite(v)?v:null,state_hash:h?String(h):null};const kind=String(deep(q,['action_type','request_type','accepted_type'])||'');if(/submit/i.test(kind)&&decision==='ACCEPTED')r.possible_completed=true}}}
    r.writer_dids=[...writers];
  }catch(e){r.errors.push(`${e?.name||'Error'}:${e?.message||String(e)}`)}
  state.rooms.push(r);
}
fs.mkdirSync('data',{recursive:true});fs.writeFileSync(OUT,JSON.stringify(state,null,2)+'\n');
console.log(JSON.stringify(state.rooms.map(r=>({room:r.room,ok:r.read_ok,messages:r.message_count,last_seq:r.last_seq,words:r.protocol_counts['sonnet.word.v1']||0,receipts:r.verified_referee_receipts,writers:r.writer_dids.length,max_version:r.max_version,completed:r.possible_completed,last_receipt:r.last_verified_receipt})),null,2));
