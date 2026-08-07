import React from 'react';

/**
 * PsPageShell — wrapper de page pour la charte v3.
 *
 * `background="light"` expose la palette Plume Astrale v3 (crème / navy / or)
 * en tant que variables CSS locales. Tous les composants enfants qui utilisent
 * `var(--pa-heading)`, `var(--pa-body)`, `var(--pa-accent)`, etc. basculent
 * automatiquement en thème clair — sans devoir toucher chacun d'entre eux.
 *
 * Navbar + Footer sont rendus globalement dans App.js.
 */
const LIGHT_TOKENS = {
  '--pa-bg':            '#F7F5F0',
  '--pa-bg-deep':       '#F7F5F0',
  '--pa-bg-mid':        '#FFFFFF',
  '--pa-surface':       '#FFFFFF',
  '--pa-surface-hover': '#FBF9F4',

  '--pa-heading':       '#0F1A3C',
  '--pa-body':          '#232323',
  '--pa-muted':         'rgba(15,26,60,0.55)',

  '--pa-accent':        '#C9A24B',
  '--pa-accent-hover':  '#B48F3E',
  '--pa-accent-bright': '#DDB966',

  '--pa-divider':       'rgba(15,26,60,0.10)',
  '--pa-divider-soft':  'rgba(15,26,60,0.06)',
};

// Léger grain papier (feTurbulence) — cohérence avec les pages produits V3
const PAPER_TEXTURE_SVG =
  "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='420' height='420'>"
  + "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/>"
  + "<feColorMatrix values='0 0 0 0 0.06  0 0 0 0 0.10  0 0 0 0 0.24  0 0 0 0.055 0'/></filter>"
  + "<rect width='100%' height='100%' filter='url(%23n)'/></svg>\")";

export default function PsPageShell({ background = 'light', children }) {
  const isLight = background === 'light';
  const style = isLight
    ? {
        ...LIGHT_TOKENS,
        background: '#F7F5F0',
        backgroundImage: PAPER_TEXTURE_SVG,
        backgroundRepeat: 'repeat',
        minHeight: '100vh',
        color: '#232323',
      }
    : { background: '#0F1A3C', minHeight: '100vh' };
  return (
    <div className="ps-home" data-testid="ps-page-shell" data-shell={background} style={style}>
      {children}
    </div>
  );
}
