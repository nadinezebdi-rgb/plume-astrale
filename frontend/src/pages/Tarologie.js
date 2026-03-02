import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Loader2, ArrowLeft, Sparkles, Download, Lock, Eye, Tag, Heart, Briefcase, Coins } from 'lucide-react';
import SEO from '@/components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const POSITION_LABELS = {
  centre: { label: 'La Situation Presente', icon: '1' },
  obstacle: { label: 'Ce Qui S\'Oppose', icon: '2' },
  conseil: { label: 'Le Conseil', icon: '3' },
  futur: { label: 'L\'Aboutissement', icon: '4' },
  synthese: { label: 'La Synthese', icon: '5' },
};

const CrossCard = ({ item, index, isLocked, onPurchase }) => {
  if (!item) return null;
  const posInfo = POSITION_LABELS[item.position_id] || {};

  return (
    <div className={`relative group ${isLocked ? 'overflow-hidden' : ''}`} data-testid={`carte-croix-${item.position_id}`}>
      {isLocked && (
        <div className="absolute inset-0 bg-[#0C0918]/85 backdrop-blur-sm z-10 flex items-center justify-center rounded-sm">
          <div className="text-center">
            <Lock className="w-6 h-6 text-[#C5A059]/50 mx-auto mb-1" />
            <p className="text-[#C5A059]/70 text-xs">Verrouille</p>
          </div>
        </div>
      )}
      <div className="bg-[#15112A]/80 border border-[#C5A059]/20 rounded-sm p-3 hover:border-[#C5A059]/50 transition-all duration-300">
        {/* Position number badge */}
        <div className="flex items-center gap-2 mb-2">
          <span className="w-6 h-6 rounded-full bg-[#C5A059]/20 border border-[#C5A059]/40 flex items-center justify-center text-[#C5A059] text-xs font-bold" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
            {posInfo.icon}
          </span>
          <span className="text-[#C5A059] text-xs uppercase tracking-widest font-medium">{posInfo.label}</span>
        </div>
        {/* Card image */}
        <div className="w-full aspect-[2/3] rounded-lg overflow-hidden mb-3 border border-[#C5A059]/30">
          {item.carte.image ? (
            <img src={`${API_URL}${item.carte.image}`} alt={item.carte.nom} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-b from-[#15112A] to-[#1C1735]">
              <span className="text-[#C5A059] text-2xl font-bold" style={{ fontFamily: 'Cormorant Garamond, serif' }}>{item.carte.numero}</span>
            </div>
          )}
        </div>
        {/* Card name */}
        <h4 className="text-[#F0E6D3] text-sm font-semibold text-center mb-1" style={{ fontFamily: 'Cormorant Garamond, serif' }}>{item.carte.nom}</h4>
        <p className="text-[#C5A059]/60 text-xs text-center">{item.carte.mots_cles || item.carte.energie}</p>
      </div>
    </div>
  );
};

const Tarologie = () => {
  const navigate = useNavigate();
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
  }, []);

  const handleTirage = async () => {
    if (!prenom.trim() || !dateNaissance) return;
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
            <p className="section-label">Lecture sacree</p>
            <h1 className="text-3xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
              Tarologie & Mediumnite
            </h1>
            <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
              Un tirage en croix de 5 Arcanes Majeurs avec interpretations profondes
            </p>
          </div>

          {/* What's included */}
          <div className="bg-[rgba(255,255,255,0.02)] border border-[#C5A059]/20 rounded-sm p-6 mb-8" data-testid="offer-details">
            <h3 className="text-[#C5A059] text-sm uppercase tracking-widest mb-4">Ce qui est inclus</h3>
            <div className="grid md:grid-cols-2 gap-3">
              {[
                'Tirage en Croix — 5 Arcanes Majeurs',
                'Interpretation detaillee par position',
                'Analyse des obstacles et conseils',
                'Vision du futur et synthese profonde',
                'Lecture mediumnique personnalisee',
                'PDF complet a telecharger',
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-2 text-[#B8B0C8]/70 text-sm">
                  <Star className="w-4 h-4 text-[#C5A059] flex-shrink-0" strokeWidth={1.5} />
                  {item}
                </div>
              ))}
            </div>
            <div className="mt-6 pt-4 border-t border-[#C5A059]/20 text-center">
              <span className="text-3xl font-bold text-gold-gradient" style={{ fontFamily: 'Cormorant Garamond, serif' }}>35 EUR</span>
              <p className="text-[#B8B0C8]/50 text-sm mt-1">Acces immediat + PDF telecharger</p>
            </div>
          </div>

          {/* Form */}
          <div className="bg-[rgba(255,255,255,0.02)] border border-[#C5A059]/20 rounded-sm p-6 mb-8" data-testid="tarologie-form">
            <h3 className="text-[#F0E6D3] mb-4" style={{ fontFamily: 'Cormorant Garamond, serif' }}>Vos Informations</h3>
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-2">Prenom</label>
                <input
                  type="text"
                  value={prenom}
                  onChange={(e) => setPrenom(e.target.value)}
                  placeholder="Votre prenom"
                  className="w-full px-4 py-3 bg-[#0C0918] border border-[#C5A059]/30 rounded-sm text-[#B8B0C8] placeholder:text-[#B8B0C8]/30 focus:outline-none focus:border-[#C5A059] transition-colors"
                  data-testid="prenom-input"
                />
              </div>
              <div>
                <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-2">Date de naissance</label>
                <input
                  type="date"
                  value={dateNaissance}
                  onChange={(e) => setDateNaissance(e.target.value)}
                  className="w-full px-4 py-3 bg-[#0C0918] border border-[#C5A059]/30 rounded-sm text-[#B8B0C8] focus:outline-none focus:border-[#C5A059] transition-colors"
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
                Decouvrir mon Tirage en Croix
              </button>
              <button
                onClick={handlePurchase}
                disabled={!prenom.trim() || !dateNaissance}
                className="btn-mystical-filled rounded-full flex items-center gap-2 justify-center px-6 py-3 disabled:opacity-50 flex-1"
                data-testid="purchase-btn"
              >
                <Lock className="w-5 h-5" /> Obtenir ma Lecture — 35 EUR
              </button>
            </div>

            {/* Promo Code */}
            <div className="mt-4 text-center">
              {!showPromo ? (
                <button onClick={() => setShowPromo(true)} className="text-[#C5A059]/60 hover:text-[#C5A059] text-sm underline transition-colors" data-testid="show-promo-btn">
                  <Tag className="w-3 h-3 inline mr-1" /> J'ai un code de reduction
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
                  <line x1="50%" y1="28%" x2="50%" y2="38%" stroke="#C5A059" strokeWidth="1" strokeDasharray="4,4" />
                  <line x1="50%" y1="62%" x2="50%" y2="72%" stroke="#C5A059" strokeWidth="1" strokeDasharray="4,4" />
                  <line x1="30%" y1="50%" x2="37%" y2="50%" stroke="#C5A059" strokeWidth="1" strokeDasharray="4,4" />
                  <line x1="63%" y1="50%" x2="70%" y2="50%" stroke="#C5A059" strokeWidth="1" strokeDasharray="4,4" />
                </svg>
              </div>

              {/* Interpretation for Centre (always visible) */}
              {getCard('centre') && (
                <div className="bg-[#15112A]/80 border border-[#C5A059]/30 rounded-sm p-6" data-testid="interpretation-centre">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="w-8 h-8 rounded-full bg-[#C5A059]/20 border border-[#C5A059] flex items-center justify-center text-[#C5A059] font-bold" style={{ fontFamily: 'Cormorant Garamond, serif' }}>1</span>
                    <div>
                      <h4 className="text-[#F0E6D3] font-medium" style={{ fontFamily: 'Cormorant Garamond, serif' }}>{getCard('centre').carte.nom}</h4>
                      <p className="text-[#C5A059]/60 text-xs">Position Centre — La Situation Presente</p>
                    </div>
                  </div>
                  <p className="text-[#C5A059]/70 text-xs italic mb-3">{getCard('centre').carte.description_arcane}</p>
                  <p className="text-[#B8B0C8]/80 text-sm leading-relaxed">{getCard('centre').interpretation}</p>
                </div>
              )}

              {/* Interpretations for other cards (locked unless paid) */}
              {!hasPaid && (
                <div className="bg-[#15112A]/80 border border-[#C5A059]/20 rounded-sm p-6 relative overflow-hidden" data-testid="interpretations-locked">
                  <div className="absolute inset-0 bg-[#0C0918]/80 backdrop-blur-sm z-10 flex items-center justify-center">
                    <div className="text-center px-6">
                      <Lock className="w-10 h-10 text-[#C5A059] mx-auto mb-3" />
                      <h3 className="text-[#F0E6D3] text-lg mb-2" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                        4 Interpretations + Lecture Mediumnique
                      </h3>
                      <p className="text-[#B8B0C8]/60 text-sm mb-4">
                        Debloquez les interpretations completes et la lecture mediumnique pour 35 EUR
                      </p>
                      <button
                        onClick={handlePurchase}
                        className="btn-mystical-filled rounded-full px-8 py-3 inline-flex items-center gap-2"
                        data-testid="unlock-interpretations-btn"
                      >
                        <Sparkles className="w-5 h-5" /> Debloquer tout le tirage
                      </button>
                    </div>
                  </div>
                  <div className="opacity-20 space-y-4">
                    {['obstacle', 'conseil', 'futur', 'synthese'].map(posId => {
                      const card = getCard(posId);
                      if (!card) return null;
                      return (
                        <div key={posId} className="border-b border-[#C5A059]/10 pb-3">
                          <h4 className="text-[#C5A059]">{card.position_nom}</h4>
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
                      <div key={posId} className="bg-[#15112A]/80 border border-[#C5A059]/20 rounded-sm p-6" data-testid={`interpretation-${posId}`}>
                        <div className="flex items-center gap-3 mb-4">
                          <span className="w-8 h-8 rounded-full bg-[#C5A059]/20 border border-[#C5A059] flex items-center justify-center text-[#C5A059] font-bold" style={{ fontFamily: 'Cormorant Garamond, serif' }}>{posInfo.icon}</span>
                          <div>
                            <h4 className="text-[#F0E6D3] font-medium" style={{ fontFamily: 'Cormorant Garamond, serif' }}>{card.carte.nom}</h4>
                            <p className="text-[#C5A059]/60 text-xs">Position {posInfo.icon} — {posInfo.label}</p>
                          </div>
                        </div>
                        <p className="text-[#C5A059]/70 text-xs italic mb-3">{card.carte.description_arcane}</p>
                        <p className="text-[#B8B0C8]/80 text-sm leading-relaxed">{card.interpretation}</p>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Lecture mediumnique - locked */}
              {!hasPaid && tirage.lecture_mediumnique && (
                <div className="bg-[#15112A]/80 border border-[#C5A059]/20 rounded-sm p-6 relative overflow-hidden" data-testid="lecture-locked">
                  <div className="absolute inset-0 bg-[#0C0918]/80 backdrop-blur-sm z-10 flex items-center justify-center">
                    <div className="text-center px-6">
                      <Lock className="w-8 h-8 text-[#C5A059]/50 mx-auto mb-2" />
                      <p className="text-[#C5A059]/70 text-sm">Lecture mediumnique incluse</p>
                    </div>
                  </div>
                  <div className="opacity-20 p-4">
                    <h3 className="text-xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>Lecture Mediumnique</h3>
                    <div className="space-y-3">
                      <div><h4 className="text-[#C5A059]">Empreinte du Passe</h4><p className="text-[#B8B0C8]/50">Lorem ipsum dolor sit amet...</p></div>
                      <div><h4 className="text-[#C5A059]">Energies du Present</h4><p className="text-[#B8B0C8]/50">Lorem ipsum dolor sit amet...</p></div>
                    </div>
                  </div>
                </div>
              )}

              {/* Full lecture if paid */}
              {hasPaid && tirage.lecture_mediumnique && (
                <div className="bg-[#15112A]/80 border border-[#C5A059]/20 rounded-sm p-6" data-testid="lecture-full">
                  <h3 className="text-xl mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                    Lecture Mediumnique
                  </h3>
                  {[
                    { key: 'passe', label: 'Empreinte du Passe' },
                    { key: 'present', label: 'Energies du Present' },
                    { key: 'futur', label: 'Visions du Futur' },
                    { key: 'conseil_ame', label: 'Message de Votre Ame' },
                  ].map(({ key, label }) => (
                    <div key={key} className="mb-4 pb-4 border-b border-[#C5A059]/10 last:border-0">
                      <h4 className="text-[#C5A059] font-medium mb-2">{label}</h4>
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
