import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import {
  Flame, Moon, Sparkles, Heart, Sun, Cloud, Wind, CloudRain,
  Check, BookOpen, Loader2, ChevronRight, Star, Lock,
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

// Mapping icon name (from backend MOODS) → lucide component
const MOOD_ICONS = { Sun, Moon, Cloud, Wind, Flame, Heart, CloudRain };

const SCORE_LABELS = {
  energy: { label: 'Énergie', desc: 'Vitalité du jour' },
  confidence: { label: 'Confiance', desc: 'Ancrage intérieur' },
  discipline: { label: 'Discipline', desc: 'Tenue des engagements' },
  intuition: { label: 'Intuition', desc: 'Lecture subtile' },
};

const greeting = () => {
  const h = new Date().getHours();
  if (h < 6) return 'Cette nuit';
  if (h < 12) return 'Ce matin';
  if (h < 18) return 'Cet après-midi';
  return 'Ce soir';
};

// ─────────────────────────────────────────────────────────────
// Gauge component
// ─────────────────────────────────────────────────────────────
const Gauge = ({ value, label, desc, color = '#D4AF37' }) => {
  const v = Math.max(20, Math.min(98, value || 50));
  return (
    <div className="rounded-2xl p-4" style={{ background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(212,175,55,0.15)' }} data-testid={`gauge-${label.toLowerCase()}`}>
      <div className="flex items-center justify-between mb-2">
        <p className="text-[10px] uppercase tracking-widest" style={{ color: 'rgba(212,175,55,0.75)', letterSpacing: '0.12em' }}>{label}</p>
        <p className="text-base" style={{ fontFamily: 'Cormorant Garamond, serif', color }}>{v}</p>
      </div>
      <div className="h-1 rounded-full overflow-hidden" style={{ background: 'rgba(212,175,55,0.08)' }}>
        <div className="h-full rounded-full transition-all duration-1000" style={{ width: `${v}%`, background: `linear-gradient(90deg, ${color}80, ${color})` }} />
      </div>
      <p className="text-[10px] mt-2" style={{ color: 'rgba(184,176,200,0.55)' }}>{desc}</p>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────
// Mood picker (morning check-in)
// ─────────────────────────────────────────────────────────────
const MoodPicker = ({ moods, currentMood, onSubmit, loading }) => {
  const [selected, setSelected] = useState(currentMood || null);
  const [intention, setIntention] = useState('');

  return (
    <div className="rounded-2xl p-6" style={{ background: 'rgba(212,175,55,0.04)', border: '1px solid rgba(212,175,55,0.18)' }} data-testid="mood-picker">
      <h3 className="text-lg mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>
        Comment te sens-tu {greeting().toLowerCase()} ?
      </h3>
      <p className="text-xs mb-5" style={{ color: 'rgba(184,176,200,0.65)' }}>
        Choisis ton humeur et pose une intention. Cela ajuste ton paysage du jour.
      </p>

      <div className="grid grid-cols-4 sm:grid-cols-7 gap-2 mb-5">
        {moods?.map(m => {
          const Icon = MOOD_ICONS[m.icon] || Sparkles;
          const isActive = selected === m.id;
          return (
            <button
              key={m.id}
              onClick={() => setSelected(m.id)}
              className="flex flex-col items-center gap-1 px-2 py-3 rounded-xl transition-all"
              style={{
                background: isActive ? 'rgba(212,175,55,0.15)' : 'rgba(255,255,255,0.02)',
                border: `1px solid ${isActive ? m.color : 'rgba(212,175,55,0.08)'}`,
                color: isActive ? m.color : 'rgba(184,176,200,0.75)',
              }}
              data-testid={`mood-${m.id}`}
            >
              <Icon style={{ width: 16, height: 16 }} strokeWidth={1.5} />
              <span className="text-[10px]">{m.label}</span>
            </button>
          );
        })}
      </div>

      <textarea
        value={intention}
        onChange={e => setIntention(e.target.value.slice(0, 200))}
        placeholder="Quelle intention pour aujourd'hui ? (optionnel)"
        rows={2}
        className="w-full bg-transparent rounded-lg p-3 text-sm outline-none transition-all"
        style={{ border: '1px solid rgba(212,175,55,0.15)', color: 'rgba(240,230,211,0.9)', resize: 'none' }}
        data-testid="intention-input"
      />

      <button
        onClick={() => onSubmit(selected, intention)}
        disabled={!selected || loading}
        className="mt-4 w-full flex items-center justify-center gap-2 px-5 py-3 rounded-full transition-all text-xs uppercase tracking-widest"
        style={{
          background: selected ? 'linear-gradient(135deg, #D4AF37, #D4AF37)' : 'rgba(255,255,255,0.04)',
          color: selected ? '#111625' : 'rgba(184,176,200,0.5)',
          letterSpacing: '0.14em',
          fontWeight: 600,
          cursor: selected ? 'pointer' : 'not-allowed',
          boxShadow: selected ? '0 4px 16px rgba(212,175,55,0.3)' : 'none',
        }}
        data-testid="checkin-submit"
      >
        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Sparkles className="w-4 h-4" strokeWidth={1.5} /> Poser mon intention</>}
      </button>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────
// Evening reflection (locked before 19h local)
// ─────────────────────────────────────────────────────────────
const EveningReflection = ({ unlocked, alreadyDone, onSubmit, response, loading, existingEntry }) => {
  const [entry, setEntry] = useState('');

  if (alreadyDone) {
    return (
      <div className="rounded-2xl p-6" style={{ background: 'rgba(167,139,250,0.06)', border: '1px solid rgba(167,139,250,0.25)' }} data-testid="evening-done">
        <div className="flex items-start gap-3 mb-3">
          <BookOpen className="w-5 h-5 mt-1" style={{ color: '#A78BFA' }} strokeWidth={1.5} />
          <div>
            <h3 className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>Ta réflexion du soir</h3>
            <p className="text-xs" style={{ color: 'rgba(184,176,200,0.6)' }}>Déjà partagée aujourd&apos;hui</p>
          </div>
        </div>
        {existingEntry?.entry && (
          <p className="text-sm italic mb-3 px-4 py-3 rounded-lg" style={{ color: 'rgba(240,230,211,0.85)', background: 'rgba(255,255,255,0.03)', fontFamily: 'Cormorant Garamond, serif' }}>
            « {existingEntry.entry} »
          </p>
        )}
        {existingEntry?.plume_response && (
          <div className="text-sm leading-relaxed" style={{ color: 'rgba(184,176,200,0.85)', lineHeight: 1.7 }}>
            <p className="text-[10px] uppercase tracking-widest mb-2" style={{ color: '#A78BFA', letterSpacing: '0.12em' }}>Soléna te répond</p>
            {existingEntry.plume_response.split('\n').filter(Boolean).map((para, i) => <p key={i} className="mb-2">{para}</p>)}
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      className="rounded-2xl p-6 transition-opacity"
      style={{
        background: unlocked ? 'rgba(167,139,250,0.06)' : 'rgba(255,255,255,0.02)',
        border: `1px solid ${unlocked ? 'rgba(167,139,250,0.25)' : 'rgba(212,175,55,0.1)'}`,
        opacity: unlocked ? 1 : 0.55,
      }}
      data-testid="evening-reflection"
    >
      <div className="flex items-start gap-3 mb-3">
        {unlocked ? (
          <BookOpen className="w-5 h-5 mt-1" style={{ color: '#A78BFA' }} strokeWidth={1.5} />
        ) : (
          <Lock className="w-5 h-5 mt-1" style={{ color: 'rgba(184,176,200,0.5)' }} strokeWidth={1.5} />
        )}
        <div>
          <h3 className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>La réflexion du soir</h3>
          <p className="text-xs" style={{ color: 'rgba(184,176,200,0.6)' }}>
            {unlocked
              ? 'Pose ici ce qui te traverse. Soléna te répondra avec attention.'
              : 'Déverrouillée chaque soir à partir de 19h pour une introspection paisible.'}
          </p>
        </div>
      </div>

      {unlocked && (
        <>
          <textarea
            value={entry}
            onChange={e => setEntry(e.target.value.slice(0, 4000))}
            placeholder="Comment cette journée s'est-elle déposée en toi ?"
            rows={5}
            disabled={loading || !!response}
            className="w-full bg-transparent rounded-lg p-3 text-sm outline-none transition-all"
            style={{ border: '1px solid rgba(167,139,250,0.18)', color: 'rgba(240,230,211,0.9)', resize: 'none' }}
            data-testid="reflection-input"
          />
          <div className="flex items-center justify-between mt-3">
            <span className="text-[10px]" style={{ color: 'rgba(184,176,200,0.5)' }}>{entry.length} / 4000</span>
            {!response ? (
              <button
                onClick={() => onSubmit(entry)}
                disabled={entry.length < 5 || loading}
                className="flex items-center gap-2 px-5 py-2.5 rounded-full text-xs uppercase tracking-widest transition-all"
                style={{
                  background: entry.length >= 5 ? 'linear-gradient(135deg, #A78BFA, #8B6FE0)' : 'rgba(255,255,255,0.04)',
                  color: entry.length >= 5 ? '#111625' : 'rgba(184,176,200,0.5)',
                  letterSpacing: '0.12em',
                  fontWeight: 600,
                  cursor: entry.length >= 5 ? 'pointer' : 'not-allowed',
                }}
                data-testid="reflection-submit"
              >
                {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <>Partager <ChevronRight className="w-3.5 h-3.5" /></>}
              </button>
            ) : null}
          </div>

          {response && (
            <div className="mt-5 pt-5" style={{ borderTop: '1px solid rgba(167,139,250,0.15)' }} data-testid="reflection-response">
              <p className="text-[10px] uppercase tracking-widest mb-3" style={{ color: '#A78BFA', letterSpacing: '0.12em' }}>Soléna te répond</p>
              <div className="text-sm leading-relaxed" style={{ color: 'rgba(184,176,200,0.9)', lineHeight: 1.75 }}>
                {response.split('\n').filter(Boolean).map((para, i) => <p key={i} className="mb-3">{para}</p>)}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────
// Main dashboard
// ─────────────────────────────────────────────────────────────
export default function CercleDashboard() {
  const { token, refreshBalance } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);
  const [checkinLoading, setCheckinLoading] = useState(false);
  const [reflectionLoading, setReflectionLoading] = useState(false);
  const [reflectionResponse, setReflectionResponse] = useState(null);

  const hour = new Date().getHours();
  const eveningUnlocked = hour >= 19 || hour < 4;

  const load = useCallback(async () => {
    try {
      const r = await axios.get(`${API}/api/cercle/daily`, { headers: { Authorization: `Bearer ${token}` } });
      setData(r.data);
    } catch (e) {
      setErr(e.response?.data?.detail || 'Impossible de charger ton Cercle.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const handleCheckin = async (mood, intention) => {
    if (!mood) return;
    setCheckinLoading(true);
    try {
      const r = await axios.post(`${API}/api/cercle/checkin`, { mood, intention }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      // Optimistic update : reflète le check-in localement + maj streak depuis la réponse
      setData(prev => prev ? {
        ...prev,
        checkin: { mood, intention },
        streak: {
          ...prev.streak,
          streak_count: r.data.streak_count ?? prev.streak?.streak_count,
          checked_in_today: true,
          next_milestone: r.data.next_milestone ?? prev.streak?.next_milestone,
        },
      } : prev);
      refreshBalance();
    } catch (e) {
      setErr(e.response?.data?.detail || 'Impossible d\'enregistrer ton check-in.');
    } finally {
      setCheckinLoading(false);
    }
  };

  const handleReflection = async (entry) => {
    setReflectionLoading(true);
    setErr(null);
    try {
      const r = await axios.post(`${API}/api/cercle/reflection`, { entry }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setReflectionResponse(r.data.response);
    } catch (e) {
      setErr(e.response?.data?.detail || 'Soléna est momentanément silencieuse.');
    } finally {
      setReflectionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" data-testid="cercle-loading">
        <Loader2 className="w-6 h-6 animate-spin" style={{ color: '#D4AF37' }} />
      </div>
    );
  }

  if (err && !data) {
    return (
      <div className="min-h-screen flex items-center justify-center px-6">
        <p className="text-sm text-center" style={{ color: '#FCA5A5' }} data-testid="cercle-error">{err}</p>
      </div>
    );
  }

  if (!data) return null;

  const dateLabel = new Date(data.date).toLocaleDateString('fr-FR', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  });
  const streak = data.streak || {};
  const alreadyReflected = !!data.reflection_today;

  return (
    <div className="min-h-screen pt-24 pb-24 px-4 sm:px-6" data-testid="cercle-dashboard">
      <div className="max-w-3xl mx-auto">

        {/* ─── Header salutation ─── */}
        <div className="mb-10 text-center">
          <p className="text-[10px] uppercase tracking-widest mb-2" style={{ color: '#D4AF37', letterSpacing: '0.3em', fontFamily: 'Cinzel, serif' }}>
            Le Cercle
          </p>
          <h1 className="text-3xl sm:text-4xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: '#F5EEE0' }} data-testid="cercle-greeting">
            {greeting()}, <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>{data.profile.prenom}</em>
          </h1>
          <p className="text-xs capitalize" style={{ color: 'rgba(184,176,200,0.6)' }}>{dateLabel}</p>
        </div>

        {/* ─── Streak + Phase lunaire ─── */}
        <div className="grid sm:grid-cols-2 gap-4 mb-8">
          {/* Streak */}
          <div className="rounded-2xl p-5 flex items-center gap-4" style={{ background: 'rgba(255,107,53,0.05)', border: '1px solid rgba(255,107,53,0.18)' }} data-testid="cercle-streak">
            <div className="relative flex-shrink-0">
              <Flame className="w-10 h-10" strokeWidth={1.5} style={{ color: streak.streak_count > 0 ? '#FF6B35' : 'rgba(212,175,55,0.5)', filter: streak.streak_count >= 7 ? 'drop-shadow(0 0 10px rgba(255,107,53,0.4))' : 'none' }} />
              {streak.streak_count > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full text-[10px] flex items-center justify-center font-bold" style={{ background: '#FF6B35', color: '#111625' }}>{streak.streak_count}</span>
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[10px] uppercase tracking-widest mb-1" style={{ color: 'rgba(184,176,200,0.65)', letterSpacing: '0.12em' }}>Assiduité</p>
              <p className="text-base" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                {streak.streak_count === 0 ? 'Commence ta présence' : `${streak.streak_count} jour${streak.streak_count > 1 ? 's' : ''}`}
              </p>
              <p className="text-[10px] mt-1" style={{ color: 'rgba(184,176,200,0.55)' }}>
                {streak.checked_in_today ? 'Présence du jour validée ✓' : (streak.next_milestone?.days ? `Prochain palier : ${streak.next_milestone.days}j (+${streak.next_milestone.bonus}cr)` : 'Tous les paliers atteints')}
              </p>
            </div>
          </div>

          {/* Phase lunaire */}
          <div className="rounded-2xl p-5 flex items-center gap-4" style={{ background: 'rgba(167,139,250,0.05)', border: '1px solid rgba(167,139,250,0.2)' }} data-testid="cercle-moon">
            <Moon className="w-9 h-9 flex-shrink-0" strokeWidth={1.5} style={{ color: '#A78BFA' }} />
            <div className="flex-1 min-w-0">
              <p className="text-[10px] uppercase tracking-widest mb-1" style={{ color: 'rgba(184,176,200,0.65)', letterSpacing: '0.12em' }}>Phase lunaire</p>
              <p className="text-base" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>{data.moon.phase}</p>
              <p className="text-[10px] mt-1 italic" style={{ color: 'rgba(184,176,200,0.65)' }}>{data.moon.theme}</p>
            </div>
          </div>
        </div>

        {/* ─── Conseil de la Plume ─── */}
        <section className="rounded-2xl p-6 mb-8" style={{ background: 'linear-gradient(135deg, rgba(212,175,55,0.08) 0%, rgba(212,175,55,0.02) 100%)', border: '1px solid rgba(212,175,55,0.22)' }} data-testid="cercle-insight">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-4 h-4" strokeWidth={1.5} style={{ color: '#D4AF37' }} />
            <p className="text-[10px] uppercase tracking-widest" style={{ color: '#D4AF37', letterSpacing: '0.14em', fontFamily: 'Cinzel, serif' }}>Le Conseil de la Plume</p>
          </div>
          <p className="text-base leading-relaxed" style={{ color: 'rgba(240,230,211,0.92)', fontFamily: 'Cormorant Garamond, serif', lineHeight: 1.7, fontStyle: 'italic' }}>
            {data.insight}
          </p>
        </section>

        {/* ─── Check-in matinal ou résumé ─── */}
        {data.checkin ? (
          <div className="rounded-2xl p-5 mb-8 flex items-start gap-4" style={{ background: 'rgba(124,184,138,0.06)', border: '1px solid rgba(124,184,138,0.2)' }} data-testid="checkin-done">
            <Check className="w-5 h-5 mt-0.5 flex-shrink-0" strokeWidth={2} style={{ color: '#7CB88A' }} />
            <div>
              <p className="text-sm mb-1" style={{ color: '#F5EEE0' }}>
                Intention posée : <span style={{ fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic', color: '#A3D6AC' }}>« {data.checkin.intention || 'Présence et douceur'} »</span>
              </p>
              <p className="text-xs" style={{ color: 'rgba(184,176,200,0.65)' }}>
                Humeur du matin : <strong style={{ color: 'rgba(240,230,211,0.85)' }}>{data.moods.find(m => m.id === data.checkin.mood)?.label || data.checkin.mood}</strong>
              </p>
            </div>
          </div>
        ) : (
          <div className="mb-8">
            <MoodPicker moods={data.moods} currentMood={null} onSubmit={handleCheckin} loading={checkinLoading} />
          </div>
        )}

        {/* ─── 4 jauges cosmiques ─── */}
        <section className="mb-8">
          <p className="text-[10px] uppercase tracking-widest mb-3" style={{ color: 'rgba(212,175,55,0.65)', letterSpacing: '0.18em', fontFamily: 'Cinzel, serif' }}>
            Tes énergies du jour
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {Object.entries(data.scores).map(([key, val]) => (
              <Gauge key={key} value={val} label={SCORE_LABELS[key]?.label || key} desc={SCORE_LABELS[key]?.desc} />
            ))}
          </div>
        </section>

        {/* ─── Tarot du jour ─── */}
        <section className="rounded-2xl p-6 mb-8 flex items-start gap-5" style={{ background: 'rgba(201,120,120,0.05)', border: '1px solid rgba(201,120,120,0.2)' }} data-testid="cercle-tarot">
          <div className="flex-shrink-0 w-14 h-20 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, rgba(201,120,120,0.15), rgba(212,175,55,0.1))', border: '1px solid rgba(212,175,55,0.25)' }}>
            <Star className="w-7 h-7" strokeWidth={1.2} style={{ color: '#D4AF37' }} />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[10px] uppercase tracking-widest mb-1" style={{ color: '#C97878', letterSpacing: '0.14em', fontFamily: 'Cinzel, serif' }}>Carte du jour</p>
            <h3 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>{data.tarot?.name}</h3>
            <p className="text-sm leading-relaxed" style={{ color: 'rgba(184,176,200,0.85)', lineHeight: 1.7 }}>{data.tarot?.message}</p>
          </div>
        </section>

        {/* ─── Reflection du soir ─── */}
        <EveningReflection
          unlocked={eveningUnlocked}
          alreadyDone={alreadyReflected}
          existingEntry={data.reflection_today}
          onSubmit={handleReflection}
          response={reflectionResponse}
          loading={reflectionLoading}
        />

        {err && (
          <p className="mt-6 text-sm text-center" style={{ color: '#FCA5A5' }} data-testid="cercle-inline-error">{err}</p>
        )}
      </div>
    </div>
  );
}
