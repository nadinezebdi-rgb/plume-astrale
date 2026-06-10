import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowLeft, Loader2, Wind, Flame, Droplets, Mountain, TreePine } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import PageHero from '@/components/PageHero';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ELEMENT_ICONS = { Bois: TreePine, Feu: Flame, Terre: Mountain, Métal: Mountain, Eau: Droplets };
const ELEMENT_COLORS = { Bois: '#4ade80', Feu: '#f87171', Terre: '#fbbf24', Métal: '#94a3b8', Eau: '#60a5fa', Wood: '#4ade80', Fire: '#f87171', Earth: '#fbbf24', Metal: '#94a3b8', Water: '#60a5fa' };

const Section = ({ title, icon, children, testId }) => (
  <section className="card-mystical mb-6" data-testid={testId}>
    <div className="flex items-center gap-2 mb-4">
      <span className="text-lg">{icon}</span>
      <h2 className="text-xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>{title}</h2>
    </div>
    {children}
  </section>
);

const ElementBar = ({ element, value, max = 100 }) => {
  const color = ELEMENT_COLORS[element] || '#C5A059';
  const pct = Math.min(100, Math.round((value / max) * 100));
  return (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span style={{ color }}>{element}</span>
        <span className="text-[#B8B0C8]/60">{pct}%</span>
      </div>
      <div className="h-2 rounded-full" style={{ background: 'rgba(255,255,255,0.08)' }}>
        <div className="h-2 rounded-full transition-all duration-700" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
};

export default function AstrologieChinoise() {
  const { isAuthenticated, user, token } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('zodiac');
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
      fetchData('zodiac', 'chinese/zodiac');
      fetchData('elements', 'chinese/elements');
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, user?.birth_date]);

  useEffect(() => {
    if (!isAuthenticated || !user?.birth_date) return;
    if (activeTab === 'bazi') fetchData('bazi', 'chinese/bazi');
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  const tabs = [
    { id: 'zodiac', label: '🐉 Zodiaque', },
    { id: 'elements', label: '🌊 Wu Xing', },
    { id: 'bazi', label: '☯️ BaZi', },
  ];

  if (!isAuthenticated) return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#0C0918' }}>
      <div className="text-center px-6">
        <p className="text-[#B8B0C8] mb-4">Connectez-vous pour accéder à l'astrologie chinoise.</p>
        <button onClick={() => navigate('/connexion')} className="btn-mystical">Se connecter</button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen" style={{ background: '#0C0918' }}>
      <div className="max-w-3xl mx-auto px-4 py-8">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-[#B8B0C8]/60 hover:text-[#C5A059] transition-colors mb-6 text-sm">
          <ArrowLeft className="w-4 h-4" /> Retour
        </button>

        <PageHero
          image="/images/astrale/image-astrale-9.jpg"
          title="Astrologie Chinoise"
          subtitle="BaZi · Wu Xing"
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

        {/* Zodiaque */}
        {activeTab === 'zodiac' && (
          <Section title="Animal du Zodiaque Chinois" icon="🐉" testId="chinese-zodiac">
            <img src="/images/astrale/chinois-zodiaque.jpg" alt="Dragon du zodiaque chinois" style={{ width: '100%', maxHeight: '320px', objectFit: 'cover', borderRadius: '16px', marginBottom: '1.5rem' }} />
            {loading.zodiac ? (
              <div className="flex items-center gap-2 text-[#C5A059]/70 text-sm"><Loader2 className="w-4 h-4 animate-spin" /> Calcul de votre animal…</div>
            ) : errors.zodiac ? (
              <p className="text-red-400/70 text-sm">{errors.zodiac}</p>
            ) : results.zodiac ? (() => {
              const d = results.zodiac;
              const animal = d.animal || d.chinese_sign || d.zodiac_animal || {};
              return (
                <div>
                  <div className="text-center mb-6">
                    <div className="text-6xl mb-3">{animal.emoji || '🐉'}</div>
                    <div className="text-2xl font-semibold mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#C5A059' }}>
                      {animal.name_fr || animal.name || 'Animal'}
                    </div>
                    <div className="text-sm text-[#B8B0C8]/60">{animal.element || ''} · {animal.yin_yang || ''}</div>
                  </div>
                  {(d.traits || animal.traits || []).length > 0 && (
                    <div className="flex flex-wrap gap-2 justify-center mb-4">
                      {(d.traits || animal.traits).map((t, i) => (
                        <span key={i} className="px-2 py-1 rounded-full text-xs"
                          style={{ background: 'rgba(197,160,89,0.12)', color: '#C5A059', border: '1px solid rgba(197,160,89,0.3)' }}>{t}</span>
                      ))}
                    </div>
                  )}
                  {(d.description || animal.description) && (
                    <p className="text-[#B8B0C8]/80 text-sm font-light leading-relaxed">{d.description || animal.description}</p>
                  )}
                  {(d.compatible_animals || animal.compatible_with || []).length > 0 && (
                    <div className="mt-4 rounded-lg p-3" style={{ background: 'rgba(96,165,250,0.1)', border: '1px solid rgba(96,165,250,0.2)' }}>
                      <p className="text-xs text-[#60a5fa] mb-1">Compatible avec</p>
                      <p className="text-[#F0E6D3] text-sm">{(d.compatible_animals || animal.compatible_with).join(', ')}</p>
                    </div>
                  )}
                </div>
              );
            })() : null}
          </Section>
        )}

        {/* Wu Xing */}
        {activeTab === 'elements' && (
          <Section title="Wu Xing — Les 5 Éléments" icon="🌊" testId="chinese-elements">
            <img src="/images/astrale/chinois-wuxing.jpg" alt="Les cinq elements Wu Xing" style={{ width: '100%', maxHeight: '320px', objectFit: 'cover', borderRadius: '16px', marginBottom: '1.5rem' }} />
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">L'équilibre des 5 éléments dans votre thème natal selon la Médecine Traditionnelle Chinoise.</p>
            {loading.elements ? (
              <div className="flex items-center gap-2 text-[#C5A059]/70 text-sm"><Loader2 className="w-4 h-4 animate-spin" /> Analyse des éléments…</div>
            ) : errors.elements ? (
              <p className="text-red-400/70 text-sm">{errors.elements}</p>
            ) : results.elements ? (() => {
              const d = results.elements;
              const balance = d.element_balance || d.elements || d.balance || {};
              const dominant = d.dominant_element || d.dominant || '';
              const lacking = d.lacking_element || d.lacking || d.missing || '';
              return (
                <div>
                  {dominant && (
                    <div className="flex gap-3 mb-4">
                      <div className="flex-1 rounded-lg p-3 text-center" style={{ background: `${ELEMENT_COLORS[dominant] || '#C5A059'}15`, border: `1px solid ${ELEMENT_COLORS[dominant] || '#C5A059'}30` }}>
                        <p className="text-xs mb-1" style={{ color: ELEMENT_COLORS[dominant] || '#C5A059' }}>Élément dominant</p>
                        <p className="font-semibold" style={{ color: ELEMENT_COLORS[dominant] || '#C5A059' }}>{dominant}</p>
                      </div>
                      {lacking && (
                        <div className="flex-1 rounded-lg p-3 text-center" style={{ background: 'rgba(248,113,113,0.1)', border: '1px solid rgba(248,113,113,0.2)' }}>
                          <p className="text-xs text-[#f87171] mb-1">À renforcer</p>
                          <p className="font-semibold text-[#f87171]">{lacking}</p>
                        </div>
                      )}
                    </div>
                  )}
                  {Object.entries(balance).map(([el, val]) => (
                    <ElementBar key={el} element={el} value={val} />
                  ))}
                  {d.interpretation && <p className="text-[#B8B0C8]/80 text-sm mt-4 font-light leading-relaxed">{d.interpretation}</p>}
                  {d.remedies && <p className="text-[#B8B0C8]/70 text-sm mt-3 font-light">{d.remedies}</p>}
                </div>
              );
            })() : null}
          </Section>
        )}

        {/* BaZi */}
        {activeTab === 'bazi' && (
          <Section title="BaZi — 4 Piliers du Destin" icon="☯️" testId="chinese-bazi">
            <img src="/images/astrale/chinois-bazi.jpg" alt="Ciel etoile et zodiaque BaZi" style={{ width: '100%', maxHeight: '320px', objectFit: 'cover', borderRadius: '16px', marginBottom: '1.5rem' }} />
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Année, Mois, Jour et Heure de naissance — les 4 colonnes qui révèlent votre destin.</p>
            {loading.bazi ? (
              <div className="flex items-center gap-2 text-[#C5A059]/70 text-sm"><Loader2 className="w-4 h-4 animate-spin" /> Calcul des 4 Piliers…</div>
            ) : errors.bazi ? (
              <p className="text-red-400/70 text-sm">{errors.bazi}</p>
            ) : results.bazi ? (() => {
              const d = results.bazi;
              const pillars = d.pillars || d.four_pillars || [];
              const labels = ['Année', 'Mois', 'Jour', 'Heure'];
              return (
                <div>
                  {pillars.length > 0 ? (
                    <div className="grid grid-cols-4 gap-2 mb-4">
                      {pillars.slice(0, 4).map((p, i) => (
                        <div key={i} className="rounded-xl p-3 text-center" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)' }}>
                          <p className="text-xs text-[#B8B0C8]/50 mb-2">{labels[i]}</p>
                          <p className="text-lg font-medium" style={{ color: '#C5A059' }}>{p.heavenly_stem || p.stem || '—'}</p>
                          <p className="text-sm text-[#B8B0C8]/70">{p.earthly_branch || p.branch || '—'}</p>
                          {p.element && <p className="text-xs mt-1" style={{ color: ELEMENT_COLORS[p.element] || '#B8B0C8' }}>{p.element}</p>}
                        </div>
                      ))}
                    </div>
                  ) : null}
                  {d.summary && <p className="text-[#B8B0C8]/80 text-sm font-light leading-relaxed">{d.summary}</p>}
                  {d.luck_pillars && (
                    <div className="mt-4">
                      <p className="text-xs text-[#B8B0C8]/50 mb-2">Grandes Fortunes (Da Yun)</p>
                      <div className="flex gap-2 overflow-x-auto pb-1">
                        {(d.luck_pillars || []).slice(0, 6).map((lp, i) => (
                          <div key={i} className="rounded-lg px-3 py-2 flex-shrink-0 text-center"
                            style={{ background: lp.is_current ? 'rgba(197,160,89,0.15)' : 'rgba(255,255,255,0.04)', border: `1px solid ${lp.is_current ? 'rgba(197,160,89,0.4)' : 'rgba(255,255,255,0.08)'}` }}>
                            <p className="text-xs" style={{ color: lp.is_current ? '#C5A059' : '#B8B0C8' }}>{lp.age || ''}ans</p>
                            <p className="text-sm font-medium" style={{ color: lp.is_current ? '#C5A059' : '#F0E6D3' }}>{lp.stem || '—'}/{lp.branch || '—'}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })() : null}
          </Section>
        )}

        <p className="text-center text-[#B8B0C8]/30 text-xs mt-8 font-light">
          4000 ans de sagesse chinoise — Calculs authentiques
        </p>
      </div>
    </div>
  );
}
