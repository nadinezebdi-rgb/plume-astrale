import React from 'react';
import { HelpCircle, Layers, TrendingUp, Sparkles, Compass, Star } from 'lucide-react';

/**
 * ServicesEquivalence — grille GaryVee "ce que valent tes credits"
 *   • Icones + prix en credits + equivalent en questions
 *   • Ancre visuellement le rapport 1 question = 10 credits
 *   • A poser sur /acheter-credits (et eventuellement sur la home)
 */
const SERVICES = [
  {
    icon: HelpCircle,
    name: 'Tarot Oui / Non',
    cost: 5,
    equiv: '½ question',
    desc: 'La reponse flash a une question binaire.',
    color: '#8B92B8',
  },
  {
    icon: Sparkles,
    name: 'Chat avec Solena',
    cost: 10,
    equiv: '1 question',
    desc: 'Une reponse personnalisee sur mesure.',
    color: '#E2BF65',
    highlight: true,
  },
  {
    icon: Layers,
    name: 'Tarot approfondi',
    cost: 30,
    equiv: '3 questions',
    desc: 'Tirage en croix : passe, present, blocage, futur.',
    color: '#B89CDB',
  },
  {
    icon: Compass,
    name: 'Numerologie complete',
    cost: 30,
    equiv: '3 questions',
    desc: 'Annee personnelle & chemin de vie.',
    color: '#B89CDB',
  },
  {
    icon: TrendingUp,
    name: 'Lecture cycle actuel',
    cost: 40,
    equiv: '4 questions',
    desc: 'Transits, Mercure retrograde, eclipses.',
    color: '#F4A97A',
  },
  {
    icon: Star,
    name: 'Theme Natal complet',
    cost: 60,
    equiv: '6 questions',
    desc: 'Ta carte d\'identite astrale — le rapport premium.',
    color: '#E7C97A',
    premium: true,
  },
];

export default function ServicesEquivalence() {
  return (
    <section
      className="w-full"
      data-testid="services-equivalence"
      style={{
        background: 'linear-gradient(160deg, rgba(226,191,101,0.04) 0%, rgba(20,15,40,0.35) 100%)',
        borderRadius: 24,
        padding: '32px 24px',
        border: '1px solid rgba(226,191,101,0.18)',
        backdropFilter: 'blur(10px)',
      }}
    >
      {/* Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-4"
          style={{ background: 'rgba(226,191,101,0.10)', border: '1px solid rgba(226,191,101,0.30)' }}>
          <Sparkles style={{ width: 11, height: 11, color: '#E2BF65' }} strokeWidth={1.5} />
          <span className="text-[10px] uppercase" style={{ color: '#E2BF65', letterSpacing: '0.3em' }}>
            Ce que valent tes credits
          </span>
        </div>
        <h3 style={{
          fontFamily: 'Cormorant Garamond, serif',
          fontWeight: 300,
          fontSize: 'clamp(1.4rem, 3vw, 2rem)',
          lineHeight: 1.15,
          color: '#F5EEE0',
          marginBottom: 8,
        }}>
          1 question = <em style={{ color: '#E2BF65', fontStyle: 'italic' }}>10 credits</em>
        </h3>
        <p className="text-sm max-w-md mx-auto" style={{
          fontFamily: 'Cormorant Garamond, serif',
          fontStyle: 'italic',
          color: 'rgba(244,232,210,0.6)',
        }}>
          Chaque service est un multiple simple, calibre pour te donner l&apos;equivalent en questions.
        </p>
      </div>

      {/* Grille des services */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {SERVICES.map((s) => {
          const Icon = s.icon;
          return (
            <div
              key={s.name}
              className="rounded-2xl p-4 flex items-start gap-3 transition-all hover:scale-[1.02]"
              style={{
                background: s.highlight
                  ? 'linear-gradient(135deg, rgba(226,191,101,0.15), rgba(226,191,101,0.05))'
                  : s.premium
                    ? 'linear-gradient(135deg, rgba(231,201,122,0.10), rgba(20,15,40,0.35))'
                    : 'rgba(255,255,255,0.02)',
                border: s.highlight || s.premium
                  ? `1px solid ${s.color}55`
                  : '1px solid rgba(226,191,101,0.15)',
                minHeight: 110,
              }}
              data-testid={`service-eq-${s.name.replace(/\s+/g, '-').toLowerCase()}`}
            >
              {/* Icon + credits chip */}
              <div className="flex flex-col items-center gap-1 flex-shrink-0" style={{ width: 52 }}>
                <div style={{
                  width: 40, height: 40, borderRadius: '50%',
                  background: `${s.color}18`,
                  border: `1px solid ${s.color}55`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <Icon style={{ width: 18, height: 18, color: s.color }} strokeWidth={1.5} />
                </div>
                <div style={{
                  fontSize: 11,
                  fontFamily: 'Inter, sans-serif',
                  color: s.color,
                  fontWeight: 700,
                  letterSpacing: '0.05em',
                }}>
                  {s.cost} cr
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span style={{
                    color: '#F5EEE0',
                    fontFamily: 'Cormorant Garamond, serif',
                    fontSize: 15,
                    fontWeight: 500,
                    lineHeight: 1.2,
                  }}>
                    {s.name}
                  </span>
                </div>
                <div style={{
                  fontSize: 10,
                  color: s.color,
                  fontFamily: 'Inter, sans-serif',
                  textTransform: 'uppercase',
                  letterSpacing: '0.18em',
                  fontWeight: 500,
                  marginBottom: 6,
                  opacity: 0.9,
                }}>
                  = {s.equiv}
                </div>
                <div style={{
                  fontSize: 11,
                  color: 'rgba(244,232,210,0.6)',
                  fontFamily: 'Inter, sans-serif',
                  lineHeight: 1.4,
                }}>
                  {s.desc}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footnote — Coup de genie GaryVee */}
      <div className="text-center mt-6 pt-5" style={{ borderTop: '1px dashed rgba(226,191,101,0.20)' }}>
        <p className="text-xs max-w-lg mx-auto" style={{
          color: 'rgba(244,232,210,0.55)',
          fontFamily: 'Cormorant Garamond, serif',
          fontStyle: 'italic',
          fontSize: 13,
          lineHeight: 1.6,
        }}>
          Astuce&nbsp;: le pack <strong style={{ color: '#E2BF65' }}>Nébuleuse à 17,99&nbsp;€</strong> donne <strong style={{ color: '#E2BF65' }}>80 crédits</strong> — de quoi t&apos;offrir un <strong style={{ color: '#E2BF65' }}>Thème Natal complet</strong> et 2 questions à Plume.
        </p>
      </div>
    </section>
  );
}
