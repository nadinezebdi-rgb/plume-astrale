import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Star, Moon, Sparkles, Heart, Eye, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Index = () => {
  const navigate = useNavigate();
  const [isHovered, setIsHovered] = useState<string | null>(null);

  const testimonials = [
    {
      name: "Marie L.",
      text: "Une révélation ! Cette étude m'a aidée à comprendre mon chemin de vie et à prendre des décisions importantes.",
      rating: 5
    },
    {
      name: "Thomas R.",
      text: "Incroyablement précis. Les conseils d'alignement ont transformé ma vision de moi-même.",
      rating: 5
    },
    {
      name: "Sophie M.",
      text: "Le rapport PDF est magnifique et les calculs astrologiques sont d'une précision remarquable.",
      rating: 5
    }
  ];

  const features = [
    {
      icon: <Star className="w-6 h-6" />,
      title: "Numérologie Personnalisée",
      description: "Découvrez votre chemin de vie, vos dons naturels et votre mission d'âme"
    },
    {
      icon: <Moon className="w-6 h-6" />,
      title: "Ascendant Astrologique",
      description: "Calcul astronomique précis basé sur votre lieu et heure de naissance"
    },
    {
      icon: <Heart className="w-6 h-6" />,
      title: "Lecture d'Âme",
      description: "Une analyse intuitive et symbolique de votre essence profonde"
    },
    {
      icon: <Eye className="w-6 h-6" />,
      title: "Année Personnelle",
      description: "Comprenez les énergies et opportunités de votre année en cours"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Conseils d'Alignement",
      description: "Des recommandations personnalisées pour votre épanouissement"
    },
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: "Rapport PDF Premium",
      description: "Un document élégant à conserver et partager"
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div className="celestial-bg absolute inset-0" />
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1554668048-5055c5654bbc?w=1920&auto=format&fit=crop&q=80')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        />
        
        <div className="relative z-10 text-center max-w-4xl mx-auto px-6">
          <div className="cosmic-glow mb-8">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 mystical-text animate-float">
              Révélez Votre
              <br />
              Destinée Cosmique
            </h1>
          </div>
          
          <p className="text-xl md:text-2xl text-foreground/80 mb-8 max-w-2xl mx-auto leading-relaxed">
            Découvrez les secrets de votre âme à travers une étude personnalisée alliant 
            <span className="text-accent font-semibold"> numérologie</span>, 
            <span className="text-primary-glow font-semibold"> astrologie</span> et 
            <span className="text-accent font-semibold"> lecture d'âme</span>
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <Button 
              onClick={() => navigate('/formulaire')}
              className="golden-button text-lg px-8 py-4 animate-glow"
              size="lg"
            >
              <Sparkles className="w-5 h-5 mr-2" />
              Commencer Mon Étude
            </Button>
            
            <div className="flex items-center gap-2 text-accent">
              <Badge variant="secondary" className="bg-accent/20 text-accent border-accent/30">
                ✨ Aperçu Gratuit
              </Badge>
              <span className="text-sm">puis 19,90€ pour l'étude complète</span>
            </div>
          </div>
          
          <div className="flex justify-center items-center gap-8 text-sm text-foreground/60">
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-accent" />
              <span>Calculs Précis</span>
            </div>
            <div className="flex items-center gap-2">
              <Moon className="w-4 h-4 text-primary-glow" />
              <span>Analyse Complète</span>
            </div>
            <div className="flex items-center gap-2">
              <Heart className="w-4 h-4 text-accent" />
              <span>Guidance Personnalisée</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 mystical-text">
              Une Étude Complète et Personnalisée
            </h2>
            <p className="text-xl text-foreground/70 max-w-3xl mx-auto">
              Chaque analyse est unique, calculée précisément selon vos données de naissance 
              et enrichie d'une guidance spirituelle bienveillante.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card 
                key={index}
                className="mystical-card hover:scale-105 transition-all duration-300 cursor-pointer"
                onMouseEnter={() => setIsHovered(`feature-${index}`)}
                onMouseLeave={() => setIsHovered(null)}
              >
                <CardHeader className="text-center">
                  <div className={`mx-auto mb-4 p-3 rounded-full bg-primary/20 text-primary-glow transition-all duration-300 ${
                    isHovered === `feature-${index}` ? 'scale-110 animate-glow' : ''
                  }`}>
                    {feature.icon}
                  </div>
                  <CardTitle className="text-xl font-semibold">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-center text-foreground/70">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 px-6 bg-card/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 mystical-text">
              Témoignages de Nos Âmes Éclairées
            </h2>
            <p className="text-xl text-foreground/70">
              Découvrez comment notre guidance a transformé des vies
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="mystical-card">
                <CardContent className="pt-6">
                  <div className="flex mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 text-accent fill-current" />
                    ))}
                  </div>
                  <p className="text-foreground/80 mb-4 italic">
                    "{testimonial.text}"
                  </p>
                  <p className="font-semibold text-accent">
                    — {testimonial.name}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="mystical-card p-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 mystical-text">
              Votre Destinée Vous Attend
            </h2>
            <p className="text-xl text-foreground/70 mb-8 max-w-2xl mx-auto">
              Commencez votre voyage de découverte personnelle dès maintenant. 
              Obtenez un aperçu gratuit, puis déverrouillez votre étude complète.
            </p>
            
            <Button 
              onClick={() => navigate('/formulaire')}
              className="golden-button text-lg px-12 py-4 animate-glow"
              size="lg"
            >
              <Moon className="w-5 h-5 mr-2" />
              Révéler Mon Chemin de Vie
            </Button>
            
            <p className="text-sm text-foreground/50 mt-6">
              Cet outil est un support de développement personnel et de réflexion intérieure. 
              Il ne remplace aucun avis médical, psychologique ou juridique.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
