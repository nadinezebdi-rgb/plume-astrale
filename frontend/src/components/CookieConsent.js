import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Cookie, Shield, BarChart3, Target, ChevronDown } from 'lucide-react';
import { getConsent, setConsent } from '@/lib/analytics';

/**
 * Bandeau RGPD BLOQUANT — modale plein-écran avec overlay opaque.
 * L'utilisateur doit choisir avant d'accéder au site (obligation Meta App review + RGPD strict).
 *
 * 3 CTAs : Tout accepter · Tout refuser · Personnaliser (granularité fine)
 * Persistance localStorage via `pa_consent_v1` (getConsent/setConsent).
 * Tant qu'aucun choix n'est fait : aucun script tiers ne se charge (voir lib/analytics.js).
 *
 * Design Nocturne Éditorial : fond navy + doré, Playfair pour le titre.
 * Réouvrable via lien "Gérer les cookies" (custom event `open-cookie-preferences`).
 */
export default function CookieConsent() {
  const [visible, setVisible] = useState(false);
  const [customOpen, setCustomOpen] = useState(false);
  const [prefs, setPrefs] = useState({ analytics: false, advertising: false });

  // Bloque le scroll du body tant que la modale est visible
  useEffect(() => {
    if (!visible || typeof document === 'undefined') return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = prev; };
  }, [visible]);

  useEffect(() => {
    if (getConsent() === null) setVisible(true);
    // Écoute un event global pour rouvrir la modale (footer "Gérer les cookies")
    const reopen = () => {
      setCustomOpen(false);
      setPrefs({ analytics: false, advertising: false });
      setVisible(true);
    };
    window.addEventListener('open-cookie-preferences', reopen);
    return () => window.removeEventListener('open-cookie-preferences', reopen);
  }, []);

  const finalize = useCallback((choice) => {
    // choice = 'accepted' (tout) | 'refused' (rien) | 'custom' (selon prefs)
    if (choice === 'accepted') {
      setConsent('accepted');
    } else if (choice === 'refused') {
      setConsent('refused');
    } else {
      // Mode custom : accepted uniquement si au moins advertising OU analytics est vrai
      setConsent(prefs.analytics || prefs.advertising ? 'accepted' : 'refused');
      try {
        localStorage.setItem('pa_consent_prefs_v1', JSON.stringify(prefs));
      } catch (_e) { /* silent */ }
    }
    setVisible(false);
  }, [prefs]);

  if (!visible) return null;

  return (
    <>
      <style>{`
        .cc-overlay {
          position: fixed; inset: 0;
          background: rgba(11, 15, 30, 0.82);
          backdrop-filter: blur(6px);
          -webkit-backdrop-filter: blur(6px);
          z-index: 99998;
          display: flex; align-items: center; justify-content: center;
          padding: 20px;
          animation: cc-fade-in 260ms ease-out;
        }
        @keyframes cc-fade-in { from { opacity: 0 } to { opacity: 1 } }
        @keyframes cc-slide-up {
          from { transform: translateY(24px) scale(0.98); opacity: 0 }
          to { transform: translateY(0) scale(1); opacity: 1 }
        }
        .cc-modal {
          position: relative;
          max-width: 560px; width: 100%;
          background: linear-gradient(180deg, #F7F5F0 0%, #FFFFFF 100%);
          border: 1px solid #E7E1D4;
          border-radius: 16px;
          box-shadow: 0 40px 80px rgba(11, 15, 30, 0.45),
                      0 0 0 1px rgba(201, 162, 75, 0.10);
          padding: 32px 32px 24px;
          font-family: 'Inter', -apple-system, sans-serif;
          animation: cc-slide-up 380ms cubic-bezier(0.16, 1, 0.3, 1);
          max-height: 90vh;
          overflow-y: auto;
        }
        .cc-eyebrow {
          display: inline-flex; align-items: center; gap: 8px;
          font-size: 11px; letter-spacing: 0.22em;
          text-transform: uppercase; color: #C9A24B;
          font-weight: 600;
          margin-bottom: 14px;
        }
        .cc-title {
          font-family: 'Playfair Display', Georgia, serif;
          font-size: 26px; line-height: 1.2;
          color: #0F1A3C; font-weight: 500;
          margin: 0 0 12px 0;
        }
        .cc-body {
          font-size: 14.5px; line-height: 1.6;
          color: #3A3A3A;
          margin: 0 0 20px 0;
        }
        .cc-body a { color: #C9A24B; text-decoration: underline; text-underline-offset: 3px; font-weight: 500; }
        .cc-actions {
          display: flex; gap: 10px; flex-wrap: wrap;
          margin-top: 8px;
        }
        .cc-btn {
          flex: 1 1 auto; min-width: 140px;
          font-size: 12px; letter-spacing: 0.10em;
          text-transform: uppercase; font-weight: 600;
          padding: 12px 18px;
          border-radius: 8px; border: none;
          cursor: pointer;
          transition: all 220ms cubic-bezier(0.16, 1, 0.3, 1);
          display: inline-flex; align-items: center; justify-content: center;
        }
        .cc-btn-primary {
          background: #C9A24B; color: #0F1A3C;
        }
        .cc-btn-primary:hover { background: #d6b262; transform: translateY(-1px); box-shadow: 0 6px 16px rgba(201, 162, 75, 0.25); }
        .cc-btn-secondary {
          background: transparent; color: #0F1A3C;
          border: 1px solid #D6CFC0;
        }
        .cc-btn-secondary:hover { background: #F0EDE3; border-color: #C9A24B; }
        .cc-btn-tertiary {
          background: transparent; color: #6C6C6C;
          padding: 10px 14px; font-size: 12px; text-transform: none; letter-spacing: 0;
          font-weight: 500; text-decoration: underline; text-underline-offset: 3px;
          border-radius: 4px;
        }
        .cc-btn-tertiary:hover { color: #0F1A3C; }
        .cc-panel {
          margin-top: 20px; padding-top: 20px;
          border-top: 1px solid #E7E1D4;
        }
        .cc-panel h4 {
          font-family: 'Inter', sans-serif;
          font-size: 11px; letter-spacing: 0.18em;
          text-transform: uppercase; color: #C9A24B;
          margin: 0 0 12px; font-weight: 600;
        }
        .cc-cat {
          display: flex; align-items: flex-start; gap: 14px;
          padding: 14px 0; border-bottom: 1px solid #F0EDE3;
        }
        .cc-cat:last-child { border-bottom: none; }
        .cc-cat-icon {
          flex-shrink: 0; width: 36px; height: 36px;
          background: #F7F5F0; border-radius: 8px;
          display: flex; align-items: center; justify-content: center;
          color: #C9A24B;
        }
        .cc-cat-info { flex: 1; }
        .cc-cat-name {
          font-size: 14px; font-weight: 600;
          color: #0F1A3C; margin: 0 0 3px;
          font-family: 'Playfair Display', Georgia, serif;
        }
        .cc-cat-desc {
          font-size: 12.5px; color: #6C6C6C;
          line-height: 1.5; margin: 0;
        }
        .cc-switch {
          position: relative; flex-shrink: 0;
          width: 40px; height: 22px;
          border-radius: 12px;
          background: #D6CFC0;
          cursor: pointer;
          transition: background 220ms ease;
          border: none;
          padding: 0;
        }
        .cc-switch::after {
          content: '';
          position: absolute; top: 3px; left: 3px;
          width: 16px; height: 16px;
          background: #FFFFFF; border-radius: 50%;
          transition: transform 220ms cubic-bezier(0.16, 1, 0.3, 1);
          box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        }
        .cc-switch.on { background: #C9A24B; }
        .cc-switch.on::after { transform: translateX(18px); }
        .cc-switch.locked {
          background: #C9A24B;
          opacity: 0.55; cursor: not-allowed;
        }
        .cc-switch.locked::after { transform: translateX(18px); }
        .cc-mode-toggle {
          background: transparent; border: none; cursor: pointer;
          font-size: 12.5px; color: #6C6C6C;
          display: inline-flex; align-items: center; gap: 4px;
          padding: 6px 0; margin-top: 6px;
          text-decoration: underline; text-underline-offset: 3px;
          font-family: 'Inter', sans-serif;
        }
        .cc-mode-toggle:hover { color: #0F1A3C; }
        .cc-mode-toggle .lucide { transition: transform 220ms ease; }
        .cc-mode-toggle.open .lucide { transform: rotate(180deg); }
        @media (max-width: 520px) {
          .cc-modal { padding: 24px 20px 20px; }
          .cc-title { font-size: 22px; }
          .cc-actions { flex-direction: column; }
          .cc-btn { min-width: unset; width: 100%; }
        }
      `}</style>
      <div
        className="cc-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="cc-title"
        aria-describedby="cc-body"
        data-testid="cookie-consent-overlay"
      >
        <div className="cc-modal" data-testid="cookie-consent">
          <span className="cc-eyebrow">
            <Cookie size={13} strokeWidth={2} /> Vos préférences
          </span>
          <h2 id="cc-title" className="cc-title">
            Un instant avant d&apos;entrer <em style={{ fontStyle: 'italic', color: '#C9A24B' }}>chez nous</em>
          </h2>
          <p id="cc-body" className="cc-body">
            Plume Astrale utilise des cookies pour faire fonctionner le site, mesurer son audience et améliorer nos publicités.
            {' '}Vous choisissez ce que vous acceptez — vos données de naissance ne sont <strong>jamais</strong> transmises à des tiers publicitaires.
            {' '}
            <Link to="/confidentialite" data-testid="cookie-privacy-link">En savoir plus</Link>.
          </p>

          <div className="cc-actions">
            <button
              type="button"
              className="cc-btn cc-btn-secondary"
              onClick={() => finalize('refused')}
              data-testid="cookie-refuse"
            >
              Tout refuser
            </button>
            <button
              type="button"
              className="cc-btn cc-btn-primary"
              onClick={() => finalize('accepted')}
              data-testid="cookie-accept"
            >
              Tout accepter
            </button>
          </div>

          <button
            type="button"
            className={`cc-mode-toggle ${customOpen ? 'open' : ''}`}
            onClick={() => setCustomOpen((v) => !v)}
            aria-expanded={customOpen}
            data-testid="cookie-customize-toggle"
          >
            Personnaliser mes choix <ChevronDown size={14} strokeWidth={1.8} />
          </button>

          {customOpen && (
            <div className="cc-panel" data-testid="cookie-custom-panel">
              <h4>Catégories de cookies</h4>

              <div className="cc-cat">
                <div className="cc-cat-icon"><Shield size={18} strokeWidth={1.6} /></div>
                <div className="cc-cat-info">
                  <p className="cc-cat-name">Cookies essentiels</p>
                  <p className="cc-cat-desc">
                    Indispensables au fonctionnement du site (session, panier, sécurité). Toujours actifs.
                  </p>
                </div>
                <button className="cc-switch on locked" aria-label="Toujours actifs" disabled />
              </div>

              <div className="cc-cat">
                <div className="cc-cat-icon"><BarChart3 size={18} strokeWidth={1.6} /></div>
                <div className="cc-cat-info">
                  <p className="cc-cat-name">Mesure d&apos;audience</p>
                  <p className="cc-cat-desc">
                    Statistiques anonymisées de visite pour améliorer nos pages (GA4).
                  </p>
                </div>
                <button
                  type="button"
                  className={`cc-switch ${prefs.analytics ? 'on' : ''}`}
                  onClick={() => setPrefs((p) => ({ ...p, analytics: !p.analytics }))}
                  aria-pressed={prefs.analytics}
                  aria-label="Mesure d'audience"
                  data-testid="cookie-toggle-analytics"
                />
              </div>

              <div className="cc-cat">
                <div className="cc-cat-icon"><Target size={18} strokeWidth={1.6} /></div>
                <div className="cc-cat-info">
                  <p className="cc-cat-name">Publicité personnalisée</p>
                  <p className="cc-cat-desc">
                    Meta Pixel (Facebook, Instagram) pour mesurer nos publicités. Données email hashées SHA-256.
                  </p>
                </div>
                <button
                  type="button"
                  className={`cc-switch ${prefs.advertising ? 'on' : ''}`}
                  onClick={() => setPrefs((p) => ({ ...p, advertising: !p.advertising }))}
                  aria-pressed={prefs.advertising}
                  aria-label="Publicité personnalisée"
                  data-testid="cookie-toggle-advertising"
                />
              </div>

              <div className="cc-actions" style={{ marginTop: 20 }}>
                <button
                  type="button"
                  className="cc-btn cc-btn-primary"
                  onClick={() => finalize('custom')}
                  data-testid="cookie-save-custom"
                >
                  Valider mes choix
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
