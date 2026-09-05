import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import SEO from '@/components/SEO';
import SEOServiceEnrich from '@/components/SEOServiceEnrich';
import {
  Sun, Cloud, Moon, Wind, Flame, Heart, CloudRain,
  Sparkles, Target, BookHeart, Send, Loader2, Flame as FlameIcon,
  Stars, Lock, ChevronDown, ChevronUp, RefreshCw,
} from 'lucide-react';
import SEO from '@/components/SEO';
import { useAuth } from '@/context/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL;
const USER_ID_KEY = 'pa_ritual_user_id';

const MOOD_ICONS = {
  Sun, Cloud, Moon, Wind, Flame, Heart, CloudRain,
};

const SCORE_LABELS = {
  energy:     { label: 'Energie',    color: '#F47F92', icon: Flame,  desc: 'Ta vitalite du jour' },
  confidence: { label: 'Confiance',  color: '#A78BFA', icon: Stars,  desc: 'Ton ancrage interieur' },
  discipline: { label: 'Discipline', color: '#E8C766', icon: Target, desc: 'Ta tenue d\'engagement' },
  intuition:  { label: 'Intuition',  color: '#C4B5FD', icon: Sparkles, desc: 'Ta lecture subtile' },
};

/* ═══════════════════════════════════════════════════════════
   GAUGE — score animé circulaire
═══════════════════════════════════════════════════════════ */
const ScoreGauge = ({ score, color, label, Icon, desc }) => {
  const [animated, setAnimated] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setAnimated(score), 200);
    return () => clearTimeout(t);
  }, [score]);

  const radius = 56;
  const stroke = 6;
  const norm = radius - stroke;
  const circ = norm * 2 * Math.PI;
  const offset = circ - (animated / 100) * circ;

  return (
    <div className="flex flex-col items-center" data-testid={`gauge-${label.toLowerCase()}`}>
      <div className="relative" style={{ width: radius * 2, height: radius * 2 }}>
        <svg width={radius * 2} height={radius * 2} className="-rotate-90">
          <circle cx={radius} cy={radius} r={norm} fill="none"
            stroke="rgba(167,139,250,0.08)" strokeWidth={stroke} />
          <circle cx={radius} cy={radius} r={norm} fill="none"
            stroke={color} strokeWidth={stroke} strokeLinecap="round"
            strokeDasharray={`${circ} ${circ}`}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 1.4s cubic-bezier(.4,0,.2,1)', filter: `drop-shadow(0 0 6px ${color}80)` }} />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <Icon style={{ width: 18, height: 18, color, opacity: 0.85 }} strokeWidth={1.4} />
          <span className="font-display text-2xl mt-1" style={{ color, fontWeight: 400, lineHeight: 1 }}>
            {animated}
          </span>
        </div>
      </div>
      <p className="text-[11px] uppercase tracking-widest mt-2.5" style={{ color: 'var(--pa-heading)', letterSpacing: '0.12em' }}>
        {label}
      </p>
      <p className="text-[10px] mt-0.5 opacity-60" style={{ color: 'var(--pa-muted)' }}>
        {desc}
      </p>
    </div>
  );
};

/* ═══════════════════════════════════════════════════════════
   MOOD CHECKIN — sélection 1-tap
═══════════════════════════════════════════════════════════ */
const MoodCheckin = ({ moods, selected, onSelect, locked }) => (
  <div className="grid grid-cols-4 sm:grid-cols-7 gap-3 sm:gap-4">
    {moods.map(m => {
      const Icon = MOOD_ICONS[m.icon] || Heart;
      const isActive = selected === m.id;
      return (
        <button
          key={m.id}
          onClick={() => !locked && onSelect(m.id)}
          disabled={locked && !isActive}
          className={`group flex flex-col items-center gap-2 transition-all duration-300 ${
            locked && !isActive ? 'opacity-30' : 'hover:scale-110'
          } ${isActive ? 'scale-110' : ''}`}
          data-testid={`mood-${m.id}`}
        >
          <div className="relative w-12 h-12 sm:w-14 sm:h-14 rounded-full flex items-center justify-center transition-all"
            style={{
              background: isActive
                ? `radial-gradient(circle at 30% 30%, ${m.color}66 0%, ${m.color}20 60%, transparent 100%)`
                : `radial-gradient(circle at 30% 30%, ${m.color}22 0%, ${m.color}08 60%, transparent 100%)`,
              border: isActive ? `1.5px solid ${m.color}` : `1px solid ${m.color}30`,
              boxShadow: isActive ? `0 0 24px ${m.color}55` : `0 0 8px ${m.color}15`,
            }}>
            <Icon style={{ width: 20, height: 20, color: m.color }} strokeWidth={1.4} />
          </div>
          <span className="text-[10px] uppercase tracking-widest"
            style={{
              color: isActive ? m.color : 'var(--pa-muted)',
              letterSpacing: '0.1em',
              fontWeight: isActive ? 600 : 400,
            }}>
            {m.label}
          </span>
        </button>
      );
    })}
  </div>
);

/* ═══════════════════════════════════════════════════════════
   STREAK FLAME
═══════════════════════════════════════════════════════════ */
const StreakFlame = ({ current, longest }) => (
  <div className="flex items-center gap-2 pa-glass rounded-full px-4 py-2" data-testid="streak-badge">
    <FlameIcon style={{
      width: 18, height: 18,
      color: current > 0 ? '#FF9F66' : 'rgba(255,159,102,0.3)',
      filter: current > 2 ? 'drop-shadow(0 0 6px #FF9F66)' : 'none',
    }} strokeWidth={1.5} />
    <div className="leading-tight">
      <span className="text-sm font-display" style={{ color: 'var(--pa-heading)', fontWeight: 500 }}>
        {current}
      </span>
      <span className="text-[10px] uppercase tracking-widest ml-1" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>
        jour{current > 1 ? 's' : ''}
      </span>
    </div>
    {longest > current && (
      <span className="text-[10px] opacity-50 ml-1" style={{ color: 'var(--pa-muted)' }}>
        / max {longest}
      </span>
    )}
  </div>
);

/* ═══════════════════════════════════════════════════════════
   PAGE
═══════════════════════════════════════════════════════════ */
const MonRituel = () => {
  const { user, isAuthenticated, authHeader } = useAuth();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [moods, setMoods] = useState([]);
  const [selectedMood, setSelectedMood] = useState(null);
  const [intention, setIntention] = useState('');
  const [intentionSaved, setIntentionSaved] = useState(false);
  const [submittingMood, setSubmittingMood] = useState(false);

  // Journal
  const [journalText, setJournalText] = useState('');
  const [journalLoading, setJournalLoading] = useState(false);
  const [journalResponse, setJournalResponse] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState([]);

  // Stable user_id (anonyme OU auth)
  const userId = useMemo(() => {
    if (isAuthenticated && user?.id) return user.id;
    let sid = null;
    try { sid = localStorage.getItem(USER_ID_KEY); } catch (e) { /* ignore */ }
    if (!sid) {
      sid = `anon-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      try { localStorage.setItem(USER_ID_KEY, sid); } catch (e) { /* ignore */ }
    }
    return sid;
  }, [isAuthenticated, user]);

  // Get birth data from localStorage formData
  const getBirthParams = useCallback(() => {
    try {
      const raw = localStorage.getItem('pa_formData');
      if (!raw) return {};
      const f = JSON.parse(raw);
      const params = {};
      if (f.prenom) params.name = f.prenom;
      if (f.dateNaissance) {
        const d = new Date(f.dateNaissance);
        if (!isNaN(d.getTime())) {
          params.day = d.getDate();
          params.month = d.getMonth() + 1;
          params.year = d.getFullYear();
        }
      }
      if (f.heureNaissance) {
        const [h, m] = f.heureNaissance.split(':');
        params.hour = parseInt(h, 10);
        params.minute = parseInt(m, 10);
      }
      if (f.latitude) params.lat = parseFloat(f.latitude);
      if (f.longitude) params.lon = parseFloat(f.longitude);
      return params;
    } catch (e) { return {}; }
  }, []);

  // Load today's ritual
  const loadToday = useCallback(async () => {
    setLoading(true);
    try {
      const params = { ...getBirthParams() };
      const res = await axios.get(`${API}/api/ritual/today`, {
        params,
        headers: authHeader(),
        timeout: 30000,
      });
      setData(res.data);
      if (res.data.checkin) {
        setSelectedMood(res.data.checkin.mood);
        if (res.data.checkin.intention) {
          setIntention(res.data.checkin.intention);
          setIntentionSaved(true);
        }
      }
    } catch (e) {
      console.error('Failed to load ritual', e);
    }
    setLoading(false);
  }, [getBirthParams, authHeader]);

  // Load moods + ritual on mount
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await axios.get(`${API}/api/ritual/moods`, { timeout: 10000 });
        if (mounted) setMoods(res.data.moods || []);
      } catch (e) { /* ignore */ }
    })();
    loadToday();
    return () => { mounted = false; };
  }, [loadToday]);

  // Submit mood
  const submitMood = async (moodId) => {
    if (submittingMood || data?.checkin?.mood === moodId) return;
    setSubmittingMood(true);
    setSelectedMood(moodId);
    try {
      const res = await axios.post(`${API}/api/ritual/checkin`, {
        mood: moodId, intention: intention,
      }, { headers: authHeader() });
      if (res.data.success) {
        // Reload data to get updated scores modulated by mood
        await loadToday();
      }
    } catch (e) {
      console.error('Mood submit failed', e);
    }
    setSubmittingMood(false);
  };

  // Save intention
  const saveIntention = async () => {
    if (!selectedMood || !intention.trim()) return;
    try {
      await axios.post(`${API}/api/ritual/checkin`, {
        mood: selectedMood, intention: intention.trim(),
      }, { headers: authHeader() });
      setIntentionSaved(true);
      setTimeout(() => setIntentionSaved(false), 2500);
    } catch (e) { /* ignore */ }
  };

  // Submit journal
  const submitJournal = async () => {
    if (!journalText.trim() || journalLoading) return;
    setJournalLoading(true);
    setJournalResponse(null);
    try {
      const birthParams = getBirthParams();
      const birth_data = (birthParams.day && birthParams.month) ? {
        day: birthParams.day, month: birthParams.month, year: birthParams.year,
      } : null;
      const res = await axios.post(`${API}/api/journal/entry`, {
        entry: journalText.trim(),
        mood: selectedMood,
        birth_data,
      }, { headers: authHeader(), timeout: 60000 });
      if (res.data.success) {
        setJournalResponse(res.data.response);
        setJournalText('');
        // Refresh history if visible
        if (showHistory) loadHistory();
      } else {
        setJournalResponse(res.data.message || "Une perturbation cosmique. Reessaie.");
      }
    } catch (e) {
      setJournalResponse("Le journal est momentanément silencieux. Vérifie ta connexion et réessaie.");
    }
    setJournalLoading(false);
  };

  // Load journal history
  const loadHistory = async () => {
    try {
      const res = await axios.get(`${API}/api/journal/history`, {
        params: { limit: 10 },
        headers: authHeader(),
      });
      setHistory(res.data.entries || []);
    } catch (e) { /* ignore */ }
  };

  useEffect(() => {
    if (showHistory) loadHistory();
  }, [showHistory]); // eslint-disable-line

  const hour = new Date().getHours();
  const isEvening = hour >= 18;

  const greeting = useMemo(() => {
    if (hour < 6)  return "Cette nuit profonde";
    if (hour < 12) return "Bon matin";
    if (hour < 18) return "Bel apres-midi";
    return "Douce soiree";
  }, [hour]);

  const firstName = user?.email?.split('@')[0]?.replace(/\b\w/g, c => c.toUpperCase()) || 'Voyageur';

  if (loading || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <Loader2 className="animate-spin" style={{ width: 28, height: 28, color: 'var(--pa-lavender-bright)' }} />
      </div>
    );
  }

  const todayFr = new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' });

  return (
    <>
      <SEO title="Mon Rituel — Plume Astrale" description="Ton rituel quotidien : humeur, scores cosmiques, journal personnalisé. Ton compagnon emotionnel." />

      <div className="min-h-screen pt-24 pb-16 px-4 sm:px-6">
        <div className="max-w-3xl mx-auto">

          {/* ═══ HEADER ═══ */}
          <header className="text-center mb-10 animate-fade-up">
            <p className="text-[10px] uppercase tracking-[0.4em] mb-2" style={{ color: 'var(--pa-lavender-bright)' }}>
              {todayFr}
            </p>
            <h1 className="font-display mb-2" style={{
              fontSize: 'clamp(28px, 5vw, 44px)',
              color: 'var(--pa-heading)',
              fontWeight: 300,
              lineHeight: 1.1,
            }}>
              {greeting},{' '}
              <span className="italic pa-shimmer-gold">{firstName}</span>.
            </h1>
            <p className="text-sm mb-5" style={{ color: 'var(--pa-muted)' }}>
              {data.moon_phase} &mdash; {data.moon_theme}
            </p>
            <div className="flex justify-center">
              <StreakFlame current={data.streak.current} longest={data.streak.longest} />
            </div>
          </header>

          {/* ═══ MOOD CHECK-IN ═══ */}
          <section className="pa-glass rounded-3xl p-6 sm:p-8 mb-8 animate-fade-up" style={{ animationDelay: '100ms' }}>
            <div className="flex items-center justify-between mb-5">
              <div>
                <p className="text-[10px] uppercase tracking-[0.3em] mb-1" style={{ color: 'var(--pa-accent-bright)' }}>
                  Check-in du matin
                </p>
                <h2 className="text-xl font-display" style={{ color: 'var(--pa-heading)', fontWeight: 400 }}>
                  Comment te sens-tu ?
                </h2>
              </div>
              {data.checkin && (
                <span className="text-[10px] uppercase tracking-widest pa-glass-gold px-3 py-1 rounded-full" style={{ color: 'var(--pa-accent)' }}>
                  Pose
                </span>
              )}
            </div>
            <MoodCheckin
              moods={moods}
              selected={selectedMood}
              onSelect={submitMood}
              locked={false}
            />
          </section>

          {/* ═══ SCORES COSMIQUES ═══ */}
          <section className="pa-glass rounded-3xl p-6 sm:p-8 mb-8 animate-fade-up" style={{ animationDelay: '200ms' }}>
            <div className="text-center mb-6">
              <p className="text-[10px] uppercase tracking-[0.3em] mb-1" style={{ color: 'var(--pa-lavender-bright)' }}>
                Tes scores cosmiques
              </p>
              <h2 className="text-xl font-display" style={{ color: 'var(--pa-heading)', fontWeight: 400 }}>
                Ton ciel <span className="italic pa-shimmer-lavender">interieur</span> du jour
              </h2>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
              {Object.entries(data.scores).map(([k, v]) => {
                const cfg = SCORE_LABELS[k];
                if (!cfg) return null;
                return (
                  <ScoreGauge
                    key={k}
                    score={v}
                    color={cfg.color}
                    label={cfg.label}
                    Icon={cfg.icon}
                    desc={cfg.desc}
                  />
                );
              })}
            </div>
          </section>

          {/* ═══ DAILY INSIGHT ═══ */}
          <section className="pa-glass-gold rounded-3xl p-6 sm:p-8 mb-8 relative overflow-hidden animate-fade-up" style={{ animationDelay: '300ms' }}>
            <div className="absolute -top-12 -right-12 w-40 h-40 rounded-full"
              style={{ background: 'radial-gradient(circle, rgba(212,175,55,0.20), transparent 70%)', filter: 'blur(30px)' }} />
            <div className="relative">
              <p className="text-[10px] uppercase tracking-[0.3em] mb-3 flex items-center gap-2" style={{ color: 'var(--pa-accent-bright)' }}>
                <Sparkles style={{ width: 12, height: 12 }} /> Ton message du jour
              </p>
              <p className="font-display italic leading-relaxed"
                style={{
                  fontSize: 'clamp(15px, 1.6vw, 18px)',
                  color: 'var(--pa-heading)',
                  fontWeight: 300,
                  lineHeight: 1.7,
                }}
                data-testid="daily-insight">
                {data.insight}
              </p>
            </div>
          </section>

          {/* ═══ INTENTION ═══ */}
          {selectedMood && (
            <section className="pa-glass rounded-3xl p-6 sm:p-8 mb-8 animate-fade-up" style={{ animationDelay: '400ms' }}>
              <p className="text-[10px] uppercase tracking-[0.3em] mb-3 flex items-center gap-2" style={{ color: 'var(--pa-lavender-bright)' }}>
                <Target style={{ width: 12, height: 12 }} /> Ton intention pour aujourd&#39;hui
              </p>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={intention}
                  onChange={e => setIntention(e.target.value)}
                  placeholder="Que veux-tu honorer aujourd'hui ?"
                  className="flex-1 bg-transparent border-b py-2 px-1 text-sm focus:outline-none transition-colors"
                  style={{ borderColor: 'rgba(167,139,250,0.25)', color: 'var(--pa-heading)' }}
                  onFocus={e => e.currentTarget.style.borderColor = 'rgba(167,139,250,0.6)'}
                  onBlur={e => e.currentTarget.style.borderColor = 'rgba(167,139,250,0.25)'}
                  maxLength={120}
                  data-testid="intention-input"
                />
                <button
                  onClick={saveIntention}
                  disabled={!intention.trim()}
                  className="text-[10px] uppercase tracking-widest px-3 py-1 rounded-full transition-all"
                  style={{
                    border: '1px solid rgba(167,139,250,0.4)',
                    color: intentionSaved ? 'var(--pa-accent-bright)' : 'var(--pa-lavender-bright)',
                    background: intentionSaved ? 'rgba(212,175,55,0.10)' : 'transparent',
                    letterSpacing: '0.1em',
                    opacity: intention.trim() ? 1 : 0.4,
                  }}
                  data-testid="save-intention"
                >
                  {intentionSaved ? 'Posee' : 'Poser'}
                </button>
              </div>
            </section>
          )}

          {/* ═══ JOURNAL INTIME ═══ */}
          <section className="pa-glass rounded-3xl p-6 sm:p-8 mb-8 animate-fade-up" style={{ animationDelay: '500ms' }}>
            <div className="mb-4">
              <p className="text-[10px] uppercase tracking-[0.3em] mb-1 flex items-center gap-2" style={{ color: 'var(--pa-lavender-bright)' }}>
                <BookHeart style={{ width: 12, height: 12 }} /> Journal avec Plume
              </p>
              <h2 className="text-xl font-display" style={{ color: 'var(--pa-heading)', fontWeight: 400 }}>
                Confie-lui ce qui te traverse
              </h2>
              <p className="text-xs mt-1" style={{ color: 'var(--pa-muted)' }}>
                Ecris librement. Plume t&#39;ecoute, te reflete, t&#39;eclaire.
              </p>
            </div>

            <textarea
              value={journalText}
              onChange={e => setJournalText(e.target.value)}
              placeholder="Aujourd'hui, je ressens..."
              rows={5}
              maxLength={4000}
              className="w-full p-4 rounded-xl resize-none focus:outline-none text-sm leading-relaxed transition-colors"
              style={{
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(167,139,250,0.15)',
                color: 'var(--pa-heading)',
                fontFamily: 'inherit',
              }}
              onFocus={e => e.currentTarget.style.borderColor = 'rgba(167,139,250,0.4)'}
              onBlur={e => e.currentTarget.style.borderColor = 'rgba(167,139,250,0.15)'}
              data-testid="journal-input"
            />
            <div className="flex justify-between items-center mt-3">
              <span className="text-[10px] opacity-50" style={{ color: 'var(--pa-muted)' }}>
                {journalText.length} / 4000
              </span>
              <button
                onClick={submitJournal}
                disabled={!journalText.trim() || journalLoading || journalText.length < 5}
                className="pa-btn-ghost"
                style={{ padding: '10px 22px', fontSize: 11 }}
                data-testid="journal-submit"
              >
                {journalLoading ? (
                  <><Loader2 style={{ width: 14, height: 14 }} className="animate-spin" /> Plume ecrit...</>
                ) : (
                  <><Send style={{ width: 14, height: 14 }} /> Envoyer a Plume</>
                )}
              </button>
            </div>

            {/* Plume's response */}
            {journalResponse && (
              <div className="mt-6 p-5 rounded-2xl animate-fade-up"
                style={{
                  background: 'linear-gradient(135deg, rgba(212,175,55,0.07), rgba(167,139,250,0.05))',
                  border: '1px solid rgba(212,175,55,0.25)',
                }}
                data-testid="journal-response">
                <p className="text-[10px] uppercase tracking-widest mb-2" style={{ color: 'var(--pa-accent-bright)', letterSpacing: '0.15em' }}>
                  Plume
                </p>
                <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: 'var(--pa-body)' }}>
                  {journalResponse}
                </p>
              </div>
            )}
          </section>

          {/* ═══ HISTORIQUE JOURNAL ═══ */}
          <section className="mb-8">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="w-full pa-glass rounded-2xl p-4 flex items-center justify-between transition-all hover:bg-white/5"
              data-testid="toggle-history"
            >
              <span className="text-[11px] uppercase tracking-[0.2em] flex items-center gap-2" style={{ color: 'var(--pa-lavender-bright)' }}>
                <BookHeart style={{ width: 13, height: 13 }} />
                Mes precedentes entrees
              </span>
              {showHistory ? <ChevronUp style={{ width: 16, height: 16, color: 'var(--pa-muted)' }} /> : <ChevronDown style={{ width: 16, height: 16, color: 'var(--pa-muted)' }} />}
            </button>
            {showHistory && (
              <div className="mt-3 space-y-3 animate-fade-up">
                {history.length === 0 ? (
                  <p className="text-center text-xs py-8 opacity-50" style={{ color: 'var(--pa-muted)' }}>
                    Tu n&#39;as pas encore d&#39;entrees. Ecris ta premiere ci-dessus.
                  </p>
                ) : (
                  history.map((h, i) => (
                    <div key={i} className="pa-glass rounded-2xl p-5">
                      <p className="text-[10px] uppercase tracking-widest mb-2 opacity-60" style={{ color: 'var(--pa-muted)' }}>
                        {h.date} &mdash; {h.mood || 'Sans humeur'}
                      </p>
                      <p className="text-sm italic mb-3" style={{ color: 'var(--pa-body)' }}>
                        &laquo; {h.entry} &raquo;
                      </p>
                      <div className="pl-4 border-l-2" style={{ borderColor: 'rgba(212,175,55,0.3)' }}>
                        <p className="text-[10px] uppercase tracking-widest mb-1" style={{ color: 'var(--pa-accent-bright)' }}>
                          Plume
                        </p>
                        <p className="text-xs leading-relaxed" style={{ color: 'var(--pa-body)' }}>
                          {h.response}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </section>

          {/* ═══ EVENING REFLECTION (>= 18h) ═══ */}
          {isEvening ? (
            <section className="pa-glass-gold rounded-3xl p-6 sm:p-8 mb-8 animate-fade-up">
              <p className="text-[10px] uppercase tracking-[0.3em] mb-2 flex items-center gap-2" style={{ color: 'var(--pa-accent-bright)' }}>
                <Moon style={{ width: 12, height: 12 }} /> Reflexion du soir
              </p>
              <h2 className="text-xl font-display mb-4" style={{ color: 'var(--pa-heading)', fontWeight: 400 }}>
                Avant de fermer la journee...
              </h2>
              <p className="text-sm mb-4" style={{ color: 'var(--pa-body)' }}>
                Pose-toi ces questions et confie ta reponse a Plume juste au-dessus :
              </p>
              <ul className="space-y-2 text-sm" style={{ color: 'var(--pa-body)' }}>
                <li>&bull; Qu&#39;est-ce qui m&#39;a nourri aujourd&#39;hui ?</li>
                <li>&bull; Quelle emotion ai-je accueillie sans la juger ?</li>
                <li>&bull; Quelle micro-graine ai-je seme ?</li>
              </ul>
            </section>
          ) : (
            <section className="pa-glass rounded-3xl p-5 mb-8 flex items-center gap-3 opacity-60">
              <Lock style={{ width: 16, height: 16, color: 'var(--pa-muted)' }} />
              <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
                La réflexion du soir se débloquera après 18h.
              </p>
            </section>
          )}

          {/* Refresh button */}
          <div className="text-center mt-12">
            <button onClick={loadToday} className="text-[10px] uppercase tracking-[0.2em] flex items-center gap-1.5 mx-auto opacity-50 hover:opacity-100 transition-opacity"
              style={{ color: 'var(--pa-muted)' }}>
              <RefreshCw style={{ width: 11, height: 11 }} /> Rafraichir
            </button>
          </div>

          {/* CTA chat */}
          <div className="mt-8 text-center">
            <Link to="/consultation" className="pa-btn-ghost" style={{ fontSize: 11, padding: '12px 26px' }}>
              <Sparkles style={{ width: 14, height: 14 }} />
              Continuer avec Plume au chat
            </Link>
          </div>

        </div>
      </div>
      <SEOServiceEnrich slug="rituel" />
    </>
  );
};

export default MonRituel;
