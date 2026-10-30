import {useEffect, useState, useCallback} from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Cookie, Shield, BarChart3, Target, ChevronDown } from 'lucide-react';
import { getConsent, setConsent } from '@/lib/analytics';

/**
 * Bandeau RGPD BOTTOM — bannière ancrée bas, sans overlay bloquant.
 * La page reste visible et scrollable derrière. 3 CTAs : Accepter · Refuser · Personnaliser.
 *
 * Persistance localStorage via `pa_consent_v1` (getConsent/setConsent).
 * Tant qu'aucun choix n'est fait : aucun script tiers ne se charge (lib/analytics.js).
 *
 * Design Nocturne Éditorial : fond navy + liseré doré, Playfair pour le lede.
 * Réouvrable via event global `open-cookie-preferences` (lien footer "Gérer les cookies").
 */
export default function CookieConsent() {
  const [visible, setVisible] = useState(false);
  const [customOpen, setCustomOpen] = useState(false);
  const [prefs, setPrefs] = useState({ analytics: false, advertising: false });

  useEffect(() => {
    if (getConsent() === null) setVisible(true);
    const reopen = () => {
      setCustomOpen(false);
      setPrefs({ analytics: false, advertising: false });
      setVisible(true);
    };
    window.addEventListener('open-cookie-preferences', reopen);
    return () => window.removeEventListener('open-cookie-preferences', reopen);
  }, []);

  const finalize = useCallback((choice) => {
    const finalPrefs = {
      analytics: choice === 'accepted' ? true : choice === 'refused' ? false : prefs.analytics,
      advertising: choice === 'accepted' ? true : choice === 'refused' ? false : prefs.advertising,
    };
    try {
      const API = process.env.REACT_APP_BACKEND_URL || '';
      fetch(`${API}/api/analytics/cookie-consent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          choice,
          analytics: finalPrefs.analytics,
          advertising: finalPrefs.advertising,
          source: 'bottom-banner',
        }),
        keepalive: true,
      }).catch(() => { /* silent */ });
    } catch (_e) { /* silent */ }

    if (choice === 'accepted') {
      setConsent('accepted');
    } else if (choice === 'refused') {
      setConsent('refused');
    } else {
      setConsent(prefs.analytics || prefs.advertising ? 'accepted' : 'refused');
      try {
        localStorage.setItem('pa_consent_prefs_v1', JSON.stringify(prefs));
      } catch (_e) { /* silent */ }
    }
    setVisible(false);
  }, [prefs]);

  const location = useLocation();
  const isImmersive = (p) => p === '/experience' || p.startsWith('/experience/');
  if (isImmersive(location.pathname)) {
    return null;
  }

  if (!visible) return null;

  return (
    <>
      <style>{`
        @keyframes cc-slide-in {
          from { transform: translateY(100%); opacity: 0 }
          to { transform: translateY(0); opacity: 1 }
        }
        @keyframes cc-fade-in { from { opacity: 0 } to { opacity: 1 } }

        .cc-bar {
          position: fixed; left: 0; right: 0; bottom: 0;
          z-index: 99998;
          background: linear-gradient(180deg, rgba(15,26,60,0.97) 0%, rgba(10,18,44,0.98) 100%);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border-top: 1px solid rgba(201, 162, 75, 0.35);
          box-shadow: 0 -20px 60px rgba(0, 0, 0, 0.35);
          color: #F7F5F0;
          font-family: 'Inter', -apple-system, sans-serif;
          animation: cc-slide-in 420ms cubic-bezier(0.16, 1, 0.3, 1);
          max-height: 85vh;
          overflow-y: auto;
        }
        .cc-bar::before {
          content: '';
          position: absolute; top: 0; left: 50%;
          transform: translateX(-50%);
          width: 120px; height: 1px;
          background: linear-gradient(90deg, transparent, #C9A24B, transparent);
        }
        .cc-bar-inner {
          max-width: 1200px;
          margin: 0 auto;
          padding: 22px 28px;
          display: flex;
          align-items: center;
          gap: 32px;
        }
        .cc-text {
          flex: 1 1 auto;
          min-width: 0;
        }
        .cc-eyebrow {
          display: inline-flex; align-items: center; gap: 7px;
          font-size: 10.5px; letter-spacing: 0.22em;
          text-transform: uppercase; color: #C9A24B;
          font-weight: 600;
          margin-bottom: 6px;
        }
        .cc-headline {
          font-family: 'Playfair Display', Georgia, serif;
          font-size: 17px; line-height: 1.35;
          color: #FFFFFF; font-weight: 500;
          margin: 0 0 4px;
        }
        .cc-headline em { font-style: italic; color: #C9A24B; }
        .cc-body {
          font-size: 13px; line-height: 1.55;
          color: rgba(247, 245, 240, 0.72);
          margin: 0;
          max-width: 760px;
        }
        .cc-body a {
          color: #C9A24B;
          text-decoration: underline;
          text-underline-offset: 2px;
          font-weight: 500;
        }
        .cc-body a:hover { color: #d6b262; }

        .cc-actions {
          display: flex;
          gap: 10px;
          align-items: center;
          flex-shrink: 0;
        }
        .cc-btn {
          font-family: 'Inter', sans-serif;
          font-size: 11.5px;
          letter-spacing: 0.12em;
          text-transform: uppercase;
          font-weight: 600;
          padding: 11px 20px;
          border-radius: 999px;
          border: none;
          cursor: pointer;
          transition: all 220ms cubic-bezier(0.16, 1, 0.3, 1);
          white-space: nowrap;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-width: 112px;
        }
        .cc-btn-accept {
          background: #C9A24B;
          color: #0F1A3C;
          box-shadow: 0 4px 14px rgba(201, 162, 75, 0.28);
        }
        .cc-btn-accept:hover {
          background: #d6b262;
          transform: translateY(-1px);
          box-shadow: 0 8px 20px rgba(201, 162, 75, 0.40);
        }
        .cc-btn-refuse {
          background: transparent;
          color: #F7F5F0;
          border: 1px solid rgba(247, 245, 240, 0.35);
        }
        .cc-btn-refuse:hover {
          background: rgba(247, 245, 240, 0.08);
          border-color: rgba(247, 245, 240, 0.6);
        }
        .cc-btn-custom {
          background: transparent;
          color: rgba(247, 245, 240, 0.7);
          padding: 11px 10px;
          font-size: 11.5px;
          letter-spacing: 0;
          text-transform: none;
          font-weight: 500;
          text-decoration: underline;
          text-underline-offset: 3px;
          min-width: 0;
          border-radius: 6px;
        }
        .cc-btn-custom:hover { color: #FFFFFF; }
        .cc-btn-custom .lucide { transition: transform 220ms ease; margin-left: 4px; }
        .cc-btn-custom.open .lucide { transform: rotate(180deg); }

        .cc-panel {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 28px 22px;
          animation: cc-fade-in 240ms ease-out;
        }
        .cc-panel-grid {
          padding: 18px 20px;
          background: rgba(247, 245, 240, 0.04);
          border: 1px solid rgba(201, 162, 75, 0.18);
          border-radius: 12px;
        }
        .cc-panel h4 {
          font-size: 10.5px; letter-spacing: 0.22em;
          text-transform: uppercase; color: #C9A24B;
          margin: 0 0 12px; font-weight: 600;
        }
        .cc-cat {
          display: flex; align-items: center; gap: 14px;
          padding: 12px 0;
          border-bottom: 1px solid rgba(247, 245, 240, 0.06);
        }
        .cc-cat:last-child { border-bottom: none; }
        .cc-cat-icon {
          flex-shrink: 0; width: 32px; height: 32px;
          background: rgba(201, 162, 75, 0.12);
          border-radius: 8px;
          display: flex; align-items: center; justify-content: center;
          color: #C9A24B;
        }
        .cc-cat-info { flex: 1; }
        .cc-cat-name {
          font-size: 13.5px; font-weight: 600;
          color: #F7F5F0; margin: 0 0 2px;
          font-family: 'Playfair Display', Georgia, serif;
        }
        .cc-cat-desc {
          font-size: 11.5px;
          color: rgba(247, 245, 240, 0.6);
          line-height: 1.45;
          margin: 0;
        }
        .cc-switch {
          position: relative; flex-shrink: 0;
          width: 38px; height: 22px;
          border-radius: 12px;
          background: rgba(247, 245, 240, 0.18);
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
          box-shadow: 0 2px 4px rgba(0,0,0,0.25);
        }
        .cc-switch.on { background: #C9A24B; }
        .cc-switch.on::after { transform: translateX(16px); }
        .cc-switch.locked {
          background: #C9A24B;
          opacity: 0.55; cursor: not-allowed;
        }
        .cc-switch.locked::after { transform: translateX(16px); }

        .cc-panel-save {
          display: flex;
          justify-content: flex-end;
          margin-top: 16px;
        }

        /* ─── Tablet ─── */
        @media (max-width: 900px) {
          .cc-bar-inner { padding: 20px 22px; gap: 20px; }
          .cc-headline { font-size: 15.5px; }
          .cc-body { font-size: 12.5px; }
        }

        /* ─── Mobile ─── */
        @media (max-width: 680px) {
          .cc-bar-inner {
            flex-direction: column;
            align-items: stretch;
            padding: 18px 18px 16px;
            gap: 16px;
          }
          .cc-actions {
            flex-wrap: wrap;
            justify-content: stretch;
          }
          .cc-btn-accept, .cc-btn-refuse {
            flex: 1 1 calc(50% - 5px);
            min-width: 0;
            padding: 12px 10px;
          }
          .cc-btn-custom {
            flex: 1 1 100%;
            text-align: center;
            padding: 8px 10px 2px;
          }
          .cc-panel { padding: 0 18px 18px; }
        }
      `}</style>

      <div
        className="cc-bar"
        role="dialog"
        aria-labelledby="cc-headline"
        aria-describedby="cc-body"
        data-testid="cookie-consent-bar"
      >
        <div className="cc-bar-inner" data-testid="cookie-consent">
          <div className="cc-text">
            <span className="cc-eyebrow">
              <Cookie size={12} strokeWidth={2} /> Vos préférences
            </span>
            <p id="cc-headline" className="cc-headline">
              Un instant avant d&apos;entrer <em>chez nous</em>.
            </p>
            <p id="cc-body" className="cc-body">
              Nous utilisons des cookies pour faire fonctionner le site, mesurer l&apos;audience et affiner nos publicités.
              {' '}Vos données de naissance ne sont <strong>jamais</strong> transmises à des tiers.
              {' '}
              <Link to="/confidentialite" data-testid="cookie-privacy-link">En savoir plus</Link>.
            </p>
          </div>

          <div className="cc-actions">
            <button
              type="button"
              className="cc-btn cc-btn-refuse"
              onClick={() => finalize('refused')}
              data-testid="cookie-refuse"
            >
              Refuser
            </button>
            <button
              type="button"
              className="cc-btn cc-btn-accept"
              onClick={() => finalize('accepted')}
              data-testid="cookie-accept"
            >
              Accepter
            </button>
            <button
              type="button"
              className={`cc-btn cc-btn-custom ${customOpen ? 'open' : ''}`}
              onClick={() => setCustomOpen((v) => !v)}
              aria-expanded={customOpen}
              data-testid="cookie-customize-toggle"
            >
              Personnaliser <ChevronDown size={13} strokeWidth={1.8} />
            </button>
          </div>
        </div>

        {customOpen && (
          <div className="cc-panel" data-testid="cookie-custom-panel">
            <div className="cc-panel-grid">
              <h4>Catégories de cookies</h4>

              <div className="cc-cat">
                <div className="cc-cat-icon"><Shield size={16} strokeWidth={1.6} /></div>
                <div className="cc-cat-info">
                  <p className="cc-cat-name">Cookies essentiels</p>
                  <p className="cc-cat-desc">
                    Indispensables au site (session, panier, sécurité). Toujours actifs.
                  </p>
                </div>
                <button className="cc-switch on locked" aria-label="Toujours actifs" disabled />
              </div>

              <div className="cc-cat">
                <div className="cc-cat-icon"><BarChart3 size={16} strokeWidth={1.6} /></div>
                <div className="cc-cat-info">
                  <p className="cc-cat-name">Mesure d&apos;audience</p>
                  <p className="cc-cat-desc">
                    Statistiques anonymisées de visite (GA4) pour améliorer nos pages.
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
                <div className="cc-cat-icon"><Target size={16} strokeWidth={1.6} /></div>
                <div className="cc-cat-info">
                  <p className="cc-cat-name">Publicité personnalisée</p>
                  <p className="cc-cat-desc">
                    Meta Pixel (Facebook, Instagram). Email hashé SHA-256.
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

              <div className="cc-panel-save">
                <button
                  type="button"
                  className="cc-btn cc-btn-accept"
                  onClick={() => finalize('custom')}
                  data-testid="cookie-save-custom"
                >
                  Valider mes choix
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
