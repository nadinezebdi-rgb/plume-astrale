import React, { useEffect, useMemo, useState } from 'react';
import { X } from 'lucide-react';
import SynastrieLeadMagnet from './SynastrieLeadMagnet';
import { event as trackEvent } from '../lib/analytics';
import { trackABEvent } from '../lib/abTracking';

const DISMISSED_KEY = 'plume_syn_exit_intent_dismissed';
const SENT_KEY = 'plume_syn_lead_sent';
const VARIANT_KEY = 'plume_syn_exit_intent_variant';
const COOLDOWN_MS = 24 * 60 * 60 * 1000; // 24h

// A/B copies : persistées en localStorage pour conserver la variante entre pages.
const VARIANTS = {
  A: {
    eyebrow: 'Extrait gratuit · 3 pages',
    title: 'Un aperçu de votre lien, offert.',
    subtitle:
      'Entrez vos deux prénoms et dates de naissance : nous générons un extrait de 3 pages de votre synastrie, envoyé par email dans la minute.',
  },
  B: {
    eyebrow: 'Avant de partir',
    title: 'On vous offre un extrait de 3 pages.',
    subtitle:
      'Les 3 premières pages de votre synastrie — Soleils croisés + ouverture de rapport — sans engagement, dans votre boîte mail en une minute.',
  },
};

function _pickVariant() {
  try {
    const existing = localStorage.getItem(VARIANT_KEY);
    if (existing && VARIANTS[existing]) return existing;
    const picked = Math.random() < 0.5 ? 'A' : 'B';
    localStorage.setItem(VARIANT_KEY, picked);
    return picked;
  } catch {
    return Math.random() < 0.5 ? 'A' : 'B';
  }
}

function _shouldSkip() {
  try {
    const sent = localStorage.getItem(SENT_KEY);
    if (sent) return true;
    const dismissed = localStorage.getItem(DISMISSED_KEY);
    if (dismissed && Date.now() - Number(dismissed) < COOLDOWN_MS) return true;
  } catch { /* noop */ }
  return false;
}

/**
 * SynastrieExitIntentModal — modal plein-écran qui s'ouvre quand le visiteur
 * déplace sa souris vers le haut de la fenêtre (intention de quitter) sur /synastrie.
 *
 * - Désactivé si lead déjà envoyé (localStorage plume_syn_lead_sent)
 * - Désactivé si déjà fermé dans les 24h (localStorage plume_syn_exit_intent_dismissed)
 * - Mobile : fallback via scroll bottom (pas d'event mouseout fiable).
 */
export default function SynastrieExitIntentModal() {
  const [open, setOpen] = useState(false);
  const variantKey = useMemo(() => _pickVariant(), []);
  const copy = VARIANTS[variantKey];

  useEffect(() => {
    if (_shouldSkip()) return undefined;

    let triggered = false;
    const trigger = (source) => {
      if (triggered) return;
      triggered = true;
      try { trackEvent('exit_intent_shown', { page: 'synastrie', source, variant: variantKey }); } catch { /* noop */ }
      trackABEvent('synastrie_exit_intent', variantKey, 'shown', { source });
      setOpen(true);
    };

    // Desktop : exit-intent via mouseout vers le haut
    const onMouseOut = (e) => {
      // relatedTarget nullish & clientY proche de 0 = souris sortie par le haut
      if (!e.relatedTarget && e.clientY <= 10) {
        trigger('mouseout_top');
      }
    };

    // Mobile fallback : atteindre 70% de scroll (approximatif engagement + intent)
    let scrollArmed = false;
    const onScroll = () => {
      const doc = document.documentElement;
      const pct = (doc.scrollTop + window.innerHeight) / (doc.scrollHeight || 1);
      if (pct >= 0.7) {
        if (scrollArmed) trigger('mobile_scroll_70');
        scrollArmed = true;
      }
    };

    // Grace period 8s avant d'armer : évite les faux positifs juste après page load
    const armTimer = setTimeout(() => {
      document.addEventListener('mouseout', onMouseOut);
      window.addEventListener('scroll', onScroll, { passive: true });
    }, 8000);

    return () => {
      clearTimeout(armTimer);
      document.removeEventListener('mouseout', onMouseOut);
      window.removeEventListener('scroll', onScroll);
    };
  }, []);

  const close = () => {
    try { localStorage.setItem(DISMISSED_KEY, String(Date.now())); } catch { /* noop */ }
    try { trackEvent('exit_intent_dismissed', { page: 'synastrie', variant: variantKey }); } catch { /* noop */ }
    trackABEvent('synastrie_exit_intent', variantKey, 'dismissed');
    setOpen(false);
  };

  // Esc key dismisses the modal.
  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => { if (e.key === 'Escape') close(); };
    document.addEventListener('keydown', onKey);
    // Lock body scroll while modal open
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = prev;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  if (!open) return null;

  return (
    <div
      data-testid="synastrie-exit-intent-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="synastrie-lead-title"
      onClick={(e) => { if (e.target === e.currentTarget) close(); }}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        background: 'rgba(10,17,48,0.78)',
        backdropFilter: 'blur(6px)',
      }}
    >
      <div
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: 720,
          maxHeight: '92vh',
          overflowY: 'auto',
          background: 'linear-gradient(180deg, #0F1A3A 0%, #0C132E 100%)',
          border: '1px solid rgba(212,175,55,0.3)',
          borderRadius: 10,
          boxShadow: '0 24px 60px rgba(0,0,0,0.6)',
        }}
      >
        <button
          type="button"
          onClick={close}
          aria-label="Fermer"
          data-testid="synastrie-exit-intent-close"
          style={{
            position: 'absolute',
            top: 14,
            right: 14,
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 34,
            height: 34,
            borderRadius: 999,
            border: '1px solid rgba(244,239,230,0.15)',
            background: 'rgba(0,0,0,0.3)',
            color: 'rgba(244,239,230,0.8)',
            cursor: 'pointer',
            zIndex: 2,
          }}
        >
          <X size={16} strokeWidth={1.8} />
        </button>
        <SynastrieLeadMagnet variant="modal" onSuccess={() => setOpen(false)} copy={copy} variantKey={variantKey} />
      </div>
    </div>
  );
}
