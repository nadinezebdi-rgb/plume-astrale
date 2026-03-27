import { getStore } from '@netlify/blobs';
import bcrypt from 'bcryptjs';
import { createToken, jsonResponse, errorResponse } from './auth-utils.mjs';

export default async (req) => {
  if (req.method !== 'POST') return errorResponse('Method not allowed', 405);

  const { email: rawEmail, password } = await req.json();
  if (!rawEmail || !password) return errorResponse('Email et mot de passe requis');

  const email = rawEmail.trim().toLowerCase();
  const store = getStore({ name: 'users', consistency: 'strong' });

  // Look up user by email
  const emailEntry = await store.get(`email:${email}`, { type: 'json' });
  if (!emailEntry) return errorResponse('Email ou mot de passe incorrect', 401);

  const user = await store.get(`user:${emailEntry.userId}`, { type: 'json' });
  if (!user || !bcrypt.compareSync(password, user.password_hash)) {
    return errorResponse('Email ou mot de passe incorrect', 401);
  }

  // Get wallet
  const walletStore = getStore({ name: 'wallets', consistency: 'strong' });
  const wallet = await walletStore.get(`wallet:${user.id}`, { type: 'json' });

  const token = createToken(user.id, email);
  return jsonResponse({
    token,
    user: {
      id: user.id,
      email: user.email,
      birth_date: user.birth_date,
      birth_time: user.birth_time,
      birth_place: user.birth_place,
      birth_country: user.birth_country,
    },
    credit_balance: wallet ? wallet.credit_balance : 0,
  });
};

export const config = {
  path: '/api/auth/login',
  method: 'POST',
};
