#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const ROOM='mb-sonnet-2-registration';
const SUBJECT='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const REF='did:key:z6MkowHQwsx9xr84WbWN3YCnKutyBnBXkT1ChKY4uEAAMzte';
const REQ='register-raindog-writer-acf7b45a0344e497';
const START_SEQ=3596822;
const INTERVAL=Number(process.env.INTERVAL||30);
const DEADLINE=Date.parse('2026-09-18T12:00:00Z');
const OUT='data/sonnet_referee_query_reply.json';
const B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const IDX=new Map([...B58].map((c,i)=>[c,i]));

function b58decode(raw){let n=0n;for(const ch of raw){const d=IDX.get(ch);if(d==null)throw new Error('bad base58');n=n*58n+BigInt(d)}let hex=n.toString(16);if(hex.length%2)hex='0'+hex;let body=hex?Buffer.from(hex,'hex'):Buffer.alloc(0);const lead=raw.length-raw.replace(/^1+/,'').length;if(lead)body=Buffer.concat([Buffer.alloc(lead),body]);return body}
function pub(did){const d=b58decode(did.slice('did:key:z'.length));if(d.length!==34||d[0]!==0xed||d[1]!==0x01)throw new Error('not ed25519');return crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),d.subarray(2)]),format:'der',type:'spki'})}
const PUB=pub(REF);
function verify(m){try{return m?.from===REF&&m.nonce!=null&&typeof m.text==='string'&&!!m.sig&&crypto.verify(null,Buffer.from(`${ROOM}|${m.nonce}|${m.text}`,'utf8'),PUB,Buffer.from(m.sig,'base64url'))}catch{return false}}
function J(s){try{return JSON.parse(s)}catch{return null}}
function sleep(ms){return new Promise(r=>setTimeout(r,ms))}
async function fetchRoom(since){const c=new AbortController(),t=setTimeout(()=>c.abort(),25000);try{const r=await fetch(`https://technocore.chat/r/${ROOM}?since=${since}&wait=10&n=${Date.now()}`,{headers:{'user-agent':'raindog-sonnet-referee-query-watch/1.0','cache-control':'no-cache'},signal:c.signal});if(!r.ok)throw new Error(`HTTP ${r.status}`);return await r.text()}finally{clearTimeout(t)}}
function relevant(m){if(!verify(m))return false;const t=String(m.text||'');if(t.includes(SUBJECT)||t.includes(REQ))return true;const p=J(t);if(!p)return false;const s=JSON.stringify(p);return s.includes(SUBJECT)||s.includes(REQ)||s.includes('3596822')}

let cursor=START_SEQ;
let round=0;
while(Date.now()<DEADLINE){
  round++;
  try{
    const raw=await fetchRoom(cursor);
    const msgs=raw.split(/\r?\n/).filter(Boolean).map(J).filter(Boolean);
    for(const m of msgs){const seq=Number(m.seq||0)||0;if(seq>cursor)cursor=seq;if(!relevant(m))continue;const out={checked_at:new Date().toISOString(),query_seq:START_SEQ,reply_seq:seq,reply_ts:m.ts||null,referee_did:REF,signature_verified:true,text:m.text};fs.mkdirSync('data',{recursive:true});fs.writeFileSync(OUT,JSON.stringify(out,null,2)+'\n');console.log('REFEREE_REPLY_FOUND=1');console.log(JSON.stringify(out,null,2));process.exit(0)}
    console.log(`ROUND=${round} cursor=${cursor} no_signed_referee_reply_yet`);
  }catch(e){console.log(`ROUND=${round} transient=${e?.name||'Error'}:${e?.message||String(e)}`)}
  await sleep(INTERVAL*1000);
}
console.log('REFEREE_REPLY_FOUND=0');
console.log('STOP=DEADLINE_REACHED');
