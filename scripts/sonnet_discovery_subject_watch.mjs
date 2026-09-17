#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const ROOM='mb-sonnet-2-discovery';
const SUBJECT='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const REFEREE='did:key:z6MkowHQwsx9xr84WbWN3YCnKutyBnBXkT1ChKY4uEAAMzte';
const TEAMS=['keepers-of-flame','nathbabu','openclaw1','forumevi-poets','teamwinner'];
const POSTED_SEQ=132195;
const POSTED_TS='2026-09-17T11:35:58.051429Z';
const WATCH_MS=4*60*1000+15*1000;
const OUT='data/sonnet_discovery_subject_watch.json';
const B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const IDX=new Map([...B58].map((c,i)=>[c,i]));

function load(){try{return JSON.parse(fs.readFileSync(OUT,'utf8'))}catch{return {}}}
function b58decode(raw){let n=0n;for(const ch of raw){const d=IDX.get(ch);if(d==null)throw new Error('bad base58');n=n*58n+BigInt(d)}let hex=n.toString(16);if(hex.length%2)hex='0'+hex;let body=hex?Buffer.from(hex,'hex'):Buffer.alloc(0);const lead=raw.length-raw.replace(/^1+/,'').length;if(lead)body=Buffer.concat([Buffer.alloc(lead),body]);return body}
function pub(did){const d=b58decode(did.slice('did:key:z'.length));if(d.length!==34||d[0]!==0xed||d[1]!==0x01)throw new Error('not ed25519');return crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),d.subarray(2)]),format:'der',type:'spki'})}
function verify(m,did){try{return m?.from===did&&m.nonce!=null&&typeof m.text==='string'&&!!m.sig&&crypto.verify(null,Buffer.from(`${ROOM}|${m.nonce}|${m.text}`,'utf8'),pub(did),Buffer.from(m.sig,'base64url'))}catch{return false}}
function J(s){try{return JSON.parse(s)}catch{return null}}
function uniqBySeq(items,max=60){const m=new Map();for(const x of items||[]){const k=Number(x?.seq||0);if(k)m.set(k,x)}return [...m.values()].sort((a,b)=>a.seq-b.seq).slice(-max)}
async function getJson(url,ms=18000){const c=new AbortController(),t=setTimeout(()=>c.abort(),ms);try{const r=await fetch(url,{headers:{'user-agent':'raindog-sonnet-discovery-subject-watch/2.0','cache-control':'no-cache'},signal:c.signal});if(!r.ok)throw new Error(`HTTP ${r.status}`);return await r.json()}finally{clearTimeout(t)}}

const old=load();
let cursor=Math.max(Number(old.last_seq||0),POSTED_SEQ);
const started=Date.now();
const state={
  schema_version:2,
  checked_at:new Date().toISOString(),
  room:ROOM,
  subject_did:SUBJECT,
  referee_did:REFEREE,
  watched_teams:TEAMS,
  technocore_write_count:0,
  posted_evidence:{seq:POSTED_SEQ,ts:POSTED_TS,signature_verified:true},
  read_ok:false,
  last_seq:cursor,
  subject_mentions:Array.isArray(old.subject_mentions)?old.subject_mentions:[],
  team_mentions:Array.isArray(old.team_mentions)?old.team_mentions:[],
  direct_roster_or_invite:Array.isArray(old.direct_roster_or_invite)?old.direct_roster_or_invite:[],
  coverage_gaps:Array.isArray(old.coverage_gaps)?old.coverage_gaps:[],
  errors:[]
};

while(Date.now()-started<WATCH_MS){
  try{
    const v=await getJson(`https://technocore.chat/r/${ROOM}?format=json&since=${cursor}&limit=200&wait=10&n=${Date.now()}`);
    state.read_ok=true;
    const first=v.first_seq==null?null:Number(v.first_seq);
    const last=Number(v.last_seq||cursor);
    if(first!=null&&first>cursor+1){
      state.coverage_gaps.push({from_cursor:cursor,first_retained_seq:first,observed_at:new Date().toISOString()});
      cursor=first-1;
      continue;
    }
    for(const m of Array.isArray(v.messages)?v.messages:[]){
      const seq=Number(m.seq||0)||0;
      const text=typeof m.text==='string'?m.text:'';
      const lower=text.toLowerCase();
      const p=J(text);
      if(m.from!==SUBJECT && text.includes(SUBJECT)){
        state.subject_mentions.push({seq,ts:m.ts||null,from:m.from||null,signed:!!m.sig,referee_signature_verified:m.from===REFEREE?verify(m,REFEREE):false,text:text.slice(0,1200)});
      }
      const team=TEAMS.find(t=>lower.includes(t));
      if(team){
        state.team_mentions.push({seq,ts:m.ts||null,team,from:m.from||null,signed:!!m.sig,referee_signature_verified:m.from===REFEREE?verify(m,REFEREE):false,text:text.slice(0,1200)});
      }
      const target=p&&typeof p==='object'?(p.target_did||p.participant_did||p.writer_did||null):null;
      const type=p&&typeof p.type==='string'?p.type:null;
      if(m.from!==SUBJECT && (target===SUBJECT || text.includes(SUBJECT)) && (type==='sonnet.note.v1'||type==='sonnet.roster.v1'||/invite|roster|seat|join/i.test(text))){
        state.direct_roster_or_invite.push({seq,ts:m.ts||null,from:m.from||null,type,target_did:target,signed:!!m.sig,referee_signature_verified:m.from===REFEREE?verify(m,REFEREE):false,text:text.slice(0,1600)});
      }
      if(seq>cursor)cursor=seq;
    }
    if(last>cursor)cursor=last;
  }catch(e){
    state.errors.push(`${new Date().toISOString()}:${e?.name||'Error'}:${e?.message||String(e)}`);
    await new Promise(r=>setTimeout(r,1200));
  }
  if(state.errors.length>20)state.errors=state.errors.slice(-20);
}

state.last_seq=cursor;
state.checked_at=new Date().toISOString();
state.subject_mentions=uniqBySeq(state.subject_mentions,60);
state.team_mentions=uniqBySeq(state.team_mentions,100);
state.direct_roster_or_invite=uniqBySeq(state.direct_roster_or_invite,60);
state.coverage_gaps=(state.coverage_gaps||[]).slice(-30);
state.latest_subject_mention=state.subject_mentions.at(-1)||null;
state.latest_direct_roster_or_invite=state.direct_roster_or_invite.at(-1)||null;
fs.mkdirSync('data',{recursive:true});
fs.writeFileSync(OUT,JSON.stringify(state,null,2)+'\n');
console.log(JSON.stringify({checked_at:state.checked_at,read_ok:state.read_ok,last_seq:state.last_seq,subject_mentions:state.subject_mentions.length,direct_roster_or_invite:state.direct_roster_or_invite.length,latest_subject_mention:state.latest_subject_mention,latest_direct_roster_or_invite:state.latest_direct_roster_or_invite,coverage_gaps:state.coverage_gaps.length,errors:state.errors},null,2));
