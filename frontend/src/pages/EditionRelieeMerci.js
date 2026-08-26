/* eslint-disable react/no-unescaped-entities */
import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function EditionRelieeMerci() {
  const [params] = useSearchParams();
  const sessionId = params.get('session_id');
  const [state, setState] = useState({ loading: true, status: null });

  useEffect(() => {
    if (!sessionId) return;
    let cancelled = false;
    let attempts = 0;

    const poll = async () => {
      attempts += 1;
      try {
        const r = await fetch(`${API}/api/edition-reliee/status?session_id=${sessionId}`);
        if (!r.ok) throw new Error('http_' + r.status);
        const data = await r.json();
        if (cancelled) return;
        setState({ loading: false, status: data });
        // Continue polling if still pending
        if (attempts < 30 && !data.email_sent) {
          setTimeout(poll, 4000);
        }
      } catch {
        if (cancelled) return;
        setState({ loading: false, status: null });
      }
    };
    poll();
    return () => { cancelled = true; };
  }, [sessionId]);

  const emailSent = state.status?.email_sent;
  const pdfReady = state.status?.pdf_ready;

  return (
    <PsPageShell background="dark">
      <SEO path="/edition-reliee/merci" title="Merci · Votre livre est en cours · Plume Astrale" noindex />
      <div style={wrap}>
        <p style={eyebrow}>ÉDITION RELIÉE · PAIEMENT REÇU</p>
        <h1 style={h1} data-testid="er-merci-title">
          Merci — nous composons son livre.
        </h1>
        <p style={body}>
          Votre paiement est confirmé. Nous générons maintenant le PDF complet de 49 pages
          à partir des données de naissance que vous nous avez transmises.
        </p>

        <div style={statusCard}>
          <StatusRow label="Paiement reçu" done />
          <StatusRow label="Composition du livre (49 pages)" done={pdfReady} loading={!pdfReady} />
          <StatusRow label="Email de relecture envoyé" done={emailSent} loading={pdfReady && !emailSent} />
        </div>

        {emailSent ? (
          <>
            <p style={body}>
              Un email vient d'arriver dans votre boîte, avec le PDF complet
              et deux boutons : <b style={{ color: '#E8C766' }}>Approuver</b> pour
              lancer l'impression, ou <b>Refuser</b> si le texte ne vous touche
              pas (remboursement intégral, aucune impression).
            </p>
            <p style={body}>
              Vous avez <b>72 heures</b> pour décider. Sans réponse, nous vous
              relançons doucement à J+1 puis J+2. Rien ne partira à l'atelier sans votre feu vert.
            </p>
          </>
        ) : (
          <p style={body}>
            La composition prend en général moins d'une minute. Cette page se met
            à jour toute seule dès que l'email part de nos serveurs. Vous pouvez la
            laisser ouverte, ou fermer et attendre l'email dans quelques instants.
          </p>
        )}

        <p style={signature}>— Nadine</p>

        <div style={{ marginTop: 32, textAlign: 'center' }}>
          <Link to="/" data-testid="er-merci-home" style={ctaGhost}>Retour au sanctuaire</Link>
        </div>
      </div>
    </PsPageShell>
  );
}

function StatusRow({ label, done, loading }) {
  return (
    <div style={statusRow} data-testid={`er-merci-step-${done ? 'done' : loading ? 'loading' : 'pending'}`}>
      <span style={{
        ...statusDot,
        background: done ? '#8FB07A' : loading ? '#D4AF37' : 'rgba(240,230,211,0.2)',
        boxShadow: done ? '0 0 12px rgba(143,176,122,0.45)' : loading ? '0 0 14px rgba(212,175,55,0.55)' : 'none',
      }} />
      <span style={{ color: done ? '#F5EEE0' : loading ? '#E8C766' : 'rgba(240,230,211,0.55)' }}>
        {label}{loading ? ' · en cours…' : ''}
      </span>
    </div>
  );
}

// ── Styles ──
const wrap = { maxWidth: 620, margin: '0 auto', padding: '80px 24px', color: '#F5EEE0', fontFamily: '"Cormorant Garamond", serif', lineHeight: 1.65 };
const eyebrow = { fontFamily: '"Cinzel", serif', fontSize: '0.75rem', letterSpacing: 3, color: '#D4AF37', margin: 0, textAlign: 'center' };
const h1 = { fontFamily: '"Playfair Display", serif', fontSize: 'clamp(2rem, 5vw, 3rem)', color: '#F5EEE0', margin: '18px 0 22px', fontWeight: 400, lineHeight: 1.15, textAlign: 'center' };
const body = { fontSize: '1.08rem', color: '#F5EEE0', margin: '14px 0' };
const statusCard = { background: 'rgba(15,26,60,0.55)', border: '1px solid rgba(212,175,55,0.22)', borderRadius: 8, padding: '22px 24px', margin: '30px 0' };
const statusRow = { display: 'flex', alignItems: 'center', gap: 14, padding: '10px 0', fontFamily: '"Cinzel", serif', fontSize: '0.85rem', letterSpacing: 1.5 };
const statusDot = { width: 12, height: 12, borderRadius: '50%', flexShrink: 0, transition: 'all 400ms ease' };
const ctaGhost = { display: 'inline-block', padding: '14px 26px', color: '#E8C766', border: '1px solid rgba(232,199,102,0.4)', textDecoration: 'none', borderRadius: 4, fontFamily: '"Cinzel", serif', fontSize: '0.8rem', letterSpacing: 2.2, textTransform: 'uppercase' };
const signature = { marginTop: 34, fontFamily: '"Playfair Display", serif', fontStyle: 'italic', fontSize: '1.4rem', color: '#E8C766', textAlign: 'right' };
