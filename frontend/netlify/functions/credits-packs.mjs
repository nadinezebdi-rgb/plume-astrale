import { corsHeaders, handleCors } from './utils/auth.mjs';

const PACKS = [
  { id: 'decouverte', name: 'Découverte', credits: 30, price: 4.99, description: 'Idéal pour commencer' },
  { id: 'exploration', name: 'Exploration', credits: 80, price: 9.99, description: 'Le plus populaire', popular: true },
  { id: 'premium', name: 'Premium', credits: 200, price: 19.99, description: 'Pour les passionnés' },
];

export default async (req) => {
  const cors = handleCors(req);
  if (cors) return cors;

  return new Response(JSON.stringify({ packs: PACKS }), { headers: corsHeaders() });
};

export const config = {
  path: '/api/credits/packs',
  method: ['GET', 'OPTIONS'],
};
