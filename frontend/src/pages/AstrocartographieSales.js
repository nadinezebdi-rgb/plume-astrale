import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, ShieldCheck, Globe, Loader2, MapPin, X, Search } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import { useAuth } from '@/context/AuthContext';
import TestimonialsWidget, { TESTIMONIALS_ASTROCARTO } from '@/components/TestimonialsWidget';

const API = process.env.REACT_APP_BACKEND_URL;

// Villes suggérées populaires (l'utilisateur peut aussi taper la sienne)
const CITY_SUGGESTIONS = [
  { city: 'Bali', country: 'Indonésie', country_code: 'ID', latitude: -8.4095, longitude: 115.1889 },
  { city: 'Lisbonne', country: 'Portugal', country_code: 'PT', latitude: 38.7223, longitude: -9.1393 },
  { city: 'Marrakech', country: 'Maroc', country_code: 'MA', latitude: 31.6295, longitude: -7.9811 },
  { city: 'Barcelone', country: 'Espagne', country_code: 'ES', latitude: 41.3874, longitude: 2.1686 },
  { city: 'Bangkok', country: 'Thaïlande', country_code: 'TH', latitude: 13.7563, longitude: 100.5018 },
  { city: 'New York', country: 'États-Unis', country_code: 'US', latitude: 40.7128, longitude: -74.0060 },
  { city: 'Kyoto', country: 'Japon', country_code: 'JP', latitude: 35.0116, longitude: 135.7681 },
  { city: 'Buenos Aires', country: 'Argentine', country_code: 'AR', latitude: -34.6037, longitude: -58.3816 },
  { city: 'Le Cap', country: 'Afrique du Sud', country_code: 'ZA', latitude: -33.9249, longitude: 18.4241 },
  { city: 'Montréal', country: 'Canada', country_code: 'CA', latitude: 45.5017, longitude: -73.5673 },
  { city: 'Sydney', country: 'Australie', country_code: 'AU', latitude: -33.8688, longitude: 151.2093 },
  { city: 'Reykjavik', country: 'Islande', country_code: 'IS', latitude: 64.1466, longitude: -21.9426 },
];

const AstrocartographieSales = () => {
  const { user } = useAuth();
  const nav = useNavigate();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    email: user?.email || '',
    first_name: user?.prenom || user?.first_name || '',
    birth_date: '',
    birth_time: '',
    birth_city: 'Paris',
    birth_country: 'FR',
    latitude: 48.8566,
    longitude: 2.3522,
  });
  const [chosen, setChosen] = useState([]);   // [{city, country, country_code, latitude, longitude}, ...]
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Pré-remplir le code promo depuis l'URL ?discount=PLUME15
  const [promoCode, setPromoCode] = useState(() => {
    try {
      const url = new URL(window.location.href);
      return (url.searchParams.get('discount') || '').toUpperCase();
    } catch { return ''; }
  });
  // Skip step 0 si un code promo est en URL (l'utilisateur vient d'un mail cross-sell)
  useEffect(() => {
    if (promoCode) setStep(1);
  }, [promoCode]);

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const searchTimer = useRef(null);

  useEffect(() => {
    if (searchTimer.current) clearTimeout(searchTimer.current);
    if (!searchQuery || searchQuery.trim().length < 2) {
      setSearchResults([]);
      return;
    }
    setSearching(true);
    searchTimer.current = setTimeout(async () => {
      try {
        const r = await axios.get(`${API}/api/astrocartographie/cities/search`, {
          params: { q: searchQuery.trim(), limit: 8 },
        });
        setSearchResults(r.data?.items || []);
      } catch { setSearchResults([]); }
      finally { setSearching(false); }
    }, 350);
    return () => searchTimer.current && clearTimeout(searchTimer.current);
  }, [searchQuery]);

  const upd = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const toggleCity = (c) => {
    setError(null);
    const key = (x) => `${x.city}|${x.latitude?.toFixed(3)}`;
    const already = chosen.findIndex((x) => key(x) === key(c));
    if (already >= 0) {
      setChosen(chosen.filter((_, i) => i !== already));
    } else if (chosen.length < 3) {
      setChosen([...chosen, c]);
    } else {
      setError('Tu as déjà choisi 3 villes. Retire-en une pour en ajouter une autre.');
    }
  };

  const handleCheckout = async () => {
    setError(null);
    if (!form.email || !form.email.includes('@')) { setError('Email invalide'); return; }
    if (!form.first_name.trim()) { setError('Prénom requis'); return; }
    if (!form.birth_date || !form.birth_time) { setError('Date et heure de naissance requises'); return; }
    if (chosen.length !== 3) { setError('Merci de choisir exactement 3 villes'); return; }
    setLoading(true);
    try {
      const r = await axios.post(`${API}/api/astrocartographie/checkout`, {
        ...form,
        chosen_cities: chosen,
        origin_url: window.location.origin,
        promo_code: promoCode.trim() || undefined,
      });
      if (r.data?.url) window.location.href = r.data.url;
      else setError('Une erreur est survenue');
    } catch (e) {
      setError(e.response?.data?.detail || 'Impossible de créer la session');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen relative" style={{ padding: '110px 20px 140px' }} data-testid="astrocartographie-page">
      <SEO path="/astrocartographie"
           title="Astrocartographie · Où vivre ta meilleure vie · 49€ · Plume Astrale"
           description="Un PDF unique de 18 pages : ta carte du monde + analyse de 3 villes que tu choisis + 2 destinations bonus par Soléna." />

      <div className="max-w-4xl mx-auto">
        {/* Hero */}
        <div className="text-center mb-14">
          <p className="text-[10px] uppercase mb-5" style={{ color: '#D4AF37', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}>
            ✦ Astrocartographie Personnalisée ✦
          </p>
          <h1 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 300, lineHeight: 1.05,
            fontSize: 'clamp(38px, 6vw, 66px)',
            color: '#F5EEE0', marginBottom: 18,
          }}>
            Où vivre <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>ta meilleure vie</em> ?
          </h1>
          <p className="text-base md:text-lg max-w-2xl mx-auto mb-8" style={{ color: 'rgba(227,215,255,0.85)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic', lineHeight: 1.6 }}>
            Un rapport intime de 18 pages : ta carte du monde avec toutes tes lignes planétaires,
            l&apos;analyse détaillée de 3 villes que tu choisis, et 2 destinations bonus que Soléna sélectionne
            spécialement pour toi.
          </p>
          <div className="inline-flex items-baseline gap-2 mb-2">
            <span style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 48, fontWeight: 300, color: '#D4AF37' }}>49€</span>
            <span className="text-xs" style={{ color: 'rgba(227,215,255,0.55)', letterSpacing: '0.2em' }}>· PAIEMENT UNIQUE</span>
          </div>
          <p className="text-xs" style={{ color: 'rgba(227,215,255,0.45)', letterSpacing: '0.1em' }}>
            Livré par email dans les 5 minutes suivant le paiement
          </p>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
          {[
            { icon: Globe, title: 'Ta carte du monde', desc: 'Une carte mondiale avec toutes tes lignes planétaires (Ascendant, Descendant, MC, IC) projetées.' },
            { icon: MapPin, title: '3 villes que tu choisis', desc: 'Pour chacune : ambiance, carrière, amour, spiritualité, corps. Un conseil intime de Soléna.' },
            { icon: Sparkles, title: '2 bonus par Soléna', desc: 'Deux destinations surprises, choisies pour toi selon la géographie unique de ton ciel.' },
          ].map(({ icon: Icon, title, desc }, i) => (
            <div key={i} className="plume-glass p-6" data-testid={`astrocarto-feature-${i}`}>
              <Icon className="w-7 h-7 mb-3" style={{ color: '#D4AF37' }} strokeWidth={1.2} />
              <h3 className="text-lg mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>{title}</h3>
              <p className="text-sm" style={{ color: 'rgba(227,215,255,0.72)', lineHeight: 1.6 }}>{desc}</p>
            </div>
          ))}
        </div>

        {step === 0 ? (
          <>
            <TestimonialsWidget
              testimonials={TESTIMONIALS_ASTROCARTO}
              title="Elles ont trouvé leur lieu"
              subtitle="Trois femmes qui ont composé leur rapport d'astrocartographie"
              testIdPrefix="astrocarto-testimonial"
            />
            <div className="text-center">
              <button onClick={() => setStep(1)} className="plume-btn-primary" data-testid="astrocarto-cta-start">
                Composer mon rapport — 49€
                <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
              </button>
              <p className="text-xs mt-4" style={{ color: 'rgba(227,215,255,0.5)', letterSpacing: '0.1em' }}>
                Paiement sécurisé Stripe · Livraison immédiate par email
              </p>
            </div>
          </>
        ) : (
          <>
            {/* Étape 1 : Données de naissance */}
            <div className="plume-glass p-8 md:p-10 max-w-xl mx-auto mb-8" data-testid="astrocarto-form-birth">
              <h2 className="text-2xl mb-6 text-center" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>
                1. Tes coordonnées astrales
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>Email pour la livraison</label>
                  <input type="email" value={form.email} onChange={e => upd('email', e.target.value)}
                         data-testid="astrocarto-email"
                         className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
                </div>
                <div>
                  <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>Prénom</label>
                  <input type="text" value={form.first_name} onChange={e => upd('first_name', e.target.value)}
                         data-testid="astrocarto-firstname"
                         className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>Date naiss.</label>
                    <input type="date" value={form.birth_date} onChange={e => upd('birth_date', e.target.value)}
                           data-testid="astrocarto-birthdate"
                           className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
                  </div>
                  <div>
                    <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>Heure naiss.</label>
                    <input type="time" value={form.birth_time} onChange={e => upd('birth_time', e.target.value)}
                           data-testid="astrocarto-birthtime"
                           className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
                  </div>
                </div>
                <div>
                  <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>Ville de naissance</label>
                  <input type="text" value={form.birth_city} onChange={e => upd('birth_city', e.target.value)}
                         data-testid="astrocarto-city"
                         className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
                </div>
              </div>
            </div>

            {/* Étape 2 : Choix des 3 villes */}
            <div className="plume-glass p-8 md:p-10 max-w-2xl mx-auto mb-8" data-testid="astrocarto-cities-picker">
              <h2 className="text-2xl mb-2 text-center" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>
                2. Choisis 3 villes à explorer
              </h2>
              <p className="text-center text-sm mb-6" style={{ color: 'rgba(227,215,255,0.65)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
                {chosen.length}/3 sélectionnées — clique pour ajouter ou retirer
              </p>

              {chosen.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-5 justify-center" data-testid="astrocarto-chosen-list">
                  {chosen.map((c) => (
                    <button key={`${c.city}-${c.latitude}`} onClick={() => toggleCity(c)}
                      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm"
                      style={{
                        background: 'rgba(212,175,55,0.15)',
                        border: '1px solid #D4AF37', color: '#F5EEE0',
                      }}
                      data-testid={`astrocarto-chosen-${c.city.toLowerCase()}`}
                    >
                      {c.city} <X className="w-3 h-3" />
                    </button>
                  ))}
                </div>
              )}

              {/* Free search input */}
              <div className="mb-4 relative" data-testid="astrocarto-search-wrap">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'rgba(212,175,55,0.6)' }} />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Cherche une autre ville (ex: Tokyo, Lima, Reykjavik...)"
                    data-testid="astrocarto-search-input"
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-plume-night-soft/40 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60"
                    style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 15 }}
                  />
                  {searching && (
                    <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 animate-spin" style={{ color: '#D4AF37' }} />
                  )}
                </div>
                {searchResults.length > 0 && (
                  <div
                    className="absolute z-20 left-0 right-0 mt-1 rounded-xl overflow-hidden"
                    style={{
                      background: 'rgba(17,22,37,0.98)',
                      border: '1px solid rgba(212,175,55,0.3)',
                      boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
                      maxHeight: 280, overflowY: 'auto',
                    }}
                    data-testid="astrocarto-search-results"
                  >
                    {searchResults.map((r, i) => (
                      <button
                        key={`${r.city}-${r.latitude}-${i}`}
                        onClick={() => {
                          toggleCity(r);
                          setSearchQuery('');
                          setSearchResults([]);
                        }}
                        style={{
                          display: 'block', width: '100%', textAlign: 'left',
                          padding: '10px 14px',
                          background: 'transparent',
                          border: 'none',
                          borderBottom: '1px solid rgba(212,175,55,0.1)',
                          color: '#F5EEE0',
                          fontFamily: 'Cormorant Garamond, serif',
                          fontSize: 14,
                          cursor: 'pointer',
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(212,175,55,0.08)'}
                        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                        data-testid={`astrocarto-search-result-${i}`}
                      >
                        <span>{r.city}</span>
                        {r.country_code && (
                          <span style={{ marginLeft: 8, fontSize: 11, opacity: 0.6 }}>· {r.country_code}</span>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <p className="text-center text-xs mb-3" style={{ color: 'rgba(227,215,255,0.5)' }}>ou choisis parmi ces suggestions</p>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {CITY_SUGGESTIONS.map((c) => {
                  const isChosen = chosen.some((x) => x.city === c.city && Math.abs(x.latitude - c.latitude) < 0.01);
                  return (
                    <button
                      key={c.city}
                      onClick={() => toggleCity(c)}
                      data-testid={`astrocarto-city-${c.city.toLowerCase().replace(/[^a-z]/g, '-')}`}
                      style={{
                        padding: '10px 8px',
                        borderRadius: 10,
                        border: `1px solid ${isChosen ? '#D4AF37' : 'rgba(212,175,55,0.25)'}`,
                        background: isChosen ? 'rgba(212,175,55,0.1)' : 'rgba(26,32,53,0.4)',
                        color: isChosen ? '#D4AF37' : '#F5EEE0',
                        fontFamily: 'Cormorant Garamond, serif',
                        fontSize: 14,
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                      }}
                    >
                      <div>{c.city}</div>
                      <div style={{ fontSize: 10, opacity: 0.65, marginTop: 2 }}>{c.country}</div>
                    </button>
                  );
                })}
              </div>
              <p className="text-[10px] text-center mt-4" style={{ color: 'rgba(227,215,255,0.45)', letterSpacing: '0.15em' }}>
                Tu peux aussi taper une ville dans le champ de recherche ci-dessus
              </p>
            </div>

            {/* Étape 3 : Promo + Checkout */}
            <div className="plume-glass p-8 md:p-10 max-w-xl mx-auto" data-testid="astrocarto-checkout-box">
              {promoCode === 'PLUME15' && (
                <div className="mb-4 p-3 rounded-xl text-center" style={{
                  background: 'rgba(212,175,55,0.12)',
                  border: '1px solid rgba(212,175,55,0.4)',
                }} data-testid="astrocarto-plume15-banner">
                  <div className="text-[10px] uppercase" style={{ color: '#D4AF37', letterSpacing: '0.28em' }}>
                    ✦ Offre clientes Plume ✦
                  </div>
                  <div className="mt-1" style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 18, color: '#F5EEE0' }}>
                    <span style={{ textDecoration: 'line-through', color: 'rgba(227,215,255,0.4)', marginRight: 8 }}>49€</span>
                    <span style={{ color: '#D4AF37' }}>41,65€</span>
                    <span style={{ fontSize: 12, marginLeft: 8, color: 'rgba(227,215,255,0.65)' }}>· 15% de réduction</span>
                  </div>
                </div>
              )}
              <div className="space-y-4">
                <div>
                  <label className="text-xs uppercase" style={{ color: 'rgba(212,175,55,0.65)', letterSpacing: '0.2em' }}>
                    Code promo (optionnel)
                  </label>
                  <input
                    type="text"
                    value={promoCode}
                    onChange={e => setPromoCode(e.target.value.toUpperCase())}
                    placeholder="Ex: ADMIN26"
                    data-testid="astrocarto-promo"
                    className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/40 border border-plume-gold/15 text-plume-lavender focus:outline-none focus:border-plume-gold/50"
                    style={{ letterSpacing: '0.2em', fontFamily: 'Cinzel, serif', fontSize: 13 }}
                  />
                </div>
                {error && <p className="text-sm text-center" style={{ color: '#F87171' }} data-testid="astrocarto-error">{error}</p>}
                <button onClick={handleCheckout} disabled={loading} className="plume-btn-primary w-full justify-center" data-testid="astrocarto-checkout-btn">
                  {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Redirection...</> :
                    promoCode === 'PLUME15' ? <>Payer 41,65€ (offre Plume) <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></> :
                    promoCode.trim() ? <>Déverrouiller mon rapport <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></>
                                     : <>Payer 49€ et recevoir mon rapport <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></>}
                </button>
                <p className="text-[10px] text-center mt-3" style={{ color: 'rgba(227,215,255,0.4)', letterSpacing: '0.2em' }}>
                  <ShieldCheck className="w-3 h-3 inline-block mr-1" /> PAIEMENT SÉCURISÉ STRIPE · TVA INCLUSE
                </p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default AstrocartographieSales;
