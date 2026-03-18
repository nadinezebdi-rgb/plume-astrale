import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Sparkles, Star, Moon, Sun, RefreshCw, 
  ArrowRight, Heart, Briefcase, Eye, ChevronDown,
  Flame, Droplets, Wind, Mountain
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const TirageDuJour = () => {
  const [tirage, setTirage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRevealed, setIsRevealed] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  // Charger le tirage du jour
  useEffect(() => {
    const fetchTirage = async () => {
      try {
        const response = await fetch(`${API_URL}/api/tarot/jour`);
        const data = await response.json();
        if (data.success) {
          setTirage(data.data);
        }
      } catch (error) {
        console.error('Erreur tirage du jour:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTirage();
  }, []);

  // Icône de l'élément
  const getElementIcon = (element) => {
    switch(element) {
      case 'Feu': return <Flame className="w-4 h-4 text-orange-400" />;
      case 'Eau': return <Droplets className="w-4 h-4 text-blue-400" />;
      case 'Air': return <Wind className="w-4 h-4 text-cyan-400" />;
      case 'Terre': return <Mountain className="w-4 h-4 text-green-400" />;
      default: return <Star className="w-4 h-4 text-[#C5A059]" />;
    }
  };

  if (isLoading) {
    return (
      <div className="card-mystical p-8 text-center">
        <div className="w-8 h-8 border-2 border-[#C5A059] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-[#B8B0C8]/60">Consultation des arcanes...</p>
      </div>
    );
  }

  if (!tirage) {
    return null;
  }

  const carte = tirage.carte;

  return (
    <div className="card-mystical overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#C5A059]/20 via-[#C5A059]/10 to-[#C5A059]/20 px-6 py-4 border-b border-[#C5A059]/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#C5A059]/20 flex items-center justify-center">
              <Sun className="w-5 h-5 text-[#C5A059]" strokeWidth={1.5} />
            </div>
            <div>
              <h3 className="text-lg text-[#F0E6D3]" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                Carte du Jour
              </h3>
              <p className="text-xs text-[#B8B0C8]/60">{tirage.date_fr}</p>
            </div>
          </div>
          <span className="text-xs bg-[#C5A059]/20 text-[#C5A059] px-3 py-1 rounded-full border border-[#C5A059]/30">
            GRATUIT
          </span>
        </div>
      </div>

      <div className="p-6">
        {/* Carte non révélée */}
        {!isRevealed && (
          <div className="text-center">
            <p className="text-[#B8B0C8]/70 mb-6 font-light">
              Votre guidance quotidienne vous attend...
            </p>
            
            {/* Carte face cachée */}
            <div 
              className="w-32 h-48 mx-auto rounded-xl bg-gradient-to-b from-[#2D1F4B] via-[#251A52] to-[#1A1050] border-2 border-[#C5A059]/50 flex flex-col items-center justify-center shadow-xl shadow-[#C5A059]/20 cursor-pointer hover:border-[#C5A059] hover:shadow-[#C5A059]/40 transition-all group mb-6"
              onClick={() => setIsRevealed(true)}
            >
              {/* Motif décoratif */}
              <div className="absolute inset-0 opacity-30 pointer-events-none">
                <div className="absolute inset-4 border border-[#C5A059]/50 rounded-lg"></div>
              </div>
              <Star className="w-14 h-14 text-[#C5A059]/60 group-hover:text-[#C5A059] transition-colors" strokeWidth={1} />
              <Moon className="w-6 h-6 text-[#C5A059]/40 mt-2" strokeWidth={1} />
            </div>

            <button
              onClick={() => setIsRevealed(true)}
              className="btn-mystical-filled rounded-xl py-3 px-8 flex items-center gap-2 mx-auto"
            >
              <Eye className="w-5 h-5" strokeWidth={1.5} />
              Révéler ma carte
              <Sparkles className="w-5 h-5" strokeWidth={1.5} />
            </button>
          </div>
        )}

        {/* Carte révélée */}
        {isRevealed && (
          <div className="animate-fadeIn">
            {/* Carte et infos principales */}
            <div className="flex flex-col md:flex-row gap-6 items-center md:items-start">
              {/* Carte visuelle */}
              <div className={`w-32 h-48 flex-shrink-0 rounded-xl bg-gradient-to-b from-[#2D1F4B] to-[#251A52] border-2 ${
                carte.orientation === 'droit' ? 'border-[#C5A059]/60' : 'border-purple-500/60'
              } flex flex-col items-center justify-center shadow-xl relative overflow-hidden ${
                carte.orientation === 'renverse' ? 'rotate-180' : ''
              }`}>
                <div className="text-center">
                  <Sparkles className={`w-10 h-10 mx-auto mb-2 ${
                    carte.orientation === 'droit' ? 'text-[#C5A059]' : 'text-purple-400'
                  }`} strokeWidth={1} />
                  <span className="text-[#C5A059] text-3xl font-bold" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                    {carte.numero}
                  </span>
                </div>
              </div>

              {/* Infos de la carte */}
              <div className="flex-1 text-center md:text-left">
                <h4 className="text-2xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                  {carte.nom}
                </h4>
                
                {/* Badges */}
                <div className="flex flex-wrap gap-2 justify-center md:justify-start mb-4">
                  <span className={`inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full ${
                    carte.orientation === 'droit' 
                      ? 'bg-[#C5A059]/20 text-[#C5A059] border border-[#C5A059]/30' 
                      : 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                  }`}>
                    {carte.orientation === 'droit' ? <Sun className="w-3 h-3" /> : <Moon className="w-3 h-3" />}
                    {carte.orientation_fr}
                  </span>
                  <span className="inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full bg-[#251A52] text-[#B8B0C8]/70 border border-[#C5A059]/20">
                    {getElementIcon(carte.element)}
                    {carte.element}
                  </span>
                  <span className="text-xs px-3 py-1 rounded-full bg-[#251A52] text-[#B8B0C8]/70 border border-[#C5A059]/20">
                    ☆ {carte.planete}
                  </span>
                </div>

                {/* Mots-clés */}
                <div className="flex flex-wrap gap-1 justify-center md:justify-start mb-4">
                  {carte.mots_cles?.map((mot, i) => (
                    <span key={i} className="text-xs text-[#C5A059] bg-[#C5A059]/10 px-2 py-0.5 rounded-full">
                      {mot}
                    </span>
                  ))}
                </div>

                {/* Message principal */}
                <p className="text-[#B8B0C8]/80 font-light leading-relaxed mb-4">
                  {carte.interpretation_generale}
                </p>

                {/* Message énergie */}
                <div className="bg-[#C5A059]/10 rounded-lg p-4 border border-[#C5A059]/20 mb-4">
                  <p className="text-[#C5A059] text-sm italic">
                    ✨ {tirage.message_energie}
                  </p>
                </div>
              </div>
            </div>

            {/* Section dépliable - Détails */}
            <div className="mt-6 border-t border-[#C5A059]/20 pt-4">
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="w-full flex items-center justify-between text-[#C5A059] hover:text-[#D4AF37] transition-colors"
              >
                <span className="text-sm font-light">Voir plus de détails</span>
                <ChevronDown className={`w-5 h-5 transition-transform ${showDetails ? 'rotate-180' : ''}`} />
              </button>

              {showDetails && (
                <div className="mt-4 space-y-4 animate-fadeIn">
                  {/* Affirmation du jour */}
                  <div className="bg-gradient-to-r from-[#2D1F4B] to-[#251A52] rounded-lg p-4 border border-[#C5A059]/20">
                    <h5 className="text-[#C5A059] text-sm mb-2 flex items-center gap-2">
                      <Sparkles className="w-4 h-4" /> Affirmation du Jour
                    </h5>
                    <p className="text-[#F0E6D3] italic font-light">
                      "{tirage.affirmation_du_jour}"
                    </p>
                  </div>

                  {/* Amour et Travail */}
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-[#251A52]/50 rounded-lg p-4 border border-pink-500/20">
                      <h5 className="text-pink-400 text-sm mb-2 flex items-center gap-2">
                        <Heart className="w-4 h-4" /> En Amour
                      </h5>
                      <p className="text-[#B8B0C8]/70 text-sm font-light">
                        {carte.interpretation_amour}
                      </p>
                    </div>
                    <div className="bg-[#251A52]/50 rounded-lg p-4 border border-blue-500/20">
                      <h5 className="text-blue-400 text-sm mb-2 flex items-center gap-2">
                        <Briefcase className="w-4 h-4" /> Au Travail
                      </h5>
                      <p className="text-[#B8B0C8]/70 text-sm font-light">
                        {carte.interpretation_travail}
                      </p>
                    </div>
                  </div>

                  {/* Rituel suggéré */}
                  <div className="bg-[#C5A059]/5 rounded-lg p-4 border border-[#C5A059]/20">
                    <h5 className="text-[#C5A059] text-sm mb-2 flex items-center gap-2">
                      {getElementIcon(carte.element)} Rituel Suggéré ({carte.element})
                    </h5>
                    <p className="text-[#B8B0C8]/80 text-sm font-light">
                      {tirage.rituel_suggere}
                    </p>
                  </div>

                  {/* Conseil */}
                  <div className="text-center bg-gradient-to-r from-[#C5A059]/10 via-[#C5A059]/20 to-[#C5A059]/10 rounded-lg p-4 border border-[#C5A059]/30">
                    <p className="text-[#C5A059] italic">
                      💫 {carte.conseil}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* CTA vers tirage complet */}
            <div className="mt-6 pt-4 border-t border-[#C5A059]/20 text-center">
              <p className="text-[#B8B0C8]/60 text-sm mb-4">
                Envie d'aller plus loin ?
              </p>
              <Link
                to="/tirage-tarot"
                className="btn-mystical rounded-xl py-3 px-6 inline-flex items-center gap-2"
              >
                Tirage complet avec votre question
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TirageDuJour;
