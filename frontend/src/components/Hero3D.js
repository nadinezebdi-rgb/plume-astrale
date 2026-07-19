import React, { lazy, Suspense } from 'react';
import { Link } from 'react-router-dom';
import { User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import StarsAndClouds from './StarsAndClouds';
import LaunchBanner from './LaunchBanner';

const Moon3D = lazy(() => import('./Moon3D'));

/**
 * Hero3D — Section hero d'accueil.
 * CTA principal : Créer un compte (20 crédits offerts).
 * Le funnel legacy "modal 2 prénoms → portrait karmique gratuit" a été retiré
 * (double lead magnet en conflit avec l'offre 20 crédits à l'inscription).
 */
export default function Hero3D() {
  const { isAuthenticated } = useAuth();
  return (
    <section
      className="relative w-full overflow-hidden"
      style={{
        background: '#0C1120',
        color: '#F5EEE0',
        minHeight: '100vh',
      }}
      data-testid="hero-3d"
    >
      {/* ═══ Bandeau d'urgence sticky top — cliquable + défilant + compte à rebours 48h ═══ */}
      <LaunchBanner />

      {/* ═══ Header ultra-épuré ═══ */}
      <header className="absolute top-0 left-0 right-0 z-30 flex items-center justify-between px-6 md:px-10"
        style={{ paddingTop: 52, paddingBottom: 12 }}>
        <Link to="/" style={{
          fontFamily: 'Cinzel, Playfair Display, serif',
          color: '#E2BF65',
          fontWeight: 400,
          fontSize: 15,
          letterSpacing: '0.35em',
          textDecoration: 'none',
          textShadow: '0 0 16px rgba(226,191,101,0.35)',
        }} data-testid="hero-brand-logo">
          PLUME ASTRALE
        </Link>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Link
            to={isAuthenticated ? '/mon-compte' : '/connexion'}
            className="flex items-center gap-2 group transition-all whitespace-nowrap"
            style={{
              color: 'rgba(226,191,101,0.85)',
              textDecoration: 'none',
              fontSize: 11,
              letterSpacing: '0.22em',
              textTransform: 'uppercase',
              padding: '8px 12px',
              borderRadius: 999,
              border: '1px solid rgba(226,191,101,0.50)',
              fontFamily: 'Inter, sans-serif',
            }}
            data-testid="hero-account-btn"
            aria-label="Mon Compte"
          >
            <User style={{ width: 12, height: 12 }} strokeWidth={1.5} />
            <span className="hidden sm:inline">Mon Compte</span>
          </Link>
          <Link
            to="/connexion"
            className="flex items-center gap-2 group transition-all whitespace-nowrap"
            style={{
              color: '#0A0603',
              textDecoration: 'none',
              fontSize: 11,
              letterSpacing: '0.22em',
              textTransform: 'uppercase',
              padding: '8px 12px',
              borderRadius: 999,
              background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 50%, #D4AF37 100%)',
              fontFamily: 'Inter, sans-serif',
              fontWeight: 600,
            }}
            data-testid="hero-login-btn"
            aria-label="Se connecter"
          >
            <User style={{ width: 12, height: 12 }} strokeWidth={1.5} />
            <span className="hidden sm:inline">Se connecter</span>
          </Link>
        </div>
      </header>

      {/* ═══ Clouds & Stars Background Overlay ═══ */}
      <StarsAndClouds />

      {/* ═══ 3D Lune avec Halo ═══ */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          zIndex: 1,
          pointerEvents: 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Halo Glow autour de la lune */}
        <div
          aria-hidden="true"
          style={{
            position: 'absolute',
            width: '600px',
            height: '600px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(232, 199, 102, 0.15) 0%, rgba(167, 139, 250, 0.08) 40%, transparent 70%)',
            filter: 'blur(60px)',
            zIndex: 0,
          }}
        />
        {/* Moon3D rendu par-dessus le halo */}
        <div style={{ position: 'absolute', inset: 0, zIndex: 1 }}>
          <Suspense fallback={null}>
            <Moon3D />
          </Suspense>
        </div>
      </div>

      {/* ═══ Vignette subtle harmony ═══ */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute', inset: 0, zIndex: 2, pointerEvents: 'none',
          background: 'radial-gradient(ellipse at 50% 50%, transparent 0%, rgba(17, 22, 37, 0.0) 100%)',
        }}
      />

      {/* ═══ ÉTAPE 1: L'Hameçon - CTA sur la lune ═══ */}
      <div
        className="relative z-10 flex flex-col items-center justify-center text-center px-4"
        style={{
          minHeight: '100vh',
          paddingTop: 'clamp(80px, 11vh, 130px)',
          paddingBottom: 'clamp(16px, 2.5vh, 32px)',
        }}
      >
        {/* Titre Principal */}
        <h2
          style={{
            fontFamily: 'Cinzel, Playfair Display, Cormorant Garamond, serif',
            fontWeight: 300,
            fontSize: 'clamp(1.7rem, 4.8vw, 3.2rem)',
            lineHeight: 1.15,
            letterSpacing: '0.02em',
            color: '#FFFFFF',
            textShadow: '0 4px 60px rgba(0,0,0,1), 0 0 30px rgba(226,191,101,0.15)',
            maxWidth: 780,
            marginBottom: 16,
          }}
          data-testid="hero-headline"
        >
          En 3 minutes,
          <br />
          comprends ce qui se joue dans ta <em style={{ fontStyle: 'italic', color: '#E8C766' }}>vie amoureuse</em>.
        </h2>

        {/* Sous-texte */}
        <p
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 'clamp(0.95rem, 1.3vw, 1.1rem)',
            fontWeight: 300,
            lineHeight: 1.7,
            color: '#CBD5E1',
            textShadow: '0 2px 20px rgba(0,0,0,0.9)',
            maxWidth: 580,
            marginBottom: 32,
            fontStyle: 'italic',
          }}
          data-testid="hero-subheadline"
        >
          20 crédits offerts à l&apos;inscription — pose tes premières questions à Soléna, tire tes cartes, découvre tes cycles d&apos;amour.
        </p>

        {/* CTA Principal — dirige vers /inscription (20 crédits offerts) */}
        <Link
          to="/inscription"
          className="group relative px-6 sm:px-8 py-4 overflow-hidden rounded-full transition-all duration-300 hover:scale-105 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[#D4AF37] max-w-[90vw]"
          style={{
            background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 50%, #D4AF37 100%)',
            color: '#0A0603',
            fontFamily: 'Cinzel, sans-serif',
            fontWeight: 700,
            fontSize: 'clamp(0.72rem, 1vw, 1.05rem)',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            border: 'none',
            cursor: 'pointer',
            boxShadow: '0 0 40px rgba(212,175,55,0.5)',
            textDecoration: 'none',
            display: 'inline-block',
            whiteSpace: 'nowrap',
          }}
          data-testid="hero-cta-button"
        >
          <span style={{ position: 'relative', zIndex: 2 }}>
            <span className="sm:hidden">Créer mon compte · 20 crédits</span>
            <span className="hidden sm:inline">Créer mon compte · 20 crédits offerts</span>
          </span>
          <div
            className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
            style={{
              background: 'radial-gradient(circle at 50% 50%, #FFF3D6 0%, #E8C766 40%, transparent 100%)',
              animation: 'pulse 2s ease-in-out infinite',
            }}
          />
        </Link>

        {/* Trust strip retiré : le badge "4.9/5 · +2 000 âmes accompagnées" apparaît
            désormais uniquement une fois, juste avant la section reviews (pas de doublon). */}

        {/* Mini-bar de trust : données · calculs · paiement */}
        <div
          className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2"
          style={{
            marginTop: 20,
            fontFamily: 'Inter, sans-serif',
            fontSize: 'clamp(0.65rem, 0.75vw, 0.72rem)',
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: 'rgba(203,213,225,0.55)',
            textShadow: '0 2px 8px rgba(0,0,0,0.7)',
          }}
          data-testid="hero-trust-chips"
        >
          <span>✓ Données réelles</span>
          <span style={{ opacity: 0.35 }}>·</span>
          <span>✓ Calculs précis</span>
          <span style={{ opacity: 0.35 }}>·</span>
          <span>✓ Paiement sécurisé Stripe</span>
        </div><div style={{ marginTop: 44, maxWidth: 660, textAlign: 'center' }} data-testid="hero-positioning-text"><h2 style={{ fontFamily: 'Cinzel, Playfair Display, Cormorant Garamond, serif', fontWeight: 400, fontSize: 'clamp(1.2rem, 2.6vw, 1.85rem)', lineHeight: 1.25, letterSpacing: '0.02em', color: '#E8C766', textShadow: '0 2px 30px rgba(0,0,0,0.95)', marginBottom: 12 }}>Votre vie change. Comprenez pourquoi.</h2><p style={{ fontFamily: 'Inter, sans-serif', fontSize: 'clamp(0.9rem, 1.2vw, 1.05rem)', fontWeight: 300, lineHeight: 1.7, color: '#CBD5E1', textShadow: '0 2px 20px rgba(0,0,0,0.9)', margin: 0 }}>Découvrez les périodes qui favorisent l&apos;amour, les opportunités et les grands tournants de votre parcours.</p></div>
      </div>


      {/* Styles locaux — keyframes pour l'animation de pulsation du CTA */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0; }
          50% { opacity: 1; }
        }
      `}</style>
    </section>
  );
}
