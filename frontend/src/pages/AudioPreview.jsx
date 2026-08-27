/**
 * AudioPreview — page test pour écouter et comparer les 3 nappes ambient.
 * URL : /experience/audio-preview  (noindex, non liée publiquement)
 *
 * Interaction : cliquer sur "ÉCOUTER" démarre la nappe correspondante.
 * Un slider volume contrôle le master. Un seul preset joue à la fois.
 * Fade-in 3s à l'ouverture, fade-out 1,4s à l'arrêt (aucun click).
 */
import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { createAmbientDrone, AMBIENT_PRESETS } from '@/experience/ambientDrone';

export default function AudioPreview() {
  const [active, setActive] = useState(null); // preset key currently playing
  const [volume, setVolume] = useState(0.7);
  const [tick, setTick] = useState(0); // counter for elapsed seconds
  const droneRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => () => {
    // Cleanup au démontage
    if (droneRef.current) { droneRef.current.stop(); droneRef.current = null; }
    if (timerRef.current) { clearInterval(timerRef.current); }
  }, []);

  const play = async (key) => {
    // Stop precedent
    if (droneRef.current) {
      droneRef.current.stop();
      droneRef.current = null;
      if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    }
    setActive(key);
    setTick(0);
    const d = createAmbientDrone(key);
    if (!d) { setActive(null); return; }
    droneRef.current = d;
    d.setVolume(volume);
    await d.start();
    timerRef.current = setInterval(() => setTick((t) => t + 1), 1000);
  };

  const stop = () => {
    if (droneRef.current) { droneRef.current.stop(); droneRef.current = null; }
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    setActive(null);
    setTick(0);
  };

  const onVolume = (v) => {
    setVolume(v);
    if (droneRef.current) droneRef.current.setVolume(v);
  };

  return (
    <>
      <meta name="robots" content="noindex, nofollow" />
      <div style={pageStyle} data-testid="audio-preview-page">
        <div style={{ maxWidth: 720, margin: '0 auto' }}>
          <p style={eyebrow}>DÉMO — MUSIQUE AMBIENT · À VALIDER</p>
          <h1 style={title}>Trois nappes pour votre expérience.</h1>
          <p style={lead}>
            Choisissez celle qui incarne le mieux <em>Plume Astrale</em>.
            Je déploierai celle que vous préférez sur les 4 scènes de <code>/experience</code>,
            avec un bouton toggle discret dans la topbar.
          </p>

          <div style={{ margin: '32px 0 24px' }}>
            <label style={{ display: 'block', ...eyebrow, marginBottom: 10 }}>
              VOLUME · {Math.round(volume * 100)}%
            </label>
            <input
              type="range" min="0" max="1" step="0.01"
              value={volume}
              onChange={(e) => onVolume(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: '#D8B76A' }}
              data-testid="audio-preview-volume"
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {AMBIENT_PRESETS.map((p) => {
              const isActive = active === p.key;
              return (
                <div key={p.key} style={{ ...cardStyle, borderColor: isActive ? 'rgba(216,183,106,0.7)' : 'rgba(216,183,106,0.2)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 20 }}>
                    <div style={{ flex: 1 }}>
                      <h3 style={cardTitle}>
                        <span style={{ color: '#D8B76A', marginRight: 10 }}>✦</span>
                        {p.name}
                      </h3>
                      <p style={subtitleStyle}>{p.subtitle}</p>
                      <p style={descStyle}>{p.description}</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => (isActive ? stop() : play(p.key))}
                      style={{ ...ctaStyle, ...(isActive ? ctaActiveStyle : {}) }}
                      data-testid={`audio-preview-toggle-${p.key}`}
                    >
                      {isActive ? '■ ARRÊTER' : '▶ ÉCOUTER'}
                    </button>
                  </div>
                  {isActive && (
                    <p style={playingStyle} data-testid={`audio-preview-playing-${p.key}`}>
                      ● En lecture · {tick}s écoulées · fade-in progressif sur les 3 premières secondes
                    </p>
                  )}
                </div>
              );
            })}
          </div>

          <div style={{ marginTop: 40, padding: 20, background: 'rgba(216,183,106,0.05)', border: '1px solid rgba(216,183,106,0.15)', borderRadius: 3 }}>
            <p style={{ ...eyebrow, marginBottom: 8 }}>NOTES TECHNIQUES</p>
            <ul style={notesStyle}>
              <li>Aucun fichier audio téléchargé — tout est généré procéduralement (Web Audio API).</li>
              <li>Poids réseau : 0 KB. Compatibilité : tous navigateurs modernes.</li>
              <li>La lecture démarre uniquement sur clic utilisateur (respect des politiques autoplay).</li>
              <li>Sur les 4 scènes de /experience, la nappe évoluera légèrement selon la scène active (filtre + volume).</li>
              <li>Un bouton toggle discret sera placé dans la topbar (sound on/off), persistant en sessionStorage.</li>
            </ul>
          </div>

          <div style={{ marginTop: 32, textAlign: 'center' }}>
            <Link to="/experience" style={backLink} data-testid="audio-preview-back">
              ← Revenir à /experience
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}

const pageStyle = {
  minHeight: '100vh',
  background: 'radial-gradient(ellipse at 50% 30%, #17102E, #070713)',
  color: '#F4EFE6',
  fontFamily: '"Cormorant Garamond", Georgia, serif',
  padding: '80px 24px 60px',
};
const eyebrow = {
  fontFamily: '"Inter", sans-serif', fontSize: 11, letterSpacing: '0.32em',
  color: 'rgba(216, 183, 106, 0.75)', textTransform: 'uppercase',
  margin: 0,
};
const title = {
  fontFamily: '"Cormorant Garamond", serif', fontWeight: 400,
  fontSize: 'clamp(36px, 5.5vw, 60px)', lineHeight: 1.1,
  margin: '16px 0 20px',
};
const lead = {
  fontStyle: 'italic', fontSize: 18,
  color: 'rgba(244, 239, 230, 0.7)', lineHeight: 1.65,
  margin: 0,
};
const cardStyle = {
  padding: '22px 24px',
  background: 'rgba(23, 16, 46, 0.5)',
  border: '1px solid rgba(216, 183, 106, 0.2)',
  borderRadius: 3,
  transition: 'border-color 400ms ease',
};
const cardTitle = {
  fontFamily: '"Cormorant Garamond", serif', fontWeight: 500,
  fontSize: 26, margin: '0 0 8px',
};
const subtitleStyle = {
  fontFamily: '"Inter", sans-serif', fontSize: 11.5,
  letterSpacing: '0.18em', textTransform: 'uppercase',
  color: 'rgba(216, 183, 106, 0.7)',
  margin: '0 0 12px',
};
const descStyle = {
  fontStyle: 'italic', fontSize: 15,
  color: 'rgba(244, 239, 230, 0.65)', lineHeight: 1.55,
  margin: 0,
};
const ctaStyle = {
  display: 'inline-flex', alignItems: 'center',
  padding: '12px 22px', background: 'transparent', color: '#F4EFE6',
  fontFamily: '"Inter", sans-serif', fontSize: 11, fontWeight: 400,
  letterSpacing: '0.24em', textTransform: 'uppercase',
  border: '1px solid rgba(216, 183, 106, 0.5)', borderRadius: 2,
  cursor: 'pointer', minWidth: 130, justifyContent: 'center',
  transition: 'background 300ms ease, color 300ms ease',
  whiteSpace: 'nowrap',
};
const ctaActiveStyle = {
  background: 'rgba(216, 183, 106, 0.9)',
  color: '#0B0B14',
  borderColor: 'rgba(216, 183, 106, 0.95)',
};
const playingStyle = {
  fontFamily: '"Inter", sans-serif', fontSize: 12,
  letterSpacing: '0.12em',
  color: 'rgba(216, 183, 106, 0.75)',
  margin: '14px 0 0',
};
const notesStyle = {
  fontFamily: '"Inter", sans-serif', fontSize: 13,
  color: 'rgba(244, 239, 230, 0.6)',
  lineHeight: 1.7,
  paddingLeft: 20, margin: 0,
};
const backLink = {
  fontFamily: '"Inter", sans-serif', fontSize: 12,
  letterSpacing: '0.24em', textTransform: 'uppercase',
  color: 'rgba(216, 183, 106, 0.7)',
  textDecoration: 'none',
};
