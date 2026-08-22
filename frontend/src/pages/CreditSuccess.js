import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { CheckCircle, Loader2 } from 'lucide-react';
import axios from 'axios';
import { revenue, EVENTS } from '@/lib/analytics';

const API = process.env.REACT_APP_BACKEND_URL;

export default function CreditSuccess() {
  const { token, refreshBalance, creditBalance } = useAuth();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('polling'); // polling | success | error
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    if (!sessionId || !token) return;
    let attempts = 0;
    const maxAttempts = 8;

    const poll = async () => {
      try {
        const res = await axios.get(`${API}/api/payments/status/${sessionId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.data.payment_status === 'paid') {
          // Pixel client : rejoue l'event_id du backend pour dédup avec CAPI.
          // Garde-fou : une fois par session_id, même si l'utilisateur refresh.
          try {
            const key = `pa_purchase_tracked_${sessionId}`;
            if (!sessionStorage.getItem(key)) {
              sessionStorage.setItem(key, '1');
              revenue(EVENTS.CREDIT_PURCHASE, res.data.amount, {
                eventID: res.data.capi_event_id,
                credits: res.data.credits,
              });
            }
          } catch (_e) { /* sessionStorage indisponible */ }
          await refreshBalance();
          setStatus('success');
          return;
        }
      } catch { /* continue polling */ }

      attempts++;
      if (attempts < maxAttempts) {
        setTimeout(poll, 2000);
      } else {
        setStatus('error');
      }
    };
    poll();
  }, [sessionId, token, refreshBalance]);

  if (status === 'polling') {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 pt-20" data-testid="credit-success-polling">
        <div className="text-center">
          <Loader2 className="w-8 h-8 mx-auto mb-4 animate-spin" style={{ color: '#D4AF37' }} />
          <p className="text-base" style={{ color: 'var(--pa-body)' }}>Vérification du paiement en cours...</p>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 pt-20" data-testid="credit-success-error">
        <div className="text-center max-w-md">
          <p className="text-base mb-4" style={{ color: '#fca5a5' }}>La vérification du paiement a expiré. Vos crédits seront ajoutés sous peu.</p>
          <button onClick={() => navigate('/acheter-credits')} className="btn-editorial text-xs px-6 py-2.5">Retour</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20" data-testid="credit-success-page">
      <div className="text-center max-w-md rounded-2xl p-8 md:p-10" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.15)', backdropFilter: 'blur(16px)' }}>
        <CheckCircle className="w-12 h-12 mx-auto mb-4" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
        <h1 className="text-2xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
          Paiement confirmé
        </h1>
        <p className="text-base mb-2" style={{ color: 'var(--pa-body)' }}>
          Vos crédits ont été ajoutés à votre compte.
        </p>
        <p className="text-lg mb-6" style={{ color: '#D4AF37' }} data-testid="new-balance">
          Solde actuel : {creditBalance} crédits
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button onClick={() => navigate('/')} className="btn-editorial text-xs px-6 py-2.5" data-testid="go-home-btn">Accueil</button>
          <Link to="/acheter-credits" className="btn-editorial text-xs px-6 py-2.5 inline-block" data-testid="buy-more-btn">Acheter encore</Link>
        </div>
      </div>
    </div>
  );
}
