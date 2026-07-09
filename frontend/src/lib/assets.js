/**
 * Helpers pour construire les URLs des assets statiques hebergees sur Supabase Storage.
 * Bucket public : `public-assets`
 * Usage : `import { asset } from '../lib/assets'; asset('videos/cercle-hero.mp4')`
 */

const SUPABASE_URL = process.env.REACT_APP_SUPABASE_URL || '';
const BUCKET = 'public-assets';

/**
 * @param {string} path — chemin dans le bucket (ex: 'videos/cercle-hero.mp4', 'images/tarot/tarot_cards_2.png')
 * @returns {string} URL publique CDN
 */
export const asset = (path) => {
  const clean = String(path || '').replace(/^\/+/, '');
  return `${SUPABASE_URL}/storage/v1/object/public/${BUCKET}/${clean}`;
};

export default asset;
