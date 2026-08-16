import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { ArrowRight, Check, Loader2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * VoyageKarmiqueSucces — Page de succès Nocturne (post-paiement).
 * Poll /api/voyage-karmique/status jusqu'à obtenir les deux liens PDF.
 */
export default function VoyageKarmiqueSucces() {
  const [params] = useSearchParams();
  const sessionId = params.get('session_id') || '';
  const [status, setStatus] = useState({ ready: false, kabbale: null, karma: null });
  const [error, setError] = useState('');
  const [attempts, setAttempts] = useState(0);

  useEffect(() => {
    if (!sessionId) { setError('Session introuvable.'); return; }
    let cancelled = false;

    async function poll() {
      try {
        const r = await fetch(`${API}/api/voyage-karmique/status?session_id=${sessionId}`);
        const d = await r.json();
        if (!r.ok) throw new Error(d?.detail || 'Statut indisponible.');
        if (cancelled) return;
        setStatus({
          ready: d.pdf_ready,
          kabbale: d.kabbale_pdf_url,
          karma: d.karma_pdf_url,
        });
        if (d.pdf_ready) return;
      } catch (e) {
        if (!cancelled) setError(e.message || 'Erreur');
      }
      setAttempts((a) => a + 1);
      if (!cancelled) setTimeout(poll, 3000);
    }
    poll();
    return () => { cancelled = true; };
  }, [sessionId]);

  if (error) {
    return (
      <section className="ne-section ne-section-night">
        <div className="ne-container" style={{ maxWidth: 640 }}>
          <div className="ne-overline" style={{ color: 'var(--ne-erreur)' }}>Une pause</div>
          <h1 className="ne-h1" style={{ marginTop: 24, color: 'var(--ne-celeste)' }}>Nous avons besoin d&rsquo;un instant.</h1>
          <p className="ne-lead" style={{ marginTop: 24, color: 'rgba(245,240,230,0.8)' }}>{error}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="ne-section ne-section-night" style={{ minHeight: '80vh', display: 'flex', alignItems: 'center' }} data-testid="voyage-succes">
      <div className="ne-container" style={{ maxWidth: 720 }}>
        {!status.ready ? (
          <div>
            <div className="ne-overline" data-testid="voyage-loading-overline">
              <Loader2 style={{ width: 12, height: 12, display: 'inline', marginRight: 6, verticalAlign: 'middle', animation: 'spin-slow 2s linear infinite' }} strokeWidth={2} />
              Nous composons vos deux livres
            </div>
            <h1 className="ne-h1" style={{ marginTop: 24, color: 'var(--ne-celeste)' }}>
              Un instant. <span className="ne-serif-italic" style={{ color: 'var(--ne-laiton)' }}>Vos pages s&rsquo;écrivent.</span>
            </h1>
            <hr className="ne-rule-short" style={{ marginTop: 32, marginBottom: 32 }} />
            <p className="ne-lead" style={{ color: 'rgba(245,240,230,0.8)' }}>
              L&rsquo;Arbre de Vie prend forme. La Lignée Karmique se déroule. Deux à cinq minutes,
              pas plus. Nous vous envoyons également les liens par email.
            </p>
            <p className="ne-caption" style={{ marginTop: 40, color: 'rgba(245,240,230,0.5)' }}>
              Vérification {attempts + 1}…
            </p>
          </div>
        ) : (
          <div data-testid="voyage-ready">
            <div className="ne-overline" style={{ color: 'var(--ne-succes)' }}>
              <Check style={{ width: 12, height: 12, display: 'inline', marginRight: 6, verticalAlign: 'middle' }} strokeWidth={2} />
              Vos deux livres sont prêts
            </div>
            <h1 className="ne-h1" style={{ marginTop: 24, color: 'var(--ne-celeste)' }}>
              Votre <span className="ne-serif-italic" style={{ color: 'var(--ne-laiton)' }}>voyage</span> commence.
            </h1>
            <hr className="ne-rule-short" style={{ marginTop: 32, marginBottom: 40 }} />

            <div style={{ display: 'grid', gap: 16 }}>
              {status.kabbale && (
                <a href={status.kabbale} target="_blank" rel="noopener noreferrer"
                  data-testid="voyage-download-kabbale"
                  style={{
                    display: 'block', padding: '24px 28px', background: 'var(--ne-astre)',
                    border: '1px solid rgba(184,147,90,0.35)', borderRadius: 2,
                    textDecoration: 'none',
                  }}>
                  <div className="ne-mono" style={{ fontSize: 10, letterSpacing: '0.28em', color: 'var(--ne-laiton)', marginBottom: 8, textTransform: 'uppercase' }}>Livre I</div>
                  <div style={{ fontFamily: 'var(--ne-serif)', fontSize: 24, color: 'var(--ne-celeste)', fontWeight: 400, marginBottom: 8 }}>
                    Arbre de Vie Kabbalistique
                  </div>
                  <div style={{ color: 'var(--ne-laiton)', fontFamily: 'var(--ne-sans)', fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                    Télécharger <ArrowRight style={{ width: 12, height: 12 }} strokeWidth={1.5} />
                  </div>
                </a>
              )}
              {status.karma && (
                <a href={status.karma} target="_blank" rel="noopener noreferrer"
                  data-testid="voyage-download-karma"
                  style={{
                    display: 'block', padding: '24px 28px', background: 'var(--ne-astre)',
                    border: '1px solid rgba(184,147,90,0.35)', borderRadius: 2,
                    textDecoration: 'none',
                  }}>
                  <div className="ne-mono" style={{ fontSize: 10, letterSpacing: '0.28em', color: 'var(--ne-laiton)', marginBottom: 8, textTransform: 'uppercase' }}>Livre II</div>
                  <div style={{ fontFamily: 'var(--ne-serif)', fontSize: 24, color: 'var(--ne-celeste)', fontWeight: 400, marginBottom: 8 }}>
                    Lignée Karmique & Destinée
                  </div>
                  <div style={{ color: 'var(--ne-laiton)', fontFamily: 'var(--ne-sans)', fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                    Télécharger <ArrowRight style={{ width: 12, height: 12 }} strokeWidth={1.5} />
                  </div>
                </a>
              )}
            </div>

            <div style={{ marginTop: 48, padding: 24, background: 'var(--ne-night)', borderLeft: '2px solid var(--ne-laiton)' }}>
              <p className="ne-serif-italic" style={{ color: 'rgba(245,240,230,0.85)', fontSize: 17, lineHeight: 1.55, margin: 0 }}>
                Prenez le temps. Une lecture, un thé, une soirée.
                <br />
                Ce voyage ne se parcourt pas &mdash; se contemple.
              </p>
              <div className="ne-signature" style={{ marginTop: 20, fontSize: 18 }}>&mdash;&nbsp;Soléna</div>
            </div>

            <div style={{ marginTop: 40 }}>
              <Link to="/" className="ne-btn-ghost" data-testid="voyage-home" style={{ color: 'var(--ne-celeste)' }}>
                Retour à Plume Astrale
              </Link>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
