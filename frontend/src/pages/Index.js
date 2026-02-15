import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Moon, Sparkles, Heart, Eye, Sun, ArrowRight } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const Index = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <Star className="w-6 h-6" strokeWidth={1} />,
      title: "Chemin de Vie",
      description: "Découvrez votre nombre sacré et la mission de votre âme"
    },
    {
      icon: <Moon className="w-6 h-6" strokeWidth={1} />,
      title: "Ascendant Cosmique",
      description: "Calcul astronomique précis de votre masque social"
    },
    {
      icon: <Sun className="w-6 h-6" strokeWidth={1} />,
      title: "Soleil & Lune",
      description: "Votre essence profonde et votre monde émotionnel"
    },
    {
      icon: <Heart className="w-6 h-6" strokeWidth={1} />,
      title: "Venus & Mars",
      description: "Votre langage amoureux et votre force d'action"
    },
    {
      icon: <Eye className="w-6 h-6" strokeWidth={1} />,
      title: "Aspects Planétaires",
      description: "Vos talents innés et défis de croissance"
    },
    {
      icon: <Sparkles className="w-6 h-6" strokeWidth={1} />,
      title: "Manuscrit PDF",
      description: "Un document céleste personnalisé à conserver"
    }
  ];

  const testimonials = [
    {
      name: "Marie L.",
      text: "Une révélation spirituelle. Cette lecture m'a reconnectée à mon essence profonde.",
      rating: 5
    },
    {
      name: "Thomas R.",
      text: "Incroyablement précis. Les aspects planétaires ont mis en lumière des schémas que je ressentais sans comprendre.",
      rating: 5
    },
    {
      name: "Sophie M.",
      text: "Le manuscrit est magnifique. Un vrai guide pour mon année personnelle.",
      rating: 5
    }
  ];

  return (
    <div className="min-h-screen relative">
      <StarField />
      
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-4 md:px-6 noise-overlay">
        {/* Background Image */}
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1630873273144-cfa9079fdd72?w=1920&auto=format&fit=crop&q=80')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        />
        
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0F0518]/50 to-[#0F0518]" />
        
        <div className="relative z-10 text-center max-w-4xl mx-auto py-24">
          <div className="animate-slide-up opacity-0 stagger-1">
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-6 font-light">
              Votre Manuscrit Céleste Personnel
            </p>
          </div>
          
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-normal mb-8 animate-slide-up opacity-0 stagger-2 leading-tight"
              style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
            Révélez Votre
            <br />
            <span className="text-gold-gradient">Destinée Cosmique</span>
          </h1>
          
          <p className="text-lg md:text-xl text-[#E0D9F6]/80 mb-12 max-w-2xl mx-auto font-light leading-relaxed animate-slide-up opacity-0 stagger-3">
            Découvrez les secrets de votre âme à travers une étude personnalisée 
            alliant numérologie sacrée, astrologie précise et lecture d'âme intuitive
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center animate-slide-up opacity-0 stagger-4">
            <button 
              onClick={() => navigate('/formulaire')}
              className="btn-mystical-filled rounded-full flex items-center gap-3"
              data-testid="cta-begin-journey"
            >
              <Sparkles className="w-5 h-5" />
              Commencer Mon Voyage
            </button>
            
            <p className="text-[#C5A059]/70 text-sm">
              Aperçu gratuit • Dès 9,90€
            </p>
          </div>
          
          <div className="flex justify-center items-center gap-8 mt-16 text-sm text-[#E0D9F6]/50 animate-slide-up opacity-0 stagger-5">
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-[#C5A059]" strokeWidth={1} />
              <span>Calculs Précis</span>
            </div>
            <div className="flex items-center gap-2">
              <Moon className="w-4 h-4 text-[#C5A059]" strokeWidth={1} />
              <span>5 Sections</span>
            </div>
            <div className="flex items-center gap-2">
              <Heart className="w-4 h-4 text-[#C5A059]" strokeWidth={1} />
              <span>Guidance Personnalisée</span>
            </div>
          </div>
        </div>
        
        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-float">
          <div className="w-6 h-10 rounded-full border border-[#C5A059]/30 flex items-start justify-center p-2">
            <div className="w-1 h-2 bg-[#C5A059] rounded-full animate-bounce" />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative py-24 px-4 md:px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-4 font-light">
              Votre Étude Complète
            </p>
            <h2 className="text-3xl md:text-5xl mb-6" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Une Analyse Cosmique Profonde
            </h2>
            <p className="text-lg text-[#E0D9F6]/70 max-w-2xl mx-auto font-light">
              Chaque manuscrit est unique, calculé avec précision selon vos données de naissance
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="card-mystical group cursor-pointer"
                data-testid={`feature-card-${index}`}
              >
                <div className="text-[#C5A059] mb-6 group-hover:scale-110 transition-transform duration-300">
                  {feature.icon}
                </div>
                <h3 className="text-xl mb-3" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                  {feature.title}
                </h3>
                <p className="text-[#E0D9F6]/60 font-light">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="relative py-24 px-4 md:px-6 bg-[#1A0B2E]/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-4 font-light">
              Témoignages
            </p>
            <h2 className="text-3xl md:text-5xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Âmes Éclairées
            </h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="card-mystical">
                <div className="flex mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 text-[#C5A059] fill-[#C5A059]" />
                  ))}
                </div>
                <p className="text-[#E0D9F6]/80 mb-6 italic font-light leading-relaxed">
                  "{testimonial.text}"
                </p>
                <p className="text-[#C5A059] text-sm">
                  — {testimonial.name}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-24 px-4 md:px-6">
        <div className="max-w-4xl mx-auto">
          <div className="card-mystical text-center p-12 md:p-16 glow-gold">
            <Sparkles className="w-12 h-12 text-[#C5A059] mx-auto mb-8" strokeWidth={1} />
            
            <h2 className="text-3xl md:text-5xl mb-6" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Votre Destinée Vous Attend
            </h2>
            
            <p className="text-lg text-[#E0D9F6]/70 mb-10 max-w-2xl mx-auto font-light">
              Commencez votre voyage de découverte personnelle. 
              Obtenez un aperçu gratuit de votre chemin de vie.
            </p>
            
            <button 
              onClick={() => navigate('/formulaire')}
              className="btn-mystical rounded-full flex items-center gap-3 mx-auto animate-glow-pulse"
              data-testid="cta-reveal-path"
            >
              <Moon className="w-5 h-5" strokeWidth={1} />
              Révéler Mon Chemin
              <ArrowRight className="w-5 h-5" strokeWidth={1} />
            </button>
            
            <p className="text-sm text-[#E0D9F6]/40 mt-8 font-light">
              Cet outil est un support de développement personnel et de réflexion intérieure.
              <br />
              Il ne remplace aucun avis médical, psychologique ou juridique.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
