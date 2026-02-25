import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sun, Moon, Star, Flame, Droplets, Wind, Mountain, Heart, Briefcase, Activity, Sparkles, ChevronRight } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SIGNES = [
  { key: 'Aries', fr: 'Bélier', icon: Flame, dates: '21 mars - 19 avril' },
  { key: 'Taurus', fr: 'Taureau', icon: Mountain, dates: '20 avril - 20 mai' },
  { key: 'Gemini', fr: 'Gémeaux', icon: Wind, dates: '21 mai - 20 juin' },
  { key: 'Cancer', fr: 'Cancer', icon: Moon, dates: '21 juin - 22 juillet' },
  { key: 'Leo', fr: 'Lion', icon: Sun, dates: '23 juillet - 22 août' },
  { key: 'Virgo', fr: 'Vierge', icon: Star, dates: '23 août - 22 sept.' },
  { key: 'Libra', fr: 'Balance', icon: Wind, dates: '23 sept. - 22 oct.' },
  { key: 'Scorpio', fr: 'Scorpion', icon: Droplets, dates: '23 oct. - 21 nov.' },
  { key: 'Sagittarius', fr: 'Sagittaire', icon: Flame, dates: '22 nov. - 21 déc.' },
  { key: 'Capricorn', fr: 'Capricorne', icon: Mountain, dates: '22 déc. - 19 janv.' },
  { key: 'Aquarius', fr: 'Verseau', icon: Wind, dates: '20 janv. - 18 fév.' },
  { key: 'Pisces', fr: 'Poissons', icon: Droplets, dates: '19 fév. - 20 mars' },
];

const ScoreBar = ({ score, max = 10, label }) => (
  <div className="flex items-center gap-3">
    <span className="text-[#E0D9F6]/60 text-sm w-24">{label}</span>
    <div className="flex-1 h-2 bg-[#1A0B2E] rounded-full overflow-hidden">
      <div 
        className="h-full rounded-full transition-all duration-1000"
        style={{ width: `${(score / max) * 100}%`, background: 'linear-gradient(90deg, #C5A059, #F3E5AB)' }}
      />
    </div>
    <span className="text-[#C5A059] text-sm font-bold w-8 text-right">{score}/{max}</span>
  </div>
);

const Quotidien = () => {
  const navigate = useNavigate();
  const [selectedSign, setSelectedSign] = useState(null);
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showSignPicker, setShowSignPicker] = useState(true);

  useEffect(() => {
    // Try to get sign from localStorage
    const data = localStorage.getItem('plume_astrale_data');
    if (data) {
      try {
        const parsed = JSON.parse(data);
        const dateNaissance = new Date(parsed.dateNaissance);
        const sign = getZodiacSign(dateNaissance);
        if (sign) {
          setSelectedSign(sign);
          setShowSignPicker(false);
          fetchContent(sign);
        }
      } catch (e) { /* ignore */ }
    }
  }, []);

  const getZodiacSign = (date) => {
    const month = date.getMonth() + 1;
    const day = date.getDate();
    if ((month === 3 && day >= 21) || (month === 4 && day <= 19)) return 'Aries';
    if ((month === 4 && day >= 20) || (month === 5 && day <= 20)) return 'Taurus';
    if ((month === 5 && day >= 21) || (month === 6 && day <= 20)) return 'Gemini';
    if ((month === 6 && day >= 21) || (month === 7 && day <= 22)) return 'Cancer';
    if ((month === 7 && day >= 23) || (month === 8 && day <= 22)) return 'Leo';
    if ((month === 8 && day >= 23) || (month === 9 && day <= 22)) return 'Virgo';
    if ((month === 9 && day >= 23) || (month === 10 && day <= 22)) return 'Libra';
    if ((month === 10 && day >= 23) || (month === 11 && day <= 21)) return 'Scorpio';
    if ((month === 11 && day >= 22) || (month === 12 && day <= 21)) return 'Sagittarius';
    if ((month === 12 && day >= 22) || (month === 1 && day <= 19)) return 'Capricorn';
    if ((month === 1 && day >= 20) || (month === 2 && day <= 18)) return 'Aquarius';
    return 'Pisces';
  };

  const fetchContent = async (sign) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/daily/${sign}`);
      const data = await res.json();
      setContent(data);
    } catch (e) {
      console.error('Error fetching daily content:', e);
    }
    setLoading(false);
  };

  const handleSelectSign = (sign) => {
    setSelectedSign(sign);
    setShowSignPicker(false);
    fetchContent(sign);
  };

  const signeInfo = SIGNES.find(s => s.key === selectedSign);

  return (
    <div className="min-h-screen relative">
      <StarField />
      <div className="relative z-10 py-12 px-4 md:px-6">
        <div className="max-w-4xl mx-auto">
          
          {/* Header */}
          <div className="text-center mb-10">
            <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-3 font-light">
              Guidance Quotidienne
            </p>
            <h1 className="text-3xl md:text-5xl mb-3" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Votre Jour Cosmique
            </h1>
            <p className="text-[#E0D9F6]/60 font-light">
              {new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
            </p>
          </div>

          {/* Sign picker toggle */}
          {!showSignPicker && signeInfo && (
            <div className="text-center mb-8">
              <button 
                onClick={() => setShowSignPicker(true)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-[#C5A059]/30 text-[#C5A059] hover:bg-[#C5A059]/10 transition-colors text-sm"
                data-testid="change-sign-btn"
              >
                <signeInfo.icon className="w-4 h-4" />
                {signeInfo.fr} — Changer de signe
              </button>
            </div>
          )}

          {/* Sign picker grid */}
          {showSignPicker && (
            <div className="card-mystical mb-10" data-testid="sign-picker">
              <h2 className="text-xl mb-6 text-center" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                Choisissez votre signe
              </h2>
              <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
                {SIGNES.map(s => {
                  const Icon = s.icon;
                  return (
                    <button
                      key={s.key}
                      onClick={() => handleSelectSign(s.key)}
                      className={`p-3 rounded-xl border transition-all text-center hover:scale-105 ${
                        selectedSign === s.key
                          ? 'border-[#C5A059] bg-[#C5A059]/20 text-[#F3E5AB]'
                          : 'border-[#C5A059]/20 bg-[#1A0B2E]/50 text-[#E0D9F6]/70 hover:border-[#C5A059]/50'
                      }`}
                      data-testid={`sign-${s.key}`}
                    >
                      <Icon className="w-5 h-5 mx-auto mb-1 text-[#C5A059]" strokeWidth={1.5} />
                      <div className="text-sm font-medium">{s.fr}</div>
                      <div className="text-xs text-[#E0D9F6]/40 mt-0.5">{s.dates}</div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className="flex justify-center py-20">
              <div className="w-12 h-12 border-2 border-[#C5A059] border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {/* Content */}
          {content && !loading && (
            <div className="space-y-6 animate-fade-in">
              
              {/* Phrase spirituelle */}
              <div className="card-mystical text-center p-8" data-testid="phrase-du-jour">
                <Sparkles className="w-8 h-8 text-[#C5A059] mx-auto mb-4" strokeWidth={1} />
                <p className="text-lg md:text-xl text-[#F3E5AB] italic font-light leading-relaxed" style={{ fontFamily: 'Cinzel, serif' }}>
                  "{content.phrase_du_jour}"
                </p>
              </div>

              {/* Energie + Lucky */}
              <div className="grid md:grid-cols-2 gap-4">
                <div className="card-mystical" data-testid="energie-jour">
                  <h3 className="text-[#C5A059] text-sm uppercase tracking-widest mb-4">Energie du Jour</h3>
                  <div className="text-center mb-4">
                    <span className="text-5xl font-bold text-gold-gradient" style={{ fontFamily: 'Cinzel, serif' }}>
                      {content.energie_du_jour}
                    </span>
                    <span className="text-[#E0D9F6]/40 text-lg">/10</span>
                  </div>
                  <div className="h-3 bg-[#1A0B2E] rounded-full overflow-hidden">
                    <div 
                      className="h-full rounded-full transition-all duration-1000"
                      style={{ width: `${(content.energie_du_jour / 10) * 100}%`, background: 'linear-gradient(90deg, #C5A059, #F3E5AB)' }}
                    />
                  </div>
                </div>
                
                <div className="card-mystical" data-testid="chance-jour">
                  <h3 className="text-[#C5A059] text-sm uppercase tracking-widest mb-4">Vos Porte-Bonheur</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-[#E0D9F6]/60 text-sm">Numeros</span>
                      <span className="text-[#F3E5AB] font-bold">{content.numeros_chance.join(' - ')}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-[#E0D9F6]/60 text-sm">Couleur</span>
                      <span className="text-[#F3E5AB] font-bold">{content.couleur_du_jour}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-[#E0D9F6]/60 text-sm">Element</span>
                      <span className="text-[#F3E5AB] font-bold">{content.element}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Conseil du jour */}
              <div className="card-mystical" data-testid="conseil-jour">
                <h3 className="text-[#C5A059] text-sm uppercase tracking-widest mb-3">Conseil du Jour</h3>
                <p className="text-[#E0D9F6]/80 leading-relaxed font-light text-lg">
                  {content.conseil_du_jour}
                </p>
              </div>

              {/* Horoscope sections */}
              <div className="card-mystical" data-testid="horoscope-detail">
                <h3 className="text-xl mb-6" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                  Horoscope Detaille
                </h3>
                
                <div className="space-y-6">
                  {[
                    { key: 'amour', label: 'Amour', icon: Heart, color: '#E8526E' },
                    { key: 'carriere', label: 'Carriere', icon: Briefcase, color: '#C5A059' },
                    { key: 'sante', label: 'Sante', icon: Activity, color: '#4ECB71' },
                    { key: 'spirituel', label: 'Spirituel', icon: Sparkles, color: '#A78BFA' },
                  ].map(({ key, label, icon: Icon, color }) => (
                    <div key={key} className="border-b border-[#C5A059]/10 last:border-0 pb-4 last:pb-0">
                      <div className="flex items-center gap-3 mb-2">
                        <Icon className="w-5 h-5" style={{ color }} strokeWidth={1.5} />
                        <span className="text-[#F3E5AB] font-medium">{label}</span>
                        <div className="flex-1" />
                        <span className="text-[#C5A059] font-bold">{content.horoscope[key].score}/10</span>
                      </div>
                      <div className="h-1.5 bg-[#1A0B2E] rounded-full overflow-hidden mb-3">
                        <div 
                          className="h-full rounded-full"
                          style={{ width: `${(content.horoscope[key].score / 10) * 100}%`, background: color }}
                        />
                      </div>
                      <p className="text-[#E0D9F6]/70 text-sm font-light leading-relaxed pl-8">
                        {content.horoscope[key].texte}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* CTA vers autres services */}
              <div className="grid md:grid-cols-2 gap-4">
                <button 
                  onClick={() => navigate('/tarot-oui-non')}
                  className="card-mystical hover:border-[#C5A059]/50 transition-all group text-left"
                  data-testid="cta-tarot-oui-non"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-[#F3E5AB] font-medium mb-1">Tarot Oui/Non</h3>
                      <p className="text-[#E0D9F6]/50 text-sm">Posez votre question aux arcanes</p>
                      <span className="text-[#C5A059] font-bold text-sm mt-1 inline-block">4,99 EUR</span>
                    </div>
                    <ChevronRight className="w-5 h-5 text-[#C5A059] group-hover:translate-x-1 transition-transform" />
                  </div>
                </button>
                <button
                  onClick={() => navigate('/tarologie')}
                  className="card-mystical hover:border-[#C5A059]/50 transition-all group text-left"
                  data-testid="cta-tarologie"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-[#F3E5AB] font-medium mb-1">Tarologie & Mediumnite</h3>
                      <p className="text-[#E0D9F6]/50 text-sm">Lecture complete 7 cartes + mediumnique</p>
                      <span className="text-[#C5A059] font-bold text-sm mt-1 inline-block">35 EUR</span>
                    </div>
                    <ChevronRight className="w-5 h-5 text-[#C5A059] group-hover:translate-x-1 transition-transform" />
                  </div>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Quotidien;
