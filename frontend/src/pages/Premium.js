import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Check, Sparkles, Crown, Loader2 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import SEO from '@/components/SEO';
import { event as trackEvent } from '@/lib/analytics';

const API = process.env.REACT_APP_BACKEND_URL;

const PREMIUM_FEATURES = [
  'Énergie quotidienne complète (4 sections)',
  'Cycles de vie illimités (3 mois + à venir)',
  'Compatibilités illimitées avec scores détaillés',
  'Historique personnel + journal astrologique',
  'Notifications quotidiennes personnalisées',
  'Accès prioritaire aux nouveautés',
];

const FREE_FEATURES = [
  'Mini horoscope quotidien',
  'Énergie du jour (aperçu)',
  '20 crédits à l\'inscription',
  '1er tarot oui/non gratuit',
];

function PricingCard({ title, price, period, features, cta, highlighted, onCta, badge, loading }) {
  return (
    <div style={{
      flex: 1,
      maxWidth: 420,
      padding: '32px 28px',
      borderRadius: 20,
      background: highlighted
        ? 'linear-gradient(180deg, rgba(212,175,55,0.15) 0%, rgba(11,14,40,0.85) 100%)'
        : 'linear-gradient(180deg, rgba(6,8,26,0.6) 0%, rgba(11,14,40,0.5) 100%)',
      border: highlighted
        ? '1.5px solid rgba(212,175,55,0.55)'
        : '1px solid rgba(212,175,55,0.18)',
      backdropFilter: 'blur(16px)',
      position: 'relative',
      boxShadow: highlighted ? '0 12px 40px rgba(212,175,55,0.15)' : '0 4px 20px rgba(0,0,0,0.3)',
    }}>
      {badge && (
        <div style={{
          position: 'absolute', top: -12, left: '50%', transform: 'translateX(-50%)',
          padding: '4px 14px', borderRadius: 999,
          background: '#D4AF37', color: '#0F1230',
          fontSize: 10, letterSpacing: '0.16em', textTransform: 'uppercase',
          fontFamily: 'Cinzel, serif', fontWeight: 600,
        }}>
          {badge}
        </div>
      )}

      <div style={{
        fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase',
        color: highlighted ? '#E8C766' : 'rgba(212,175,55,0.7)',
        fontFamily: 'Cinzel, serif', marginBottom: 8,
      }}>
        {title}
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 24 }}>
        <span style={{
          fontFamily: 'Cormorant Garamond, serif', fontSize: 48,
          color: highlighted ? '#F4E4BC' : '#fff', fontWeight: 400, lineHeight: 1,
        }}>{price}</span>
        {period && <span style={{ color: 'rgba(255,255,255,0.55)', fontSize: 13 }}>{period}</span>}
      </div>

      <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 28px', display: 'flex', flexDirection: 'column', gap: 11 }}>
        {features.map((f, i) => (
          <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, fontSize: 13.5, color: 'rgba(255,255,255,0.78)', lineHeight: 1.5 }}>
            <Check style={{
              width: 15, height: 15, color: highlighted ? '#D4AF37' : 'rgba(212,175,55,0.6)',
              flexShrink: 0, marginTop: 2,
            }} strokeWidth={2} />
            <span>{f}</span>
          </li>
        ))}
      </ul>

      <button onClick={onCta} disabled={loading} style={{
        width: '100%', padding: '14px 24px', borderRadius: 999,
        background: highlighted ? '#D4AF37' : 'transparent',
        color: highlighted ? '#0F1230' : '#D4AF37',
        border: highlighted ? 'none' : '1px solid rgba(212,175,55,0.4)',
        fontFamily: 'Cinzel, serif', fontSize: 11, fontWeight: 600,
        letterSpacing: '0.18em', textTransform: 'uppercase',
        cursor: loading ? 'wait' : 'pointer',
        opacity: loading ? 0.7 : 1,
        display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8,
      }} data-testid={`premium-cta-${title.toLowerCase()}`}>
        {loading ? <><Loader2 className="animate-spin" style={{ width: 14, height: 14 }} /> Redirection</> : cta}
      </button>
    </div>
  );
}

export default function Premium() {
  const navigate = useNavigate();
  const { user, isAuthenticated, token } = useAuth();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  useEffect(() => {
    if (!isAuthenticated || !token) return;
    axios.get(`${API}/api/premium/status`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => setStatus(r.data))
      .catch(() => {});
  }, [isAuthenticated, token]);

  const handleSubscribe = async () => {
    if (!isAuthenticated) { navigate('/inscription'); return; }
    setLoading(true);
    setErr(null);
    trackEvent('premium_checkout_started');
    try {
      const r = await axios.post(`${API}/api/premium/checkout`,
        { origin_url: window.location.origin },
        { headers: { Authorization: `Bearer ${token}` } });
      window.location.href = r.data.url;
    } catch (e) {
      setErr(e.response?.data?.detail || "Erreur lors de la creation de l'abonnement.");
      setLoading(false);
    }
  };

  const handleManage = async () => {
    setLoading(true);
    setErr(null);
    try {
      const r = await axios.post(`${API}/api/premium/portal`,
        { return_url: window.location.href },
        { headers: { Authorization: `Bearer ${token}` } });
      window.location.href = r.data.url;
    } catch (e) {
      if (e.response?.status === 404) {
        setErr("Votre accès Premium a été accordé manuellement (hors Stripe). Aucun portail de gestion n'est disponible pour ce type d'accès.");
      } else {
        setErr("Impossible d'ouvrir le portail de gestion. Réessayez dans quelques instants.");
      }
      setLoading(false);
    }
  };

  const isPremium = status?.is_premium || user?.is_premium;
  // Only show Stripe-managed subscriptions in the management UI
  const hasStripeSubscription = !!status?.subscription_id;

  return (
    <>
      <SEO title="Plume Astrale Premium — 14,99€/mois" description="Abonnement premium : énergie complète, cycles illimités, compatibilités, journal et notifications quotidiennes." />
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #131840 0%, #1B2150 50%, #131840 100%)',
        paddingTop: 100, paddingBottom: 80,
        padding: '100px 16px 80px',
      }} data-testid="premium-page">
        <div style={{ maxWidth: 1000, margin: '0 auto' }}>

          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              padding: '6px 16px', borderRadius: 999, marginBottom: 16,
              background: 'rgba(212,175,55,0.12)', border: '1px solid rgba(212,175,55,0.3)',
            }}>
              <Crown style={{ width: 13, height: 13, color: '#E8C766' }} strokeWidth={1.5} />
              <span style={{ fontSize: 10, letterSpacing: '0.2em', color: '#E8C766', textTransform: 'uppercase', fontFamily: 'Cinzel, serif' }}>
                Plume Astrale Premium
              </span>
            </div>
            <h1 style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: 'clamp(34px, 5vw, 50px)', color: '#F4E4BC', marginBottom: 12, fontWeight: 300, lineHeight: 1.15,
            }}>
              Une guidance vivante,<br />
              <span style={{ color: '#D4AF37', fontStyle: 'italic' }}>chaque jour</span>
            </h1>
            <p style={{ fontSize: 16, color: 'rgba(255,255,255,0.7)', maxWidth: 580, margin: '0 auto', lineHeight: 1.6 }}>
              L&apos;abonnement Premium ouvre l&apos;accès complet aux cycles, compatibilités,
              au journal personnel et aux notifications. Une connexion quotidienne à ton thème natal.
            </p>
          </div>

          {isPremium && (
            <div style={{
              maxWidth: 540, margin: '0 auto 32px',
              padding: '20px 24px', borderRadius: 14, textAlign: 'center',
              background: 'rgba(124,184,138,0.1)', border: '1px solid rgba(124,184,138,0.4)',
            }} data-testid="premium-active-badge">
              <p style={{ fontSize: 14, color: '#A3D6AC', marginBottom: 10 }}>
                ✦ Tu es membre Premium actif
              </p>
              {hasStripeSubscription ? (
                <button onClick={handleManage} disabled={loading} style={{
                  padding: '10px 22px', borderRadius: 999,
                  background: 'transparent', border: '1px solid rgba(124,184,138,0.5)',
                  color: '#A3D6AC', fontFamily: 'Cinzel, serif', fontSize: 11,
                  letterSpacing: '0.18em', textTransform: 'uppercase', cursor: 'pointer',
                }} data-testid="manage-subscription-btn">
                  {loading ? 'Redirection...' : "Gerer mon abonnement"}
                </button>
              ) : (
                <p style={{ fontSize: 12, color: 'rgba(255,255,255,0.55)', fontStyle: 'italic' }} data-testid="premium-manual-grant-note">
                  Accès offert — aucun abonnement Stripe à gérer.
                </p>
              )}
            </div>
          )}

          {err && (
            <div style={{ maxWidth: 540, margin: '0 auto 20px', padding: 12, borderRadius: 10, background: 'rgba(255,100,100,0.1)', border: '1px solid rgba(255,100,100,0.3)', color: '#fca5a5', fontSize: 13, textAlign: 'center' }}>
              {err}
            </div>
          )}

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 24, justifyContent: 'center' }}>
            <PricingCard
              title="Decouverte"
              price="0€"
              features={FREE_FEATURES}
              cta={isAuthenticated ? 'Plan actuel' : 'Creer mon compte'}
              onCta={() => navigate(isAuthenticated ? '/mon-compte' : '/inscription')}
            />
            <PricingCard
              title="Premium mensuel"
              price="14,99€"
              period="/ mois"
              features={['7 jours d\'essai gratuit', ...PREMIUM_FEATURES]}
              cta={isPremium ? 'Deja membre' : "Demarrer mon essai gratuit"}
              highlighted
              badge="7 jours offerts"
              onCta={isPremium ? () => {} : handleSubscribe}
              loading={loading}
            />
          </div>

          <p style={{
            textAlign: 'center', marginTop: 28, fontSize: 12,
            color: 'rgba(212,175,55,0.75)', lineHeight: 1.6, maxWidth: 600, margin: '28px auto 0',
            fontStyle: 'italic',
          }}>
            ✦ Carte requise pour activer l&apos;essai — aucun debit pendant 7 jours, annulable a tout moment ✦
          </p>

          <p style={{
            textAlign: 'center', marginTop: 40, fontSize: 12,
            color: 'rgba(255,255,255,0.45)', lineHeight: 1.6, maxWidth: 600, margin: '40px auto 0',
          }}>
            <Sparkles style={{ width: 12, height: 12, display: 'inline', marginRight: 4, color: 'rgba(212,175,55,0.5)' }} />
            Sans engagement — annulable a tout moment depuis ton espace.
            Les consultations Plume restent en crédits (2cr/message) pour garantir une experience qualitative.
          </p>

          <div style={{
            marginTop: 60, paddingTop: 30, textAlign: 'center',
            borderTop: '1px solid rgba(212,175,55,0.1)',
          }}>
            <p style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', lineHeight: 1.6 }}>
              Calculs astrologiques propulsés par <strong style={{ color: 'rgba(212,175,55,0.75)' }}>AstrologyAPI</strong> ·
              Paiement sécurisé par <strong style={{ color: 'rgba(212,175,55,0.75)' }}>Stripe</strong>
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
