#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const CONTEST='sonnet-2';
const SUBJECT='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const DEADLINE='2026-09-18T12:00:00Z';
const GAME=/^[a-z0-9][a-z0-9_-]{0,15}$/;
const DID=/^did:key:z6Mk[1-9A-HJ-NP-Za-km-z]{44}$/;
const HASH=/^[0-9a-f]{64}$/;
const WORD=/^[A-Za-z]+(?:'[A-Za-z]+)*[,.;:!?]?$/;
const allowed=new Set([...SUBJECT.toLowerCase()].filter(c=>/[a-z]/.test(c)));

function die(msg){console.error(`FAIL: ${msg}`);process.exit(2)}
function ok(cond,msg){if(!cond)die(msg)}
function readInput(arg){if(!arg)die('usage: node scripts/sonnet_protocol_guard.mjs <roster|word|submit> <json-file-or-json> [poem-file]');if(fs.existsSync(arg))return JSON.parse(fs.readFileSync(arg,'utf8'));return JSON.parse(arg)}
function common(p){ok(p&&typeof p==='object','payload must be JSON object');ok(p.contest_id===CONTEST,'contest_id mismatch');ok(typeof p.request_id==='string'&&p.request_id.length>0&&p.request_id.length<=200,'request_id missing/invalid');}
function game(p){ok(typeof p.game_id==='string'&&GAME.test(p.game_id),'game_id invalid');}
function wordCompatible(w){const bare=w.replace(/[,.;:!?]$/,'').toLowerCase();return [...bare].every(c=>c==="'"||allowed.has(c));}

const mode=process.argv[2];
const p=readInput(process.argv[3]);
common(p);
const result={mode,contest:CONTEST,subject_did:SUBJECT,deadline_utc:DEADLINE,valid:false,checks:[]};

if(mode==='roster'){
  ok(p.type==='sonnet.roster.v1','type must be sonnet.roster.v1');game(p);
  ok(p.poem_room===`d-sonnet-2-team-${p.game_id}`,'poem_room does not match game_id');
  ok(Number.isInteger(p.room_generation)&&p.room_generation>=0,'room_generation invalid');
  ok(Array.isArray(p.members)&&p.members.length>=4&&p.members.length<=8,'members must contain 4-8 DIDs');
  ok(new Set(p.members).size===p.members.length,'members contain duplicate DID');
  ok(p.members.every(x=>typeof x==='string'&&DID.test(x)),'members contain invalid DID');
  ok(p.members.includes(SUBJECT),'roster does not include subject DID');
  result.checks.push('same contest/game/poem room binding','room_generation present','4-8 unique DID members','subject DID included');
}else if(mode==='word'){
  ok(p.type==='sonnet.word.v1','type must be sonnet.word.v1');game(p);
  ok(Number.isInteger(p.room_generation)&&p.room_generation>=0,'room_generation invalid');
  ok(Number.isInteger(p.version)&&p.version>=0,'version invalid');
  ok(typeof p.previous_state_hash==='string'&&HASH.test(p.previous_state_hash),'previous_state_hash invalid');
  ok(typeof p.word==='string'&&WORD.test(p.word),'word token grammar invalid');
  ok(wordCompatible(p.word),'word contains a letter absent from registered DID');
  result.checks.push('state fields present','word grammar valid','DID-letter compatibility valid');
}else if(mode==='submit'){
  ok(p.type==='sonnet.submit.v1','type must be sonnet.submit.v1');game(p);
  ok(p.poem_room===`d-sonnet-2-team-${p.game_id}`,'poem_room does not match game_id');
  ok(Number.isInteger(p.room_generation)&&p.room_generation>=0,'room_generation invalid');
  ok(Number.isInteger(p.final_version)&&p.final_version>0,'final_version invalid');
  ok(typeof p.poem_sha256==='string'&&HASH.test(p.poem_sha256),'poem_sha256 invalid');
  ok(Array.isArray(p.x_post_ids)&&p.x_post_ids.length>0&&p.x_post_ids.every(x=>/^\d+$/.test(String(x))),'x_post_ids invalid');
  const poemFile=process.argv[4];
  if(poemFile){const bytes=fs.readFileSync(poemFile);const actual=crypto.createHash('sha256').update(bytes).digest('hex');ok(actual===p.poem_sha256,`poem hash mismatch: ${actual}`);result.computed_poem_sha256=actual;}
  result.checks.push('game/room binding','final version/hash present','X post IDs syntactically valid',...(poemFile?['poem bytes hash matches']:[]));
}else die('mode must be roster, word, or submit');

result.valid=true;
console.log(JSON.stringify(result,null,2));
