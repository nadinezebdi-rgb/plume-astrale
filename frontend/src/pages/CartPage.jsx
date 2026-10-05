import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { ArrowRight, ShoppingCart, Trash2 } from 'lucide-react';
import SEO from '@/components/SEO';
import PsPageShell from '@/components/PsPageShell';
import { useCart } from '@/context/CartContext';

const API = process.env.REACT_APP_BACKEND_URL;

// Identifiant produit attendu par /api/promo/validate quand il diffère de la clé du panier.
const PROMO_PRODUCT = { natal: 'theme_natal_pdf_oneshot' };

const IDLE_PROMO = { status: 'idle', message: '', finals: {}, adminOnly: false };

const formatPrice = (amount) => new Intl.NumberFormat('fr-FR', {
  style: 'currency',
  currency: 'EUR',
}).format(amount);

export default function CartPage() {
  const { items, total, removeItem, clearCart, promoCode, setPromoCode, startCheckout } = useCart();
  const [codeInput, setCodeInput] = useState(promoCode || '');
  const [validating, setValidating] = useState(false);
  const [promo, setPromo] = useState(IDLE_PROMO);

  const itemsSignature = items.map((item) => item.key).join('|');

  const validateCode = async (code) => {
    setValidating(true);
    try {
      const results = await Promise.all(items.map(async (item) => {
        try {
          const r = await axios.post(`${API}/api/promo/validate`, {
            code,
            product: PROMO_PRODUCT[item.key] || item.key,
            amount: item.priceValue,
          });
          return [item, r.data || {}];
        } catch {
          return [item, {}];
        }
      }));
      const finals = {};
      let adminOnly = false;
      let message = '';
      results.forEach(([item, d]) => {
        if (!d.valid) return;
        finals[item.key] = typeof d.final_amount === 'number' ? Math.max(0, d.final_amount) : item.priceValue;
        adminOnly = adminOnly || !!d.admin_only;
        message = message || d.message || '';
      });
      if (Object.keys(finals).length === 0) {
        setPromo({ ...IDLE_PROMO, status: 'ko', message: 'Code invalide, expiré ou non applicable à ces lectures.' });
        setPromoCode('');
      } else {
        setPromo({ status: 'ok', message, finals, adminOnly });
      }
    } finally {
      setValidating(false);
    }
  };

  const applyCode = () => {
    const code = codeInput.trim().toUpperCase();
    if (!code || !items.length) return;
    if (code === promoCode) validateCode(code);
    else setPromoCode(code);
  };

  const removeCode = () => {
    setPromoCode('');
    setCodeInput('');
    setPromo(IDLE_PROMO);
  };

  // Recalcule la remise au chargement et quand le contenu du panier ou le code change.
  useEffect(() => {
    if (promoCode && items.length) validateCode(promoCode);
    else setPromo((current) => (current.status === 'ko' ? current : IDLE_PROMO));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [itemsSignature, promoCode]);

  const itemFinal = (item) => (promo.status === 'ok' && item.key in promo.finals ? promo.finals[item.key] : item.priceValue);
  const finalTotal = items.reduce((sum, item) => sum + itemFinal(item), 0);
  const discount = total - finalTotal;
  const firstItem = items[0];

  return (
    <PsPageShell background="light">
      <SEO path="/panier" title="Mon panier · Plume Astrale" noindex />
      <main data-testid="cart-page" style={{ maxWidth: 880, minHeight: '70vh', margin: '0 auto', padding: '72px 24px 96px' }}>
        <p style={{ margin: '0 0 12px', color: 'var(--plume-gold)', font: '12px Inter, sans-serif', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
          Votre sélection
        </p>
        <h1 style={{ margin: 0, color: 'var(--plume-night)', font: '500 40px/1.15 Playfair Display, Georgia, serif' }}>
          Mon panier <ShoppingCart size={25} aria-hidden="true" style={{ verticalAlign: 'middle' }} />
        </h1>

        {items.length === 0 ? (
          <div data-testid="cart-empty" style={{ marginTop: 36, padding: '30px 0', borderTop: '1px solid rgba(17,22,37,0.14)', borderBottom: '1px solid rgba(17,22,37,0.14)' }}>
            <p style={{ margin: '0 0 18px', color: 'var(--pa-muted)', font: '16px/1.6 Inter, sans-serif' }}>
              Votre panier est vide. Parcourez les lectures et ajoutez celles qui vous intéressent.
            </p>
            <Link to="/" style={{ display: 'inline-flex', minHeight: 44, alignItems: 'center', gap: 8, color: 'var(--plume-night)', font: '600 14px Inter, sans-serif' }}>
              Explorer les prestations <ArrowRight size={16} aria-hidden="true" />
            </Link>
          </div>
        ) : (
          <>
            <ul data-testid="cart-items" style={{ margin: '36px 0 0', padding: 0, listStyle: 'none', borderTop: '1px solid rgba(17,22,37,0.14)' }}>
              {items.map((item) => (
                <li key={item.key} data-testid={`cart-item-${item.key}`} style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) auto auto', alignItems: 'center', gap: 20, padding: '20px 0', borderBottom: '1px solid rgba(17,22,37,0.14)' }}>
                  <div>
                    <h2 style={{ margin: '0 0 4px', color: 'var(--plume-night)', font: '500 20px/1.25 Playfair Display, Georgia, serif' }}>{item.title}</h2>
                    <p style={{ margin: 0, color: 'var(--pa-muted)', font: '13px/1.5 Inter, sans-serif' }}>{item.tagline}</p>
                  </div>
                  <strong style={{ color: 'var(--plume-night)', font: '600 14px Inter, sans-serif', whiteSpace: 'nowrap' }}>
                    {itemFinal(item) !== item.priceValue ? (
                      <>
                        <span style={{ marginRight: 8, color: 'var(--pa-muted)', fontWeight: 400, textDecoration: 'line-through' }}>{item.price}</span>
                        {itemFinal(item) === 0 ? 'Offert' : formatPrice(itemFinal(item))}
                      </>
                    ) : item.price}
                  </strong>
                  <button
                    type="button"
                    aria-label={`Retirer ${item.title} du panier`}
                    data-testid={`cart-remove-${item.key}`}
                    onClick={() => removeItem(item.key)}
                    style={{ display: 'grid', width: 40, height: 40, placeItems: 'center', border: '1px solid rgba(17,22,37,0.16)', borderRadius: 4, background: 'transparent', color: 'var(--plume-night)', cursor: 'pointer' }}
                  >
                    <Trash2 size={17} aria-hidden="true" />
                  </button>
                  <Link to={item.to} onClick={() => startCheckout(item.key)} data-testid={`cart-checkout-${item.key}`} style={{ gridColumn: '1 / -1', justifySelf: 'start', color: 'var(--plume-night)', font: '600 13px Inter, sans-serif', textDecorationColor: 'var(--plume-gold)', textUnderlineOffset: 4 }}>
                    Payer cette lecture <ArrowRight size={14} aria-hidden="true" style={{ verticalAlign: 'middle' }} />
                  </Link>
                </li>
              ))}
            </ul>

            <div data-testid="cart-promo" style={{ padding: '22px 0', borderBottom: '1px solid rgba(17,22,37,0.14)' }}>
              <label htmlFor="cart-promo-input" style={{ display: 'block', margin: '0 0 8px', color: 'var(--plume-night)', font: '600 14px Inter, sans-serif' }}>
                Code promo
              </label>
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                <input
                  id="cart-promo-input"
                  type="text"
                  value={codeInput}
                  onChange={(e) => setCodeInput(e.target.value.toUpperCase())}
                  onKeyDown={(e) => { if (e.key === 'Enter') applyCode(); }}
                  placeholder="Saisissez votre code"
                  autoComplete="off"
                  data-testid="cart-promo-input"
                  style={{ flex: '1 1 220px', minHeight: 44, padding: '0 14px', border: '1px solid rgba(17,22,37,0.25)', borderRadius: 3, background: '#fff', color: 'var(--plume-night)', font: '14px Inter, sans-serif', letterSpacing: '0.08em' }}
                />
                <button
                  type="button"
                  onClick={applyCode}
                  disabled={!codeInput.trim() || validating}
                  data-testid="cart-promo-apply"
                  style={{ minHeight: 44, padding: '0 20px', border: '1px solid var(--plume-night)', borderRadius: 3, background: 'transparent', color: 'var(--plume-night)', font: '600 13px Inter, sans-serif', cursor: codeInput.trim() && !validating ? 'pointer' : 'not-allowed', opacity: codeInput.trim() ? 1 : 0.5 }}
                >
                  {validating ? 'Vérification…' : 'Appliquer'}
                </button>
                {promo.status === 'ok' && (
                  <button type="button" onClick={removeCode} data-testid="cart-promo-remove" style={{ minHeight: 44, padding: '0 8px', border: 0, background: 'transparent', color: 'var(--pa-muted)', font: '13px Inter, sans-serif', textDecoration: 'underline', cursor: 'pointer' }}>
                    Retirer
                  </button>
                )}
              </div>
              {promo.status === 'ok' && (
                <p data-testid="cart-promo-ok" style={{ margin: '10px 0 0', color: '#2F6B3F', font: '13px/1.5 Inter, sans-serif' }}>
                  Code {promoCode} appliqué. {promo.message}
                  {promo.adminOnly ? ' Cette remise nécessite un compte administrateur au paiement.' : ''}
                </p>
              )}
              {promo.status === 'ko' && (
                <p data-testid="cart-promo-ko" style={{ margin: '10px 0 0', color: '#A33A3A', font: '13px/1.5 Inter, sans-serif' }}>{promo.message}</p>
              )}
              <p style={{ margin: '10px 0 0', color: 'var(--pa-muted)', font: '12px/1.5 Inter, sans-serif' }}>
                Le code est repris automatiquement sur la page de paiement de chaque lecture.
              </p>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 20, padding: '24px 0', borderBottom: '1px solid rgba(17,22,37,0.14)' }}>
              <div>
                <strong style={{ color: 'var(--plume-night)', font: '600 14px Inter, sans-serif' }}>Total</strong>
                {discount > 0 && (
                  <p data-testid="cart-discount" style={{ margin: '5px 0 0', color: '#2F6B3F', font: '12px/1.5 Inter, sans-serif' }}>
                    Remise : −{formatPrice(discount)} (au lieu de {formatPrice(total)})
                  </p>
                )}
                <p style={{ margin: '5px 0 0', color: 'var(--pa-muted)', font: '12px/1.5 Inter, sans-serif' }}>
                  Chaque lecture est réglée sur son propre parcours, qui recueille vos informations de naissance.
                </p>
              </div>
              <strong data-testid="cart-total" style={{ color: 'var(--plume-night)', font: '600 20px Inter, sans-serif', whiteSpace: 'nowrap' }}>{formatPrice(finalTotal)}</strong>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: 16, paddingTop: 20 }}>
              <button type="button" onClick={clearCart} data-testid="cart-clear" style={{ minHeight: 44, padding: '0 8px', border: 0, background: 'transparent', color: 'var(--pa-muted)', font: '13px Inter, sans-serif', textDecoration: 'underline', textUnderlineOffset: 4, cursor: 'pointer' }}>
                Vider le panier
              </button>
              <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 16 }}>
                <Link to="/" style={{ color: 'var(--plume-night)', font: '600 13px Inter, sans-serif', textDecorationColor: 'var(--plume-gold)', textUnderlineOffset: 4 }}>
                  Ajouter d&apos;autres lectures
                </Link>
                <Link
                  to={firstItem.to}
                  onClick={() => startCheckout(firstItem.key)}
                  data-testid="cart-finalize"
                  style={{ display: 'inline-flex', minHeight: 48, alignItems: 'center', gap: 10, padding: '0 22px', borderRadius: 3, background: 'var(--plume-gold)', color: 'var(--plume-night)', font: '600 14px Inter, sans-serif', textDecoration: 'none' }}
                >
                  Finaliser ma commande <ArrowRight size={16} aria-hidden="true" />
                </Link>
              </div>
            </div>
          </>
        )}
      </main>
    </PsPageShell>
  );
}