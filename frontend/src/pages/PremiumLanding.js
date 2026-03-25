import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Star, Sparkles, BookOpen, Eye, TrendingUp, Tag, Loader2 } from 'lucide-react';
import SEO from '@/components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const STEPS_PREVIEW = [
  { num: 'I', title: 'Votre Fondement', desc: 'Les forces et tensions qui vous definissent', icon: Star },
  { num: 'II', title: 'Votre Chemin d\'Ame', desc: 'Le nombre qui guide votre trajectoire', icon: Sparkles },
  { num: 'III', title: 'Votre Cycle Actuel', desc: 'Les mouvements de cette periode', icon: Eye },
  { num: 'IV', title: 'Vos Schemas Repetitifs', desc: 'Ce qui revient et ce que cela revele', icon: BookOpen },
  { num: 'V', title: 'Projection 12 Mois', desc: 'Mars 2026 - Fevrier 2027', icon: TrendingUp },
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
        setPromoSuccess('Code valide ! Acces Premium debloque.');
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
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (err) {
      console.error('Payment error:', err);
    }
  };

  return (
    <div className="relative z-10" data-testid="premium-landing">
      <SEO path="/premium" />
      {/* Hero */}
      <section className="pt-28 pb-16 px-6 md:px-8" data-testid="premium-hero">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-xs tracking-widest uppercase mb-6" style={{ color: 'var(--pa-accent)', letterSpacing: '0.25em' }}>
            Experience Premium
          </p>
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
            Votre Cartographie<br />
            <span style={{ color: 'var(--pa-accent)', fontStyle: 'italic' }}>Celeste Complete</span>
          </h1>
          <p className="text-base md:text-lg max-w-xl mx-auto mb-10" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>
            Un parcours guide et immersif en 5 etapes, croisant astrologie, numerologie et cycles de vie pour vous offrir une lecture profonde et structuree de votre periode actuelle.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button onClick={handleStart} className="btn-editorial-filled text-xs px-8 py-3" data-testid="premium-start-btn">
              Commencer le parcours <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
            </button>
            <button onClick={handlePayment} className="btn-editorial text-xs px-8 py-3" data-testid="premium-pay-btn">
              199 EUR &mdash; Acces immediat
            </button>
          </div>
        </div>
      </section>

      {/* Steps preview */}
      <section className="px-6 md:px-8 pb-16" data-testid="premium-steps-preview">
        <div className="max-w-3xl mx-auto">
          <div className="w-10 h-px mx-auto mb-12" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />
          <p className="text-xs tracking-widest uppercase mb-8 text-center" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>
            Les 5 etapes de votre parcours
          </p>
          <div className="space-y-6">
            {STEPS_PREVIEW.map((step, i) => {
              const Icon = step.icon;
              return (
                <div key={i} className="flex items-start gap-5 card-editorial p-6" data-testid={`premium-step-preview-${i}`}>
                  <div className="flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center" style={{ border: '1px solid var(--pa-divider)', background: 'rgba(197,160,89,0.05)' }}>
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

      {/* Value proposition */}
      <section className="px-6 md:px-8 pb-16" data-testid="premium-value">
        <div className="max-w-2xl mx-auto">
          <div className="w-10 h-px mx-auto mb-12" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />
          <div className="text-center mb-10">
            <h2 className="text-3xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
              Ce que contient votre experience
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              'Analyse natale croisee (signe + element + modalite)',
              'Num\u00e9rologie compl\u00e8te (chemin de vie + expression + \u00e2me)',
              'Lecture du cycle actuel personnalis\u00e9e par IA',
              'Identification des schemas repetitifs',
              'Projection 12 mois avec periodes sensibles',
              'PDF Premium telechargeale (30+ pages)',
              'Acces illimite a votre parcours',
              'Question de reflexion a chaque etape',
            ].map((item, i) => (
              <div key={i} className="flex items-start gap-3 py-2">
                <span className="w-1.5 h-1.5 rounded-full flex-shrink-0 mt-1.5" style={{ background: 'var(--pa-accent)' }} />
                <span className="text-sm" style={{ color: 'var(--pa-body)' }}>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing CTA */}
      <section className="px-6 md:px-8 pb-20" data-testid="premium-pricing">
        <div className="max-w-lg mx-auto text-center">
          <div className="card-editorial p-8 md:p-10">
            <p className="text-xs tracking-widest uppercase mb-4" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>
              Paiement unique
            </p>
            <div className="mb-6">
              <span className="text-5xl" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>199</span>
              <span className="text-lg ml-1" style={{ color: 'var(--pa-muted)' }}>EUR</span>
            </div>
            <p className="text-sm mb-8" style={{ color: 'var(--pa-body)' }}>
              Acces immediat et illimite a votre parcours complet + PDF Premium
            </p>
            <button onClick={handleStart} className="btn-editorial-filled w-full justify-center mb-4" data-testid="premium-cta-btn">
              Commencer maintenant <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
            </button>
            <div className="flex flex-wrap justify-center gap-4 text-xs mt-4" style={{ color: 'var(--pa-muted)' }}>
              <span>Paiement securise</span>
              <span>Acces immediat</span>
              <span>Rembourse 30j</span>
            </div>

            {/* Promo code */}
            <div className="mt-6 pt-6" style={{ borderTop: '1px solid var(--pa-divider)' }}>
              {!showPromo ? (
                <button onClick={() => setShowPromo(true)} className="text-xs transition-colors duration-300 hover:text-[#C5A059]" style={{ color: 'var(--pa-muted)' }} data-testid="premium-show-promo">
                  <Tag className="w-3 h-3 inline mr-1" strokeWidth={1} /> J'ai un code de reduction
                </button>
              ) : (
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <input type="text" value={promoCode} onChange={(e) => { setPromoCode(e.target.value.toUpperCase()); setPromoError(''); }}
                      placeholder="Code promo" className="input-boxed flex-1 text-center text-sm" data-testid="premium-promo-input" />
                    <button onClick={handleApplyPromo} disabled={promoLoading} className="btn-editorial text-xs px-5 py-2 disabled:opacity-50" data-testid="premium-apply-promo">
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
          Plume Astrale &mdash; Experience Premium
        </p>
      </footer>
    </div>
  );
};

export default PremiumLanding;
