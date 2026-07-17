import React, { useState, useEffect, useCallback } from 'react';
import PageHero from '@/components/PageHero';
import { useNavigate } from 'react-router-dom';
import { Sun, Moon, Star, Heart, Briefcase, Activity, Coins, RefreshCw, Loader2 } from 'lucide-react';
import SEO from '@/components/SEO';
import NatalCompletionPrompt from '@/components/NatalCompletionPrompt';
import { TransitsToday } from '@/pages/RevolutionSolaire';

const periodMap = { jour: 'daily', semaine: 'weekly', mois: 'monthly' };

const Horoscope = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [activeTab, setActiveTab] = useState('jour');
  const [loading, setLoading] = useState(false);
  const [apiData, setApiData] = useState(null);
  const [natalData, setNatalData] = useState(null);
  const [error, setError] = useState(null);

  const getSigneFromDate = (dateStr) => {
    const date = new Date(dateStr);
    const month = date.getMonth() + 1;
    const day = date.getDate();

    if ((month === 3 && day >= 21) || (month === 4 && day <= 19)) return 'Bélier';
    if ((month === 4 && day >= 20) || (month === 5 && day <= 20)) return 'Taureau';
    if ((month === 5 && day >= 21) || (month === 6 && day <= 20)) return 'Gémeaux';
    if ((month === 6 && day >= 21) || (month === 7 && day <= 22)) return 'Cancer';
    if ((month === 7 && day >= 23) || (month === 8 && day <= 22)) return 'Lion';
    if ((month === 8 && day >= 23) || (month === 9 && day <= 22)) return 'Vierge';
    if ((month === 9 && day >= 23) || (month === 10 && day <= 22)) return 'Balance';
    if ((month === 10 && day >= 23) || (month === 11 && day <= 21)) return 'Scorpion';
    if ((month === 11 && day >= 22) || (month === 12 && day <= 21)) return 'Sagittaire';
    if ((month === 12 && day >= 22) || (month === 1 && day <= 19)) return 'Capricorne';
    if ((month === 1 && day >= 20) || (month === 2 && day <= 18)) return 'Verseau';
    return 'Poissons';
  };

  const fallbackHoroscopes = {
    jour: {
      title: "Horoscope du Jour",
      date: new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' }),
      general: "Les astres vous invitent aujourd'hui à écouter votre intuition. Une opportunité inattendue pourrait se présenter dans l'après-midi.",
      amour: { score: 4, text: "Vénus vous sourit. Profitez de moments tendres avec vos proches." },
      travail: { score: 3, text: "Mercure en transit suggère de la prudence dans vos communications." },
      sante: { score: 5, text: "Excellente vitalité ! La Lune soutient votre énergie." },
      finance: { score: 3, text: "Évitez les dépenses impulsives aujourd'hui." }
    },
    semaine: {
      title: "Horoscope de la Semaine",
      date: new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long' }),
      general: "Cette semaine marque un tournant important. Les énergies cosmiques favorisent les nouveaux départs.",
      amour: { score: 4, text: "Semaine propice aux discussions profondes." },
      travail: { score: 5, text: "Excellent moment pour les négociations et les présentations." },
      sante: { score: 3, text: "Attention à la fatigue en milieu de semaine." },
      finance: { score: 4, text: "Une rentrée d'argent imprévue est possible." }
    },
    mois: {
      title: "Horoscope du Mois",
      date: new Date().toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' }),
      general: "Ce mois est un mois de transformation intérieure. De nouvelles opportunités de croissance se présentent.",
      amour: { score: 5, text: "Mois béni pour l'amour et les relations." },
      travail: { score: 4, text: "Des projets en sommeil reprennent vie." },
      sante: { score: 4, text: "Énergie stable avec un pic de vitalité." },
      finance: { score: 3, text: "Prudence en début de mois, la suite est plus favorable." }
    }
  };

  const fetchHoroscope = useCallback(async (dateStr, period) => {
    setLoading(true);
    setError(null);
    try {
      const birthDate = new Date(dateStr);
      const params = {
        day: birthDate.getDate(),
        month: birthDate.getMonth() + 1,
        year: birthDate.getFullYear(),
        hour: 12,
        min: 0,
        lat: 48.8566,
        lon: 2.3522,
        tzone: 1,
        period: periodMap[period] || 'daily',
      };

      const res = await fetch(`${process.env.REACT_APP_BACKEND_URL || ''}/api/astrology/horoscope-prediction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      const data = await res.json();
      if (data.success) {
        setApiData(data.data);
      }
    } catch (e) {
      console.warn('Astrology API unavailable, using fallback data');
      setApiData(null);
    }
    setLoading(false);
  }, []);

  const fetchNatalChart = useCallback(async (dateStr) => {
    try {
      const birthDate = new Date(dateStr);
      const params = {
        day: birthDate.getDate(),
        month: birthDate.getMonth() + 1,
        year: birthDate.getFullYear(),
        hour: 12,
        min: 0,
        lat: 48.8566,
        lon: 2.3522,
        tzone: 1,
      };

      const res = await fetch(`${process.env.REACT_APP_BACKEND_URL || ''}/api/astrology/natal-chart`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      const data = await res.json();
      if (data.success) {
        setNatalData(data.data);
      }
    } catch (e) {
      console.warn('Natal chart API unavailable');
    }
  }, []);

  useEffect(() => {
    const data = localStorage.getItem('plume_astrale_data');
    if (!data) {
      navigate('/formulaire');
      return;
    }
    const parsed = JSON.parse(data);
    setUserData(parsed);
    fetchHoroscope(parsed.dateNaissance, 'jour');
    fetchNatalChart(parsed.dateNaissance);
  }, [navigate, fetchHoroscope, fetchNatalChart]);

  useEffect(() => {
    if (userData?.dateNaissance) {
      fetchHoroscope(userData.dateNaissance, activeTab);
    }
  }, [activeTab, fetchHoroscope, userData?.dateNaissance]);

  const renderStars = (score) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((i) => (
          <Star
            key={i}
            className={`w-4 h-4 ${i <= score ? 'text-[#D4AF37] fill-[#D4AF37]' : 'text-[#B8B0C8]/20'}`}
            strokeWidth={1}
          />
        ))}
      </div>
    );
  };

  // ── Mapping life_areas API v3 -> icones + couleurs FR
  const AREA_META = {
    identity:   { label: 'Identité',    color: 'rgba(212,175,55,0.2)', text: '#D4AF37' },
    health:     { label: 'Santé',       color: 'rgba(167,238,167,0.18)', text: '#7CB88A' },
    finance:    { label: 'Finances',    color: 'rgba(212,175,55,0.2)', text: '#D4AF37' },
    career:     { label: 'Carrière',    color: 'rgba(167,200,255,0.18)', text: '#6BB5E8' },
    love:       { label: 'Amour',       color: 'rgba(255,167,200,0.18)', text: '#F49AAE' },
    relationships:{ label: 'Relations', color: 'rgba(232,199,102,0.18)', text: '#E8C766' },
    creativity: { label: 'Créativité',  color: 'rgba(196,167,238,0.18)', text: '#A78BFA' },
    spirituality:{label: 'Spiritualité',color: 'rgba(212,175,55,0.18)', text: '#F4E4BC' },
  };

  if (!userData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const userSign = getSigneFromDate(userData.dateNaissance);
  const currentHoroscope = fallbackHoroscopes[activeTab];

  const titleMap = { jour: "Horoscope du Jour", semaine: "Horoscope de la Semaine", mois: "Horoscope du Mois" };

  return (
    <div className="min-h-screen">
      <SEO path="/horoscope" />

      <div className="px-6 md:px-8 py-20 md:py-28">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <p className="text-[#D4AF37] uppercase tracking-[0.3em] text-sm mb-4 font-light">
              Votre Horoscope
            </p>

            <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
              {userSign}
            </h1>

            <p className="text-lg text-[#B8B0C8]/70 font-light">
              {userData.prenom ? `${userData.prenom}, ` : ''}découvrez ce que les astres vous réservent
            </p>

            {/* Planetary positions from Astrology API */}
            {natalData && (
              <div className="mt-4 flex flex-wrap justify-center gap-3">
                {natalData.soleil && (
                  <span className="text-xs px-3 py-1 rounded-full bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/20">
                    ☉ Soleil en {natalData.soleil.signe}
                  </span>
                )}
                {natalData.lune && (
                  <span className="text-xs px-3 py-1 rounded-full bg-[#6BB5E8]/10 text-[#6BB5E8] border border-[#6BB5E8]/20">
                    ☽ Lune en {natalData.lune.signe}
                  </span>
                )}
                {natalData.ascendant && (
                  <span className="text-xs px-3 py-1 rounded-full bg-[#A78BFA]/10 text-[#A78BFA] border border-[#A78BFA]/20">
                    ↑ Ascendant {natalData.ascendant.signe}
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Soft nudge: complete birth_time if missing */}
          <div className="mb-8 max-w-2xl mx-auto">
            <NatalCompletionPrompt />
          </div>

          {/* Transits du jour sur votre theme natal */}
          <div className="mb-8 max-w-2xl mx-auto">
            <TransitsToday />
          </div>

          {/* Tabs */}
          <div className="flex justify-center gap-2 mb-8">
            {[
              { id: 'jour', label: 'Jour', icon: <Sun className="w-4 h-4" strokeWidth={1} /> },
              { id: 'semaine', label: 'Semaine', icon: <Star className="w-4 h-4" strokeWidth={1} /> },
              { id: 'mois', label: 'Mois', icon: <Moon className="w-4 h-4" strokeWidth={1} /> }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-3 rounded-full text-sm transition-all ${
                  activeTab === tab.id
                    ? 'bg-[#D4AF37] text-[#111625]'
                    : 'bg-[#15112A]/50 text-[#B8B0C8]/70 hover:bg-[#15112A] border border-[#D4AF37]/20'
                }`}
                data-testid={`tab-${tab.id}`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-[#D4AF37]" />
            </div>
          )}

          {/* Horoscope Content */}
          {!loading && (
            <div className="space-y-6 animate-fade-in">
              {/* OVERALL THEME (Astrology API v3) */}
              {apiData?.overall_theme && (
                <div className="card-mystical border border-[#D4AF37]/20">
                  <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
                    <h2 className="text-xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                      {titleMap[activeTab]}
                    </h2>
                    <div className="flex items-center gap-3">
                      {typeof apiData.overall_rating === 'number' && renderStars(apiData.overall_rating)}
                      <span className="text-[#D4AF37] text-sm">{apiData.date || ''}</span>
                    </div>
                  </div>
                  <p className="text-[#F5EEE0]/85 leading-relaxed text-base" style={{ fontFamily: 'Cormorant Garamond, serif', lineHeight: '1.85' }}>
                    {apiData.overall_theme}
                  </p>
                  {apiData.keywords && Array.isArray(apiData.keywords) && apiData.keywords.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-2">
                      {apiData.keywords.slice(0, 6).map((k, i) => (
                        <span key={i} className="text-xs px-3 py-1 rounded-full bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/20">
                          {k}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* LIFE AREAS (Astrology API v3) -- 8 zones de vie */}
              {apiData?.life_areas && Array.isArray(apiData.life_areas) && apiData.life_areas.length > 0 ? (
                <div className="grid md:grid-cols-2 gap-6">
                  {apiData.life_areas.map((area, idx) => {
                    const meta = AREA_META[area.area] || { label: area.title || area.area, color: 'rgba(212,175,55,0.15)', text: '#D4AF37' };
                    return (
                      <div key={idx} className="card-mystical">
                        <div className="flex items-center gap-3 mb-3">
                          <div className="p-2 rounded-full" style={{ background: meta.color, color: meta.text }}>
                            <Star className="w-5 h-5" strokeWidth={1.2} fill="currentColor" />
                          </div>
                          <div className="flex-1">
                            <h3 className="text-[#F5EEE0]">{area.title || meta.label}</h3>
                            {typeof area.rating === 'number' && renderStars(area.rating)}
                          </div>
                        </div>
                        <p className="text-[#B8B0C8]/85 text-sm font-light leading-relaxed">
                          {area.prediction || area.text || ''}
                        </p>
                        {area.advice && (
                          <p className="mt-3 text-xs italic text-[#D4AF37]/85">
                            <span style={{ letterSpacing: '0.1em' }}>CONSEIL —</span> {area.advice}
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                /* Fallback static cards si jamais l'API est down */
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="card-mystical">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="p-2 rounded-full bg-pink-500/20 text-pink-400"><Heart className="w-5 h-5" strokeWidth={1} /></div>
                      <div className="flex-1"><h3 className="text-[#F5EEE0]">Amour</h3>{renderStars(currentHoroscope.amour.score)}</div>
                    </div>
                    <p className="text-[#B8B0C8]/70 text-sm font-light">{currentHoroscope.amour.text}</p>
                  </div>
                  <div className="card-mystical">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="p-2 rounded-full bg-blue-500/20 text-blue-400"><Briefcase className="w-5 h-5" strokeWidth={1} /></div>
                      <div className="flex-1"><h3 className="text-[#F5EEE0]">Travail</h3>{renderStars(currentHoroscope.travail.score)}</div>
                    </div>
                    <p className="text-[#B8B0C8]/70 text-sm font-light">{currentHoroscope.travail.text}</p>
                  </div>
                  <div className="card-mystical">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="p-2 rounded-full bg-emerald-500/20 text-emerald-400"><Activity className="w-5 h-5" strokeWidth={1} /></div>
                      <div className="flex-1"><h3 className="text-[#F5EEE0]">Santé</h3>{renderStars(currentHoroscope.sante.score)}</div>
                    </div>
                    <p className="text-[#B8B0C8]/70 text-sm font-light">{currentHoroscope.sante.text}</p>
                  </div>
                  <div className="card-mystical">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="p-2 rounded-full bg-[#D4AF37]/20 text-[#D4AF37]"><Coins className="w-5 h-5" strokeWidth={1} /></div>
                      <div className="flex-1"><h3 className="text-[#F5EEE0]">Finances</h3>{renderStars(currentHoroscope.finance.score)}</div>
                    </div>
                    <p className="text-[#B8B0C8]/70 text-sm font-light">{currentHoroscope.finance.text}</p>
                  </div>
                </div>
              )}

              {/* PLANETARY INFLUENCES (v3) */}
              {apiData?.planetary_influences && Array.isArray(apiData.planetary_influences) && apiData.planetary_influences.length > 0 && (
                <div className="card-mystical">
                  <h3 className="text-sm tracking-widest uppercase mb-4 text-[#D4AF37]" style={{ letterSpacing: '0.12em' }}>
                    Influences planétaires
                  </h3>
                  <div className="space-y-3">
                    {apiData.planetary_influences.map((pi, i) => (
                      <div key={i} className="text-sm">
                        <span className="text-[#D4AF37] font-medium">{pi.planet || pi.name}</span>
                        {pi.aspect && <span className="text-[#B8B0C8]/50"> — {pi.aspect}</span>}
                        {pi.description && <p className="text-[#B8B0C8]/70 mt-1">{pi.description}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Planetary Details (natal chart sidebar) */}
              {natalData?.planetes && (
                <div className="card-mystical">
                  <h3 className="text-lg mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                    Positions Planétaires Natales
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {natalData.planetes.slice(0, 9).map((p, i) => (
                      <div key={i} className="flex items-center gap-2 text-sm">
                        <span className="text-[#D4AF37]">{p.nom}</span>
                        <span className="text-[#B8B0C8]/50">→</span>
                        <span className="text-[#B8B0C8]/80">{p.signe}</span>
                        {p.retrograde && <span className="text-xs text-red-400">℞</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* LUCKY ELEMENTS (v3) */}
              {apiData?.lucky_elements && (
                <div className="card-mystical text-center">
                  <h3 className="text-lg mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                    Éléments chanceux
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    {apiData.lucky_elements.numbers && (
                      <div>
                        <p className="text-[#D4AF37]/70 text-xs uppercase tracking-widest mb-2">Nombres</p>
                        <p className="text-[#F5EEE0]">{(apiData.lucky_elements.numbers || []).join(' · ')}</p>
                      </div>
                    )}
                    {apiData.lucky_elements.colors && (
                      <div>
                        <p className="text-[#D4AF37]/70 text-xs uppercase tracking-widest mb-2">Couleurs</p>
                        <p className="text-[#F5EEE0]">{(apiData.lucky_elements.colors || []).join(' · ')}</p>
                      </div>
                    )}
                    {apiData.lucky_elements.days && (
                      <div>
                        <p className="text-[#D4AF37]/70 text-xs uppercase tracking-widest mb-2">Jours</p>
                        <p className="text-[#F5EEE0]">{(apiData.lucky_elements.days || []).join(' · ')}</p>
                      </div>
                    )}
                    {apiData.lucky_elements.gemstones && (
                      <div>
                        <p className="text-[#D4AF37]/70 text-xs uppercase tracking-widest mb-2">Pierres</p>
                        <p className="text-[#F5EEE0]">{(apiData.lucky_elements.gemstones || []).join(' · ')}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Refresh Notice */}
          <div className="mt-8 text-center text-[#B8B0C8]/40 text-sm flex items-center justify-center gap-2">
            <RefreshCw className="w-4 h-4" />
            <span>Horoscope alimenté par Astrology API — mis à jour en temps réel</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Horoscope;
