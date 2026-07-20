import React, { useEffect, useState, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { CheckCircle2, Download, ArrowRight, Loader2, Mail, Globe2, Sparkles } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import CercleSolenaInvite from '@/components/CercleSolenaInvite';

const API = process.env.REACT_APP_BACKEND_URL;

const STEPS = [
  { key: 'payment', label: 'Paiement confirmé' },
  { key: 'compute', label: 'Cartographie kabbalistique en cours' },
  { key: 'pdf', label: 'Génération de ton PDF (15 pages)' },
  { key: 'email', label: 'Envoi par email' },
];

const KabbaleSucces = () => {
  const [params] = useSearchParams();
  const sessionId = params.get('session_id');
  const [status, setStatus] = useState({});
  const [polling, setPolling] = useState(true);

  const poll = useCallback(async () => {
    if (!sessionId) return;
    try {
      const r = await axios.get(`${API}/api/kabbale/status?session_id=${sessionId}`);
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
    <div className="min-h-screen relative" style={{ padding: '110px 20px 140px' }} data-testid="kabbale-success-page">
      <SEO path="/kabbale/succes" title="Ton Arbre de Vie est en cours · Plume Astrale" description="Ton PDF Kabbale est en génération." />
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-6" style={{ background: 'rgba(212,175,55,0.15)', border: '1px solid rgba(212,175,55,0.4)' }}>
            <CheckCircle2 className="w-8 h-8" style={{ color: '#D4AF37' }} strokeWidth={1.4} />
          </div>
          <p className="text-[10px] uppercase mb-4" style={{ color: '#D4AF37', letterSpacing: '0.32em', fontFamily: 'Cinzel, serif' }}>
            ✦ Paiement confirmé ✦
          </p>
          <h1 style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, lineHeight: 1.1, fontSize: 'clamp(32px, 5vw, 52px)', color: '#F5EEE0', marginBottom: 16 }}>
            Ton <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>Arbre de Vie</em><br />se dessine
          </h1>
          <p className="text-base max-w-lg mx-auto" style={{ color: 'rgba(227,215,255,0.75)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic', lineHeight: 1.6 }}>
            Ton PDF sera envoyé par email dans les prochaines minutes.
          </p>
        </div>

        <div className="plume-glass p-8 mb-8">
          <ul className="space-y-4">
            {STEPS.map((s, i) => {
              const st = stepState(s.key);
              return (
                <li key={s.key} className="flex items-center gap-3" data-testid={`kabbale-step-${s.key}-${st}`}>
                  <div className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center" style={{
                    background: st === 'done' ? 'rgba(212,175,55,0.2)' : 'rgba(26,32,53,0.6)',
                    border: `1px solid ${st === 'done' ? '#D4AF37' : 'rgba(212,175,55,0.25)'}`,
                  }}>
                    {st === 'done' ? <CheckCircle2 className="w-4 h-4" style={{ color: '#D4AF37' }} strokeWidth={2} />
                     : st === 'active' ? <Loader2 className="w-4 h-4 animate-spin" style={{ color: '#D4AF37' }} strokeWidth={2} />
                     : <span className="w-2 h-2 rounded-full" style={{ background: 'rgba(212,175,55,0.35)' }} />}
                  </div>
                  <span className="text-sm" style={{ color: st === 'pending' ? 'rgba(227,215,255,0.5)' : '#F5EEE0', fontFamily: 'Cormorant Garamond, serif', fontSize: 17 }}>
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
              <a href={`${API}${status.pdf_url}`} target="_blank" rel="noopener noreferrer" className="plume-btn-primary" data-testid="kabbale-download-btn">
                <Download className="w-4 h-4" strokeWidth={1.5} />
                Télécharger mon PDF
              </a>
            )}
            <Link to="/" className="plume-btn-secondary" data-testid="kabbale-home-btn">
              Retour à l'accueil
              <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
            </Link>
          </div>
          {status.email_sent && (
            <p className="text-xs mt-6 inline-flex items-center gap-2" style={{ color: 'rgba(227,215,255,0.55)' }}>
              <Mail className="w-3.5 h-3.5" /> Email envoyé à ton adresse.
            </p>
          )}
        </div>

        {/* Upsell Astrocartographie — la CB est encore chaude */}
        {status.pdf_ready && (
          <div
            className="plume-glass p-6 md:p-8 mt-14 relative overflow-hidden"
            data-testid="kabbale-upsell-astrocarto"
            style={{
              border: '1px solid rgba(212,175,55,0.4)',
              boxShadow: '0 30px 80px -30px rgba(212,175,55,0.25)',
            }}
          >
            <div
              className="absolute top-3 right-3 px-3 py-1 rounded-full text-[10px] uppercase"
              style={{
                background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 50%, #D4AF37 100%)',
                color: '#0A0603',
                fontFamily: 'Cinzel, serif',
                letterSpacing: '0.18em',
                fontWeight: 700,
              }}
              data-testid="kabbale-upsell-badge"
            >
              -20€ · Duo Soléna
            </div>

            <p className="text-[10px] uppercase mb-3" style={{ color: '#D4AF37', letterSpacing: '0.32em', fontFamily: 'Cinzel, serif' }}>
              ✦ Ton chemin continue ✦
            </p>

            <h3
              style={{
                fontFamily: 'Cormorant Garamond, serif',
                fontWeight: 300,
                fontSize: 'clamp(24px, 3vw, 32px)',
                color: '#F5EEE0',
                lineHeight: 1.15,
                marginBottom: 10,
              }}
              data-testid="kabbale-upsell-title"
            >
              Maintenant que tu connais ton âme,{' '}
              <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>où va-t-elle s&apos;épanouir</em> ?
            </h3>

            <p
              className="text-sm md:text-base mb-5"
              style={{
                color: 'rgba(227,215,255,0.8)',
                fontFamily: 'Cormorant Garamond, serif',
                fontStyle: 'italic',
                lineHeight: 1.55,
              }}
            >
              Compose ton Astrocartographie personnalisée — 18 pages avec toutes tes lignes
              planétaires, 3 villes de ton choix et 2 destinations bonus par Soléna.
            </p>

            <div className="flex items-baseline gap-3 mb-5" data-testid="kabbale-upsell-pricing">
              <span style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 40, color: '#D4AF37', fontWeight: 300 }}>
                29€
              </span>
              <span style={{ textDecoration: 'line-through', color: 'rgba(227,215,255,0.4)', fontSize: 20 }}>49€</span>
              <span className="text-xs" style={{ color: 'rgba(212,175,55,0.85)', letterSpacing: '0.15em' }}>
                · CODE APPLIQUÉ AUTO
              </span>
            </div>

            <p className="text-[11px] mb-5" style={{ color: 'rgba(227,215,255,0.55)', lineHeight: 1.55 }}>
              <Sparkles className="w-3 h-3 inline mr-1" style={{ color: '#D4AF37' }} />
              Offre exclusive réservée aux âmes qui viennent de recevoir leur Arbre de Vie.
              Le code KABBALE20 est appliqué automatiquement au checkout.
            </p>

            <Link
              to="/astrocartographie?discount=KABBALE20"
              className="plume-btn-primary w-full justify-center"
              data-testid="kabbale-upsell-cta"
              style={{ display: 'inline-flex' }}
            >
              <Globe2 className="w-4 h-4" strokeWidth={1.5} />
              Composer mon rapport — 29€
              <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
            </Link>
          </div>
        )}

        {/* Invitation Cercle Soléna — 1 mois offert (post-purchase) */}
        {status.pdf_ready && (
          <CercleSolenaInvite sourceProduct="kabbale" testId="kabbale-post-purchase-cercle" />
        )}
      </div>
    </div>
  );
};

export default KabbaleSucces;
