import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Sparkles, Star, Moon, Heart, Briefcase, Coins, Leaf, 
  Sun, RefreshCw, ArrowRight, ChevronDown, Eye, Wand2,
  CircleDot, HelpCircle
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const TirageTarot = () => {
  const navigate = useNavigate();
  
  // États
  const [step, setStep] = useState(1); // 1: question, 2: tirage, 3: révélation
  const [question, setQuestion] = useState('');
  const [domaine, setDomaine] = useState('general');
  const [typeTirage, setTypeTirage] = useState('marseille'); // marseille ou celtique
  const [isLoading, setIsLoading] = useState(false);
  const [tirageData, setTirageData] = useState(null);
  const [revealedCards, setRevealedCards] = useState([]);
  const [currentRevealIndex, setCurrentRevealIndex] = useState(-1);
  const [isRevealing, setIsRevealing] = useState(false);
  const [showDomaines, setShowDomaines] = useState(false);

  // Domaines avec icônes
  const domaines = {
    amour: { nom: "Amour & Relations", icone: Heart, couleur: "text-pink-400" },
    travail: { nom: "Carrière & Travail", icone: Briefcase, couleur: "text-blue-400" },
    argent: { nom: "Finances & Abondance", icone: Coins, couleur: "text-yellow-400" },
    sante: { nom: "Santé & Bien-être", icone: Leaf, couleur: "text-green-400" },
    spirituel: { nom: "Spiritualité & Développement", icone: Sun, couleur: "text-purple-400" },
    general: { nom: "Question Générale", icone: CircleDot, couleur: "text-[#C5A059]" }
  };

  // Positions pour le tirage celtique
  const positionsCeltique = [
    "La Situation Présente",
    "L'Obstacle ou le Défi", 
    "Le Fondement",
    "Le Passé Récent",
    "La Couronne - Le Meilleur Possible",
    "Le Futur Proche",
    "Votre Attitude",
    "L'Environnement",
    "Espoirs et Craintes",
    "Le Résultat Final"
  ];

  // Lancer le tirage
  const lancerTirage = async () => {
    if (question.length < 5) {
      alert("Veuillez formuler une question d'au moins 5 caractères");
      return;
    }

    setIsLoading(true);
    
    try {
      const endpoint = typeTirage === 'marseille' 
        ? `${API_URL}/api/tarot/marseille`
        : `${API_URL}/api/tarot/celtique`;
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, domaine })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setTirageData(data.data);
        setStep(2);
        setRevealedCards([]);
        setCurrentRevealIndex(-1);
      } else {
        alert("Erreur lors du tirage. Veuillez réessayer.");
      }
    } catch (error) {
      console.error('Erreur:', error);
      alert("Erreur de connexion. Veuillez réessayer.");
    } finally {
      setIsLoading(false);
    }
  };

  // Révéler les cartes une par une
  const startReveal = () => {
    setIsRevealing(true);
    setCurrentRevealIndex(0);
  };

  // Animation de révélation
  useEffect(() => {
    if (isRevealing && currentRevealIndex >= 0 && tirageData) {
      const maxCards = typeTirage === 'marseille' ? 3 : 10;
      
      if (currentRevealIndex < maxCards) {
        const timer = setTimeout(() => {
          setRevealedCards(prev => [...prev, currentRevealIndex]);
          setCurrentRevealIndex(prev => prev + 1);
        }, 1500); // 1.5 secondes entre chaque carte
        
        return () => clearTimeout(timer);
      } else {
        setIsRevealing(false);
        setStep(3);
      }
    }
  }, [currentRevealIndex, isRevealing, tirageData, typeTirage]);

  // Révéler une carte manuellement
  const revealCard = (index) => {
    if (!revealedCards.includes(index)) {
      setRevealedCards(prev => [...prev, index]);
    }
  };

  // Recommencer
  const recommencer = () => {
    setStep(1);
    setQuestion('');
    setTirageData(null);
    setRevealedCards([]);
    setCurrentRevealIndex(-1);
    setIsRevealing(false);
  };

  // Rendu de la carte
  const renderCard = (carte, index, isRevealed) => {
    const DomaineIcon = domaines[domaine]?.icone || CircleDot;
    
    return (
      <div 
        key={index}
        className={`relative transition-all duration-700 transform-gpu ${
          isRevealed ? 'scale-100' : 'scale-95 hover:scale-100'
        }`}
        style={{ perspective: '1000px' }}
      >
        <div 
          className={`relative w-full transition-all duration-700 transform-style-preserve-3d ${
            isRevealed ? 'rotate-y-0' : ''
          }`}
          onClick={() => !isRevealing && revealCard(index)}
        >
          {/* Face cachée */}
          <div className={`card-mystical cursor-pointer transition-all duration-500 ${
            isRevealed ? 'opacity-0 absolute inset-0 pointer-events-none' : 'opacity-100'
          }`}>
            <div className="py-8 text-center">
              <div className="w-24 h-36 mx-auto rounded-xl bg-gradient-to-b from-[#2D1F4B] to-[#1C1735] border-2 border-[#C5A059]/40 flex flex-col items-center justify-center shadow-lg shadow-[#C5A059]/10 relative overflow-hidden">
                {/* Motif décoratif */}
                <div className="absolute inset-0 opacity-20">
                  <div className="absolute top-2 left-2 w-4 h-4 border border-[#C5A059] rounded-full"></div>
                  <div className="absolute top-2 right-2 w-4 h-4 border border-[#C5A059] rounded-full"></div>
                  <div className="absolute bottom-2 left-2 w-4 h-4 border border-[#C5A059] rounded-full"></div>
                  <div className="absolute bottom-2 right-2 w-4 h-4 border border-[#C5A059] rounded-full"></div>
                </div>
                <Star className="w-10 h-10 text-[#C5A059]/60" strokeWidth={1} />
                <div className="absolute inset-0 bg-gradient-to-t from-[#C5A059]/10 to-transparent"></div>
              </div>
              <p className="text-[#B8B0C8]/50 text-sm mt-4 font-light">
                {typeTirage === 'marseille' 
                  ? ['Passé', 'Présent', 'Futur'][index]
                  : positionsCeltique[index]
                }
              </p>
              {!isRevealing && (
                <p className="text-[#C5A059]/60 text-xs mt-2">Cliquez pour révéler</p>
              )}
            </div>
          </div>
          
          {/* Face révélée */}
          <div className={`card-mystical transition-all duration-500 ${
            isRevealed ? 'opacity-100' : 'opacity-0 absolute inset-0 pointer-events-none'
          } ${carte.orientation === 'renverse' ? 'border-red-500/30' : 'border-[#C5A059]/30'}`}>
            <div className="py-6 text-center">
              {/* Position */}
              <p className="text-[#C5A059] uppercase tracking-widest text-xs mb-3">
                {typeTirage === 'marseille' 
                  ? ['Passé', 'Présent', 'Futur'][index]
                  : positionsCeltique[index]
                }
              </p>
              
              {/* Icône */}
              <div className={`w-14 h-14 mx-auto mb-3 rounded-full flex items-center justify-center ${
                carte.orientation === 'droit' 
                  ? 'bg-[#C5A059]/20' 
                  : 'bg-red-500/20'
              }`}>
                <Sparkles className={`w-7 h-7 ${
                  carte.orientation === 'droit' ? 'text-[#C5A059]' : 'text-red-400'
                }`} strokeWidth={1} />
              </div>
              
              {/* Nom de la carte */}
              <h3 className="text-lg mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                {carte.nom}
              </h3>
              
              {/* Orientation */}
              <span className={`text-xs px-2 py-1 rounded-full ${
                carte.orientation === 'droit' 
                  ? 'bg-[#C5A059]/20 text-[#C5A059]' 
                  : 'bg-red-500/20 text-red-400'
              }`}>
                {carte.orientation_fr}
              </span>
              
              {/* Mots-clés */}
              <div className="flex flex-wrap justify-center gap-1 mt-3 mb-4">
                {carte.mots_cles?.slice(0, 3).map((mot, i) => (
                  <span key={i} className="text-xs text-[#B8B0C8]/60 bg-[#1C1735] px-2 py-0.5 rounded">
                    {mot}
                  </span>
                ))}
              </div>
              
              {/* Interprétation */}
              <p className="text-[#B8B0C8]/70 text-sm font-light leading-relaxed mb-4 px-2">
                {carte.interpretation?.slice(0, 150)}...
              </p>
              
              {/* Conseil */}
              <div className="bg-[#C5A059]/10 rounded-lg p-3 border border-[#C5A059]/20 mx-2">
                <p className="text-[#C5A059] text-xs italic">
                  "{carte.conseil}"
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen">
      <div className="px-6 md:px-8 py-20 md:py-28">
        <div className="max-w-6xl mx-auto">
          
          {/* ÉTAPE 1: Formulaire de question */}
          {step === 1 && (
            <div className="max-w-2xl mx-auto">
              {/* Header */}
              <div className="text-center mb-10">
                <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-4 font-light">
                  Tirage de Tarot
                </p>
                <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                  Consultez les Arcanes
                </h1>
                <p className="text-lg text-[#B8B0C8]/70 font-light">
                  Formulez votre question et laissez les cartes vous guider
                </p>
              </div>

              {/* Choix du type de tirage */}
              <div className="grid md:grid-cols-2 gap-4 mb-8">
                <div 
                  className={`card-mystical cursor-pointer transition-all ${
                    typeTirage === 'marseille' ? 'border-[#C5A059] bg-[#C5A059]/10' : 'hover:border-[#C5A059]/50'
                  }`}
                  onClick={() => setTypeTirage('marseille')}
                  data-testid="select-marseille"
                >
                  <div className="text-center py-4">
                    <div className="flex justify-center gap-2 mb-3">
                      {[1,2,3].map(i => (
                        <div key={i} className="w-8 h-12 rounded bg-gradient-to-b from-[#2D1F4B] to-[#1C1735] border border-[#C5A059]/30"></div>
                      ))}
                    </div>
                    <h3 className="text-lg mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                      Tirage Marseille
                    </h3>
                    <p className="text-[#B8B0C8]/60 text-sm">3 cartes • Passé, Présent, Futur</p>
                    <p className="text-[#C5A059] text-lg font-semibold mt-2">19€</p>
                  </div>
                </div>

                <div 
                  className={`card-mystical cursor-pointer transition-all ${
                    typeTirage === 'celtique' ? 'border-[#C5A059] bg-[#C5A059]/10' : 'hover:border-[#C5A059]/50'
                  }`}
                  onClick={() => setTypeTirage('celtique')}
                  data-testid="select-celtique"
                >
                  <div className="text-center py-4">
                    <div className="flex justify-center gap-1 mb-3 flex-wrap" style={{ maxWidth: '120px', margin: '0 auto' }}>
                      {[1,2,3,4,5,6,7,8,9,10].map(i => (
                        <div key={i} className="w-4 h-6 rounded bg-gradient-to-b from-[#2D1F4B] to-[#1C1735] border border-[#C5A059]/30"></div>
                      ))}
                    </div>
                    <h3 className="text-lg mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                      Croix Celtique
                    </h3>
                    <p className="text-[#B8B0C8]/60 text-sm">10 cartes • Analyse complète</p>
                    <p className="text-[#C5A059] text-lg font-semibold mt-2">29€</p>
                  </div>
                </div>
              </div>

              {/* Choix du domaine */}
              <div className="mb-6">
                <label className="block text-[#B8B0C8]/80 text-sm mb-2 font-light">
                  Domaine de votre question
                </label>
                <div 
                  className="card-mystical cursor-pointer"
                  onClick={() => setShowDomaines(!showDomaines)}
                >
                  <div className="flex items-center justify-between py-2">
                    <div className="flex items-center gap-3">
                      {React.createElement(domaines[domaine].icone, { 
                        className: `w-5 h-5 ${domaines[domaine].couleur}`, 
                        strokeWidth: 1.5 
                      })}
                      <span className="text-[#F0E6D3]">{domaines[domaine].nom}</span>
                    </div>
                    <ChevronDown className={`w-5 h-5 text-[#C5A059] transition-transform ${showDomaines ? 'rotate-180' : ''}`} />
                  </div>
                </div>
                
                {showDomaines && (
                  <div className="mt-2 card-mystical divide-y divide-[#C5A059]/10">
                    {Object.entries(domaines).map(([key, value]) => (
                      <div 
                        key={key}
                        className={`flex items-center gap-3 py-3 px-4 cursor-pointer hover:bg-[#C5A059]/10 transition-colors ${
                          domaine === key ? 'bg-[#C5A059]/10' : ''
                        }`}
                        onClick={() => { setDomaine(key); setShowDomaines(false); }}
                      >
                        {React.createElement(value.icone, { 
                          className: `w-5 h-5 ${value.couleur}`, 
                          strokeWidth: 1.5 
                        })}
                        <span className="text-[#F0E6D3]">{value.nom}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Champ de question */}
              <div className="mb-8">
                <label className="block text-[#B8B0C8]/80 text-sm mb-2 font-light">
                  Votre question
                </label>
                <div className="relative">
                  <HelpCircle className="absolute left-4 top-4 w-5 h-5 text-[#C5A059]/50" strokeWidth={1.5} />
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Formulez votre question avec clarté et sincérité..."
                    className="w-full bg-[#1C1735] border border-[#C5A059]/30 rounded-xl py-4 pl-12 pr-4 text-[#F0E6D3] placeholder-[#B8B0C8]/40 focus:outline-none focus:border-[#C5A059] transition-colors resize-none"
                    rows={4}
                    data-testid="input-question"
                  />
                </div>
                <p className="text-[#B8B0C8]/40 text-xs mt-2">
                  Exemples : "Vais-je trouver l'amour cette année ?" • "Mon projet professionnel va-t-il aboutir ?"
                </p>
              </div>

              {/* Bouton de tirage */}
              <button
                onClick={lancerTirage}
                disabled={isLoading || question.length < 5}
                className={`w-full btn-mystical-filled rounded-xl py-4 flex items-center justify-center gap-3 text-lg ${
                  question.length < 5 ? 'opacity-50 cursor-not-allowed' : ''
                }`}
                data-testid="btn-lancer-tirage"
              >
                {isLoading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-[#1C1735] border-t-transparent rounded-full animate-spin"></div>
                    Préparation du tirage...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-5 h-5" strokeWidth={1.5} />
                    Consulter les Arcanes
                    <ArrowRight className="w-5 h-5" strokeWidth={1.5} />
                  </>
                )}
              </button>
            </div>
          )}

          {/* ÉTAPE 2: Révélation des cartes */}
          {step === 2 && tirageData && (
            <div>
              {/* Header */}
              <div className="text-center mb-10">
                <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-4 font-light">
                  {typeTirage === 'marseille' ? 'Tirage Marseille' : 'Croix Celtique'}
                </p>
                <h1 className="text-2xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                  Les Cartes Sont Tirées
                </h1>
                <p className="text-[#B8B0C8]/70 font-light max-w-xl mx-auto">
                  "{question}"
                </p>
              </div>

              {/* Bouton révéler tout */}
              {!isRevealing && revealedCards.length === 0 && (
                <div className="text-center mb-8">
                  <button
                    onClick={startReveal}
                    className="btn-mystical-filled rounded-xl py-4 px-8 flex items-center gap-3 mx-auto text-lg"
                    data-testid="btn-reveal-all"
                  >
                    <Eye className="w-5 h-5" strokeWidth={1.5} />
                    Révéler les cartes une par une
                    <Sparkles className="w-5 h-5" strokeWidth={1.5} />
                  </button>
                  <p className="text-[#B8B0C8]/50 text-sm mt-3">
                    Ou cliquez sur chaque carte pour la révéler manuellement
                  </p>
                </div>
              )}

              {/* Animation en cours */}
              {isRevealing && (
                <div className="text-center mb-8">
                  <div className="inline-flex items-center gap-3 bg-[#C5A059]/20 px-6 py-3 rounded-full">
                    <div className="w-4 h-4 border-2 border-[#C5A059] border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-[#C5A059]">
                      Révélation en cours... Carte {revealedCards.length + 1} sur {typeTirage === 'marseille' ? 3 : 10}
                    </span>
                  </div>
                </div>
              )}

              {/* Grille des cartes */}
              <div className={`grid gap-6 ${
                typeTirage === 'marseille' 
                  ? 'md:grid-cols-3' 
                  : 'md:grid-cols-5'
              }`}>
                {tirageData.cartes.map((carte, index) => 
                  renderCard(carte, index, revealedCards.includes(index))
                )}
              </div>

              {/* Boutons d'action */}
              <div className="text-center mt-10">
                {revealedCards.length === tirageData.cartes.length && !isRevealing && (
                  <button
                    onClick={() => setStep(3)}
                    className="btn-mystical-filled rounded-xl py-4 px-8 flex items-center gap-3 mx-auto text-lg"
                    data-testid="btn-voir-synthese"
                  >
                    Voir la synthèse complète
                    <ArrowRight className="w-5 h-5" strokeWidth={1.5} />
                  </button>
                )}
              </div>
            </div>
          )}

          {/* ÉTAPE 3: Synthèse */}
          {step === 3 && tirageData && (
            <div className="max-w-4xl mx-auto">
              {/* Header */}
              <div className="text-center mb-10">
                <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-4 font-light">
                  Synthèse de votre tirage
                </p>
                <h1 className="text-2xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                  L'Interprétation des Arcanes
                </h1>
              </div>

              {/* Question rappel */}
              <div className="card-mystical bg-[#C5A059]/10 mb-8">
                <p className="text-center">
                  <span className="text-[#B8B0C8]/60 text-sm">Votre question : </span>
                  <span className="text-[#F0E6D3] italic">"{question}"</span>
                </p>
              </div>

              {/* Synthèse pour Marseille */}
              {typeTirage === 'marseille' && tirageData.synthese && (
                <div className="space-y-6">
                  {/* Tendance générale */}
                  <div className="card-mystical">
                    <h3 className="text-xl mb-4 text-[#C5A059]" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                      Tendance Générale : {tirageData.synthese.tendance_generale}
                    </h3>
                    <p className="text-[#B8B0C8]/70">{tirageData.synthese.fil_conducteur}</p>
                  </div>

                  {/* Messages par position */}
                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="card-mystical">
                      <h4 className="text-[#C5A059] mb-2">Passé</h4>
                      <p className="text-[#B8B0C8]/70 text-sm">{tirageData.synthese.message_passe}</p>
                    </div>
                    <div className="card-mystical">
                      <h4 className="text-[#C5A059] mb-2">Présent</h4>
                      <p className="text-[#B8B0C8]/70 text-sm">{tirageData.synthese.message_present}</p>
                    </div>
                    <div className="card-mystical">
                      <h4 className="text-[#C5A059] mb-2">Futur</h4>
                      <p className="text-[#B8B0C8]/70 text-sm">{tirageData.synthese.message_futur}</p>
                    </div>
                  </div>

                  {/* Conseil final */}
                  <div className="card-mystical bg-[#C5A059]/10 border-[#C5A059]/40">
                    <div className="flex items-start gap-4">
                      <Sparkles className="w-8 h-8 text-[#C5A059] flex-shrink-0 mt-1" strokeWidth={1} />
                      <div>
                        <h4 className="text-[#C5A059] text-lg mb-2" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                          Conseil des Arcanes
                        </h4>
                        <p className="text-[#F0E6D3] italic">{tirageData.conseil_final}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Synthèse pour Celtique */}
              {typeTirage === 'celtique' && tirageData.analyse && (
                <div className="space-y-6">
                  {/* Énergie globale */}
                  <div className="card-mystical">
                    <h3 className="text-xl mb-4 text-[#C5A059]" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                      Énergie Globale
                    </h3>
                    <p className="text-[#F0E6D3] mb-4">{tirageData.analyse.energie_globale}</p>
                    <div className="flex gap-4 text-sm">
                      <span className="text-green-400">✓ {tirageData.analyse.cartes_droites} cartes droites</span>
                      <span className="text-red-400">↻ {tirageData.analyse.cartes_renversees} cartes renversées</span>
                      <span className="text-[#C5A059]">◆ Élément dominant : {tirageData.analyse.element_dominant}</span>
                    </div>
                  </div>

                  {/* Points clés */}
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="card-mystical">
                      <h4 className="text-[#C5A059] mb-2">Situation Actuelle</h4>
                      <p className="text-[#F0E6D3] font-semibold mb-1">{tirageData.analyse.situation_actuelle?.carte}</p>
                      <p className="text-[#B8B0C8]/70 text-sm">{tirageData.analyse.situation_actuelle?.message}</p>
                    </div>
                    <div className="card-mystical">
                      <h4 className="text-[#C5A059] mb-2">Obstacle Principal</h4>
                      <p className="text-[#F0E6D3] font-semibold mb-1">{tirageData.analyse.obstacle_principal?.carte}</p>
                      <p className="text-[#B8B0C8]/70 text-sm">{tirageData.analyse.obstacle_principal?.message}</p>
                    </div>
                    <div className="card-mystical">
                      <h4 className="text-[#C5A059] mb-2">Fondement</h4>
                      <p className="text-[#F0E6D3] font-semibold mb-1">{tirageData.analyse.fondement?.carte}</p>
                      <p className="text-[#B8B0C8]/70 text-sm">{tirageData.analyse.fondement?.message}</p>
                    </div>
                    <div className="card-mystical">
                      <h4 className="text-[#C5A059] mb-2">Résultat Probable</h4>
                      <p className="text-[#F0E6D3] font-semibold mb-1">{tirageData.analyse.resultat_probable?.carte}</p>
                      <p className="text-[#B8B0C8]/70 text-sm">{tirageData.analyse.resultat_probable?.message}</p>
                    </div>
                  </div>

                  {/* Synthèse finale */}
                  <div className="card-mystical">
                    <h4 className="text-[#C5A059] text-lg mb-3" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                      Synthèse Finale
                    </h4>
                    <p className="text-[#B8B0C8]/80 whitespace-pre-line">{tirageData.analyse.synthese_finale}</p>
                  </div>

                  {/* Conseil d'action */}
                  <div className="card-mystical bg-[#C5A059]/10 border-[#C5A059]/40">
                    <div className="flex items-start gap-4">
                      <Sparkles className="w-8 h-8 text-[#C5A059] flex-shrink-0 mt-1" strokeWidth={1} />
                      <div>
                        <h4 className="text-[#C5A059] text-lg mb-2" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                          Conseil d'Action
                        </h4>
                        <p className="text-[#F0E6D3] whitespace-pre-line">{tirageData.analyse.conseil_action}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Actions finales */}
              <div className="flex flex-col md:flex-row gap-4 justify-center mt-10">
                <button
                  onClick={recommencer}
                  className="btn-mystical rounded-xl py-3 px-8 flex items-center justify-center gap-2"
                  data-testid="btn-nouveau-tirage"
                >
                  <RefreshCw className="w-5 h-5" strokeWidth={1.5} />
                  Nouveau tirage
                </button>
                <button
                  onClick={() => navigate('/')}
                  className="btn-mystical-filled rounded-xl py-3 px-8 flex items-center justify-center gap-2"
                >
                  Retour à l'accueil
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TirageTarot;
