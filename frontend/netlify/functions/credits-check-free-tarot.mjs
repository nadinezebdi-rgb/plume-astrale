import { getStore } from '@netlify/blobs';
import { extractUser, jsonResponse, errorResponse } from '../lib/auth-helpers.mjs';

export default async (req) => {
  let payload;
  try {
    payload = extractUser(req);
  } catch (err) {
    return errorResponse(err.message, 401);
  }

  const freeTarot = getStore({ name: 'free-tarot', consistency: 'strong' });
  const freeUsed = await freeTarot.get(payload.user_id);

  return jsonResponse({ free_used: !!freeUsed });
};

export const config = {
  path: '/api/credits/check-free-tarot',
  method: 'GET',
};
