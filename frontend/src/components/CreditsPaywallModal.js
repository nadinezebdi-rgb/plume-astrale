import React, { useState } from 'react';
import axios from 'axios';
import { X, Loader2, Sparkles, Zap, Flame } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL;

// Packs synchronises avec /app/backend/config.py PACKS
const PACKS = [
  {
    id: 'initiation',
    name: 'Initiation',
    price: '4,99 €',
    credits: 15,
    bonus: 0,
    icon: Sparkles,
    subtitle: '15 crédits · idéal pour continuer maintenant',
    accent: '#B8961F',
  },
  {
    id: 'astro_amour',
    name: 'Clarté',
    price: '14,99 €',
    credits: 50,
    bonus: 10,
    icon: Zap,
    subtitle: '50 crédits + 10 offerts = 60 crédits',
    caption: '≈ 1 Thème Natal complet (60 cr) accessible en 1 clic',
    badge: '⭐ Best-Seller',
    accent: '#E7C97A',
    highlight: true,
  },
  {
    id: 'flammes_jumelles',
    name: 'Flammes Jumelles',
    price: '29,99 €',
    credits: 100,
    bonus: 30,
    icon: Flame,
    subtitle: '100 crédits + 30 offerts = 130 crédits',
    caption: 'Explore ton thème en profondeur, ton karma, tes futures relations',
    badge: 'Meilleure valeur',
    accent: '#B8961F',
  },
];

/**
 * CreditsPaywallModal — pop-up narrative de conversion.
 * Props :
 *  - open : bool
 *  - onClose : () => void
 *  - context : 'chat_out' | 'chat_low' | 'generic' (defaut: 'chat_out')
 */
export default function CreditsPaywallModal({ open, onClose, context = 'chat_out' }) {
  const { token } = useAuth();
  const [loadingPack, setLoadingPack] = useState(null);

  if (!open) return null;

  const buy = async (packId) => {
    setLoadingPack(packId);
    try {
      const res = await axios.post(
        `${API}/api/credits/checkout`,
        { pack_id: packId, origin_url: window.location.origin },
        { headers: token ? { Authorization: `Bearer ${token}` } : {} },
      );
      if (res.data?.url) {
        window.location.href = res.data.url;
      } else {
        alert('Impossible de démarrer le paiement. Réessaie.');
        setLoadingPack(null);
      }
    } catch (e) {
      const msg = e.response?.data?.detail || e.message || 'Erreur';
      alert(msg);
      setLoadingPack(null);
    }
  };

  const HEADLINES = {
    chat_out: {
      title: "Vous n'avez plus de puissance astrale.",
      body: "Rechargez vos crédits pour continuer la révélation. Plume a encore beaucoup à te dire — le Pack Initiation à seulement 4,99 € suffit pour poursuivre la conversation.",
    },
    chat_low: {
      title: 'Ta lumière faiblit.',
      body: "Il te reste juste assez d'énergie pour une dernière question. Recharge maintenant pour ne rien manquer de ce que Plume a à te dire.",
    },
    generic: {
      title: 'Réactive ta puissance astrale.',
      body: 'Rechargez vos crédits pour continuer votre parcours avec Plume.',
    },
  };
  const h = HEADLINES[context] || HEADLINES.chat_out;

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center px-4 py-6"
      style={{ background: 'rgba(6,3,20,0.82)', backdropFilter: 'blur(6px)' }}
      onClick={onClose}
      data-testid="credits-paywall-overlay"
    >
      <div
        className="relative max-w-4xl w-full rounded-3xl overflow-hidden max-h-[92vh] overflow-y-auto"
        style={{
          background: 'linear-gradient(180deg,#12082A,#0C0918)',
          border: '1px solid rgba(184,150,31,0.35)',
          boxShadow: '0 40px 120px rgba(0,0,0,0.6), 0 0 60px rgba(184,150,31,0.10)',
        }}
        onClick={(e) => e.stopPropagation()}
        data-testid="credits-paywall-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="paywall-title"
      >
        {/* Close */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-full transition-all hover:scale-110"
          style={{ color: '#B8961F', background: 'rgba(184,150,31,0.08)' }}
          aria-label="Fermer"
          data-testid="credits-paywall-close"
        >
          <X className="w-5 h-5" strokeWidth={1.5} />
        </button>

        {/* Header */}
        <div className="px-6 md:px-12 pt-10 pb-6 text-center">
          <div className="inline-flex items-center gap-2 mb-4">
            <Sparkles className="w-4 h-4" style={{ color: '#B8961F' }} strokeWidth={1.5} />
            <span
              className="text-xs uppercase"
              style={{ color: '#B8961F', letterSpacing: '0.3em' }}
            >
              Offre de recharge
            </span>
            <Sparkles className="w-4 h-4" style={{ color: '#B8961F' }} strokeWidth={1.5} />
          </div>
          <h2
            id="paywall-title"
            className="text-3xl md:text-4xl mb-3"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: '#F4E8D2' }}
          >
            {h.title}
          </h2>
          <p className="text-sm md:text-base opacity-75 max-w-lg mx-auto" style={{ color: '#F4E8D2' }}>
            {h.body}
          </p>
        </div>

        {/* Packs */}
        <div className="px-6 md:px-8 pb-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          {PACKS.map((p) => {
            const Icon = p.icon;
            const totalCr = p.credits + p.bonus;
            return (
              <div
                key={p.id}
                className="relative rounded-2xl p-6 flex flex-col"
                style={{
                  background: p.highlight
                    ? 'linear-gradient(160deg,rgba(184,150,31,0.15),rgba(184,150,31,0.03))'
                    : 'rgba(255,255,255,0.03)',
                  border: p.highlight
                    ? '1.5px solid #B8961F'
                    : '1px solid rgba(184,150,31,0.22)',
                }}
                data-testid={`paywall-pack-${p.id}`}
              >
                {p.badge && (
                  <div
                    className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-[10px] uppercase whitespace-nowrap"
                    style={{
                      background: '#B8961F',
                      color: '#0C0918',
                      letterSpacing: '0.15em',
                      fontWeight: 600,
                    }}
                  >
                    {p.badge}
                  </div>
                )}
                <Icon
                  className="w-8 h-8 mb-3 mx-auto"
                  style={{ color: p.accent }}
                  strokeWidth={1.4}
                />
                <div
                  className="text-2xl text-center mb-1"
                  style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F4E8D2' }}
                >
                  {p.name}
                </div>
                <div className="text-center mb-3">
                  <span
                    className="text-3xl"
                    style={{ fontFamily: 'Cormorant Garamond, serif', color: p.accent }}
                  >
                    {p.price}
                  </span>
                </div>
                <div className="text-xs text-center mb-1" style={{ color: '#F4E8D2', opacity: 0.9 }}>
                  {p.subtitle}
                </div>
                {p.bonus > 0 && (
                  <div
                    className="text-[10px] uppercase text-center mb-2"
                    style={{ color: p.accent, letterSpacing: '0.2em' }}
                  >
                    + {p.bonus} offerts
                  </div>
                )}
                {p.caption && (
                  <div className="text-[11px] text-center italic mt-2 mb-3 opacity-70" style={{ color: '#F4E8D2' }}>
                    {p.caption}
                  </div>
                )}
                <div className="flex-1" />
                <button
                  onClick={() => buy(p.id)}
                  disabled={loadingPack !== null}
                  className="w-full py-3 rounded-full text-xs uppercase transition-all disabled:opacity-50 mt-3"
                  style={{
                    background: p.highlight ? '#B8961F' : 'transparent',
                    color: p.highlight ? '#0C0918' : '#B8961F',
                    border: p.highlight ? 'none' : '1px solid #B8961F',
                    letterSpacing: '0.2em',
                    fontWeight: 500,
                  }}
                  data-testid={`paywall-buy-${p.id}`}
                >
                  {loadingPack === p.id ? (
                    <Loader2 className="w-4 h-4 mx-auto animate-spin" />
                  ) : (
                    <>Recharger · {totalCr} cr</>
                  )}
                </button>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="px-6 pb-8 text-center">
          <button
            onClick={onClose}
            className="text-xs uppercase opacity-60 hover:opacity-100 transition-all"
            style={{ color: '#F4E8D2', letterSpacing: '0.15em' }}
            data-testid="paywall-later"
          >
            Peut-être plus tard
          </button>
          <div className="mt-4 text-[10px] opacity-40" style={{ color: '#F4E8D2' }}>
            Paiement sécurisé · Stripe · Aucun engagement
          </div>
        </div>
      </div>
    </div>
  );
}
