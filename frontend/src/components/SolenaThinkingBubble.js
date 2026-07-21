import React, { useEffect, useState } from 'react';

/**
 * SolenaThinkingBubble — Bulle inline "Soléna réfléchit" pour le chat.
 *
 * Cycle de 90 secondes maximum couvert par 12 messages poétiques qui évoluent
 * progressivement pour maintenir l'attention (et l'espoir) du visiteur.
 * Fin de cycle → boucle discrète sur les 4 derniers messages "elle affine…".
 *
 * Design : bulle discrète alignée à gauche (côté assistant), 3 points animés
 * en séquence, message rotatif en italique, barre de souffle très fine.
 */

const STEPS = [
  { at: 0,   text: "Soléna reçoit ta question…" },
  { at: 4,   text: "Elle relit ton ciel de naissance…" },
  { at: 10,  text: "Elle écoute ce que ton Soleil te répond…" },
  { at: 18,  text: "Elle consulte ta Lune et ta Vénus…" },
  { at: 26,  text: "Elle regarde ce que Mars te propose ces jours-ci…" },
  { at: 34,  text: "Elle décrypte les aspects qui te concernent…" },
  { at: 44,  text: "Elle choisit chaque mot pour toi, pas pour ton signe…" },
  { at: 54,  text: "Elle relie ta question à ton chemin d'âme…" },
  { at: 62,  text: "Elle prend un instant pour te répondre juste…" },
  { at: 72,  text: "Elle finalise sa réponse — encore quelques mots…" },
  { at: 82,  text: "Elle affine la formulation pour que ça résonne…" },
  { at: 90,  text: "Elle est presque prête — merci pour ta patience…" },
];

const SolenaThinkingBubble = ({ testId = 'solena-thinking-bubble' }) => {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const t0 = Date.now();
    const iv = setInterval(() => {
      setElapsed(Math.floor((Date.now() - t0) / 1000));
    }, 400);
    return () => clearInterval(iv);
  }, []);

  const step = STEPS.reduce((acc, s) => (elapsed >= s.at ? s : acc), STEPS[0]);
  // Barre de souffle : progresse jusqu'à 92% puis oscille (Soléna termine).
  const rawProgress = Math.min(92, (elapsed / 90) * 100);
  const breathing = Math.sin(elapsed / 1.4) * 2;
  const progress = elapsed >= 90 ? 88 + breathing : rawProgress;

  return (
    <div
      style={{ display: 'flex', justifyContent: 'flex-start' }}
      data-testid={testId}
      role="status"
      aria-live="polite"
      aria-label="Soléna réfléchit à ta question"
    >
      <div
        style={{
          padding: '14px 18px 12px',
          borderRadius: '18px 18px 18px 4px',
          background: 'linear-gradient(135deg, rgba(212,175,55,0.05) 0%, rgba(255,255,255,0.04) 100%)',
          border: '1px solid rgba(212,175,55,0.18)',
          display: 'flex',
          flexDirection: 'column',
          gap: 8,
          maxWidth: 340,
          minWidth: 240,
        }}
      >
        {/* Ligne 1 : 3 points dorés animés + label discret */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div className="stb-dots" aria-hidden="true">
            <span /><span /><span />
          </div>
          <span
            style={{
              fontFamily: 'Cinzel, serif',
              fontSize: 9,
              letterSpacing: '0.28em',
              color: 'rgba(212,175,55,0.65)',
              textTransform: 'uppercase',
            }}
          >
            Soléna réfléchit
          </span>
        </div>

        {/* Ligne 2 : message rotatif poétique */}
        <p
          key={step.at}
          className="stb-message"
          style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontStyle: 'italic',
            fontSize: 14,
            lineHeight: 1.45,
            color: 'rgba(245,238,224,0.82)',
            margin: 0,
          }}
        >
          {step.text}
        </p>

        {/* Ligne 3 : barre de souffle très fine */}
        <div
          style={{
            marginTop: 4,
            height: 2,
            borderRadius: 2,
            background: 'rgba(212,175,55,0.08)',
            overflow: 'hidden',
          }}
          aria-hidden="true"
        >
          <div
            style={{
              width: `${progress}%`,
              height: '100%',
              background:
                'linear-gradient(90deg, rgba(212,175,55,0.35) 0%, #D4AF37 60%, rgba(212,175,55,0.35) 100%)',
              transition: 'width 900ms cubic-bezier(0.22, 1, 0.36, 1)',
              boxShadow: '0 0 8px rgba(212,175,55,0.5)',
            }}
          />
        </div>
      </div>

      <style>{`
        .stb-dots {
          display: inline-flex;
          gap: 4px;
          align-items: center;
        }
        .stb-dots span {
          width: 5px;
          height: 5px;
          border-radius: 50%;
          background: #D4AF37;
          box-shadow: 0 0 6px rgba(212,175,55,0.55);
          animation: stb-blink 1.4s ease-in-out infinite;
        }
        .stb-dots span:nth-child(2) { animation-delay: 0.2s; }
        .stb-dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes stb-blink {
          0%, 80%, 100% { transform: scale(0.7); opacity: 0.35; }
          40%           { transform: scale(1.15); opacity: 1;    }
        }
        .stb-message {
          animation: stb-fade-in 500ms ease-out;
        }
        @keyframes stb-fade-in {
          from { opacity: 0; transform: translateY(3px); }
          to   { opacity: 1; transform: translateY(0);  }
        }
      `}</style>
    </div>
  );
};

export default SolenaThinkingBubble;
