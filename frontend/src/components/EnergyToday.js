import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Sparkles, Zap, Heart, ShieldAlert, Lightbulb, RefreshCcw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL;

const SECTION_META = {
  dominante:  { icon: Zap,         color: '#D4AF37', titre: 'Énergie dominante' },
  relationnel:{ icon: Heart,       color: '#E0A6C8', titre: 'Relationnel' },
  attention:  { icon: ShieldAlert, color: '#E8C766', titre: 'Attention' },
  opportunite:{ icon: Lightbulb,   color: '#A6D6E0', titre: 'Opportunité' },
};

function EnergyCard({ id, data }) {
  const meta = SECTION_META[id];
  const Icon = meta.icon;
  return (
    <div
      style={{
        padding: '20px 22px',
        borderRadius: 16,
        background: 'linear-gradient(180deg, rgba(6,8,26,0.85) 0%, rgba(11,14,40,0.75) 100%)',
        border: `1px solid ${meta.color}40`,
        backdropFilter: 'blur(20px)',
        boxShadow: '0 4px 24px rgba(0,0,0,0.3)',
      }}
      data-testid={`energy-card-${id}`}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
        <Icon style={{ width: 16, height: 16, color: meta.color }} strokeWidth={1.5} />
        <span style={{
          fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase',
          color: 'rgba(255,255,255,0.6)', fontFamily: 'Cinzel, serif',
        }}>
          {meta.titre}
        </span>
      </div>
      <div style={{
        fontFamily: 'Cormorant Garamond, serif', fontSize: 26, lineHeight: 1.1,
        color: meta.color, marginBottom: 10, fontWeight: 400,
      }}>
        {data?.label || '—'}
      </div>
      <p style={{ fontSize: 13, lineHeight: 1.55, color: 'rgba(255,255,255,0.78)', margin: 0 }}>
        {data?.text}
      </p>
    </div>
  );
}

function GuestCTA() {
  const navigate = useNavigate();
  return (
    <div
      style={{
        maxWidth: 540, margin: '0 auto', padding: '32px 26px', textAlign: 'center',
        borderRadius: 18,
        background: 'linear-gradient(180deg, rgba(6,8,26,0.85) 0%, rgba(11,14,40,0.7) 100%)',
        border: '1px solid rgba(212,175,55,0.3)',
      }}
      data-testid="energy-guest-cta"
    >
      <Sparkles style={{ width: 24, height: 24, color: '#D4AF37', margin: '0 auto 12px', display: 'block' }} strokeWidth={1.5} />
      <h2 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 28, color: '#F4E4BC', marginBottom: 10, fontWeight: 400 }}>
        Découvre ton énergie du jour
      </h2>
      <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.7)', marginBottom: 22, lineHeight: 1.6 }}>
        Une lecture personnalisée chaque matin, basée sur ton thème natal et les mouvements planétaires actuels.
      </p>
      <button onClick={() => navigate('/inscription')} style={{
        padding: '12px 28px', borderRadius: 999, border: 'none',
        background: '#D4AF37', color: '#0F1230',
        fontFamily: 'Cinzel, serif', fontSize: 11, fontWeight: 600,
        letterSpacing: '0.18em', textTransform: 'uppercase', cursor: 'pointer',
      }} data-testid="energy-register-btn">
        Recevoir mes 20 crédits
      </button>
    </div>
  );
}

export default function EnergyToday({ compact = false }) {
  const { isAuthenticated, token, user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  useEffect(() => {
    if (!isAuthenticated || !token) return;
    let cancelled = false;
    setLoading(true);
    axios.get(`${API}/api/energy/today`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => { if (!cancelled) { setData(r.data); setErr(null); } })
      .catch(e => { if (!cancelled) setErr(e.response?.data?.message || 'Service indisponible'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [isAuthenticated, token]);

  if (!isAuthenticated) return <GuestCTA />;

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 40 }} data-testid="energy-loading">
        <RefreshCcw className="animate-spin" style={{ width: 22, height: 22, color: '#D4AF37', margin: '0 auto 12px', display: 'block' }} />
        <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.6)' }}>Plume consulte les astres de ta journée...</p>
      </div>
    );
  }

  if (err || !data?.success) {
    return (
      <div style={{ textAlign: 'center', padding: 30, color: 'rgba(255,255,255,0.7)', fontSize: 14 }} data-testid="energy-error">
        {err || data?.message || 'Energie du jour indisponible. Reviens demain.'}
        {!data?.has_data && (
          <p style={{ fontSize: 12, marginTop: 8, color: 'rgba(212,175,55,0.7)' }}>
            Complète ta date, heure et lieu de naissance pour activer cette lecture.
          </p>
        )}
      </div>
    );
  }

  const today = new Date(data.date || Date.now()).toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' });
  const prenom = data.prenom || user?.prenom;

  return (
    <div data-testid="energy-today">
      <div style={{ textAlign: 'center', marginBottom: 20 }}>
        <div style={{
          fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase',
          color: 'rgba(212,175,55,0.75)', fontFamily: 'Cinzel, serif', marginBottom: 6,
        }}>
          {today}
        </div>
        <h2 style={{
          fontFamily: 'Cormorant Garamond, serif', fontSize: 'clamp(26px, 4vw, 34px)',
          color: '#F4E4BC', marginBottom: 8, fontWeight: 400, lineHeight: 1.2,
        }}>
          {prenom ? `${prenom}, ton énergie aujourd\u2019hui` : 'Ton énergie aujourd\u2019hui'}
        </h2>
        <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.55)', fontStyle: 'italic' }}>
          Lecture nourrie par ton thème natal et les transits du jour
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: compact ? '1fr' : 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: 14,
        maxWidth: compact ? 600 : 980,
        margin: '0 auto',
      }}>
        <EnergyCard id="dominante" data={data.dominante} />
        <EnergyCard id="relationnel" data={data.relationnel} />
        <EnergyCard id="attention" data={data.attention} />
        <EnergyCard id="opportunite" data={data.opportunite} />
      </div>
    </div>
  );
}
