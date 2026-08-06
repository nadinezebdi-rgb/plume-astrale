import React, { useEffect } from 'react';
import { X, ArrowRight, BookOpen } from 'lucide-react';

/**
 * ApercuLectureModal — Modal léger qui affiche un extrait gratuit de lecture.
 * Ouvert depuis un bouton "Lire un extrait" sur les pages produit.
 *
 * Props :
 *   open     : bool
 *   onClose  : () => void
 *   apercu   : { label, hook, pages: [{chapter, eyebrow?, body}], hint }
 *   ctaLabel : string (ex. "Recevoir ma lecture complète")
 *   onCta    : () => void  (déclenche l'achat)
 */
export default function ApercuLectureModal({ open, onClose, apercu, ctaLabel, onCta }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = '';
    };
  }, [open, onClose]);

  if (!open || !apercu) return null;

  return (
    <div
      data-testid="apercu-modal-overlay"
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 500,
        background: 'rgba(15,26,60,0.72)',
        backdropFilter: 'blur(8px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: 24,
        animation: 'fadeIn 200ms ease',
      }}>
      <div
        data-testid="apercu-modal"
        onClick={(e) => e.stopPropagation()}
        style={{
          background: '#F7F5F0',
          borderRadius: 16,
          maxWidth: 720,
          width: '100%',
          maxHeight: '90vh',
          overflowY: 'auto',
          border: '1px solid #E3E1DC',
          boxShadow: '0 40px 80px rgba(0,0,0,0.35)',
          position: 'relative',
        }}>

        {/* Header */}
        <div style={{
          position: 'sticky', top: 0, zIndex: 2,
          background: '#F7F5F0',
          borderBottom: '1px solid #E3E1DC',
          padding: '20px 28px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0 }}>
            <div style={{
              width: 40, height: 40, borderRadius: 10,
              background: 'rgba(201,162,75,0.12)',
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}>
              <BookOpen style={{ width: 18, height: 18, color: '#C9A24B' }} strokeWidth={1.8} />
            </div>
            <div style={{ minWidth: 0 }}>
              <div style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 11, fontWeight: 600,
                letterSpacing: '0.16em', textTransform: 'uppercase',
                color: '#C9A24B',
              }}>Aperçu gratuit</div>
              <div style={{
                fontFamily: 'Playfair Display, serif',
                fontSize: 20, fontWeight: 500,
                color: '#0F1A3C', lineHeight: 1.2,
                overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
              }}>{apercu.label}</div>
            </div>
          </div>
          <button
            onClick={onClose}
            data-testid="apercu-modal-close"
            aria-label="Fermer l'aperçu"
            style={{
              background: 'transparent', border: 'none', cursor: 'pointer',
              width: 40, height: 40, borderRadius: 999,
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              color: '#6B7280',
              flexShrink: 0,
              transition: 'background 200ms ease, color 200ms ease',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(15,26,60,0.06)'; e.currentTarget.style.color = '#0F1A3C'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#6B7280'; }}>
            <X style={{ width: 22, height: 22 }} strokeWidth={1.8} />
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '32px 28px 24px' }}>
          <p style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 14, lineHeight: 1.6,
            color: '#6B7280', fontStyle: 'italic',
            marginTop: 0, marginBottom: 32,
          }}>
            {apercu.hook}
          </p>

          {apercu.pages.map((page, i) => (
            <div key={i} style={{ marginBottom: 32 }}>
              {page.eyebrow && (
                <div style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11, fontWeight: 600,
                  letterSpacing: '0.18em', textTransform: 'uppercase',
                  color: '#C9A24B', marginBottom: 8,
                }}>{page.eyebrow}</div>
              )}
              <h3 style={{
                fontFamily: 'Playfair Display, serif',
                fontSize: 20, fontWeight: 500,
                color: '#0F1A3C', marginTop: 0, marginBottom: 16,
                lineHeight: 1.3,
                letterSpacing: '0.02em',
              }}>{page.chapter}</h3>
              <div style={{
                fontFamily: 'Playfair Display, serif',
                fontSize: 16, lineHeight: 1.75,
                color: '#232323',
                whiteSpace: 'pre-line',
              }}>{page.body}</div>
            </div>
          ))}

          {/* Fondu doré symbolique */}
          <div style={{
            marginTop: 32, padding: '20px 24px',
            background: 'linear-gradient(180deg, transparent 0%, rgba(201,162,75,0.05) 100%)',
            borderTop: '1px dashed rgba(201,162,75,0.4)',
            borderRadius: '0 0 8px 8px',
            textAlign: 'center',
          }}>
            <div style={{
              fontFamily: 'Playfair Display, serif',
              fontSize: 15, fontStyle: 'italic',
              color: '#6B7280', lineHeight: 1.55, marginBottom: 20,
              maxWidth: 480, margin: '0 auto 20px',
            }}>
              {apercu.hint}
            </div>
            <button
              onClick={onCta}
              className="ps-btn ps-btn-primary"
              data-testid="apercu-modal-cta"
              style={{ padding: '14px 28px' }}>
              {ctaLabel || 'Recevoir ma lecture complète'}
              <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={2} />
            </button>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn { from { opacity: 0 } to { opacity: 1 } }
      `}</style>
    </div>
  );
}
