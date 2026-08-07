import React, { useEffect, useState } from 'react';
import { X, Gift, Send, CheckCircle2, AlertCircle } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * GiftModal — formulaire "Offrir cette lecture" avec message personnalisé.
 * Props :
 *   open, onClose, productSlug, productLabel, productPrice
 */
export default function GiftModal({ open, onClose, productSlug, productLabel, productPrice }) {
  const [form, setForm] = useState({
    buyer_name: '', buyer_email: '',
    recipient_name: '', recipient_email: '',
    occasion: '', message: '',
  });
  const [status, setStatus] = useState({ state: 'idle', message: '', url: '' });

  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = '';
    };
  }, [open, onClose]);

  useEffect(() => {
    if (open) setStatus({ state: 'idle', message: '', url: '' });
  }, [open, productSlug]);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    if (status.state === 'loading') return;
    setStatus({ state: 'loading', message: '', url: '' });
    try {
      const r = await fetch(`${API}/api/gift/reserve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, product_slug: productSlug }),
      });
      const data = await r.json().catch(() => ({}));
      if (!r.ok) {
        setStatus({ state: 'error', message: data.detail || 'Une erreur est survenue.' });
        return;
      }
      setStatus({ state: 'success', message: data.message, url: data.checkout_url || '' });
    } catch {
      setStatus({ state: 'error', message: 'Impossible de contacter le serveur.' });
    }
  };

  if (!open) return null;

  return (
    <div data-testid="gift-modal-overlay" onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 500,
        background: 'rgba(15,26,60,0.72)', backdropFilter: 'blur(8px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: 24, animation: 'fadeIn 200ms ease',
      }}>
      <div data-testid="gift-modal" onClick={(e) => e.stopPropagation()}
        style={{
          background: '#F7F5F0', borderRadius: 16,
          maxWidth: 640, width: '100%',
          maxHeight: '90vh', overflowY: 'auto',
          border: '1px solid #E3E1DC',
          boxShadow: '0 40px 80px rgba(0,0,0,0.35)',
        }}>
        {/* Header */}
        <div style={{
          position: 'sticky', top: 0, zIndex: 2,
          background: '#F7F5F0',
          borderBottom: '1px solid #E3E1DC',
          padding: '20px 28px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 40, height: 40, borderRadius: 10,
              background: 'rgba(201,162,75,0.12)',
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Gift style={{ width: 18, height: 18, color: '#C9A24B' }} strokeWidth={1.8} />
            </div>
            <div>
              <div style={{
                fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 600,
                letterSpacing: '0.16em', textTransform: 'uppercase', color: '#C9A24B',
              }}>Offrir cette lecture</div>
              <div style={{
                fontFamily: 'Playfair Display, serif', fontSize: 20, fontWeight: 500,
                color: '#0F1A3C', lineHeight: 1.2,
              }}>{productLabel} · {productPrice}</div>
            </div>
          </div>
          <button onClick={onClose} data-testid="gift-modal-close" aria-label="Fermer"
            style={{
              background: 'transparent', border: 'none', cursor: 'pointer',
              width: 40, height: 40, borderRadius: 999, color: '#6B7280',
            }}>
            <X style={{ width: 22, height: 22 }} strokeWidth={1.8} />
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '28px' }}>
          {status.state === 'success' ? (
            <div style={{ textAlign: 'center', padding: '20px 0' }} data-testid="gift-success">
              <div style={{
                width: 64, height: 64, borderRadius: 999,
                background: '#EDF7F1', display: 'inline-flex',
                alignItems: 'center', justifyContent: 'center', marginBottom: 20,
              }}>
                <CheckCircle2 style={{ width: 32, height: 32, color: '#3C7A5A' }} strokeWidth={1.5} />
              </div>
              <h3 style={{
                fontFamily: 'Playfair Display, serif',
                fontSize: 24, color: '#0F1A3C', marginBottom: 12,
              }}>
                Ton cadeau est <span className="ps-italic">réservé.</span>
              </h3>
              <p style={{
                fontFamily: 'Inter, sans-serif', fontSize: 15, lineHeight: 1.6,
                color: '#232323', margin: 0, marginBottom: 24, maxWidth: 400,
                marginLeft: 'auto', marginRight: 'auto',
              }}>{status.message}</p>
              {status.url && (
                <a href={status.url} className="ps-btn ps-btn-primary"
                  data-testid="gift-checkout-link"
                  style={{ padding: '14px 28px' }}>
                  Finaliser le paiement
                </a>
              )}
            </div>
          ) : (
            <form onSubmit={onSubmit} data-testid="gift-form" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <p style={{
                fontFamily: 'Inter, sans-serif', fontSize: 14, lineHeight: 1.55,
                color: '#6B7280', margin: 0, marginBottom: 4,
              }}>
                Écris quelques mots à la personne à qui tu offres cette lecture — nous
                composerons un joli bon cadeau PDF que tu pourras lui transmettre quand tu voudras.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <FieldInput label="Ton prénom" name="buyer_name" value={form.buyer_name} onChange={onChange} required />
                <FieldInput label="Ton email" name="buyer_email" type="email" value={form.buyer_email} onChange={onChange} required />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <FieldInput label="Prénom du/de la destinataire" name="recipient_name" value={form.recipient_name} onChange={onChange} required />
                <FieldInput label="Occasion (optionnel)" name="occasion" placeholder="Anniversaire, Noël…" value={form.occasion} onChange={onChange} />
              </div>

              <div className="ps-field">
                <label className="ps-label" htmlFor="g-message">Ton petit mot pour elle/lui</label>
                <textarea id="g-message" name="message"
                  className="ps-input" rows={4} maxLength={1000}
                  data-testid="gift-message"
                  placeholder="Un mot doux, une intention, quelques lignes qu'elle lira en ouvrant son cadeau…"
                  value={form.message} onChange={onChange}
                  style={{ resize: 'vertical', minHeight: 100, fontFamily: 'Inter, sans-serif' }} />
                <span className="ps-caption" style={{ textAlign: 'right' }}>
                  {form.message.length}/1000
                </span>
              </div>

              {status.state === 'error' && (
                <div data-testid="gift-error" style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  padding: '10px 14px',
                  background: '#FBEEEA', border: '1px solid #B4442E',
                  borderRadius: 10, color: '#6E2A1B',
                  fontFamily: 'Inter, sans-serif', fontSize: 14,
                }}>
                  <AlertCircle style={{ width: 16, height: 16 }} strokeWidth={2} />
                  {status.message}
                </div>
              )}

              <button type="submit" disabled={status.state === 'loading'}
                className="ps-btn ps-btn-primary" data-testid="gift-submit"
                style={{
                  justifyContent: 'center', padding: '14px 28px', marginTop: 4,
                  opacity: status.state === 'loading' ? 0.7 : 1,
                }}>
                {status.state === 'loading' ? 'Envoi…' : (
                  <>Offrir cette lecture · {productPrice}<Send style={{ width: 16, height: 16 }} strokeWidth={2} /></>
                )}
              </button>
              <p className="ps-caption" style={{ textAlign: 'center', margin: 0 }}>
                Tu recevras un email pour finaliser le paiement en toute sécurité.
              </p>
            </form>
          )}
        </div>
      </div>
      <style>{`@keyframes fadeIn { from{opacity:0} to{opacity:1} }`}</style>
    </div>
  );
}

function FieldInput({ label, name, type = 'text', value, onChange, required, placeholder }) {
  return (
    <div className="ps-field">
      <label className="ps-label" htmlFor={`g-${name}`}>{label}</label>
      <input id={`g-${name}`} name={name} type={type}
        className="ps-input" value={value} onChange={onChange}
        placeholder={placeholder} required={required}
        data-testid={`gift-input-${name}`}
        autoComplete={type === 'email' ? 'email' : 'off'} />
    </div>
  );
}
