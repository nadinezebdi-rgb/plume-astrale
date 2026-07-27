import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Star, RefreshCw, Lock, ArrowRight } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import LibraryImage from '@/components/LibraryImage';
import TarotCardBack from '@/components/TarotCardBack';

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
  const { isAuthenticated } = useAuth();
  const [cards, setCards] = useState([]);
  const [revealed, setRevealed] = useState([]);
  const canReveal = isAuthenticated;

  useEffect(() => {
    setCards(drawThree());
    setRevealed([]);
  }, []);

  const reveal = (i) => {
    if (!canReveal) return;
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
          <p className="text-[#D4AF37] uppercase tracking-[0.3em] text-sm mb-3 font-light">
            Tirage à 3 cartes
          </p>
          <h1 className="text-3xl md:text-5xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
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
            const clickable = canReveal && !isRevealed;
            return (
              <div
                key={i}
                onClick={() => reveal(i)}
                data-testid={`tarot-card-${i}`}
                className={`card-mystical text-center transition-all min-h-[280px] flex flex-col ${
                  clickable ? 'cursor-pointer hover:border-[#D4AF37] hover:scale-[1.02]' : ''
                } ${isRevealed ? 'border-[#D4AF37] glow-gold' : ''}`}
              >
                <p className="text-[#D4AF37] uppercase tracking-[0.25em] text-xs mb-3">
                  {POSITIONS[i]}
                </p>

                {isRevealed ? (
                  <div className="flex-1 flex flex-col">
                    {/* Image de la carte (bibliothèque Supabase, srcSet responsive) */}
                    <div className="mx-auto mb-3" style={{
                      width: 140, height: 200,
                      borderRadius: 8,
                      overflow: 'hidden',
                      border: '2px solid rgba(212,175,55,0.55)',
                      boxShadow: '0 8px 32px rgba(212,175,55,0.25)',
                    }}>
                      <LibraryImage
                        type="tarot"
                        name={card.name}
                        size={200}
                        alt={card.name}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      />
                    </div>
                    <h3 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                      {card.name}
                    </h3>
                    <p className={`text-xs uppercase tracking-widest mb-3 ${ELEMENT_COLOR[card.element] || 'text-[#D4AF37]'}`}>
                      Élément {card.element}
                    </p>
                    <p className="text-[#F5EEE0]/90 text-sm mb-3 font-light">
                      {card.meaning}
                    </p>
                    <p className="text-[#B8B0C8]/70 text-xs italic mt-auto">
                      « {card.advice} »
                    </p>
                  </div>
                ) : (
                  <div className="flex-1 flex flex-col items-center justify-center">
                    {canReveal ? (
                      <>
                        <TarotCardBack size={{ width: 130, height: 190 }} testId={`tarot-back-${i}`} />
                        <p className="text-[#B8B0C8]/70 text-sm mt-4">Cliquez pour révéler</p>
                      </>
                    ) : (
                      <>
                        <TarotCardBack size={{ width: 130, height: 190 }} testId={`tarot-back-locked-${i}`} />
                        <div className="flex items-center gap-2 mt-4">
                          <Lock className="w-4 h-4 text-[#D4AF37]/70" strokeWidth={1.5} />
                          <p className="text-[#B8B0C8]/70 text-sm">Connectez-vous</p>
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Actions */}
        {canReveal ? (
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
          <div className="card-mystical max-w-md mx-auto text-center" data-testid="tarot-signup-gate">
            <Lock className="w-8 h-8 mx-auto text-[#D4AF37] mb-3" strokeWidth={1.3} />
            <h3 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
              Créez votre compte pour révéler
            </h3>
            <p className="text-[#B8B0C8]/60 text-sm mb-5 font-light">
              20 crédits offerts à l&apos;inscription pour explorer votre thème natal.
            </p>
            <button onClick={() => navigate('/inscription?next=/tarot')}
              className="btn-mystical-filled rounded-full px-6 py-2.5 inline-flex items-center gap-2"
              data-testid="btn-signup">
              Créer un compte gratuit <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Vitrine des 22 arcanes majeurs — atteste de la vraie bibliothèque interne */}
        <div className="mt-20 text-center" data-testid="tarot-deck-preview">
          <p
            className="text-[#D4AF37] uppercase tracking-[0.28em] text-[11px] mb-4"
            style={{ fontFamily: 'Cinzel, serif' }}
          >
            ✦ Les 22 arcanes peints à la main ✦
          </p>
          <h3
            className="mb-2"
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: 'clamp(1.4rem, 3vw, 2rem)',
              color: '#F5EEE0',
              lineHeight: 1.15,
            }}
          >
            Un jeu unique, dessiné pour Plume Astrale
          </h3>
          <p className="text-[#B8B0C8]/70 text-sm max-w-xl mx-auto mb-8 font-light">
            Chaque carte de notre bibliothèque interne a été composée à la main dans l&apos;esprit
            du Tarot de Marseille — palette or nuit profonde, aucun visuel standard IA.
          </p>
          <div className="flex flex-wrap justify-center gap-2 sm:gap-3">
            {TAROT_DECK.map((c, idx) => (
              <div
                key={c.name}
                title={c.name}
                data-testid={`deck-preview-${idx}`}
                style={{
                  width: 60, height: 90,
                  borderRadius: 5,
                  overflow: 'hidden',
                  border: '1px solid rgba(212,175,55,0.35)',
                  boxShadow: '0 2px 10px rgba(0,0,0,0.4)',
                  background: '#0e0a24',
                }}
              >
                <LibraryImage
                  type="tarot"
                  name={c.name}
                  size={90}
                  alt={c.name}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Tarot;
