import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Gift, Eye, Sparkles, Hash, Moon, Heart, TrendingUp, Star, ArrowRight, Check, Lock } from 'lucide-react';
import { useAuth, hasTrialed, markTrial, addHistory } from '@/context/AuthContext';
import SEO from '@/components/SEO';

const SERVICES = [
  {
    id: 'tarot-oui-non',
    route: '/tarot-oui-non',
    icon: Eye,
    title: 'Tarot Oui / Non',
    desc: 'Posez une question et recevez une réponse claire des Arcanes Majeurs.',
    normalCost: '1 crédit',
    glow: 'pink',
  },
  {
    id: 'tirage-tarot',
    route: '/tirage-tarot',
    icon: Sparkles,
    title: 'Lecture Tarot',
    desc: 'Tirage Marseille ou Croix Celtique avec interprétation complète.',
    normalCost: '10 crédits',
    glow: 'purple',
  },
  {
    id: 'numerologie',
    route: '/numerologie',
    icon: Hash,
    title: 'Numérologie',
    desc: 'Chemin de vie, nombre d\'âme et année personnelle.',
    normalCost: '10 crédits',
    glow: 'gold',
  },
  {
    id: 'tarologie',
    route: '/tarologie',
    icon: Moon,
    title: 'Tarologie',
    desc: 'Tirage en croix de 5 Arcanes avec lecture profonde et PDF.',
    normalCost: '10 crédits',
    glow: 'purple',
  },
  {
    id: 'compatibilite',
    route: '/compatibilite-amoureuse',
    icon: Heart,
    title: 'Compatibilité Amoureuse',
    desc: 'Rapport astral complet entre deux personnes.',
    normalCost: '10 crédits',
    glow: 'pink',
  },
  {
    id: 'theme-astral',
    route: '/formulaire',
    icon: Star,
    title: 'Thème Astral',
    desc: 'Calcul complet de votre carte du ciel avec interprétation.',
    normalCost: '10 crédits',
    glow: 'gold',
  },
  {
    id: 'horoscope',
    route: '/quotidien',
    icon: TrendingUp,
    title: 'Horoscope Quotidien',
    desc: 'Votre guidance cosmique du jour avec scores détaillés.',
    normalCost: 'Gratuit',
    glow: 'purple',
    alwaysFree: true,
  },
];

const glowColors = {
  gold: { accent: '#F4C542', bg: 'rgba(244,197,66,0.06)', border: 'rgba(244,197,66,0.2)' },
  pink: { accent: '#E879F9', bg: 'rgba(232,121,249,0.06)', border: 'rgba(232,121,249,0.2)' },
  purple: { accent: '#A78BFA', bg: 'rgba(167,139,250,0.06)', border: 'rgba(167,139,250,0.2)' },
};

export default function EssaiGratuit() {
  const navigate = useNavigate();
  const { isAuthenticated, loginAsGuest, applyFreeTrial } = useAuth();
  const [guestLoading, setGuestLoading] = useState(false);

  const handleTryService = (service) => {
    if (!isAuthenticated) {
      // Auto-connect as guest
      loginAsGuest();
    }

    if (service.alwaysFree) {
      navigate(service.route);
      return;
    }

    if (!hasTrialed(service.id)) {
      applyFreeTrial(service.id);
    }
    // Navigate with trial bypass param
    navigate(`${service.route}?essai=1`);
  };

  const handleGuestAccess = () => {
    setGuestLoading(true);
    loginAsGuest();
    setTimeout(() => {
      setGuestLoading(false);
      navigate('/');
    }, 500);
  };

  return (
    <div className="min-h-screen relative pt-20 pb-12 px-4 md:px-8" data-testid="essai-gratuit-page">
      <SEO path="/essai-gratuit" />
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Gift className="w-7 h-7" style={{ color: '#34D399' }} strokeWidth={1.5} />
          </div>
          <h1 className="text-3xl md:text-4xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
            Essayez gratuitement
          </h1>
          <p className="text-sm max-w-md mx-auto" style={{ color: 'var(--pa-muted)', lineHeight: '1.8' }}>
            Découvrez toutes les applications de Plume Astrale.
            Chaque service peut être essayé une fois gratuitement, sans engagement.
          </p>
        </div>

        {/* Guest access banner */}
        {!isAuthenticated && (
          <div className="rounded-2xl p-6 mb-8 text-center" style={{ background: 'rgba(52,211,153,0.06)', border: '1px solid rgba(52,211,153,0.2)' }}>
            <p className="text-sm mb-4" style={{ color: 'var(--pa-heading)' }}>
              Accédez instantanément en mode invité — pas de mot de passe requis
            </p>
            <button
              onClick={handleGuestAccess}
              disabled={guestLoading}
              className="inline-flex items-center gap-2 text-xs uppercase tracking-widest px-6 py-2.5 rounded-full transition-all duration-300"
              style={{ border: '1px solid rgba(52,211,153,0.5)', color: '#34D399', letterSpacing: '0.1em', background: 'rgba(52,211,153,0.08)' }}
            >
              <Gift className="w-3.5 h-3.5" />
              {guestLoading ? 'Connexion...' : 'Accès gratuit instantané'}
            </button>
            <p className="text-xs mt-3" style={{ color: 'var(--pa-muted)' }}>
              50 crédits offerts pour explorer toutes les fonctionnalités
            </p>
          </div>
        )}

        {/* Service grid */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {SERVICES.map((service) => {
            const trialed = hasTrialed(service.id);
            const colors = glowColors[service.glow] || glowColors.purple;
            const Icon = service.icon;

            return (
              <div
                key={service.id}
                className="rounded-2xl p-5 transition-all duration-300 hover:-translate-y-1"
                style={{ background: colors.bg, border: `1px solid ${colors.border}`, backdropFilter: 'blur(12px)' }}
              >
                <div className="flex items-start justify-between mb-3">
                  <Icon className="w-5 h-5" style={{ color: colors.accent }} strokeWidth={1.5} />
                  {service.alwaysFree ? (
                    <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(52,211,153,0.15)', color: '#34D399' }}>
                      Toujours gratuit
                    </span>
                  ) : trialed ? (
                    <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(197,160,89,0.15)', color: '#C5A059' }}>
                      <Check className="w-3 h-3" /> Essayé
                    </span>
                  ) : (
                    <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(52,211,153,0.15)', color: '#34D399' }}>
                      1 essai gratuit
                    </span>
                  )}
                </div>

                <h3 className="text-base mb-1.5" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                  {service.title}
                </h3>
                <p className="text-xs mb-4" style={{ color: 'var(--pa-muted)', lineHeight: '1.6' }}>
                  {service.desc}
                </p>

                <div className="flex items-center justify-between">
                  <span className="text-xs" style={{ color: 'var(--pa-muted)' }}>
                    Prix : <span style={{ color: colors.accent }}>{service.normalCost}</span>
                  </span>
                  <button
                    onClick={() => handleTryService(service)}
                    className="flex items-center gap-1.5 text-xs uppercase tracking-widest px-4 py-1.5 rounded-full transition-all duration-300"
                    style={{
                      border: `1px solid ${service.alwaysFree || !trialed ? 'rgba(52,211,153,0.4)' : colors.border}`,
                      color: service.alwaysFree || !trialed ? '#34D399' : colors.accent,
                      letterSpacing: '0.08em',
                    }}
                  >
                    {service.alwaysFree ? 'Accéder' : trialed ? 'Relancer' : 'Essayer'}
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-12">
          <div className="rounded-2xl p-8" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(197,160,89,0.15)' }}>
            <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
              Envie d'aller plus loin ?
            </h2>
            <p className="text-sm mb-5" style={{ color: 'var(--pa-muted)' }}>
              Créez un compte pour accéder à toutes les fonctionnalités et recevoir 50 crédits offerts.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              {!isAuthenticated && (
                <button
                  onClick={() => navigate('/inscription')}
                  className="inline-flex items-center justify-center gap-2 text-xs uppercase tracking-widest px-6 py-2.5 rounded-full transition-all"
                  style={{ border: '1px solid rgba(197,160,89,0.5)', color: '#C5A059', background: 'rgba(197,160,89,0.08)', letterSpacing: '0.1em' }}
                >
                  Créer un compte
                </button>
              )}
              <button
                onClick={() => navigate('/acheter-credits')}
                className="inline-flex items-center justify-center gap-2 text-xs uppercase tracking-widest px-6 py-2.5 rounded-full transition-all"
                style={{ border: '1px solid rgba(197,160,89,0.3)', color: '#C5A059', letterSpacing: '0.1em' }}
              >
                Voir les offres de crédits
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
