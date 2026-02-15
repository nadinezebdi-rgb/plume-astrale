import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Moon, Lock, Sparkles, ArrowRight, Heart, Eye, Sun, Zap, Loader2 } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Apercu = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [cheminVie, setCheminVie] = useState(0);
  const [anneePersonnelle, setAnneePersonnelle] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const handlePurchase = async () => {
    setIsLoading(true);
    
    try {
      const response = await fetch(`${API_URL}/api/checkout/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_id: 'manuscrit',
          origin_url: window.location.origin,
          user_email: userData?.email || null,
          user_data: userData
        })
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la création du paiement');
      }

      const data = await response.json();
      
      // Redirect to Stripe Checkout
      if (data.url) {
        window.location.href = data.url;
      } else {
        throw new Error('URL de paiement non reçue');
      }
    } catch (error) {
      console.error('Payment error:', error);
      alert('Une erreur est survenue. Veuillez réessayer.');
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const data = localStorage.getItem('plume_astrale_data');
    if (!data) {
      navigate('/formulaire');
      return;
    }
    
    const parsedData = JSON.parse(data);
    setUserData(parsedData);
    
    // Calculs numérologie
    const dateNaissance = new Date(parsedData.dateNaissance);
    setCheminVie(calculerCheminVie(dateNaissance));
    setAnneePersonnelle(calculerAnneePersonnelle(dateNaissance));
  }, [navigate]);

  const calculerCheminVie = (date) => {
    const jour = date.getDate();
    const mois = date.getMonth() + 1;
    const annee = date.getFullYear();
    let somme = jour + mois + annee;
    
    while (somme > 9 && somme !== 11 && somme !== 22 && somme !== 33) {
      somme = somme.toString().split('').reduce((acc, digit) => acc + parseInt(digit), 0);
    }
    return somme;
  };

  const calculerAnneePersonnelle = (dateNaissance) => {
    const jour = dateNaissance.getDate();
    const mois = dateNaissance.getMonth() + 1;
    const anneeActuelle = new Date().getFullYear();
    let somme = jour + mois + anneeActuelle;
    
    while (somme > 9) {
      somme = somme.toString().split('').reduce((acc, digit) => acc + parseInt(digit), 0);
    }
    return somme;
  };

  const getCheminVieInfo = (chemin) => {
    const interpretations = {
      1: { titre: "Le Pionnier", apercu: "Vous êtes né(e) pour diriger et innover. Votre énergie naturelle vous pousse vers l'indépendance et la création de nouveaux chemins." },
      2: { titre: "Le Diplomate", apercu: "Votre don pour l'harmonie fait de vous un médiateur naturel. Sensibilité et coopération sont vos forces." },
      3: { titre: "L'Artiste", apercu: "Créativité et communication sont vos forces. Vous inspirez les autres par votre joie de vivre et votre expression unique." },
      4: { titre: "Le Bâtisseur", apercu: "Stabilité et méthode caractérisent votre approche. Vous construisez des fondations solides pour l'avenir." },
      5: { titre: "L'Aventurier", apercu: "Liberté et changement nourrissent votre âme. Vous êtes fait(e) pour explorer de nouveaux horizons." },
      6: { titre: "Le Guérisseur", apercu: "Amour et service aux autres définissent votre essence. Vous êtes un pilier de soutien pour votre entourage." },
      7: { titre: "Le Sage", apercu: "Recherche spirituelle et analyse profonde vous caractérisent. Vous cherchez la vérité au-delà des apparences." },
      8: { titre: "Le Leader", apercu: "Ambition et réussite matérielle vous motivent. Vous transformez les idées en succès concrets." },
      9: { titre: "L'Humanitaire", apercu: "Compassion universelle et service à l'humanité vous animent. Vous élevez la conscience collective." },
      11: { titre: "L'Inspirateur", apercu: "Intuition et inspiration vous connectent aux dimensions supérieures. Vous êtes un canal de lumière." },
      22: { titre: "Le Maître Bâtisseur", apercu: "Vision et réalisation se conjuguent en vous. Vous matérialisez des projets d'envergure mondiale." },
      33: { titre: "Le Maître Guérisseur", apercu: "Amour inconditionnel et sagesse universelle émanent de vous. Vous guidez l'humanité vers l'élévation." }
    };
    return interpretations[chemin] || interpretations[1];
  };

  const getAnneePersonnelleInfo = (annee) => {
    const interpretations = {
      1: { titre: "Nouveaux Départs", apercu: "2026 marque un nouveau cycle. C'est le moment d'initier des projets majeurs." },
      2: { titre: "Coopération", apercu: "Cette année favorise les partenariats. Patience et diplomatie sont vos atouts." },
      3: { titre: "Créativité", apercu: "Votre créativité s'épanouit. Expression artistique et communication sont favorisées." },
      4: { titre: "Construction", apercu: "Travail et organisation sont à l'honneur. Posez des bases solides." },
      5: { titre: "Liberté", apercu: "Changements et nouvelles expériences vous attendent. Embrassez l'aventure." },
      6: { titre: "Responsabilité", apercu: "Famille et responsabilités sont au centre. Votre rôle de soutien est essentiel." },
      7: { titre: "Réflexion", apercu: "Introspection et développement spirituel sont favorisés. Prenez du temps pour vous." },
      8: { titre: "Réussite", apercu: "Succès matériel et reconnaissance sont à portée. Votre ambition porte ses fruits." },
      9: { titre: "Accomplissement", apercu: "Fin d'un cycle. C'est le moment de partager vos acquis et préparer le renouveau." }
    };
    return interpretations[annee] || interpretations[1];
  };

  const lockedSections = [
    { icon: <Sun className="w-6 h-6" strokeWidth={1} />, title: "Identité Céleste", desc: "Soleil, Lune & Ascendant" },
    { icon: <Heart className="w-6 h-6" strokeWidth={1} />, title: "Cœur & Relations", desc: "Venus, Mars & Synthèse affective" },
    { icon: <Zap className="w-6 h-6" strokeWidth={1} />, title: "Défis & Talents", desc: "Aspects planétaires révélés" },
    { icon: <Eye className="w-6 h-6" strokeWidth={1} />, title: "Conseil de la Plume", desc: "Guidance personnalisée 2026" }
  ];

  if (!userData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-2 border-[#C5A059] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const cheminVieInfo = getCheminVieInfo(cheminVie);
  const anneePersonnelleInfo = getAnneePersonnelleInfo(anneePersonnelle);

  return (
    <div className="min-h-screen relative">
      <StarField />
      
      <div className="relative z-10 py-12 px-4 md:px-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-4 font-light animate-fade-in">
              Votre Aperçu Cosmique
            </p>
            
            <h1 className="text-3xl md:text-5xl mb-4 animate-slide-up opacity-0 stagger-1" 
                style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              {userData.prenom ? `${userData.prenom}, ` : ''}Les Étoiles Vous Parlent
            </h1>
            
            <p className="text-lg text-[#E0D9F6]/70 font-light animate-slide-up opacity-0 stagger-2">
              Découvrez les premiers secrets de votre destinée
            </p>
          </div>

          {/* Progress Steps */}
          <div className="flex justify-center items-center gap-4 mb-12 text-sm animate-slide-up opacity-0 stagger-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-[#C5A059] text-[#0F0518] flex items-center justify-center font-semibold">✓</div>
              <span className="text-[#C5A059]">Informations</span>
            </div>
            <ArrowRight className="w-4 h-4 text-[#E0D9F6]/30" />
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-[#C5A059] text-[#0F0518] flex items-center justify-center font-semibold">2</div>
              <span className="text-[#C5A059]">Aperçu</span>
            </div>
            <ArrowRight className="w-4 h-4 text-[#E0D9F6]/30" />
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full border border-[#C5A059]/30 text-[#E0D9F6]/50 flex items-center justify-center font-semibold">3</div>
              <span className="text-[#E0D9F6]/50">Étude complète</span>
            </div>
          </div>

          {/* Free Content */}
          <div className="space-y-8 mb-12">
            {/* Chemin de Vie */}
            <div className="card-mystical animate-slide-up opacity-0 stagger-4" data-testid="chemin-vie-card">
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className="p-4 rounded-full bg-[#C5A059]/10 text-[#C5A059]">
                    <Star className="w-8 h-8" strokeWidth={1} />
                  </div>
                  <div>
                    <h2 className="text-2xl md:text-3xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                      Chemin de Vie : {cheminVie}
                    </h2>
                    <p className="text-[#C5A059] text-lg">{cheminVieInfo.titre}</p>
                  </div>
                </div>
                <span className="px-4 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-sm border border-emerald-500/30">
                  Gratuit
                </span>
              </div>
              
              <p className="text-[#E0D9F6]/80 text-lg leading-relaxed mb-6 font-light">
                {cheminVieInfo.apercu}
              </p>
              
              <div className="bg-[#1A0B2E]/50 rounded-xl p-6 border border-[#C5A059]/10">
                <div className="flex items-start gap-3">
                  <Lock className="w-5 h-5 text-[#C5A059]/50 mt-1 flex-shrink-0" />
                  <div>
                    <p className="text-[#E0D9F6]/60 mb-2 font-medium">Dans l'étude complète :</p>
                    <p className="text-[#E0D9F6]/40 text-sm italic font-light">
                      Dons naturels, défis principaux, mission de vie détaillée, conseils d'évolution personnalisés...
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Année Personnelle */}
            <div className="card-mystical animate-slide-up opacity-0 stagger-5" data-testid="annee-personnelle-card">
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className="p-4 rounded-full bg-[#C5A059]/10 text-[#C5A059]">
                    <Moon className="w-8 h-8" strokeWidth={1} />
                  </div>
                  <div>
                    <h2 className="text-2xl md:text-3xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                      Année 2026 : {anneePersonnelle}
                    </h2>
                    <p className="text-[#C5A059] text-lg">{anneePersonnelleInfo.titre}</p>
                  </div>
                </div>
                <span className="px-4 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-sm border border-emerald-500/30">
                  Gratuit
                </span>
              </div>
              
              <p className="text-[#E0D9F6]/80 text-lg leading-relaxed mb-6 font-light">
                {anneePersonnelleInfo.apercu}
              </p>
              
              <div className="bg-[#1A0B2E]/50 rounded-xl p-6 border border-[#C5A059]/10">
                <div className="flex items-start gap-3">
                  <Lock className="w-5 h-5 text-[#C5A059]/50 mt-1 flex-shrink-0" />
                  <div>
                    <p className="text-[#E0D9F6]/60 mb-2 font-medium">Dans l'étude complète :</p>
                    <p className="text-[#E0D9F6]/40 text-sm italic font-light">
                      Conseils mois par mois, périodes favorables, défis à anticiper, stratégies d'alignement...
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Locked Content Preview */}
          <div className="grid md:grid-cols-2 gap-6 mb-12">
            {lockedSections.map((section, index) => (
              <div 
                key={index}
                className="card-mystical opacity-60 relative overflow-hidden"
                data-testid={`locked-section-${index}`}
              >
                <div className="absolute inset-0 bg-[#0F0518]/60 backdrop-blur-sm z-10 flex items-center justify-center">
                  <Lock className="w-8 h-8 text-[#C5A059]/50" />
                </div>
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-full bg-[#2D1B4E]/50 text-[#E0D9F6]/30">
                    {section.icon}
                  </div>
                  <div>
                    <h3 className="text-xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                      {section.title}
                    </h3>
                    <p className="text-[#E0D9F6]/40 text-sm">{section.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* CTA Manuscrit Premium */}
          <div className="card-mystical text-center p-10 md:p-14 glow-gold">
            <Sparkles className="w-12 h-12 text-[#C5A059] mx-auto mb-6" strokeWidth={1} />
            
            <h2 className="text-2xl md:text-4xl mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Le Manuscrit de la Plume
            </h2>
            
            <p className="text-[#E0D9F6]/80 mb-6 max-w-xl mx-auto font-light text-lg leading-relaxed">
              Un trésor céleste à conserver précieusement toute votre vie.
            </p>
            
            <p className="text-[#E0D9F6]/60 mb-8 max-w-xl mx-auto font-light leading-relaxed">
              Ce manuscrit unique, créé spécialement pour vous, deviendra votre guide spirituel personnel. 
              Vous y reviendrez encore et encore, découvrant de nouvelles révélations à chaque lecture.
            </p>
            
            <div className="flex flex-wrap justify-center gap-6 mb-10 text-sm">
              <div className="flex items-center gap-2 text-[#E0D9F6]/70">
                <Star className="w-5 h-5 text-[#C5A059]" strokeWidth={1} />
                <span>Analyse complète de votre âme</span>
              </div>
              <div className="flex items-center gap-2 text-[#E0D9F6]/70">
                <Moon className="w-5 h-5 text-[#C5A059]" strokeWidth={1} />
                <span>Guidance personnalisée 2026</span>
              </div>
              <div className="flex items-center gap-2 text-[#E0D9F6]/70">
                <Heart className="w-5 h-5 text-[#C5A059]" strokeWidth={1} />
                <span>Document PDF à garder pour toujours</span>
              </div>
            </div>
            
            <div className="mb-10 py-6 border-t border-b border-[#C5A059]/20">
              <div className="text-5xl font-bold text-gold-gradient mb-2" style={{ fontFamily: 'Cinzel, serif' }}>
                29,90€
              </div>
              <p className="text-[#C5A059]/80 text-sm">
                Un investissement unique pour une guidance éternelle
              </p>
            </div>
            
            <button 
              onClick={() => navigate('/paiement', { state: { plan: 'manuscrit', price: 29.90 } })}
              className="btn-mystical-filled rounded-full flex items-center gap-3 mx-auto animate-glow-pulse text-lg px-10 py-4"
              data-testid="cta-unlock-full"
            >
              <Sparkles className="w-6 h-6" />
              Recevoir Mon Manuscrit de la Plume
            </button>
            
            <p className="text-[#E0D9F6]/50 text-sm mt-6 font-light">
              Accès immédiat après paiement • Téléchargement illimité
            </p>
            
            <div className="mt-8 pt-6 border-t border-[#C5A059]/10">
              <p className="text-[#E0D9F6]/40 text-xs italic">
                "Ce manuscrit m'accompagne chaque jour. C'est devenu mon livre de chevet spirituel." — Marie L.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Apercu;
