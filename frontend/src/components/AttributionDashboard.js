import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { RefreshCw, TrendingUp, Users, Euro, Target, Loader2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const RANGES = [
  { key: 7, label: '7 jours' },
  { key: 30, label: '30 jours' },
  { key: 90, label: '90 jours' },
  { key: 365, label: '1 an' },
];

const eur = (cents) => (cents == null ? '0,00 €' : (cents / 100).toFixed(2).replace('.', ',') + ' €');
const pct = (v) => (v == null ? '—' : `${v}%`);
const fmtDate = (iso) => {
  if (!iso) return '';
  try { return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }); }
  catch { return iso.slice(0, 10); }
};

/**
 * AttributionDashboard — panel admin des KPI d'attribution UTM.
 * Interroge /api/admin/analytics/attribution?days=N
 */
export default function AttributionDashboard() {
  const { token } = useAuth();
  const [days, setDays] = useState(30);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchData = useCallback(async () => {
    if (!token) return;
    setLoading(true); setError('');
    try {
      const r = await axios.get(`${API}/api/admin/analytics/attribution`, {
        params: { days },
        headers: { Authorization: `Bearer ${token}` },
      });
      setData(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || 'Erreur chargement analytics');
    } finally {
      setLoading(false);
    }
  }, [days, token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  return (
    <div className="rounded-2xl p-6"
      style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(197,160,89,0.20)', backdropFilter: 'blur(12px)' }}
      data-testid="attribution-dashboard">

      {/* Header + range picker */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4" style={{ color: '#C5A059' }} strokeWidth={1.5} />
            <h2 className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F4E8D2', fontWeight: 400 }}>
              KPI Attribution
            </h2>
          </div>
          <p className="text-[11px] opacity-60 mt-1" style={{ color: '#F4E8D2' }}>
            Suivi des ventes par campagne UTM · leads · taux de conversion · A/B testing
          </p>
        </div>
        <div className="flex gap-1.5">
          {RANGES.map(r => (
            <button key={r.key} onClick={() => setDays(r.key)}
              className="text-[10px] uppercase px-3 py-1.5 rounded-full transition-all"
              style={{
                border: '1px solid',
                borderColor: days === r.key ? '#C5A059' : 'rgba(197,160,89,0.25)',
                color: days === r.key ? '#0C0918' : '#C5A059',
                background: days === r.key ? '#C5A059' : 'transparent',
                letterSpacing: '0.12em',
              }}
              data-testid={`analytics-range-${r.key}`}>
              {r.label}
            </button>
          ))}
          <button onClick={fetchData} disabled={loading}
            className="text-[10px] uppercase px-3 py-1.5 rounded-full transition-all disabled:opacity-40"
            style={{ border: '1px solid rgba(197,160,89,0.25)', color: '#C5A059', letterSpacing: '0.12em' }}
            data-testid="analytics-refresh-btn">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {loading && !data && (
        <div className="py-12 flex items-center justify-center">
          <Loader2 className="w-6 h-6 animate-spin" style={{ color: '#C5A059' }} />
        </div>
      )}

      {error && (
        <div className="p-4 rounded-lg text-sm mb-4"
          style={{ background: 'rgba(255,80,80,0.10)', color: '#ffb0b0', border: '1px solid rgba(255,80,80,0.30)' }}>
          {error}
        </div>
      )}

      {data && (
        <>
          {/* Totals KPI cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            <KpiCard icon={Users} label="Leads" value={data.totals.leads} testid="kpi-leads" />
            <KpiCard icon={Target} label="Achats" value={data.totals.purchases} testid="kpi-purchases" />
            <KpiCard icon={Euro} label="Revenu" value={eur(data.totals.revenue_cents)} accent testid="kpi-revenue" />
            <KpiCard icon={TrendingUp} label="Taux conv." value={pct(data.funnel.purchase_rate)} testid="kpi-cvr" />
          </div>

          {/* Grid layout by_campaign + by_source */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <Section title="Par campagne" empty="Aucune campagne trackée pour l'instant.">
              {(data.by_campaign || []).length > 0 && (
                <table className="w-full text-xs" data-testid="table-campaigns">
                  <thead>
                    <tr style={{ color: '#C5A059', opacity: 0.7 }}>
                      <Th>Source / Campagne</Th>
                      <Th right>Leads</Th>
                      <Th right>Achats</Th>
                      <Th right>CVR</Th>
                      <Th right>Revenu</Th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.by_campaign.map((c, i) => (
                      <tr key={i} style={{ borderTop: '1px solid rgba(197,160,89,0.10)' }}
                          data-testid={`row-campaign-${i}`}>
                        <Td>
                          <span style={{ color: '#F4E8D2' }}>{c.source || 'direct'}</span>
                          <span className="opacity-50 mx-1">/</span>
                          <span style={{ color: '#C5A059' }}>{c.campaign || 'unknown'}</span>
                        </Td>
                        <Td right>{c.leads}</Td>
                        <Td right>{c.purchases}</Td>
                        <Td right accent={c.cvr > 5}>{pct(c.cvr)}</Td>
                        <Td right accent>{eur(c.revenue_cents)}</Td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </Section>

            <Section title="Par source" empty="Pas de trafic tracké.">
              {(data.by_source || []).length > 0 && (
                <table className="w-full text-xs" data-testid="table-sources">
                  <thead>
                    <tr style={{ color: '#C5A059', opacity: 0.7 }}>
                      <Th>Source</Th>
                      <Th right>Leads</Th>
                      <Th right>Achats</Th>
                      <Th right>Revenu</Th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.by_source.map((s, i) => (
                      <tr key={i} style={{ borderTop: '1px solid rgba(197,160,89,0.10)' }}
                          data-testid={`row-source-${i}`}>
                        <Td>
                          <span style={{ color: '#F4E8D2', textTransform: 'capitalize' }}>{s.source}</span>
                        </Td>
                        <Td right>{s.leads}</Td>
                        <Td right>{s.purchases}</Td>
                        <Td right accent>{eur(s.revenue_cents)}</Td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </Section>
          </div>

          {/* A/B Content variants */}
          <Section title="A/B testing (par utm_content)"
                  empty="Pas de variantes utm_content trackées. Ajoute ?utm_content=video_01_hook_a pour comparer.">
            {(data.by_content || []).length > 0 && (
              <table className="w-full text-xs" data-testid="table-content">
                <thead>
                  <tr style={{ color: '#C5A059', opacity: 0.7 }}>
                    <Th>Contenu</Th>
                    <Th>Campagne</Th>
                    <Th right>Achats</Th>
                    <Th right>Revenu</Th>
                  </tr>
                </thead>
                <tbody>
                  {data.by_content.map((c, i) => (
                    <tr key={i} style={{ borderTop: '1px solid rgba(197,160,89,0.10)' }}
                        data-testid={`row-content-${i}`}>
                      <Td><span style={{ color: '#F4E8D2', fontFamily: 'monospace' }}>{c.content}</span></Td>
                      <Td><span className="opacity-70">{c.source} / {c.campaign}</span></Td>
                      <Td right>{c.purchases}</Td>
                      <Td right accent>{eur(c.revenue_cents)}</Td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Section>

          {/* Recent purchases */}
          <div className="mt-6">
            <Section title="Derniers achats" empty="Aucun achat sur cette période.">
              {(data.recent_purchases || []).length > 0 && (
                <table className="w-full text-xs" data-testid="table-recent">
                  <thead>
                    <tr style={{ color: '#C5A059', opacity: 0.7 }}>
                      <Th>Date</Th>
                      <Th>Email</Th>
                      <Th>Produit</Th>
                      <Th right>Montant</Th>
                      <Th>Source</Th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.recent_purchases.map((r, i) => (
                      <tr key={i} style={{ borderTop: '1px solid rgba(197,160,89,0.10)' }}
                          data-testid={`row-purchase-${i}`}>
                        <Td><span className="opacity-70">{fmtDate(r.created_at)}</span></Td>
                        <Td><span style={{ color: '#F4E8D2' }}>{r.email || '—'}</span></Td>
                        <Td><span className="opacity-70">{r.pack_id}</span></Td>
                        <Td right accent>{r.amount ? `${r.amount.toFixed(2).replace('.', ',')} €` : '—'}</Td>
                        <Td>
                          {r.utm_source ? (
                            <span style={{ color: '#C5A059' }}>
                              {r.utm_source}
                              {r.utm_campaign && <span className="opacity-70"> · {r.utm_campaign}</span>}
                            </span>
                          ) : <span className="opacity-40">direct</span>}
                        </Td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </Section>
          </div>
        </>
      )}
    </div>
  );
}

// ────────────────────────────────────────────────
// Sub-components
// ────────────────────────────────────────────────
function KpiCard({ icon: Icon, label, value, accent, testid }) {
  return (
    <div className="rounded-xl p-4"
      style={{ background: accent ? 'rgba(197,160,89,0.10)' : 'rgba(0,0,0,0.20)', border: '1px solid rgba(197,160,89,0.20)' }}
      data-testid={testid}>
      <div className="flex items-center gap-1.5 mb-2 opacity-80">
        <Icon className="w-3.5 h-3.5" style={{ color: '#C5A059' }} strokeWidth={1.5} />
        <span className="text-[10px] uppercase" style={{ color: '#C5A059', letterSpacing: '0.2em' }}>{label}</span>
      </div>
      <div className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: accent ? '#C5A059' : '#F4E8D2', fontWeight: 400 }}>
        {value}
      </div>
    </div>
  );
}

function Section({ title, children, empty }) {
  const isEmpty = React.Children.toArray(children).every(c => !c);
  return (
    <div>
      <div className="text-[10px] uppercase mb-3" style={{ color: '#C5A059', letterSpacing: '0.25em' }}>{title}</div>
      {isEmpty ? (
        <div className="rounded-lg p-4 text-xs opacity-60 text-center" style={{ background: 'rgba(0,0,0,0.20)', border: '1px dashed rgba(197,160,89,0.20)' }}>
          {empty}
        </div>
      ) : children}
    </div>
  );
}

function Th({ children, right }) {
  return <th className={`py-2 text-[10px] uppercase font-normal ${right ? 'text-right' : 'text-left'}`} style={{ letterSpacing: '0.15em' }}>{children}</th>;
}
function Td({ children, right, accent }) {
  return <td className={`py-2 ${right ? 'text-right' : 'text-left'}`} style={{ color: accent ? '#C5A059' : undefined, fontWeight: accent ? 500 : 400 }}>{children}</td>;
}
