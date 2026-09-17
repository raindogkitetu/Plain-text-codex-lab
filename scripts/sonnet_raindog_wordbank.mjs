#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const DID='did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const PIN='81761a462bab4d2389e16f995ff9f91688654afc';
const EXPECTED_SHA256='81917843c7f44ce2b094ac63873c2c7a4cf802040792c455ba3ca406891c3d22';
const URL=`https://raw.githubusercontent.com/flop-labs/technocore-sonnet-challenge/${PIN}/cmudict.dict`;
const OUT='data/sonnet_raindog_wordbank.json';
const allowed=new Set([...DID.toLowerCase()].filter(c=>/[a-z]/.test(c)));
const missing=[...'abcdefghijklmnopqrstuvwxyz'].filter(c=>!allowed.has(c));

const res=await fetch(URL,{headers:{'user-agent':'raindog-sonnet-wordbank/1.0','cache-control':'no-cache'}});
if(!res.ok)throw new Error(`dictionary HTTP ${res.status}`);
const buf=Buffer.from(await res.arrayBuffer());
const sha=crypto.createHash('sha256').update(buf).digest('hex');
if(sha!==EXPECTED_SHA256)throw new Error(`dictionary sha256 mismatch: ${sha}`);
const text=buf.toString('utf8');

const words=new Map();
const vowel=/^(AA|AE|AH|AO|AW|AY|EH|ER|EY|IH|IY|OW|OY|UH|UW)([012])$/;
for(const line of text.split(/\r?\n/)){
  if(!line||line.startsWith(';;;'))continue;
  const parts=line.trim().split(/\s+/);if(parts.length<2)continue;
  const raw=parts.shift();
  const base=raw.replace(/\(\d+\)$/,'').toLowerCase();
  if(!/^[a-z]+(?:'[a-z]+)*$/.test(base))continue;
  if([...base].some(c=>/[a-z]/.test(c)&&!allowed.has(c)))continue;
  const phones=parts;
  const syl=phones.filter(p=>vowel.test(p)).length;
  if(!syl)continue;
  let anchor=-1;
  for(let i=phones.length-1;i>=0;i--){const m=phones[i].match(vowel);if(m&&m[2]!=='0'){anchor=i;break}}
  if(anchor<0){for(let i=phones.length-1;i>=0;i--){if(vowel.test(phones[i])){anchor=i;break}}}
  const rhyme=anchor>=0?phones.slice(anchor).map(p=>p.replace(/[012]$/,'')).join(' '):null;
  const prev=words.get(base)||{word:base,max_syllables:0,rhyme_keys:new Set()};
  prev.max_syllables=Math.max(prev.max_syllables,syl);
  if(rhyme)prev.rhyme_keys.add(rhyme);
  words.set(base,prev);
}

const all=[...words.values()].map(x=>({word:x.word,syllables:x.max_syllables,rhyme_keys:[...x.rhyme_keys]}));
all.sort((a,b)=>a.syllables-b.syllables||a.word.length-b.word.length||a.word.localeCompare(b.word));
const by={};
for(let s=1;s<=5;s++)by[s]=all.filter(x=>x.syllables===s).slice(0,400);

const preferred=['a','i','my','sky','sun','sea','rain','road','world','soul','flame','fire','fires','ember','embers','dream','rise','rose','moon','dawn','wind','snow','smile','sad','sorrow','memory','summer','day','dusk','dark','alone','air','blue','deep','far','free','gold','love','alive'];
const preferred_verified=preferred.map(w=>words.get(w)).filter(Boolean).map(x=>({word:x.word,syllables:x.max_syllables,rhyme_keys:[...x.rhyme_keys]}));

const fam=new Map();
for(const x of all){
  if(x.syllables>3||x.word.length>10)continue;
  for(const key of x.rhyme_keys){if(!fam.has(key))fam.set(key,[]);fam.get(key).push(x.word)}
}
const rhyme_families=[...fam.entries()]
  .filter(([,ws])=>new Set(ws).size>=4)
  .map(([key,ws])=>({rhyme_key:key,words:[...new Set(ws)].sort((a,b)=>a.length-b.length||a.localeCompare(b)).slice(0,30)}))
  .sort((a,b)=>b.words.length-a.words.length||a.rhyme_key.localeCompare(b.rhyme_key))
  .slice(0,60);

const out={
  schema_version:1,
  generated_at:new Date().toISOString(),
  contest:'sonnet-2',
  did:DID,
  official_package_commit:PIN,
  cmudict_sha256:sha,
  dictionary_verified:true,
  allowed_letters:[...allowed].sort().join(''),
  missing_letters:missing.join(''),
  eligible_dictionary_words:all.length,
  preferred_verified,
  by_syllables:by,
  rhyme_families
};
fs.mkdirSync('data',{recursive:true});
fs.writeFileSync(OUT,JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({dictionary_verified:true,sha256:sha,allowed_letters:out.allowed_letters,missing_letters:out.missing_letters,eligible_dictionary_words:all.length,preferred_verified,top_rhyme_families:rhyme_families.slice(0,10)},null,2));
