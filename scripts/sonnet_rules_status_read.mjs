#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';
const ROOM='d-sonnet-2-rules';
const REF='did:key:z6MkowHQwsx9xr84WbWN3YCnKutyBnBXkT1ChKY4uEAAMzte';
const DID='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const REQ='register-raindog-writer-acf7b45a0344e497';
const OUT='data/sonnet_rules_status_read.json';
const B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const IDX=new Map([...B58].map((c,i)=>[c,i]));
function b58(raw){let n=0n;for(const ch of raw){const d=IDX.get(ch);if(d==null)throw Error('b58');n=n*58n+BigInt(d)}let h=n.toString(16);if(h.length%2)h='0'+h;let b=h?Buffer.from(h,'hex'):Buffer.alloc(0);const l=raw.length-raw.replace(/^1+/,'').length;if(l)b=Buffer.concat([Buffer.alloc(l),b]);return b}
function pub(did){const d=b58(did.slice('did:key:z'.length));return crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),d.subarray(2)]),format:'der',type:'spki'})}
function verify(m){try{return m?.from===REF&&m.nonce!=null&&m.sig&&typeof m.text==='string'&&crypto.verify(null,Buffer.from(`${ROOM}|${m.nonce}|${m.text}`),pub(REF),Buffer.from(m.sig,'base64url'))}catch{return false}}
function J(s){try{return JSON.parse(s)}catch{return null}}
async function get(url){const r=await fetch(url,{headers:{'user-agent':'raindog-sonnet-rules-status/1.0','cache-control':'no-cache'}});if(!r.ok)throw Error(`HTTP ${r.status}`);return await r.text()}
const state={checked_at:new Date().toISOString(),room:ROOM,referee_did:REF,subject_did:DID,request_id:REQ,technocore_write_count:0,verified_messages:[],subject_mentions:[]};
try{const raw=await get(`https://technocore.chat/r/${ROOM}/export?n=${Date.now()}`);for(const m of raw.split(/\r?\n/).filter(Boolean).map(J).filter(Boolean)){if(!verify(m))continue;const p=J(m.text);state.verified_messages.push({seq:Number(m.seq||0)||null,ts:m.ts||null,type:p?.type||null,text_preview:typeof m.text==='string'?m.text.slice(0,220):null});if(m.text.includes(DID)||m.text.includes(REQ))state.subject_mentions.push({seq:Number(m.seq||0)||null,ts:m.ts||null,type:p?.type||null,text:m.text.slice(0,2000)})}}catch(e){state.error=`${e?.name||'Error'}:${e?.message||String(e)}`}
fs.mkdirSync('data',{recursive:true});fs.writeFileSync(OUT,JSON.stringify(state,null,2)+'\n');console.log(JSON.stringify({verified:state.verified_messages.length,mentions:state.subject_mentions},null,2));
