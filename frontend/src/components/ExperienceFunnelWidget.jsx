import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import { RefreshCw, Loader2, TrendingUp, TrendingDown, Users, Coins, MousePointerClick } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Widget Admin — Experience Funnel A/B (Feb 2026)
 *
 * Compare la conversion Homepage vs Experience (route /experience) sur les
 * KPI qui pilotent le ROI publicitaire :
 *   - Visiteurs uniques par variant
 *   - Taux à chaque étape du funnel (intent, tarot, feather, signup, purchase)
 *   - Revenu total EUR
 *   - **CA / visiteur** (le KPI qui décide le budget publicitaire)
 *
 * Data source : Mongo `experience_funnel_events` alimenté par `sendFunnelEvent`
 * dans lib/analytics.js. Aucune PII stockée — visitor_id anonyme + variant.
 */

// Ordre des étapes affichées dans le tableau
const STEPS = [
  { key: 'experience_visit',       label: 'Visite',              gold: 'entrée' },
  { key: 'intent_selected',        label: 'Intention',           gold: 'qualification' },
  { key: 'tarot_card_selected',    label: 'Carte tirée',         gold: 'micro-exp.' },
  { key: 'tarot_continue_clicked', label: 'Continue',            gold: 'engagement' },
  { key: 'feather_completed',      label: 'Plume finale',        gold: 'signature' },
  { key: 'signup_started',         label: 'Signup — début',      gold: 'lead' },
  { key: 'signup_completed',       label: 'Signup — complet',    gold: 'compte créé' },
  { key: 'credit_purchase',        label: 'Achat',               gold: 'CA' },
];

const PERIODS = [
  { hours: 24,   label: '24 h' },
  { hours: 168,  label: '7 j' },
  { hours: 720,  label: '30 j' },
];

function formatPct(n) {
  if (!n && n !== 0) return '—';
  return `${(n * 100).toFixed(1)} %`;
}

function formatEur(n) {
  if (n === null || n === undefined) return '—';
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(n);
}

export default function ExperienceFunnelWidget({ token }) {
  const [hours, setHours] = useState(168);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const r = await axios.get(`${API}/api/admin/experience/funnel?hours=${hours}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setData(r.data);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }, [token, hours]);

  useEffect(() => { load(); }, [load]);

  const variants = data?.variants || {};
  const homepage = variants.homepage || null;
  const experience = variants.experience || null;

  // Compare CA/visiteur — le KPI le plus important commercialement
  const rpvHome = homepage?.revenue_per_visitor_eur ?? null;
  const rpvExp = experience?.revenue_per_visitor_eur ?? null;
  const rpvWinner = useMemo(() => {
    if (rpvHome === null || rpvExp === null) return null;
    if (rpvHome === rpvExp) return 'tie';
    return rpvExp > rpvHome ? 'experience' : 'homepage';
  }, [rpvHome, rpvExp]);

  return (
    <div
      data-testid="experience-funnel-widget"
      style={{
        marginTop: 24,
        padding: 20,
        borderRadius: 12,
        background: 'rgba(11, 15, 45, 0.55)',
        border: '1px solid rgba(216, 183, 106, 0.22)',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <p style={{
            fontFamily: '"Inter", sans-serif', fontSize: 10, letterSpacing: '0.28em',
            textTransform: 'uppercase', color: '#D8B76A', margin: 0,
          }}>
            Funnel A/B · Homepage vs Experience
          </p>
          <h3 style={{
            fontFamily: '"Cormorant Garamond", serif', fontStyle: 'italic',
            color: '#F4EFE6', fontSize: 22, margin: '4px 0 0',
          }}>
            Revenu par visiteur — comparaison des variants
          </h3>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          {PERIODS.map((p) => (
            <button
              key={p.hours}
              type="button"
              onClick={() => setHours(p.hours)}
              data-testid={`funnel-period-${p.hours}h`}
              style={{
                padding: '6px 14px', border: '1px solid rgba(216,183,106,0.35)',
                background: hours === p.hours ? 'rgba(216,183,106,0.18)' : 'transparent',
                color: '#F4EFE6', fontFamily: '"Inter", sans-serif',
                fontSize: 11, letterSpacing: '0.14em', textTransform: 'uppercase',
                borderRadius: 2, cursor: 'pointer',
              }}
            >
              {p.label}
            </button>
          ))}
          <button
            type="button"
            onClick={load}
            disabled={loading}
            data-testid="funnel-refresh"
            style={{
              padding: 8, background: 'transparent', border: '1px solid rgba(216,183,106,0.35)',
              color: '#F4EFE6', borderRadius: 2, cursor: 'pointer',
            }}
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {error && (
        <div style={{
          padding: 12, borderRadius: 4, background: 'rgba(239,68,68,0.1)',
          border: '1px solid rgba(239,68,68,0.35)', color: '#fca5a5',
          fontSize: 12, marginBottom: 12,
        }} data-testid="funnel-error">
          {error}
        </div>
      )}

      {/* KPI cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 20 }}>
        <KpiCard
          testid="kpi-visitors-home"
          icon={<Users className="w-4 h-4" />}
          label="Visiteurs Homepage"
          value={homepage?.visitors ?? 0}
        />
        <KpiCard
          testid="kpi-visitors-exp"
          icon={<Users className="w-4 h-4" />}
          label="Visiteurs Experience"
          value={experience?.visitors ?? 0}
        />
        <KpiCard
          testid="kpi-rpv-home"
          icon={<Coins className="w-4 h-4" />}
          label="CA / visiteur Homepage"
          value={rpvHome !== null ? formatEur(rpvHome) : '—'}
          highlight={rpvWinner === 'homepage'}
        />
        <KpiCard
          testid="kpi-rpv-exp"
          icon={<Coins className="w-4 h-4" />}
          label="CA / visiteur Experience"
          value={rpvExp !== null ? formatEur(rpvExp) : '—'}
          highlight={rpvWinner === 'experience'}
        />
      </div>

      {/* Funnel table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }} data-testid="funnel-table">
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(216,183,106,0.35)' }}>
              <th style={thStyle}>Étape</th>
              <th style={{ ...thStyle, textAlign: 'right' }}>Homepage</th>
              <th style={{ ...thStyle, textAlign: 'right' }}>Experience</th>
              <th style={{ ...thStyle, textAlign: 'right' }}>Δ</th>
            </tr>
          </thead>
          <tbody>
            {STEPS.map((s) => {
              const h = homepage?.steps?.[s.key] ?? 0;
              const e = experience?.steps?.[s.key] ?? 0;
              const hVisits = homepage?.visitors || 0;
              const eVisits = experience?.visitors || 0;
              const hRate = hVisits ? h / hVisits : 0;
              const eRate = eVisits ? e / eVisits : 0;
              const winning = eRate > hRate;
              return (
                <tr key={s.key} data-testid={`funnel-row-${s.key}`} style={{ borderBottom: '1px solid rgba(216,183,106,0.10)' }}>
                  <td style={tdStyle}>
                    <div style={{ fontFamily: '"Cormorant Garamond", serif', fontStyle: 'italic', color: '#F4EFE6', fontSize: 15 }}>
                      {s.label}
                    </div>
                    <div style={{ fontFamily: '"Inter", sans-serif', fontSize: 9.5, letterSpacing: '0.22em', textTransform: 'uppercase', color: 'rgba(216,183,106,0.55)', marginTop: 2 }}>
                      {s.gold}
                    </div>
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right', color: '#F4EFE6' }}>
                    <div>{h}</div>
                    <div style={{ fontSize: 10.5, color: 'rgba(244,239,230,0.5)' }}>{formatPct(hRate)}</div>
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right', color: '#F4EFE6' }}>
                    <div>{e}</div>
                    <div style={{ fontSize: 10.5, color: 'rgba(244,239,230,0.5)' }}>{formatPct(eRate)}</div>
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right' }}>
                    {hRate === 0 && eRate === 0 ? (
                      <span style={{ color: 'rgba(244,239,230,0.35)' }}>—</span>
                    ) : winning ? (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: '#10B981' }}>
                        <TrendingUp className="w-3.5 h-3.5" />
                        +{formatPct(eRate - hRate)}
                      </span>
                    ) : (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: '#EF4444' }}>
                        <TrendingDown className="w-3.5 h-3.5" />
                        {formatPct(eRate - hRate)}
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p style={{ marginTop: 12, fontSize: 10.5, color: 'rgba(244,239,230,0.45)', fontFamily: '"Inter", sans-serif' }}>
        Données Mongo `experience_funnel_events` · période {hours}h · alimenté par consentement RGPD accepté.
        Aucune PII stockée · visitor_id anonyme.
      </p>
    </div>
  );
}

function KpiCard({ icon, label, value, highlight, testid }) {
  return (
    <div
      data-testid={testid}
      style={{
        padding: 12, borderRadius: 6,
        background: highlight ? 'rgba(216,183,106,0.10)' : 'rgba(255,255,255,0.02)',
        border: `1px solid ${highlight ? 'rgba(216,183,106,0.45)' : 'rgba(216,183,106,0.15)'}`,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#D8B76A', marginBottom: 6 }}>
        {icon}
        <span style={{ fontFamily: '"Inter", sans-serif', fontSize: 9.5, letterSpacing: '0.22em', textTransform: 'uppercase' }}>
          {label}
        </span>
      </div>
      <div style={{ fontFamily: '"Cormorant Garamond", serif', color: '#F4EFE6', fontSize: 24, lineHeight: 1 }}>
        {value}
      </div>
    </div>
  );
}

const thStyle = {
  fontFamily: '"Inter", sans-serif', fontSize: 9.5, letterSpacing: '0.22em',
  textTransform: 'uppercase', color: 'rgba(216,183,106,0.75)',
  textAlign: 'left', padding: '10px 8px', fontWeight: 400,
};
const tdStyle = {
  padding: '10px 8px', verticalAlign: 'top',
};
