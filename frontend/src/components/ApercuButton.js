import React from 'react';
import { BookOpen } from 'lucide-react';

/**
 * ApercuButton — bouton discret et élégant pour télécharger l'aperçu 3 pages
 * d'un livre de la Bibliothèque Plume Astrale.
 *
 * Props :
 *   - bookKey : 'natal' | 'synastry' | 'kabbale' | 'astrocarto' | 'karmique'
 *   - variant : 'default' (bordure or) | 'ghost' (transparent, plus discret)
 */
const ApercuButton = ({ bookKey, variant = 'default', label }) => {
  const href = `${process.env.REACT_APP_BACKEND_URL}/api/apercus/${bookKey}.pdf`;

  const baseStyle = {
    color: 'rgba(212,175,55,0.85)',
    fontFamily: 'Cinzel, serif',
    letterSpacing: '0.24em',
    textTransform: 'uppercase',
    textDecoration: 'none',
    padding: '10px 22px',
    borderRadius: 999,
    transition: 'all 250ms ease',
  };

  const styleByVariant = {
    default: {
      ...baseStyle,
      border: '1px solid rgba(212,175,55,0.35)',
      background: 'rgba(14,10,30,0.35)',
    },
    ghost: {
      ...baseStyle,
      border: '1px solid rgba(212,175,55,0.18)',
      background: 'transparent',
    },
  };

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      data-testid={`apercu-${bookKey}`}
      className="inline-flex items-center gap-2 text-[11px] hover:opacity-100 hover:border-[rgba(212,175,55,0.7)]"
      style={styleByVariant[variant] || styleByVariant.default}
    >
      <BookOpen className="w-3.5 h-3.5" strokeWidth={1.5} />
      {label || "Feuilleter l'aperçu — 3 pages"}
    </a>
  );
};

export default ApercuButton;
