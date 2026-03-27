import { createHmac, timingSafeEqual } from 'node:crypto';

const JWT_SECRET = Netlify.env.get('JWT_SECRET') || 'plume-astrale-secret-key-2026';
const JWT_EXPIRY_HOURS = 72;

function base64url(buf) {
  return Buffer.from(buf).toString('base64url');
}

export function createToken(userId, email) {
  const header = base64url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const now = Math.floor(Date.now() / 1000);
  const payload = base64url(JSON.stringify({
    user_id: userId,
    email,
    iat: now,
    exp: now + JWT_EXPIRY_HOURS * 3600,
  }));
  const signature = base64url(
    createHmac('sha256', JWT_SECRET).update(`${header}.${payload}`).digest()
  );
  return `${header}.${payload}.${signature}`;
}

export function decodeToken(token) {
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  const [header, payload, signature] = parts;

  const expected = base64url(
    createHmac('sha256', JWT_SECRET).update(`${header}.${payload}`).digest()
  );

  const sigBuf = Buffer.from(signature, 'base64url');
  const expBuf = Buffer.from(expected, 'base64url');
  if (sigBuf.length !== expBuf.length || !timingSafeEqual(sigBuf, expBuf)) {
    return null;
  }

  const data = JSON.parse(Buffer.from(payload, 'base64url').toString());
  if (data.exp && data.exp < Math.floor(Date.now() / 1000)) {
    return null;
  }
  return data;
}

export function getUserFromRequest(req) {
  const auth = req.headers.get('Authorization') || '';
  if (!auth.startsWith('Bearer ')) return null;
  return decodeToken(auth.split(' ')[1]);
}

export function jsonResponse(data, status = 200) {
  return Response.json(data, { status });
}

export function errorResponse(detail, status = 400) {
  return Response.json({ detail }, { status });
}
