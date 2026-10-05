import React, { createContext, useContext, useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { getCartPromo, setCartPromo, getPendingCartItem, setPendingCartItem } from '@/lib/cartPromo';

const STORAGE_KEY = 'plume-astrale-cart-v1';
const CartContext = createContext(null);

function readCart() {
  try {
    const value = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '[]');
    return Array.isArray(value)
      ? value.filter((item) => item?.key && item?.title && item?.to && Number.isFinite(item.priceValue))
      : [];
  } catch {
    return [];
  }
}

export function CartProvider({ children }) {
  const [items, setItems] = useState(readCart);
  const [promoCode, setPromoCodeState] = useState(getCartPromo);

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    } catch { /* Storage may be unavailable in private browsing. */ }
  }, [items]);

  // Un panier vide ne garde pas de code promo.
  useEffect(() => {
    if (items.length === 0 && promoCode) {
      setCartPromo('');
      setPromoCodeState('');
    }
  }, [items, promoCode]);

  const addItem = (item) => {
    const priceValue = Number(String(item.price || '').replace(/[^\d,.-]/g, '').replace(',', '.'));
    if (!item?.key || !item?.title || !item?.to || !Number.isFinite(priceValue) || priceValue <= 0) return;
    setItems((current) => current.some((entry) => entry.key === item.key)
      ? current
      : [...current, {
          key: item.key,
          title: item.title,
          tagline: item.tagline,
          price: item.price,
          priceValue,
          to: item.to,
        }]);
  };

  const removeItem = (key) => setItems((current) => current.filter((item) => item.key !== key));
  const setPromoCode = (code) => {
    setCartPromo(code);
    setPromoCodeState(code);
  };
  const clearCart = () => {
    setItems([]);
    setPromoCode('');
    setPendingCartItem('');
  };
  const startCheckout = (key) => setPendingCartItem(key);
  const total = items.reduce((sum, item) => sum + item.priceValue, 0);

  return (
    <CartContext.Provider value={{ items, count: items.length, total, addItem, removeItem, clearCart, promoCode, setPromoCode, startCheckout }}>
      {children}
    </CartContext.Provider>
  );
}

const SUCCESS_PATH = /^\/(?:[^/]+\/)?(?:succes|merci)\/?$/;

// Au retour d'un paiement lancé depuis le panier : retire la lecture payée et propose la suivante.
export function CartCheckoutBridge() {
  const { items, removeItem, setPromoCode } = useCart();
  const { pathname } = useLocation();
  const [remaining, setRemaining] = useState(0);

  useEffect(() => {
    if (!SUCCESS_PATH.test(pathname)) {
      setRemaining(0);
      return;
    }
    const pending = getPendingCartItem();
    if (!pending) return;
    setPendingCartItem('');
    const left = items.filter((item) => item.key !== pending).length;
    removeItem(pending);
    if (left === 0) setPromoCode('');
    setRemaining(left);
    // Exécuté une seule fois par arrivée sur une page de succès.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  if (!remaining) return null;
  return (
    <div
      data-testid="cart-next-banner"
      style={{ position: 'fixed', left: 16, right: 16, bottom: 16, zIndex: 80, maxWidth: 520, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 14, padding: '14px 18px', borderRadius: 6, background: '#111625', border: '1px solid rgba(212,175,55,0.5)', color: '#F5EEE0', font: '14px Inter, sans-serif', boxShadow: '0 10px 30px rgba(0,0,0,0.35)' }}
    >
      <span>Paiement validé. Il reste {remaining} lecture{remaining > 1 ? 's' : ''} dans votre panier.</span>
      <Link to="/panier" style={{ color: '#D4AF37', fontWeight: 600, whiteSpace: 'nowrap' }}>Continuer ma commande</Link>
    </div>
  );
}

export function useCart() {
  const cart = useContext(CartContext);
  if (!cart) throw new Error('useCart must be used inside CartProvider');
  return cart;
}