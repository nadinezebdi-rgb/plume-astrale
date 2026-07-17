import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { Check, Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Desabonnement = () => {
  const [params] = useSearchParams();
  const email = params.get('email') || '';
  const [status, setStatus] = useState('loading'); // loading | done | error
  const [msg, setMsg] = useState('');

  useEffect(() => {
    if (!email) { setStatus('error'); setMsg('Lien de désabonnement invalide.'); return; }
    (async () => {
      try {
        const res = await axios.get(`${API_URL}/api/oracle/unsubscribe`, { params: { email } });
        setStatus('done');
        setMsg(res.data?.message || 'Vous êtes désabonné(e).');
      } catch (e) {
        setStatus('error');
        setMsg(e.response?.data?.detail || 'Impossible de traiter votre demande.');
      }
    })();
  }, [email]);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '100px 20px' }} data-testid="unsub-page">
      <div style={{
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(212,175,55,0.18)',
        borderRadius: 18, padding: 36, maxWidth: 460, width: '100%',
        textAlign: 'center',
      }}>
        {status === 'loading' && (
          <>
            <Loader2 style={{ width: 28, height: 28, color: '#D4AF37', margin: '0 auto 16px' }} className="animate-spin" />
            <p style={{ color: 'rgba(184,176,200,0.85)' }}>Désabonnement en cours...</p>
          </>
        )}
        {status === 'done' && (
          <>
            <div style={{ width: 56, height: 56, borderRadius: '50%', background: 'rgba(74,222,128,0.12)', border: '1px solid rgba(74,222,128,0.35)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 18 }}>
              <Check style={{ width: 24, height: 24, color: '#4ADE80' }} strokeWidth={2} />
            </div>
            <h1 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 26, color: '#F5EEE0', fontWeight: 300, marginBottom: 12 }}>
              C&apos;est fait.
            </h1>
            <p style={{ color: 'rgba(184,176,200,0.85)', fontSize: 15, lineHeight: 1.6, marginBottom: 24 }}>{msg}</p>
          </>
        )}
        {status === 'error' && (
          <>
            <h1 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 24, color: '#F5EEE0', fontWeight: 300, marginBottom: 12 }}>
              Désolée
            </h1>
            <p style={{ color: 'rgba(252,165,165,0.9)', fontSize: 14, marginBottom: 20 }}>{msg}</p>
          </>
        )}
        <Link to="/" style={{ display: 'inline-block', marginTop: 16, fontSize: 11, letterSpacing: '0.14em', color: '#D4AF37', textTransform: 'uppercase', textDecoration: 'none', border: '1px solid rgba(212,175,55,0.4)', padding: '10px 24px', borderRadius: 999 }}>
          Retour à l&apos;accueil
        </Link>
      </div>
    </div>
  );
};

export default Desabonnement;
