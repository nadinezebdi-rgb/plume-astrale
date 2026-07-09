import React, { useState } from 'react';
import { Clock, ArrowRight, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import NatalDataModal from './NatalDataModal';

/**
 * Soft prompt shown when an authenticated user is missing their birth_time.
 * Unlocks accurate Ascendant + houses calculations.
 *
 * Props:
 *  - variant: 'banner' (full-width compact) | 'card' (boxed) — default 'card'
 *  - className: optional outer classes
 */
export default function NatalCompletionPrompt({ variant = 'card', className = '' }) {
  const { isAuthenticated, user } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);

  if (!isAuthenticated) return null;
  if (!user) return null;
  // Show only if birth_time is missing (empty or null) but birth_date exists
  // (no point if the user hasn't done any onboarding)
  const hasDate = !!user.birth_date;
  const hasTime = !!user.birth_time && user.birth_time !== '00:00';
  if (!hasDate || hasTime) return null;

  const wrapperBase = {
    background: 'linear-gradient(135deg, rgba(167,139,250,0.10) 0%, rgba(212,175,55,0.10) 100%)',
    border: '1px solid rgba(212,175,55,0.30)',
    backdropFilter: 'blur(12px)',
    borderRadius: variant === 'banner' ? 14 : 18,
    padding: variant === 'banner' ? '14px 18px' : '20px 22px',
  };

  return (
    <>
      <div
        data-testid="natal-completion-prompt"
        className={className}
        style={wrapperBase}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 14,
            flexWrap: 'wrap',
          }}
        >
          <div
            style={{
              width: 38, height: 38, borderRadius: '50%',
              background: 'rgba(212,175,55,0.18)',
              border: '1px solid rgba(212,175,55,0.45)',
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <Clock style={{ width: 18, height: 18, color: '#E8C766' }} strokeWidth={1.6} />
          </div>

          <div style={{ flex: '1 1 220px', minWidth: 0 }}>
            <p
              style={{
                fontFamily: 'Cinzel, serif',
                fontSize: 11, letterSpacing: '0.18em',
                color: '#E8C766', textTransform: 'uppercase',
                marginBottom: 4,
              }}
            >
              <Sparkles style={{ width: 11, height: 11, display: 'inline', marginRight: 4, marginBottom: 2 }} />
              Débloque ton Ascendant
            </p>
            <p
              style={{
                color: 'var(--pa-body, rgba(244,228,188,0.85))',
                fontSize: 13.5,
                lineHeight: 1.5,
                margin: 0,
              }}
            >
              Ajoute ton <strong style={{ color: '#F4E4BC' }}>heure de naissance</strong> pour
              révéler ton Ascendant précis et lire tes maisons astrologiques.
            </p>
          </div>

          <button
            onClick={() => setModalOpen(true)}
            data-testid="natal-completion-cta"
            style={{
              padding: '9px 18px', borderRadius: 999,
              background: '#D4AF37', color: '#0F1230',
              fontFamily: 'Cinzel, serif', fontSize: 11, fontWeight: 600,
              letterSpacing: '0.14em', textTransform: 'uppercase',
              border: 'none', cursor: 'pointer',
              display: 'inline-flex', alignItems: 'center', gap: 6,
              whiteSpace: 'nowrap',
              transition: 'transform 0.2s ease',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-1px)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; }}
          >
            Compléter
            <ArrowRight style={{ width: 12, height: 12 }} strokeWidth={2} />
          </button>
        </div>
      </div>

      <NatalDataModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSuccess={() => setModalOpen(false)}
      />
    </>
  );
}
