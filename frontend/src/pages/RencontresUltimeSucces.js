import React, { useEffect, useState, useRef } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { CheckCircle2, Loader2, FileText, Mail, Sparkles, ArrowRight, Download, Heart } from 'lucide-react';
import SEO from '../components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

const STAGES = {
  pending:    { icon: Loader2,     color: '#CBD5E1', pct: 15, label: 'Confirmation du paiement' },
  generating: { icon: FileText,    color: '#E7C97A', pct: 45, label: 'Ton PDF est en préparation' },
  emailing:   { icon: Mail,        color: '#E7C97A', pct: 78, label: "Envoi de l'email en cours" },
  delivered:  { icon: CheckCircle2, color: '#4ADE80', pct: 100, label: 'Livré avec succès' },
  error:      { icon: Sparkles,    color: '#F87171', pct: 0, label: 'Une perturbation cosmique' },
};

const STAGE_ORDER = ['pending', 'generating', 'emailing', 'delivered'];

export default function RencontresUltimeSucces() {
  const [params] = useSearchParams();
  const sessionId = params.get('session_id');
  const [status, setStatus] = useState({ stage: 'pending', message: 'Connexion aux astres…' });
  const [maxStageIdx, setMaxStageIdx] = useState(0);
  const [tick, setTick] = useState(0);
  const pollRef = useRef(null);

  useEffect(() => {
    if (!sessionId) {
      setStatus({ stage: 'error', message: 'session_id manquant dans l\'URL.' });
      return;
    }

    let cancelled = false;
    let attempts = 0;

    const poll = async () => {
      if (cancelled) return;
      attempts += 1;
      try {
        const r = await axios.get(`${API}/api/rencontres/ultime/status`, {
          params: { session_id: sessionId },
          timeout: 12000,
        });
        if (cancelled) return;
        const s = r.data || {};
        setStatus(s);
        // Track the highest stage reached so the UI doesn't regress
        const idx = STAGE_ORDER.indexOf(s.stage);
        if (idx > -1) setMaxStageIdx((prev) => Math.max(prev, idx));

        if (s.stage === 'delivered' || s.stage === 'error') return;   // stop polling
        // Continue polling
        pollRef.current = setTimeout(poll, 2000);
      } catch (e) {
        if (cancelled) return;
        if (attempts >= 30) {
          setStatus({ stage: 'error', message: 'Impossible de contacter les astres. Rafraîchis la page dans une minute.' });
          return;
        }
        pollRef.current = setTimeout(poll, 2500);
      }
    };

    poll();
    // Tick pour animation subtile
    const iv = setInterval(() => setTick((t) => (t + 1) % 1000), 400);
    return () => {
      cancelled = true;
      if (pollRef.current) clearTimeout(pollRef.current);
      clearInterval(iv);
    };
     
  }, [sessionId]);

  const currentStage = STAGES[status.stage] || STAGES.pending;
  const CurrentIcon = currentStage.icon;

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'radial-gradient(ellipse at 50% 20%, #1a1147 0%, #0C0918 55%, #050308 100%)',
        color: '#F4E8D2',
        padding: '60px 20px 80px',
        fontFamily: 'Inter, sans-serif',
      }}
      data-testid="rencontres-succes-page"
    >
      <SEO path="/rencontres-astrales/succes" />

      {/* Ambient stars */}
      <div aria-hidden="true" style={{ position: 'fixed', inset: 0, pointerEvents: 'none', opacity: 0.5 }}>
        <StarField />
      </div>

      <div className="max-w-2xl mx-auto relative z-10">

        {/* Kicker */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full"
            style={{ background: 'rgba(226,191,101,0.08)', border: '1px solid rgba(226,191,101,0.30)' }}>
            <Sparkles style={{ width: 12, height: 12, color: '#E2BF65' }} strokeWidth={1.5} />
            <span className="text-[10px] uppercase" style={{ color: '#E2BF65', letterSpacing: '0.3em', fontWeight: 400 }}>
              Paiement confirmé
            </span>
          </div>
        </div>

        {/* Title */}
        <h1
          className="text-center mb-4"
          style={{
            fontFamily: 'Cinzel, Playfair Display, Cormorant Garamond, serif',
            fontWeight: 300,
            fontSize: 'clamp(1.9rem, 4.5vw, 3rem)',
            lineHeight: 1.1,
            color: '#F4E8D2',
          }}
          data-testid="succes-title"
        >
          Merci — <em style={{ color: '#E2BF65', fontStyle: 'italic', fontWeight: 300 }}>ton Guide t&apos;attend.</em>
        </h1>
        <p className="text-center mb-14 mx-auto max-w-lg" style={{
          fontFamily: 'Cormorant Garamond, serif',
          fontSize: '1.15rem',
          fontStyle: 'italic',
          color: 'rgba(244,232,210,0.75)',
          lineHeight: 1.6,
        }}>
          15 pages de guidance amoureuse sont préparées rien que pour toi.
          Cela prend quelques instants — Solena y met tout son cœur.
        </p>

        {/* Progress card */}
        <div
          className="rounded-3xl p-8 md:p-10"
          style={{
            background: 'linear-gradient(160deg, rgba(212,175,55,0.06) 0%, rgba(20,15,40,0.6) 100%)',
            border: '1px solid rgba(226,191,101,0.30)',
            backdropFilter: 'blur(14px)',
            boxShadow: '0 30px 80px rgba(226,191,101,0.10)',
          }}
          data-testid="succes-progress-card"
        >

          {/* Icon + label */}
          <div className="flex items-center gap-4 mb-6">
            <div style={{
              width: 60, height: 60, borderRadius: '50%',
              background: `radial-gradient(circle, ${currentStage.color}22 0%, transparent 70%)`,
              border: `1px solid ${currentStage.color}55`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}>
              <CurrentIcon
                style={{ width: 28, height: 28, color: currentStage.color }}
                strokeWidth={1.5}
                className={(status.stage === 'pending' || status.stage === 'generating' || status.stage === 'emailing') ? 'animate-spin-slow' : ''}
              />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-[10px] uppercase" style={{ color: currentStage.color, letterSpacing: '0.28em', fontWeight: 500 }}>
                {currentStage.label}
              </div>
              <div className="mt-1 text-base md:text-lg" style={{
                fontFamily: 'Cormorant Garamond, serif',
                color: '#F4E8D2',
                lineHeight: 1.4,
              }} data-testid="succes-message">
                {status.message}
                {(status.stage === 'pending' || status.stage === 'generating' || status.stage === 'emailing') && (
                  <span style={{ color: '#E2BF65', marginLeft: 4 }}>{'.'.repeat(1 + (tick % 3))}</span>
                )}
              </div>
            </div>
          </div>

          {/* Progress bar */}
          <div style={{
            position: 'relative',
            height: 6,
            background: 'rgba(255,255,255,0.05)',
            borderRadius: 999,
            overflow: 'hidden',
            marginBottom: 24,
          }}>
            <div style={{
              position: 'absolute', top: 0, left: 0, bottom: 0,
              width: `${currentStage.pct}%`,
              background: `linear-gradient(90deg, #E2BF65, #E8C766, #E2BF65)`,
              boxShadow: '0 0 16px rgba(226,191,101,0.6)',
              transition: 'width 0.8s cubic-bezier(0.16, 1, 0.3, 1)',
              borderRadius: 999,
            }} />
          </div>

          {/* Steps checklist */}
          <div className="space-y-3">
            {STAGE_ORDER.map((key, i) => {
              const s = STAGES[key];
              const done = i < maxStageIdx || status.stage === 'delivered';
              const active = i === maxStageIdx && status.stage !== 'delivered';
              const StepIcon = done ? CheckCircle2 : s.icon;
              const iconColor = done ? '#4ADE80' : active ? '#E2BF65' : 'rgba(203,213,225,0.4)';
              return (
                <div key={key} className="flex items-center gap-3" data-testid={`succes-step-${key}`}>
                  <StepIcon
                    style={{ width: 16, height: 16, color: iconColor, flexShrink: 0 }}
                    strokeWidth={2}
                    className={active ? 'animate-spin-slow' : ''}
                  />
                  <span style={{
                    fontSize: 13,
                    color: done ? 'rgba(74,222,128,0.85)' : active ? '#E2BF65' : 'rgba(203,213,225,0.4)',
                    fontFamily: 'Inter, sans-serif',
                    letterSpacing: '0.02em',
                    fontWeight: done ? 500 : 400,
                    textDecoration: done ? 'none' : 'none',
                  }}>
                    {STEP_LABELS[key]}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Delivered — download + next steps */}
          {status.stage === 'delivered' && (
            <div className="mt-8 pt-6" style={{ borderTop: '1px solid rgba(226,191,101,0.20)' }} data-testid="succes-delivered-actions">
              {status.email && (
                <p className="text-sm text-center mb-5" style={{
                  fontFamily: 'Cormorant Garamond, serif',
                  color: 'rgba(244,232,210,0.85)',
                  fontStyle: 'italic',
                  lineHeight: 1.5,
                }}>
                  Un email vient d&apos;être envoyé à<br />
                  <strong style={{ color: '#E2BF65', fontStyle: 'normal', fontWeight: 500 }}>{status.email}</strong>
                </p>
              )}
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                {status.pdf_url && (
                  <a
                    href={`${API}${status.pdf_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="plume-btn-primary"
                    data-testid="succes-download-btn"
                  >
                    <Download style={{ width: 14, height: 14 }} strokeWidth={2} />
                    Télécharger mon Guide (PDF)
                  </a>
                )}
                <Link to="/" className="plume-btn-secondary" data-testid="succes-home-btn">
                  Retour à l&apos;accueil
                  <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
                </Link>
              </div>
              <p className="text-[10px] uppercase text-center mt-5" style={{
                color: 'rgba(203,213,225,0.45)',
                letterSpacing: '0.25em',
              }}>
                Pense à vérifier tes courriers indésirables · Le PDF reste accessible via ce lien
              </p>
            </div>
          )}

          {/* Error state */}
          {status.stage === 'error' && (
            <div className="mt-8 pt-6" style={{ borderTop: '1px solid rgba(248,113,113,0.20)' }}>
              <p className="text-sm text-center" style={{ color: 'rgba(248,113,113,0.85)' }}>
                Si le problème persiste, contacte <a href="mailto:contact@plume-astrale.fr" style={{ color: '#E2BF65' }}>contact@plume-astrale.fr</a> avec ce numéro de session : <code style={{ fontSize: 11, color: '#E8C766' }}>{sessionId}</code>
              </p>
            </div>
          )}
        </div>

        {/* Signature */}
        {status.stage !== 'error' && (
          <div className="text-center mt-10">
            <Heart style={{ width: 16, height: 16, color: '#E2BF65', margin: '0 auto 8px', display: 'block' }} strokeWidth={1.5} />
            <div className="text-sm" style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontStyle: 'italic',
              color: '#E2BF65',
              letterSpacing: '0.05em',
            }}>
              — Solena
            </div>
            <div className="text-[10px] uppercase mt-1" style={{ color: 'rgba(244,232,210,0.5)', letterSpacing: '0.25em' }}>
              Guide astrologue chez Plume Astrale
            </div>
          </div>
        )}
      </div>

      {/* Animations */}
      <style>{`
        @keyframes pa-spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .animate-spin-slow { animation: pa-spin-slow 2s linear infinite; }
      `}</style>
    </div>
  );
}

const STEP_LABELS = {
  pending:    'Paiement confirmé par Stripe',
  generating: 'Génération de ton PDF 15 pages',
  emailing:   'Envoi de l\'email avec ton Guide',
  delivered:  'Vérifie ta boîte mail !',
};

// Small starfield for ambience
function StarField() {
  const stars = useRef(null);
  if (!stars.current) {
    stars.current = Array.from({ length: 55 }, () => ({
      x: Math.random() * 100,
      y: Math.random() * 100,
      r: Math.random() * 1.2 + 0.4,
      op: 0.3 + Math.random() * 0.5,
      delay: Math.random() * 4,
    }));
  }
  return (
    <svg
      aria-hidden="true"
      preserveAspectRatio="none"
      viewBox="0 0 100 100"
      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
    >
      <style>{`
        @keyframes pa-tw { 0%,100% { opacity: 0.3; } 50% { opacity: 1; } }
        .pa-tw-star { animation: pa-tw 3.4s ease-in-out infinite; }
      `}</style>
      {stars.current.map((s, i) => (
        <circle
          key={i}
          className="pa-tw-star"
          cx={s.x}
          cy={s.y}
          r={s.r * 0.08}
          fill="#F4E8D2"
          style={{ animationDelay: `${s.delay}s`, opacity: s.op }}
        />
      ))}
    </svg>
  );
}
