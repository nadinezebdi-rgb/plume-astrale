import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const Choix = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    const data = localStorage.getItem('plume_astrale_data');
    if (!data) { navigate('/formulaire'); return; }
    setUserData(JSON.parse(data));
  }, [navigate]);

  const handleSelectPlan = (plan) => {
    localStorage.setItem('plume_astrale_plan', plan);
    navigate('/paiement');
  };

  if (!userData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-5 h-5 animate-spin" style={{ color: 'var(--pa-accent)' }} />
      </div>
    );
  }

  const essentielFeatures = [
    { text: 'Chemin de vie complet', on: true },
    { text: 'Annee personnelle 2026', on: true },
    { text: 'Identite celeste', on: true },
    { text: 'Mission de vie', on: true },
    { text: 'PDF telechargeable', on: true },
    { text: 'Tirage Tarot personnalise', on: false },
    { text: 'Compatibilite amoureuse', on: false },
    { text: 'Horoscope mensuel', on: false },
  ];

  const premiumFeatures = [
    { text: 'Chemin de vie complet', on: true },
    { text: 'Annee personnelle 2026', on: true },
    { text: 'Identite celeste', on: true },
    { text: 'Mission de vie', on: true },
    { text: 'PDF telechargeable', on: true },
    { text: 'Tirage Tarot personnalise', on: true, highlight: true },
    { text: 'Compatibilite amoureuse', on: true, highlight: true },
    { text: 'Horoscope mensuel', on: true, highlight: true },
  ];

  return (
    <div className="min-h-screen relative">
      <StarField count={60} />
      <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
      <div className="max-w-3xl mx-auto">

        {/* Header */}
        <div className="text-center mb-16">
          <p className="section-label">Choisissez votre guidance</p>
          <h1
            className="text-3xl md:text-4xl mb-4"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
          >
            {userData.prenom ? `${userData.prenom}, v` : 'V'}otre manuscrit vous attend.
          </h1>
          <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
            Deux chemins s'offrent a vous. Choisissez celui qui resonne.
          </p>
        </div>

        {/* Plans grid */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">

          {/* Essentiel */}
          <div className="py-10 px-8 rounded-sm" style={{ border: '1px solid var(--pa-divider)' }}>
            <p className="text-xs tracking-widest uppercase mb-3" style={{ color: 'var(--pa-muted)', letterSpacing: '0.12em' }}>Essentiel</p>
            <div className="flex items-baseline gap-2 mb-2">
              <span className="text-3xl" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>9,90 EUR</span>
            </div>
            <p className="text-xs mb-8" style={{ color: 'var(--pa-muted)' }}>Votre manuscrit celeste de base</p>

            <div className="space-y-3 mb-10">
              {essentielFeatures.map((f, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="w-1 h-1 rounded-full flex-shrink-0" style={{ background: f.on ? 'var(--pa-accent)' : 'var(--pa-divider)' }} />
                  <span className="text-sm" style={{ color: f.on ? 'var(--pa-body)' : 'var(--pa-muted)', opacity: f.on ? 1 : 0.5 }}>
                    {f.text}
                  </span>
                </div>
              ))}
            </div>

            <button onClick={() => handleSelectPlan('essentiel')} className="btn-editorial w-full justify-center" data-testid="btn-essentiel">
              Decouvrir l'essentiel
            </button>
          </div>

          {/* Premium */}
          <div className="py-10 px-8 rounded-sm relative" style={{ border: '1px solid rgba(196, 168, 130, 0.3)' }}>
            <div className="absolute -top-3 left-8">
              <span className="text-xs tracking-widest uppercase px-4 py-1" style={{ background: 'var(--pa-accent)', color: 'var(--pa-bg)', letterSpacing: '0.1em' }}>
                Recommande
              </span>
            </div>

            <p className="text-xs tracking-widest uppercase mb-3 mt-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Premium</p>
            <div className="flex items-baseline gap-2 mb-2">
              <span className="text-3xl" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>29,90 EUR</span>
            </div>
            <p className="text-xs mb-8" style={{ color: 'var(--pa-muted)' }}>L'experience cosmique complete</p>

            <div className="space-y-3 mb-10">
              {premiumFeatures.map((f, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="w-1 h-1 rounded-full flex-shrink-0" style={{ background: f.highlight ? 'var(--pa-accent)' : 'var(--pa-accent)' }} />
                  <span className="text-sm" style={{ color: f.highlight ? 'var(--pa-accent)' : 'var(--pa-body)' }}>
                    {f.text}
                  </span>
                </div>
              ))}
            </div>

            <button onClick={() => handleSelectPlan('premium')} className="btn-editorial-filled w-full justify-center" data-testid="btn-premium">
              Recevoir mon manuscrit complet
            </button>
          </div>
        </div>

        {/* Trust */}
        <div className="flex flex-wrap justify-center gap-8 text-xs" style={{ color: 'var(--pa-muted)' }}>
          <span>Paiement securise</span>
          <span>Acces immediat</span>
          <span>Satisfait ou rembourse 30j</span>
        </div>
      </div>
    </div>
  );
};

export default Choix;
