import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sun, Moon, Star, Heart, Briefcase, Activity, Coins, RefreshCw } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const Horoscope = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [activeTab, setActiveTab] = useState('jour');

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

  const horoscopes = {
    jour: {
      title: "Horoscope du Jour",
      date: new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' }),
      general: "Les astres vous invitent aujourd'hui à écouter votre intuition. Une opportunité inattendue pourrait se présenter dans l'après-midi. Restez ouvert(e) aux signes de l'univers.",
      amour: { score: 4, text: "Vénus vous sourit. Si vous êtes en couple, profitez de moments tendres. Célibataire ? Une rencontre significative est possible." },
      travail: { score: 3, text: "Mercure en transit suggère de la prudence dans vos communications. Relisez vos emails avant de les envoyer." },
      sante: { score: 5, text: "Excellente vitalité ! La Lune soutient votre énergie. Profitez-en pour commencer une nouvelle routine bien-être." },
      finance: { score: 3, text: "Évitez les dépenses impulsives aujourd'hui. Une bonne affaire pourrait arriver bientôt, gardez vos ressources." }
    },
    semaine: {
      title: "Horoscope de la Semaine",
      date: "15 - 21 Février 2026",
      general: "Cette semaine marque un tournant important. Les énergies cosmiques favorisent les nouveaux départs et les transformations profondes. C'est le moment idéal pour lancer un projet qui vous tient à cœur.",
      amour: { score: 4, text: "Semaine propice aux discussions profondes avec votre partenaire. Les célibataires pourraient faire une rencontre importante mercredi." },
      travail: { score: 5, text: "Excellent moment pour les négociations et les présentations. Votre charisme naturel impressionne vos interlocuteurs." },
      sante: { score: 3, text: "Attention à la fatigue en milieu de semaine. Accordez-vous des moments de repos et privilégiez un sommeil réparateur." },
      finance: { score: 4, text: "Une rentrée d'argent imprévue est possible. C'est aussi le bon moment pour revoir votre budget." }
    },
    mois: {
      title: "Horoscope de Février 2026",
      date: "Février 2026",
      general: "Février est un mois de transformation intérieure. La pleine Lune du 12 illumine votre secteur émotionnel, vous invitant à faire le tri dans vos relations. La fin du mois apporte de nouvelles opportunités de croissance.",
      amour: { score: 5, text: "Mois béni pour l'amour. Les couples renforcent leurs liens. Les célibataires sont particulièrement magnétiques autour du 14." },
      travail: { score: 4, text: "Des projets en sommeil reprennent vie. Votre créativité est à son apogée. Utilisez-la pour impressionner." },
      sante: { score: 4, text: "Énergie stable avec un pic de vitalité vers le 20. Bon mois pour commencer une nouvelle discipline sportive." },
      finance: { score: 3, text: "Prudence en début de mois. La deuxième quinzaine est plus favorable aux investissements et aux achats importants." }
    }
  };

  useEffect(() => {
    const data = localStorage.getItem('plume_astrale_data');
    if (!data) {
      navigate('/formulaire');
      return;
    }
    setUserData(JSON.parse(data));
  }, [navigate]);

  const renderStars = (score) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((i) => (
          <Star 
            key={i} 
            className={`w-4 h-4 ${i <= score ? 'text-[#C5A059] fill-[#C5A059]' : 'text-[#E0D9F6]/20'}`} 
            strokeWidth={1} 
          />
        ))}
      </div>
    );
  };

  if (!userData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-2 border-[#C5A059] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const userSign = getSigneFromDate(userData.dateNaissance);
  const currentHoroscope = horoscopes[activeTab];

  return (
    <div className="min-h-screen relative">
      <StarField />
      
      <div className="relative z-10 py-12 px-4 md:px-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-4 font-light">
              Votre Horoscope
            </p>
            
            <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              {userSign}
            </h1>
            
            <p className="text-lg text-[#E0D9F6]/70 font-light">
              {userData.prenom ? `${userData.prenom}, ` : ''}découvrez ce que les astres vous réservent
            </p>
          </div>

          {/* Tabs */}
          <div className="flex justify-center gap-2 mb-8">
            {[
              { id: 'jour', label: 'Jour', icon: <Sun className="w-4 h-4" strokeWidth={1} /> },
              { id: 'semaine', label: 'Semaine', icon: <Star className="w-4 h-4" strokeWidth={1} /> },
              { id: 'mois', label: 'Mois', icon: <Moon className="w-4 h-4" strokeWidth={1} /> }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-3 rounded-full text-sm transition-all ${
                  activeTab === tab.id 
                    ? 'bg-[#C5A059] text-[#0F0518]' 
                    : 'bg-[#1A0B2E]/50 text-[#E0D9F6]/70 hover:bg-[#1A0B2E] border border-[#C5A059]/20'
                }`}
                data-testid={`tab-${tab.id}`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>

          {/* Horoscope Content */}
          <div className="space-y-6 animate-fade-in">
            {/* General */}
            <div className="card-mystical">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                  {currentHoroscope.title}
                </h2>
                <span className="text-[#C5A059] text-sm">{currentHoroscope.date}</span>
              </div>
              <p className="text-[#E0D9F6]/80 font-light leading-relaxed">
                {currentHoroscope.general}
              </p>
            </div>

            {/* Categories */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Amour */}
              <div className="card-mystical">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 rounded-full bg-pink-500/20 text-pink-400">
                    <Heart className="w-5 h-5" strokeWidth={1} />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-[#F3E5AB]">Amour</h3>
                    {renderStars(currentHoroscope.amour.score)}
                  </div>
                </div>
                <p className="text-[#E0D9F6]/70 text-sm font-light">
                  {currentHoroscope.amour.text}
                </p>
              </div>

              {/* Travail */}
              <div className="card-mystical">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 rounded-full bg-blue-500/20 text-blue-400">
                    <Briefcase className="w-5 h-5" strokeWidth={1} />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-[#F3E5AB]">Travail</h3>
                    {renderStars(currentHoroscope.travail.score)}
                  </div>
                </div>
                <p className="text-[#E0D9F6]/70 text-sm font-light">
                  {currentHoroscope.travail.text}
                </p>
              </div>

              {/* Santé */}
              <div className="card-mystical">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 rounded-full bg-emerald-500/20 text-emerald-400">
                    <Activity className="w-5 h-5" strokeWidth={1} />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-[#F3E5AB]">Santé</h3>
                    {renderStars(currentHoroscope.sante.score)}
                  </div>
                </div>
                <p className="text-[#E0D9F6]/70 text-sm font-light">
                  {currentHoroscope.sante.text}
                </p>
              </div>

              {/* Finance */}
              <div className="card-mystical">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 rounded-full bg-[#C5A059]/20 text-[#C5A059]">
                    <Coins className="w-5 h-5" strokeWidth={1} />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-[#F3E5AB]">Finances</h3>
                    {renderStars(currentHoroscope.finance.score)}
                  </div>
                </div>
                <p className="text-[#E0D9F6]/70 text-sm font-light">
                  {currentHoroscope.finance.text}
                </p>
              </div>
            </div>

            {/* Lucky Numbers */}
            <div className="card-mystical text-center">
              <h3 className="text-lg mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                Nombres Chanceux
              </h3>
              <div className="flex justify-center gap-4">
                {[3, 7, 12, 21, 33].map((num) => (
                  <div 
                    key={num}
                    className="w-12 h-12 rounded-full bg-[#C5A059]/20 border border-[#C5A059]/30 flex items-center justify-center text-[#C5A059] font-medium"
                  >
                    {num}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Refresh Notice */}
          <div className="mt-8 text-center text-[#E0D9F6]/40 text-sm flex items-center justify-center gap-2">
            <RefreshCw className="w-4 h-4" />
            <span>Horoscope mis à jour chaque jour à minuit</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Horoscope;
