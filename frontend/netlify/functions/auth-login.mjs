import { getStore } from '@netlify/blobs';
import { verifyPassword, signJWT, corsHeaders, handleCors } from './utils/auth.mjs';

export default async (req) => {
  const cors = handleCors(req);
  if (cors) return cors;

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ detail: 'Method not allowed' }), { status: 405, headers: corsHeaders() });
  }

  try {
    const { email, password } = await req.json();

    if (!email || !password) {
      return new Response(JSON.stringify({ detail: 'Email et mot de passe requis' }), { status: 400, headers: corsHeaders() });
    }

    const store = getStore({ name: 'users', consistency: 'strong' });
    const emailKey = email.toLowerCase().trim();

    const user = await store.get(emailKey, { type: 'json' });
    if (!user) {
      return new Response(JSON.stringify({ detail: 'Email ou mot de passe incorrect' }), { status: 401, headers: corsHeaders() });
    }

    const valid = await verifyPassword(password, user.password);
    if (!valid) {
      return new Response(JSON.stringify({ detail: 'Email ou mot de passe incorrect' }), { status: 401, headers: corsHeaders() });
    }

    const token = signJWT({ userId: user.id, email: emailKey });
    const { password: _, ...safeUser } = user;

    return new Response(JSON.stringify({
      token,
      user: safeUser,
      credit_balance: user.credit_balance,
    }), { headers: corsHeaders() });

  } catch (err) {
    return new Response(JSON.stringify({ detail: 'Erreur de connexion' }), { status: 500, headers: corsHeaders() });
  }
};

export const config = {
  path: '/api/auth/login',
  method: ['POST', 'OPTIONS'],
};
