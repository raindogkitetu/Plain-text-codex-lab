#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const DISC='mb-sonnet-2-discovery';
const REF='did:key:z6MkowHQwsx9xr84WbWN3YCnKutyBnBXkT1ChKY4uEAAMzte';
const SUBJECT='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const OUT='data/sonnet_candidate_live.json';
const SEEDS=['keepers-of-flame','nathbabu','openclaw1','forumevi-poets','teamwinner'];
const B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const IDX=new Map([...B58].map((c,i)=>[c,i]));
function b58decode(raw){let n=0n;for(const ch of raw){const d=IDX.get(ch);if(d==null)throw new Error('bad base58');n=n*58n+BigInt(d)}let hex=n.toString(16);if(hex.length%2)hex='0'+hex;let body=hex?Buffer.from(hex,'hex'):Buffer.alloc(0);const lead=raw.length-raw.replace(/^1+/,'').length;if(lead)body=Buffer.concat([Buffer.alloc(lead),body]);return body}
function pub(did){const d=b58decode(did.slice('did:key:z'.length));return crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),d.subarray(2)]),format:'der',type:'spki'})}
function verify(m,room){try{return m?.from===REF&&m.nonce!=null&&typeof m.text==='string'&&!!m.sig&&crypto.verify(null,Buffer.from(`${room}|${m.nonce}|${m.text}`,'utf8'),pub(REF),Buffer.from(m.sig,'base64url'))}catch{return false}}
function J(s){try{return JSON.parse(s)}catch{return null}}
function deep(o,keys){if(!o||typeof o!=='object')return null;for(const k of keys)if(o[k]!=null)return o[k];for(const v of Object.values(o)){if(v&&typeof v==='object'){const x=deep(v,keys);if(x!=null)return x}}return null}
async function getJson(url,ms=18000){const c=new AbortController(),t=setTimeout(()=>c.abort(),ms);try{const r=await fetch(url,{headers:{'user-agent':'raindog-sonnet-candidate-live/1.0','cache-control':'no-cache'},signal:c.signal});if(!r.ok)throw new Error(`HTTP ${r.status}`);return await r.json()}finally{clearTimeout(t)}}

const now=Date.now();
const out={schema_version:1,checked_at:new Date().toISOString(),subject_did:SUBJECT,referee_did:REF,technocore_write_count:0,candidates:[],errors:[]};
let disc=[];
try{const v=await getJson(`https://technocore.chat/r/${DISC}?format=json&limit=200&n=${now}`);disc=Array.isArray(v.messages)?v.messages:[]}catch(e){out.errors.push(`discovery:${e?.name||'Error'}:${e?.message||String(e)}`)}
const ids=new Set(SEEDS);
const signals=[];
for(const m of disc){
  const text=typeof m.text==='string'?m.text:'';const p=J(text);let g=p?.game_id?String(p.game_id).toLowerCase():null;
  if(!g){const mm=text.match(/game_id[\s"':=]+([a-z0-9][a-z0-9_-]{0,15})/i);if(mm)g=mm[1].toLowerCase()}
  if(g)ids.add(g);
  if(g&&/writer|roster|seat|slot|join|recruit|member|available|open/i.test(text))signals.push({game_id:g,seq:Number(m.seq||0)||null,ts:m.ts||null,from:m.from||null,target_did:p?.target_did||null,text:text.slice(0,900)});
}

for(const game_id of [...ids].slice(0,20)){
  const room=`d-sonnet-2-team-${game_id}`;
  const c={game_id,room,read_ok:false,setup_accepted:false,word_posts:0,last_seq:null,last_ts:null,recruitment_signals:signals.filter(s=>s.game_id===game_id).slice(-5),direct_to_subject:false,score:0,errors:[]};
  c.direct_to_subject=c.recruitment_signals.some(s=>s.target_did===SUBJECT||s.text.includes(SUBJECT));
  try{
    const v=await getJson(`https://technocore.chat/r/${room}?format=json&limit=200&n=${Date.now()}`);
    c.read_ok=true;c.last_seq=v.last_seq??null;
    const msgs=Array.isArray(v.messages)?v.messages:[];
    for(const m of msgs){c.last_ts=m.ts||c.last_ts;const p=J(m.text);if(p?.type==='sonnet.word.v1')c.word_posts++;if(m.from===REF&&verify(m,room)&&p?.type==='sonnet.receipt.v1'){const dec=String(deep(p,['decision','status'])||'').toUpperCase();const req=String(deep(p,['request_id'])||'');if(dec==='ACCEPTED'&&(/setup|room/i.test(req)||deep(p,['room_generation'])!=null))c.setup_accepted=true;}}
  }catch(e){c.errors.push(`${e?.name||'Error'}:${e?.message||String(e)}`)}
  const latestSig=c.recruitment_signals.at(-1)||null;
  const ageMin=latestSig?.ts?Math.max(0,(now-Date.parse(latestSig.ts))/60000):9999;
  c.score=(c.setup_accepted?5:0)+(c.word_posts===0?3:-Math.min(c.word_posts,3))+(c.recruitment_signals.length?3:0)+(ageMin<=60?3:ageMin<=180?1:0)+(c.direct_to_subject?5:0);
  c.latest_recruitment=latestSig;
  out.candidates.push(c);
}
out.candidates.sort((a,b)=>b.score-a.score||((Date.parse(b.latest_recruitment?.ts||0)||0)-(Date.parse(a.latest_recruitment?.ts||0)||0)));
out.candidates=out.candidates.slice(0,8);
out.top3=out.candidates.slice(0,3).map(c=>({game_id:c.game_id,score:c.score,setup_accepted:c.setup_accepted,word_posts:c.word_posts,direct_to_subject:c.direct_to_subject,latest_recruitment:c.latest_recruitment}));
fs.mkdirSync('data',{recursive:true});fs.writeFileSync(OUT,JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({checked_at:out.checked_at,top3:out.top3,errors:out.errors},null,2));
