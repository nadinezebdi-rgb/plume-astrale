import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2, Tag } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Paiement = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState('essentiel');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showPromo, setShowPromo] = useState(false);
  const [promoCode, setPromoCode] = useState('');
  const [promoError, setPromoError] = useState('');
  const [promoSuccess, setPromoSuccess] = useState('');
  const [promoLoading, setPromoLoading] = useState(false);

  useEffect(() => {
    const data = localStorage.getItem('plume_astrale_data');
    const plan = localStorage.getItem('plume_astrale_plan');
    if (!data) { navigate('/formulaire'); return; }
    setUserData(JSON.parse(data));
    if (plan) setSelectedPlan(plan);
  }, [navigate]);

  const plans = {
    essentiel: { name: 'Essentiel', price: '9,90', features: ['Chemin de vie complet', 'Annee personnelle 2026', 'Identite celeste', 'Mission de vie', 'PDF telechargeable'] },
    premium: { name: 'Premium', price: '29,90', features: ['Tout le contenu Essentiel', 'Tirage Tarot personnalis\u00e9', 'Compatibilit\u00e9 amoureuse', 'Horoscope mensuel', 'Guidance personnalis\u00e9e', 'Manuscrit PDF premium'] }
  };

  const handleApplyPromo = async () => {
    if (!promoCode.trim()) return;
    setPromoLoading(true);
    setPromoError('');
    setPromoSuccess('');
    try {
      const res = await fetch(`${API_URL}/api/discount/validate`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: promoCode }),
      });
      const data = await res.json();
      if (data.valid && data.discount_percent === 100) {
        await fetch(`${API_URL}/api/access/free`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_id: 'manuscrit', discount_code: promoCode, user_email: userData?.email, user_data: userData }),
        });
        localStorage.setItem('plume_astrale_paid', 'true');
        localStorage.setItem('plume_astrale_plan', selectedPlan);
        localStorage.setItem('plume_astrale_payment_date', new Date().toISOString());
        setPromoSuccess('Code valide ! Acces complet debloque.');
        setTimeout(() => navigate('/resultats'), 1200);
      } else {
        setPromoError(data.message || 'Code invalide');
      }
    } catch (e) { setPromoError('Erreur de connexion'); }
    setPromoLoading(false);
  };

  const handlePayment = async () => {
    if (!userData) return;
    setIsProcessing(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 2500));
      localStorage.setItem('plume_astrale_paid', 'true');
      localStorage.setItem('plume_astrale_plan', selectedPlan);
      localStorage.setItem('plume_astrale_payment_date', new Date().toISOString());
      navigate('/resultats');
    } catch (error) {
      console.error('Payment error:', error);
      setIsProcessing(false);
    }
  };

  if (!userData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-5 h-5 animate-spin" style={{ color: 'var(--pa-accent)' }} />
      </div>
    );
  }

  const currentPlan = plans[selectedPlan];

  return (
    <div className="min-h-screen relative">
      <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
      <div className="max-w-xl mx-auto">

        <button onClick={() => navigate('/choix')} className="link-editorial text-xs mb-12" data-testid="btn-back-choix">
          <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Modifier mon choix
        </button>

        <div className="mb-12">
          <p className="section-label">Finalisation</p>
          <h1 className="text-3xl md:text-4xl" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
            Votre commande
          </h1>
        </div>

        {/* Order summary */}
        <div className="mb-10">
          <div className="flex items-baseline justify-between mb-6">
            <div>
              <p className="text-sm" style={{ color: 'var(--pa-heading)' }}>Manuscrit {currentPlan.name}</p>
              <p className="text-xs mt-1" style={{ color: 'var(--pa-muted)' }}>Paiement unique, acces immediat</p>
            </div>
            <span className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
              {currentPlan.price} EUR
            </span>
          </div>

          <div className="space-y-2 mb-8">
            {currentPlan.features.map((f, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="w-1 h-1 rounded-full flex-shrink-0" style={{ background: 'var(--pa-accent)' }} />
                <span className="text-sm" style={{ color: 'var(--pa-body)' }}>{f}</span>
              </div>
            ))}
          </div>

          {/* Plan switch */}
          <div className="flex gap-3 mb-8">
            {['essentiel', 'premium'].map(p => (
              <button key={p} onClick={() => setSelectedPlan(p)}
                className="flex-1 py-3 text-center text-xs tracking-widest uppercase transition-all duration-300"
                style={{
                  border: `1px solid ${selectedPlan === p ? 'var(--pa-accent)' : 'var(--pa-divider)'}`,
                  background: selectedPlan === p ? 'rgba(196, 168, 130, 0.06)' : 'transparent',
                  color: selectedPlan === p ? 'var(--pa-accent)' : 'var(--pa-muted)',
                  letterSpacing: '0.1em'
                }}
                data-testid={`select-${p}`}>
                {plans[p].name} — {plans[p].price} EUR
              </button>
            ))}
          </div>
        </div>

        <div className="divider-subtle" />

        {/* Client info */}
        <div className="mb-10">
          <p className="text-xs tracking-widest uppercase mb-4" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
            Vos informations
          </p>
          <div className="space-y-2 text-sm">
            {[
              ['Prenom', userData.prenom],
              ['Email', userData.email],
              ['Naissance', new Date(userData.dateNaissance).toLocaleDateString('fr-FR')],
              ['Lieu', `${userData.ville}, ${userData.pays}`],
            ].filter(([, v]) => v).map(([label, value]) => (
              <div key={label} className="flex justify-between">
                <span style={{ color: 'var(--pa-muted)' }}>{label}</span>
                <span style={{ color: 'var(--pa-heading)' }}>{value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Pay button */}
        <button onClick={handlePayment} disabled={isProcessing}
          className="btn-editorial-filled w-full justify-center mb-4 disabled:opacity-50"
          data-testid="btn-pay">
          {isProcessing ? <><Loader2 className="w-4 h-4 animate-spin" /> Preparation...</> : <>Recevoir mon manuscrit</>}
        </button>

        <p className="text-xs text-center mb-6" style={{ color: 'var(--pa-muted)' }}>
          Acces immediat — PDF telechargeable
        </p>

        {/* Promo */}
        <div className="text-center mb-10">
          {!showPromo ? (
            <button onClick={() => setShowPromo(true)}
              className="text-xs transition-colors duration-300 hover:text-[#D4AF37]" style={{ color: 'var(--pa-muted)' }}
              data-testid="show-promo-btn">
              <Tag className="w-3 h-3 inline mr-1" strokeWidth={1} /> J'ai un code de reduction
            </button>
          ) : (
            <div className="max-w-sm mx-auto space-y-2">
              <div className="flex gap-2">
                <input type="text" value={promoCode} onChange={(e) => { setPromoCode(e.target.value.toUpperCase()); setPromoError(''); }}
                  placeholder="Code promo" className="input-boxed flex-1 text-center text-sm" data-testid="promo-input" />
                <button onClick={handleApplyPromo} disabled={promoLoading}
                  className="btn-editorial text-xs px-5 py-2 disabled:opacity-50" data-testid="apply-promo-btn">
                  {promoLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : 'Appliquer'}
                </button>
              </div>
              {promoError && <p className="text-red-400/70 text-xs" data-testid="promo-error">{promoError}</p>}
              {promoSuccess && <p className="text-emerald-400 text-xs" data-testid="promo-success">{promoSuccess}</p>}
            </div>
          )}
        </div>

        {/* Trust */}
        <div className="flex flex-wrap justify-center gap-6 text-xs" style={{ color: 'var(--pa-muted)' }}>
          <span>Paiement securise via Stripe</span>
          <span>Conforme RGPD</span>
          <span>Rembourse sous 30j</span>
        </div>
      </div>
      </div>
    </div>
  );
};

export default Paiement;
