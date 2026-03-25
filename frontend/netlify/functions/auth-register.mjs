import { getStore } from '@netlify/blobs';
import { hashPassword, signJWT, corsHeaders, handleCors } from './utils/auth.mjs';

export default async (req) => {
  const cors = handleCors(req);
  if (cors) return cors;

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ detail: 'Method not allowed' }), { status: 405, headers: corsHeaders() });
  }

  try {
    const { email, password, birth_day, birth_month, birth_year, birth_hour, birth_minute, birth_place, birth_country } = await req.json();

    if (!email || !password) {
      return new Response(JSON.stringify({ detail: 'Email et mot de passe requis' }), { status: 400, headers: corsHeaders() });
    }
    if (password.length < 6) {
      return new Response(JSON.stringify({ detail: 'Le mot de passe doit contenir au moins 6 caractères' }), { status: 400, headers: corsHeaders() });
    }

    const store = getStore({ name: 'users', consistency: 'strong' });
    const emailKey = email.toLowerCase().trim();

    const existing = await store.get(emailKey, { type: 'json' });
    if (existing) {
      return new Response(JSON.stringify({ detail: 'Un compte existe déjà avec cet email' }), { status: 409, headers: corsHeaders() });
    }

    const hashedPassword = await hashPassword(password);
    const userId = crypto.randomUUID();
    const now = new Date().toISOString();

    const user = {
      id: userId,
      email: emailKey,
      password: hashedPassword,
      birth_day, birth_month, birth_year,
      birth_hour, birth_minute,
      birth_place, birth_country,
      credit_balance: 20,
      free_tarot_used: false,
      created_at: now,
    };

    await store.setJSON(emailKey, user);

    const token = signJWT({ userId, email: emailKey });
    const { password: _, ...safeUser } = user;

    return new Response(JSON.stringify({
      token,
      user: safeUser,
      credit_balance: user.credit_balance,
    }), { status: 201, headers: corsHeaders() });

  } catch (err) {
    return new Response(JSON.stringify({ detail: 'Erreur lors de l\'inscription' }), { status: 500, headers: corsHeaders() });
  }
};

export const config = {
  path: '/api/auth/register',
  method: ['POST', 'OPTIONS'],
};
