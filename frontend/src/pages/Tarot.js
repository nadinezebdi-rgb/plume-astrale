import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Star, RefreshCw } from 'lucide-react';

const Tarot = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [isPaid, setIsPaid] = useState(false);
  const [cards, setCards] = useState([]);
  const [revealedCards, setRevealedCards] = useState([]);

  const tarotDeck = [
    { name: "Le Bateleur", meaning: "Nouveau départ, potentiel.", advice: "Passez à l'action." },
    { name: "La Papesse", meaning: "Intuition et sagesse.", advice: "Écoutez votre intuition." },
    { name: "L'Impératrice", meaning: "Créativité et abondance.", advice: "Exprimez-vous." },
    { name: "L'Empereur", meaning: "Structure et stabilité.", advice: "Organisez-vous." },
    { name: "Le Pape", meaning: "Sagesse et tradition.", advice: "Cherchez conseil." },
    { name: "L'Amoureux", meaning: "Choix et amour.", advice: "Suivez votre cœur." },
    { name: "Le Chariot", meaning: "Victoire et volonté.", advice: "Avancez avec force." },
    { name: "La Justice", meaning: "Équilibre et vérité.", advice: "Soyez juste." },
    { name: "L'Hermite", meaning: "Introspection.", advice: "Prenez du recul." },
    { name: "La Roue de Fortune", meaning: "Changement.", advice: "Acceptez les cycles." },
    { name: "La Force", meaning: "Courage.", advice: "Maîtrisez vos émotions." },
    { name: "Le Pendu", meaning: "Lâcher-prise.", advice: "Changez de perspective." },
    { name: "La Mort", meaning: "Transformation.", advice: "Acceptez la fin." },
    { name: "Tempérance", meaning: "Équilibre.", advice: "Restez modéré." },
    { name: "Le Diable", meaning: "Attachements.", advice: "Libérez-vous." },
    { name: "La Maison Dieu", meaning: "Révélation.", advice: "Acceptez la vérité." },
    { name: "L'Étoile", meaning: "Espoir.", advice: "Gardez foi." },
    { name: "La Lune", meaning: "Illusion.", advice: "Écoutez votre intuition." },
    { name: "Le Soleil", meaning: "Succès.", advice: "Rayonnez." },
    { name: "Le Jugement", meaning: "Renaissance.", advice: "Éveillez-vous." },
    { name: "Le Monde", meaning: "Accomplissement.", advice: "Célébrez." },
    { name: "Le Mat", meaning: "Liberté.", advice: "Osez." }
  ];

  const drawCards = () => {
    const shuffled = [...tarotDeck].sort(() => Math.random() - 0.5);
    setCards(shuffled.slice(0, 3));
    setRevealedCards([]);
  };

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

    drawCards();

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const revealCard = (index) => {
    if (!revealedCards.includes(index)) {
      setRevealedCards([...revealedCards, index]);
    }
  };

  if (!userData) {
    return <div className="text-center p-10">Chargement...</div>;
  }

  return (
    <div className="p-10 text-center">
      <h1>Tirage Tarot</h1>

      <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
        {cards.map((card, index) => (
          <div key={index} onClick={() => isPaid && revealCard(index)}>
            {revealedCards.includes(index) ? (
              <div>
                <h3>{card.name}</h3>
                <p>{card.meaning}</p>
                <p><i>{card.advice}</i></p>
              </div>
            ) : (
              <div>
                <Star />
                <p>{isPaid ? "Clique pour révéler" : "Premium requis"}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      <button onClick={drawCards} style={{ marginTop: '20px' }}>
        <RefreshCw /> Nouveau tirage
      </button>
    </div>
  );
};

export default Tarot;

