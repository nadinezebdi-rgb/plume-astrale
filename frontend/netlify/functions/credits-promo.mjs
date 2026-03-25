import { getStore } from '@netlify/blobs';
import { getUserFromRequest, corsHeaders, handleCors } from './utils/auth.mjs';

export default async (req) => {
  const cors = handleCors(req);
  if (cors) return cors;

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ detail: 'Method not allowed' }), { status: 405, headers: corsHeaders() });
  }

  try {
    const { code } = await req.json();

    if (!code) {
      return new Response(JSON.stringify({ valid: false, detail: 'Code requis' }), { status: 400, headers: corsHeaders() });
    }

    const promoStore = getStore('promos');
    let promo = await promoStore.get(code.toUpperCase(), { type: 'json' });

    if (!promo) {
      if (code.toUpperCase() === 'PLUME2026') {
        promo = { code: 'PLUME2026', discount: 100, credits: 10, type: 'percentage' };
      } else {
        return new Response(JSON.stringify({ valid: false, detail: 'Code promo invalide' }), { status: 404, headers: corsHeaders() });
      }
    }

    const payload = getUserFromRequest(req);
    if (payload && promo.credits) {
      const store = getStore({ name: 'users', consistency: 'strong' });
      const user = await store.get(payload.email, { type: 'json' });
      if (user) {
        user.credit_balance = (user.credit_balance || 0) + promo.credits;
        await store.setJSON(payload.email, user);
      }
    }

    return new Response(JSON.stringify({
      valid: true,
      discount: promo.discount || 0,
      credits: promo.credits || 0,
      code: promo.code,
    }), { headers: corsHeaders() });

  } catch (err) {
    return new Response(JSON.stringify({ detail: 'Erreur serveur' }), { status: 500, headers: corsHeaders() });
  }
};

export const config = {
  path: '/api/credits/promo',
  method: ['POST', 'OPTIONS'],
};
