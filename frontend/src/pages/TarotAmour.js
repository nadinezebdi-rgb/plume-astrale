import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Heart, Loader2, ArrowLeft, ArrowRight, Coins } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import FadeInEnrichedText from '@/components/FadeInEnrichedText';
import useCardFlipSound from '@/hooks/useCardFlipSound';
import { event as track, EVENTS } from '@/lib/analytics';

const API = process.env.REACT_APP_BACKEND_URL;
const CREDIT_COST = 3;

const TarotAmour = () => {
  const navigate = useNavigate();
  const { isAuthenticated, session, user } = useAuth();
  const [question, setQuestion] = useState('');
  const [reading, setReading] = useState(null);
  const [revealedIdx, setRevealedIdx] = useState(-1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const playFlip = useCardFlipSound(0.4);

  const handleTirage = async () => {
    if (!question.trim() || question.trim().length < 3) {
      setError('Merci de formuler une question complète (min. 3 caractères).');
      return;
    }
    if (!isAuthenticated) {
      navigate('/connexion?redirect=/services/tarot/amour');
      return;
    }
    setError('');
    setReading(null);
    setRevealedIdx(-1);
    setLoading(true);
    track(EVENTS.CREDIT_PURCHASE, { tool: 'tarot_amour', cost: CREDIT_COST });
    try {
      const r = await axios.post(
        `${API}/api/tarot/amour`,
        { question, prenom: user?.first_name || user?.email?.split('@')[0] || 'toi' },
        { headers: { Authorization: `Bearer ${session.access_token}` } },
      );
      setReading(r.data);
      // 3 flips en cascade — 700 ms entre chaque
      r.data.tirage.forEach((_, i) => {
        setTimeout(() => {
          setRevealedIdx((cur) => Math.max(cur, i));
          playFlip();
        }, 700 * (i + 1));
      });
    } catch (e) {
      setError(e.response?.data?.detail || 'Impossible de réaliser le tirage.');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setReading(null);
    setRevealedIdx(-1);
    setQuestion('');
    setError('');
  };

  return (
    <>
      <SEO
        title="Tirage Amoureux — Tarot 3 cartes | Plume Astrale"
        description="Tirage 3 cartes spécial couple : Toi, L'Autre, Le Lien. Une lecture de compatibilité claire pour 3 crédits."
      />

      <div className="max-w-4xl mx-auto px-6 pt-28 pb-24">
        <button onClick={() => navigate('/outils')} className="link-editorial text-xs mb-8 flex items-center gap-2" data-testid="tarot-amour-back">
          <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Outils
        </button>

        <div className="text-center mb-10">
          <p className="text-[10px] uppercase mb-3" style={{ color: '#D4AF37', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}>
            <Heart className="w-3 h-3 inline mr-1.5" fill="#D4AF37" strokeWidth={0} /> Tirage amoureux
          </p>
          <h1
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontWeight: 300,
              fontSize: 'clamp(32px, 4.5vw, 48px)',
              color: '#F5EEE0',
              lineHeight: 1.1,
              marginBottom: 12,
            }}
          >
            <em style={{ fontStyle: 'italic', color: '#D4AF37' }}>Toi</em>, l&apos;autre, et le lien qui vous unit
          </h1>
          <p className="text-sm md:text-base max-w-xl mx-auto" style={{ color: 'rgba(227,215,255,0.7)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
            Trois cartes pour lire ta relation amoureuse (couple, béguin, ex, âme sœur). Nomme la personne dans ta question pour un résultat sur-mesure.
          </p>
          <div className="mt-4 inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs" style={{ background: 'rgba(212,175,55,0.1)', border: '1px solid rgba(212,175,55,0.3)', color: '#D4AF37' }}>
            <Coins className="w-3.5 h-3.5" strokeWidth={1.5} />
            {CREDIT_COST} crédits par tirage
          </div>
        </div>

        {!reading && (
          <div className="plume-glass p-6 md:p-8 max-w-2xl mx-auto" data-testid="tarot-amour-form">
            <label className="block text-[10px] uppercase mb-3" style={{ color: '#D4AF37', letterSpacing: '0.25em', fontFamily: 'Cinzel, serif' }}>
              Votre question amoureuse
            </label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ex : Ma relation avec Julien va-t-elle évoluer positivement ?"
              rows={3}
              className="w-full p-3 rounded-lg mb-4"
              data-testid="tarot-amour-question"
              style={{
                background: 'rgba(20,15,35,0.6)',
                border: '1px solid rgba(212,175,55,0.25)',
                color: '#F5EEE0',
                fontFamily: 'Cormorant Garamond, serif',
                fontSize: 15,
              }}
            />
            <button
              onClick={handleTirage}
              disabled={loading}
              className="plume-btn-primary w-full justify-center"
              data-testid="tarot-amour-submit"
              style={{ display: 'inline-flex' }}
            >
              {loading
                ? <><Loader2 className="w-4 h-4 animate-spin" /> Consultation en cours...</>
                : <><Heart className="w-4 h-4" strokeWidth={1.5} /> Tirer les 3 cartes ({CREDIT_COST} crédits) <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></>}
            </button>
            {error && (
              <p className="text-xs mt-3" style={{ color: '#f87171' }} data-testid="tarot-amour-error">{error}</p>
            )}
          </div>
        )}

        {reading && (
          <div className="fade-in" data-testid="tarot-amour-result">
            {/* 3 cartes côte à côte */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 max-w-3xl mx-auto">
              {reading.tirage.map((entry, idx) => (
                <div key={idx} className="flex flex-col items-center" data-testid={`amour-slot-${entry.position_id}`}>
                  <div className="tarot-flip-scene" style={{ width: 140, height: 240 }}>
                    <div className={`tarot-flip-inner ${revealedIdx >= idx ? 'is-flipped' : ''}`}>
                      <div className="tarot-flip-back">
                        <div className="tarot-back-pattern">
                          <div className="tarot-back-star">✦</div>
                          <div className="tarot-back-title">PLUME ASTRALE</div>
                          <div className="tarot-back-star">✦</div>
                        </div>
                      </div>
                      <div
                        className={`tarot-flip-front ${entry.carte.is_reversed ? 'is-reversed' : ''}`}
                        style={{ border: '2px solid rgba(212,175,55,0.5)', boxShadow: '0 0 30px rgba(212,175,55,0.3)' }}
                      >
                        <img
                          src={entry.carte.image.startsWith('http') ? entry.carte.image : `${API}${entry.carte.image}`}
                          alt={entry.carte.nom}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    </div>
                  </div>
                  {/* Label position + nom carte (post-reveal) */}
                  <div className="text-center mt-4">
                    <div style={{ fontFamily: 'Cinzel, serif', fontSize: 11, color: '#D4AF37', letterSpacing: '0.28em' }}>
                      {entry.position_nom.toUpperCase()}
                    </div>
                    {revealedIdx >= idx && (
                      <div className="mt-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontSize: 20, fontStyle: 'italic' }}>
                        {entry.carte.nom}
                        {entry.carte.is_reversed && <span style={{ marginLeft: 6, fontSize: 14 }}>🔄</span>}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Interprétations détaillées */}
            {revealedIdx >= 2 && (
              <>
                <h2 className="text-center mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 26, color: '#F5EEE0', fontStyle: 'italic', fontWeight: 300 }}>
                  Le message des Arcanes
                </h2>
                <div className="space-y-4 mb-10 max-w-2xl mx-auto">
                  {reading.tirage.map((entry, idx) => (
                    <div key={idx} className="plume-glass p-5" data-testid={`amour-interp-${entry.position_id}`}>
                      <div className="flex items-center gap-2 mb-2">
                        <Heart className="w-4 h-4" fill="#D4AF37" strokeWidth={0} />
                        <div style={{ fontFamily: 'Cinzel, serif', fontSize: 12, color: '#F5EEE0', letterSpacing: '0.18em' }}>
                          {entry.position_nom.toUpperCase()} — <span style={{ color: '#D4AF37' }}>{entry.carte.nom}</span>
                          {entry.carte.is_reversed && <span style={{ marginLeft: 6, fontSize: 11 }}>🔄</span>}
                        </div>
                      </div>
                      <div className="text-xs mb-2" style={{ color: 'rgba(227,215,255,0.55)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
                        {entry.position_description}
                      </div>
                      {entry.carte.mots_cles_amour && (
                        <div className="text-sm mb-2" style={{ color: '#E3D7FF', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
                          {entry.carte.mots_cles_amour}
                        </div>
                      )}
                      <p className="text-sm" style={{ color: 'rgba(245,238,224,0.85)', fontFamily: 'Cormorant Garamond, serif', lineHeight: 1.55 }}>
                        {entry.interpretation}
                      </p>
                    </div>
                  ))}
                </div>

                {/* Synthèse Soléna */}
                <div className="plume-glass p-6 md:p-8 mb-8 max-w-2xl mx-auto" data-testid="amour-synthese">
                  <p className="text-[10px] uppercase mb-3" style={{ color: '#D4AF37', letterSpacing: '0.32em', fontFamily: 'Cinzel, serif' }}>
                    ✦ Le mot de Soléna ✦
                  </p>
                  <FadeInEnrichedText text={reading.synthese} testId="amour-synthese-text" />
                </div>

                <div className="text-center">
                  <button onClick={reset} className="plume-btn-ghost" data-testid="tarot-amour-reset">
                    Poser une autre question
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      <style>{`
        .fade-in { animation: fadeIn 0.6s ease-out; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
      `}</style>
    </>
  );
};

export default TarotAmour;
