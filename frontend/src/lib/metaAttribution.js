/**
 * Attribution Meta — transmission des signaux au backend, pour TOUS les tunnels.
 *
 * Un unique intercepteur axios couvre les treize routes de checkout (kabbale,
 * astrocartographie, thème natal, voyage-karmique, packs de crédits, ...)
 * sans avoir à toucher à chaque page produit.
 *
 * Rien n'est envoyé tant que l'utilisateur n'a pas accepté les cookies :
 * `getCapiAttribution()` renvoie alors un objet vide.
 */
import axios from 'axios';
import { getCapiAttribution } from '@/lib/analytics';

let _installed = false;

export function installMetaAttribution() {
  if (_installed) return;
  _installed = true;

  axios.interceptors.request.use((config) => {
    try {
      const url = config.url || '';
      if (config.method?.toLowerCase() !== 'post' || !url.includes('/checkout')) {
        return config;
      }
      const { event_id: eventId, fbp, fbc } = getCapiAttribution('purchase');
      if (!eventId) return config;
      config.headers = config.headers || {};
      config.headers['X-Meta-Event-Id'] = eventId;
      if (fbp) config.headers['X-Meta-Fbp'] = fbp;
      if (fbc) config.headers['X-Meta-Fbc'] = fbc;
    } catch (_e) { /* ne jamais bloquer un paiement pour du tracking */ }
    return config;
  });
}
