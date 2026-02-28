import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Loader2, ArrowLeft, Sparkles, Lock, ArrowRight, Moon, User, MapPin, Clock, Calendar, Mail } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const MAX_FREE_TIRAGES = 3;
const STORAGE_KEY = 'plume_tarot_tirages';
const DATA_KEY = 'plume_tarot_user_data';

const TarotOuiNon = () => {
  const navigate = useNavigate();
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isRevealed, setIsRevealed] = useState(false);
  const [tirageCount, setTirageCount] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [hasRegistered, setHasRegistered] = useState(false);
  
  // Registration form
  const [formData, setFormData] = useState({
    prenom: '',
    email: '',
    dateNaissance: '',
    heureNaissance: '',
    ville: '',
  });

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) setTirageCount(parseInt(saved, 10) || 0);
    const userData = localStorage.getItem(DATA_KEY);
    if (userData) setHasRegistered(true);
  }, []);

  const handleTirage = async () => {
    if (!question.trim()) return;

    // Check if limit reached and not registered
    if (tirageCount >= MAX_FREE_TIRAGES && !hasRegistered) {
      setShowForm(true);
      return;
    }

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
      
      const newCount = tirageCount + 1;
      setTirageCount(newCount);
      localStorage.setItem(STORAGE_KEY, newCount.toString());
      
      setTimeout(() => setIsRevealed(true), 1500);
    } catch (e) {
      console.error('Tarot error:', e);
    }
    setLoading(false);
  };

  const handleRegistration = (e) => {
    e.preventDefault();
    if (!formData.prenom || !formData.email || !formData.dateNaissance) return;
    
    // Save user data
    localStorage.setItem(DATA_KEY, JSON.stringify(formData));
    // Also save to main plume data for cross-selling
    localStorage.setItem('plume_astrale_data', JSON.stringify({
      prenom: formData.prenom,
      dateNaissance: formData.dateNaissance,
      heureNaissance: formData.heureNaissance || '12:00',
      ville: formData.ville || 'Paris',
      email: formData.email,
    }));
    
    setHasRegistered(true);
    setShowForm(false);
  };

  const remainingFree = Math.max(0, MAX_FREE_TIRAGES - tirageCount);

  const getOrientationStyle = (orientation) => {
    if (orientation === 'oui') return { color: '#4ECB71', label: 'OUI', bg: 'rgba(78, 203, 113, 0.15)' };
    if (orientation === 'non') return { color: '#E8526E', label: 'NON', bg: 'rgba(232, 82, 110, 0.15)' };
    return { color: '#C5A059', label: 'NEUTRE', bg: 'rgba(197, 160, 89, 0.15)' };
  };

  // Registration form modal
  if (showForm && !hasRegistered) {
    return (
      <div className="min-h-screen relative">
        <StarField />
        <div className="relative z-10 py-12 px-4 md:px-6">
          <div className="max-w-lg mx-auto">
            <button onClick={() => setShowForm(false)} className="flex items-center gap-2 text-[#C5A059]/60 hover:text-[#C5A059] mb-8 transition-colors" data-testid="back-form-btn">
              <ArrowLeft className="w-4 h-4" /> Retour
            </button>

            <div className="card-mystical p-8 glow-gold" data-testid="registration-form">
              <div className="text-center mb-8">
                <Lock className="w-10 h-10 text-[#C5A059] mx-auto mb-4" strokeWidth={1} />
                <h2 className="text-2xl mb-2" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                  Continuez vos tirages
                </h2>
                <p className="text-[#E0D9F6]/60 text-sm font-light">
                  Vous avez utilise vos {MAX_FREE_TIRAGES} tirages gratuits.
                  Renseignez vos informations pour continuer a consulter les Arcanes.
                </p>
              </div>

              <form onSubmit={handleRegistration} className="space-y-4">
                <div>
                  <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1.5">
                    <User className="w-3.5 h-3.5 inline mr-1" /> Prenom *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.prenom}
                    onChange={e => setFormData({...formData, prenom: e.target.value})}
                    placeholder="Votre prenom"
                    className="w-full px-4 py-2.5 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] placeholder:text-[#E0D9F6]/30 focus:outline-none focus:border-[#C5A059] text-sm"
                    data-testid="form-prenom"
                  />
                </div>
                <div>
                  <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1.5">
                    <Mail className="w-3.5 h-3.5 inline mr-1" /> Email *
                  </label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={e => setFormData({...formData, email: e.target.value})}
                    placeholder="votre@email.com"
                    className="w-full px-4 py-2.5 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] placeholder:text-[#E0D9F6]/30 focus:outline-none focus:border-[#C5A059] text-sm"
                    data-testid="form-email"
                  />
                </div>
                <div>
                  <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1.5">
                    <Calendar className="w-3.5 h-3.5 inline mr-1" /> Date de Naissance *
                  </label>
                  <input
                    type="date"
                    required
                    value={formData.dateNaissance}
                    onChange={e => setFormData({...formData, dateNaissance: e.target.value})}
                    className="w-full px-4 py-2.5 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] focus:outline-none focus:border-[#C5A059] text-sm"
                    data-testid="form-date"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1.5">
                      <Clock className="w-3.5 h-3.5 inline mr-1" /> Heure de Naissance
                    </label>
                    <input
                      type="time"
                      value={formData.heureNaissance}
                      onChange={e => setFormData({...formData, heureNaissance: e.target.value})}
                      className="w-full px-4 py-2.5 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] focus:outline-none focus:border-[#C5A059] text-sm"
                      data-testid="form-heure"
                    />
                  </div>
                  <div>
                    <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1.5">
                      <MapPin className="w-3.5 h-3.5 inline mr-1" /> Ville de Naissance
                    </label>
                    <input
                      type="text"
                      value={formData.ville}
                      onChange={e => setFormData({...formData, ville: e.target.value})}
                      placeholder="Paris"
                      className="w-full px-4 py-2.5 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] placeholder:text-[#E0D9F6]/30 focus:outline-none focus:border-[#C5A059] text-sm"
                      data-testid="form-ville"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="btn-mystical-filled rounded-full flex items-center gap-2 mx-auto mt-6 px-8 py-3"
                  data-testid="form-submit"
                >
                  <Sparkles className="w-5 h-5" /> Debloquer mes tirages
                </button>
                
                <p className="text-center text-[#E0D9F6]/30 text-xs mt-3">
                  En continuant, vous acceptez de recevoir des communications de Plume Astrale.
                </p>
              </form>
            </div>

            {/* Astrology upsell */}
            <div className="mt-6 card-mystical text-center p-6" data-testid="astro-upsell-from-tarot">
              <Moon className="w-8 h-8 text-[#C5A059] mx-auto mb-3" strokeWidth={1} />
              <p className="text-[#F3E5AB] text-sm mb-3" style={{ fontFamily: 'Cinzel, serif' }}>
                Decouvrez aussi votre Theme Astral Complet
              </p>
              <p className="text-[#E0D9F6]/50 text-xs mb-4">
                28+ pages personnalisees avec carte du ciel, aspects planetaires et previsions
              </p>
              <button
                onClick={() => navigate('/formulaire')}
                className="text-[#C5A059] text-sm underline hover:text-[#F3E5AB] transition-colors"
              >
                Voir mon apercu gratuit
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative">
      <StarField />
      <div className="relative z-10 py-12 px-4 md:px-6">
        <div className="max-w-2xl mx-auto">
          
          {/* Back */}
          <button onClick={() => navigate('/')} className="flex items-center gap-2 text-[#C5A059]/60 hover:text-[#C5A059] mb-8 transition-colors" data-testid="back-btn">
            <ArrowLeft className="w-4 h-4" /> Accueil
          </button>

          {/* Header */}
          <div className="text-center mb-8">
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-3 font-light">
              Tirage Sacre
            </p>
            <h1 className="text-3xl md:text-5xl mb-3" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Tarot Oui / Non
            </h1>
            <p className="text-[#E0D9F6]/60 font-light text-sm">
              Posez votre question et laissez les Arcanes Majeurs vous repondre
            </p>
          </div>

          {/* Free tirages counter */}
          {!hasRegistered && (
            <div className="text-center mb-6" data-testid="tirage-counter">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#C5A059]/10 border border-[#C5A059]/20">
                <Star className="w-3.5 h-3.5 text-[#C5A059]" />
                <span className="text-[#C5A059] text-xs font-medium">
                  {remainingFree > 0 
                    ? `${remainingFree} tirage${remainingFree > 1 ? 's' : ''} gratuit${remainingFree > 1 ? 's' : ''} restant${remainingFree > 1 ? 's' : ''}`
                    : 'Tirages gratuits epuises'
                  }
                </span>
              </div>
            </div>
          )}

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
              <div className="card-mystical text-center p-8 glow-gold" data-testid="carte-result">
                <div className="mb-4">
                  <span className="text-[#C5A059] text-sm uppercase tracking-widest">Arcane Tire</span>
                </div>
                
                <div className="w-32 h-44 mx-auto mb-6 rounded-xl overflow-hidden" 
                     style={{ border: '2px solid #C5A059' }}>
                  {result.carte?.image ? (
                    <img src={`${API_URL}${result.carte.image}`} alt={result.carte.nom} className="w-full h-full object-cover" data-testid="carte-image" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #1A0B2E, #2D1B4E)' }}>
                      <span className="text-[#C5A059] text-3xl font-bold" style={{ fontFamily: 'Cinzel, serif' }}>
                        {result.carte?.numero === 0 ? '0' : result.carte?.numero}
                      </span>
                    </div>
                  )}
                </div>

                <h2 className="text-2xl mb-2" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                  {result.carte?.nom}
                </h2>
                <p className="text-[#C5A059]/70 text-sm mb-4">{result.carte?.energie}</p>

                {(() => {
                  const style = getOrientationStyle(result.orientation);
                  return (
                    <div className="inline-block px-6 py-2 rounded-full text-lg font-bold mb-6"
                         style={{ color: style.color, background: style.bg, border: `1px solid ${style.color}40` }}
                         data-testid="orientation-badge">
                      {style.label}
                    </div>
                  );
                })()}
              </div>

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
                  Decouvrez la Tarologie & Mediumnite complete : 5 cartes, lecture mediumnique et PDF personnalise
                </p>
                <button
                  onClick={() => navigate('/tarologie')}
                  className="btn-mystical-filled rounded-full px-8 py-3 inline-flex items-center gap-2"
                  data-testid="cta-tarologie-full"
                >
                  <Sparkles className="w-5 h-5" /> Tarologie Complete — 35 EUR
                </button>
              </div>

              {/* Astrology upsell if registered */}
              {hasRegistered && (
                <div className="card-mystical text-center p-6 border-[#C5A059]/20" data-testid="astro-cross-sell">
                  <Moon className="w-7 h-7 text-[#C5A059] mx-auto mb-3" strokeWidth={1} />
                  <h3 className="text-lg mb-2" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                    Votre Theme Astral Complet
                  </h3>
                  <p className="text-[#E0D9F6]/50 text-xs mb-4">
                    Vos donnees de naissance sont deja enregistrees. Decouvrez votre carte du ciel, vos aspects planetaires et vos previsions 2026.
                  </p>
                  <button
                    onClick={() => navigate('/resultats')}
                    className="text-[#C5A059] text-sm flex items-center gap-1 mx-auto hover:text-[#F3E5AB] transition-colors"
                  >
                    Voir mon apercu gratuit <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TarotOuiNon;
