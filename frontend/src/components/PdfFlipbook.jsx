import React, { useEffect, useMemo, useRef, useState } from 'react';
import { X, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';

/**
 * PdfFlipbook — Feuilletage interactif d'un aperçu PDF en 3-4 pages.
 *
 * Utilise l'endpoint public backend :
 *   GET /api/pdf-preview/{product}/pages/meta   → { total_pages }
 *   GET /api/pdf-preview/{product}/page/{n}.jpg → JPEG rendu à 150 DPI
 *
 * Effet page-flip via CSS 3D perspective + rotateY sur l'axe vertical droit
 * de la page courante. Aucune dépendance externe.
 *
 * Props :
 *   - product : slug du produit (astrocartographie, kabbale, ...)
 *   - title   : titre affiché en overlay
 *   - onClose : callback fermeture (rend le composant modal)
 *   - testid  : préfixe data-testid (défaut : pdf-flipbook)
 */
export default function PdfFlipbook({ product, title, onClose, testid = 'pdf-flipbook' }) {
  const backend = process.env.REACT_APP_BACKEND_URL;
  const [totalPages, setTotalPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const [flipping, setFlipping] = useState(null); // 'next' | 'prev' | null
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const flipTimeout = useRef(null);

  // Charge la meta au montage
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(`${backend}/api/pdf-preview/${product}/pages/meta`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((d) => {
        if (!cancelled) {
          setTotalPages(d.total_pages || 0);
          setLoading(false);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e.message);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
      if (flipTimeout.current) clearTimeout(flipTimeout.current);
    };
  }, [backend, product]);

  // Précharge silencieusement les pages voisines pour un feuilletage fluide
  useEffect(() => {
    if (!totalPages) return;
    [-1, 1, 2].forEach((offset) => {
      const idx = currentPage + offset;
      if (idx >= 0 && idx < totalPages) {
        const img = new Image();
        img.src = `${backend}/api/pdf-preview/${product}/page/${idx}.jpg`;
      }
    });
  }, [backend, product, currentPage, totalPages]);

  const goTo = (direction) => {
    if (flipping) return;
    const next = direction === 'next' ? currentPage + 1 : currentPage - 1;
    if (next < 0 || next >= totalPages) return;
    setFlipping(direction);
    flipTimeout.current = setTimeout(() => {
      setCurrentPage(next);
      setFlipping(null);
    }, 620);
  };

  // Clavier : ← → esc
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'ArrowRight') goTo('next');
      else if (e.key === 'ArrowLeft') goTo('prev');
      else if (e.key === 'Escape') onClose?.();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [currentPage, totalPages, flipping, onClose]);

  const pageUrl = useMemo(
    () => (idx) => `${backend}/api/pdf-preview/${product}/page/${idx}.jpg`,
    [backend, product],
  );

  return (
    <div
      data-testid={testid}
      role="dialog"
      aria-modal="true"
      aria-label={`Feuilletage — ${title}`}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 1200,
        background: 'radial-gradient(ellipse at center, rgba(15,26,60,0.92) 0%, rgba(8,14,32,0.98) 100%)',
        backdropFilter: 'blur(6px)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '48px 20px 32px',
      }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose?.(); }}
    >
      {/* Header title + close */}
      <div style={{
        position: 'absolute', top: 20, left: 24, right: 24,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{
          fontFamily: 'Playfair Display, serif',
          fontSize: 18,
          color: '#F7F5F0',
          fontStyle: 'italic',
          letterSpacing: '0.02em',
        }}>
          Aperçu — <span style={{ color: '#C9A24B' }}>{title}</span>
        </div>
        <button
          type="button"
          onClick={onClose}
          data-testid={`${testid}-close`}
          aria-label="Fermer le feuilletage"
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            padding: '8px 14px',
            borderRadius: 999,
            background: 'rgba(247,245,240,0.10)',
            color: '#F7F5F0',
            border: '1px solid rgba(247,245,240,0.25)',
            fontFamily: 'Inter, sans-serif',
            fontSize: 12,
            fontWeight: 500,
            letterSpacing: '0.10em',
            textTransform: 'uppercase',
            cursor: 'pointer',
          }}
        >
          <X style={{ width: 14, height: 14 }} strokeWidth={2} />
          Fermer
        </button>
      </div>

      {/* Zone du livre */}
      <div
        style={{
          position: 'relative',
          width: 'min(560px, 92vw)',
          aspectRatio: '210 / 297', // A4 portrait
          perspective: '1800px',
          transformStyle: 'preserve-3d',
        }}
      >
        {loading && (
          <div style={{
            position: 'absolute', inset: 0, display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            color: '#C9A24B', gap: 10, fontFamily: 'Inter, sans-serif', fontSize: 13,
          }}>
            <Loader2 style={{ width: 18, height: 18 }} className="animate-spin" strokeWidth={1.8} />
            Chargement de l&apos;aperçu…
          </div>
        )}
        {error && (
          <div style={{
            position: 'absolute', inset: 0, display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            color: '#B0533F', textAlign: 'center', padding: 24,
            fontFamily: 'Inter, sans-serif', fontSize: 13,
          }}>
            Impossible de charger l&apos;aperçu. Réessaie dans un instant.
          </div>
        )}

        {/* Page courante (statique) */}
        {!loading && !error && totalPages > 0 && (
          <>
            {/* Ombre portée + coin corné */}
            <div
              aria-hidden
              style={{
                position: 'absolute', inset: 0,
                boxShadow: '0 40px 80px -20px rgba(0,0,0,0.55), 0 12px 28px -8px rgba(0,0,0,0.35)',
                borderRadius: 6,
                background: '#FFFFFF',
              }}
            />
            <img
              src={pageUrl(currentPage)}
              alt={`Page ${currentPage + 1} sur ${totalPages}`}
              data-testid={`${testid}-page-${currentPage}`}
              style={{
                position: 'absolute', inset: 0,
                width: '100%', height: '100%',
                objectFit: 'contain',
                background: '#FFFFFF',
                borderRadius: 6,
                userSelect: 'none',
                pointerEvents: 'none',
              }}
              draggable={false}
            />

            {/* Page tournante (superposée pendant l'animation) */}
            {flipping && (
              <div
                aria-hidden
                style={{
                  position: 'absolute', inset: 0,
                  transformOrigin: flipping === 'next' ? 'left center' : 'right center',
                  transformStyle: 'preserve-3d',
                  animation: `flipbook-${flipping} 620ms cubic-bezier(0.6, 0.04, 0.4, 1) forwards`,
                  zIndex: 3,
                }}
              >
                <div
                  style={{
                    position: 'absolute', inset: 0,
                    backfaceVisibility: 'hidden',
                    background: '#FFFFFF',
                    borderRadius: 6,
                    overflow: 'hidden',
                    boxShadow: '0 12px 30px rgba(0,0,0,0.35)',
                  }}
                >
                  <img
                    src={pageUrl(flipping === 'next' ? currentPage : currentPage - 1)}
                    alt=""
                    style={{
                      width: '100%', height: '100%',
                      objectFit: 'contain',
                      pointerEvents: 'none',
                    }}
                    draggable={false}
                  />
                  {/* Voile qui s'assombrit au flip pour effet volume */}
                  <div
                    style={{
                      position: 'absolute', inset: 0,
                      background: flipping === 'next'
                        ? 'linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.05) 60%, rgba(0,0,0,0.25) 100%)'
                        : 'linear-gradient(-90deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.05) 60%, rgba(0,0,0,0.25) 100%)',
                      opacity: 0.9,
                    }}
                  />
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Contrôles navigation */}
      {!loading && !error && totalPages > 0 && (
        <div style={{
          marginTop: 28,
          display: 'flex',
          alignItems: 'center',
          gap: 18,
          background: 'rgba(247,245,240,0.06)',
          border: '1px solid rgba(247,245,240,0.15)',
          padding: '10px 22px',
          borderRadius: 999,
        }}>
          <button
            type="button"
            onClick={() => goTo('prev')}
            disabled={currentPage === 0 || flipping}
            data-testid={`${testid}-prev`}
            aria-label="Page précédente"
            style={navBtnStyle(currentPage === 0 || !!flipping)}
          >
            <ChevronLeft style={{ width: 18, height: 18 }} strokeWidth={2} />
          </button>
          <span style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 12,
            fontWeight: 500,
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
            color: '#F7F5F0',
            minWidth: 80,
            textAlign: 'center',
          }}>
            Page {currentPage + 1} <span style={{ color: 'rgba(247,245,240,0.45)' }}>/ {totalPages}</span>
          </span>
          <button
            type="button"
            onClick={() => goTo('next')}
            disabled={currentPage >= totalPages - 1 || flipping}
            data-testid={`${testid}-next`}
            aria-label="Page suivante"
            style={navBtnStyle(currentPage >= totalPages - 1 || !!flipping)}
          >
            <ChevronRight style={{ width: 18, height: 18 }} strokeWidth={2} />
          </button>
        </div>
      )}

      <p style={{
        marginTop: 14,
        fontFamily: 'Inter, sans-serif',
        fontSize: 11,
        letterSpacing: '0.14em',
        textTransform: 'uppercase',
        color: 'rgba(247,245,240,0.45)',
      }}>
        Aperçu · les {totalPages || 3} premières pages
      </p>

      {/* Keyframes injectées inline (indépendant du CSS global) */}
      <style>{`
        @keyframes flipbook-next {
          0%   { transform: rotateY(0deg); }
          100% { transform: rotateY(-175deg); }
        }
        @keyframes flipbook-prev {
          0%   { transform: rotateY(0deg); }
          100% { transform: rotateY(175deg); }
        }
      `}</style>
    </div>
  );
}

function navBtnStyle(disabled) {
  return {
    width: 40, height: 40,
    borderRadius: 999,
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: disabled ? 'rgba(247,245,240,0.05)' : '#C9A24B',
    color: disabled ? 'rgba(247,245,240,0.35)' : '#0F1A3C',
    border: 'none',
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition: 'background 0.2s ease, transform 0.2s ease',
  };
}
