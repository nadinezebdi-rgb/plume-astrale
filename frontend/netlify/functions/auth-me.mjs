import { getStore } from '@netlify/blobs';
import { extractUser, jsonResponse, errorResponse } from '../lib/auth-helpers.mjs';

export default async (req) => {
  let payload;
  try {
    payload = extractUser(req);
  } catch (err) {
    return errorResponse(err.message, 401);
  }

  const users = getStore({ name: 'users', consistency: 'strong' });
  const wallets = getStore({ name: 'wallets', consistency: 'strong' });

  const user = await users.get(`id:${payload.user_id}`, { type: 'json' });
  if (!user) {
    return errorResponse('Utilisateur introuvable', 401);
  }

  const wallet = await wallets.get(user.id, { type: 'json' });
  const creditBalance = wallet ? wallet.credit_balance : 0;

  return jsonResponse({
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
  path: '/api/auth/me',
  method: 'GET',
};
