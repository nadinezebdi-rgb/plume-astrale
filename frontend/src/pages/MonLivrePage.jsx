/* eslint-disable react/no-unescaped-entities */
/**
 * MonLivrePage.jsx — Lecteur flipbook du Livre Astral (LOT 4.4).
 *
 * - Rasterise chaque page via GET /api/composer/pages/{session_id}/{n}.jpg
 * - Navigation clavier : flèches gauche/droite, PageUp/Down, Home/End
 * - Preload +1/+2 pour un feuilletage fluide
 * - Son doux de feuille (WebAudio synth court — pas de fichier externe)
 * - Bouton téléchargement PDF
 *
 * URL : /mon-compte/mon-livre?session_id=…
 */
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function MonLivrePage() {
  const [sp] = useSearchParams();
  const sessionId = sp.get('session_id');
  const [totalPages, setTotalPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [turning, setTurning] = useState(false);
  const [error, setError] = useState(null);
  const audioCtxRef = useRef(null);

  // ── Fetch metadata (total pages, pdf url) ──
  useEffect(() => {
    if (!sessionId) return;
    let cancelled = false;
    (async () => {
      try {
        const r = await fetch(`${API}/api/composer/status/${sessionId}`);
        if (!r.ok) throw new Error(`status HTTP ${r.status}`);
        const data = await r.json();
        if (cancelled) return;
        if (!data.pdf_ready) {
          setError("Votre livre n'est pas encore prêt. Réessayez dans quelques minutes.");
          return;
        }
        setTotalPages(data.pdf_pages || 0);
        setPdfUrl(data.pdf_url || null);
      } catch (e) {
        if (!cancelled) setError('Impossible de charger votre livre. ' + e.message);
      }
    })();
    return () => { cancelled = true; };
  }, [sessionId]);

  // ── Son doux de feuille (WebAudio synth, ~120 ms) ──
  const playFlipSound = useCallback(() => {
    try {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)();
      }
      const ctx = audioCtxRef.current;
      const now = ctx.currentTime;
      // Bruit rose court : buffer 0.15s + enveloppe rapide
      const bufSize = Math.floor(ctx.sampleRate * 0.14);
      const buf = ctx.createBuffer(1, bufSize, ctx.sampleRate);
      const data = buf.getChannelData(0);
      let b = 0;
      for (let i = 0; i < bufSize; i++) {
        // Bruit rose filtré + décroissance rapide → sonorité "papier"
        const white = Math.random() * 2 - 1;
        b = 0.99 * b + 0.01 * white;
        const env = Math.exp(-i / (bufSize * 0.25));
        data[i] = b * env * 0.35;
      }
      const src = ctx.createBufferSource();
      src.buffer = buf;
      const filter = ctx.createBiquadFilter();
      filter.type = 'bandpass'; filter.frequency.value = 2800; filter.Q.value = 0.9;
      const gain = ctx.createGain(); gain.gain.value = 0.5;
      src.connect(filter); filter.connect(gain); gain.connect(ctx.destination);
      src.start(now); src.stop(now + 0.2);
    } catch (e) {
      // Silent fail — no audio available
    }
  }, []);

  // ── Navigation ──
  const goTo = useCallback((n) => {
    if (!totalPages) return;
    const clamped = Math.max(1, Math.min(totalPages, n));
    if (clamped === currentPage) return;
    setTurning(true);
    playFlipSound();
    setCurrentPage(clamped);
    setTimeout(() => setTurning(false), 260);
  }, [currentPage, totalPages, playFlipSound]);

  const next = useCallback(() => goTo(currentPage + 1), [goTo, currentPage]);
  const prev = useCallback(() => goTo(currentPage - 1), [goTo, currentPage]);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); next(); }
      else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); prev(); }
      else if (e.key === 'Home') { e.preventDefault(); goTo(1); }
      else if (e.key === 'End') { e.preventDefault(); goTo(totalPages); }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [next, prev, goTo, totalPages]);

  // Preload +1 et +2 pour un feuilletage fluide
  const preloadUrls = useMemo(() => {
    if (!sessionId || !totalPages) return [];
    return [1, 2].map((d) => currentPage + d).filter((n) => n <= totalPages)
      .map((n) => `${API}/api/composer/pages/${sessionId}/${n}.jpg`);
  }, [sessionId, totalPages, currentPage]);

  useEffect(() => {
    preloadUrls.forEach((url) => { const i = new Image(); i.src = url; });
  }, [preloadUrls]);

  const currentImgUrl = sessionId && totalPages
    ? `${API}/api/composer/pages/${sessionId}/${currentPage}.jpg`
    : null;

  return (
    <PsPageShell background="dark">
      <SEO path="/mon-compte/mon-livre" title="Mon Livre Astral"
           description="Feuilletez votre Livre Astral en ligne." noindex />
      <div data-testid="mon-livre-page" style={styles.wrap}>
        <p style={styles.eyebrow}>MON LIVRE ASTRAL</p>
        <h1 style={styles.h1}>Feuilletez votre livre</h1>

        {error && <p style={styles.errorBox} data-testid="mon-livre-error">{error}</p>}

        {!error && !totalPages && (
          <p style={styles.subtitle}>Chargement…</p>
        )}

        {totalPages > 0 && (
          <>
            <div style={styles.readerFrame} data-testid="reader-frame">
              <button
                onClick={prev}
                disabled={currentPage <= 1}
                aria-label="Page précédente"
                data-testid="prev-page-btn"
                style={{ ...styles.navBtn, ...styles.navBtnLeft,
                         opacity: currentPage <= 1 ? 0.25 : 1 }}
              >‹</button>
              <div
                style={{
                  ...styles.pageStage,
                  transform: turning ? 'rotateY(-2deg)' : 'rotateY(0)',
                  filter: turning ? 'brightness(0.92)' : 'none',
                }}
              >
                {currentImgUrl && (
                  <img
                    src={currentImgUrl}
                    alt={`Page ${currentPage}`}
                    data-testid="page-image"
                    style={styles.pageImg}
                  />
                )}
              </div>
              <button
                onClick={next}
                disabled={currentPage >= totalPages}
                aria-label="Page suivante"
                data-testid="next-page-btn"
                style={{ ...styles.navBtn, ...styles.navBtnRight,
                         opacity: currentPage >= totalPages ? 0.25 : 1 }}
              >›</button>
            </div>

            <div style={styles.controls} data-testid="reader-controls">
              <span style={styles.pageCounter}>
                Page <b>{currentPage}</b> <span style={styles.divider}>/</span> {totalPages}
              </span>
              <input
                type="range"
                min={1} max={totalPages} value={currentPage}
                data-testid="page-slider"
                onChange={(e) => goTo(Number(e.target.value))}
                style={styles.slider}
              />
              {pdfUrl && (
                <a href={pdfUrl} target="_blank" rel="noreferrer"
                   data-testid="download-full-pdf"
                   style={styles.ctaGhost}>Télécharger le PDF</a>
              )}
            </div>

            <p style={styles.hint}>
              Utilisez les flèches ← → du clavier pour tourner les pages.
              Home et End pour aller au début ou à la fin.
            </p>
          </>
        )}

        <Link to="/mon-compte" style={{ ...styles.ctaGhost, marginTop: 40, textDecoration: 'none' }}>
          Retour à mon compte
        </Link>
      </div>
    </PsPageShell>
  );
}


const styles = {
  wrap: { maxWidth: 900, margin: '0 auto', padding: '60px 24px 100px',
          color: '#F5EEE0', fontFamily: '"Cormorant Garamond","Lora",serif', textAlign: 'center' },
  eyebrow: { fontFamily: '"Cinzel",serif', fontSize: '0.72rem', letterSpacing: 4, color: '#C9AE7C', margin: 0 },
  h1: { fontFamily: '"Cormorant Garamond",serif', fontSize: 'clamp(2rem,4.6vw,2.8rem)',
        color: '#F5EEE0', margin: '14px 0 32px', fontWeight: 300 },
  subtitle: { fontSize: '1.05rem', color: 'rgba(245,238,224,0.75)', fontStyle: 'italic' },
  errorBox: { padding: '14px 16px', background: 'rgba(232,144,107,0.10)',
              border: '1px solid rgba(232,144,107,0.35)', borderRadius: 4,
              color: '#F5EEE0', margin: '20px auto', maxWidth: 520 },
  readerFrame: { position: 'relative', width: 'min(560px,90vw)', aspectRatio: '148/210',
                 margin: '20px auto', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  pageStage: { position: 'relative', width: '100%', height: '100%',
               background: '#FBF7F0', boxShadow: '0 20px 60px rgba(0,0,0,0.45), 0 0 0 1px rgba(201,174,124,0.25)',
               transition: 'transform 0.26s ease, filter 0.26s ease',
               transformOrigin: 'left center' },
  pageImg: { width: '100%', height: '100%', objectFit: 'contain', display: 'block' },
  navBtn: { position: 'absolute', top: '50%', transform: 'translateY(-50%)',
            background: 'transparent', border: '1px solid rgba(201,174,124,0.45)',
            color: '#C9AE7C', width: 40, height: 40, borderRadius: '50%',
            fontSize: 24, cursor: 'pointer', fontFamily: 'serif',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'opacity 0.2s, background 0.2s' },
  navBtnLeft: { left: -60 },
  navBtnRight: { right: -60 },
  controls: { display: 'flex', gap: 20, alignItems: 'center', justifyContent: 'center',
              flexWrap: 'wrap', marginTop: 24 },
  pageCounter: { fontFamily: '"Cormorant Garamond",serif', fontSize: '1.1rem',
                 color: '#F5EEE0', fontVariantNumeric: 'tabular-nums' },
  divider: { color: 'rgba(201,174,124,0.6)', fontStyle: 'italic', margin: '0 6px' },
  slider: { flex: '1 1 280px', maxWidth: 320, accentColor: '#C9AE7C' },
  hint: { fontSize: '0.85rem', color: 'rgba(245,238,224,0.55)',
          fontStyle: 'italic', marginTop: 24 },
  ctaGhost: { display: 'inline-block', padding: '10px 18px', background: 'transparent',
              color: '#F5EEE0', border: '1px solid rgba(201,174,124,0.45)', borderRadius: 2,
              fontFamily: '"Cinzel",serif', fontSize: '0.75rem', letterSpacing: 2.2 },
};
