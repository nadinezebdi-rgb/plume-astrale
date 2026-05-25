import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Sparkles, Sun, Moon, ArrowUp } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const ICONS = {
  sun: Sun,
  moon: Moon,
  ascendant: ArrowUp,
};

const PlanetCard = ({ id, data }) => {
  const Icon = ICONS[id];
  return (
    <div
      style={{
        flex: 1,
        minWidth: 200,
        padding: '18px 16px',
        borderRadius: 14,
        background: 'linear-gradient(180deg, rgba(8,10,28,0.85) 0%, rgba(20,17,48,0.75) 100%)',
        border: '1px solid rgba(212,180,106,0.40)',
        backdropFilter: 'blur(10px)',
        position: 'relative',
        overflow: 'hidden',
      }}
      data-testid={`natal-card-${id}`}
    >
      {/* Glyphe en grand en arrière-plan */}
      <div style={{
        position: 'absolute', right: -8, bottom: -22,
        fontSize: 92, color: 'rgba(212,180,106,0.07)', lineHeight: 1, fontFamily: 'serif', pointerEvents: 'none',
      }}>
        {data.symbol}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, position: 'relative' }}>
        {Icon && <Icon style={{ width: 14, height: 14, color: '#D4B46A' }} strokeWidth={1.5} />}
        <span style={{
          fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase',
          color: 'rgba(212,180,106,0.7)', fontFamily: 'Cinzel, serif',
        }}>
          {data.label}
        </span>
      </div>

      <div style={{
        fontFamily: 'Cormorant Garamond, serif', fontSize: 28, lineHeight: 1.1,
        color: '#F4E4BC', marginBottom: 4, position: 'relative',
      }}>
        {data.sign} <span style={{ fontSize: 22, opacity: 0.6 }}>{data.symbol}</span>
      </div>

      <div style={{
        fontSize: 11, color: 'rgba(255,255,255,0.55)', marginBottom: 8,
        fontStyle: 'italic', position: 'relative',
      }}>
        {data.description}
      </div>

      <div style={{
        fontSize: 10.5, color: 'rgba(212,180,106,0.85)', position: 'relative',
        letterSpacing: '0.04em',
      }}>
        {data.theme}
        {data.house ? <span style={{ opacity: 0.5 }}> · Maison {data.house}</span> : null}
      </div>
    </div>
  );
};

export default function NatalEssentials({ token, prenom: prenomProp }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    if (!token) { setLoading(false); return; }
    let cancelled = false;
    axios.get(`${API}/api/natal/essentials`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => { if (!cancelled) setData(r.data); })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [token]);

  if (loading || !data || !data.has_data) return null;

  const { essentials } = data;
  const prenom = data.prenom || prenomProp;

  return (
    <div
      style={{
        maxWidth: 920, margin: '0 auto 16px', padding: '0 16px',
        animation: 'fadeIn 0.6s ease',
      }}
      data-testid="natal-essentials-panel"
    >
      <div
        style={{
          padding: '18px 20px 20px',
          borderRadius: 16,
          background: 'linear-gradient(180deg, rgba(6,8,26,0.85) 0%, rgba(11,14,40,0.75) 100%)',
          border: '1px solid rgba(212,180,106,0.35)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
          backdropFilter: 'blur(20px)',
        }}
      >
        {/* En-tête */}
        <div
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: collapsed ? 0 : 14, gap: 12, flexWrap: 'wrap' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1, minWidth: 0 }}>
            <Sparkles style={{ width: 14, height: 14, color: '#D4B46A', flexShrink: 0 }} strokeWidth={1.5} />
            <div style={{ minWidth: 0 }}>
              <div style={{
                fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase',
                color: 'rgba(212,180,106,0.7)', fontFamily: 'Cinzel, serif', marginBottom: 2,
              }}>
                Comment Plume t'écoute
              </div>
              <div style={{
                fontFamily: 'Cormorant Garamond, serif', fontSize: 17, color: '#F4E4BC', lineHeight: 1.3,
              }}>
                {prenom ? `${prenom}, ta ` : 'Ta '}consultation est nourrie par ton thème natal réel
              </div>
            </div>
          </div>
          <button
            onClick={() => setCollapsed(!collapsed)}
            style={{
              background: 'transparent', border: '1px solid rgba(212,180,106,0.3)',
              color: 'rgba(212,180,106,0.8)', fontSize: 10, letterSpacing: '0.1em',
              padding: '6px 14px', borderRadius: 999, cursor: 'pointer',
              textTransform: 'uppercase', fontFamily: 'Cinzel, serif',
            }}
            data-testid="natal-toggle-btn"
          >
            {collapsed ? 'Voir' : 'Masquer'}
          </button>
        </div>

        {!collapsed && (
          <>
            {/* Cartes Soleil / Lune / Ascendant */}
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 12 }}>
              {essentials.sun && <PlanetCard id="sun" data={essentials.sun} />}
              {essentials.moon && <PlanetCard id="moon" data={essentials.moon} />}
              {essentials.ascendant && <PlanetCard id="ascendant" data={essentials.ascendant} />}
            </div>

            {/* Mention pédagogique */}
            <div style={{
              fontSize: 11, color: 'rgba(255,255,255,0.45)', lineHeight: 1.5,
              fontStyle: 'italic', textAlign: 'center', paddingTop: 6,
              borderTop: '1px solid rgba(212,180,106,0.08)',
            }}>
              Chaque réponse de Plume est calibrée sur ces 3 axes — pas un assistant générique, mais une voix qui connaît
              déjà <span style={{ color: '#D4B46A' }}>ton ciel de naissance</span>.
            </div>
          </>
        )}
      </div>

      <style>{`
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </div>
  );
}
