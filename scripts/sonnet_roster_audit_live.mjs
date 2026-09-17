#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const SUBJECT='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const REF='did:key:z6MkowHQwsx9xr84WbWN3YCnKutyBnBXkT1ChKY4uEAAMzte';
const STATE='data/sonnet_discovery_subject_watch.json';
const OUT='data/sonnet_roster_audit_live.json';
const B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const IDX=new Map([...B58].map((c,i)=>[c,i]));

function b58decode(raw){let n=0n;for(const ch of raw){const d=IDX.get(ch);if(d==null)throw new Error('bad base58');n=n*58n+BigInt(d)}let hex=n.toString(16);if(hex.length%2)hex='0'+hex;let body=hex?Buffer.from(hex,'hex'):Buffer.alloc(0);const lead=raw.length-raw.replace(/^1+/,'').length;if(lead)body=Buffer.concat([Buffer.alloc(lead),body]);return body}
function pub(did){const d=b58decode(did.slice('did:key:z'.length));if(d.length!==34||d[0]!==0xed||d[1]!==0x01)throw new Error('not ed25519');return crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),d.subarray(2)]),format:'der',type:'spki'})}
function verify(m,did,room){try{return !!m&&m.from===did&&m.nonce!=null&&typeof m.text==='string'&&!!m.sig&&crypto.verify(null,Buffer.from(`${room}|${m.nonce}|${m.text}`,'utf8'),pub(did),Buffer.from(m.sig,'base64url'))}catch{return false}}
function J(s){try{return JSON.parse(s)}catch{return null}}
function deep(o,keys){if(!o||typeof o!=='object')return null;for(const k of keys)if(o[k]!=null)return o[k];for(const v of Object.values(o)){if(v&&typeof v==='object'){const x=deep(v,keys);if(x!=null)return x}}return null}
function rosterValid(p){return !!p&&p.type==='sonnet.roster.v1'&&p.contest_id==='sonnet-2'&&typeof p.game_id==='string'&&p.poem_room===`d-sonnet-2-team-${p.game_id}`&&Number.isInteger(p.room_generation)&&p.room_generation>=0&&Array.isArray(p.members)&&p.members.length>=4&&p.members.length<=8&&new Set(p.members).size===p.members.length&&p.members.includes(SUBJECT)}
async function getText(url,ms=30000){const c=new AbortController(),t=setTimeout(()=>c.abort(),ms);try{const r=await fetch(url,{headers:{'user-agent':'raindog-sonnet-roster-audit/1.0','cache-control':'no-cache'},signal:c.signal});if(!r.ok)throw new Error(`HTTP ${r.status}`);return await r.text()}finally{clearTimeout(t)}}

const state=JSON.parse(fs.readFileSync(STATE,'utf8'));
const directs=Array.isArray(state.direct_roster_or_invite)?state.direct_roster_or_invite:[];
const parsed=[];
for(const m of directs){const p=J(m?.text);if(!p||p.type!=='sonnet.roster.v1'||!p.members?.includes?.(SUBJECT))continue;parsed.push({seq:Number(m.seq||0)||null,ts:m.ts||null,from:m.from||null,signed:!!m.signed,payload:p})}

const dedup=new Map();
for(const x of parsed){const k=`${x.payload.game_id}|${x.payload.request_id||''}|${x.payload.room_generation}`;const old=dedup.get(k);if(!old||(x.seq||0)>(old.seq||0))dedup.set(k,x)}

const results=[];
for(const x of dedup.values()){
  const p=x.payload;const room=p.poem_room;const r={game_id:p.game_id,poem_room:room,room_generation:p.room_generation,request_id:p.request_id||null,members:p.members,member_count:p.members.length,contains_subject:p.members.includes(SUBJECT),payload_valid:rosterValid(p),invite_seq:x.seq,invite_ts:x.ts,invite_from:x.from,invite_signed:x.signed,room_read_ok:false,room_errors:[],word_posts:0,subject_word_posts:0,subject_exact_roster_posts:0,verified_referee_receipts:[],matching_referee_receipt:null,last_seq:null,last_ts:null};
  try{
    const raw=await getText(`https://technocore.chat/r/${room}/export?n=${Date.now()}-${encodeURIComponent(p.game_id)}`);
    const msgs=raw.split(/\r?\n/).filter(Boolean).map(J).filter(Boolean);r.room_read_ok=true;
    const exact=JSON.stringify(p);
    for(const m of msgs){const seq=Number(m.seq||0)||0;if(seq>(r.last_seq||0)){r.last_seq=seq;r.last_ts=m.ts||r.last_ts}const q=J(m.text);
      if(q?.type==='sonnet.word.v1'){r.word_posts++;if(m.from===SUBJECT)r.subject_word_posts++}
      if(m.from===SUBJECT&&q?.type==='sonnet.roster.v1'&&JSON.stringify(q)===exact)r.subject_exact_roster_posts++;
      if(verify(m,REF,room)&&q?.type==='sonnet.receipt.v1'){
        const decision=String(deep(q,['decision','status'])||'unknown').toUpperCase();
        const req=String(deep(q,['request_id'])||'');
        const rec={seq,ts:m.ts||null,decision,request_id:req||null,reason:deep(q,['reason','reason_code','error'])??null,action_type:deep(q,['action_type','request_type','accepted_type'])??null,signature_verified:true};
        r.verified_referee_receipts.push(rec);
        if(req&&p.request_id&&req===String(p.request_id))r.matching_referee_receipt=rec;
      }
    }
  }catch(e){r.room_errors.push(`${e?.name||'Error'}:${e?.message||String(e)}`)}
  r.score=(r.payload_valid?20:0)+(r.room_read_ok?10:0)+(r.matching_referee_receipt?.decision==='ACCEPTED'?50:0)+(r.word_posts===0?10:0)+(r.subject_exact_roster_posts>0?5:0)-r.room_errors.length*20;
  results.push(r);
}
results.sort((a,b)=>b.score-a.score||String(b.invite_ts||'').localeCompare(String(a.invite_ts||'')));
const out={checked_at:new Date().toISOString(),subject_did:SUBJECT,source_checked_at:state.checked_at||null,direct_roster_count:directs.length,unique_rosters:results.length,best:results[0]||null,candidates:results,technocore_write_count:0};
fs.writeFileSync(OUT,JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out,null,2));
