import React from 'react';
import { Sparkles } from 'lucide-react';

/**
 * Badge "✨ Enrichi par Soléna" — affiché sur les blocs de texte qui ont été
 * passés dans la couche narrative GPT-5.4 (services/enrich_narrative.py).
 *
 * Props :
 *   - visible (bool, default true) : rend null si false
 *   - variant : 'default' | 'compact' | 'inline'
 *   - align   : 'left' | 'center' | 'right'
 */
export const EnrichedBadge = ({ visible = true, variant = 'default', align = 'left' }) => {
  if (!visible) return null;

  const base = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    borderRadius: 999,
    fontFamily: 'Cinzel, serif',
    letterSpacing: '0.2em',
    textTransform: 'uppercase',
    color: '#D4AF37',
    background: 'rgba(212,175,55,0.12)',
    border: '1px solid rgba(212,175,55,0.35)',
    whiteSpace: 'nowrap',
  };

  const sizes = {
    default: { padding: '6px 12px', fontSize: 10 },
    compact: { padding: '3px 10px', fontSize: 9 },
    inline:  { padding: '2px 8px',  fontSize: 9 },
  };

  const wrapStyle = {
    display: 'flex',
    justifyContent: align === 'center' ? 'center' : align === 'right' ? 'flex-end' : 'flex-start',
    marginBottom: 12,
  };

  return (
    <div style={wrapStyle} data-testid="enriched-badge">
      <span style={{ ...base, ...sizes[variant] }}>
        <Sparkles style={{ width: 12, height: 12 }} strokeWidth={1.5} />
        Enrichi par Soléna
      </span>
    </div>
  );
};

export default EnrichedBadge;
