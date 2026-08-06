import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Send, Mail, Instagram, CheckCircle2, AlertCircle } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * /contact — Page contact charte v3.
 * Formulaire propre + honeypot anti-bot + envoi via /api/contact.
 * Contient également coordonnées directes (email, Instagram).
 */
export default function Contact() {
  const [form, setForm] = useState({
    name: '', email: '', subject: '', message: '', honeypot: '',
  });
  const [status, setStatus] = useState({ state: 'idle', message: '' });

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    if (status.state === 'loading') return;
    setStatus({ state: 'loading', message: '' });
    try {
      const r = await fetch(`${API}/api/contact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await r.json().catch(() => ({}));
      if (!r.ok) {
        setStatus({ state: 'error', message: data.detail || 'Une erreur est survenue. Merci de réessayer dans un instant.' });
        return;
      }
      setStatus({ state: 'success', message: data.message || 'Ton message est parti. Soléna te répond sous 24-48h.' });
      setForm({ name: '', email: '', subject: '', message: '', honeypot: '' });
    } catch {
      setStatus({ state: 'error', message: "Impossible de contacter le serveur. Vérifie ta connexion." });
    }
  };

  return (
    <PsPageShell background="light">
      <section className="ps-section ps-section-light" data-testid="contact-page">
        <div className="ps-container">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 64 }} className="ps-contact-grid">
            {/* Colonne texte */}
            <div>
              <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Écris à Soléna</p>
              <h1 className="ps-h1" style={{ color: '#0F1A3C', marginBottom: 24 }}>
                Une question, <span className="ps-italic">un mot ?</span>
              </h1>
              <p className="ps-body" style={{ color: '#232323', marginBottom: 32 }}>
                Un doute avant commande, une précision sur ta lecture, un retour après réception —
                écris-nous. Chaque message est lu par Soléna en personne. Réponse en 24 à 48h,
                du lundi au vendredi.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 32 }}>
                <ContactCoord icon={Mail} label="Par email" value="contact@plume-astrale.fr" href="mailto:contact@plume-astrale.fr" testid="contact-coord-email" />
                <ContactCoord icon={Instagram} label="Sur Instagram" value="@plume.astrale" href="https://instagram.com/plume.astrale" external testid="contact-coord-insta" />
              </div>

              <div style={{
                padding: 24,
                background: '#fff',
                border: '1px solid #E3E1DC',
                borderRadius: 12,
              }}>
                <p className="ps-caption" style={{ marginBottom: 12, fontWeight: 500, color: '#0F1A3C' }}>
                  Un souci technique urgent ?
                </p>
                <p className="ps-caption" style={{ margin: 0 }}>
                  Précise ton numéro de commande dans le sujet (« #ORD-xxxx ») —
                  on retrouve ton dossier immédiatement.
                </p>
              </div>
            </div>

            {/* Colonne formulaire */}
            <form onSubmit={onSubmit} data-testid="contact-form" style={{
              display: 'flex', flexDirection: 'column', gap: 20,
              background: '#fff',
              border: '1px solid #E3E1DC',
              borderRadius: 12,
              padding: 32,
            }}>
              <div className="ps-field">
                <label className="ps-label" htmlFor="c-name">Ton prénom</label>
                <input id="c-name" name="name" type="text" required autoComplete="given-name"
                  data-testid="contact-name"
                  value={form.name} onChange={onChange}
                  placeholder="Comment tu t'appelles ?"
                  className="ps-input" />
              </div>

              <div className="ps-field">
                <label className="ps-label" htmlFor="c-email">Ton email</label>
                <input id="c-email" name="email" type="email" required autoComplete="email"
                  data-testid="contact-email"
                  value={form.email} onChange={onChange}
                  placeholder="pour te répondre"
                  className="ps-input" />
              </div>

              <div className="ps-field">
                <label className="ps-label" htmlFor="c-subject">Sujet</label>
                <input id="c-subject" name="subject" type="text" required
                  data-testid="contact-subject"
                  value={form.subject} onChange={onChange}
                  placeholder="En un mot, ta demande"
                  minLength={2} maxLength={200}
                  className="ps-input" />
              </div>

              <div className="ps-field">
                <label className="ps-label" htmlFor="c-message">Ton message</label>
                <textarea id="c-message" name="message" required
                  data-testid="contact-message"
                  value={form.message} onChange={onChange}
                  placeholder="Prends le temps qu'il faut. On lit tout."
                  minLength={10} maxLength={4000} rows={7}
                  className="ps-input"
                  style={{ resize: 'vertical', minHeight: 140, fontFamily: 'Inter, sans-serif' }} />
                <span className="ps-caption" style={{ textAlign: 'right' }}>
                  {form.message.length}/4000
                </span>
              </div>

              {/* Honeypot anti-bot */}
              <input type="text" name="honeypot" tabIndex={-1} autoComplete="off"
                value={form.honeypot} onChange={onChange}
                style={{ position: 'absolute', left: -9999, width: 1, height: 1, opacity: 0 }}
                aria-hidden="true" />

              {status.state === 'success' && (
                <div style={statusBox('success')} data-testid="contact-status-success">
                  <CheckCircle2 style={{ width: 18, height: 18, flexShrink: 0 }} strokeWidth={2} />
                  <span>{status.message}</span>
                </div>
              )}
              {status.state === 'error' && (
                <div style={statusBox('error')} data-testid="contact-status-error">
                  <AlertCircle style={{ width: 18, height: 18, flexShrink: 0 }} strokeWidth={2} />
                  <span>{status.message}</span>
                </div>
              )}

              <button type="submit"
                disabled={status.state === 'loading'}
                className="ps-btn ps-btn-primary"
                data-testid="contact-submit"
                style={{
                  justifyContent: 'center',
                  marginTop: 4,
                  opacity: status.state === 'loading' ? 0.7 : 1,
                  cursor: status.state === 'loading' ? 'wait' : 'pointer',
                }}>
                {status.state === 'loading' ? 'Envoi en cours…' : (
                  <>
                    Envoyer mon message
                    <Send style={{ width: 16, height: 16 }} strokeWidth={2} />
                  </>
                )}
              </button>

              <p className="ps-caption" style={{ textAlign: 'center', marginTop: 4 }}>
                Vos données sont utilisées uniquement pour te répondre.
                {' '}<Link to="/mentions-legales" style={{ color: '#C9A24B', textDecoration: 'underline' }}>
                  RGPD
                </Link>.
              </p>
            </form>
          </div>

          <style>{`
            @media (min-width: 900px) {
              .ps-contact-grid { grid-template-columns: 1fr 1.1fr !important; }
            }
          `}</style>
        </div>
      </section>
    </PsPageShell>
  );
}

function ContactCoord({ icon: Icon, label, value, href, external, testid }) {
  const commonStyle = {
    display: 'flex', alignItems: 'center', gap: 14,
    padding: '16px 20px',
    background: '#fff',
    border: '1px solid #E3E1DC',
    borderRadius: 12,
    textDecoration: 'none',
    color: '#232323',
    transition: 'border-color 200ms ease, transform 200ms ease',
  };
  return (
    <a href={href}
      target={external ? '_blank' : undefined}
      rel={external ? 'noopener noreferrer' : undefined}
      data-testid={testid}
      style={commonStyle}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = '#C9A24B';
        e.currentTarget.style.transform = 'translateY(-1px)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = '#E3E1DC';
        e.currentTarget.style.transform = 'translateY(0)';
      }}>
      <div style={{
        width: 40, height: 40, borderRadius: 10,
        background: '#F7F5F0',
        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0,
      }}>
        <Icon style={{ width: 18, height: 18, color: '#C9A24B' }} strokeWidth={1.6} />
      </div>
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <span style={{
          fontFamily: 'Inter, sans-serif', fontSize: 12,
          color: '#6B7280', letterSpacing: '0.06em',
        }}>{label}</span>
        <span style={{
          fontFamily: 'Inter, sans-serif', fontSize: 15,
          fontWeight: 500, color: '#0F1A3C',
        }}>{value}</span>
      </div>
    </a>
  );
}

function statusBox(kind) {
  const colors = kind === 'success'
    ? { bg: '#EDF7F1', border: '#3C7A5A', color: '#1F4A34' }
    : { bg: '#FBEEEA', border: '#B4442E', color: '#6E2A1B' };
  return {
    display: 'flex', alignItems: 'center', gap: 10,
    padding: '12px 16px',
    background: colors.bg,
    border: `1px solid ${colors.border}`,
    borderRadius: 10,
    color: colors.color,
    fontFamily: 'Inter, sans-serif',
    fontSize: 14, lineHeight: 1.5,
  };
}
