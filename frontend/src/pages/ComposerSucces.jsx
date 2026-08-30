/* eslint-disable react/no-unescaped-entities */
/**
 * ComposerSucces.jsx — Page merci /composer/succes (2026-03)
 *
 * Poll léger sur payment_transactions pour montrer l'état :
 *  1. Paiement reçu
 *  2. Composition du livre
 *  3. Email envoyé
 */
import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function ComposerSucces() {
  const [sp] = useSearchParams();
  const sessionId = sp.get('session_id');
  const [tx, setTx] = useState(null);
  const [error, setError] = useState(null);
  const [attempts, setAttempts] = useState(0);

  useEffect(() => {
    if (!sessionId) return;
    let cancelled = false;
    let timer;
    async function poll() {
      try {
        const r = await fetch(`${API}/api/theme-natal-oneshot/status?session_id=${sessionId}`);
        if (r.ok) {
          const data = await r.json();
          if (!cancelled) {
            setTx(data);
            if (!data.email_sent && attempts < 40) {
              timer = setTimeout(poll, 4000);
              setAttempts((a) => a + 1);
            }
          }
        } else if (!cancelled) {
          setError("Impossible de récupérer l'état de votre commande.");
        }
      } catch {
        if (!cancelled) setError('Connexion instable — nous continuons à composer votre livre en arrière-plan.');
      }
    }
    poll();
    return () => { cancelled = true; clearTimeout(timer); };
  }, [sessionId, attempts]);

  return (
    <PsPageShell background="dark">
      <SEO
        path="/composer/succes"
        title="Merci · Votre livre est en composition"
        description="Merci pour votre commande. Nous composons votre livre — vous le recevrez par email dans quelques minutes."
        noindex
      />
      <div data-testid="composer-succes" style={wrap}>
        <p style={eyebrow}>MERCI</p>
        <h1 style={h1Style}>Votre livre est en train de s'écrire.</h1>
        <p style={bodyStyle}>
          Nous avons reçu votre paiement. Notre moteur compose maintenant votre exemplaire —
          il arrive dans votre boîte email dans quelques minutes.
        </p>

        <ul style={statusList}>
          <StatusItem done label="Paiement reçu" />
          <StatusItem done={!!tx?.pdf_ready} label={tx?.pdf_ready ? 'Livre composé' : 'Composition en cours'} pending={!tx?.pdf_ready}/>
          <StatusItem done={!!tx?.email_sent} label={tx?.email_sent ? 'Email envoyé' : 'Envoi de l\'email'} pending={!tx?.email_sent}/>
        </ul>

        {error && <p style={errorBox}>{error}</p>}

        <p style={{ ...bodyStyle, marginTop: 40 }}>
          Vous pouvez fermer cette page — nous vous prévenons dès que tout est prêt.
          Un souci ? Écrivez à <a href="mailto:contact@plume-astrale.fr" style={linkGold}>contact@plume-astrale.fr</a>.
        </p>
        <Link to="/" style={{ ...ctaGhost, marginTop: 24, textDecoration: 'none', display: 'inline-block' }}>
          Retour à l'accueil
        </Link>
      </div>
    </PsPageShell>
  );
}

function StatusItem({ done, pending, label }) {
  return (
    <li style={{ ...statusItem, opacity: done ? 1 : pending ? 0.7 : 0.4 }}>
      <span style={{ ...statusDot, background: done ? '#D4AF37' : pending ? 'rgba(212,175,55,0.4)' : 'rgba(245,238,224,0.15)' }}>
        {done ? '✓' : pending ? '…' : ''}
      </span>
      <span>{label}</span>
    </li>
  );
}

const wrap = { maxWidth: 720, margin: '0 auto', padding: '80px 24px', color: '#F5EEE0', fontFamily: '"Cormorant Garamond", serif', textAlign: 'center', lineHeight: 1.65 };
const eyebrow = { fontFamily: '"Cinzel", serif', fontSize: '0.75rem', letterSpacing: 3, color: '#D4AF37', margin: 0 };
const h1Style = { fontFamily: '"Playfair Display", serif', fontSize: 'clamp(2.2rem, 5vw, 3rem)', color: '#F5EEE0', margin: '14px 0 20px', fontWeight: 400, lineHeight: 1.2 };
const bodyStyle = { fontSize: '1.1rem', color: '#F5EEE0', margin: '12px 0' };
const statusList = { listStyle: 'none', padding: 0, margin: '40px auto', maxWidth: 420, display: 'grid', gap: 14, textAlign: 'left' };
const statusItem = { display: 'flex', alignItems: 'center', gap: 14, padding: '12px 16px', background: 'rgba(15,26,60,0.5)', border: '1px solid rgba(212,175,55,0.22)', borderRadius: 4 };
const statusDot = { width: 26, height: 26, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0F1A3C', fontFamily: '"Cinzel", serif', fontWeight: 700, fontSize: '0.8rem' };
const errorBox = { padding: '12px 14px', background: 'rgba(232,144,107,0.14)', border: '1px solid rgba(232,144,107,0.35)', borderRadius: 4, color: '#F5EEE0', marginTop: 20 };
const linkGold = { color: '#D4AF37', textDecoration: 'underline', textDecorationColor: 'rgba(212,175,55,0.4)' };
const ctaGhost = { display: 'inline-block', padding: '12px 22px', background: 'transparent', color: '#F5EEE0', border: '1px solid rgba(212,175,55,0.35)', borderRadius: 4, fontFamily: '"Cinzel", serif', fontSize: '0.82rem', letterSpacing: 2, cursor: 'pointer' };
