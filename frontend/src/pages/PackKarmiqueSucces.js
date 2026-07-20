import React, { useEffect, useState, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { CheckCircle2, Download, ArrowRight, Loader2, Mail } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import CercleSolenaInvite from '@/components/CercleSolenaInvite';

const API = process.env.REACT_APP_BACKEND_URL;

const STEPS = [
  { key: 'payment', label: 'Paiement confirmé' },
  { key: 'compute', label: 'Analyse karmique + Arbre de Vie en cours' },
  { key: 'pdf', label: 'Génération de ton PDF (~40 pages)' },
  { key: 'email', label: 'Envoi par email' },
];

const PackKarmiqueSucces = () => {
  const [params] = useSearchParams();
  const sessionId = params.get('session_id');
  const [status, setStatus] = useState({});
  const [polling, setPolling] = useState(true);

  const poll = useCallback(async () => {
    if (!sessionId) return;
    try {
      const r = await axios.get(`${API}/api/pack-karmique/status?session_id=${sessionId}`);
      setStatus(r.data || {});
      if (r.data?.pdf_ready) setPolling(false);
    } catch (e) { /* silent */ }
  }, [sessionId]);

  useEffect(() => {
    if (!sessionId) return;
    poll();
    if (!polling) return;
    const id = setInterval(poll, 3500);
    return () => clearInterval(id);
  }, [sessionId, polling, poll]);

  const stepState = (key) => {
    const paid = status.payment_status === 'paid' || status.status === 'completed';
    if (key === 'payment') return paid ? 'done' : 'pending';
    if (key === 'compute') return status.pdf_ready ? 'done' : (paid ? 'active' : 'pending');
    if (key === 'pdf') return status.pdf_ready ? 'done' : (paid ? 'active' : 'pending');
    if (key === 'email') return status.email_sent ? 'done' : (status.pdf_ready ? 'active' : 'pending');
    return 'pending';
  };

  return (
    <div className="min-h-screen relative" style={{ padding: '110px 20px 140px' }} data-testid="pack-karmique-success-page">
      <SEO path="/pack-karmique/succes" title="Ton Pack Karmique est en cours · Plume Astrale" description="Ton PDF Pack Karmique + Kabbale est en génération." />
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-6" style={{ background: 'rgba(212,175,55,0.15)', border: '1px solid rgba(212,175,55,0.4)' }}>
            <CheckCircle2 className="w-8 h-8" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.4} />
          </div>
          <p className="text-[10px] uppercase mb-4" style={{ color: 'var(--pa-accent)', letterSpacing: '0.32em', fontFamily: 'Cinzel, serif' }}>
            ✦ Paiement confirmé ✦
          </p>
          <h1 style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, lineHeight: 1.1, fontSize: 'clamp(32px, 5vw, 52px)', color: 'var(--pa-heading)', marginBottom: 16 }}>
            Ton <em style={{ color: 'var(--pa-accent)', fontStyle: 'italic' }}>Pack Karmique</em><br />se compose
          </h1>
          <p className="text-base max-w-lg mx-auto" style={{ color: 'var(--pa-body)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic', lineHeight: 1.6 }}>
            ~40 pages en cours de génération. Ton PDF sera envoyé par email dans quelques minutes.
          </p>
        </div>

        <div className="plume-glass p-8 mb-8">
          <ul className="space-y-4">
            {STEPS.map((s) => {
              const st = stepState(s.key);
              return (
                <li key={s.key} className="flex items-center gap-3" data-testid={`pack-karmique-step-${s.key}-${st}`}>
                  <div className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center" style={{
                    background: st === 'done' ? 'rgba(212,175,55,0.2)' : 'rgba(26,32,53,0.6)',
                    border: `1px solid ${st === 'done' ? 'var(--pa-accent)' : 'rgba(212,175,55,0.25)'}`,
                  }}>
                    {st === 'done' ? <CheckCircle2 className="w-4 h-4" style={{ color: 'var(--pa-accent)' }} strokeWidth={2} />
                     : st === 'active' ? <Loader2 className="w-4 h-4 animate-spin" style={{ color: 'var(--pa-accent)' }} strokeWidth={2} />
                     : <span className="w-2 h-2 rounded-full" style={{ background: 'rgba(212,175,55,0.35)' }} />}
                  </div>
                  <span className="text-sm" style={{ color: st === 'pending' ? 'var(--pa-muted)' : 'var(--pa-heading)', fontFamily: 'Cormorant Garamond, serif', fontSize: 17 }}>
                    {s.label}
                  </span>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="text-center">
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            {status.pdf_url && (
              <a href={`${API}${status.pdf_url}`} target="_blank" rel="noopener noreferrer" className="plume-btn-primary" data-testid="pack-karmique-download-btn">
                <Download className="w-4 h-4" strokeWidth={1.5} />
                Télécharger mon PDF
              </a>
            )}
            <Link to="/" className="plume-btn-secondary" data-testid="pack-karmique-home-btn">
              Retour à l'accueil
              <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
            </Link>
          </div>
          {status.email_sent && (
            <p className="text-xs mt-6 inline-flex items-center gap-2" style={{ color: 'var(--pa-muted)' }}>
              <Mail className="w-3.5 h-3.5" /> Email envoyé à ton adresse.
            </p>
          )}
        </div>

        {/* Invitation Cercle Soléna — 1 mois offert (post-purchase) */}
        {status.pdf_ready && (
          <CercleSolenaInvite sourceProduct="pack_karmique" testId="karmique-post-purchase-cercle" />
        )}
      </div>
    </div>
  );
};

export default PackKarmiqueSucces;
