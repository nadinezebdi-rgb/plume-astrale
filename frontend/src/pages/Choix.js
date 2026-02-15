import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Moon, Heart, Sparkles, CheckCircle, Crown, Zap, Sun, Eye } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const Choix = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState(null);

  useEffect(() => {
    const data = localStorage.getItem('plume_astrale_data');
    if (!data) {
      navigate('/formulaire');
      return;
    }
    setUserData(JSON.parse(data));
  }, [navigate]);

  const handleSelectPlan = (plan) => {
    setSelectedPlan(plan);
    localStorage.setItem('plume_astrale_plan', plan);
    navigate('/paiement');
  };

  const plans = {
    essentiel: {
      name: 'Essentiel',
      price: '9,90',
      description: 'Votre manuscrit céleste de base',
      features: [
        { text: 'Chemin de vie complet', included: true },
        { text: 'Année personnelle 2026', included: true },
        { text: 'Identité céleste (Soleil, Lune, Ascendant)', included: true },
        { text: 'Mission de vie', included: true },
        { text: 'PDF téléchargeable', included: true },
        { text: 'Tirage Tarot personnalisé', included: false },
        { text: 'Compatibilité amoureuse', included: false },
        { text: 'Horoscope mensuel détaillé', included: false },
        { text: 'Guidance IA personnalisée', included: false },
      ],
      buttonText: 'Découvrir l\'essentiel',
      buttonSubtext: 'Accès immédiat • PDF inclus',
      color: 'secondary'
    },
    premium: {
      name: 'Premium',
      price: '29,90',
      description: 'L\'expérience cosmique complète',
      badge: 'Recommandé',
      features: [
        { text: 'Chemin de vie complet', included: true },
        { text: 'Année personnelle 2026', included: true },
        { text: 'Identité céleste (Soleil, Lune, Ascendant)', included: true },
        { text: 'Mission de vie', included: true },
        { text: 'PDF téléchargeable', included: true },
        { text: 'Tirage Tarot personnalisé', included: true, highlight: true },
        { text: 'Compatibilité amoureuse', included: true, highlight: true },
        { text: 'Horoscope mensuel détaillé', included: true, highlight: true },
        { text: 'Guidance IA personnalisée', included: true, highlight: true },
      ],
      buttonText: 'Recevoir mon manuscrit complet',
      buttonSubtext: 'Accès immédiat • Tout inclus',
      color: 'primary'
    }
  };

  if (!userData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-2 border-[#C5A059] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen relative">
      <StarField />
      
      <div className="relative z-10 py-12 px-4 md:px-6">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-4 font-light">
              Choisissez Votre Guidance
            </p>
            
            <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              {userData.prenom ? `${userData.prenom}, ` : ''}Votre Manuscrit Vous Attend
            </h1>
            
            <p className="text-lg text-[#E0D9F6]/70 font-light max-w-2xl mx-auto">
              Deux chemins s'offrent à vous. Choisissez celui qui résonne avec votre âme.
            </p>
          </div>

          {/* Plans */}
          <div className="grid md:grid-cols-2 gap-8 mb-12">
            {/* Essentiel */}
            <div className="card-mystical relative">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-full bg-[#C5A059]/10 text-[#C5A059]">
                  <Star className="w-6 h-6" strokeWidth={1} />
                </div>
                <div>
                  <h2 className="text-2xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                    {plans.essentiel.name}
                  </h2>
                  <p className="text-[#E0D9F6]/60 text-sm">{plans.essentiel.description}</p>
                </div>
              </div>

              <div className="mb-6">
                <span className="text-4xl font-bold text-[#F3E5AB]" style={{ fontFamily: 'Cinzel, serif' }}>
                  {plans.essentiel.price}€
                </span>
                <span className="text-[#E0D9F6]/50 ml-2">paiement unique</span>
              </div>

              <div className="space-y-3 mb-8">
                {plans.essentiel.features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-3">
                    {feature.included ? (
                      <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border border-[#E0D9F6]/20 flex-shrink-0" />
                    )}
                    <span className={feature.included ? 'text-[#E0D9F6]/80' : 'text-[#E0D9F6]/30'}>
                      {feature.text}
                    </span>
                  </div>
                ))}
              </div>

              <button
                onClick={() => handleSelectPlan('essentiel')}
                className="btn-mystical w-full rounded-xl py-4"
                data-testid="btn-essentiel"
              >
                {plans.essentiel.buttonText}
              </button>
              <p className="text-center text-xs text-[#E0D9F6]/40 mt-3">
                {plans.essentiel.buttonSubtext}
              </p>
            </div>

            {/* Premium */}
            <div className="card-mystical relative border-[#C5A059]/40 glow-gold">
              {/* Badge Recommandé */}
              <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                <span className="px-4 py-1 rounded-full bg-gradient-to-r from-[#C5A059] to-[#FFD700] text-[#0F0518] text-sm font-medium flex items-center gap-1">
                  <Crown className="w-4 h-4" />
                  Recommandé
                </span>
              </div>

              <div className="flex items-center gap-3 mb-6 mt-2">
                <div className="p-3 rounded-full bg-[#C5A059]/20 text-[#C5A059]">
                  <Sparkles className="w-6 h-6" strokeWidth={1} />
                </div>
                <div>
                  <h2 className="text-2xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                    {plans.premium.name}
                  </h2>
                  <p className="text-[#E0D9F6]/60 text-sm">{plans.premium.description}</p>
                </div>
              </div>

              <div className="mb-6">
                <span className="text-4xl font-bold text-gold-gradient" style={{ fontFamily: 'Cinzel, serif' }}>
                  {plans.premium.price}€
                </span>
                <span className="text-[#E0D9F6]/50 ml-2">paiement unique</span>
              </div>

              <div className="space-y-3 mb-8">
                {plans.premium.features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <CheckCircle className={`w-5 h-5 flex-shrink-0 ${feature.highlight ? 'text-[#C5A059]' : 'text-emerald-400'}`} />
                    <span className={`${feature.highlight ? 'text-[#C5A059] font-medium' : 'text-[#E0D9F6]/80'}`}>
                      {feature.text}
                    </span>
                    {feature.highlight && (
                      <span className="px-2 py-0.5 rounded-full bg-[#C5A059]/20 text-[#C5A059] text-xs">
                        Nouveau
                      </span>
                    )}
                  </div>
                ))}
              </div>

              <button
                onClick={() => handleSelectPlan('premium')}
                className="btn-mystical-filled w-full rounded-xl py-4 text-lg animate-glow-pulse"
                data-testid="btn-premium"
              >
                {plans.premium.buttonText}
              </button>
              <p className="text-center text-xs text-[#E0D9F6]/50 mt-3">
                {plans.premium.buttonSubtext}
              </p>
            </div>
          </div>

          {/* Features Comparison */}
          <div className="text-center mb-12">
            <h3 className="text-xl mb-6" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Ce que vous recevez avec Premium
            </h3>
            <div className="grid md:grid-cols-4 gap-6">
              <div className="card-mystical p-6 text-center">
                <Sun className="w-8 h-8 text-[#C5A059] mx-auto mb-3" strokeWidth={1} />
                <h4 className="text-[#F3E5AB] mb-2">Tirage Tarot</h4>
                <p className="text-[#E0D9F6]/50 text-sm">3 cartes tirées pour votre guidance</p>
              </div>
              <div className="card-mystical p-6 text-center">
                <Heart className="w-8 h-8 text-[#C5A059] mx-auto mb-3" strokeWidth={1} />
                <h4 className="text-[#F3E5AB] mb-2">Compatibilité</h4>
                <p className="text-[#E0D9F6]/50 text-sm">Analyse de vos affinités amoureuses</p>
              </div>
              <div className="card-mystical p-6 text-center">
                <Moon className="w-8 h-8 text-[#C5A059] mx-auto mb-3" strokeWidth={1} />
                <h4 className="text-[#F3E5AB] mb-2">Horoscope Mensuel</h4>
                <p className="text-[#E0D9F6]/50 text-sm">Prévisions détaillées pour 2026</p>
              </div>
              <div className="card-mystical p-6 text-center">
                <Eye className="w-8 h-8 text-[#C5A059] mx-auto mb-3" strokeWidth={1} />
                <h4 className="text-[#F3E5AB] mb-2">Guidance IA</h4>
                <p className="text-[#E0D9F6]/50 text-sm">Conseils personnalisés illimités</p>
              </div>
            </div>
          </div>

          {/* Trust Badges */}
          <div className="flex flex-wrap justify-center gap-8 text-sm text-[#E0D9F6]/50">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>Paiement sécurisé</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>Accès immédiat</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>Satisfait ou remboursé 30j</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Choix;
