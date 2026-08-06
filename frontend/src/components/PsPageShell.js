import React from 'react';
import NavbarV2 from './NavbarV2';
import FooterV2 from './FooterV2';

/**
 * PsPageShell — wrapper de page pour la charte v3.
 * Fournit Navbar sticky + fond crème par défaut + Footer navy.
 *
 * Usage :
 *   <PsPageShell background="light|dark">
 *     ...contenu...
 *   </PsPageShell>
 */
export default function PsPageShell({ background = 'light', children }) {
  const bg = background === 'dark' ? '#0F1A3C' : '#F7F5F0';
  return (
    <div className="ps-home" data-testid="ps-page-shell" style={{ background: bg, minHeight: '100vh' }}>
      <NavbarV2 />
      {children}
      <FooterV2 />
    </div>
  );
}
