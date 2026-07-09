import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Coins, LogIn, ArrowRight } from 'lucide-react';

/**
 * CreditGate — wraps service content.
 * If not authenticated → shows login prompt.
 * If insufficient credits → shows buy prompt.
 * Otherwise renders children.
 *
 * Props:
 *   serviceId  — key in SERVICE_COSTS (for useCredits)
 *   cost       — display cost in credits
 *   label      — service name for display
 *   onUnlock   — callback when credits are deducted (or free draw granted)
 *   children   — the actual service UI
 *   bypass     — if true, skip gate (e.g. free preview)
 */
export default function CreditGate({ serviceId, cost, label, onUnlock, children, bypass }) {
  const { isAuthenticated, creditBalance, useCredits } = useAuth();
  const navigate = useNavigate();
  const [unlocked, setUnlocked] = React.useState(false);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  if (bypass || unlocked) return <>{children}</>;

  // Not authenticated
  if (!isAuthenticated) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-6 text-center" data-testid="credit-gate-login">
        <LogIn className="w-8 h-8 mb-4" style={{ color: '#B8961F' }} strokeWidth={1.5} />
        <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
          Connexion requise
        </h2>
        <p className="text-sm mb-6 max-w-sm" style={{ color: 'var(--pa-muted)' }}>
          Connectez-vous pour acc&eacute;der &agrave; {label}.
          <br />20 cr&eacute;dits offerts &agrave; l'inscription.
        </p>
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={() => navigate('/connexion')}
            className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full transition-all duration-300"
            style={{ border: '1px solid rgba(184,150,31,0.5)', color: '#B8961F', letterSpacing: '0.1em' }}
            data-testid="gate-login-btn"
          >
            Se connecter
          </button>
          <button
            onClick={() => navigate('/inscription')}
            className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full transition-all duration-300"
            style={{ border: '1px solid rgba(184,150,31,0.3)', color: '#B8961F', background: 'rgba(184,150,31,0.08)', letterSpacing: '0.1em' }}
            data-testid="gate-register-btn"
          >
            Cr&eacute;er un compte
          </button>
        </div>
      </div>
    );
  }

  const handleUnlock = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await useCredits(serviceId);
      setUnlocked(true);
      if (onUnlock) onUnlock(result);
    } catch (err) {
      const detail = err.response?.data?.detail || '';
      if (detail.includes('insuffisants')) {
        setError('insufficient');
      } else {
        setError(detail || 'Erreur');
      }
    } finally {
      setLoading(false);
    }
  };

  // Insufficient credits
  if (error === 'insufficient' || (cost > 0 && creditBalance < cost)) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-6 text-center" data-testid="credit-gate-insufficient">
        <Coins className="w-8 h-8 mb-4" style={{ color: '#B8961F' }} strokeWidth={1.5} />
        <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
          Cr&eacute;dits insuffisants
        </h2>
        <p className="text-sm mb-2" style={{ color: 'var(--pa-muted)' }}>
          {label} co&ucirc;te <span style={{ color: '#B8961F', fontWeight: 600 }}>{cost} cr&eacute;dits</span>.
        </p>
        <p className="text-sm mb-6" style={{ color: 'var(--pa-muted)' }}>
          Votre solde : <span style={{ color: '#B8961F' }}>{creditBalance} cr&eacute;dits</span>
        </p>
        <button
          onClick={() => navigate('/acheter-credits')}
          className="flex items-center gap-2 text-xs uppercase tracking-widest px-6 py-2.5 rounded-full transition-all duration-500"
          style={{ border: '1px solid #B8961F', color: '#0C0918', background: '#B8961F', letterSpacing: '0.1em', fontWeight: 600 }}
          data-testid="gate-buy-credits-btn"
        >
          Acheter des cr&eacute;dits <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  }

  // Has enough credits — show unlock button
  return (
    <div className="flex flex-col items-center justify-center py-12 px-6 text-center" data-testid="credit-gate-unlock">
      <Coins className="w-7 h-7 mb-3" style={{ color: '#B8961F' }} strokeWidth={1.5} />
      <p className="text-sm mb-1" style={{ color: 'var(--pa-body)' }}>
        {label}
      </p>
      <p className="text-xs mb-5" style={{ color: 'var(--pa-muted)' }}>
        Co&ucirc;t : <span style={{ color: '#B8961F' }}>{cost > 0 ? `${cost} cr\u00e9dits` : 'Gratuit'}</span>
        {' '}&middot;{' '}Solde : <span style={{ color: '#B8961F' }}>{creditBalance} cr&eacute;dits</span>
      </p>
      {error && error !== 'insufficient' && (
        <p className="text-xs mb-3" style={{ color: '#fca5a5' }}>{error}</p>
      )}
      <button
        onClick={handleUnlock}
        disabled={loading}
        className="text-xs uppercase tracking-widest px-8 py-2.5 rounded-full transition-all duration-500"
        style={{
          border: '1px solid rgba(184,150,31,0.5)',
          color: loading ? 'var(--pa-muted)' : '#B8961F',
          letterSpacing: '0.1em',
        }}
        data-testid="gate-unlock-btn"
      >
        {loading ? 'Traitement...' : cost > 0 ? `Utiliser ${cost} cr\u00e9dits` : 'Commencer'}
      </button>
    </div>
  );
}
