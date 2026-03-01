import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, ArrowLeft, ArrowRight } from 'lucide-react';

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
  const [formData, setFormData] = useState({
    prenom: '', email: '', dateNaissance: '', heureNaissance: '', ville: '',
  });

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) setTirageCount(parseInt(saved, 10) || 0);
    const userData = localStorage.getItem(DATA_KEY);
    if (userData) setHasRegistered(true);
  }, []);

  const handleTirage = async () => {
    if (!question.trim()) return;
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
    localStorage.setItem(DATA_KEY, JSON.stringify(formData));
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
    if (orientation === 'oui') return { color: '#7CB88A', label: 'OUI' };
    if (orientation === 'non') return { color: '#C97878', label: 'NON' };
    return { color: 'var(--pa-accent)', label: 'NEUTRE' };
  };

  // Registration form
  if (showForm && !hasRegistered) {
    return (
      <div className="min-h-screen flex flex-col justify-center px-6 md:px-8 py-12">
        <div className="max-w-md mx-auto w-full">
          <button onClick={() => setShowForm(false)} className="link-editorial text-xs mb-12" data-testid="back-form-btn">
            <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Retour
          </button>

          <div data-testid="registration-form">
            <p className="section-label">Inscription</p>
            <h2
              className="text-2xl md:text-3xl mb-4"
              style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
            >
              Continuez vos tirages
            </h2>
            <p className="text-sm mb-10" style={{ color: 'var(--pa-muted)' }}>
              Vous avez utilise vos {MAX_FREE_TIRAGES} tirages gratuits.
              Renseignez vos informations pour continuer.
            </p>

            <form onSubmit={handleRegistration} className="space-y-6">
              <div>
                <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Prenom *</label>
                <input type="text" required value={formData.prenom} onChange={e => setFormData({...formData, prenom: e.target.value})}
                  placeholder="Votre prenom" className="input-boxed" data-testid="form-prenom" />
              </div>
              <div>
                <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Email *</label>
                <input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})}
                  placeholder="votre@email.com" className="input-boxed" data-testid="form-email" />
              </div>
              <div>
                <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Date de naissance *</label>
                <input type="date" required value={formData.dateNaissance} onChange={e => setFormData({...formData, dateNaissance: e.target.value})}
                  className="input-boxed" data-testid="form-date" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Heure</label>
                  <input type="time" value={formData.heureNaissance} onChange={e => setFormData({...formData, heureNaissance: e.target.value})}
                    className="input-boxed" data-testid="form-heure" />
                </div>
                <div>
                  <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Ville</label>
                  <input type="text" value={formData.ville} onChange={e => setFormData({...formData, ville: e.target.value})}
                    placeholder="Paris" className="input-boxed" data-testid="form-ville" />
                </div>
              </div>

              <button type="submit" className="btn-editorial w-full justify-center mt-4" data-testid="form-submit">
                Debloquer mes tirages
              </button>
            </form>
          </div>

          {/* Astrology suggestion */}
          <div className="mt-12 pt-8" style={{ borderTop: '1px solid var(--pa-divider)' }} data-testid="astro-upsell-from-tarot">
            <p className="text-sm mb-3" style={{ color: 'var(--pa-heading)', fontFamily: 'Cormorant Garamond, serif', fontSize: '1.1rem' }}>
              Decouvrez aussi votre Theme Astral
            </p>
            <p className="text-xs mb-4" style={{ color: 'var(--pa-muted)' }}>
              28+ pages personnalisees avec carte du ciel et previsions
            </p>
            <button onClick={() => navigate('/formulaire')} className="link-editorial text-xs">
              Voir mon apercu gratuit <ArrowRight className="w-3.5 h-3.5" strokeWidth={1.5} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-6 md:px-8 py-20 md:py-28">
      <div className="max-w-xl mx-auto">

        {/* Back */}
        <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12" data-testid="back-btn">
          <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
        </button>

        {/* Header */}
        <div className="mb-12">
          <p className="section-label">Tirage sacre</p>
          <h1
            className="text-3xl md:text-4xl mb-4"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
          >
            Tarot Oui / Non
          </h1>
          <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
            Posez votre question et laissez les Arcanes Majeurs vous repondre
          </p>
        </div>

        {/* Counter */}
        {!hasRegistered && (
          <div className="mb-8" data-testid="tirage-counter">
            <span className="text-xs tracking-widest" style={{ color: 'var(--pa-accent)', letterSpacing: '0.1em' }}>
              {remainingFree > 0
                ? `${remainingFree} tirage${remainingFree > 1 ? 's' : ''} gratuit${remainingFree > 1 ? 's' : ''} restant${remainingFree > 1 ? 's' : ''}`
                : 'Tirages gratuits epuises'
              }
            </span>
          </div>
        )}

        {/* Question */}
        <div className="mb-8" data-testid="question-form">
          <label className="block text-xs tracking-widest uppercase mb-3" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
            Votre question
          </label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Posez votre question ici..."
            className="input-boxed resize-none h-24 w-full"
            data-testid="question-input"
          />
          <button
            onClick={handleTirage}
            disabled={loading || !question.trim()}
            className="btn-editorial mt-6 disabled:opacity-30"
            data-testid="tirage-btn"
          >
            {loading ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Consultation des Arcanes...</>
            ) : (
              <>Tirer une carte</>
            )}
          </button>
        </div>

        {/* Result */}
        {result && isRevealed && (
          <div className="mt-12 pt-12 animate-fade-in" style={{ borderTop: '1px solid var(--pa-divider)' }}>

            {/* Card */}
            <div className="text-center mb-12" data-testid="carte-result">
              <p className="text-xs tracking-widest uppercase mb-6" style={{ color: 'var(--pa-muted)', letterSpacing: '0.12em' }}>
                Arcane tire
              </p>

              <div className="w-28 h-40 mx-auto mb-6 rounded-lg overflow-hidden"
                   style={{ border: '1px solid var(--pa-divider)' }}>
                {result.carte?.image ? (
                  <img src={`${API_URL}${result.carte.image}`} alt={result.carte.nom} className="w-full h-full object-cover" data-testid="carte-image" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center" style={{ background: 'var(--pa-surface)' }}>
                    <span className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-accent)' }}>
                      {result.carte?.numero === 0 ? '0' : result.carte?.numero}
                    </span>
                  </div>
                )}
              </div>

              <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)' }}>
                {result.carte?.nom}
              </h2>
              <p className="text-xs mb-6" style={{ color: 'var(--pa-muted)' }}>{result.carte?.energie}</p>

              {(() => {
                const style = getOrientationStyle(result.orientation);
                return (
                  <span
                    className="inline-block px-6 py-2 text-sm tracking-widest uppercase"
                    style={{ color: style.color, border: `1px solid ${style.color}30`, letterSpacing: '0.15em' }}
                    data-testid="orientation-badge"
                  >
                    {style.label}
                  </span>
                );
              })()}
            </div>

            {/* Message */}
            <div className="mb-12" data-testid="message-result">
              <p className="text-xs tracking-widest uppercase mb-4" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
                Message des Arcanes
              </p>
              <p className="text-base leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
                {result.reponse}
              </p>
            </div>

            {/* Suggestions */}
            <div className="pt-10" style={{ borderTop: '1px solid var(--pa-divider)' }}>
              <p className="text-xs tracking-widest uppercase mb-6" style={{ color: 'var(--pa-muted)', letterSpacing: '0.12em' }}>
                Pour aller plus loin
              </p>

              <div className="space-y-6" data-testid="upsell-tarologie">
                <button onClick={() => navigate('/tarologie')} className="block w-full text-left group">
                  <p className="text-sm mb-1 transition-colors duration-300 group-hover:text-[#C5A059]" style={{ color: 'var(--pa-heading)' }}>
                    Tarologie & Mediumnite — 35 EUR
                  </p>
                  <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
                    5 cartes, lecture mediumnique et PDF personnalise
                  </p>
                </button>

                {hasRegistered && (
                  <button onClick={() => navigate('/resultats')} className="block w-full text-left group" data-testid="astro-cross-sell">
                    <p className="text-sm mb-1 transition-colors duration-300 group-hover:text-[#C5A059]" style={{ color: 'var(--pa-heading)' }}>
                      Votre Theme Astral Complet
                    </p>
                    <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
                      Carte du ciel, aspects planetaires et previsions 2026
                    </p>
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TarotOuiNon;
