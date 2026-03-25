import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Sparkles, Star, RefreshCw, Lock, Crown, BookOpen, Eye } from 'lucide-react';

const Tarot = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [isPaid, setIsPaid] = useState(false);
  const [cards, setCards] = useState([]);
  const [revealedCards, setRevealedCards] = useState([]);
  const [journal, setJournal] = useState(null);
  const [journalLoading, setJournalLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');

  const tarotDeck = [
    { name: "Le Bateleur", meaning: "Nouveau d\u00e9part, potentiel.", advice: "Passez \u00e0 l\u2019action." },
    { name: "La Papesse", meaning: "Intuition et sagesse.", advice: "\u00c9coutez votre intuition." },
    { name: "L\u2019Imp\u00e9ratrice", meaning: "Cr\u00e9ativit\u00e9 et abondance.", advice: "Exprimez-vous." },
    { name: "L\u2019Empereur", meaning: "Structure et stabilit\u00e9.", advice: "Organisez-vous." },
    { name: "Le Pape", meaning: "Sagesse et tradition.", advice: "Cherchez conseil." },
    { name: "L\u2019Amoureux", meaning: "Choix et amour.", advice: "Suivez votre c\u0153ur." },
    { name: "Le Chariot", meaning: "Victoire et volont\u00e9.", advice: "Avancez avec force." },
    { name: "La Justice", meaning: "\u00c9quilibre et v\u00e9rit\u00e9.", advice: "Soyez juste." },
    { name: "L\u2019Hermite", meaning: "Introspection.", advice: "Prenez du recul." },
    { name: "La Roue de Fortune", meaning: "Changement.", advice: "Acceptez les cycles." },
    { name: "La Force", meaning: "Courage.", advice: "Ma\u00eetrisez vos \u00e9motions." },
    { name: "Le Pendu", meaning: "L\u00e2cher-prise.", advice: "Changez de perspective." },
    { name: "La Mort", meaning: "Transformation.", advice: "Acceptez la fin." },
    { name: "Temp\u00e9rance", meaning: "\u00c9quilibre.", advice: "Restez mod\u00e9r\u00e9." },
    { name: "Le Diable", meaning: "Attachements.", advice: "Lib\u00e9rez-vous." },
    { name: "La Maison Dieu", meaning: "R\u00e9v\u00e9lation.", advice: "Acceptez la v\u00e9rit\u00e9." },
    { name: "L\u2019\u00c9toile", meaning: "Espoir.", advice: "Gardez foi." },
    { name: "La Lune", meaning: "Illusion.", advice: "\u00c9coutez votre intuition." },
    { name: "Le Soleil", meaning: "Succ\u00e8s.", advice: "Rayonnez." },
    { name: "Le Jugement", meaning: "Renaissance.", advice: "\u00c9veillez-vous." },
    { name: "Le Monde", meaning: "Accomplissement.", advice: "C\u00e9l\u00e9brez." },
    { name: "Le Mat", meaning: "Libert\u00e9.", advice: "Osez." }
  ];

  const drawCards = () => {
    const shuffled = [...tarotDeck].sort(() => Math.random() - 0.5);
    setCards(shuffled.slice(0, 3));
    setRevealedCards([]);
  };

  const fetchJournal = async (data) => {
    setJournalLoading(true);
    setLoadingMessage('Connexion aux \u00e9nergies...');

    setTimeout(() => {
      setLoadingMessage('Lecture en cours...');
    }, 1500);

    try {
      const res = await fetch("/api/journal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: data.prenom,
          sign: data.sign,
          lifePath: data.lifePath
        })
      });

      const result = await res.json();
      if (result.journal) {
        setJournal(result.journal);
      }
    } catch (error) {
      console.error('Erreur journal IA:', error);
    } finally {
      setTimeout(() => {
        setJournalLoading(false);
        setLoadingMessage('');
      }, 500);
    }
  };

  useEffect(() => {
    const data = localStorage.getItem('plume_astrale_data');
    const paid = localStorage.getItem('plume_astrale_paid');
    const plan = localStorage.getItem('plume_astrale_plan');

    if (!data) {
      navigate('/formulaire');
      return;
    }

    const parsed = JSON.parse(data);
    setUserData(parsed);
    setIsPaid(paid === 'true' && plan === 'premium');

    drawCards();
    fetchJournal(parsed);

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const revealCard = (index) => {
    if (!revealedCards.includes(index)) {
      setRevealedCards([...revealedCards, index]);
    }
  };

  if (!userData) {
    return (
      <div className="min-h-screen bg-[#0C0918] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#C5A059] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0C0918] text-[#F0E6D3] py-10 px-4">
      <div className="max-w-3xl mx-auto space-y-8">

        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl md:text-4xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
            Tirage Tarot
          </h1>
          <p className="text-[#B8B0C8]/60 text-sm">Votre guidance quotidienne</p>
        </div>

        {/* Cards Section */}
        <div className="card-mystical p-6">
          <div className="flex items-center gap-2 mb-6 justify-center">
            <Star className="w-5 h-5 text-[#C5A059]" strokeWidth={1.5} />
            <h2 className="text-xl text-[#C5A059]" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
              Votre Tirage
            </h2>
            <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full border border-green-500/30 ml-2">
              GRATUIT
            </span>
          </div>

          <div className="flex gap-4 md:gap-6 justify-center flex-wrap">
            {cards.map((card, index) => (
              <div
                key={index}
                onClick={() => revealCard(index)}
                className={`w-28 h-44 md:w-32 md:h-48 rounded-xl border-2 flex flex-col items-center justify-center shadow-xl cursor-pointer transition-all duration-500 ${
                  revealedCards.includes(index)
                    ? 'bg-gradient-to-b from-[#2D1F4B] to-[#1C1735] border-[#C5A059]/60'
                    : 'bg-gradient-to-b from-[#2D1F4B] via-[#1C1735] to-[#0C0918] border-[#C5A059]/30 hover:border-[#C5A059] hover:shadow-[#C5A059]/30'
                }`}
              >
                {revealedCards.includes(index) ? (
                  <div className="text-center p-3 animate-fadeIn">
                    <Sparkles className="w-6 h-6 text-[#C5A059] mx-auto mb-2" strokeWidth={1} />
                    <h3 className="text-sm font-semibold text-[#F0E6D3] mb-1" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                      {card.name}
                    </h3>
                    <p className="text-xs text-[#B8B0C8]/70">{card.meaning}</p>
                    <p className="text-xs text-[#C5A059] mt-1 italic">{card.advice}</p>
                  </div>
                ) : (
                  <div className="text-center">
                    <Star className="w-10 h-10 text-[#C5A059]/50 mx-auto mb-2" strokeWidth={1} />
                    <p className="text-xs text-[#B8B0C8]/50">Cliquez</p>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="text-center mt-6">
            <button
              onClick={drawCards}
              className="btn-mystical rounded-xl py-2 px-6 inline-flex items-center gap-2 text-sm"
            >
              <RefreshCw className="w-4 h-4" /> Nouveau tirage
            </button>
          </div>
        </div>

        {/* Journal IA Section */}
        <div className="card-mystical p-6">
          <div className="flex items-center gap-2 mb-4 justify-center">
            <BookOpen className="w-5 h-5 text-[#C5A059]" strokeWidth={1.5} />
            <h2 className="text-xl text-[#C5A059]" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
              Votre Journal Astral
            </h2>
          </div>

          {journalLoading ? (
            <div className="text-center py-8 space-y-4">
              <div className="w-10 h-10 border-2 border-[#C5A059] border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="text-[#C5A059] animate-pulse text-lg" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                {loadingMessage}
              </p>
              <div className="flex justify-center gap-1">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-2 h-2 bg-[#C5A059]/60 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 0.2}s` }}
                  />
                ))}
              </div>
            </div>
          ) : journal ? (
            <div className="animate-fadeIn">
              <div className="bg-gradient-to-b from-[#C5A059]/10 to-transparent rounded-xl p-5 border border-[#C5A059]/20">
                <p className="text-[#F0E6D3]/90 whitespace-pre-line leading-relaxed font-light">
                  {journal}
                </p>
              </div>
            </div>
          ) : (
            <p className="text-center text-[#B8B0C8]/50 py-4">
              Journal indisponible pour le moment.
            </p>
          )}
        </div>

        {/* Monetization CTA */}
        <div className="card-mystical p-6 text-center border border-[#C5A059]/30 bg-gradient-to-b from-[#C5A059]/10 to-transparent">
          <Crown className="w-8 h-8 text-[#C5A059] mx-auto mb-3" strokeWidth={1.5} />
          <p className="text-xl text-[#F0E6D3] mb-2" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
            Votre destin\u00e9e compl\u00e8te vous attend
          </p>
          <p className="text-[#B8B0C8]/60 text-sm mb-6">
            D\u00e9bloquez l'acc\u00e8s complet \u00e0 votre guidance
          </p>

          <div className="grid md:grid-cols-2 gap-4 mb-6">
            {/* Free tier */}
            <div className="rounded-xl border border-[#B8B0C8]/20 p-4 bg-[#1C1735]/50">
              <p className="text-[#B8B0C8]/80 text-xs uppercase tracking-wider mb-2">Gratuit</p>
              <ul className="text-sm text-[#B8B0C8]/60 space-y-2">
                <li className="flex items-center gap-2 justify-center">
                  <Eye className="w-4 h-4 text-green-400" /> 1 tirage par jour
                </li>
              </ul>
            </div>

            {/* Premium tier */}
            <div className="rounded-xl border border-[#C5A059]/40 p-4 bg-[#C5A059]/10 relative overflow-hidden">
              <div className="absolute top-0 right-0 bg-[#C5A059] text-[#0C0918] text-xs px-3 py-0.5 rounded-bl-lg font-semibold">
                PREMIUM
              </div>
              <p className="text-[#C5A059] text-xs uppercase tracking-wider mb-2">Payant</p>
              <ul className="text-sm text-[#F0E6D3]/80 space-y-2">
                <li className="flex items-center gap-2 justify-center">
                  <Sparkles className="w-4 h-4 text-[#C5A059]" /> Tirage complet
                </li>
                <li className="flex items-center gap-2 justify-center">
                  <BookOpen className="w-4 h-4 text-[#C5A059]" /> Interpr\u00e9tation d\u00e9taill\u00e9e
                </li>
                <li className="flex items-center gap-2 justify-center">
                  <Star className="w-4 h-4 text-[#C5A059]" /> Journal IA quotidien
                </li>
              </ul>
            </div>
          </div>

          <Link
            to="/premium"
            className="btn-mystical-filled rounded-xl py-3 px-8 inline-flex items-center gap-2"
          >
            <Lock className="w-4 h-4" />
            D\u00e9couvrir l'offre Premium
            <Sparkles className="w-4 h-4" />
          </Link>
        </div>

      </div>
    </div>
  );
};

export default Tarot;
