import { corsHeaders, handleCors } from './utils/auth.mjs';

export default async (req) => {
  const cors = handleCors(req);
  if (cors) return cors;

  return new Response(JSON.stringify({
    success: true,
    message: 'Accès gratuit accordé',
  }), { headers: corsHeaders() });
};

export const config = {
  path: '/api/access/free',
  method: ['POST', 'OPTIONS'],
};
