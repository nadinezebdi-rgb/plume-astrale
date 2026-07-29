import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Sparkles, Gift, ArrowRight, Loader2 } from 'lucide-react';
import axios from 'axios';
import { event as track, EVENTS } from '@/lib/analytics';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

/**
 * Bandeau invitation Cercle Soléna, affiché après un achat PDF réussi.
 * Propose un premier mois offert (trial 30j) — le moment où la CB
 * est encore chaude et l'utilisateur au sommet de son émotion positive.
 *
 * L'utilisateur clique → checkout Stripe subscription avec trial_period_days=30.
 * Si non connecté (rare sur une page succès), redirige vers /cercle-solena.
 *
 * Props:
 *  - sourceProduct : nom du produit qui vient d'être acheté (analytics + copy)
 *  - testId        : préfixe data-testid (défaut : 'post-purchase-cercle')
 */
const CercleSolenaInvite = ({ sourceProduct = 'pdf', testId = 'post-purchase-cercle' }) => {
  const navigate = useNavigate();
  const { isAuthenticated, session } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  const handleClaim = async () => {
    track(EVENTS.CERCLE_SOLENA_CHECKOUT, {
      source: `post_purchase_${sourceProduct}`,
      trial: true,
    });
    if (!isAuthenticated) {
      navigate('/cercle-solena');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const r = await axios.post(
        `${API}/subscriptions/cercle-solena/checkout`,
        { origin_url: window.location.origin, with_trial: true },
        { headers: { Authorization: `Bearer ${session.access_token}` } },
      );
      window.location.href = r.data.url;
    } catch (e) {
      setError(e.response?.data?.detail || 'Réessaie dans un instant.');
      setLoading(false);
    }
  };

  return (
    <div
      className="plume-glass p-6 md:p-8 mt-14 relative overflow-hidden"
      data-testid={testId}
      style={{
        border: '1px solid rgba(212,175,55,0.4)',
        boxShadow: '0 30px 80px -30px rgba(212,175,55,0.3)',
      }}
    >
      {/* Badge d'offre */}
      <div
        className="absolute top-3 right-3 px-3 py-1 rounded-full text-[10px] uppercase"
        style={{
          background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 50%, #D4AF37 100%)',
          color: '#0A0603',
          fontFamily: 'Cinzel, serif',
          letterSpacing: '0.18em',
          fontWeight: 700,
        }}
        data-testid={`${testId}-badge`}
      >
        1 mois offert
      </div>

      <p
        className="text-[10px] uppercase mb-3"
        style={{ color: '#D4AF37', letterSpacing: '0.32em', fontFamily: 'Cinzel, serif' }}
      >
        <Gift className="w-3 h-3 inline mr-1.5" strokeWidth={1.5} />
        Un cadeau pour toi
      </p>

      <h3
        style={{
          fontFamily: 'Cormorant Garamond, serif',
          fontWeight: 300,
          fontSize: 'clamp(22px, 2.8vw, 30px)',
          color: '#F5EEE0',
          lineHeight: 1.2,
          marginBottom: 10,
        }}
        data-testid={`${testId}-title`}
      >
        Merci d&apos;avoir choisi Plume Astrale.{' '}
        <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>Continue le voyage — offert.</em>
      </h3>

      <p
        className="text-sm md:text-base mb-5"
        style={{
          color: 'rgba(227,215,255,0.8)',
          fontFamily: 'Cormorant Garamond, serif',
          fontStyle: 'italic',
          lineHeight: 1.55,
        }}
      >
        Ton premier mois au Cercle Soléna est <strong style={{ color: '#D4AF37' }}>offert</strong>.
        Reçois 50 crédits chat supplémentaires, rejoins la communauté privée et bénéficie de -10%
        sur toutes tes futures lectures. Résilie en 1 clic à tout moment.
      </p>

      <div className="flex items-baseline gap-3 mb-5" data-testid={`${testId}-pricing`}>
        <span style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 34, color: '#D4AF37', fontWeight: 300 }}>
          0€
        </span>
        <span style={{ color: 'rgba(227,215,255,0.65)', fontSize: 14, fontStyle: 'italic' }}>
          pendant 30 jours
        </span>
        <span className="text-xs" style={{ color: 'rgba(227,215,255,0.45)', letterSpacing: '0.1em' }}>
          · puis 19€/mois
        </span>
      </div>

      <p className="text-[11px] mb-5" style={{ color: 'rgba(227,215,255,0.55)', lineHeight: 1.55 }}>
        <Sparkles className="w-3 h-3 inline mr-1" style={{ color: '#D4AF37' }} />
        Offre réservée aux clientes qui viennent de recevoir leur lecture. Aucun renouvellement
        automatique sans ton accord.
      </p>

      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={handleClaim}
          disabled={loading}
          className="plume-btn-primary flex-1 justify-center"
          data-testid={`${testId}-cta`}
          style={{ display: 'inline-flex' }}
        >
          {loading
            ? <><Loader2 className="w-4 h-4 animate-spin" /> Redirection...</>
            : <><Gift className="w-4 h-4" strokeWidth={1.5} /> Activer mon mois offert <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></>}
        </button>
        <button
          onClick={() => setDismissed(true)}
          className="text-xs px-4 py-2 hover:opacity-80"
          data-testid={`${testId}-dismiss`}
          style={{ color: 'rgba(227,215,255,0.5)', letterSpacing: '0.15em' }}
        >
          Plus tard
        </button>
      </div>

      {error && (
        <p className="mt-3 text-xs" data-testid={`${testId}-error`} style={{ color: '#f87171' }}>
          {error}
        </p>
      )}
    </div>
  );
};

export default CercleSolenaInvite;
