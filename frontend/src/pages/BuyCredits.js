import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Coins, Sparkles, Star, Zap, ArrowRight, Shield, Tag, Loader2, MessageCircle, Moon } from 'lucide-react';
import axios from 'axios';
import LibraryImage, { signFromDate } from '@/components/LibraryImage';
import SEO from '@/components/SEO';
import ServicesEquivalence from '@/components/ServicesEquivalence';

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
      const d = res.data;
      let msg = d.description || 'Code applique';
      if (d.premium_days_added > 0) {
        msg += ` — Premium offert ${d.premium_days_added} jours !`;
      } else if (d.credits_added > 0) {
        msg += ` — ${d.credits_added} credits ajoutes !`;
      }
      setSuccess(msg);
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
          className="inline-flex items-center gap-1.5 text-xs transition-colors hover:text-[#D4AF37]"
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
              style={{ borderColor: 'rgba(212,175,55,0.3)', color: 'var(--pa-body)' }}
              onFocus={e => e.target.style.borderColor = '#D4AF37'}
              onBlur={e => e.target.style.borderColor = 'rgba(212,175,55,0.3)'}
              data-testid="promo-code-input"
            />
            <button
              onClick={handleApply}
              disabled={loading || !code.trim()}
              className="px-5 py-2 rounded-full text-xs uppercase tracking-widest transition-all disabled:opacity-50"
              style={{ border: '1px solid rgba(212,175,55,0.4)', color: '#D4AF37', letterSpacing: '0.08em' }}
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
    id: 'comete',
    name: 'Comète',
    credits: 30,
    bonus: 0,
    amount: 7.99,
    icon: Star,
    badge: null,
    tagline: "L'étincelle rapide pour poser tes premières questions.",
    projections: ['3 questions à Plume', 'Reprends le fil sans attendre'],
  },
  {
    id: 'nebuleuse',
    name: 'Nébuleuse',
    credits: 80,
    bonus: 0,
    amount: 17.99,
    icon: Sparkles,
    badge: 'Le plus choisi',
    tagline: 'Ton Thème Natal complet accessible en 1 clic.',
    projections: ['8 questions à Plume', '1 Thème Natal complet (60 cr) + 2 questions', 'Ou 2 tarots approfondis'],
  },
  {
    id: 'constellation',
    name: 'Constellation',
    credits: 180,
    bonus: 0,
    amount: 34.99,
    icon: Zap,
    badge: 'Meilleure valeur',
    tagline: 'Explore ton thème en profondeur, ton karma, tes relations.',
    projections: ['18 questions à Plume', '3 Thèmes Natals complets', 'Karma & synastrie amoureuse'],
  },
  {
    id: 'voie_lactee',
    name: 'Voie Lactée',
    credits: 350,
    bonus: 0,
    amount: 59.99,
    icon: Zap,
    badge: null,
    tagline: "L'expérience complète, sans jamais compter.",
    projections: ['35 questions à Plume', 'Tous les rapports premium', 'Le grand voyage intérieur'],
  },
];

const SERVICE_COSTS = [
  { name: 'Consultation astrale personnalisée', cost: '10 crédits / question' },
  { name: 'Tarot Oui / Non', cost: '1er tirage gratuit, puis 2 crédits' },
  { name: 'Lecture Tarot approfondie', cost: '10 crédits' },
  { name: 'Lecture astrologique', cost: '20 crédits' },
  { name: 'Numérologie', cost: '10 crédits' },
  { name: 'Cartographie Premium', cost: '60 crédits' },
];

export default function BuyCredits() {
  const { isAuthenticated, token, creditBalance, loading: authLoading, user } = useAuth();
  const userSign = signFromDate(user?.birth_date);
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
            style={{ background: 'rgba(212,175,55,0.08)', border: '1px solid rgba(212,175,55,0.2)' }}
            data-testid="bonus-banner"
          >
            <p className="text-sm" style={{ color: '#D4AF37' }}>
              20 credits offerts a l&#39;inscription pour commencer votre exploration
            </p>
          </div>
        )}

        <div className="text-center mb-4">
          <div className="flex items-center justify-center gap-3 mb-3">
            {userSign ? (
              <LibraryImage type="sign" name={userSign} size={40} alt={`Signe ${userSign}`} />
            ) : (
              <Coins className="w-6 h-6" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
            )}
            <h1
              className="text-3xl sm:text-4xl"
              style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}
            >
              Acheter des credits
            </h1>
          </div>
          <p className="text-sm mb-2" style={{ color: 'var(--pa-muted)' }}>
            {userSign && <>Bonjour <span style={{ color: '#D4AF37' }}>{userSign}</span> · </>}Votre solde actuel :
            <span style={{ color: '#D4AF37', fontWeight: 600 }} data-testid="current-balance">
              {' '}{creditBalance} credits
            </span>
          </p>
        </div>

        <p className="text-center text-sm mb-10" style={{ color: 'var(--pa-body)', opacity: 0.8 }}>
          Chaque experience est personnalisee a partir de vos donnees astrologiques.
        </p>

        {/* ===== SECTION PACKS ===== */}
        <div className="text-center mb-6">
          <h2 className="text-2xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
            Rechargez votre puissance astrale
          </h2>
          <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
            10 crédits = 1 question à Plume. Chaque pack contient des crédits offerts.
          </p>
        </div>

        {/* Grille GaryVee — equivalences services */}
        <div className="mb-12">
          <ServicesEquivalence />
        </div>

        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          {PACKS.map((pack) => {
            const isPopular = pack.id === 'nebuleuse';
            const Icon = pack.icon;
            const total = pack.credits + (pack.bonus || 0);
            return (
              <div
                key={pack.id}
                className={`rounded-2xl p-6 relative transition-all duration-300 hover:scale-[1.02] ${isPopular ? 'md:-translate-y-2' : ''}`}
                style={{
                  background: isPopular ? 'rgba(212,175,55,0.07)' : 'rgba(255,255,255,0.03)',
                  border: isPopular ? '1px solid rgba(212,175,55,0.4)' : '1px solid rgba(212,175,55,0.15)',
                  backdropFilter: 'blur(12px)',
                }}
                data-testid={`pack-card-${pack.id}`}
              >
                {pack.badge && (
                  <div
                    className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-[10px] uppercase tracking-widest whitespace-nowrap"
                    style={{ background: '#D4AF37', color: '#111625', letterSpacing: '0.08em', fontWeight: 600 }}
                    data-testid="popular-badge"
                  >
                    {pack.badge}
                  </div>
                )}
                <div className="flex flex-col items-center text-center pt-2">
                  <div className="mb-3" style={{ color: '#D4AF37' }}>
                    <Icon className="w-7 h-7" strokeWidth={1.5} />
                  </div>
                  <h3 className="text-lg mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                    {pack.name}
                  </h3>
                  <div className="text-3xl mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#D4AF37', fontWeight: 400 }}>
                    {pack.amount % 1 === 0 ? pack.amount : pack.amount.toFixed(2).replace('.', ',')} &euro;
                  </div>
                  <p className="text-sm mb-0" style={{ color: 'var(--pa-body)' }}>
                    {pack.credits} crédits{pack.bonus > 0 && <span style={{ color: '#D4AF37', fontWeight: 500 }}> + {pack.bonus} offerts</span>}
                  </p>
                  <p className="text-xs mb-2" style={{ color: '#D4AF37', letterSpacing: '0.08em' }}>
                    = {total} crédits · {Math.floor(total / 10)} questions à Plume
                  </p>
                  {pack.tagline && (
                    <p className="text-[11px] italic mb-4 opacity-75" style={{ color: 'var(--pa-body)' }}>
                      {pack.tagline}
                    </p>
                  )}
                  <div className="w-full mb-4 py-3 px-3 rounded-lg text-left" style={{ background: 'rgba(212,175,55,0.05)', border: '1px solid rgba(212,175,55,0.08)' }}>
                    <p className="text-[10px] uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.08em' }}>
                      Exemple :
                    </p>
                    {pack.projections.map((p, i) => (
                      <p key={`${pack.id || pack.name}-proj-${i}`} className="text-xs py-0.5" style={{ color: 'var(--pa-body)' }}>
                        &bull; {p}
                      </p>
                    ))}
                  </div>
                  <button
                    onClick={() => handleBuy(pack.id)}
                    disabled={loadingPack === pack.id}
                    className={isPopular ? 'plume-btn-primary w-full justify-center' : 'plume-btn-secondary w-full justify-center'}
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

        <div className="rounded-2xl p-6 md:p-8" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(212,175,55,0.1)' }}>
          <h2 className="text-xl mb-5 text-center" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
            Que faire avec vos credits ?
          </h2>
          <div className="space-y-3">
            {SERVICE_COSTS.map(s => (
              <div key={s.name} className="flex items-center justify-between py-2" style={{ borderBottom: '1px solid rgba(212,175,55,0.08)' }}>
                <span className="text-sm" style={{ color: 'var(--pa-body)' }}>{s.name}</span>
                <span className="text-sm font-medium" style={{ color: '#D4AF37' }}>{s.cost}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-12 text-center">
          <h3 className="text-lg mb-5" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
            Continuer l&#39;exploration
          </h3>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/tarot-oui-non" className="plume-btn-secondary" data-testid="cta-tarot">
              Tirage tarot <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <Link to="/formulaire" className="plume-btn-secondary" data-testid="cta-theme">
              Theme astral <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <Link to="/numerologie" className="plume-btn-secondary" data-testid="cta-numerologie">
              Numerologie <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

      </div>
    </div>
  );
}
