#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const ROOM='mb-sonnet-2-discovery';
const REFEREE_DID='did:key:z6MkowHQwsx9xr84WbWN3YCnKutyBnBXkT1ChKY4uEAAMzte';
const SUBJECT_DID='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const OUT='data/sonnet_discovery_snapshot.json';
const B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const IDX=new Map([...B58].map((c,i)=>[c,i]));

function b58decode(raw){let n=0n;for(const ch of raw){const d=IDX.get(ch);if(d==null)throw new Error('bad base58');n=n*58n+BigInt(d)}let hex=n.toString(16);if(hex.length%2)hex='0'+hex;let body=hex?Buffer.from(hex,'hex'):Buffer.alloc(0);const lead=raw.length-raw.replace(/^1+/,'').length;if(lead)body=Buffer.concat([Buffer.alloc(lead),body]);return body}
function pub(did){const d=b58decode(did.slice('did:key:z'.length));if(d.length!==34||d[0]!==0xed||d[1]!==0x01)throw new Error('not ed25519');return crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),d.subarray(2)]),format:'der',type:'spki'})}
function verify(m,did,room=ROOM){try{return !!m&&m.from===did&&m.nonce!=null&&typeof m.text==='string'&&!!m.sig&&crypto.verify(null,Buffer.from(`${room}|${m.nonce}|${m.text}`,'utf8'),pub(did),Buffer.from(m.sig,'base64url'))}catch{return false}}
function parseJson(s){try{return JSON.parse(s)}catch{return null}}
function deep(o,keys){if(!o||typeof o!=='object')return null;for(const k of keys)if(o[k]!=null)return o[k];for(const v of Object.values(o)){if(v&&typeof v==='object'){const x=deep(v,keys);if(x!=null)return x}}return null}
async function getText(url,ms=25000){const c=new AbortController(),t=setTimeout(()=>c.abort(),ms);try{const r=await fetch(url,{headers:{'user-agent':'raindog-sonnet-discovery/1.0','cache-control':'no-cache'},signal:c.signal});if(!r.ok)throw new Error(`HTTP ${r.status}`);return await r.text()}finally{clearTimeout(t)}}
async function getJson(url,ms=25000){return JSON.parse(await getText(url,ms))}

const state={schema_version:1,checked_at:new Date().toISOString(),room:ROOM,subject_did:SUBJECT_DID,referee_did:REFEREE_DID,technocore_write_count:0,export_scanned:false,rooms_scanned:false,message_count:0,protocol_messages:[],referee_receipts:[],team_requests:[],rosters:[],withdrawals:[],recruitment_signals:[],team_rooms:[],candidate_teams:[],errors:[]};
let messages=[];
try{
  const raw=await getText(`https://technocore.chat/r/${ROOM}/export?n=${Date.now()}`,30000);
  state.export_scanned=true;
  messages=raw.split(/\r?\n/).filter(Boolean).map(parseJson).filter(Boolean);
}catch(e){state.errors.push(`discovery_export:${e?.name||'Error'}:${e?.message||String(e)}`)}
state.message_count=messages.length;

const teams=new Map();
function team(game){if(!teams.has(game))teams.set(game,{game_id:game,requesters:new Set(),member_dids:new Set(),roster_sizes:[],poem_rooms:new Set(),latest_seq:0,latest_ts:null,referee_receipts:[],recruitment_signals:[],withdrawals:0});return teams.get(game)}

for(const m of messages){
  const seq=Number(m.seq||0)||0, ts=m.ts||null;
  const p=parseJson(m.text);
  if(p && typeof p.type==='string' && p.type.startsWith('sonnet.')){
    state.protocol_messages.push({seq,ts,from:m.from||null,type:p.type,game_id:p.game_id??deep(p,['game_id'])??null,request_id:p.request_id??deep(p,['request_id'])??null,signed:!!m.sig});
    if(p.type==='sonnet.team-request.v1'){
      const g=String(p.game_id||''); if(g){const t=team(g);t.requesters.add(m.from||'');t.latest_seq=Math.max(t.latest_seq,seq);t.latest_ts=ts||t.latest_ts;state.team_requests.push({seq,ts,from:m.from||null,game_id:g,request_id:p.request_id||null});}
    } else if(p.type==='sonnet.roster.v1'){
      const g=String(p.game_id||''); if(g){const t=team(g);const members=Array.isArray(p.members)?p.members.map(String):[];for(const d of members)t.member_dids.add(d);t.roster_sizes.push(members.length);if(p.poem_room)t.poem_rooms.add(String(p.poem_room));t.latest_seq=Math.max(t.latest_seq,seq);t.latest_ts=ts||t.latest_ts;state.rosters.push({seq,ts,from:m.from||null,game_id:g,poem_room:p.poem_room||null,room_generation:p.room_generation??null,members,request_id:p.request_id||null});}
    } else if(p.type==='sonnet.withdraw.v1'){
      const g=String(p.game_id||''); if(g){const t=team(g);t.withdrawals++;t.latest_seq=Math.max(t.latest_seq,seq);t.latest_ts=ts||t.latest_ts;state.withdrawals.push({seq,ts,from:m.from||null,game_id:g,request_id:p.request_id||null});}
    }
  }

  if(m.from===REFEREE_DID && verify(m,REFEREE_DID)){
    const rp=parseJson(m.text);
    if(rp?.type==='sonnet.receipt.v1'){
      const g=String(deep(rp,['game_id'])||'');
      const rec={seq,ts,decision:String(deep(rp,['decision','status'])||'unknown').toUpperCase(),reason:deep(rp,['reason','reason_code','error'])??null,request_id:deep(rp,['request_id'])??null,game_id:g||null,signature_verified:true};
      state.referee_receipts.push(rec);
      if(g){const t=team(g);t.referee_receipts.push(rec);t.latest_seq=Math.max(t.latest_seq,seq);t.latest_ts=ts||t.latest_ts;}
    }
  }

  if(!p && typeof m.text==='string'){
    const txt=m.text.replace(/\s+/g,' ').trim();
    if(/writer|team|join|roster|recruit|member|slot|need|looking/i.test(txt)){
      const clipped=txt.slice(0,240);
      state.recruitment_signals.push({seq,ts,from:m.from||null,text:clipped,signed:!!m.sig});
    }
  }
}

try{
  const rooms=await getJson(`https://technocore.chat/rooms?format=json&limit=500&n=${Date.now()}`,30000);
  state.rooms_scanned=true;
  const list=Array.isArray(rooms)?rooms:(Array.isArray(rooms.rooms)?rooms.rooms:[]);
  for(const r of list){const name=String(r.room||r.name||'');if(!name.startsWith('d-sonnet-2-team-'))continue;const g=name.slice('d-sonnet-2-team-'.length);state.team_rooms.push({room:name,game_id:g,last_seq:r.last_seq??null,size:r.size??null,idle:r.idle??r.idle_seconds??null,topic:typeof r.topic==='string'?r.topic.slice(0,180):null});const t=team(g);t.poem_rooms.add(name);}
}catch(e){state.errors.push(`rooms:${e?.name||'Error'}:${e?.message||String(e)}`)}

for(const s of state.recruitment_signals){
  for(const [g,t] of teams){if(s.text.toLowerCase().includes(g.toLowerCase()))t.recruitment_signals.push(s)}
}

const candidates=[];
for(const [g,t] of teams){
  const maxRoster=t.roster_sizes.length?Math.max(...t.roster_sizes):0;
  const accepted=t.referee_receipts.filter(r=>r.decision==='ACCEPTED').length;
  const refused=t.referee_receipts.filter(r=>r.decision==='REFUSED'||r.decision==='REJECTED').length;
  const hasRoom=t.poem_rooms.size>0;
  const score=(hasRoom?4:0)+(accepted?3:0)+(t.recruitment_signals.length?3:0)+(maxRoster>0&&maxRoster<8?2:0)-(maxRoster>=8?5:0)-(refused?1:0)-(t.withdrawals?1:0);
  candidates.push({game_id:g,score,poem_rooms:[...t.poem_rooms],requesters:[...t.requesters].filter(Boolean),known_member_dids:[...t.member_dids],max_observed_roster_size:maxRoster,accepted_referee_receipts:accepted,refused_referee_receipts:refused,withdrawals:t.withdrawals,recruitment_signals:t.recruitment_signals.slice(-3),latest_seq:t.latest_seq,latest_ts:t.latest_ts});
}
candidates.sort((a,b)=>b.score-a.score||b.latest_seq-a.latest_seq);
state.candidate_teams=candidates.slice(0,10);
state.summary={teams_observed:teams.size,team_rooms_observed:state.team_rooms.length,protocol_messages:state.protocol_messages.length,referee_receipts:state.referee_receipts.length,recruitment_signals:state.recruitment_signals.length,top_candidates:state.candidate_teams.slice(0,3).map(x=>({game_id:x.game_id,score:x.score,max_roster:x.max_observed_roster_size,rooms:x.poem_rooms,latest_ts:x.latest_ts}))};

fs.mkdirSync('data',{recursive:true});
fs.writeFileSync(OUT,JSON.stringify(state,null,2)+'\n');
console.log(JSON.stringify(state.summary,null,2));
