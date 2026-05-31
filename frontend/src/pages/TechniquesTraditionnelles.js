import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowLeft, Loader2, Star, Clock, Compass, Triangle } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Section = ({ title, icon, children, testId }) => (
  <section className="card-mystical mb-6" data-testid={testId}>
    <div className="flex items-center gap-2 mb-4">
      <span className="text-lg">{icon}</span>
      <h2 className="text-xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>{title}</h2>
    </div>
    {children}
  </section>
);

const ItemCard = ({ title, subtitle, value, color = '#C5A059' }) => (
  <div className="rounded-xl p-3 mb-2" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
    <div className="flex justify-between items-start">
      <div>
        <p className="text-sm font-medium" style={{ color: '#F0E6D3' }}>{title}</p>
        {subtitle && <p className="text-xs text-[#B8B0C8]/60 mt-0.5">{subtitle}</p>}
      </div>
      {value && <span className="text-xs font-medium px-2 py-0.5 rounded" style={{ background: `${color}20`, color }}>{value}</span>}
    </div>
  </div>
);

export default function TechniquesTraditionnelles() {
  const { isAuthenticated, user, token } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('arabicparts');
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState({});
  const [errors, setErrors] = useState({});

  const authHeaders = { Authorization: `Bearer ${token}` };

  const fetchData = async (key, endpoint, method = 'post') => {
    if (results[key] || loading[key]) return;
    setLoading(prev => ({ ...prev, [key]: true }));
    try {
      const res = method === 'get'
        ? await axios.get(`${API_URL}/api/astrology/v3/${endpoint}`, { headers: authHeaders })
        : await axios.post(`${API_URL}/api/astrology/v3/${endpoint}`, {}, { headers: authHeaders });
      setResults(prev => ({ ...prev, [key]: res.data }));
    } catch {
      setErrors(prev => ({ ...prev, [key]: 'Données temporairement indisponibles.' }));
    } finally {
      setLoading(prev => ({ ...prev, [key]: false }));
    }
  };

  useEffect(() => {
    if (isAuthenticated && user?.birth_date) {
      fetchData('arabicparts', 'traditional/arabic-parts');
      fetchData('planetaryhours', 'traditional/planetary-hours', 'get');
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, user?.birth_date]);

  useEffect(() => {
    if (!isAuthenticated || !user?.birth_date) return;
    const map = {
      fixedstars: 'traditional/fixed-stars',
      dignities: 'traditional/dignities',
      sabian: 'traditional/sabian-symbols',
      midpoints: 'traditional/midpoints',
      asteroids: 'traditional/asteroids',
      eclipses: 'traditional/eclipses',
      draconic: 'traditional/draconic',
      kabbalah: 'traditional/kabbalah',
    };
    if (map[activeTab]) fetchData(activeTab, map[activeTab]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  const tabs = [
    { id: 'arabicparts', label: '🌙 Parts Arabes' },
    { id: 'fixedstars', label: '⭐ Étoiles Fixes' },
    { id: 'dignities', label: '👑 Dignités' },
    { id: 'sabian', label: '🔮 Sabians' },
    { id: 'planetaryhours', label: '🕐 Heures Planétaires' },
    { id: 'midpoints', label: '📐 Midpoints' },
    { id: 'asteroids', label: '🪐 Astéroïdes' },
    { id: 'eclipses', label: '🌑 Éclipses' },
    { id: 'draconic', label: '🐉 Draconique' },
    { id: 'kabbalah', label: '✡️ Kabbale' },
  ];

  const LoadingState = ({ text }) => (
    <div className="flex items-center gap-2 text-[#C5A059]/70 text-sm"><Loader2 className="w-4 h-4 animate-spin" />{text}</div>
  );
  const ErrorState = ({ msg }) => <p className="text-red-400/70 text-sm">{msg}</p>;

  if (!isAuthenticated) return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#0C0918' }}>
      <div className="text-center px-6">
        <p className="text-[#B8B0C8] mb-4">Connectez-vous pour accéder aux techniques traditionnelles.</p>
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
        <div className="text-center mb-8">
          <h1 className="text-3xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>Techniques Traditionnelles</h1>
          <p className="text-[#B8B0C8]/70 text-sm font-light">Parts arabes · Étoiles fixes · Dignités · Kabbale · Sabians · Astéroïdes · Éclipses</p>
        </div>

        {/* Tabs scrollables */}
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

        {/* Parts Arabes */}
        {activeTab === 'arabicparts' && (
          <Section title="Parts Arabes (97+ lots)" icon="🌙" testId="arabic-parts">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Formules hellénistiques révélant les thèmes de destinée cachés dans votre thème natal.</p>
            {loading.arabicparts ? <LoadingState text="Calcul des parts arabes…" />
              : errors.arabicparts ? <ErrorState msg={errors.arabicparts} />
              : results.arabicparts ? (() => {
                const parts = results.arabicparts.lots || results.arabicparts.arabic_parts || results.arabicparts.parts || [];
                return (
                  <div>
                    {parts.slice(0, 12).map((p, i) => (
                      <ItemCard key={i}
                        title={p.name || p.lot_name || `Part ${i+1}`}
                        subtitle={p.description || p.meaning || ''}
                        value={p.position || p.degree ? `${p.sign || ''} ${p.degree ? Number(p.degree).toFixed(1)+'°' : ''}`.trim() : undefined}
                      />
                    ))}
                    {results.arabicparts.fortune && (
                      <div className="mt-3 rounded-xl p-4" style={{ background: 'rgba(197,160,89,0.1)', border: '1px solid rgba(197,160,89,0.25)' }}>
                        <p className="text-xs text-[#C5A059] mb-1">Part de Fortune</p>
                        <p className="text-sm text-[#F0E6D3]">{results.arabicparts.fortune.sign} {results.arabicparts.fortune.interpretation || ''}</p>
                      </div>
                    )}
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Étoiles Fixes */}
        {activeTab === 'fixedstars' && (
          <Section title="Étoiles Fixes (50+)" icon="⭐" testId="fixed-stars">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Les grandes étoiles de la Voie Lactée et leur influence sur vos planètes natales.</p>
            {loading.fixedstars ? <LoadingState text="Calcul des étoiles fixes…" />
              : errors.fixedstars ? <ErrorState msg={errors.fixedstars} />
              : results.fixedstars ? (() => {
                const stars = results.fixedstars.stars || results.fixedstars.fixed_stars || results.fixedstars.conjunctions || [];
                return (
                  <div>
                    {stars.slice(0, 8).map((s, i) => (
                      <div key={i} className="rounded-xl p-3 mb-2" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
                        <div className="flex justify-between items-start mb-1">
                          <p className="text-sm font-medium text-[#F0E6D3]">{s.star_name || s.name}</p>
                          {s.conjunct_planet && <span className="text-xs text-[#C5A059]">conjoint {s.conjunct_planet}</span>}
                        </div>
                        {(s.influence || s.meaning) && <p className="text-xs text-[#B8B0C8]/60 font-light">{s.influence || s.meaning}</p>}
                      </div>
                    ))}
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Dignités */}
        {activeTab === 'dignities' && (
          <Section title="Dignités Planétaires" icon="👑" testId="dignities">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">La force et faiblesse des planètes selon la tradition (domicile, exaltation, chute, exil).</p>
            {loading.dignities ? <LoadingState text="Calcul des dignités…" />
              : errors.dignities ? <ErrorState msg={errors.dignities} />
              : results.dignities ? (() => {
                const digs = results.dignities.planets || results.dignities.dignities || [];
                const DIGNITY_COLORS = { ruler: '#4ade80', exaltation: '#C5A059', detriment: '#f87171', fall: '#f87171', peregrine: '#B8B0C8' };
                return (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-[#B8B0C8]/50 text-xs border-b border-white/10">
                          <th className="text-left pb-2 pr-4">Planète</th>
                          <th className="text-left pb-2 pr-4">Signe</th>
                          <th className="text-left pb-2">Dignité</th>
                        </tr>
                      </thead>
                      <tbody>
                        {digs.slice(0, 10).map((d, i) => {
                          const dignity = d.dignity || d.essential_dignity || '';
                          const color = DIGNITY_COLORS[dignity?.toLowerCase()] || '#B8B0C8';
                          return (
                            <tr key={i} className="border-b border-white/5">
                              <td className="py-2 pr-4 font-medium text-[#F0E6D3]">{d.planet || d.name}</td>
                              <td className="py-2 pr-4 text-[#C5A059]">{d.sign}</td>
                              <td className="py-2">
                                {dignity && <span className="px-2 py-0.5 rounded text-xs" style={{ background: `${color}20`, color }}>{dignity}</span>}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Symboles Sabians */}
        {activeTab === 'sabian' && (
          <Section title="Symboles Sabians" icon="🔮" testId="sabian-symbols">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">360 images symboliques — une pour chaque degré du zodiaque. La poésie de vos planètes.</p>
            {loading.sabian ? <LoadingState text="Calcul des symboles sabians…" />
              : errors.sabian ? <ErrorState msg={errors.sabian} />
              : results.sabian ? (() => {
                const symbols = results.sabian.symbols || results.sabian.sabian_symbols || [];
                return (
                  <div>
                    {symbols.slice(0, 8).map((s, i) => (
                      <div key={i} className="rounded-xl p-4 mb-3" style={{ background: 'rgba(167,139,250,0.08)', border: '1px solid rgba(167,139,250,0.2)' }}>
                        <div className="flex justify-between items-center mb-2">
                          <p className="text-sm font-medium text-[#a78bfa]">{s.planet}</p>
                          <p className="text-xs text-[#B8B0C8]/50">{s.sign} {s.degree}°</p>
                        </div>
                        <p className="text-sm text-[#F0E6D3] italic mb-1">"{s.symbol || s.title}"</p>
                        {s.keynote && <p className="text-xs text-[#B8B0C8]/60 font-light">{s.keynote}</p>}
                      </div>
                    ))}
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Heures Planétaires */}
        {activeTab === 'planetaryhours' && (
          <Section title="Heures Planétaires du Jour" icon="🕐" testId="planetary-hours">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Chaque heure de la journée est gouvernée par une planète — timing de l'action idéale.</p>
            {loading.planetaryhours ? <LoadingState text="Calcul des heures planétaires…" />
              : errors.planetaryhours ? <ErrorState msg={errors.planetaryhours} />
              : results.planetaryhours ? (() => {
                const hours = results.planetaryhours.hours || results.planetaryhours.planetary_hours || [];
                const currentHour = results.planetaryhours.current_hour || {};
                return (
                  <div>
                    {currentHour.planet && (
                      <div className="rounded-xl p-4 mb-4 text-center" style={{ background: 'rgba(197,160,89,0.15)', border: '1px solid rgba(197,160,89,0.35)' }}>
                        <p className="text-xs text-[#C5A059] mb-1">Heure planétaire actuelle</p>
                        <p className="text-xl font-semibold text-[#C5A059]">{currentHour.planet}</p>
                        {currentHour.meaning && <p className="text-xs text-[#B8B0C8]/70 mt-1">{currentHour.meaning}</p>}
                      </div>
                    )}
                    <div className="space-y-1">
                      {hours.slice(0, 12).map((h, i) => (
                        <div key={i} className="flex items-center gap-3 px-3 py-2 rounded-lg"
                          style={{ background: h.is_current ? 'rgba(197,160,89,0.12)' : 'rgba(255,255,255,0.03)' }}>
                          <span className="text-xs text-[#B8B0C8]/50 w-12 flex-shrink-0">{h.time || `${String(i).padStart(2,'0')}:00`}</span>
                          <span className="text-sm" style={{ color: h.is_current ? '#C5A059' : '#F0E6D3' }}>{h.planet}</span>
                          {h.meaning && <span className="text-xs text-[#B8B0C8]/50">{h.meaning}</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Midpoints */}
        {activeTab === 'midpoints' && (
          <Section title="Points Médians (Midpoints)" icon="📐" testId="midpoints">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Points médians planétaires — cosmobiologie de Reinhold Ebertin.</p>
            {loading.midpoints ? <LoadingState text="Calcul des midpoints…" />
              : errors.midpoints ? <ErrorState msg={errors.midpoints} />
              : results.midpoints ? (() => {
                const mp = results.midpoints.midpoints || [];
                return (
                  <div>
                    {mp.slice(0, 10).map((m, i) => (
                      <ItemCard key={i}
                        title={`${m.planet_1}/${m.planet_2}`}
                        subtitle={m.interpretation || m.meaning || ''}
                        value={m.position || (m.sign ? `${m.sign} ${m.degree?.toFixed(0)}°` : undefined)}
                        color="#60a5fa"
                      />
                    ))}
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Astéroïdes */}
        {activeTab === 'asteroids' && (
          <Section title="Astéroïdes & Archétypes Féminins" icon="🪐" testId="asteroids">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Chiron (guérison), Cérès (nourricière), Pallas (sagesse), Junon (partenariat), Vesta (feu sacré) + plus.</p>
            {loading.asteroids ? <LoadingState text="Calcul des astéroïdes…" />
              : errors.asteroids ? <ErrorState msg={errors.asteroids} />
              : results.asteroids ? (() => {
                const asts = results.asteroids.asteroids || [];
                return (
                  <div>
                    {asts.map((a, i) => (
                      <div key={i} className="rounded-xl p-3 mb-2" style={{ background: 'rgba(167,139,250,0.08)', border: '1px solid rgba(167,139,250,0.2)' }}>
                        <div className="flex justify-between items-start mb-1">
                          <p className="text-sm font-medium text-[#a78bfa]">{a.name}</p>
                          <span className="text-xs text-[#B8B0C8]/50">{a.sign} {a.degree ? `${Number(a.degree).toFixed(1)}°` : ''}</span>
                        </div>
                        {(a.interpretation || a.meaning) && <p className="text-xs text-[#B8B0C8]/70 font-light">{a.interpretation || a.meaning}</p>}
                      </div>
                    ))}
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Éclipses */}
        {activeTab === 'eclipses' && (
          <Section title="Éclipses & Impact Natal" icon="🌑" testId="eclipses">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Éclipses solaires et lunaires proches et leur activation de votre thème natal.</p>
            {loading.eclipses ? <LoadingState text="Calcul des éclipses…" />
              : errors.eclipses ? <ErrorState msg={errors.eclipses} />
              : results.eclipses ? (() => {
                const ecl = results.eclipses.eclipses || [];
                return (
                  <div>
                    {ecl.slice(0, 4).map((e, i) => (
                      <div key={i} className="rounded-xl p-4 mb-3" style={{ background: i % 2 === 0 ? 'rgba(248,113,113,0.08)' : 'rgba(96,165,250,0.08)', border: `1px solid ${i % 2 === 0 ? 'rgba(248,113,113,0.2)' : 'rgba(96,165,250,0.2)'}` }}>
                        <div className="flex justify-between items-center mb-2">
                          <p className="text-sm font-semibold" style={{ color: i % 2 === 0 ? '#f87171' : '#60a5fa' }}>
                            {e.type === 'solar' || e.eclipse_type === 'solar' ? '☀️ Éclipse Solaire' : '🌙 Éclipse Lunaire'}
                          </p>
                          <span className="text-xs text-[#B8B0C8]/50">{e.date}</span>
                        </div>
                        <p className="text-sm text-[#F0E6D3]">{e.sign} {e.degree ? `${Number(e.degree).toFixed(1)}°` : ''}</p>
                        {e.natal_impact && <p className="text-xs text-[#B8B0C8]/70 mt-1 font-light">{e.natal_impact}</p>}
                      </div>
                    ))}
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Draconique */}
        {activeTab === 'draconic' && (
          <Section title="Thème Draconique — L'Âme" icon="🐉" testId="draconic">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Le thème de votre âme — vos intentions profondes avant l'incarnation.</p>
            {loading.draconic ? <LoadingState text="Calcul du chart draconique…" />
              : errors.draconic ? <ErrorState msg={errors.draconic} />
              : results.draconic ? (() => {
                const planets = results.draconic.planets || results.draconic.positions || [];
                return (
                  <div>
                    {results.draconic.summary && <p className="text-[#B8B0C8]/80 text-sm mb-4 font-light">{results.draconic.summary}</p>}
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="text-[#B8B0C8]/50 text-xs border-b border-white/10">
                            <th className="text-left pb-2 pr-4">Planète</th>
                            <th className="text-left pb-2 pr-4">Signe Draconique</th>
                            <th className="text-left pb-2">Degré</th>
                          </tr>
                        </thead>
                        <tbody>
                          {planets.slice(0, 10).map((p, i) => (
                            <tr key={i} className="border-b border-white/5">
                              <td className="py-2 pr-4 font-medium text-[#F0E6D3]">{p.name || p.planet}</td>
                              <td className="py-2 pr-4 text-[#C5A059]">{p.draconic_sign || p.sign}</td>
                              <td className="py-2 text-[#B8B0C8]/50">{p.degree ? `${Number(p.degree).toFixed(1)}°` : '—'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                );
              })() : null}
          </Section>
        )}

        {/* Kabbale */}
        {activeTab === 'kabbalah' && (
          <Section title="Kabbale — Sephiroth & Anges" icon="✡️" testId="kabbalah">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">L'Arbre de Vie kabbalistique, les 72 anges gardiens et les corrections de l'âme (Tikkunim).</p>
            {loading.kabbalah ? <LoadingState text="Calcul kabbalistique…" />
              : errors.kabbalah ? <ErrorState msg={errors.kabbalah} />
              : results.kabbalah ? (() => {
                const d = results.kabbalah;
                return (
                  <div>
                    {d.guardian_angel && (
                      <div className="text-center rounded-xl p-4 mb-4" style={{ background: 'rgba(197,160,89,0.12)', border: '1px solid rgba(197,160,89,0.3)' }}>
                        <p className="text-xs text-[#C5A059] mb-1">Ange Gardien</p>
                        <p className="text-xl font-semibold text-[#C5A059]">{d.guardian_angel}</p>
                        {d.angel_meaning && <p className="text-xs text-[#B8B0C8]/60 mt-1">{d.angel_meaning}</p>}
                      </div>
                    )}
                    {d.sephiroth && (
                      <div className="mb-4">
                        <p className="text-xs text-[#B8B0C8]/50 mb-2">Sephiroth dominants</p>
                        <div className="flex flex-wrap gap-2">
                          {(d.sephiroth.dominant || d.sephiroth || []).slice(0, 5).map((s, i) => (
                            <span key={i} className="px-3 py-1 rounded-full text-sm" style={{ background: 'rgba(167,139,250,0.15)', color: '#a78bfa', border: '1px solid rgba(167,139,250,0.3)' }}>
                              {s.name || s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {d.tikkun && <p className="text-[#B8B0C8]/80 text-sm font-light leading-relaxed">{d.tikkun}</p>}
                    {d.life_path && <p className="text-[#B8B0C8]/80 text-sm mt-3 font-light">{d.life_path}</p>}
                  </div>
                );
              })() : null}
          </Section>
        )}

        <p className="text-center text-[#B8B0C8]/30 text-xs mt-8 font-light">
          Tradition hellénistique · médiévale · kabbalistique — Swiss Ephemeris
        </p>
      </div>
    </div>
  );
}
