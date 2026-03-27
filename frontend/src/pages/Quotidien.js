import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Loader2 } from 'lucide-react';
import SEO from '@/components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const SIGNES = [
  { key: 'Aries', fr: 'Belier', dates: '21 mars - 19 avril' },
  { key: 'Taurus', fr: 'Taureau', dates: '20 avril - 20 mai' },
  { key: 'Gemini', fr: 'Gemeaux', dates: '21 mai - 20 juin' },
  { key: 'Cancer', fr: 'Cancer', dates: '21 juin - 22 juillet' },
  { key: 'Leo', fr: 'Lion', dates: '23 juillet - 22 aout' },
  { key: 'Virgo', fr: 'Vierge', dates: '23 aout - 22 sept.' },
  { key: 'Libra', fr: 'Balance', dates: '23 sept. - 22 oct.' },
  { key: 'Scorpio', fr: 'Scorpion', dates: '23 oct. - 21 nov.' },
  { key: 'Sagittarius', fr: 'Sagittaire', dates: '22 nov. - 21 dec.' },
  { key: 'Capricorn', fr: 'Capricorne', dates: '22 dec. - 19 janv.' },
  { key: 'Aquarius', fr: 'Verseau', dates: '20 janv. - 18 fev.' },
  { key: 'Pisces', fr: 'Poissons', dates: '19 fev. - 20 mars' },
];

const ScoreBar = ({ score, max = 10, label, color = 'var(--pa-accent)' }) => (
  <div className="flex items-center gap-4">
    <span className="text-xs tracking-widest uppercase w-24 flex-shrink-0" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>{label}</span>
    <div className="flex-1 h-px relative" style={{ background: 'var(--pa-divider)' }}>
      <div className="h-px absolute left-0 top-0 transition-all duration-1000" style={{ width: `${(score / max) * 100}%`, background: color }} />
    </div>
    <span className="text-xs w-8 text-right" style={{ color }}>{score}/{max}</span>
  </div>
);

const Quotidien = () => {
  const navigate = useNavigate();
  const [selectedSign, setSelectedSign] = useState(null);
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showSignPicker, setShowSignPicker] = useState(true);

  useEffect(() => {
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
      } catch (e) {}
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
      <SEO path="/quotidien" />
      <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
      <div className="max-w-2xl mx-auto">

        <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12">
          <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
        </button>

        {/* Header */}
        <div className="mb-12 flex items-start gap-6">
          <img src="https://customer-assets.emergentagent.com/job_6ebe2661-1b82-4742-afc5-632bf29dfcc5/artifacts/vg88c54m_IMG4.png" alt="" className="w-20 md:w-28 flex-shrink-0 rounded-full opacity-80" style={{ filter: 'drop-shadow(0 0 20px rgba(197,160,89,0.15))' }} />
          <div>
          <p className="section-label">Guidance quotidienne</p>
          <h1
            className="text-3xl md:text-4xl mb-4"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
          >
            Votre jour cosmique
          </h1>
          <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
            {new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
          </div>
        </div>

        {/* Sign toggle */}
        {!showSignPicker && signeInfo && (
          <div className="mb-10">
            <button onClick={() => setShowSignPicker(true)} className="link-editorial text-xs" data-testid="change-sign-btn">
              {signeInfo.fr} — Changer de signe
            </button>
          </div>
        )}

        {/* Sign picker */}
        {showSignPicker && (
          <div className="mb-12" data-testid="sign-picker">
            <p className="text-xs tracking-widest uppercase mb-6" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
              Choisissez votre signe
            </p>
            <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
              {SIGNES.map(s => (
                <button
                  key={s.key}
                  onClick={() => handleSelectSign(s.key)}
                  className="py-3 px-2 text-center transition-all duration-300"
                  style={{
                    border: `1px solid ${selectedSign === s.key ? 'var(--pa-accent)' : 'var(--pa-divider)'}`,
                    background: selectedSign === s.key ? 'rgba(196, 168, 130, 0.06)' : 'transparent',
                    color: selectedSign === s.key ? 'var(--pa-heading)' : 'var(--pa-muted)',
                  }}
                  data-testid={`sign-${s.key}`}
                >
                  <div className="text-sm">{s.fr}</div>
                  <div className="text-xs mt-0.5 opacity-50">{s.dates}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex justify-center py-20">
            <Loader2 className="w-6 h-6 animate-spin" style={{ color: 'var(--pa-accent)' }} />
          </div>
        )}

        {/* Content */}
        {content && !loading && (
          <div className="animate-fade-in">

            {/* Phrase du jour */}
            <div className="text-center mb-16" data-testid="phrase-du-jour">
              <p
                className="text-xl md:text-2xl italic leading-relaxed"
                style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 300, lineHeight: '1.6' }}
              >
                "{content.phrase_du_jour}"
              </p>
            </div>

            <div className="divider-subtle" />

            {/* Phase Lunaire */}
            {content.phase_lunaire && (
              <div className="mb-12" data-testid="phase-lunaire">
                <div className="flex items-baseline justify-between mb-4">
                  <p className="text-xs tracking-widest uppercase" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Phase lunaire</p>
                  <span style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontSize: '1.1rem' }}>
                    {content.phase_lunaire.phase}
                  </span>
                </div>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
                  {content.phase_lunaire.conseil}
                </p>
              </div>
            )}

            {/* Énergie + Lucky */}
            <div className="grid md:grid-cols-2 gap-10 mb-12">
              <div data-testid="energie-jour">
                <p className="text-xs tracking-widest uppercase mb-4" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
                  &Eacute;nergie du jour
                </p>
                <div className="flex items-baseline gap-2 mb-4">
                  <span className="text-4xl" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
                    {content.energie_du_jour}
                  </span>
                  <span className="text-sm" style={{ color: 'var(--pa-muted)' }}>/10</span>
                </div>
                <div className="h-px relative" style={{ background: 'var(--pa-divider)' }}>
                  <div className="h-px absolute left-0 top-0 transition-all duration-1000"
                    style={{ width: `${(content.energie_du_jour / 10) * 100}%`, background: 'var(--pa-accent)' }} />
                </div>
              </div>

              <div data-testid="chance-jour">
                <p className="text-xs tracking-widest uppercase mb-4" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
                  Porte-bonheur
                </p>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span style={{ color: 'var(--pa-muted)' }}>Numeros</span>
                    <span style={{ color: 'var(--pa-heading)' }}>{content.numeros_chance.join(' - ')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span style={{ color: 'var(--pa-muted)' }}>Couleur</span>
                    <span style={{ color: 'var(--pa-heading)' }}>{content.couleur_du_jour}</span>
                  </div>
                  <div className="flex justify-between">
                    <span style={{ color: 'var(--pa-muted)' }}>Element</span>
                    <span style={{ color: 'var(--pa-heading)' }}>{content.element}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Conseil */}
            <div className="mb-12" data-testid="conseil-jour">
              <p className="text-xs tracking-widest uppercase mb-4" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
                Conseil du jour
              </p>
              <p className="text-base leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
                {content.conseil_du_jour}
              </p>
            </div>

            <div className="divider-subtle" />

            {/* Horoscope detail */}
            <div data-testid="horoscope-detail">
              <p className="text-xs tracking-widest uppercase mb-8" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
                Horoscope detaille
              </p>
              <div className="space-y-8">
                {[
                  { key: 'amour', label: 'Amour', color: '#C97878' },
                  { key: 'carriere', label: 'Carriere', color: '#C5A059' },
                  { key: 'sante', label: 'Sante', color: '#7CB88A' },
                  { key: 'spirituel', label: 'Spirituel', color: '#A78BFA' },
                ].map(({ key, label, color }) => (
                  <div key={key}>
                    <ScoreBar score={content.horoscope[key].score} label={label} color={color} />
                    <p className="text-sm leading-relaxed mt-3 ml-28" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
                      {content.horoscope[key].texte}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Suggestions */}
            <div className="mt-16 pt-10" style={{ borderTop: '1px solid var(--pa-divider)' }}>
              <p className="text-xs tracking-widest uppercase mb-6" style={{ color: 'var(--pa-muted)', letterSpacing: '0.12em' }}>
                Approfondir
              </p>
              <div className="space-y-4">
                <button onClick={() => navigate('/tarot-oui-non')} className="block w-full text-left group" data-testid="cta-tarot-oui-non">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm mb-0.5 transition-colors duration-300 group-hover:text-[#C5A059]" style={{ color: 'var(--pa-heading)' }}>
                        Tarot Oui/Non
                      </p>
                      <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>Posez votre question aux arcanes</p>
                    </div>
                    <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.5} />
                  </div>
                </button>
                <button onClick={() => navigate('/tarologie')} className="block w-full text-left group" data-testid="cta-tarologie">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm mb-0.5 transition-colors duration-300 group-hover:text-[#C5A059]" style={{ color: 'var(--pa-heading)' }}>
                        Tarologie & M&eacute;diumni&eacute; — 35 EUR
                      </p>
                      <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>Lecture compl&egrave;te et PDF personnalis&eacute;</p>
                    </div>
                    <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.5} />
                  </div>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      </div>
    </div>
  );
};

export default Quotidien;
