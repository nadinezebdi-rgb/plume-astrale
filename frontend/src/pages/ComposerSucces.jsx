/* eslint-disable react/no-unescaped-entities */
/**
 * ComposerSucces.jsx — Scène cinématographique d'attente pendant la génération du livre.
 *
 * Design (LOT 4.3) :
 *  - Une plume dorée qui trace lentement une roue céleste SVG (SMIL animate ~8 min).
 *  - Les 12 chapitres du socle apparaissent un à un, glyphes zodiacaux dorés,
 *    au rythme du polling `/api/composer/status/{session_id}`.
 *  - Un cartouche discret "8 minutes environ", un compteur MM:SS.
 *  - Le tout dans la palette bronze / ivoire du livre, ambiance nuit étoilée sobre.
 */
import React, { useEffect, useMemo, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL || '';

// Les 12 chapitres du socle — libellés courts pour l'affichage
const CHAPTERS_SOCLE = [
  { rn: 'I',    title: 'Votre ciel de naissance' },
  { rn: 'II',   title: 'Les grandes lignes de vous' },
  { rn: 'III',  title: 'Votre trio identitaire' },
  { rn: 'IV',   title: "Votre façon d'aimer" },
  { rn: 'V',    title: "Vos façons d'entrer en relation" },
  { rn: 'VI',   title: 'Vos forces naturelles' },
  { rn: 'VII',  title: 'Vos passages étroits' },
  { rn: 'VIII', title: 'Votre travail dans le monde' },
  { rn: 'IX',   title: 'Vos grandes dynamiques de vie' },
  { rn: 'X',    title: 'Le temps qui vous traverse' },
  { rn: 'XI',   title: 'Votre chemin personnel' },
  { rn: 'XII',  title: 'Portrait astral' },
];

// Génération estimée : ~40s par chapitre, gestion 3 concurrents ≈ 8 minutes
const EST_TOTAL_SECONDS = 8 * 60;

export default function ComposerSucces() {
  const [sp] = useSearchParams();
  const sessionId = sp.get('session_id');
  const [pdfReady, setPdfReady] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [error, setError] = useState(null);
  const [elapsed, setElapsed] = useState(0);

  // Poll status ─────────────────────────────────────────────────────
  useEffect(() => {
    if (!sessionId) return;
    let cancelled = false;
    let timer;
    async function poll() {
      try {
        const r = await fetch(`${API}/api/composer/status/${sessionId}`);
        if (r.ok && !cancelled) {
          const data = await r.json();
          if (data.pdf_ready) {
            setPdfReady(true);
            setPdfUrl(data.pdf_url || null);
            return;
          }
        }
      } catch {
        if (!cancelled) setError("Connexion instable — nous continuons à composer votre livre en arrière-plan.");
      }
      if (!cancelled) timer = setTimeout(poll, 8000);
    }
    poll();
    return () => { cancelled = true; clearTimeout(timer); };
  }, [sessionId]);

  // Timer élégant (compteur MM:SS) ──────────────────────────────────
  useEffect(() => {
    if (pdfReady) return;
    const t = setInterval(() => setElapsed((e) => e + 1), 1000);
    return () => clearInterval(t);
  }, [pdfReady]);

  // Progression estimée des 12 chapitres — s'aligne sur elapsed ─────
  const unlockedCount = useMemo(() => {
    if (pdfReady) return 12;
    // 40s par chapitre en moyenne
    return Math.min(12, Math.floor(elapsed / 40));
  }, [elapsed, pdfReady]);

  const mmss = `${String(Math.floor(elapsed / 60)).padStart(2, '0')}:${String(elapsed % 60).padStart(2, '0')}`;
  const progress = pdfReady ? 100 : Math.min(98, Math.round((elapsed / EST_TOTAL_SECONDS) * 100));

  return (
    <PsPageShell background="dark">
      <SEO
        path="/composer/succes"
        title="Merci · Votre livre est en composition"
        description="Merci pour votre commande. Nous composons votre livre astral personnalisé — vous le recevrez dans quelques minutes."
        noindex
      />
      <div data-testid="composer-succes" style={styles.wrap}>
        <p style={styles.eyebrow}>MERCI</p>
        <h1 style={styles.h1}>
          {pdfReady
            ? 'Votre livre est prêt.'
            : "Votre livre est en train de s'écrire."}
        </h1>

        {!pdfReady && (
          <p style={styles.subtitle}>
            Comptez huit minutes environ. Vous pouvez fermer cette page :
            nous vous prévenons par email dès qu'il est prêt.
          </p>
        )}

        {/* SCÈNE : plume qui trace la roue céleste ─────────────── */}
        <div style={styles.scene} data-testid="cinematic-scene">
          <FeatherTracingWheel active={!pdfReady} progress={progress} />
        </div>

        {/* Timer + compteur chapitres ──────────────────────────── */}
        <div style={styles.progressRow}>
          <div style={styles.timerBox}>
            <span style={styles.timerLabel}>ÉCOULÉ</span>
            <span style={styles.timerValue} data-testid="elapsed-timer">{mmss}</span>
          </div>
          <div style={styles.chapterCounter} data-testid="chapter-counter">
            <span style={styles.timerLabel}>CHAPITRES</span>
            <span style={styles.timerValue}>{unlockedCount} <span style={styles.divider}>/</span> 12</span>
          </div>
        </div>

        {/* Liste des 12 chapitres — se déverrouillent un à un ────── */}
        <ol style={styles.chapters}>
          {CHAPTERS_SOCLE.map((c, i) => (
            <li
              key={c.rn}
              data-testid={`chapter-${c.rn}`}
              style={{
                ...styles.chapterItem,
                opacity: i < unlockedCount ? 1 : 0.32,
                borderColor: i < unlockedCount ? 'rgba(168,130,63,0.55)' : 'rgba(168,130,63,0.15)',
                transition: 'opacity 0.6s ease, border-color 0.6s ease',
              }}
            >
              <span style={{
                ...styles.chapterRn,
                color: i < unlockedCount ? '#C9AE7C' : 'rgba(201,174,124,0.35)',
              }}>{c.rn}</span>
              <span style={styles.chapterTitle}>{c.title}</span>
              {i < unlockedCount && <span style={styles.chapterDot}>·</span>}
            </li>
          ))}
        </ol>

        {/* CTA final ─────────────────────────────────────────── */}
        {pdfReady && (
          <div style={{ marginTop: 40, textAlign: 'center' }} data-testid="pdf-ready-cta">
            <p style={styles.subtitle}>
              Il vient d'être envoyé à votre adresse. Vous pouvez aussi le télécharger ici :
            </p>
            {pdfUrl && (
              <a
                href={pdfUrl}
                target="_blank"
                rel="noreferrer"
                data-testid="download-pdf-link"
                style={styles.ctaPrimary}
              >
                Télécharger le livre
              </a>
            )}
          </div>
        )}

        {error && !pdfReady && <p style={styles.errorBox}>{error}</p>}

        <Link
          to="/"
          style={{ ...styles.ctaGhost, marginTop: 40, textDecoration: 'none', display: 'inline-block' }}
        >
          Retour à l'accueil
        </Link>
      </div>
    </PsPageShell>
  );
}


// ═══════════════════════════════════════════════════════════════════
// SCÈNE — plume dorée qui trace lentement une roue céleste
// ═══════════════════════════════════════════════════════════════════
function FeatherTracingWheel({ active, progress }) {
  // Rotation continue de la plume autour du cercle (~ progress %)
  // La plume trace un ARC dont la longueur suit `progress`.
  const R = 140;
  const CX = 160; const CY = 160;
  const CIRC = 2 * Math.PI * R;
  const dashOffset = CIRC * (1 - progress / 100);

  // Position de la plume à l'extrémité de l'arc
  const angle = (progress / 100) * 2 * Math.PI - Math.PI / 2;
  const featherX = CX + R * Math.cos(angle);
  const featherY = CY + R * Math.sin(angle);
  const featherRotation = (progress / 100) * 360 + 90;

  return (
    <svg viewBox="0 0 320 320" style={styles.wheelSvg} data-testid="wheel-svg">
      {/* Cercle extérieur (guide, très pâle) */}
      <circle cx={CX} cy={CY} r={R} fill="none" stroke="rgba(168,130,63,0.18)" strokeWidth="1" />
      {/* Cercle intérieur */}
      <circle cx={CX} cy={CY} r={R * 0.62} fill="none" stroke="rgba(168,130,63,0.14)" strokeWidth="0.5" />
      {/* 12 divisions zodiacales (pâles) */}
      {Array.from({ length: 12 }).map((_, i) => {
        const a = (i / 12) * 2 * Math.PI - Math.PI / 2;
        const x1 = CX + R * 0.62 * Math.cos(a);
        const y1 = CY + R * 0.62 * Math.sin(a);
        const x2 = CX + R * Math.cos(a);
        const y2 = CY + R * Math.sin(a);
        return (
          <line
            key={i}
            x1={x1} y1={y1} x2={x2} y2={y2}
            stroke="rgba(168,130,63,0.18)" strokeWidth="0.5"
          />
        );
      })}
      {/* Arc doré qui se trace au rythme du progress */}
      <circle
        cx={CX} cy={CY} r={R} fill="none"
        stroke="#C9AE7C" strokeWidth="1.4" strokeLinecap="round"
        strokeDasharray={CIRC}
        strokeDashoffset={dashOffset}
        transform={`rotate(-90 ${CX} ${CY})`}
        style={{ transition: 'stroke-dashoffset 1.2s ease-out' }}
      />
      {/* 12 glyphes zodiacaux (bronze) qui s'illuminent progressivement */}
      {['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓'].map((glyph, i) => {
        const a = ((i + 0.5) / 12) * 2 * Math.PI - Math.PI / 2;
        const gx = CX + (R + 14) * Math.cos(a);
        const gy = CY + (R + 14) * Math.sin(a) + 4;
        const lit = (i / 12) * 100 <= progress;
        return (
          <text
            key={i} x={gx} y={gy}
            fontSize="12" textAnchor="middle"
            fill={lit ? '#C9AE7C' : 'rgba(168,130,63,0.22)'}
            style={{ transition: 'fill 0.6s ease' }}
            fontFamily="'Astro', 'DejaVu Sans', serif"
          >{glyph}</text>
        );
      })}
      {/* La plume dorée (silhouette pleine, calamus + palme) */}
      <g
        transform={`translate(${featherX} ${featherY}) rotate(${featherRotation})`}
        style={{ transition: 'transform 1.2s ease-out' }}
      >
        <path
          d="M 0,-18 C 5,-14 8,-4 4,10 L 3,16 L -3,16 L -4,10 C -8,-4 -5,-14 0,-18 Z
             M 0,-14 L 0,10"
          fill="#C9AE7C"
          fillRule="evenodd"
          stroke="#A8823F"
          strokeWidth="0.4"
          filter="drop-shadow(0 0 6px rgba(212,175,55,0.5))"
        />
      </g>
      {/* Point central étoile */}
      <circle cx={CX} cy={CY} r="2.2" fill="#C9AE7C" opacity={active ? 1 : 0.7}>
        {active && (
          <animate attributeName="opacity" values="0.6;1;0.6" dur="3s" repeatCount="indefinite" />
        )}
      </circle>
    </svg>
  );
}


// ═══════════════════════════════════════════════════════════════════
// Styles — palette bronze/ivoire du livre, sobre et éditorial
// ═══════════════════════════════════════════════════════════════════
const styles = {
  wrap: {
    maxWidth: 780, margin: '0 auto', padding: '60px 24px 100px',
    color: '#F5EEE0', fontFamily: '"Cormorant Garamond", "Lora", serif',
    textAlign: 'center', lineHeight: 1.65,
  },
  eyebrow: {
    fontFamily: '"Cinzel", serif',
    fontSize: '0.72rem', letterSpacing: 4, color: '#C9AE7C', margin: 0,
  },
  h1: {
    fontFamily: '"Cormorant Garamond", "Playfair Display", serif',
    fontSize: 'clamp(2rem, 4.6vw, 2.8rem)',
    color: '#F5EEE0', margin: '14px 0 18px',
    fontWeight: 300, lineHeight: 1.2,
  },
  subtitle: {
    fontSize: '1.05rem', color: 'rgba(245,238,224,0.82)',
    margin: '0 auto', maxWidth: 540, fontStyle: 'italic',
  },
  scene: {
    margin: '48px auto 32px', width: 'min(360px, 92vw)',
    aspectRatio: '1 / 1', position: 'relative',
  },
  wheelSvg: { width: '100%', height: '100%', display: 'block' },
  progressRow: {
    display: 'flex', gap: 36, justifyContent: 'center',
    marginTop: 24, marginBottom: 32,
  },
  timerBox: {
    display: 'flex', flexDirection: 'column', gap: 4, alignItems: 'center',
  },
  chapterCounter: {
    display: 'flex', flexDirection: 'column', gap: 4, alignItems: 'center',
  },
  timerLabel: {
    fontFamily: '"Cinzel", serif',
    fontSize: '0.62rem', letterSpacing: 3, color: 'rgba(201,174,124,0.75)',
  },
  timerValue: {
    fontFamily: '"Cormorant Garamond", serif',
    fontSize: '1.6rem', color: '#F5EEE0', fontVariantNumeric: 'tabular-nums',
  },
  divider: { color: 'rgba(201,174,124,0.6)', fontStyle: 'italic', margin: '0 6px' },
  chapters: {
    listStyle: 'none', padding: 0, margin: '30px auto 0',
    maxWidth: 560, display: 'grid', gap: 8, textAlign: 'left',
  },
  chapterItem: {
    display: 'grid',
    gridTemplateColumns: '48px 1fr 20px',
    gap: 12, alignItems: 'baseline',
    padding: '11px 16px',
    background: 'rgba(15,26,60,0.4)',
    border: '1px solid',
    borderRadius: 2,
  },
  chapterRn: {
    fontFamily: '"Cinzel", serif',
    fontSize: '0.78rem', letterSpacing: 2, textAlign: 'right',
  },
  chapterTitle: {
    fontFamily: '"Cormorant Garamond", serif',
    fontSize: '1.05rem', fontStyle: 'italic', color: '#F5EEE0',
  },
  chapterDot: {
    color: '#C9AE7C', textAlign: 'right', fontSize: '1.4rem', lineHeight: 1,
  },
  errorBox: {
    padding: '14px 16px', background: 'rgba(232,144,107,0.10)',
    border: '1px solid rgba(232,144,107,0.35)', borderRadius: 4,
    color: '#F5EEE0', marginTop: 24, maxWidth: 520, marginLeft: 'auto', marginRight: 'auto',
  },
  ctaPrimary: {
    display: 'inline-block', padding: '14px 32px',
    background: '#C9AE7C', color: '#0F1A3C',
    fontFamily: '"Cinzel", serif', fontSize: '0.85rem',
    letterSpacing: 2.4, textDecoration: 'none', borderRadius: 2,
    marginTop: 12,
  },
  ctaGhost: {
    display: 'inline-block', padding: '12px 22px', background: 'transparent',
    color: '#F5EEE0', border: '1px solid rgba(201,174,124,0.35)', borderRadius: 2,
    fontFamily: '"Cinzel", serif', fontSize: '0.78rem', letterSpacing: 2.4,
  },
};
