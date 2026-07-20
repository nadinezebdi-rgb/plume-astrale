import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Sparkles, X } from 'lucide-react';

/**
 * LiveSalesCounter — bandeau flottant bas-gauche qui alterne des
 * notifications sociales ("Marie vient de recevoir son Astrocarto").
 *
 * Objectif : urgence sociale douce, sans agressivité — style
 * Cartier/Aesop, pas Booking.com. Chaque notif reste 5s puis rotation.
 *
 * Le compteur est PERSISTANT sur toute la session (localStorage) : si
 * l'utilisatrice ferme le widget, il ne réapparaît plus avant 24h.
 */

// Prénoms variés (à peu près 60% FR / 40% international) — pas d'inventés
const NAMES = [
  'Marie', 'Sophie', 'Camille', 'Léa', 'Anaïs', 'Chloé',
  'Elena', 'Amélie', 'Juliette', 'Charlotte', 'Alice', 'Emma',
  'Clara', 'Manon', 'Zoé', 'Inès', 'Louise', 'Sarah', 'Nina',
  'Océane', 'Éléonore', 'Isabelle', 'Anna', 'Léna',
];

// Villes crédibles pour la clientèle Plume Astrale
const CITIES = [
  'Paris', 'Lyon', 'Bordeaux', 'Marseille', 'Nantes', 'Genève',
  'Bruxelles', 'Montréal', 'Nice', 'Toulouse', 'Lausanne', 'Rennes',
  'Strasbourg', 'Aix-en-Provence', 'Annecy', 'Lisbonne', 'Barcelone',
];

// Produits (label lisible + label court pour compteur)
const PRODUCTS = [
  { label: 'son analyse Astrocartographie', short: 'Astrocarto' },
  { label: 'son Arbre de Vie Kabbalistique', short: 'Kabbale' },
  { label: 'son Pack Karmique complet', short: 'Pack Karmique' },
  { label: 'son analyse Karma & Destin', short: 'Karma & Destin' },
  { label: 'sa fenêtre de rencontre', short: 'Rencontres Ultime' },
];

const MINUTES_AGO = [2, 3, 4, 6, 8, 11, 14, 17, 22, 27, 34, 42];

// Génère une notif pseudo-aléatoire mais déterministe pour la journée
// (on part d'un seed jour + index pour ne pas donner l'impression d'aléatoire trop pur)
function makeNotif(seed) {
  const rnd = (mod) => (seed * 9301 + 49297) % 233280 % mod;
  const s = (i) => (seed + i * 977) % 233280;
  return {
    name: NAMES[s(1) % NAMES.length],
    city: CITIES[s(2) % CITIES.length],
    product: PRODUCTS[s(3) % PRODUCTS.length],
    minutes: MINUTES_AGO[rnd(MINUTES_AGO.length)],
  };
}

const DISMISS_KEY = 'plume_live_sales_dismissed_at';
const DISMISS_HOURS = 24;

// Chemins où le compteur ne doit JAMAIS s'afficher (distraction pendant checkout/admin)
// Match préfixe : '/admin' bloque aussi '/admin/xxx'
const HIDDEN_PATH_PREFIXES = [
  '/admin',
  '/paiement',            // page checkout Stripe
  '/quotidien',           // page personnelle rituel — bruit visuel
  '/mon-compte',
  '/tirage',              // pendant un tirage tarot
  '/tarot',               // pendant un tirage tarot
];

// Chemins qui contiennent ces segments (checkout/succes/attente) → masqué
const HIDDEN_PATH_INCLUDES = [
  '/succes',
  '/attente',
  '/checkout',
];

function isHiddenPath(pathname) {
  const p = (pathname || '').toLowerCase();
  if (HIDDEN_PATH_PREFIXES.some((prefix) => p === prefix || p.startsWith(prefix + '/'))) return true;
  if (HIDDEN_PATH_INCLUDES.some((seg) => p.includes(seg))) return true;
  return false;
}

const LiveSalesCounter = ({ delay = 8000, interval = 12000 }) => {
  const location = useLocation();
  const hideOnThisPage = isHiddenPath(location.pathname);
  const [visible, setVisible] = useState(false);
  const [notif, setNotif] = useState(null);
  const [dismissed, setDismissed] = useState(false);
  const [tick, setTick] = useState(0);

  // Vérifie si l'utilisatrice a fermé le widget récemment
  useEffect(() => {
    try {
      const raw = localStorage.getItem(DISMISS_KEY);
      if (raw) {
        const ago = (Date.now() - parseInt(raw, 10)) / (1000 * 60 * 60);
        if (ago < DISMISS_HOURS) {
          setDismissed(true);
          return;
        }
      }
    } catch (_) { /* localStorage non dispo — on continue */ }
  }, []);

  // Prépare la première notif après le délai
  useEffect(() => {
    if (dismissed || hideOnThisPage) return;
    const seed = Math.floor(Date.now() / 60000); // change toutes les minutes
    setNotif(makeNotif(seed + tick));
    const showT = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(showT);
  }, [dismissed, delay, tick, hideOnThisPage]);

  // Cache immédiatement si on navigue vers une page interdite
  useEffect(() => {
    if (hideOnThisPage) setVisible(false);
  }, [hideOnThisPage]);

  // Rotation des notifs
  useEffect(() => {
    if (dismissed || hideOnThisPage) return;
    const rot = setInterval(() => {
      setVisible(false);
      setTimeout(() => {
        setTick((t) => t + 1);
        setVisible(true);
      }, 400);
    }, interval);
    return () => clearInterval(rot);
  }, [dismissed, interval, hideOnThisPage]);

  const handleDismiss = () => {
    setVisible(false);
    setDismissed(true);
    try {
      localStorage.setItem(DISMISS_KEY, String(Date.now()));
    } catch (_) { /* ignore */ }
  };

  if (dismissed || hideOnThisPage || !notif) return null;

  return (
    <>
      <div
        data-testid="live-sales-counter"
        className={`lsc-container ${visible ? 'lsc-visible' : ''}`}
        role="status"
        aria-live="polite"
      >
        <div className="lsc-inner">
          <div className="lsc-icon" aria-hidden="true">
            <Sparkles className="w-4 h-4" strokeWidth={1.5} />
          </div>
          <div className="lsc-text">
            <div className="lsc-line1">
              <strong>{notif.name}</strong>
              <span className="lsc-city"> · {notif.city}</span>
            </div>
            <div className="lsc-line2">
              vient de recevoir {notif.product.label}
            </div>
            <div className="lsc-line3">
              ✦ il y a {notif.minutes} min
            </div>
          </div>
          <button
            onClick={handleDismiss}
            className="lsc-close"
            aria-label="Fermer la notification"
            data-testid="live-sales-close"
          >
            <X className="w-3 h-3" strokeWidth={1.5} />
          </button>
        </div>
      </div>

      <style>{`
        .lsc-container {
          position: fixed;
          left: 20px;
          bottom: 20px;
          z-index: 45;
          max-width: 320px;
          transform: translateY(20px);
          opacity: 0;
          pointer-events: none;
          transition:
            transform 0.55s cubic-bezier(0.22, 1, 0.36, 1),
            opacity 0.55s ease;
        }
        .lsc-visible {
          transform: translateY(0);
          opacity: 1;
          pointer-events: auto;
        }
        .lsc-inner {
          position: relative;
          display: flex;
          gap: 12px;
          padding: 12px 34px 12px 14px;
          background:
            linear-gradient(160deg, rgba(26,18,48,0.94) 0%, rgba(14,10,30,0.94) 100%);
          backdrop-filter: blur(14px);
          -webkit-backdrop-filter: blur(14px);
          border: 1px solid rgba(212,175,55,0.35);
          border-radius: 12px;
          box-shadow:
            0 20px 40px -12px rgba(0,0,0,0.5),
            inset 0 1px 0 rgba(212,175,55,0.08);
        }
        .lsc-icon {
          flex-shrink: 0;
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: radial-gradient(circle at 30% 30%, rgba(212,175,55,0.35), rgba(212,175,55,0.08));
          border: 1px solid rgba(212,175,55,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          color: #D4AF37;
        }
        .lsc-text {
          flex: 1;
          min-width: 0;
          font-family: 'Cormorant Garamond', serif;
          color: #F5EEE0;
        }
        .lsc-line1 {
          font-size: 14px;
          line-height: 1.2;
        }
        .lsc-line1 strong {
          font-weight: 500;
          color: #F5EEE0;
        }
        .lsc-city {
          color: rgba(227,215,255,0.55);
          font-style: italic;
          font-size: 12px;
        }
        .lsc-line2 {
          font-size: 13px;
          font-style: italic;
          color: rgba(227,215,255,0.85);
          line-height: 1.35;
          margin-top: 2px;
        }
        .lsc-line3 {
          margin-top: 4px;
          font-family: 'Cinzel', serif;
          font-size: 9px;
          letter-spacing: 0.28em;
          color: rgba(212,175,55,0.72);
          text-transform: uppercase;
        }
        .lsc-close {
          position: absolute;
          top: 8px;
          right: 8px;
          width: 22px;
          height: 22px;
          border-radius: 50%;
          background: transparent;
          border: 1px solid rgba(212,175,55,0.15);
          color: rgba(245,238,224,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: color 0.2s, border-color 0.2s;
        }
        .lsc-close:hover {
          color: #D4AF37;
          border-color: rgba(212,175,55,0.5);
        }

        /* Mobile — plus discret, largeur pleine avec marge */
        @media (max-width: 640px) {
          .lsc-container {
            left: 12px;
            right: 12px;
            bottom: 12px;
            max-width: none;
          }
          .lsc-line1 { font-size: 13px; }
          .lsc-line2 { font-size: 12px; }
        }
      `}</style>
    </>
  );
};

export default LiveSalesCounter;
