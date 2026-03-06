import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Coins, Sparkles, Star, Zap } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

const PACK_ICONS = {
  decouverte: <Star className="w-6 h-6" strokeWidth={1.5} />,
  exploration: <Sparkles className="w-6 h-6" strokeWidth={1.5} />,
  premium: <Zap className="w-6 h-6" strokeWidth={1.5} />,
};

const PACK_COLORS = {
  decouverte: { border: 'rgba(197,160,89,0.2)', bg: 'rgba(197,160,89,0.04)' },
  exploration: { border: 'rgba(197,160,89,0.35)', bg: 'rgba(197,160,89,0.07)' },
  premium: { border: 'rgba(255,215,0,0.4)', bg: 'rgba(255,215,0,0.06)' },
};

export default function BuyCredits() {
  const { isAuthenticated, token, creditBalance } = useAuth();
  const navigate = useNavigate();
  const [packs, setPacks] = useState([]);
  const [loadingPack, setLoadingPack] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) { navigate('/connexion'); return; }
    axios.get(`${API}/api/credits/packs`).then(r => setPacks(r.data.packs));
  }, [isAuthenticated, navigate]);

  const handleBuy = async (packId) => {
    setLoadingPack(packId);
    try {
      const res = await axios.post(`${API}/api/credits/checkout`, {
        pack_id: packId,
        origin_url: window.location.origin,
      }, { headers: { Authorization: `Bearer ${token}` } });
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
        {/* Header */}
        <div className="text-center mb-10">
          <div className="flex items-center justify-center gap-3 mb-3">
            <Coins className="w-6 h-6" style={{ color: '#C5A059' }} strokeWidth={1.5} />
            <h1 className="text-3xl sm:text-4xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
              Acheter des crédits
            </h1>
          </div>
          <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
            Votre solde actuel : <span style={{ color: '#C5A059', fontWeight: 600 }} data-testid="current-balance">{creditBalance} crédits</span>
          </p>
        </div>

        {/* Packs */}
        <div className="grid gap-5 md:grid-cols-3">
          {packs.map((pack) => {
            const colors = PACK_COLORS[pack.id] || PACK_COLORS.decouverte;
            const isPopular = pack.id === 'exploration';
            return (
              <div
                key={pack.id}
                className="rounded-2xl p-6 relative transition-all duration-300 hover:scale-[1.02]"
                style={{ background: colors.bg, border: `1px solid ${colors.border}`, backdropFilter: 'blur(12px)' }}
                data-testid={`pack-card-${pack.id}`}
              >
                {isPopular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-[10px] uppercase tracking-widest"
                    style={{ background: '#C5A059', color: '#0C0918', letterSpacing: '0.08em', fontWeight: 600 }}>
                    Populaire
                  </div>
                )}
                <div className="flex flex-col items-center text-center pt-2">
                  <div className="mb-3" style={{ color: '#C5A059' }}>{PACK_ICONS[pack.id]}</div>
                  <h3 className="text-lg mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                    {pack.name}
                  </h3>
                  <div className="text-3xl mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#C5A059', fontWeight: 400 }}>
                    {pack.amount.toFixed(2).replace('.', ',')} &euro;
                  </div>
                  <p className="text-sm mb-1" style={{ color: 'var(--pa-body)' }}>
                    {pack.credits} crédits
                  </p>
                  <p className="text-xs mb-5" style={{ color: 'var(--pa-muted)' }}>
                    {(pack.amount / pack.credits).toFixed(2).replace('.', ',')} &euro; / crédit
                  </p>
                  <button
                    onClick={() => handleBuy(pack.id)}
                    disabled={loadingPack === pack.id}
                    className="w-full py-2.5 text-xs uppercase tracking-widest rounded-full transition-all duration-500"
                    style={{
                      border: `1px solid ${isPopular ? '#C5A059' : 'rgba(197,160,89,0.4)'}`,
                      color: loadingPack === pack.id ? 'var(--pa-muted)' : '#C5A059',
                      background: isPopular ? 'rgba(197,160,89,0.1)' : 'transparent',
                      letterSpacing: '0.1em',
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

        {/* Service costs */}
        <div className="mt-12 rounded-2xl p-6 md:p-8" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(197,160,89,0.1)' }}>
          <h2 className="text-xl mb-5 text-center" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
            Coût des services
          </h2>
          <div className="space-y-3">
            {[
              { name: 'Tarot Oui / Non', cost: '1er tirage gratuit, puis 2 crédits' },
              { name: 'Lecture Tarot approfondie', cost: '10 crédits' },
              { name: 'Lecture astrologique', cost: '10 crédits' },
              { name: 'Numérologie — Chemin d\'âme', cost: '10 crédits' },
              { name: 'Cartographie Premium', cost: '60 crédits' },
            ].map(s => (
              <div key={s.name} className="flex items-center justify-between py-2" style={{ borderBottom: '1px solid rgba(197,160,89,0.08)' }}>
                <span className="text-sm" style={{ color: 'var(--pa-body)' }}>{s.name}</span>
                <span className="text-sm" style={{ color: '#C5A059' }}>{s.cost}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
