import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

const PLUME_IMG = "https://customer-assets.emergentagent.com/job_6ebe2661-1b82-4742-afc5-632bf29dfcc5/artifacts/v8g1i6qn_une%20plume.png";
const SOLEIL_IMG = "https://customer-assets.emergentagent.com/job_6ebe2661-1b82-4742-afc5-632bf29dfcc5/artifacts/sm8ajzvy_symbole%20dor%C3%A9.png";
const OEIL_IMG = "https://customer-assets.emergentagent.com/job_6ebe2661-1b82-4742-afc5-632bf29dfcc5/artifacts/ef0rea3g_3%C3%A8me%20oeil.png";

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen relative" data-testid="homepage">

      {/* ─── HERO ─── */}
      <section className="relative z-10 min-h-screen flex flex-col justify-center px-6 md:px-8" data-testid="hero-section">
        <div className="max-w-4xl mx-auto w-full flex flex-col md:flex-row items-center gap-6 md:gap-14">
          <div className="flex-1">
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 400, color: 'var(--pa-accent)', letterSpacing: '0.04em' }}>
              Plume Astrale
            </h1>
            <p className="text-xl sm:text-2xl md:text-3xl mb-4 leading-snug" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
              Lorsque certaines p&eacute;riodes deviennent floues,<br />
              <span style={{ fontStyle: 'italic', opacity: 0.85 }}>il est possible de les comprendre.</span>
            </p>
            <p className="text-sm max-w-md mb-6" style={{ color: 'var(--pa-body)', lineHeight: '1.7' }}>
              Un espace de guidance symbolique, fond&eacute; sur des calculs astrologiques pr&eacute;cis et une interpr&eacute;tation experte.
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <button onClick={() => navigate('/tarot-oui-non')} className="btn-editorial text-xs px-6 py-2.5" data-testid="cta-tarot-entry">Recevoir une r&eacute;ponse imm&eacute;diate</button>
              <button onClick={() => navigate('/formulaire')} className="btn-editorial text-xs px-6 py-2.5" data-testid="cta-astrology-entry">Comprendre ma p&eacute;riode actuelle</button>
            </div>
          </div>
          <div className="w-44 md:w-60 lg:w-72 flex-shrink-0 opacity-90">
            <img src={PLUME_IMG} alt="" className="w-full h-auto" style={{ filter: 'drop-shadow(0 0 30px rgba(197,160,89,0.15))' }} />
          </div>
        </div>
      </section>

      {/* ─── CONTENT FLOW ─── */}
      <div className="relative z-10 max-w-2xl mx-auto px-6 md:px-8">

        {/* NOTRE CADRE */}
        <div className="mb-10" data-testid="section-cadre">
          <p className="text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>Notre cadre</p>
          <h2 className="text-2xl md:text-3xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>Un cadre clair. Une approche responsable.</h2>
          <div className="space-y-2 text-sm" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>
            <p>Plume Astrale ne pr&eacute;dit pas votre avenir. Elle &eacute;claire des dynamiques.</p>
            <p>Les calculs sont pr&eacute;cis. L'interpr&eacute;tation est structur&eacute;e.</p>
            <p style={{ color: 'var(--pa-heading)', opacity: 0.85 }}>La d&eacute;cision vous appartient toujours.</p>
          </div>
        </div>

        {/* thin gold line */}
        <div className="w-8 h-px mb-10" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />

        {/* RÉPONSE IMMÉDIATE */}
        <div className="mb-10" data-testid="section-tarot">
          <p className="text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>R&eacute;ponse imm&eacute;diate</p>
          <h2 className="text-2xl md:text-3xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>Besoin d'un &eacute;clairage rapide ?</h2>
          <div className="space-y-2 text-sm mb-5" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>
            <p>Le tirage Oui / Non ouvre une r&eacute;flexion. Trois tirages gratuits pour commencer.</p>
            <p>Une r&eacute;ponse n'est jamais un verdict. C'est un symbole &agrave; explorer.</p>
          </div>
          <button onClick={() => navigate('/tarot-oui-non')} className="link-editorial group text-sm" data-testid="cta-tarot">
            Faire un tirage <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" strokeWidth={1.5} />
          </button>
        </div>

        {/* thin gold line */}
        <div className="w-8 h-px mb-10" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />

        {/* COMPRÉHENSION APPROFONDIE + Soleil */}
        <div className="mb-10 flex flex-col md:flex-row items-start gap-6 md:gap-10" data-testid="section-astrology">
          <div className="w-28 md:w-36 flex-shrink-0 mx-auto md:mx-0 opacity-80">
            <img src={SOLEIL_IMG} alt="" className="w-full h-auto rounded-full" style={{ filter: 'drop-shadow(0 0 20px rgba(197,160,89,0.12))' }} />
          </div>
          <div className="flex-1">
            <p className="text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>Compr&eacute;hension approfondie</p>
            <h2 className="text-2xl md:text-3xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>Comprendre la p&eacute;riode que vous traversez.</h2>
            <div className="space-y-2 text-sm" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>
              <p>&Agrave; partir de votre th&egrave;me natal et de vos transits :</p>
              <ul className="space-y-1 pl-0">
                {['Les tensions pr\u00e9sentes','Les cycles en cours','Les axes d\'\u00e9volution'].map((t,i) => (
                  <li key={i} className="flex items-center gap-2"><span className="text-xs" style={{ color: 'var(--pa-accent)' }}>&ndash;</span><span>{t}</span></li>
                ))}
              </ul>
              <p style={{ color: 'var(--pa-heading)', opacity: 0.85 }}>Il ne s'agit pas de pr&eacute;dire. Il s'agit de relier les &eacute;l&eacute;ments.</p>
            </div>
            <button onClick={() => navigate('/formulaire')} className="link-editorial group text-sm mt-4" data-testid="cta-astrology">
              D&eacute;couvrir mon aper&ccedil;u <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" strokeWidth={1.5} />
            </button>
          </div>
        </div>

        {/* thin gold line */}
        <div className="w-8 h-px mb-10" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />

        {/* MÉTHODE */}
        <div className="mb-10" data-testid="section-method">
          <p className="text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>M&eacute;thode</p>
          <div className="space-y-2 text-sm" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>
            <p style={{ color: 'var(--pa-heading)', fontFamily: 'Cormorant Garamond, serif', fontSize: '1.15rem', lineHeight: '1.5' }}>
              Calculs astrologiques professionnels.<br />Lecture symbolique experte.<br />Restitution claire et accessible.
            </p>
            <p>Chaque lecture est personnalis&eacute;e &agrave; partir de vos donn&eacute;es de naissance.</p>
            <p style={{ color: 'var(--pa-heading)', opacity: 0.85 }}>Nous traduisons des configurations symboliques. Rien de plus. Rien de moins.</p>
          </div>
        </div>

        {/* thin gold line */}
        <div className="w-8 h-px mb-10" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />

        {/* POUR ALLER PLUS LOIN */}
        <div className="mb-10" data-testid="section-further">
          <p className="text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>Pour aller plus loin</p>
          <h2 className="text-2xl md:text-3xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>Approfondir. Ou rester en lien.</h2>
          <div className="space-y-2 py-1 mb-2">
            {['Lecture synth\u00e8se','Cartographie annuelle','Suivi mensuel'].map((t,i) => (
              <div key={i} className="flex gap-3 items-baseline">
                <span className="text-xs tracking-widest flex-shrink-0 w-5 text-right" style={{ color: 'var(--pa-accent)' }}>{String(i+1).padStart(2,'0')}</span>
                <span className="text-sm" style={{ color: 'var(--pa-heading)' }}>{t}</span>
              </div>
            ))}
          </div>
          <p className="text-sm" style={{ color: 'var(--pa-body)' }}>Vous avancez &agrave; votre rythme.</p>
        </div>

        {/* thin gold line */}
        <div className="w-8 h-px mb-10" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />

        {/* POSTURE */}
        <div className="mb-10" data-testid="section-posture">
          <p className="text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>Posture</p>
          <h2 className="text-2xl md:text-3xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
            Une guidance symbolique, <span style={{ fontStyle: 'italic' }}>pas une v&eacute;rit&eacute; absolue.</span>
          </h2>
          <div className="space-y-2 text-sm" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>
            <p>La symbolique &eacute;claire. Elle n'impose pas.</p>
            <p style={{ color: 'var(--pa-heading)', opacity: 0.85 }}>Nos lectures sont des rep&egrave;res. Pas des directives.</p>
          </div>
        </div>

        {/* 3ÈME OEIL */}
        <div className="flex justify-center mb-10">
          <img src={OEIL_IMG} alt="" className="w-36 md:w-48 h-auto rounded-full" style={{ filter: 'drop-shadow(0 0 40px rgba(197,160,89,0.25))' }} />
        </div>

        {/* FINAL */}
        <div className="text-center pb-16" data-testid="section-final">
          <h2 className="text-2xl md:text-3xl mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
            Prenez un moment pour vous comprendre autrement.
          </h2>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button onClick={() => navigate('/tarot-oui-non')} className="btn-editorial text-xs px-6 py-2.5" data-testid="cta-final-tarot">Recevoir une r&eacute;ponse</button>
            <button onClick={() => navigate('/formulaire')} className="btn-editorial text-xs px-6 py-2.5" data-testid="cta-final-astrology">Comprendre ma p&eacute;riode</button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 py-6 px-6 text-center" style={{ borderTop: '1px solid var(--pa-divider)' }}>
        <p className="text-xs tracking-widest" style={{ color: 'var(--pa-muted)', letterSpacing: '0.15em' }}>Plume Astrale &mdash; Guidance symbolique personnalis&eacute;e.</p>
      </footer>
    </div>
  );
};

export default Index;
