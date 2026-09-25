import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, ArrowLeft, ArrowRight, Coins, LogIn, Sparkles, Star } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import SEO from '@/components/SEO';
import { EnrichedBadge } from '@/components/EnrichedBadge';
import { FadeInEnrichedText } from '@/components/FadeInEnrichedText';
import axios from 'axios';
import useCardFlipSound from '@/hooks/useCardFlipSound';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// ── Styles inline pour l'animation de retournement de carte ──────────────────
const cardFlipStyle = `
  @keyframes cardReveal {
    0%   { opacity: 0; transform: rotateY(-90deg) scale(0.85); }
    60%  { opacity: 1; transform: rotateY(8deg) scale(1.03); }
    100% { opacity: 1; transform: rotateY(0deg) scale(1); }
  }
  @keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 30px rgba(212,175,55,0.15), 0 0 60px rgba(120,80,200,0.08); }
    50%       { box-shadow: 0 0 50px rgba(212,175,55,0.35), 0 0 100px rgba(120,80,200,0.18); }
  }
  @keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .card-flip-reveal { animation: cardReveal 0.7s cubic-bezier(0.34,1.56,0.64,1) forwards; }
  .card-glow        { animation: glowPulse 3s ease-in-out infinite; }
  .fade-slide-up    { animation: fadeSlideUp 0.6s ease forwards; }
  .fade-delay-1     { animation-delay: 0.15s; opacity: 0; }
  .fade-delay-2     { animation-delay: 0.30s; opacity: 0; }
  .fade-delay-3     { animation-delay: 0.50s; opacity: 0; }
`;

const TarotOuiNon = () => {
  const navigate = useNavigate();
  const { isAuthenticated, token, creditBalance, refreshBalance } = useAuth();
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isRevealed, setIsRevealed] = useState(false);
  const [freeUsed, setFreeUsed] = useState(null);
  const [creditError, setCreditError] = useState('');
  const [imgError, setImgError] = useState(false);
  const playFlip = useCardFlipSound(0.4);

  useEffect(() => {
    if (!isAuthenticated || !token) { setFreeUsed(false); return; }
    axios.get(`${API_URL}/api/credits/check-free-tarot`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then(r => setFreeUsed(r.data.free_used)).catch(() => setFreeUsed(false));
  }, [isAuthenticated, token]);

  const handleTirage = async () => {
    if (!question.trim() || !isAuthenticated) return;
    setCreditError('');
    setLoading(true);
    setResult(null);
    setIsRevealed(false);
    setImgError(false);
    try {
      const creditRes = await axios.post(`${API_URL}/api/credits/use`,
        { service_id: 'tarot_oui_non' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (creditRes.data.free_draw) setFreeUsed(true);
    } catch (err) {
      const detail = err.response?.data?.detail || '';
      setCreditError(detail.includes('insuffisants') ? 'insufficient' : (detail || 'Erreur crédits'));
      setLoading(false);
      return;
    }
    try {
      const res = await fetch(`${API_URL}/api/tarot/oui-non`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question.trim() }),
      });
      const data = await res.json();
      setResult(data);
      await refreshBalance();
      setTimeout(() => { setIsRevealed(true); playFlip(); }, 800);
    } catch (e) {
      console.error('Tarot error:', e);
    }
    setLoading(false);
  };

  const getOrientationConfig = (orientation) => {
    if (orientation === 'oui') return {
      color: '#7CB88A', bg: 'rgba(124,184,138,0.08)',
      border: 'rgba(124,184,138,0.3)', label: 'OUI',
      icon: '✦', glow: 'rgba(124,184,138,0.2)'
    };
    if (orientation === 'non') return {
      color: '#C97878', bg: 'rgba(201,120,120,0.08)',
      border: 'rgba(201,120,120,0.3)', label: 'NON',
      icon: '✧', glow: 'rgba(201,120,120,0.2)'
    };
    return {
      color: '#D4AF37', bg: 'rgba(212,175,55,0.08)',
      border: 'rgba(212,175,55,0.3)', label: 'NEUTRE',
      icon: '◈', glow: 'rgba(212,175,55,0.2)'
    };
  };

  // ── Gate non connecté ────────────────────────────────────────────────────────
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen relative">
        <style>{cardFlipStyle}</style>
        <SEO path="/tarot-oui-non" />
        <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
          <div className="max-w-xl mx-auto">
            <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12 flex items-center gap-2">
              <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
            </button>
            <div className="mb-10">
              <p className="text-xs tracking-widest uppercase mb-3" style={{ color: 'var(--pa-accent)', letterSpacing: '0.14em' }}>Tirage sacré</p>
              <h1 className="text-4xl md:text-5xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)', lineHeight: 1.15 }}>
                Tarot Oui / Non
              </h1>
              <p className="text-sm" style={{ color: 'var(--pa-muted)', lineHeight: 1.8 }}>
                Posez votre question et laissez les Arcanes Majeurs vous répondre
              </p>
            </div>
            <div className="rounded-2xl p-8 text-center" style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}>
              <LogIn className="w-9 h-9 mx-auto mb-5" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
              <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                Connexion requise
              </h2>
              <p className="text-sm mb-1" style={{ color: 'var(--pa-muted)' }}>Connectez-vous pour accéder au Tarot Oui&nbsp;/&nbsp;Non.</p>
              <p className="text-sm mb-7" style={{ color: '#D4AF37' }}>1er tirage gratuit · puis 5 crédits · 20 crédits offerts à l&apos;inscription</p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button onClick={() => navigate('/connexion')} className="text-xs uppercase tracking-widest px-7 py-3 rounded-full transition-all duration-300 hover:bg-[rgba(212,175,55,0.08)]" style={{ border: '1px solid rgba(212,175,55,0.5)', color: '#D4AF37', letterSpacing: '0.1em' }}>
                  Se connecter
                </button>
                <button onClick={() => navigate('/inscription')} className="text-xs uppercase tracking-widest px-7 py-3 rounded-full transition-all duration-300" style={{ border: '1px solid #D4AF37', color: '#111625', background: '#D4AF37', letterSpacing: '0.1em', fontWeight: 600 }}>
                  Créer un compte
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Gate crédits insuffisants ────────────────────────────────────────────────
  if (creditError === 'insufficient') {
    return (
      <div className="min-h-screen relative">
        <style>{cardFlipStyle}</style>
        <SEO path="/tarot-oui-non" />
        <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
          <div className="max-w-xl mx-auto">
            <button onClick={() => { setCreditError(''); }} className="link-editorial text-xs mb-12 flex items-center gap-2">
              <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Retour
            </button>
            <div className="rounded-2xl p-8 text-center" style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}>
              <Coins className="w-9 h-9 mx-auto mb-5" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
              <h2 className="text-xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>Crédits insuffisants</h2>
              <p className="text-sm mb-1" style={{ color: 'var(--pa-muted)' }}>Ce tirage coûte <span style={{ color: '#D4AF37', fontWeight: 600 }}>5 crédits</span>.</p>
              <p className="text-sm mb-7" style={{ color: 'var(--pa-muted)' }}>Votre solde : <span style={{ color: '#D4AF37' }}>{creditBalance} crédits</span></p>
              <button onClick={() => navigate('/acheter-credits')} className="flex items-center gap-2 mx-auto text-xs uppercase tracking-widest px-7 py-3 rounded-full transition-all duration-300" style={{ border: '1px solid #D4AF37', color: '#111625', background: '#D4AF37', letterSpacing: '0.1em', fontWeight: 600 }}>
                Acheter des crédits <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Page principale ──────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen relative">
      <style>{cardFlipStyle}</style>
      <SEO path="/tarot-oui-non" />
      <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
        <div className="max-w-2xl mx-auto">

          {/* Retour */}
          <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12 flex items-center gap-2">
            <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
          </button>

          {/* En-tête */}
          <div className="mb-10">
            <p className="text-xs tracking-widest uppercase mb-3" style={{ color: 'var(--pa-accent)', letterSpacing: '0.14em' }}>Tirage sacré</p>
            <h1 className="text-4xl md:text-5xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)', lineHeight: 1.15 }}>
              Tarot Oui / Non
            </h1>
            <p className="text-sm" style={{ color: 'var(--pa-muted)', lineHeight: 1.8 }}>
              Posez votre question et laissez les Arcanes Majeurs vous répondre
            </p>
          </div>

          {/* Info crédits */}
          <div className="mb-8 flex items-center gap-2">
            <Coins className="w-4 h-4 flex-shrink-0" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
            <span className="text-xs" style={{ color: 'var(--pa-accent)', letterSpacing: '0.08em' }}>
              {freeUsed === false ? '✦ 1er tirage offert' : `5 crédits par tirage · Solde : ${creditBalance} crédits`}
            </span>
          </div>

          {/* Formulaire */}
          <div className="mb-10 rounded-2xl p-6 md:p-8" style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}>
            <label className="block text-xs tracking-widest uppercase mb-3" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
              Votre question
            </label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ex : Vais-je trouver l'amour cette année ? Mon projet va-t-il aboutir ?"
              className="resize-none w-full rounded-xl p-4 text-sm outline-none transition-all duration-300"
              rows={3}
              style={{
                background: 'var(--pa-bg)',
                border: '1px solid var(--pa-divider)',
                color: 'var(--pa-body)',
                lineHeight: '1.7',
              }}
              onFocus={e => e.target.style.borderColor = 'rgba(212,175,55,0.5)'}
              onBlur={e => e.target.style.borderColor = 'var(--pa-divider)'}
            />
            {creditError && creditError !== 'insufficient' && (
              <p className="text-xs mt-2" style={{ color: '#fca5a5' }}>{creditError}</p>
            )}
            <button
              onClick={handleTirage}
              disabled={loading || !question.trim()}
              className="mt-5 w-full flex items-center justify-center gap-3 py-3.5 rounded-xl text-sm tracking-widest uppercase transition-all duration-300 disabled:opacity-30 disabled:cursor-not-allowed"
              style={{
                background: loading || !question.trim() ? 'var(--pa-surface-hover)' : '#D4AF37',
                color: loading || !question.trim() ? 'var(--pa-muted)' : '#111625',
                fontWeight: 600, letterSpacing: '0.12em',
                border: '1px solid rgba(212,175,55,0.4)',
              }}
            >
              {loading ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Consultation des Arcanes...</>
              ) : (
                <><Sparkles className="w-4 h-4" /> {freeUsed === false ? 'Tirer une carte (gratuit)' : 'Tirer une carte (5 crédits)'}</>
              )}
            </button>
          </div>

          {/* ── RÉSULTAT ── */}
          {result && isRevealed && (() => {
            const oc = getOrientationConfig(result.orientation);
            const raw = result.carte?.image;
            // Supporte : URL absolue Supabase CDN (https://…) OU chemin relatif (/api/…)
            const imageUrl = raw
              ? (raw.startsWith('http') ? raw : `${API_URL}${raw}`)
              : null;
            return (
              <div className="mt-4">
                {/* Carte révélée */}
                <div className="flex flex-col items-center mb-10">
                  <p className="text-xs tracking-widest uppercase mb-7" style={{ color: 'var(--pa-muted)', letterSpacing: '0.14em' }}>
                    ✦ Arcane tiré ✦
                  </p>

                  {/* Image de la carte — grande et belle, flip 3D magique */}
                  <div
                    className="tarot-flip-scene mb-7"
                    style={{
                      width: '200px', height: '340px',
                    }}
                  >
                    <div
                      className={`tarot-flip-inner ${isRevealed ? 'is-flipped' : ''}`}
                      data-testid="tarot-flip-card"
                    >
                      {/* Dos de carte (visible initialement) */}
                      <div className="tarot-flip-back">
                        <div className="tarot-back-pattern">
                          <div className="tarot-back-star">✦</div>
                          <div className="tarot-back-title">PLUME ASTRALE</div>
                          <div className="tarot-back-star">✦</div>
                        </div>
                      </div>
                      {/* Face de carte (révélée après le flip) */}
                      <div
                        className={`tarot-flip-front ${result.carte?.is_reversed ? 'is-reversed' : ''}`}
                        style={{
                          border: `2px solid ${oc.border}`,
                          boxShadow: `0 0 40px ${oc.glow}, 0 20px 60px rgba(0,0,0,0.5)`,
                        }}
                      >
                        {imageUrl && !imgError ? (
                          <img
                            src={imageUrl}
                            alt={result.carte.nom}
                            className="w-full h-full object-cover"
                            onError={() => setImgError(true)}
                          />
                        ) : (
                          <div className="w-full h-full flex flex-col items-center justify-center gap-3"
                               style={{ background: 'linear-gradient(160deg, var(--pa-surface) 0%, var(--pa-bg-deep) 100%)' }}>
                            <span className="text-5xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-accent)', fontWeight: 300 }}>
                              {result.carte?.numero === 0 ? '0' : (result.carte?.numero || 'I')}
                            </span>
                            <Star className="w-5 h-5" style={{ color: oc.color, opacity: 0.6 }} strokeWidth={1} />
                            <span className="text-xs text-center px-4" style={{ color: 'var(--pa-muted)', fontFamily: 'Cormorant Garamond, serif', fontSize: '11px', lineHeight: 1.5 }}>
                              {result.carte?.nom}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Badge "Carte retournée" */}
                  {result.carte?.is_reversed && (
                    <div
                      className="mb-4 px-3 py-1 rounded-full text-[10px] uppercase inline-flex items-center gap-1.5"
                      data-testid="tarot-reversed-badge"
                      style={{
                        background: 'rgba(212,175,55,0.12)',
                        border: '1px solid rgba(212,175,55,0.4)',
                        color: '#D4AF37',
                        letterSpacing: '0.22em',
                        fontFamily: 'Cinzel, serif',
                      }}
                    >
                      🔄 Carte retournée
                    </div>
                  )}

                  {/* Nom + énergie */}
                  <div className="fade-slide-up fade-delay-1 text-center">
                    <h2 className="text-2xl md:text-3xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                      {result.carte?.nom}
                    </h2>
                    <p className="text-xs mb-6" style={{ color: 'var(--pa-muted)', letterSpacing: '0.08em', fontStyle: 'italic' }}>
                      {result.carte?.energie}
                    </p>
                  </div>

                  {/* Badge OUI / NON / NEUTRE */}
                  <div className="fade-slide-up fade-delay-2">
                    <span className="inline-flex items-center gap-2 px-8 py-2.5 rounded-full text-sm tracking-widest uppercase font-semibold"
                      style={{ color: oc.color, background: oc.bg, border: `1px solid ${oc.border}`, letterSpacing: '0.18em' }}>
                      <span style={{ fontSize: '16px' }}>{oc.icon}</span>
                      {oc.label}
                      <span style={{ fontSize: '16px' }}>{oc.icon}</span>
                    </span>
                  </div>
                </div>

                {/* Message des Arcanes */}
                <div className="fade-slide-up fade-delay-2 rounded-2xl p-6 md:p-8 mb-8"
                     style={{ background: 'var(--pa-surface)', border: `1px solid ${oc.border}` }}>
                  <div className="flex items-center justify-between flex-wrap gap-2 mb-4">
                    <p className="text-xs tracking-widest uppercase" style={{ color: oc.color, letterSpacing: '0.14em' }}>
                      ✦ Message des Arcanes
                    </p>
                    <EnrichedBadge variant="compact" visible={!!result.reponse_enrichie} />
                  </div>
                  <FadeInEnrichedText
                    text={result.reponse}
                    enabled={!!result.reponse_enrichie}
                    speed={160}
                    style={{ color: 'var(--pa-body)', lineHeight: '1.95', fontFamily: 'Cormorant Garamond, serif', fontSize: '17px' }}
                    dataTestid="tarot-response-text"
                  />
                </div>

                {/* Énergie de la carte */}
                <div className="fade-slide-up fade-delay-3 rounded-2xl p-5 mb-8"
                     style={{ background: 'rgba(212,175,55,0.04)', border: '1px solid rgba(212,175,55,0.12)' }}>
                  <p className="text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
                    Énergie de la carte
                  </p>
                  <p className="text-sm" style={{ color: 'var(--pa-muted)', lineHeight: 1.8 }}>
                    {result.carte?.energie}
                  </p>
                </div>

                {/* Nouveau tirage */}
                <div className="fade-slide-up fade-delay-3 flex flex-col sm:flex-row gap-3 mb-10">
                  <button
                    onClick={() => { setResult(null); setIsRevealed(false); setQuestion(''); setImgError(false); }}
                    className="flex-1 py-3 rounded-xl text-xs uppercase tracking-widest transition-all duration-300 hover:bg-[rgba(212,175,55,0.08)]"
                    style={{ border: '1px solid rgba(212,175,55,0.3)', color: '#D4AF37', letterSpacing: '0.12em' }}
                  >
                    Nouveau tirage
                  </button>
                  <button
                    onClick={() => navigate('/tirage-tarot')}
                    className="flex-1 py-3 rounded-xl text-xs uppercase tracking-widest transition-all duration-300"
                    style={{ border: '1px solid rgba(212,175,55,0.5)', color: '#111625', background: '#D4AF37', letterSpacing: '0.12em', fontWeight: 600 }}
                  >
                    Tirage approfondi
                  </button>
                </div>

                {/* Pour aller plus loin */}
                <div className="pt-8" style={{ borderTop: '1px solid var(--pa-divider)' }}>
                  <p className="text-xs tracking-widest uppercase mb-5" style={{ color: 'var(--pa-muted)', letterSpacing: '0.12em' }}>Pour aller plus loin</p>
                  <div className="space-y-4">
                    <button onClick={() => navigate('/tarologie')} className="block w-full text-left group rounded-xl p-4 transition-all duration-300 hover:bg-[var(--pa-surface)]">
                      <p className="text-sm mb-1 transition-colors duration-300 group-hover:text-[#D4AF37]" style={{ color: 'var(--pa-heading)' }}>
                        Tarologie & Lecture Symbolique — 35 €
                      </p>
                      <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>Tirage complet 7 cartes + lecture symbolique en PDF</p>
                    </button>
                    <button onClick={() => navigate('/formulaire')} className="block w-full text-left group rounded-xl p-4 transition-all duration-300 hover:bg-[var(--pa-surface)]">
                      <p className="text-sm mb-1 transition-colors duration-300 group-hover:text-[#D4AF37]" style={{ color: 'var(--pa-heading)' }}>
                        Votre Thème Astral Complet
                      </p>
                      <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>Carte du ciel, aspects planétaires et prévisions 2026</p>
                    </button>
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      </div>
    </div>
  );
};

export default TarotOuiNon;
