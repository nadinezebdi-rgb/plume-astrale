/* eslint-disable react/no-unescaped-entities */
import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL || '';

/**
 * Page /relecture/:token — la cliente arrive ici depuis le bouton
 * "Dire pourquoi ça ne va pas" de l'email de relecture 72h.
 *
 * Elle peut :
 *  - Ouvrir/relire le PDF (pdf_url du dossier)
 *  - Écrire un mot libre expliquant pourquoi le texte ne la touche pas
 *  - Refuser explicitement → remboursement intégral, rien imprimé
 */
export default function RelectureRefus() {
  const { token } = useParams();
  const [state, setState] = useState({ loading: true, error: null, approval: null });
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  const load = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/print-approval/${token}`);
      if (!r.ok) {
        setState({ loading: false, error: 'Ce lien de relecture n\'est pas valide ou a déjà été utilisé.', approval: null });
        return;
      }
      const data = await r.json();
      setState({ loading: false, error: null, approval: data });
    } catch {
      setState({ loading: false, error: 'Impossible de charger le dossier pour le moment.', approval: null });
    }
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const submitRefuse = async () => {
    setSubmitting(true);
    try {
      const r = await fetch(`${API}/api/print-approval/refuse/${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: reason.trim() || null }),
      });
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        alert(d.detail || 'Refus impossible pour le moment. Écrivez-nous à contact@plume-astrale.fr.');
        return;
      }
      setDone(true);
    } finally {
      setSubmitting(false);
    }
  };

  if (state.loading) {
    return (
      <PsPageShell background="dark">
        <SEO path={`/relecture/${token}`} title="Relecture · Plume Astrale" noindex />
        <div style={wrap}>
          <p style={eyebrow}>PLUME ASTRALE · ÉDITION RELIÉE</p>
          <p style={body}>Chargement de votre dossier…</p>
        </div>
      </PsPageShell>
    );
  }

  if (state.error) {
    return (
      <PsPageShell background="dark">
        <SEO path={`/relecture/${token}`} title="Relecture · Plume Astrale" noindex />
        <div style={wrap}>
          <p style={eyebrow}>PLUME ASTRALE · ÉDITION RELIÉE</p>
          <h1 style={h1}>Lien introuvable</h1>
          <p style={body}>{state.error}</p>
          <p style={body}>
            Écrivez-nous à{' '}
            <a href="mailto:contact@plume-astrale.fr" style={link}>contact@plume-astrale.fr</a>
            {' '}et nous vous rappelons dans la journée.
          </p>
          <Link to="/" style={ctaGhost}>Retour au sanctuaire</Link>
        </div>
      </PsPageShell>
    );
  }

  const { approval } = state;
  const status = approval.status;

  if (done || status === 'refused') {
    return (
      <PsPageShell background="dark">
        <SEO path={`/relecture/${token}`} title="Refus enregistré · Plume Astrale" noindex />
        <div style={wrap}>
          <p style={eyebrow}>PLUME ASTRALE · ÉDITION RELIÉE</p>
          <h1 style={h1}>C'est noté. Rien ne s'imprime.</h1>
          <p style={body}>
            Merci pour votre franchise. Le remboursement intégral est déclenché sur la carte
            utilisée pour la commande — comptez 3 à 5 jours ouvrés pour le voir apparaître.
          </p>
          <p style={body}>
            Si vous voulez qu'on reprenne le texte ensemble avant impression,
            écrivez-nous à{' '}
            <a href="mailto:contact@plume-astrale.fr" style={link}>contact@plume-astrale.fr</a>
            {' '}— je vous rappelle dans la journée.
          </p>
          <p style={signature}>— Nadine</p>
          <Link to="/" style={ctaGhost}>Retour au sanctuaire</Link>
        </div>
      </PsPageShell>
    );
  }

  if (status === 'approved') {
    return (
      <PsPageShell background="dark">
        <SEO path={`/relecture/${token}`} title="Déjà approuvé · Plume Astrale" noindex />
        <div style={wrap}>
          <p style={eyebrow}>PLUME ASTRALE · ÉDITION RELIÉE</p>
          <h1 style={h1}>Vous avez déjà validé ce livre.</h1>
          <p style={body}>
            L'impression est en cours ou a été livrée. Si vous voulez modifier quelque chose,
            écrivez-nous vite à <a href="mailto:contact@plume-astrale.fr" style={link}>contact@plume-astrale.fr</a>.
          </p>
          <Link to="/" style={ctaGhost}>Retour au sanctuaire</Link>
        </div>
      </PsPageShell>
    );
  }

  return (
    <PsPageShell background="dark">
      <SEO path={`/relecture/${token}`} title="Votre relecture · Plume Astrale" noindex />
      <div style={wrap}>
        <p style={eyebrow}>PLUME ASTRALE · ÉDITION RELIÉE</p>
        <h1 style={h1} data-testid="relecture-title">
          Dites-nous ce qui ne va pas.
        </h1>
        <p style={body}>
          Avant de refuser, prenez trente secondes pour nous dire ce qui coince. Une phrase suffit.
          Nous ne réimprimons pas un livre qui ne vous touche pas — et si c'est réparable,
          nous préférons le corriger que le rembourser.
        </p>

        <div style={pdfCard}>
          <p style={eyebrowGold}>LE PDF EN RELECTURE</p>
          <a href={approval.pdf_url} target="_blank" rel="noopener noreferrer"
             data-testid="relecture-pdf-link" style={ctaGhost}>
            Rouvrir le PDF
          </a>
        </div>

        <label style={label}>
          <span style={labelText}>Ce qui ne vous touche pas (optionnel, mais précieux)</span>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Une phrase, un paragraphe, un exemple — comme il vous vient."
            rows={6}
            maxLength={1000}
            data-testid="relecture-reason-input"
            style={textarea}
          />
        </label>

        <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginTop: 24 }}>
          <button
            type="button"
            onClick={submitRefuse}
            disabled={submitting}
            data-testid="relecture-refuse-btn"
            style={ctaRefuse}
          >
            {submitting ? 'Envoi…' : 'REFUSER · REMBOURSEMENT INTÉGRAL'}
          </button>
          <Link to="/" style={ctaGhost}>Y réfléchir encore</Link>
        </div>

        <p style={signature}>— Nadine</p>
      </div>
    </PsPageShell>
  );
}

// ── Styles inline (isolés — pas de collision avec le design system) ──
const wrap = {
  maxWidth: 640, margin: '0 auto', padding: '80px 24px', color: '#F5EEE0',
  fontFamily: '"Cormorant Garamond", serif', lineHeight: 1.65,
};
const eyebrow = {
  fontFamily: '"Cinzel", serif', fontSize: '0.75rem', letterSpacing: 3,
  color: '#D4AF37', margin: 0, textAlign: 'center',
};
const eyebrowGold = {
  ...eyebrow, marginBottom: 12,
};
const h1 = {
  fontFamily: '"Playfair Display", serif', fontSize: 'clamp(2rem, 5vw, 3rem)',
  color: '#F5EEE0', margin: '18px 0 24px', fontWeight: 400, lineHeight: 1.15,
  textAlign: 'center',
};
const body = { fontSize: '1.08rem', color: '#F5EEE0', margin: '14px 0' };
const pdfCard = {
  background: 'rgba(15,26,60,0.55)', border: '1px solid rgba(212,175,55,0.25)',
  borderRadius: 8, padding: '24px 22px', margin: '32px 0', textAlign: 'center',
};
const label = { display: 'block', marginTop: 28 };
const labelText = {
  display: 'block', fontFamily: '"Cinzel", serif', fontSize: '0.7rem',
  letterSpacing: 2, color: '#D4AF37', marginBottom: 10, textTransform: 'uppercase',
};
const textarea = {
  width: '100%', padding: '14px 16px', background: 'rgba(15,26,60,0.6)',
  border: '1px solid rgba(212,175,55,0.3)', borderRadius: 4, color: '#F5EEE0',
  fontSize: '1rem', fontFamily: 'inherit', lineHeight: 1.55, resize: 'vertical',
  boxSizing: 'border-box',
};
const ctaRefuse = {
  padding: '14px 26px', background: 'transparent', color: '#F0E6D3',
  border: '1px solid rgba(212,175,55,0.5)', borderRadius: 4,
  fontFamily: '"Cinzel", serif', fontSize: '0.8rem', letterSpacing: 2.2,
  cursor: 'pointer', fontWeight: 500, textTransform: 'uppercase',
};
const ctaGhost = {
  display: 'inline-block', padding: '14px 26px', color: '#E8C766',
  border: '1px solid rgba(232,199,102,0.4)', textDecoration: 'none',
  borderRadius: 4, fontFamily: '"Cinzel", serif', fontSize: '0.8rem',
  letterSpacing: 2.2, textTransform: 'uppercase',
};
const link = { color: '#D4AF37', textDecoration: 'underline' };
const signature = {
  marginTop: 40, fontFamily: '"Playfair Display", serif', fontStyle: 'italic',
  fontSize: '1.4rem', color: '#E8C766', textAlign: 'right',
};
