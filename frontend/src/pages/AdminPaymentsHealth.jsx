import React, { useEffect, useState, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { Loader2, RefreshCw, AlertTriangle, CheckCircle2, XCircle, Play, Eye, Receipt, Undo2 } from 'lucide-react';
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

/**
 * Mini-composant : recherche de paiements par montant + liste + bouton Rembourser.
 * Backend : GET /api/admin/stripe-refund/find-test-payments?amount_eur=&days=
 */
function RefundFinder({ token, apiBase, onRefund, refundingId }) {
  const [amount, setAmount] = React.useState('24');
  const [days, setDays] = React.useState(30);
  const [results, setResults] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [err, setErr] = React.useState(null);

  const search = async () => {
    setLoading(true); setErr(null); setResults(null);
    try {
      const r = await axios.get(
        `${apiBase}/api/admin/stripe-refund/find-test-payments?amount_eur=${encodeURIComponent(amount)}&days=${days}`,
        { headers: { Authorization: `Bearer ${token}` } },
      );
      setResults(r.data);
    } catch (e) {
      setErr(e.response?.data?.detail || 'Recherche échouée.');
    } finally { setLoading(false); }
  };

  return (
    <div>
      <div className="flex gap-3 flex-wrap items-end mb-4">
        <div>
          <label htmlFor="refund-amount" className="text-[10px] uppercase tracking-widest block mb-1" style={{ color: 'var(--pa-muted)' }}>Montant (€)</label>
          <input id="refund-amount" type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)}
                 className="px-3 py-2 rounded-lg text-sm w-28"
                 style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(212,175,55,0.25)', color: '#F5EEE0' }}
                 data-testid="refund-finder-amount"/>
        </div>
        <div>
          <label htmlFor="refund-days" className="text-[10px] uppercase tracking-widest block mb-1" style={{ color: 'var(--pa-muted)' }}>Fenêtre (jours)</label>
          <select id="refund-days" value={days} onChange={(e) => setDays(parseInt(e.target.value, 10))}
                  className="px-3 py-2 rounded-lg text-sm"
                  style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(212,175,55,0.25)', color: '#F5EEE0' }}
                  data-testid="refund-finder-days">
            <option value={7}>7</option>
            <option value={30}>30</option>
            <option value={60}>60</option>
            <option value={90}>90</option>
          </select>
        </div>
        <button onClick={search} disabled={loading || !amount}
                className="text-xs uppercase tracking-widest px-4 py-2 rounded-full flex items-center gap-2"
                style={{ border: '1px solid rgba(212,175,55,0.35)', color: '#D4AF37' }}
                data-testid="refund-finder-search">
          {loading ? <Loader2 className="w-3 h-3 animate-spin"/> : <Eye className="w-3 h-3"/>}
          Chercher
        </button>
      </div>
      {err && <div className="text-xs mb-3" style={{ color: '#FCA5A5' }}>{err}</div>}
      {results && results.count === 0 && (
        <div className="text-sm" style={{ color: 'var(--pa-muted)' }}>Aucun paiement trouvé pour {results.amount_eur} € sur {results.window_days} j.</div>
      )}
      {results && results.count > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm" data-testid="refund-finder-results">
            <thead style={{ background: 'rgba(212,175,55,0.06)' }}>
              <tr>
                <th className="text-left px-3 py-2 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Date</th>
                <th className="text-left px-3 py-2 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Email</th>
                <th className="text-left px-3 py-2 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Pack</th>
                <th className="text-right px-3 py-2 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Montant</th>
                <th className="px-3 py-2"></th>
              </tr>
            </thead>
            <tbody>
              {results.matches.map((p) => (
                <tr key={p.session_id} style={{ borderTop: '1px solid rgba(212,175,55,0.08)' }}>
                  <td className="px-3 py-2 text-xs" style={{ color: 'var(--pa-muted)' }}>{(p.created_at || '').slice(0, 16).replace('T', ' ')}</td>
                  <td className="px-3 py-2">{p.user_email}</td>
                  <td className="px-3 py-2 text-xs">{p.pack_id}</td>
                  <td className="px-3 py-2 text-right">{Number(p.amount || 0).toFixed(2)} €</td>
                  <td className="px-3 py-2 text-right">
                    {p.already_refunded ? (
                      <span className="text-[10px] uppercase tracking-widest px-2 py-1 rounded-full"
                        style={{ background: 'rgba(74,222,128,0.12)', color: '#4ADE80' }}>
                        déjà remboursé
                      </span>
                    ) : (
                      <button
                        onClick={() => onRefund(p.session_id)}
                        disabled={refundingId === p.session_id}
                        className="text-xs uppercase tracking-widest px-3 py-1.5 rounded-full flex items-center gap-2 ml-auto"
                        style={{ background: '#D4AF37', color: '#111625', fontWeight: 600 }}
                        data-testid={`refund-btn-${p.session_id}`}>
                        {refundingId === p.session_id ? <Loader2 className="w-3 h-3 animate-spin"/> : <Undo2 className="w-3 h-3"/>}
                        Rembourser
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function AdminPaymentsHealth() {
  const { user, token, loading: authLoading } = useAuth();
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(60);
  const [recovering, setRecovering] = useState(false);
  const [recoveryReport, setRecoveryReport] = useState(null);
  const [error, setError] = useState(null);
  // AUDIT (2026-10-30 · Nao) : compteur facture + remboursement
  const [invoiceCounter, setInvoiceCounter] = useState(null);
  const [refundingId, setRefundingId] = useState(null);
  const [refundReport, setRefundReport] = useState(null);

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const [h, inv] = await Promise.all([
        axios.get(`${API}/api/admin/payments-health?days=${days}`,
          { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/api/admin/invoice-counter`,
          { headers: { Authorization: `Bearer ${token}` } }).catch(() => ({ data: null })),
      ]);
      setHealth(h.data);
      setInvoiceCounter(inv.data);
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

  // AUDIT (2026-10-30 · Nao) : remboursement one-shot d'une session Stripe.
  //   1. prompt confirmation + raison + note (dry-run d'abord)
  //   2. appel /api/admin/stripe-refund?dry_run=true → affiche l'aperçu charge
  //   3. 2e confirmation → appel dry_run=false
  const refundSession = async (sessionId) => {
    const reason = window.prompt(
      `Raison du remboursement (requested_by_customer / duplicate / fraudulent) :`,
      'requested_by_customer',
    );
    if (!reason) return;
    const note = window.prompt('Note interne (facultative, 200 car max) :', '') || '';
    setRefundingId(sessionId); setRefundReport(null); setError(null);
    try {
      // Dry-run d'abord — affiche montant/charge
      const preview = await axios.post(`${API}/api/admin/stripe-refund`, {
        session_id: sessionId, reason, note, dry_run: true,
      }, { headers: { Authorization: `Bearer ${token}` } });
      const charge = preview.data?.charge || {};
      const confirmTxt = (
        `Confirmer le REMBOURSEMENT ?\n\n` +
        `• Session : ${sessionId}\n` +
        `• Montant : ${charge.amount || '?'} ${(charge.currency || '').toUpperCase()}\n` +
        `• Email : ${charge.customer_email || '—'}\n` +
        `• Carte : **** ${charge.card_last4 || '????'}\n` +
        `• Déjà remboursé : ${charge.already_refunded ? 'OUI' : 'non'}\n` +
        `• Raison : ${reason}\n\n` +
        `Clique OK pour exécuter le refund Stripe réel.`
      );
      if (!window.confirm(confirmTxt)) {
        setRefundingId(null);
        return;
      }
      const r = await axios.post(`${API}/api/admin/stripe-refund`, {
        session_id: sessionId, reason, note, dry_run: false,
      }, { headers: { Authorization: `Bearer ${token}` } });
      setRefundReport({ sessionId, ...r.data });
      load();
    } catch (e) {
      setError(e.response?.data?.detail || 'Remboursement échoué.');
    } finally { setRefundingId(null); }
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
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
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

            {/* AUDIT (2026-10-30 · Nao) : Compteur facture séquentiel annuel FR */}
            {invoiceCounter && (
              <div className="rounded-2xl p-5 mb-8 flex items-center gap-5 flex-wrap" style={{
                background: 'rgba(212,175,55,0.06)',
                border: '1px solid rgba(212,175,55,0.22)',
              }} data-testid="invoice-counter-banner">
                <Receipt className="w-10 h-10 flex-shrink-0" style={{ color: '#D4AF37' }} strokeWidth={1.4}/>
                <div className="flex-1 min-w-0">
                  <div className="text-[10px] uppercase tracking-widest mb-1" style={{ color: 'var(--pa-muted)', letterSpacing: '0.12em' }}>
                    Compteur facture {invoiceCounter.year} — exigence comptable FR
                  </div>
                  <div className="flex items-baseline gap-4 flex-wrap">
                    <span className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#D4AF37' }}>
                      {invoiceCounter.last_number || <em style={{ color: 'var(--pa-muted)' }}>aucune facture émise</em>}
                    </span>
                    <span className="text-xs" style={{ color: 'var(--pa-muted)' }}>
                      · prochaine → <span style={{ color: '#F5EEE0' }}>{invoiceCounter.next_number}</span>
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full"
                      style={{
                        background: invoiceCounter.backend === 'mongo' ? 'rgba(74,222,128,0.12)' : 'rgba(239,68,68,0.12)',
                        color: invoiceCounter.backend === 'mongo' ? '#4ADE80' : '#FCA5A5',
                      }}>
                      backend : {invoiceCounter.backend}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* AUDIT (2026-10-30 · Nao) : rapport remboursement one-shot */}
            {refundReport && (
              <div className="rounded-2xl p-5 mb-8" style={{
                background: refundReport.refunded ? 'rgba(74,222,128,0.10)' : 'rgba(239,68,68,0.10)',
                border: `1px solid ${refundReport.refunded ? 'rgba(74,222,128,0.35)' : 'rgba(239,68,68,0.35)'}`,
              }} data-testid="refund-report">
                <div className="text-sm mb-1" style={{ color: refundReport.refunded ? '#4ADE80' : '#FCA5A5' }}>
                  {refundReport.refunded ? '✓ Remboursement Stripe exécuté' : '✗ Remboursement non exécuté'}
                </div>
                <div className="text-xs" style={{ color: 'var(--pa-muted)' }}>
                  Session {refundReport.sessionId}
                  {refundReport.refund_id && <> · Refund <code>{refundReport.refund_id}</code></>}
                  {refundReport.amount_refunded != null && <> · <strong>{refundReport.amount_refunded} {(refundReport.currency || '').toUpperCase()}</strong></>}
                  {refundReport.status && <> · statut {refundReport.status}</>}
                  {refundReport.reason_skipped && <> · {refundReport.reason_skipped}</>}
                </div>
                <button onClick={() => setRefundReport(null)} className="mt-2 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>
                  fermer
                </button>
              </div>
            )}

            {/* AUDIT (2026-10-30 · Nao) : Recherche paiements + bouton Rembourser */}
            <div className="rounded-2xl p-6 mb-8" style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(212,175,55,0.18)',
            }} data-testid="refund-finder">
              <h2 className="text-xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#D4AF37' }}>
                Remboursement Stripe one-shot
              </h2>
              <p className="text-sm mb-4" style={{ color: 'var(--pa-muted)' }}>
                Cherche un paiement par montant (défaut 24 € = test Thème Natal), puis clique <em>Rembourser</em> pour exécuter un refund 100 % Stripe. Confirmation obligatoire en 2 étapes.
              </p>
              <RefundFinder token={token} apiBase={API} onRefund={refundSession} refundingId={refundingId}/>
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
