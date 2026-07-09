import React from 'react';

/**
 * Fil d'Ariane — Signature #2.
 * Une fine ligne verticale doree 1px au centre du viewport qui connecte les sections.
 * Visible uniquement sur desktop >= 1024px.
 */
const ScrollThread = () => (
  <div className="plume-scroll-thread" aria-hidden="true" data-testid="plume-scroll-thread" />
);

export default ScrollThread;
