import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, ArrowLeft, ArrowRight, Coins, LogIn, Hash, Sparkles, BookOpen, Star, Heart } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import SEO from '@/components/SEO';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const Numerologie = () => {
  const navigate = useNavigate();
  const { isAuthenticated, token, creditBalance, refreshBalance } = useAuth();
  const [formData, setFormData] = useState({
    prenom: '', dateNaissance: '', heureNaissance: '12:00', ville: 'Paris',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [unlocked, setUnlocked] = useState(false);
  const [showForm, setShowForm] = useState(false);

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
    { key: 'nombre_ame', label: 'Nombre de l\'&Acirc;me', color: '#C97878' },
    { key: 'nombre_personnalite', label: 'Nombre de Personalit\u00e9', color: '#7CB88A' },
    { key: 'nombre_anniversaire', label: 'Nombre d\'Anniversaire', color: '#6BB5E8' },
    { key: 'annee_personnelle_2026', label: 'Ann\u00e9e Personnelle 2026', color: '#C5A059' },
  ].filter(c => result[c.key]) : [];

  return (
    <div className="min-h-screen relative">
      <SEO path="/numerologie" />
      <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
      <div className="max-w-xl mx-auto">

        <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12" data-testid="back-btn">
          <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
        </button>

        {/* Header */}
        <div className="mb-12 flex items-start gap-6">
          <img src="https://customer-assets.emergentagent.com/job_6ebe2661-1b82-4742-afc5-632bf29dfcc5/artifacts/tba0xz5m_IMG5.png" alt="" className="w-20 md:w-28 flex-shrink-0 rounded-lg opacity-80" style={{ filter: 'drop-shadow(0 0 20px rgba(197,160,89,0.15))' }} />
          <div>
            <p className="section-label">Science des nombres</p>
            <h1 className="text-3xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
              Num&eacute;rologie &mdash; Chemin d'&Acirc;me
            </h1>
            <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
              D&eacute;couvrez les nombres sacr&eacute;s qui r&eacute;v&egrave;lent votre mission de vie
            </p>
          </div>
        </div>

        {/* Educational content — always visible */}
        {!result && !showForm && (
          <div className="space-y-8 mb-10 animate-fade-in">

            {/* Qu'est-ce que la numérologie */}
            <div>
              <h2 className="text-xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                Qu'est-ce que la num&eacute;rologie ?
              </h2>
              <div className="space-y-3 text-sm leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
                <p>
                  La num&eacute;rologie est un syst&egrave;me ancestral qui &eacute;tudie la signification symbolique des nombres.
                  Chaque lettre de votre pr&eacute;nom et chaque chiffre de votre date de naissance portent
                  une vibration unique qui influence votre parcours de vie.
                </p>
                <p>
                  Contrairement &agrave; la voyance, la num&eacute;rologie repose sur des calculs pr&eacute;cis.
                  Elle ne pr&eacute;dit pas l'avenir &mdash; elle r&eacute;v&egrave;le des <span style={{ color: '#C5A059' }}>potentiels</span>,
                  des <span style={{ color: '#C5A059' }}>d&eacute;fis</span> et des <span style={{ color: '#C5A059' }}>cycles</span> qui vous sont propres.
                </p>
              </div>
            </div>

            {/* Les nombres clés */}
            <div>
              <h3 className="text-lg mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                Les nombres cl&eacute;s de votre profil
              </h3>
              <div className="space-y-4">
                {[
                  {
                    icon: <Star className="w-4 h-4" style={{ color: '#A78BFA' }} strokeWidth={1.5} />,
                    title: 'Chemin de Vie',
                    desc: 'Le nombre le plus important. Calcul\u00e9 \u00e0 partir de votre date de naissance, il r\u00e9v\u00e8le votre mission fondamentale, les le\u00e7ons \u00e0 apprendre et la direction g\u00e9n\u00e9rale de votre existence.',
                    color: '#A78BFA',
                  },
                  {
                    icon: <Heart className="w-4 h-4" style={{ color: '#C97878' }} strokeWidth={1.5} />,
                    title: 'Nombre de l\'\u00c2me',
                    desc: 'D\u00e9riv\u00e9 des voyelles de votre pr\u00e9nom, il exprime vos d\u00e9sirs profonds, ce qui vous motive int\u00e9rieurement et ce que votre \u00e2me cherche v\u00e9ritablement.',
                    color: '#C97878',
                  },
                  {
                    icon: <BookOpen className="w-4 h-4" style={{ color: '#7CB88A' }} strokeWidth={1.5} />,
                    title: 'Nombre d\'Expression',
                    desc: 'Calcul\u00e9 \u00e0 partir de toutes les lettres de votre pr\u00e9nom, il d\u00e9crit vos talents naturels, votre mani\u00e8re d\'\u00eatre et l\'image que vous projetez dans le monde.',
                    color: '#7CB88A',
                  },
                  {
                    icon: <Sparkles className="w-4 h-4" style={{ color: '#C5A059' }} strokeWidth={1.5} />,
                    title: 'Ann\u00e9e Personnelle',
                    desc: 'Ce cycle de 9 ans r\u00e9v\u00e8le l\'\u00e9nergie dominante de votre ann\u00e9e en cours. Il vous aide \u00e0 comprendre les opportunit\u00e9s et les d\u00e9fis sp\u00e9cifiques de cette p\u00e9riode.',
                    color: '#C5A059',
                  },
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

            {/* À qui s'adresse */}
            <div className="p-5 rounded-xl" style={{ background: 'rgba(197,160,89,0.05)', border: '1px solid rgba(197,160,89,0.12)' }}>
              <h3 className="text-base mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#C5A059', fontWeight: 400 }}>
                &Agrave; qui s'adresse cette analyse ?
              </h3>
              <ul className="space-y-2">
                {[
                  'Vous traversez une p\u00e9riode de questionnement sur votre direction de vie',
                  'Vous souhaitez mieux comprendre vos talents et vos d\u00e9fis',
                  'Vous voulez conna\u00eetre l\'\u00e9nergie de votre ann\u00e9e en cours',
                  'Vous cherchez un \u00e9clairage compl\u00e9mentaire \u00e0 l\'astrologie',
                ].map((t, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm" style={{ color: 'var(--pa-body)' }}>
                    <span style={{ color: '#C5A059', flexShrink: 0 }}>&ndash;</span>
                    <span>{t}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* CTA */}
            <div className="text-center pt-4">
              {!isAuthenticated ? (
                <div className="space-y-3" data-testid="credit-gate-login">
                  <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
                    <span style={{ color: '#C5A059' }}>10 cr&eacute;dits</span> &middot; 20 cr&eacute;dits offerts &agrave; l'inscription
                  </p>
                  <div className="flex gap-3 justify-center">
                    <button onClick={() => navigate('/connexion')} className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full" style={{ border: '1px solid rgba(197,160,89,0.5)', color: '#C5A059', letterSpacing: '0.1em' }} data-testid="gate-login-btn">Se connecter</button>
                    <button onClick={() => navigate('/inscription')} className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full" style={{ border: '1px solid rgba(197,160,89,0.3)', color: '#C5A059', background: 'rgba(197,160,89,0.08)', letterSpacing: '0.1em' }} data-testid="gate-register-btn">Cr&eacute;er un compte</button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setShowForm(true)}
                  className="text-xs uppercase tracking-widest px-8 py-3 rounded-full transition-all duration-500"
                  style={{ border: '1px solid rgba(197,160,89,0.5)', color: '#C5A059', letterSpacing: '0.1em' }}
                  data-testid="start-analysis-btn"
                >
                  <span className="flex items-center gap-2">
                    <Hash className="w-4 h-4" /> Commencer mon analyse &mdash; 10 cr&eacute;dits
                  </span>
                </button>
              )}
            </div>
          </div>
        )}

        {/* Form */}
        {!result && showForm && isAuthenticated && (
          <div data-testid="numerology-form" className="animate-fade-in">
            <div className="mb-6 flex items-center gap-2">
              <Coins className="w-4 h-4" style={{ color: '#C5A059' }} strokeWidth={1.5} />
              <span className="text-xs tracking-widest" style={{ color: 'var(--pa-accent)', letterSpacing: '0.1em' }}>
                {creditBalance < 10
                  ? `Cr\u00e9dits insuffisants (${creditBalance}/10)`
                  : `10 cr\u00e9dits \u00b7 Solde : ${creditBalance} cr\u00e9dits`
                }
              </span>
            </div>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Pr&eacute;nom complet *</label>
                <input type="text" required value={formData.prenom} onChange={e => setFormData({...formData, prenom: e.target.value})}
                  placeholder="Votre pr&eacute;nom complet" className="input-boxed" data-testid="input-prenom" />
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
                {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Calcul en cours...</> : unlocked ? <>R&eacute;v&eacute;ler mes nombres</> : <>R&eacute;v&eacute;ler mes nombres (10 cr&eacute;dits)</>}
              </button>
              {!unlocked && creditBalance < 10 && (
                <button type="button" onClick={() => navigate('/acheter-credits')} className="flex items-center gap-2 text-xs mt-3 transition-colors hover:text-[#C5A059]" style={{ color: 'var(--pa-muted)' }}>
                  Acheter des cr&eacute;dits <ArrowRight className="w-3 h-3" />
                </button>
              )}
            </form>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="animate-fade-in" data-testid="numerology-results">
            {result.chemin_de_vie && (
              <div className="text-center mb-16" data-testid="life-path-card">
                <p className="text-xs tracking-widest uppercase mb-6" style={{ color: 'var(--pa-accent)', letterSpacing: '0.15em' }}>
                  Chemin de Vie
                </p>
                <div className="text-6xl md:text-7xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
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

            <div className="space-y-10">
              {numberCards.map((card) => (
                <div key={card.key} className="flex gap-6 items-start" data-testid={`numero-${result[card.key].nombre}`}>
                  <span className="text-3xl flex-shrink-0 w-12 text-right" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: card.color }}>
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

            <div className="mt-16 pt-10" style={{ borderTop: '1px solid var(--pa-divider)' }} data-testid="astro-cta">
              <p className="text-sm mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontSize: '1.1rem' }}>
                Compl&eacute;tez votre profil avec l'Astrologie
              </p>
              <p className="text-xs mb-4" style={{ color: 'var(--pa-muted)' }}>
                Th&egrave;me astral complet avec carte du ciel et pr&eacute;visions d&eacute;taill&eacute;es
              </p>
              <button onClick={() => navigate('/formulaire')} className="link-editorial text-xs group">
                D&eacute;couvrir mon Th&egrave;me Astral
                <ArrowRight className="w-3.5 h-3.5 transition-transform duration-300 group-hover:translate-x-1" strokeWidth={1.5} />
              </button>
            </div>

            <button onClick={() => { setResult(null); setShowForm(true); }}
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
