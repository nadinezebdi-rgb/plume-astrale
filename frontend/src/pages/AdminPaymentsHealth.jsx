import React, { useEffect, useState, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { Loader2, RefreshCw, AlertTriangle, CheckCircle2, XCircle, Play, Eye } from 'lucide-react';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

const STATUS_META = {
  green:  { color: '#4ADE80', bg: 'rgba(74,222,128,0.10)', label: 'TOUT VA BIEN',       Icon: CheckCircle2 },
  orange: { color: '#F59E0B', bg: 'rgba(245,158,11,0.10)', label: 'ATTENTION',          Icon: AlertTriangle },
  red:    { color: '#EF4444', bg: 'rgba(239,68,68,0.10)',  label: 'INCIDENT PAIEMENTS', Icon: XCircle },
};

const KpiBadge = ({ label, value, sub, color = '#D4AF37', testid }) => (
  <div className="rounded-2xl p-5" style={{
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(212,175,55,0.18)',
    backdropFilter: 'blur(12px)',
  }} data-testid={testid}>
    <div className="text-[10px] uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.12em' }}>{label}</div>
    <div className="text-3xl mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color, fontWeight: 400 }}>{value}</div>
    {sub && <div className="text-xs" style={{ color: 'var(--pa-muted)' }}>{sub}</div>}
  </div>
);

export default function AdminPaymentsHealth() {
  const { user, token, loading: authLoading } = useAuth();
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(60);
  const [recovering, setRecovering] = useState(false);
  const [recoveryReport, setRecoveryReport] = useState(null);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const r = await axios.get(`${API}/api/admin/payments-health?days=${days}`,
        { headers: { Authorization: `Bearer ${token}` } });
      setHealth(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || 'Erreur lors du chargement.');
    } finally { setLoading(false); }
  }, [days, token]);

  useEffect(() => { if (token) load(); }, [token, load]);

  const runRecovery = async (dryRun) => {
    if (!dryRun) {
      const ok = window.confirm(
        'ATTENTION : ceci va vérifier chaque session bloquée côté Stripe et déclencher la livraison des PDFs pour les paiements réellement passés. Continuer ?'
      );
      if (!ok) return;
    }
    setRecovering(true); setRecoveryReport(null);
    try {
      const r = await axios.post(`${API}/api/admin/stripe-recovery`, {
        days, limit: 200, dry_run: dryRun,
      }, { headers: { Authorization: `Bearer ${token}` } });
      setRecoveryReport(r.data);
      if (!dryRun) load();
    } catch (e) {
      setError(e.response?.data?.detail || 'Recovery échoué.');
    } finally { setRecovering(false); }
  };

  if (authLoading) return null;
  if (!user) return <Navigate to="/connexion" replace />;

  const meta = health ? STATUS_META[health.overall_status] : STATUS_META.orange;
  const StatusIcon = meta.Icon;

  return (
    <div className="min-h-screen py-16 px-6" style={{ background: '#0B0E1F', color: 'var(--pa-body)' }} data-testid="admin-payments-health">
      <SEO path="/admin/payments-health" title="Payments Health · Plume Astrale" />

      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
          <h1 className="text-3xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#D4AF37' }}>
            Santé des paiements Stripe
          </h1>
          <div className="flex items-center gap-3">
            <select value={days} onChange={(e) => setDays(parseInt(e.target.value, 10))}
                    className="text-xs uppercase tracking-widest px-3 py-2 rounded-full"
                    style={{ border: '1px solid rgba(212,175,55,0.35)', background: 'transparent', color: '#D4AF37' }}
                    data-testid="days-select">
              <option value={7}>7 jours</option>
              <option value={30}>30 jours</option>
              <option value={60}>60 jours</option>
              <option value={90}>90 jours</option>
              <option value={365}>1 an</option>
            </select>
            <button onClick={load} disabled={loading}
                    className="text-xs uppercase tracking-widest px-4 py-2 rounded-full flex items-center gap-2"
                    style={{ border: '1px solid rgba(212,175,55,0.35)', color: '#D4AF37' }}
                    data-testid="reload-btn">
              {loading ? <Loader2 className="w-3 h-3 animate-spin"/> : <RefreshCw className="w-3 h-3"/>}
              Actualiser
            </button>
          </div>
        </div>

        {error && (
          <div className="rounded-xl p-4 mb-6" style={{ background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.35)', color: '#FCA5A5' }}>
            {error}
          </div>
        )}

        {loading && !health && (
          <div className="flex justify-center py-16"><Loader2 className="w-6 h-6 animate-spin" style={{ color: '#D4AF37' }}/></div>
        )}

        {health && (
          <>
            {/* Feu tricolore principal */}
            <div className="rounded-3xl p-6 mb-8 flex items-center gap-6" style={{
              background: meta.bg, border: `1px solid ${meta.color}55`,
            }} data-testid="status-banner">
              <StatusIcon className="w-12 h-12 flex-shrink-0" style={{ color: meta.color }} strokeWidth={1.5}/>
              <div>
                <div className="text-2xl mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: meta.color }}>
                  {meta.label}
                </div>
                <div className="text-sm" style={{ color: 'var(--pa-body)' }}>
                  Webhook Stripe : {health.webhook_secret_configured
                    ? <span style={{ color: '#4ADE80' }}>✓ configuré</span>
                    : <span style={{ color: '#EF4444', fontWeight: 600 }}>❌ NON CONFIGURÉ — les paiements ne déclenchent pas la livraison PDF !</span>}
                </div>
              </div>
            </div>

            {/* KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <KpiBadge testid="kpi-conversion" label="Taux de conversion"
                value={`${health.conversion_rate_pct}%`}
                sub={`${health.paid_sessions_count} payées / ${health.total_real_sessions} sessions`}
                color={health.conversion_rate_pct < 5 ? '#EF4444' : health.conversion_rate_pct < 15 ? '#F59E0B' : '#4ADE80'}
              />
              <KpiBadge testid="kpi-paid" label="Revenus encaissés"
                value={`${health.paid_sessions_amount_eur.toFixed(2)} €`}
                sub={`${health.paid_sessions_count} paiements sur ${health.window_days}j`}
                color="#4ADE80"
              />
              <KpiBadge testid="kpi-stuck" label="Sessions bloquées"
                value={health.stuck_sessions_count}
                sub={`sur les ${health.window_days} derniers jours`}
                color={health.stuck_sessions_count > 20 ? '#EF4444' : '#F59E0B'}
              />
              <KpiBadge testid="kpi-lost" label="Perte potentielle"
                value={`${health.stuck_sessions_amount_eur.toFixed(2)} €`}
                sub="cumul montants bloqués"
                color="#EF4444"
              />
            </div>

            {/* Recovery actions */}
            <div className="rounded-2xl p-6 mb-8" style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(212,175,55,0.18)',
            }}>
              <h2 className="text-xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#D4AF37' }}>
                Recovery des sessions bloquées
              </h2>
              <p className="text-sm mb-4" style={{ color: 'var(--pa-muted)' }}>
                Croise chaque session bloquée avec Stripe et déclenche la livraison PDF pour celles réellement payées.
                Le mode <em>dry-run</em> ne modifie rien, il montre seulement combien seraient recovered.
              </p>
              <div className="flex flex-wrap gap-3">
                <button onClick={() => runRecovery(true)} disabled={recovering}
                        className="text-xs uppercase tracking-widest px-4 py-2 rounded-full flex items-center gap-2"
                        style={{ border: '1px solid rgba(212,175,55,0.35)', color: '#D4AF37' }}
                        data-testid="recovery-dry-btn">
                  <Eye className="w-3 h-3"/> Dry-run (aperçu seulement)
                </button>
                <button onClick={() => runRecovery(false)} disabled={recovering}
                        className="text-xs uppercase tracking-widest px-4 py-2 rounded-full flex items-center gap-2"
                        style={{ background: '#D4AF37', color: '#111625', fontWeight: 600 }}
                        data-testid="recovery-run-btn">
                  {recovering ? <Loader2 className="w-3 h-3 animate-spin"/> : <Play className="w-3 h-3"/>}
                  Lancer le recovery réel
                </button>
              </div>

              {recoveryReport && (
                <div className="mt-5 rounded-lg p-4" style={{ background: 'rgba(0,0,0,0.35)', border: '1px solid rgba(212,175,55,0.18)' }}>
                  <div className="text-sm mb-2" style={{ color: '#D4AF37' }}>
                    Rapport ({recoveryReport.dry_run ? 'dry-run' : 'appliqué'}) — {recoveryReport.scanned} sessions scannées
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs" data-testid="recovery-report">
                    {Object.entries(recoveryReport.action_counts || {}).map(([action, n]) => (
                      <div key={action} className="rounded p-2" style={{ background: 'rgba(255,255,255,0.04)' }}>
                        <div className="text-[10px] uppercase" style={{ color: 'var(--pa-muted)' }}>{action}</div>
                        <div className="text-lg" style={{ color: '#D4AF37' }}>{n}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Répartition par pack */}
            <div className="rounded-2xl overflow-hidden mb-8" style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(212,175,55,0.18)',
            }}>
              <div className="px-6 py-4" style={{ borderBottom: '1px solid rgba(212,175,55,0.15)' }}>
                <h2 className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#D4AF37' }}>
                  Par produit
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm" data-testid="by-pack-table">
                  <thead style={{ background: 'rgba(212,175,55,0.06)' }}>
                    <tr>
                      <th className="text-left px-4 py-3 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Pack</th>
                      <th className="text-right px-4 py-3 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Payées</th>
                      <th className="text-right px-4 py-3 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Bloquées</th>
                      <th className="text-right px-4 py-3 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Perte € potentielle</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(health.by_pack || []).map((p) => (
                      <tr key={p.pack_id} style={{ borderTop: '1px solid rgba(212,175,55,0.08)' }}>
                        <td className="px-4 py-3">{p.pack_id}</td>
                        <td className="px-4 py-3 text-right" style={{ color: '#4ADE80' }}>{p.paid}</td>
                        <td className="px-4 py-3 text-right" style={{ color: p.stuck > 5 ? '#EF4444' : '#F59E0B' }}>{p.stuck}</td>
                        <td className="px-4 py-3 text-right" style={{ color: '#EF4444' }}>{p.stuck_amount.toFixed(2)} €</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Dernières sessions bloquées */}
            <div className="rounded-2xl overflow-hidden" style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(212,175,55,0.18)',
            }}>
              <div className="px-6 py-4" style={{ borderBottom: '1px solid rgba(212,175,55,0.15)' }}>
                <h2 className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#D4AF37' }}>
                  20 dernières sessions bloquées
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm" data-testid="latest-stuck-table">
                  <thead style={{ background: 'rgba(212,175,55,0.06)' }}>
                    <tr>
                      <th className="text-left px-4 py-3 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Date</th>
                      <th className="text-left px-4 py-3 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Email</th>
                      <th className="text-left px-4 py-3 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Pack</th>
                      <th className="text-right px-4 py-3 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Montant</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(health.latest_stuck || []).map((s) => (
                      <tr key={s.session_id} style={{ borderTop: '1px solid rgba(212,175,55,0.08)' }}>
                        <td className="px-4 py-3 text-xs" style={{ color: 'var(--pa-muted)' }}>{s.created_at?.slice(0, 16).replace('T', ' ')}</td>
                        <td className="px-4 py-3">{s.user_email}</td>
                        <td className="px-4 py-3 text-xs">{s.pack_id}</td>
                        <td className="px-4 py-3 text-right">{Number(s.amount || 0).toFixed(2)} €</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
