import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, ArrowLeft, ArrowRight } from 'lucide-react';
import SEO from '@/components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const MAX_FREE_TIRAGES = 1;
const STORAGE_KEY = 'plume_tarot_tirages';
const STORAGE_DATE_KEY = 'plume_tarot_date';
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
    // Reset counter daily
    const today = new Date().toDateString();
    const savedDate = localStorage.getItem(STORAGE_DATE_KEY);
    if (savedDate !== today) {
      localStorage.setItem(STORAGE_DATE_KEY, today);
      localStorage.setItem(STORAGE_KEY, '0');
      setTirageCount(0);
    } else {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) setTirageCount(parseInt(saved, 10) || 0);
    }
    const userData = localStorage.getItem(DATA_KEY);
    if (userData) setHasRegistered(true);
  }, []);

  const handleTirage = async () => {
    if (!question.trim()) return;
    if (tirageCount >= MAX_FREE_TIRAGES) {
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

  const canDrawFree = tirageCount < MAX_FREE_TIRAGES;

  const getOrientationStyle = (orientation) => {
    if (orientation === 'oui') return { color: '#7CB88A', label: 'OUI' };
    if (orientation === 'non') return { color: '#C97878', label: 'NON' };
    return { color: 'var(--pa-accent)', label: 'NEUTRE' };
  };

  // Paywall for additional draws
  if (showForm && tirageCount >= MAX_FREE_TIRAGES) {
    return (
      <div className="min-h-screen relative">
        <div className="relative z-10 flex flex-col justify-center px-6 md:px-8 py-12" style={{ minHeight: '100vh' }}>
        <div className="max-w-md mx-auto w-full">
          <button onClick={() => setShowForm(false)} className="link-editorial text-xs mb-12" data-testid="back-form-btn">
            <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Retour
          </button>

          <div data-testid="paywall-form">
            <p className="section-label">Tirage suppl&eacute;mentaire</p>
            <h2
              className="text-2xl md:text-3xl mb-4"
              style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
            >
              Continuez vos tirages
            </h2>
            <p className="text-sm mb-6" style={{ color: 'var(--pa-muted)' }}>
              Vous avez utilis&eacute; votre tirage gratuit du jour.
            </p>

            <div className="card-mystical mb-8 text-center glow-gold">
              <p className="text-3xl font-bold mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-accent)' }}>
                4,99 &euro;
              </p>
              <p className="text-sm mb-4" style={{ color: 'var(--pa-muted)' }}>par tirage suppl&eacute;mentaire</p>
              <ul className="text-xs text-left mx-auto max-w-xs space-y-2 mb-6" style={{ color: 'var(--pa-body)' }}>
                <li>&#x2714; Tirage Oui/Non avec Arcane Majeur</li>
                <li>&#x2714; R&eacute;ponse d&eacute;taill&eacute;e et personnalis&eacute;e</li>
                <li>&#x2714; Conseil des Arcanes</li>
              </ul>
              <button className="btn-editorial w-full justify-center" data-testid="buy-tirage-btn">
                Obtenir mon tirage — 4,99 &euro;
              </button>
            </div>

            <p className="text-center text-xs" style={{ color: 'var(--pa-muted)' }}>
              Revenez demain pour un nouveau tirage gratuit
            </p>
          </div>

          {/* Astrology suggestion */}
          <div className="mt-12 pt-8" style={{ borderTop: '1px solid var(--pa-divider)' }} data-testid="astro-upsell-from-tarot">
            <p className="text-sm mb-3" style={{ color: 'var(--pa-heading)', fontFamily: 'Cormorant Garamond, serif', fontSize: '1.1rem' }}>
              D&eacute;couvrez aussi votre Th&egrave;me Astral
            </p>
            <p className="text-xs mb-4" style={{ color: 'var(--pa-muted)' }}>
              28+ pages personnalis&eacute;es avec carte du ciel et pr&eacute;visions
            </p>
            <button onClick={() => navigate('/formulaire')} className="link-editorial text-xs">
              Voir mon aper&ccedil;u gratuit <ArrowRight className="w-3.5 h-3.5" strokeWidth={1.5} />
            </button>
          </div>
        </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative">
      <SEO path="/tarot-oui-non" />
      <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
      <div className="max-w-xl mx-auto">

        {/* Back */}
        <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12" data-testid="back-btn">
          <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
        </button>

        {/* Header */}
        <div className="mb-12 flex items-start gap-6">
          <img src="https://customer-assets.emergentagent.com/job_6ebe2661-1b82-4742-afc5-632bf29dfcc5/artifacts/fupfyxdu_img2.png" alt="" className="w-20 md:w-28 flex-shrink-0 rounded-lg opacity-80" style={{ filter: 'drop-shadow(0 0 20px rgba(197,160,89,0.15))' }} />
          <div>
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
        </div>

        {/* Counter */}
        <div className="mb-8" data-testid="tirage-counter">
          <span className="text-xs tracking-widest" style={{ color: 'var(--pa-accent)', letterSpacing: '0.1em' }}>
            {tirageCount === 0
              ? '1 tirage gratuit aujourd\'hui'
              : 'Tirage gratuit utilis\u00e9 — 4,99\u20ac par tirage suppl\u00e9mentaire'
            }
          </span>
        </div>

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
                    Tarologie & M&eacute;diumni&eacute; — 35 EUR
                  </p>
                  <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
                    5 cartes, lecture m&eacute;diumnique et PDF personnalis&eacute;
                  </p>
                </button>

                {hasRegistered && (
                  <button onClick={() => navigate('/resultats')} className="block w-full text-left group" data-testid="astro-cross-sell">
                    <p className="text-sm mb-1 transition-colors duration-300 group-hover:text-[#C5A059]" style={{ color: 'var(--pa-heading)' }}>
                      Votre Thème Astral Complet
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
    </div>
  );
};

export default TarotOuiNon;
