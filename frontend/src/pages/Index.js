import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const PLUME_IMG = "https://customer-assets.emergentagent.com/job_6ebe2661-1b82-4742-afc5-632bf29dfcc5/artifacts/v8g1i6qn_une%20plume.png";
const SOLEIL_IMG = "https://customer-assets.emergentagent.com/job_6ebe2661-1b82-4742-afc5-632bf29dfcc5/artifacts/sm8ajzvy_symbole%20dor%C3%A9.png";

const SectionDivider = () => <div className="w-10 h-px mx-auto my-8 md:my-10" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />;

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen relative" data-testid="homepage">
      <StarField count={90} />

      {/* ─── HERO ─── */}
      <section className="relative z-10 min-h-screen flex flex-col justify-center px-6 md:px-8" data-testid="hero-section">
        <div className="max-w-4xl mx-auto w-full flex flex-col md:flex-row items-center gap-8 md:gap-16">

          {/* Text */}
          <div className="flex-1">
            <h1
              className="text-3xl sm:text-4xl md:text-5xl lg:text-7xl mb-3"
              style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 400, color: 'var(--pa-accent)', letterSpacing: '0.04em' }}
            >
              Plume Astrale
            </h1>

            <p
              className="text-xl sm:text-2xl md:text-3xl mb-5 leading-snug"
              style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
            >
              Lorsque certaines p&eacute;riodes deviennent floues,
              <br />
              <span style={{ fontStyle: 'italic', opacity: 0.85 }}>il est possible de les comprendre.</span>
            </p>

            <p className="text-sm max-w-md mb-8" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>
              Un espace de guidance symbolique,
              fond&eacute; sur des calculs astrologiques pr&eacute;cis
              et une interpr&eacute;tation experte.
            </p>

            <div className="flex flex-col sm:flex-row gap-3">
              <button onClick={() => navigate('/tarot-oui-non')} className="btn-editorial text-xs px-6 py-3" data-testid="cta-tarot-entry">
                Recevoir une r&eacute;ponse imm&eacute;diate
              </button>
              <button onClick={() => navigate('/formulaire')} className="btn-editorial text-xs px-6 py-3" data-testid="cta-astrology-entry">
                Comprendre ma p&eacute;riode actuelle
              </button>
            </div>
          </div>

          {/* Plume image */}
          <div className="w-48 md:w-64 lg:w-80 flex-shrink-0 opacity-90">
            <img src={PLUME_IMG} alt="Plume dorée" className="w-full h-auto drop-shadow-2xl" style={{ filter: 'drop-shadow(0 0 30px rgba(197, 160, 89, 0.15))' }} />
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── NOTRE CADRE ─── */}
      <section className="relative z-10 py-12 md:py-16 px-6 md:px-8" data-testid="section-cadre">
        <div className="max-w-2xl mx-auto">
          <p className="section-label mb-4">Notre cadre</p>
          <h2 className="text-2xl md:text-3xl mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}>
            Un cadre clair. Une approche responsable.
          </h2>
          <div className="space-y-4 text-sm md:text-base" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
            <p>Plume Astrale ne pr&eacute;dit pas votre avenir.<br />Elle &eacute;claire des dynamiques.</p>
            <p>Les calculs sont pr&eacute;cis.<br />L'interpr&eacute;tation est structur&eacute;e.</p>
            <p style={{ color: 'var(--pa-heading)', opacity: 0.85 }}>La d&eacute;cision vous appartient toujours.</p>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── RÉPONSE IMMÉDIATE ─── */}
      <section className="relative z-10 py-12 md:py-16 px-6 md:px-8" data-testid="section-tarot">
        <div className="max-w-2xl mx-auto">
          <p className="section-label mb-4">R&eacute;ponse imm&eacute;diate</p>
          <h2 className="text-2xl md:text-3xl mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}>
            Besoin d'un &eacute;clairage rapide ?
          </h2>
          <div className="space-y-4 text-sm md:text-base mb-8" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
            <p>Le tirage Oui / Non ouvre une r&eacute;flexion.<br />Trois tirages gratuits pour commencer.</p>
            <p>Une r&eacute;ponse n'est jamais un verdict.<br />C'est un symbole &agrave; explorer.</p>
          </div>
          <button onClick={() => navigate('/tarot-oui-non')} className="link-editorial group" data-testid="cta-tarot">
            Faire un tirage <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" strokeWidth={1.5} />
          </button>
        </div>
      </section>

      <SectionDivider />

      {/* ─── COMPRÉHENSION APPROFONDIE + Soleil ─── */}
      <section className="relative z-10 py-12 md:py-16 px-6 md:px-8" data-testid="section-astrology">
        <div className="max-w-3xl mx-auto flex flex-col md:flex-row items-start gap-8 md:gap-14">
          {/* Soleil doré */}
          <div className="w-32 md:w-44 flex-shrink-0 mx-auto md:mx-0 opacity-80">
            <img src={SOLEIL_IMG} alt="Symbole solaire" className="w-full h-auto rounded-full" style={{ filter: 'drop-shadow(0 0 20px rgba(197, 160, 89, 0.12))' }} />
          </div>

          <div className="flex-1">
            <p className="section-label mb-4">Compr&eacute;hension approfondie</p>
            <h2 className="text-2xl md:text-3xl mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}>
              Comprendre la p&eacute;riode que vous traversez.
            </h2>
            <div className="space-y-4 text-sm md:text-base" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
              <p>&Agrave; partir de votre th&egrave;me natal et de vos transits :</p>
              <ul className="space-y-2 pl-0">
                {['Les tensions pr\u00e9sentes', 'Les cycles en cours', 'Les axes d\'\u00e9volution'].map((item, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <span className="text-xs" style={{ color: 'var(--pa-accent)' }}>&ndash;</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
              <p style={{ color: 'var(--pa-heading)', opacity: 0.85 }}>Il ne s'agit pas de pr&eacute;dire.<br />Il s'agit de relier les &eacute;l&eacute;ments.</p>
            </div>
            <div className="mt-8">
              <button onClick={() => navigate('/formulaire')} className="link-editorial group" data-testid="cta-astrology">
                D&eacute;couvrir mon aper&ccedil;u <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" strokeWidth={1.5} />
              </button>
            </div>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── MÉTHODE ─── */}
      <section className="relative z-10 py-12 md:py-16 px-6 md:px-8" data-testid="section-method">
        <div className="max-w-2xl mx-auto">
          <p className="section-label mb-4">M&eacute;thode</p>
          <div className="space-y-4 text-sm md:text-base" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
            <p style={{ color: 'var(--pa-heading)', fontFamily: 'Cormorant Garamond, serif', fontSize: '1.2rem', lineHeight: '1.6' }}>
              Calculs astrologiques professionnels.<br />Lecture symbolique experte.<br />Restitution claire et accessible.
            </p>
            <p>Chaque lecture est personnalis&eacute;e &agrave; partir de vos donn&eacute;es de naissance.</p>
            <p style={{ color: 'var(--pa-heading)', opacity: 0.85 }}>Nous traduisons des configurations symboliques.<br />Rien de plus. Rien de moins.</p>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── POUR ALLER PLUS LOIN ─── */}
      <section className="relative z-10 py-12 md:py-16 px-6 md:px-8" data-testid="section-further">
        <div className="max-w-2xl mx-auto">
          <p className="section-label mb-4">Pour aller plus loin</p>
          <h2 className="text-2xl md:text-3xl mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}>
            Approfondir. Ou rester en lien.
          </h2>
          <div className="space-y-4 py-2 mb-4">
            {['Lecture synth\u00e8se', 'Cartographie annuelle', 'Suivi mensuel'].map((item, i) => (
              <div key={i} className="flex gap-4 items-baseline">
                <span className="text-xs tracking-widest flex-shrink-0 w-5 text-right" style={{ color: 'var(--pa-accent)' }}>{String(i + 1).padStart(2, '0')}</span>
                <span style={{ color: 'var(--pa-heading)' }}>{item}</span>
              </div>
            ))}
          </div>
          <p className="text-sm" style={{ color: 'var(--pa-body)' }}>Vous avancez &agrave; votre rythme.</p>
        </div>
      </section>

      <SectionDivider />

      {/* ─── POSTURE ─── */}
      <section className="relative z-10 py-12 md:py-16 px-6 md:px-8" data-testid="section-posture">
        <div className="max-w-2xl mx-auto">
          <p className="section-label mb-4">Posture</p>
          <h2 className="text-2xl md:text-3xl mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}>
            Une guidance symbolique,<br /><span style={{ fontStyle: 'italic' }}>pas une v&eacute;rit&eacute; absolue.</span>
          </h2>
          <div className="space-y-4 text-sm md:text-base" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
            <p>La symbolique &eacute;claire.<br />Elle n'impose pas.</p>
            <p style={{ color: 'var(--pa-heading)', opacity: 0.85 }}>Nos lectures sont des rep&egrave;res.<br />Pas des directives.</p>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── FINAL ─── */}
      <section className="relative z-10 py-16 md:py-20 pb-24 md:pb-32 px-6 md:px-8" data-testid="section-final">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl md:text-3xl mb-8" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}>
            Prenez un moment pour vous<br /> comprendre autrement.
          </h2>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button onClick={() => navigate('/tarot-oui-non')} className="btn-editorial text-xs px-6 py-3" data-testid="cta-final-tarot">
              Recevoir une r&eacute;ponse
            </button>
            <button onClick={() => navigate('/formulaire')} className="btn-editorial text-xs px-6 py-3" data-testid="cta-final-astrology">
              Comprendre ma p&eacute;riode
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 py-8 px-6 text-center" style={{ borderTop: '1px solid var(--pa-divider)' }}>
        <p className="text-xs tracking-widest" style={{ color: 'var(--pa-muted)', letterSpacing: '0.15em' }}>
          Plume Astrale &mdash; Guidance symbolique personnalis&eacute;e.
        </p>
      </footer>
    </div>
  );
};

export default Index;
