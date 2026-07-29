import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, Loader2, Star, Moon, Sun } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import { useAuth } from '@/context/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL;

const ThemeNatalOneshot = () => {
  const { user } = useAuth();
  const nav = useNavigate();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    email: user?.email || '',
    first_name: user?.prenom || user?.first_name || '',
    birth_date: '',
    birth_time: '',
    birth_city: 'Paris',
    birth_country: 'FR',
    latitude: 48.8566,
    longitude: 2.3522,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [promoCode, setPromoCode] = useState('');

  const upd = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const handleCheckout = async () => {
    setError(null);
    if (!form.email || !form.email.includes('@')) return setError('Email invalide');
    if (!form.first_name.trim()) return setError('Prénom requis');
    if (!form.birth_date || !form.birth_time) return setError('Date et heure de naissance requises');
    setLoading(true);
    try {
      const r = await axios.post(`${API}/api/theme-natal-oneshot/checkout`, {
        ...form,
        origin_url: window.location.origin,
        promo_code: promoCode.trim() || undefined,
      });
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
                    Date naiss.
                  </label>
                  <input
                    type="date"
                    value={form.birth_date}
                    onChange={(e) => upd('birth_date', e.target.value)}
                    data-testid="theme-natal-oneshot-birthdate"
                    className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60"
                  />
                </div>
                <div>
                  <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>
                    Heure naiss.
                  </label>
                  <input
                    type="time"
                    value={form.birth_time}
                    onChange={(e) => upd('birth_time', e.target.value)}
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
                  style={{ color: 'rgba(212,175,55,0.65)', letterSpacing: '0.2em' }}
                >
                  Code promo (optionnel)
                </label>
                <input
                  type="text"
                  value={promoCode}
                  onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
                  placeholder="Ex: ADMIN26"
                  data-testid="theme-natal-oneshot-promo"
                  className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/40 border border-plume-gold/15 text-plume-lavender focus:outline-none focus:border-plume-gold/50"
                  style={{ letterSpacing: '0.2em', fontFamily: 'Cinzel, serif', fontSize: 13 }}
                />
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
                ) : promoCode.trim() ? (
                  <>
                    Déverrouiller mon Thème <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
                  </>
                ) : (
                  <>
                    Payer 29€ et recevoir mon Thème <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
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
