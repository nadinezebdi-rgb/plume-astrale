import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Lock, Eye, EyeOff, Check, Loader2 } from 'lucide-react';
import SEO from '../components/SEO';
import { supabase } from '../lib/supabase';

export default function ReinitialiserMotDePasse() {
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');
  const [sessionReady, setSessionReady] = useState(false);

  // Supabase met l'access_token dans l'URL fragment (#access_token=...) — detectSessionInUrl s'en occupe.
  useEffect(() => {
    let mounted = true;
    (async () => {
      const { data } = await supabase.auth.getSession();
      if (mounted) {
        if (data?.session) {
          setSessionReady(true);
        } else {
          // Attendre 1.5s pour que detectSessionInUrl parse le fragment
          setTimeout(async () => {
            const { data: d2 } = await supabase.auth.getSession();
            if (mounted) setSessionReady(!!d2?.session);
          }, 1500);
        }
      }
    })();
    return () => { mounted = false; };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password.length < 8) { setError('Le mot de passe doit contenir au moins 8 caractères.'); return; }
    if (password !== confirm) { setError('Les deux mots de passe ne correspondent pas.'); return; }
    setError(''); setLoading(true);
    try {
      const { error: err } = await supabase.auth.updateUser({ password });
      if (err) throw err;
      setDone(true);
      setTimeout(() => navigate('/connexion'), 2500);
    } catch (err) {
      setError(err?.message || 'Impossible de mettre à jour le mot de passe. Demandez un nouveau lien.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20 pb-12" data-testid="reset-password-page">
      <SEO path="/reinitialiser-mot-de-passe" />
      <div className="w-full max-w-md">
        <div className="rounded-2xl p-8 md:p-10" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.15)', backdropFilter: 'blur(16px)' }}>

          <div className="flex items-center justify-center gap-3 mb-3">
            <Lock className="w-5 h-5" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
            <h1 className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
              Nouveau mot de passe
            </h1>
          </div>
          <p className="text-center text-sm mb-8" style={{ color: 'var(--pa-muted)' }}>
            Choisissez un nouveau mot de passe pour votre compte.
          </p>

          {done ? (
            <div className="text-center" data-testid="reset-success">
              <div className="w-12 h-12 mx-auto mb-4 rounded-full flex items-center justify-center" style={{ background: 'rgba(74,222,128,0.12)', border: '1px solid rgba(74,222,128,0.35)' }}>
                <Check className="w-5 h-5" strokeWidth={2} style={{ color: '#4ADE80' }} />
              </div>
              <p className="text-base mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)' }}>
                Mot de passe mis à jour
              </p>
              <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
                Redirection vers la page de connexion...
              </p>
            </div>
          ) : !sessionReady ? (
            <div className="text-center py-6" data-testid="reset-no-session">
              <Loader2 className="w-5 h-5 mx-auto animate-spin mb-3" style={{ color: '#D4AF37' }} />
              <p className="text-sm mb-4" style={{ color: 'var(--pa-muted)' }}>
                Vérification du lien...
              </p>
              <p className="text-xs mb-4" style={{ color: 'var(--pa-muted)' }}>
                Si vous arrivez ici sans avoir cliqué sur le lien de l'e-mail, demandez un nouveau lien.
              </p>
              <Link to="/mot-de-passe-oublie" className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full" style={{ border: '1px solid rgba(212,175,55,0.5)', color: '#D4AF37' }}>
                Demander un nouveau lien
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="p-3 rounded-lg text-sm text-center" style={{ background: 'rgba(220,38,38,0.1)', border: '1px solid rgba(220,38,38,0.3)', color: '#fca5a5' }} data-testid="reset-error">
                  {error}
                </div>
              )}
              <div className="relative">
                <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Nouveau mot de passe</label>
                <input
                  type={showPw ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  minLength={8}
                  autoFocus
                  className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors pr-10"
                  style={{ borderColor: 'rgba(212,175,55,0.3)', color: 'var(--pa-body)' }}
                  onFocus={e => e.target.style.borderColor = '#D4AF37'}
                  onBlur={e => e.target.style.borderColor = 'rgba(212,175,55,0.3)'}
                  data-testid="reset-password-input"
                />
                <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-0 bottom-2" style={{ color: 'var(--pa-muted)' }}>
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              <div>
                <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Confirmer</label>
                <input
                  type={showPw ? 'text' : 'password'}
                  value={confirm}
                  onChange={e => setConfirm(e.target.value)}
                  required
                  minLength={8}
                  className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors"
                  style={{ borderColor: 'rgba(212,175,55,0.3)', color: 'var(--pa-body)' }}
                  onFocus={e => e.target.style.borderColor = '#D4AF37'}
                  onBlur={e => e.target.style.borderColor = 'rgba(212,175,55,0.3)'}
                  data-testid="reset-confirm-input"
                />
              </div>
              <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
                · Minimum 8 caractères · Privilégiez une phrase ou un mélange de lettres, chiffres et symboles.
              </p>
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 mt-2 text-xs uppercase tracking-widest rounded-full transition-all duration-500 flex items-center justify-center gap-2 disabled:opacity-60"
                style={{ border: '1px solid rgba(212,175,55,0.5)', color: '#D4AF37', background: 'transparent', letterSpacing: '0.12em' }}
                data-testid="reset-submit-button"
              >
                {loading ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Mise à jour...</> : 'Mettre à jour'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
