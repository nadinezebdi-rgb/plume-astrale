import { getStore } from '@netlify/blobs';
import { extractUser, jsonResponse, errorResponse } from '../lib/auth-helpers.mjs';

const CREDIT_PROMO_CODES = {
  PLUMEASTRALE: { credits: 100, description: '100 crédits offerts' },
  TESTPLUME: { credits: 200, description: '200 crédits de test' },
  BIENVENUE: { credits: 50, description: '50 crédits de bienvenue' },
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

  const code = (body.code || '').trim().toUpperCase();
  if (!code || !(code in CREDIT_PROMO_CODES)) {
    return errorResponse('Code promo invalide', 400);
  }

  const promo = CREDIT_PROMO_CODES[code];
  const promoUsed = getStore({ name: 'promo-used', consistency: 'strong' });
  const wallets = getStore({ name: 'wallets', consistency: 'strong' });

  // Check if already used by this user
  const key = `${payload.user_id}:${code}`;
  const existing = await promoUsed.get(key);
  if (existing) {
    return errorResponse('Ce code a déjà été utilisé sur votre compte', 400);
  }

  // Mark as used
  await promoUsed.set(key, 'true');

  // Add credits to wallet
  const wallet = await wallets.get(payload.user_id, { type: 'json' });
  if (!wallet) {
    return errorResponse('Portefeuille introuvable', 400);
  }

  wallet.credit_balance += promo.credits;
  wallet.updated_at = new Date().toISOString();
  await wallets.setJSON(payload.user_id, wallet);

  return jsonResponse({
    success: true,
    credits_added: promo.credits,
    description: promo.description,
    credit_balance: wallet.credit_balance,
  });
};

export const config = {
  path: '/api/credits/promo',
  method: 'POST',
};
