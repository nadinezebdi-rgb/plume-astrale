import React, { useEffect, useState, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { CheckCircle2, Star, Moon, Loader2, Mail, Download } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

const CHILD_META = {
  numerologie: { name: 'Numérologie Sacrée', icon: Star },
  kabbale_arbre_de_vie: { name: 'Arbre de Vie Kabbale', icon: Moon },
};

const DuoCompletionSucces = () => {
  const [params] = useSearchParams();
  const sessionId = params.get('session_id');
  const [status, setStatus] = useState({ children: [] });
  const [polling, setPolling] = useState(true);

  const poll = useCallback(async () => {
    if (!sessionId) return;
    try {
      const r = await axios.get(`${API}/api/duo-completion/status?session_id=${sessionId}`);
      setStatus(r.data || { children: [] });
      if (r.data?.all_ready) setPolling(false);
    } catch (e) { /* silent */ }
  }, [sessionId]);

  useEffect(() => {
    if (!sessionId) return;
    poll();
    if (!polling) return;
    const id = setInterval(poll, 4000);
    return () => clearInterval(id);
  }, [sessionId, polling, poll]);

  return (
    <div className="min-h-screen relative" style={{ padding: '110px 20px 140px' }} data-testid="duo-completion-success-page">
      <SEO path="/duo-completion/succes" title="Ton Duo arrive · Plume Astrale" />

      <div className="max-w-2xl mx-auto text-center">
        <div className="mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full mb-4"
            style={{ background: 'linear-gradient(135deg, rgba(212,175,55,0.15), rgba(212,175,55,0.05))', border: '1px solid rgba(212,175,55,0.35)' }}>
            <CheckCircle2 className="w-10 h-10" style={{ color: '#D4AF37' }} strokeWidth={1.4} />
          </div>
          <p className="text-[10px] uppercase mb-3" style={{ color: '#D4AF37', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}>
            ✦ Paiement Confirmé ✦
          </p>
          <h1 style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, fontSize: 'clamp(32px, 5vw, 48px)', color: '#F5EEE0', lineHeight: 1.15 }}>
            Ton <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>Duo</em> se compose
          </h1>
          <p className="mt-4" style={{ color: 'rgba(227,215,255,0.75)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
            Ta Numérologie et ta Kabbale sont en cours de rédaction — livraison par email dans quelques minutes.
          </p>
        </div>

        <div className="plume-glass p-6 md:p-8 mb-8" data-testid="duo-completion-steps">
          {['numerologie', 'kabbale_arbre_de_vie'].map((kind) => {
            const child = (status.children || []).find((c) => c.kind === kind);
            const meta = CHILD_META[kind];
            const Icon = meta.icon;
            const ready = child?.pdf_ready;
            return (
              <div key={kind} className="flex items-center gap-3 py-3" data-testid={`duo-child-${kind}`}>
                <div className="shrink-0 w-9 h-9 rounded-full flex items-center justify-center"
                  style={{
                    background: ready ? 'rgba(74,222,128,0.15)' : 'rgba(212,175,55,0.10)',
                    border: `1px solid ${ready ? 'rgba(74,222,128,0.4)' : 'rgba(212,175,55,0.25)'}`,
                  }}>
                  {ready ? <CheckCircle2 className="w-4 h-4" style={{ color: '#4ADE80' }} strokeWidth={2} />
                    : <Loader2 className="w-4 h-4 animate-spin" style={{ color: '#D4AF37' }} strokeWidth={1.6} />}
                </div>
                <div className="flex-1 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-left">
                    <Icon className="w-4 h-4" style={{ color: '#D4AF37' }} strokeWidth={1.4} />
                    <span style={{ color: '#F5EEE0', fontFamily: 'Cormorant Garamond, serif', fontSize: 16 }}>
                      {meta.name}
                    </span>
                  </div>
                  {ready && child.pdf_url && (
                    <a href={child.pdf_url}
                      className="text-xs px-3 py-1.5 rounded-full inline-flex items-center gap-1.5"
                      data-testid={`duo-download-${kind}`}
                      style={{ background: 'rgba(212,175,55,0.15)', border: '1px solid rgba(212,175,55,0.4)', color: '#E8C766', textDecoration: 'none' }}>
                      <Download className="w-3 h-3" strokeWidth={1.6} />
                      PDF
                    </a>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {!status.all_ready && (
          <p className="text-xs" style={{ color: 'rgba(227,215,255,0.55)', letterSpacing: '0.15em' }}>
            <Mail className="w-3 h-3 inline mr-1" strokeWidth={1.5} />
            Tes 2 PDFs arriveront aussi par email dans les 3 minutes.
          </p>
        )}

        <div className="mt-8">
          <Link to="/" className="text-xs uppercase" style={{ color: 'rgba(212,175,55,0.7)', letterSpacing: '0.2em', textDecoration: 'none' }}>
            Retour à l&apos;accueil
          </Link>
        </div>
      </div>
    </div>
  );
};

export default DuoCompletionSucces;
