import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Sun, Moon, Star, Sparkles, Heart, TrendingUp, Calendar, ArrowRight, Coins, Users, Eye } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ZODIAC_SIGNS = [
  { sign: 'belier', label: 'B\u00e9lier', dates: '21 mar \u2013 19 avr', symbol: '\u2648' },
  { sign: 'taureau', label: 'Taureau', dates: '20 avr \u2013 20 mai', symbol: '\u2649' },
  { sign: 'gemeaux', label: 'G\u00e9meaux', dates: '21 mai \u2013 20 juin', symbol: '\u264a' },
  { sign: 'cancer', label: 'Cancer', dates: '21 juin \u2013 22 jul', symbol: '\u264b' },
  { sign: 'lion', label: 'Lion', dates: '23 jul \u2013 22 ao\u00fb', symbol: '\u264c' },
  { sign: 'vierge', label: 'Vierge', dates: '23 ao\u00fb \u2013 22 sep', symbol: '\u264d' },
  { sign: 'balance', label: 'Balance', dates: '23 sep \u2013 22 oct', symbol: '\u264e' },
  { sign: 'scorpion', label: 'Scorpion', dates: '23 oct \u2013 21 nov', symbol: '\u264f' },
  { sign: 'sagittaire', label: 'Sagittaire', dates: '22 nov \u2013 21 d\u00e9c', symbol: '\u2650' },
  { sign: 'capricorne', label: 'Capricorne', dates: '22 d\u00e9c \u2013 19 jan', symbol: '\u2651' },
  { sign: 'verseau', label: 'Verseau', dates: '20 jan \u2013 18 f\u00e9v', symbol: '\u2652' },
  { sign: 'poissons', label: 'Poissons', dates: '19 f\u00e9v \u2013 20 mar', symbol: '\u2653' },
];

const DAILY_INSIGHTS = [
  {
    title: '\u00c9nergie du jour',
    icon: Sun,
    color: '#C5A059',
    content: 'Aujourd\u2019hui, la Lune transite en aspect harmonieux avec V\u00e9nus. C\u2019est une journ\u00e9e favorable aux connections \u00e9motionnelles, \u00e0 la cr\u00e9ativit\u00e9 et aux rencontres. Laissez votre intuition guider vos choix.',
  },
  {
    title: 'Nombre du jour',
    icon: Star,
    color: '#A78BFA',
    content: 'Le nombre 7 r\u00e8gne aujourd\u2019hui \u2014 journ\u00e9e d\u2019introspection et de r\u00e9flexion profonde. Prenez du recul sur vos projets. La solitude choisie est source de r\u00e9v\u00e9lations.',
  },
  {
    title: 'Arcane du jour',
    icon: Eye,
    color: '#C97878',
    content: 'L\u2019\u00c9toile (XVII) brille pour vous aujourd\u2019hui. Symbole d\u2019espoir et de renouveau, cette carte vous invite \u00e0 faire confiance au processus. Apr\u00e8s la temp\u00eate vient la lumi\u00e8re.',
  },
];

export default function Cercle() {
  const navigate = useNavigate();
  const { isAuthenticated, creditBalance, user } = useAuth();
  const [dailyCard, setDailyCard] = useState(null);
  const [selectedSign, setSelectedSign] = useState(null);

  useEffect(() => {
    // Fetch daily tarot card
    axios.get(`${API_URL}/api/tarot/jour`).then(r => {
      if (r.data) setDailyCard(r.data);
    }).catch(() => {});
  }, []);

  // Determine user's zodiac from birth_date if available
  useEffect(() => {
    if (user?.birth_date) {
      const parts = user.birth_date.split('-');
      if (parts.length === 3) {
        const m = parseInt(parts[1]);
        const d = parseInt(parts[2]);
        const idx = getZodiacIndex(m, d);
        if (idx >= 0) setSelectedSign(ZODIAC_SIGNS[idx].sign);
      }
    }
  }, [user]);

  const getZodiacIndex = (m, d) => {
    const ranges = [
      [3,21,4,19],[4,20,5,20],[5,21,6,20],[6,21,7,22],
      [7,23,8,22],[8,23,9,22],[9,23,10,22],[10,23,11,21],
      [11,22,12,21],[12,22,1,19],[1,20,2,18],[2,19,3,20],
    ];
    for (let i = 0; i < ranges.length; i++) {
      const [m1,d1,m2,d2] = ranges[i];
      if ((m === m1 && d >= d1) || (m === m2 && d <= d2)) return i;
    }
    return -1;
  };

  const today = new Date();
  const dateStr = today.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });

  return (
    <div className="min-h-screen pt-24 pb-16 px-4" data-testid="cercle-page">
      <SEO path="/cercle" />
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="text-center mb-12">
          <p className="text-xs uppercase tracking-widest mb-3" style={{ color: 'var(--pa-accent)', letterSpacing: '0.15em' }}>
            Votre espace quotidien
          </p>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 300 }}>
            Le Cercle
          </h1>
          <p className="text-sm capitalize" style={{ color: 'var(--pa-muted)' }}>
            {dateStr}
          </p>
        </div>

        {/* Daily insights */}
        <div className="grid gap-4 md:grid-cols-3 mb-12">
          {DAILY_INSIGHTS.map((insight, i) => {
            const Icon = insight.icon;
            return (
              <div key={i} className="rounded-2xl p-5 transition-all duration-300 hover:scale-[1.02]"
                style={{ background: 'rgba(255,255,255,0.02)', border: `1px solid ${insight.color}20`, backdropFilter: 'blur(8px)' }}
                data-testid={`insight-${i}`}
              >
                <div className="flex items-center gap-2 mb-3">
                  <Icon className="w-4 h-4" style={{ color: insight.color }} strokeWidth={1.5} />
                  <h3 className="text-xs uppercase tracking-widest" style={{ color: insight.color, letterSpacing: '0.1em' }}>
                    {insight.title}
                  </h3>
                </div>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>
                  {insight.content}
                </p>
              </div>
            );
          })}
        </div>

        {/* Carte du jour */}
        {dailyCard && (
          <div className="rounded-2xl p-6 md:p-8 mb-12" style={{ background: 'rgba(197,160,89,0.04)', border: '1px solid rgba(197,160,89,0.12)' }} data-testid="daily-card">
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="flex-shrink-0">
                {dailyCard.carte?.image && (
                  <img
                    src={`${API_URL}${dailyCard.carte.image}`}
                    alt={dailyCard.carte.nom || 'Carte du jour'}
                    className="w-24 h-36 object-cover rounded-lg"
                    style={{ border: '1px solid rgba(197,160,89,0.2)', filter: 'drop-shadow(0 0 15px rgba(197,160,89,0.1))' }}
                  />
                )}
              </div>
              <div className="text-center md:text-left flex-1">
                <p className="text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
                  Carte du jour
                </p>
                <h2 className="text-2xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                  {dailyCard.carte?.nom || dailyCard.carte?.name}
                </h2>
                <p className="text-xs mb-3" style={{ color: '#C5A059' }}>
                  {dailyCard.carte?.energie || dailyCard.carte?.archetype}
                </p>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>
                  {dailyCard.message_jour || dailyCard.interpretation}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Zodiac selector */}
        <div className="mb-12">
          <h2 className="text-xl text-center mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
            Votre signe astrologique
          </h2>
          <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-12 gap-2 mb-6">
            {ZODIAC_SIGNS.map(z => (
              <button
                key={z.sign}
                onClick={() => setSelectedSign(z.sign)}
                className="flex flex-col items-center gap-1 p-2 rounded-xl transition-all duration-300"
                style={{
                  background: selectedSign === z.sign ? 'rgba(197,160,89,0.12)' : 'rgba(255,255,255,0.02)',
                  border: selectedSign === z.sign ? '1px solid rgba(197,160,89,0.4)' : '1px solid rgba(197,160,89,0.08)',
                }}
                data-testid={`zodiac-${z.sign}`}
              >
                <span className="text-lg">{z.symbol}</span>
                <span className="text-[9px] uppercase tracking-wider" style={{ color: selectedSign === z.sign ? '#C5A059' : 'var(--pa-muted)' }}>
                  {z.label}
                </span>
              </button>
            ))}
          </div>
          {selectedSign && (
            <div className="text-center">
              <p className="text-sm mb-3" style={{ color: 'var(--pa-body)' }}>
                Vous &ecirc;tes <span style={{ color: '#C5A059', fontWeight: 500 }}>{ZODIAC_SIGNS.find(z => z.sign === selectedSign)?.label}</span>
              </p>
              <Link
                to="/formulaire"
                className="inline-flex items-center gap-2 text-xs uppercase tracking-widest px-5 py-2 rounded-full transition-all duration-300 hover:bg-[#C5A059]/10"
                style={{ border: '1px solid rgba(197,160,89,0.3)', color: '#C5A059', letterSpacing: '0.08em' }}
                data-testid="full-chart-cta"
              >
                Voir mon th&egrave;me astral complet <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
          )}
        </div>

        {/* Vos services */}
        <div className="mb-12">
          <h2 className="text-xl text-center mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
            Vos exp&eacute;riences
          </h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {[
              { to: '/tarot-oui-non', icon: Eye, label: 'Tarot Oui / Non', desc: 'Posez une question, recevez une r\u00e9ponse claire', cost: '1er gratuit, puis 2 cr', color: '#C97878' },
              { to: '/tirage-tarot', icon: Sparkles, label: 'Lecture Tarot approfondie', desc: 'Tirage Marseille ou Croix Celtique', cost: '10 cr\u00e9dits', color: '#A78BFA' },
              { to: '/numerologie', icon: Star, label: 'Num\u00e9rologie', desc: 'Chemin de vie et nombres sacr\u00e9s', cost: '10 cr\u00e9dits', color: '#7CB88A' },
              { to: '/compatibilite-amoureuse', icon: Heart, label: 'Compatibilit\u00e9 Astrale', desc: 'Rapport PDF de compatibilit\u00e9 amoureuse', cost: '10 cr\u00e9dits', color: '#C97878' },
              { to: '/tarologie', icon: Moon, label: 'Tarologie & M\u00e9diumni\u00e9', desc: 'Tirage en croix avec lecture profonde', cost: '10 cr\u00e9dits', color: '#C5A059' },
              { to: '/premium/experience', icon: TrendingUp, label: 'Cartographie Premium', desc: '5 \u00e9tapes initiatiques + PDF complet', cost: '60 cr\u00e9dits', color: '#FFD700' },
            ].map(s => {
              const Icon = s.icon;
              return (
                <Link
                  key={s.to}
                  to={s.to}
                  className="flex items-start gap-4 p-4 rounded-xl transition-all duration-300 group hover:scale-[1.01]"
                  style={{ background: 'rgba(255,255,255,0.02)', border: `1px solid ${s.color}15` }}
                  data-testid={`service-link-${s.to.replace(/\//g, '')}`}
                >
                  <Icon className="w-5 h-5 mt-0.5 flex-shrink-0 group-hover:scale-110 transition-transform" style={{ color: s.color }} strokeWidth={1.5} />
                  <div>
                    <p className="text-sm mb-0.5 group-hover:text-[#C5A059] transition-colors" style={{ color: 'var(--pa-heading)' }}>{s.label}</p>
                    <p className="text-xs mb-1" style={{ color: 'var(--pa-muted)' }}>{s.desc}</p>
                    <span className="text-[10px] uppercase tracking-wider" style={{ color: s.color, letterSpacing: '0.08em' }}>{s.cost}</span>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Credits footer */}
        {isAuthenticated ? (
          <div className="text-center p-5 rounded-2xl" style={{ background: 'rgba(197,160,89,0.05)', border: '1px solid rgba(197,160,89,0.12)' }} data-testid="cercle-credits">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Coins className="w-4 h-4" style={{ color: '#C5A059' }} strokeWidth={1.5} />
              <span className="text-sm" style={{ color: '#C5A059', fontWeight: 500 }}>{creditBalance} cr&eacute;dits</span>
            </div>
            <Link to="/acheter-credits" className="text-xs transition-colors hover:text-[#C5A059]" style={{ color: 'var(--pa-muted)' }}>
              Acheter des cr&eacute;dits &rarr;
            </Link>
          </div>
        ) : (
          <div className="text-center p-5 rounded-2xl" style={{ background: 'rgba(197,160,89,0.05)', border: '1px solid rgba(197,160,89,0.12)' }} data-testid="cercle-join">
            <p className="text-sm mb-3" style={{ color: 'var(--pa-body)' }}>
              Rejoignez le Cercle &mdash; <span style={{ color: '#C5A059' }}>20 cr&eacute;dits offerts</span> &agrave; l'inscription
            </p>
            <div className="flex gap-3 justify-center">
              <Link to="/connexion" className="text-xs uppercase tracking-widest px-5 py-2 rounded-full" style={{ border: '1px solid rgba(197,160,89,0.4)', color: '#C5A059', letterSpacing: '0.08em' }} data-testid="cercle-login-btn">Se connecter</Link>
              <Link to="/inscription" className="text-xs uppercase tracking-widest px-5 py-2 rounded-full" style={{ border: '1px solid rgba(197,160,89,0.4)', color: '#C5A059', background: 'rgba(197,160,89,0.08)', letterSpacing: '0.08em' }} data-testid="cercle-register-btn">Cr&eacute;er un compte</Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
