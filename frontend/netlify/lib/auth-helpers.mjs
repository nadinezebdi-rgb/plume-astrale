/**
 * Shared authentication helpers for Netlify Functions.
 * Uses Node.js built-in crypto (no external dependencies).
 */
import { createHmac, scrypt, randomBytes, timingSafeEqual } from 'crypto';
import { promisify } from 'util';

const scryptAsync = promisify(scrypt);

const JWT_EXPIRY_HOURS = 72;

function getJwtSecret() {
  return (typeof Netlify !== 'undefined' && Netlify.env.get('JWT_SECRET')) || 'plume-astrale-secret-key-2026';
}

// ─── Password Hashing (scrypt) ───

export async function hashPassword(password) {
  const salt = randomBytes(16).toString('hex');
  const hash = await scryptAsync(password, salt, 64);
  return `${salt}:${hash.toString('hex')}`;
}

export async function verifyPassword(plain, stored) {
  const [salt, hash] = stored.split(':');
  const hashBuffer = Buffer.from(hash, 'hex');
  const derived = await scryptAsync(plain, salt, 64);
  return timingSafeEqual(hashBuffer, derived);
}

// ─── JWT ───

function base64url(data) {
  return Buffer.from(typeof data === 'string' ? data : JSON.stringify(data)).toString('base64url');
}

function base64urlDecode(str) {
  return JSON.parse(Buffer.from(str, 'base64url').toString());
}

export function createToken(userId, email) {
  const header = base64url({ alg: 'HS256', typ: 'JWT' });
  const now = Math.floor(Date.now() / 1000);
  const payload = base64url({
    user_id: userId,
    email,
    exp: now + JWT_EXPIRY_HOURS * 3600,
    iat: now,
  });
  const signature = createHmac('sha256', getJwtSecret())
    .update(`${header}.${payload}`)
    .digest('base64url');
  return `${header}.${payload}.${signature}`;
}

export function decodeToken(token) {
  const parts = token.split('.');
  if (parts.length !== 3) throw new Error('Token invalide');

  const [header, payload, signature] = parts;
  const expected = createHmac('sha256', getJwtSecret())
    .update(`${header}.${payload}`)
    .digest('base64url');

  if (expected !== signature) throw new Error('Token invalide');

  const data = base64urlDecode(payload);
  if (data.exp && data.exp < Math.floor(Date.now() / 1000)) {
    throw new Error('Token expiré');
  }
  return data;
}

/**
 * Extract and validate the current user from Authorization header.
 * Returns the decoded token payload { user_id, email }.
 * Throws if invalid.
 */
export function extractUser(req) {
  const auth = req.headers.get('authorization') || '';
  if (!auth.startsWith('Bearer ')) {
    throw new Error('Authentification requise');
  }
  const token = auth.slice(7);
  return decodeToken(token);
}

// ─── Response helpers ───

export function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

export function errorResponse(detail, status = 400) {
  return new Response(JSON.stringify({ detail }), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}
