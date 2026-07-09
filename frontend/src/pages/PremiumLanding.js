import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Star, Sparkles, BookOpen, Eye, TrendingUp, Tag, Loader2 } from 'lucide-react';
import SEO from '@/components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const STEPS_PREVIEW = [
  { num: 'I',   title: 'Votre Fondement',        desc: 'Les forces et tensions qui vous définissent',    icon: Star },
  { num: 'II',  title: 'Votre Chemin d\'Âme',    desc: 'Le nombre qui guide votre trajectoire',          icon: Sparkles },
  { num: 'III', title: 'Votre Cycle Actuel',      desc: 'Les mouvements de cette période',                icon: Eye },
  { num: 'IV',  title: 'Vos Schémas Répétitifs', desc: 'Ce qui revient et ce que cela révèle',           icon: BookOpen },
  { num: 'V',   title: 'Projection 12 Mois',      desc: 'Avril 2026 — Mars 2027',                         icon: TrendingUp },
];

const FEATURES = [
  { emoji: '🌟', text: 'Horoscope quotidien personnalisé' },
  { emoji: '🃏', text: 'Tarot quotidien — 1 carte / jour' },
  { emoji: '🌟', text: 'Consultation astrale personnalisée — Une guidance vivante de ton thème natal' },
  { emoji: '💑', text: 'Compatibilité amoureuse illimitée' },
];

const PremiumLanding = () => {
  const navigate = useNavigate();
  const [showPromo, setShowPromo] = useState(false);
  const [promoCode, setPromoCode] = useState('');
  const [promoLoading, setPromoLoading] = useState(false);
  const [promoError, setPromoError] = useState('');
  const [promoSuccess, setPromoSuccess] = useState('');

  const handleStart = () => {
    const data = localStorage.getItem('plume_astrale_data');
    if (data) {
      navigate('/premium/experience');
    } else {
      localStorage.setItem('plume_astrale_premium_redirect', 'true');
      navigate('/formulaire');
    }
  };

  const handleApplyPromo = async () => {
    if (!promoCode.trim()) return;
    setPromoLoading(true);
    setPromoError('');
    setPromoSuccess('');
    try {
      const res = await fetch(`${API_URL}/api/discount/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: promoCode }),
      });
      const data = await res.json();
      if (data.valid && data.discount_percent === 100) {
        const userData = JSON.parse(localStorage.getItem('plume_astrale_data') || '{}');
        await fetch(`${API_URL}/api/access/free`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product_id: 'premium',
            discount_code: promoCode,
            user_email: userData.email || '',
            user_data: userData,
            origin_url: window.location.origin,
          }),
        });
        localStorage.setItem('plume_premium_paid', 'true');
        setPromoSuccess('Code valide ! Accès Premium débloqué.');
        setTimeout(() => {
          if (localStorage.getItem('plume_astrale_data')) {
            navigate('/premium/experience');
          } else {
            localStorage.setItem('plume_astrale_premium_redirect', 'true');
            navigate('/formulaire');
          }
        }, 1200);
      } else {
        setPromoError(data.message || 'Code invalide');
      }
    } catch {
      setPromoError('Erreur de connexion');
    }
    setPromoLoading(false);
  };

  const handlePayment = async () => {
    const userData = JSON.parse(localStorage.getItem('plume_astrale_data') || '{}');
    try {
      const res = await fetch(`${API_URL}/api/checkout/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: 'premium',
          origin_url: window.location.origin,
          user_email: userData.email || '',
          user_data: userData,
        }),
      });
      const data = await res.json();
      if (data.url) window.location.href = data.url;
    } catch (err) {
      console.error('Payment error:', err);
    }
  };

  return (
    <div className="relative z-10" data-testid="premium-landing">
      <SEO path="/premium" />

      {/* ── Hero ── */}
      <section className="pt-28 pb-16 px-6 md:px-8" data-testid="premium-hero">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-xs tracking-widest uppercase mb-6" style={{ color: 'var(--pa-accent)', letterSpacing: '0.25em' }}>
            ✨ Abonnement Premium
          </p>
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl mb-6"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
            Reçois ton message<br />
            <span style={{ color: 'var(--pa-accent)', fontStyle: 'italic' }}>chaque jour</span>
          </h1>
          <p className="text-base md:text-lg max-w-xl mx-auto mb-10" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>
            Horoscope · Tarot · Consultation personnalisée · Compatibilité — tout ce dont tu as besoin pour naviguer ton destin.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handleStart}
              className="flex items-center justify-center gap-2 text-[13px] uppercase tracking-widest px-8 py-3.5 rounded-full transition-all duration-300"
              style={{
                background: 'linear-gradient(135deg, #B8961F, #D4AF37)',
                color: '#0B0B0F',
                fontWeight: 600,
                letterSpacing: '0.1em',
                border: 'none',
              }}
              onMouseEnter={e => { e.currentTarget.style.boxShadow = '0 0 24px rgba(184,150,31,0.5)'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
              onMouseLeave={e => { e.currentTarget.style.boxShadow = 'none'; e.currentTarget.style.transform = 'translateY(0)'; }}
              data-testid="premium-start-btn"
            >
              ✨ Devenir Premium
            </button>
            <button
              onClick={handlePayment}
              className="flex items-center justify-center gap-2 text-[13px] uppercase tracking-widest px-8 py-3.5 rounded-full transition-all duration-300"
              style={{ border: '1px solid rgba(184,150,31,0.4)', color: '#B8961F', letterSpacing: '0.1em' }}
              onMouseEnter={e => e.currentTarget.style.borderColor = '#B8961F'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'rgba(184,150,31,0.4)'}
              data-testid="premium-pay-btn"
            >
              9,99 € / mois — Accès immédiat
            </button>
          </div>
        </div>
      </section>

      {/* ── Steps preview ── */}
      <section className="px-6 md:px-8 pb-16" data-testid="premium-steps-preview">
        <div className="max-w-3xl mx-auto">
          <div className="w-10 h-px mx-auto mb-12" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />
          <p className="text-xs tracking-widest uppercase mb-8 text-center" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>
            Les 5 étapes de votre parcours
          </p>
          <div className="space-y-6">
            {STEPS_PREVIEW.map((step, i) => {
              const Icon = step.icon;
              return (
                <div key={i} className="flex items-start gap-5 card-editorial p-6" data-testid={`premium-step-preview-${i}`}>
                  <div className="flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center"
                    style={{ border: '1px solid var(--pa-divider)', background: 'rgba(184,150,31,0.05)' }}>
                    <Icon className="w-5 h-5" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.5} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-baseline gap-3 mb-1">
                      <span className="text-xs" style={{ color: 'var(--pa-accent)', letterSpacing: '0.1em' }}>{step.num}</span>
                      <h3 className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 400, color: 'var(--pa-heading)' }}>{step.title}</h3>
                    </div>
                    <p className="text-sm" style={{ color: 'var(--pa-body)' }}>{step.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── Value proposition ── */}
      <section className="px-6 md:px-8 pb-16" data-testid="premium-value">
        <div className="max-w-2xl mx-auto">
          <div className="w-10 h-px mx-auto mb-12" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />
          <div className="text-center mb-10">
            <h2 className="text-3xl md:text-4xl mb-4"
              style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
              Ce que contient votre expérience
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              'Analyse natale croisée (signe + élément + modalité)',
              'Numérologie complète (chemin de vie + expression + âme)',
              'Lecture personnalisée de ton cycle actuel',
              'Identification des schémas répétitifs',
              'Projection 12 mois avec périodes sensibles',
              'PDF Premium téléchargeable (30+ pages)',
              'Accès illimité à votre parcours',
              'Question de réflexion à chaque étape',
            ].map((item, i) => (
              <div key={i} className="flex items-start gap-3 py-2">
                <span className="w-1.5 h-1.5 rounded-full flex-shrink-0 mt-1.5" style={{ background: 'var(--pa-accent)' }} />
                <span className="text-sm" style={{ color: 'var(--pa-body)' }}>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Pricing CTA ── */}
      <section className="px-6 md:px-8 pb-20" data-testid="premium-pricing">
        <div className="max-w-lg mx-auto text-center">
          <div className="card-editorial p-8 md:p-10">

            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-6 text-[11px] uppercase tracking-widest"
              style={{ background: 'rgba(184,150,31,0.12)', border: '1px solid rgba(184,150,31,0.3)', color: '#B8961F', letterSpacing: '0.12em' }}>
              ✨ Abonnement mensuel
            </div>

            <h2 className="text-3xl md:text-4xl mb-2"
              style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
              PLUME PREMIUM
            </h2>
            <p className="text-sm mb-6" style={{ color: 'var(--pa-muted)' }}>
              Reçois ton message chaque jour
            </p>

            {/* Features */}
            <div className="text-left mb-8 space-y-3">
              {FEATURES.map((f, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="text-lg flex-shrink-0">{f.emoji}</span>
                  <span className="text-sm" style={{ color: 'var(--pa-body)' }}>{f.text}</span>
                </div>
              ))}
            </div>

            {/* Prix */}
            <div className="mb-6">
              <span className="text-5xl" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>9</span>
              <span className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: '#B8961F' }}>,99</span>
              <span className="text-lg ml-1" style={{ color: 'var(--pa-muted)' }}>€ / mois</span>
            </div>

            <button
              onClick={handleStart}
              className="w-full flex items-center justify-center gap-2 mb-4"
              data-testid="premium-cta-btn"
              style={{
                background: 'linear-gradient(135deg, #B8961F, #D4AF37)',
                color: '#0B0B0F',
                padding: '14px 28px',
                borderRadius: '999px',
                fontWeight: 600,
                fontSize: '13px',
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                transition: 'all 0.3s ease',
                border: 'none',
                cursor: 'pointer',
              }}
              onMouseEnter={e => { e.currentTarget.style.boxShadow = '0 0 24px rgba(184,150,31,0.5)'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
              onMouseLeave={e => { e.currentTarget.style.boxShadow = 'none'; e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              ✨ Devenir Premium
            </button>

            <div className="flex flex-wrap justify-center gap-4 text-xs mt-4" style={{ color: 'var(--pa-muted)' }}>
              <span>Résiliation à tout moment</span>
              <span>Accès immédiat</span>
              <span>Paiement sécurisé</span>
            </div>

            {/* Promo code */}
            <div className="mt-6 pt-6" style={{ borderTop: '1px solid var(--pa-divider)' }}>
              {!showPromo ? (
                <button onClick={() => setShowPromo(true)} className="text-xs transition-colors duration-300 hover:text-[#B8961F]"
                  style={{ color: 'var(--pa-muted)' }} data-testid="premium-show-promo">
                  <Tag className="w-3 h-3 inline mr-1" strokeWidth={1} /> J'ai un code de réduction
                </button>
              ) : (
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <input type="text" value={promoCode}
                      onChange={(e) => { setPromoCode(e.target.value.toUpperCase()); setPromoError(''); }}
                      placeholder="Code promo"
                      className="input-boxed flex-1 text-center text-sm"
                      data-testid="premium-promo-input" />
                    <button onClick={handleApplyPromo} disabled={promoLoading}
                      className="btn-editorial text-xs px-5 py-2 disabled:opacity-50"
                      data-testid="premium-apply-promo">
                      {promoLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : 'Appliquer'}
                    </button>
                  </div>
                  {promoError && <p className="text-red-400/70 text-xs" data-testid="premium-promo-error">{promoError}</p>}
                  {promoSuccess && <p className="text-emerald-400 text-xs" data-testid="premium-promo-success">{promoSuccess}</p>}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-6 px-6 text-center" style={{ borderTop: '1px solid var(--pa-divider)' }}>
        <p className="text-xs tracking-widest" style={{ color: 'var(--pa-muted)', letterSpacing: '0.15em' }}>
          Plume Astrale — Expérience Premium
        </p>
      </footer>
    </div>
  );
};

export default PremiumLanding;
