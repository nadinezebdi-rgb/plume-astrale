const PROMO_KEY = 'plume-astrale-cart-promo-v1';
const PENDING_KEY = 'plume-astrale-cart-pending-v1';

const read = (storage, key) => {
  try {
    return storage.getItem(key) || '';
  } catch {
    return '';
  }
};

const write = (storage, key, value) => {
  try {
    if (value) storage.setItem(key, value);
    else storage.removeItem(key);
  } catch { /* Storage may be unavailable in private browsing. */ }
};

// Code promo saisi dans le panier, repris automatiquement sur les pages de paiement.
export const getCartPromo = () => read(window.localStorage, PROMO_KEY);
export const setCartPromo = (code) => write(window.localStorage, PROMO_KEY, code);

// Lecture en cours de paiement depuis le panier (retirée du panier au retour de paiement).
export const getPendingCartItem = () => read(window.sessionStorage, PENDING_KEY);
export const setPendingCartItem = (key) => write(window.sessionStorage, PENDING_KEY, key);
