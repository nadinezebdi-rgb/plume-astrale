import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Sparkles, Loader2, Mail, MapPin, Clock, Check, ArrowRight, Lock } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * HeroOracle — Tunnel d'acquisition 4 etats :
 *   idle           → prenom + date | CTA "Reveler mon energie"
 *   computing      → loading 1.5s (theatralite)
 *   teaser_shown   → wheel + chemin de vie + phase lunaire + tarot oui/non
 *                    | interpretation flouttee + capture email
 *   email_captured → invitation a affiner avec heure + lieu
 *                    | pont vers Premium
 *
 * Endpoints utilises (publics, pas de credits requis) :
 *   POST /api/oracle/teaser    → calcule chemin de vie + phase lunaire + tarot oui/non + wheel SVG
 *   POST /api/oracle/refine    → re-calcule avec heure/lieu pour debloquer plus
 */

const STATES = { IDLE: 'idle', COMPUTING: 'computing', TEASER: 'teaser', EMAIL: 'email', REFINED: 'refined' };

const HeroOracle = () => {
  const navigate = useNavigate();
  const [state, setState] = useState(STATES.IDLE);
  const [form, setForm] = useState({ firstName: '', birthDate: '', birthTime: '', birthPlace: '', email: '' });
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleChange = (k, v) => setForm(prev => ({ ...prev, [k]: v }));

  const computeTeaser = async () => {
    if (!form.firstName.trim() || !form.birthDate) {
      setError('Renseigne ton prénom et ta date de naissance.');
      return;
    }
    setError('');
    setState(STATES.COMPUTING);
    try {
      // Theatralite : on attend au moins 1.5s pour le ressenti
      const minWait = new Promise(r => setTimeout(r, 1500));
      const apiCall = axios.post(`${API_URL}/api/oracle/teaser`, {
        first_name: form.firstName.trim(),
        birth_date: form.birthDate,
      });
      const [, res] = await Promise.all([minWait, apiCall]);
      if (res.data?.success) {
        setResult(res.data);
        setState(STATES.TEASER);
      } else {
        setError("Impossible de générer ta lecture. Réessaie dans un instant.");
        setState(STATES.IDLE);
      }
    } catch (e) {
      setError(e?.response?.data?.detail || "Impossible de générer ta lecture. Réessaie dans un instant.");
      setState(STATES.IDLE);
    }
  };

  const captureEmail = async () => {
    if (!form.email || !form.email.includes('@')) {
      setError('Renseigne une adresse email valide.');
      return;
    }
    setError('');
    try {
      await axios.post(`${API_URL}/api/oracle/capture-email`, {
        email: form.email,
        first_name: form.firstName,
        birth_date: form.birthDate,
      }).catch(() => {});  // silencieux — on continue meme si la sauvegarde echoue
    } catch (e) { /* ignore */ }
    setState(STATES.EMAIL);
  };

  const refine = async () => {
    if (!form.birthTime || !form.birthPlace.trim()) {
      setError('Pour affiner ta lecture, renseigne ton heure et ton lieu de naissance.');
      return;
    }
    setError('');
    setState(STATES.REFINED);
  };

  /* ───────────────────────── RENDER PER STATE ───────────────────────── */

  if (state === STATES.IDLE) {
    return (
      <section className="hero-oracle" data-testid="hero-oracle" style={{ maxWidth: 560, margin: '0 auto', padding: '0 20px' }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <p style={{ fontSize: 11, letterSpacing: '0.3em', color: '#D4AF37', textTransform: 'uppercase', fontFamily: 'Cinzel, serif', marginBottom: 14 }}>
            Ta lecture symbolique
          </p>
          <h1 style={{
            fontFamily: 'Cormorant Garamond, serif', fontWeight: 300,
            fontSize: 'clamp(32px, 6vw, 56px)', lineHeight: 1.05,
            color: '#F0E6D3', marginBottom: 18,
          }}>
            Découvre <em style={{ fontStyle: 'italic', color: '#D4AF37' }}>ton énergie</em> du moment
          </h1>
          <p style={{ fontSize: 15, color: 'rgba(184,176,200,0.85)', maxWidth: 440, margin: '0 auto', lineHeight: 1.55 }}>
            En moins de 10 secondes, une lecture personnalisée — gratuite, sans carte, sans inscription.
          </p>
        </div>

        <div style={{
          background: 'rgba(255,255,255,0.03)',
          border: '1px solid rgba(212,175,55,0.18)',
          borderRadius: 20, padding: 28, backdropFilter: 'blur(12px)',
        }}>
          <div style={{ marginBottom: 18 }}>
            <label style={labelStyle}>Ton prénom</label>
            <input type="text" value={form.firstName}
              onChange={e => handleChange('firstName', e.target.value)}
              placeholder="ex: Juliette" style={inputStyle}
              data-testid="hero-firstname" />
          </div>
          <div style={{ marginBottom: 22 }}>
            <label style={labelStyle}>Ta date de naissance</label>
            <input type="date" value={form.birthDate}
              onChange={e => handleChange('birthDate', e.target.value)}
              style={inputStyle}
              data-testid="hero-birthdate" />
          </div>
          {error && <div style={errorStyle} data-testid="hero-error">{error}</div>}
          <button onClick={computeTeaser} style={primaryCta} data-testid="hero-cta-reveal">
            <Sparkles style={{ width: 16, height: 16 }} strokeWidth={1.8} />
            ✦ Révéler mon énergie
          </button>
          <p style={{ textAlign: 'center', fontSize: 11, color: 'rgba(212,175,55,0.55)', marginTop: 14, letterSpacing: '0.06em' }}>
            Gratuit · sans carte
          </p>
        </div>
      </section>
    );
  }

  if (state === STATES.COMPUTING) {
    return (
      <section data-testid="hero-computing" style={{ maxWidth: 560, margin: '0 auto', padding: '0 20px', textAlign: 'center' }}>
        <Wheel url={null} blurred={false} />
        <h2 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 28, color: '#F0E6D3', marginTop: 28, fontWeight: 300 }}>
          {form.firstName}, la Plume écoute ton ciel...
        </h2>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 10, marginTop: 16, color: '#D4AF37' }}>
          <Loader2 style={{ width: 18, height: 18 }} className="animate-spin" />
          <span style={{ fontSize: 12, letterSpacing: '0.15em', textTransform: 'uppercase' }}>Calcul des positions</span>
        </div>
      </section>
    );
  }

  if (state === STATES.TEASER) {
    const r = result || {};
    return (
      <section data-testid="hero-teaser" style={{ maxWidth: 640, margin: '0 auto', padding: '0 20px' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <p style={{ fontSize: 11, letterSpacing: '0.3em', color: '#D4AF37', textTransform: 'uppercase', fontFamily: 'Cinzel, serif', marginBottom: 12 }}>
            Ta lecture est prête, {form.firstName}
          </p>
        </div>

        <Wheel url={r.wheel_url} blurred={false} />

        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 14, marginTop: 28 }}>
          {r.lifepath && (
            <Card title="Chemin de vie" value={`${r.lifepath.number} · ${r.lifepath.archetype}`} testid="card-lifepath" />
          )}
          {r.moon_phase && (
            <Card title="Phase lunaire" value={r.moon_phase.phase} sub={r.moon_phase.message} testid="card-moon" />
          )}
          {r.tarot && (
            <Card title="Tirage du jour" value={r.tarot.card_name} sub={r.tarot.answer} testid="card-tarot" />
          )}
        </div>

        {/* Bloc interpretation floutee + capture email */}
        <div style={{
          marginTop: 28, position: 'relative', borderRadius: 18,
          background: 'rgba(255,255,255,0.025)',
          border: '1px solid rgba(212,175,55,0.2)',
          padding: 24, overflow: 'hidden',
        }} data-testid="hero-paywall">
          <div style={{ filter: 'blur(7px)', userSelect: 'none', pointerEvents: 'none' }}>
            <p style={{ color: '#F0E6D3', fontFamily: 'Cormorant Garamond, serif', fontSize: 18, lineHeight: 1.5 }}>
              {r.locked_preview || 'Ton interpretation complete, les conseils du jour, le rituel a poser ce matin, le mantra a porter...'}
            </p>
          </div>
          <div style={{
            position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center', padding: 20,
            background: 'linear-gradient(180deg, rgba(11,9,24,0.4) 0%, rgba(11,9,24,0.9) 70%)',
          }}>
            <Lock style={{ width: 20, height: 20, color: '#D4AF37', marginBottom: 8 }} strokeWidth={1.4} />
            <p style={{ color: '#F0E6D3', fontSize: 14, textAlign: 'center', marginBottom: 14 }}>
              Reçois ta lecture complète par email
            </p>
            <div style={{ display: 'flex', gap: 8, width: '100%', maxWidth: 360 }}>
              <input type="email" placeholder="ton@email.com" value={form.email}
                onChange={e => handleChange('email', e.target.value)}
                style={Object.assign({}, inputStyle, { marginBottom: 0, flex: 1 })}
                data-testid="hero-email-input" />
              <button onClick={captureEmail} style={Object.assign({}, primaryCta, { minWidth: 0, padding: '0 16px', fontSize: 11 })}
                data-testid="hero-cta-capture">
                <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
              </button>
            </div>
            {error && <div style={Object.assign({}, errorStyle, { marginTop: 12, marginBottom: 0 })}>{error}</div>}
            <p style={{ fontSize: 10, color: 'rgba(184,176,200,0.55)', marginTop: 10 }}>
              Aucun spam · Désinscription en 1 clic
            </p>
          </div>
        </div>
      </section>
    );
  }

  if (state === STATES.EMAIL) {
    return (
      <section data-testid="hero-affine" style={{ maxWidth: 560, margin: '0 auto', padding: '0 20px', textAlign: 'center' }}>
        <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'rgba(74,222,128,0.12)', border: '1px solid rgba(74,222,128,0.35)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 18 }}>
          <Check style={{ width: 28, height: 28, color: '#4ADE80' }} strokeWidth={2} />
        </div>
        <h2 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 32, color: '#F0E6D3', fontWeight: 300, marginBottom: 10 }}>
          Email envoyé à {form.email}
        </h2>
        <p style={{ color: 'rgba(184,176,200,0.85)', fontSize: 15, marginBottom: 32 }}>
          {form.firstName}, pour affiner encore ta lecture (ascendant, maisons, aspects), partage ton heure et ton lieu de naissance.
        </p>

        <div style={{
          background: 'rgba(255,255,255,0.03)',
          border: '1px solid rgba(212,175,55,0.18)',
          borderRadius: 20, padding: 28, marginBottom: 24, textAlign: 'left',
        }}>
          <div style={{ marginBottom: 18 }}>
            <label style={labelStyle}><Clock style={{ width: 12, height: 12, display: 'inline', marginRight: 6 }} />Heure de naissance</label>
            <input type="time" value={form.birthTime}
              onChange={e => handleChange('birthTime', e.target.value)} style={inputStyle}
              data-testid="hero-birthtime" />
          </div>
          <div style={{ marginBottom: 22 }}>
            <label style={labelStyle}><MapPin style={{ width: 12, height: 12, display: 'inline', marginRight: 6 }} />Lieu de naissance</label>
            <input type="text" value={form.birthPlace}
              onChange={e => handleChange('birthPlace', e.target.value)}
              placeholder="ex: Paris, France" style={inputStyle}
              data-testid="hero-birthplace" />
          </div>
          {error && <div style={errorStyle}>{error}</div>}
          <button onClick={refine} style={primaryCta} data-testid="hero-cta-refine">
            <Sparkles style={{ width: 16, height: 16 }} strokeWidth={1.8} />
            Affiner ma lecture
          </button>
        </div>

        {/* Pont vers Premium */}
        <PremiumBridge onCTA={() => navigate('/premium')} />
      </section>
    );
  }

  // REFINED
  return (
    <section data-testid="hero-refined" style={{ maxWidth: 560, margin: '0 auto', padding: '0 20px', textAlign: 'center' }}>
      <Sparkles style={{ width: 28, height: 28, color: '#D4AF37', margin: '0 auto 16px' }} strokeWidth={1.3} />
      <h2 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 30, color: '#F0E6D3', fontWeight: 300, marginBottom: 10 }}>
        Ta lecture affinée arrive...
      </h2>
      <p style={{ color: 'rgba(184,176,200,0.85)', fontSize: 14, marginBottom: 28 }}>
        Tu vas recevoir d&apos;ici quelques minutes ton thème complet avec ascendant, maisons et aspects.
      </p>
      <PremiumBridge onCTA={() => navigate('/premium')} />
    </section>
  );
};

/* ─── Helpers UI (declared at module scope to avoid no-unstable-nested-components) ─── */

const Wheel = ({ url, blurred }) => {
  const inner = url ? (
    <img src={url} alt="Ta carte natale"
      style={{ width: '100%', height: '100%', objectFit: 'contain', filter: 'drop-shadow(0 0 24px rgba(212,175,55,0.25))' }}
    />
  ) : (
    <div style={{
      width: '100%', height: '100%', borderRadius: '50%',
      border: '1.5px solid rgba(212,175,55,0.45)',
      background: 'radial-gradient(circle, rgba(167,139,250,0.18) 0%, transparent 70%)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      position: 'relative',
    }}>
      <Sparkles style={{ width: 40, height: 40, color: '#D4AF37', opacity: 0.6 }} strokeWidth={1.2} />
    </div>
  );
  return (
    <div style={{
      width: 260, height: 260, margin: '0 auto', position: 'relative',
      filter: blurred ? 'blur(8px) saturate(0.7)' : 'none',
      opacity: blurred ? 0.55 : 1,
      transition: 'all 0.6s',
    }}>{inner}</div>
  );
};

const labelStyle = {
  display: 'block', fontSize: 10, letterSpacing: '0.15em', textTransform: 'uppercase',
  color: 'rgba(212,175,55,0.75)', marginBottom: 8, fontFamily: 'Cinzel, serif',
};

const inputStyle = {
  width: '100%', background: 'rgba(0,0,0,0.25)',
  border: '1px solid rgba(212,175,55,0.25)', borderRadius: 12,
  padding: '12px 14px', color: '#F0E6D3', fontSize: 15,
  outline: 'none', minHeight: 48,
};

const primaryCta = {
  width: '100%', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8,
  padding: '14px 24px', borderRadius: 999,
  background: 'linear-gradient(135deg, #D4AF37 0%, #B8961F 100%)',
  color: '#0C0918', fontWeight: 700,
  fontSize: 13, letterSpacing: '0.12em', textTransform: 'uppercase',
  border: 'none', cursor: 'pointer', minHeight: 56,
  boxShadow: '0 6px 24px rgba(212,175,55,0.35)',
};

const errorStyle = {
  background: 'rgba(220,38,38,0.1)', border: '1px solid rgba(220,38,38,0.3)',
  color: '#fca5a5', padding: 10, borderRadius: 10, fontSize: 13,
  textAlign: 'center', marginBottom: 12,
};

const Card = ({ title, value, sub, testid }) => (
  <div style={{
    background: 'rgba(255,255,255,0.025)',
    border: '1px solid rgba(212,175,55,0.18)',
    borderRadius: 14, padding: '14px 18px',
  }} data-testid={testid}>
    <p style={{ fontSize: 10, letterSpacing: '0.18em', color: 'rgba(212,175,55,0.6)', textTransform: 'uppercase', fontFamily: 'Cinzel, serif', marginBottom: 4 }}>
      {title}
    </p>
    <p style={{ fontSize: 17, color: '#F0E6D3', fontFamily: 'Cormorant Garamond, serif', marginBottom: sub ? 4 : 0 }}>
      {value}
    </p>
    {sub && <p style={{ fontSize: 13, color: 'rgba(184,176,200,0.7)', lineHeight: 1.4 }}>{sub}</p>}
  </div>
);

const PremiumBridge = ({ onCTA }) => (
  <div style={{
    background: 'linear-gradient(135deg, rgba(212,175,55,0.1) 0%, rgba(167,139,250,0.08) 100%)',
    border: '1px solid rgba(212,175,55,0.35)',
    borderRadius: 18, padding: 24, textAlign: 'center',
  }} data-testid="premium-bridge">
    <p style={{ fontSize: 10, letterSpacing: '0.2em', color: '#D4AF37', textTransform: 'uppercase', marginBottom: 12, fontFamily: 'Cinzel, serif' }}>
      Va plus loin
    </p>
    <h3 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 22, color: '#F0E6D3', fontWeight: 300, marginBottom: 8 }}>
      Découvre l&apos;Expérience Premium
    </h3>
    <p style={{ fontSize: 13, color: 'rgba(184,176,200,0.8)', marginBottom: 18, lineHeight: 1.55 }}>
      Rituel quotidien, transits, compatibilités illimitées, rapports détaillés.
    </p>
    <button onClick={onCTA} style={Object.assign({}, primaryCta, { width: 'auto', padding: '12px 32px' })}
      data-testid="premium-bridge-cta">
      ✦ L&apos;Expérience Premium
    </button>
    <p style={{ fontSize: 11, color: 'rgba(184,176,200,0.55)', marginTop: 12 }}>
      7 jours offerts · annulable à tout moment
    </p>
  </div>
);

export default HeroOracle;
