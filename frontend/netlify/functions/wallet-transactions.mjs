import { getStore } from '@netlify/blobs';
import { extractUser, jsonResponse, errorResponse } from '../lib/auth-helpers.mjs';

export default async (req) => {
  let payload;
  try {
    payload = extractUser(req);
  } catch (err) {
    return errorResponse(err.message, 401);
  }

  const wallets = getStore({ name: 'wallets', consistency: 'strong' });
  const wallet = await wallets.get(payload.user_id, { type: 'json' });

  return jsonResponse({
    transactions: wallet ? (wallet.transactions || []) : [],
  });
};

export const config = {
  path: '/api/wallet/transactions',
  method: 'GET',
};
