import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const SectionDivider = () => <div className="divider-subtle" />;

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen relative" data-testid="homepage">
      <StarField count={90} />

      {/* ─── HERO ─── */}
      <section className="relative z-10 min-h-screen flex flex-col justify-center px-6 md:px-8" data-testid="hero-section">
        <div className="max-w-3xl mx-auto w-full">
          <p
            className="text-xs tracking-widest uppercase mb-16 md:mb-20"
            style={{ color: 'var(--pa-accent)', letterSpacing: '0.25em', opacity: 0.7 }}
          >
            Plume Astrale
          </p>

          <h1
            className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl mb-8 md:mb-10 leading-tight"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
          >
            Lorsque certaines p&eacute;riodes<br className="hidden sm:block" /> deviennent floues,
            <br />
            <span style={{ fontStyle: 'italic', opacity: 0.85 }}>il est possible de les comprendre.</span>
          </h1>

          <p
            className="text-sm md:text-base max-w-xl mb-16 md:mb-20 leading-relaxed"
            style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}
          >
            Un espace de guidance symbolique,
            fond&eacute; sur des calculs astrologiques pr&eacute;cis
            et une interpr&eacute;tation experte.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 sm:gap-6">
            <button
              onClick={() => navigate('/tarot-oui-non')}
              className="btn-editorial"
              data-testid="cta-tarot-entry"
            >
              Recevoir une r&eacute;ponse imm&eacute;diate
            </button>
            <button
              onClick={() => navigate('/formulaire')}
              className="btn-editorial"
              data-testid="cta-astrology-entry"
            >
              Comprendre ma p&eacute;riode actuelle
            </button>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── NOTRE CADRE ─── */}
      <section className="section-editorial relative z-10" data-testid="section-cadre">
        <div className="section-narrow">
          <p className="section-label">Notre cadre</p>
          <h2
            className="text-2xl sm:text-3xl md:text-4xl mb-10 md:mb-14"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}
          >
            Un cadre clair. Une approche responsable.
          </h2>

          <div className="space-y-6 text-sm md:text-base" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
            <p>
              Plume Astrale ne pr&eacute;dit pas votre avenir.
              <br />
              Elle &eacute;claire des dynamiques.
            </p>
            <p>
              Les calculs sont pr&eacute;cis.
              <br />
              L'interpr&eacute;tation est structur&eacute;e.
            </p>
            <p style={{ color: 'var(--pa-heading)', opacity: 0.85 }}>
              La d&eacute;cision vous appartient toujours.
            </p>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── RÉPONSE IMMÉDIATE ─── */}
      <section className="section-editorial relative z-10" data-testid="section-tarot">
        <div className="section-narrow">
          <p className="section-label">R&eacute;ponse imm&eacute;diate</p>
          <h2
            className="text-2xl sm:text-3xl md:text-4xl mb-10 md:mb-14"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}
          >
            Besoin d'un &eacute;clairage rapide ?
          </h2>

          <div className="space-y-6 text-sm md:text-base mb-12 md:mb-16" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
            <p>
              Le tirage Oui / Non ouvre une r&eacute;flexion.
              <br />
              Trois tirages gratuits pour commencer.
            </p>
            <p>
              Une r&eacute;ponse n'est jamais un verdict.
              <br />
              C'est un symbole &agrave; explorer.
            </p>
          </div>

          <button
            onClick={() => navigate('/tarot-oui-non')}
            className="link-editorial group"
            data-testid="cta-tarot"
          >
            Faire un tirage
            <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" strokeWidth={1.5} />
          </button>
        </div>
      </section>

      <SectionDivider />

      {/* ─── COMPRÉHENSION APPROFONDIE ─── */}
      <section className="section-editorial relative z-10" data-testid="section-astrology">
        <div className="section-narrow">
          <p className="section-label">Compr&eacute;hension approfondie</p>
          <h2
            className="text-2xl sm:text-3xl md:text-4xl mb-10 md:mb-14"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}
          >
            Comprendre la p&eacute;riode que vous traversez.
          </h2>

          <div className="space-y-6 text-sm md:text-base" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
            <p>&Agrave; partir de votre th&egrave;me natal et de vos transits :</p>

            <ul className="space-y-3 pl-0">
              {[
                'Les tensions pr\u00e9sentes',
                'Les cycles en cours',
                'Les axes d\'\u00e9volution',
              ].map((item, i) => (
                <li key={i} className="flex items-center gap-4">
                  <span className="w-4 text-center text-xs" style={{ color: 'var(--pa-accent)' }}>&ndash;</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>

            <p className="pt-2" style={{ color: 'var(--pa-heading)', opacity: 0.85 }}>
              Il ne s'agit pas de pr&eacute;dire.
              <br />
              Il s'agit de relier les &eacute;l&eacute;ments.
            </p>
          </div>

          <div className="mt-12 md:mt-16">
            <button
              onClick={() => navigate('/formulaire')}
              className="link-editorial group"
              data-testid="cta-astrology"
            >
              D&eacute;couvrir mon aper&ccedil;u
              <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" strokeWidth={1.5} />
            </button>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── MÉTHODE ─── */}
      <section className="section-editorial relative z-10" data-testid="section-method">
        <div className="section-narrow">
          <p className="section-label">M&eacute;thode</p>

          <div className="space-y-6 text-sm md:text-base" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
            <p style={{ color: 'var(--pa-heading)', fontFamily: 'Cormorant Garamond, serif', fontSize: '1.3rem', lineHeight: '1.6' }}>
              Calculs astrologiques professionnels.
              <br />
              Lecture symbolique experte.
              <br />
              Restitution claire et accessible.
            </p>

            <p className="pt-4">
              Chaque lecture est personnalis&eacute;e
              &agrave; partir de vos donn&eacute;es de naissance.
            </p>

            <p style={{ color: 'var(--pa-heading)', opacity: 0.85 }}>
              Nous traduisons des configurations symboliques.
              <br />
              Rien de plus. Rien de moins.
            </p>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── POUR ALLER PLUS LOIN ─── */}
      <section className="section-editorial relative z-10" data-testid="section-further">
        <div className="section-narrow">
          <p className="section-label">Pour aller plus loin</p>
          <h2
            className="text-2xl sm:text-3xl md:text-4xl mb-10 md:mb-14"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}
          >
            Approfondir. Ou rester en lien.
          </h2>

          <div className="space-y-8 py-4 mb-8">
            {[
              'Lecture synth\u00e8se',
              'Cartographie annuelle',
              'Suivi mensuel',
            ].map((item, i) => (
              <div key={i} className="flex gap-6 items-baseline">
                <span
                  className="text-xs tracking-widest flex-shrink-0 w-6 text-right"
                  style={{ color: 'var(--pa-accent)' }}
                >
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span className="text-base" style={{ color: 'var(--pa-heading)' }}>{item}</span>
              </div>
            ))}
          </div>

          <p className="text-sm md:text-base" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
            Vous avancez &agrave; votre rythme.
          </p>
        </div>
      </section>

      <SectionDivider />

      {/* ─── POSTURE ─── */}
      <section className="section-editorial relative z-10" data-testid="section-posture">
        <div className="section-narrow">
          <p className="section-label">Posture</p>
          <h2
            className="text-2xl sm:text-3xl md:text-4xl mb-10 md:mb-14"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}
          >
            Une guidance symbolique,
            <br />
            <span style={{ fontStyle: 'italic' }}>pas une v&eacute;rit&eacute; absolue.</span>
          </h2>

          <div className="space-y-6 text-sm md:text-base" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
            <p>
              La symbolique &eacute;claire.
              <br />
              Elle n'impose pas.
            </p>
            <p style={{ color: 'var(--pa-heading)', opacity: 0.85 }}>
              Nos lectures sont des rep&egrave;res.
              <br />
              Pas des directives.
            </p>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── FINAL ─── */}
      <section className="section-editorial pb-32 md:pb-40 relative z-10" data-testid="section-final">
        <div className="section-narrow text-center">
          <h2
            className="text-2xl sm:text-3xl md:text-4xl mb-12 md:mb-14"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}
          >
            Prenez un moment pour vous<br /> comprendre autrement.
          </h2>

          <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center">
            <button
              onClick={() => navigate('/tarot-oui-non')}
              className="btn-editorial"
              data-testid="cta-final-tarot"
            >
              Recevoir une r&eacute;ponse
            </button>
            <button
              onClick={() => navigate('/formulaire')}
              className="btn-editorial"
              data-testid="cta-final-astrology"
            >
              Comprendre ma p&eacute;riode
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 py-12 px-6 text-center" style={{ borderTop: '1px solid var(--pa-divider)' }}>
        <p className="text-xs tracking-widest" style={{ color: 'var(--pa-muted)', letterSpacing: '0.15em' }}>
          Plume Astrale &mdash; Guidance symbolique personnalis&eacute;e.
        </p>
      </footer>
    </div>
  );
};

export default Index;
