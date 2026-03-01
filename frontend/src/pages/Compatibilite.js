import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, Sparkles, Star, Flame, ArrowRight, Tag, Loader2 } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Compatibilite = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [isPaid, setIsPaid] = useState(false);
  const [partnerSign, setPartnerSign] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [showPromo, setShowPromo] = useState(false);
  const [promoCode, setPromoCode] = useState('');
  const [promoError, setPromoError] = useState('');
  const [promoSuccess, setPromoSuccess] = useState('');
  const [promoLoading, setPromoLoading] = useState(false);

  const signes = [
    'Bélier', 'Taureau', 'Gémeaux', 'Cancer', 
    'Lion', 'Vierge', 'Balance', 'Scorpion',
    'Sagittaire', 'Capricorne', 'Verseau', 'Poissons'
  ];

  const getSigneFromDate = (dateStr) => {
    const date = new Date(dateStr);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    
    if ((month === 3 && day >= 21) || (month === 4 && day <= 19)) return 'Bélier';
    if ((month === 4 && day >= 20) || (month === 5 && day <= 20)) return 'Taureau';
    if ((month === 5 && day >= 21) || (month === 6 && day <= 20)) return 'Gémeaux';
    if ((month === 6 && day >= 21) || (month === 7 && day <= 22)) return 'Cancer';
    if ((month === 7 && day >= 23) || (month === 8 && day <= 22)) return 'Lion';
    if ((month === 8 && day >= 23) || (month === 9 && day <= 22)) return 'Vierge';
    if ((month === 9 && day >= 23) || (month === 10 && day <= 22)) return 'Balance';
    if ((month === 10 && day >= 23) || (month === 11 && day <= 21)) return 'Scorpion';
    if ((month === 11 && day >= 22) || (month === 12 && day <= 21)) return 'Sagittaire';
    if ((month === 12 && day >= 22) || (month === 1 && day <= 19)) return 'Capricorne';
    if ((month === 1 && day >= 20) || (month === 2 && day <= 18)) return 'Verseau';
    return 'Poissons';
  };

  const getCompatibility = (sign1, sign2) => {
    const compatibilityMatrix = {
      'Bélier': { 'Bélier': 70, 'Taureau': 55, 'Gémeaux': 85, 'Cancer': 50, 'Lion': 95, 'Vierge': 45, 'Balance': 75, 'Scorpion': 60, 'Sagittaire': 93, 'Capricorne': 40, 'Verseau': 80, 'Poissons': 65 },
      'Taureau': { 'Bélier': 55, 'Taureau': 85, 'Gémeaux': 45, 'Cancer': 90, 'Lion': 65, 'Vierge': 92, 'Balance': 70, 'Scorpion': 88, 'Sagittaire': 40, 'Capricorne': 95, 'Verseau': 35, 'Poissons': 85 },
      'Gémeaux': { 'Bélier': 85, 'Taureau': 45, 'Gémeaux': 75, 'Cancer': 50, 'Lion': 88, 'Vierge': 60, 'Balance': 93, 'Scorpion': 40, 'Sagittaire': 80, 'Capricorne': 45, 'Verseau': 95, 'Poissons': 55 },
      'Cancer': { 'Bélier': 50, 'Taureau': 90, 'Gémeaux': 50, 'Cancer': 80, 'Lion': 55, 'Vierge': 85, 'Balance': 60, 'Scorpion': 94, 'Sagittaire': 45, 'Capricorne': 70, 'Verseau': 40, 'Poissons': 96 },
      'Lion': { 'Bélier': 95, 'Taureau': 65, 'Gémeaux': 88, 'Cancer': 55, 'Lion': 75, 'Vierge': 50, 'Balance': 85, 'Scorpion': 60, 'Sagittaire': 92, 'Capricorne': 55, 'Verseau': 70, 'Poissons': 45 },
      'Vierge': { 'Bélier': 45, 'Taureau': 92, 'Gémeaux': 60, 'Cancer': 85, 'Lion': 50, 'Vierge': 78, 'Balance': 55, 'Scorpion': 88, 'Sagittaire': 40, 'Capricorne': 95, 'Verseau': 50, 'Poissons': 70 },
      'Balance': { 'Bélier': 75, 'Taureau': 70, 'Gémeaux': 93, 'Cancer': 60, 'Lion': 85, 'Vierge': 55, 'Balance': 80, 'Scorpion': 65, 'Sagittaire': 78, 'Capricorne': 50, 'Verseau': 90, 'Poissons': 60 },
      'Scorpion': { 'Bélier': 60, 'Taureau': 88, 'Gémeaux': 40, 'Cancer': 94, 'Lion': 60, 'Vierge': 88, 'Balance': 65, 'Scorpion': 85, 'Sagittaire': 55, 'Capricorne': 80, 'Verseau': 45, 'Poissons': 92 },
      'Sagittaire': { 'Bélier': 93, 'Taureau': 40, 'Gémeaux': 80, 'Cancer': 45, 'Lion': 92, 'Vierge': 40, 'Balance': 78, 'Scorpion': 55, 'Sagittaire': 82, 'Capricorne': 50, 'Verseau': 85, 'Poissons': 60 },
      'Capricorne': { 'Bélier': 40, 'Taureau': 95, 'Gémeaux': 45, 'Cancer': 70, 'Lion': 55, 'Vierge': 95, 'Balance': 50, 'Scorpion': 80, 'Sagittaire': 50, 'Capricorne': 85, 'Verseau': 55, 'Poissons': 75 },
      'Verseau': { 'Bélier': 80, 'Taureau': 35, 'Gémeaux': 95, 'Cancer': 40, 'Lion': 70, 'Vierge': 50, 'Balance': 90, 'Scorpion': 45, 'Sagittaire': 85, 'Capricorne': 55, 'Verseau': 78, 'Poissons': 60 },
      'Poissons': { 'Bélier': 65, 'Taureau': 85, 'Gémeaux': 55, 'Cancer': 96, 'Lion': 45, 'Vierge': 70, 'Balance': 60, 'Scorpion': 92, 'Sagittaire': 60, 'Capricorne': 75, 'Verseau': 60, 'Poissons': 88 }
    };
    
    return compatibilityMatrix[sign1]?.[sign2] || 50;
  };

  const getCompatibilityDetails = (score) => {
    if (score >= 90) return { level: 'Flamme Jumelle', color: 'text-pink-400', description: 'Une connexion rare et intense. Vos âmes vibrent à l\'unisson.' };
    if (score >= 80) return { level: 'Âmes Sœurs', color: 'text-emerald-400', description: 'Une harmonie naturelle. Vous vous comprenez intuitivement.' };
    if (score >= 70) return { level: 'Belle Alchimie', color: 'text-[#C5A059]', description: 'Une complémentarité enrichissante avec des défis stimulants.' };
    if (score >= 60) return { level: 'Connexion Possible', color: 'text-blue-400', description: 'Des efforts mutuels peuvent créer une belle relation.' };
    if (score >= 50) return { level: 'Travail Nécessaire', color: 'text-amber-400', description: 'Des différences à transcender pour grandir ensemble.' };
    return { level: 'Défi Karmique', color: 'text-red-400', description: 'Une relation d\'apprentissage intense. Leçons importantes à tirer.' };
  };

  useEffect(() => {
    const data = localStorage.getItem('plume_astrale_data');
    const paid = localStorage.getItem('plume_astrale_paid');
    const plan = localStorage.getItem('plume_astrale_plan');
    
    if (!data) {
      navigate('/formulaire');
      return;
    }
    
    setUserData(JSON.parse(data));
    setIsPaid(paid === 'true' && plan === 'premium');
  }, [navigate]);

  const handleCalculate = () => {
    if (partnerSign) {
      setShowResult(true);
    }
  };

  if (!userData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-2 border-[#C5A059] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const userSign = getSigneFromDate(userData.dateNaissance);
  const compatibility = partnerSign ? getCompatibility(userSign, partnerSign) : 0;
  const details = getCompatibilityDetails(compatibility);

  return (
    <div className="min-h-screen relative">
      <StarField />
      
      <div className="relative z-10 py-12 px-4 md:px-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-4 font-light">
              Compatibilité Amoureuse
            </p>
            
            <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              L'Alchimie des Cœurs
            </h1>
            
            <p className="text-lg text-[#E0D9F6]/70 font-light">
              Découvrez votre connexion cosmique
            </p>
          </div>

          {isPaid ? (
            <div className="space-y-8">
              {/* Your Sign */}
              <div className="card-mystical text-center">
                <p className="text-[#E0D9F6]/60 mb-2">Votre signe</p>
                <div className="flex items-center justify-center gap-3">
                  <Star className="w-6 h-6 text-[#C5A059]" strokeWidth={1} />
                  <span className="text-2xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                    {userSign}
                  </span>
                </div>
              </div>

              {/* Partner Selection */}
              <div className="card-mystical">
                <p className="text-center text-[#E0D9F6]/60 mb-6">Sélectionnez le signe de votre partenaire</p>
                <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
                  {signes.map((signe) => (
                    <button
                      key={signe}
                      onClick={() => setPartnerSign(signe)}
                      className={`p-3 rounded-lg transition-all ${
                        partnerSign === signe 
                          ? 'bg-[#C5A059] text-[#0F0518]' 
                          : 'bg-[#1A0B2E]/50 text-[#E0D9F6]/70 hover:bg-[#1A0B2E] border border-[#C5A059]/20'
                      }`}
                      data-testid={`sign-${signe}`}
                    >
                      {signe}
                    </button>
                  ))}
                </div>

                {partnerSign && !showResult && (
                  <button
                    onClick={handleCalculate}
                    className="btn-mystical-filled rounded-full flex items-center gap-2 mx-auto mt-8"
                    data-testid="btn-calculate"
                  >
                    <Heart className="w-4 h-4" />
                    Révéler notre compatibilité
                  </button>
                )}
              </div>

              {/* Result */}
              {showResult && (
                <div className="card-mystical text-center glow-gold animate-fade-in">
                  <div className="flex justify-center items-center gap-4 mb-8">
                    <div className="text-center">
                      <Star className="w-8 h-8 text-[#C5A059] mx-auto mb-2" strokeWidth={1} />
                      <p className="text-[#F3E5AB]">{userSign}</p>
                    </div>
                    <Heart className="w-10 h-10 text-pink-400 animate-pulse" />
                    <div className="text-center">
                      <Star className="w-8 h-8 text-[#C5A059] mx-auto mb-2" strokeWidth={1} />
                      <p className="text-[#F3E5AB]">{partnerSign}</p>
                    </div>
                  </div>

                  <div className="mb-6">
                    <div className="text-6xl font-bold text-gold-gradient mb-2" style={{ fontFamily: 'Cinzel, serif' }}>
                      {compatibility}%
                    </div>
                    <p className={`text-xl font-medium ${details.color}`}>
                      {details.level}
                    </p>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full h-3 bg-[#1A0B2E] rounded-full mb-6 overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-[#C5A059] to-[#FFD700] transition-all duration-1000"
                      style={{ width: `${compatibility}%` }}
                    />
                  </div>

                  <p className="text-[#E0D9F6]/70 font-light mb-8 max-w-lg mx-auto">
                    {details.description}
                  </p>

                  {/* Detailed Analysis */}
                  <div className="grid md:grid-cols-3 gap-4 text-left">
                    <div className="bg-[#1A0B2E]/50 rounded-xl p-4 border border-[#C5A059]/10">
                      <Flame className="w-5 h-5 text-red-400 mb-2" />
                      <p className="text-[#F3E5AB] text-sm mb-1">Passion</p>
                      <p className="text-[#E0D9F6]/50 text-xs">Intensité émotionnelle forte. Attention aux tempêtes.</p>
                    </div>
                    <div className="bg-[#1A0B2E]/50 rounded-xl p-4 border border-[#C5A059]/10">
                      <Heart className="w-5 h-5 text-pink-400 mb-2" />
                      <p className="text-[#F3E5AB] text-sm mb-1">Affection</p>
                      <p className="text-[#E0D9F6]/50 text-xs">Tendresse naturelle. Communication du cœur fluide.</p>
                    </div>
                    <div className="bg-[#1A0B2E]/50 rounded-xl p-4 border border-[#C5A059]/10">
                      <Star className="w-5 h-5 text-[#C5A059] mb-2" />
                      <p className="text-[#F3E5AB] text-sm mb-1">Durabilité</p>
                      <p className="text-[#E0D9F6]/50 text-xs">Fondations solides si respect mutuel maintenu.</p>
                    </div>
                  </div>

                  <button
                    onClick={() => { setPartnerSign(''); setShowResult(false); }}
                    className="btn-mystical rounded-full mt-8"
                    data-testid="btn-new-compatibility"
                  >
                    Tester une autre compatibilité
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="card-mystical max-w-md mx-auto text-center">
              <Heart className="w-12 h-12 text-[#C5A059] mx-auto mb-4" strokeWidth={1} />
              <h3 className="text-xl mb-2" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                Compatibilité Premium
              </h3>
              <p className="text-[#E0D9F6]/60 mb-6 font-light">
                Débloquez l'analyse de compatibilité avec l'offre Premium
              </p>
              <button
                onClick={() => navigate('/choix')}
                className="btn-mystical-filled rounded-full"
                data-testid="btn-unlock-compatibility"
              >
                Recevoir mon manuscrit complet
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Compatibilite;
