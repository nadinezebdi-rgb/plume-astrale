import { getStore } from '@netlify/blobs';
import { verifyPassword, createToken, jsonResponse, errorResponse } from '../lib/auth-helpers.mjs';

const DAILY_BONUS = 1;

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

  const users = getStore({ name: 'users', consistency: 'strong' });
  const wallets = getStore({ name: 'wallets', consistency: 'strong' });

  const user = await users.get(`email:${email}`, { type: 'json' });
  if (!user) {
    return errorResponse('Email ou mot de passe incorrect', 401);
  }

  const valid = await verifyPassword(password, user.password_hash);
  if (!valid) {
    return errorResponse('Email ou mot de passe incorrect', 401);
  }

  const token = createToken(user.id, email);

  // Get wallet and apply daily bonus if eligible
  let wallet = await wallets.get(user.id, { type: 'json' });
  let creditBalance = 0;

  if (wallet) {
    const now = new Date();
    const todayStr = now.toISOString().slice(0, 10);
    const lastBonus = wallet.last_daily_bonus;

    if (lastBonus) {
      const lastBonusDate = lastBonus.slice(0, 10);
      if (lastBonusDate < todayStr) {
        wallet.credit_balance += DAILY_BONUS;
        wallet.last_daily_bonus = now.toISOString();
        wallet.updated_at = now.toISOString();
        await wallets.setJSON(user.id, wallet);
      }
    } else {
      // First daily bonus check — give if account was created before today
      const createdDate = (user.created_at || '').slice(0, 10);
      if (createdDate && createdDate < todayStr) {
        wallet.credit_balance += DAILY_BONUS;
        wallet.last_daily_bonus = now.toISOString();
        wallet.updated_at = now.toISOString();
        await wallets.setJSON(user.id, wallet);
      }
    }
    creditBalance = wallet.credit_balance;
  }

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
    credit_balance: creditBalance,
  });
};

export const config = {
  path: '/api/auth/login',
  method: 'POST',
};
