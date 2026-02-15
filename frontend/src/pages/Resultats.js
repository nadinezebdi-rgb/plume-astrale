import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Moon, Heart, Zap, Download, Mail, Share2, Sparkles, Sun, Eye, CheckCircle, Loader2, Book, Gift } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Resultats = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [activeTab, setActiveTab] = useState('identite');
  const [cheminVie, setCheminVie] = useState(0);
  const [anneePersonnelle, setAnneePersonnelle] = useState(0);
  const [ascendant, setAscendant] = useState('');
  const [planetsData, setPlanetsData] = useState(null);
  const [horoscopeData, setHoroscopeData] = useState(null);
  const [zodiacSign, setZodiacSign] = useState('');
  const [zodiacFrench, setZodiacFrench] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);

  const downloadPDF = async () => {
    setIsDownloading(true);
    try {
      const response = await fetch(`${API_URL}/api/pdf/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_data: userData })
      });

      if (!response.ok) throw new Error('PDF generation failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `manuscrit_plume_${userData?.prenom || 'celestial'}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download error:', error);
      alert('Erreur lors du téléchargement. Veuillez réessayer.');
    }
    setIsDownloading(false);
  };

  useEffect(() => {
    const loadData = async () => {
      const data = localStorage.getItem('plume_astrale_data');
      const paid = localStorage.getItem('plume_astrale_paid');
      
      if (!data || !paid) {
        navigate('/formulaire');
        return;
      }
      
      const parsedData = JSON.parse(data);
      setUserData(parsedData);
      
      const dateNaissance = new Date(parsedData.dateNaissance);
      setCheminVie(calculerCheminVie(dateNaissance));
      setAnneePersonnelle(calculerAnneePersonnelle(dateNaissance));
      
      // Fetch real astrology data from API
      try {
        // Get planets data
        const planetsResponse = await fetch(`${API_URL}/api/astrology/planets`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            date_naissance: parsedData.dateNaissance,
            heure_naissance: parsedData.heureNaissance,
            ville: parsedData.ville,
            pays: parsedData.pays
          })
        });
        
        if (planetsResponse.ok) {
          const planetsResult = await planetsResponse.json();
          if (planetsResult.success) {
            setPlanetsData(planetsResult.data);
            
            // Find Sun sign and Ascendant from API data
            const sunData = planetsResult.data.find(p => p.name === 'Sun');
            const ascendantData = planetsResult.data.find(p => p.name === 'Ascendant');
            
            if (sunData) {
              setZodiacSign(sunData.sign);
              setZodiacFrench(getSigneFrancais(sunData.sign));
            }
            
            if (ascendantData) {
              setAscendant(getSigneFrancais(ascendantData.sign));
            } else {
              setAscendant(calculerAscendant(parsedData));
            }
          }
        }
        
        // Get horoscope data
        const horoscopeResponse = await fetch(`${API_URL}/api/astrology/horoscope`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            date_naissance: parsedData.dateNaissance,
            heure_naissance: parsedData.heureNaissance,
            ville: parsedData.ville,
            pays: parsedData.pays
          })
        });
        
        if (horoscopeResponse.ok) {
          const horoscopeResult = await horoscopeResponse.json();
          if (horoscopeResult.success) {
            setHoroscopeData(horoscopeResult.data);
            setZodiacFrench(horoscopeResult.zodiac_french);
          }
        }
        
      } catch (error) {
        console.error('Error fetching astrology data:', error);
        // Fallback to calculated ascendant
        setAscendant(calculerAscendant(parsedData));
      }
      
      setIsLoading(false);
    };
    
    loadData();
  }, [navigate]);

  const getSigneFrancais = (sign) => {
    const signes = {
      'Aries': 'Bélier', 'Taurus': 'Taureau', 'Gemini': 'Gémeaux',
      'Cancer': 'Cancer', 'Leo': 'Lion', 'Virgo': 'Vierge',
      'Libra': 'Balance', 'Scorpio': 'Scorpion', 'Sagittarius': 'Sagittaire',
      'Capricorn': 'Capricorne', 'Aquarius': 'Verseau', 'Pisces': 'Poissons'
    };
    return signes[sign] || sign;
  };

  const getElementFromSign = (sign) => {
    const elements = {
      'Bélier': 'Feu', 'Lion': 'Feu', 'Sagittaire': 'Feu',
      'Taureau': 'Terre', 'Vierge': 'Terre', 'Capricorne': 'Terre',
      'Gémeaux': 'Air', 'Balance': 'Air', 'Verseau': 'Air',
      'Cancer': 'Eau', 'Scorpion': 'Eau', 'Poissons': 'Eau'
    };
    return elements[sign] || 'Terre';
  };

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

  const calculerAscendant = (data) => {
    const heure = parseInt(data.heureNaissance.split(':')[0]);
    const signes = ['Bélier', 'Taureau', 'Gémeaux', 'Cancer', 'Lion', 'Vierge', 'Balance', 'Scorpion', 'Sagittaire', 'Capricorne', 'Verseau', 'Poissons'];
    return signes[heure % 12];
  };

  const tabs = [
    { id: 'identite', label: 'Identité Céleste', icon: <Sun className="w-4 h-4" strokeWidth={1} /> },
    { id: 'mission', label: 'Mission de Vie', icon: <Star className="w-4 h-4" strokeWidth={1} /> },
    { id: 'coeur', label: 'Cœur & Relations', icon: <Heart className="w-4 h-4" strokeWidth={1} /> },
    { id: 'defis', label: 'Défis & Talents', icon: <Zap className="w-4 h-4" strokeWidth={1} /> },
    { id: 'conseil', label: 'Conseil de la Plume', icon: <Eye className="w-4 h-4" strokeWidth={1} /> }
  ];

  const getCheminVieComplet = (chemin) => {
    const interpretations = {
      1: { titre: "Le Pionnier", dons: "Leadership naturel, indépendance, innovation, courage, détermination", defis: "Impatience, égocentrisme, tendance à l'isolement", mission: "Ouvrir de nouveaux chemins, inspirer l'autonomie chez les autres", conseils: "Cultivez la patience, apprenez à déléguer, équilibrez votre besoin d'indépendance avec la coopération." },
      2: { titre: "Le Diplomate", dons: "Empathie, coopération, sens de l'harmonie, intuition, médiation", defis: "Hypersensibilité, indécision, tendance à s'effacer", mission: "Créer l'harmonie, faciliter la coopération, guérir les relations", conseils: "Affirmez-vous davantage, fixez des limites saines, développez votre confiance en vous." },
      3: { titre: "L'Artiste", dons: "Créativité, communication, joie de vivre, inspiration artistique", defis: "Dispersion, superficialité, procrastination", mission: "Inspirer par l'art et la beauté, communiquer la joie, élever les vibrations", conseils: "Focalisez votre énergie créative, développez la discipline, approfondissez vos talents." },
      4: { titre: "Le Bâtisseur", dons: "Organisation, persévérance, fiabilité, sens pratique", defis: "Rigidité, résistance au changement, perfectionnisme", mission: "Construire des fondations solides, organiser et structurer", conseils: "Acceptez le changement comme opportunité, prenez du temps pour vous détendre." },
      5: { titre: "L'Aventurier", dons: "Liberté, adaptabilité, curiosité, esprit d'aventure", defis: "Instabilité, impatience, difficulté d'engagement", mission: "Élargir les horizons, apporter le changement, connecter les cultures", conseils: "Trouvez l'équilibre entre liberté et responsabilité." },
      6: { titre: "Le Guérisseur", dons: "Amour inconditionnel, compassion, sens du service", defis: "Sacrifice excessif, porter les problèmes des autres", mission: "Guérir et nourrir, créer l'harmonie familiale", conseils: "Prenez soin de vous autant que des autres." },
      7: { titre: "Le Sage", dons: "Sagesse intuitive, analyse profonde, spiritualité", defis: "Isolement, analyse excessive", mission: "Rechercher et transmettre la sagesse spirituelle", conseils: "Partagez votre sagesse avec le monde." },
      8: { titre: "Le Leader", dons: "Ambition constructive, sens des affaires, leadership", defis: "Matérialisme excessif, tendance à dominer", mission: "Créer l'abondance éthique, diriger avec intégrité", conseils: "Utilisez votre pouvoir avec sagesse." },
      9: { titre: "L'Humanitaire", dons: "Compassion universelle, vision globale, générosité", defis: "Idéalisme excessif, difficulté avec les détails", mission: "Servir l'humanité, élever la conscience collective", conseils: "Ancrez vos idéaux dans la réalité." },
      11: { titre: "L'Inspirateur", dons: "Intuition développée, inspiration spirituelle, charisme", defis: "Hypersensibilité, nervosité, difficulté à s'ancrer", mission: "Inspirer et élever les autres, canaliser la lumière", conseils: "Ancrez votre sensibilité dans le concret." },
      22: { titre: "Le Maître Bâtisseur", dons: "Vision globale, réalisation exceptionnelle", defis: "Pression énorme, perfectionnisme", mission: "Matérialiser des projets d'envergure mondiale", conseils: "Acceptez votre mission avec humilité." }
    };
    return interpretations[chemin] || interpretations[1];
  };

  const getAscendantComplet = (signe) => {
    const interpretations = {
      'Bélier': { element: "Feu", description: "Votre ascendant Bélier vous donne une apparence dynamique et énergique. Vous dégagez une aura de leadership naturel.", traits: "Spontané, énergique, direct, courageux" },
      'Taureau': { element: "Terre", description: "Votre ascendant Taureau vous confère une présence stable et rassurante.", traits: "Stable, patient, sensuel, déterminé" },
      'Gémeaux': { element: "Air", description: "Votre ascendant Gémeaux vous donne une apparence vive et communicative.", traits: "Curieux, communicatif, adaptable" },
      'Cancer': { element: "Eau", description: "Votre ascendant Cancer vous confère une présence douce et protectrice.", traits: "Sensible, protecteur, intuitif" },
      'Lion': { element: "Feu", description: "Votre ascendant Lion vous donne une présence majestueuse et charismatique.", traits: "Charismatique, généreux, créatif" },
      'Vierge': { element: "Terre", description: "Votre ascendant Vierge vous confère une apparence soignée et méthodique.", traits: "Méticuleux, analytique, serviable" },
      'Balance': { element: "Air", description: "Votre ascendant Balance vous donne une présence harmonieuse et diplomatique.", traits: "Harmonieux, diplomatique, esthète" },
      'Scorpion': { element: "Eau", description: "Votre ascendant Scorpion vous confère une présence intense et magnétique.", traits: "Intense, magnétique, transformateur" },
      'Sagittaire': { element: "Feu", description: "Votre ascendant Sagittaire vous donne une apparence optimiste et aventureuse.", traits: "Optimiste, philosophe, aventurier" },
      'Capricorne': { element: "Terre", description: "Votre ascendant Capricorne vous confère une présence sérieuse et ambitieuse.", traits: "Ambitieux, responsable, patient" },
      'Verseau': { element: "Air", description: "Votre ascendant Verseau vous donne une apparence originale et avant-gardiste.", traits: "Original, indépendant, visionnaire" },
      'Poissons': { element: "Eau", description: "Votre ascendant Poissons vous confère une présence douce et spirituelle.", traits: "Sensible, intuitif, artistique" }
    };
    return interpretations[signe] || interpretations['Bélier'];
  };

  const aspectsPlanetaires = [
    { aspect: "Trigone", planetes: "Soleil - Jupiter", description: "Favorise l'expansion personnelle et l'optimisme. Vous attirez naturellement la chance." },
    { aspect: "Carré", planetes: "Lune - Saturne", description: "Tension entre émotions et structure. Invitation à équilibrer vulnérabilité et discipline." },
    { aspect: "Trigone", planetes: "Vénus - Neptune", description: "Sublime sensibilité artistique et amour inconditionnel. Vous percevez la beauté invisible." },
    { aspect: "Sextile", planetes: "Mars - Uranus", description: "Stimule l'audace créative et l'innovation. Talent pour les solutions originales." }
  ];

  const conseilsAlignement = [
    { domaine: "Spiritualité", conseil: "Créez un rituel quotidien de connexion spirituelle. La méditation vous aidera à rester aligné(e)." },
    { domaine: "Relations", conseil: "Entourez-vous de personnes qui respectent votre sensibilité et encouragent votre croissance." },
    { domaine: "Carrière", conseil: "Choisissez un travail qui a du sens et vous permet d'exprimer vos dons naturels." },
    { domaine: "Santé", conseil: "Écoutez votre corps et respectez ses besoins. Votre sensibilité vous rend réceptif aux énergies." },
    { domaine: "Créativité", conseil: "Exprimez votre créativité sous toutes ses formes. Laissez votre âme s'exprimer." }
  ];

  if (!userData || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-[#C5A059] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-[#E0D9F6]/70">Calcul de votre thème astral...</p>
        </div>
      </div>
    );
  }

  const cheminVieInfo = getCheminVieComplet(cheminVie);
  const ascendantInfo = getAscendantComplet(ascendant);
  
  // Get planet data for display
  const sunPlanet = planetsData?.find(p => p.name === 'Sun');
  const moonPlanet = planetsData?.find(p => p.name === 'Moon');
  const venusPlanet = planetsData?.find(p => p.name === 'Venus');
  const marsPlanet = planetsData?.find(p => p.name === 'Mars');
  const mercuryPlanet = planetsData?.find(p => p.name === 'Mercury');
  const jupiterPlanet = planetsData?.find(p => p.name === 'Jupiter');
  const saturnPlanet = planetsData?.find(p => p.name === 'Saturn');
  const ascendantPlanet = planetsData?.find(p => p.name === 'Ascendant');
  
  // Build aspects from horoscope data
  const realAspects = horoscopeData?.aspects?.slice(0, 6) || aspectsPlanetaires;

  return (
    <div className="min-h-screen relative">
      <StarField />
      
      <div className="relative z-10 py-12 px-4 md:px-6">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/20 text-emerald-400 text-sm border border-emerald-500/30 mb-6">
              <CheckCircle className="w-4 h-4" />
              <span>Étude Complète Débloquée</span>
            </div>
            
            <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Votre Manuscrit Céleste
            </h1>
            
            {userData.prenom && (
              <p className="text-xl text-[#C5A059] mb-4">
                {userData.prenom}, découvrez qui vous êtes vraiment
              </p>
            )}
            
            <p className="text-[#E0D9F6]/70 font-light">
              Analyse personnalisée basée sur vos données de naissance
            </p>
            
            {/* Actions */}
            <div className="flex flex-wrap justify-center gap-4 mt-8">
              <button 
                onClick={downloadPDF}
                disabled={isDownloading}
                className="btn-mystical-filled rounded-full flex items-center gap-2 text-sm disabled:opacity-50" 
                data-testid="btn-download"
              >
                {isDownloading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Download className="w-4 h-4" strokeWidth={1} />
                )}
                {isDownloading ? 'Génération...' : 'Télécharger PDF'}
              </button>
              <button className="btn-mystical rounded-full flex items-center gap-2 text-sm" data-testid="btn-email">
                <Mail className="w-4 h-4" strokeWidth={1} />
                Envoyer par Email
              </button>
              <button className="btn-mystical rounded-full flex items-center gap-2 text-sm" data-testid="btn-share">
                <Share2 className="w-4 h-4" strokeWidth={1} />
                Partager
              </button>
            </div>
            
            {/* Book promotion */}
            <div className="mt-8 p-4 rounded-xl bg-gradient-to-r from-[#C5A059]/10 to-transparent border border-[#C5A059]/30">
              <div className="flex flex-col sm:flex-row items-center gap-4">
                <div className="flex items-center gap-3">
                  <Gift className="w-8 h-8 text-[#C5A059]" />
                  <div className="text-left">
                    <p className="text-[#F3E5AB] font-medium">Envie d'un livre à offrir ?</p>
                    <p className="text-[#E0D9F6]/60 text-sm">Recevez votre manuscrit imprimé en édition reliée</p>
                  </div>
                </div>
                <button
                  onClick={() => navigate('/livre')}
                  className="btn-mystical rounded-full flex items-center gap-2 text-sm whitespace-nowrap"
                  data-testid="btn-order-book"
                >
                  <Book className="w-4 h-4" />
                  Commander le livre • 49,90€
                </button>
              </div>
            </div>
          </div>

          {/* Tabs Navigation */}
          <div className="flex flex-wrap justify-center gap-2 mb-12">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-3 rounded-full text-sm transition-all duration-300 ${
                  activeTab === tab.id 
                    ? 'bg-[#C5A059] text-[#0F0518]' 
                    : 'bg-[#1A0B2E]/50 text-[#E0D9F6]/70 hover:bg-[#1A0B2E] border border-[#C5A059]/20'
                }`}
                data-testid={`tab-${tab.id}`}
              >
                {tab.icon}
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="space-y-8">
            {/* Section 1: Identité Céleste */}
            {activeTab === 'identite' && (
              <div className="space-y-8 animate-fade-in">
                {/* Soleil */}
                <div className="card-mystical">
                  <div className="flex items-start justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <div className="p-4 rounded-full bg-[#C5A059]/10 text-[#C5A059]">
                        <Sun className="w-8 h-8" strokeWidth={1} />
                      </div>
                      <div>
                        <h2 className="text-2xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                          Votre Soleil
                        </h2>
                        <p className="text-[#C5A059]">
                          {sunPlanet ? `${getSigneFrancais(sunPlanet.sign)} • Maison ${sunPlanet.house}` : `Chemin de Vie ${cheminVie}`}
                        </p>
                      </div>
                    </div>
                    {sunPlanet && (
                      <div className="text-right">
                        <span className="text-[#E0D9F6]/50 text-sm">Position</span>
                        <p className="text-[#C5A059]">{sunPlanet.normDegree?.toFixed(1)}°</p>
                      </div>
                    )}
                  </div>
                  <p className="text-[#E0D9F6]/80 leading-relaxed font-light mb-6">
                    {sunPlanet ? (
                      <>
                        Votre Soleil en <span className="text-[#C5A059]">{getSigneFrancais(sunPlanet.sign)}</span> révèle 
                        votre essence profonde et votre identité fondamentale. Situé dans la <span className="text-[#C5A059]">Maison {sunPlanet.house}</span>, 
                        il éclaire particulièrement le domaine de votre vie lié à cette maison. 
                        Combiné à votre chemin de vie {cheminVie} ({cheminVieInfo.titre}), vous rayonnez d'une énergie unique.
                      </>
                    ) : (
                      <>
                        Votre essence fondamentale rayonne d'une énergie unique. Votre Soleil, combiné à votre chemin de vie {cheminVie}, 
                        révèle une nature profondément créative et visionnaire. Vous êtes venu(e) sur Terre pour manifester 
                        cette lumière intérieure de manière authentique.
                      </>
                    )}
                  </p>
                  {sunPlanet && (
                    <div className="bg-[#1A0B2E]/50 rounded-xl p-4 border border-[#C5A059]/10">
                      <p className="text-[#C5A059] text-sm mb-2">Caractéristiques du Soleil en {getSigneFrancais(sunPlanet.sign)}</p>
                      <p className="text-[#E0D9F6]/60 font-light text-sm">
                        Élément {getElementFromSign(getSigneFrancais(sunPlanet.sign))} • 
                        {sunPlanet.isRetro === 'true' ? ' Rétrograde' : ' Direct'} • 
                        Vitesse {sunPlanet.speed?.toFixed(2)}°/jour
                      </p>
                    </div>
                  )}
                </div>

                {/* Lune */}
                <div className="card-mystical">
                  <div className="flex items-start justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <div className="p-4 rounded-full bg-[#C5A059]/10 text-[#C5A059]">
                        <Moon className="w-8 h-8" strokeWidth={1} />
                      </div>
                      <div>
                        <h2 className="text-2xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                          Votre Lune
                        </h2>
                        <p className="text-[#C5A059]">
                          {moonPlanet ? `${getSigneFrancais(moonPlanet.sign)} • Maison ${moonPlanet.house}` : 'Votre monde émotionnel'}
                        </p>
                      </div>
                    </div>
                    {moonPlanet && (
                      <div className="text-right">
                        <span className="text-[#E0D9F6]/50 text-sm">Position</span>
                        <p className="text-[#C5A059]">{moonPlanet.normDegree?.toFixed(1)}°</p>
                      </div>
                    )}
                  </div>
                  <p className="text-[#E0D9F6]/80 leading-relaxed font-light">
                    {moonPlanet ? (
                      <>
                        Votre Lune en <span className="text-[#C5A059]">{getSigneFrancais(moonPlanet.sign)}</span> représente 
                        votre moi caché, votre monde émotionnel et votre sensibilité intérieure. 
                        Influencée par l'élément {getElementFromSign(getSigneFrancais(moonPlanet.sign))}, vous possédez 
                        une intelligence émotionnelle remarquable. La Maison {moonPlanet.house} colore la façon dont vous 
                        exprimez et nourrissez vos émotions.
                      </>
                    ) : (
                      <>
                        Votre Lune représente votre moi caché, votre monde émotionnel et votre sensibilité intérieure. 
                        Influencée par l'élément Terre, vous possédez une intelligence émotionnelle remarquable. 
                        Vous percevez les non-dits, ressentez les énergies ambiantes et naviguez avec aisance 
                        dans l'océan des émotions.
                      </>
                    )}
                  </p>
                </div>

                {/* Ascendant */}
                <div className="card-mystical">
                  <div className="flex items-start justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <div className="p-4 rounded-full bg-[#C5A059]/10 text-[#C5A059]">
                        <Star className="w-8 h-8" strokeWidth={1} />
                      </div>
                      <div>
                        <h2 className="text-2xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                          Ascendant {ascendantPlanet ? getSigneFrancais(ascendantPlanet.sign) : ascendant}
                        </h2>
                        <p className="text-[#C5A059]">
                          Élément {ascendantPlanet ? getElementFromSign(getSigneFrancais(ascendantPlanet.sign)) : ascendantInfo.element} • Votre masque social
                        </p>
                      </div>
                    </div>
                    {ascendantPlanet && (
                      <div className="text-right">
                        <span className="text-[#E0D9F6]/50 text-sm">Position</span>
                        <p className="text-[#C5A059]">{ascendantPlanet.normDegree?.toFixed(1)}°</p>
                      </div>
                    )}
                  </div>
                  <p className="text-[#E0D9F6]/80 leading-relaxed font-light mb-4">
                    {ascendantPlanet ? (
                      <>
                        Votre Ascendant en <span className="text-[#C5A059]">{getSigneFrancais(ascendantPlanet.sign)}</span> est 
                        votre masque social, la première impression que vous donnez aux autres. Il influence votre apparence 
                        physique et votre façon d'aborder le monde.
                      </>
                    ) : (
                      ascendantInfo.description
                    )}
                  </p>
                  <div className="bg-[#1A0B2E]/50 rounded-xl p-4 border border-[#C5A059]/10">
                    <p className="text-[#C5A059] text-sm mb-2">Traits dominants</p>
                    <p className="text-[#E0D9F6]/60 font-light">{ascendantInfo.traits}</p>
                  </div>
                </div>

                {/* Planètes supplémentaires */}
                {planetsData && (
                  <div className="card-mystical">
                    <h3 className="text-xl mb-6" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                      Positions Planétaires Complètes
                    </h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      {planetsData.filter(p => !['Sun', 'Moon', 'Ascendant'].includes(p.name)).slice(0, 6).map((planet, index) => (
                        <div key={index} className="bg-[#1A0B2E]/50 rounded-xl p-4 border border-[#C5A059]/10">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="text-[#F3E5AB]">{planet.name}</p>
                              <p className="text-[#C5A059] text-sm">{getSigneFrancais(planet.sign)}</p>
                            </div>
                            <div className="text-right">
                              <p className="text-[#E0D9F6]/60 text-sm">Maison {planet.house}</p>
                              <p className="text-[#E0D9F6]/40 text-xs">{planet.normDegree?.toFixed(1)}°</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Section 2: Mission de Vie */}
            {activeTab === 'mission' && (
              <div className="space-y-8 animate-fade-in">
                <div className="card-mystical">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="p-4 rounded-full bg-[#C5A059]/10 text-[#C5A059]">
                      <Star className="w-8 h-8" strokeWidth={1} />
                    </div>
                    <div>
                      <h2 className="text-2xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                        Chemin de Vie {cheminVie} : {cheminVieInfo.titre}
                      </h2>
                    </div>
                  </div>
                  
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-[#C5A059] mb-3 flex items-center gap-2">
                        <Sparkles className="w-4 h-4" /> Vos Dons Naturels
                      </h3>
                      <p className="text-[#E0D9F6]/80 font-light leading-relaxed">{cheminVieInfo.dons}</p>
                    </div>
                    
                    <div className="border-t border-[#C5A059]/10 pt-6">
                      <h3 className="text-[#C5A059] mb-3 flex items-center gap-2">
                        <Zap className="w-4 h-4" /> Vos Défis Principaux
                      </h3>
                      <p className="text-[#E0D9F6]/80 font-light leading-relaxed">{cheminVieInfo.defis}</p>
                    </div>
                    
                    <div className="border-t border-[#C5A059]/10 pt-6">
                      <h3 className="text-[#C5A059] mb-3 flex items-center gap-2">
                        <Star className="w-4 h-4" /> Votre Mission
                      </h3>
                      <p className="text-[#E0D9F6]/80 font-light leading-relaxed">{cheminVieInfo.mission}</p>
                    </div>
                    
                    <div className="bg-[#C5A059]/10 rounded-xl p-6 border border-[#C5A059]/20">
                      <h3 className="text-[#F3E5AB] mb-3">Conseils d'Évolution</h3>
                      <p className="text-[#E0D9F6]/80 font-light leading-relaxed">{cheminVieInfo.conseils}</p>
                    </div>
                  </div>
                </div>

                {/* Année Personnelle */}
                <div className="card-mystical">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="p-4 rounded-full bg-[#C5A059]/10 text-[#C5A059]">
                      <Moon className="w-8 h-8" strokeWidth={1} />
                    </div>
                    <div>
                      <h2 className="text-2xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                        Année Personnelle 2026 : {anneePersonnelle}
                      </h2>
                    </div>
                  </div>
                  <p className="text-[#E0D9F6]/80 font-light leading-relaxed mb-6">
                    Les énergies cosmiques de 2026 vous invitent à la réflexion, à la transformation et à la préparation 
                    d'un nouveau cycle. C'est une période propice pour trouver l'équilibre intérieur, lâcher prise 
                    sur ce qui ne vous sert plus, et approfondir votre spiritualité.
                  </p>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-[#1A0B2E]/50 rounded-xl p-4 border border-[#C5A059]/10">
                      <p className="text-[#C5A059] text-sm mb-2">Périodes favorables</p>
                      <p className="text-[#E0D9F6]/60 font-light text-sm">Mars-Mai et Septembre-Novembre</p>
                    </div>
                    <div className="bg-[#1A0B2E]/50 rounded-xl p-4 border border-[#C5A059]/10">
                      <p className="text-[#C5A059] text-sm mb-2">Points d'attention</p>
                      <p className="text-[#E0D9F6]/60 font-light text-sm">Évitez les décisions impulsives en juin-juillet</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Section 3: Cœur & Relations */}
            {activeTab === 'coeur' && (
              <div className="space-y-8 animate-fade-in">
                <div className="card-mystical">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="p-4 rounded-full bg-[#C5A059]/10 text-[#C5A059]">
                      <Heart className="w-8 h-8" strokeWidth={1} />
                    </div>
                    <div>
                      <h2 className="text-2xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                        Vénus - Votre Langage Amoureux
                      </h2>
                    </div>
                  </div>
                  <p className="text-[#E0D9F6]/80 font-light leading-relaxed">
                    Votre Vénus, influencée par l'énergie Terre, vous prédispose à un amour fidèle, sensuel et 
                    profondément engagé. L'amour se construit avec patience, soin et attention aux détails. 
                    Votre loyauté est sans faille et votre tendresse s'exprime par des gestes concrets.
                  </p>
                </div>

                <div className="card-mystical">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="p-4 rounded-full bg-[#C5A059]/10 text-[#C5A059]">
                      <Zap className="w-8 h-8" strokeWidth={1} />
                    </div>
                    <div>
                      <h2 className="text-2xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                        Mars - Votre Force d'Action
                      </h2>
                    </div>
                  </div>
                  <p className="text-[#E0D9F6]/80 font-light leading-relaxed">
                    Votre Mars en énergie Terre confère une action méthodique et persévérante. Vous agissez avec 
                    une détermination implacable, sans vous précipiter. L'endurance est votre arme secrète.
                  </p>
                </div>

                <div className="card-mystical bg-[#C5A059]/5">
                  <h3 className="text-xl mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                    Synthèse Affective
                  </h3>
                  <p className="text-[#E0D9F6]/80 font-light leading-relaxed">
                    La combinaison de votre Vénus et Mars révèle un équilibre entre réceptivité et affirmation. 
                    L'élément Terre dominant colore vos relations de stabilité et de sensualité. 
                    Pour des relations épanouissantes, cultivez l'authenticité et acceptez la vulnérabilité comme force.
                  </p>
                </div>
              </div>
            )}

            {/* Section 4: Défis & Talents */}
            {activeTab === 'defis' && (
              <div className="animate-fade-in">
                <div className="card-mystical mb-8">
                  <h2 className="text-2xl mb-6" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                    Aspects Planétaires de Votre Thème
                  </h2>
                  <p className="text-[#E0D9F6]/70 font-light mb-8">
                    Les aspects révèlent vos talents innés et vos défis de croissance. Les carrés et oppositions 
                    sont vos meilleurs professeurs.
                  </p>
                  
                  <div className="space-y-6">
                    {aspectsPlanetaires.map((aspect, index) => (
                      <div key={index} className="bg-[#1A0B2E]/50 rounded-xl p-6 border border-[#C5A059]/10">
                        <div className="flex items-center gap-3 mb-3">
                          <span className={`px-3 py-1 rounded-full text-xs ${
                            aspect.aspect === 'Trigone' ? 'bg-emerald-500/20 text-emerald-400' :
                            aspect.aspect === 'Sextile' ? 'bg-blue-500/20 text-blue-400' :
                            'bg-amber-500/20 text-amber-400'
                          }`}>
                            {aspect.aspect}
                          </span>
                          <span className="text-[#F3E5AB]">{aspect.planetes}</span>
                        </div>
                        <p className="text-[#E0D9F6]/70 font-light text-sm">{aspect.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Section 5: Conseil de la Plume */}
            {activeTab === 'conseil' && (
              <div className="space-y-8 animate-fade-in">
                <div className="card-mystical">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="p-4 rounded-full bg-[#C5A059]/10 text-[#C5A059]">
                      <Sparkles className="w-8 h-8" strokeWidth={1} />
                    </div>
                    <div>
                      <h2 className="text-2xl" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                        Message de la Plume Astrale
                      </h2>
                    </div>
                  </div>
                  
                  <p className="text-[#E0D9F6]/80 font-light leading-relaxed mb-6">
                    {userData.prenom ? `${userData.prenom}, votre` : 'Votre'} thème astral est unique. Votre chemin de vie {cheminVie} ({cheminVieInfo.titre}), 
                    combiné à votre ascendant {ascendant} et à l'élément Terre dominant, révèle une âme profonde 
                    et créative destinée à construire et à inspirer.
                  </p>
                  
                  <div className="bg-[#C5A059]/10 rounded-xl p-6 border border-[#C5A059]/20 mb-8">
                    <p className="text-[#F3E5AB] text-center italic" style={{ fontFamily: 'Cinzel, serif' }}>
                      "Que les étoiles vous guident, que la Plume vous éclaire, 
                      et que votre destinée se révèle dans toute sa splendeur."
                    </p>
                  </div>
                  
                  <h3 className="text-xl mb-6" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                    Trois Clés Essentielles pour 2026
                  </h3>
                  
                  <div className="space-y-4">
                    <div className="flex gap-4">
                      <div className="w-8 h-8 rounded-full bg-[#C5A059]/20 flex items-center justify-center text-[#C5A059] flex-shrink-0">1</div>
                      <div>
                        <p className="text-[#F3E5AB] mb-1">Honorez votre essence d'Artiste</p>
                        <p className="text-[#E0D9F6]/60 font-light text-sm">Inspirez, communiquez la joie, élevez les vibrations.</p>
                      </div>
                    </div>
                    <div className="flex gap-4">
                      <div className="w-8 h-8 rounded-full bg-[#C5A059]/20 flex items-center justify-center text-[#C5A059] flex-shrink-0">2</div>
                      <div>
                        <p className="text-[#F3E5AB] mb-1">Cultivez la force de votre élément Terre</p>
                        <p className="text-[#E0D9F6]/60 font-light text-sm">Maîtrisez et utilisez consciemment vos outils de navigation.</p>
                      </div>
                    </div>
                    <div className="flex gap-4">
                      <div className="w-8 h-8 rounded-full bg-[#C5A059]/20 flex items-center justify-center text-[#C5A059] flex-shrink-0">3</div>
                      <div>
                        <p className="text-[#F3E5AB] mb-1">Transformez les défis en sagesse</p>
                        <p className="text-[#E0D9F6]/60 font-light text-sm">Les aspects difficiles sont des invitations à grandir.</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Conseils d'alignement */}
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {conseilsAlignement.map((conseil, index) => (
                    <div key={index} className="card-mystical">
                      <h4 className="text-[#C5A059] mb-3">{conseil.domaine}</h4>
                      <p className="text-[#E0D9F6]/70 font-light text-sm">{conseil.conseil}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="mt-16 text-center">
            <div className="card-mystical p-8 glow-gold">
              <h2 className="text-2xl mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                Votre Voyage ne Fait que Commencer
              </h2>
              <p className="text-[#E0D9F6]/60 mb-6 font-light">
                Cette étude est un guide pour votre évolution personnelle. 
                Revisitez-la régulièrement pour approfondir votre compréhension.
              </p>
              <p className="text-sm text-[#E0D9F6]/40 font-light">
                Cet outil est un support de développement personnel. 
                Il ne remplace aucun avis médical, psychologique ou juridique.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Resultats;
