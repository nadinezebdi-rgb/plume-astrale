import { jsonResponse } from '../lib/auth-helpers.mjs';

const SERVICE_COSTS = {
  tarot_oui_non: 2,
  lecture_tarot: 10,
  lecture_astrologique: 10,
  numerologie: 10,
  cartographie_premium: 60,
};

export default async () => {
  return jsonResponse({ costs: SERVICE_COSTS });
};

export const config = {
  path: '/api/credits/service-costs',
  method: 'GET',
};
