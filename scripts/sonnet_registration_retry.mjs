#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const EXPECTED_DID = 'did:key:z6MkpLFbURxSo93yf4njy2KSsFNLkixNnKALs2wEsEM15fx4';
const REFEREE_DID = 'did:key:z6MkowHQwsx9xr84WbWN3YCnKutyBnBXkT1ChKY4uEAAMzte';
const ROOM = 'mb-sonnet-2-registration';
const CONTEST_ID = 'sonnet-2';
const REQUEST_ID = 'register-raindog-writer-acf7b45a0344e497';
const X_ACCOUNT_URL = 'https://x.com/raindog_kitetu';
const DEADLINE = '2026-09-18T12:00:00.000Z';
const PAYLOAD = `{"type":"sonnet.register.v1","contest_id":"${CONTEST_ID}","role":"writer","x_account_url":"${X_ACCOUNT_URL}","request_id":"${REQUEST_ID}"}`;
const STATE_PATH = 'data/sonnet_registration_retry_state.json';
const MONITOR_PATH = 'data/sonnet_receipt_monitor_state.json';
const B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const PKCS8_ED25519_PREFIX = Buffer.from('302e020100300506032b657004220420', 'hex');
const SPKI_ED25519_PREFIX = Buffer.from('302a300506032b6570032100', 'hex');
const MULTICODEC_ED25519 = Buffer.from([0xed, 0x01]);
const INVISIBLE_RE = /[\p{Cc}\p{Cf}\p{Cs}\p{Co}\p{Zl}\p{Zp}]/u;

function nowIso() { return new Date().toISOString(); }
function sha256(text) { return crypto.createHash('sha256').update(text).digest('hex'); }
function loadJson(path) { try { return JSON.parse(fs.readFileSync(path, 'utf8')); } catch { return null; } }
function writeJson(path, value) { fs.mkdirSync('data', { recursive: true }); fs.writeFileSync(path, JSON.stringify(value, null, 2) + '\n'); }
function ghOutput(key, value) { if (process.env.GITHUB_OUTPUT) fs.appendFileSync(process.env.GITHUB_OUTPUT, `${key}=${String(value).replace(/\n/g, ' ')}\n`); }
function fail(message) { console.error(message); process.exit(1); }

function swept(text) {
  const out = [...text].map((ch) => INVISIBLE_RE.test(ch) ? ' ' : ch).join('').trim();
  if (!out) fail('payload is empty after Technocore single-line sweep');
  if (out.length > 4096) fail('payload exceeds Technocore message limit');
  return out;
}

function base58(raw) {
  let n = BigInt(`0x${raw.toString('hex') || '0'}`);
  let out = '';
  while (n > 0n) {
    const rem = Number(n % 58n);
    n /= 58n;
    out = B58[rem] + out;
  }
  let leading = 0;
  while (leading < raw.length && raw[leading] === 0) leading++;
  return '1'.repeat(leading) + out;
}

function seedBytesFromSecret(value) {
  if (!value) fail('TECHNOCORE_SIGN_SEED is missing');
  if (/^[0-9a-fA-F]{64}$/.test(value)) return Buffer.from(value, 'hex');
  return crypto.createHash('sha256').update(value, 'utf8').digest();
}

function keyFromSeed(value) {
  const seed = seedBytesFromSecret(value);
  return crypto.createPrivateKey({ key: Buffer.concat([PKCS8_ED25519_PREFIX, seed]), format: 'der', type: 'pkcs8' });
}

function didFromPrivateKey(privateKey) {
  const spki = crypto.createPublicKey(privateKey).export({ format: 'der', type: 'spki' });
  if (!Buffer.isBuffer(spki) || spki.length !== SPKI_ED25519_PREFIX.length + 32 || !spki.subarray(0, SPKI_ED25519_PREFIX.length).equals(SPKI_ED25519_PREFIX)) {
    fail('unexpected Ed25519 public key encoding');
  }
  const raw = spki.subarray(SPKI_ED25519_PREFIX.length);
  return `did:key:z${base58(Buffer.concat([MULTICODEC_ED25519, raw]))}`;
}

function candidateSecrets(raw) {
  const out = new Set();
  const add = (v) => { if (typeof v === 'string' && v.length) out.add(v); };
  add(raw);
  const trimmed = raw.trim();
  add(trimmed);
  let unquoted = trimmed;
  if ((unquoted.startsWith('"') && unquoted.endsWith('"')) || (unquoted.startsWith("'") && unquoted.endsWith("'"))) unquoted = unquoted.slice(1, -1);
  add(unquoted);
  for (const prefix of ['SIGN_SEED=', 'TECHNOCORE_SIGN_SEED=']) {
    if (unquoted.startsWith(prefix)) {
      let v = unquoted.slice(prefix.length).trim();
      if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
      add(v);
    }
  }
  for (const v of [...out]) if (/^0x[0-9a-fA-F]{64}$/.test(v)) add(v.slice(2));
  return [...out];
}

function privateKeyFromEnv() {
  const secret = process.env.TECHNOCORE_SIGN_SEED || '';
  if (!secret) return null;
  for (const candidate of candidateSecrets(secret)) {
    const key = keyFromSeed(candidate);
    if (didFromPrivateKey(key) === EXPECTED_DID) return key;
  }
  fail('Technocore signing secret does not derive the expected DID after safe normalization; WRITE blocked');
}

function baseState(existing = {}) {
  return {
    schema_version: 1,
    contest: CONTEST_ID,
    action: 'sonnet.register.v1',
    room: ROOM,
    request_id: REQUEST_ID,
    expected_did: EXPECTED_DID,
    referee_did: REFEREE_DID,
    x_account_url: X_ACCOUNT_URL,
    deadline_utc: DEADLINE,
    payload_sha256: sha256(PAYLOAD),
    retry_authorized: true,
    max_logical_registration_retry: 1,
    new_request_id_generated: false,
    ...existing,
  };
}

function preflight() {
  const monitor = loadJson(MONITOR_PATH);
  const existing = loadJson(STATE_PATH) || {};

  if (!monitor) fail('receipt monitor state missing; WRITE blocked');
  if (monitor.request_id !== REQUEST_ID || monitor.subject_did !== EXPECTED_DID || monitor.room !== ROOM) fail('receipt monitor identity/request/room mismatch; WRITE blocked');
  if (monitor.receipt || monitor.terminal === true || ['ACCEPTED', 'REFUSED'].includes(String(monitor.status || '').toUpperCase())) {
    const state = baseState({ ...existing, status: 'NO_WRITE_RECEIPT_TERMINAL', write_started: !!existing.write_started, write_completed: !!existing.write_completed, checked_at: nowIso() });
    writeJson(STATE_PATH, state);
    ghOutput('send', 'false'); ghOutput('reason', 'receipt_terminal');
    console.log('No write: referee receipt is already terminal.');
    return;
  }
  if (Date.now() >= Date.parse(DEADLINE)) {
    const state = baseState({ ...existing, status: 'NO_WRITE_DEADLINE_PASSED', checked_at: nowIso() });
    writeJson(STATE_PATH, state);
    ghOutput('send', 'false'); ghOutput('reason', 'deadline_passed');
    console.log('No write: contest deadline has passed.');
    return;
  }
  if (!['PENDING', 'PENDING_HISTORY_EXPIRED'].includes(String(monitor.status || ''))) {
    fail(`receipt monitor status ${monitor.status} is not safe for retry; WRITE blocked`);
  }
  if (existing.write_started === true) {
    ghOutput('send', 'false'); ghOutput('reason', 'already_started');
    console.log('No write: retry action has already been started; dedupe lock is active.');
    return;
  }

  const key = privateKeyFromEnv();
  if (!key) {
    ghOutput('send', 'false'); ghOutput('reason', 'missing_secret');
    console.log('No write: TECHNOCORE_SIGN_SEED GitHub Secret is not configured yet.');
    return;
  }

  const clean = swept(PAYLOAD);
  if (clean !== PAYLOAD) fail('registration payload changes under Technocore sweep; WRITE blocked');
  if (didFromPrivateKey(key) !== EXPECTED_DID) fail('derived DID mismatch; WRITE blocked');

  const state = baseState({
    ...existing,
    status: 'ARMED_ONCE',
    write_started: true,
    write_started_at: nowIso(),
    write_completed: false,
    write_attempt_count: 0,
    confirmed_http_2xx_count: 0,
    registration_resend_count: 0,
    result_unknown: false,
    last_http_status: null,
    last_response_sha256: null,
    last_nonce: null,
    checked_at: nowIso(),
  });
  writeJson(STATE_PATH, state);
  ghOutput('send', 'true'); ghOutput('reason', 'armed');
  console.log('Preflight passed: one retry is armed and dedupe-locked.');
}

async function send() {
  const state = loadJson(STATE_PATH);
  if (!state || state.write_started !== true || state.write_completed === true || state.status !== 'ARMED_ONCE') fail('retry state is not armed for exactly one send');
  if (state.request_id !== REQUEST_ID || state.payload_sha256 !== sha256(PAYLOAD)) fail('retry state/payload mismatch; WRITE blocked');
  if (Date.now() >= Date.parse(DEADLINE)) fail('contest deadline passed before send; WRITE blocked');

  const key = privateKeyFromEnv();
  if (!key) fail('TECHNOCORE_SIGN_SEED disappeared after preflight; WRITE blocked');
  const text = swept(PAYLOAD);
  const nonce = (BigInt(Date.now()) * 1_000_000n).toString();
  if (!/^[0-9]{1,19}$/.test(nonce)) fail('generated nonce is outside Technocore limits');
  const canonical = `${ROOM}|${nonce}|${text}`;
  const signature = crypto.sign(null, Buffer.from(canonical, 'utf8'), key);
  const publicKey = crypto.createPublicKey(key);
  if (!crypto.verify(null, Buffer.from(canonical, 'utf8'), publicKey, signature)) fail('local Ed25519 verification failed; WRITE blocked');
  const sig = signature.toString('base64url');
  if (!/^[A-Za-z0-9_-]{86}$/.test(sig)) fail('signature encoding is not Technocore base64url form');

  const url = `https://technocore.chat/r/${ROOM}/say-signed/${encodeURIComponent(EXPECTED_DID)}/${sig}/${nonce}/${encodeURIComponent(text)}`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20_000);
  let response = null;
  let body = '';
  let networkError = null;

  try {
    response = await fetch(url, {
      method: 'GET',
      headers: { 'user-agent': 'raindog-sonnet-registration-retry/1.2', 'cache-control': 'no-cache' },
      redirect: 'error',
      signal: controller.signal,
    });
    body = await response.text();
  } catch (err) {
    networkError = `${String(err?.name || 'Error')}:${String(err?.message || 'fetch failed')}`;
  } finally {
    clearTimeout(timer);
  }

  const next = baseState({
    ...state,
    status: networkError ? 'WRITE_RESULT_UNKNOWN' : (response?.ok ? 'RETRY_SENT_HTTP_2XX' : `RETRY_SENT_HTTP_${response?.status ?? 'UNKNOWN'}`),
    write_completed: true,
    write_completed_at: nowIso(),
    write_attempt_count: 1,
    confirmed_http_2xx_count: response?.ok ? 1 : 0,
    registration_resend_count: 1,
    result_unknown: !!networkError,
    last_http_status: response?.status ?? null,
    last_response_sha256: body ? sha256(body) : null,
    last_nonce: nonce,
    network_error: networkError,
    checked_at: nowIso(),
  });
  writeJson(STATE_PATH, next);
  ghOutput('send_ok', response?.ok ? 'true' : 'false');
  ghOutput('result', next.status);

  if (networkError) console.log('Technocore retry issued once; network result is unknown. Automatic resend is disabled by the dedupe lock.');
  else console.log(`Technocore retry issued once; HTTP status ${response.status}. Automatic resend is disabled.`);
}

function selftest() {
  const seed = Buffer.from([...Array(32).keys()]).toString('hex');
  const key = keyFromSeed(seed);
  const did = didFromPrivateKey(key);
  const expected = 'did:key:z6MkehRgf7yJbgaGfYsdoAsKdBPE3dj2CYhowQdcjqSJgvVd';
  if (did !== expected) fail('selftest DID vector mismatch');
  const msg = 'lobby|1234567890|selftest';
  const sig = crypto.sign(null, Buffer.from(msg), key);
  if (sig.toString('base64url').length !== 86 || !crypto.verify(null, Buffer.from(msg), crypto.createPublicKey(key), sig)) fail('selftest signature failed');
  console.log('selftest ok');
}

const mode = process.argv[2];
if (mode === 'preflight') preflight();
else if (mode === 'send') await send();
else if (mode === 'selftest') selftest();
else fail('usage: sonnet_registration_retry.mjs <selftest|preflight|send>');