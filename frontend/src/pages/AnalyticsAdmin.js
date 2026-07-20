import React, { useMemo } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Link } from 'react-router-dom';
import { ArrowUpRight, TrendingUp, Users, ShoppingCart, Sparkles, DollarSign } from 'lucide-react';
import SEO from '@/components/SEO';
import PageHero from '@/components/PageHero';

/**
 * Tableau de bord Plausible/GA4 — synthèse humaine des conversions.
 * Affiche uniquement pour les admins. Aucune donnée serveur récupérée
 * côté client : le composant fournit les liens Plausible pré-configurés
 * (filtres + périodes) pour lire les vraies données sur plausible.io.
 *
 * Pourquoi pas de fetch temps réel ?
 *  1. Plausible Stats API nécessite un API key personnel (payant tier Business+)
 *  2. Iframe embed nécessite d'activer "Public link" par KPI (Nathalie contrôle)
 *  3. Le vrai dashboard vit sur plausible.io — cette page est un COCKPIT de
 *     lecture rapide qui te dit QUOI regarder et OÙ cliquer.
 */

// Domaine plausible configuré côté .env (fallback plume-astrale.fr)
const DOMAIN = process.env.REACT_APP_PLAUSIBLE_DOMAIN || 'plume-astrale.fr';
const PLAUSIBLE_BASE = `https://plausible.io/${DOMAIN}`;

const KPIS = [
  {
    icon: Users,
    label: 'VISITEURS UNIQUES',
    goal: 'Croissance mensuelle',
    target: '+ 20% mois/mois',
    query: '',
    color: '#A78BFA',
    reading: 'Ta courbe globale — regarde toujours en vue "Last 30 days" pour lisser les pics.',
  },
  {
    icon: TrendingUp,
    label: 'SIGNUPS COMPLETED',
    goal: 'Inscriptions abouties',
    target: '≥ 3% des visiteurs',
    query: '?filters=((event,goal,is,signup_completed))',
    color: '#E8C766',
    reading: 'Combien de visiteurs vont jusqu\'à créer un compte. Si tu vois < 2%, c\'est ton hero ou ton formulaire qui coince.',
  },
  {
    icon: ShoppingCart,
    label: 'CHECKOUTS INITIÉS',
    goal: 'Kabbale + Astrocarto + Karmique',
    target: '≥ 25% des signups',
    query: '?filters=((event,goal,is,(kabbale_checkout|astrocarto_checkout|pack_karmique_checkout)))',
    color: '#D4AF37',
    reading: 'Nombre de tentatives de paiement lancées. Écart avec le nombre de paiements réels = ton taux d\'abandon panier.',
  },
  {
    icon: DollarSign,
    label: 'REVENUE PDF',
    goal: 'Ventes PDF unitaires',
    target: 'Suivi mensuel',
    query: '?filters=((event,goal,is,(kabbale_checkout|astrocarto_checkout|pack_karmique_checkout)))&period=month',
    color: '#22c55e',
    reading: 'Plausible calcule automatiquement le revenue si tu as bien passé revenue.amount + currency dans les events (déjà branché côté code).',
  },
  {
    icon: Sparkles,
    label: 'CERCLE SOLÉNA',
    goal: 'Abonnements mensuels',
    target: '≥ 5% des acheteurs PDF',
    query: '?filters=((event,goal,is,cercle_solena_checkout))',
    color: '#F4D98C',
    reading: 'Objectif LTV : chaque abonnement Cercle vaut 12× plus qu\'une vente unique. Vise 5% de conversion post-achat PDF.',
  },
  {
    icon: TrendingUp,
    label: 'BUNDLE CLICK',
    goal: 'Intérêt Duo Soléna',
    target: '≥ 10% des visiteurs /mon-compte',
    query: '?filters=((event,goal,is,bundle_click))',
    color: '#E8C766',
    reading: 'Signal fort : mesure combien de connectés cliquent sur ton offre 68€. Si faible, le placement du BundleCard n\'est pas assez visible.',
  },
];

const FUNNEL_STEPS = [
  { label: 'Visiteurs uniques',          formula: '/dashboard',                     ratio: null },
  { label: 'Inscriptions',               formula: 'signup_completed',               ratio: 'des visiteurs' },
  { label: 'Checkouts initiés',          formula: '*_checkout',                     ratio: 'des inscrits' },
  { label: 'Paiements réussis',          formula: 'purchase (via Stripe webhook)',  ratio: 'des checkouts' },
  { label: 'Abonnements Cercle Soléna',  formula: 'cercle_solena_checkout',         ratio: 'des acheteurs' },
];

const AnalyticsAdmin = () => {
  const { user } = useAuth();
  const isAdmin = user?.is_admin || user?.role === 'admin' || user?.email === 'admin@plume-astrale.fr';

  const configured = useMemo(() => !!process.env.REACT_APP_PLAUSIBLE_DOMAIN, []);

  if (!isAdmin) {
    return (
      <div className="max-w-md mx-auto pt-40 pb-20 px-6 text-center">
        <p style={{ color: 'rgba(227,215,255,0.75)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
          Cette page est réservée à l&apos;équipe Plume Astrale.
        </p>
        <Link to="/" className="link-editorial text-xs mt-4 inline-block">← Retour à l&apos;accueil</Link>
      </div>
    );
  }

  return (
    <>
      <SEO title="Analytics — Plume Astrale" description="Tableau de bord analytics interne" noindex />
      <PageHero
        badge="✦ Cockpit Analytics ✦"
        title="Tes chiffres, sans te noyer"
        subtitle="6 KPIs qui décident. Un clic pour aller lire le détail sur Plausible."
      />

      <div className="max-w-5xl mx-auto px-6 pb-24 pt-4">

        {!configured && (
          <div className="plume-glass p-5 mb-8" data-testid="analytics-not-configured" style={{ border: '1px solid rgba(251,146,60,0.35)' }}>
            <div className="text-[11px] uppercase mb-2" style={{ color: '#fb923c', letterSpacing: '0.2em', fontFamily: 'Cinzel, serif' }}>
              ⚠ Configuration incomplète
            </div>
            <p className="text-sm" style={{ color: 'rgba(227,215,255,0.8)', fontFamily: 'Cormorant Garamond, serif' }}>
              La variable <code style={{ color: '#D4AF37' }}>REACT_APP_PLAUSIBLE_DOMAIN</code> n&apos;est pas définie.
              Les liens ci-dessous pointent vers <strong>plume-astrale.fr</strong> par défaut.
              Consulte <code style={{ color: '#D4AF37' }}>/app/memory/setup_cercle_solena_analytics.md</code>.
            </p>
          </div>
        )}

        {/* Grille des 6 KPI */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
          {KPIS.map((k, i) => {
            const Icon = k.icon;
            return (
              <a
                key={k.label}
                href={`${PLAUSIBLE_BASE}${k.query}`}
                target="_blank"
                rel="noopener noreferrer"
                className="plume-glass p-5 group hover:opacity-95 transition-all"
                data-testid={`analytics-kpi-${i}`}
                style={{ border: '1px solid rgba(212,175,55,0.2)', textDecoration: 'none', display: 'block' }}
              >
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
                    style={{ background: `${k.color}22`, border: `1px solid ${k.color}44` }}
                  >
                    <Icon className="w-5 h-5" strokeWidth={1.4} style={{ color: k.color }} />
                  </div>
                  <ArrowUpRight
                    className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity"
                    style={{ color: k.color }}
                  />
                </div>

                <div style={{ fontFamily: 'Cinzel, serif', fontSize: 11, color: '#F5EEE0', letterSpacing: '0.15em', marginBottom: 4 }}>
                  {k.label}
                </div>
                <div className="text-sm mb-2" style={{ color: 'rgba(227,215,255,0.7)', fontFamily: 'Cormorant Garamond, serif' }}>
                  {k.goal}
                </div>
                <div
                  className="text-[11px] mb-3 inline-block px-2 py-0.5 rounded-full"
                  style={{ background: `${k.color}15`, color: k.color, letterSpacing: '0.1em' }}
                >
                  Cible : {k.target}
                </div>
                <p
                  className="text-xs mt-2"
                  style={{ color: 'rgba(227,215,255,0.55)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic', lineHeight: 1.5 }}
                >
                  {k.reading}
                </p>
              </a>
            );
          })}
        </div>

        {/* Funnel de conversion */}
        <section className="plume-glass p-6 md:p-8 mb-8" data-testid="analytics-funnel">
          <div className="text-[10px] uppercase mb-3" style={{ color: '#D4AF37', letterSpacing: '0.32em', fontFamily: 'Cinzel, serif' }}>
            ✦ Le tunnel qui compte ✦
          </div>
          <h2 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 28, color: '#F5EEE0', marginBottom: 20, fontStyle: 'italic', fontWeight: 300 }}>
            De la visite à l&apos;abonnement — 5 étapes
          </h2>

          <ol className="space-y-4">
            {FUNNEL_STEPS.map((step, i) => (
              <li key={i} className="flex items-start gap-4" data-testid={`analytics-funnel-step-${i}`}>
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-0.5"
                  style={{ background: 'rgba(212,175,55,0.15)', border: '1px solid rgba(212,175,55,0.4)', color: '#D4AF37', fontFamily: 'Cinzel, serif', fontSize: 13 }}
                >
                  {i + 1}
                </div>
                <div className="flex-1">
                  <div style={{ fontFamily: 'Cinzel, serif', fontSize: 13, color: '#F5EEE0', letterSpacing: '0.12em' }}>
                    {step.label}
                  </div>
                  <div className="flex items-baseline gap-3 mt-1">
                    <code className="text-[11px]" style={{ color: '#D4AF37' }}>{step.formula}</code>
                    {step.ratio && (
                      <span className="text-[11px]" style={{ color: 'rgba(227,215,255,0.5)' }}>
                        ratio {step.ratio}
                      </span>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ol>
        </section>

        {/* Liens rapides */}
        <section className="plume-glass p-6 md:p-8" data-testid="analytics-quick-links">
          <div className="text-[10px] uppercase mb-3" style={{ color: '#D4AF37', letterSpacing: '0.32em', fontFamily: 'Cinzel, serif' }}>
            ✦ Liens rapides ✦
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
            <a href={`${PLAUSIBLE_BASE}?period=day`}   target="_blank" rel="noopener noreferrer" className="flex items-center justify-between p-3 rounded-lg hover:bg-white/5" style={{ border: '1px solid rgba(212,175,55,0.15)', color: '#F5EEE0', textDecoration: 'none' }}>
              <span>Aujourd&apos;hui</span>
              <ArrowUpRight className="w-4 h-4" style={{ color: '#D4AF37' }} />
            </a>
            <a href={`${PLAUSIBLE_BASE}?period=7d`}    target="_blank" rel="noopener noreferrer" className="flex items-center justify-between p-3 rounded-lg hover:bg-white/5" style={{ border: '1px solid rgba(212,175,55,0.15)', color: '#F5EEE0', textDecoration: 'none' }}>
              <span>7 derniers jours</span>
              <ArrowUpRight className="w-4 h-4" style={{ color: '#D4AF37' }} />
            </a>
            <a href={`${PLAUSIBLE_BASE}?period=30d`}   target="_blank" rel="noopener noreferrer" className="flex items-center justify-between p-3 rounded-lg hover:bg-white/5" style={{ border: '1px solid rgba(212,175,55,0.15)', color: '#F5EEE0', textDecoration: 'none' }}>
              <span>30 derniers jours</span>
              <ArrowUpRight className="w-4 h-4" style={{ color: '#D4AF37' }} />
            </a>
            <a href={`${PLAUSIBLE_BASE}?period=month`} target="_blank" rel="noopener noreferrer" className="flex items-center justify-between p-3 rounded-lg hover:bg-white/5" style={{ border: '1px solid rgba(212,175,55,0.15)', color: '#F5EEE0', textDecoration: 'none' }}>
              <span>Mois en cours</span>
              <ArrowUpRight className="w-4 h-4" style={{ color: '#D4AF37' }} />
            </a>
          </div>
          <p className="text-[11px] mt-4" style={{ color: 'rgba(227,215,255,0.5)', fontStyle: 'italic', fontFamily: 'Cormorant Garamond, serif' }}>
            Astuce : ajoute <code style={{ color: '#D4AF37' }}>plausible.io/{DOMAIN}</code> à tes favoris pour un accès en 1 clic.
          </p>
        </section>
      </div>
    </>
  );
};

export default AnalyticsAdmin;
