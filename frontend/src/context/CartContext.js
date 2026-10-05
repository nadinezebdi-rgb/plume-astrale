import React, { createContext, useContext, useEffect, useState } from 'react';

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

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    } catch { /* Storage may be unavailable in private browsing. */ }
  }, [items]);

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
  const clearCart = () => setItems([]);
  const total = items.reduce((sum, item) => sum + item.priceValue, 0);

  return (
    <CartContext.Provider value={{ items, count: items.length, total, addItem, removeItem, clearCart }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const cart = useContext(CartContext);
  if (!cart) throw new Error('useCart must be used inside CartProvider');
  return cart;
}