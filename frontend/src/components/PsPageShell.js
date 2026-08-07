import React from 'react';

/**
 * PsPageShell — wrapper de page pour la charte v3.
 * Depuis iter 81, Navbar + Footer sont rendus globalement dans App.js —
 * PsPageShell ne s'occupe plus que du fond et du min-height.
 */
export default function PsPageShell({ background = 'light', children }) {
  const bg = background === 'dark' ? '#0F1A3C' : '#F7F5F0';
  return (
    <div className="ps-home" data-testid="ps-page-shell" style={{ background: bg, minHeight: '100vh' }}>
      {children}
    </div>
  );
}
