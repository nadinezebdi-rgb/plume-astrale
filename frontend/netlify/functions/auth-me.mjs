import { getStore } from '@netlify/blobs';
import { getUserFromRequest, jsonResponse, errorResponse } from './auth-utils.mjs';

export default async (req) => {
  const payload = getUserFromRequest(req);
  if (!payload) return errorResponse('Authentification requise', 401);

  const store = getStore({ name: 'users', consistency: 'strong' });
  const user = await store.get(`user:${payload.user_id}`, { type: 'json' });
  if (!user) return errorResponse('Utilisateur introuvable', 401);

  const walletStore = getStore({ name: 'wallets', consistency: 'strong' });
  const wallet = await walletStore.get(`wallet:${user.id}`, { type: 'json' });

  return jsonResponse({
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
  path: '/api/auth/me',
  method: 'GET',
};
