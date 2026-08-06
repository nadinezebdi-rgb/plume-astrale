import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, ShieldCheck, Star } from 'lucide-react';
import SEO from '@/components/SEO';
import { useAuth } from '@/context/AuthContext';
import PdfBookOpen from '@/components/PdfBookOpen';
import ApercuButton from '@/components/ApercuButton';
import TestimonialsWidget, { TESTIMONIALS_KABBALE } from '@/components/TestimonialsWidget';

/**
 * ThemeNatalLuxe — landing dédiée au Thème Natal luxe (49 pages, voix Soléna).
 *
 * Positionnement : produit d'entrée premium. Prix affiché 17,99€ offre bienvenue
 * (barré 29€) → convertit vers /mon-compte (utilisateur connecté) ou /inscription.
 *
 * Hook Gary Vee : "Regarde ton exemplaire s'ouvrir" avant même de payer.
 */

const ThemeNatalLuxe = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [ctaHover, setCtaHover] = useState(false);

  const handleCta = () => {
    if (isAuthenticated) {
      navigate('/mon-compte?generate=natal');
    } else {
      navigate('/inscription?next=/mon-compte');
    }
  };

  return (
    <div
      className="min-h-screen relative"
      style={{ padding: '110px 20px 140px' }}
      data-testid="theme-natal-luxe-page"
    >
      <SEO
        path="/theme-natal-luxe"
        title="Ton Thème Natal Luxe · 49 pages écrites par Soléna · Plume Astrale"
        description="Un PDF premium de 49 pages où 11 planètes racontent qui tu es vraiment. Écrit par Soléna à partir de 73 dimensions astrologiques. Offre bienvenue : 17,99€ au lieu de 29€."
      />

      <div className="max-w-3xl mx-auto">
        {/* ─── HERO ────────────────────────────────────────────── */}
        <div className="text-center mb-14">
          <p
            className="text-[10px] uppercase mb-4"
            style={{
              color: '#D4AF37',
              letterSpacing: '0.4em',
              fontFamily: 'Cinzel, serif',
            }}
            data-testid="natal-luxe-eyebrow"
          >
            ✦ Édition Plume Astrale ✦
          </p>
          <h1
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontWeight: 300,
              fontSize: 'clamp(38px, 5.5vw, 62px)',
              color: '#F5EEE0',
              lineHeight: 1.05,
              marginBottom: 20,
            }}
          >
            Ton Thème Natal —
            <br />
            <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>
              écrit pour toi, pas pour ton signe.
            </em>
          </h1>
          <p
            className="max-w-xl mx-auto text-base"
            style={{
              color: 'rgba(227,215,255,0.75)',
              fontFamily: 'Cormorant Garamond, serif',
              lineHeight: 1.6,
              fontStyle: 'italic',
            }}
          >
            49 pages où <span style={{ color: '#F5EEE0' }}>11 planètes</span> racontent
            qui tu es vraiment. PDF premium à télécharger, signé Soléna.
            Écrit à partir de <span style={{ color: '#F5EEE0' }}>73 dimensions astrologiques</span>
            {' '}analysées spécifiquement pour toi.
          </p>
        </div>

        {/* ─── LIVRE 3D ANIMÉ ─────────────────────────────────── */}
        <PdfBookOpen testId="natal-luxe-book-open" theme="natal" />

        {/* ─── CE QUE TU RECEVRAS ─────────────────────────────── */}
        <div className="mb-14" data-testid="natal-luxe-includes">
          <h2
            className="text-center mb-8"
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontWeight: 300,
              fontSize: 'clamp(24px, 3vw, 32px)',
              color: '#F5EEE0',
            }}
          >
            Ce que ta lecture contient
          </h2>
          <div className="grid md:grid-cols-2 gap-5">
            {[
              { title: 'Ton Soleil', text: 'Ce qui t\'anime au plus profond, ta lumière, ta trajectoire de devenir.' },
              { title: 'Ta Lune', text: 'Tes émotions cachées, tes réflexes de l\'enfance, ta façon de te consoler.' },
              { title: 'Ton Ascendant', text: 'Le masque que ton âme a choisi — ce que les autres perçoivent en premier.' },
              { title: 'Mercure, Vénus, Mars', text: 'Pensée, amour, action — les trois moteurs de ta vie quotidienne.' },
              { title: 'Jupiter, Saturne', text: 'Ta zone d\'expansion et ta discipline intérieure — les deux forces qui te structurent.' },
              { title: 'Uranus, Neptune, Pluton', text: 'Rupture, rêve, transformation — les trois planètes des grandes mutations d\'âme.' },
              { title: 'La danse des aspects', text: 'Ce que tes planètes se disent entre elles — la conversation secrète de ton chart.' },
              { title: 'Signature Soléna', text: 'Chaque paragraphe écrit spécifiquement pour toi, jamais recopié d\'un signe.' },
            ].map((item, i) => (
              <div
                key={i}
                className="plume-glass p-5"
                style={{ background: 'rgba(26,18,48,0.42)', borderColor: 'rgba(212,175,55,0.22)' }}
                data-testid={`natal-include-${i}`}
              >
                <div
                  className="text-[10px] mb-2"
                  style={{
                    color: '#D4AF37',
                    letterSpacing: '0.3em',
                    fontFamily: 'Cinzel, serif',
                    textTransform: 'uppercase',
                  }}
                >
                  ✦ {item.title}
                </div>
                <p
                  className="text-sm"
                  style={{
                    color: 'rgba(245,238,224,0.82)',
                    fontFamily: 'Cormorant Garamond, serif',
                    lineHeight: 1.55,
                  }}
                >
                  {item.text}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* ─── TÉMOIGNAGES ────────────────────────────────────── */}
        <div className="mb-14">
          <TestimonialsWidget
            testimonials={TESTIMONIALS_KABBALE}
            testId="natal-luxe-testimonials"
          />
        </div>

        {/* ─── PRICING + CTA ──────────────────────────────────── */}
        <div
          className="mx-auto text-center p-8 md:p-12 relative overflow-hidden"
          style={{
            maxWidth: 620,
            background: 'linear-gradient(160deg, rgba(26,18,48,0.85) 0%, rgba(14,10,30,0.92) 100%)',
            border: '1px solid rgba(212,175,55,0.5)',
            borderRadius: 12,
            boxShadow: '0 40px 80px -20px rgba(0,0,0,0.5)',
          }}
          data-testid="natal-luxe-pricing"
        >
          {/* Badge cadeau bienvenue */}
          <div
            className="inline-block px-4 py-1.5 mb-6"
            style={{
              background: 'linear-gradient(90deg, #8a6d1a, #D4AF37, #8a6d1a)',
              color: '#0E0A1E',
              fontFamily: 'Cinzel, serif',
              fontSize: 10,
              letterSpacing: '0.32em',
              borderRadius: 999,
              fontWeight: 600,
              textTransform: 'uppercase',
              boxShadow: '0 4px 16px rgba(212,175,55,0.35)',
            }}
            data-testid="natal-luxe-welcome-badge"
          >
            ✦ Cadeau bienvenue ·  20 crédits offerts  ·  ✦
          </div>

          {/* Grand chiffre "20" style Cartier */}
          <div className="mb-3 relative" data-testid="natal-luxe-credits">
            <span
              style={{
                fontFamily: 'Cormorant Garamond, serif',
                fontWeight: 300,
                fontSize: 'clamp(78px, 12vw, 128px)',
                color: '#F5EEE0',
                lineHeight: 0.95,
                textShadow: '0 4px 40px rgba(212,175,55,0.35)',
                display: 'inline-block',
                verticalAlign: 'middle',
              }}
            >
              20
            </span>
            <span
              className="ml-3"
              style={{
                fontFamily: 'Cinzel, serif',
                fontWeight: 400,
                fontSize: 'clamp(18px, 2.5vw, 24px)',
                color: '#D4AF37',
                letterSpacing: '0.22em',
                textTransform: 'uppercase',
                verticalAlign: 'middle',
              }}
            >
              crédits
            </span>
          </div>

          <p
            className="mb-8"
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: 17,
              fontStyle: 'italic',
              color: 'rgba(245,238,224,0.85)',
              lineHeight: 1.5,
              maxWidth: 440,
              margin: '0 auto 32px',
            }}
          >
            Offerts <span style={{ color: '#D4AF37', fontWeight: 500, fontStyle: 'normal' }}>automatiquement</span> à la création de ton compte.
            Ton Thème Natal Ultra coûte <span style={{ color: '#F5EEE0' }}>80 crédits</span> — accessible dès le premier pack <span style={{ color: '#F5EEE0' }}>Nébuleuse à 17,99€</span> qui t&apos;en donne <span style={{ color: '#F5EEE0' }}>80</span>. Aucun code à saisir.
          </p>

          <button
            onClick={handleCta}
            onMouseEnter={() => setCtaHover(true)}
            onMouseLeave={() => setCtaHover(false)}
            data-testid="natal-luxe-cta"
            className="w-full max-w-md mx-auto flex items-center justify-center gap-3 py-4 px-8 mb-4 transition-all"
            style={{
              background: ctaHover
                ? 'linear-gradient(90deg, #D4AF37 0%, #f5e19a 50%, #D4AF37 100%)'
                : 'linear-gradient(90deg, #8a6d1a 0%, #D4AF37 50%, #8a6d1a 100%)',
              color: '#0E0A1E',
              border: 'none',
              borderRadius: 10,
              fontFamily: 'Cinzel, serif',
              fontSize: 13,
              letterSpacing: '0.28em',
              fontWeight: 600,
              textTransform: 'uppercase',
              cursor: 'pointer',
              boxShadow: ctaHover
                ? '0 20px 40px -10px rgba(212,175,55,0.6)'
                : '0 10px 30px -8px rgba(212,175,55,0.35)',
              transform: ctaHover ? 'translateY(-2px)' : 'translateY(0)',
            }}
          >
            <Sparkles className="w-4 h-4" strokeWidth={1.5} />
            {isAuthenticated ? 'Créer ma lecture astrale' : 'Recevoir mes 20 crédits'}
            <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
          </button>

          <div className="mt-4">
            <ApercuButton bookKey="natal" variant="ghost" />
          </div>

          <div
            className="flex items-center justify-center gap-2 mt-6 text-[11px]"
            style={{
              color: 'rgba(227,215,255,0.55)',
              fontFamily: 'Cinzel, serif',
              letterSpacing: '0.2em',
            }}
          >
            <ShieldCheck className="w-3 h-3" strokeWidth={1.5} />
            Inscription gratuite · Sans carte bancaire · Sans engagement
          </div>

          <div
            className="flex items-center justify-center gap-1 mt-3"
            data-testid="natal-luxe-stars"
          >
            {[1,2,3,4,5].map(i => (
              <Star key={i} className="w-3.5 h-3.5" fill="#D4AF37" strokeWidth={0} />
            ))}
            <span
              className="ml-2 text-xs"
              style={{
                color: 'rgba(245,238,224,0.65)',
                fontFamily: 'Cormorant Garamond, serif',
                fontStyle: 'italic',
              }}
            >
              4,9/5 sur 217 lectrices Plume Astrale
            </span>
          </div>
        </div>

        {/* Retour discret */}
        <div className="text-center mt-10">
          <Link
            to="/"
            className="text-xs"
            style={{
              color: 'rgba(212,175,55,0.55)',
              fontFamily: 'Cinzel, serif',
              letterSpacing: '0.24em',
              textTransform: 'uppercase',
            }}
          >
            ← Retour à l&apos;accueil
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ThemeNatalLuxe;
