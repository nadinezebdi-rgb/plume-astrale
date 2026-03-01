import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CreditCard, Shield, CheckCircle, ArrowLeft, Sparkles, Star, Heart, Crown, Tag, Loader2 } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

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
    
    if (!data) {
      navigate('/formulaire');
      return;
    }
    setUserData(JSON.parse(data));
    if (plan) setSelectedPlan(plan);
  }, [navigate]);

  const plans = {
    essentiel: {
      name: 'Essentiel',
      price: '9,90',
      features: [
        "Chemin de vie complet",
        "Année personnelle 2026",
        "Identité céleste (Soleil, Lune, Ascendant)",
        "Mission de vie détaillée",
        "PDF téléchargeable"
      ]
    },
    premium: {
      name: 'Premium',
      price: '29,90',
      features: [
        "Tout le contenu Essentiel",
        "Tirage Tarot personnalisé (3 cartes)",
        "Compatibilité amoureuse illimitée",
        "Horoscope mensuel détaillé",
        "Guidance IA personnalisée",
        "Manuscrit PDF premium"
      ]
    }
  };

  const handlePayment = async () => {
    if (!userData) return;
    
    setIsProcessing(true);
    
    try {
      // Simulation du paiement Stripe
      await new Promise(resolve => setTimeout(resolve, 2500));
      
      localStorage.setItem('plume_astrale_paid', 'true');
      localStorage.setItem('plume_astrale_plan', selectedPlan);
      localStorage.setItem('plume_astrale_payment_date', new Date().toISOString());
      
      navigate('/resultats');
    } catch (error) {
      console.error('Erreur de paiement:', error);
      setIsProcessing(false);
    }
  };

  if (!userData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-2 border-[#C5A059] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const currentPlan = plans[selectedPlan];

  return (
    <div className="min-h-screen relative">
      <StarField />
      
      <div className="relative z-10 py-12 px-4 md:px-6">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <button 
              onClick={() => navigate('/choix')}
              className="inline-flex items-center gap-2 text-[#C5A059]/70 hover:text-[#C5A059] transition-colors mb-8"
              data-testid="btn-back-choix"
            >
              <ArrowLeft className="w-4 h-4" strokeWidth={1} />
              <span className="text-sm">Modifier mon choix</span>
            </button>
            
            <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Finaliser Votre Commande
            </h1>
          </div>

          <div className="grid lg:grid-cols-2 gap-12">
            {/* Order Summary */}
            <div className="space-y-6">
              <div className="card-mystical">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    {selectedPlan === 'premium' ? (
                      <Crown className="w-6 h-6 text-[#C5A059]" strokeWidth={1} />
                    ) : (
                      <Star className="w-6 h-6 text-[#C5A059]" strokeWidth={1} />
                    )}
                    <h2 className="text-2xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                      Manuscrit {currentPlan.name}
                    </h2>
                  </div>
                  {selectedPlan === 'premium' && (
                    <span className="px-3 py-1 rounded-full bg-[#C5A059]/20 text-[#C5A059] text-xs">
                      Recommandé
                    </span>
                  )}
                </div>
                
                <div className="space-y-3 mb-8">
                  {currentPlan.features.map((feature, index) => (
                    <div key={index} className="flex items-center gap-3">
                      <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                      <span className="text-[#E0D9F6]/80 font-light">{feature}</span>
                    </div>
                  ))}
                </div>
                
                <div className="border-t border-[#C5A059]/20 pt-6">
                  <div className="flex justify-between items-center text-2xl">
                    <span style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>Total</span>
                    <span className="text-gold-gradient font-bold">{currentPlan.price}€</span>
                  </div>
                  <p className="text-[#E0D9F6]/40 text-sm mt-2">
                    Paiement unique • Accès immédiat
                  </p>
                </div>
              </div>

              {/* Change Plan */}
              <div className="card-mystical">
                <p className="text-[#E0D9F6]/60 text-sm mb-4">Changer d'offre</p>
                <div className="flex gap-3">
                  <button
                    onClick={() => setSelectedPlan('essentiel')}
                    className={`flex-1 p-4 rounded-xl border transition-all ${
                      selectedPlan === 'essentiel'
                        ? 'border-[#C5A059] bg-[#C5A059]/10'
                        : 'border-[#C5A059]/20 hover:border-[#C5A059]/40'
                    }`}
                    data-testid="select-essentiel"
                  >
                    <p className="text-[#F3E5AB]">Essentiel</p>
                    <p className="text-[#C5A059] font-bold">9,90€</p>
                  </button>
                  <button
                    onClick={() => setSelectedPlan('premium')}
                    className={`flex-1 p-4 rounded-xl border transition-all ${
                      selectedPlan === 'premium'
                        ? 'border-[#C5A059] bg-[#C5A059]/10'
                        : 'border-[#C5A059]/20 hover:border-[#C5A059]/40'
                    }`}
                    data-testid="select-premium"
                  >
                    <p className="text-[#F3E5AB]">Premium</p>
                    <p className="text-[#C5A059] font-bold">29,90€</p>
                  </button>
                </div>
              </div>

              {/* Security */}
              <div className="card-mystical">
                <div className="flex items-center gap-3 mb-4">
                  <Shield className="w-6 h-6 text-emerald-400" />
                  <span className="text-[#F3E5AB] font-medium">Paiement 100% Sécurisé</span>
                </div>
                <div className="space-y-2 text-sm text-[#E0D9F6]/50">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-emerald-400 rounded-full" />
                    <span>Chiffrement SSL 256 bits</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-emerald-400 rounded-full" />
                    <span>Traitement sécurisé par Stripe</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-emerald-400 rounded-full" />
                    <span>Conforme RGPD</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Payment Form */}
            <div className="space-y-6">
              <div className="card-mystical">
                <div className="flex items-center gap-3 mb-6">
                  <CreditCard className="w-6 h-6 text-[#C5A059]" strokeWidth={1} />
                  <h2 className="text-2xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                    Vos Informations
                  </h2>
                </div>

                {/* Client Info */}
                <div className="mb-8">
                  <div className="bg-[#1A0B2E]/50 rounded-xl p-4 space-y-2 text-sm border border-[#C5A059]/10">
                    {userData.prenom && (
                      <div className="flex justify-between">
                        <span className="text-[#E0D9F6]/50">Prénom</span>
                        <span className="text-[#E0D9F6]">{userData.prenom}</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-[#E0D9F6]/50">Email</span>
                      <span className="text-[#E0D9F6]">{userData.email}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#E0D9F6]/50">Date de naissance</span>
                      <span className="text-[#E0D9F6]">
                        {new Date(userData.dateNaissance).toLocaleDateString('fr-FR')}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#E0D9F6]/50">Lieu</span>
                      <span className="text-[#E0D9F6]">{userData.ville}, {userData.pays}</span>
                    </div>
                  </div>
                </div>

                {/* Payment Button - Optimisé selon la stratégie */}
                <button
                  onClick={handlePayment}
                  disabled={isProcessing}
                  className="btn-mystical-filled w-full rounded-xl py-5 flex items-center justify-center gap-3 text-lg"
                  data-testid="btn-pay"
                >
                  {isProcessing ? (
                    <>
                      <div className="w-5 h-5 border-2 border-[#0F0518] border-t-transparent rounded-full animate-spin" />
                      <span>Préparation de votre manuscrit...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      <span>Recevoir mon manuscrit</span>
                    </>
                  )}
                </button>

                <p className="text-center text-xs text-[#E0D9F6]/40 mt-4 font-light">
                  Accès immédiat • PDF téléchargeable
                </p>

                {/* Guarantee */}
                <div className="mt-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                  <div className="flex items-center gap-2 text-emerald-400 font-medium mb-2">
                    <Shield className="w-5 h-5" />
                    Garantie Satisfait ou Remboursé
                  </div>
                  <p className="text-sm text-emerald-400/70 font-light">
                    Si vous n'êtes pas satisfait, nous vous remboursons sous 30 jours. Sans condition.
                  </p>
                </div>
              </div>

              {/* After Payment */}
              <div className="card-mystical">
                <h3 className="text-xl mb-6" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                  Après Votre Paiement
                </h3>
                <div className="space-y-4 text-sm">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-[#C5A059]/20 flex items-center justify-center text-[#C5A059] font-medium">1</div>
                    <span className="text-[#E0D9F6]/80">Accès immédiat à votre étude complète</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-[#C5A059]/20 flex items-center justify-center text-[#C5A059] font-medium">2</div>
                    <span className="text-[#E0D9F6]/80">Génération de votre manuscrit PDF</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-[#C5A059]/20 flex items-center justify-center text-[#C5A059] font-medium">3</div>
                    <span className="text-[#E0D9F6]/80">Envoi par email avec lien permanent</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Paiement;
