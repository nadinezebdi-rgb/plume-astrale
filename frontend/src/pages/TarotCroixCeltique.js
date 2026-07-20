import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Sparkles, Loader2, ArrowLeft, ArrowRight, Coins } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import FadeInEnrichedText from '@/components/FadeInEnrichedText';
import { event as track, EVENTS } from '@/lib/analytics';

const API = process.env.REACT_APP_BACKEND_URL;
const CREDIT_COST = 9;

const TarotCroixCeltique = () => {
  const navigate = useNavigate();
  const { isAuthenticated, session, user } = useAuth();
  const [question, setQuestion] = useState('');
  const [reading, setReading] = useState(null);
  const [revealedIdx, setRevealedIdx] = useState(-1); // Révèle progressivement les 10 cartes
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleTirage = async () => {
    if (!question.trim() || question.trim().length < 3) {
      setError('Merci de formuler une question complète (min. 3 caractères).');
      return;
    }
    if (!isAuthenticated) {
      navigate('/connexion?redirect=/outils/tarot/croix-celtique');
      return;
    }
    setError('');
    setReading(null);
    setRevealedIdx(-1);
    setLoading(true);
    track(EVENTS.CREDIT_PURCHASE, { tool: 'tarot_croix_celtique', cost: CREDIT_COST });
    try {
      const r = await axios.post(
        `${API}/api/tarot/croix-celtique`,
        { question, prenom: user?.first_name || user?.email?.split('@')[0] || 'toi' },
        { headers: { Authorization: `Bearer ${session.access_token}` } },
      );
      setReading(r.data);
      // Révélation progressive : 1 carte toutes les 900 ms
      r.data.tirage.forEach((_, i) => {
        setTimeout(() => setRevealedIdx((cur) => Math.max(cur, i)), 900 * (i + 1));
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
        title="Croix Celtique — Tarot 10 cartes | Plume Astrale"
        description="Tirage traditionnel de la Croix Celtique. 10 cartes lues par Soléna pour les questions profondes."
      />

      <div className="max-w-5xl mx-auto px-6 pt-28 pb-24">
        <button onClick={() => navigate('/outils')} className="link-editorial text-xs mb-8 flex items-center gap-2" data-testid="croix-celtique-back">
          <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Outils
        </button>

        <div className="text-center mb-10">
          <p className="text-[10px] uppercase mb-3" style={{ color: '#D4AF37', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}>
            ✦ Tirage sacré ✦
          </p>
          <h1
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontWeight: 300,
              fontSize: 'clamp(32px, 4.5vw, 52px)',
              color: '#F5EEE0',
              lineHeight: 1.1,
              marginBottom: 12,
            }}
          >
            La <em style={{ fontStyle: 'italic', color: '#D4AF37' }}>Croix Celtique</em>
          </h1>
          <p className="text-sm md:text-base max-w-xl mx-auto" style={{ color: 'rgba(227,215,255,0.7)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
            10 cartes disposées en croix pour éclairer les questions profondes — passé, présent, futur, environnement, ton propre regard et l&apos;issue.
          </p>
          <div className="mt-4 inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs" style={{ background: 'rgba(212,175,55,0.1)', border: '1px solid rgba(212,175,55,0.3)', color: '#D4AF37' }}>
            <Coins className="w-3.5 h-3.5" strokeWidth={1.5} />
            {CREDIT_COST} crédits par tirage
          </div>
        </div>

        {!reading && (
          <div className="plume-glass p-6 md:p-8 max-w-2xl mx-auto" data-testid="croix-celtique-form">
            <label className="block text-[10px] uppercase mb-3" style={{ color: '#D4AF37', letterSpacing: '0.25em', fontFamily: 'Cinzel, serif' }}>
              Votre question
            </label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ex : Quel est mon chemin de vie pour la prochaine année ?"
              rows={3}
              className="w-full p-3 rounded-lg mb-4"
              data-testid="croix-celtique-question"
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
              data-testid="croix-celtique-submit"
              style={{ display: 'inline-flex' }}
            >
              {loading
                ? <><Loader2 className="w-4 h-4 animate-spin" /> Consultation des Arcanes...</>
                : <><Sparkles className="w-4 h-4" strokeWidth={1.5} /> Tirer les 10 cartes ({CREDIT_COST} crédits) <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></>}
            </button>
            {error && (
              <p className="text-xs mt-3" style={{ color: '#f87171' }} data-testid="croix-celtique-error">{error}</p>
            )}
          </div>
        )}

        {reading && (
          <div className="fade-in" data-testid="croix-celtique-result">
            {/* Grille des 10 cartes — layout croix celtique */}
            <div className="tarot-croix-layout mb-14">
              {reading.tirage.map((entry, idx) => (
                <div
                  key={idx}
                  className={`tarot-croix-slot slot-${entry.position_id}`}
                  data-testid={`croix-slot-${entry.position_id}`}
                >
                  <div className="tarot-flip-scene" style={{ width: 100, height: 170 }}>
                    <div className={`tarot-flip-inner ${revealedIdx >= idx ? 'is-flipped' : ''}`}>
                      <div className="tarot-flip-back">
                        <div className="tarot-back-pattern">
                          <div className="tarot-back-star" style={{ fontSize: 18 }}>✦</div>
                          <div className="tarot-back-title" style={{ fontSize: 8, letterSpacing: '0.28em' }}>PLUME</div>
                          <div className="tarot-back-star" style={{ fontSize: 18 }}>✦</div>
                        </div>
                      </div>
                      <div
                        className={`tarot-flip-front ${entry.carte.is_reversed ? 'is-reversed' : ''}`}
                        style={{ border: '1.5px solid rgba(212,175,55,0.5)', boxShadow: '0 0 20px rgba(212,175,55,0.25)' }}
                      >
                        <img
                          src={entry.carte.image.startsWith('http') ? entry.carte.image : `${API}${entry.carte.image}`}
                          alt={entry.carte.nom}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    </div>
                  </div>
                  <div className="text-center mt-2">
                    <div style={{ fontFamily: 'Cinzel, serif', fontSize: 9, color: '#D4AF37', letterSpacing: '0.15em' }}>
                      {entry.position_id}. {entry.position_nom}
                    </div>
                    {revealedIdx >= idx && (
                      <div className="text-[10px] mt-0.5" style={{ color: 'rgba(227,215,255,0.7)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
                        {entry.carte.nom}
                        {entry.carte.is_reversed && <span style={{ color: '#D4AF37', marginLeft: 4 }}>🔄</span>}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Interprétations détaillées */}
            {revealedIdx >= 9 && (
              <>
                <h2 className="text-center mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 26, color: '#F5EEE0', fontStyle: 'italic', fontWeight: 300 }}>
                  Les 10 chapitres de ta lecture
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
                  {reading.tirage.map((entry, idx) => (
                    <div key={idx} className="plume-glass p-5" data-testid={`croix-interp-${entry.position_id}`}>
                      <div className="flex items-center gap-2 mb-2">
                        <span
                          className="inline-block w-7 h-7 rounded-full flex items-center justify-center text-xs"
                          style={{ background: 'rgba(212,175,55,0.15)', border: '1px solid rgba(212,175,55,0.4)', color: '#D4AF37', fontFamily: 'Cinzel, serif' }}
                        >
                          {entry.position_id}
                        </span>
                        <div style={{ fontFamily: 'Cinzel, serif', fontSize: 12, color: '#F5EEE0', letterSpacing: '0.12em' }}>
                          {entry.position_nom.toUpperCase()}
                        </div>
                      </div>
                      <div className="text-sm mb-2" style={{ color: 'rgba(227,215,255,0.55)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
                        {entry.position_description}
                      </div>
                      <div className="mb-2" style={{ color: '#D4AF37', fontFamily: 'Cormorant Garamond, serif', fontSize: 17 }}>
                        {entry.carte.nom}
                        {entry.carte.is_reversed && <span style={{ marginLeft: 6, fontSize: 12 }}>🔄 retournée</span>}
                      </div>
                      <p className="text-sm" style={{ color: 'rgba(245,238,224,0.85)', fontFamily: 'Cormorant Garamond, serif', lineHeight: 1.55 }}>
                        {entry.interpretation}
                      </p>
                    </div>
                  ))}
                </div>

                {/* Synthèse Soléna */}
                <div className="plume-glass p-6 md:p-8 mb-8" data-testid="croix-synthese">
                  <p className="text-[10px] uppercase mb-3" style={{ color: '#D4AF37', letterSpacing: '0.32em', fontFamily: 'Cinzel, serif' }}>
                    ✦ Synthèse de Soléna ✦
                  </p>
                  <FadeInEnrichedText text={reading.synthese} testId="croix-synthese-text" />
                </div>

                <div className="text-center">
                  <button onClick={reset} className="plume-btn-ghost" data-testid="croix-celtique-reset">
                    Poser une autre question
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Layout CSS croix celtique */}
      <style>{`
        .tarot-croix-layout {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 20px 30px;
          max-width: 720px;
          margin: 0 auto;
          justify-items: center;
        }
        /* Position spatiale approchant la croix celtique traditionnelle */
        .slot-1  { grid-column: 2; grid-row: 2; }  /* Coeur (centre) */
        .slot-2  { grid-column: 2; grid-row: 2; transform: rotate(90deg) translate(0, 60px); z-index: 2; opacity: 0.95; }  /* Défi (horizontal sur le coeur) */
        .slot-3  { grid-column: 2; grid-row: 3; }  /* Racine (bas) */
        .slot-4  { grid-column: 1; grid-row: 2; }  /* Passé (gauche) */
        .slot-5  { grid-column: 2; grid-row: 1; }  /* Sommet (haut) */
        .slot-6  { grid-column: 3; grid-row: 2; }  /* Futur (droite) */
        .slot-7  { grid-column: 4; grid-row: 4; }  /* Toi-même */
        .slot-8  { grid-column: 4; grid-row: 3; }  /* Entourage */
        .slot-9  { grid-column: 4; grid-row: 2; }  /* Espoirs/Craintes */
        .slot-10 { grid-column: 4; grid-row: 1; }  /* Issue */
        @media (max-width: 640px) {
          .tarot-croix-layout { grid-template-columns: repeat(2, 1fr); }
          .slot-1, .slot-2, .slot-3, .slot-4, .slot-5, .slot-6, .slot-7, .slot-8, .slot-9, .slot-10 {
            grid-column: auto; grid-row: auto; transform: none;
          }
        }
        .fade-in { animation: fadeIn 0.6s ease-out; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
      `}</style>
    </>
  );
};

export default TarotCroixCeltique;
