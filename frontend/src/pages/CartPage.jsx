import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ShoppingCart, Trash2 } from 'lucide-react';
import SEO from '@/components/SEO';
import PsPageShell from '@/components/PsPageShell';
import { useCart } from '@/context/CartContext';

const formatPrice = (amount) => new Intl.NumberFormat('fr-FR', {
  style: 'currency',
  currency: 'EUR',
}).format(amount);

export default function CartPage() {
  const { items, total, removeItem, clearCart } = useCart();

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
                  <strong style={{ color: 'var(--plume-night)', font: '600 14px Inter, sans-serif', whiteSpace: 'nowrap' }}>{item.price}</strong>
                  <button
                    type="button"
                    aria-label={`Retirer ${item.title} du panier`}
                    data-testid={`cart-remove-${item.key}`}
                    onClick={() => removeItem(item.key)}
                    style={{ display: 'grid', width: 40, height: 40, placeItems: 'center', border: '1px solid rgba(17,22,37,0.16)', borderRadius: 4, background: 'transparent', color: 'var(--plume-night)', cursor: 'pointer' }}
                  >
                    <Trash2 size={17} aria-hidden="true" />
                  </button>
                  <Link to={item.to} data-testid={`cart-checkout-${item.key}`} style={{ gridColumn: '1 / -1', justifySelf: 'start', color: 'var(--plume-night)', font: '600 13px Inter, sans-serif', textDecorationColor: 'var(--plume-gold)', textUnderlineOffset: 4 }}>
                    Continuer vers cette lecture <ArrowRight size={14} aria-hidden="true" style={{ verticalAlign: 'middle' }} />
                  </Link>
                </li>
              ))}
            </ul>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 20, padding: '24px 0', borderBottom: '1px solid rgba(17,22,37,0.14)' }}>
              <div>
                <strong style={{ color: 'var(--plume-night)', font: '600 14px Inter, sans-serif' }}>Total indicatif</strong>
                <p style={{ margin: '5px 0 0', color: 'var(--pa-muted)', font: '12px/1.5 Inter, sans-serif' }}>
                  Chaque lecture se finalise sur son parcours d&apos;achat dédié.
                </p>
              </div>
              <strong data-testid="cart-total" style={{ color: 'var(--plume-night)', font: '600 20px Inter, sans-serif', whiteSpace: 'nowrap' }}>{formatPrice(total)}</strong>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: 16, paddingTop: 20 }}>
              <button type="button" onClick={clearCart} data-testid="cart-clear" style={{ minHeight: 44, padding: '0 8px', border: 0, background: 'transparent', color: 'var(--pa-muted)', font: '13px Inter, sans-serif', textDecoration: 'underline', textUnderlineOffset: 4, cursor: 'pointer' }}>
                Vider le panier
              </button>
              <Link to="/" style={{ display: 'inline-flex', minHeight: 48, alignItems: 'center', gap: 10, padding: '0 20px', borderRadius: 3, background: 'var(--plume-gold)', color: 'var(--plume-night)', font: '600 13px Inter, sans-serif', textDecoration: 'none' }}>
                Ajouter d&apos;autres lectures <ArrowRight size={16} aria-hidden="true" />
              </Link>
            </div>
          </>
        )}
      </main>
    </PsPageShell>
  );
}