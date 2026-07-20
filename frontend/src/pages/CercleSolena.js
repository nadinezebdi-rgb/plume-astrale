import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Check, Sparkles, Users, Gift, Calendar, ArrowRight, Loader2 } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import PageHero from '@/components/PageHero';
import { event as track, EVENTS } from '@/lib/analytics';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const BENEFITS = [
  { icon: Gift,     title: '3 crédits offerts chaque mois', desc: 'Rechargés automatiquement à ta date d\u2019anniversaire d\u2019abonnement.' },
  { icon: Users,    title: 'Accès au Cercle Soléna',       desc: 'Communauté privée d\u2019initiées — échanges, méditations, réponses de Soléna en direct.' },
  { icon: Calendar, title: 'Lecture Nouvelle Lune',        desc: 'Une lecture symbolique mensuelle offerte à chaque cycle lunaire.' },
  { icon: Sparkles, title: 'Réductions sur les PDF',      desc: '-10% sur Kabbale, Astrocarto, Pack Karmique pendant toute la durée de ton abonnement.' },
];

const CercleSolena = () => {
  const navigate = useNavigate();
  const { isAuthenticated, session, loading: authLoading } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState(null);

  // Vérifie si l'utilisateur est déjà abonné
  useEffect(() => {
    if (!isAuthenticated || !session?.access_token) return;
    axios.get(`${API}/subscriptions/cercle-solena/status`, {
      headers: { Authorization: `Bearer ${session.access_token}` },
    }).then((r) => setStatus(r.data)).catch(() => {});
  }, [isAuthenticated, session]);

  const handleCheckout = async () => {
    track(EVENTS.CERCLE_SOLENA_CHECKOUT, { authenticated: isAuthenticated });
    if (!isAuthenticated) {
      navigate('/connexion?redirect=/cercle-solena');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const r = await axios.post(
        `${API}/subscriptions/cercle-solena/checkout`,
        { origin_url: window.location.origin },
        { headers: { Authorization: `Bearer ${session.access_token}` } },
      );
      window.location.href = r.data.url;
    } catch (e) {
      setError(e.response?.data?.detail || 'Impossible de créer la session. Réessaie dans un instant.');
      setLoading(false);
    }
  };

  const isAlreadyMember = status?.active;

  return (
    <>
      <SEO
        title="Cercle Soléna — Abonnement mensuel Plume Astrale"
        description="Rejoins le Cercle Soléna. 3 crédits/mois, accès communauté, réductions permanentes. 19€/mois, résiliable à tout moment."
      />
      <PageHero
        badge="✦ Cercle Soléna ✦"
        title="Un rendez-vous mensuel avec ton étoile"
        subtitle="19€ par mois pour continuer à te lire, mois après mois — accès communauté, crédits, réductions."
      />

      <div className="max-w-4xl mx-auto px-6 pb-24 pt-4">
        {/* Pricing card centrale */}
        <div
          className="plume-glass p-6 md:p-10 mb-10 text-center relative overflow-hidden"
          data-testid="cercle-solena-pricing"
          style={{
            border: '1px solid rgba(212,175,55,0.4)',
            boxShadow: '0 30px 80px -30px rgba(212,175,55,0.3)',
          }}
        >
          <p className="text-[10px] uppercase mb-4" style={{ color: '#D4AF37', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}>
            ✦ Abonnement mensuel ✦
          </p>

          <div className="flex items-baseline justify-center gap-2 mb-2">
            <span style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 72, color: '#D4AF37', fontWeight: 300, lineHeight: 1 }}>19€</span>
            <span style={{ color: 'rgba(227,215,255,0.65)', fontSize: 18, fontStyle: 'italic', fontFamily: 'Cormorant Garamond, serif' }}>/mois</span>
          </div>
          <p className="text-xs mb-6" style={{ color: 'rgba(227,215,255,0.55)', letterSpacing: '0.15em' }}>
            Sans engagement · Résiliation en 1 clic
          </p>

          {isAlreadyMember ? (
            <div
              className="inline-flex items-center gap-2 px-5 py-3 rounded-full"
              data-testid="cercle-already-member"
              style={{ background: 'rgba(212,175,55,0.15)', border: '1px solid rgba(212,175,55,0.4)', color: '#D4AF37', fontFamily: 'Cinzel, serif', fontSize: 13, letterSpacing: '0.2em' }}
            >
              <Check className="w-4 h-4" strokeWidth={1.8} />
              TU ES MEMBRE DU CERCLE
            </div>
          ) : (
            <>
              <button
                onClick={handleCheckout}
                disabled={loading || authLoading}
                className="plume-btn-primary"
                data-testid="cercle-solena-cta"
                style={{ display: 'inline-flex', minWidth: 260, justifyContent: 'center' }}
              >
                {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Redirection...</> :
                  isAuthenticated ? <>Rejoindre le Cercle <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></>
                                  : <>Créer mon compte pour rejoindre <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></>}
              </button>
              {error && (
                <p className="mt-3 text-xs" style={{ color: '#f87171' }} data-testid="cercle-solena-error">{error}</p>
              )}
              <p className="text-[11px] mt-4" style={{ color: 'rgba(227,215,255,0.5)', letterSpacing: '0.1em' }}>
                Paiement sécurisé Stripe · Facture PDF envoyée par email
              </p>
            </>
          )}
        </div>

        {/* Avantages */}
        <h2
          className="text-center mb-8"
          style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 300,
            fontSize: 'clamp(24px, 3vw, 34px)',
            color: '#F5EEE0',
            fontStyle: 'italic',
          }}
        >
          Ce que tu reçois chaque mois
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
          {BENEFITS.map((b, i) => {
            const Icon = b.icon;
            return (
              <div key={i} className="plume-glass p-5 flex items-start gap-4" data-testid={`cercle-benefit-${i}`}>
                <div
                  className="shrink-0 w-11 h-11 rounded-full flex items-center justify-center"
                  style={{ background: 'rgba(212,175,55,0.12)', border: '1px solid rgba(212,175,55,0.35)' }}
                >
                  <Icon className="w-5 h-5" strokeWidth={1.4} style={{ color: '#D4AF37' }} />
                </div>
                <div>
                  <div style={{ fontFamily: 'Cinzel, serif', fontSize: 13, color: '#F5EEE0', letterSpacing: '0.12em', marginBottom: 4 }}>
                    {b.title}
                  </div>
                  <div className="text-sm" style={{ color: 'rgba(227,215,255,0.7)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic', lineHeight: 1.5 }}>
                    {b.desc}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* FAQ minimaliste */}
        <div className="plume-glass p-6 md:p-8" data-testid="cercle-faq">
          <h3 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 22, color: '#F5EEE0', marginBottom: 14, fontStyle: 'italic' }}>
            Questions fréquentes
          </h3>
          <div className="space-y-4 text-sm" style={{ color: 'rgba(227,215,255,0.75)', fontFamily: 'Cormorant Garamond, serif' }}>
            <div>
              <div style={{ color: '#D4AF37', fontFamily: 'Cinzel, serif', fontSize: 12, letterSpacing: '0.12em', marginBottom: 4 }}>PUIS-JE RÉSILIER À TOUT MOMENT ?</div>
              <p>Oui. Depuis ta page « Mon Compte », un clic ouvre le Portail Stripe où tu résilies en 3 secondes. L&apos;accès reste actif jusqu&apos;à la fin du mois en cours.</p>
            </div>
            <div>
              <div style={{ color: '#D4AF37', fontFamily: 'Cinzel, serif', fontSize: 12, letterSpacing: '0.12em', marginBottom: 4 }}>QUAND SONT CRÉDITÉS LES 3 CRÉDITS ?</div>
              <p>Immédiatement au 1er paiement, puis chaque renouvellement mensuel. Les crédits ne se cumulent pas indéfiniment — utilise-les dans le mois pour en profiter.</p>
            </div>
            <div>
              <div style={{ color: '#D4AF37', fontFamily: 'Cinzel, serif', fontSize: 12, letterSpacing: '0.12em', marginBottom: 4 }}>C&apos;EST QUOI, LA COMMUNAUTÉ ?</div>
              <p>Un espace privé où Soléna partage des lectures collectives, tu poses des questions et rencontres d&apos;autres âmes en cheminement. Discord dédié.</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default CercleSolena;
