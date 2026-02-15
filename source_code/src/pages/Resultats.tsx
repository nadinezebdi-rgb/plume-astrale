import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Star, Moon, Heart, Eye, Zap, Download, Mail, Share2, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface UserData {
  prenom: string;
  dateNaissance: string;
  heureNaissance: string;
  ville: string;
  pays: string;
  email: string;
}

const Resultats = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [cheminVie, setCheminVie] = useState<number>(0);
  const [anneePersonnelle, setAnneePersonnelle] = useState<number>(0);
  const [ascendant, setAscendant] = useState<string>('');

  useEffect(() => {
    const data = localStorage.getItem('numerologie_data');
    const paid = localStorage.getItem('numerologie_paid');
    
    if (!data || !paid) {
      navigate('/formulaire');
      return;
    }
    
    const parsedData = JSON.parse(data);
    setUserData(parsedData);
    
    // Calculs
    const dateNaissance = new Date(parsedData.dateNaissance);
    const cheminVieCalcule = calculerCheminVie(dateNaissance);
    const anneePersonnelleCalculee = calculerAnneePersonnelle(dateNaissance);
    const ascendantCalcule = calculerAscendant(parsedData);
    
    setCheminVie(cheminVieCalcule);
    setAnneePersonnelle(anneePersonnelleCalculee);
    setAscendant(ascendantCalcule);
  }, [navigate]);

  const calculerCheminVie = (date: Date): number => {
    const jour = date.getDate();
    const mois = date.getMonth() + 1;
    const annee = date.getFullYear();
    
    let somme = jour + mois + annee;
    
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

  const calculerAscendant = (data: UserData): string => {
    // Simulation d'un calcul d'ascendant basé sur l'heure
    const heure = parseInt(data.heureNaissance.split(':')[0]);
    const signes = [
      'Bélier', 'Taureau', 'Gémeaux', 'Cancer', 'Lion', 'Vierge',
      'Balance', 'Scorpion', 'Sagittaire', 'Capricorne', 'Verseau', 'Poissons'
    ];
    
    return signes[heure % 12];
  };

  const getCheminVieComplet = (chemin: number) => {
    const interpretations = {
      1: {
        titre: "Le Pionnier",
        dons: "Leadership naturel, indépendance, innovation, courage, détermination",
        defis: "Impatience, égocentrisme, tendance à l'isolement, difficulté à accepter l'aide",
        mission: "Ouvrir de nouveaux chemins, inspirer l'autonomie chez les autres, créer et innover pour faire avancer l'humanité",
        conseils: "Cultivez la patience, apprenez à déléguer, équilibrez votre besoin d'indépendance avec la coopération. Votre énergie pionnière est précieuse, mais elle doit être canalisée avec sagesse."
      },
      2: {
        titre: "Le Diplomate",
        dons: "Empathie, coopération, sens de l'harmonie, intuition, capacité de médiation",
        defis: "Hypersensibilité, indécision, tendance à s'effacer, dépendance émotionnelle",
        mission: "Créer l'harmonie, faciliter la coopération, guérir les relations, apporter la paix",
        conseils: "Affirmez-vous davantage, fixez des limites saines, développez votre confiance en vous. Votre don pour l'harmonie ne doit pas vous faire oublier vos propres besoins."
      },
      3: {
        titre: "L'Artiste",
        dons: "Créativité, communication, joie de vivre, inspiration, expression artistique",
        defis: "Dispersion, superficialité, tendance à la procrastination, émotions changeantes",
        mission: "Inspirer par l'art et la beauté, communiquer la joie, élever les vibrations collectives",
        conseils: "Focalisez votre énergie créative, développez la discipline, approfondissez vos talents. Votre lumière créative peut transformer le monde."
      },
      4: {
        titre: "Le Bâtisseur",
        dons: "Organisation, persévérance, fiabilité, sens pratique, construction durable",
        defis: "Rigidité, résistance au changement, tendance au surmenage, perfectionnisme",
        mission: "Construire des fondations solides, organiser et structurer, créer la stabilité",
        conseils: "Acceptez le changement comme une opportunité, prenez du temps pour vous détendre, cultivez la flexibilité. Votre stabilité est un don précieux."
      },
      5: {
        titre: "L'Aventurier",
        dons: "Liberté, adaptabilité, curiosité, communication, esprit d'aventure",
        defis: "Instabilité, impatience, difficulté d'engagement, tendance à fuir les responsabilités",
        mission: "Élargir les horizons, apporter le changement, connecter les cultures et les idées",
        conseils: "Trouvez un équilibre entre liberté et responsabilité, canalisez votre énergie vers des projets significatifs. Votre soif de liberté peut libérer les autres."
      },
      6: {
        titre: "Le Guérisseur",
        dons: "Amour inconditionnel, compassion, sens du service, guérison, harmonie familiale",
        defis: "Sacrifice excessif, tendance à porter les problèmes des autres, perfectionnisme relationnel",
        mission: "Guérir et nourrir, créer l'harmonie familiale, servir avec amour",
        conseils: "Prenez soin de vous autant que des autres, établissez des limites saines, acceptez l'imperfection. Votre amour guérit, mais vous devez vous préserver."
      },
      7: {
        titre: "Le Sage",
        dons: "Sagesse intuitive, analyse profonde, spiritualité, recherche de vérité, introspection",
        defis: "Isolement, tendance à l'analyse excessive, difficulté à exprimer ses émotions",
        mission: "Rechercher et transmettre la sagesse, élever la conscience spirituelle, guider par l'exemple",
        conseils: "Partagez votre sagesse avec le monde, cultivez les relations humaines, équilibrez solitude et connexion. Votre lumière intérieure doit rayonner."
      },
      8: {
        titre: "Le Leader",
        dons: "Ambition constructive, sens des affaires, leadership, capacité de réalisation matérielle",
        defis: "Matérialisme excessif, tendance à dominer, stress lié au succès, déséquilibre vie/travail",
        mission: "Créer l'abondance éthique, diriger avec intégrité, transformer le monde matériel",
        conseils: "Utilisez votre pouvoir avec sagesse, cultivez l'humilité, équilibrez succès matériel et valeurs spirituelles. Votre leadership peut transformer la société."
      },
      9: {
        titre: "L'Humanitaire",
        dons: "Compassion universelle, vision globale, générosité, sagesse, capacité d'inspiration",
        defis: "Idéalisme excessif, difficulté à gérer les détails pratiques, tendance au sacrifice",
        mission: "Servir l'humanité, élever la conscience collective, apporter la guérison globale",
        conseils: "Ancrez vos idéaux dans la réalité, prenez soin de vos besoins personnels, cultivez la patience. Votre vision peut changer le monde."
      },
      11: {
        titre: "L'Inspirateur",
        dons: "Intuition développée, inspiration spirituelle, capacité de révélation, charisme",
        defis: "Hypersensibilité, nervosité, difficulté à s'ancrer, pression spirituelle",
        mission: "Inspirer et élever les autres, canaliser la lumière spirituelle, révéler les vérités cachées",
        conseils: "Ancrez votre sensibilité dans le concret, développez votre confiance, partagez vos dons avec humilité. Vous êtes un canal de lumière."
      },
      22: {
        titre: "Le Maître Bâtisseur",
        dons: "Vision globale, capacité de réalisation exceptionnelle, leadership spirituel, transformation",
        defis: "Pression énorme, perfectionnisme, difficulté à gérer cette énergie puissante",
        mission: "Matérialiser des projets d'envergure mondiale, transformer la société, laisser un héritage durable",
        conseils: "Acceptez votre mission avec humilité, entourez-vous de soutien, équilibrez vision et action. Votre potentiel est immense."
      }
    };
    
    return interpretations[chemin as keyof typeof interpretations] || interpretations[1];
  };

  const getAscendantComplet = (signe: string) => {
    const interpretations = {
      'Bélier': {
        element: "Feu",
        description: "Votre ascendant Bélier vous donne une apparence dynamique et énergique. Vous dégagez une aura de leadership naturel et d'initiative. Les autres vous perçoivent comme quelqu'un de direct, courageux et prêt à relever les défis.",
        traits: "Spontané, énergique, direct, courageux, impatient",
        influence: "Cet ascendant amplifie votre capacité d'action et votre charisme naturel. Il vous pousse à prendre des initiatives et à vous affirmer dans vos relations."
      },
      'Taureau': {
        element: "Terre",
        description: "Votre ascendant Taureau vous confère une présence stable et rassurante. Vous dégagez une aura de fiabilité et de sensualité. Les autres vous perçoivent comme quelqu'un de patient, déterminé et ancré.",
        traits: "Stable, patient, sensuel, déterminé, possessif",
        influence: "Cet ascendant renforce votre besoin de sécurité et votre appréciation des plaisirs de la vie. Il vous aide à construire des bases solides."
      },
      'Gémeaux': {
        element: "Air",
        description: "Votre ascendant Gémeaux vous donne une apparence vive et communicative. Vous dégagez une curiosité intellectuelle et une adaptabilité remarquable. Les autres vous perçoivent comme quelqu'un d'intelligent et de sociable.",
        traits: "Curieux, communicatif, adaptable, intellectuel, changeant",
        influence: "Cet ascendant stimule votre soif d'apprendre et votre capacité à communiquer. Il vous ouvre de multiples possibilités d'expression."
      },
      'Cancer': {
        element: "Eau",
        description: "Votre ascendant Cancer vous confère une présence douce et protectrice. Vous dégagez une sensibilité émotionnelle et un instinct maternel/paternel. Les autres vous perçoivent comme quelqu'un d'empathique et de bienveillant.",
        traits: "Sensible, protecteur, intuitif, émotionnel, nostalgique",
        influence: "Cet ascendant développe votre empathie et votre capacité à nourrir les autres. Il vous connecte à vos émotions profondes."
      },
      'Lion': {
        element: "Feu",
        description: "Votre ascendant Lion vous donne une présence majestueuse et charismatique. Vous dégagez une confiance naturelle et une générosité du cœur. Les autres vous perçoivent comme quelqu'un de noble et d'inspirant.",
        traits: "Charismatique, généreux, créatif, fier, théâtral",
        influence: "Cet ascendant amplifie votre créativité et votre besoin de reconnaissance. Il vous pousse à briller et à inspirer les autres."
      },
      'Vierge': {
        element: "Terre",
        description: "Votre ascendant Vierge vous confère une apparence soignée et méthodique. Vous dégagez une intelligence pratique et un souci du détail. Les autres vous perçoivent comme quelqu'un de fiable et de perfectionniste.",
        traits: "Méticuleux, analytique, serviable, perfectionniste, critique",
        influence: "Cet ascendant développe votre sens de l'organisation et votre désir d'amélioration. Il vous aide à perfectionner vos talents."
      },
      'Balance': {
        element: "Air",
        description: "Votre ascendant Balance vous donne une présence harmonieuse et diplomatique. Vous dégagez un sens esthétique raffiné et un besoin d'équilibre. Les autres vous perçoivent comme quelqu'un de charmant et de juste.",
        traits: "Harmonieux, diplomatique, esthète, indécis, charmeur",
        influence: "Cet ascendant renforce votre quête d'harmonie et votre sens de la beauté. Il vous aide à créer des relations équilibrées."
      },
      'Scorpion': {
        element: "Eau",
        description: "Votre ascendant Scorpion vous confère une présence intense et magnétique. Vous dégagez une profondeur émotionnelle et un pouvoir de transformation. Les autres vous perçoivent comme quelqu'un de mystérieux et de puissant.",
        traits: "Intense, magnétique, transformateur, secret, passionné",
        influence: "Cet ascendant développe votre capacité de régénération et votre intuition profonde. Il vous connecte aux mystères de la vie."
      },
      'Sagittaire': {
        element: "Feu",
        description: "Votre ascendant Sagittaire vous donne une apparence optimiste et aventureuse. Vous dégagez une soif de liberté et une vision philosophique. Les autres vous perçoivent comme quelqu'un d'inspirant et de sage.",
        traits: "Optimiste, philosophe, aventurier, franc, idéaliste",
        influence: "Cet ascendant stimule votre quête de sens et votre besoin d'expansion. Il vous pousse vers de nouveaux horizons."
      },
      'Capricorne': {
        element: "Terre",
        description: "Votre ascendant Capricorne vous confère une présence sérieuse et ambitieuse. Vous dégagez une détermination et une maturité naturelle. Les autres vous perçoivent comme quelqu'un de responsable et de fiable.",
        traits: "Ambitieux, responsable, patient, traditionnel, réservé",
        influence: "Cet ascendant renforce votre sens des responsabilités et votre capacité d'accomplissement. Il vous aide à construire votre réputation."
      },
      'Verseau': {
        element: "Air",
        description: "Votre ascendant Verseau vous donne une apparence originale et avant-gardiste. Vous dégagez une indépendance d'esprit et une vision humanitaire. Les autres vous perçoivent comme quelqu'un d'unique et de visionnaire.",
        traits: "Original, indépendant, humanitaire, rebelle, visionnaire",
        influence: "Cet ascendant stimule votre individualité et votre conscience sociale. Il vous pousse à innover et à réformer."
      },
      'Poissons': {
        element: "Eau",
        description: "Votre ascendant Poissons vous confère une présence douce et spirituelle. Vous dégagez une sensibilité artistique et une compassion universelle. Les autres vous perçoivent comme quelqu'un d'inspiré et de compatissant.",
        traits: "Sensible, intuitif, artistique, rêveur, compatissant",
        influence: "Cet ascendant développe votre intuition et votre créativité. Il vous connecte aux dimensions spirituelles et artistiques de la vie."
      }
    };
    
    return interpretations[signe as keyof typeof interpretations] || interpretations['Bélier'];
  };

  const getLectureAme = () => {
    return {
      essence: "Votre âme porte en elle la sagesse des cycles cosmiques. Vous êtes venu(e) sur Terre pour expérimenter l'équilibre entre le matériel et le spirituel, entre l'action et la contemplation.",
      mission: "Votre mission d'âme consiste à être un pont entre les mondes, à traduire la sagesse spirituelle en actions concrètes. Vous êtes ici pour guider les autres vers leur propre lumière intérieure.",
      defis: "Votre principal défi est d'apprendre à faire confiance à votre intuition tout en restant ancré(e) dans la réalité. Vous devez équilibrer votre sensibilité avec votre force intérieure.",
      dons: "Vos dons spirituels incluent une intuition développée, une capacité de guérison naturelle, et un don pour percevoir les énergies subtiles. Vous avez également un talent pour inspirer et élever les autres.",
      guidance: "Cultivez la méditation et la connexion avec la nature. Votre chemin spirituel passe par l'acceptation de votre sensibilité comme une force, non comme une faiblesse. Faites confiance à votre guidance intérieure."
    };
  };

  const getConseilsAlignement = () => {
    return [
      {
        domaine: "Spiritualité",
        conseil: "Créez un rituel quotidien de connexion spirituelle, même de 10 minutes. La méditation, la prière ou la contemplation de la nature vous aideront à rester aligné(e)."
      },
      {
        domaine: "Relations",
        conseil: "Entourez-vous de personnes qui respectent votre sensibilité et encouragent votre croissance. Évitez les énergies toxiques qui drainent votre vitalité."
      },
      {
        domaine: "Carrière",
        conseil: "Choisissez un travail qui a du sens pour vous et qui vous permet d'exprimer vos dons naturels. L'argent viendra naturellement quand vous suivez votre passion."
      },
      {
        domaine: "Santé",
        conseil: "Écoutez votre corps et respectez ses besoins. Votre sensibilité vous rend plus réceptif(ve) aux énergies, alors protégez-vous et rechargez-vous régulièrement."
      },
      {
        domaine: "Créativité",
        conseil: "Exprimez votre créativité sous toutes ses formes. Que ce soit par l'art, l'écriture, la musique ou toute autre forme d'expression, laissez votre âme s'exprimer."
      }
    ];
  };

  const handleDownloadPDF = () => {
    // Simulation du téléchargement PDF
    alert('Génération du PDF en cours... Vous recevrez un email avec le lien de téléchargement.');
  };

  const handleSendEmail = () => {
    // Simulation de l'envoi par email
    alert(`Votre étude complète a été envoyée à ${userData?.email}`);
  };

  if (!userData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const cheminVieInfo = getCheminVieComplet(cheminVie);
  const ascendantInfo = getAscendantComplet(ascendant);
  const lectureAme = getLectureAme();
  const conseilsAlignement = getConseilsAlignement();

  return (
    <div className="min-h-screen py-12 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center items-center gap-4 mb-6">
            <Badge variant="secondary" className="bg-green-500/20 text-green-600 border-green-500/30">
              ✓ Étude Complète Débloquée
            </Badge>
          </div>
          
          <h1 className="text-4xl md:text-6xl font-bold mb-6 mystical-text">
            Votre Destinée Révélée
          </h1>
          {userData.prenom && (
            <p className="text-2xl text-accent mb-4">
              {userData.prenom}, découvrez qui vous êtes vraiment ✨
            </p>
          )}
          <p className="text-xl text-foreground/70 mb-8">
            Analyse personnalisée basée sur vos données de naissance
          </p>
          
          {/* Actions */}
          <div className="flex flex-wrap justify-center gap-4 mb-8">
            <Button onClick={handleDownloadPDF} className="golden-button">
              <Download className="w-4 h-4 mr-2" />
              Télécharger PDF
            </Button>
            <Button onClick={handleSendEmail} variant="outline" className="border-primary/30 hover:bg-primary/10">
              <Mail className="w-4 h-4 mr-2" />
              Envoyer par Email
            </Button>
            <Button variant="outline" className="border-primary/30 hover:bg-primary/10">
              <Share2 className="w-4 h-4 mr-2" />
              Partager
            </Button>
          </div>
        </div>

        {/* Contenu principal */}
        <Tabs defaultValue="numerologie" className="w-full">
          <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4 mb-8">
            <TabsTrigger value="numerologie" className="flex items-center gap-2">
              <Star className="w-4 h-4" />
              Numérologie
            </TabsTrigger>
            <TabsTrigger value="astrologie" className="flex items-center gap-2">
              <Moon className="w-4 h-4" />
              Astrologie
            </TabsTrigger>
            <TabsTrigger value="ame" className="flex items-center gap-2">
              <Heart className="w-4 h-4" />
              Lecture d'Âme
            </TabsTrigger>
            <TabsTrigger value="conseils" className="flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Conseils
            </TabsTrigger>
          </TabsList>

          {/* Numérologie */}
          <TabsContent value="numerologie" className="space-y-8">
            {/* Chemin de vie */}
            <Card className="mystical-card">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-full bg-primary/20 text-primary">
                    <Star className="w-8 h-8" />
                  </div>
                  <div>
                    <CardTitle className="text-3xl">Chemin de Vie : {cheminVie}</CardTitle>
                    <CardDescription className="text-xl text-accent">{cheminVieInfo.titre}</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold mb-3 text-primary">🎁 Vos Dons Naturels</h3>
                  <p className="text-foreground/80 leading-relaxed">{cheminVieInfo.dons}</p>
                </div>
                
                <Separator />
                
                <div>
                  <h3 className="text-xl font-semibold mb-3 text-accent">⚡ Vos Défis Principaux</h3>
                  <p className="text-foreground/80 leading-relaxed">{cheminVieInfo.defis}</p>
                </div>
                
                <Separator />
                
                <div>
                  <h3 className="text-xl font-semibold mb-3 text-primary">🌟 Votre Mission de Vie</h3>
                  <p className="text-foreground/80 leading-relaxed">{cheminVieInfo.mission}</p>
                </div>
                
                <Separator />
                
                <div className="bg-primary/10 p-6 rounded-lg border border-primary/20">
                  <h3 className="text-xl font-semibold mb-3 text-accent">💫 Conseils d'Évolution</h3>
                  <p className="text-foreground/80 leading-relaxed">{cheminVieInfo.conseils}</p>
                </div>
              </CardContent>
            </Card>

            {/* Année personnelle */}
            <Card className="mystical-card">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-full bg-secondary/20 text-accent">
                    <Sparkles className="w-8 h-8" />
                  </div>
                  <div>
                    <CardTitle className="text-3xl">Année Personnelle 2024 : {anneePersonnelle}</CardTitle>
                    <CardDescription className="text-xl">Vos énergies et opportunités cette année</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-primary">🎯 Focus de l'année</h3>
                    <p className="text-foreground/80">Cette année {anneePersonnelle} vous invite à vous concentrer sur le développement personnel et l'expansion de vos horizons.</p>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-accent">⏰ Périodes favorables</h3>
                    <p className="text-foreground/80">Mars-Mai et Septembre-Novembre seront particulièrement propices à vos projets et décisions importantes.</p>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-primary">💡 Opportunités</h3>
                    <p className="text-foreground/80">Nouvelles rencontres, projets créatifs, et développement spirituel seront au rendez-vous cette année.</p>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-accent">⚠️ Points d'attention</h3>
                    <p className="text-foreground/80">Évitez les décisions impulsives en juin-juillet. Prenez le temps de la réflexion avant d'agir.</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Astrologie */}
          <TabsContent value="astrologie" className="space-y-8">
            <Card className="mystical-card">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-full bg-primary/20 text-primary">
                    <Moon className="w-8 h-8" />
                  </div>
                  <div>
                    <CardTitle className="text-3xl">Ascendant {ascendant}</CardTitle>
                    <CardDescription className="text-xl">Élément {ascendantInfo.element} • Votre masque social</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold mb-3 text-primary">🎭 Votre Apparence Sociale</h3>
                  <p className="text-foreground/80 leading-relaxed">{ascendantInfo.description}</p>
                </div>
                
                <Separator />
                
                <div>
                  <h3 className="text-xl font-semibold mb-3 text-accent">✨ Traits Dominants</h3>
                  <p className="text-foreground/80 leading-relaxed">{ascendantInfo.traits}</p>
                </div>
                
                <Separator />
                
                <div className="bg-secondary/10 p-6 rounded-lg border border-secondary/20">
                  <h3 className="text-xl font-semibold mb-3 text-accent">🌟 Influence sur Votre Vie</h3>
                  <p className="text-foreground/80 leading-relaxed">{ascendantInfo.influence}</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Lecture d'âme */}
          <TabsContent value="ame" className="space-y-8">
            <Card className="mystical-card">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-full bg-accent/20 text-accent">
                    <Heart className="w-8 h-8" />
                  </div>
                  <div>
                    <CardTitle className="text-3xl">Lecture de Votre Âme</CardTitle>
                    <CardDescription className="text-xl">Votre essence spirituelle révélée</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold mb-3 text-primary">🌟 Votre Essence</h3>
                  <p className="text-foreground/80 leading-relaxed">{lectureAme.essence}</p>
                </div>
                
                <Separator />
                
                <div>
                  <h3 className="text-xl font-semibold mb-3 text-accent">🎯 Mission d'Âme</h3>
                  <p className="text-foreground/80 leading-relaxed">{lectureAme.mission}</p>
                </div>
                
                <Separator />
                
                <div>
                  <h3 className="text-xl font-semibold mb-3 text-primary">⚡ Défis Spirituels</h3>
                  <p className="text-foreground/80 leading-relaxed">{lectureAme.defis}</p>
                </div>
                
                <Separator />
                
                <div>
                  <h3 className="text-xl font-semibold mb-3 text-accent">🎁 Dons Spirituels</h3>
                  <p className="text-foreground/80 leading-relaxed">{lectureAme.dons}</p>
                </div>
                
                <div className="bg-accent/10 p-6 rounded-lg border border-accent/20">
                  <h3 className="text-xl font-semibold mb-3 text-accent">🧭 Guidance Spirituelle</h3>
                  <p className="text-foreground/80 leading-relaxed">{lectureAme.guidance}</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Conseils d'alignement */}
          <TabsContent value="conseils" className="space-y-8">
            <div className="grid gap-6">
              {conseilsAlignement.map((conseil, index) => (
                <Card key={index} className="mystical-card">
                  <CardHeader>
                    <CardTitle className="text-xl flex items-center gap-2">
                      <Zap className="w-6 h-6 text-accent" />
                      {conseil.domaine}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-foreground/80 leading-relaxed">{conseil.conseil}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>

        {/* Footer */}
        <div className="mt-16 text-center">
          <Card className="mystical-card bg-gradient-to-br from-primary/10 to-accent/10 border-primary/30">
            <CardContent className="p-8">
              <h2 className="text-2xl font-bold mb-4 mystical-text">
                Votre Voyage ne Fait que Commencer
              </h2>
              <p className="text-foreground/70 mb-6">
                Cette étude est un guide pour votre évolution personnelle. 
                Revisitez-la régulièrement pour approfondir votre compréhension de vous-même.
              </p>
              <p className="text-sm text-muted-foreground">
                Cet outil est un support de développement personnel et de réflexion intérieure. 
                Il ne remplace aucun avis médical, psychologique ou juridique.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Resultats;