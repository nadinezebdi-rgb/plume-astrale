import React, { useEffect, useState, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { CheckCircle2, Download, ArrowRight, Loader2, Mail } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import CercleSolenaInvite from '@/components/CercleSolenaInvite';

const API = process.env.REACT_APP_BACKEND_URL;

const STEPS = [
  { key: 'payment', label: 'Paiement confirmé' },
  { key: 'compute', label: 'Calcul de tes 11 planètes & aspects' },
  { key: 'pdf', label: 'Génération de ton PDF luxe (20-40 pages)' },
  { key: 'email', label: 'Envoi par email' },
];

const ThemeNatalOneshotSucces = () => {
  const [params] = useSearchParams();
  const sessionId = params.get('session_id');
  const [status, setStatus] = useState({});
  const [polling, setPolling] = useState(true);

  const poll = useCallback(async () => {
    if (!sessionId) return;
    try {
      const r = await axios.get(`${API}/api/theme-natal-oneshot/status?session_id=${sessionId}`);
      setStatus(r.data || {});
      if (r.data?.pdf_ready) setPolling(false);
    } catch (e) {
      /* silent */
    }
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
    if (key === 'compute') return status.pdf_ready ? 'done' : paid ? 'active' : 'pending';
    if (key === 'pdf') return status.pdf_ready ? 'done' : paid ? 'active' : 'pending';
    if (key === 'email') return status.email_sent ? 'done' : status.pdf_ready ? 'active' : 'pending';
    return 'pending';
  };

  return (
    <div className="min-h-screen relative" style={{ padding: '110px 20px 140px' }} data-testid="theme-natal-oneshot-success-page">
      <SEO path="/theme-natal/succes" title="Ton Thème Natal arrive · Plume Astrale" />

      <div className="max-w-2xl mx-auto text-center">
        <div className="mb-8" data-testid="theme-natal-oneshot-success-icon">
          <div
            className="inline-flex items-center justify-center w-20 h-20 rounded-full mb-4"
            style={{
              background: 'linear-gradient(135deg, rgba(212,175,55,0.15), rgba(212,175,55,0.05))',
              border: '1px solid rgba(212,175,55,0.35)',
            }}
          >
            <CheckCircle2 className="w-10 h-10" style={{ color: '#D4AF37' }} strokeWidth={1.4} />
          </div>
          <p className="text-[10px] uppercase mb-3" style={{ color: '#D4AF37', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}>
            ✦ Paiement Confirmé ✦
          </p>
          <h1
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontWeight: 300,
              fontSize: 'clamp(32px, 5vw, 48px)',
              color: '#F5EEE0',
              lineHeight: 1.15,
            }}
          >
            Ton <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>Thème Natal</em> se compose
          </h1>
          <p className="mt-4" style={{ color: 'rgba(227,215,255,0.75)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
            Soléna trace les 20 à 40 pages de ton portrait céleste. Livraison par email dans quelques minutes.
          </p>
        </div>

        {/* Steps */}
        <div className="plume-glass p-6 md:p-8 mb-8" data-testid="theme-natal-oneshot-steps">
          {STEPS.map((s) => {
            const st = stepState(s.key);
            return (
              <div key={s.key} className="flex items-center gap-3 py-3" data-testid={`theme-natal-oneshot-step-${s.key}`}>
                <div
                  className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
                  style={{
                    background:
                      st === 'done'
                        ? 'rgba(74,222,128,0.15)'
                        : st === 'active'
                        ? 'rgba(212,175,55,0.15)'
                        : 'rgba(255,255,255,0.04)',
                    border: `1px solid ${st === 'done' ? 'rgba(74,222,128,0.4)' : st === 'active' ? 'rgba(212,175,55,0.4)' : 'rgba(255,255,255,0.08)'}`,
                  }}
                >
                  {st === 'done' ? (
                    <CheckCircle2 className="w-4 h-4" style={{ color: '#4ADE80' }} strokeWidth={2} />
                  ) : st === 'active' ? (
                    <Loader2 className="w-4 h-4 animate-spin" style={{ color: '#D4AF37' }} strokeWidth={1.6} />
                  ) : (
                    <span className="w-2 h-2 rounded-full" style={{ background: 'rgba(255,255,255,0.2)' }} />
                  )}
                </div>
                <span
                  className="text-sm text-left"
                  style={{
                    color: st === 'done' ? '#F5EEE0' : st === 'active' ? '#F5EEE0' : 'rgba(227,215,255,0.55)',
                    fontFamily: 'Cormorant Garamond, serif',
                  }}
                >
                  {s.label}
                </span>
              </div>
            );
          })}
        </div>

        {/* Download */}
        {status.pdf_ready && status.pdf_url ? (
          <a
            href={status.pdf_url}
            className="plume-btn-primary inline-flex"
            data-testid="theme-natal-oneshot-download-btn"
          >
            <Download className="w-4 h-4" strokeWidth={1.5} />
            Télécharger mon Thème Natal
            <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
          </a>
        ) : (
          <p className="text-xs" style={{ color: 'rgba(227,215,255,0.55)', letterSpacing: '0.15em' }}>
            <Mail className="w-3 h-3 inline mr-1" strokeWidth={1.5} />
            Ton PDF arrivera aussi par email dans les 3 minutes.
          </p>
        )}

        <div className="mt-14">
          <CercleSolenaInvite sourceProduct="theme_natal_oneshot" testId="theme-natal-oneshot-post-purchase-cercle" />
        </div>

        <div className="mt-8">
          <Link
            to="/"
            className="text-xs uppercase"
            style={{ color: 'rgba(212,175,55,0.7)', letterSpacing: '0.2em', textDecoration: 'none' }}
            data-testid="theme-natal-oneshot-back-home"
          >
            Retour à l&apos;accueil
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ThemeNatalOneshotSucces;
