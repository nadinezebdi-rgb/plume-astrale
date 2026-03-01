import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Minus } from 'lucide-react';

const SectionDivider = () => (
  <div className="divider-subtle" />
);

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen" data-testid="homepage">

      {/* ─── HERO ─── */}
      <section className="min-h-screen flex flex-col justify-center px-6 md:px-8" data-testid="hero-section">
        <div className="max-w-3xl mx-auto w-full">
          {/* Wordmark */}
          <p
            className="text-xs tracking-widest uppercase mb-16 md:mb-24 opacity-50"
            style={{ color: 'var(--pa-accent)', letterSpacing: '0.25em' }}
          >
            Plume Astrale
          </p>

          {/* Headline */}
          <h1
            className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl mb-8 md:mb-10 leading-tight"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
          >
            Lorsque certaines periodes<br className="hidden sm:block" /> deviennent floues,
            <br />
            <span style={{ fontStyle: 'italic', opacity: 0.85 }}>il est possible de les comprendre.</span>
          </h1>

          {/* Subtitle */}
          <p
            className="text-sm md:text-base max-w-xl mb-16 md:mb-20 leading-relaxed"
            style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}
          >
            Plume Astrale est un espace digital de guidance symbolique,
            alliant calculs astrologiques precis et interpretation experte
            pour vous accompagner avec clarte et discernement.
          </p>

          {/* Two entry CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 sm:gap-6">
            <button
              onClick={() => navigate('/tarot-oui-non')}
              className="btn-editorial"
              data-testid="cta-tarot-entry"
            >
              <Minus className="w-4 h-4 opacity-40" strokeWidth={1} />
              Recevoir une reponse immediate
            </button>
            <button
              onClick={() => navigate('/formulaire')}
              className="btn-editorial"
              data-testid="cta-astrology-entry"
            >
              <Minus className="w-4 h-4 opacity-40" strokeWidth={1} />
              Comprendre ma periode actuelle
            </button>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── NOTRE CADRE ─── */}
      <section className="section-editorial" data-testid="section-cadre">
        <div className="section-narrow">
          <p className="section-label">Notre cadre</p>
          <h2
            className="text-2xl sm:text-3xl md:text-4xl mb-10 md:mb-14"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}
          >
            Un cadre clair, une approche responsable.
          </h2>

          <div className="space-y-6 text-sm md:text-base" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
            <p>
              Plume Astrale n'est pas un outil de prediction automatique.
            </p>
            <p>
              La plateforme s'appuie sur des outils de calcul astral professionnels,
              similaires a ceux utilises par des astrologues confirmes,
              et propose une interpretation structuree et symbolique des donnees obtenues.
            </p>
            <p style={{ color: 'var(--pa-heading)', opacity: 0.8 }}>
              Nous ne decidons rien a votre place.
              <br />
              Nous eclairons des dynamiques.
            </p>
            <p>
              La lecture reste un espace de reflexion.
              <br />
              La decision vous appartient toujours.
            </p>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── REPONSE IMMEDIATE (TAROT) ─── */}
      <section className="section-editorial" data-testid="section-tarot">
        <div className="section-narrow">
          <p className="section-label">La reponse immediate</p>
          <h2
            className="text-2xl sm:text-3xl md:text-4xl mb-10 md:mb-14"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}
          >
            Lorsque vous avez besoin d'un eclairage rapide.
          </h2>

          <div className="space-y-6 text-sm md:text-base mb-12 md:mb-16" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
            <p>
              Le tirage Oui / Non vous permet d'explorer une question precise.
              Trois tirages gratuits vous sont offerts pour ouvrir la reflexion.
            </p>
            <p>
              Chaque reponse met en lumiere une dynamique symbolique.
              <br />
              Elle ne constitue ni un verdict, ni une obligation.
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

      {/* ─── COMPREHENSION APPROFONDIE (ASTROLOGIE) ─── */}
      <section className="section-editorial" data-testid="section-astrology">
        <div className="section-narrow">
          <p className="section-label">La comprehension approfondie</p>
          <h2
            className="text-2xl sm:text-3xl md:text-4xl mb-10 md:mb-14"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}
          >
            Comprendre la periode que vous traversez.
          </h2>

          <div className="space-y-6 text-sm md:text-base" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
            <p>
              Votre theme natal et vos transits actuels revelent des mouvements plus profonds.
              A travers des calculs astrologiques precis et une lecture experte,
              nous mettons en coherence :
            </p>

            <ul className="space-y-3 pl-0">
              {[
                'Les tensions presentes',
                'Les axes d\'evolution',
                'Les cycles en cours',
                'Les decisions a clarifier',
              ].map((item, i) => (
                <li key={i} className="flex items-center gap-4">
                  <span className="w-1 h-1 rounded-full flex-shrink-0" style={{ background: 'var(--pa-accent)' }} />
                  <span>{item}</span>
                </li>
              ))}
            </ul>

            <p className="pt-4" style={{ color: 'var(--pa-heading)', opacity: 0.8 }}>
              Il ne s'agit pas de predire.
              <br />
              Il s'agit de comprendre.
            </p>
          </div>

          <div className="mt-12 md:mt-16">
            <button
              onClick={() => navigate('/formulaire')}
              className="link-editorial group"
              data-testid="cta-astrology"
            >
              Decouvrir mon apercu gratuit
              <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" strokeWidth={1.5} />
            </button>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── COMMENT NOUS TRAVAILLONS ─── */}
      <section className="section-editorial" data-testid="section-method">
        <div className="section-narrow">
          <p className="section-label">Notre methode</p>
          <h2
            className="text-2xl sm:text-3xl md:text-4xl mb-10 md:mb-14"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}
          >
            Une approche structuree et transparente.
          </h2>

          <div className="space-y-6 text-sm md:text-base" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
            <p>Plume Astrale combine :</p>

            <ul className="space-y-3 pl-0">
              {[
                'Des outils de calcul astrologique professionnels',
                'Une base symbolique rigoureuse',
                'Une interpretation experte',
                'Une restitution claire et accessible',
              ].map((item, i) => (
                <li key={i} className="flex items-center gap-4">
                  <span className="w-1 h-1 rounded-full flex-shrink-0" style={{ background: 'var(--pa-accent)' }} />
                  <span>{item}</span>
                </li>
              ))}
            </ul>

            <p className="pt-2">
              Chaque lecture est personnalisee a partir de vos donnees de naissance.
              Le contenu est genere a partir de calculs precis,
              puis structure selon une grille d'interpretation coherente.
            </p>

            <p style={{ color: 'var(--pa-heading)', opacity: 0.8 }}>
              Nous ne produisons pas des phrases generiques.
              <br />
              Nous traduisons des configurations symboliques.
            </p>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── POUR ALLER PLUS LOIN ─── */}
      <section className="section-editorial" data-testid="section-further">
        <div className="section-narrow">
          <p className="section-label">Pour aller plus loin</p>
          <h2
            className="text-2xl sm:text-3xl md:text-4xl mb-10 md:mb-14"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}
          >
            Approfondir ou rester en lien.
          </h2>

          <div className="space-y-6 text-sm md:text-base" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
            <p>Selon votre besoin, vous pouvez :</p>

            <div className="space-y-8 py-4">
              {[
                { label: 'Lecture Synthese', desc: 'Explorer une lecture synthese de votre cycle actuel' },
                { label: 'Cartographie Annuelle', desc: 'Acceder a une cartographie approfondie annuelle' },
                { label: 'Suivi Mensuel', desc: 'Maintenir un suivi symbolique mensuel' },
              ].map((item, i) => (
                <div key={i} className="flex gap-6 items-start">
                  <span
                    className="text-xs tracking-widest mt-1 flex-shrink-0 w-6 text-right"
                    style={{ color: 'var(--pa-accent)', fontFamily: 'DM Sans, sans-serif' }}
                  >
                    {String(i + 1).padStart(2, '0')}
                  </span>
                  <div>
                    <p style={{ color: 'var(--pa-heading)', fontWeight: 400 }}>{item.label}</p>
                    <p className="text-sm mt-1" style={{ color: 'var(--pa-muted)' }}>{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>

            <p className="pt-2">
              Chaque niveau correspond a un degre d'exploration different.
              <br />
              Vous avancez a votre rythme.
            </p>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── NOTRE POSTURE ─── */}
      <section className="section-editorial" data-testid="section-posture">
        <div className="section-narrow">
          <p className="section-label">Notre posture</p>
          <h2
            className="text-2xl sm:text-3xl md:text-4xl mb-10 md:mb-14"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}
          >
            Une guidance symbolique,
            <br />
            <span style={{ fontStyle: 'italic' }}>pas une verite absolue.</span>
          </h2>

          <div className="space-y-6 text-sm md:text-base" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
            <p>
              Plume Astrale n'est ni un substitut medical,
              ni un outil de decision automatique.
            </p>
            <p style={{ color: 'var(--pa-heading)', opacity: 0.8 }}>
              La symbolique eclaire.
              <br />
              Elle n'impose pas.
            </p>
            <p>
              Nous croyons a l'autonomie interieure.
              <br />
              Nos lectures sont des reperes, pas des directives.
            </p>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ─── SECTION FINALE ─── */}
      <section className="section-editorial pb-32 md:pb-40" data-testid="section-final">
        <div className="section-narrow text-center">
          <h2
            className="text-2xl sm:text-3xl md:text-4xl mb-8 md:mb-10"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}
          >
            Prenez un moment pour vous<br /> comprendre autrement.
          </h2>

          <p
            className="text-sm md:text-base mb-14 md:mb-16 max-w-md mx-auto"
            style={{ color: 'var(--pa-body)', lineHeight: '2' }}
          >
            Que vous cherchiez une reponse immediate
            ou une comprehension plus profonde,
            vous pouvez commencer ici.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center">
            <button
              onClick={() => navigate('/tarot-oui-non')}
              className="btn-editorial"
              data-testid="cta-final-tarot"
            >
              <Minus className="w-4 h-4 opacity-40" strokeWidth={1} />
              Recevoir une reponse
            </button>
            <button
              onClick={() => navigate('/formulaire')}
              className="btn-editorial"
              data-testid="cta-final-astrology"
            >
              <Minus className="w-4 h-4 opacity-40" strokeWidth={1} />
              Comprendre ma periode
            </button>
          </div>
        </div>
      </section>

      {/* Footer minimal */}
      <footer className="py-12 px-6 text-center" style={{ borderTop: '1px solid var(--pa-divider)' }}>
        <p className="text-xs tracking-widest" style={{ color: 'var(--pa-muted)', letterSpacing: '0.15em' }}>
          Plume Astrale — Guidance symbolique personnalisee
        </p>
      </footer>
    </div>
  );
};

export default Index;
