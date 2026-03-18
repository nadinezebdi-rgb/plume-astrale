import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Sun, Moon, Star, Sparkles, Heart, TrendingUp, ArrowRight, Coins, Eye, Flame, Check } from 'lucide-react';
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

const MILESTONES = [7, 14, 30, 60, 100];
const MILESTONE_BONUSES = { 7: 3, 14: 5, 30: 10, 60: 15, 100: 25 };

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

// Streak visual component
const StreakCard = ({ streak, onCheckin, loading }) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  if (!isAuthenticated) {
    return (
      <div className="rounded-2xl p-6 text-center mb-10" style={{ background: 'linear-gradient(135deg, rgba(197,160,89,0.08) 0%, rgba(197,160,89,0.03) 100%)', border: '1px solid rgba(197,160,89,0.2)' }} data-testid="streak-card-unauthenticated">
        <Flame className="w-8 h-8 mx-auto mb-3" style={{ color: '#C5A059' }} strokeWidth={1.5} />
        <h3 className="text-lg mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
          Streak quotidien
        </h3>
        <p className="text-sm mb-4" style={{ color: 'var(--pa-muted)' }}>
          Revenez chaque jour pour gagner des cr&eacute;dits et d&eacute;bloquer des bonus
        </p>
        <button onClick={() => navigate('/inscription')} className="text-xs uppercase tracking-widest px-6 py-2 rounded-full" style={{ border: '1px solid rgba(197,160,89,0.4)', color: '#C5A059', letterSpacing: '0.08em' }} data-testid="streak-register-btn">
          Cr&eacute;er un compte
        </button>
      </div>
    );
  }

  const count = streak?.streak_count || 0;
  const checkedToday = streak?.checked_in_today || false;
  const longest = streak?.longest_streak || 0;
  const totalCheckins = streak?.total_checkins || 0;
  const nextMilestone = streak?.next_milestone || {};

  // Progress to next milestone
  const progressMax = nextMilestone.days || 7;
  const progressPct = progressMax > 0 ? Math.min((count / progressMax) * 100, 100) : 0;

  return (
    <div className="rounded-2xl p-6 md:p-8 mb-10" style={{ background: 'linear-gradient(135deg, rgba(197,160,89,0.08) 0%, rgba(255,215,0,0.03) 100%)', border: '1px solid rgba(197,160,89,0.25)' }} data-testid="streak-card">

      {/* Header row */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-4">
          <div className="relative">
            <Flame className="w-10 h-10" style={{ color: count > 0 ? '#FF6B35' : '#C5A059', filter: count >= 7 ? 'drop-shadow(0 0 8px rgba(255,107,53,0.4))' : 'none' }} strokeWidth={1.5} />
            {count > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold" style={{ background: '#FF6B35', color: '#fff' }}>
                {count}
              </span>
            )}
          </div>
          <div>
            <h3 className="text-xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
              {count === 0 ? 'Commencez votre streak' : `${count} jour${count > 1 ? 's' : ''} cons\u00e9cutif${count > 1 ? 's' : ''}`}
            </h3>
            <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
              {count === 0
                ? 'Faites votre premier check-in pour d\u00e9marrer'
                : `Record : ${longest} jours \u00b7 ${totalCheckins} check-ins au total`
              }
            </p>
          </div>
        </div>

        {/* Check-in button */}
        {checkedToday ? (
          <div className="flex items-center gap-2 px-5 py-2.5 rounded-full" style={{ background: 'rgba(124,184,138,0.1)', border: '1px solid rgba(124,184,138,0.3)' }} data-testid="streak-checked-today">
            <Check className="w-4 h-4" style={{ color: '#7CB88A' }} strokeWidth={2} />
            <span className="text-xs uppercase tracking-widest" style={{ color: '#7CB88A', letterSpacing: '0.08em' }}>Check-in fait</span>
          </div>
        ) : (
          <button
            onClick={onCheckin}
            disabled={loading}
            className="flex items-center gap-2 px-6 py-2.5 rounded-full text-xs uppercase tracking-widest transition-all duration-500 hover:scale-105"
            style={{
              background: 'linear-gradient(135deg, #C5A059 0%, #D4AF37 100%)',
              color: '#120A28',
              letterSpacing: '0.08em',
              fontWeight: 600,
              boxShadow: '0 2px 12px rgba(197,160,89,0.3)',
            }}
            data-testid="streak-checkin-btn"
          >
            <Flame className="w-4 h-4" strokeWidth={2} />
            {loading ? 'Check-in...' : 'Check-in du jour'}
          </button>
        )}
      </div>

      {/* Progress to next milestone */}
      {nextMilestone.days && (
        <div className="mb-5">
          <div className="flex justify-between mb-1.5">
            <span className="text-[10px] uppercase tracking-wider" style={{ color: 'var(--pa-muted)', letterSpacing: '0.08em' }}>
              Prochain palier : {nextMilestone.days} jours
            </span>
            <span className="text-[10px]" style={{ color: '#C5A059' }}>
              +{nextMilestone.bonus} cr&eacute;dits bonus
            </span>
          </div>
          <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(197,160,89,0.1)' }}>
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{
                width: `${progressPct}%`,
                background: 'linear-gradient(90deg, #C5A059 0%, #FF6B35 100%)',
              }}
              data-testid="streak-progress-bar"
            />
          </div>
          <p className="text-[10px] mt-1.5 text-right" style={{ color: 'var(--pa-muted)' }}>
            {nextMilestone.remaining > 0 ? `Encore ${nextMilestone.remaining} jour${nextMilestone.remaining > 1 ? 's' : ''}` : 'Palier atteint !'}
          </p>
        </div>
      )}

      {/* Milestone timeline */}
      <div className="flex items-center justify-between">
        {MILESTONES.map((m, i) => {
          const reached = count >= m;
          const isCurrent = nextMilestone.days === m;
          return (
            <div key={m} className="flex flex-col items-center gap-1">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold transition-all"
                style={{
                  background: reached ? 'linear-gradient(135deg, #C5A059 0%, #FF6B35 100%)' : isCurrent ? 'rgba(197,160,89,0.15)' : 'rgba(255,255,255,0.03)',
                  color: reached ? '#120A28' : isCurrent ? '#C5A059' : 'var(--pa-muted)',
                  border: reached ? 'none' : `1px solid ${isCurrent ? 'rgba(197,160,89,0.4)' : 'rgba(197,160,89,0.1)'}`,
                  boxShadow: reached ? '0 0 8px rgba(197,160,89,0.3)' : 'none',
                }}
                data-testid={`milestone-${m}`}
              >
                {reached ? <Check className="w-3.5 h-3.5" strokeWidth={2.5} /> : m}
              </div>
              <span className="text-[9px]" style={{ color: reached ? '#C5A059' : 'var(--pa-muted)' }}>
                +{MILESTONE_BONUSES[m]}cr
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Streak reward popup
const StreakRewardPopup = ({ result, onClose }) => {
  if (!result || result.already_checked_in) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4" style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)' }} onClick={onClose} data-testid="streak-reward-popup">
      <div className="rounded-2xl p-8 max-w-sm w-full text-center" style={{ background: '#120A28', border: '1px solid rgba(197,160,89,0.3)' }} onClick={e => e.stopPropagation()}>
        <div className="relative mb-4">
          <Flame className="w-16 h-16 mx-auto" style={{ color: '#FF6B35', filter: 'drop-shadow(0 0 20px rgba(255,107,53,0.4))' }} strokeWidth={1.5} />
          <span className="absolute top-0 right-1/2 translate-x-1/2 -translate-y-1 text-2xl font-bold" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#FF6B35' }}>
            {result.streak_count}
          </span>
        </div>

        <h2 className="text-2xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
          {result.milestone_name ? result.milestone_name + ' !' : `Jour ${result.streak_count}`}
        </h2>

        <div className="flex items-center justify-center gap-2 mb-3">
          <Coins className="w-5 h-5" style={{ color: '#C5A059' }} strokeWidth={1.5} />
          <span className="text-lg" style={{ color: '#C5A059', fontWeight: 500 }}>
            +{result.credits_earned} cr&eacute;dit{result.credits_earned > 1 ? 's' : ''}
          </span>
        </div>

        {result.milestone_bonus > 0 && (
          <p className="text-sm mb-3 px-3 py-1.5 rounded-full inline-block" style={{ background: 'rgba(255,107,53,0.1)', border: '1px solid rgba(255,107,53,0.2)', color: '#FF6B35' }}>
            Bonus palier : +{result.milestone_bonus} cr&eacute;dits
          </p>
        )}

        <p className="text-xs mb-5" style={{ color: 'var(--pa-muted)' }}>
          {result.next_milestone?.remaining > 0
            ? `Prochain palier dans ${result.next_milestone.remaining} jour${result.next_milestone.remaining > 1 ? 's' : ''} (+${result.next_milestone.bonus} bonus)`
            : 'Continuez votre streak !'
          }
        </p>

        <button
          onClick={onClose}
          className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full transition-all"
          style={{ border: '1px solid rgba(197,160,89,0.4)', color: '#C5A059', letterSpacing: '0.08em' }}
          data-testid="streak-close-popup"
        >
          Continuer
        </button>
      </div>
    </div>
  );
};

export default function Cercle() {
  const navigate = useNavigate();
  const { isAuthenticated, creditBalance, user, token, refreshBalance } = useAuth();
  const [dailyCard, setDailyCard] = useState(null);
  const [selectedSign, setSelectedSign] = useState(null);
  const [streak, setStreak] = useState(null);
  const [checkinLoading, setCheckinLoading] = useState(false);
  const [checkinResult, setCheckinResult] = useState(null);

  // Fetch daily card + streak status
  useEffect(() => {
    axios.get(`${API_URL}/api/tarot/jour`).then(r => {
      if (r.data) setDailyCard(r.data);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!isAuthenticated || !token) return;
    axios.get(`${API_URL}/api/streak/status`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => setStreak(r.data))
      .catch(() => {});
  }, [isAuthenticated, token]);

  // Determine user's zodiac from birth_date
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

  const handleCheckin = async () => {
    setCheckinLoading(true);
    try {
      const res = await axios.post(`${API_URL}/api/streak/checkin`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setCheckinResult(res.data);
      setStreak(prev => ({
        ...prev,
        streak_count: res.data.streak_count,
        checked_in_today: true,
        longest_streak: res.data.longest_streak,
        total_checkins: res.data.total_checkins,
        next_milestone: res.data.next_milestone,
      }));
      await refreshBalance();
    } catch (err) {
      console.error('Checkin error:', err);
    } finally {
      setCheckinLoading(false);
    }
  };

  const today = new Date();
  const dateStr = today.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });

  return (
    <div className="min-h-screen pt-24 pb-16 px-4" data-testid="cercle-page">
      <SEO path="/cercle" />
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="text-center mb-10">
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

        {/* Streak Card */}
        <StreakCard streak={streak} onCheckin={handleCheckin} loading={checkinLoading} />

        {/* Streak reward popup */}
        <StreakRewardPopup
          result={checkinResult}
          onClose={() => setCheckinResult(null)}
        />

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
