import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Loader2, ArrowLeft, Sparkles, Download, Lock, Eye, Tag, Heart, Briefcase, Coins, LogIn, ArrowRight, BookOpen } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import SEO from '@/components/SEO';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const POSITION_LABELS = {
  centre: { label: 'La Situation Presente', icon: '1' },
  obstacle: { label: 'Ce Qui S\'Oppose', icon: '2' },
  conseil: { label: 'Le Conseil', icon: '3' },
  futur: { label: 'L\'Aboutissement', icon: '4' },
  synthese: { label: 'La Synthese', icon: '5' },
};

const PREDICTION_CATS = [
  { key: 'love', label: 'Amour', icon: Heart, color: '#C97878' },
  { key: 'career', label: 'Carriere', icon: Briefcase, color: '#7CB88A' },
  { key: 'finance', label: 'Finances', icon: Coins, color: '#B8961F' },
];

const CrossCard = ({ item, index, isLocked, onPurchase }) => {
  if (!item) return null;
  const posInfo = POSITION_LABELS[item.position_id] || {};

  return (
    <div className={`relative group ${isLocked ? 'overflow-hidden' : ''}`} data-testid={`carte-croix-${item.position_id}`}>
      {isLocked && (
        <div className="absolute inset-0 bg-[#0C0918]/85 backdrop-blur-sm z-10 flex items-center justify-center rounded-sm">
          <div className="text-center">
            <Lock className="w-6 h-6 text-[#B8961F]/50 mx-auto mb-1" />
            <p className="text-[#B8961F]/70 text-xs">Verrouille</p>
          </div>
        </div>
      )}
      <div className="bg-[#15112A]/80 border border-[#B8961F]/20 rounded-sm p-3 hover:border-[#B8961F]/50 transition-all duration-300">
        {/* Position number badge */}
        <div className="flex items-center gap-2 mb-2">
          <span className="w-6 h-6 rounded-full bg-[#B8961F]/20 border border-[#B8961F]/40 flex items-center justify-center text-[#B8961F] text-xs font-bold" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
            {posInfo.icon}
          </span>
          <span className="text-[#B8961F] text-xs uppercase tracking-widest font-medium">{posInfo.label}</span>
        </div>
        {/* Card image */}
        <div className="w-full aspect-[2/3] rounded-lg overflow-hidden mb-3 border border-[#B8961F]/30">
          {item.carte.image ? (
            <img src={`${API_URL}${item.carte.image}`} alt={item.carte.nom} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-b from-[#15112A] to-[#1C1735]">
              <span className="text-[#B8961F] text-2xl font-bold" style={{ fontFamily: 'Cormorant Garamond, serif' }}>{item.carte.numero}</span>
            </div>
          )}
        </div>
        {/* Card name */}
        <h4 className="text-[#F0E6D3] text-sm font-semibold text-center mb-1" style={{ fontFamily: 'Cormorant Garamond, serif' }}>{item.carte.nom}</h4>
        <p className="text-[#B8961F]/60 text-xs text-center">{item.carte.mots_cles || item.carte.energie}</p>
      </div>
    </div>
  );
};

const Tarologie = () => {
  const navigate = useNavigate();
  const { isAuthenticated, token, creditBalance, refreshBalance } = useAuth();
  const [prenom, setPrenom] = useState('');
  const [dateNaissance, setDateNaissance] = useState('');
  const [loading, setLoading] = useState(false);
  const [tirage, setTirage] = useState(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [hasPaid, setHasPaid] = useState(false);
  const [selectedCard, setSelectedCard] = useState(null);
  const [showPromo, setShowPromo] = useState(false);
  const [promoCode, setPromoCode] = useState('');
  const [promoError, setPromoError] = useState('');
  const [promoSuccess, setPromoSuccess] = useState('');
  const [promoLoading, setPromoLoading] = useState(false);
  const [predictions, setPredictions] = useState(null);
  const [predLoading, setPredLoading] = useState(false);
  const [showContent, setShowContent] = useState(false);

  React.useEffect(() => {
    const data = localStorage.getItem('plume_astrale_data');
    if (data) {
      try {
        const parsed = JSON.parse(data);
        if (parsed.prenom) setPrenom(parsed.prenom);
        if (parsed.dateNaissance) setDateNaissance(parsed.dateNaissance);
      } catch (e) { /* ignore */ }
    }
    const paid = localStorage.getItem('plume_tarologie_paid');
    if (paid === 'true') setHasPaid(true);
    // Fetch predictions
    fetchPredictions();
  }, []);

  const fetchPredictions = async () => {
    setPredLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/tarot/predictions`);
      const data = await res.json();
      if (data.success) setPredictions(data.predictions);
    } catch (e) { /* silent fail */ }
    setPredLoading(false);
  };

  const handleTirage = async () => {
    if (!prenom.trim() || !dateNaissance) return;

    // Deduct credits if not already paid
    if (!hasPaid) {
      try {
        await axios.post(`${API_URL}/api/credits/use`,
          { service_id: 'lecture_tarot' },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        await refreshBalance();
        setHasPaid(true);
      } catch (err) {
        const detail = err.response?.data?.detail || '';
        if (detail.includes('insuffisants')) {
          navigate('/acheter-credits');
          return;
        }
        alert(detail || 'Erreur');
        return;
      }
    }

    setLoading(true);
    setSelectedCard(null);
    try {
      const res = await fetch(`${API_URL}/api/tarologie/tirage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prenom: prenom.trim(), date_naissance: dateNaissance }),
      });
      const data = await res.json();
      setTirage(data);
    } catch (e) {
      console.error('Tirage error:', e);
    }
    setLoading(false);
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
        await fetch(`${API_URL}/api/access/free`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_id: 'tarologie_mediumnite', discount_code: promoCode, user_data: { prenom, dateNaissance } }),
        });
        localStorage.setItem('plume_tarologie_paid', 'true');
        setHasPaid(true);
        setPromoSuccess('Code valide ! Acces complet debloque.');
      } else {
        setPromoError(data.message || 'Code invalide');
      }
    } catch (e) {
      setPromoError('Erreur de connexion');
    }
    setPromoLoading(false);
  };

  const handlePurchase = async () => {
    try {
      const res = await fetch(`${API_URL}/api/checkout/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: 'tarologie_mediumnite',
          origin_url: window.location.origin,
          user_data: { prenom, dateNaissance }
        }),
      });
      const data = await res.json();
      if (data.url) window.location.href = data.url;
    } catch (e) {
      console.error('Payment error:', e);
    }
  };

  const handleDownloadPDF = async () => {
    setPdfLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/tarologie/pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prenom: prenom.trim(), date_naissance: dateNaissance }),
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `tarologie_croix_${prenom}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error('PDF error:', e);
    }
    setPdfLoading(false);
  };

  // Get cards by position
  const getCard = (posId) => tirage?.tirage?.find(c => c.position_id === posId);

  return (
    <div className="min-h-screen">
      <SEO path="/tarologie" />
      <div className="px-6 md:px-8 py-20 md:py-28">
        <div className="max-w-3xl mx-auto">
          
          <button onClick={() => navigate(-1)} className="link-editorial text-xs mb-12" data-testid="back-btn">
            <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Retour
          </button>

          {/* Header */}
          <div className="mb-12">
            <p className="section-label">Lecture sacr&eacute;e</p>
            <h1 className="text-3xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
              Tarologie & M&eacute;diumni&eacute;
            </h1>
            <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
              Un tirage en croix de 5 Arcanes Majeurs avec interpr&eacute;tations profondes
            </p>
          </div>

          {/* Educational intro — visible when no tirage yet */}
          {!tirage && !showContent && (
            <div className="space-y-8 mb-10 animate-fade-in">
              {/* Qu'est-ce que la tarologie */}
              <div>
                <h2 className="text-xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                  Qu'est-ce que la Tarologie ?
                </h2>
                <div className="space-y-3 text-sm leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
                  <p>
                    La tarologie est l'art d'interpr&eacute;ter les <span style={{ color: '#B8961F' }}>Arcanes Majeurs du Tarot</span> pour
                    &eacute;clairer une situation, comprendre des dynamiques invisibles et ouvrir des perspectives.
                  </p>
                  <p>
                    Ce n'est pas de la divination. C'est un <span style={{ color: '#B8961F' }}>miroir symbolique</span> : chaque carte
                    refl&egrave;te un aspect de votre v&eacute;cu, de vos blocages ou de vos ressources cach&eacute;es.
                  </p>
                </div>
              </div>

              {/* À quoi ça sert */}
              <div>
                <h3 className="text-lg mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                  &Agrave; quoi sert une lecture de Tarot ?
                </h3>
                <div className="space-y-3">
                  {[
                    { icon: <Eye className="w-4 h-4" style={{ color: '#A78BFA' }} strokeWidth={1.5} />, title: 'Clarifier une situation confuse', desc: 'Quand vous tournez en rond dans une d\u00e9cision, les cartes mettent en lumi\u00e8re ce que votre mental ne voit plus.', color: '#A78BFA' },
                    { icon: <Heart className="w-4 h-4" style={{ color: '#C97878' }} strokeWidth={1.5} />, title: 'Comprendre une relation', desc: 'Le tarot r\u00e9v\u00e8le les dynamiques \u00e9motionnelles en jeu \u2014 ce qui nourrit ou bloque une relation.', color: '#C97878' },
                    { icon: <BookOpen className="w-4 h-4" style={{ color: '#7CB88A' }} strokeWidth={1.5} />, title: 'Identifier vos blocages', desc: 'Certaines cartes pointent vers des peurs, des sch\u00e9mas r\u00e9p\u00e9titifs ou des croyances limitantes \u00e0 d\u00e9passer.', color: '#7CB88A' },
                    { icon: <Sparkles className="w-4 h-4" style={{ color: '#B8961F' }} strokeWidth={1.5} />, title: 'Ouvrir de nouvelles voies', desc: 'Le tirage ne donne pas d\u2019ordres. Il ouvre un espace de r\u00e9flexion pour avancer avec plus de conscience.', color: '#B8961F' },
                  ].map((item, i) => (
                    <div key={i} className="flex gap-4 items-start p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.02)', border: `1px solid ${item.color}15` }}>
                      <div className="mt-0.5">{item.icon}</div>
                      <div>
                        <h4 className="text-sm mb-1" style={{ color: item.color, fontWeight: 500 }}>{item.title}</h4>
                        <p className="text-xs leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Le tirage en croix */}
              <div className="p-5 rounded-xl" style={{ background: 'rgba(184,150,31,0.05)', border: '1px solid rgba(184,150,31,0.12)' }}>
                <h3 className="text-base mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#B8961F', fontWeight: 400 }}>
                  Le tirage en Croix &mdash; 5 positions
                </h3>
                <div className="space-y-2">
                  {[
                    { n: '1', label: 'La Situation Pr\u00e9sente', desc: 'O\u00f9 vous en \u00eates maintenant' },
                    { n: '2', label: 'Ce Qui S\'Oppose', desc: 'Les obstacles ou r\u00e9sistances' },
                    { n: '3', label: 'Le Conseil', desc: 'Ce que les cartes vous sugg\u00e8rent' },
                    { n: '4', label: 'L\'Aboutissement', desc: 'La direction vers laquelle cela tend' },
                    { n: '5', label: 'La Synth\u00e8se', desc: 'Le message global du tirage' },
                  ].map(p => (
                    <div key={p.n} className="flex items-center gap-3">
                      <span className="w-6 h-6 rounded-full flex items-center justify-center text-xs" style={{ background: 'rgba(184,150,31,0.15)', color: '#B8961F', border: '1px solid rgba(184,150,31,0.3)' }}>{p.n}</span>
                      <span className="text-sm" style={{ color: 'var(--pa-heading)' }}>{p.label}</span>
                      <span className="text-xs" style={{ color: 'var(--pa-muted)' }}>&mdash; {p.desc}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* CTA */}
              <div className="text-center pt-2">
                {!isAuthenticated ? (
                  <div className="space-y-3" data-testid="credit-gate-login">
                    <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
                      <span style={{ color: '#B8961F' }}>10 cr&eacute;dits</span> &middot; 20 cr&eacute;dits offerts &agrave; l'inscription
                    </p>
                    <div className="flex gap-3 justify-center">
                      <button onClick={() => navigate('/connexion')} className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full" style={{ border: '1px solid rgba(184,150,31,0.5)', color: '#B8961F', letterSpacing: '0.1em' }} data-testid="gate-login-btn">Se connecter</button>
                      <button onClick={() => navigate('/inscription')} className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full" style={{ border: '1px solid rgba(184,150,31,0.3)', color: '#B8961F', background: 'rgba(184,150,31,0.08)', letterSpacing: '0.1em' }} data-testid="gate-register-btn">Cr&eacute;er un compte</button>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => setShowContent(true)}
                    className="text-xs uppercase tracking-widest px-8 py-3 rounded-full transition-all duration-500"
                    style={{ border: '1px solid rgba(184,150,31,0.5)', color: '#B8961F', letterSpacing: '0.1em' }}
                    data-testid="start-tirage-btn"
                  >
                    Commencer mon tirage &mdash; 10 cr&eacute;dits
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Predictions from API */}
          {showContent && (
          <div className="mb-10" data-testid="tarot-predictions">
            <p className="section-label mb-4">Vos predictions du jour</p>
            {predLoading ? (
              <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--pa-muted)' }}>
                <Loader2 className="w-4 h-4 animate-spin" /> Consultation des cartes...
              </div>
            ) : predictions ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {PREDICTION_CATS.map(({ key, label, icon: Icon, color }) => {
                  const pred = predictions[key];
                  if (!pred) return null;
                  return (
                    <div key={key} className="card-editorial p-5" data-testid={`prediction-${key}`}>
                      <div className="flex items-center gap-2 mb-3">
                        <Icon className="w-4 h-4" style={{ color }} strokeWidth={1.5} />
                        <span className="text-xs tracking-widest uppercase" style={{ color, letterSpacing: '0.1em' }}>{label}</span>
                      </div>
                      <p className="text-sm leading-relaxed" style={{ color: 'var(--pa-body)' }}>
                        {pred.texte?.length > 200 ? pred.texte.substring(0, 200) + '...' : pred.texte}
                      </p>
                    </div>
                  );
                })}
              </div>
            ) : null}
          </div>
          )}

          {/* What's included */}
          {showContent && (
          <div className="bg-[rgba(255,255,255,0.02)] border border-[#B8961F]/20 rounded-sm p-6 mb-8" data-testid="offer-details">
            <h3 className="text-[#B8961F] text-sm uppercase tracking-widest mb-4">Ce qui est inclus</h3>
            <div className="grid md:grid-cols-2 gap-3">
              {[
                'Tirage en Croix — 5 Arcanes Majeurs',
                'Interpretation detaillee par position',
                'Analyse des obstacles et conseils',
                'Vision du futur et synthese profonde',
                'Lecture m\u00e9diumnique personnalis\u00e9e',
                'PDF complet a telecharger',
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-2 text-[#B8B0C8]/70 text-sm">
                  <Star className="w-4 h-4 text-[#B8961F] flex-shrink-0" strokeWidth={1.5} />
                  {item}
                </div>
              ))}
            </div>
            <div className="mt-6 pt-4 border-t border-[#B8961F]/20 text-center">
              <span className="text-3xl font-bold text-gold-gradient" style={{ fontFamily: 'Cormorant Garamond, serif' }}>10 cr&eacute;dits</span>
              <p className="text-[#B8B0C8]/50 text-sm mt-1">Acc&egrave;s imm&eacute;diat + PDF &agrave; t&eacute;l&eacute;charger</p>
            </div>
          </div>
          )}

          {/* Form */}
          {showContent && (
          <div className="bg-[rgba(255,255,255,0.02)] border border-[#B8961F]/20 rounded-sm p-6 mb-8" data-testid="tarologie-form">
            <h3 className="text-[#F0E6D3] mb-4" style={{ fontFamily: 'Cormorant Garamond, serif' }}>Vos Informations</h3>
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-[#B8961F] text-xs uppercase tracking-widest mb-2">Prenom</label>
                <input
                  type="text"
                  value={prenom}
                  onChange={(e) => setPrenom(e.target.value)}
                  placeholder="Votre prenom"
                  className="w-full px-4 py-3 bg-[#0C0918] border border-[#B8961F]/30 rounded-sm text-[#B8B0C8] placeholder:text-[#B8B0C8]/30 focus:outline-none focus:border-[#B8961F] transition-colors"
                  data-testid="prenom-input"
                />
              </div>
              <div>
                <label className="block text-[#B8961F] text-xs uppercase tracking-widest mb-2">Date de naissance</label>
                <input
                  type="date"
                  value={dateNaissance}
                  onChange={(e) => setDateNaissance(e.target.value)}
                  className="w-full px-4 py-3 bg-[#0C0918] border border-[#B8961F]/30 rounded-sm text-[#B8B0C8] focus:outline-none focus:border-[#B8961F] transition-colors"
                  data-testid="date-input"
                />
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={handleTirage}
                disabled={loading || !prenom.trim() || !dateNaissance}
                className="btn-mystical rounded-full flex items-center gap-2 justify-center px-6 py-3 disabled:opacity-50 flex-1"
                data-testid="preview-tirage-btn"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Eye className="w-5 h-5" />}
                Découvrir mon Tirage en Croix
              </button>
              <button
                onClick={handlePurchase}
                disabled={!prenom.trim() || !dateNaissance}
                className="btn-mystical-filled rounded-full flex items-center gap-2 justify-center px-6 py-3 disabled:opacity-50 flex-1"
                data-testid="purchase-btn"
              >
                <Lock className="w-5 h-5" /> Obtenir ma Lecture &mdash; 10 cr&eacute;dits
              </button>
            </div>

            {/* Promo Code */}
            <div className="mt-4 text-center">
              {!showPromo ? (
                <button onClick={() => setShowPromo(true)} className="text-[#B8961F]/60 hover:text-[#B8961F] text-sm underline transition-colors" data-testid="show-promo-btn">
                  <Tag className="w-3 h-3 inline mr-1" /> J'ai un code de reduction
                </button>
              ) : (
                <div className="max-w-sm mx-auto space-y-2">
                  <div className="flex gap-2">
                    <input type="text" value={promoCode} onChange={(e) => { setPromoCode(e.target.value.toUpperCase()); setPromoError(''); }}
                      placeholder="Code promo" className="flex-1 px-4 py-2 bg-[#0C0918] border border-[#B8961F]/30 rounded-full text-[#B8B0C8] text-center placeholder:text-[#B8B0C8]/30 focus:outline-none focus:border-[#B8961F] text-sm"
                      data-testid="promo-input" />
                    <button onClick={handleApplyPromo} disabled={promoLoading}
                      className="px-5 py-2 bg-[#B8961F]/20 border border-[#B8961F]/50 rounded-full text-[#B8961F] hover:bg-[#B8961F]/30 text-sm disabled:opacity-50"
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

          {/* Cross Spread */}
          {tirage && (
            <div className="space-y-8 animate-fade-in" data-testid="tirage-en-croix">
              <div className="text-center mb-6">
                <h3 className="text-xl md:text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                  Votre Tirage en Croix
                </h3>
                <p className="text-[#B8B0C8]/40 text-sm mt-2">Cliquez sur une carte pour lire son interpretation</p>
              </div>

              {/* Cross Layout */}
              <div className="relative mx-auto" style={{ maxWidth: '520px' }}>
                {/* Row 1: Futur (top center) */}
                <div className="flex justify-center mb-3">
                  <div className="w-36 md:w-40">
                    <CrossCard item={getCard('futur')} index={3} isLocked={!hasPaid && true} onPurchase={handlePurchase} />
                  </div>
                </div>

                {/* Row 2: Obstacle - Centre - Conseil */}
                <div className="flex justify-center items-center gap-3 mb-3">
                  <div className="w-36 md:w-40">
                    <CrossCard item={getCard('obstacle')} index={1} isLocked={!hasPaid && true} onPurchase={handlePurchase} />
                  </div>
                  <div className="w-36 md:w-40">
                    <CrossCard item={getCard('centre')} index={0} isLocked={false} onPurchase={handlePurchase} />
                  </div>
                  <div className="w-36 md:w-40">
                    <CrossCard item={getCard('conseil')} index={2} isLocked={!hasPaid && true} onPurchase={handlePurchase} />
                  </div>
                </div>

                {/* Row 3: Synthese (bottom center) */}
                <div className="flex justify-center">
                  <div className="w-36 md:w-40">
                    <CrossCard item={getCard('synthese')} index={4} isLocked={!hasPaid && true} onPurchase={handlePurchase} />
                  </div>
                </div>

                {/* Connecting lines (decorative) */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none z-0 opacity-20" style={{ top: 0, left: 0 }}>
                  <line x1="50%" y1="28%" x2="50%" y2="38%" stroke="#B8961F" strokeWidth="1" strokeDasharray="4,4" />
                  <line x1="50%" y1="62%" x2="50%" y2="72%" stroke="#B8961F" strokeWidth="1" strokeDasharray="4,4" />
                  <line x1="30%" y1="50%" x2="37%" y2="50%" stroke="#B8961F" strokeWidth="1" strokeDasharray="4,4" />
                  <line x1="63%" y1="50%" x2="70%" y2="50%" stroke="#B8961F" strokeWidth="1" strokeDasharray="4,4" />
                </svg>
              </div>

              {/* Interpretation for Centre (always visible) */}
              {getCard('centre') && (
                <div className="bg-[#15112A]/80 border border-[#B8961F]/30 rounded-sm p-6" data-testid="interpretation-centre">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="w-8 h-8 rounded-full bg-[#B8961F]/20 border border-[#B8961F] flex items-center justify-center text-[#B8961F] font-bold" style={{ fontFamily: 'Cormorant Garamond, serif' }}>1</span>
                    <div>
                      <h4 className="text-[#F0E6D3] font-medium" style={{ fontFamily: 'Cormorant Garamond, serif' }}>{getCard('centre').carte.nom}</h4>
                      <p className="text-[#B8961F]/60 text-xs">Position Centre — La Situation Presente</p>
                    </div>
                  </div>
                  <p className="text-[#B8961F]/70 text-xs italic mb-3">{getCard('centre').carte.description_arcane}</p>
                  <p className="text-[#B8B0C8]/80 text-sm leading-relaxed">{getCard('centre').interpretation}</p>
                </div>
              )}

              {/* Interpretations for other cards (locked unless paid) */}
              {!hasPaid && (
                <div className="bg-[#15112A]/80 border border-[#B8961F]/20 rounded-sm p-6 relative overflow-hidden" data-testid="interpretations-locked">
                  <div className="absolute inset-0 bg-[#0C0918]/80 backdrop-blur-sm z-10 flex items-center justify-center">
                    <div className="text-center px-6">
                      <Lock className="w-10 h-10 text-[#B8961F] mx-auto mb-3" />
                      <h3 className="text-[#F0E6D3] text-lg mb-2" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                        4 Interpretations + Lecture Mediumnique
                      </h3>
                      <p className="text-[#B8B0C8]/60 text-sm mb-4">
                        D&eacute;bloquez les interpr&eacute;tations compl&egrave;tes et la lecture m&eacute;diumnique pour 10 cr&eacute;dits
                      </p>
                      <button
                        onClick={handlePurchase}
                        className="btn-mystical-filled rounded-full px-8 py-3 inline-flex items-center gap-2"
                        data-testid="unlock-interpretations-btn"
                      >
                        <Sparkles className="w-5 h-5" /> D&eacute;bloquer tout le tirage
                      </button>
                    </div>
                  </div>
                  <div className="opacity-20 space-y-4">
                    {['obstacle', 'conseil', 'futur', 'synthese'].map(posId => {
                      const card = getCard(posId);
                      if (!card) return null;
                      return (
                        <div key={posId} className="border-b border-[#B8961F]/10 pb-3">
                          <h4 className="text-[#B8961F]">{card.position_nom}</h4>
                          <p className="text-[#B8B0C8]/50 text-sm">Lorem ipsum dolor sit amet consectetur adipiscing elit...</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Full interpretations if paid */}
              {hasPaid && (
                <div className="space-y-4" data-testid="interpretations-full">
                  {['obstacle', 'conseil', 'futur', 'synthese'].map(posId => {
                    const card = getCard(posId);
                    if (!card) return null;
                    const posInfo = POSITION_LABELS[posId];
                    return (
                      <div key={posId} className="bg-[#15112A]/80 border border-[#B8961F]/20 rounded-sm p-6" data-testid={`interpretation-${posId}`}>
                        <div className="flex items-center gap-3 mb-4">
                          <span className="w-8 h-8 rounded-full bg-[#B8961F]/20 border border-[#B8961F] flex items-center justify-center text-[#B8961F] font-bold" style={{ fontFamily: 'Cormorant Garamond, serif' }}>{posInfo.icon}</span>
                          <div>
                            <h4 className="text-[#F0E6D3] font-medium" style={{ fontFamily: 'Cormorant Garamond, serif' }}>{card.carte.nom}</h4>
                            <p className="text-[#B8961F]/60 text-xs">Position {posInfo.icon} — {posInfo.label}</p>
                          </div>
                        </div>
                        <p className="text-[#B8961F]/70 text-xs italic mb-3">{card.carte.description_arcane}</p>
                        <p className="text-[#B8B0C8]/80 text-sm leading-relaxed">{card.interpretation}</p>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Lecture mediumnique - locked */}
              {!hasPaid && tirage.lecture_mediumnique && (
                <div className="bg-[#15112A]/80 border border-[#B8961F]/20 rounded-sm p-6 relative overflow-hidden" data-testid="lecture-locked">
                  <div className="absolute inset-0 bg-[#0C0918]/80 backdrop-blur-sm z-10 flex items-center justify-center">
                    <div className="text-center px-6">
                      <Lock className="w-8 h-8 text-[#B8961F]/50 mx-auto mb-2" />
                      <p className="text-[#B8961F]/70 text-sm">Lecture m&eacute;diumnique incluse</p>
                    </div>
                  </div>
                  <div className="opacity-20 p-4">
                    <h3 className="text-xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>Lecture Mediumnique</h3>
                    <div className="space-y-3">
                      <div><h4 className="text-[#B8961F]">Empreinte du Passe</h4><p className="text-[#B8B0C8]/50">Lorem ipsum dolor sit amet...</p></div>
                      <div><h4 className="text-[#B8961F]">Energies du Present</h4><p className="text-[#B8B0C8]/50">Lorem ipsum dolor sit amet...</p></div>
                    </div>
                  </div>
                </div>
              )}

              {/* Full lecture if paid */}
              {hasPaid && tirage.lecture_mediumnique && (
                <div className="bg-[#15112A]/80 border border-[#B8961F]/20 rounded-sm p-6" data-testid="lecture-full">
                  <h3 className="text-xl mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                    Lecture Mediumnique
                  </h3>
                  {[
                    { key: 'passe', label: 'Empreinte du Passe' },
                    { key: 'present', label: 'Energies du Present' },
                    { key: 'futur', label: 'Visions du Futur' },
                    { key: 'conseil_ame', label: 'Message de Votre Ame' },
                  ].map(({ key, label }) => (
                    <div key={key} className="mb-4 pb-4 border-b border-[#B8961F]/10 last:border-0">
                      <h4 className="text-[#B8961F] font-medium mb-2">{label}</h4>
                      <p className="text-[#B8B0C8]/70 font-light leading-relaxed">
                        {tirage.lecture_mediumnique[key]}
                      </p>
                    </div>
                  ))}

                  <button
                    onClick={handleDownloadPDF}
                    disabled={pdfLoading}
                    className="btn-mystical-filled rounded-full flex items-center gap-2 mx-auto mt-6 px-8 py-3"
                    data-testid="download-pdf-btn"
                  >
                    {pdfLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Download className="w-5 h-5" />}
                    Telecharger le PDF Complet
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

export default Tarologie;
