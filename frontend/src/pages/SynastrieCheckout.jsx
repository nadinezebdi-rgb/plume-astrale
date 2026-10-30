import {useEffect, useMemo, useState} from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Loader2, ShieldCheck } from 'lucide-react';
import SEO from '@/components/SEO';
import { event as trackEvent } from '../lib/analytics';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const INPUT_STYLE = {
  width: '100%',
  padding: '12px 14px',
  background: 'rgba(15,26,60,0.6)',
  border: '1px solid rgba(212,175,55,0.3)',
  borderRadius: 4,
  color: '#F5EEE0',
  fontSize: 14,
  fontFamily: 'Inter, sans-serif',
  boxSizing: 'border-box',
  outline: 'none',
};

const LABEL_STYLE = {
  display: 'block',
  fontFamily: '"Cinzel", serif',
  fontSize: 10,
  letterSpacing: '0.18em',
  textTransform: 'uppercase',
  color: 'rgba(212,175,55,0.85)',
  marginBottom: 6,
};

/**
 * /synastrie/checkout — page de paiement 49€ dédiée synastrie.
 * Collecte les 2 personnes + email → POST /api/synastrie/checkout → redirect Stripe.
 * Pré-remplit depuis localStorage.plume_astrale_data et passe ab_variant/session_id.
 */
export default function SynastrieCheckout() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [p1, setP1] = useState({ prenom: '', birth_date: '', birth_place: 'Paris, France' });
  const [p2, setP2] = useState({ prenom: '', birth_date: '', birth_place: 'Paris, France' });
  const [state, setState] = useState({ status: 'idle', message: '' });

  // Lire les params AB depuis localStorage/sessionStorage (set par ExitIntentModal / LeadMagnet)
  const abContext = useMemo(() => {
    try {
      return {
        ab_variant: localStorage.getItem('plume_syn_exit_intent_variant') || undefined,
        ab_session_id: sessionStorage.getItem('plume_ab_sid') || undefined,
      };
    } catch {
      return {};
    }
  }, []);

  // Pré-remplissage depuis le profil local
  useEffect(() => {
    try {
      const raw = localStorage.getItem('plume_astrale_data');
      if (!raw) return;
      const data = JSON.parse(raw);
      if (data?.prenom || data?.dateNaissance) {
        setP1((prev) => ({
          ...prev,
          prenom: prev.prenom || data?.prenom || '',
          birth_date: prev.birth_date || data?.dateNaissance || '',
          birth_place: data?.lieuNaissance || data?.birth_place || prev.birth_place,
        }));
      }
      if (data?.email) setEmail((prev) => prev || data.email);
    } catch { /* noop */ }
  }, []);

  useEffect(() => {
    try { trackEvent('begin_checkout', { product: 'synastrie', value: 49, currency: 'EUR' }); } catch { /* noop */ }
  }, []);

  const update1 = (k, v) => setP1((prev) => ({ ...prev, [k]: v }));
  const update2 = (k, v) => setP2((prev) => ({ ...prev, [k]: v }));

  const canSubmit = email.trim() && p1.prenom.trim() && p1.birth_date && p2.prenom.trim() && p2.birth_date && state.status !== 'loading';

  const submit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    setState({ status: 'loading', message: '' });
    try {
      const res = await fetch(`${API_URL}/api/synastrie/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.trim(),
          origin_url: window.location.origin,
          person1: {
            prenom: p1.prenom.trim(),
            birth_date: p1.birth_date,
            birth_place: p1.birth_place || 'Paris, France',
          },
          person2: {
            prenom: p2.prenom.trim(),
            birth_date: p2.birth_date,
            birth_place: p2.birth_place || 'Paris, France',
          },
          ...abContext,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.checkout_url) {
        throw new Error(data?.detail || data?.message || 'Erreur à la création du paiement');
      }
      try { trackEvent('add_payment_info', { product: 'synastrie', value: 49, currency: 'EUR', variant: abContext.ab_variant || null }); } catch { /* noop */ }
      // Redirect vers Stripe Checkout
      window.location.href = data.checkout_url;
    } catch (err) {
      setState({ status: 'error', message: err.message || 'Impossible de démarrer le paiement, réessayez.' });
    }
  };

  return (
    <>
      <SEO
        path="/synastrie/checkout"
        title="Paiement sécurisé · Synastrie Plume Astrale"
        description="Finalisez votre rapport synastrie complet 25 pages · 49€, livré par email en moins de 10 minutes."
      />
      <main
        data-testid="synastrie-checkout-page"
        style={{ minHeight: '80vh', padding: '72px 20px', background: 'linear-gradient(180deg,#0F1A3A 0%, #0C132E 100%)', color: '#F5EEE0' }}
      >
        <div style={{ maxWidth: 720, margin: '0 auto', padding: '36px 32px', background: 'rgba(11,26,46,0.65)', border: '1px solid rgba(212,175,55,0.25)', borderRadius: 10, backdropFilter: 'blur(8px)' }}>
          <button
            onClick={() => navigate(-1)}
            data-testid="synastrie-checkout-back"
            style={{ background: 'transparent', border: 'none', color: 'rgba(244,239,230,0.6)', fontSize: 12, cursor: 'pointer', marginBottom: 16 }}
          >
            ← Retour
          </button>
          <p style={{ fontFamily: '"Cinzel", serif', fontSize: 11, letterSpacing: '0.3em', textTransform: 'uppercase', color: '#D4AF37', margin: '0 0 10px' }}>
            Rapport complet · 25 pages
          </p>
          <h1 style={{ fontFamily: '"Fraunces", "Playfair Display", serif', fontVariationSettings: "'opsz' 144, 'SOFT' 50", fontWeight: 400, fontSize: 'clamp(28px, 3.6vw, 36px)', lineHeight: 1.15, letterSpacing: '-0.01em', margin: '0 0 10px' }}>
            Votre synastrie, <em style={{ fontStyle: 'italic', color: '#E8A5B9' }}>composée pour vous.</em>
          </h1>
          <p style={{ color: 'rgba(244,239,230,0.78)', fontSize: 15, lineHeight: 1.6, margin: '0 0 28px' }}>
            Entrez les 2 dates de naissance, et nous générons votre rapport 25 pages (livré par email en moins de 10 min).
          </p>

          <form onSubmit={submit} data-testid="synastrie-checkout-form">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 20, marginBottom: 20 }}>
              <div style={cardStyle} data-testid="synastrie-checkout-person1">
                <h3 style={h3Style}>Vous</h3>
                <label style={LABEL_STYLE}>Prénom</label>
                <input type="text" value={p1.prenom} onChange={(e) => update1('prenom', e.target.value)} placeholder="Marie" style={INPUT_STYLE} data-testid="synastrie-checkout-p1-prenom" required />
                <label style={{ ...LABEL_STYLE, marginTop: 14 }}>Date de naissance</label>
                <input type="date" value={p1.birth_date} onChange={(e) => update1('birth_date', e.target.value)} style={INPUT_STYLE} data-testid="synastrie-checkout-p1-date" required />
                <label style={{ ...LABEL_STYLE, marginTop: 14 }}>Lieu de naissance</label>
                <input type="text" value={p1.birth_place} onChange={(e) => update1('birth_place', e.target.value)} placeholder="Paris, France" style={INPUT_STYLE} data-testid="synastrie-checkout-p1-place" required />
              </div>
              <div style={cardStyle} data-testid="synastrie-checkout-person2">
                <h3 style={h3Style}>L&apos;autre</h3>
                <label style={LABEL_STYLE}>Prénom</label>
                <input type="text" value={p2.prenom} onChange={(e) => update2('prenom', e.target.value)} placeholder="Jules" style={INPUT_STYLE} data-testid="synastrie-checkout-p2-prenom" required />
                <label style={{ ...LABEL_STYLE, marginTop: 14 }}>Date de naissance</label>
                <input type="date" value={p2.birth_date} onChange={(e) => update2('birth_date', e.target.value)} style={INPUT_STYLE} data-testid="synastrie-checkout-p2-date" required />
                <label style={{ ...LABEL_STYLE, marginTop: 14 }}>Lieu de naissance</label>
                <input type="text" value={p2.birth_place} onChange={(e) => update2('birth_place', e.target.value)} placeholder="Lyon, France" style={INPUT_STYLE} data-testid="synastrie-checkout-p2-place" required />
              </div>
            </div>

            <label style={LABEL_STYLE}>Votre email (livraison du rapport)</label>
            <div style={{ position: 'relative', marginBottom: 24 }}>
              <Mail size={16} style={{ position: 'absolute', top: 15, left: 14, color: 'rgba(212,175,55,0.65)' }} strokeWidth={1.6} />
              <input id="syn-checkout-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="vous@exemple.fr" style={{ ...INPUT_STYLE, paddingLeft: 40 }} data-testid="synastrie-checkout-email" required />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 14 }}>
              <div>
                <div style={{ fontFamily: '"Fraunces", serif', fontSize: 36, color: '#D4AF37', fontWeight: 400, lineHeight: 1 }}>49€</div>
                <div style={{ fontSize: 11, letterSpacing: '0.14em', color: 'rgba(244,239,230,0.6)', textTransform: 'uppercase' }}>
                  Paiement unique · 25 pages · 10 min
                </div>
              </div>
              <button
                type="submit"
                disabled={!canSubmit}
                data-testid="synastrie-checkout-submit"
                style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '15px 32px', background: canSubmit ? 'linear-gradient(135deg,#D4AF37,#E8C766)' : 'rgba(212,175,55,0.3)', color: '#0F1A3C', border: 'none', borderRadius: 4, fontFamily: '"Cinzel", serif', fontSize: 13, letterSpacing: '0.2em', textTransform: 'uppercase', fontWeight: 600, cursor: canSubmit ? 'pointer' : 'not-allowed' }}
              >
                {state.status === 'loading' ? <><Loader2 size={16} className="animate-spin" />Préparation…</> : <>Payer · 49€</>}
              </button>
            </div>

            {state.status === 'error' && (
              <p data-testid="synastrie-checkout-error" style={{ margin: 0, color: '#F87171', fontSize: 13 }}>{state.message}</p>
            )}
          </form>

          <div style={{ marginTop: 28, paddingTop: 20, borderTop: '1px solid rgba(244,239,230,0.08)', display: 'flex', gap: 10, alignItems: 'center', fontSize: 12, color: 'rgba(244,239,230,0.55)' }}>
            <ShieldCheck size={14} strokeWidth={1.6} style={{ color: '#4ADE80' }} />
            Paiement sécurisé par Stripe · Remboursement 14 jours · Vos données ne sont jamais revendues
          </div>
        </div>
      </main>
    </>
  );
}

const h3Style = {
  margin: '0 0 14px',
  fontFamily: '"Fraunces", "Playfair Display", serif',
  fontVariationSettings: "'opsz' 144, 'SOFT' 50",
  fontWeight: 400,
  fontSize: 18,
  color: 'rgba(244,239,230,0.9)',
};
const cardStyle = {
  padding: '18px 18px 20px',
  background: 'rgba(255,255,255,0.03)',
  border: '1px solid rgba(212,175,55,0.18)',
  borderRadius: 6,
};
