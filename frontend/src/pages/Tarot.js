import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Star, Moon, Heart, RefreshCw } from 'lucide-react';

const Tarot = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [isPaid, setIsPaid] = useState(false);
  const [cards, setCards] = useState([]);
  const [isRevealing, setIsRevealing] = useState(false);
  const [revealedCards, setRevealedCards] = useState([]);

  const tarotDeck = [
    { name: "Le Bateleur", meaning: "Nouveau départ, potentiel, volonté. Les outils sont entre vos mains pour créer votre réalité.", advice: "Passez à l'action avec confiance." },
    { name: "La Papesse", meaning: "Intuition, sagesse intérieure, mystère. Écoutez votre voix intérieure.", advice: "Prenez du recul et méditez avant d'agir." },
    { name: "L'Impératrice", meaning: "Abondance, créativité, nature. La fertilité dans tous les domaines.", advice: "Nourrissez vos projets avec amour." },
    { name: "L'Empereur", meaning: "Structure, autorité, stabilité. Le pouvoir de construire.", advice: "Établissez des fondations solides." },
    { name: "Le Pape", meaning: "Sagesse, enseignement, tradition. Le guide spirituel.", advice: "Cherchez conseil auprès d'un mentor." },
    { name: "L'Amoureux", meaning: "Choix, amour, harmonie. L'union des opposés.", advice: "Suivez votre cœur dans vos décisions." },
    { name: "Le Chariot", meaning: "Victoire, détermination, avancement. Le triomphe par la volonté.", advice: "Foncez vers vos objectifs avec détermination." },
    { name: "La Justice", meaning: "Équilibre, vérité, karma. Ce qui est juste sera révélé.", advice: "Agissez avec intégrité et équité." },
    { name: "L'Hermite", meaning: "Introspection, recherche, solitude. La lumière intérieure.", advice: "Prenez du temps pour vous retrouver." },
    { name: "La Roue de Fortune", meaning: "Cycles, destin, changement. Rien n'est permanent.", advice: "Acceptez les changements comme opportunités." },
    { name: "La Force", meaning: "Courage, patience, maîtrise. La force douce.", advice: "Domptez vos instincts avec douceur." },
    { name: "Le Pendu", meaning: "Sacrifice, lâcher-prise, perspective. Voir autrement.", advice: "Changez votre point de vue sur la situation." },
    { name: "La Mort", meaning: "Transformation, fin, renaissance. La métamorphose nécessaire.", advice: "Laissez mourir ce qui doit partir." },
    { name: "Tempérance", meaning: "Équilibre, patience, modération. L'alchimie des énergies.", advice: "Trouvez le juste milieu." },
    { name: "Le Diable", meaning: "Attachements, ombres, matérialisme. Face à ses chaînes.", advice: "Libérez-vous de ce qui vous enchaîne." },
    { name: "La Maison Dieu", meaning: "Révélation, libération, choc. L'éclair de vérité.", advice: "Acceptez la vérité même si elle dérange." },
    { name: "L'Étoile", meaning: "Espoir, inspiration, sérénité. La lumière après l'orage.", advice: "Gardez foi en vos rêves." },
    { name: "La Lune", meaning: "Illusions, intuition, inconscient. Les mystères de la nuit.", advice: "Faites confiance à vos rêves et intuitions." },
    { name: "Le Soleil", meaning: "Succès, joie, vitalité. La lumière triomphante.", advice: "Rayonnez votre lumière intérieure." },
    { name: "Le Jugement", meaning: "Renaissance, appel, réveil. Le moment de vérité.", advice: "Répondez à votre vocation profonde." },
    { name: "Le Monde", meaning: "Accomplissement, intégration, succès. Le cycle complet.", advice: "Célébrez vos réussites et préparez le nouveau cycle." },
    { name: "Le Mat", meaning: "Liberté, foi, nouveau voyage. L'âme en quête.", advice: "Osez l'inconnu avec légèreté." }
  ];

  useEffect(() => {
    const data = localStorage.getItem('plume_astrale_data');
    const paid = localStorage.getItem('plume_astrale_paid');
    const plan = localStorage.getItem('plume_astrale_plan');
    
    if (!data) {
      navigate('/formulaire');
      return;
    }
    
    setUserData(JSON.parse(data));
    setIsPaid(paid === 'true' && plan === 'premium');
    
    // eslint-disable-next-line react-hooks/exhaustive-deps
useEffect(() => {
  drawCards();
}, []);

  const drawCards = () => {
    const shuffled = [...tarotDeck].sort(() => Math.random() - 0.5);
    setCards(shuffled.slice(0, 3));
    setRevealedCards([]);
    setIsRevealing(false);
  };

  const revealCard = (index) => {
    if (!revealedCards.includes(index)) {
      setRevealedCards([...revealedCards, index]);
    }
  };

  const positions = ['Passé', 'Présent', 'Futur'];

  if (!userData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-2 border-[#C5A059] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      
      <div className="px-6 md:px-8 py-20 md:py-28">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-4 font-light">
              Tirage de Tarot
            </p>
            
            <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
              Les Arcanes Vous Parlent
            </h1>
            
            <p className="text-lg text-[#B8B0C8]/70 font-light max-w-2xl mx-auto">
              {userData.prenom ? `${userData.prenom}, ` : ''}concentrez-vous sur votre question et révélez les cartes
            </p>
          </div>

          {/* Cards */}
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            {cards.map((card, index) => (
              <div key={index} className="text-center">
                <p className="text-[#C5A059] uppercase tracking-widest text-sm mb-4">
                  {positions[index]}
                </p>
                
                <div 
                  className={`card-mystical cursor-pointer transition-all duration-700 transform ${
                    revealedCards.includes(index) ? 'rotate-0' : 'hover:scale-105'
                  }`}
                  onClick={() => isPaid && revealCard(index)}
                  data-testid={`tarot-card-${index}`}
                >
                  {revealedCards.includes(index) ? (
                    <div className="py-8">
                      <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#C5A059]/20 flex items-center justify-center">
                        <Sparkles className="w-8 h-8 text-[#C5A059]" strokeWidth={1} />
                      </div>
                      <h3 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                        {card.name}
                      </h3>
                      <p className="text-[#B8B0C8]/70 text-sm mb-4 font-light">
                        {card.meaning}
                      </p>
                      <div className="bg-[#C5A059]/10 rounded-lg p-4 border border-[#C5A059]/20">
                        <p className="text-[#C5A059] text-sm italic">
                          "{card.advice}"
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="py-12">
                      <div className="w-20 h-28 mx-auto rounded-lg bg-gradient-to-b from-[#1C1735] to-[#15112A] border border-[#C5A059]/30 flex items-center justify-center">
                        <Star className="w-8 h-8 text-[#C5A059]/50" strokeWidth={1} />
                      </div>
                      <p className="text-[#B8B0C8]/40 text-sm mt-4">
                        {isPaid ? 'Cliquez pour révéler' : 'Premium requis'}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className="text-center">
            {isPaid ? (
              <button
                onClick={drawCards}
                className="btn-mystical rounded-full flex items-center gap-2 mx-auto"
                data-testid="btn-new-draw"
              >
                <RefreshCw className="w-4 h-4" strokeWidth={1} />
                Nouveau tirage
              </button>
            ) : (
              <div className="card-mystical max-w-md mx-auto text-center">
                <Sparkles className="w-10 h-10 text-[#C5A059] mx-auto mb-4" strokeWidth={1} />
                <h3 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                  Tirage Premium
                </h3>
                <p className="text-[#B8B0C8]/60 mb-6 font-light">
                  Débloquez le tirage de Tarot avec l'offre Premium
                </p>
                <button
                  onClick={() => navigate('/choix')}
                  className="btn-mystical-filled rounded-full"
                  data-testid="btn-unlock-tarot"
                >
                  Recevoir mon manuscrit complet
                </button>
              </div>
            )}
          </div>

          {/* Interpretation Guide */}
          {isPaid && revealedCards.length === 3 && (
            <div className="mt-12 card-mystical bg-[#C5A059]/5">
              <h3 className="text-xl mb-4 text-center" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                Interprétation de Votre Tirage
              </h3>
              <p className="text-[#B8B0C8]/70 font-light text-center leading-relaxed">
                <strong className="text-[#C5A059]">{cards[0].name}</strong> dans le passé montre les fondations de votre situation. 
                <strong className="text-[#C5A059]"> {cards[1].name}</strong> au présent révèle les énergies actuelles. 
                <strong className="text-[#C5A059]"> {cards[2].name}</strong> pour le futur indique la direction probable si vous suivez votre chemin actuel.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
 );
};

export default Tarot;
