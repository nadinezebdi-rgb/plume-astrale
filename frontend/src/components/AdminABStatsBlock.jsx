import React, { useCallback, useEffect, useState } from 'react';
import { TrendingUp, Loader2 } from 'lucide-react';

const EXPERIMENT = 'synastrie_exit_intent';

/**
 * Bloc de stats A/B lu depuis GET /api/admin/ab-stats (first-party tracking).
 * Affiche shown/dismissed/converted + taux de conversion par variante.
 */
export default function AdminABStatsBlock({ backend, token }) {
  const [period, setPeriod] = useState('30d');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${backend}/api/admin/ab-stats?experiment=${EXPERIMENT}&period=${period}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      const json = await res.json();
      setData(json);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [backend, token, period]);

  useEffect(() => { load(); }, [load]);

  const winner = data?.variants?.length
    ? [...data.variants].sort((a, b) => b.conversion_rate - a.conversion_rate)[0]
    : null;

  return (
    <section
      data-testid="admin-ab-stats-block"
      style={{
        marginBottom: 32,
        padding: '20px 22px',
        background: 'linear-gradient(180deg, rgba(212,175,55,0.06), rgba(255,255,255,0.02))',
        border: '1px solid rgba(212,175,55,0.25)',
        borderRadius: 8,
      }}
    >
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, marginBottom: 16, flexWrap: 'wrap' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 10 }}>
          <TrendingUp size={18} style={{ color: 'var(--plume-gold)' }} strokeWidth={1.5} />
          <div>
            <div style={{ fontFamily: 'Cinzel, serif', fontSize: 10.5, letterSpacing: '0.22em', textTransform: 'uppercase', color: 'var(--plume-gold)' }}>
              A/B Experiment
            </div>
            <h2 style={{ fontFamily: '"Fraunces", serif', fontWeight: 400, fontSize: 20, margin: '2px 0 0' }}>
              Exit-intent synastrie — conversion variantes
            </h2>
          </div>
        </div>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          data-testid="ab-stats-period"
          style={{
            padding: '6px 10px', background: 'rgba(15,26,60,0.65)',
            border: '1px solid rgba(212,175,55,0.3)', color: 'var(--plume-ivory)',
            borderRadius: 4, fontFamily: 'Inter, sans-serif', fontSize: 12.5, cursor: 'pointer',
          }}
        >
          <option value="7d">7 derniers jours</option>
          <option value="30d">30 derniers jours</option>
          <option value="all">Tout</option>
        </select>
      </header>

      {loading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'rgba(244,239,230,0.6)', fontSize: 13 }}>
          <Loader2 size={14} className="animate-spin" /> Chargement…
        </div>
      )}

      {error && (
        <div style={{ color: '#F87171', fontSize: 13 }}>Erreur : {error}</div>
      )}

      {!loading && !error && data?.migration_needed && (
        <div data-testid="ab-stats-migration-hint" style={{
          padding: '12px 14px', background: 'rgba(246,199,122,0.08)',
          border: '1px solid rgba(246,199,122,0.3)', borderRadius: 6,
          color: 'rgba(244,239,230,0.9)', fontSize: 13, lineHeight: 1.5,
        }}>
          <strong>Migration requise.</strong> La table <code>public.ab_events</code> n&apos;existe pas encore.
          Exécute <code>/app/backend/migrations/2026_02_ab_events.sql</code> dans le SQL Editor Supabase
          pour activer les stats A/B first-party.
        </div>
      )}

      {!loading && !error && !data?.migration_needed && data?.variants?.length === 0 && (
        <div data-testid="ab-stats-empty" style={{ color: 'rgba(244,239,230,0.6)', fontSize: 13 }}>
          Aucun événement enregistré sur cette période. Les stats apparaîtront dès qu&apos;un visiteur verra la modal exit-intent.
        </div>
      )}

      {!loading && data?.variants?.length > 0 && (
        <div data-testid="ab-stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 14 }}>
          {data.variants.map((v) => {
            const isWinner = winner && v.variant === winner.variant && v.conversion_rate > 0;
            return (
              <article
                key={v.variant}
                data-testid={`ab-stats-variant-${v.variant}`}
                style={{
                  position: 'relative',
                  padding: '18px 18px 16px',
                  background: 'rgba(11,26,46,0.55)',
                  border: `1px solid ${isWinner ? 'rgba(74,222,128,0.5)' : 'rgba(244,239,230,0.1)'}`,
                  borderRadius: 6,
                }}
              >
                {isWinner && (
                  <span style={{
                    position: 'absolute', top: -10, right: 12,
                    padding: '2px 10px', borderRadius: 999,
                    background: '#4ADE80', color: '#0F1A3C',
                    fontSize: 10, fontWeight: 600, letterSpacing: '0.12em', textTransform: 'uppercase',
                    fontFamily: 'Inter, sans-serif',
                  }}>
                    Meilleure
                  </span>
                )}
                <div style={{ fontFamily: '"Fraunces", serif', fontSize: 22, color: '#F5EEE0', marginBottom: 4 }}>
                  Variante {v.variant}
                </div>
                <div style={{ fontSize: 28, fontFamily: '"Fraunces", serif', color: 'var(--plume-gold)', marginBottom: 2 }}>
                  {v.conversion_rate}%
                </div>
                <div style={{ fontSize: 11, color: 'rgba(244,239,230,0.55)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 12 }}>
                  Taux de conversion
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, fontSize: 12 }}>
                  <StatCell label="Vues" value={v.shown} />
                  <StatCell label="Fermées" value={v.dismissed} />
                  <StatCell label="Converties" value={v.converted} highlight />
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

function StatCell({ label, value, highlight }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 18, fontWeight: 500, color: highlight ? '#4ADE80' : '#F5EEE0' }}>
        {value}
      </div>
      <div style={{ fontSize: 10, color: 'rgba(244,239,230,0.5)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
        {label}
      </div>
    </div>
  );
}
