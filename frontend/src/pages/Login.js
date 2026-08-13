import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogIn, Eye, EyeOff } from 'lucide-react';
import SEO from '../components/SEO';
import { event as trackEvent } from '@/lib/analytics';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

const handleSubmit = async (e) => {
  e.preventDefault();

  if (!email || !password) {
    setError("Veuillez remplir tous les champs");
    return;
  }

  setError('');
  setLoading(true);

  try {
    await login(email, password);

    trackEvent('login_success');

    // redirection après connexion : respecte ?redirect=... sinon /mon-compte
    const params = new URLSearchParams(window.location.search);
    const redirect = params.get('redirect');
    navigate(redirect || "/mon-compte");

  } catch (err) {
    console.error("LOGIN ERROR:", err);
    setError("Email ou mot de passe incorrect");
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20 pb-12" data-testid="login-page">
      <SEO path="/connexion" />
      <div className="w-full max-w-md">
        <div className="rounded-2xl p-8 md:p-10" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.15)', backdropFilter: 'blur(16px)' }}>
          <div className="flex items-center justify-center gap-3 mb-8">
            <LogIn className="w-5 h-5" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
            <h1 className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
              Connexion
            </h1>
          </div>

          {error && (
            <div className="mb-6 p-3 rounded-lg text-sm text-center" style={{ background: 'rgba(220,38,38,0.1)', border: '1px solid rgba(220,38,38,0.3)', color: '#fca5a5' }} data-testid="login-error">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5" autoComplete="off">
            <div>
              <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Adresse e-mail</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                autoComplete="off"
                className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors"
                style={{ borderColor: 'rgba(212,175,55,0.3)', color: 'var(--pa-body)' }}
                onFocus={e => e.target.style.borderColor = '#D4AF37'}
                onBlur={e => e.target.style.borderColor = 'rgba(212,175,55,0.3)'}
                data-testid="login-email-input"
              />
            </div>
            <div className="relative">
              <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Mot de passe</label>
              <input
                type={showPw ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                autoComplete="new-password"
                className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors pr-10"
                style={{ borderColor: 'rgba(212,175,55,0.3)', color: 'var(--pa-body)' }}
                onFocus={e => e.target.style.borderColor = '#D4AF37'}
                onBlur={e => e.target.style.borderColor = 'rgba(212,175,55,0.3)'}
                data-testid="login-password-input"
              />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-0 bottom-2" style={{ color: 'var(--pa-muted)' }}>
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>

            <div className="flex justify-end">
              <Link to="/mot-de-passe-oublie" className="text-xs hover:opacity-80 transition-opacity" style={{ color: 'var(--pa-muted)', letterSpacing: '0.05em' }} data-testid="login-forgot-link">
                Mot de passe oublié ?
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 mt-4 text-xs uppercase tracking-widest rounded-full transition-all duration-500"
              style={{
                border: '1px solid rgba(212,175,55,0.5)',
                color: loading ? 'var(--pa-muted)' : '#D4AF37',
                background: 'transparent',
                letterSpacing: '0.12em',
              }}
              data-testid="login-submit-button"
            >
              {loading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>

          <p className="text-center mt-6 text-sm" style={{ color: 'var(--pa-muted)' }}>
            Pas encore de compte ?{' '}
            <Link to="/inscription" className="transition-colors hover:opacity-80" style={{ color: '#D4AF37' }} data-testid="login-register-link">
              Créer un compte
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
