import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Moon, Sparkles, Heart, ArrowRight, Sun } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen relative">
      <StarField />
      
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-4 md:px-6 noise-overlay">
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1630873273144-cfa9079fdd72?w=1920&auto=format&fit=crop&q=80')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0F0518]/50 to-[#0F0518]" />
        
        <div className="relative z-10 text-center max-w-4xl mx-auto py-24">
          <div className="animate-slide-up opacity-0 stagger-1">
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-6 font-light">
              Plume Astrale
            </p>
          </div>
          
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-normal mb-6 animate-slide-up opacity-0 stagger-2 leading-tight"
              style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
            Devenez qui vous etes
          </h1>
          
          <p className="text-lg md:text-xl text-[#E0D9F6]/70 mb-16 max-w-2xl mx-auto font-light leading-relaxed animate-slide-up opacity-0 stagger-3">
            Choisissez votre porte d'entree vers la connaissance de soi
          </p>
          
          {/* Two main CTAs */}
          <div className="grid md:grid-cols-2 gap-6 max-w-3xl mx-auto animate-slide-up opacity-0 stagger-4">
            
            {/* Tarot Entry */}
            <button 
              onClick={() => navigate('/tarot-oui-non')}
              className="group relative overflow-hidden rounded-2xl border border-[#C5A059]/30 bg-gradient-to-br from-[#2D1B4E]/80 to-[#1A0B2E]/80 p-8 md:p-10 text-left transition-all hover:border-[#C5A059]/60 hover:shadow-[0_0_30px_rgba(197,160,89,0.15)]"
              data-testid="cta-tarot-entry"
            >
              <div className="absolute top-0 right-0 w-32 h-32 bg-[#C5A059]/5 rounded-full -translate-y-1/2 translate-x-1/2 group-hover:scale-150 transition-transform duration-500" />
              <Star className="w-10 h-10 text-[#C5A059] mb-5 group-hover:scale-110 transition-transform" strokeWidth={1} />
              <h2 className="text-xl md:text-2xl mb-3" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                Obtenir une reponse immediate
              </h2>
              <p className="text-[#E0D9F6]/60 text-sm mb-5 font-light leading-relaxed">
                Le Tarot Oui/Non repond a vos questions les plus pressantes.
                Posez votre question et laissez les Arcanes vous guider.
              </p>
              <div className="flex items-center gap-2 text-[#C5A059] text-sm font-medium">
                <Sparkles className="w-4 h-4" />
                3 tirages gratuits
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>

            {/* Astrology Entry */}
            <button 
              onClick={() => navigate('/formulaire')}
              className="group relative overflow-hidden rounded-2xl border border-[#C5A059]/30 bg-gradient-to-br from-[#2D1B4E]/80 to-[#1A0B2E]/80 p-8 md:p-10 text-left transition-all hover:border-[#C5A059]/60 hover:shadow-[0_0_30px_rgba(197,160,89,0.15)]"
              data-testid="cta-astrology-entry"
            >
              <div className="absolute top-0 right-0 w-32 h-32 bg-[#C5A059]/5 rounded-full -translate-y-1/2 translate-x-1/2 group-hover:scale-150 transition-transform duration-500" />
              <Moon className="w-10 h-10 text-[#C5A059] mb-5 group-hover:scale-110 transition-transform" strokeWidth={1} />
              <h2 className="text-xl md:text-2xl mb-3" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                Comprendre ma periode actuelle
              </h2>
              <p className="text-[#E0D9F6]/60 text-sm mb-5 font-light leading-relaxed">
                Votre theme astral complet revele les energies qui vous guident.
                Decouvrez votre carte du ciel personnalisee.
              </p>
              <div className="flex items-center gap-2 text-[#C5A059] text-sm font-medium">
                <Sun className="w-4 h-4" />
                Apercu gratuit
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </button>
          </div>
          
          {/* Trust indicators */}
          <div className="flex flex-wrap justify-center items-center gap-6 md:gap-10 mt-14 text-sm text-[#E0D9F6]/40 animate-slide-up opacity-0 stagger-5">
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-[#C5A059]" strokeWidth={1} />
              <span>Calculs Precis</span>
            </div>
            <div className="flex items-center gap-2">
              <Moon className="w-4 h-4 text-[#C5A059]" strokeWidth={1} />
              <span>28+ Pages PDF</span>
            </div>
            <div className="flex items-center gap-2">
              <Heart className="w-4 h-4 text-[#C5A059]" strokeWidth={1} />
              <span>Guidance Personnalisee</span>
            </div>
          </div>
        </div>
      </section>

      {/* Other services - compact */}
      <section className="relative py-20 px-4 md:px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-4 font-light">
              Nos Services
            </p>
            <h2 className="text-2xl md:text-4xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Explorez d'autres chemins
            </h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-5">
            <button
              onClick={() => navigate('/compatibilite-amoureuse')}
              className="card-mystical group text-left hover:border-[#C5A059]/50 transition-all"
              data-testid="cta-compatibilite"
            >
              <Heart className="w-7 h-7 text-[#E8526E] mb-3" strokeWidth={1} />
              <h3 className="text-base mb-1" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                Compatibilite Amoureuse
              </h3>
              <p className="text-[#E0D9F6]/50 text-xs font-light">
                Decouvrez la connexion cosmique entre vous et votre partenaire
              </p>
            </button>
            <button
              onClick={() => navigate('/quotidien')}
              className="card-mystical group text-left hover:border-[#C5A059]/50 transition-all"
              data-testid="cta-quotidien"
            >
              <Sun className="w-7 h-7 text-[#C5A059] mb-3" strokeWidth={1} />
              <h3 className="text-base mb-1" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                Guidance du Jour
              </h3>
              <p className="text-[#E0D9F6]/50 text-xs font-light">
                Horoscope quotidien avec phase lunaire en temps reel
              </p>
            </button>
            <button
              onClick={() => navigate('/tarologie')}
              className="card-mystical group text-left hover:border-[#C5A059]/50 transition-all"
              data-testid="cta-tarologie"
            >
              <Sparkles className="w-7 h-7 text-[#A78BFA] mb-3" strokeWidth={1} />
              <h3 className="text-base mb-1" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                Tarologie Complete
              </h3>
              <p className="text-[#E0D9F6]/50 text-xs font-light">
                Tirage en Croix 5 cartes + lecture mediumnique
              </p>
            </button>
          </div>
        </div>
      </section>

      {/* Testimonials - compact */}
      <section className="relative py-16 px-4 md:px-6 bg-[#1A0B2E]/30">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-2xl md:text-3xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Ames Eclairees
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { name: "Marie L.", text: "Une revelation spirituelle. Cette lecture m'a reconnectee a mon essence profonde." },
              { name: "Thomas R.", text: "Incroyablement precis. Les aspects planetaires ont mis en lumiere des schemas que je ressentais sans comprendre." },
              { name: "Sophie M.", text: "Le manuscrit est magnifique. Un vrai guide pour mon annee personnelle." }
            ].map((t, i) => (
              <div key={i} className="card-mystical">
                <div className="flex mb-3">
                  {[...Array(5)].map((_, j) => (
                    <Star key={j} className="w-3.5 h-3.5 text-[#C5A059] fill-[#C5A059]" />
                  ))}
                </div>
                <p className="text-[#E0D9F6]/70 mb-4 italic font-light text-sm leading-relaxed">"{t.text}"</p>
                <p className="text-[#C5A059] text-sm">— {t.name}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="relative py-12 px-4 md:px-6">
        <p className="text-center text-xs text-[#E0D9F6]/30 max-w-xl mx-auto font-light">
          Cet outil est un support de developpement personnel et de reflexion interieure.
          Il ne remplace aucun avis medical, psychologique ou juridique.
        </p>
      </section>
    </div>
  );
};

export default Index;
