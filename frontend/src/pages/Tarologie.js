import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Loader2, ArrowLeft, Sparkles, Download, Lock, Eye } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Tarologie = () => {
  const navigate = useNavigate();
  const [prenom, setPrenom] = useState('');
  const [dateNaissance, setDateNaissance] = useState('');
  const [loading, setLoading] = useState(false);
  const [tirage, setTirage] = useState(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [hasPaid, setHasPaid] = useState(false);

  // Check if already paid
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
      a.download = `tarologie_mediumnite_${prenom}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error('PDF error:', e);
    }
    setPdfLoading(false);
  };

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
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-3 font-light">
              Lecture Sacree
            </p>
            <h1 className="text-3xl md:text-5xl mb-3" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Tarologie & Mediumnite
            </h1>
            <p className="text-[#E0D9F6]/60 font-light max-w-lg mx-auto">
              Un tirage complet de 7 Arcanes Majeurs accompagne d'une lecture mediumnique profonde
            </p>
          </div>

          {/* What's included */}
          <div className="card-mystical mb-8" data-testid="offer-details">
            <h3 className="text-[#C5A059] text-sm uppercase tracking-widest mb-4">Ce qui est inclus</h3>
            <div className="grid md:grid-cols-2 gap-3">
              {[
                'Tirage de 7 Arcanes Majeurs',
                'Interpretation de chaque position',
                'Lecture mediumnique personnalisee',
                'Messages du passe, present, futur',
                'Conseil de votre ame',
                'PDF complet a telecharger',
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-2 text-[#E0D9F6]/70 text-sm">
                  <Star className="w-4 h-4 text-[#C5A059] flex-shrink-0" strokeWidth={1.5} />
                  {item}
                </div>
              ))}
            </div>
            <div className="mt-6 pt-4 border-t border-[#C5A059]/20 text-center">
              <span className="text-3xl font-bold text-gold-gradient" style={{ fontFamily: 'Cinzel, serif' }}>35 EUR</span>
              <p className="text-[#E0D9F6]/50 text-sm mt-1">Acces immediat + PDF telecharger</p>
            </div>
          </div>

          {/* Form */}
          <div className="card-mystical mb-8" data-testid="tarologie-form">
            <h3 className="text-[#F3E5AB] mb-4" style={{ fontFamily: 'Cinzel, serif' }}>Vos Informations</h3>
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-2">Prenom</label>
                <input
                  type="text"
                  value={prenom}
                  onChange={(e) => setPrenom(e.target.value)}
                  placeholder="Votre prenom"
                  className="w-full px-4 py-3 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-xl text-[#E0D9F6] placeholder:text-[#E0D9F6]/30 focus:outline-none focus:border-[#C5A059]"
                  data-testid="prenom-input"
                />
              </div>
              <div>
                <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-2">Date de naissance</label>
                <input
                  type="date"
                  value={dateNaissance}
                  onChange={(e) => setDateNaissance(e.target.value)}
                  className="w-full px-4 py-3 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-xl text-[#E0D9F6] focus:outline-none focus:border-[#C5A059]"
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
                Apercu du Tirage
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
          </div>

          {/* Tirage Preview / Full */}
          {tirage && (
            <div className="space-y-6 animate-fade-in">
              <h3 className="text-xl text-center" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                Votre Tirage des 7 Arcanes
              </h3>
              
              {tirage.tirage.map((item, i) => {
                const isLocked = !hasPaid && i >= 2;
                return (
                  <div key={i} className={`card-mystical relative ${isLocked ? 'overflow-hidden' : ''}`} data-testid={`carte-${i}`}>
                    {isLocked && (
                      <div className="absolute inset-0 bg-[#0F0518]/80 backdrop-blur-sm z-10 flex items-center justify-center">
                        <div className="text-center">
                          <Lock className="w-8 h-8 text-[#C5A059]/50 mx-auto mb-2" />
                          <p className="text-[#C5A059]/70 text-sm">Contenu verrouille</p>
                        </div>
                      </div>
                    )}
                    <div className="flex items-start gap-4">
                      <div className="w-14 h-20 rounded-lg overflow-hidden flex-shrink-0"
                           style={{ border: '1px solid #C5A059' }}>
                        {item.carte.image ? (
                          <img src={`${API_URL}${item.carte.image}`} alt={item.carte.nom} className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #1A0B2E, #2D1B4E)' }}>
                            <span className="text-[#C5A059] font-bold" style={{ fontFamily: 'Cinzel, serif' }}>{item.carte.numero}</span>
                          </div>
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[#C5A059] text-xs uppercase tracking-widest">Position {i+1}</span>
                          <span className="text-[#E0D9F6]/30">—</span>
                          <span className="text-[#E0D9F6]/50 text-xs">{item.position}</span>
                        </div>
                        <h4 className="text-[#F3E5AB] font-medium mb-1">{item.carte.nom}</h4>
                        <p className="text-[#E0D9F6]/40 text-xs mb-2">{item.carte.energie}</p>
                        <p className="text-[#E0D9F6]/70 text-sm font-light leading-relaxed">
                          {item.message}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Lecture mediumnique - locked */}
              {!hasPaid && (
                <div className="card-mystical relative overflow-hidden" data-testid="lecture-locked">
                  <div className="absolute inset-0 bg-[#0F0518]/80 backdrop-blur-sm z-10 flex items-center justify-center">
                    <div className="text-center px-6">
                      <Lock className="w-10 h-10 text-[#C5A059] mx-auto mb-3" />
                      <h3 className="text-[#F3E5AB] text-lg mb-2" style={{ fontFamily: 'Cinzel, serif' }}>
                        Lecture Mediumnique
                      </h3>
                      <p className="text-[#E0D9F6]/60 text-sm mb-4">
                        Debloquez la lecture complete + PDF pour 35 EUR
                      </p>
                      <button
                        onClick={handlePurchase}
                        className="btn-mystical-filled rounded-full px-8 py-3 inline-flex items-center gap-2"
                        data-testid="unlock-mediumnite-btn"
                      >
                        <Sparkles className="w-5 h-5" /> Debloquer la Lecture
                      </button>
                    </div>
                  </div>
                  <div className="opacity-20 p-6">
                    <h3 className="text-xl mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>Lecture Mediumnique</h3>
                    <div className="space-y-4">
                      <div><h4 className="text-[#C5A059]">Empreinte du Passe</h4><p className="text-[#E0D9F6]/50">Lorem ipsum dolor sit amet consectetur...</p></div>
                      <div><h4 className="text-[#C5A059]">Energies du Present</h4><p className="text-[#E0D9F6]/50">Lorem ipsum dolor sit amet consectetur...</p></div>
                      <div><h4 className="text-[#C5A059]">Visions du Futur</h4><p className="text-[#E0D9F6]/50">Lorem ipsum dolor sit amet consectetur...</p></div>
                    </div>
                  </div>
                </div>
              )}

              {/* Full lecture if paid */}
              {hasPaid && tirage.lecture_mediumnique && (
                <div className="card-mystical" data-testid="lecture-full">
                  <h3 className="text-xl mb-6" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
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
                      <p className="text-[#E0D9F6]/70 font-light leading-relaxed">
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
