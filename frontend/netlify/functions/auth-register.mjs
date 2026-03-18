import { getStore } from '@netlify/blobs';
import { hashPassword, createToken, jsonResponse, errorResponse } from '../lib/auth-helpers.mjs';
import { randomUUID } from 'crypto';

const REGISTRATION_BONUS = 20;

export default async (req) => {
  if (req.method !== 'POST') {
    return errorResponse('Method not allowed', 405);
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return errorResponse('Corps de requête invalide');
  }

  const email = (body.email || '').trim().toLowerCase();
  const password = body.password || '';

  if (!email || !password) {
    return errorResponse('Email et mot de passe requis');
  }
  if (password.length < 6) {
    return errorResponse('Le mot de passe doit contenir au moins 6 caractères');
  }

  const users = getStore({ name: 'users', consistency: 'strong' });
  const wallets = getStore({ name: 'wallets', consistency: 'strong' });

  // Check if email already exists
  const existing = await users.get(`email:${email}`, { type: 'json' });
  if (existing) {
    return errorResponse('Cet email est déjà utilisé', 400);
  }

  const userId = randomUUID();
  const passwordHash = await hashPassword(password);

  const userDoc = {
    id: userId,
    email,
    password_hash: passwordHash,
    birth_date: body.birth_date || null,
    birth_time: body.birth_time || null,
    birth_place: body.birth_place || null,
    birth_country: body.birth_country || 'France',
    created_at: new Date().toISOString(),
  };

  // Store user indexed by both email and ID
  await users.setJSON(`email:${email}`, userDoc);
  await users.setJSON(`id:${userId}`, userDoc);

  // Create wallet with registration bonus
  const wallet = {
    id: randomUUID(),
    user_id: userId,
    credit_balance: REGISTRATION_BONUS,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    last_daily_bonus: null,
  };
  await wallets.setJSON(userId, wallet);

  const token = createToken(userId, email);

  return jsonResponse({
    token,
    user: {
      id: userId,
      email,
      birth_date: userDoc.birth_date,
      birth_time: userDoc.birth_time,
      birth_place: userDoc.birth_place,
      birth_country: userDoc.birth_country,
    },
    credit_balance: REGISTRATION_BONUS,
  });
};

export const config = {
  path: '/api/auth/register',
  method: 'POST',
};
