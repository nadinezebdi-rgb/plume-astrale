import React, { useEffect, useState } from 'react';
import { ArrowRight } from 'lucide-react';

/**
 * StickyMobileCta — barre CTA persistante en bas d'écran sur mobile,
 * visible uniquement quand le hero (avec le prix) sort du viewport.
 *
 * Positionnée AU-DESSUS de la mobile tabbar (72px + safe-area).
 * Cachée sur >= 768px (les CTA hero desktop restent visibles).
 *
 * Impact conversion : +15-25% typique sur pages de vente longues.
 */
export default function StickyMobileCta({
  priceMain,
  priceStrike,
  ctaLabel,
  onCta,
  testid = 'sticky-mobile-cta',
}) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const heroCta = document.querySelector('[data-testid$="-cta-hero"]');
    if (!heroCta) return;

    // Observer : dès que le CTA hero sort du viewport, on affiche la sticky bar
    const io = new IntersectionObserver(
      ([entry]) => setVisible(!entry.isIntersecting),
      { threshold: 0, rootMargin: '0px' },
    );
    io.observe(heroCta);
    return () => io.disconnect();
  }, []);

  return (
    <div
      className="sticky-mobile-cta"
      data-testid={testid}
      data-visible={visible ? 'true' : 'false'}
      style={{
        position: 'fixed',
        left: 0,
        right: 0,
        bottom: 'calc(72px + env(safe-area-inset-bottom, 0px))',
        zIndex: 40,
        padding: '10px 12px',
        background: 'rgba(255, 255, 255, 0.97)',
        borderTop: '1px solid #E3E1DC',
        boxShadow: '0 -8px 24px rgba(15, 26, 60, 0.10)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        transform: visible ? 'translateY(0)' : 'translateY(120%)',
        transition: 'transform 280ms cubic-bezier(0.22, 1, 0.36, 1)',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', minWidth: 0, flexShrink: 0 }}>
        <div style={{
          fontFamily: 'Playfair Display, serif',
          fontSize: 22,
          lineHeight: 1,
          fontWeight: 500,
          color: '#0F1A3C',
          whiteSpace: 'nowrap',
        }}>
          {priceMain}
        </div>
        {priceStrike && (
          <div style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 11,
            color: '#6B7280',
            textDecoration: 'line-through',
            marginTop: 2,
          }}>
            {priceStrike}
          </div>
        )}
      </div>
      <button
        type="button"
        onClick={onCta}
        data-testid={`${testid}-btn`}
        className="ps-btn ps-btn-primary"
        style={{ flex: 1, padding: '12px 14px', minWidth: 0, fontSize: 13, letterSpacing: '0.01em' }}
      >
        <span style={{
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          minWidth: 0,
        }}>
          {ctaLabel}
        </span>
        <ArrowRight style={{ width: 15, height: 15, flexShrink: 0 }} strokeWidth={2} />
      </button>
      <style>{`
        @media (min-width: 768px) {
          .sticky-mobile-cta { display: none !important; }
        }
      `}</style>
    </div>
  );
}
