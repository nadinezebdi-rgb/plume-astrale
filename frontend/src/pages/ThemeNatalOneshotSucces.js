import React, { useEffect, useState, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { CheckCircle2, Download, ArrowRight, Loader2, Mail, Star, Moon, Sparkles, Zap } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import CercleSolenaInvite from '@/components/CercleSolenaInvite';
import { useAuth } from '@/context/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL;

const STEPS = [
  { key: 'payment', label: 'Paiement confirmé' },
  { key: 'compute', label: 'Calcul de tes 11 planètes & aspects' },
  { key: 'pdf', label: 'Génération de ton PDF luxe (20-40 pages)' },
  { key: 'email', label: 'Envoi par email' },
];

const ThemeNatalOneshotSucces = () => {
  const { token } = useAuth();
  const [params] = useSearchParams();
  const sessionId = params.get('session_id');
  const [status, setStatus] = useState({});
  const [polling, setPolling] = useState(true);
  const [duoLoading, setDuoLoading] = useState(false);
  const [duoError, setDuoError] = useState(null);

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

  // Cross-sell : passe au checkout Duo Complémentaire en réutilisant les infos du Thème Natal
  const launchDuoUpsell = async () => {
    setDuoError(null);
    setDuoLoading(true);
    try {
      // 1) Récupère le pdf_ctx depuis le Thème Natal parent
      const ctxRes = await axios.get(`${API}/api/duo-completion/pdf-ctx-for-theme-natal?session_id=${sessionId}`);
      const ctx = ctxRes.data || {};
      if (!ctx.has_context) throw new Error('Contexte astral introuvable');
      // 2) Lance le checkout Duo avec les infos pré-remplies
      const r = await axios.post(
        `${API}/api/duo-completion/checkout`,
        {
          email: ctx.email,
          first_name: ctx.first_name,
          birth_date: ctx.birth_date,
          birth_time: typeof ctx.birth_time === 'number' ? String(ctx.birth_time).padStart(2, '0') + ':00' : (ctx.birth_time || '12:00'),
          birth_city: ctx.birth_city || 'Paris',
          birth_country: 'FR',
          latitude: ctx.latitude,
          longitude: ctx.longitude,
          origin_url: window.location.origin,
          parent_theme_natal_session_id: sessionId,
        },
        token ? { headers: { Authorization: `Bearer ${token}` } } : {},
      );
      if (r.data?.url) window.location.href = r.data.url;
      else setDuoError('Une erreur est survenue');
    } catch (e) {
      setDuoError(e.response?.data?.detail || e.message || 'Impossible de créer la session Duo');
    } finally {
      setDuoLoading(false);
    }
  };

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

        {/* ═══ CROSS-SELL DUO COMPLÉMENTAIRE (Gary Vee post-purchase upsell) ═══ */}
        {status.pdf_ready && (
          <div
            className="mt-12 mb-4 p-6 md:p-8 rounded-2xl relative overflow-hidden text-left"
            data-testid="theme-natal-cross-sell-duo"
            style={{
              background: 'linear-gradient(135deg, rgba(212,175,55,0.08) 0%, rgba(232,199,102,0.04) 100%)',
              border: '1px solid rgba(212,175,55,0.35)',
              boxShadow: '0 20px 60px -25px rgba(212,175,55,0.35)',
            }}
          >
            <div
              className="absolute top-3 right-3 px-2.5 py-1 rounded-full text-[9px] uppercase"
              style={{
                background: 'linear-gradient(135deg, #D4AF37, #E8C766)',
                color: '#0A0603',
                fontFamily: 'Cinzel, serif',
                letterSpacing: '0.18em',
                fontWeight: 700,
              }}
            >
              Recommandé
            </div>

            <p
              className="text-[10px] uppercase mb-3"
              style={{ color: '#D4AF37', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}
            >
              ✦ Complète Ton Portrait ✦
            </p>

            <h2
              style={{
                fontFamily: 'Cormorant Garamond, serif',
                fontWeight: 300,
                fontSize: 'clamp(24px, 3.5vw, 34px)',
                color: '#F5EEE0',
                lineHeight: 1.2,
                marginBottom: 12,
              }}
            >
              Tu viens de recevoir ton Thème Natal.
              <br />
              <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>
                Deux miroirs manquent encore à ton reflet.
              </em>
            </h2>

            <p
              className="mb-5"
              style={{
                color: 'rgba(227,215,255,0.8)',
                fontFamily: 'Cormorant Garamond, serif',
                fontSize: 16,
                lineHeight: 1.6,
                fontStyle: 'italic',
              }}
            >
              Ta <strong style={{ color: '#F5EEE0', fontStyle: 'normal' }}>Numérologie sacrée</strong> et
              ton <strong style={{ color: '#F5EEE0', fontStyle: 'normal' }}>Arbre de Vie Kabbale</strong> lisent
              ton âme sous deux angles complémentaires. Ils raisonnent avec ton ciel — tu comprendras pourquoi ton
              Soleil chante ces notes précises.
            </p>

            {/* What's included mini */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-5">
              {[
                { icon: Star, name: 'Numérologie Sacrée', page: '12', desc: 'Chemin de vie, année perso, année maîtresse' },
                { icon: Moon, name: 'Arbre de Vie Kabbale', page: '15', desc: 'Les 10 sephiroth · tes correspondances' },
              ].map((item, i) => {
                const Icon = item.icon;
                return (
                  <div
                    key={i}
                    className="flex items-start gap-3 p-3 rounded-xl"
                    data-testid={`cross-sell-item-${i}`}
                    style={{ background: 'rgba(17,22,37,0.4)', border: '1px solid rgba(212,175,55,0.15)' }}
                  >
                    <div
                      className="shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
                      style={{ background: 'rgba(212,175,55,0.12)', border: '1px solid rgba(212,175,55,0.35)' }}
                    >
                      <Icon className="w-4 h-4" style={{ color: '#D4AF37' }} strokeWidth={1.4} />
                    </div>
                    <div>
                      <div
                        style={{
                          fontFamily: 'Cormorant Garamond, serif',
                          fontSize: 15,
                          color: '#F5EEE0',
                          fontWeight: 500,
                          marginBottom: 2,
                        }}
                      >
                        {item.name}
                      </div>
                      <div
                        className="text-xs"
                        style={{ color: 'rgba(227,215,255,0.7)', lineHeight: 1.4 }}
                      >
                        PDF {item.page} pages · {item.desc}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Prix + économie + CTA */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="flex items-baseline gap-3">
                <span
                  style={{
                    color: 'rgba(227,215,255,0.55)',
                    textDecoration: 'line-through',
                    fontSize: 18,
                    fontFamily: 'Cormorant Garamond, serif',
                  }}
                >
                  58€
                </span>
                <span
                  style={{
                    fontFamily: 'Cormorant Garamond, serif',
                    fontSize: 42,
                    fontWeight: 300,
                    color: '#D4AF37',
                    lineHeight: 1,
                  }}
                  data-testid="cross-sell-duo-price"
                >
                  50€
                </span>
                <div
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full"
                  style={{
                    background: 'linear-gradient(135deg, rgba(74,222,128,0.15), rgba(74,222,128,0.05))',
                    border: '1px solid rgba(74,222,128,0.3)',
                  }}
                >
                  <Zap className="w-3 h-3" style={{ color: '#4ADE80' }} strokeWidth={2} />
                  <span
                    style={{
                      color: '#4ADE80',
                      fontSize: 10,
                      fontFamily: 'Cinzel, serif',
                      letterSpacing: '0.15em',
                    }}
                  >
                    -8€
                  </span>
                </div>
              </div>

              <button
                onClick={launchDuoUpsell}
                disabled={duoLoading}
                className="plume-btn-primary"
                data-testid="cross-sell-duo-cta"
                style={{ display: 'inline-flex', whiteSpace: 'nowrap' }}
              >
                {duoLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> Redirection...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" strokeWidth={1.5} />
                    Ajouter à mon portrait
                  </>
                )}
              </button>
            </div>

            {duoError && (
              <p
                className="text-xs mt-3"
                style={{ color: '#F87171' }}
                data-testid="cross-sell-duo-error"
              >
                {duoError}
              </p>
            )}

            <p
              className="text-[10px] mt-4"
              style={{ color: 'rgba(227,215,255,0.45)', letterSpacing: '0.15em' }}
            >
              Aucune info à re-saisir — tes coordonnées astrales sont déjà connues.
            </p>
          </div>
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
