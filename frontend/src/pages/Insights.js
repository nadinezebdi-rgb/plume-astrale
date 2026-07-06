import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowLeft, Loader2, Heart, Briefcase, Activity, Brain, Zap } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import PageHero from '@/components/PageHero';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Section = ({ title, icon: Icon, children, testId }) => (
  <section className="card-mystical mb-6" data-testid={testId}>
    <div className="flex items-center gap-2 mb-4">
      <Icon className="w-5 h-5 text-[#C5A059]" strokeWidth={1.5} />
      <h2 className="text-xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>{title}</h2>
    </div>
    {children}
  </section>
);

const BiorythmBar = ({ label, value, color }) => {
  const pct = Math.round(((value + 100) / 200) * 100);
  const isPositive = value >= 0;
  return (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm" style={{ color: '#F0E6D3' }}>{label}</span>
        <span className="text-sm font-medium" style={{ color: isPositive ? '#4ade80' : '#f87171' }}>
          {isPositive ? '+' : ''}{value?.toFixed ? value.toFixed(0) : value}%
        </span>
      </div>
      <div className="h-3 rounded-full relative" style={{ background: 'rgba(255,255,255,0.08)' }}>
        <div className="absolute top-0 left-1/2 w-0.5 h-full bg-white/20 z-10" />
        <div className="h-3 rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, background: `linear-gradient(90deg, ${color}80, ${color})` }} />
      </div>
    </div>
  );
};

const ArchetypeCard = ({ archetype, score, description, isShadow }) => (
  <div className="rounded-xl p-4 mb-3" style={{ background: isShadow ? 'rgba(248,113,113,0.08)' : 'rgba(197,160,89,0.08)', border: `1px solid ${isShadow ? 'rgba(248,113,113,0.2)' : 'rgba(197,160,89,0.2)'}` }}>
    <div className="flex justify-between items-center mb-1">
      <p className="text-sm font-semibold" style={{ color: isShadow ? '#f87171' : '#C5A059' }}>{archetype}</p>
      {score !== undefined && (
        <div className="flex items-center gap-1">
          <div className="h-1.5 w-16 rounded-full" style={{ background: 'rgba(255,255,255,0.1)' }}>
            <div className="h-1.5 rounded-full" style={{ width: `${score}%`, background: isShadow ? '#f87171' : '#C5A059' }} />
          </div>
          <span className="text-xs" style={{ color: isShadow ? '#f87171' : '#C5A059' }}>{score}</span>
        </div>
      )}
    </div>
    {description && <p className="text-xs text-[#B8B0C8]/70 font-light">{description}</p>}
  </div>
);

export default function Insights() {
  const { isAuthenticated, user, token } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('biorhythms');
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState({});
  const [errors, setErrors] = useState({});

  const authHeaders = { Authorization: `Bearer ${token}` };

  const fetchData = async (key, endpoint) => {
    if (results[key] || loading[key]) return;
    setLoading(prev => ({ ...prev, [key]: true }));
    try {
      const res = await axios.post(`${API_URL}/api/astrology/v3/${endpoint}`, {}, { headers: authHeaders });
      setResults(prev => ({ ...prev, [key]: res.data }));
    } catch {
      setErrors(prev => ({ ...prev, [key]: 'Données temporairement indisponibles.' }));
    } finally {
      setLoading(prev => ({ ...prev, [key]: false }));
    }
  };

  useEffect(() => {
    if (isAuthenticated && user?.birth_date) {
      fetchData('biorhythms', 'insights/biorhythms');
      fetchData('personality', 'insights/personality');
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, user?.birth_date]);

  useEffect(() => {
    if (!isAuthenticated || !user?.birth_date) return;
    const map = {
      moonwellness: 'insights/moon-wellness',
      body: 'insights/body-health',
      career: 'insights/career',
      archetypes: 'insights/archetypes',
      energy: 'insights/energy-cycles',
    };
    if (map[activeTab]) fetchData(activeTab, map[activeTab]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  const tabs = [
    { id: 'biorhythms', label: '📈 Biorythmes', icon: Activity },
    { id: 'personality', label: '🧠 Personnalité', icon: Brain },
  ];

  const LoadingState = ({ text }) => (
    <div className="flex items-center gap-2 text-[#C5A059]/70 text-sm"><Loader2 className="w-4 h-4 animate-spin" />{text}</div>
  );

  if (!isAuthenticated) return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#0C0918' }}>
      <div className="text-center px-6">
        <p className="text-[#B8B0C8] mb-4">Connectez-vous pour accéder à vos insights personnalisés.</p>
        <button onClick={() => navigate('/connexion')} className="btn-mystical">Se connecter</button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen" style={{ background: '#0C0918' }}>
      <div className="max-w-2xl mx-auto px-4 py-8">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-[#B8B0C8]/60 hover:text-[#C5A059] transition-colors mb-6 text-sm">
          <ArrowLeft className="w-4 h-4" /> Retour
        </button>

        <PageHero
          image="/images/astrale/image-astrale-1.jpg"
          title="Insights Personnalisés"
          subtitle="Biorythmes · Archétypes · Carrière · Santé · Énergie"
        />

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {tabs.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className="px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-all flex-shrink-0"
              style={{
                background: activeTab === tab.id ? 'rgba(197,160,89,0.2)' : 'rgba(255,255,255,0.05)',
                color: activeTab === tab.id ? '#C5A059' : '#B8B0C8',
                border: `1px solid ${activeTab === tab.id ? 'rgba(197,160,89,0.4)' : 'rgba(255,255,255,0.1)'}`,
              }}>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Biorythmes */}
        {activeTab === 'biorhythms' && (
          <Section title="Biorythmes du Jour" icon={Activity} testId="biorhythms">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Vos cycles naturels physique, émotionnel et intellectuel aujourd'hui.</p>
            {loading.biorhythms ? <LoadingState text="Calcul des biorythmes…" />
              : errors.biorhythms ? <p className="text-red-400/70 text-sm">{errors.biorhythms}</p>
              : results.biorhythms ? (() => {
                const d = results.biorhythms;
                const cycles = d.cycles || d.biorhythms || {};
                return (
                  <div>
                    <BiorythmBar label="Physique" value={cycles.physical ?? cycles.physical_cycle ?? 0} color="#f87171" />
                    <BiorythmBar label="Émotionnel" value={cycles.emotional ?? cycles.emotional_cycle ?? 0} color="#a78bfa" />
                    <BiorythmBar label="Intellectuel" value={cycles.intellectual ?? cycles.intellectual_cycle ?? 0} color="#60a5fa" />
                    {(cycles.intuitive !== undefined) && <BiorythmBar label="Intuitif" value={cycles.intuitive ?? 0} color="#4ade80" />}
                    {d.summary && <p className="text-[#B8B0C8]/70 text-sm mt-4 font-light">{d.summary}</p>}
                    {d.recommendations && d.recommendations.map((r, i) => (
                      <div key={i} className="rounded-lg px-3 py-2 mt-2" style={{ background: 'rgba(255,255,255,0.04)' }}>
                        <p className="text-xs text-[#B8B0C8]/60">{r}</p>
                      </div>
                    ))}
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Personnalité */}
        {activeTab === 'personality' && (
          <Section title="Analyse de Personnalité" icon={Brain} testId="personality">
            {loading.personality ? <LoadingState text="Analyse de votre personnalité…" />
              : errors.personality ? <p className="text-red-400/70 text-sm">{errors.personality}</p>
              : results.personality ? (() => {
                const d = results.personality;
                const traits = d.traits || d.personality_traits || [];
                return (
                  <div>
                    {d.summary && <p className="text-[#B8B0C8]/80 text-sm mb-4 font-light leading-relaxed">{d.summary}</p>}
                    {traits.length > 0 && (
                      <div className="grid grid-cols-2 gap-2 mb-4">
                        {traits.slice(0, 8).map((t, i) => (
                          <div key={i} className="rounded-lg p-3" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
                            <p className="text-sm font-medium text-[#F0E6D3]">{t.trait || t.name || t}</p>
                            {t.description && <p className="text-xs text-[#B8B0C8]/60 mt-1">{t.description}</p>}
                          </div>
                        ))}
                      </div>
                    )}
                    {d.strengths && (
                      <div className="mb-3">
                        <p className="text-xs text-[#4ade80] mb-2">Forces</p>
                        <div className="flex flex-wrap gap-2">
                          {d.strengths.map((s, i) => (
                            <span key={i} className="px-2 py-1 rounded-full text-xs" style={{ background: 'rgba(74,222,128,0.12)', color: '#4ade80', border: '1px solid rgba(74,222,128,0.25)' }}>{s}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {d.challenges && (
                      <div>
                        <p className="text-xs text-[#f87171] mb-2">Défis à intégrer</p>
                        <div className="flex flex-wrap gap-2">
                          {d.challenges.map((c, i) => (
                            <span key={i} className="px-2 py-1 rounded-full text-xs" style={{ background: 'rgba(248,113,113,0.1)', color: '#f87171', border: '1px solid rgba(248,113,113,0.2)' }}>{c}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Archétypes Jungiens */}
        {activeTab === 'archetypes' && (
          <Section title="Archétypes Jungiens" icon={Sparkles} testId="archetypes">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Les 12 archétypes de Carol Pearson depuis votre thème natal — Héros, Amant, Sage, Magicien…</p>
            {loading.archetypes ? <LoadingState text="Analyse des archétypes…" />
              : errors.archetypes ? <p className="text-red-400/70 text-sm">{errors.archetypes}</p>
              : results.archetypes ? (() => {
                const d = results.archetypes;
                const archs = d.archetypes || [];
                const dominant = d.dominant_archetype || archs.find(a => a.is_dominant);
                const shadow = d.shadow_archetype || {};
                return (
                  <div>
                    {dominant && (
                      <div className="text-center rounded-xl p-4 mb-4" style={{ background: 'rgba(197,160,89,0.15)', border: '1px solid rgba(197,160,89,0.35)' }}>
                        <p className="text-xs text-[#C5A059] mb-1">Archétype dominant</p>
                        <p className="text-2xl font-semibold text-[#C5A059]">{dominant.name || dominant}</p>
                        {(dominant.description || dominant.summary) && <p className="text-xs text-[#B8B0C8]/70 mt-2 font-light">{dominant.description || dominant.summary}</p>}
                      </div>
                    )}
                    {archs.slice(0, 6).map((a, i) => (
                      <ArchetypeCard key={i} archetype={a.name} score={a.score} description={a.integration || a.description} isShadow={a.is_shadow} />
                    ))}
                    {(shadow.name || shadow.archetype) && (
                      <ArchetypeCard archetype={shadow.name || shadow.archetype} description={shadow.description || shadow.integration} isShadow={true} />
                    )}
                    {d.integration_guidance && (
                      <div className="mt-4 rounded-xl p-4" style={{ background: 'rgba(167,139,250,0.1)', border: '1px solid rgba(167,139,250,0.2)' }}>
                        <p className="text-xs text-[#a78bfa] mb-1">Guidance d'intégration</p>
                        <p className="text-sm text-[#B8B0C8]/80 font-light">{d.integration_guidance}</p>
                      </div>
                    )}
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Carrière */}
        {activeTab === 'career' && (
          <Section title="Astrologie de Carrière" icon={Briefcase} testId="career">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Vocation naturelle, aptitudes professionnelles et timing de carrière selon votre thème natal.</p>
            {loading.career ? <LoadingState text="Analyse de votre vocation…" />
              : errors.career ? <p className="text-red-400/70 text-sm">{errors.career}</p>
              : results.career ? (() => {
                const d = results.career;
                return (
                  <div>
                    {d.summary && <p className="text-[#B8B0C8]/80 text-sm mb-4 font-light leading-relaxed">{d.summary}</p>}
                    {d.vocations && (
                      <div className="mb-4">
                        <p className="text-xs text-[#B8B0C8]/50 mb-2">Vocations naturelles</p>
                        <div className="flex flex-wrap gap-2">
                          {d.vocations.map((v, i) => (
                            <span key={i} className="px-3 py-1 rounded-full text-sm" style={{ background: 'rgba(197,160,89,0.15)', color: '#C5A059', border: '1px solid rgba(197,160,89,0.3)' }}>{v}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {d.strengths && (
                      <div className="mb-4">
                        <p className="text-xs text-[#B8B0C8]/50 mb-2">Forces professionnelles</p>
                        {d.strengths.map((s, i) => (
                          <div key={i} className="rounded-lg px-3 py-2 mb-1" style={{ background: 'rgba(74,222,128,0.08)', border: '1px solid rgba(74,222,128,0.15)' }}>
                            <p className="text-sm text-[#4ade80]">{typeof s === 'string' ? s : (s.name || s.strength)}</p>
                            {s.description && <p className="text-xs text-[#B8B0C8]/60">{s.description}</p>}
                          </div>
                        ))}
                      </div>
                    )}
                    {d.timing && <p className="text-[#B8B0C8]/70 text-sm font-light">{d.timing}</p>}
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Santé */}
        {activeTab === 'body' && (
          <Section title="Santé & Corps Astral" icon={Heart} testId="body-health">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Influences planétaires sur vos systèmes corporels — zones de sensibilité et de force.</p>
            {loading.body ? <LoadingState text="Analyse santé…" />
              : errors.body ? <p className="text-red-400/70 text-sm">{errors.body}</p>
              : results.body ? (() => {
                const d = results.body;
                return (
                  <div>
                    {d.summary && <p className="text-[#B8B0C8]/80 text-sm mb-4 font-light leading-relaxed">{d.summary}</p>}
                    {d.body_systems && d.body_systems.map((sys, i) => (
                      <div key={i} className="rounded-xl p-3 mb-2" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
                        <div className="flex justify-between items-center mb-1">
                          <p className="text-sm font-medium text-[#F0E6D3]">{sys.system || sys.name}</p>
                          <span className="text-xs" style={{ color: sys.strength >= 70 ? '#4ade80' : sys.strength >= 40 ? '#fbbf24' : '#f87171' }}>
                            {sys.planet && `${sys.planet} · `}{sys.strength ? `${sys.strength}%` : ''}
                          </span>
                        </div>
                        {sys.description && <p className="text-xs text-[#B8B0C8]/60 font-light">{sys.description}</p>}
                      </div>
                    ))}
                    {d.recommendations && (
                      <div className="mt-4 rounded-xl p-4" style={{ background: 'rgba(96,165,250,0.1)', border: '1px solid rgba(96,165,250,0.2)' }}>
                        <p className="text-xs text-[#60a5fa] mb-2">Recommandations</p>
                        {(Array.isArray(d.recommendations) ? d.recommendations : [d.recommendations]).map((r, i) => (
                          <p key={i} className="text-sm text-[#B8B0C8]/80 font-light mb-1">{r}</p>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Bien-être lunaire */}
        {activeTab === 'moonwellness' && (
          <Section title="Bien-être selon la Lune" icon={Zap} testId="moon-wellness">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Recommandations personnalisées basées sur votre cycle lunaire natal.</p>
            {loading.moonwellness ? <LoadingState text="Analyse lunaire…" />
              : errors.moonwellness ? <p className="text-red-400/70 text-sm">{errors.moonwellness}</p>
              : results.moonwellness ? (() => {
                const d = results.moonwellness;
                return (
                  <div>
                    {d.moon_phase && (
                      <div className="text-center rounded-xl p-4 mb-4" style={{ background: 'rgba(167,139,250,0.1)', border: '1px solid rgba(167,139,250,0.25)' }}>
                        <p className="text-xs text-[#a78bfa] mb-1">Phase lunaire actuelle</p>
                        <p className="text-xl font-semibold text-[#a78bfa]">{d.moon_phase}</p>
                      </div>
                    )}
                    {d.recommendations && (
                      <div className="space-y-2">
                        {(Array.isArray(d.recommendations) ? d.recommendations : []).map((r, i) => (
                          <div key={i} className="rounded-lg px-4 py-3" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
                            <p className="text-sm text-[#F0E6D3]">{typeof r === 'string' ? r : r.text || r.recommendation}</p>
                          </div>
                        ))}
                      </div>
                    )}
                    {d.summary && <p className="text-[#B8B0C8]/80 text-sm mt-4 font-light">{d.summary}</p>}
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Énergie */}
        {activeTab === 'energy' && (
          <Section title="Cycles d'Énergie" icon={Zap} testId="energy-cycles">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Optimisez vos moments de workout, méditation et productivité avec vos cycles cosmiques.</p>
            {loading.energy ? <LoadingState text="Analyse des cycles d'énergie…" />
              : errors.energy ? <p className="text-red-400/70 text-sm">{errors.energy}</p>
              : results.energy ? (() => {
                const d = results.energy;
                const peak = d.peak_times || d.energy_peaks || [];
                const low = d.low_times || d.energy_lows || [];
                return (
                  <div>
                    {d.overall_energy !== undefined && (
                      <div className="text-center rounded-xl p-4 mb-4" style={{ background: 'rgba(197,160,89,0.12)', border: '1px solid rgba(197,160,89,0.3)' }}>
                        <p className="text-xs text-[#C5A059] mb-1">Énergie globale aujourd'hui</p>
                        <p className="text-2xl font-bold text-[#C5A059]">{d.overall_energy}/100</p>
                      </div>
                    )}
                    {peak.length > 0 && (
                      <div className="mb-3">
                        <p className="text-xs text-[#4ade80] mb-2">Pics d'énergie</p>
                        <div className="flex flex-wrap gap-2">
                          {peak.map((t, i) => (
                            <span key={i} className="px-3 py-1 rounded-full text-sm" style={{ background: 'rgba(74,222,128,0.12)', color: '#4ade80', border: '1px solid rgba(74,222,128,0.25)' }}>{t}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {d.summary && <p className="text-[#B8B0C8]/80 text-sm mt-3 font-light leading-relaxed">{d.summary}</p>}
                  </div>
                );
              })() : null}
          </Section>
        )}

        <p className="text-center text-[#B8B0C8]/30 text-xs mt-8 font-light">
          IA Astrologique — Swiss Ephemeris — Personnalisé selon votre thème natal
        </p>
      </div>
    </div>
  );
}
