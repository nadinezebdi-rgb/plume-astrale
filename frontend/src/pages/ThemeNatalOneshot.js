import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, Loader2, Star, Moon, Sun, Check, X } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import { useAuth } from '@/context/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL;
const PACK_PRICE = 29;

// Helpers date FR : dd/MM/yyyy <-> yyyy-MM-dd (format API)
const fromISO = (iso) => {
  if (!iso || iso.length < 10) return '';
  const [y, m, d] = iso.slice(0, 10).split('-');
  return `${d}/${m}/${y}`;
};
const toISO = (fr) => {
  if (!fr) return '';
  const m = fr.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  if (!m) return '';
  return `${m[3]}-${m[2]}-${m[1]}`;
};
const applyDateMask = (v) => {
  const digits = v.replace(/\D/g, '').slice(0, 8);
  let out = digits;
  if (digits.length > 4) out = `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
  else if (digits.length > 2) out = `${digits.slice(0, 2)}/${digits.slice(2)}`;
  return out;
};
const applyTimeMask = (v) => {
  const digits = v.replace(/\D/g, '').slice(0, 4);
  if (digits.length > 2) return `${digits.slice(0, 2)}:${digits.slice(2)}`;
  return digits;
};

const ThemeNatalOneshot = () => {
  const { user, token, isAuthenticated } = useAuth();
  const nav = useNavigate();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    email: '', first_name: '', birth_date: '', birth_date_fr: '',
    birth_time: '', birth_city: '', birth_country: 'FR',
    latitude: null, longitude: null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [promoCode, setPromoCode] = useState('');
  const [promoState, setPromoState] = useState({ status: 'idle', message: '', discount_percent: 0, discount_amount: 0, final_amount: PACK_PRICE });
  const [validatingPromo, setValidatingPromo] = useState(false);

  // Pré-remplissage depuis /api/auth/me au chargement si authentifié
  useEffect(() => {
    if (!isAuthenticated || !token) return;
    (async () => {
      try {
        const r = await axios.get(`${API}/api/auth/me`, { headers: { Authorization: `Bearer ${token}` } });
        const u = r.data?.user || {};
        setForm((f) => ({
          ...f,
          email: u.email || f.email || '',
          first_name: u.prenom || f.first_name || '',
          birth_date: u.birth_date || f.birth_date || '',
          birth_date_fr: u.birth_date ? fromISO(u.birth_date) : f.birth_date_fr || '',
          birth_time: (u.birth_time || f.birth_time || '').slice(0, 5),
          birth_city: u.birth_place || f.birth_city || '',
          birth_country: u.birth_country || f.birth_country || 'FR',
          latitude: u.latitude ?? f.latitude,
          longitude: u.longitude ?? f.longitude,
        }));
      } catch (e) {
        // profil non chargeable — laisse champs vides pour saisie manuelle
      }
    })();
  }, [isAuthenticated, token]);

  const upd = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const applyPromo = async () => {
    const code = promoCode.trim();
    if (!code) return;
    setValidatingPromo(true);
    setPromoState({ status: 'idle', message: '', discount_percent: 0, discount_amount: 0, final_amount: PACK_PRICE });
    try {
      const r = await axios.post(`${API}/api/promo/validate`, { code, product: 'theme_natal_pdf_oneshot', amount: PACK_PRICE });
      const d = r.data || {};
      if (d.valid) {
        setPromoState({
          status: 'ok',
          message: d.message || 'Code appliqué.',
          discount_percent: d.discount_percent || 0,
          discount_amount: d.discount_amount || 0,
          final_amount: typeof d.final_amount === 'number' ? d.final_amount : PACK_PRICE,
          admin_only: d.admin_only,
          stripe_promo_id: d.stripe_promo_id,
          source: d.source,
        });
      } else {
        setPromoState({ status: 'ko', message: d.message || 'Code invalide ou expiré.', final_amount: PACK_PRICE });
      }
    } catch (e) {
      setPromoState({ status: 'ko', message: e.response?.data?.detail || 'Code invalide ou expiré.', final_amount: PACK_PRICE });
    } finally {
      setValidatingPromo(false);
    }
  };

  const handleCheckout = async () => {
    setError(null);
    if (!form.email || !form.email.includes('@')) return setError('Email invalide');
    if (!form.first_name.trim()) return setError('Prénom requis');
    // birth_date_fr est prioritaire (masque local), sinon utilise birth_date ISO existant
    const isoDate = form.birth_date || toISO(form.birth_date_fr);
    if (!isoDate || !form.birth_time) return setError('Date et heure de naissance requises (JJ/MM/AAAA et HH:MM)');
    if (!form.birth_city.trim()) return setError('Ville de naissance requise');
    setLoading(true);
    try {
      const r = await axios.post(
        `${API}/api/theme-natal-oneshot/checkout`,
        {
          email: form.email,
          first_name: form.first_name,
          birth_date: isoDate,
          birth_time: form.birth_time,
          birth_city: form.birth_city,
          birth_country: form.birth_country,
          latitude: form.latitude,
          longitude: form.longitude,
          origin_url: window.location.origin,
          promo_code: promoState.status === 'ok' && promoCode.trim() ? promoCode.trim() : undefined,
        },
        token ? { headers: { Authorization: `Bearer ${token}` } } : {},
      );
      if (r.data?.url) window.location.href = r.data.url;
      else setError('Une erreur est survenue');
    } catch (e) {
      setError(e.response?.data?.detail || 'Impossible de créer la session');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative" style={{ padding: '110px 20px 140px' }} data-testid="theme-natal-oneshot-page">
      <SEO
        path="/theme-natal"
        title="Ton Thème Natal Complet · 29€ · Plume Astrale"
        description="Un PDF luxe de 20 à 40 pages : tes 11 planètes, ton ascendant, tes maisons, tes aspects — enrichi par l'IA voix Soléna. Reçu par email en 3 minutes."
      />

      <div className="max-w-4xl mx-auto">
        {/* Hero */}
        <div className="text-center mb-14">
          <p
            className="text-[10px] uppercase mb-5"
            style={{ color: '#D4AF37', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}
          >
            ✦ Ton Portrait Céleste ✦
          </p>
          <h1
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontWeight: 300,
              lineHeight: 1.05,
              fontSize: 'clamp(38px, 6vw, 66px)',
              color: '#F5EEE0',
              marginBottom: 18,
            }}
            data-testid="theme-natal-oneshot-title"
          >
            Ton <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>Thème Natal</em>
            <br />
            Complet
          </h1>
          <p
            className="text-base md:text-lg max-w-2xl mx-auto mb-8"
            style={{
              color: 'rgba(227,215,255,0.85)',
              fontFamily: 'Cormorant Garamond, serif',
              fontStyle: 'italic',
              lineHeight: 1.6,
            }}
          >
            Un document luxe de 20 à 40 pages qui décode ton ciel de naissance —
            11 planètes, ascendant, maisons, aspects, enrichi par la voix de Soléna.
          </p>
          <div className="inline-flex items-baseline gap-2 mb-2" data-testid="theme-natal-oneshot-price">
            <span
              style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 48, fontWeight: 300, color: '#D4AF37' }}
            >
              29€
            </span>
            <span className="text-xs" style={{ color: 'rgba(227,215,255,0.55)', letterSpacing: '0.2em' }}>
              · PAIEMENT UNIQUE
            </span>
          </div>
          <p className="text-xs" style={{ color: 'rgba(227,215,255,0.45)', letterSpacing: '0.1em' }}>
            Livré par email dans les 3 minutes suivant le paiement
          </p>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
          {[
            { icon: Sun, title: 'Tes 11 planètes en signes & maisons', desc: 'Soleil, Lune, Mercure, Vénus, Mars, Jupiter, Saturne, Uranus, Neptune, Pluton, Chiron.' },
            { icon: Moon, title: 'Ton ascendant & tes 12 maisons', desc: 'Le décor complet de ta scène astrale — Placidus, avec cuspides précises.' },
            { icon: Star, title: 'Ta carte du ciel et tes aspects', desc: 'Wheel astral en HD + tous les aspects majeurs interprétés par l\'IA Soléna.' },
          ].map(({ icon: Icon, title, desc }, i) => (
            <div key={i} className="plume-glass p-6" data-testid={`theme-natal-oneshot-feature-${i}`}>
              <Icon className="w-7 h-7 mb-3" style={{ color: '#D4AF37' }} strokeWidth={1.2} />
              <h3
                className="text-lg mb-2"
                style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}
              >
                {title}
              </h3>
              <p className="text-sm" style={{ color: 'rgba(227,215,255,0.72)', lineHeight: 1.6 }}>
                {desc}
              </p>
            </div>
          ))}
        </div>

        {step === 0 ? (
          <div className="text-center">
            <button
              onClick={() => setStep(1)}
              className="plume-btn-primary"
              data-testid="theme-natal-oneshot-cta-start"
            >
              Recevoir mon Thème Natal — 29€
              <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
            </button>
            <p className="text-xs mt-4" style={{ color: 'rgba(227,215,255,0.5)', letterSpacing: '0.1em' }}>
              Paiement sécurisé Stripe · Sans engagement · TVA incluse
            </p>
          </div>
        ) : (
          <div className="plume-glass p-8 md:p-10 max-w-xl mx-auto" data-testid="theme-natal-oneshot-form">
            <h2
              className="text-2xl mb-6 text-center"
              style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}
            >
              Tes coordonnées astrales
            </h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>
                  E-mail pour la livraison
                </label>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => upd('email', e.target.value)}
                  data-testid="theme-natal-oneshot-email"
                  className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60"
                />
              </div>
              <div>
                <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>
                  Prénom
                </label>
                <input
                  type="text"
                  value={form.first_name}
                  onChange={(e) => upd('first_name', e.target.value)}
                  data-testid="theme-natal-oneshot-firstname"
                  className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>
                    Date naiss. (JJ/MM/AAAA)
                  </label>
                  <input
                    type="text"
                    inputMode="numeric"
                    placeholder="JJ/MM/AAAA"
                    maxLength={10}
                    value={form.birth_date_fr}
                    onChange={(e) => {
                      const masked = applyDateMask(e.target.value);
                      upd('birth_date_fr', masked);
                      upd('birth_date', toISO(masked));
                    }}
                    data-testid="theme-natal-oneshot-birthdate"
                    className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60"
                  />
                </div>
                <div>
                  <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>
                    Heure naiss. (HH:MM, 24h)
                  </label>
                  <input
                    type="text"
                    inputMode="numeric"
                    placeholder="HH:MM"
                    maxLength={5}
                    value={form.birth_time}
                    onChange={(e) => upd('birth_time', applyTimeMask(e.target.value))}
                    data-testid="theme-natal-oneshot-birthtime"
                    className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>
                  Ville de naissance
                </label>
                <input
                  type="text"
                  value={form.birth_city}
                  onChange={(e) => upd('birth_city', e.target.value)}
                  data-testid="theme-natal-oneshot-city"
                  className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60"
                />
              </div>
              <div>
                <label
                  className="text-xs uppercase"
                  style={{ color: 'rgba(212,175,55,0.75)', letterSpacing: '0.2em' }}
                >
                  Code promo (optionnel)
                </label>
                <div className="flex gap-2 mt-2">
                  <input
                    type="text"
                    value={promoCode}
                    onChange={(e) => {
                      setPromoCode(e.target.value.toUpperCase());
                      // reset state si l'utilisateur re-saisit
                      if (promoState.status !== 'idle') setPromoState({ status: 'idle', message: '', discount_percent: 0, discount_amount: 0, final_amount: PACK_PRICE });
                    }}
                    placeholder="Ex: TOUT2026"
                    data-testid="theme-natal-oneshot-promo"
                    className="flex-1 px-4 py-3 rounded-xl bg-plume-night-soft/40 border border-plume-gold/15 text-plume-lavender focus:outline-none focus:border-plume-gold/50"
                    style={{ letterSpacing: '0.2em', fontFamily: 'Cinzel, serif', fontSize: 13 }}
                  />
                  <button
                    type="button"
                    onClick={applyPromo}
                    disabled={!promoCode.trim() || validatingPromo}
                    data-testid="theme-natal-oneshot-promo-apply"
                    style={{
                      padding: '0 20px',
                      borderRadius: 12,
                      background: 'rgba(212,175,55,0.12)',
                      color: '#D4AF37',
                      border: '1px solid rgba(212,175,55,0.4)',
                      fontSize: 11,
                      letterSpacing: '0.15em',
                      textTransform: 'uppercase',
                      fontFamily: 'Cinzel, serif',
                      cursor: 'pointer',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {validatingPromo ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Appliquer le code'}
                  </button>
                </div>
                {promoState.status === 'ok' && (
                  <div
                    className="mt-3 p-3 rounded-lg flex items-start gap-2"
                    data-testid="theme-natal-oneshot-promo-ok"
                    style={{
                      background: 'rgba(74,222,128,0.10)',
                      border: '1px solid rgba(74,222,128,0.35)',
                    }}
                  >
                    <Check className="w-4 h-4 shrink-0 mt-0.5" style={{ color: '#4ADE80' }} strokeWidth={2} />
                    <div className="text-xs flex-1">
                      <div style={{ color: '#4ADE80', fontFamily: 'Cinzel, serif', letterSpacing: '0.1em', marginBottom: 4 }}>
                        CODE APPLIQUÉ
                      </div>
                      <div style={{ color: 'rgba(227,215,255,0.85)', lineHeight: 1.5, fontFamily: 'Cormorant Garamond, serif' }}>
                        {promoState.message}
                      </div>
                      <div className="mt-2 flex items-baseline gap-2">
                        <span style={{ color: 'rgba(227,215,255,0.5)', textDecoration: 'line-through', fontSize: 14 }}>
                          {PACK_PRICE.toFixed(2)}€
                        </span>
                        <span style={{ color: '#D4AF37', fontSize: 22, fontFamily: 'Cormorant Garamond, serif', fontWeight: 400 }}>
                          {promoState.final_amount === 0 ? 'Gratuit' : `${promoState.final_amount.toFixed(2)}€`}
                        </span>
                      </div>
                      {promoState.admin_only && (
                        <div style={{ color: 'rgba(232,199,102,0.75)', fontSize: 11, fontStyle: 'italic', marginTop: 4 }}>
                          Ce code nécessite un compte administrateur pour être appliqué.
                        </div>
                      )}
                    </div>
                  </div>
                )}
                {promoState.status === 'ko' && (
                  <div
                    className="mt-3 p-3 rounded-lg flex items-start gap-2"
                    data-testid="theme-natal-oneshot-promo-ko"
                    style={{ background: 'rgba(248,113,113,0.10)', border: '1px solid rgba(248,113,113,0.35)' }}
                  >
                    <X className="w-4 h-4 shrink-0 mt-0.5" style={{ color: '#F87171' }} strokeWidth={2} />
                    <div className="text-xs" style={{ color: '#F87171', fontFamily: 'Cormorant Garamond, serif' }}>
                      {promoState.message}
                    </div>
                  </div>
                )}
              </div>
              {error && (
                <p
                  className="text-sm text-center"
                  style={{ color: '#F87171' }}
                  data-testid="theme-natal-oneshot-error"
                >
                  {error}
                </p>
              )}
              <button
                onClick={handleCheckout}
                disabled={loading}
                className="plume-btn-primary w-full justify-center"
                data-testid="theme-natal-oneshot-checkout-btn"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> Redirection...
                  </>
                ) : promoState.status === 'ok' && promoState.final_amount === 0 ? (
                  <>
                    Déverrouiller mon Thème <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
                  </>
                ) : promoState.status === 'ok' ? (
                  <>
                    Payer {promoState.final_amount.toFixed(2)}€ et recevoir mon Thème <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
                  </>
                ) : (
                  <>
                    Payer {PACK_PRICE}€ et recevoir mon Thème <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
                  </>
                )}
              </button>
              <p
                className="text-[10px] text-center mt-3"
                style={{ color: 'rgba(227,215,255,0.4)', letterSpacing: '0.2em' }}
              >
                🔒 PAIEMENT SÉCURISÉ STRIPE · TVA INCLUSE
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ThemeNatalOneshot;
