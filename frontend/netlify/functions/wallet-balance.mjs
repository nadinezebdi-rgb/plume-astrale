import { getStore } from '@netlify/blobs';
import { getUserFromRequest, jsonResponse, errorResponse } from './auth-utils.mjs';

export default async (req) => {
  const payload = getUserFromRequest(req);
  if (!payload) return errorResponse('Authentification requise', 401);

  const walletStore = getStore({ name: 'wallets', consistency: 'strong' });
  const wallet = await walletStore.get(`wallet:${payload.user_id}`, { type: 'json' });

  return jsonResponse({
    credit_balance: wallet ? wallet.credit_balance : 0,
  });
};

export const config = {
  path: '/api/wallet/balance',
  method: 'GET',
};
