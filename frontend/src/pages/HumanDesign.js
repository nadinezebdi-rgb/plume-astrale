import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowLeft, Loader2, Zap, Circle, Diamond } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import PageHero from '@/components/PageHero';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TYPE_INFO = {
  Generator: { emoji: '⚡', color: '#4ade80', desc: 'Vous avez une énergie durable et magnétique. Attendez de répondre avant d\'agir.' },
  'Manifesting Generator': { emoji: '🌪️', color: '#f59e0b', desc: 'Multi-passionné et rapide. Répondez puis informez les autres.' },
  Projector: { emoji: '🔭', color: '#a78bfa', desc: 'Sage-guide naturel. Attendez l\'invitation pour partager votre sagesse.' },
  Manifestor: { emoji: '🔥', color: '#f87171', desc: 'Initiateur de changements. Informez les autres avant d\'agir.' },
  Reflector: { emoji: '🌙', color: '#60a5fa', desc: 'Miroir de la communauté. Attendez un cycle lunaire complet pour décider.' },
};

const CENTER_NAMES_FR = {
  head: 'Tête', ajna: 'Ajna', throat: 'Gorge', g: 'Centre G / Identité',
  heart: 'Cœur / Volonté', sacral: 'Sacré', solar: 'Plexus Solaire',
  spleen: 'Rate', root: 'Racine',
};

const CenterDot = ({ name, defined, size = 48 }) => {
  const fr = CENTER_NAMES_FR[name?.toLowerCase()] || name;
  return (
    <div className="flex flex-col items-center gap-1">
      <div className="rounded-full flex items-center justify-center"
        style={{
          width: size, height: size,
          background: defined ? 'rgba(197,160,89,0.3)' : 'rgba(255,255,255,0.06)',
          border: `2px solid ${defined ? '#C5A059' : 'rgba(255,255,255,0.2)'}`,
          color: defined ? '#C5A059' : '#B8B0C8',
        }}>
        <span className="text-xs font-medium text-center leading-tight px-1">{fr?.slice(0, 4)}</span>
      </div>
    </div>
  );
};

export default function HumanDesign() {
  const { isAuthenticated, user, token } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated || !user?.birth_date) return;
    setLoading(true);
    axios.post(`${API_URL}/api/astrology/v3/traditional/human-design`, {}, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => setData(res.data))
      .catch(() => setError('Human Design temporairement indisponible.'))
      .finally(() => setLoading(false));
  }, [isAuthenticated, user?.birth_date, token]);

  if (!isAuthenticated) return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#0C0918' }}>
      <div className="text-center px-6">
        <p className="text-[#B8B0C8] mb-4">Connectez-vous pour découvrir votre Human Design.</p>
        <button onClick={() => navigate('/connexion')} className="btn-mystical">Se connecter</button>
      </div>
    </div>
  );

  const hdType = data?.type || data?.human_design_type || '';
  const profile = data?.profile || '';
  const authority = data?.authority || data?.inner_authority || '';
  const strategy = data?.strategy || '';
  const centers = data?.centers || data?.defined_centers || [];
  const definedCenters = Array.isArray(centers) ? centers : (centers.defined || []);
  const undefinedCenters = Array.isArray(centers) ? [] : (centers.undefined || []);
  const gates = data?.gates || data?.defined_gates || [];
  const channels = data?.channels || data?.defined_channels || [];
  const notSelf = data?.not_self_theme || data?.not_self || '';
  const signatureTheme = data?.signature || data?.signature_theme || '';
  const typeInfo = TYPE_INFO[hdType] || {};

  return (
    <div className="min-h-screen" style={{ background: '#0C0918' }}>
      <div className="max-w-2xl mx-auto px-4 py-8">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-[#B8B0C8]/60 hover:text-[#C5A059] transition-colors mb-6 text-sm">
          <ArrowLeft className="w-4 h-4" /> Retour
        </button>

        <PageHero
          image="/images/astrale/image-astrale-6.jpg"
          title="Human Design"
          subtitle="Type · Profil · Autorité · Centres · Canaux · Portes"
        />

        {loading && (
          <div className="card-mystical flex items-center justify-center gap-3 py-12">
            <Loader2 className="w-6 h-6 animate-spin text-[#C5A059]" />
            <span className="text-[#B8B0C8]/70">Calcul de votre BodyGraph…</span>
          </div>
        )}

        {error && <div className="card-mystical text-center"><p className="text-red-400/70">{error}</p></div>}

        {!loading && !error && data && (
          <>
            {/* Type card */}
            {hdType && (
              <div className="card-mystical mb-5 text-center" data-testid="hd-type">
                <div className="text-4xl mb-2">{typeInfo.emoji || '✨'}</div>
                <div className="text-2xl font-semibold mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: typeInfo.color || '#C5A059' }}>
                  {hdType}
                </div>
                {profile && <div className="text-sm text-[#B8B0C8]/60 mb-3">Profil {profile}</div>}
                {typeInfo.desc && <p className="text-sm text-[#B8B0C8]/80 font-light">{typeInfo.desc}</p>}
              </div>
            )}

            {/* Strategy + Authority */}
            <div className="grid grid-cols-2 gap-4 mb-5">
              {strategy && (
                <div className="card-mystical text-center" data-testid="hd-strategy">
                  <p className="text-xs text-[#B8B0C8]/50 mb-1">Stratégie</p>
                  <Zap className="w-5 h-5 mx-auto mb-1 text-[#C5A059]" strokeWidth={1.5} />
                  <p className="text-sm font-medium" style={{ color: '#F0E6D3' }}>{strategy}</p>
                </div>
              )}
              {authority && (
                <div className="card-mystical text-center" data-testid="hd-authority">
                  <p className="text-xs text-[#B8B0C8]/50 mb-1">Autorité Intérieure</p>
                  <Circle className="w-5 h-5 mx-auto mb-1 text-[#a78bfa]" strokeWidth={1.5} />
                  <p className="text-sm font-medium" style={{ color: '#F0E6D3' }}>{authority}</p>
                </div>
              )}
            </div>

            {/* Signature / Not Self */}
            {(signatureTheme || notSelf) && (
              <div className="grid grid-cols-2 gap-4 mb-5">
                {signatureTheme && (
                  <div className="rounded-xl p-3 text-center" style={{ background: 'rgba(74,222,128,0.1)', border: '1px solid rgba(74,222,128,0.25)' }}>
                    <p className="text-xs text-[#4ade80] mb-1">Thème signature</p>
                    <p className="text-sm font-medium text-[#F0E6D3]">{signatureTheme}</p>
                  </div>
                )}
                {notSelf && (
                  <div className="rounded-xl p-3 text-center" style={{ background: 'rgba(248,113,113,0.1)', border: '1px solid rgba(248,113,113,0.25)' }}>
                    <p className="text-xs text-[#f87171] mb-1">Thème non-Soi</p>
                    <p className="text-sm font-medium text-[#F0E6D3]">{notSelf}</p>
                  </div>
                )}
              </div>
            )}

            {/* Centres définis */}
            {(definedCenters.length > 0 || undefinedCenters.length > 0) && (
              <div className="card-mystical mb-5" data-testid="hd-centers">
                <h3 className="text-lg mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                  Les 9 Centres Énergétiques
                </h3>
                <div className="grid grid-cols-3 gap-3">
                  {[...definedCenters.map(c => ({ name: typeof c === 'string' ? c : c.name, defined: true })),
                    ...undefinedCenters.map(c => ({ name: typeof c === 'string' ? c : c.name, defined: false }))
                  ].map((c, i) => (
                    <div key={i} className="flex flex-col items-center gap-1 p-2 rounded-lg"
                      style={{ background: c.defined ? 'rgba(197,160,89,0.1)' : 'rgba(255,255,255,0.04)', border: `1px solid ${c.defined ? 'rgba(197,160,89,0.3)' : 'rgba(255,255,255,0.08)'}` }}>
                      <span className="text-xs font-medium" style={{ color: c.defined ? '#C5A059' : '#B8B0C8' }}>
                        {CENTER_NAMES_FR[c.name?.toLowerCase()] || c.name}
                      </span>
                      <span className="text-xs" style={{ color: c.defined ? '#C5A059' : '#B8B0C8/40' }}>
                        {c.defined ? '● Défini' : '○ Ouvert'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Canaux */}
            {channels.length > 0 && (
              <div className="card-mystical mb-5" data-testid="hd-channels">
                <h3 className="text-lg mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                  Canaux définis <span className="text-sm text-[#B8B0C8]/40 ml-1">({channels.length})</span>
                </h3>
                <div className="grid grid-cols-2 gap-2">
                  {channels.slice(0, 8).map((ch, i) => (
                    <div key={i} className="rounded-lg px-3 py-2" style={{ background: 'rgba(167,139,250,0.1)', border: '1px solid rgba(167,139,250,0.2)' }}>
                      <p className="text-sm text-[#a78bfa]">{ch.name || ch.channel || `${ch.gate_1}–${ch.gate_2}`}</p>
                      {ch.theme && <p className="text-xs text-[#B8B0C8]/50 mt-0.5">{ch.theme}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Portes actives */}
            {gates.length > 0 && (
              <div className="card-mystical mb-5" data-testid="hd-gates">
                <h3 className="text-lg mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                  Portes actives <span className="text-sm text-[#B8B0C8]/40 ml-1">({gates.length})</span>
                </h3>
                <div className="flex flex-wrap gap-2">
                  {gates.slice(0, 20).map((g, i) => {
                    const num = typeof g === 'number' ? g : (g.number || g.gate);
                    const name = typeof g === 'object' ? (g.name || g.hexagram || '') : '';
                    return (
                      <div key={i} className="rounded-lg px-3 py-2 text-center" style={{ background: 'rgba(197,160,89,0.08)', border: '1px solid rgba(197,160,89,0.2)' }}>
                        <p className="text-sm font-medium text-[#C5A059]">{num}</p>
                        {name && <p className="text-xs text-[#B8B0C8]/50">{name}</p>}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Description générale */}
            {data.description && (
              <div className="card-mystical">
                <p className="text-[#B8B0C8]/80 text-sm font-light leading-relaxed">{data.description}</p>
              </div>
            )}
          </>
        )}

        <p className="text-center text-[#B8B0C8]/30 text-xs mt-8 font-light">
          Human Design — Synthèse Astrologie · I Ching · Kabbale · Chakras
        </p>
      </div>
    </div>
  );
}
