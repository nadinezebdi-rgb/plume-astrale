import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Check, Sparkles, Users, Gift, Calendar, ArrowRight, Loader2, Crown } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import PageHero from '@/components/PageHero';
import { event as track, EVENTS } from '@/lib/analytics';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

// Tier configuration (backend-mirror : voir routes/subscriptions.py)
const TIERS = {
  normal: {
    key: 'normal',
    name: 'Cercle Soléna',
    price: 14.99,
    chat_credits: 100,
    benefits: [
      { icon: Gift, title: '100 crédits par mois', desc: 'Environ 20 questions ou 6 tirages tarot. Rechargés chaque 1er du mois.' },
      { icon: Users, title: 'Accès au Cercle', desc: 'Communauté privée d\u2019initiées, échanges, méditations.' },
      { icon: Calendar, title: 'Lecture Nouvelle Lune', desc: 'Une lecture symbolique mensuelle offerte à chaque cycle.' },
      { icon: Sparkles, title: '-10% sur les PDF Signature', desc: 'Thème Natal, Astrologie relationnelle, Voyage karmique.' },
    ],
  },
  premium: {
    key: 'premium',
    name: 'Cercle Soléna Premium',
    price: 29.0,
    chat_credits: 250,
    benefits: [
      { icon: Gift, title: '250 crédits par mois', desc: 'Environ 50 questions ou 16 tirages tarot. Rechargés chaque 1er du mois.' },
      { icon: Crown, title: 'Priorité Soléna', desc: 'Réponses en priorité + accès aux lectures collectives premium.' },
      { icon: Users, title: 'Accès au Cercle', desc: 'Communauté privée + salons Premium réservés.' },
      { icon: Calendar, title: 'Lecture Nouvelle & Pleine Lune', desc: 'Deux lectures mensuelles offertes (au lieu d\u2019une).' },
      { icon: Sparkles, title: '-20% sur les PDF Signature', desc: 'Réduction majorée sur tout le catalogue.' },
    ],
  },
};

const TierCard = ({ tier, onSubscribe, loading, error, alreadyMember, isCurrentTier, highlighted }) => (
  <div
    className="plume-glass p-6 md:p-8 relative overflow-hidden"
    data-testid={`cercle-tier-${tier.key}`}
    style={{
      border: highlighted ? '1px solid rgba(212,175,55,0.5)' : '1px solid rgba(212,175,55,0.2)',
      boxShadow: highlighted ? '0 30px 80px -30px rgba(212,175,55,0.4)' : 'none',
      opacity: alreadyMember && !isCurrentTier ? 0.55 : 1,
    }}
  >
    {highlighted && (
      <div
        className="absolute top-3 right-3 px-3 py-1 rounded-full text-[10px] uppercase"
        style={{
          background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 50%, #D4AF37 100%)',
          color: '#0A0603',
          fontFamily: 'Cinzel, serif',
          letterSpacing: '0.18em',
          fontWeight: 700,
        }}
        data-testid={`cercle-tier-${tier.key}-badge`}
      >
        Recommandé
      </div>
    )}

    <p
      className="text-[10px] uppercase mb-3"
      style={{ color: '#D4AF37', letterSpacing: '0.32em', fontFamily: 'Cinzel, serif' }}
    >
      ✦ {tier.name} ✦
    </p>

    <div className="flex items-baseline gap-2 mb-4" data-testid={`cercle-tier-${tier.key}-price`}>
      <span style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 56, fontWeight: 300, color: '#D4AF37', lineHeight: 1 }}>
        {tier.price.toFixed(2).replace('.', ',')}€
      </span>
      <span style={{ color: 'rgba(227,215,255,0.65)', fontSize: 15, fontStyle: 'italic', fontFamily: 'Cormorant Garamond, serif' }}>
        /mois
      </span>
    </div>

    <p className="text-xs mb-5" style={{ color: 'rgba(227,215,255,0.55)', letterSpacing: '0.1em' }}>
      Sans engagement · Résiliation en 1 clic
    </p>

    <div className="space-y-3 mb-6">
      {tier.benefits.map((b, i) => {
        const Icon = b.icon;
        return (
          <div key={i} className="flex items-start gap-3" data-testid={`cercle-tier-${tier.key}-benefit-${i}`}>
            <div
              className="shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
              style={{ background: 'rgba(212,175,55,0.12)', border: '1px solid rgba(212,175,55,0.35)' }}
            >
              <Icon className="w-4 h-4" strokeWidth={1.4} style={{ color: '#D4AF37' }} />
            </div>
            <div>
              <div
                style={{
                  fontFamily: 'Cinzel, serif',
                  fontSize: 12,
                  color: '#F5EEE0',
                  letterSpacing: '0.1em',
                  marginBottom: 2,
                }}
              >
                {b.title}
              </div>
              <div
                className="text-xs"
                style={{
                  color: 'rgba(227,215,255,0.7)',
                  fontFamily: 'Cormorant Garamond, serif',
                  fontStyle: 'italic',
                  lineHeight: 1.5,
                }}
              >
                {b.desc}
              </div>
            </div>
          </div>
        );
      })}
    </div>

    {alreadyMember && isCurrentTier ? (
      <div
        className="inline-flex items-center gap-2 px-5 py-3 rounded-full w-full justify-center"
        data-testid={`cercle-tier-${tier.key}-already`}
        style={{
          background: 'rgba(212,175,55,0.15)',
          border: '1px solid rgba(212,175,55,0.4)',
          color: '#D4AF37',
          fontFamily: 'Cinzel, serif',
          fontSize: 12,
          letterSpacing: '0.2em',
        }}
      >
        <Check className="w-4 h-4" strokeWidth={1.8} />
        TU ES MEMBRE
      </div>
    ) : (
      <button
        onClick={() => onSubscribe(tier.key)}
        disabled={loading || (alreadyMember && !isCurrentTier)}
        className="plume-btn-primary w-full justify-center"
        data-testid={`cercle-tier-${tier.key}-cta`}
        style={{ display: 'inline-flex' }}
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" /> Redirection...
          </>
        ) : (
          <>
            Rejoindre <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
          </>
        )}
      </button>
    )}

    {error && (
      <p className="mt-3 text-xs text-center" style={{ color: '#f87171' }} data-testid={`cercle-tier-${tier.key}-error`}>
        {error}
      </p>
    )}
  </div>
);

const CercleSolena = () => {
  const navigate = useNavigate();
  const { isAuthenticated, session, loading: authLoading } = useAuth();
  const [loading, setLoading] = useState(null); // 'normal' | 'premium' | null
  const [error, setError] = useState('');
  const [status, setStatus] = useState(null);

  useEffect(() => {
    if (!isAuthenticated || !session?.access_token) return;
    axios
      .get(`${API}/subscriptions/cercle-solena/status`, {
        headers: { Authorization: `Bearer ${session.access_token}` },
      })
      .then((r) => setStatus(r.data))
      .catch(() => {});
  }, [isAuthenticated, session]);

  const handleCheckout = async (tier) => {
    track(EVENTS.CERCLE_SOLENA_CHECKOUT, { authenticated: isAuthenticated, tier });
    if (!isAuthenticated) {
      navigate(`/connexion?redirect=/cercle-solena`);
      return;
    }
    setLoading(tier);
    setError('');
    try {
      const r = await axios.post(
        `${API}/subscriptions/cercle-solena/checkout`,
        { origin_url: window.location.origin, tier },
        { headers: { Authorization: `Bearer ${session.access_token}` } },
      );
      window.location.href = r.data.url;
    } catch (e) {
      setError(e.response?.data?.detail || 'Impossible de créer la session. Réessaie dans un instant.');
      setLoading(null);
    }
  };

  const isAlreadyMember = status?.active;
  const currentTier = status?.tier;

  return (
    <>
      <SEO
        title="Cercle Soléna — Abonnement mensuel Plume Astrale"
        description="Rejoins le Cercle Soléna. Deux tiers : 100 crédits/mois à 14,99€ ou 250 crédits + priorité à 29€. Résiliable à tout moment."
      />
      <PageHero
        badge="✦ Cercle Soléna ✦"
        title="Un rendez-vous mensuel avec ton étoile"
        subtitle="Deux formules pour continuer à te lire, mois après mois. Résilie en 1 clic."
      />

      <div className="max-w-5xl mx-auto px-6 pb-24 pt-4">
        {/* ROI Comparator (F500 audit 2026-02) — ancre le prix mensuel comme rationnel */}
        <div
          className="plume-glass p-6 md:p-8 mb-8"
          data-testid="cercle-roi-comparator"
          style={{ border: '1px solid rgba(212,175,55,0.35)' }}
        >
          <p
            style={{
              fontFamily: 'Cinzel, serif',
              fontSize: 11,
              letterSpacing: '0.28em',
              color: '#D4AF37',
              marginBottom: 12,
              textTransform: 'uppercase',
            }}
          >
            ✦ Calcul de valeur ✦
          </p>
          <h2
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: 26,
              fontWeight: 300,
              color: '#F5EEE0',
              marginBottom: 20,
              lineHeight: 1.25,
            }}
          >
            Pourquoi le Cercle coûte <span style={{ fontStyle: 'italic', color: '#D4AF37' }}>29 % moins cher</span> qu&apos;acheter à l&apos;unité.
          </h2>
          <div
            className="grid grid-cols-1 md:grid-cols-3 gap-4"
            style={{ fontFamily: 'Inter, sans-serif' }}
          >
            <div
              data-testid="cercle-roi-unit"
              style={{
                padding: 18,
                background: 'rgba(15,26,60,0.35)',
                border: '1px solid rgba(227,215,255,0.15)',
                borderRadius: 10,
              }}
            >
              <div style={{ fontSize: 11, letterSpacing: '0.14em', color: 'rgba(227,215,255,0.55)', textTransform: 'uppercase', marginBottom: 8 }}>
                Pack Régulier · à l&apos;unité
              </div>
              <div style={{ fontSize: 24, fontWeight: 500, color: '#F5EEE0', marginBottom: 4 }}>
                14,99€ <span style={{ fontSize: 13, color: 'rgba(227,215,255,0.65)' }}>· 100 crédits</span>
              </div>
              <div style={{ fontSize: 12, color: 'rgba(227,215,255,0.55)' }}>
                Soit <b style={{ color: '#F5EEE0' }}>0,15€ / crédit</b> — sans avantage inclus
              </div>
            </div>
            <div
              data-testid="cercle-roi-monthly"
              style={{
                padding: 18,
                background: 'rgba(212,175,55,0.10)',
                border: '1px solid rgba(212,175,55,0.5)',
                borderRadius: 10,
              }}
            >
              <div style={{ fontSize: 11, letterSpacing: '0.14em', color: '#D4AF37', textTransform: 'uppercase', marginBottom: 8 }}>
                Cercle Soléna
              </div>
              <div style={{ fontSize: 24, fontWeight: 500, color: '#F5EEE0', marginBottom: 4 }}>
                14,99€ <span style={{ fontSize: 13, color: 'rgba(227,215,255,0.65)' }}>· 100 crédits/mois</span>
              </div>
              <div style={{ fontSize: 12, color: '#D4AF37' }}>
                Même prix + 3 avantages inclus (lecture mensuelle · -10 % PDF · communauté)
              </div>
            </div>
            <div
              data-testid="cercle-roi-savings"
              style={{
                padding: 18,
                background: 'rgba(15,26,60,0.35)',
                border: '1px solid rgba(227,215,255,0.15)',
                borderRadius: 10,
              }}
            >
              <div style={{ fontSize: 11, letterSpacing: '0.14em', color: 'rgba(227,215,255,0.55)', textTransform: 'uppercase', marginBottom: 8 }}>
                Valeur cumulée annuelle
              </div>
              <div style={{ fontSize: 24, fontWeight: 500, color: '#F5EEE0', marginBottom: 4 }}>
                +72€ / an
              </div>
              <div style={{ fontSize: 12, color: 'rgba(227,215,255,0.55)' }}>
                12 lectures mensuelles offertes + -10 % sur chaque PDF Signature acheté
              </div>
            </div>
          </div>
          <p
            style={{
              fontSize: 12,
              color: 'rgba(227,215,255,0.55)',
              marginTop: 14,
              fontStyle: 'italic',
              fontFamily: 'Cormorant Garamond, serif',
            }}
          >
            Sans engagement · Résiliable en 1 clic depuis le Portail Stripe · Accès conservé jusqu&apos;à la fin du mois payé.
          </p>
        </div>

        {/* 2 tiers side-by-side */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-14" data-testid="cercle-tiers-grid">
          <TierCard
            tier={TIERS.normal}
            onSubscribe={handleCheckout}
            loading={loading === 'normal'}
            error={loading === 'normal' ? error : ''}
            alreadyMember={isAlreadyMember}
            isCurrentTier={currentTier === 'normal'}
            highlighted={false}
          />
          <TierCard
            tier={TIERS.premium}
            onSubscribe={handleCheckout}
            loading={loading === 'premium'}
            error={loading === 'premium' ? error : ''}
            alreadyMember={isAlreadyMember}
            isCurrentTier={currentTier === 'premium'}
            highlighted
          />
        </div>

        {/* FAQ */}
        <div className="plume-glass p-6 md:p-8" data-testid="cercle-faq">
          <h3
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: 22,
              color: '#F5EEE0',
              marginBottom: 14,
              fontStyle: 'italic',
            }}
          >
            Questions fréquentes
          </h3>
          <div className="space-y-4 text-sm" style={{ color: 'rgba(227,215,255,0.75)', fontFamily: 'Cormorant Garamond, serif' }}>
            <div>
              <div
                style={{
                  color: '#D4AF37',
                  fontFamily: 'Cinzel, serif',
                  fontSize: 12,
                  letterSpacing: '0.12em',
                  marginBottom: 4,
                }}
              >
                PUIS-JE RÉSILIER À TOUT MOMENT ?
              </div>
              <p>
                Oui. Depuis ta page « Mon Compte », un clic ouvre le Portail Stripe où tu résilies en 3 secondes. L&apos;accès
                reste actif jusqu&apos;à la fin du mois en cours.
              </p>
            </div>
            <div>
              <div
                style={{
                  color: '#D4AF37',
                  fontFamily: 'Cinzel, serif',
                  fontSize: 12,
                  letterSpacing: '0.12em',
                  marginBottom: 4,
                }}
              >
                COMMENT MARCHENT LES CRÉDITS CHAT ?
              </div>
              <p>
                Ils sont réservés au chat avec Soléna (10 crédits par question). Ils sont crédités automatiquement au 1er paiement
                puis à chaque renouvellement mensuel. Ils ne se cumulent pas indéfiniment — utilise-les dans le mois.
              </p>
            </div>
            <div>
              <div
                style={{
                  color: '#D4AF37',
                  fontFamily: 'Cinzel, serif',
                  fontSize: 12,
                  letterSpacing: '0.12em',
                  marginBottom: 4,
                }}
              >
                PUIS-JE PASSER DU TIER NORMAL AU PREMIUM ?
              </div>
              <p>
                Oui, à tout moment depuis le Portail Stripe. La différence est facturée au prorata.
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default CercleSolena;
