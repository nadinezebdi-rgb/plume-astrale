import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Sparkles, Star, Moon, Heart, Briefcase, Coins, Leaf, 
  Sun, RefreshCw, ArrowRight, ChevronDown, Eye, Wand2,
  CircleDot, HelpCircle, LogIn
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { asset } from '../lib/assets';
import LibraryImage from '@/components/LibraryImage';
import TarotCardBack from '@/components/TarotCardBack';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const TirageTarot = () => {
  const navigate = useNavigate();
  const { isAuthenticated, token, creditBalance, refreshBalance } = useAuth();
  
  // États
  const [step, setStep] = useState(0); // 0: credit gate, 1: question, 2: tirage, 3: révélation
  const [question, setQuestion] = useState('');
  const [domaine, setDomaine] = useState('general');
  const [typeTirage, setTypeTirage] = useState('marseille'); // marseille ou celtique
  const [isLoading, setIsLoading] = useState(false);
  const [tirageData, setTirageData] = useState(null);
  const [revealedCards, setRevealedCards] = useState([]);
  const [currentRevealIndex, setCurrentRevealIndex] = useState(-1);
  const [isRevealing, setIsRevealing] = useState(false);
  const [showDomaines, setShowDomaines] = useState(false);
  const [syntheseUnlocked, setSyntheseUnlocked] = useState(false);
  const [creditUnlocked, setCreditUnlocked] = useState(false);

  // Domaines avec icônes
  const domaines = {
    amour: { nom: "Amour & Relations", icone: Heart, couleur: "text-pink-400" },
    travail: { nom: "Carrière & Travail", icone: Briefcase, couleur: "text-blue-400" },
    argent: { nom: "Finances & Abondance", icone: Coins, couleur: "text-yellow-400" },
    sante: { nom: "Santé & Bien-être", icone: Leaf, couleur: "text-green-400" },
    spirituel: { nom: "Spiritualité & Développement", icone: Sun, couleur: "text-[#B8A9E8]" },
    general: { nom: "Question Générale", icone: CircleDot, couleur: "text-[#D4AF37]" }
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

  // Credit unlock handler
  const handleCreditUnlock = async () => {
    try {
      await axios.post(`${API_URL}/api/credits/use`,
        { service_id: 'lecture_tarot' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      await refreshBalance();
      setCreditUnlocked(true);
      setStep(1);
    } catch (err) {
      const detail = err.response?.data?.detail || '';
      if (detail.includes('insuffisants')) {
        navigate('/acheter-credits');
      } else {
        alert(detail || 'Erreur');
      }
    }
  };

  // Recommencer
  const recommencer = () => {
    setStep(creditUnlocked ? 1 : 0);
    setQuestion('');
    setTirageData(null);
    setRevealedCards([]);
    setCurrentRevealIndex(-1);
    setIsRevealing(false);
    if (!creditUnlocked) {
      setCreditUnlocked(false);
    }
  };

  // Rendu de la carte avec les vraies images
  const renderCard = (carte, index, isRevealed) => {
    // URLs des images de tarot
    const tarotImages = {
      default: asset('images/tarot/tarot_cards_2.png')
    };
    
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
          {/* Face cachée - Dos de carte mystique */}
          <div className={`card-mystical cursor-pointer transition-all duration-500 ${
            isRevealed ? 'opacity-0 absolute inset-0 pointer-events-none' : 'opacity-100'
          }`}>
            <div className="py-8 text-center">
              <div className="w-28 h-44 mx-auto rounded-xl bg-gradient-to-b from-[#2D1F4B] via-[#1C1735] to-[#111625] border-2 border-[#D4AF37]/50 flex flex-col items-center justify-center shadow-xl shadow-[#D4AF37]/20 relative overflow-hidden group hover:border-[#D4AF37] hover:shadow-[#D4AF37]/40 transition-all">
                {/* Motif décoratif élaboré */}
                <div className="absolute inset-0 opacity-30">
                  <div className="absolute top-2 left-2 w-6 h-6 border-2 border-[#D4AF37] rounded-full"></div>
                  <div className="absolute top-2 right-2 w-6 h-6 border-2 border-[#D4AF37] rounded-full"></div>
                  <div className="absolute bottom-2 left-2 w-6 h-6 border-2 border-[#D4AF37] rounded-full"></div>
                  <div className="absolute bottom-2 right-2 w-6 h-6 border-2 border-[#D4AF37] rounded-full"></div>
                  {/* Croix centrale */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-px h-full bg-gradient-to-b from-transparent via-[#D4AF37]/50 to-transparent"></div>
                    <div className="absolute w-full h-px bg-gradient-to-r from-transparent via-[#D4AF37]/50 to-transparent"></div>
                  </div>
                </div>
                {/* Étoile centrale */}
                <div className="relative z-10">
                  <Star className="w-12 h-12 text-[#D4AF37]/70 group-hover:text-[#D4AF37] transition-colors" strokeWidth={1} />
                  <Moon className="w-6 h-6 text-[#D4AF37]/50 absolute -top-1 -right-1" strokeWidth={1} />
                </div>
                {/* Reflet */}
                <div className="absolute inset-0 bg-gradient-to-t from-[#D4AF37]/5 to-transparent"></div>
                <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              </div>
              <p className="text-[#B8B0C8]/60 text-sm mt-4 font-light">
                {typeTirage === 'marseille' 
                  ? ['Passé', 'Présent', 'Futur'][index]
                  : positionsCeltique[index]
                }
              </p>
              {!isRevealing && (
                <p className="text-[#D4AF37]/60 text-xs mt-2 animate-pulse">Cliquez pour révéler</p>
              )}
            </div>
          </div>
          
          {/* Face révélée - Carte avec image */}
          <div className={`card-mystical transition-all duration-500 ${
            isRevealed ? 'opacity-100' : 'opacity-0 absolute inset-0 pointer-events-none'
          } ${carte.orientation === 'renverse' ? 'border-[#B8A9E8]/50' : 'border-[#D4AF37]/40'}`}>
            <div className="py-4 text-center">
              {/* Position */}
              <p className="text-[#D4AF37] uppercase tracking-[0.2em] text-xs mb-3 font-light">
                {typeTirage === 'marseille' 
                  ? ['Passé', 'Présent', 'Futur'][index]
                  : positionsCeltique[index]
                }
              </p>
              
              {/* Image de la carte */}
              <div className={`relative w-24 h-40 mx-auto mb-3 rounded-lg overflow-hidden border-2 ${
                carte.orientation === 'droit' 
                  ? 'border-[#D4AF37]/60' 
                  : 'border-[#B8A9E8]/60 rotate-180'
              } shadow-lg`}>
                <div className="absolute inset-0 bg-gradient-to-b from-[#2D1F4B] to-[#1C1735]">
                  {/* Placeholder avec icône stylisée */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <Sparkles className={`w-10 h-10 mx-auto mb-1 ${
                        carte.orientation === 'droit' ? 'text-[#D4AF37]' : 'text-[#B8A9E8]'
                      }`} strokeWidth={1} />
                      <span className="text-[#D4AF37] text-2xl font-bold" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                        {carte.numero}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Nom de la carte */}
              <h3 className="text-lg mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                {carte.nom}
              </h3>
              
              {/* Orientation avec badge stylisé */}
              <span className={`inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full ${
                carte.orientation === 'droit' 
                  ? 'bg-[#D4AF37]/20 text-[#D4AF37] border border-[#D4AF37]/30' 
                  : 'bg-[#B8A9E8]/20 text-[#E3D7FF] border border-[#B8A9E8]/30'
              }`}>
                {carte.orientation === 'droit' ? (
                  <><Sun className="w-3 h-3" /> Droit</>
                ) : (
                  <><Moon className="w-3 h-3" /> Renversé</>
                )}
              </span>
              
              {/* Mots-clés */}
              <div className="flex flex-wrap justify-center gap-1 mt-3 mb-3">
                {carte.mots_cles?.slice(0, 3).map((mot, i) => (
                  <span key={i} className="text-xs text-[#B8B0C8]/70 bg-[#1C1735]/80 px-2 py-0.5 rounded-full border border-[#D4AF37]/10">
                    {mot}
                  </span>
                ))}
              </div>
              
              {/* Élément et Planète */}
              <div className="flex justify-center gap-3 mb-3 text-xs text-[#B8B0C8]/50">
                <span>◆ {carte.element}</span>
                <span>☆ {carte.planete}</span>
              </div>
              
              {/* Interprétation */}
              <p className="text-[#B8B0C8]/80 text-sm font-light leading-relaxed mb-3 px-2">
                {carte.interpretation?.slice(0, 120)}...
              </p>
              
              {/* Conseil */}
              <div className="bg-gradient-to-r from-[#D4AF37]/10 via-[#D4AF37]/20 to-[#D4AF37]/10 rounded-lg p-3 border border-[#D4AF37]/20 mx-2">
                <p className="text-[#D4AF37] text-xs italic leading-relaxed">
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
    <div className="min-h-screen relative">
      {/* Background image décoratif */}
      <div 
        className="fixed inset-0 opacity-5 pointer-events-none"
        style={{
          backgroundImage: `url('${asset('images/tarot/tarot_cards_2.png')}')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat'
        }}
      />
      
      <div className="px-6 md:px-8 py-20 md:py-28 relative z-10">
        <div className="max-w-6xl mx-auto">
          
          {/* ÉTAPE 0: Credit Gate */}
          {step === 0 && (
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-10">
                <p className="text-[#D4AF37] uppercase tracking-[0.3em] text-sm mb-4 font-light">
                  Tirage de Tarot
                </p>
                <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                  Consultez les Arcanes
                </h1>
                <p className="text-lg text-[#B8B0C8]/70 font-light">
                  Lecture Tarot approfondie
                </p>
              </div>

              {/* 3 dos de carte décoratifs — teasing du jeu */}
              <div className="flex justify-center gap-4 mb-10" data-testid="tarot-teaser-backs">
                <div style={{ transform: 'rotate(-6deg)' }}>
                  <TarotCardBack size={{ width: 110, height: 160 }} />
                </div>
                <div style={{ transform: 'translateY(-8px)' }}>
                  <TarotCardBack size={{ width: 120, height: 175 }} />
                </div>
                <div style={{ transform: 'rotate(6deg)' }}>
                  <TarotCardBack size={{ width: 110, height: 160 }} />
                </div>
              </div>

              {!isAuthenticated ? (
                <div className="flex flex-col items-center justify-center py-12 text-center" data-testid="credit-gate-login">
                  <LogIn className="w-8 h-8 mb-4" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
                  <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                    Connexion requise
                  </h2>
                  <p className="text-sm mb-6" style={{ color: 'var(--pa-muted)' }}>
                    Connectez-vous pour accéder au tirage de Tarot.
                    <br /><span style={{ color: '#D4AF37' }}>10 crédits &middot; 20 crédits offerts à l'inscription</span>
                  </p>
                  <div className="flex gap-3">
                    <button onClick={() => navigate('/connexion')} className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full" style={{ border: '1px solid rgba(212,175,55,0.5)', color: '#D4AF37', letterSpacing: '0.1em' }} data-testid="gate-login-btn">Se connecter</button>
                    <button onClick={() => navigate('/inscription')} className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full" style={{ border: '1px solid rgba(212,175,55,0.3)', color: '#D4AF37', background: 'rgba(212,175,55,0.08)', letterSpacing: '0.1em' }} data-testid="gate-register-btn">Créer un compte</button>
                  </div>
                </div>
              ) : creditBalance < 10 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center" data-testid="credit-gate-insufficient">
                  <Coins className="w-8 h-8 mb-4" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
                  <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>Crédits insuffisants</h2>
                  <p className="text-sm mb-2" style={{ color: 'var(--pa-muted)' }}>
                    Le tirage coûte <span style={{ color: '#D4AF37', fontWeight: 600 }}>10 crédits</span>.
                  </p>
                  <p className="text-sm mb-6" style={{ color: 'var(--pa-muted)' }}>Solde : <span style={{ color: '#D4AF37' }}>{creditBalance} crédits</span></p>
                  <button onClick={() => navigate('/acheter-credits')} className="flex items-center gap-2 text-xs uppercase tracking-widest px-6 py-2.5 rounded-full" style={{ border: '1px solid #D4AF37', color: '#111625', background: '#D4AF37', letterSpacing: '0.1em', fontWeight: 600 }} data-testid="gate-buy-credits-btn">
                    Acheter des crédits <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-center" data-testid="credit-gate-unlock">
                  <Coins className="w-7 h-7 mb-3" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
                  <p className="text-sm mb-1" style={{ color: 'var(--pa-body)' }}>Lecture Tarot approfondie</p>
                  <p className="text-xs mb-5" style={{ color: 'var(--pa-muted)' }}>
                    Coût : <span style={{ color: '#D4AF37' }}>10 crédits</span> &middot; Solde : <span style={{ color: '#D4AF37' }}>{creditBalance} crédits</span>
                  </p>
                  <button onClick={handleCreditUnlock} className="text-xs uppercase tracking-widest px-8 py-2.5 rounded-full" style={{ border: '1px solid rgba(212,175,55,0.5)', color: '#D4AF37', letterSpacing: '0.1em' }} data-testid="gate-unlock-btn">
                    Utiliser 10 crédits
                  </button>
                </div>
              )}

              {/* Vitrine des 22 arcanes majeurs peints à la main pour Plume Astrale */}
              <div className="mt-16 text-center" data-testid="tarot-deck-preview">
                <p
                  className="text-[#D4AF37] uppercase tracking-[0.28em] text-[11px] mb-3"
                  style={{ fontFamily: 'Cinzel, serif' }}
                >
                  ✦ Les 22 arcanes peints à la main ✦
                </p>
                <h3
                  className="mb-2"
                  style={{
                    fontFamily: 'Cormorant Garamond, serif',
                    fontSize: 'clamp(1.3rem, 2.6vw, 1.8rem)',
                    color: '#F5EEE0',
                    lineHeight: 1.15,
                  }}
                >
                  Un jeu unique, dessiné pour Plume Astrale
                </h3>
                <p className="text-[#B8B0C8]/70 text-sm max-w-xl mx-auto mb-7 font-light">
                  Chaque arcane a été composé à la main dans l&apos;esprit du Tarot de Marseille — or profond
                  sur nuit d&apos;encre, aucun visuel standard IA.
                </p>
                <div className="flex flex-wrap justify-center gap-2">
                  {[
                    'Le Mat', 'Le Bateleur', 'La Papesse', "L'Impératrice", "L'Empereur",
                    'Le Pape', 'Les Amoureux', 'Le Chariot', 'La Justice', "L'Hermite",
                    'La Roue de Fortune', 'La Force', 'Le Pendu', "L'Arcane sans Nom",
                    'La Tempérance', 'Le Diable', 'La Maison Dieu', "L'Étoile", 'La Lune',
                    'Le Soleil', 'Le Jugement', 'Le Monde',
                  ].map((cardName, idx) => (
                    <div
                      key={cardName}
                      title={cardName}
                      data-testid={`deck-preview-${idx}`}
                      style={{
                        width: 58, height: 87,
                        borderRadius: 4,
                        overflow: 'hidden',
                        border: '1px solid rgba(212,175,55,0.35)',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.45)',
                        background: '#0e0a24',
                      }}
                    >
                      <LibraryImage
                        type="tarot"
                        name={cardName}
                        size={87}
                        alt={cardName}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ÉTAPE 1: Formulaire de question */}
          {step === 1 && (
            <div className="max-w-2xl mx-auto">
              {/* Header */}
              <div className="text-center mb-10">
                <p className="text-[#D4AF37] uppercase tracking-[0.3em] text-sm mb-4 font-light">
                  Tirage de Tarot
                </p>
                <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
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
                    typeTirage === 'marseille' ? 'border-[#D4AF37] bg-[#D4AF37]/10' : 'hover:border-[#D4AF37]/50'
                  }`}
                  onClick={() => setTypeTirage('marseille')}
                  data-testid="select-marseille"
                >
                  <div className="text-center py-4">
                    <div className="flex justify-center gap-2 mb-3">
                      {[1,2,3].map(i => (
                        <div key={i} className="w-8 h-12 rounded bg-gradient-to-b from-[#2D1F4B] to-[#1C1735] border border-[#D4AF37]/30"></div>
                      ))}
                    </div>
                    <h3 className="text-lg mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                      Tirage Marseille
                    </h3>
                    <p className="text-[#B8B0C8]/60 text-sm">3 cartes • Passé, Présent, Futur</p>
                    <p className="text-[#D4AF37] text-lg font-semibold mt-2">10 crédits</p>
                  </div>
                </div>

                <div 
                  className={`card-mystical cursor-pointer transition-all ${
                    typeTirage === 'celtique' ? 'border-[#D4AF37] bg-[#D4AF37]/10' : 'hover:border-[#D4AF37]/50'
                  }`}
                  onClick={() => setTypeTirage('celtique')}
                  data-testid="select-celtique"
                >
                  <div className="text-center py-4">
                    <div className="flex justify-center gap-1 mb-3 flex-wrap" style={{ maxWidth: '120px', margin: '0 auto' }}>
                      {[1,2,3,4,5,6,7,8,9,10].map(i => (
                        <div key={i} className="w-4 h-6 rounded bg-gradient-to-b from-[#2D1F4B] to-[#1C1735] border border-[#D4AF37]/30"></div>
                      ))}
                    </div>
                    <h3 className="text-lg mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                      Croix Celtique
                    </h3>
                    <p className="text-[#B8B0C8]/60 text-sm">10 cartes • Analyse complète</p>
                    <p className="text-[#D4AF37] text-lg font-semibold mt-2">10 crédits</p>
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
                      <span className="text-[#F5EEE0]">{domaines[domaine].nom}</span>
                    </div>
                    <ChevronDown className={`w-5 h-5 text-[#D4AF37] transition-transform ${showDomaines ? 'rotate-180' : ''}`} />
                  </div>
                </div>
                
                {showDomaines && (
                  <div className="mt-2 card-mystical divide-y divide-[#D4AF37]/10">
                    {Object.entries(domaines).map(([key, value]) => (
                      <div 
                        key={key}
                        className={`flex items-center gap-3 py-3 px-4 cursor-pointer hover:bg-[#D4AF37]/10 transition-colors ${
                          domaine === key ? 'bg-[#D4AF37]/10' : ''
                        }`}
                        onClick={() => { setDomaine(key); setShowDomaines(false); }}
                      >
                        {React.createElement(value.icone, { 
                          className: `w-5 h-5 ${value.couleur}`, 
                          strokeWidth: 1.5 
                        })}
                        <span className="text-[#F5EEE0]">{value.nom}</span>
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
                  <HelpCircle className="absolute left-4 top-4 w-5 h-5 text-[#D4AF37]/50" strokeWidth={1.5} />
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Formulez votre question avec clarté et sincérité..."
                    className="w-full bg-[#1C1735] border border-[#D4AF37]/30 rounded-xl py-4 pl-12 pr-4 text-[#F5EEE0] placeholder-[#B8B0C8]/40 focus:outline-none focus:border-[#D4AF37] transition-colors resize-none"
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
                <p className="text-[#D4AF37] uppercase tracking-[0.3em] text-sm mb-4 font-light">
                  {typeTirage === 'marseille' ? 'Tirage Marseille' : 'Croix Celtique'}
                </p>
                <h1 className="text-2xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
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
                  <div className="inline-flex items-center gap-3 bg-[#D4AF37]/20 px-6 py-3 rounded-full">
                    <div className="w-4 h-4 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-[#D4AF37]">
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
                <p className="text-[#D4AF37] uppercase tracking-[0.3em] text-sm mb-4 font-light">
                  Synthèse de votre tirage
                </p>
                <h1 className="text-2xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                  L'Interprétation des Arcanes
                </h1>
              </div>

              {/* Question rappel */}
              <div className="card-mystical bg-[#D4AF37]/10 mb-8">
                <p className="text-center">
                  <span className="text-[#B8B0C8]/60 text-sm">Votre question : </span>
                  <span className="text-[#F5EEE0] italic">"{question}"</span>
                </p>
              </div>

              {/* Bouton Voir la Synthèse / Synthèse payante */}
              {!syntheseUnlocked ? (
                <div className="text-center py-8" data-testid="synthese-paywall">
                  <div className="card-mystical glow-gold max-w-md mx-auto py-8">
                    <Sparkles className="w-10 h-10 text-[#D4AF37] mx-auto mb-4" strokeWidth={1} />
                    <h3 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                      Synth&egrave;se Compl&egrave;te
                    </h3>
                    <p className="text-[#B8B0C8]/60 text-sm mb-6 px-4">
                      D&eacute;couvrez l'analyse d&eacute;taill&eacute;e de votre tirage : tendance g&eacute;n&eacute;rale, messages pass&eacute;/pr&eacute;sent/futur et conseil des Arcanes
                    </p>
                    <p className="text-3xl font-bold mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#D4AF37' }}>
                      4,99 &euro;
                    </p>
                    <button
                      onClick={() => setSyntheseUnlocked(true)}
                      className="btn-mystical-filled rounded-full px-8 py-3 inline-flex items-center gap-2"
                      data-testid="btn-unlock-synthese"
                    >
                      <Eye className="w-5 h-5" /> Voir la synth&egrave;se
                    </button>
                  </div>
                </div>
              ) : (
                <>
              {/* Synthèse pour Marseille */}
              {typeTirage === 'marseille' && tirageData.synthese && (
                <div className="space-y-6">
                  {/* Tendance générale */}
                  <div className="card-mystical">
                    <h3 className="text-xl mb-4 text-[#D4AF37]" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                      Tendance Générale : {tirageData.synthese.tendance_generale}
                    </h3>
                    <p className="text-[#B8B0C8]/70">{tirageData.synthese.fil_conducteur}</p>
                  </div>

                  {/* Messages par position */}
                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="card-mystical">
                      <h4 className="text-[#D4AF37] mb-2">Passé</h4>
                      <p className="text-[#B8B0C8]/70 text-sm">{tirageData.synthese.message_passe}</p>
                    </div>
                    <div className="card-mystical">
                      <h4 className="text-[#D4AF37] mb-2">Présent</h4>
                      <p className="text-[#B8B0C8]/70 text-sm">{tirageData.synthese.message_present}</p>
                    </div>
                    <div className="card-mystical">
                      <h4 className="text-[#D4AF37] mb-2">Futur</h4>
                      <p className="text-[#B8B0C8]/70 text-sm">{tirageData.synthese.message_futur}</p>
                    </div>
                  </div>

                  {/* Conseil final */}
                  <div className="card-mystical bg-[#D4AF37]/10 border-[#D4AF37]/40">
                    <div className="flex items-start gap-4">
                      <Sparkles className="w-8 h-8 text-[#D4AF37] flex-shrink-0 mt-1" strokeWidth={1} />
                      <div>
                        <h4 className="text-[#D4AF37] text-lg mb-2" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                          Conseil des Arcanes
                        </h4>
                        <p className="text-[#F5EEE0] italic">{tirageData.conseil_final}</p>
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
                    <h3 className="text-xl mb-4 text-[#D4AF37]" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                      Énergie Globale
                    </h3>
                    <p className="text-[#F5EEE0] mb-4">{tirageData.analyse.energie_globale}</p>
                    <div className="flex gap-4 text-sm">
                      <span className="text-green-400">✓ {tirageData.analyse.cartes_droites} cartes droites</span>
                      <span className="text-red-400">↻ {tirageData.analyse.cartes_renversees} cartes renversées</span>
                      <span className="text-[#D4AF37]">◆ Élément dominant : {tirageData.analyse.element_dominant}</span>
                    </div>
                  </div>

                  {/* Points clés */}
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="card-mystical">
                      <h4 className="text-[#D4AF37] mb-2">Situation Actuelle</h4>
                      <p className="text-[#F5EEE0] font-semibold mb-1">{tirageData.analyse.situation_actuelle?.carte}</p>
                      <p className="text-[#B8B0C8]/70 text-sm">{tirageData.analyse.situation_actuelle?.message}</p>
                    </div>
                    <div className="card-mystical">
                      <h4 className="text-[#D4AF37] mb-2">Obstacle Principal</h4>
                      <p className="text-[#F5EEE0] font-semibold mb-1">{tirageData.analyse.obstacle_principal?.carte}</p>
                      <p className="text-[#B8B0C8]/70 text-sm">{tirageData.analyse.obstacle_principal?.message}</p>
                    </div>
                    <div className="card-mystical">
                      <h4 className="text-[#D4AF37] mb-2">Fondement</h4>
                      <p className="text-[#F5EEE0] font-semibold mb-1">{tirageData.analyse.fondement?.carte}</p>
                      <p className="text-[#B8B0C8]/70 text-sm">{tirageData.analyse.fondement?.message}</p>
                    </div>
                    <div className="card-mystical">
                      <h4 className="text-[#D4AF37] mb-2">Résultat Probable</h4>
                      <p className="text-[#F5EEE0] font-semibold mb-1">{tirageData.analyse.resultat_probable?.carte}</p>
                      <p className="text-[#B8B0C8]/70 text-sm">{tirageData.analyse.resultat_probable?.message}</p>
                    </div>
                  </div>

                  {/* Synthèse finale */}
                  <div className="card-mystical">
                    <h4 className="text-[#D4AF37] text-lg mb-3" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                      Synthèse Finale
                    </h4>
                    <p className="text-[#B8B0C8]/80 whitespace-pre-line">{tirageData.analyse.synthese_finale}</p>
                  </div>

                  {/* Conseil d'action */}
                  <div className="card-mystical bg-[#D4AF37]/10 border-[#D4AF37]/40">
                    <div className="flex items-start gap-4">
                      <Sparkles className="w-8 h-8 text-[#D4AF37] flex-shrink-0 mt-1" strokeWidth={1} />
                      <div>
                        <h4 className="text-[#D4AF37] text-lg mb-2" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                          Conseil d'Action
                        </h4>
                        <p className="text-[#F5EEE0] whitespace-pre-line">{tirageData.analyse.conseil_action}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
                </>
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
