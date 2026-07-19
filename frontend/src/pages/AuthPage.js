// frontend/src/pages/AuthPage.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { supabase } from '@/lib/supabase';
import { LogIn, UserPlus, Eye, EyeOff, Loader2, ArrowLeft } from 'lucide-react';
import SEO from '@/components/SEO';
import { event as trackEvent } from '@/lib/analytics';

const COUNTRIES = [
  'France', 'Belgique', 'Suisse', 'Canada', 'Luxembourg', 'Monaco',
  'Algérie', 'Maroc', 'Tunisie', 'Sénégal', "Côte d'Ivoire",
  'États-Unis', 'Royaume-Uni', 'Allemagne', 'Espagne', 'Italie', 'Portugal', 'Autre',
];

const fieldClass =
  'w-full bg-transparent border-b py-2 text-base outline-none transition-colors';
const fieldStyle = { borderColor: 'rgba(212,175,55,0.3)', color: 'var(--pa-body)' };
const focusGold = (e) => (e.target.style.borderColor = '#D4AF37');
const blurGold = (e) => (e.target.style.borderColor = 'rgba(212,175,55,0.3)');

export default function AuthPage() {
  const navigate = useNavigate();
  const { login, register } = useAuth();

  // mode: 'login' | 'register' — pilote l'animation de transition entre les deux vues
  const [mode, setMode] = useState('login');
  const [step, setStep] = useState(1); // étape inscription (1 = identifiants, 2 = naissance)
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState(''); // NOUVEAU champ
  const [birthDay, setBirthDay] = useState('');
  const [birthMonth, setBirthMonth] = useState('');
  const [birthYear, setBirthYear] = useState('');
  const [birthHour, setBirthHour] = useState('');
  const [birthMinute, setBirthMinute] = useState('');
  const [birthPlace, setBirthPlace] = useState('');
  const [birthCountry, setBirthCountry] = useState('France');

  const switchMode = (next) => {
    setError('');
    setStep(1);
    setMode(next);
  };

  // ---- Connexion Google (Supabase OAuth) ----
  const handleGoogle = async () => {
    setError('');
    try {
      const params = new URLSearchParams(window.location.search);
      const redirect = params.get('redirect') || '/mon-compte';
      await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: window.location.origin + redirect },
      });
    } catch (err) {
      console.error('GOOGLE OAUTH ERROR:', err);
      setError('Connexion Google impossible pour le moment');
    }
  };

  // ---- Connexion classique ----
  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) return setError('Veuillez remplir tous les champs');
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      trackEvent('login_success');
      const params = new URLSearchParams(window.location.search);
      navigate(params.get('redirect') || '/mon-compte');
    } catch (err) {
      console.error('LOGIN ERROR:', err);
      setError('Email ou mot de passe incorrect');
    } finally {
      setLoading(false);
    }
  };

  // ---- Inscription : étape 1 -> étape 2 ----
  const goStep2 = () => {
    if (!email || !password || !confirmPassword)
      return setError('Veuillez remplir tous les champs');
    if (password.length < 6)
      return setError('Le mot de passe doit contenir au moins 6 caractères');
    if (password !== confirmPassword)
      return setError('Les mots de passe ne correspondent pas');
    setError('');
    setStep(2);
  };

  // ---- Inscription : soumission finale (les crédits sont attribués côté serveur) ----
  const handleRegister = async (e) => {
    e.preventDefault();
    const birthDate =
      birthYear && birthMonth && birthDay
        ? birthYear + '-' + birthMonth.padStart(2, '0') + '-' + birthDay.padStart(2, '0')
        : '';
    if (!birthDate || !birthPlace)
      return setError('Veuillez remplir tous les champs obligatoires');

    setError('');
    setLoading(true);
    try {
      const h = (birthHour || '00').toString().padStart(2, '0');
      const m = (birthMinute || '00').toString().padStart(2, '0');
      await register({
        email,
        password,
        birth_date: birthDate,
        birth_time: h + ':' + m,
        birth_place: birthPlace,
        birth_country: birthCountry,
      });
      trackEvent('register_success');
      navigate('/'); // l'utilisateur reçoit ses crédits d'inscription côté backend
    } catch (err) {
      console.error('Register error:', err);
      setError(err?.response?.data?.detail || "Erreur lors de l'inscription");
    } finally {
      setLoading(false);
    }
  };

  const isLogin = mode === 'login';

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20 pb-12" data-testid="auth-page">
      <SEO path={isLogin ? '/connexion' : '/inscription'} />
      <div className="w-full max-w-md">
        <div
          className="rounded-2xl p-8 md:p-10 overflow-hidden"
          style={{
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(212,175,55,0.15)',
            backdropFilter: 'blur(16px)',
          }}
        >
          {/* En-tête */}
          <div className="flex items-center justify-center gap-3 mb-8">
            {isLogin ? (
              <LogIn className="w-5 h-5" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
            ) : (
              <UserPlus className="w-5 h-5" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
            )}
            <h1
              className="text-2xl"
              style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}
            >
              {isLogin ? 'Connexion' : 'Créer un compte'}
            </h1>
          </div>

          {/* Onglets Se connecter / Créer un compte */}
          <div
            className="relative flex mb-8 rounded-full p-1"
            style={{ background: 'rgba(212,175,55,0.08)', border: '1px solid rgba(212,175,55,0.2)' }}
          >
            <span
              className="absolute top-1 bottom-1 w-1/2 rounded-full transition-transform duration-500 ease-out"
              style={{
                background: 'rgba(212,175,55,0.9)',
                transform: isLogin ? 'translateX(0%)' : 'translateX(100%)',
              }}
            />
            <button
              type="button"
              onClick={() => switchMode('login')}
              className="relative z-10 flex-1 py-2 text-xs uppercase tracking-widest transition-colors"
              style={{ color: isLogin ? '#111625' : 'var(--pa-muted)', letterSpacing: '0.1em' }}
            >
              Se connecter
            </button>
            <button
              type="button"
              onClick={() => switchMode('register')}
              className="relative z-10 flex-1 py-2 text-xs uppercase tracking-widest transition-colors"
              style={{ color: !isLogin ? '#111625' : 'var(--pa-muted)', letterSpacing: '0.1em' }}
            >
              Créer un compte
            </button>
          </div>

          {error && (
            <div
              className="mb-6 p-3 rounded-lg text-sm text-center"
              style={{ background: 'rgba(220,38,38,0.1)', border: '1px solid rgba(220,38,38,0.3)', color: '#fca5a5' }}
              data-testid="auth-error"
            >
              {error}
            </div>
          )}

          {/* Zone animée : fondu + léger glissement à chaque changement de vue */}
          <div key={mode + '-' + step} className="auth-fade">
            {isLogin ? (
              /* ---------- VUE CONNEXION ---------- */
              <form onSubmit={handleLogin} className="space-y-5">
                <Field label="Email" type="email" value={email} onChange={setEmail} required />
                <PasswordField
                  label="Mot de passe"
                  value={password}
                  onChange={setPassword}
                  show={showPw}
                  toggle={() => setShowPw(!showPw)}
                />
                <div className="flex justify-end">
                  <a
                    href="/mot-de-passe-oublie"
                    className="text-xs hover:opacity-80 transition-opacity"
                    style={{ color: 'var(--pa-muted)', letterSpacing: '0.05em' }}
                  >
                    Mot de passe oublié ?
                  </a>
                </div>
                <SubmitButton loading={loading} label="Se connecter" loadingLabel="Connexion..." />
                <GoogleDivider onClick={handleGoogle} />
              </form>
            ) : step === 1 ? (
              /* ---------- VUE INSCRIPTION — ÉTAPE 1 ---------- */
              <div className="space-y-5">
                <Field label="Email" type="email" value={email} onChange={setEmail} required />
                <PasswordField
                  label="Mot de passe"
                  value={password}
                  onChange={setPassword}
                  show={showPw}
                  toggle={() => setShowPw(!showPw)}
                />
                <PasswordField
                  label="Confirmer le mot de passe"
                  value={confirmPassword}
                  onChange={setConfirmPassword}
                  show={showPw}
                  toggle={() => setShowPw(!showPw)}
                />
                <button
                  type="button"
                  onClick={goStep2}
                  className="w-full py-3 mt-4 text-xs uppercase tracking-widest rounded-full transition-all duration-500"
                  style={{ border: '1px solid rgba(212,175,55,0.5)', color: '#D4AF37', background: 'transparent', letterSpacing: '0.12em' }}
                >
                  Continuer
                </button>
                <GoogleDivider onClick={handleGoogle} />
              </div>
            ) : (
              /* ---------- VUE INSCRIPTION — ÉTAPE 2 (données de naissance) ---------- */
              <form onSubmit={handleRegister} className="space-y-5">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex items-center gap-1 text-xs mb-2"
                  style={{ color: 'var(--pa-muted)' }}
                >
                  <ArrowLeft className="w-3 h-3" /> Retour
                </button>

                <div className="grid grid-cols-3 gap-3">
                  <Field label="Jour" value={birthDay} onChange={setBirthDay} placeholder="JJ" />
                  <Field label="Mois" value={birthMonth} onChange={setBirthMonth} placeholder="MM" />
                  <Field label="Année" value={birthYear} onChange={setBirthYear} placeholder="AAAA" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Field label="Heure" value={birthHour} onChange={setBirthHour} placeholder="HH" />
                  <Field label="Minute" value={birthMinute} onChange={setBirthMinute} placeholder="MM" />
                </div>
                <Field label="Ville de naissance" value={birthPlace} onChange={setBirthPlace} required />

                <div>
                  <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>
                    Pays de naissance
                  </label>
                  <select
                    value={birthCountry}
                    onChange={(e) => setBirthCountry(e.target.value)}
                    className={fieldClass}
                    style={fieldStyle}
                    onFocus={focusGold}
                    onBlur={blurGold}
                  >
                    {COUNTRIES.map((c) => (
                      <option key={c} value={c} style={{ color: '#111625' }}>{c}</option>
                    ))}
                  </select>
                </div>

                <SubmitButton loading={loading} label="Créer mon compte" loadingLabel="Création..." />
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---------- Sous-composants ---------- */
function Field({ label, type = 'text', value, onChange, required, placeholder }) {
  return (
    <div>
      <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        placeholder={placeholder}
        className={fieldClass}
        style={fieldStyle}
        onFocus={focusGold}
        onBlur={blurGold}
      />
    </div>
  );
}

function PasswordField({ label, value, onChange, show, toggle }) {
  return (
    <div className="relative">
      <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>
        {label}
      </label>
      <input
        type={show ? 'text' : 'password'}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required
        className={fieldClass + ' pr-10'}
        style={fieldStyle}
        onFocus={focusGold}
        onBlur={blurGold}
      />
      <button type="button" onClick={toggle} className="absolute right-0 bottom-2" style={{ color: 'var(--pa-muted)' }}>
        {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
      </button>
    </div>
  );
}

function SubmitButton({ loading, label, loadingLabel }) {
  return (
    <button
      type="submit"
      disabled={loading}
      className="w-full py-3 mt-4 text-xs uppercase tracking-widest rounded-full transition-all duration-500 flex items-center justify-center gap-2"
      style={{
        border: '1px solid rgba(212,175,55,0.5)',
        color: loading ? 'var(--pa-muted)' : '#D4AF37',
        background: 'transparent',
        letterSpacing: '0.12em',
      }}
    >
      {loading && <Loader2 className="w-4 h-4 animate-spin" />}
      {loading ? loadingLabel : label}
    </button>
  );
}

function GoogleDivider({ onClick }) {
  return (
    <>
      <div className="flex items-center gap-3 my-6">
        <span className="flex-1 h-px" style={{ background: 'rgba(212,175,55,0.2)' }} />
        <span className="text-xs uppercase tracking-widest" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>
          ou continuer avec
        </span>
        <span className="flex-1 h-px" style={{ background: 'rgba(212,175,55,0.2)' }} />
      </div>
      <button
        type="button"
        onClick={onClick}
        className="w-full py-3 rounded-full flex items-center justify-center gap-3 text-sm transition-all duration-300 hover:opacity-90"
        style={{ border: '1px solid rgba(212,175,55,0.3)', background: 'rgba(255,255,255,0.04)', color: 'var(--pa-body)' }}
      >
        <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
          <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.9 29.3 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34.5 6.1 29.5 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.3-.4-3.5z"/>
          <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 16 19 13 24 13c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34.5 6.1 29.5 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/>
          <path fill="#4CAF50" d="M24 44c5.2 0 10-2 13.6-5.2l-6.3-5.3C29.2 34.9 26.7 36 24 36c-5.3 0-9.7-3.1-11.3-8l-6.5 5C9.6 39.6 16.2 44 24 44z"/>
          <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.1-4 5.5l6.3 5.3C40.9 36 44 30.6 44 24c0-1.3-.1-2.3-.4-3.5z"/>
        </svg>
        Google
      </button>
    </>
  );
}
