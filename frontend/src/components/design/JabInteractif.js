import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Sparkles } from 'lucide-react';
import { SOLENA } from '../../lib/solena';

/**
 * JabInteractif — "Jab" GaryVee : donner de la valeur GRATUITEMENT avant de vendre.
 *  - Portrait mystique de Solena en glassmorphism (colonne gauche).
 *  - 3 cartes cliquables [1] [2] [3] pour recevoir une guidance instantanée.
 *  - Au clic : la carte se retourne, révèle un message court + CTA pour ouvrir Solena Chat.
 *
 * Convertit sans friction, rassure, et engage émotionnellement en 5 secondes.
 */

const CARDS = [
  {
    id: 1,
    title: 'La Lune',
    message:
      "Tu portes une émotion qui n'a pas encore trouvé ses mots. Un cycle féminin s'achève — laisse-toi guider par ton intuition ces sept prochains jours.",
    keyword: 'Intuition',
  },
  {
    id: 2,
    title: "L'Étoile",
    message:
      "Une lumière que tu croyais éteinte revient. Une opportunité amoureuse ou spirituelle se dessine dans les 21 jours. Ouvre les yeux le vrai est plus près que tu ne penses.",
    keyword: 'Espoir',
  },
  {
    id: 3,
    title: 'Le Soleil',
    message:
      "Tu es sur le point de rayonner. Une clarté nouvelle t'attend — c'est le bon moment pour poser une question qui te ronge depuis longtemps. La réponse te trouvera.",
    keyword: 'Clarté',
  },
];

const CardFace = ({ card, revealed, onClick }) => (
  <motion.button
    onClick={onClick}
    whileHover={{ y: -6, scale: 1.02 }}
    whileTap={{ scale: 0.98 }}
    transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
    className="relative flex-1 min-w-0"
    style={{
      background: revealed
        ? 'linear-gradient(160deg, rgba(212,175,55,0.14) 0%, rgba(26,32,53,0.85) 100%)'
        : 'linear-gradient(160deg, rgba(26,32,53,0.75) 0%, rgba(17,22,37,0.9) 100%)',
      border: revealed
        ? '1px solid rgba(212,175,55,0.55)'
        : '1px solid rgba(212,175,55,0.20)',
      borderRadius: 22,
      padding: revealed ? '26px 20px' : '48px 20px',
      minHeight: 260,
      color: '#F5EEE0',
      cursor: 'pointer',
      textAlign: 'left',
      boxShadow: revealed
        ? '0 22px 60px rgba(212,175,55,0.18), 0 0 30px rgba(212,175,55,0.10)'
        : '0 10px 28px rgba(0,0,0,0.35)',
      backdropFilter: 'blur(14px)',
      WebkitBackdropFilter: 'blur(14px)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: revealed ? 'flex-start' : 'center',
      alignItems: revealed ? 'flex-start' : 'center',
      transition: 'padding 0.4s cubic-bezier(0.22, 1, 0.36, 1)',
    }}
    data-testid={`jab-card-${card.id}`}
    aria-label={`Carte ${card.id} — ${card.title}`}
  >
    <AnimatePresence mode="wait">
      {!revealed ? (
        <motion.div
          key="closed"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="flex flex-col items-center gap-3"
        >
          <div
            style={{
              width: 60,
              height: 60,
              borderRadius: '50%',
              border: '1px solid rgba(212,175,55,0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontFamily: 'Cinzel, serif',
              fontSize: 26,
              color: '#D4AF37',
              fontWeight: 300,
            }}
          >
            {card.id}
          </div>
          <p
            className="text-[10px] uppercase mt-2"
            style={{
              color: 'rgba(212,175,55,0.7)',
              letterSpacing: '0.28em',
              fontFamily: 'Cinzel, serif',
            }}
          >
            Cliquer pour révéler
          </p>
        </motion.div>
      ) : (
        <motion.div
          key="open"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center justify-between mb-3">
            <p
              className="text-[10px] uppercase"
              style={{
                color: '#D4AF37',
                letterSpacing: '0.32em',
                fontFamily: 'Cinzel, serif',
              }}
            >
              ✦ {card.keyword} ✦
            </p>
            <span
              style={{
                fontFamily: 'Cinzel, serif',
                fontSize: 14,
                color: 'rgba(212,175,55,0.55)',
              }}
            >
              {card.id}
            </span>
          </div>
          <h3
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: 24,
              lineHeight: 1.1,
              color: '#F5EEE0',
              fontWeight: 400,
              marginBottom: 12,
            }}
          >
            {card.title}
          </h3>
          <p
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontStyle: 'italic',
              color: 'rgba(227,215,255,0.85)',
              lineHeight: 1.55,
              fontSize: 15,
            }}
          >
            {card.message}
          </p>
        </motion.div>
      )}
    </AnimatePresence>
  </motion.button>
);

const JabInteractif = () => {
  const navigate = useNavigate();
  const [pickedId, setPickedId] = useState(null);

  const openSolena = () => {
    // Redirection vers la page de discussion avec Soléna
    navigate('/outils/consultation');
  };

  return (
    <section
      className="relative py-20 md:py-24 px-4 z-10"
      data-testid="jab-interactif-section"
      style={{
        background:
          'radial-gradient(ellipse 70% 60% at 50% 40%, rgba(212,175,55,0.05) 0%, transparent 70%)',
      }}
    >
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-14">
          <p
            className="text-[10px] uppercase mb-4"
            style={{
              color: 'rgba(212,175,55,0.8)',
              letterSpacing: '0.35em',
              fontFamily: 'Cinzel, serif',
            }}
          >
            ✦ Guidance immédiate ✦
          </p>
          <h2
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontWeight: 300,
              fontSize: 'clamp(2rem, 4.5vw, 3.2rem)',
              lineHeight: 1.1,
              color: '#F5EEE0',
              marginBottom: 14,
            }}
          >
            Choisis une carte, <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>reçois ton message</em>
          </h2>
          <p
            className="max-w-xl mx-auto text-base md:text-lg"
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              color: 'rgba(227,215,255,0.65)',
              fontStyle: 'italic',
              lineHeight: 1.55,
            }}
          >
            Trois cartes, une intuition. Ce que ton âme veut entendre aujourd&apos;hui.
          </p>
        </div>

        <div className="grid md:grid-cols-5 gap-8 md:gap-10 items-center">
          {/* Portrait Solena — glassmorphism */}
          <div className="md:col-span-2 flex justify-center">
            <div className="relative w-full max-w-xs">
              <div
                aria-hidden="true"
                style={{
                  position: 'absolute',
                  inset: '-14%',
                  background:
                    'radial-gradient(circle, rgba(212,175,55,0.35), transparent 65%)',
                  filter: 'blur(38px)',
                }}
              />
              <div
                style={{
                  position: 'relative',
                  aspectRatio: '9/13',
                  width: '100%',
                  borderRadius: 28,
                  overflow: 'hidden',
                  border: '1px solid rgba(212,175,55,0.35)',
                  boxShadow:
                    '0 30px 80px rgba(0,0,0,0.4), 0 0 40px rgba(212,175,55,0.12)',
                  background: '#111625',
                  backdropFilter: 'blur(14px)',
                }}
              >
                <img
                  src={SOLENA.portrait}
                  alt="Portrait de Solena"
                  loading="lazy"
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    objectPosition: 'center 15%',
                    display: 'block',
                  }}
                  data-testid="jab-solena-portrait"
                />
                <div
                  style={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    padding: '28px 22px 18px',
                    background:
                      'linear-gradient(180deg, transparent, rgba(0,0,0,0.72))',
                    pointerEvents: 'none',
                  }}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Sparkles style={{ width: 11, height: 11, color: '#D4AF37' }} strokeWidth={1.5} />
                    <p
                      className="text-[10px] uppercase"
                      style={{
                        color: '#D4AF37',
                        letterSpacing: '0.28em',
                        fontFamily: 'Cinzel, serif',
                      }}
                    >
                      Solena guide ton choix
                    </p>
                  </div>
                  <p
                    className="text-xs"
                    style={{
                      color: 'rgba(244,232,210,0.85)',
                      fontFamily: 'Cormorant Garamond, serif',
                      fontStyle: 'italic',
                      lineHeight: 1.45,
                    }}
                  >
                    Ferme les yeux, respire, et laisse une carte t&apos;appeler.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Colonne cartes — 3/5 */}
          <div className="md:col-span-3">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {CARDS.map((c) => (
                <CardFace
                  key={c.id}
                  card={c}
                  revealed={pickedId === c.id}
                  onClick={() => setPickedId(pickedId === c.id ? null : c.id)}
                />
              ))}
            </div>

            {/* CTA post-révélation */}
            <AnimatePresence>
              {pickedId && (
                <motion.div
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 8 }}
                  transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                  className="mt-8 text-center"
                >
                  <p
                    className="text-sm mb-4"
                    style={{
                      color: 'rgba(227,215,255,0.75)',
                      fontFamily: 'Cormorant Garamond, serif',
                      fontStyle: 'italic',
                      lineHeight: 1.55,
                    }}
                  >
                    Tu veux aller plus loin ? Solena décode ton ciel de naissance pour approfondir ce message.
                  </p>
                  <button
                    onClick={openSolena}
                    className="inline-flex items-center gap-2 px-7 py-3 rounded-full text-xs uppercase transition-all hover:scale-[1.02]"
                    style={{
                      background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 50%, #D4AF37 100%)',
                      color: '#111625',
                      letterSpacing: '0.2em',
                      fontWeight: 700,
                      boxShadow: '0 12px 40px rgba(212,175,55,0.30)',
                      border: 'none',
                      cursor: 'pointer',
                      fontFamily: 'Cinzel, serif',
                    }}
                    data-testid="jab-cta-solena"
                  >
                    Continuer avec Solena
                    <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
                  </button>
                  <p
                    className="text-[10px] mt-3"
                    style={{
                      color: 'rgba(212,175,55,0.5)',
                      letterSpacing: '0.22em',
                    }}
                  >
                    GRATUIT · SANS CARTE BANCAIRE
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
};

export default JabInteractif;
