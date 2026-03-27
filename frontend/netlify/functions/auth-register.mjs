import { getStore } from '@netlify/blobs';
import bcrypt from 'bcryptjs';
import { createToken, jsonResponse, errorResponse } from './auth-utils.mjs';

export default async (req) => {
  if (req.method !== 'POST') return errorResponse('Method not allowed', 405);

  const { email: rawEmail, password, birth_date, birth_time, birth_place, birth_country } = await req.json();
  if (!rawEmail || !password) return errorResponse('Email et mot de passe requis');

  const email = rawEmail.trim().toLowerCase();
  const store = getStore({ name: 'users', consistency: 'strong' });

  const existing = await store.get(`email:${email}`, { type: 'json' });
  if (existing) return errorResponse('Cet email est déjà utilisé', 400);

  const userId = crypto.randomUUID();
  const passwordHash = bcrypt.hashSync(password, 10);

  const userDoc = {
    id: userId,
    email,
    password_hash: passwordHash,
    birth_date: birth_date || '',
    birth_time: birth_time || '',
    birth_place: birth_place || '',
    birth_country: birth_country || 'France',
    created_at: new Date().toISOString(),
  };

  // Store user by ID and by email (for login lookup)
  await store.setJSON(`user:${userId}`, userDoc);
  await store.setJSON(`email:${email}`, { userId });

  // Create wallet with 20 bonus credits
  const walletStore = getStore({ name: 'wallets', consistency: 'strong' });
  await walletStore.setJSON(`wallet:${userId}`, {
    user_id: userId,
    credit_balance: 20,
    created_at: new Date().toISOString(),
  });

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
    credit_balance: 20,
  });
};

export const config = {
  path: '/api/auth/register',
  method: 'POST',
};
