/**
 * ExperienceRoot — orchestrateur du prototype /experience
 * ─────────────────────────────────────────────────────────────
 * • Détecte les capacités device (reducedMotion, mobile, low-end, WebGL)
 * • Route le rendu :
 *     - Fallback statique si prefers-reduced-motion OU WebGL absent
 *     - Sinon : canvas 3D + overlay UI scrollable (4 sections × 100vh)
 * • Écoute le scroll pour mettre à jour globalProgress et currentScene
 * • Gère les CTA / choix qui pilotent le store et déclenchent des scrolls
 */
import React, { useEffect, useLayoutEffect, useMemo, useRef, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDeviceProfile } from './hooks/useDeviceProfile';
import { useExperienceStore } from './useExperienceStore';
import ExperienceCanvas from './ExperienceCanvas';
import ExperienceFallback from './ExperienceFallback';
import { getCardBackTexture, getCardFaceTexture } from './scenes/cardTextures';
import { storeIntent, storeDrawnCard, captureUtm, detectZodiacCampaign, readUtm } from './intentConfig';
import ZodiacInterlude from './ZodiacInterlude';
import { event as trackEvent, EVENTS } from '@/lib/analytics';
import './Experience.css';

const INTENTS = [
  { id: 'relationship',       glyph: '♡', label: 'Une relation me questionne' },
  { id: 'clarity',            glyph: '☾', label: "J'ai besoin d'y voir plus clair" },
  { id: 'self_discovery',     glyph: '✦', label: 'Je veux mieux me comprendre' },
  { id: 'specific_question',  glyph: '◇', label: "J'ai une question précise" },
];

const CARDS = [
  { id: 'heart',  glyph: '♡', name: 'La Rencontre',  tagline: 'Ce qui vous relie',   rot: -6, dy: 0 },
  { id: 'moon',   glyph: '☾', name: 'Le Voile',      tagline: 'Ce qui se dévoile',   rot:  0, dy: -8 },
  { id: 'star',   glyph: '✦', name: 'La Trajectoire', tagline: 'Ce qui vous porte',  rot:  6, dy: 0 },
];

export default function ExperienceRoot() {
  useDeviceProfile();
  const rootRef = useRef(null);
  const navigate = useNavigate();

  // Store
  const setGlobalProgress = useExperienceStore((s) => s.setGlobalProgress);
  const setScene = useExperienceStore((s) => s.setScene);
  const setIntent = useExperienceStore((s) => s.setIntent);
  const setDrawnCard = useExperienceStore((s) => s.setDrawnCard);
  const setHoveredIntent = useExperienceStore((s) => s.setHoveredIntent);
  const intent = useExperienceStore((s) => s.intent);
  const drawnCard = useExperienceStore((s) => s.drawnCard);
  const currentScene = useExperienceStore((s) => s.currentScene);
  const reducedMotion = useExperienceStore((s) => s.reducedMotion);
  const webglAvailable = useExperienceStore((s) => s.webglAvailable);

  // UI local
  const [hoveringIntent, setHoveringIntent] = useState(false);
  const [hoveringCard, setHoveringCard] = useState(false);
  const [scene2Step, setScene2Step] = useState(0); // 0=phrase1, 1=phrase2+choices, 2=chosen
  const [scene4Step, setScene4Step] = useState(0); // 0=silence, 1=writing, 2=phrase1, 3=phrase2, 4=cta
  const [zodiacVisible, setZodiacVisible] = useState(false);
  const sectionRefs = useRef({ 1: null, 2: null, 3: null, 4: null });

  // Fallback pour reduced-motion ou pas de WebGL
  const useFallback = reducedMotion || !webglAvailable;

  // ── Scroll → globalProgress & currentScene ─────────────────
  useEffect(() => {
    if (useFallback) return;
    const onScroll = () => {
      const root = rootRef.current;
      if (!root) return;
      const total = root.scrollHeight - window.innerHeight;
      const progress = Math.max(0, Math.min(1, window.scrollY / total));
      setGlobalProgress(progress);

      const scene =
        progress < 0.25 ? 1 :
        progress < 0.50 ? 2 :
        progress < 0.75 ? 3 :
        4;
      setScene(scene);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, [setGlobalProgress, setScene, useFallback]);

  // ── Scène 2 : timing des phrases ─────────────────────────────
  useEffect(() => {
    if (currentScene !== 2) return;
    setScene2Step(0);
    const t1 = setTimeout(() => setScene2Step(1), 3000);
    return () => clearTimeout(t1);
  }, [currentScene]);

  // ── Scène 4 : timing des phrases (aligné sur les phases de Scene04Feather V2) ─
  //  Phase A CHAOS       [0.0, 0.8]      chaos
  //  Phase B ATTRACTION  [0.8, 1.6]      attraction subtile
  //  Phase C FORMATION   [1.6, 6.0]      plume se dessine
  //  Phase D PAUSE       [6.0, 8.0]      silence visuel — plume complète
  //  Phase E WRITING     [8.0, 12.0]     plume écrit "Plume Astrale" gauche→droite
  //  Phase F STABLE      [12.0, ∞)       texte stable + sweep + phrases HTML
  useEffect(() => {
    if (currentScene !== 4) return;
    setScene4Step(0);
    const t1 = setTimeout(() => setScene4Step(1), 12500); // "Plume Astrale" vient d'être écrit
    const t2 = setTimeout(() => setScene4Step(2), 14000); // "Votre histoire est unique"
    const t3 = setTimeout(() => setScene4Step(3), 16000); // "Votre ciel aussi"
    const t4 = setTimeout(() => {
      setScene4Step(4);
      trackEvent(EVENTS.EXP_FEATHER_COMPLETED, {});
      trackEvent(EVENTS.EXP_SIGNUP_CTA_VIEWED, { intent_type: intent || 'none' });
    }, 18000); // CTA final
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); clearTimeout(t4); };
  }, [currentScene, intent]);

  // ── Smooth scroll helper ─────────────────────────────────────
  const scrollToScene = useCallback((n) => {
    const el = sectionRefs.current[n];
    if (!el) return;
    el.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'start' });
  }, [reducedMotion]);

  // ── Textures des cartes (générées une fois) ─────────────────
  const cardBackImage = useMemo(() => getCardBackTexture(), []);
  const cardFaceImage = useMemo(() => getCardFaceTexture(), []);

  // ── Capture UTM + démarrage funnel (une seule fois) ─────────
  useEffect(() => {
    trackEvent(EVENTS.EXP_STARTED, {});
  }, []);

  // ── Tracking par scène ──────────────────────────────────────
  useEffect(() => {
    if (currentScene === 2) trackEvent(EVENTS.EXP_SCENE2_VIEWED, {});
    if (currentScene === 3) trackEvent(EVENTS.EXP_TAROT_STARTED, {});
    if (currentScene === 4) trackEvent(EVENTS.EXP_FEATHER_STARTED, {});
  }, [currentScene]);

  // ── Détection campagne horoscope (court-circuit) ────────────
  //  IMPORTANT : captureUtm() doit être exécuté AVANT detectZodiacCampaign()
  //  car ce dernier lit sessionStorage. On les enchaîne dans le useMemo pour
  //  garantir l'ordre lors du render initial (les useEffect s'exécuteraient
  //  trop tard et le shortcut serait mémoïsé à null).
  const zodiac = useMemo(() => {
    captureUtm();
    return detectZodiacCampaign();
  }, []);

  // ── Handlers ─────────────────────────────────────────────────
  const handleIntentChoice = useCallback((intentId) => {
    setIntent(intentId);
    storeIntent(intentId);
    trackEvent(EVENTS.EXP_INTENT_SELECTED, { intent_type: intentId });
    setScene2Step(2);
    // Ouvre l'interlude Zodiac. Le passage à la scène 3 se fera après
    // completion / skip du signe.
    setTimeout(() => setZodiacVisible(true), 700);
  }, [setIntent]);

  const handleZodiacComplete = useCallback((sign) => {
    setZodiacVisible(false);
    if (sign) trackEvent('zodiac_confirmed', { zodiac: sign.key });
    setTimeout(() => scrollToScene(3), 350);
  }, [scrollToScene]);

  const handleZodiacSkip = useCallback(() => {
    setZodiacVisible(false);
    setTimeout(() => scrollToScene(3), 200);
  }, [scrollToScene]);

  const handleCardDraw = useCallback((cardId) => {
    if (drawnCard) return;
    setDrawnCard(cardId);
    storeDrawnCard(cardId);
    trackEvent(EVENTS.EXP_TAROT_SELECTED, { card: cardId });
    // Après ~1.2s la carte est retournée → track reveal
    setTimeout(() => trackEvent(EVENTS.EXP_TAROT_REVEALED, { card: cardId }), 1200);
  }, [setDrawnCard, drawnCard]);

  const handleFinalCTA = useCallback(() => {
    trackEvent(EVENTS.EXP_SIGNUP_CTA_CLICKED, { intent_type: intent || 'none', card: drawnCard || 'none' });
    // Construit un lien /inscription enrichi (intent + card + utm) pour survivre à sessionStorage
    const utm = readUtm();
    const params = new URLSearchParams();
    if (intent) params.set('intent', intent);
    if (drawnCard) params.set('exp_card', drawnCard);
    // Passe utm_* / source / campaign
    Object.entries(utm).forEach(([k, v]) => { if (v) params.set(k, v); });
    params.set('welcome', '1'); // AuthenticatedHome le lira post-inscription
    navigate(`/inscription?${params.toString()}`);
  }, [navigate, intent, drawnCard]);

  const handleSkip = useCallback(() => {
    trackEvent(EVENTS.EXP_SKIPPED, { at_scene: currentScene });
    navigate('/');
  }, [navigate, currentScene]);

  // ── Fallback (pas d'animation lourde) ─────────────────────────
  if (useFallback) {
    return (
      <ExperienceFallback
        intents={INTENTS}
        cards={CARDS}
        onIntentChoice={handleIntentChoice}
        onCardDraw={handleCardDraw}
        onFinalCTA={handleFinalCTA}
        intent={intent}
        drawnCard={drawnCard}
      />
    );
  }

  // ── Rendu normal ─────────────────────────────────────────────
  return (
    <div
      className="exp-root"
      ref={rootRef}
      data-testid="experience-root"
    >
      {/* Topbar fixe */}
      <header className="exp-topbar" data-testid="experience-topbar">
        <span className="exp-topbar__logo">PLUME <em style={{ fontStyle: 'italic', letterSpacing: '0.05em' }}>Astrale</em></span>
        <div style={{ display: 'flex', gap: 24, alignItems: 'center', pointerEvents: 'auto' }}>
          {zodiac && (
            <a
              href={`/horoscope/${zodiac}`}
              className="exp-topbar__exit"
              data-testid="experience-zodiac-shortcut"
              style={{ color: '#D8B76A' }}
            >
              → Horoscope {zodiac.charAt(0).toUpperCase() + zodiac.slice(1)}
            </a>
          )}
          <button
            type="button"
            className="exp-topbar__exit"
            onClick={handleSkip}
            data-testid="experience-skip"
          >
            Passer l&apos;expérience →
          </button>
        </div>
      </header>

      <ExperienceCanvas />

      {/* Indicateur discret de scène */}
      <div className="exp-scene-indicator" aria-live="polite">
        {currentScene} · {['ENTRÉE', 'INTENTION', 'TAROT', 'PLUME'][currentScene - 1]}
      </div>

      <div className="exp-ui-layer">
        {/* ─── Scène 01 ───────────────────────────────────── */}
        <section
          ref={(el) => (sectionRefs.current[1] = el)}
          className="exp-section exp-s1"
          data-testid="experience-scene-1"
        >
          <div className="exp-section-inner">
            <div className="exp-s1__stack">
              <div className="exp-s1__brand-wrap">
                <p className="exp-eyebrow exp-s1__brand">PLUME <em style={{ fontStyle: 'italic', letterSpacing: '0.06em', color: 'var(--exp-gold)' }}>Astrale</em></p>
                <p className="exp-h2 exp-s1__phrase-1">
                  Certaines réponses ne se cherchent pas.
                </p>
                <p className="exp-h1 exp-s1__phrase-2">
                  Elles <em>se révèlent.</em>
                </p>
              </div>

              <div className="exp-s1__cta">
                <button
                  type="button"
                  className="exp-btn"
                  onClick={() => scrollToScene(2)}
                  data-testid="scene-1-cta"
                >
                  <span className="exp-btn__glyph">✦</span>
                  Entrer dans mon univers
                </button>
              </div>
            </div>

            <div className="exp-scroll-hint" aria-hidden="true">
              <span className="exp-eyebrow">↓ Faites défiler pour commencer</span>
              <div className="exp-scroll-hint__line" />
            </div>
          </div>
        </section>

        {/* ─── Scène 02 ───────────────────────────────────── */}
        <section
          ref={(el) => (sectionRefs.current[2] = el)}
          className="exp-section"
          data-testid="experience-scene-2"
        >
          <div className="exp-section-inner">
            <div className="exp-s2__intro">
              <p
                className="exp-lead exp-s2__phrase"
                data-visible={scene2Step === 0}
              >
                Vous n&apos;êtes peut-être pas arrivé ici par hasard.
              </p>
              <p
                className="exp-h2 exp-s2__phrase"
                data-visible={scene2Step >= 1}
              >
                Qu&apos;est-ce qui vous amène aujourd&apos;hui&nbsp;?
              </p>
            </div>

            <div
              className="exp-s2__grid"
              data-hovering={hoveringIntent ? 'true' : 'false'}
              data-testid="scene-2-grid"
              style={{ opacity: scene2Step >= 1 ? 1 : 0, transition: 'opacity 1.4s ease' }}
            >
              {INTENTS.map((it) => (
                <button
                  key={it.id}
                  type="button"
                  className="exp-s2__choice exp-gilded"
                  data-testid={`scene-2-choice-${it.id}`}
                  data-active={intent === it.id}
                  onMouseEnter={() => { setHoveringIntent(true); setHoveredIntent(it.id); }}
                  onMouseLeave={() => { setHoveringIntent(false); setHoveredIntent(null); }}
                  onFocus={() => setHoveredIntent(it.id)}
                  onBlur={() => setHoveredIntent(null)}
                  onClick={() => handleIntentChoice(it.id)}
                >
                  <span className="exp-s2__choice-glyph">{it.glyph}</span>
                  <span className="exp-s2__choice-label">{it.label}</span>
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* ─── Scène 03 ───────────────────────────────────── */}
        <section
          ref={(el) => (sectionRefs.current[3] = el)}
          className="exp-section"
          data-testid="experience-scene-3"
        >
          <div className="exp-section-inner">
            <div className="exp-s3__intro">
              <p className="exp-lead">
                Il y a probablement une question à laquelle vous pensez en ce moment.
              </p>
              <p className="exp-eyebrow" style={{ opacity: 0.6 }}>
                Gardez-la quelques secondes en tête.
              </p>
            </div>

            <div
              className="exp-s3__cards"
              data-hovering={hoveringCard ? 'true' : 'false'}
              data-testid="scene-3-cards"
            >
              {CARDS.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  className="exp-s3__card"
                  data-testid={`scene-3-card-${c.id}`}
                  data-flipped={drawnCard === c.id}
                  data-featured={c.id === 'moon' ? 'true' : 'false'}
                  style={{ '--card-rot': `${c.rot}deg`, '--card-dy': `${c.dy}px` }}
                  disabled={drawnCard && drawnCard !== c.id}
                  onMouseEnter={() => setHoveringCard(true)}
                  onMouseLeave={() => setHoveringCard(false)}
                  onClick={() => handleCardDraw(c.id)}
                  aria-label={`Tirer la carte ${c.name}`}
                >
                  <div
                    className="exp-s3__back"
                    aria-hidden={drawnCard === c.id}
                    style={{ backgroundImage: `url(${cardBackImage})` }}
                  />
                  <div
                    className="exp-s3__face"
                    aria-hidden={drawnCard !== c.id}
                    style={{ backgroundImage: `url(${cardFaceImage})` }}
                  />
                </button>
              ))}
            </div>

            <div className="exp-s3__result" data-visible={drawnCard !== null}>
              <p className="exp-lead">Cette carte éclaire une partie de votre question.</p>
              <p className="exp-lead" style={{ opacity: 0.6, marginTop: -8 }}>
                Mais seule, elle ne raconte pas toute l&apos;histoire.
              </p>
              <button
                type="button"
                className="exp-linkline"
                onClick={() => {
                  trackEvent(EVENTS.EXP_TAROT_CONTINUE, { card: drawnCard });
                  scrollToScene(4);
                }}
                data-testid="scene-3-continue"
              >
                ✦ Découvrir la suite de mon tirage
                <span className="exp-linkline__chevron">↓</span>
              </button>
            </div>
          </div>
        </section>

        {/* ─── Scène 04 ───────────────────────────────────── */}        <section
          ref={(el) => (sectionRefs.current[4] = el)}
          className="exp-section"
          data-testid="experience-scene-4"
        >
          <div className="exp-section-inner exp-s4__stack">
            {/* Zone réservée au dessin particules (plume → "Plume Astrale") */}
            <div className="exp-s4__particle-space" aria-hidden="true" />

            <div className="exp-s4__phrases">
              <p className="exp-h2 exp-s4__phrase" data-visible={scene4Step >= 2}>
                Votre histoire est unique.
              </p>
              <p className="exp-h2 exp-s4__phrase" data-visible={scene4Step >= 3}>
                Votre ciel aussi.
              </p>
            </div>

            <div className="exp-s4__final-cta" data-visible={scene4Step >= 4}>
              <p className="exp-lead" style={{ marginBottom: 8 }}>Votre voyage ne fait que commencer.</p>
              <p style={{
                fontFamily: '"Inter", sans-serif', fontSize: 11, letterSpacing: '0.32em',
                textTransform: 'uppercase', color: 'var(--exp-gold)',
                margin: '0 0 8px', display: 'flex', alignItems: 'center', gap: 10,
              }}>
                <span style={{ fontSize: 18 }}>🎁</span> 20 crédits offerts
              </p>
              <p className="exp-lead" style={{ opacity: 0.55, marginBottom: 32 }}>
                pour découvrir Plume Astrale.
              </p>
              <button
                type="button"
                className="exp-btn"
                onClick={handleFinalCTA}
                data-testid="scene-4-cta"
              >
                <span className="exp-btn__glyph">✦</span>
                Commencer mon voyage
              </button>
              <button
                type="button"
                className="exp-linkline"
                onClick={() => {
                  trackEvent(EVENTS.EXP_SIGNUP_CTA_CLICKED, { intent_type: intent, card: drawnCard, mode: 'login' });
                  navigate('/connexion');
                }}
                data-testid="scene-4-cta-secondary"
              >
                Déjà membre ? Se connecter
                <span className="exp-linkline__chevron">→</span>
              </button>
            </div>
          </div>
        </section>
      </div>

      <ZodiacInterlude
        visible={zodiacVisible}
        onComplete={handleZodiacComplete}
        onSkip={handleZodiacSkip}
      />
    </div>
  );
}

// ── Layout effect : reset scroll top on mount ──
export function useResetScrollTop() {
  useLayoutEffect(() => { window.scrollTo(0, 0); }, []);
}
