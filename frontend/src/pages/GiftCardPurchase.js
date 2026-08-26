import React, { useEffect, useState } from 'react';
import { Gift, Heart, Loader2 } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * /carte-cadeau — Landing d'achat de la carte cadeau Plume Astrale.
 * Résout l'objection "je n'ai pas son heure de naissance" (audit 2026-02-26).
 */
export default function GiftCardPurchase() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({
    product_kind: 'theme_natal',
    purchaser_first_name: '',
    purchaser_email: '',
    recipient_first_name: '',
    recipient_email: '',
    personal_message: '',
  });
  const [status, setStatus] = useState('idle'); // idle | loading | error
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API}/api/gift-cards/products`)
      .then((r) => r.json())
      .then((d) => setProducts(d.products || []))
      .catch(() => setProducts([]));
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setStatus('loading');
    setError(null);
    try {
      const res = await fetch(`${API}/api/gift-cards/purchase`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) {
        setStatus('error');
        setError(data?.detail || 'Impossible de créer le paiement pour l\'instant.');
        return;
      }
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (err) {
      setStatus('error');
      setError('Connexion interrompue. Réessayez dans un instant.');
    }
  }

  const selectedProduct = products.find((p) => p.kind === form.product_kind);
  const priceLabel = selectedProduct ? `${(selectedProduct.price_cents / 100).toFixed(0)}€` : '';

  return (
    <PsPageShell background="dark">
      <SEO
        path="/carte-cadeau"
        title="Offrir un livre Plume Astrale · Carte cadeau"
        description="Offre un livre composé sur mesure — même sans son heure de naissance. Ta carte cadeau arrive par email, le destinataire complète ses données à son rythme."
      />
      <div style={{ maxWidth: 720, margin: '0 auto', padding: '64px 24px', color: '#F5EEE0', fontFamily: '"Cormorant Garamond", serif' }}>
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <Gift size={40} color="#D4AF37" strokeWidth={1.4} />
          <h1 style={{ fontFamily: '"Playfair Display", serif', fontSize: '2.4rem', margin: '18px 0 8px' }}>
            Offrir un livre Plume Astrale
          </h1>
          <p style={{ color: '#B9B0D5', maxWidth: 560, margin: '0 auto', lineHeight: 1.6 }}>
            Pas besoin de son heure de naissance. Tu paies aujourd&apos;hui, elle reçoit un code par
            email et complète ses données à son rythme. Le livre arrive quelques minutes après.
          </p>
        </div>

        <form onSubmit={handleSubmit} data-testid="gift-card-purchase-form" style={{ display: 'grid', gap: 20 }}>
          {/* Produit */}
          <label style={{ display: 'grid', gap: 8 }}>
            <span style={{ fontSize: '0.75rem', letterSpacing: 2, color: '#D4AF37', fontFamily: '"Cinzel", serif' }}>
              LE LIVRE À OFFRIR
            </span>
            <select
              value={form.product_kind}
              onChange={(e) => setForm({ ...form, product_kind: e.target.value })}
              data-testid="gift-product-select"
              style={inputStyle}
            >
              {products.map((p) => (
                <option key={p.kind} value={p.kind}>
                  {p.label} — {(p.price_cents / 100).toFixed(0)}€
                </option>
              ))}
            </select>
            {selectedProduct && (
              <small style={{ color: '#B9B0D5', fontStyle: 'italic' }}>{selectedProduct.description}</small>
            )}
          </label>

          <fieldset style={fieldsetStyle}>
            <legend style={legendStyle}>VOS COORDONNÉES (POUR LE REÇU)</legend>
            <div style={rowStyle}>
              <input required placeholder="Votre prénom" data-testid="gift-purchaser-name"
                     value={form.purchaser_first_name}
                     onChange={(e) => setForm({ ...form, purchaser_first_name: e.target.value })}
                     style={inputStyle} />
              <input required type="email" placeholder="votre@email.fr" data-testid="gift-purchaser-email"
                     value={form.purchaser_email}
                     onChange={(e) => setForm({ ...form, purchaser_email: e.target.value })}
                     style={inputStyle} />
            </div>
          </fieldset>

          <fieldset style={fieldsetStyle}>
            <legend style={legendStyle}>LE DESTINATAIRE</legend>
            <div style={rowStyle}>
              <input placeholder="Son prénom (optionnel)" data-testid="gift-recipient-name"
                     value={form.recipient_first_name}
                     onChange={(e) => setForm({ ...form, recipient_first_name: e.target.value })}
                     style={inputStyle} />
              <input required type="email" placeholder="son@email.fr" data-testid="gift-recipient-email"
                     value={form.recipient_email}
                     onChange={(e) => setForm({ ...form, recipient_email: e.target.value })}
                     style={inputStyle} />
            </div>
            <textarea placeholder="Message personnel (facultatif — 800 caractères max)"
                      data-testid="gift-personal-message"
                      maxLength={800} rows={4}
                      value={form.personal_message}
                      onChange={(e) => setForm({ ...form, personal_message: e.target.value })}
                      style={{ ...inputStyle, marginTop: 12, resize: 'vertical', fontFamily: 'inherit' }} />
          </fieldset>

          {error && (
            <div data-testid="gift-error" style={{ padding: 14, background: 'rgba(220,60,60,0.12)', border: '1px solid rgba(220,60,60,0.4)', borderRadius: 4, color: '#F5C6C6' }}>
              {error}
            </div>
          )}

          <button type="submit" disabled={status === 'loading'} data-testid="gift-submit-btn"
                  style={{
                    padding: '16px 32px',
                    background: 'linear-gradient(135deg, #D4AF37, #E8C766)',
                    color: '#0F1A3C',
                    border: 'none', borderRadius: 4, cursor: status === 'loading' ? 'wait' : 'pointer',
                    fontFamily: '"Cinzel", serif', fontSize: '0.95rem', letterSpacing: 3,
                    display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 10,
                  }}>
            {status === 'loading' ? (
              <><Loader2 size={18} className="animate-spin" /> Redirection Stripe…</>
            ) : (
              <><Heart size={18} strokeWidth={1.6} /> OFFRIR CE LIVRE {priceLabel && `· ${priceLabel}`}</>
            )}
          </button>

          <p style={{ fontSize: '0.85rem', color: '#B9B0D5', textAlign: 'center', marginTop: 8 }}>
            Paiement sécurisé Stripe · Garantie 14 jours · Livraison immédiate au destinataire
          </p>
        </form>
      </div>
    </PsPageShell>
  );
}

const inputStyle = {
  padding: '12px 14px',
  background: 'rgba(15,26,60,0.55)',
  border: '1px solid rgba(212,175,55,0.28)',
  borderRadius: 4,
  color: '#F5EEE0',
  fontSize: '1rem',
  fontFamily: '"Cormorant Garamond", serif',
  width: '100%',
  boxSizing: 'border-box',
};
const fieldsetStyle = { border: '1px solid rgba(212,175,55,0.15)', borderRadius: 6, padding: 20 };
const legendStyle = { fontSize: '0.72rem', letterSpacing: 2, color: '#D4AF37', fontFamily: '"Cinzel", serif', padding: '0 8px' };
const rowStyle = { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 };
