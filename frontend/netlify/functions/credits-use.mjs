import { getStore } from '@netlify/blobs';
import { getUserFromRequest, corsHeaders, handleCors } from './utils/auth.mjs';

const SERVICE_COSTS = {
  'tarot-oui-non': 2,
  'tarologie': 10,
  'numerologie': 10,
  'compatibilite': 10,
  'theme-astral': 10,
  'premium': 60,
  'tirage-tarot': 10,
};

export default async (req) => {
  const cors = handleCors(req);
  if (cors) return cors;

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ detail: 'Method not allowed' }), { status: 405, headers: corsHeaders() });
  }

  try {
    const payload = getUserFromRequest(req);
    if (!payload) {
      return new Response(JSON.stringify({ detail: 'Non authentifié' }), { status: 401, headers: corsHeaders() });
    }

    const { service_id } = await req.json();
    const cost = SERVICE_COSTS[service_id] || 10;

    const store = getStore({ name: 'users', consistency: 'strong' });
    const user = await store.get(payload.email, { type: 'json' });

    if (!user) {
      return new Response(JSON.stringify({ detail: 'Utilisateur introuvable' }), { status: 404, headers: corsHeaders() });
    }

    if (user.credit_balance < cost) {
      return new Response(JSON.stringify({ detail: 'Crédits insuffisants', credit_balance: user.credit_balance }), { status: 402, headers: corsHeaders() });
    }

    user.credit_balance -= cost;
    await store.setJSON(payload.email, user);

    return new Response(JSON.stringify({
      credit_balance: user.credit_balance,
      cost,
      service_id,
    }), { headers: corsHeaders() });

  } catch (err) {
    return new Response(JSON.stringify({ detail: 'Erreur serveur' }), { status: 500, headers: corsHeaders() });
  }
};

export const config = {
  path: '/api/credits/use',
  method: ['POST', 'OPTIONS'],
};
