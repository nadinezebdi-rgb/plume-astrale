import { corsHeaders, handleCors } from './utils/auth.mjs';

export default async (req) => {
  const cors = handleCors(req);
  if (cors) return cors;

  return new Response(JSON.stringify({
    valid: true,
    discount: 100,
    type: 'percentage',
  }), { headers: corsHeaders() });
};

export const config = {
  path: '/api/discount/validate',
  method: ['POST', 'OPTIONS'],
};
