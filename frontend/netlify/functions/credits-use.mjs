import { getStore } from '@netlify/blobs';
import { getUserFromRequest, jsonResponse, errorResponse } from './auth-utils.mjs';

const SERVICE_COSTS = {
  tarot_oui_non: 2,
  lecture_tarot: 10,
  lecture_astrologique: 10,
  numerologie: 10,
  cartographie_premium: 60,
};

export default async (req) => {
  if (req.method !== 'POST') return errorResponse('Method not allowed', 405);

  const payload = getUserFromRequest(req);
  if (!payload) return errorResponse('Authentification requise', 401);

  const { service_id } = await req.json();
  const cost = SERVICE_COSTS[service_id];
  if (cost === undefined) return errorResponse('Service inconnu', 400);

  const walletStore = getStore({ name: 'wallets', consistency: 'strong' });
  const wallet = await walletStore.get(`wallet:${payload.user_id}`, { type: 'json' });
  if (!wallet) return errorResponse('Portefeuille introuvable', 404);
  if (wallet.credit_balance < cost) return errorResponse('Crédits insuffisants', 400);

  wallet.credit_balance -= cost;
  wallet.updated_at = new Date().toISOString();
  await walletStore.setJSON(`wallet:${payload.user_id}`, wallet);

  return jsonResponse({ credit_balance: wallet.credit_balance });
};

export const config = {
  path: '/api/credits/use',
  method: 'POST',
};
