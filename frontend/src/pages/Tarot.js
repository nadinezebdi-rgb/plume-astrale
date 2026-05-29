import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Star, RefreshCw, Lock, ArrowRight } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const TAROT_DECK = [
  { name: 'Le Bateleur', meaning: 'Nouveau départ, potentiel à révéler.', advice: 'Passez à l\'action avec confiance.', element: 'Feu' },
  { name: 'La Papesse', meaning: 'Intuition profonde et sagesse cachée.', advice: 'Écoutez votre voix intérieure.', element: 'Eau' },
  { name: 'L\'Impératrice', meaning: 'Créativité, abondance, fertilité.', advice: 'Exprimez votre puissance créatrice.', element: 'Terre' },
  { name: 'L\'Empereur', meaning: 'Structure, autorité, stabilité.', advice: 'Organisez votre territoire.', element: 'Feu' },
  { name: 'Le Pape', meaning: 'Sagesse spirituelle, transmission.', advice: 'Cherchez un guide ou enseignement.', element: 'Air' },
  { name: 'L\'Amoureux', meaning: 'Choix du cœur, union.', advice: 'Suivez ce qui vibre en vous.', element: 'Air' },
  { name: 'Le Chariot', meaning: 'Victoire, volonté, élan.', advice: 'Avancez avec détermination.', element: 'Eau' },
  { name: 'La Justice', meaning: 'Équilibre, vérité, karma.', advice: 'Soyez juste avec vous-même.', element: 'Air' },
  { name: 'L\'Hermite', meaning: 'Introspection, quête intérieure.', advice: 'Prenez du recul, méditez.', element: 'Terre' },
  { name: 'La Roue de Fortune', meaning: 'Cycles, changement de cap.', advice: 'Acceptez les vagues du destin.', element: 'Feu' },
  { name: 'La Force', meaning: 'Courage, maîtrise douce.', advice: 'Apprivoisez vos émotions.', element: 'Feu' },
  { name: 'Le Pendu', meaning: 'Lâcher-prise, nouvelle perspective.', advice: 'Changez d\'angle de vue.', element: 'Eau' },
  { name: 'L\'Arcane sans Nom', meaning: 'Transformation profonde.', advice: 'Acceptez ce qui s\'achève.', element: 'Eau' },
  { name: 'Tempérance', meaning: 'Équilibre, alchimie intérieure.', advice: 'Trouvez la juste mesure.', element: 'Feu' },
  { name: 'Le Diable', meaning: 'Attachements, passions terrestres.', advice: 'Identifiez ce qui vous lie.', element: 'Terre' },
  { name: 'La Maison Dieu', meaning: 'Rupture, révélation, libération.', advice: 'Accueillez la vérité qui éclate.', element: 'Feu' },
  { name: 'L\'Étoile', meaning: 'Espoir, inspiration, guidance.', advice: 'Gardez foi en votre étoile.', element: 'Air' },
  { name: 'La Lune', meaning: 'Inconscient, rêves, illusions.', advice: 'Distinguez l\'imaginaire du réel.', element: 'Eau' },
  { name: 'Le Soleil', meaning: 'Succès, joie rayonnante.', advice: 'Célébrez votre lumière.', element: 'Feu' },
  { name: 'Le Jugement', meaning: 'Renaissance, appel intérieur.', advice: 'Éveillez-vous à votre mission.', element: 'Air' },
  { name: 'Le Monde', meaning: 'Accomplissement, unité.', advice: 'Savourez la complétude.', element: 'Terre' },
  { name: 'Le Mat', meaning: 'Liberté, élan vers l\'inconnu.', advice: 'Osez le saut dans l\'infini.', element: 'Air' },
];

const POSITIONS = ['Passé', 'Présent', 'Avenir'];

const ELEMENT_COLOR = {
  Feu: 'text-red-300',
  Eau: 'text-blue-300',
  Terre: 'text-emerald-300',
  Air: 'text-amber-200',
};

const drawThree = () => {
  const shuffled = [...TAROT_DECK].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, 3);
};

const Tarot = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const [cards, setCards] = useState([]);
  const [revealed, setRevealed] = useState([]);
  const isPremium = user?.is_premium;

  useEffect(() => {
    setCards(drawThree());
    setRevealed([]);
  }, []);

  const reveal = (i) => {
    if (!isPremium) return;
    setRevealed(prev => prev.includes(i) ? prev : [...prev, i]);
  };

  const reshuffle = () => {
    setCards(drawThree());
    setRevealed([]);
  };

  return (
    <div className="min-h-screen px-6 md:px-8 py-20 md:py-28" data-testid="tarot-page">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-3 font-light">
            Tirage à 3 cartes
          </p>
          <h1 className="text-3xl md:text-5xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
            Le Tarot de Marseille
          </h1>
          <p className="text-base text-[#B8B0C8]/70 font-light max-w-xl mx-auto">
            Trois lames pour éclairer votre passé, votre présent, votre devenir.
          </p>
        </div>

        {/* Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mb-10">
          {cards.map((card, i) => {
            const isRevealed = revealed.includes(i);
            const canReveal = isPremium && !isRevealed;
            return (
              <div
                key={i}
                onClick={() => reveal(i)}
                data-testid={`tarot-card-${i}`}
                className={`card-mystical text-center transition-all min-h-[280px] flex flex-col ${
                  canReveal ? 'cursor-pointer hover:border-[#C5A059] hover:scale-[1.02]' : ''
                } ${isRevealed ? 'border-[#C5A059] glow-gold' : ''}`}
              >
                <p className="text-[#C5A059] uppercase tracking-[0.25em] text-xs mb-3">
                  {POSITIONS[i]}
                </p>

                {isRevealed ? (
                  <div className="flex-1 flex flex-col">
                    <Star className="w-8 h-8 mx-auto text-[#C5A059] mb-3" strokeWidth={1.2} />
                    <h3 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                      {card.name}
                    </h3>
                    <p className={`text-xs uppercase tracking-widest mb-3 ${ELEMENT_COLOR[card.element] || 'text-[#C5A059]'}`}>
                      Élément {card.element}
                    </p>
                    <p className="text-[#F0E6D3]/90 text-sm mb-3 font-light">
                      {card.meaning}
                    </p>
                    <p className="text-[#B8B0C8]/70 text-xs italic mt-auto">
                      « {card.advice} »
                    </p>
                  </div>
                ) : (
                  <div className="flex-1 flex flex-col items-center justify-center">
                    {isPremium ? (
                      <>
                        <div className="w-20 h-28 mx-auto mb-4 rounded-md border-2 border-[#C5A059]/40 bg-gradient-to-b from-[#1a1432] to-[#0C0918] flex items-center justify-center">
                          <Sparkles className="w-7 h-7 text-[#C5A059]/60" strokeWidth={1} />
                        </div>
                        <p className="text-[#B8B0C8]/60 text-sm">Cliquez pour révéler</p>
                      </>
                    ) : (
                      <>
                        <Lock className="w-7 h-7 mx-auto text-[#C5A059]/60 mb-3" strokeWidth={1.4} />
                        <p className="text-[#B8B0C8]/60 text-sm">Premium requis</p>
                      </>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Actions */}
        {isPremium ? (
          <div className="flex flex-col sm:flex-row justify-center gap-3" data-testid="tarot-actions">
            <button
              onClick={reshuffle}
              className="btn-mystical rounded-full px-6 py-2.5 flex items-center gap-2 justify-center"
              data-testid="btn-reshuffle"
            >
              <RefreshCw className="w-4 h-4" /> Nouveau tirage
            </button>
            <button
              onClick={() => navigate('/tarologie')}
              className="btn-mystical-filled rounded-full px-6 py-2.5 flex items-center gap-2 justify-center"
              data-testid="btn-tarologie"
            >
              Tirage approfondi <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="card-mystical max-w-md mx-auto text-center" data-testid="tarot-premium-gate">
            <Lock className="w-8 h-8 mx-auto text-[#C5A059] mb-3" strokeWidth={1.3} />
            <h3 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
              Réservé aux membres Premium
            </h3>
            <p className="text-[#B8B0C8]/60 text-sm mb-5 font-light">
              7 jours d'essai gratuit — annulable à tout moment.
            </p>
            {isAuthenticated ? (
              <button onClick={() => navigate('/premium')}
                className="btn-mystical-filled rounded-full px-6 py-2.5 inline-flex items-center gap-2"
                data-testid="btn-premium">
                <Sparkles className="w-4 h-4" /> Découvrir Premium
              </button>
            ) : (
              <button onClick={() => navigate('/inscription?next=/tarot')}
                className="btn-mystical-filled rounded-full px-6 py-2.5 inline-flex items-center gap-2"
                data-testid="btn-signup">
                Créer un compte <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Tarot;
