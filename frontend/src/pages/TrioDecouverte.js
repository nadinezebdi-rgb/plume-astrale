import React, { useState } from 'react';
import { Sparkles, ArrowRight, Loader2, Check, Star, Moon, Sun, Zap } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import { useAuth } from '@/context/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL;

const INCLUDED = [
  { icon: Sun, name: 'Thème Natal Complet', price: 29, desc: 'PDF luxe 20-40 pages · 11 planètes + ascendant + maisons + aspects' },
  { icon: Star, name: 'Numérologie Sacrée', price: 19, desc: 'PDF 12 pages · chemin de vie, année personnelle, année maîtresse' },
  { icon: Moon, name: 'Arbre de Vie Kabbale', price: 39, desc: 'PDF 15 pages · les 10 sephiroth + tes correspondances' },
];

const TOTAL_INDIV = INCLUDED.reduce((s, i) => s + i.price, 0); // 87
const TRIO_PRICE = 79;
const SAVE = TOTAL_INDIV - TRIO_PRICE; // 12

const TrioDecouverte = () => {
  const { user } = useAuth();
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
      const r = await axios.post(`${API}/api/trio-decouverte/checkout`, {
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
    <div className="min-h-screen relative" style={{ padding: '110px 20px 140px' }} data-testid="trio-decouverte-page">
      <SEO
        path="/trio-decouverte"
        title="Trio Découverte · 79€ · Plume Astrale"
        description="Ton Thème Natal + ta Numérologie + ton Arbre de Vie Kabbale. 3 PDFs livrés en 5 minutes. Économise 12€ vs achats séparés."
      />

      <div className="max-w-4xl mx-auto">
        {/* Hero */}
        <div className="text-center mb-14">
          <p
            className="text-[10px] uppercase mb-5"
            style={{ color: '#D4AF37', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}
            data-testid="trio-decouverte-eyebrow"
          >
            ✦ Bundle Signature ✦
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
            data-testid="trio-decouverte-title"
          >
            Le <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>Trio</em>
            <br />
            Découverte
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
            Trois portraits sacrés — astral, numérique, kabbalistique — qui se répondent en écho.
            Livrés par email dans les 5 minutes.
          </p>

          <div className="inline-flex flex-col items-center gap-2 mb-2" data-testid="trio-decouverte-price">
            <div className="flex items-baseline gap-3">
              <span
                style={{
                  color: 'rgba(227,215,255,0.55)',
                  textDecoration: 'line-through',
                  fontSize: 22,
                  fontFamily: 'Cormorant Garamond, serif',
                }}
              >
                {TOTAL_INDIV}€
              </span>
              <span style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 58, fontWeight: 300, color: '#D4AF37', lineHeight: 1 }}>
                {TRIO_PRICE}€
              </span>
            </div>
            <div
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full"
              style={{
                background: 'linear-gradient(135deg, rgba(74,222,128,0.15), rgba(74,222,128,0.05))',
                border: '1px solid rgba(74,222,128,0.3)',
              }}
            >
              <Zap className="w-3 h-3" style={{ color: '#4ADE80' }} strokeWidth={2} />
              <span style={{ color: '#4ADE80', fontSize: 11, fontFamily: 'Cinzel, serif', letterSpacing: '0.15em' }}>
                ÉCONOMISE {SAVE}€
              </span>
            </div>
          </div>
          <p className="text-xs mt-3" style={{ color: 'rgba(227,215,255,0.45)', letterSpacing: '0.1em' }}>
            Paiement unique · 3 PDFs livrés par email dans les 5 minutes
          </p>
        </div>

        {/* What's included */}
        <div className="plume-glass p-6 md:p-8 mb-10" data-testid="trio-decouverte-included">
          <p
            className="text-[10px] uppercase mb-4 text-center"
            style={{ color: '#D4AF37', letterSpacing: '0.32em', fontFamily: 'Cinzel, serif' }}
          >
            ✦ Ce que tu reçois ✦
          </p>
          <div className="space-y-4">
            {INCLUDED.map((item, i) => {
              const Icon = item.icon;
              return (
                <div key={i} className="flex items-start gap-4 pb-4" style={{ borderBottom: i < INCLUDED.length - 1 ? '1px solid rgba(212,175,55,0.1)' : 'none' }} data-testid={`trio-included-${i}`}>
                  <div
                    className="shrink-0 w-10 h-10 rounded-full flex items-center justify-center"
                    style={{ background: 'rgba(212,175,55,0.12)', border: '1px solid rgba(212,175,55,0.35)' }}
                  >
                    <Icon className="w-5 h-5" style={{ color: '#D4AF37' }} strokeWidth={1.4} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <div
                        style={{
                          fontFamily: 'Cormorant Garamond, serif',
                          fontSize: 20,
                          color: '#F5EEE0',
                          fontWeight: 400,
                        }}
                      >
                        {item.name}
                      </div>
                      <div
                        style={{
                          color: 'rgba(227,215,255,0.55)',
                          fontSize: 13,
                          fontFamily: 'Cormorant Garamond, serif',
                          fontStyle: 'italic',
                        }}
                      >
                        valeur {item.price}€
                      </div>
                    </div>
                    <div className="text-sm" style={{ color: 'rgba(227,215,255,0.72)', lineHeight: 1.55 }}>
                      {item.desc}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {step === 0 ? (
          <div className="text-center">
            <button
              onClick={() => setStep(1)}
              className="plume-btn-primary"
              data-testid="trio-decouverte-cta-start"
              style={{ padding: '16px 36px', fontSize: 14 }}
            >
              Recevoir mon Trio — {TRIO_PRICE}€ <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
            </button>
            <p className="text-xs mt-4" style={{ color: 'rgba(227,215,255,0.5)', letterSpacing: '0.1em' }}>
              Paiement sécurisé Stripe · Sans engagement · TVA incluse
            </p>
          </div>
        ) : (
          <div className="plume-glass p-8 md:p-10 max-w-xl mx-auto" data-testid="trio-decouverte-form">
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
                <input type="email" value={form.email} onChange={(e) => upd('email', e.target.value)} data-testid="trio-decouverte-email"
                  className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
              </div>
              <div>
                <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>Prénom</label>
                <input type="text" value={form.first_name} onChange={(e) => upd('first_name', e.target.value)} data-testid="trio-decouverte-firstname"
                  className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>Date naiss.</label>
                  <input type="date" value={form.birth_date} onChange={(e) => upd('birth_date', e.target.value)} data-testid="trio-decouverte-birthdate"
                    className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
                </div>
                <div>
                  <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>Heure naiss.</label>
                  <input type="time" value={form.birth_time} onChange={(e) => upd('birth_time', e.target.value)} data-testid="trio-decouverte-birthtime"
                    className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
                </div>
              </div>
              <div>
                <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>Ville de naissance</label>
                <input type="text" value={form.birth_city} onChange={(e) => upd('birth_city', e.target.value)} data-testid="trio-decouverte-city"
                  className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
              </div>
              <div>
                <label className="text-xs uppercase" style={{ color: 'rgba(212,175,55,0.65)', letterSpacing: '0.2em' }}>Code promo (optionnel)</label>
                <input type="text" value={promoCode} onChange={(e) => setPromoCode(e.target.value.toUpperCase())} placeholder="Ex: ADMIN26" data-testid="trio-decouverte-promo"
                  className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/40 border border-plume-gold/15 text-plume-lavender focus:outline-none focus:border-plume-gold/50"
                  style={{ letterSpacing: '0.2em', fontFamily: 'Cinzel, serif', fontSize: 13 }} />
              </div>
              {error && <p className="text-sm text-center" style={{ color: '#F87171' }} data-testid="trio-decouverte-error">{error}</p>}
              <button onClick={handleCheckout} disabled={loading} className="plume-btn-primary w-full justify-center" data-testid="trio-decouverte-checkout-btn">
                {loading ? (<><Loader2 className="w-4 h-4 animate-spin" /> Redirection...</>) : promoCode.trim() ? (<>Déverrouiller mon Trio <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></>) : (<>Payer {TRIO_PRICE}€ et recevoir mon Trio <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></>)}
              </button>
              <p className="text-[10px] text-center mt-3" style={{ color: 'rgba(227,215,255,0.4)', letterSpacing: '0.2em' }}>
                🔒 PAIEMENT SÉCURISÉ STRIPE · TVA INCLUSE
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrioDecouverte;
