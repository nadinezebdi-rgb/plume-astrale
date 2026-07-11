import React, { useState } from 'react';
import axios from 'axios';
import { X, Loader2, Sparkles, Zap, Flame, Check, AlertCircle } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * PACKS restructurés avec ancrage psychologique
 * Strategy: Pack 2 (Clarté) doit être IRRÉSISTIBLE
 *  - Meilleur ratio prix/valeur APPARENT
 *  - Bonus DRAMATIQUE (10 offerts)
 *  - Stats sociales (78% choisissent ce pack)
 */
const PACKS = [
  {
    id: 'initiation',
    name: 'Initiation',
    emoji: '🌙',
    price: '4,99 €',
    credits: 15,
    bonus: 0,
    totalCredits: 15,
    subtitle: 'Pour essayer maintenant',
    features: [
      'Chat Solena x 1',
      'Oracle personnalisé',
      'Accès 7 jours',
    ],
    pricePerCredit: '0,33€',
    badge: null,
    accent: '#A89B7E',
    highlight: false,
  },
  {
    id: 'clarte',
    name: 'Clarté',
    emoji: '✨',
    price: '14,99 €',
    credits: 50,
    bonus: 10,
    totalCredits: 60,
    originalPrice: '19,99 €',
    savings: 'Économise 5€',
    subtitle: 'Thème natal complet accessible',
    features: [
      '50 crédits + 10 BONUS 🎁',
      'Thème natal PDF 40 pages',
      'Chat Solena illimité 30j',
      'Synastrie de base',
    ],
    pricePerCredit: '0,25€',
    badge: {
      text: '⭐ BESTSELLER',
      stat: '78% choisissent ce pack',
    },
    accent: '#D4AF37',
    highlight: true,
  },
  {
    id: 'flammes_jumelles',
    name: 'Flammes Jumelles',
    emoji: '🔥',
    price: '29,99 €',
    credits: 100,
    bonus: 30,
    totalCredits: 130,
    subtitle: 'Accès illimité 30 jours',
    features: [
      '100 crédits + 30 BONUS 🎁',
      'Synastrie complète',
      'Session coaching (valeur 50€)',
      'Accès prioritaire features',
    ],
    pricePerCredit: '0,23€',
    badge: {
      text: '🔥 MEILLEURE VALEUR',
      stat: '10 places/jour',
    },
    accent: '#E8944A',
    highlight: false,
  },
];

/**
 * CreditsPaywallModal — OPTIMISÉE POUR LA CONVERSION
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

  // Contexte narratif d'urgence
  const HEADLINES = {
    chat_out: {
      title: '✨ Ta puissance astrale t\'appelle',
      emoji: '🌙',
      body: 'Solena a encore tellement à révéler sur ton destin amoureux. Quelques euros pour débloquer une guidance sans limite.',
    },
    chat_low: {
      title: '⚡ Ta lumière faiblit',
      emoji: '💫',
      body: 'Une dernière étincelle avant le silence cosmique. Recharge maintenant pour ne rien manquer.',
    },
    generic: {
      title: '🔮 Redécouvre ta destinée',
      emoji: '✨',
      body: 'Accès illimité à tes lectures astrales personnalisées.',
    },
  };
  const h = HEADLINES[context] || HEADLINES.chat_out;

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center px-4 py-6 overflow-y-auto"
      style={{
        background: 'linear-gradient(135deg, rgba(6,3,20,0.92), rgba(20,10,40,0.88))',
        backdropFilter: 'blur(8px)',
      }}
      onClick={onClose}
      data-testid="credits-paywall-overlay"
    >
      <div
        className="relative w-full max-w-5xl rounded-3xl overflow-hidden"
        style={{
          background: 'linear-gradient(165deg, rgba(212,175,55,0.08) 0%, rgba(6,3,20,0.95) 100%)',
          border: '1px solid rgba(212,175,55,0.25)',
          boxShadow: '0 50px 150px rgba(212,175,55,0.15), 0 0 80px rgba(212,175,55,0.08)',
        }}
        onClick={(e) => e.stopPropagation()}
        data-testid="credits-paywall-modal"
        role="dialog"
        aria-modal="true"
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-50 p-2 rounded-full transition-all hover:scale-110"
          style={{ color: '#D4AF37', background: 'rgba(212,175,55,0.1)' }}
          aria-label="Fermer"
          data-testid="credits-paywall-close"
        >
          <X size={20} strokeWidth={1.5} />
        </button>

        {/* HEADER */}
        <div className="px-6 md:px-12 pt-12 pb-8 text-center">
          <div className="text-5xl mb-4">{h.emoji}</div>
          <h2
            className="text-3xl md:text-4xl mb-4"
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontWeight: 300,
              color: '#F4E8D2',
            }}>
            {h.title}
          </h2>
          <p
            className="max-w-lg mx-auto text-sm md:text-base"
            style={{ color: 'rgba(244,232,210,0.8)', lineHeight: 1.6 }}>
            {h.body}
          </p>
        </div>

        {/* PACKS GRID — Ancrage psychologique appliqué */}
        <div className="px-6 md:px-8 pb-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {PACKS.map((p) => (
              <PackCard
                key={p.id}
                pack={p}
                isLoading={loadingPack === p.id}
                onBuy={() => buy(p.id)}
              />
            ))}
          </div>
        </div>

        {/* FOOTER TRUST */}
        <div
          className="px-6 py-4 text-center border-t"
          style={{ borderColor: 'rgba(212,175,55,0.1)' }}>
          <div className="flex flex-wrap justify-center gap-4 text-[10px] uppercase mb-4"
            style={{ color: 'rgba(212,175,55,0.6)', letterSpacing: '0.15em' }}>
            <span className="flex items-center gap-1">
              <Check size={12} /> Paiement sécurisé Stripe
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <Check size={12} /> Aucun engagement
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <Check size={12} /> Support 24/7
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-xs uppercase opacity-60 hover:opacity-100 transition"
            style={{
              color: '#D4AF37',
              letterSpacing: '0.15em',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
            }}
            data-testid="paywall-later"
          >
            Peut-être plus tard
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * PackCard — Composant pour chaque pack avec ancrage psychologique
 */
function PackCard({ pack, isLoading, onBuy }) {
  return (
    <div
      className="relative rounded-2xl p-7 flex flex-col transition-all transform hover:scale-105"
      style={{
        background: pack.highlight
          ? 'linear-gradient(135deg, rgba(232,199,102,0.12), rgba(212,175,55,0.06))'
          : 'rgba(212,175,55,0.04)',
        border: pack.highlight
          ? '2px solid rgba(232,199,102,0.4)'
          : '1px solid rgba(212,175,55,0.18)',
        boxShadow: pack.highlight
          ? '0 0 30px rgba(232,199,102,0.1), inset 0 0 30px rgba(232,199,102,0.04)'
          : 'none',
      }}
      data-testid={`paywall-pack-${pack.id}`}
    >
      {/* BADGE avec scarcité psychologique */}
      {pack.badge && (
        <div
          className="absolute -top-4 left-4 px-3 py-1.5 rounded-lg text-[10px] uppercase font-bold"
          style={{
            background: pack.accent,
            color: '#0C0918',
            letterSpacing: '0.15em',
            boxShadow: `0 4px 12px ${pack.accent}40`,
          }}>
          {pack.badge.text}
          <div style={{ fontSize: '8px', fontWeight: 400, marginTop: '2px' }}>
            {pack.badge.stat}
          </div>
        </div>
      )}

      {/* EMOJI + TITRE */}
      <div className="text-4xl mb-3">{pack.emoji}</div>
      <h3
        className="text-xl font-semibold mb-1"
        style={{ color: pack.accent }}>
        {pack.name}
      </h3>

      {/* SOUS-TITRE */}
      <p
        className="text-[10px] uppercase mb-4"
        style={{
          color: 'rgba(244,232,210,0.6)',
          letterSpacing: '0.15em',
        }}>
        {pack.subtitle}
      </p>

      {/* PRICING — Ancrage psychologique */}
      <div className="mb-5">
        <div className="flex items-baseline gap-2 mb-1">
          <span
            className="text-3xl font-bold"
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              color: pack.accent,
            }}>
            {pack.price}
          </span>
          {pack.originalPrice && (
            <span
              className="text-xs line-through"
              style={{ color: 'rgba(244,232,210,0.3)' }}>
              {pack.originalPrice}
            </span>
          )}
        </div>
        {pack.savings && (
          <div
            className="text-[10px] font-semibold"
            style={{ color: '#4ADE80' }}>
            💚 {pack.savings}
          </div>
        )}
        <div
          className="text-xs mt-2"
          style={{ color: 'rgba(244,232,210,0.5)' }}>
          <strong style={{ color: pack.accent }}>
            {pack.totalCredits} crédits
          </strong>
          {' '}→ {pack.pricePerCredit}/crédit
        </div>
      </div>

      {/* FEATURES */}
      <ul className="space-y-2 mb-6 flex-1">
        {pack.features.map((feature, i) => (
          <li key={i} className="flex items-start gap-2 text-xs">
            <Check
              size={14}
              style={{ color: pack.accent, flexShrink: 0, marginTop: '2px' }}
              strokeWidth={2}
            />
            <span style={{ color: 'rgba(244,232,210,0.8)' }}>{feature}</span>
          </li>
        ))}
      </ul>

      {/* CTA — Spécial pour le pack highlight */}
      <button
        onClick={onBuy}
        disabled={isLoading}
        className="w-full py-3 rounded-lg text-sm font-bold uppercase transition-all disabled:opacity-50"
        style={{
          background: pack.highlight
            ? `linear-gradient(135deg, ${pack.accent}, ${pack.accent}dd)`
            : 'rgba(212,175,55,0.1)',
          color: pack.highlight ? '#0C0918' : pack.accent,
          border: pack.highlight ? 'none' : `1px solid ${pack.accent}`,
          letterSpacing: '0.15em',
          cursor: isLoading ? 'not-allowed' : 'pointer',
        }}
        data-testid={`paywall-buy-${pack.id}`}
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 mx-auto animate-spin" />
        ) : (
          <>
            {pack.highlight ? '⚡ ' : ''}
            {pack.id === 'initiation' ? 'Essayer' : 'Accéder'}
          </>
        )}
      </button>
    </div>
  );
}
