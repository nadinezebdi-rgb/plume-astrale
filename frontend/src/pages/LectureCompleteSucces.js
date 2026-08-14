import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

export default function LectureCompleteSucces() {
  const [params] = useSearchParams();
  const sessionId = params.get('session_id');
  const [status, setStatus] = useState('loading');
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!sessionId) {
      setStatus('missing');
      return;
    }
    let cancel = false;
    let tries = 0;
    const poll = async () => {
      try {
        const res = await fetch(`${API}/api/lecture-complete/status?session_id=${sessionId}`);
        const j = await res.json();
        if (cancel) return;
        setData(j);
        if (j.payment_status === 'paid' || j.status === 'completed') {
          setStatus('paid');
          return;
        }
        tries += 1;
        if (tries < 30) setTimeout(poll, 3000);
        else setStatus('timeout');
      } catch (e) {
        if (!cancel) setStatus('error');
      }
    };
    poll();
    return () => { cancel = true; };
  }, [sessionId]);

  return (
    <>
      <SEO path="/lecture-complete/succes" title="Merci · Plume Astrale" />
      <div
        style={{
          background: '#0b1020',
          color: '#e8e6f0',
          minHeight: '100vh',
          fontFamily: 'Georgia, serif',
          padding: '80px 20px 40px',
          textAlign: 'center',
        }}
        data-testid="lecture-complete-succes"
      >
        <div style={{ maxWidth: 620, margin: '0 auto' }}>
          <h1 style={{ color: '#d9b26a', fontSize: '2.2rem', marginBottom: 20 }}>
            ✦ Ta lecture est en route
          </h1>
          {status === 'loading' && (
            <p style={{ color: '#b8b4c9', fontSize: '1.1rem' }}>
              On vérifie ton paiement… ne ferme pas cette page.
            </p>
          )}
          {status === 'paid' && (
            <>
              <p style={{ fontSize: '1.15rem', lineHeight: 1.7 }}>
                Merci profondément pour ta confiance. Soléna a bien reçu ta commande.
                <br />
                Tu recevras un email de confirmation à <strong>{data?.email || 'ton adresse'}</strong>
                {' '}dans les prochaines minutes, puis ta lecture complète sous 48h ouvrées.
              </p>
              <p style={{ marginTop: 24, color: '#b8b4c9' }}>
                Une question ? Écris à <a href="mailto:solena@plume-astrale.fr" style={{ color: '#d9b26a' }}>solena@plume-astrale.fr</a>
              </p>
            </>
          )}
          {status === 'timeout' && (
            <p style={{ color: '#f87171' }}>
              La confirmation prend plus de temps que prévu. Vérifie tes emails dans quelques minutes.
              Si tu vois un débit sur ta carte mais rien ne bouge, contacte le support Plume Astrale.
            </p>
          )}
          {status === 'error' && (
            <p style={{ color: '#f87171' }}>
              Impossible de vérifier ta commande. Écris au support Plume Astrale avec le numéro de session : <code>{sessionId}</code>
            </p>
          )}
          {status === 'missing' && (
            <p style={{ color: '#f87171' }}>Aucune session détectée.</p>
          )}
          <div style={{ marginTop: 40 }}>
            <Link
              to="/"
              style={{
                display: 'inline-block',
                background: 'transparent',
                color: '#d9b26a',
                border: '1px solid #d9b26a',
                padding: '14px 28px',
                borderRadius: 40,
                textDecoration: 'none',
                letterSpacing: '.5px',
              }}
              data-testid="lecture-succes-home"
            >
              Retour à l'accueil
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
