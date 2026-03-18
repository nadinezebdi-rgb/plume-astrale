import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { UserPlus, Eye, EyeOff, ChevronRight, ChevronLeft, Gift } from 'lucide-react';
import SEO from '@/components/SEO';

const COUNTRIES = [
  'France', 'Belgique', 'Suisse', 'Canada', 'Luxembourg', 'Monaco',
  'Algérie', 'Maroc', 'Tunisie', 'Sénégal', 'Côte d\'Ivoire',
  'États-Unis', 'Royaume-Uni', 'Allemagne', 'Espagne', 'Italie', 'Portugal', 'Autre',
];

export default function Register() {
  const { register, loginAsGuest } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(1); // 1: credentials, 2: astro profile
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [birthDate, setBirthDate] = useState('');
  const [birthHour, setBirthHour] = useState('');
  const [birthMinute, setBirthMinute] = useState('');
  const [birthPlace, setBirthPlace] = useState('');
  const [birthCountry, setBirthCountry] = useState('France');

  const goStep2 = () => {
    if (!email || !password) { setError('Veuillez remplir tous les champs'); return; }
    if (password.length < 6) { setError('Le mot de passe doit contenir au moins 6 caractères'); return; }
    setError('');
    setStep(2);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!birthDate || !birthPlace) { setError('Veuillez remplir tous les champs obligatoires'); return; }
    setError('');
    setLoading(true);

    const h = birthHour.padStart(2, '0');
    const m = birthMinute.padStart(2, '0');
    const birthTime = `${h}:${m}`;

    try {
      await register({
        email,
        password,
        birth_date: birthDate,
        birth_time: birthTime,
        birth_place: birthPlace,
        birth_country: birthCountry,
      });
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'inscription');
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    borderColor: 'rgba(197,160,89,0.3)',
    color: 'var(--pa-body)',
    background: 'transparent',
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20 pb-12" data-testid="register-page">
      <SEO path="/inscription" />
      <div className="w-full max-w-md">
        <div className="rounded-2xl p-8 md:p-10" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(197,160,89,0.15)', backdropFilter: 'blur(16px)' }}>
          <div className="flex items-center justify-center gap-3 mb-2">
            <UserPlus className="w-5 h-5" style={{ color: '#C5A059' }} strokeWidth={1.5} />
            <h1 className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
              Créer un compte
            </h1>
          </div>
          <p className="text-center text-sm mb-6" style={{ color: 'var(--pa-muted)' }}>
            {step === 1 ? 'Étape 1/2 — Identifiants' : 'Étape 2/2 — Profil astrologique'}
          </p>

          {/* Step indicator */}
          <div className="flex gap-2 mb-6 justify-center">
            <div className="h-1 w-12 rounded-full" style={{ background: '#C5A059' }} />
            <div className="h-1 w-12 rounded-full" style={{ background: step === 2 ? '#C5A059' : 'rgba(197,160,89,0.2)' }} />
          </div>

          {error && (
            <div className="mb-6 p-3 rounded-lg text-sm text-center" style={{ background: 'rgba(220,38,38,0.1)', border: '1px solid rgba(220,38,38,0.3)', color: '#fca5a5' }} data-testid="register-error">
              {error}
            </div>
          )}

          {step === 1 ? (
            <div className="space-y-5">
              <div>
                <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Email</label>
                <input
                  type="email" value={email} onChange={e => setEmail(e.target.value)} required
                  className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors"
                  style={inputStyle}
                  onFocus={e => e.target.style.borderColor = '#C5A059'}
                  onBlur={e => e.target.style.borderColor = 'rgba(197,160,89,0.3)'}
                  data-testid="register-email-input"
                />
              </div>
              <div className="relative">
                <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Mot de passe</label>
                <input
                  type={showPw ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} required
                  className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors pr-10"
                  style={inputStyle}
                  onFocus={e => e.target.style.borderColor = '#C5A059'}
                  onBlur={e => e.target.style.borderColor = 'rgba(197,160,89,0.3)'}
                  data-testid="register-password-input"
                />
                <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-0 bottom-2" style={{ color: 'var(--pa-muted)' }}>
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              <button
                onClick={goStep2}
                className="w-full py-3 mt-4 text-xs uppercase tracking-widest rounded-full flex items-center justify-center gap-2 transition-all duration-500"
                style={{ border: '1px solid rgba(197,160,89,0.5)', color: '#C5A059', letterSpacing: '0.12em' }}
                data-testid="register-step2-button"
              >
                Continuer <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Date de naissance *</label>
                <input
                  type="date" value={birthDate} onChange={e => setBirthDate(e.target.value)} required
                  className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors"
                  style={inputStyle}
                  data-testid="register-birth-date"
                />
              </div>
              <div>
                <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Heure de naissance</label>
                <div className="flex items-center gap-2">
                  <input
                    type="number" min="0" max="23" placeholder="HH"
                    value={birthHour}
                    onChange={e => {
                      const v = e.target.value;
                      if (v === '' || (parseInt(v) >= 0 && parseInt(v) <= 23)) setBirthHour(v);
                    }}
                    className="w-20 bg-transparent border-b py-2 text-base text-center outline-none transition-colors"
                    style={inputStyle}
                    data-testid="register-birth-hour"
                  />
                  <span style={{ color: 'var(--pa-muted)', fontSize: '1.2rem' }}>:</span>
                  <input
                    type="number" min="0" max="59" placeholder="MM"
                    value={birthMinute}
                    onChange={e => {
                      const v = e.target.value;
                      if (v === '' || (parseInt(v) >= 0 && parseInt(v) <= 59)) setBirthMinute(v);
                    }}
                    className="w-20 bg-transparent border-b py-2 text-base text-center outline-none transition-colors"
                    style={inputStyle}
                    data-testid="register-birth-minute"
                  />
                  <span className="text-xs ml-2" style={{ color: 'var(--pa-muted)' }}>(format 24h)</span>
                </div>
              </div>
              <div>
                <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Lieu de naissance *</label>
                <input
                  type="text" value={birthPlace} onChange={e => setBirthPlace(e.target.value)} required
                  placeholder="ex: Paris"
                  className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors"
                  style={inputStyle}
                  onFocus={e => e.target.style.borderColor = '#C5A059'}
                  onBlur={e => e.target.style.borderColor = 'rgba(197,160,89,0.3)'}
                  data-testid="register-birth-place"
                />
              </div>
              <div>
                <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Pays</label>
                <select
                  value={birthCountry} onChange={e => setBirthCountry(e.target.value)}
                  className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors"
                  style={{ ...inputStyle, background: '#0C0918' }}
                  data-testid="register-birth-country"
                >
                  {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              <div className="flex gap-3 mt-4">
                <button
                  type="button" onClick={() => setStep(1)}
                  className="flex-1 py-3 text-xs uppercase tracking-widest rounded-full flex items-center justify-center gap-2 transition-all duration-500"
                  style={{ border: '1px solid rgba(197,160,89,0.2)', color: 'var(--pa-muted)', letterSpacing: '0.12em' }}
                  data-testid="register-back-button"
                >
                  <ChevronLeft className="w-4 h-4" /> Retour
                </button>
                <button
                  type="submit" disabled={loading}
                  className="flex-1 py-3 text-xs uppercase tracking-widest rounded-full transition-all duration-500"
                  style={{ border: '1px solid rgba(197,160,89,0.5)', color: loading ? 'var(--pa-muted)' : '#C5A059', letterSpacing: '0.12em' }}
                  data-testid="register-submit-button"
                >
                  {loading ? 'Création...' : 'Créer mon compte'}
                </button>
              </div>
            </form>
          )}

          <p className="text-center mt-6 text-sm" style={{ color: 'var(--pa-muted)' }}>
            Déjà un compte ?{' '}
            <Link to="/connexion" className="transition-colors hover:opacity-80" style={{ color: '#C5A059' }} data-testid="register-login-link">
              Se connecter
            </Link>
          </p>

          {step === 1 && (
            <div className="mt-6 p-4 rounded-xl text-center" style={{ background: 'rgba(197,160,89,0.06)', border: '1px solid rgba(197,160,89,0.1)' }}>
              <p className="text-sm" style={{ color: '#C5A059' }} data-testid="register-bonus-info">
                50 crédits offerts à l'inscription
              </p>
            </div>
          )}

          {/* Guest access */}
          <div className="mt-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex-1 h-px" style={{ background: 'rgba(197,160,89,0.15)' }} />
              <span className="text-xs" style={{ color: 'var(--pa-muted)' }}>ou</span>
              <div className="flex-1 h-px" style={{ background: 'rgba(197,160,89,0.15)' }} />
            </div>
            <button
              onClick={() => { loginAsGuest(); navigate('/'); }}
              className="w-full py-2.5 text-xs uppercase tracking-widest rounded-full flex items-center justify-center gap-2 transition-all duration-500"
              style={{ border: '1px solid rgba(52,211,153,0.4)', color: '#34D399', background: 'rgba(52,211,153,0.06)', letterSpacing: '0.12em' }}
              data-testid="register-guest-button"
            >
              <Gift className="w-4 h-4" />
              Accès gratuit sans inscription
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
