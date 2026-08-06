import React, { useEffect, useState } from 'react';
import { Sparkles } from 'lucide-react';

/**
 * SolenaWritingLoader — Overlay plein écran affiché pendant que GPT-5.4
 * traduit + reformule le rapport natal de l'API v3 en voix Soléna.
 *
 * Message rotatif (7 étapes) pour occuper les ~60 secondes de génération.
 * Barre de progression déterministe basée sur un timing estimé.
 *
 * Usage :
 *   {loading && <SolenaWritingLoader estimatedSeconds={55} />}
 */

const STEPS = [
  { at: 0,   text: "Ton ciel s'aligne — je consulte tes 73 dimensions astrales…" },
  { at: 8,   text: "Je relis ton Soleil, ta Lune, tes 8 autres planètes…" },
  { at: 18,  text: "Je décrypte les aspects qui te distinguent des autres personnes de ton signe…" },
  { at: 28,  text: "J'écoute ce que tes planètes se disent entre elles…" },
  { at: 38,  text: "Je choisis chaque mot pour toi — pas pour ton signe, pour TOI…" },
  { at: 48,  text: "Je relie ta géographie astrale à ton histoire intérieure…" },
  { at: 58,  text: "Je finalise ta lecture — la mise en page, la signature…" },
];

const FLYING_WORDS = [
  '☉ Soleil', '☽ Lune', '♀ Vénus', '♂ Mars', '☿ Mercure',
  '♃ Jupiter', '♄ Saturne', '♆ Neptune', '♇ Pluton', '⚹ Aspects',
];

const SolenaWritingLoader = ({ estimatedSeconds = 55, testId = 'solena-writing-loader' }) => {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const t0 = Date.now();
    const iv = setInterval(() => {
      setElapsed(Math.floor((Date.now() - t0) / 1000));
    }, 500);
    return () => clearInterval(iv);
  }, []);

  // Message courant selon les secondes écoulées
  const currentStep = STEPS.reduce((acc, s) => (elapsed >= s.at ? s : acc), STEPS[0]);
  const progress = Math.min(99, Math.round((elapsed / estimatedSeconds) * 100));

  return (
    <div
      className="swl-overlay"
      data-testid={testId}
      role="dialog"
      aria-live="polite"
      aria-label="Génération de ton Thème Natal en cours"
    >
      {/* étoiles filantes en fond */}
      <div className="swl-stars">
        {[...Array(24)].map((_, i) => (
          <div
            key={i}
            className="swl-star"
            style={{
              left: `${(i * 37) % 100}%`,
              top: `${(i * 53) % 100}%`,
              animationDelay: `${(i * 0.3) % 4}s`,
            }}
          />
        ))}
      </div>

      {/* mots planétaires flottants */}
      <div className="swl-words" aria-hidden="true">
        {FLYING_WORDS.map((w, i) => (
          <span
            key={w}
            className="swl-word"
            style={{
              animationDelay: `${i * 1.2}s`,
              left: `${(i * 11 + 5) % 90}%`,
            }}
          >
            {w}
          </span>
        ))}
      </div>

      <div className="swl-card">
        {/* Signature Soléna */}
        <div className="swl-signature">
          <div className="swl-orb">
            <Sparkles className="w-5 h-5" strokeWidth={1.2} />
          </div>
          <div>
            <div className="swl-label">✦ Soléna écrit ta lecture ✦</div>
            <div className="swl-name">Plume Astrale</div>
          </div>
        </div>

        {/* Message rotatif */}
        <div className="swl-message-frame">
          <p className="swl-message" key={currentStep.at}>
            {currentStep.text}
          </p>
        </div>

        {/* Barre de progression */}
        <div className="swl-progress" aria-hidden="true">
          <div className="swl-progress-bar" style={{ width: `${progress}%` }} />
        </div>
        <div className="swl-meta">
          <span>{elapsed}s écoulées</span>
          <span>≈ 45–60 secondes de rédaction</span>
        </div>

        {/* Note discrète */}
        <p className="swl-note">
          Chaque phrase est écrite spécifiquement pour toi.
          Merci de ne pas fermer cette fenêtre.
        </p>
      </div>

      <style>{`
        .swl-overlay {
          position: fixed;
          inset: 0;
          z-index: 100;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 24px;
          background:
            radial-gradient(ellipse at 30% 20%, rgba(212,175,55,0.10), transparent 55%),
            radial-gradient(ellipse at 70% 80%, rgba(167,139,250,0.12), transparent 55%),
            linear-gradient(160deg, #0e0a1e 0%, #1a1230 50%, #0a0813 100%);
          backdrop-filter: blur(8px);
          -webkit-backdrop-filter: blur(8px);
          animation: swl-fade-in 0.6s ease-out;
        }
        @keyframes swl-fade-in {
          from { opacity: 0; }
          to   { opacity: 1; }
        }

        /* étoiles filantes */
        .swl-stars {
          position: absolute; inset: 0; overflow: hidden; pointer-events: none;
        }
        .swl-star {
          position: absolute;
          width: 2px; height: 2px;
          background: #D4AF37;
          border-radius: 50%;
          box-shadow: 0 0 4px rgba(212,175,55,0.8);
          animation: swl-twinkle 4s ease-in-out infinite;
        }
        @keyframes swl-twinkle {
          0%, 100% { opacity: 0.2; transform: scale(0.6); }
          50%      { opacity: 1;   transform: scale(1.4); }
        }

        /* mots flottants */
        .swl-words {
          position: absolute; inset: 0; overflow: hidden; pointer-events: none;
        }
        .swl-word {
          position: absolute;
          bottom: -40px;
          font-family: 'Cinzel', serif;
          font-size: 13px;
          letter-spacing: 0.2em;
          color: rgba(212,175,55,0.5);
          text-shadow: 0 0 8px rgba(212,175,55,0.35);
          animation: swl-rise 12s linear infinite;
          white-space: nowrap;
        }
        @keyframes swl-rise {
          0%   { transform: translateY(0) rotate(-2deg); opacity: 0; }
          10%  { opacity: 0.7; }
          80%  { opacity: 0.5; }
          100% { transform: translateY(-110vh) rotate(3deg); opacity: 0; }
        }

        /* carte centrale */
        .swl-card {
          position: relative;
          z-index: 1;
          width: 100%;
          max-width: 480px;
          padding: 36px 32px 32px;
          background: linear-gradient(160deg, rgba(26,18,48,0.86) 0%, rgba(14,10,30,0.92) 100%);
          border: 1px solid rgba(212,175,55,0.35);
          border-radius: 16px;
          box-shadow:
            0 40px 80px -20px rgba(0,0,0,0.6),
            inset 0 1px 0 rgba(212,175,55,0.08);
        }

        .swl-signature {
          display: flex; align-items: center; gap: 12px;
          margin-bottom: 20px;
          padding-bottom: 16px;
          border-bottom: 1px solid rgba(212,175,55,0.18);
        }
        .swl-orb {
          width: 40px; height: 40px;
          border-radius: 50%;
          background: radial-gradient(circle at 30% 30%,
            rgba(212,175,55,0.4), rgba(212,175,55,0.08));
          border: 1px solid rgba(212,175,55,0.55);
          display: flex; align-items: center; justify-content: center;
          color: #D4AF37;
          animation: swl-pulse 2.4s ease-in-out infinite;
        }
        @keyframes swl-pulse {
          0%, 100% { transform: scale(1);   box-shadow: 0 0 12px rgba(212,175,55,0.3); }
          50%      { transform: scale(1.08); box-shadow: 0 0 22px rgba(212,175,55,0.55); }
        }
        .swl-label {
          font-family: 'Cinzel', serif;
          font-size: 10px;
          letter-spacing: 0.32em;
          color: #D4AF37;
          text-transform: uppercase;
          margin-bottom: 3px;
        }
        .swl-name {
          font-family: 'Cormorant Garamond', serif;
          font-style: italic;
          font-size: 14px;
          color: rgba(245,238,224,0.7);
        }

        .swl-message-frame {
          min-height: 84px;
          margin-bottom: 22px;
          display: flex; align-items: center;
        }
        .swl-message {
          font-family: 'Cormorant Garamond', serif;
          font-size: 18px;
          line-height: 1.45;
          color: #F5EEE0;
          font-style: italic;
          animation: swl-msg-in 0.6s ease-out;
          text-align: center;
          width: 100%;
        }
        @keyframes swl-msg-in {
          from { opacity: 0; transform: translateY(6px); }
          to   { opacity: 1; transform: translateY(0);   }
        }

        .swl-progress {
          height: 3px;
          border-radius: 3px;
          background: rgba(212,175,55,0.12);
          overflow: hidden;
        }
        .swl-progress-bar {
          height: 100%;
          background: linear-gradient(90deg,
            rgba(212,175,55,0.4) 0%,
            #D4AF37 40%,
            #f5e19a 70%,
            #D4AF37 100%);
          transition: width 0.8s cubic-bezier(0.22, 1, 0.36, 1);
          box-shadow: 0 0 12px rgba(212,175,55,0.6);
        }

        .swl-meta {
          display: flex; justify-content: space-between;
          margin-top: 8px; margin-bottom: 20px;
          font-family: 'Cinzel', serif;
          font-size: 9px;
          letter-spacing: 0.24em;
          color: rgba(212,175,55,0.55);
          text-transform: uppercase;
        }

        .swl-note {
          font-family: 'Cormorant Garamond', serif;
          font-style: italic;
          font-size: 13px;
          color: rgba(227,215,255,0.55);
          text-align: center;
          line-height: 1.5;
          margin: 0;
        }

        @media (max-width: 500px) {
          .swl-card { padding: 26px 20px; }
          .swl-message { font-size: 16px; }
        }
      `}</style>
    </div>
  );
};

export default SolenaWritingLoader;
