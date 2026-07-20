import React, { useState, useEffect } from 'react';
import PageHero from '@/components/PageHero';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Heart, Sparkles, Star, Users, Briefcase, Home, Loader2, LogIn, ArrowRight, Tag, Share2, Download, Copy, Check } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import SafeEmptyState from '@/components/design/SafeEmptyState';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const RELATIONS = [
  { id: 'love', label: 'Amour', icon: Heart, accent: 'pink-400' },
  { id: 'friendship', label: 'Amitié', icon: Users, accent: 'blue-400' },
  { id: 'family', label: 'Famille', icon: Home, accent: 'emerald-400' },
  { id: 'work', label: 'Travail', icon: Briefcase, accent: 'amber-400' },
];

const initialPartner = () => ({
  name: '',
  day: '', month: '', year: '',
  hour: '12', minute: '0',
  city: '', country_code: 'FR',
});

const Compatibilite = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, token, loading: authLoading } = useAuth();
  const [relType, setRelType] = useState('love');
  const [partner, setPartner] = useState(initialPartner());
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPromo, setShowPromo] = useState(false);
  const [promoCode, setPromoCode] = useState('');
  const [promoLoading, setPromoLoading] = useState(false);
  const [promoError, setPromoError] = useState('');
  const [promoOk, setPromoOk] = useState(false);
  const [sharing, setSharing] = useState(false);
  const [shareLinkCopied, setShareLinkCopied] = useState(false);

  useEffect(() => {
    // Pas d'auto-redirect : l'utilisateur peut découvrir la page
  }, [isAuthenticated]);

  const handleField = (k, v) => setPartner(prev => ({ ...prev, [k]: v }));

  const isValid =
    partner.name.trim() &&
    partner.day && partner.month && partner.year;

  const handleSubmit = async () => {
    if (!isValid) {
      setError('Veuillez compléter le nom et la date de naissance du partenaire.');
      return;
    }
    if (!isAuthenticated) {
      navigate('/connexion?next=/compatibilite');
      return;
    }
    if (!user?.birth_date) {
      setError('Vos données natales sont incomplètes. Renseignez-les depuis Mon Compte.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    try {
      const body = {
        relationship_type: relType,
        person2: {
          name: partner.name.trim(),
          year: parseInt(partner.year, 10),
          month: parseInt(partner.month, 10),
          day: parseInt(partner.day, 10),
          hour: parseInt(partner.hour || 12, 10),
          minute: parseInt(partner.minute || 0, 10),
          city: partner.city.trim() || undefined,
          country_code: partner.country_code || undefined,
        },
      };
      const res = await axios.post(`${API_URL}/api/astrology/v3/synastry`, body, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.data?.success) {
        setResult(res.data);
      } else {
        setError(res.data?.detail || 'Analyse impossible. Réessayez plus tard.');
      }
    } catch (e) {
      setError(e.response?.data?.detail || 'Erreur lors de la connexion au service astrologique.');
    }
    setLoading(false);
  };

  const handleApplyPromo = async () => {
    if (!promoCode.trim()) return;
    setPromoLoading(true); setPromoError('');
    try {
      const res = await axios.post(`${API_URL}/api/discount/validate`, { code: promoCode });
      if (res.data.valid && res.data.discount_percent === 100) {
        setPromoOk(true);
      } else {
        setPromoError(res.data.message || 'Code invalide');
      }
    } catch {
      setPromoError('Erreur de connexion');
    }
    setPromoLoading(false);
  };

  const downloadCard = async () => {
    if (!result) return;
    setSharing(true);
    try {
      const res = await axios.post(`${API_URL}/api/astrology/v3/synastry/share-card`, {
        name_1: result.name_1,
        name_2: result.name_2,
        score: result.score,
        level: result.level,
        relationship_type: result.relationship_type,
      }, { responseType: 'blob' });
      const url = window.URL.createObjectURL(res.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `synastrie_${result.name_1}_${result.name_2}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      setError("Impossible de generer la carte pour l'instant.");
    }
    setSharing(false);
  };

  const shareNative = async () => {
    if (!result) return;
    const text = `${result.name_1} & ${result.name_2} : ${result.score}% de compatibilité (${result.level}) — découvrez la vôtre sur plume-astrale.fr`;
    if (navigator.share) {
      try {
        // Try sharing with image too
        const res = await axios.post(`${API_URL}/api/astrology/v3/synastry/share-card`, {
          name_1: result.name_1, name_2: result.name_2, score: result.score,
          level: result.level, relationship_type: result.relationship_type,
        }, { responseType: 'blob' });
        const file = new File([res.data], 'synastrie.png', { type: 'image/png' });
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          await navigator.share({ files: [file], text, title: 'Plume Astrale — Synastrie' });
          return;
        }
        await navigator.share({ text, title: 'Plume Astrale — Synastrie', url: 'https://plume-astrale.fr/compatibilite' });
      } catch {}
    } else {
      navigator.clipboard.writeText(text + ' https://plume-astrale.fr/compatibilite');
      setShareLinkCopied(true);
      setTimeout(() => setShareLinkCopied(false), 2500);
    }
  };

  const shareWhatsApp = () => {
    if (!result) return;
    const text = `${result.name_1} & ${result.name_2} : ${result.score}% de compatibilité (${result.level}) sur Plume Astrale → https://plume-astrale.fr/compatibilite`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
  };

  const currentRel = RELATIONS.find(r => r.id === relType);

  return (
    <div className="min-h-screen px-6 md:px-8 py-20 md:py-28" data-testid="compatibilite-page">
      <PageHero
        image="/images/astrale/image-astrale-8.jpg"
        title="Compatibilité"
        subtitle="Synastronie · Affinités cosmiques · Liens d'âmes"
      />
      <div className="max-w-3xl mx-auto">

        {/* Header */}
        <div className="text-center mb-12">
          <p className="text-[#D4AF37] uppercase tracking-[0.3em] text-sm mb-3 font-light">
            Synastrie Cosmique · Swiss Ephemeris
          </p>
          <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
            L'Alchimie de vos Liens
          </h1>
          <p className="text-base text-[#B8B0C8]/70 font-light max-w-xl mx-auto">
            Analysez la résonance astrologique de vos relations amoureuses, amicales, familiales ou professionnelles.
          </p>
        </div>

        {/* Relationship type selector */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8" data-testid="relation-tabs">
          {RELATIONS.map(r => {
            const Icon = r.icon;
            const active = r.id === relType;
            return (
              <button
                key={r.id}
                onClick={() => { setRelType(r.id); setResult(null); }}
                data-testid={`relation-tab-${r.id}`}
                className={`flex flex-col items-center gap-2 py-4 px-3 rounded-lg border transition-all ${
                  active
                    ? 'border-[#D4AF37] bg-[#D4AF37]/15 text-[#F5EEE0]'
                    : 'border-[#D4AF37]/20 text-[#B8B0C8]/60 hover:border-[#D4AF37]/40 hover:text-[#B8B0C8]'
                }`}
              >
                <Icon className="w-5 h-5" strokeWidth={1.4} />
                <span className="text-sm">{r.label}</span>
              </button>
            );
          })}
        </div>

        {/* Auth gate */}
        {!authLoading && !isAuthenticated && (
          <div className="card-mystical text-center py-10 mb-6" data-testid="auth-gate">
            <LogIn className="w-7 h-7 mb-3 mx-auto" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
            <p className="text-[#F5EEE0] mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: '1.25rem' }}>
              Connectez-vous pour analyser vos liens
            </p>
            <p className="text-sm text-[#B8B0C8]/60 mb-5">
              Vos données natales sont nécessaires pour calculer la synastrie réelle.
            </p>
            <div className="flex gap-3 justify-center">
              <button onClick={() => navigate('/connexion?next=/compatibilite')}
                className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full border border-[#D4AF37]/50 text-[#D4AF37]"
                data-testid="gate-login">
                Se connecter
              </button>
              <button onClick={() => navigate('/inscription')}
                className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full bg-[#D4AF37]/10 border border-[#D4AF37]/30 text-[#D4AF37]"
                data-testid="gate-register">
                Créer un compte
              </button>
            </div>
          </div>
        )}

        {/* Partner form */}
        {isAuthenticated && !result && (
          <div className="card-mystical" data-testid="partner-form">
            <h3 className="text-lg mb-5 flex items-center gap-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
              <currentRel.icon className="w-5 h-5 text-[#D4AF37]" strokeWidth={1.5} />
              Données de l'autre personne — {currentRel.label.toLowerCase()}
            </h3>

            {!user?.birth_date && (
              <div className="mb-4 p-3 rounded-md bg-amber-900/30 border border-amber-500/30 text-amber-200 text-sm">
                Renseignez d'abord vos propres données natales depuis <button onClick={() => navigate('/mon-compte')} className="underline">Mon Compte</button>.
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-[#D4AF37] text-xs uppercase tracking-widest mb-1">Prénom (ou alias)</label>
                <input type="text" value={partner.name}
                  onChange={(e) => handleField('name', e.target.value)}
                  className="w-full px-3 py-2.5 bg-[#15112A] border border-[#D4AF37]/30 rounded-lg text-[#F5EEE0] placeholder:text-[#B8B0C8]/30 focus:outline-none focus:border-[#D4AF37] text-sm"
                  placeholder="Prénom du partenaire"
                  data-testid="partner-name" />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-[#D4AF37] text-xs uppercase tracking-widest mb-1">Jour</label>
                  <input type="number" min="1" max="31" value={partner.day} onChange={(e) => handleField('day', e.target.value)}
                    className="w-full px-3 py-2.5 bg-[#15112A] border border-[#D4AF37]/30 rounded-lg text-[#F5EEE0] focus:outline-none focus:border-[#D4AF37] text-sm"
                    placeholder="JJ" data-testid="partner-day" />
                </div>
                <div>
                  <label className="block text-[#D4AF37] text-xs uppercase tracking-widest mb-1">Mois</label>
                  <input type="number" min="1" max="12" value={partner.month} onChange={(e) => handleField('month', e.target.value)}
                    className="w-full px-3 py-2.5 bg-[#15112A] border border-[#D4AF37]/30 rounded-lg text-[#F5EEE0] focus:outline-none focus:border-[#D4AF37] text-sm"
                    placeholder="MM" data-testid="partner-month" />
                </div>
                <div>
                  <label className="block text-[#D4AF37] text-xs uppercase tracking-widest mb-1">Année</label>
                  <input type="number" min="1920" max="2025" value={partner.year} onChange={(e) => handleField('year', e.target.value)}
                    className="w-full px-3 py-2.5 bg-[#15112A] border border-[#D4AF37]/30 rounded-lg text-[#F5EEE0] focus:outline-none focus:border-[#D4AF37] text-sm"
                    placeholder="AAAA" data-testid="partner-year" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#D4AF37] text-xs uppercase tracking-widest mb-1">Heure (si connue)</label>
                  <div className="grid grid-cols-2 gap-2">
                    <input type="number" min="0" max="23" value={partner.hour} onChange={(e) => handleField('hour', e.target.value)}
                      className="w-full px-3 py-2.5 bg-[#15112A] border border-[#D4AF37]/30 rounded-lg text-[#F5EEE0] focus:outline-none focus:border-[#D4AF37] text-sm"
                      placeholder="HH" data-testid="partner-hour" />
                    <input type="number" min="0" max="59" value={partner.minute} onChange={(e) => handleField('minute', e.target.value)}
                      className="w-full px-3 py-2.5 bg-[#15112A] border border-[#D4AF37]/30 rounded-lg text-[#F5EEE0] focus:outline-none focus:border-[#D4AF37] text-sm"
                      placeholder="MM" data-testid="partner-minute" />
                  </div>
                </div>
                <div>
                  <label className="block text-[#D4AF37] text-xs uppercase tracking-widest mb-1">Ville de naissance</label>
                  <input type="text" value={partner.city} onChange={(e) => handleField('city', e.target.value)}
                    className="w-full px-3 py-2.5 bg-[#15112A] border border-[#D4AF37]/30 rounded-lg text-[#F5EEE0] focus:outline-none focus:border-[#D4AF37] text-sm"
                    placeholder="Paris" data-testid="partner-city" />
                </div>
              </div>
            </div>

            {error && (
              <div className="mt-5 p-3 rounded-md bg-red-900/30 border border-red-500/30 text-red-300 text-sm" data-testid="form-error">
                {error}
              </div>
            )}

            <div className="mt-6 flex justify-center">
              <button
                onClick={handleSubmit}
                disabled={!isValid || loading || !user?.birth_date}
                className="btn-mystical-filled rounded-full px-8 py-3 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                data-testid="btn-analyze"
              >
                {loading ? (
                  <><Loader2 className="w-4 h-4 animate-spin" /> Analyse cosmique...</>
                ) : (
                  <><Sparkles className="w-4 h-4" /> Révéler la synastrie</>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Result */}
        {result && !(result.score !== undefined || result.name_1 || result.report || result.dominant_element) && (
          <SafeEmptyState
            productName="votre compatibilité"
            onRetry={() => { setResult(null); }}
          />
        )}

        {result && (result.score !== undefined || result.name_1 || result.report || result.dominant_element) && (
          <div className="space-y-6 animate-fade-in" data-testid="result-card">
            <div className="card-mystical text-center glow-gold">
              <div className="flex justify-center items-center gap-5 mb-6">
                <div className="text-center">
                  <Star className="w-7 h-7 text-[#D4AF37] mx-auto mb-1" strokeWidth={1} />
                  <p className="text-[#F5EEE0] text-sm">{result.name_1}</p>
                </div>
                <currentRel.icon className="w-9 h-9 text-pink-400 animate-pulse" />
                <div className="text-center">
                  <Star className="w-7 h-7 text-[#D4AF37] mx-auto mb-1" strokeWidth={1} />
                  <p className="text-[#F5EEE0] text-sm">{result.name_2}</p>
                </div>
              </div>

              <p className="text-[#D4AF37] uppercase tracking-[0.3em] text-xs mb-1" data-testid="result-rel-type">
                Compatibilité {result.relationship_label}
              </p>
              <div className="text-7xl font-bold text-gold-gradient mb-2" style={{ fontFamily: 'Cormorant Garamond, serif' }} data-testid="result-score">
                {result.score}%
              </div>
              <p className={`text-xl font-medium ${result.color}`} data-testid="result-level">
                {result.level}
              </p>

              <div className="w-full h-3 bg-[#15112A] rounded-full my-6 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-[#D4AF37] to-[#D4AF37] transition-all duration-1000"
                  style={{ width: `${result.score}%` }}
                />
              </div>

              <p className="text-[#B8B0C8]/80 font-light max-w-lg mx-auto" data-testid="result-description">
                {result.description}
              </p>
            </div>

            {/* Key aspects */}
            {result.aspects && result.aspects.length > 0 && (
              <div className="card-mystical" data-testid="result-aspects">
                <h3 className="text-lg mb-4 flex items-center gap-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                  <Sparkles className="w-5 h-5 text-[#D4AF37]" strokeWidth={1.5} />
                  Aspects astrologiques clés
                </h3>
                <ul className="space-y-3">
                  {result.aspects.map((a, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm" data-testid={`aspect-${i}`}>
                      <span className="text-[#D4AF37] mt-1">·</span>
                      <div>
                        <span className="text-[#F5EEE0]">{a.planet_1} {a.aspect} {a.planet_2}</span>
                        {a.orb !== null && <span className="text-[#B8B0C8]/50 ml-2">(orbe {a.orb}°)</span>}
                        {a.description && <p className="text-[#B8B0C8]/70 mt-1 text-xs">{a.description}</p>}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-3 justify-center" data-testid="result-share-actions">
              <button onClick={downloadCard} disabled={sharing}
                className="btn-mystical-filled rounded-full px-6 py-2.5 flex items-center gap-2 justify-center disabled:opacity-60"
                data-testid="btn-download-card">
                {sharing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                Telecharger la carte
              </button>
              <button onClick={shareNative}
                className="btn-mystical rounded-full px-6 py-2.5 flex items-center gap-2 justify-center"
                data-testid="btn-share-native">
                {shareLinkCopied ? <><Check className="w-4 h-4 text-emerald-400" /> Lien copie</> : <><Share2 className="w-4 h-4" /> Partager</>}
              </button>
              <button onClick={shareWhatsApp}
                className="btn-mystical rounded-full px-6 py-2.5 flex items-center gap-2 justify-center"
                data-testid="btn-share-whatsapp">
                <Sparkles className="w-4 h-4" /> WhatsApp
              </button>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button onClick={() => { setResult(null); setPartner(initialPartner()); }}
                className="btn-mystical rounded-full px-6 py-2.5"
                data-testid="btn-new-test">
                Tester un autre lien
              </button>
              <button onClick={() => navigate('/horoscope')}
                className="btn-mystical-filled rounded-full px-6 py-2.5 flex items-center gap-2 justify-center"
                data-testid="btn-horoscope">
                Mon horoscope <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default Compatibilite;
