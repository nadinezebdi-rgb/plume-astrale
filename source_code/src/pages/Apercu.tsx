import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Star, Moon, Heart, Lock, Sparkles, ArrowRight, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface UserData {
  prenom: string;
  dateNaissance: string;
  heureNaissance: string;
  ville: string;
  pays: string;
  email: string;
}

const Apercu = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [cheminVie, setCheminVie] = useState<number>(0);
  const [anneePersonnelle, setAnneePersonnelle] = useState<number>(0);

  useEffect(() => {
    const data = localStorage.getItem('numerologie_data');
    if (!data) {
      navigate('/formulaire');
      return;
    }
    
    const parsedData = JSON.parse(data);
    setUserData(parsedData);
    
    // Calculs numérologie
    const dateNaissance = new Date(parsedData.dateNaissance);
    const cheminVieCalcule = calculerCheminVie(dateNaissance);
    const anneePersonnelleCalculee = calculerAnneePersonnelle(dateNaissance);
    
    setCheminVie(cheminVieCalcule);
    setAnneePersonnelle(anneePersonnelleCalculee);
  }, [navigate]);

  const calculerCheminVie = (date: Date): number => {
    const jour = date.getDate();
    const mois = date.getMonth() + 1;
    const annee = date.getFullYear();
    
    let somme = jour + mois + annee;
    
    // Réduction théosophique
    while (somme > 9 && somme !== 11 && somme !== 22 && somme !== 33) {
      somme = somme.toString().split('').reduce((acc, digit) => acc + parseInt(digit), 0);
    }
    
    return somme;
  };

  const calculerAnneePersonnelle = (dateNaissance: Date): number => {
    const jour = dateNaissance.getDate();
    const mois = dateNaissance.getMonth() + 1;
    const anneeActuelle = new Date().getFullYear();
    
    let somme = jour + mois + anneeActuelle;
    
    while (somme > 9) {
      somme = somme.toString().split('').reduce((acc, digit) => acc + parseInt(digit), 0);
    }
    
    return somme;
  };

  const getCheminVieApercu = (chemin: number): { titre: string; apercu: string; complet: string } => {
    const interpretations = {
      1: {
        titre: "Le Pionnier",
        apercu: "Vous êtes né(e) pour diriger et innover. Votre énergie naturelle vous pousse vers l'indépendance et la création.",
        complet: "Découvrez vos dons de leadership, comment surmonter votre impatience naturelle, et votre mission de vie unique..."
      },
      2: {
        titre: "Le Diplomate",
        apercu: "Votre don pour l'harmonie et la coopération fait de vous un médiateur naturel. Vous excellez dans les relations.",
        complet: "Explorez votre sensibilité émotionnelle, vos talents de guérison, et comment équilibrer vos besoins avec ceux des autres..."
      },
      3: {
        titre: "L'Artiste",
        apercu: "Créativité et communication sont vos forces. Vous inspirez les autres par votre joie de vivre et votre expression.",
        complet: "Révélez vos talents artistiques cachés, comment canaliser votre énergie créative, et votre rôle d'inspirateur..."
      },
      4: {
        titre: "Le Bâtisseur",
        apercu: "Stabilité et méthode caractérisent votre approche. Vous construisez des fondations solides pour l'avenir.",
        complet: "Comprenez votre besoin de sécurité, vos talents d'organisation, et comment transformer vos rêves en réalité..."
      },
      5: {
        titre: "L'Aventurier",
        apercu: "Liberté et changement nourrissent votre âme. Vous êtes fait(e) pour explorer et découvrir de nouveaux horizons.",
        complet: "Explorez votre soif de liberté, comment équilibrer stabilité et aventure, et votre mission d'éveil des consciences..."
      },
      6: {
        titre: "Le Guérisseur",
        apercu: "Amour et service aux autres définissent votre essence. Vous êtes un pilier de soutien pour votre entourage.",
        complet: "Découvrez vos dons de guérison, comment éviter l'épuisement émotionnel, et votre rôle de gardien de l'harmonie..."
      },
      7: {
        titre: "Le Sage",
        apercu: "Recherche spirituelle et analyse profonde vous caractérisent. Vous cherchez la vérité au-delà des apparences.",
        complet: "Révélez votre sagesse intérieure, vos dons intuitifs, et comment partager vos découvertes spirituelles..."
      },
      8: {
        titre: "Le Leader",
        apercu: "Ambition et réussite matérielle vous motivent. Vous avez le don de transformer les idées en succès concrets.",
        complet: "Comprenez votre relation au pouvoir, comment équilibrer succès et éthique, et votre mission de transformation sociale..."
      },
      9: {
        titre: "L'Humanitaire",
        apercu: "Compassion universelle et service à l'humanité vous animent. Vous êtes ici pour élever la conscience collective.",
        complet: "Explorez votre mission humanitaire, comment gérer votre hypersensibilité, et votre rôle de guide spirituel..."
      },
      11: {
        titre: "L'Inspirateur",
        apercu: "Intuition et inspiration vous connectent aux dimensions supérieures. Vous êtes un canal de lumière.",
        complet: "Révélez vos dons psychiques, comment ancrer votre sensibilité, et votre mission d'éveil spirituel..."
      },
      22: {
        titre: "Le Maître Bâtisseur",
        apercu: "Vision et réalisation se conjuguent en vous. Vous pouvez matérialiser des projets d'envergure mondiale.",
        complet: "Découvrez votre potentiel de transformation globale, comment gérer cette énergie puissante, et votre héritage spirituel..."
      }
    };
    
    return interpretations[chemin as keyof typeof interpretations] || interpretations[1];
  };

  const getAnneePersonnelleApercu = (annee: number): { titre: string; apercu: string } => {
    const interpretations = {
      1: {
        titre: "Année de Nouveaux Départs",
        apercu: "2024 marque un nouveau cycle. C'est le moment d'initier des projets et de prendre des décisions importantes."
      },
      2: {
        titre: "Année de Coopération",
        apercu: "Cette année favorise les partenariats et la diplomatie. Patience et collaboration seront vos atouts."
      },
      3: {
        titre: "Année de Créativité",
        apercu: "Votre créativité s'épanouit cette année. Expression artistique et communication sont favorisées."
      },
      4: {
        titre: "Année de Construction",
        apercu: "Travail acharné et organisation sont à l'honneur. Posez des bases solides pour votre avenir."
      },
      5: {
        titre: "Année de Liberté",
        apercu: "Changements et nouvelles expériences vous attendent. Embrassez la liberté et l'aventure."
      },
      6: {
        titre: "Année de Responsabilité",
        apercu: "Famille et responsabilités sont au centre. Votre rôle de soutien sera particulièrement important."
      },
      7: {
        titre: "Année de Réflexion",
        apercu: "Introspection et développement spirituel sont favorisés. Prenez du temps pour vous ressourcer."
      },
      8: {
        titre: "Année de Réussite",
        apercu: "Succès matériel et reconnaissance professionnelle sont à portée de main. Votre ambition porte ses fruits."
      },
      9: {
        titre: "Année d'Accomplissement",
        apercu: "Fin d'un cycle et bilan. C'est le moment de partager vos acquis et de vous préparer au renouveau."
      }
    };
    
    return interpretations[annee as keyof typeof interpretations] || interpretations[1];
  };

  if (!userData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const cheminVieInfo = getCheminVieApercu(cheminVie);
  const anneePersonnelleInfo = getAnneePersonnelleApercu(anneePersonnelle);

  return (
    <div className="min-h-screen py-12 px-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-6 mystical-text">
            Votre Aperçu Cosmique
          </h1>
          {userData.prenom && (
            <p className="text-2xl text-accent mb-4">
              Bonjour {userData.prenom} ✨
            </p>
          )}
          <p className="text-xl text-foreground/70 mb-8">
            Découvrez les premiers secrets de votre destinée
          </p>
          
          <div className="flex justify-center items-center gap-4 text-sm text-foreground/60">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">✓</div>
              <span>Informations</span>
            </div>
            <ArrowRight className="w-4 h-4" />
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">2</div>
              <span>Aperçu</span>
            </div>
            <ArrowRight className="w-4 h-4" />
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-muted-foreground font-semibold">3</div>
              <span>Étude complète</span>
            </div>
          </div>
        </div>

        {/* Aperçu gratuit */}
        <div className="grid gap-8 mb-12">
          {/* Chemin de vie */}
          <Card className="mystical-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-full bg-primary/20 text-primary">
                    <Star className="w-6 h-6" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl">Votre Chemin de Vie : {cheminVie}</CardTitle>
                    <CardDescription className="text-lg text-accent">{cheminVieInfo.titre}</CardDescription>
                  </div>
                </div>
                <Badge variant="secondary" className="bg-accent/20 text-accent border-accent/30">
                  Aperçu Gratuit
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-lg text-foreground/80 leading-relaxed mb-4">
                {cheminVieInfo.apercu}
              </p>
              <div className="bg-muted/30 p-4 rounded-lg border border-border/50">
                <div className="flex items-start gap-3">
                  <Lock className="w-5 h-5 text-muted-foreground mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-medium text-foreground/70 mb-2">Dans l'étude complète :</p>
                    <p className="text-sm text-muted-foreground italic">
                      {cheminVieInfo.complet}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Année personnelle */}
          <Card className="mystical-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-full bg-secondary/20 text-accent">
                    <Moon className="w-6 h-6" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl">Votre Année 2024 : {anneePersonnelle}</CardTitle>
                    <CardDescription className="text-lg text-accent">{anneePersonnelleInfo.titre}</CardDescription>
                  </div>
                </div>
                <Badge variant="secondary" className="bg-accent/20 text-accent border-accent/30">
                  Aperçu Gratuit
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-lg text-foreground/80 leading-relaxed mb-4">
                {anneePersonnelleInfo.apercu}
              </p>
              <div className="bg-muted/30 p-4 rounded-lg border border-border/50">
                <div className="flex items-start gap-3">
                  <Lock className="w-5 h-5 text-muted-foreground mt-1 flex-shrink-0" />
                  <div>
                    <p className="font-medium text-foreground/70 mb-2">Dans l'étude complète :</p>
                    <p className="text-sm text-muted-foreground italic">
                      Conseils mois par mois, périodes favorables, défis à anticiper, et stratégies d'alignement personnalisées...
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Contenu verrouillé */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card className="mystical-card opacity-75">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-full bg-muted/50">
                    <Heart className="w-6 h-6 text-muted-foreground" />
                  </div>
                  <div>
                    <CardTitle className="text-xl text-muted-foreground">Lecture d'Âme</CardTitle>
                    <CardDescription>Votre essence spirituelle révélée</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center h-24 bg-muted/20 rounded-lg border border-dashed border-muted-foreground/30">
                  <div className="text-center">
                    <Lock className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">Contenu Premium</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="mystical-card opacity-75">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-full bg-muted/50">
                    <Eye className="w-6 h-6 text-muted-foreground" />
                  </div>
                  <div>
                    <CardTitle className="text-xl text-muted-foreground">Ascendant Astrologique</CardTitle>
                    <CardDescription>Calcul astronomique précis</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center h-24 bg-muted/20 rounded-lg border border-dashed border-muted-foreground/30">
                  <div className="text-center">
                    <Lock className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">Contenu Premium</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <Separator className="bg-border/50 mb-12" />

        {/* CTA Premium */}
        <Card className="mystical-card bg-gradient-to-br from-primary/10 to-accent/10 border-primary/30">
          <CardContent className="p-8 text-center">
            <div className="mb-6">
              <h2 className="text-3xl md:text-4xl font-bold mb-4 mystical-text">
                Déverrouillez Votre Destinée Complète
              </h2>
              <p className="text-xl text-foreground/70 mb-6">
                Accédez à votre analyse complète avec calculs précis, guidance personnalisée et rapport PDF premium
              </p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-4 mb-8 text-sm">
              <div className="flex items-center gap-2 justify-center">
                <Sparkles className="w-4 h-4 text-accent" />
                <span>Lecture d'âme complète</span>
              </div>
              <div className="flex items-center gap-2 justify-center">
                <Star className="w-4 h-4 text-primary" />
                <span>Ascendant astrologique</span>
              </div>
              <div className="flex items-center gap-2 justify-center">
                <Heart className="w-4 h-4 text-accent" />
                <span>Conseils d'alignement</span>
              </div>
            </div>
            
            <div className="mb-6">
              <div className="text-4xl font-bold text-accent mb-2">19,90€</div>
              <p className="text-sm text-muted-foreground">Paiement unique • Accès immédiat • Rapport PDF inclus</p>
            </div>
            
            <Button 
              onClick={() => navigate('/paiement')}
              className="golden-button text-lg px-12 py-4 animate-glow"
              size="lg"
            >
              <Sparkles className="w-5 h-5 mr-2" />
              Débloquer Mon Étude Complète
            </Button>
            
            <p className="text-xs text-muted-foreground mt-4">
              Garantie satisfait ou remboursé 30 jours
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Apercu;