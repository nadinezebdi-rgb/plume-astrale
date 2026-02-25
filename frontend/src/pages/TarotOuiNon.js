import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Loader2, ArrowLeft, Sparkles, Lock } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TarotOuiNon = () => {
  const navigate = useNavigate();
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isPaid, setIsPaid] = useState(false);
  const [isRevealed, setIsRevealed] = useState(false);

  const handleTirage = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setResult(null);
    setIsRevealed(false);

    try {
      const res = await fetch(`${API_URL}/api/tarot/oui-non`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question.trim() }),
      });
      const data = await res.json();
      setResult(data);
      
      // Auto-reveal for free preview (partial)
      setTimeout(() => setIsRevealed(true), 1500);
    } catch (e) {
      console.error('Tarot error:', e);
    }
    setLoading(false);
  };

  const handlePurchase = async () => {
    try {
      const res = await fetch(`${API_URL}/api/checkout/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: 'tarot_oui_non',
          origin_url: window.location.origin,
          user_data: { question }
        }),
      });
      const data = await res.json();
      if (data.url) window.location.href = data.url;
    } catch (e) {
      console.error('Payment error:', e);
    }
  };

  const getOrientationStyle = (orientation) => {
    if (orientation === 'oui') return { color: '#4ECB71', label: 'OUI', bg: 'rgba(78, 203, 113, 0.15)' };
    if (orientation === 'non') return { color: '#E8526E', label: 'NON', bg: 'rgba(232, 82, 110, 0.15)' };
    return { color: '#C5A059', label: 'NEUTRE', bg: 'rgba(197, 160, 89, 0.15)' };
  };

  return (
    <div className="min-h-screen relative">
      <StarField />
      <div className="relative z-10 py-12 px-4 md:px-6">
        <div className="max-w-2xl mx-auto">
          
          {/* Back */}
          <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-[#C5A059]/60 hover:text-[#C5A059] mb-8 transition-colors" data-testid="back-btn">
            <ArrowLeft className="w-4 h-4" /> Retour
          </button>

          {/* Header */}
          <div className="text-center mb-10">
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-3 font-light">
              Tirage Sacre
            </p>
            <h1 className="text-3xl md:text-5xl mb-3" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Tarot Oui / Non
            </h1>
            <p className="text-[#E0D9F6]/60 font-light">
              Posez votre question et laissez les Arcanes Majeurs vous repondre
            </p>
          </div>

          {/* Question input */}
          <div className="card-mystical mb-8" data-testid="question-form">
            <label className="block text-[#C5A059] text-sm uppercase tracking-widest mb-3">
              Votre Question
            </label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Posez votre question ici... (ex: Vais-je trouver l'amour cette annee ?)"
              className="w-full px-4 py-3 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-xl text-[#E0D9F6] placeholder:text-[#E0D9F6]/30 focus:outline-none focus:border-[#C5A059] resize-none h-24"
              data-testid="question-input"
            />
            <button
              onClick={handleTirage}
              disabled={loading || !question.trim()}
              className="btn-mystical-filled rounded-full flex items-center gap-2 mx-auto mt-4 px-8 py-3 disabled:opacity-50"
              data-testid="tirage-btn"
            >
              {loading ? (
                <><Loader2 className="w-5 h-5 animate-spin" /> Consultation des Arcanes...</>
              ) : (
                <><Star className="w-5 h-5" /> Tirer une Carte</>
              )}
            </button>
          </div>

          {/* Result */}
          {result && isRevealed && (
            <div className="space-y-6 animate-fade-in">
              {/* Card reveal */}
              <div className="card-mystical text-center p-8 glow-gold" data-testid="carte-result">
                <div className="mb-4">
                  <span className="text-[#C5A059] text-sm uppercase tracking-widest">Arcane Tire</span>
                </div>
                
                <div className="w-32 h-44 mx-auto mb-6 rounded-xl overflow-hidden" 
                     style={{ border: '2px solid #C5A059' }}>
                  {result.carte.image ? (
                    <img src={`${API_URL}${result.carte.image}`} alt={result.carte.nom} className="w-full h-full object-cover" data-testid="carte-image" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #1A0B2E, #2D1B4E)' }}>
                      <span className="text-[#C5A059] text-3xl font-bold" style={{ fontFamily: 'Cinzel, serif' }}>
                        {result.carte.numero === 0 ? '0' : result.carte.numero}
                      </span>
                    </div>
                  )}
                </div>

                <h2 className="text-2xl mb-2" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                  {result.carte.nom}
                </h2>
                <p className="text-[#C5A059]/70 text-sm mb-4">{result.carte.energie}</p>

                {/* Orientation badge */}
                {(() => {
                  const style = getOrientationStyle(result.orientation);
                  return (
                    <div className="inline-block px-6 py-2 rounded-full text-lg font-bold mb-6"
                         style={{ color: style.color, background: style.bg, border: `1px solid ${style.color}40` }}>
                      {style.label}
                    </div>
                  );
                })()}
              </div>

              {/* Message - partially locked */}
              <div className="card-mystical" data-testid="message-result">
                <h3 className="text-[#C5A059] text-sm uppercase tracking-widest mb-3">Message des Arcanes</h3>
                <p className="text-[#E0D9F6]/80 leading-relaxed font-light text-lg">
                  {result.reponse}
                </p>
              </div>

              {/* Upsell - Tarologie complete */}
              <div className="card-mystical text-center p-8 border-[#C5A059]/30" data-testid="upsell-tarologie">
                <Sparkles className="w-8 h-8 text-[#C5A059] mx-auto mb-4" strokeWidth={1} />
                <h3 className="text-xl mb-2" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                  Envie d'aller plus loin ?
                </h3>
                <p className="text-[#E0D9F6]/60 text-sm mb-6">
                  Decouvrez la Tarologie & Mediumnite complete : 7 cartes, lecture mediumnique et PDF personnalise
                </p>
                <button
                  onClick={() => navigate('/tarologie')}
                  className="btn-mystical-filled rounded-full px-8 py-3 inline-flex items-center gap-2"
                  data-testid="cta-tarologie-full"
                >
                  <Sparkles className="w-5 h-5" /> Tarologie Complete — 35 EUR
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TarotOuiNon;
