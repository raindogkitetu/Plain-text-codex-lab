#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const ROOM='mb-sonnet-2-discovery';
const SUBJECT='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const REFEREE='did:key:z6MkowHQwsx9xr84WbWN3YCnKutyBnBXkT1ChKY4uEAAMzte';
const TEAM='keepers-of-flame';
const OUT='data/sonnet_discovery_subject_watch.json';
const B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const IDX=new Map([...B58].map((c,i)=>[c,i]));
function b58decode(raw){let n=0n;for(const ch of raw){const d=IDX.get(ch);if(d==null)throw new Error('bad base58');n=n*58n+BigInt(d)}let hex=n.toString(16);if(hex.length%2)hex='0'+hex;let body=hex?Buffer.from(hex,'hex'):Buffer.alloc(0);const lead=raw.length-raw.replace(/^1+/,'').length;if(lead)body=Buffer.concat([Buffer.alloc(lead),body]);return body}
function pub(did){const d=b58decode(did.slice('did:key:z'.length));if(d.length!==34||d[0]!==0xed||d[1]!==0x01)throw new Error('not ed25519');return crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),d.subarray(2)]),format:'der',type:'spki'})}
function verify(m,did){try{return m?.from===did&&m.nonce!=null&&typeof m.text==='string'&&!!m.sig&&crypto.verify(null,Buffer.from(`${ROOM}|${m.nonce}|${m.text}`,'utf8'),pub(did),Buffer.from(m.sig,'base64url'))}catch{return false}}
function J(s){try{return JSON.parse(s)}catch{return null}}
async function getText(url,ms=30000){const c=new AbortController(),t=setTimeout(()=>c.abort(),ms);try{const r=await fetch(url,{headers:{'user-agent':'raindog-sonnet-discovery-subject-watch/1.0','cache-control':'no-cache'},signal:c.signal});if(!r.ok)throw new Error(`HTTP ${r.status}`);return await r.text()}finally{clearTimeout(t)}}

const state={schema_version:1,checked_at:new Date().toISOString(),room:ROOM,subject_did:SUBJECT,referee_did:REFEREE,team:TEAM,technocore_write_count:0,read_ok:false,message_count:0,last_seq:null,subject_messages:[],team_mentions:[],subject_mentions:[],errors:[]};
try{
  const raw=await getText(`https://technocore.chat/r/${ROOM}/export?n=${Date.now()}`);
  const msgs=raw.split(/\r?\n/).filter(Boolean).map(J).filter(Boolean);
  state.read_ok=true; state.message_count=msgs.length;
  for(const m of msgs){
    const seq=Number(m.seq||0)||0;if(seq>(state.last_seq||0))state.last_seq=seq;
    const text=typeof m.text==='string'?m.text:'';
    if(m.from===SUBJECT){state.subject_messages.push({seq,ts:m.ts||null,signature_verified:verify(m,SUBJECT),text:text.slice(0,700)});}
    if(text.toLowerCase().includes(TEAM)) state.team_mentions.push({seq,ts:m.ts||null,from:m.from||null,signed:!!m.sig,referee_signature_verified:m.from===REFEREE?verify(m,REFEREE):false,text:text.slice(0,700)});
    if(text.includes(SUBJECT) && m.from!==SUBJECT) state.subject_mentions.push({seq,ts:m.ts||null,from:m.from||null,signed:!!m.sig,referee_signature_verified:m.from===REFEREE?verify(m,REFEREE):false,text:text.slice(0,700)});
  }
  state.subject_messages=state.subject_messages.slice(-10);
  state.team_mentions=state.team_mentions.slice(-30);
  state.subject_mentions=state.subject_mentions.slice(-30);
}catch(e){state.errors.push(`${e?.name||'Error'}:${e?.message||String(e)}`)}
fs.mkdirSync('data',{recursive:true});
fs.writeFileSync(OUT,JSON.stringify(state,null,2)+'\n');
console.log(JSON.stringify({checked_at:state.checked_at,read_ok:state.read_ok,last_seq:state.last_seq,subject_messages:state.subject_messages.length,latest_subject:state.subject_messages.at(-1)||null,team_mentions:state.team_mentions.length,subject_mentions:state.subject_mentions.length,errors:state.errors},null,2));
