import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import axios from 'axios';
import { Download, Loader2, Mail, CheckCircle2 } from 'lucide-react';
import SEO from '@/components/SEO';
import { event as trackEvent } from '@/lib/analytics';

const API = process.env.REACT_APP_BACKEND_URL;

export default function SynastrieSucces() {
  const [params] = useSearchParams();
  const sessionId = params.get('session_id');
  const [status, setStatus] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    if (!sessionId) {
      setErr('Aucun identifiant de session.');
      return;
    }
    let mounted = true;
    let attempts = 0;
    const poll = async () => {
      try {
        const r = await axios.get(`${API}/api/synastrie/status/${sessionId}`);
        if (!mounted) return;
        setStatus(r.data);
        if (r.data.status === 'paid' && r.data.pdf_ready) { trackEvent('synastrie_purchase_success'); return; }
      } catch (e) {
        if (mounted) setErr('Impossible de verifier le statut.');
      }
      attempts++;
      if (mounted && attempts < 30) setTimeout(poll, 2500);
    };
    poll();
    return () => { mounted = false; };
  }, [sessionId]);

  const isPaid = status?.status === 'paid';
  const pdfReady = isPaid && status?.pdf_ready;

  return (
    <div className="min-h-screen pt-24 pb-20 px-4 flex items-start justify-center" data-testid="synastrie-success-page">
      <SEO path="/synastrie/succes" />
      <div className="max-w-xl w-full">
        <div className="rounded-2xl p-8 sm:p-10 text-center" style={{ background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(212,175,55,0.2)' }}>
          {!status && !err && (
            <>
              <Loader2 className="w-10 h-10 mx-auto mb-4 animate-spin" style={{ color: '#D4AF37' }} />
              <p className="text-sm" style={{ color: 'rgba(184,176,200,0.75)' }}>Verification de votre paiement...</p>
            </>
          )}

          {err && (
            <p className="text-sm" style={{ color: '#FCA5A5' }} data-testid="synastrie-success-error">{err}</p>
          )}

          {isPaid && (
            <>
              <CheckCircle2 className="w-12 h-12 mx-auto mb-4" strokeWidth={1.5} style={{ color: '#7CB88A' }} />
              <h1 className="text-3xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3', fontWeight: 300 }}>
                Paiement confirme
              </h1>
              <p className="text-sm mb-6" style={{ color: 'rgba(184,176,200,0.85)', lineHeight: 1.7 }}>
                Votre rapport est en cours de composition.<br />
                Vous recevrez un email avec le lien de telechargement dans quelques instants.
              </p>

              {pdfReady && status.pdf_path ? (
                <a
                  href={status.pdf_path}
                  download
                  className="inline-flex items-center justify-center gap-2 px-7 py-3 rounded-full"
                  style={{ background: 'linear-gradient(135deg, #D4AF37, #B8961F)', color: '#0C0918', fontFamily: 'Cinzel, serif', fontSize: 12, letterSpacing: '0.14em', textTransform: 'uppercase', fontWeight: 600 }}
                  data-testid="synastrie-download-btn"
                >
                  <Download className="w-4 h-4" /> Telecharger mon rapport
                </a>
              ) : (
                <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full" style={{ background: 'rgba(167,139,250,0.1)', border: '1px solid rgba(167,139,250,0.3)' }}>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" style={{ color: '#A78BFA' }} />
                  <span className="text-xs" style={{ color: '#A78BFA' }}>PDF en preparation...</span>
                </div>
              )}

              <div className="mt-8 pt-6 flex items-center justify-center gap-2 text-xs" style={{ borderTop: '1px solid rgba(212,175,55,0.1)', color: 'rgba(184,176,200,0.6)' }}>
                <Mail className="w-3.5 h-3.5" />
                {status?.email_sent ? 'Email envoye' : 'Email en cours d\'envoi'}
              </div>
            </>
          )}

          {status && status.status === 'pending' && !err && (
            <>
              <Loader2 className="w-10 h-10 mx-auto mb-4 animate-spin" style={{ color: '#D4AF37' }} />
              <p className="text-sm" style={{ color: 'rgba(184,176,200,0.75)' }}>Confirmation du paiement en cours...</p>
            </>
          )}
        </div>

        <Link to="/" className="block text-center mt-6 text-xs" style={{ color: 'rgba(184,176,200,0.55)' }}>← Retour a l&apos;accueil</Link>
      </div>
    </div>
  );
}
