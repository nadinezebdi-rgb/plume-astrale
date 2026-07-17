import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Heart, Flame, Waves, Wind, Mountain, ArrowRight, Sparkles } from 'lucide-react';
import SEO from '../components/SEO';
import { SIGN_LIST } from '../lib/astrosexo-data';
import { event as trackEvent } from '../lib/analytics';

const ELEMENT_ICONS = { Feu: Flame, Terre: Mountain, Air: Wind, Eau: Waves };
const ELEMENT_COLORS = {
  Feu: '#E67E5C', Terre: '#A38B5F', Air: '#8DB4C9', Eau: '#7C93C8',
};

export default function AstroSexo() {
  const [selected, setSelected] = useState(null);

  const handleSelect = (sign) => {
    setSelected(sign);
    trackEvent('astrosexo_sign_selected', { sign: sign.sign });
    setTimeout(() => {
      document.getElementById('astrosexo-reveal')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  };

  return (
    <div className="min-h-screen pt-24 pb-20 px-4" data-testid="astrosexo-page">
      <SEO path="/astrosexo" />
      <div className="max-w-4xl mx-auto">

        {/* Hero */}
        <div className="text-center mb-14">
          <p className="text-[10px] uppercase tracking-[0.3em] mb-3" style={{ color: '#D4AF37', fontFamily: 'Cinzel, serif' }}>
            L&apos;alchimie des signes
          </p>
          <h1 className="text-4xl sm:text-5xl mb-5" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 300, lineHeight: 1.05 }}>
            <em style={{ fontStyle: 'italic', color: '#D4AF37' }}>AstroSexo</em>
          </h1>
          <p className="text-base max-w-xl mx-auto mb-3" style={{ color: 'rgba(184,176,200,0.85)', lineHeight: 1.65 }}>
            Découvrez votre profil sensuel astrologique et les 3 signes qui vibrent le plus avec vous.
          </p>
          <p className="text-xs italic max-w-lg mx-auto" style={{ color: 'rgba(212,175,55,0.75)', lineHeight: 1.65 }}>
            L&apos;astrologie ne remplace pas l&apos;alchimie vécue — elle l&apos;éclaire. Choisissez votre signe pour lire ce que les étoiles murmurent sur vos élans intimes.
          </p>
        </div>

        {/* Grid des 12 signes */}
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2 mb-14" data-testid="signs-grid">
          {SIGN_LIST.map((s) => {
            const Icon = ELEMENT_ICONS[s.element] || Heart;
            const isActive = selected?.id === s.id;
            return (
              <button
                key={s.id}
                onClick={() => handleSelect(s)}
                className="flex flex-col items-center gap-1 p-3 rounded-xl transition-all"
                style={{
                  background: isActive ? 'rgba(212,175,55,0.14)' : 'rgba(255,255,255,0.025)',
                  border: `1px solid ${isActive ? '#D4AF37' : 'rgba(212,175,55,0.15)'}`,
                  color: isActive ? '#F5EEE0' : 'rgba(240,230,211,0.75)',
                  transform: isActive ? 'scale(1.05)' : 'scale(1)',
                }}
                data-testid={`sign-${s.id}`}
              >
                <Icon className="w-4 h-4" strokeWidth={1.5} style={{ color: ELEMENT_COLORS[s.element] }} />
                <span className="text-xs" style={{ fontFamily: 'Cormorant Garamond, serif' }}>{s.sign}</span>
              </button>
            );
          })}
        </div>

        {/* Reveal */}
        {selected && (
          <section id="astrosexo-reveal" className="rounded-2xl p-6 sm:p-8 mb-10" style={{
            background: 'linear-gradient(135deg, rgba(212,175,55,0.08), rgba(167,139,250,0.06))',
            border: '1px solid rgba(212,175,55,0.3)',
          }} data-testid="astrosexo-reveal">
            <div className="flex items-baseline justify-between mb-4 pb-4" style={{ borderBottom: '1px solid rgba(212,175,55,0.2)' }}>
              <div>
                <p className="text-[10px] uppercase tracking-widest" style={{ color: '#D4AF37', letterSpacing: '0.14em', fontFamily: 'Cinzel, serif' }}>Le profil sensuel du</p>
                <h2 className="text-3xl mt-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 300 }}>
                  <em style={{ color: '#D4AF37' }}>{selected.sign}</em>
                </h2>
              </div>
              <p className="text-xs" style={{ color: 'rgba(184,176,200,0.6)' }}>{selected.dates}</p>
            </div>

            <p className="text-sm mb-6" style={{ color: 'rgba(240,230,211,0.9)', lineHeight: 1.75, fontFamily: 'Cormorant Garamond, serif', fontSize: 15 }}>
              {selected.profile}
            </p>

            <p className="text-[10px] uppercase tracking-widest mb-4" style={{ color: '#D4AF37', letterSpacing: '0.14em', fontFamily: 'Cinzel, serif' }}>Vos 3 signes les plus compatibles</p>
            <div className="grid sm:grid-cols-3 gap-3 mb-6">
              {selected.ideal.map((match, i) => (
                <div key={i} className="rounded-xl p-4" style={{
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid rgba(212,175,55,0.2)',
                }} data-testid={`match-${i}`}>
                  <h3 className="text-base mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#E8C766' }}>
                    ✦ {match.sign}
                  </h3>
                  <p className="text-xs" style={{ color: 'rgba(184,176,200,0.85)', lineHeight: 1.6 }}>{match.reason}</p>
                </div>
              ))}
            </div>

            <p className="text-[11px] italic mt-2" style={{ color: 'rgba(184,176,200,0.6)' }}>
              ✦ L&apos;analyse par signe solaire est une porte d&apos;entrée. Pour une lecture véritablement précise, votre thème natal complet et celui de votre partenaire révèlent bien plus.
            </p>
          </section>
        )}

        {/* CTA vers Astrologie relationnelle */}
        <section className="rounded-2xl p-8 sm:p-10 text-center" style={{
          background: 'linear-gradient(135deg, rgba(17,22,37,0.9), rgba(30,26,51,0.85))',
          border: '1px solid rgba(212,175,55,0.35)',
        }} data-testid="astrosexo-cta">
          <Sparkles className="w-8 h-8 mx-auto mb-4" strokeWidth={1.3} style={{ color: '#D4AF37' }} />
          <h2 className="text-2xl sm:text-3xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 300 }}>
            Envie d&apos;aller au-delà du signe solaire ?
          </h2>
          <p className="text-sm max-w-xl mx-auto mb-6" style={{ color: 'rgba(184,176,200,0.85)', lineHeight: 1.65 }}>
            L&apos;<strong>Astrologie relationnelle</strong> analyse vos deux thèmes natals complets — Vénus, Mars, la 8e maison, les aspects entre vos planètes — pour révéler la véritable géographie de votre lien.
          </p>
          <Link
            to="/synastrie"
            onClick={() => trackEvent('astrosexo_cta_click')}
            className="inline-flex items-center gap-2 px-8 py-3.5 rounded-full transition-all"
            style={{
              background: 'linear-gradient(135deg, #D4AF37, #D4AF37)',
              color: '#111625',
              fontFamily: 'Cinzel, serif', fontSize: 12, letterSpacing: '0.14em', textTransform: 'uppercase', fontWeight: 600,
              boxShadow: '0 6px 24px rgba(212,175,55,0.3)',
            }}
            data-testid="astrosexo-cta-btn"
          >
            Composer notre rapport — 49€ <ArrowRight className="w-4 h-4" />
          </Link>
          <p className="text-[10px] mt-4" style={{ color: 'rgba(184,176,200,0.6)' }}>
            ✦ Extrait gratuit 3 pages disponible
          </p>
        </section>
      </div>
    </div>
  );
}
