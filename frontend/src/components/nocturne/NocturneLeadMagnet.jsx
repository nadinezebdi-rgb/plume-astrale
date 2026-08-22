import React, { useState } from 'react';
import { ArrowRight, Check, Loader2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * NocturneLeadMagnet — Formulaire éditorial 4 champs pour recevoir l'aperçu 5 pages.
 *
 * Design Nocturne : filet inférieur, labels overline, animation respiratoire.
 * POST /api/lead-magnet/generate → PDF envoyé par email + lien immédiat.
 */
export default function NocturneLeadMagnet() {
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [birthDate, setBirthDate] = useState('');
  const [birthPlace, setBirthPlace] = useState('');
  const [status, setStatus] = useState('idle'); // idle | loading | success | error
  const [pdfUrl, setPdfUrl] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email || !firstName || !birthDate) return;
    setStatus('loading');
    setErrorMsg('');
    try {
      const res = await fetch(`${API}/api/lead-magnet/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          first_name: firstName.trim(),
          birth_date: birthDate,
          birth_place: birthPlace.trim() || null,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setStatus('error');
        setErrorMsg(
          res.status === 429
            ? 'Vous avez déjà reçu un aperçu récemment. Regardez dans votre boîte email.'
            : (data?.detail?.message || data?.detail || 'Nous n\'avons pas pu générer votre aperçu.')
        );
        return;
      }
      setPdfUrl(data.pdf_url);
      setStatus('success');
    } catch (err) {
      setStatus('error');
      setErrorMsg('Un instant, la connexion s\'est interrompue. Réessayez dans quelques secondes.');
    }
  }

  if (status === 'success') {
    return (
      <section className="ne-section ne-section-paper" data-testid="lead-magnet-success">
        <div className="ne-container">
          <div style={{ maxWidth: 640 }}>
            <div className="ne-overline" style={{ color: 'var(--ne-succes)' }}>
              <Check style={{ width: 12, height: 12, display: 'inline', marginRight: 6, verticalAlign: 'middle' }} strokeWidth={2} />
              Votre aperçu est prêt
            </div>
            <h2 className="ne-h1" style={{ marginTop: 24, color: 'var(--ne-fusain)' }}>
              Merci. <span className="ne-serif-italic" style={{ color: 'var(--ne-vigne)' }}>Votre aperçu vous attend.</span>
            </h2>
            <hr className="ne-rule-short" style={{ marginTop: 32, marginBottom: 32 }} />
            <p className="ne-lead" style={{ color: 'rgba(10,10,15,0.75)', marginBottom: 40 }}>
              Cinq pages composées pour vous. Vous pouvez le télécharger immédiatement,
              ou attendre l&rsquo;email — les deux vous sont offerts.
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
              <a
                href={pdfUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="ne-btn ne-btn-primary"
                data-testid="lead-magnet-download"
              >
                Télécharger l&rsquo;aperçu
                <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={1.5} />
              </a>
              <a
                href="/theme-natal"
                className="ne-btn-ghost"
                data-testid="lead-magnet-continue"
              >
                Découvrir la lecture complète — 39€
              </a>
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="ne-section ne-section-paper" data-testid="lead-magnet-form">
      <div className="ne-container">
        <div style={{ maxWidth: 640 }}>
          <div className="ne-overline">Un cadeau, jamais une conversion</div>
          <h2 className="ne-h1" style={{ marginTop: 24, color: 'var(--ne-fusain)' }}>
            Recevez votre <span className="ne-serif-italic" style={{ color: 'var(--ne-vigne)' }}>aperçu Nocturne</span> — 5 pages, offert.
          </h2>
          <hr className="ne-rule-short" style={{ marginTop: 32, marginBottom: 32 }} />
          <p className="ne-lead" style={{ color: 'rgba(10,10,15,0.72)', marginBottom: 48 }}>
            Trois champs suffisent — votre prénom, votre date de naissance, votre email.
            Nous composons votre aperçu et vous l&rsquo;envoyons dans l&rsquo;instant.
          </p>

          <form onSubmit={handleSubmit} data-testid="lead-magnet-form-el">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 32 }}>
              <div className="ne-field">
                <label className="ne-label" htmlFor="lm-firstname">Prénom</label>
                <input
                  id="lm-firstname"
                  className="ne-input"
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="Votre prénom"
                  required
                  maxLength={80}
                  data-testid="lead-magnet-firstname"
                />
              </div>

              <div className="ne-field">
                <label className="ne-label" htmlFor="lm-birthdate">Date de naissance</label>
                <input
                  id="lm-birthdate"
                  className="ne-input"
                  type="date"
                  value={birthDate}
                  onChange={(e) => setBirthDate(e.target.value)}
                  required
                  data-testid="lead-magnet-birthdate"
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 32, marginTop: 0 }}>
              <div className="ne-field">
                <label className="ne-label" htmlFor="lm-place">Lieu de naissance <span style={{ opacity: 0.5, fontSize: 10 }}>(facultatif)</span></label>
                <input
                  id="lm-place"
                  className="ne-input"
                  type="text"
                  value={birthPlace}
                  onChange={(e) => setBirthPlace(e.target.value)}
                  placeholder="Ville, pays"
                  maxLength={120}
                  data-testid="lead-magnet-place"
                />
              </div>

              <div className="ne-field">
                <label className="ne-label" htmlFor="lm-email">Email</label>
                <input
                  id="lm-email"
                  className="ne-input"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="votre@email.fr"
                  required
                  data-testid="lead-magnet-email"
                />
              </div>
            </div>

            {status === 'error' && (
              <p
                data-testid="lead-magnet-error"
                style={{
                  marginTop: 24, fontFamily: 'var(--ne-sans)', fontSize: 14,
                  color: 'var(--ne-erreur)', fontStyle: 'italic',
                }}
              >
                {errorMsg}
              </p>
            )}

            <div style={{ marginTop: 48, display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'center' }}>
              <button
                type="submit"
                disabled={status === 'loading'}
                className="ne-btn ne-btn-primary"
                data-testid="lead-magnet-submit"
                style={status === 'loading' ? { opacity: 0.7, cursor: 'wait' } : undefined}
              >
                {status === 'loading' ? (
                  <>
                    <Loader2 style={{ width: 16, height: 16, animation: 'spin-slow 2s linear infinite' }} strokeWidth={1.5} />
                    Nous composons votre aperçu…
                  </>
                ) : (
                  <>
                    Recevoir mon aperçu
                    <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={1.5} />
                  </>
                )}
              </button>
              <p className="ne-caption" style={{ margin: 0, color: 'rgba(10,10,15,0.5)' }}>
                Aucune carte bancaire. Aucun engagement. Un cadeau.
              </p>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
}
