import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, Loader2, ArrowLeft, Sparkles, Download, Star, Users, Tag, MessageCircle, Coins, LogIn, ArrowRight } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import SEO from '@/components/SEO';
import axios from 'axios';
import { asset } from '../lib/assets';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const PersonForm = ({ person, onChange, label, num }) => (
  <div className="space-y-4">
    <h3 className="text-lg flex items-center gap-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
      <Heart className="w-5 h-5 text-[#C5A059]" strokeWidth={1.5} /> {label}
    </h3>

    <div className="grid grid-cols-2 gap-3">
      <div>
        <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Pr&eacute;nom</label>
        <input type="text" value={person.first_name} onChange={(e) => onChange('first_name', e.target.value)}
          className="w-full px-3 py-2 bg-[#15112A] border border-[#C5A059]/30 rounded-lg text-[#B8B0C8] placeholder:text-[#B8B0C8]/30 focus:outline-none focus:border-[#C5A059] text-sm"
          placeholder="Pr&#233;nom" data-testid={`person${num}-first-name`} />
      </div>
      <div>
        <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Nom</label>
        <input type="text" value={person.last_name} onChange={(e) => onChange('last_name', e.target.value)}
          className="w-full px-3 py-2 bg-[#15112A] border border-[#C5A059]/30 rounded-lg text-[#B8B0C8] placeholder:text-[#B8B0C8]/30 focus:outline-none focus:border-[#C5A059] text-sm"
          placeholder="Nom" data-testid={`person${num}-last-name`} />
      </div>
    </div>

    <div>
      <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Genre</label>
      <div className="flex gap-3">
        {[{ val: 'male', label: 'Homme' }, { val: 'female', label: 'Femme' }].map(g => (
          <button key={g.val} type="button" onClick={() => onChange('gender', g.val)}
            className={`flex-1 py-2 rounded-lg border text-sm transition-all ${person.gender === g.val ? 'border-[#C5A059] bg-[#C5A059]/20 text-[#F0E6D3]' : 'border-[#C5A059]/20 text-[#B8B0C8]/60 hover:border-[#C5A059]/40'}`}
            data-testid={`person${num}-gender-${g.val}`}>
            {g.label}
          </button>
        ))}
      </div>
    </div>

    <div className="grid grid-cols-3 gap-3">
      <div>
        <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Jour</label>
        <input type="number" min="1" max="31" value={person.day} onChange={(e) => onChange('day', e.target.value)}
          className="w-full px-3 py-2 bg-[#15112A] border border-[#C5A059]/30 rounded-lg text-[#B8B0C8] focus:outline-none focus:border-[#C5A059] text-sm"
          placeholder="JJ" data-testid={`person${num}-day`} />
      </div>
      <div>
        <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Mois</label>
        <input type="number" min="1" max="12" value={person.month} onChange={(e) => onChange('month', e.target.value)}
          className="w-full px-3 py-2 bg-[#15112A] border border-[#C5A059]/30 rounded-lg text-[#B8B0C8] focus:outline-none focus:border-[#C5A059] text-sm"
          placeholder="MM" data-testid={`person${num}-month`} />
      </div>
      <div>
        <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Ann&eacute;e</label>
        <input type="number" min="1920" max="2025" value={person.year} onChange={(e) => onChange('year', e.target.value)}
          className="w-full px-3 py-2 bg-[#15112A] border border-[#C5A059]/30 rounded-lg text-[#B8B0C8] focus:outline-none focus:border-[#C5A059] text-sm"
          placeholder="AAAA" data-testid={`person${num}-year`} />
      </div>
    </div>

    <div className="grid grid-cols-2 gap-3">
      <div>
        <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Heure</label>
        <input type="number" min="0" max="23" value={person.hour} onChange={(e) => onChange('hour', e.target.value)}
          className="w-full px-3 py-2 bg-[#15112A] border border-[#C5A059]/30 rounded-lg text-[#B8B0C8] focus:outline-none focus:border-[#C5A059] text-sm"
          data-testid={`person${num}-hour`} />
      </div>
      <div>
        <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Minute</label>
        <input type="number" min="0" max="59" value={person.minute} onChange={(e) => onChange('minute', e.target.value)}
          className="w-full px-3 py-2 bg-[#15112A] border border-[#C5A059]/30 rounded-lg text-[#B8B0C8] focus:outline-none focus:border-[#C5A059] text-sm"
          data-testid={`person${num}-minute`} />
      </div>
    </div>

    <div>
      <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Lieu de naissance</label>
      <input type="text" value={person.place} onChange={(e) => onChange('place', e.target.value)}
        className="w-full px-3 py-2 bg-[#15112A] border border-[#C5A059]/30 rounded-lg text-[#B8B0C8] placeholder:text-[#B8B0C8]/30 focus:outline-none focus:border-[#C5A059] text-sm"
        placeholder="Ville, Pays" data-testid={`person${num}-place`} />
    </div>
  </div>
);

const Compatibilite2 = () => {
  const navigate = useNavigate();
  const { isAuthenticated, token, creditBalance, refreshBalance } = useAuth();
  const [step, setStep] = useState(0); // 0: auth gate, 1-4: existing steps
  const [loading, setLoading] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [error, setError] = useState('');
  const [question, setQuestion] = useState('');
  const [showPromo, setShowPromo] = useState(false);
  const [promoCode, setPromoCode] = useState('');
  const [promoError, setPromoError] = useState('');
  const [promoSuccess, setPromoSuccess] = useState('');
  const [promoLoading, setPromoLoading] = useState(false);
  const [creditUnlocked, setCreditUnlocked] = useState(false);

  const [person1, setPerson1] = useState({
    first_name: '', last_name: '', gender: 'male',
    day: '', month: '', year: '',
    hour: '12', minute: '0',
    place: 'Paris, France', lat: 48.8566, lon: 2.3522, timezone: 1.0,
  });

  const [person2, setPerson2] = useState({
    first_name: '', last_name: '', gender: 'female',
    day: '', month: '', year: '',
    hour: '12', minute: '0',
    place: 'Paris, France', lat: 48.8566, lon: 2.3522, timezone: 1.0,
  });

  const updatePerson = (setter) => (field, value) => {
    setter(prev => ({ ...prev, [field]: value }));
  };

  const isStep1Valid = person1.first_name && person1.day && person1.month && person1.year;
  const isStep2Valid = person2.first_name && person2.day && person2.month && person2.year;

  const goToStep = (s) => {
    setStep(s);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handlePurchase = async () => {
    try {
      const res = await fetch(`${API_URL}/api/checkout/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: 'compatibilite',
          origin_url: window.location.origin,
          user_data: { person1, person2, question }
        }),
      });
      const data = await res.json();
      if (data.url) {
        localStorage.setItem('plume_compat_data', JSON.stringify({ person1, person2, question }));
        window.location.href = data.url;
      }
    } catch (e) {
      console.error('Payment error:', e);
    }
  };

  const handleApplyPromo = async () => {
    if (!promoCode.trim()) return;
    setPromoLoading(true);
    setPromoError('');
    setPromoSuccess('');
    try {
      const res = await fetch(`${API_URL}/api/discount/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: promoCode }),
      });
      const data = await res.json();
      if (data.valid && data.discount_percent === 100) {
        setPromoSuccess('Code valide ! G\u00e9n\u00e9ration gratuite...');
        await handleGenerateFree();
      } else {
        setPromoError(data.message || 'Code invalide');
      }
    } catch (e) {
      setPromoError('Erreur de connexion');
    }
    setPromoLoading(false);
  };

  const handleGenerateFree = async () => {
    // Deduct credits if not already done
    if (!creditUnlocked) {
      try {
        await axios.post(`${API_URL}/api/credits/use`,
          { service_id: 'lecture_astrologique' },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        await refreshBalance();
        setCreditUnlocked(true);
      } catch (err) {
        const detail = err.response?.data?.detail || '';
        if (detail.includes('insuffisants')) {
          navigate('/acheter-credits');
          return;
        }
        setError(detail || 'Erreur');
        return;
      }
    }

    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/api/compatibility/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          person1: { ...person1, day: parseInt(person1.day), month: parseInt(person1.month), year: parseInt(person1.year), hour: parseInt(person1.hour), minute: parseInt(person1.minute) },
          person2: { ...person2, day: parseInt(person2.day), month: parseInt(person2.month), year: parseInt(person2.year), hour: parseInt(person2.hour), minute: parseInt(person2.minute) },
          question,
        }),
      });
      const data = await res.json();
      if (data.pdf_url) {
        setPdfUrl(data.pdf_url);
        goToStep(4);
      } else {
        setError(data.detail || 'Erreur lors de la g\u00e9n\u00e9ration');
      }
    } catch (e) {
      setError('Erreur de connexion');
    }
    setLoading(false);
  };

  const questionExamples = [
    "Avons-nous une r\u00e9elle compatibilit\u00e9 sur le long terme ?",
    "Comment g\u00e9rer nos diff\u00e9rences de caract\u00e8re ?",
    "Sommes-nous faits pour fonder une famille ensemble ?",
    "Comment raviver la flamme dans notre couple ?",
  ];

  return (
    <div className="min-h-screen">
      <SEO path="/compatibilite-amoureuse" />
      <div className="px-6 md:px-8 py-20 md:py-28">
        <div className="max-w-3xl mx-auto">

          <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-[#C5A059]/60 hover:text-[#C5A059] mb-8 transition-colors" data-testid="back-btn">
            <ArrowLeft className="w-4 h-4" /> Retour
          </button>

          {/* Header */}
          <div className="text-center mb-10">
            {/* Hero image */}
            <div className="flex justify-center mb-6">
              <div className="relative w-48 h-48 md:w-64 md:h-64">
                <img src={asset('images/compatibilite/mains-constellations.png')} alt="Connexion c&eacute;leste"
                  className="w-full h-full object-contain rounded-full opacity-90" data-testid="hero-image" />
                <div className="absolute inset-0 rounded-full" style={{ background: 'radial-gradient(circle, transparent 60%, #0C0918 100%)' }} />
              </div>
            </div>
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-3 font-light">
              Connexion C&eacute;leste
            </p>
            <h1 className="text-3xl md:text-5xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
              Compatibilit&eacute; Astrale
            </h1>
            <p className="text-[#B8B0C8]/60 font-light max-w-lg mx-auto">
              D&eacute;couvrez les secrets cosmiques de votre relation amoureuse. Un rapport complet r&eacute;v&egrave;le les forces, d&eacute;fis et cl&eacute;s de votre union.
            </p>
          </div>

          {/* Progress steps */}
          {step >= 1 && (
          <div className="flex items-center justify-center gap-2 mb-8">
            {[1, 2, 3, 4].map(s => (
              <div key={s} className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${step >= s ? 'bg-[#C5A059] text-[#0C0918]' : 'border border-[#C5A059]/30 text-[#C5A059]/40'}`}>
                  {s}
                </div>
                {s < 4 && <div className={`w-8 h-0.5 ${step > s ? 'bg-[#C5A059]' : 'bg-[#C5A059]/20'}`} />}
              </div>
            ))}
          </div>
          )}

          {/* Step 0: Auth Gate */}
          {step === 0 && (
            <div className="animate-fade-in">
              {!isAuthenticated ? (
                <div className="flex flex-col items-center justify-center py-12 text-center" data-testid="credit-gate-login">
                  <LogIn className="w-8 h-8 mb-4" style={{ color: '#C5A059' }} strokeWidth={1.5} />
                  <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>Connexion requise</h2>
                  <p className="text-sm mb-6" style={{ color: 'var(--pa-muted)' }}>
                    Connectez-vous pour accéder à la Compatibilité Astrale.
                    <br /><span style={{ color: '#C5A059' }}>10 crédits &middot; 20 crédits offerts à l'inscription</span>
                  </p>
                  <div className="flex gap-3">
                    <button onClick={() => navigate('/connexion')} className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full" style={{ border: '1px solid rgba(197,160,89,0.5)', color: '#C5A059', letterSpacing: '0.1em' }} data-testid="gate-login-btn">Se connecter</button>
                    <button onClick={() => navigate('/inscription')} className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full" style={{ border: '1px solid rgba(197,160,89,0.3)', color: '#C5A059', background: 'rgba(197,160,89,0.08)', letterSpacing: '0.1em' }} data-testid="gate-register-btn">Créer un compte</button>
                  </div>
                </div>
              ) : creditBalance < 10 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center" data-testid="credit-gate-insufficient">
                  <Coins className="w-8 h-8 mb-4" style={{ color: '#C5A059' }} strokeWidth={1.5} />
                  <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>Crédits insuffisants</h2>
                  <p className="text-sm mb-2" style={{ color: 'var(--pa-muted)' }}>Ce rapport coûte <span style={{ color: '#C5A059', fontWeight: 600 }}>10 crédits</span>.</p>
                  <p className="text-sm mb-6" style={{ color: 'var(--pa-muted)' }}>Solde : <span style={{ color: '#C5A059' }}>{creditBalance} crédits</span></p>
                  <button onClick={() => navigate('/acheter-credits')} className="flex items-center gap-2 text-xs uppercase tracking-widest px-6 py-2.5 rounded-full" style={{ border: '1px solid #C5A059', color: '#0C0918', background: '#C5A059', letterSpacing: '0.1em', fontWeight: 600 }} data-testid="gate-buy-credits-btn">
                    Acheter des crédits <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-8 text-center" data-testid="credit-gate-unlock">
                  <Coins className="w-7 h-7 mb-3" style={{ color: '#C5A059' }} strokeWidth={1.5} />
                  <p className="text-sm mb-1" style={{ color: 'var(--pa-body)' }}>Rapport de Compatibilité Astrale</p>
                  <p className="text-xs mb-5" style={{ color: 'var(--pa-muted)' }}>
                    Coût : <span style={{ color: '#C5A059' }}>10 crédits</span> &middot; Solde : <span style={{ color: '#C5A059' }}>{creditBalance} crédits</span>
                  </p>
                  <button onClick={() => setStep(1)} className="text-xs uppercase tracking-widest px-8 py-2.5 rounded-full" style={{ border: '1px solid rgba(197,160,89,0.5)', color: '#C5A059', letterSpacing: '0.1em' }} data-testid="gate-start-btn">
                    Commencer l'analyse
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Step 1: Person 1 */}
          {step === 1 && (
            <div className="card-mystical animate-fade-in" data-testid="step-1">
              <PersonForm person={person1} onChange={updatePerson(setPerson1)} label="Partenaire 1" num={1} />
              <button onClick={() => goToStep(2)} disabled={!isStep1Valid}
                className="btn-mystical-filled rounded-full flex items-center gap-2 mx-auto mt-6 px-8 py-3 disabled:opacity-50"
                data-testid="next-step-btn">
                Continuer vers Partenaire 2 <Users className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Step 2: Person 2 */}
          {step === 2 && (
            <div className="card-mystical animate-fade-in" data-testid="step-2">
              <PersonForm person={person2} onChange={updatePerson(setPerson2)} label="Partenaire 2" num={2} />
              <div className="flex flex-col sm:flex-row gap-3 mt-6">
                <button onClick={() => goToStep(1)} className="btn-mystical rounded-full px-6 py-3 flex items-center gap-2 justify-center" data-testid="prev-step-btn">
                  <ArrowLeft className="w-4 h-4" /> Retour
                </button>
                <button onClick={() => goToStep(3)} disabled={!isStep2Valid}
                  className="btn-mystical-filled rounded-full flex items-center gap-2 justify-center px-8 py-3 disabled:opacity-50 flex-1"
                  data-testid="to-question-btn">
                  Continuer <MessageCircle className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Question */}
          {step === 3 && (
            <div className="card-mystical animate-fade-in" data-testid="step-3-question">
              {/* Visual: couple passion */}
              <div className="flex justify-center mb-6">
                <img src={asset('images/compatibilite/couple-passion.png')} alt="Union des &acirc;mes"
                  className="w-40 h-40 object-contain rounded-xl opacity-80" data-testid="question-image" />
              </div>
              <h3 className="text-lg flex items-center gap-2 mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                <MessageCircle className="w-5 h-5 text-[#C5A059]" strokeWidth={1.5} /> Votre Question
              </h3>
              <p className="text-[#B8B0C8]/60 text-sm mb-4">
                Posez une question sp&eacute;cifique sur votre relation. Notre analyse astrologique y r&eacute;pondra dans votre rapport.
              </p>

              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                rows={3}
                className="w-full px-4 py-3 bg-[#15112A] border border-[#C5A059]/30 rounded-lg text-[#B8B0C8] placeholder:text-[#B8B0C8]/30 focus:outline-none focus:border-[#C5A059] text-sm resize-none"
                placeholder="Ex : Avons-nous une r&#233;elle compatibilit&#233; sur le long terme ?"
                data-testid="question-input"
              />

              {/* Example questions */}
              <div className="mt-3 flex flex-wrap gap-2">
                {questionExamples.map((q, i) => (
                  <button key={i} onClick={() => setQuestion(q)}
                    className="text-xs px-3 py-1.5 rounded-full border border-[#C5A059]/20 text-[#C5A059]/70 hover:border-[#C5A059]/50 hover:text-[#C5A059] transition-all"
                    data-testid={`question-example-${i}`}>
                    {q}
                  </button>
                ))}
              </div>

              {error && (
                <div className="mt-4 p-3 rounded-lg bg-red-900/30 border border-red-500/30 text-red-300 text-sm" data-testid="error-msg">
                  {error}
                </div>
              )}

              <div className="flex flex-col sm:flex-row gap-3 mt-6">
                <button onClick={() => goToStep(2)} className="btn-mystical rounded-full px-6 py-3 flex items-center gap-2 justify-center" data-testid="back-to-p2-btn">
                  <ArrowLeft className="w-4 h-4" /> Retour
                </button>
                <button onClick={handleGenerateFree} disabled={loading}
                  className="btn-mystical-filled rounded-full flex items-center gap-2 justify-center px-8 py-3 disabled:opacity-50 flex-1"
                  data-testid="generate-btn">
                  {loading ? <><Loader2 className="w-5 h-5 animate-spin" /> G&eacute;n&eacute;ration en cours...</> : <><Sparkles className="w-5 h-5" /> G&eacute;n&eacute;rer le Rapport &mdash; 10 cr&eacute;dits</>}
                </button>
              </div>

              {/* Promo Code */}
              <div className="mt-4 text-center">
                {!showPromo ? (
                  <button onClick={() => setShowPromo(true)} className="text-[#C5A059]/60 hover:text-[#C5A059] text-sm underline transition-colors" data-testid="show-promo-btn">
                    <Tag className="w-3 h-3 inline mr-1" /> J'ai un code de r&eacute;duction
                  </button>
                ) : (
                  <div className="max-w-sm mx-auto space-y-2">
                    <div className="flex gap-2">
                      <input type="text" value={promoCode} onChange={(e) => { setPromoCode(e.target.value.toUpperCase()); setPromoError(''); }}
                        placeholder="Code promo" className="flex-1 px-4 py-2 bg-[#0C0918] border border-[#C5A059]/30 rounded-full text-[#B8B0C8] text-center placeholder:text-[#B8B0C8]/30 focus:outline-none focus:border-[#C5A059] text-sm"
                        data-testid="promo-input" />
                      <button onClick={handleApplyPromo} disabled={promoLoading}
                        className="px-5 py-2 bg-[#C5A059]/20 border border-[#C5A059]/50 rounded-full text-[#C5A059] hover:bg-[#C5A059]/30 text-sm disabled:opacity-50"
                        data-testid="apply-promo-btn">
                        {promoLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Appliquer'}
                      </button>
                    </div>
                    {promoError && <p className="text-red-400 text-xs">{promoError}</p>}
                    {promoSuccess && <p className="text-emerald-400 text-xs">{promoSuccess}</p>}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 4: Result */}
          {step === 4 && pdfUrl && (
            <div className="space-y-6 animate-fade-in" data-testid="step-4-result">
              <div className="card-mystical text-center p-10 glow-gold">
                {/* Visual grid */}
                <div className="flex justify-center gap-4 mb-6">
                  <img src={asset('images/compatibilite/visage-dualite.png')} alt="Dualit&eacute; cosmique"
                    className="w-24 h-24 md:w-32 md:h-32 object-cover rounded-xl opacity-80" />
                  <img src={asset('images/compatibilite/coeur-mosaique.png')} alt="Union sacr&eacute;e"
                    className="w-24 h-24 md:w-32 md:h-32 object-cover rounded-xl opacity-80" />
                </div>
                <h2 className="text-2xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                  Votre Rapport est Pr&ecirc;t !
                </h2>
                <p className="text-[#B8B0C8]/60 mb-2">
                  Analyse de compatibilit&eacute; entre <span className="text-[#F0E6D3] font-medium">{person1.first_name}</span> et <span className="text-[#F0E6D3] font-medium">{person2.first_name}</span>
                </p>
                <p className="text-[#C5A059]/60 text-sm mb-6">Rapport d&eacute;taill&eacute; avec profils individuels, analyse des &eacute;l&eacute;ments, r&eacute;solution de conflits et cl&eacute;s de r&eacute;ussite</p>

                <a href={pdfUrl} download={`compatibilite_${person1.first_name}_${person2.first_name}.pdf`}
                  className="btn-mystical-filled rounded-full inline-flex items-center gap-2 px-8 py-3"
                  data-testid="download-pdf-btn">
                  <Download className="w-5 h-5" /> T&eacute;l&eacute;charger le PDF
                </a>
              </div>

              {/* Upsells */}
              <div className="grid md:grid-cols-2 gap-4">
                <button onClick={() => navigate('/formulaire')} className="card-mystical hover:border-[#C5A059]/50 transition-all group text-left" data-testid="upsell-manuscrit">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-[#F0E6D3] font-medium mb-1">Th&egrave;me Astral Pro</h3>
                      <p className="text-[#B8B0C8]/50 text-sm">68 pages d'analyse personnelle</p>
                      <span className="text-[#C5A059] font-bold text-sm mt-1 inline-block">10 cr&eacute;dits</span>
                    </div>
                    <Star className="w-5 h-5 text-[#C5A059] group-hover:scale-110 transition-transform" />
                  </div>
                </button>
                <button onClick={() => navigate('/tarologie')} className="card-mystical hover:border-[#C5A059]/50 transition-all group text-left" data-testid="upsell-tarologie">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-[#F0E6D3] font-medium mb-1">Tarologie & M&eacute;diumni&eacute;</h3>
                      <p className="text-[#B8B0C8]/50 text-sm">Tirage 7 cartes + lecture m&eacute;diumnique</p>
                      <span className="text-[#C5A059] font-bold text-sm mt-1 inline-block">10 cr&eacute;dits</span>
                    </div>
                    <Sparkles className="w-5 h-5 text-[#C5A059] group-hover:scale-110 transition-transform" />
                  </div>
                </button>
              </div>

              <button onClick={() => { goToStep(1); setPdfUrl(null); setQuestion(''); }}
                className="text-[#C5A059]/50 hover:text-[#C5A059] text-sm mx-auto block transition-colors" data-testid="new-test-btn">
                Tester une autre compatibilit&eacute;
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Compatibilite2;
