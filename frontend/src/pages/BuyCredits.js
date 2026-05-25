import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Coins, Sparkles, Star, Zap, ArrowRight, Shield, Tag, Loader2, MessageCircle, Moon } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

const PromoCodeSection = ({ token, onSuccess }) => {
  const [open, setOpen] = useState(false);
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleApply = async () => {
    if (!code.trim()) return;
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const res = await axios.post(`${API}/api/credits/promo`, { code }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSuccess(res.data.description + ' — ' + res.data.credits_added + ' credits ajoutes !');
      setCode('');
      if (onSuccess) onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Code invalide');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="text-center mb-10" data-testid="promo-section">
      {!open ? (
        <button
          onClick={() => setOpen(true)}
          className="inline-flex items-center gap-1.5 text-xs transition-colors hover:text-[#C5A059]"
          style={{ color: 'var(--pa-muted)' }}
          data-testid="show-promo-btn"
        >
          <Tag className="w-3 h-3" /> Code promo
        </button>
      ) : (
        <div className="max-w-sm mx-auto space-y-2">
          <div className="flex gap-2">
            <input
              type="text"
              value={code}
              onChange={e => { setCode(e.target.value.toUpperCase()); setError(''); }}
              placeholder="Code promo"
              className="flex-1 px-4 py-2 bg-transparent border rounded-full text-center text-sm outline-none transition-colors"
              style={{ borderColor: 'rgba(197,160,89,0.3)', color: 'var(--pa-body)' }}
              onFocus={e => e.target.style.borderColor = '#C5A059'}
              onBlur={e => e.target.style.borderColor = 'rgba(197,160,89,0.3)'}
              data-testid="promo-code-input"
            />
            <button
              onClick={handleApply}
              disabled={loading || !code.trim()}
              className="px-5 py-2 rounded-full text-xs uppercase tracking-widest transition-all disabled:opacity-50"
              style={{ border: '1px solid rgba(197,160,89,0.4)', color: '#C5A059', letterSpacing: '0.08em' }}
              data-testid="apply-promo-btn"
            >
              {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Appliquer'}
            </button>
          </div>
          {error && <p className="text-xs" style={{ color: '#fca5a5' }} data-testid="promo-error">{error}</p>}
          {success && <p className="text-xs" style={{ color: '#7CB88A' }} data-testid="promo-success">{success}</p>}
        </div>
      )}
    </div>
  );
};

const PACKS = [
  {
    id: 'starter',
    name: 'Starter',
    credits: 20,
    amount: 4.99,
    icon: Star,
    badge: null,
    projections: ['10 tirages Oui / Non', '2 lectures astrologiques'],
  },
  {
    id: 'popular',
    name: 'Populaire',
    credits: 120,
    amount: 19.99,
    icon: Sparkles,
    badge: 'Le plus choisi',
    projections: ['60 tirages Oui / Non', '12 lectures approfondies', '2 cartographies'],
  },
  {
    id: 'premium',
    name: 'Premium',
    credits: 350,
    amount: 49,
    icon: Zap,
    badge: 'Meilleure valeur',
    projections: ['175 tirages Oui / Non', '35 lectures approfondies', '5 cartographies'],
  },
];

// Packs dedies a la Consultation astrale personnalisee (2 credits par message)
const CHAT_PACKS = [
  {
    id: 'chat_lueur',
    name: 'Lueur',
    credits: 20,
    amount: 4.99,
    icon: MessageCircle,
    badge: null,
    messages: 10,
    projections: ['10 messages de consultation', 'Reponses en francais', 'Guidance personnalisee'],
  },
  {
    id: 'chat_constellation',
    name: 'Constellation',
    credits: 60,
    amount: 12.99,
    icon: Sparkles,
    badge: 'Le plus choisi',
    messages: 30,
    projections: ['30 messages de consultation', 'Conversations approfondies', 'Acces a toutes les questions'],
  },
  {
    id: 'chat_voie_lactee',
    name: 'Voie Lactee',
    credits: 150,
    amount: 24.99,
    icon: Moon,
    badge: 'Meilleure valeur',
    messages: 75,
    projections: ['75 messages de consultation', 'Exploration spirituelle complete', 'Utilisable sur tout le site'],
  },
];

const SERVICE_COSTS = [
  { name: 'Tarot Oui / Non', cost: '1er tirage gratuit, puis 2 credits' },
  { name: 'Consultation astrale personnalisée', cost: '2 credits / message' },
  { name: 'Lecture Tarot approfondie', cost: '10 credits' },
  { name: 'Lecture astrologique', cost: '10 credits' },
  { name: 'Numerologie', cost: '10 credits' },
  { name: 'Cartographie Premium', cost: '60 credits' },
];

export default function BuyCredits() {
  const { isAuthenticated, token, creditBalance, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [loadingPack, setLoadingPack] = useState(null);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) { navigate('/connexion'); }
  }, [isAuthenticated, navigate, authLoading]);

  const handleBuy = async (packId) => {
    setLoadingPack(packId);
    try {
      const res = await axios.post(
        `${API}/api/credits/checkout`,
        { pack_id: packId, origin_url: window.location.origin },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      window.location.href = res.data.url;
    } catch (err) {
      alert(err.response?.data?.detail || 'Erreur');
      setLoadingPack(null);
    }
  };

  return (
    <div className="min-h-screen pt-24 pb-16 px-4" data-testid="buy-credits-page">
      <SEO path="/acheter-credits" />
      <div className="max-w-3xl mx-auto">

        {creditBalance <= 20 && (
          <div
            className="mb-8 p-4 rounded-xl text-center"
            style={{ background: 'rgba(197,160,89,0.08)', border: '1px solid rgba(197,160,89,0.2)' }}
            data-testid="bonus-banner"
          >
            <p className="text-sm" style={{ color: '#C5A059' }}>
              20 credits offerts a l&#39;inscription pour commencer votre exploration
            </p>
          </div>
        )}

        <div className="text-center mb-4">
          <div className="flex items-center justify-center gap-3 mb-3">
            <Coins className="w-6 h-6" style={{ color: '#C5A059' }} strokeWidth={1.5} />
            <h1
              className="text-3xl sm:text-4xl"
              style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}
            >
              Acheter des credits
            </h1>
          </div>
          <p className="text-sm mb-2" style={{ color: 'var(--pa-muted)' }}>
            Votre solde actuel :
            <span style={{ color: '#C5A059', fontWeight: 600 }} data-testid="current-balance">
              {' '}{creditBalance} credits
            </span>
          </p>
        </div>

        <p className="text-center text-sm mb-10" style={{ color: 'var(--pa-body)', opacity: 0.8 }}>
          Chaque experience est personnalisee a partir de vos donnees astrologiques.
        </p>

        {/* ===== SECTION CHAT PACKS ===== */}
        <div className="mb-12">
          <div className="text-center mb-6">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-3" style={{ background: 'rgba(197,160,89,0.08)', border: '1px solid rgba(197,160,89,0.2)' }}>
              <MessageCircle className="w-3.5 h-3.5" style={{ color: '#C5A059' }} />
              <span className="text-[11px] uppercase tracking-widest" style={{ color: '#C5A059', letterSpacing: '0.1em', fontWeight: 600 }}>
                Nouveau — Packs Consultation astrale
              </span>
            </div>
            <h2 className="text-2xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
              Packs Conversation
            </h2>
            <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
              Pose tes questions a l&#39;oracle IA. 2 credits par message — en francais.
            </p>
          </div>

          <div className="grid gap-5 md:grid-cols-3">
            {CHAT_PACKS.map((pack) => {
              const isPopular = pack.id === 'chat_constellation';
              const Icon = pack.icon;
              return (
                <div
                  key={pack.id}
                  className={`rounded-2xl p-6 relative transition-all duration-300 hover:scale-[1.02] ${isPopular ? 'md:-translate-y-2' : ''}`}
                  style={{
                    background: isPopular ? 'rgba(197,160,89,0.07)' : 'rgba(255,255,255,0.03)',
                    border: isPopular ? '1px solid rgba(197,160,89,0.4)' : '1px solid rgba(197,160,89,0.15)',
                    backdropFilter: 'blur(12px)',
                  }}
                  data-testid={`chat-pack-card-${pack.id}`}
                >
                  {pack.badge && (
                    <div
                      className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-[10px] uppercase tracking-widest whitespace-nowrap"
                      style={{ background: '#C5A059', color: '#0C0918', letterSpacing: '0.08em', fontWeight: 600 }}
                    >
                      {pack.badge}
                    </div>
                  )}
                  <div className="flex flex-col items-center text-center pt-2">
                    <div className="mb-3" style={{ color: '#C5A059' }}>
                      <Icon className="w-7 h-7" strokeWidth={1.5} />
                    </div>
                    <h3 className="text-lg mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                      {pack.name}
                    </h3>
                    <div className="text-3xl mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#C5A059', fontWeight: 400 }}>
                      {pack.amount % 1 === 0 ? pack.amount : pack.amount.toFixed(2).replace('.', ',')} &euro;
                    </div>
                    <p className="text-sm mb-0" style={{ color: 'var(--pa-body)' }}>
                      {pack.messages} messages chat
                    </p>
                    <p className="text-xs mb-4" style={{ color: 'var(--pa-muted)' }}>
                      ({pack.credits} credits — {(pack.amount / pack.messages).toFixed(2).replace('.', ',')} &euro;/message)
                    </p>
                    <div className="w-full mb-4 py-3 px-3 rounded-lg text-left" style={{ background: 'rgba(197,160,89,0.05)', border: '1px solid rgba(197,160,89,0.08)' }}>
                      {pack.projections.map((p, i) => (
                        <p key={i} className="text-xs py-0.5" style={{ color: 'var(--pa-body)' }}>
                          &bull; {p}
                        </p>
                      ))}
                    </div>
                    <button
                      onClick={() => handleBuy(pack.id)}
                      disabled={loadingPack === pack.id}
                      className="w-full py-2.5 text-xs uppercase tracking-widest rounded-full transition-all duration-500"
                      style={{
                        border: `1px solid ${isPopular ? '#C5A059' : 'rgba(197,160,89,0.4)'}`,
                        color: loadingPack === pack.id ? 'var(--pa-muted)' : isPopular ? '#0C0918' : '#C5A059',
                        background: isPopular ? '#C5A059' : 'transparent',
                        letterSpacing: '0.1em',
                        fontWeight: isPopular ? 600 : 400,
                      }}
                      data-testid={`buy-chat-pack-${pack.id}`}
                    >
                      {loadingPack === pack.id ? 'Redirection...' : 'Acheter'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* ===== SECTION PACKS GENERAUX ===== */}
        <div className="text-center mb-6">
          <h2 className="text-2xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
            Packs Univers Complet
          </h2>
          <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
            Utilisables sur tout le site — tarot, astrologie, numerologie, chat.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-3">
          {PACKS.map((pack) => {
            const isPopular = pack.id === 'popular';
            const Icon = pack.icon;
            return (
              <div
                key={pack.id}
                className={`rounded-2xl p-6 relative transition-all duration-300 hover:scale-[1.02] ${isPopular ? 'md:-translate-y-2' : ''}`}
                style={{
                  background: isPopular ? 'rgba(197,160,89,0.07)' : 'rgba(255,255,255,0.03)',
                  border: isPopular ? '1px solid rgba(197,160,89,0.4)' : '1px solid rgba(197,160,89,0.15)',
                  backdropFilter: 'blur(12px)',
                }}
                data-testid={`pack-card-${pack.id}`}
              >
                {pack.badge && (
                  <div
                    className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-[10px] uppercase tracking-widest whitespace-nowrap"
                    style={{ background: '#C5A059', color: '#0C0918', letterSpacing: '0.08em', fontWeight: 600 }}
                    data-testid="popular-badge"
                  >
                    {pack.badge}
                  </div>
                )}
                <div className="flex flex-col items-center text-center pt-2">
                  <div className="mb-3" style={{ color: '#C5A059' }}>
                    <Icon className="w-7 h-7" strokeWidth={1.5} />
                  </div>
                  <h3 className="text-lg mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                    {pack.name}
                  </h3>
                  <div className="text-3xl mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#C5A059', fontWeight: 400 }}>
                    {pack.amount % 1 === 0 ? pack.amount : pack.amount.toFixed(2).replace('.', ',')} &euro;
                  </div>
                  <p className="text-sm mb-1" style={{ color: 'var(--pa-body)' }}>
                    {pack.credits} credits
                  </p>
                  <p className="text-xs mb-4" style={{ color: 'var(--pa-muted)' }}>
                    {(pack.amount / pack.credits).toFixed(2).replace('.', ',')} &euro; / credit
                  </p>
                  <div className="w-full mb-4 py-3 px-3 rounded-lg text-left" style={{ background: 'rgba(197,160,89,0.05)', border: '1px solid rgba(197,160,89,0.08)' }}>
                    <p className="text-[10px] uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.08em' }}>
                      Exemple :
                    </p>
                    {pack.projections.map((p, i) => (
                      <p key={i} className="text-xs py-0.5" style={{ color: 'var(--pa-body)' }}>
                        &bull; {p}
                      </p>
                    ))}
                  </div>
                  <button
                    onClick={() => handleBuy(pack.id)}
                    disabled={loadingPack === pack.id}
                    className="w-full py-2.5 text-xs uppercase tracking-widest rounded-full transition-all duration-500"
                    style={{
                      border: `1px solid ${isPopular ? '#C5A059' : 'rgba(197,160,89,0.4)'}`,
                      color: loadingPack === pack.id ? 'var(--pa-muted)' : isPopular ? '#0C0918' : '#C5A059',
                      background: isPopular ? '#C5A059' : 'transparent',
                      letterSpacing: '0.1em',
                      fontWeight: isPopular ? 600 : 400,
                    }}
                    data-testid={`buy-pack-${pack.id}`}
                  >
                    {loadingPack === pack.id ? 'Redirection...' : 'Acheter'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex items-center justify-center gap-2 mt-6 mb-6">
          <Shield className="w-4 h-4" style={{ color: 'var(--pa-muted)' }} strokeWidth={1.5} />
          <p className="text-xs" style={{ color: 'var(--pa-muted)' }} data-testid="no-expiry-note">
            Les credits ne expirent pas et peuvent etre utilises a votre rythme.
          </p>
        </div>

        <PromoCodeSection token={token} onSuccess={() => window.location.reload()} />

        <div className="rounded-2xl p-6 md:p-8" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(197,160,89,0.1)' }}>
          <h2 className="text-xl mb-5 text-center" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
            Que faire avec vos credits ?
          </h2>
          <div className="space-y-3">
            {SERVICE_COSTS.map(s => (
              <div key={s.name} className="flex items-center justify-between py-2" style={{ borderBottom: '1px solid rgba(197,160,89,0.08)' }}>
                <span className="text-sm" style={{ color: 'var(--pa-body)' }}>{s.name}</span>
                <span className="text-sm font-medium" style={{ color: '#C5A059' }}>{s.cost}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-12 text-center">
          <h3 className="text-lg mb-5" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
            Continuer l&#39;exploration
          </h3>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/tarot-oui-non"
              className="flex items-center justify-center gap-2 text-xs uppercase tracking-widest px-6 py-2.5 rounded-full transition-all duration-300 hover:bg-[#C5A059]/10"
              style={{ border: '1px solid rgba(197,160,89,0.3)', color: '#C5A059', letterSpacing: '0.08em' }}
              data-testid="cta-tarot">
              Tirage tarot <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <Link to="/formulaire"
              className="flex items-center justify-center gap-2 text-xs uppercase tracking-widest px-6 py-2.5 rounded-full transition-all duration-300 hover:bg-[#C5A059]/10"
              style={{ border: '1px solid rgba(197,160,89,0.3)', color: '#C5A059', letterSpacing: '0.08em' }}
              data-testid="cta-theme">
              Theme astral <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <Link to="/numerologie"
              className="flex items-center justify-center gap-2 text-xs uppercase tracking-widest px-6 py-2.5 rounded-full transition-all duration-300 hover:bg-[#C5A059]/10"
              style={{ border: '1px solid rgba(197,160,89,0.3)', color: '#C5A059', letterSpacing: '0.08em' }}
              data-testid="cta-numerologie">
              Numerologie <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

      </div>
    </div>
  );
}
