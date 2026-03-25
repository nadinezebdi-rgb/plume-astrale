import { getStore } from '@netlify/blobs';
import { getUserFromRequest, corsHeaders, handleCors } from './utils/auth.mjs';

export default async (req) => {
  const cors = handleCors(req);
  if (cors) return cors;

  try {
    const payload = getUserFromRequest(req);
    if (!payload) {
      return new Response(JSON.stringify({ detail: 'Non authentifié' }), { status: 401, headers: corsHeaders() });
    }

    const store = getStore({ name: 'users', consistency: 'strong' });
    const user = await store.get(payload.email, { type: 'json' });

    if (!user) {
      return new Response(JSON.stringify({ detail: 'Utilisateur introuvable' }), { status: 404, headers: corsHeaders() });
    }

    return new Response(JSON.stringify({
      free_tarot_available: !user.free_tarot_used,
    }), { headers: corsHeaders() });

  } catch (err) {
    return new Response(JSON.stringify({ detail: 'Erreur serveur' }), { status: 500, headers: corsHeaders() });
  }
};

export const config = {
  path: '/api/credits/check-free-tarot',
  method: ['GET', 'OPTIONS'],
};
