#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const SUBJECT='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const CUTOFF=Date.parse('2026-09-11T12:00:00.000Z');
const IN='data/sonnet_identity_evidence_scan.json';
const OUT='data/sonnet_identity_evidence_retry.json';
const B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const IDX=new Map([...B58].map((c,i)=>[c,i]));
function b58decode(raw){let n=0n;for(const ch of raw){const d=IDX.get(ch);if(d==null)throw new Error('bad base58');n=n*58n+BigInt(d)}let hex=n.toString(16);if(hex.length%2)hex='0'+hex;let body=hex?Buffer.from(hex,'hex'):Buffer.alloc(0);const lead=raw.length-raw.replace(/^1+/,'').length;if(lead)body=Buffer.concat([Buffer.alloc(lead),body]);return body}
function pub(did){const d=b58decode(did.slice('did:key:z'.length));if(d.length!==34||d[0]!==0xed||d[1]!==0x01)throw new Error('not ed25519');return crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),d.subarray(2)]),format:'der',type:'spki'})}
const PUB=pub(SUBJECT);
function verify(m,room){try{return m?.from===SUBJECT&&m.nonce!=null&&typeof m.text==='string'&&!!m.sig&&crypto.verify(null,Buffer.from(`${room}|${m.nonce}|${m.text}`,'utf8'),PUB,Buffer.from(m.sig,'base64url'))}catch{return false}}
function J(s){try{return JSON.parse(s)}catch{return null}}
function sleep(ms){return new Promise(r=>setTimeout(r,ms))}
async function getRoom(room,attempt){const c=new AbortController(),t=setTimeout(()=>c.abort(),35000);try{const r=await fetch(`https://technocore.chat/r/${encodeURIComponent(room)}/export?n=${Date.now()}-${attempt}`,{headers:{'user-agent':'raindog-sonnet-evidence-retry/1.0','cache-control':'no-cache'},signal:c.signal});if(!r.ok)throw new Error(`HTTP ${r.status}`);return await r.text()}finally{clearTimeout(t)}}

const src=JSON.parse(fs.readFileSync(IN,'utf8'));
const roomNames=new Set();
for(const e of src.errors||[]){
  const s=String(e||'');
  const i=s.indexOf(':');
  if(i<=0)continue;
  const room=s.slice(0,i);
  if(room==='rooms'||room==='events')continue;
  if(/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(room))roomNames.add(room);
}
const evidence=[];const errors=[];const recovered=[];
for(const room of roomNames){
  let raw=null;let lastErr=null;
  for(let a=1;a<=5;a++){
    try{raw=await getRoom(room,a);lastErr=null;break}catch(e){lastErr=`${e?.name||'Error'}:${e?.message||String(e)}`;await sleep(1200*a)}
  }
  if(raw==null){errors.push(`${room}:${lastErr}`);continue}
  recovered.push(room);
  if(!raw.includes(SUBJECT))continue;
  for(const line of raw.split(/\r?\n/).filter(Boolean)){
    const m=J(line);if(!m||m.from!==SUBJECT)continue;
    const ts=Date.parse(m.ts||'');if(!Number.isFinite(ts)||ts>=CUTOFF)continue;
    evidence.push({room,seq:Number(m.seq||0)||null,ts:m.ts||null,signature_verified:verify(m,room),text_sha256:typeof m.text==='string'?crypto.createHash('sha256').update(m.text).digest('hex'):null,text_preview:typeof m.text==='string'?m.text.slice(0,240):null});
  }
}
const verified=evidence.filter(x=>x.signature_verified);
const out={checked_at:new Date().toISOString(),failed_rooms_from_initial_scan:[...roomNames],recovered_rooms:recovered,still_failed_rooms:errors,verified_prestart_evidence_count:verified.length,verified_prestart_evidence:verified,unverified_prestart_candidates:evidence.filter(x=>!x.signature_verified),technocore_write_count:0};
fs.writeFileSync(OUT,JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out,null,2));
