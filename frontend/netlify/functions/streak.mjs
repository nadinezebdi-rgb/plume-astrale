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

    const today = new Date().toISOString().slice(0, 10);

    if (req.method === 'GET') {
      return new Response(JSON.stringify({
        streak: user.streak || 0,
        last_checkin: user.last_checkin || null,
        checked_in_today: user.last_checkin === today,
      }), { headers: corsHeaders() });
    }

    if (req.method === 'POST') {
      if (user.last_checkin === today) {
        return new Response(JSON.stringify({
          detail: 'Déjà enregistré aujourd\'hui',
          streak: user.streak || 0,
        }), { status: 409, headers: corsHeaders() });
      }

      const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
      const isConsecutive = user.last_checkin === yesterday;

      user.streak = isConsecutive ? (user.streak || 0) + 1 : 1;
      user.last_checkin = today;

      if (user.streak % 7 === 0) {
        user.credit_balance = (user.credit_balance || 0) + 5;
      }

      await store.setJSON(payload.email, user);

      return new Response(JSON.stringify({
        streak: user.streak,
        last_checkin: user.last_checkin,
        credit_balance: user.credit_balance,
      }), { headers: corsHeaders() });
    }

    return new Response(JSON.stringify({ detail: 'Method not allowed' }), { status: 405, headers: corsHeaders() });

  } catch (err) {
    return new Response(JSON.stringify({ detail: 'Erreur serveur' }), { status: 500, headers: corsHeaders() });
  }
};

export const config = {
  path: ['/api/streak/status', '/api/streak/checkin'],
  method: ['GET', 'POST', 'OPTIONS'],
};
