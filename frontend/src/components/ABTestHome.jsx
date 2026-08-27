/**
 * ABTestHome — wrapper de la route `/` qui split 50/50 les visiteurs
 * entre la home classique et le prototype immersif `/experience`.
 *
 * Activation : REACT_APP_EXP_AB_TEST === 'on' dans .env.
 * Persistance : sessionStorage `ab_home_variant` (même variante au refresh).
 * Bypass : ?ab=off (force homepage), ?ab=exp (force experience), ?ab=home.
 * Tracking : event 'ab_home_assigned' avec variant.
 *
 * Non-breaking : si la flag est OFF ou absente → toujours la homepage.
 */
import React, { useEffect, useMemo } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import Homepage from '@/pages/Homepage';
import { event as trackEvent } from '@/lib/analytics';

const STORAGE_KEY = 'ab_home_variant';

function readOverride(search) {
  try {
    const p = new URLSearchParams(search);
    const v = p.get('ab');
    if (v === 'off' || v === 'home') return 'homepage';
    if (v === 'exp' || v === 'experience') return 'experience';
  } catch { /* noop */ }
  return null;
}

function readStored() {
  try { return window.sessionStorage.getItem(STORAGE_KEY); } catch { return null; }
}

function assignVariant() {
  const v = Math.random() < 0.5 ? 'homepage' : 'experience';
  try { window.sessionStorage.setItem(STORAGE_KEY, v); } catch { /* noop */ }
  return v;
}

export default function ABTestHome() {
  const location = useLocation();
  const enabled = process.env.REACT_APP_EXP_AB_TEST === 'on';

  const variant = useMemo(() => {
    // Override URL toujours prioritaire (utile QA / preview) même si flag OFF.
    const override = readOverride(location.search);
    if (override) return override;
    if (!enabled) return 'homepage';
    return readStored() || assignVariant();
  }, [enabled, location.search]);

  useEffect(() => {
    if (!enabled) return;
    trackEvent('ab_home_assigned', { variant });
  }, [enabled, variant]);

  if (variant === 'experience') {
    // Préserve la query string entrante (utm_source etc.) pour /experience
    const qs = location.search || '';
    return <Navigate to={`/experience${qs}`} replace />;
  }
  return <Homepage />;
}
