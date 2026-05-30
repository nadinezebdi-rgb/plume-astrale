import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowLeft, Loader2, Star, Moon, Sun, BookOpen, Clock, Layers } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
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

const Tag = ({ text, color = '#C5A059' }) => (
  <span className="inline-block px-2 py-0.5 rounded text-xs font-medium mr-1 mb-1"
    style={{ background: `${color}22`, color, border: `1px solid ${color}44` }}>
    {text}
  </span>
);

const NakshatraCard = ({ data }) => {
  if (!data) return null;
  const n = data.nakshatra || data;
  return (
    <div className="rounded-xl p-4 mb-3" style={{ background: 'rgba(197,160,89,0.08)', border: '1px solid rgba(197,160,89,0.2)' }}>
      <div className="text-lg font-semibold mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
        {n.name || 'Nakshatra'}
      </div>
      <div className="text-sm text-[#B8B0C8]/70 mb-2">{n.meaning || n.symbol || ''}</div>
      {n.deity && <Tag text={`Divinité : ${n.deity}`} />}
      {n.lord && <Tag text={`Seigneur : ${n.lord}`} color="#a78bfa" />}
      {n.quality && <Tag text={n.quality} color="#60a5fa" />}
      {n.description && <p className="text-sm text-[#B8B0C8]/80 mt-3 font-light">{n.description}</p>}
    </div>
  );
};

const DashaTimeline = ({ data }) => {
  if (!data) return null;
  const periods = data.mahadashas || data.dasha_periods || data.periods || [];
  if (!periods.length) return <p className="text-[#B8B0C8]/50 text-sm">Données Dasha non disponibles.</p>;
  return (
    <div className="space-y-2">
      {periods.slice(0, 6).map((p, i) => {
        const isActive = p.is_current || p.active;
        return (
          <div key={i} className="flex items-center gap-3 rounded-lg px-3 py-2"
            style={{ background: isActive ? 'rgba(197,160,89,0.15)' : 'rgba(255,255,255,0.03)', border: `1px solid ${isActive ? 'rgba(197,160,89,0.4)' : 'rgba(255,255,255,0.07)'}` }}>
            {isActive && <span className="w-2 h-2 rounded-full bg-[#C5A059] animate-pulse flex-shrink-0" />}
            <div className="flex-1 min-w-0">
              <span className="text-sm font-medium" style={{ color: isActive ? '#C5A059' : '#F0E6D3' }}>
                {p.planet || p.lord || p.name}
              </span>
              {p.start_date && <span className="text-xs text-[#B8B0C8]/50 ml-2">{p.start_date} → {p.end_date}</span>}
            </div>
            {isActive && <span className="text-xs text-[#C5A059] font-medium">En cours</span>}
          </div>
        );
      })}
    </div>
  );
};

const PlanetTable = ({ data }) => {
  const planets = data?.planets || data?.positions || [];
  if (!planets.length) return <p className="text-[#B8B0C8]/50 text-sm">Données planétaires non disponibles.</p>;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-[#B8B0C8]/50 text-xs border-b border-white/10">
            <th className="text-left pb-2 pr-4">Planète</th>
            <th className="text-left pb-2 pr-4">Signe</th>
            <th className="text-left pb-2 pr-4">Maison</th>
            <th className="text-left pb-2">Degré</th>
          </tr>
        </thead>
        <tbody>
          {planets.slice(0, 10).map((p, i) => (
            <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-colors">
              <td className="py-2 pr-4 font-medium" style={{ color: '#F0E6D3' }}>{p.name || p.planet}</td>
              <td className="py-2 pr-4 text-[#C5A059]">{p.sign || p.rashi}</td>
              <td className="py-2 pr-4 text-[#B8B0C8]/70">{p.house ? `Maison ${p.house}` : '—'}</td>
              <td className="py-2 text-[#B8B0C8]/50">{p.degree ? `${Number(p.degree).toFixed(1)}°` : '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default function AstrologieVedique() {
  const { isAuthenticated, user, token } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('natal');
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState({});
  const [errors, setErrors] = useState({});

  const authHeaders = { Authorization: `Bearer ${token}` };

  const fetchData = async (key, endpoint) => {
    if (results[key] || loading[key]) return;
    setLoading(prev => ({ ...prev, [key]: true }));
    setErrors(prev => ({ ...prev, [key]: '' }));
    try {
      const res = await axios.post(`${API_URL}/api/astrology/v3/${endpoint}`, {}, { headers: authHeaders });
      setResults(prev => ({ ...prev, [key]: res.data }));
    } catch (e) {
      setErrors(prev => ({ ...prev, [key]: 'Données temporairement indisponibles.' }));
    } finally {
      setLoading(prev => ({ ...prev, [key]: false }));
    }
  };

  useEffect(() => {
    if (isAuthenticated && user?.birth_date) {
      fetchData('natal', 'vedic/natal');
      fetchData('nakshatra', 'vedic/nakshatra');
      fetchData('dasha', 'vedic/dasha');
    }
  }, [isAuthenticated, user?.birth_date]);

  useEffect(() => {
    if (isAuthenticated && user?.birth_date) {
      if (activeTab === 'navamsa') fetchData('navamsa', 'vedic/navamsa');
      if (activeTab === 'divisional') fetchData('divisional', 'vedic/divisional-charts');
    }
  }, [activeTab, isAuthenticated, user?.birth_date]);

  const tabs = [
    { id: 'natal', label: 'Kundli', icon: Star },
    { id: 'nakshatra', label: 'Nakshatra', icon: Moon },
    { id: 'dasha', label: 'Dasha', icon: Clock },
    { id: 'navamsa', label: 'Navamsa D9', icon: Sun },
    { id: 'divisional', label: 'Charts D1-D60', icon: Layers },
  ];

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0C0918' }}>
        <div className="text-center px-6">
          <p className="text-[#B8B0C8] mb-4">Connectez-vous pour accéder à votre astrologie védique.</p>
          <button onClick={() => navigate('/connexion')} className="btn-mystical">Se connecter</button>
        </div>
      </div>
    );
  }

  if (!user?.birth_date) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0C0918' }}>
        <div className="text-center px-6">
          <p className="text-[#B8B0C8] mb-4">Complétez votre profil astral pour accéder au Kundli védique.</p>
          <button onClick={() => navigate('/formulaire')} className="btn-mystical">Compléter mon profil</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ background: '#0C0918' }}>
      <div className="max-w-3xl mx-auto px-4 py-8">
        {/* Header */}
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-[#B8B0C8]/60 hover:text-[#C5A059] transition-colors mb-6 text-sm">
          <ArrowLeft className="w-4 h-4" /> Retour
        </button>

        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-3">
            <Sparkles className="w-6 h-6 text-[#C5A059]" strokeWidth={1.5} />
            <h1 className="text-3xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
              Astrologie Védique
            </h1>
            <Sparkles className="w-6 h-6 text-[#C5A059]" strokeWidth={1.5} />
          </div>
          <p className="text-[#B8B0C8]/70 text-sm font-light">
            Votre Kundli (thème natal védique) — Nakshatra, Dasha, Navamsa — Précision Swiss Ephemeris
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-all flex-shrink-0"
                style={{
                  background: activeTab === tab.id ? 'rgba(197,160,89,0.2)' : 'rgba(255,255,255,0.05)',
                  color: activeTab === tab.id ? '#C5A059' : '#B8B0C8',
                  border: `1px solid ${activeTab === tab.id ? 'rgba(197,160,89,0.4)' : 'rgba(255,255,255,0.1)'}`,
                }}>
                <Icon className="w-3.5 h-3.5" strokeWidth={1.5} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Contenu par onglet */}
        {activeTab === 'natal' && (
          <Section title="Kundli — Thème Natal Védique" icon={Star} testId="vedic-natal">
            {loading.natal ? (
              <div className="flex items-center gap-2 text-[#C5A059]/70 text-sm"><Loader2 className="w-4 h-4 animate-spin" /> Calcul du Kundli…</div>
            ) : errors.natal ? (
              <p className="text-red-400/70 text-sm">{errors.natal}</p>
            ) : results.natal ? (
              <>
                {results.natal.summary && <p className="text-[#B8B0C8]/80 text-sm mb-4 font-light leading-relaxed">{results.natal.summary}</p>}
                <PlanetTable data={results.natal} />
                {results.natal.ascendant && (
                  <div className="mt-4 rounded-lg p-3" style={{ background: 'rgba(167,139,250,0.1)', border: '1px solid rgba(167,139,250,0.2)' }}>
                    <span className="text-xs text-[#a78bfa]">Ascendant védique</span>
                    <p className="text-[#F0E6D3] font-medium">{results.natal.ascendant}</p>
                  </div>
                )}
              </>
            ) : null}
          </Section>
        )}

        {activeTab === 'nakshatra' && (
          <Section title="Nakshatra de Naissance" icon={Moon} testId="vedic-nakshatra">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Votre mansion lunaire védique — archétype profond, nature intérieure.</p>
            {loading.nakshatra ? (
              <div className="flex items-center gap-2 text-[#C5A059]/70 text-sm"><Loader2 className="w-4 h-4 animate-spin" /> Calcul du Nakshatra…</div>
            ) : errors.nakshatra ? (
              <p className="text-red-400/70 text-sm">{errors.nakshatra}</p>
            ) : results.nakshatra ? (
              <NakshatraCard data={results.nakshatra} />
            ) : null}
          </Section>
        )}

        {activeTab === 'dasha' && (
          <Section title="Vimshottari Dasha — Périodes de Vie" icon={Clock} testId="vedic-dasha">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Les grandes périodes planétaires qui gouvernent votre vie — Mahadashas et sous-périodes.</p>
            {loading.dasha ? (
              <div className="flex items-center gap-2 text-[#C5A059]/70 text-sm"><Loader2 className="w-4 h-4 animate-spin" /> Calcul des Dashas…</div>
            ) : errors.dasha ? (
              <p className="text-red-400/70 text-sm">{errors.dasha}</p>
            ) : results.dasha ? (
              <DashaTimeline data={results.dasha} />
            ) : null}
          </Section>
        )}

        {activeTab === 'navamsa' && (
          <Section title="Navamsa D9 — Mariage & Âme" icon={Sun} testId="vedic-navamsa">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Le chart divisonnel le plus important — partenaire idéal, vocation spirituelle, destin de l'âme.</p>
            {loading.navamsa ? (
              <div className="flex items-center gap-2 text-[#C5A059]/70 text-sm"><Loader2 className="w-4 h-4 animate-spin" /> Calcul du Navamsa…</div>
            ) : errors.navamsa ? (
              <p className="text-red-400/70 text-sm">{errors.navamsa}</p>
            ) : results.navamsa ? (
              <>
                {results.navamsa.summary && <p className="text-[#B8B0C8]/80 text-sm mb-4 font-light leading-relaxed">{results.navamsa.summary}</p>}
                <PlanetTable data={results.navamsa} />
              </>
            ) : null}
          </Section>
        )}

        {activeTab === 'divisional' && (
          <Section title="Charts Divisionnels D1–D60" icon={Layers} testId="vedic-divisional">
            <p className="text-[#B8B0C8]/60 text-sm mb-4 font-light">Les 16 Shodasha Vargas — chaque domaine de vie révélé par un chart dédié.</p>
            {loading.divisional ? (
              <div className="flex items-center gap-2 text-[#C5A059]/70 text-sm"><Loader2 className="w-4 h-4 animate-spin" /> Calcul des charts divisionnels…</div>
            ) : errors.divisional ? (
              <p className="text-red-400/70 text-sm">{errors.divisional}</p>
            ) : results.divisional ? (
              <div className="grid grid-cols-2 gap-3">
                {(results.divisional.charts || results.divisional.divisional_charts || []).slice(0, 12).map((c, i) => (
                  <div key={i} className="rounded-lg p-3" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
                    <div className="text-xs text-[#C5A059] font-medium mb-1">{c.name || c.chart_name || `D${i+1}`}</div>
                    <div className="text-xs text-[#B8B0C8]/60">{c.domain || c.description || ''}</div>
                  </div>
                ))}
              </div>
            ) : null}
          </Section>
        )}

        {/* Footer */}
        <p className="text-center text-[#B8B0C8]/30 text-xs mt-8 font-light">
          Calculs védiques — Ayanamsa Lahiri — Swiss Ephemeris (NASA JPL)
        </p>
      </div>
    </div>
  );
}
