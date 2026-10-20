import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Sparkles, CheckCircle2, Loader2 } from 'lucide-react';
import { event as trackEvent } from '../lib/analytics';
import { trackABEvent } from '../lib/abTracking';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const INPUT_STYLE = {
  width: '100%',
  padding: '12px 14px',
  background: 'rgba(15,26,60,0.6)',
  border: '1px solid rgba(212,175,55,0.3)',
  borderRadius: 4,
  color: '#F5EEE0',
  fontSize: 14,
  fontFamily: 'Inter, sans-serif',
  boxSizing: 'border-box',
  outline: 'none',
};

const LABEL_STYLE = {
  display: 'block',
  fontFamily: '"Cinzel", serif',
  fontSize: 10,
  letterSpacing: '0.18em',
  textTransform: 'uppercase',
  color: 'rgba(212,175,55,0.85)',
  marginBottom: 6,
};

/**
 * SynastrieLeadMagnet — formulaire email qui déclenche l'envoi
 * d'un extrait synastrie 3 pages personnalisé (via /api/synastrie/free-extract).
 *
 * Props:
 *  - variant: 'section' (default) | 'modal' — adapte le padding/background pour s'intégrer dans une modal
 *  - onSuccess: callback optionnel (ex: fermer la modal avant redirection)
 */
export default function SynastrieLeadMagnet({ variant = 'section', onSuccess, copy, variantKey } = {}) {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [p1, setP1] = useState({ prenom: '', birth_date: '', birth_place: 'Paris, France' });
  const [p2, setP2] = useState({ prenom: '', birth_date: '', birth_place: 'Paris, France' });
  const [consent, setConsent] = useState(true);
  const [state, setState] = useState({ status: 'idle', message: '' });

  // Pré-remplir Personne 1 et l'email depuis localStorage.plume_astrale_data
  // si l'utilisateur a déjà saisi son profil ailleurs sur le site (home, composer…).
  React.useEffect(() => {
    try {
      const raw = localStorage.getItem('plume_astrale_data');
      if (!raw) return;
      const data = JSON.parse(raw);
      if (data?.prenom || data?.dateNaissance || data?.email) {
        setP1((prev) => ({
          ...prev,
          prenom: prev.prenom || data?.prenom || '',
          birth_date: prev.birth_date || data?.dateNaissance || '',
          birth_place: prev.birth_place || data?.lieuNaissance || data?.birth_place || prev.birth_place,
        }));
        if (data?.email) setEmail((prev) => prev || data.email);
      }
    } catch { /* noop */ }
  }, []);

  const update1 = (k, v) => setP1((prev) => ({ ...prev, [k]: v }));
  const update2 = (k, v) => setP2((prev) => ({ ...prev, [k]: v }));

  const canSubmit = email.trim() && p1.prenom.trim() && p1.birth_date && p2.prenom.trim() && p2.birth_date && state.status !== 'loading';

  const submit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    setState({ status: 'loading', message: '' });
    try {
      trackEvent('generate_lead', { source: 'synastrie_lead_magnet', method: 'email' });
      const res = await fetch(`${API_URL}/api/synastrie/free-extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.trim(),
          consent_marketing: consent,
          person1: {
            prenom: p1.prenom.trim(),
            birth_date: p1.birth_date,
            birth_place: p1.birth_place || 'Paris, France',
          },
          person2: {
            prenom: p2.prenom.trim(),
            birth_date: p2.birth_date,
            birth_place: p2.birth_place || 'Paris, France',
          },
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || data.success === false) {
        throw new Error(data?.detail || data?.message || 'Erreur serveur');
      }
      trackEvent('synastrie_free_extract_sent', { email_domain: email.split('@')[1] || '', variant: variantKey || null });
      if (variantKey) {
        trackABEvent('synastrie_exit_intent', variantKey, 'converted', { email_domain: email.split('@')[1] || '' });
      }
      setState({ status: 'success', message: data.message || 'Extrait envoyé ! Vérifiez votre boîte email.' });
      try {
        if (typeof onSuccess === 'function') onSuccess();
      } catch { /* noop */ }
      // Petit délai 1s pour laisser le toast "Extrait envoyé · redirection…" s'afficher avant redirect.
      setTimeout(() => navigate('/synastrie/extrait-envoye'), 1000);
    } catch (err) {
      setState({ status: 'error', message: err.message || "Impossible d'envoyer l'extrait, réessayez." });
    }
  };

  if (state.status === 'success') {
    return (
      <>
        <section
          aria-label="Extrait synastrie envoyé"
          data-testid="synastrie-lead-success"
          style={variant === 'modal' ? modalInlineStyle : outerStyle}
        >
          <div style={variant === 'modal' ? modalInnerStyle : innerStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
              <CheckCircle2 size={22} style={{ color: '#4ADE80' }} strokeWidth={1.5} />
              <h2 style={h2Style}>Votre extrait est en route</h2>
            </div>
            <p style={copyStyle}>{state.message}</p>
            <p style={{ ...copyStyle, marginTop: 10, fontSize: 13, opacity: 0.72 }}>
              Un email avec le lien vers votre extrait 3 pages vient d&apos;être envoyé à <strong>{email}</strong>. Pensez à vérifier vos spams si rien n&apos;arrive sous 5 minutes.
            </p>
          </div>
        </section>
        {/* Toast de confirmation éphémère pendant la redirection vers la thanks page */}
        <div
          role="status"
          aria-live="polite"
          data-testid="synastrie-lead-toast"
          style={{
            position: 'fixed',
            top: 24,
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 10000,
            display: 'inline-flex',
            alignItems: 'center',
            gap: 10,
            padding: '12px 20px',
            background: 'linear-gradient(135deg, #0F1A3A, #0C132E)',
            border: '1px solid rgba(74,222,128,0.4)',
            borderRadius: 999,
            boxShadow: '0 10px 30px rgba(0,0,0,0.35)',
            color: '#F5EEE0',
            fontFamily: 'Inter, sans-serif',
            fontSize: 13.5,
            letterSpacing: '0.02em',
            animation: 'synLeadToast 320ms cubic-bezier(0.16, 1, 0.3, 1) both',
          }}
        >
          <CheckCircle2 size={16} style={{ color: '#4ADE80' }} strokeWidth={1.8} />
          <span>Extrait envoyé · redirection…</span>
          <style>{`
            @keyframes synLeadToast {
              from { opacity: 0; transform: translate(-50%, -8px); }
              to   { opacity: 1; transform: translate(-50%, 0); }
            }
          `}</style>
        </div>
      </>
    );
  }

  return (
    <section
      aria-labelledby="synastrie-lead-title"
      data-testid="synastrie-lead-magnet"
      style={variant === 'modal' ? modalInlineStyle : outerStyle}
    >
      <div style={variant === 'modal' ? modalInnerStyle : innerStyle}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <p style={{ fontFamily: '"Cinzel", serif', fontSize: 11, letterSpacing: '0.3em', textTransform: 'uppercase', color: '#D4AF37', margin: '0 0 10px' }}>
            <Sparkles size={14} style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: 6 }} strokeWidth={1.5} />
            {copy?.eyebrow || 'Extrait gratuit · 3 pages'}
          </p>
          <h2 id="synastrie-lead-title" style={h2Style} data-testid="synastrie-lead-title">
            {copy?.title || 'Un aperçu de votre lien, offert.'}
          </h2>
          <p style={copyStyle}>
            {copy?.subtitle || 'Entrez vos deux prénoms et dates de naissance : nous générons un extrait de 3 pages de votre synastrie (Soleils croisés + ouverture de rapport), envoyé par email dans la minute.'}
          </p>
        </div>

        <form onSubmit={submit} data-testid="synastrie-lead-form">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 20, marginBottom: 20 }}>
            {/* Personne 1 */}
            <div style={cardStyle} data-testid="synastrie-lead-person1">
              <h3 style={h3Style}>Vous</h3>
              <label style={LABEL_STYLE} htmlFor="syn-lead-p1-prenom">Prénom</label>
              <input
                id="syn-lead-p1-prenom"
                type="text"
                value={p1.prenom}
                onChange={(e) => update1('prenom', e.target.value)}
                placeholder="Marie"
                style={INPUT_STYLE}
                data-testid="synastrie-lead-p1-prenom"
                required
              />
              <label style={{ ...LABEL_STYLE, marginTop: 14 }} htmlFor="syn-lead-p1-date">Date de naissance</label>
              <input
                id="syn-lead-p1-date"
                type="date"
                value={p1.birth_date}
                onChange={(e) => update1('birth_date', e.target.value)}
                style={INPUT_STYLE}
                data-testid="synastrie-lead-p1-date"
                required
              />
            </div>
            {/* Personne 2 */}
            <div style={cardStyle} data-testid="synastrie-lead-person2">
              <h3 style={h3Style}>L&apos;autre</h3>
              <label style={LABEL_STYLE} htmlFor="syn-lead-p2-prenom">Prénom</label>
              <input
                id="syn-lead-p2-prenom"
                type="text"
                value={p2.prenom}
                onChange={(e) => update2('prenom', e.target.value)}
                placeholder="Jules"
                style={INPUT_STYLE}
                data-testid="synastrie-lead-p2-prenom"
                required
              />
              <label style={{ ...LABEL_STYLE, marginTop: 14 }} htmlFor="syn-lead-p2-date">Date de naissance</label>
              <input
                id="syn-lead-p2-date"
                type="date"
                value={p2.birth_date}
                onChange={(e) => update2('birth_date', e.target.value)}
                style={INPUT_STYLE}
                data-testid="synastrie-lead-p2-date"
                required
              />
            </div>
          </div>

          <label style={LABEL_STYLE} htmlFor="syn-lead-email">Votre email</label>
          <div style={{ position: 'relative', marginBottom: 18 }}>
            <Mail size={16} style={{ position: 'absolute', top: 15, left: 14, color: 'rgba(212,175,55,0.65)' }} strokeWidth={1.6} />
            <input
              id="syn-lead-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="vous@exemple.fr"
              style={{ ...INPUT_STYLE, paddingLeft: 40 }}
              data-testid="synastrie-lead-email"
              required
            />
          </div>

          <label style={{ display: 'flex', alignItems: 'flex-start', gap: 10, fontSize: 12, color: 'rgba(244,239,230,0.68)', marginBottom: 22, fontFamily: 'Inter, sans-serif', lineHeight: 1.5 }}>
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
              data-testid="synastrie-lead-consent"
              style={{ marginTop: 3, accentColor: '#D4AF37' }}
            />
            <span>
              J&apos;accepte de recevoir mon extrait par email + occasionnellement des conseils astrologiques. Je peux me désabonner en 1 clic.
            </span>
          </label>

          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <button
              type="submit"
              disabled={!canSubmit}
              data-testid="synastrie-lead-submit"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
                padding: '14px 28px',
                background: canSubmit ? 'linear-gradient(135deg, #D4AF37, #E8C766)' : 'rgba(212,175,55,0.35)',
                color: '#0F1A3C',
                border: 'none',
                borderRadius: 4,
                fontFamily: '"Cinzel", serif',
                fontSize: 13,
                letterSpacing: '0.2em',
                textTransform: 'uppercase',
                fontWeight: 600,
                cursor: canSubmit ? 'pointer' : 'not-allowed',
                transition: 'transform 180ms ease, box-shadow 180ms ease',
              }}
              onMouseEnter={(e) => { if (canSubmit) e.currentTarget.style.transform = 'translateY(-1px)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              {state.status === 'loading' ? (
                <>
                  <Loader2 size={16} strokeWidth={1.8} style={{ animation: 'spin 900ms linear infinite' }} />
                  Génération…
                </>
              ) : (
                <>Recevoir mon extrait gratuit</>
              )}
            </button>
          </div>

          {state.status === 'error' && (
            <p data-testid="synastrie-lead-error" style={{ marginTop: 16, textAlign: 'center', color: '#F87171', fontSize: 13 }}>
              {state.message}
            </p>
          )}
        </form>
      </div>
    </section>
  );
}

const outerStyle = {
  padding: '72px 20px',
  background: 'linear-gradient(180deg, #0F1A3A 0%, #0C132E 100%)',
  color: '#F5EEE0',
};

const innerStyle = {
  maxWidth: 720,
  margin: '0 auto',
  padding: '36px 32px',
  background: 'rgba(11,26,46,0.65)',
  border: '1px solid rgba(212,175,55,0.25)',
  borderRadius: 8,
  backdropFilter: 'blur(8px)',
};

const h2Style = {
  margin: 0,
  fontFamily: '"Fraunces", "Playfair Display", serif',
  fontVariationSettings: "'opsz' 144, 'SOFT' 50",
  fontWeight: 400,
  fontSize: 'clamp(24px, 3.4vw, 32px)',
  lineHeight: 1.2,
  letterSpacing: '-0.01em',
  color: '#F5EEE0',
};

const h3Style = {
  margin: '0 0 14px',
  fontFamily: '"Fraunces", "Playfair Display", serif',
  fontVariationSettings: "'opsz' 144, 'SOFT' 50",
  fontWeight: 400,
  fontSize: 18,
  color: 'rgba(244,239,230,0.9)',
};

const copyStyle = {
  margin: '12px auto 0',
  maxWidth: 540,
  fontSize: 14.5,
  lineHeight: 1.6,
  color: 'rgba(244,239,230,0.78)',
};

const cardStyle = {
  padding: '18px 18px 20px',
  background: 'rgba(255,255,255,0.03)',
  border: '1px solid rgba(212,175,55,0.18)',
  borderRadius: 6,
};

const modalInlineStyle = {
  padding: 0,
  background: 'transparent',
  color: '#F5EEE0',
};

const modalInnerStyle = {
  maxWidth: 720,
  margin: 0,
  padding: '28px 24px 24px',
  background: 'transparent',
  border: 'none',
  borderRadius: 0,
};
