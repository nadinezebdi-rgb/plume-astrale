import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowLeft, Loader2, Send, Clock, Star } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import PageHero from '@/components/PageHero';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const EXAMPLE_QUESTIONS = [
  "Vais-je obtenir cet emploi ?",
  "Est-ce le bon moment pour déménager ?",
  "Ma relation va-t-elle évoluer positivement ?",
  "Vais-je réussir ce projet ?",
  "Dois-je accepter cette offre ?",
];

export default function Horairie() {
  const { isAuthenticated, token } = useAuth();
  const navigate = useNavigate();
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAsk = async () => {
    const q = question.trim();
    if (!q || q.length < 5) return;
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await axios.post(
        `${API_URL}/api/astrology/v3/horary/ask`,
        { question: q },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data?.detail || 'Erreur lors de la consultation horaire.');
    }
    setLoading(false);
  };

  if (!isAuthenticated) return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#0C0918' }}>
      <div className="text-center px-6">
        <p className="text-[#B8B0C8] mb-4">Connectez-vous pour accéder à l'astrologie horaire.</p>
        <button onClick={() => navigate('/connexion')} className="btn-mystical">Se connecter</button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen" style={{ background: '#0C0918' }}>
      <div className="max-w-2xl mx-auto px-4 py-8">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-[#B8B0C8]/60 hover:text-[#C5A059] transition-colors mb-6 text-sm">
          <ArrowLeft className="w-4 h-4" /> Retour
        </button>

        <PageHero
          image="/images/astrale/image-astrale-4.jpg"
          title="Horairie"
          subtitle="L'art divinatoire le plus précis — posez une question"
        />

        {/* Saisie de la question */}
        <div className="card-mystical mb-6">
          <h2 className="text-lg mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
            Votre question
          </h2>
          <p className="text-[#B8B0C8]/60 text-xs mb-4 font-light">
            Posez une question précise sur un sujet qui vous tient à cœur. L'horairie répond aux questions binaires ou de timing.
          </p>
          <textarea
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="Ex: Vais-je obtenir cet emploi ?"
            rows={3}
            style={{
              width: '100%', background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(197,160,89,0.25)', borderRadius: 12,
              padding: '12px 16px', color: '#F0E6D3', fontSize: 15,
              fontFamily: 'Cormorant Garamond, serif', outline: 'none',
              resize: 'vertical', lineHeight: 1.6,
            }}
          />
          <div className="flex justify-between items-center mt-3">
            <span className="text-xs text-[#B8B0C8]/40">{question.length}/200 caractères</span>
            <button
              onClick={handleAsk}
              disabled={loading || question.trim().length < 5}
              className="flex items-center gap-2 px-5 py-2.5 rounded-full transition-all"
              style={{
                background: question.trim().length >= 5 ? 'rgba(197,160,89,0.2)' : 'rgba(255,255,255,0.04)',
                border: `1px solid ${question.trim().length >= 5 ? 'rgba(197,160,89,0.5)' : 'rgba(255,255,255,0.1)'}`,
                color: question.trim().length >= 5 ? '#C5A059' : '#B8B0C8',
                cursor: loading ? 'wait' : 'pointer',
                fontSize: 13,
              }}
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              {loading ? 'Consultation…' : 'Consulter les astres'}
            </button>
          </div>
        </div>

        {/* Questions exemples */}
        <div className="mb-6">
          <p className="text-xs text-[#B8B0C8]/40 mb-2">Questions exemples :</p>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_QUESTIONS.map((q, i) => (
              <button key={i} onClick={() => setQuestion(q)}
                className="px-3 py-1.5 rounded-full text-xs transition-all"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)', color: '#B8B0C8' }}>
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Erreur */}
        {error && (
          <div className="rounded-xl p-4 mb-6" style={{ background: 'rgba(248,113,113,0.1)', border: '1px solid rgba(248,113,113,0.25)' }}>
            <p className="text-sm text-[#f87171]">{error}</p>
          </div>
        )}

        {/* Résultat */}
        {result && (
          <div className="space-y-4">
            {/* Réponse principale */}
            <div className="card-mystical">
              <div className="flex items-center gap-2 mb-4">
                <Star className="w-5 h-5 text-[#C5A059]" strokeWidth={1.5} />
                <h2 className="text-xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                  Réponse de l'horairie
                </h2>
              </div>

              {/* Verdict */}
              {(result.answer || result.verdict || result.judgment) && (
                <div className="rounded-xl p-4 mb-4 text-center"
                  style={{ background: 'rgba(197,160,89,0.15)', border: '1px solid rgba(197,160,89,0.35)' }}>
                  <p className="text-xl font-semibold"
                    style={{ fontFamily: 'Cormorant Garamond, serif', color: '#C5A059' }}>
                    {result.answer || result.verdict || result.judgment}
                  </p>
                </div>
              )}

              {/* Confidence */}
              {result.confidence !== undefined && (
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-xs text-[#B8B0C8]/50">Confiance</span>
                  <div className="flex-1 h-2 rounded-full" style={{ background: 'rgba(255,255,255,0.08)' }}>
                    <div className="h-2 rounded-full transition-all"
                      style={{ width: `${result.confidence}%`, background: 'linear-gradient(90deg, #C5A059, #f0e6d3)' }} />
                  </div>
                  <span className="text-xs text-[#C5A059]">{result.confidence}%</span>
                </div>
              )}

              {/* Analyse */}
              {(result.analysis || result.interpretation || result.explanation) && (
                <p className="text-sm text-[#B8B0C8]/80 font-light leading-relaxed">
                  {result.analysis || result.interpretation || result.explanation}
                </p>
              )}

              {/* Timing */}
              {result.timing && (
                <div className="mt-4 rounded-lg p-3" style={{ background: 'rgba(96,165,250,0.1)', border: '1px solid rgba(96,165,250,0.2)' }}>
                  <div className="flex items-center gap-2 mb-1">
                    <Clock className="w-4 h-4 text-[#60a5fa]" strokeWidth={1.5} />
                    <span className="text-xs text-[#60a5fa]">Timing</span>
                  </div>
                  <p className="text-sm text-[#F0E6D3]">{result.timing}</p>
                </div>
              )}
            </div>

            {/* Facteurs planétaires */}
            {(result.significators || result.key_factors || result.planetary_factors || []).length > 0 && (
              <div className="card-mystical">
                <h3 className="text-lg mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                  Significateurs planétaires
                </h3>
                <div className="space-y-2">
                  {(result.significators || result.key_factors || result.planetary_factors).slice(0, 5).map((f, i) => (
                    <div key={i} className="rounded-lg px-3 py-2"
                      style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
                      <p className="text-sm font-medium text-[#C5A059]">{f.planet || f.name || f.significator}</p>
                      {(f.role || f.description || f.meaning) &&
                        <p className="text-xs text-[#B8B0C8]/60 mt-0.5">{f.role || f.description || f.meaning}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Avertissement */}
            <p className="text-center text-[#B8B0C8]/30 text-xs">
              L'horairie est un outil de guidance symbolique — elle éclaire sans dicter.
            </p>
          </div>
        )}

        <p className="text-center text-[#B8B0C8]/30 text-xs mt-8 font-light">
          Astrologie horaire traditionnelle — Lilly · Bonatti · Swiss Ephemeris
        </p>
      </div>
    </div>
  );
}
