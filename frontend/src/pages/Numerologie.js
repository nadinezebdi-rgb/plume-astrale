import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, ArrowLeft, ArrowRight, Coins, LogIn } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import SEO from '@/components/SEO';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Numerologie = () => {
  const navigate = useNavigate();
  const { isAuthenticated, token, creditBalance, refreshBalance } = useAuth();
  const [formData, setFormData] = useState({
    prenom: '', dateNaissance: '', heureNaissance: '12:00', ville: 'Paris',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [unlocked, setUnlocked] = useState(false);

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

    // Deduct credits first if not already unlocked
    if (!unlocked) {
      try {
        await axios.post(`${API_URL}/api/credits/use`,
          { service_id: 'numerologie' },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        await refreshBalance();
        setUnlocked(true);
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
    try {
      const res = await fetch(`${API_URL}/api/numerology/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (data.success) setResult(data.data);
    } catch (e) {
      console.error('Numerology error:', e);
    }
    setLoading(false);
  };

  const numberCards = result ? [
    { key: 'nombre_expression', label: 'Nombre d\'Expression', color: '#A78BFA' },
    { key: 'nombre_ame', label: 'Nombre de l\'Ame', color: '#C97878' },
    { key: 'nombre_personnalite', label: 'Nombre de Personnalite', color: '#7CB88A' },
    { key: 'nombre_anniversaire', label: 'Nombre d\'Anniversaire', color: '#6BB5E8' },
    { key: 'annee_personnelle_2026', label: 'Annee Personnelle 2026', color: '#C5A059' },
  ].filter(c => result[c.key]) : [];

  return (
    <div className="min-h-screen relative">
      <SEO path="/numerologie" />
      <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
      <div className="max-w-xl mx-auto">

        <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12" data-testid="back-btn">
          <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
        </button>

        <div className="mb-12 flex items-start gap-6">
          <img src="https://customer-assets.emergentagent.com/job_6ebe2661-1b82-4742-afc5-632bf29dfcc5/artifacts/tba0xz5m_IMG5.png" alt="" className="w-20 md:w-28 flex-shrink-0 rounded-lg opacity-80" style={{ filter: 'drop-shadow(0 0 20px rgba(197,160,89,0.15))' }} />
          <div>
          <p className="section-label">Science des nombres</p>
          <h1
            className="text-3xl md:text-4xl mb-4"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
          >
            Votre Profil Numerologique
          </h1>
          <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
            Découvrez les nombres sacrés qui guident votre destinée
          </p>
          </div>
        </div>

        {/* Auth/Credit gate */}
        {!isAuthenticated ? (
          <div className="flex flex-col items-center justify-center py-12 text-center" data-testid="credit-gate-login">
            <LogIn className="w-8 h-8 mb-4" style={{ color: '#C5A059' }} strokeWidth={1.5} />
            <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>Connexion requise</h2>
            <p className="text-sm mb-6" style={{ color: 'var(--pa-muted)' }}>
              Connectez-vous pour accéder à la Numérologie.
              <br /><span style={{ color: '#C5A059' }}>10 crédits &middot; 20 crédits offerts à l'inscription</span>
            </p>
            <div className="flex gap-3">
              <button onClick={() => navigate('/connexion')} className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full" style={{ border: '1px solid rgba(197,160,89,0.5)', color: '#C5A059', letterSpacing: '0.1em' }} data-testid="gate-login-btn">Se connecter</button>
              <button onClick={() => navigate('/inscription')} className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full" style={{ border: '1px solid rgba(197,160,89,0.3)', color: '#C5A059', background: 'rgba(197,160,89,0.08)', letterSpacing: '0.1em' }} data-testid="gate-register-btn">Créer un compte</button>
            </div>
          </div>
        ) : !result ? (
          <div data-testid="numerology-form">
            {/* Credit cost info */}
            <div className="mb-6 flex items-center gap-2">
              <Coins className="w-4 h-4" style={{ color: '#C5A059' }} strokeWidth={1.5} />
              <span className="text-xs tracking-widest" style={{ color: 'var(--pa-accent)', letterSpacing: '0.1em' }}>
                {creditBalance < 10
                  ? `Crédits insuffisants (${creditBalance}/10)`
                  : `10 crédits \u00b7 Solde : ${creditBalance} crédits`
                }
              </span>
            </div>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Prenom complet *</label>
                <input type="text" required value={formData.prenom} onChange={e => setFormData({...formData, prenom: e.target.value})}
                  placeholder="Votre prenom complet" className="input-boxed" data-testid="input-prenom" />
              </div>
              <div>
                <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Date de naissance *</label>
                <input type="date" required value={formData.dateNaissance} onChange={e => setFormData({...formData, dateNaissance: e.target.value})}
                  className="input-boxed" data-testid="input-date" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Heure</label>
                  <input type="time" value={formData.heureNaissance} onChange={e => setFormData({...formData, heureNaissance: e.target.value})}
                    className="input-boxed" data-testid="input-heure" />
                </div>
                <div>
                  <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Ville</label>
                  <input type="text" value={formData.ville} onChange={e => setFormData({...formData, ville: e.target.value})}
                    placeholder="Paris" className="input-boxed" data-testid="input-ville" />
                </div>
              </div>

              <button type="submit" disabled={loading || (!unlocked && creditBalance < 10)} className="btn-editorial mt-4 disabled:opacity-30" data-testid="submit-btn">
                {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Calcul en cours...</> : unlocked ? <>Révéler mes nombres</> : <>Révéler mes nombres (10 crédits)</>}
              </button>
              {!unlocked && creditBalance < 10 && (
                <button type="button" onClick={() => navigate('/acheter-credits')} className="flex items-center gap-2 text-xs mt-3 transition-colors hover:text-[#C5A059]" style={{ color: 'var(--pa-muted)' }}>
                  Acheter des crédits <ArrowRight className="w-3 h-3" />
                </button>
              )}
            </form>
          </div>
        ) : (
          <div className="animate-fade-in" data-testid="numerology-results">

            {/* Life Path */}
            {result.chemin_de_vie && (
              <div className="text-center mb-16" data-testid="life-path-card">
                <p className="text-xs tracking-widest uppercase mb-6" style={{ color: 'var(--pa-accent)', letterSpacing: '0.15em' }}>
                  Chemin de Vie
                </p>
                <div
                  className="text-6xl md:text-7xl mb-4"
                  style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
                >
                  {result.chemin_de_vie.nombre}
                </div>
                <p className="text-lg mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-accent)' }}>
                  {result.chemin_de_vie.titre}
                </p>
                <p className="text-sm leading-relaxed max-w-md mx-auto" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
                  {result.chemin_de_vie.description}
                </p>
              </div>
            )}

            <div className="divider-subtle" />

            {/* Other numbers */}
            <div className="space-y-10">
              {numberCards.map((card) => (
                <div key={card.key} className="flex gap-6 items-start" data-testid={`numero-${result[card.key].nombre}`}>
                  <span
                    className="text-3xl flex-shrink-0 w-12 text-right"
                    style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: card.color }}
                  >
                    {result[card.key].nombre}
                  </span>
                  <div>
                    <p className="text-xs tracking-widest uppercase mb-2" style={{ color: card.color, letterSpacing: '0.1em' }}>
                      {card.label}
                    </p>
                    <p className="text-sm leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
                      {result[card.key].description}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* CTA */}
            <div className="mt-16 pt-10" style={{ borderTop: '1px solid var(--pa-divider)' }} data-testid="astro-cta">
              <p className="text-sm mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontSize: '1.1rem' }}>
                Completez votre profil avec l'Astrologie
              </p>
              <p className="text-xs mb-4" style={{ color: 'var(--pa-muted)' }}>
                Theme astral complet avec carte du ciel et previsions detaillees
              </p>
              <button onClick={() => navigate('/formulaire')} className="link-editorial text-xs group">
                Découvrir mon Thème Astral
                <ArrowRight className="w-3.5 h-3.5 transition-transform duration-300 group-hover:translate-x-1" strokeWidth={1.5} />
              </button>
            </div>

            <button onClick={() => setResult(null)}
              className="text-xs mt-10 block transition-colors duration-300 hover:text-[#C5A059]"
              style={{ color: 'var(--pa-muted)' }}
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
