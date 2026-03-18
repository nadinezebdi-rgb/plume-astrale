import { getStore } from '@netlify/blobs';
import { extractUser, jsonResponse, errorResponse } from '../lib/auth-helpers.mjs';

const SERVICE_COSTS = {
  tarot_oui_non: 2,
  lecture_tarot: 10,
  lecture_astrologique: 10,
  numerologie: 10,
  cartographie_premium: 60,
};

export default async (req) => {
  if (req.method !== 'POST') {
    return errorResponse('Method not allowed', 405);
  }

  let payload;
  try {
    payload = extractUser(req);
  } catch (err) {
    return errorResponse(err.message, 401);
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return errorResponse('Corps de requête invalide');
  }

  const serviceId = body.service_id;
  if (!serviceId || !(serviceId in SERVICE_COSTS)) {
    return errorResponse('Service inconnu', 400);
  }

  const wallets = getStore({ name: 'wallets', consistency: 'strong' });
  const freeTarot = getStore({ name: 'free-tarot', consistency: 'strong' });

  // Special case: first Tarot Oui/Non draw is free
  if (serviceId === 'tarot_oui_non') {
    const freeUsed = await freeTarot.get(payload.user_id);
    if (!freeUsed) {
      await freeTarot.set(payload.user_id, 'true');
      const wallet = await wallets.get(payload.user_id, { type: 'json' });
      return jsonResponse({
        success: true,
        free_draw: true,
        credit_balance: wallet ? wallet.credit_balance : 0,
      });
    }
  }

  const cost = SERVICE_COSTS[serviceId];
  const wallet = await wallets.get(payload.user_id, { type: 'json' });
  if (!wallet) {
    return errorResponse('Portefeuille introuvable', 402);
  }
  if (wallet.credit_balance < cost) {
    return errorResponse('Crédits insuffisants', 402);
  }

  wallet.credit_balance -= cost;
  wallet.updated_at = new Date().toISOString();
  await wallets.setJSON(payload.user_id, wallet);

  return jsonResponse({
    success: true,
    free_draw: false,
    credit_balance: wallet.credit_balance,
  });
};

export const config = {
  path: '/api/credits/use',
  method: 'POST',
};
