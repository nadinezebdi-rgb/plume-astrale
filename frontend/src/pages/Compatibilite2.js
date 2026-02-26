import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, Loader2, ArrowLeft, Sparkles, Download, Star, Users, Tag } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Compatibilite2 = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [error, setError] = useState('');
  const [showPromo, setShowPromo] = useState(false);
  const [promoCode, setPromoCode] = useState('');
  const [promoError, setPromoError] = useState('');
  const [promoSuccess, setPromoSuccess] = useState('');
  const [promoLoading, setPromoLoading] = useState(false);

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

  const handlePurchase = async () => {
    try {
      const res = await fetch(`${API_URL}/api/checkout/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: 'compatibilite',
          origin_url: window.location.origin,
          user_data: { person1, person2 }
        }),
      });
      const data = await res.json();
      if (data.url) {
        localStorage.setItem('plume_compat_data', JSON.stringify({ person1, person2 }));
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
        setPromoSuccess('Code valide ! Generation gratuite...');
        // Generate for free
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
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/api/compatibility/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          person1: { ...person1, day: parseInt(person1.day), month: parseInt(person1.month), year: parseInt(person1.year), hour: parseInt(person1.hour), minute: parseInt(person1.minute) },
          person2: { ...person2, day: parseInt(person2.day), month: parseInt(person2.month), year: parseInt(person2.year), hour: parseInt(person2.hour), minute: parseInt(person2.minute) },
        }),
      });
      const data = await res.json();
      if (data.pdf_url) {
        setPdfUrl(data.pdf_url);
        setStep(3);
      } else {
        setError(data.detail || 'Erreur lors de la generation');
      }
    } catch (e) {
      setError('Erreur de connexion');
    }
    setLoading(false);
  };

  const PersonForm = ({ person, onChange, label, genderDefault }) => (
    <div className="space-y-4">
      <h3 className="text-lg flex items-center gap-2" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
        <Heart className="w-5 h-5 text-[#C5A059]" strokeWidth={1.5} /> {label}
      </h3>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Prenom</label>
          <input type="text" value={person.first_name} onChange={(e) => onChange('first_name', e.target.value)}
            className="w-full px-3 py-2 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] placeholder:text-[#E0D9F6]/30 focus:outline-none focus:border-[#C5A059] text-sm"
            placeholder="Prenom" data-testid={`${label}-first-name`} />
        </div>
        <div>
          <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Nom</label>
          <input type="text" value={person.last_name} onChange={(e) => onChange('last_name', e.target.value)}
            className="w-full px-3 py-2 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] placeholder:text-[#E0D9F6]/30 focus:outline-none focus:border-[#C5A059] text-sm"
            placeholder="Nom" data-testid={`${label}-last-name`} />
        </div>
      </div>

      <div>
        <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Genre</label>
        <div className="flex gap-3">
          {[{ val: 'male', label: 'Homme' }, { val: 'female', label: 'Femme' }].map(g => (
            <button key={g.val} onClick={() => onChange('gender', g.val)}
              className={`flex-1 py-2 rounded-lg border text-sm transition-all ${person.gender === g.val ? 'border-[#C5A059] bg-[#C5A059]/20 text-[#F3E5AB]' : 'border-[#C5A059]/20 text-[#E0D9F6]/60 hover:border-[#C5A059]/40'}`}
              data-testid={`${label}-gender-${g.val}`}>
              {g.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Jour</label>
          <input type="number" min="1" max="31" value={person.day} onChange={(e) => onChange('day', e.target.value)}
            className="w-full px-3 py-2 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] focus:outline-none focus:border-[#C5A059] text-sm"
            placeholder="JJ" data-testid={`${label}-day`} />
        </div>
        <div>
          <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Mois</label>
          <input type="number" min="1" max="12" value={person.month} onChange={(e) => onChange('month', e.target.value)}
            className="w-full px-3 py-2 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] focus:outline-none focus:border-[#C5A059] text-sm"
            placeholder="MM" data-testid={`${label}-month`} />
        </div>
        <div>
          <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Annee</label>
          <input type="number" min="1920" max="2025" value={person.year} onChange={(e) => onChange('year', e.target.value)}
            className="w-full px-3 py-2 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] focus:outline-none focus:border-[#C5A059] text-sm"
            placeholder="AAAA" data-testid={`${label}-year`} />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Heure</label>
          <input type="number" min="0" max="23" value={person.hour} onChange={(e) => onChange('hour', e.target.value)}
            className="w-full px-3 py-2 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] focus:outline-none focus:border-[#C5A059] text-sm"
            data-testid={`${label}-hour`} />
        </div>
        <div>
          <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Minute</label>
          <input type="number" min="0" max="59" value={person.minute} onChange={(e) => onChange('minute', e.target.value)}
            className="w-full px-3 py-2 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] focus:outline-none focus:border-[#C5A059] text-sm"
            data-testid={`${label}-minute`} />
        </div>
      </div>

      <div>
        <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1">Lieu de naissance</label>
        <input type="text" value={person.place} onChange={(e) => onChange('place', e.target.value)}
          className="w-full px-3 py-2 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] placeholder:text-[#E0D9F6]/30 focus:outline-none focus:border-[#C5A059] text-sm"
          placeholder="Ville, Pays" data-testid={`${label}-place`} />
      </div>
    </div>
  );

  return (
    <div className="min-h-screen relative">
      <StarField />
      <div className="relative z-10 py-12 px-4 md:px-6">
        <div className="max-w-3xl mx-auto">

          <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-[#C5A059]/60 hover:text-[#C5A059] mb-8 transition-colors" data-testid="back-btn">
            <ArrowLeft className="w-4 h-4" /> Retour
          </button>

          {/* Header */}
          <div className="text-center mb-10">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 rounded-full flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #C5A059, #F3E5AB)' }}>
                <Heart className="w-8 h-8 text-[#0F0518]" />
              </div>
            </div>
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-3 font-light">
              Connexion Celeste
            </p>
            <h1 className="text-3xl md:text-5xl mb-3" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Compatibilite Astrale
            </h1>
            <p className="text-[#E0D9F6]/60 font-light max-w-lg mx-auto">
              Decouvrez les secrets cosmiques de votre relation amoureuse. Un rapport complet de 24 pages revele les forces, defis et destins de votre union.
            </p>
          </div>

          {/* Progress steps */}
          <div className="flex items-center justify-center gap-2 mb-8">
            {[1, 2, 3].map(s => (
              <div key={s} className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${step >= s ? 'bg-[#C5A059] text-[#0F0518]' : 'border border-[#C5A059]/30 text-[#C5A059]/40'}`}>
                  {s}
                </div>
                {s < 3 && <div className={`w-12 h-0.5 ${step > s ? 'bg-[#C5A059]' : 'bg-[#C5A059]/20'}`} />}
              </div>
            ))}
          </div>

          {/* Step 1: Person 1 */}
          {step === 1 && (
            <div className="card-mystical animate-fade-in" data-testid="step-1">
              <PersonForm person={person1} onChange={updatePerson(setPerson1)} label="Personne 1" />
              <button onClick={() => setStep(2)} disabled={!isStep1Valid}
                className="btn-mystical-filled rounded-full flex items-center gap-2 mx-auto mt-6 px-8 py-3 disabled:opacity-50"
                data-testid="next-step-btn">
                Continuer <Users className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Step 2: Person 2 */}
          {step === 2 && (
            <div className="card-mystical animate-fade-in" data-testid="step-2">
              <PersonForm person={person2} onChange={updatePerson(setPerson2)} label="Personne 2" />
              
              {error && (
                <div className="mt-4 p-3 rounded-lg bg-red-900/30 border border-red-500/30 text-red-300 text-sm" data-testid="error-msg">
                  {error}
                </div>
              )}

              <div className="flex flex-col sm:flex-row gap-3 mt-6">
                <button onClick={() => setStep(1)} className="btn-mystical rounded-full px-6 py-3 flex items-center gap-2 justify-center" data-testid="prev-step-btn">
                  <ArrowLeft className="w-4 h-4" /> Retour
                </button>
                <button onClick={handleGenerateFree} disabled={!isStep2Valid || loading}
                  className="btn-mystical-filled rounded-full flex items-center gap-2 justify-center px-8 py-3 disabled:opacity-50 flex-1"
                  data-testid="generate-btn">
                  {loading ? <><Loader2 className="w-5 h-5 animate-spin" /> Generation en cours...</> : <><Sparkles className="w-5 h-5" /> Generer le Rapport — 29,90 EUR</>}
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Result */}
          {step === 3 && pdfUrl && (
            <div className="space-y-6 animate-fade-in" data-testid="step-3">
              <div className="card-mystical text-center p-10 glow-gold">
                <Sparkles className="w-12 h-12 text-[#C5A059] mx-auto mb-4" strokeWidth={1} />
                <h2 className="text-2xl mb-3" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                  Votre Rapport est Pret !
                </h2>
                <p className="text-[#E0D9F6]/60 mb-2">
                  Analyse de compatibilite entre <span className="text-[#F3E5AB] font-medium">{person1.first_name}</span> et <span className="text-[#F3E5AB] font-medium">{person2.first_name}</span>
                </p>
                <p className="text-[#C5A059]/60 text-sm mb-6">24 pages d'analyse astrologique detaillee</p>

                <a href={pdfUrl} target="_blank" rel="noopener noreferrer"
                  className="btn-mystical-filled rounded-full inline-flex items-center gap-2 px-8 py-3"
                  data-testid="download-pdf-btn">
                  <Download className="w-5 h-5" /> Telecharger le PDF
                </a>
              </div>

              {/* Upsells */}
              <div className="grid md:grid-cols-2 gap-4">
                <button onClick={() => navigate('/formulaire')} className="card-mystical hover:border-[#C5A059]/50 transition-all group text-left" data-testid="upsell-manuscrit">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-[#F3E5AB] font-medium mb-1">Theme Astral Pro</h3>
                      <p className="text-[#E0D9F6]/50 text-sm">68 pages d'analyse personnelle</p>
                      <span className="text-[#C5A059] font-bold text-sm mt-1 inline-block">29,90 EUR</span>
                    </div>
                    <Star className="w-5 h-5 text-[#C5A059] group-hover:scale-110 transition-transform" />
                  </div>
                </button>
                <button onClick={() => navigate('/tarologie')} className="card-mystical hover:border-[#C5A059]/50 transition-all group text-left" data-testid="upsell-tarologie">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-[#F3E5AB] font-medium mb-1">Tarologie & Mediumnite</h3>
                      <p className="text-[#E0D9F6]/50 text-sm">Tirage 7 cartes + lecture mediumnique</p>
                      <span className="text-[#C5A059] font-bold text-sm mt-1 inline-block">35 EUR</span>
                    </div>
                    <Sparkles className="w-5 h-5 text-[#C5A059] group-hover:scale-110 transition-transform" />
                  </div>
                </button>
              </div>

              <button onClick={() => { setStep(1); setPdfUrl(null); }}
                className="text-[#C5A059]/50 hover:text-[#C5A059] text-sm mx-auto block transition-colors" data-testid="new-test-btn">
                Tester une autre compatibilite
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Compatibilite2;
