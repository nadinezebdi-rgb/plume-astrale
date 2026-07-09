import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, Check, Loader2 } from 'lucide-react';
import SEO from '../components/SEO';
import { supabase } from '../lib/supabase';

export default function MotDePasseOublie() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) { setError('Veuillez renseigner votre adresse e-mail.'); return; }
    setError(''); setLoading(true);
    try {
      const redirectTo = `${window.location.origin}/reinitialiser-mot-de-passe`;
      const { error: err } = await supabase.auth.resetPasswordForEmail(email.trim(), { redirectTo });
      if (err) throw err;
      setSent(true);
    } catch (err) {
      setError(err?.message || "Impossible d'envoyer l'e-mail. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20 pb-12" data-testid="forgot-password-page">
      <SEO path="/mot-de-passe-oublie" />
      <div className="w-full max-w-md">
        <div className="rounded-2xl p-8 md:p-10" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(184,150,31,0.15)', backdropFilter: 'blur(16px)' }}>

          <Link to="/connexion" className="text-xs flex items-center gap-2 mb-6 hover:opacity-80" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }} data-testid="back-to-login">
            <ArrowLeft className="w-3.5 h-3.5" /> Retour à la connexion
          </Link>

          <div className="flex items-center justify-center gap-3 mb-3">
            <Mail className="w-5 h-5" style={{ color: '#B8961F' }} strokeWidth={1.5} />
            <h1 className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
              Mot de passe oublié
            </h1>
          </div>
          <p className="text-center text-sm mb-8" style={{ color: 'var(--pa-muted)' }}>
            Indiquez votre e-mail, nous vous enverrons un lien sécurisé pour réinitialiser votre mot de passe.
          </p>

          {sent ? (
            <div className="text-center" data-testid="forgot-success">
              <div className="w-12 h-12 mx-auto mb-4 rounded-full flex items-center justify-center" style={{ background: 'rgba(74,222,128,0.12)', border: '1px solid rgba(74,222,128,0.35)' }}>
                <Check className="w-5 h-5" strokeWidth={2} style={{ color: '#4ADE80' }} />
              </div>
              <p className="text-base mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)' }}>
                E-mail envoyé
              </p>
              <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
                Si un compte existe pour <strong>{email}</strong>, vous recevrez le lien dans quelques instants.
                Vérifiez aussi vos courriers indésirables.
              </p>
              <Link to="/connexion" className="inline-block mt-6 text-xs uppercase tracking-widest px-6 py-2.5 rounded-full" style={{ border: '1px solid rgba(184,150,31,0.5)', color: '#B8961F' }}>
                Retour
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="p-3 rounded-lg text-sm text-center" style={{ background: 'rgba(220,38,38,0.1)', border: '1px solid rgba(220,38,38,0.3)', color: '#fca5a5' }} data-testid="forgot-error">
                  {error}
                </div>
              )}
              <div>
                <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Adresse e-mail</label>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  autoFocus
                  placeholder="vous@exemple.com"
                  className="w-full bg-transparent border-b py-2 text-base outline-none transition-colors"
                  style={{ borderColor: 'rgba(184,150,31,0.3)', color: 'var(--pa-body)' }}
                  onFocus={e => e.target.style.borderColor = '#B8961F'}
                  onBlur={e => e.target.style.borderColor = 'rgba(184,150,31,0.3)'}
                  data-testid="forgot-email-input"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 mt-2 text-xs uppercase tracking-widest rounded-full transition-all duration-500 flex items-center justify-center gap-2 disabled:opacity-60"
                style={{ border: '1px solid rgba(184,150,31,0.5)', color: '#B8961F', background: 'transparent', letterSpacing: '0.12em' }}
                data-testid="forgot-submit-button"
              >
                {loading ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Envoi en cours...</> : 'Envoyer le lien'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
