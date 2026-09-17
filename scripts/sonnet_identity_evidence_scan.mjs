#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const SUBJECT='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const CUTOFF=Date.parse('2026-09-11T12:00:00.000Z');
const OUT='data/sonnet_identity_evidence_scan.json';
const B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const IDX=new Map([...B58].map((c,i)=>[c,i]));

function b58decode(raw){let n=0n;for(const ch of raw){const d=IDX.get(ch);if(d==null)throw new Error('bad base58');n=n*58n+BigInt(d)}let hex=n.toString(16);if(hex.length%2)hex='0'+hex;let body=hex?Buffer.from(hex,'hex'):Buffer.alloc(0);const lead=raw.length-raw.replace(/^1+/,'').length;if(lead)body=Buffer.concat([Buffer.alloc(lead),body]);return body}
function pub(did){const d=b58decode(did.slice('did:key:z'.length));if(d.length!==34||d[0]!==0xed||d[1]!==0x01)throw new Error('not ed25519');return crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),d.subarray(2)]),format:'der',type:'spki'})}
const PUB=pub(SUBJECT);
function verify(m,room){try{return m?.from===SUBJECT&&m.nonce!=null&&typeof m.text==='string'&&!!m.sig&&crypto.verify(null,Buffer.from(`${room}|${m.nonce}|${m.text}`,'utf8'),PUB,Buffer.from(m.sig,'base64url'))}catch{return false}}
function J(s){try{return JSON.parse(s)}catch{return null}}
function sleep(ms){return new Promise(r=>setTimeout(r,ms))}
async function getText(url,ms=25000){const c=new AbortController(),t=setTimeout(()=>c.abort(),ms);try{const r=await fetch(url,{headers:{'user-agent':'raindog-sonnet-evidence-scan/1.1','cache-control':'no-cache'},signal:c.signal});if(!r.ok)throw new Error(`HTTP ${r.status}`);return await r.text()}finally{clearTimeout(t)}}

function roomListFromJson(x){
  const out=new Set();
  const visit=v=>{
    if(!v)return;
    if(Array.isArray(v)){for(const z of v)visit(z);return}
    if(typeof v!=='object')return;
    for(const k of ['room','name','room_name','slug'])if(typeof v[k]==='string'&&/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(v[k]))out.add(v[k]);
    for(const z of Object.values(v))if(z&&typeof z==='object')visit(z);
  };
  visit(x);return out;
}
function addRoomTokens(text,set){
  if(typeof text!=='string')return;
  for(const m of text.matchAll(/\b[A-Za-z0-9][A-Za-z0-9._-]{1,127}\b/g)){
    const s=m[0];
    if(s==='events'||s.startsWith('did')||/^\d+$/.test(s))continue;
    if(s.includes('-')||s.includes('_')||/^(lobby|general|help|registration|discovery|campaign|votes|submissions|results|rules)$/i.test(s))set.add(s);
  }
}

const rooms=new Set();
const errors=[];
try{
  const raw=await getText(`https://technocore.chat/rooms?format=json&limit=500&n=${Date.now()}`,30000);
  const x=J(raw);
  if(x)for(const r of roomListFromJson(x))rooms.add(r);
}catch(e){errors.push(`rooms:${e?.name||'Error'}:${e?.message||String(e)}`)}

// Enumerate the server-written public room event lane as a second source.
try{
  let cursor=0;
  for(let page=0;page<20;page++){
    const raw=await getText(`https://technocore.chat/r/events?format=json&since=${cursor}&limit=200&n=${Date.now()}-${page}`,25000);
    const x=J(raw);
    if(!x)break;
    const msgs=Array.isArray(x.messages)?x.messages:[];
    for(const m of msgs){addRoomTokens(m?.text,rooms);if(typeof m?.room==='string')rooms.add(m.room)}
    const last=Number(x.last_seq||cursor);
    if(last<=cursor||msgs.length===0)break;
    cursor=last;
    if(msgs.length<200)break;
    await sleep(100);
  }
}catch(e){errors.push(`events:${e?.name||'Error'}:${e?.message||String(e)}`)}

// Ensure all contest rooms already known locally are included even if discovery APIs change.
for(const f of ['data/sonnet_discovery_subject_watch.json','data/sonnet_candidate_live.json']){
  try{
    const txt=fs.readFileSync(f,'utf8');
    for(const m of txt.matchAll(/(?:mb|d)-[A-Za-z0-9._-]+/g))rooms.add(m[0]);
  }catch{}
}

const evidence=[];
const scanned=[];
const list=[...rooms].filter(r=>r&&r!=='events').slice(0,550);
let next=0;
const workers=Math.min(4,Math.max(1,list.length));
async function worker(){
  while(true){
    const i=next++;if(i>=list.length)return;
    const room=list[i];
    try{
      const raw=await getText(`https://technocore.chat/r/${encodeURIComponent(room)}/export?n=${Date.now()}-${i}`,30000);
      scanned.push(room);
      if(!raw.includes(SUBJECT)){await sleep(100);continue}
      for(const line of raw.split(/\r?\n/).filter(Boolean)){
        const m=J(line);if(!m||m.from!==SUBJECT)continue;
        const ts=Date.parse(m.ts||'');if(!Number.isFinite(ts)||ts>=CUTOFF)continue;
        const ok=verify(m,room);
        evidence.push({room,seq:Number(m.seq||0)||null,ts:m.ts||null,nonce:m.nonce??null,signature_verified:ok,text_sha256:typeof m.text==='string'?crypto.createHash('sha256').update(m.text).digest('hex'):null,text_preview:typeof m.text==='string'?m.text.slice(0,240):null});
      }
    }catch(e){errors.push(`${room}:${e?.name||'Error'}:${e?.message||String(e)}`)}
    await sleep(100);
  }
}
await Promise.all(Array.from({length:workers},()=>worker()));
evidence.sort((a,b)=>String(a.ts).localeCompare(String(b.ts)));
const verified=evidence.filter(x=>x.signature_verified);
const out={checked_at:new Date().toISOString(),subject_did:SUBJECT,cutoff_utc:new Date(CUTOFF).toISOString(),rooms_discovered:list.length,rooms_scanned:scanned.length,verified_prestart_evidence_count:verified.length,verified_prestart_evidence:verified,unverified_prestart_candidates:evidence.filter(x=>!x.signature_verified),errors:errors.slice(-50),technocore_write_count:0};
fs.mkdirSync('data',{recursive:true});
fs.writeFileSync(OUT,JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out,null,2));
