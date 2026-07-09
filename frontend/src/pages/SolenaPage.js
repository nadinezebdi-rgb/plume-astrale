import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Heart, Star, ArrowRight, Moon, CheckCircle2 } from 'lucide-react';
import SEO from '@/components/SEO';
import { SOLENA } from '@/lib/solena';

/**
 * SolenaPage — page bio SEO de Solena, ambassadrice de Plume Astrale.
 * Objectif : crédibilité + storytelling + conversion vers /rencontres-astrales.
 */
export default function SolenaPage() {
  return (
    <div style={{
      background: 'radial-gradient(ellipse at top, #1a1147 0%, #0C0918 50%, #060314 100%)',
      color: '#F4E8D2',
      minHeight: '100vh',
      position: 'relative',
      overflow: 'hidden',
    }}>
      <SEO
        title="Solena — Astrologue & Guide Spirituelle · Plume Astrale"
        description="Rencontrez Solena, astrologue et tarologue depuis 15 ans, ambassadrice de Plume Astrale. Ma méthode holistique, mes spécialités et ma mission."
        path="/solena"
      />

      {/* Portrait Solena en background subtil (fini les vidéos) */}
      <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', zIndex: 0 }} aria-hidden="true">
        <img
          src={SOLENA.portrait}
          alt=""
          style={{
            position: 'absolute', top: 0, left: 0,
            width: '100%', height: '100%', objectFit: 'cover',
            opacity: 0.18, filter: 'blur(3px) saturate(1.1)',
          }}
        />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(180deg, rgba(17,22,37,0.80) 0%, rgba(17,22,37,0.95) 60%, #111625 100%)',
        }} />
      </div>

      <div className="relative max-w-6xl mx-auto px-4 md:px-8 py-16 md:py-24" style={{ zIndex: 2 }}>

        {/* ═════ HERO ═════ */}
        <div className="grid md:grid-cols-2 gap-12 items-center mb-24" data-testid="solena-hero-section">
          <div className="order-2 md:order-1">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full mb-6"
              style={{ background: 'rgba(184,150,31,0.10)', border: '1px solid rgba(184,150,31,0.35)' }}>
              <Sparkles className="w-3 h-3" style={{ color: '#B8961F' }} strokeWidth={1.5} />
              <span className="text-[10px] uppercase" style={{ color: '#B8961F', letterSpacing: '0.25em' }}>
                {SOLENA.tagline}
              </span>
            </div>

            <h1 className="text-5xl md:text-7xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, lineHeight: 1 }}>
              Je suis <em style={{ color: '#B8961F', fontStyle: 'italic' }}>{SOLENA.name}</em>.
            </h1>

            <p className="text-lg md:text-xl opacity-85 leading-relaxed mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 400 }}>
              {SOLENA.bio_short}
            </p>

            <div className="flex flex-wrap gap-3">
              <Link to="/rencontres-astrales"
                className="px-6 py-3 rounded-full text-xs uppercase flex items-center gap-2 transition-all hover:scale-[1.02]"
                style={{
                  background: 'linear-gradient(135deg, #B8961F, #E8C766)',
                  color: '#0C0918',
                  letterSpacing: '0.2em', fontWeight: 600,
                  boxShadow: '0 20px 60px rgba(184,150,31,0.25)',
                }}
                data-testid="solena-cta-rencontres">
                <Heart className="w-3.5 h-3.5" /> Consulter Solena
              </Link>
              <Link to="/consultation"
                className="px-6 py-3 rounded-full text-xs uppercase flex items-center gap-2 transition-all"
                style={{ border: '1px solid rgba(184,150,31,0.4)', color: '#B8961F', letterSpacing: '0.2em' }}
                data-testid="solena-cta-chat">
                Chatter avec Plume
              </Link>
            </div>
          </div>

          <div className="order-1 md:order-2 flex justify-center">
            <div className="relative">
              <div style={{
                position: 'absolute', inset: '-10%',
                background: 'radial-gradient(circle, rgba(184,150,31,0.30), transparent 70%)',
                filter: 'blur(30px)',
              }} />
              <img src={SOLENA.portrait} alt="Portrait de Solena — astrologue"
                loading="eager"
                style={{
                  position: 'relative',
                  width: '100%', maxWidth: 420, aspectRatio: '1/1',
                  objectFit: 'cover', objectPosition: 'center 20%',
                  borderRadius: '50%',
                  border: '3px solid rgba(184,150,31,0.55)',
                  boxShadow: '0 40px 100px rgba(184,150,31,0.30), 0 0 60px rgba(184,150,31,0.20)',
                }}
                data-testid="solena-portrait" />
            </div>
          </div>
        </div>

        {/* ═════ MISSION / BIO LONGUE ═════ */}
        <div className="max-w-3xl mx-auto mb-24" data-testid="solena-bio-section">
          <div className="text-center mb-10">
            <div className="text-[10px] uppercase mb-3" style={{ color: '#B8961F', letterSpacing: '0.3em' }}>
              Ma mission
            </div>
            <h2 className="text-4xl md:text-5xl" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}>
              Une <em style={{ color: '#B8961F', fontStyle: 'italic' }}>conversation intime</em>
              <br />avec ton ciel de naissance.
            </h2>
          </div>

          <div className="space-y-6 text-base md:text-lg leading-relaxed" style={{ color: '#F4E8D2', opacity: 0.90 }}>
            {SOLENA.bio_long.map((p, i) => (
              <p key={i} style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 400 }}>{p}</p>
            ))}
          </div>
        </div>

        {/* ═════ SPÉCIALITÉS ═════ */}
        <div className="mb-24" data-testid="solena-specialities">
          <div className="text-center mb-10">
            <div className="text-[10px] uppercase mb-3" style={{ color: '#B8961F', letterSpacing: '0.3em' }}>
              Mes spécialités
            </div>
            <h2 className="text-3xl md:text-4xl" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}>
              Six voies pour <em style={{ color: '#B8961F', fontStyle: 'italic' }}>t&apos;éclairer</em>
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
            {SOLENA.specialities.map((s, i) => (
              <div key={i}
                className="rounded-2xl p-5 flex items-start gap-3 transition-all hover:scale-[1.02]"
                style={{
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid rgba(184,150,31,0.20)',
                  backdropFilter: 'blur(12px)',
                }}
                data-testid={`speciality-${i}`}>
                <div className="flex-shrink-0 mt-0.5">
                  <CheckCircle2 className="w-5 h-5" style={{ color: '#B8961F' }} strokeWidth={1.5} />
                </div>
                <div className="text-sm md:text-base" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 400 }}>
                  {s}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ═════ CTA FINAL ═════ */}
        <div className="rounded-3xl p-8 md:p-12 max-w-4xl mx-auto text-center relative overflow-hidden"
          style={{
            background: 'linear-gradient(135deg, #0C0918, #1a1147)',
            border: '2px solid #B8961F',
            boxShadow: '0 40px 120px rgba(184,150,31,0.25)',
          }} data-testid="solena-final-cta">
          <div style={{
            position: 'absolute', top: -80, right: -80, width: 300, height: 300,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(184,150,31,0.25), transparent)',
          }} />

          <div className="relative">
            <Moon className="w-10 h-10 mx-auto mb-4" style={{ color: '#B8961F' }} strokeWidth={1.2} />
            <h2 className="text-3xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}>
              Prête à découvrir ce que <em style={{ color: '#B8961F', fontStyle: 'italic' }}>tes étoiles</em> murmurent ?
            </h2>
            <p className="text-base opacity-80 max-w-xl mx-auto mb-8 leading-relaxed">
              Une révélation gratuite t&apos;attend : le portrait de ton âme sœur et tes prochaines fenêtres de rencontre.
            </p>
            <Link to="/rencontres-astrales"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-full text-sm uppercase transition-all hover:scale-[1.02]"
              style={{
                background: 'linear-gradient(135deg, #B8961F, #E8C766)',
                color: '#0C0918',
                letterSpacing: '0.2em', fontWeight: 700,
                boxShadow: '0 20px 60px rgba(184,150,31,0.35)',
              }}
              data-testid="solena-final-cta-btn">
              <Heart className="w-4 h-4" /> Commencer maintenant · Gratuit
              <ArrowRight className="w-4 h-4" />
            </Link>
            <p className="text-[10px] mt-4 opacity-50" style={{ letterSpacing: '0.15em' }}>
              Aucune carte bancaire · Résultat instantané
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}
