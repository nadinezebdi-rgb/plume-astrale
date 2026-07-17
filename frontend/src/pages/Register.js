import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { UserPlus, Eye, EyeOff, Loader2, ArrowLeft } from 'lucide-react';
import SEO from '@/components/SEO';

const COUNTRIES = [
  'France', 'Belgique', 'Suisse', 'Canada', 'Luxembourg', 'Monaco',
  'Algérie', 'Maroc', 'Tunisie', 'Sénégal', "Côte d'Ivoire",
  'États-Unis', 'Royaume-Uni', 'Allemagne', 'Espagne', 'Italie', 'Portugal', 'Autre',
];

const inputStyle = {
  borderColor: 'rgba(212,175,55,0.3)',
  color: 'var(--pa-body)',
};

export default function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [step, setStep] = useState(1);
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [birthDay, setBirthDay] = useState('');
  const [birthMonth, setBirthMonth] = useState('');
  const [birthYear, setBirthYear] = useState('');
  const [birthHour, setBirthHour] = useState('');
  const [birthMinute, setBirthMinute] = useState('');
  const [birthPlace, setBirthPlace] = useState('');
  const [birthCountry, setBirthCountry] = useState('France');

  const goStep2 = () => {
    if (!email || !password) {
      setError('Veuillez remplir tous les champs');
      return;
    }
    if (password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }
    setError('');
    setStep(2);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const birthDate = birthYear && birthMonth && birthDay
      ? `${birthYear}-${birthMonth.padStart(2,'0')}-${birthDay.padStart(2,'0')}`
      : '';
    if (!birthDate || !birthPlace) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const h = (birthHour || '00').toString().padStart(2, '0');
      const m = (birthMinute || '00').toString().padStart(2, '0');

      await register({
        email,
        password,
        birth_date: `${birthYear}-${birthMonth.padStart(2,'0')}-${birthDay.padStart(2,'0')}`,
        birth_time: `${h}:${m}`,
        birth_place: birthPlace,
        birth_country: birthCountry,
      });

      navigate('/');
    } catch (err) {
      console.error('Register error:', err);
      const msg = err?.response?.data?.detail || "Erreur lors de l'inscription";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20 pb-12" data-testid="register-page">
      <SEO path="/inscription" />
      <div className="w-full max-w-md">
        <div
          className="rounded-2xl p-8 md:p-10"
          style={{
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(212,175,55,0.15)',
            backdropFilter: 'blur(16px)',
          }}
        >
          {/* Header */}
          <div className="flex items-center justify-center gap-3 mb-8">
            <UserPlus className="w-5 h-5" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
            <h1
              className="text-2xl"
              style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}
            >
              Créer un compte
            </h1>
          </div>

          {/* Étapes */}
          <div className="flex items-center justify-center gap-2 mb-8">
            {[1, 2].map((s) => (
              <div key={s} className="flex items-center gap-2">
                <div
                  className="w-6 h-6 rounded-full flex items-center justify-center text-xs transition-all duration-300"
                  style={{
                    background: step >= s ? '#D4AF37' : 'rgba(212,175,55,0.1)',
                    color: step >= s ? '#111625' : 'var(--pa-muted)',
                    border: '1px solid rgba(212,175,55,0.3)',
                    fontWeight: 600,
                  }}
                >
                  {s}
                </div>
                {s < 2 && (
                  <div
                    className="w-8 h-px"
                    style={{ background: step > s ? '#D4AF37' : 'rgba(212,175,55,0.2)' }}
                  />
                )}
              </div>
            ))}
          </div>

          {/* Erreur */}
          {error && (
            <div
              className="mb-6 p-3 rounded-lg text-sm text-center"
              style={{
                background: 'rgba(220,38,38,0.1)',
                border: '1px solid rgba(220,38,38,0.3)',
                color: '#fca5a5',
              }}
              data-testid="register-error"
            >
              {error}
            </div>
          )}

          {/* ÉTAPE 1 — Email & Mot de passe */}
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <label
                  className="block text-xs uppercase tracking-widest mb-2"
                  style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}
                >
                  Email
                </label>
                <input
                  type="email"
                  placeholder="votre@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors"
                  style={inputStyle}
                  onFocus={(e) => (e.target.style.borderColor = '#D4AF37')}
                  onBlur={(e) => (e.target.style.borderColor = 'rgba(212,175,55,0.3)')}
                  data-testid="register-email-input"
                />
              </div>

              <div className="relative">
                <label
                  className="block text-xs uppercase tracking-widest mb-2"
                  style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}
                >
                  Mot de passe
                </label>
                <input
                  type={showPw ? 'text' : 'password'}
                  placeholder="Minimum 6 caractères"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors pr-10"
                  style={inputStyle}
                  onFocus={(e) => (e.target.style.borderColor = '#D4AF37')}
                  onBlur={(e) => (e.target.style.borderColor = 'rgba(212,175,55,0.3)')}
                  data-testid="register-password-input"
                />
                <button
                  type="button"
                  onClick={() => setShowPw(!showPw)}
                  className="absolute right-0 bottom-2"
                  style={{ color: 'var(--pa-muted)' }}
                >
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              <button
                onClick={goStep2}
                className="w-full py-3 mt-2 text-xs uppercase tracking-widest rounded-full transition-all duration-500"
                style={{
                  border: '1px solid rgba(212,175,55,0.5)',
                  color: '#D4AF37',
                  background: 'transparent',
                  letterSpacing: '0.12em',
                }}
                data-testid="register-next-btn"
              >
                Continuer
              </button>
            </div>
          )}

          {/* ÉTAPE 2 — Naissance */}
          {step === 2 && (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label
                  className="block text-xs uppercase tracking-widest mb-2"
                  style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}
                >
                  Date de naissance
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <select value={birthDay} onChange={(e) => setBirthDay(e.target.value)}
                    className="bg-transparent border-b py-2 text-base outline-none" style={inputStyle}
                    onFocus={(e) => (e.target.style.borderColor = '#D4AF37')}
                    onBlur={(e) => (e.target.style.borderColor = 'rgba(212,175,55,0.3)')}>
                    <option value="">Jour</option>
                    {Array.from({length:31},(_,i)=>i+1).map(d=><option key={d} value={String(d)} style={{background:'#111625'}}>{d}</option>)}
                  </select>
                  <select value={birthMonth} onChange={(e) => setBirthMonth(e.target.value)}
                    className="bg-transparent border-b py-2 text-base outline-none" style={inputStyle}
                    onFocus={(e) => (e.target.style.borderColor = '#D4AF37')}
                    onBlur={(e) => (e.target.style.borderColor = 'rgba(212,175,55,0.3)')}>
                    <option value="">Mois</option>
                    {['Janv','Févr','Mars','Avr','Mai','Juin','Juil','Août','Sept','Oct','Nov','Déc'].map((m,i)=>
                      <option key={i+1} value={String(i+1)} style={{background:'#111625'}}>{m}</option>)}
                  </select>
                  <select value={birthYear} onChange={(e) => setBirthYear(e.target.value)}
                    className="bg-transparent border-b py-2 text-base outline-none" style={inputStyle}
                    onFocus={(e) => (e.target.style.borderColor = '#D4AF37')}
                    onBlur={(e) => (e.target.style.borderColor = 'rgba(212,175,55,0.3)')}>
                    <option value="">Année</option>
                    {Array.from({length:100},(_,i)=>new Date().getFullYear()-i).map(y=>
                      <option key={y} value={String(y)} style={{background:'#111625'}}>{y}</option>)}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label
                    className="block text-xs uppercase tracking-widest mb-2"
                    style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}
                  >
                    Heure
                  </label>
                  <input
                    type="number"
                    placeholder="HH"
                    min="0"
                    max="23"
                    value={birthHour}
                    onChange={(e) => setBirthHour(e.target.value)}
                    className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors"
                    style={inputStyle}
                    onFocus={(e) => (e.target.style.borderColor = '#D4AF37')}
                    onBlur={(e) => (e.target.style.borderColor = 'rgba(212,175,55,0.3)')}
                    data-testid="register-hour-input"
                  />
                </div>
                <div>
                  <label
                    className="block text-xs uppercase tracking-widest mb-2"
                    style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}
                  >
                    Minute
                  </label>
                  <input
                    type="number"
                    placeholder="MM"
                    min="0"
                    max="59"
                    value={birthMinute}
                    onChange={(e) => setBirthMinute(e.target.value)}
                    className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors"
                    style={inputStyle}
                    onFocus={(e) => (e.target.style.borderColor = '#D4AF37')}
                    onBlur={(e) => (e.target.style.borderColor = 'rgba(212,175,55,0.3)')}
                    data-testid="register-minute-input"
                  />
                </div>
              </div>

              <div>
                <label
                  className="block text-xs uppercase tracking-widest mb-2"
                  style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}
                >
                  Lieu de naissance
                </label>
                <input
                  type="text"
                  placeholder="Ville, ex: Paris"
                  value={birthPlace}
                  onChange={(e) => setBirthPlace(e.target.value)}
                  className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors"
                  style={inputStyle}
                  onFocus={(e) => (e.target.style.borderColor = '#D4AF37')}
                  onBlur={(e) => (e.target.style.borderColor = 'rgba(212,175,55,0.3)')}
                  data-testid="register-birthplace-input"
                />
              </div>

              <div>
                <label
                  className="block text-xs uppercase tracking-widest mb-2"
                  style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}
                >
                  Pays
                </label>
                <select
                  value={birthCountry}
                  onChange={(e) => setBirthCountry(e.target.value)}
                  className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors"
                  style={{ ...inputStyle, background: 'transparent' }}
                  onFocus={(e) => (e.target.style.borderColor = '#D4AF37')}
                  onBlur={(e) => (e.target.style.borderColor = 'rgba(212,175,55,0.3)')}
                  data-testid="register-country-select"
                >
                  {COUNTRIES.map((c) => (
                    <option key={c} value={c} style={{ background: '#111625' }}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex items-center gap-1 py-3 px-5 text-xs uppercase tracking-widest rounded-full transition-all duration-300"
                  style={{
                    border: '1px solid rgba(212,175,55,0.2)',
                    color: 'var(--pa-muted)',
                    background: 'transparent',
                  }}
                  data-testid="register-back-btn"
                >
                  <ArrowLeft className="w-3 h-3" /> Retour
                </button>

                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 flex items-center justify-center gap-2 py-3 text-xs uppercase tracking-widest rounded-full transition-all duration-500"
                  style={{
                    border: '1px solid rgba(212,175,55,0.5)',
                    color: loading ? 'var(--pa-muted)' : '#D4AF37',
                    background: 'transparent',
                    letterSpacing: '0.12em',
                  }}
                  data-testid="register-submit-btn"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" /> Création...
                    </>
                  ) : (
                    'Créer mon compte'
                  )}
                </button>
              </div>
            </form>
          )}

          <p className="text-center mt-6 text-sm" style={{ color: 'var(--pa-muted)' }}>
            Déjà un compte ?{' '}
            <Link
              to="/connexion"
              className="transition-colors hover:opacity-80"
              style={{ color: '#D4AF37' }}
              data-testid="register-login-link"
            >
              Se connecter
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
