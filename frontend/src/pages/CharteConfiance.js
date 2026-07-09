import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Shield, Compass, BookOpen, Sparkles, Eye, Heart, ArrowLeft } from 'lucide-react';
import SEO from '@/components/SEO';

const CharteConfiance = () => {
  const navigate = useNavigate();

  return (
    <div className="relative z-10" data-testid="charte-confiance">
      <SEO path="/charte-de-confiance" />

      {/* Hero */}
      <section className="pt-28 pb-16 px-6 md:px-8">
        <div className="max-w-2xl mx-auto">
          <button onClick={() => navigate(-1)} className="link-editorial text-xs mb-10" data-testid="back-btn">
            <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Retour
          </button>
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ border: '1px solid var(--pa-divider)', background: 'rgba(184,150,31,0.05)' }}>
              <Shield className="w-5 h-5" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.5} />
            </div>
            <p className="text-xs tracking-widest uppercase" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>
              Notre cadre
            </p>
          </div>
          <h1 className="text-4xl sm:text-5xl md:text-6xl mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
            Un cadre clair.<br />
            <span style={{ color: 'var(--pa-accent)', fontStyle: 'italic' }}>Une approche responsable.</span>
          </h1>
        </div>
      </section>

      {/* Philosophie */}
      <section className="px-6 md:px-8 pb-14" data-testid="section-philosophie">
        <div className="max-w-2xl mx-auto">
          <div className="w-10 h-px mb-10" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />
          <div className="flex items-start gap-4 mb-6">
            <Compass className="w-5 h-5 flex-shrink-0 mt-1" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.5} />
            <p className="text-xs tracking-widest uppercase" style={{ color: 'var(--pa-accent)', letterSpacing: '0.15em' }}>Philosophie</p>
          </div>
          <p className="text-base md:text-lg leading-relaxed mb-4" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
            Plume Astrale ne predit pas votre avenir, elle eclaire des dynamiques.
          </p>
          <p className="text-base leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
            Les calculs sont precis, l'interpretation est structuree. La decision vous appartient toujours.
          </p>
        </div>
      </section>

      {/* Services */}
      <section className="px-6 md:px-8 pb-14" data-testid="section-services">
        <div className="max-w-2xl mx-auto">
          <div className="w-10 h-px mb-10" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />
          <div className="flex items-start gap-4 mb-8">
            <BookOpen className="w-5 h-5 flex-shrink-0 mt-1" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.5} />
            <p className="text-xs tracking-widest uppercase" style={{ color: 'var(--pa-accent)', letterSpacing: '0.15em' }}>Services</p>
          </div>

          <div className="space-y-8">
            {/* Reponse immediate */}
            <div className="card-editorial p-6" data-testid="service-tirage">
              <div className="flex items-center gap-3 mb-3">
                <Sparkles className="w-4 h-4" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.5} />
                <h3 className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 400, color: 'var(--pa-heading)' }}>
                  Reponse immediate
                </h3>
              </div>
              <p className="text-xs tracking-widest uppercase mb-3" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>
                Tirage Oui / Non
              </p>
              <p className="text-sm leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>
                Trois tirages gratuits pour commencer. Une reponse n'est jamais un verdict, c'est un symbole a explorer.
              </p>
            </div>

            {/* Comprehension approfondie */}
            <div className="card-editorial p-6" data-testid="service-comprehension">
              <div className="flex items-center gap-3 mb-3">
                <Eye className="w-4 h-4" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.5} />
                <h3 className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 400, color: 'var(--pa-heading)' }}>
                  Comprehension approfondie
                </h3>
              </div>
              <p className="text-sm leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>
                Analyse du theme natal et des transits : tensions, cycles, axes d'evolution. Il s'agit de relier les elements, pas de predire.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Methode */}
      <section className="px-6 md:px-8 pb-14" data-testid="section-methode">
        <div className="max-w-2xl mx-auto">
          <div className="w-10 h-px mb-10" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />
          <div className="flex items-start gap-4 mb-8">
            <Shield className="w-5 h-5 flex-shrink-0 mt-1" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.5} />
            <p className="text-xs tracking-widest uppercase" style={{ color: 'var(--pa-accent)', letterSpacing: '0.15em' }}>Methode</p>
          </div>
          <div className="space-y-4">
            {[
              'Calculs astrologiques professionnels',
              'Lecture symbolique experte',
              'Restitution claire et structuree',
              'Chaque lecture est personnalis\u00e9e',
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: 'var(--pa-accent)' }} />
                <span className="text-sm" style={{ color: 'var(--pa-body)' }}>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Offres Premium */}
      <section className="px-6 md:px-8 pb-14" data-testid="section-offres">
        <div className="max-w-2xl mx-auto">
          <div className="w-10 h-px mb-10" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />
          <div className="flex items-start gap-4 mb-8">
            <Heart className="w-5 h-5 flex-shrink-0 mt-1" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.5} />
            <p className="text-xs tracking-widest uppercase" style={{ color: 'var(--pa-accent)', letterSpacing: '0.15em' }}>Offres Premium</p>
          </div>
          <div className="space-y-4">
            {[
              { num: '01', title: 'Lecture synthese' },
              { num: '02', title: 'Cartographie annuelle' },
              { num: '03', title: 'Suivi mensuel' },
            ].map((offer) => (
              <div key={offer.num} className="flex items-baseline gap-4 py-3" style={{ borderBottom: '1px solid var(--pa-divider)' }}>
                <span className="text-xs tracking-widest" style={{ color: 'var(--pa-accent)', letterSpacing: '0.1em' }}>{offer.num}</span>
                <span className="text-base" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>{offer.title}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Posture */}
      <section className="px-6 md:px-8 pb-14" data-testid="section-posture">
        <div className="max-w-2xl mx-auto">
          <div className="w-10 h-px mb-10" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />
          <div className="card-editorial p-8 text-center" style={{ background: 'rgba(184,150,31,0.04)', borderColor: 'rgba(184,150,31,0.15)' }}>
            <Shield className="w-6 h-6 mx-auto mb-4" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.5} />
            <h3 className="text-xl md:text-2xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
              Une guidance symbolique, pas une verite absolue.
            </h3>
            <p className="text-sm leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>
              Nos lectures sont des reperes, pas des directives. Elles eclairent des dynamiques pour vous aider a naviguer avec plus de conscience.
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 md:px-8 pb-20" data-testid="section-cta">
        <div className="max-w-md mx-auto text-center">
          <button onClick={() => navigate('/tarot-oui-non')} className="btn-editorial-filled text-xs px-10 py-3" data-testid="cta-recevoir-reponse">
            Recevoir une reponse <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
          </button>
          <p className="text-xs mt-4" style={{ color: 'var(--pa-muted)' }}>
            3 tirages gratuits par jour — Aucun engagement
          </p>
        </div>
      </section>
    </div>
  );
};

export default CharteConfiance;
