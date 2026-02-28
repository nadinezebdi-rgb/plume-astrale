import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Hash, Loader2, ArrowLeft, Sparkles, Star, Heart, User, Calendar, MapPin, Clock } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const NumeroCard = ({ title, nombre, description, color = '#C5A059' }) => (
  <div className="card-mystical" data-testid={`numero-${nombre}`}>
    <div className="flex items-start gap-4">
      <div className="flex-shrink-0 w-14 h-14 rounded-xl flex items-center justify-center"
           style={{ background: `${color}15`, border: `1px solid ${color}30` }}>
        <span className="text-2xl font-bold" style={{ fontFamily: 'Cinzel, serif', color }}>{nombre}</span>
      </div>
      <div className="flex-1 min-w-0">
        <h3 className="text-sm uppercase tracking-widest mb-1" style={{ color }}>
          {title}
        </h3>
        <p className="text-[#E0D9F6]/70 text-sm font-light leading-relaxed">
          {description}
        </p>
      </div>
    </div>
  </div>
);

const Numerologie = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    prenom: '',
    dateNaissance: '',
    heureNaissance: '12:00',
    ville: 'Paris',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Try to pre-fill from localStorage
  React.useEffect(() => {
    const saved = localStorage.getItem('plume_astrale_data');
    if (saved) {
      try {
        const data = JSON.parse(saved);
        setFormData(prev => ({
          ...prev,
          prenom: data.prenom || prev.prenom,
          dateNaissance: data.dateNaissance || prev.dateNaissance,
          heureNaissance: data.heureNaissance || prev.heureNaissance,
          ville: data.ville || prev.ville,
        }));
      } catch(e) {}
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.prenom || !formData.dateNaissance) return;
    
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/numerology/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (data.success) {
        setResult(data.data);
      }
    } catch (e) {
      console.error('Numerology error:', e);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen relative">
      <StarField />
      <div className="relative z-10 py-12 px-4 md:px-6">
        <div className="max-w-2xl mx-auto">
          
          <button onClick={() => navigate('/')} className="flex items-center gap-2 text-[#C5A059]/60 hover:text-[#C5A059] mb-8 transition-colors" data-testid="back-btn">
            <ArrowLeft className="w-4 h-4" /> Accueil
          </button>

          <div className="text-center mb-10">
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-3 font-light">
              Science des Nombres
            </p>
            <h1 className="text-3xl md:text-5xl mb-3" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Votre Profil Numerologique
            </h1>
            <p className="text-[#E0D9F6]/60 font-light text-sm max-w-md mx-auto">
              Decouvrez les nombres sacres qui guident votre destinee
            </p>
          </div>

          {!result ? (
            <div className="card-mystical p-8" data-testid="numerology-form">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-[#C5A059] text-xs uppercase tracking-widest mb-1.5">
                    <User className="w-3.5 h-3.5 inline mr-1" /> Prenom complet *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.prenom}
                    onChange={e => setFormData({...formData, prenom: e.target.value})}
                    placeholder="Votre prenom complet (pour le calcul d'expression)"
                    className="w-full px-4 py-2.5 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] placeholder:text-[#E0D9F6]/30 focus:outline-none focus:border-[#C5A059] text-sm"
                    data-testid="input-prenom"
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
                    data-testid="input-date"
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
                      data-testid="input-heure"
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
                      data-testid="input-ville"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="btn-mystical-filled rounded-full flex items-center gap-2 mx-auto mt-6 px-8 py-3 disabled:opacity-50"
                  data-testid="submit-btn"
                >
                  {loading ? (
                    <><Loader2 className="w-5 h-5 animate-spin" /> Calcul en cours...</>
                  ) : (
                    <><Hash className="w-5 h-5" /> Reveler mes Nombres</>
                  )}
                </button>
              </form>
            </div>
          ) : (
            <div className="space-y-5 animate-fade-in" data-testid="numerology-results">
              
              {/* Life Path - Hero */}
              {result.chemin_de_vie && (
                <div className="card-mystical text-center p-8 glow-gold" data-testid="life-path-card">
                  <Hash className="w-10 h-10 text-[#C5A059] mx-auto mb-3" strokeWidth={1} />
                  <p className="text-[#C5A059] text-xs uppercase tracking-widest mb-2">Chemin de Vie</p>
                  <div className="text-6xl font-bold mb-2" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                    {result.chemin_de_vie.nombre}
                  </div>
                  <p className="text-xl mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#C5A059' }}>
                    {result.chemin_de_vie.titre}
                  </p>
                  <p className="text-[#E0D9F6]/70 font-light leading-relaxed text-sm max-w-md mx-auto">
                    {result.chemin_de_vie.description}
                  </p>
                </div>
              )}

              {/* Other numbers */}
              {result.nombre_expression && (
                <NumeroCard 
                  title="Nombre d'Expression" 
                  nombre={result.nombre_expression.nombre}
                  description={result.nombre_expression.description}
                  color="#A78BFA"
                />
              )}
              {result.nombre_ame && (
                <NumeroCard 
                  title="Nombre de l'Ame" 
                  nombre={result.nombre_ame.nombre}
                  description={result.nombre_ame.description}
                  color="#E8526E"
                />
              )}
              {result.nombre_personnalite && (
                <NumeroCard 
                  title="Nombre de Personnalite" 
                  nombre={result.nombre_personnalite.nombre}
                  description={result.nombre_personnalite.description}
                  color="#4ECB71"
                />
              )}
              {result.nombre_anniversaire && (
                <NumeroCard 
                  title="Nombre d'Anniversaire" 
                  nombre={result.nombre_anniversaire.nombre}
                  description={result.nombre_anniversaire.description}
                  color="#6BB5E8"
                />
              )}
              {result.annee_personnelle_2026 && (
                <NumeroCard 
                  title="Annee Personnelle 2026" 
                  nombre={result.annee_personnelle_2026.nombre}
                  description={result.annee_personnelle_2026.description}
                  color="#C5A059"
                />
              )}

              {/* CTA - Astrology */}
              <div className="card-mystical text-center p-6 border-[#C5A059]/30" data-testid="astro-cta">
                <Sparkles className="w-8 h-8 text-[#C5A059] mx-auto mb-3" strokeWidth={1} />
                <h3 className="text-lg mb-2" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                  Completez votre profil avec l'Astrologie
                </h3>
                <p className="text-[#E0D9F6]/50 text-xs mb-4">
                  Votre theme astral complet avec carte du ciel, aspects planetaires et previsions detaillees
                </p>
                <button
                  onClick={() => navigate('/formulaire')}
                  className="btn-mystical-filled rounded-full px-6 py-2.5 inline-flex items-center gap-2 text-sm"
                >
                  <Star className="w-4 h-4" /> Decouvrir mon Theme Astral
                </button>
              </div>

              <button
                onClick={() => { setResult(null); }}
                className="text-[#C5A059]/60 text-sm hover:text-[#C5A059] mx-auto block transition-colors"
                data-testid="new-reading-btn"
              >
                Nouveau calcul
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Numerologie;
