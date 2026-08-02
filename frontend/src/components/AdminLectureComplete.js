import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { RefreshCw, CheckCircle2, XCircle, Clock, AlertTriangle, Mail, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';

const API = process.env.REACT_APP_BACKEND_URL;

const KIND_LABEL = {
  theme_natal_pdf_oneshot: 'Thème Natal',
  karma_destin_analysis: 'Karma & Destinée',
  kabbale_arbre_de_vie: 'Arbre de Vie Kabbale',
  fenetre_rencontre_avancee: 'Fenêtres Rencontre',
  rencontres_ultime: 'Rencontres Ultime',
};

const StatusPill = ({ status, ready, error }) => {
  if (error) {
    return (
      <span title={error} style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: '#f87171', fontSize: 12 }}>
        <XCircle className="w-3.5 h-3.5" /> échec
      </span>
    );
  }
  if (ready || status === 'success') {
    return (
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: '#4ADE80', fontSize: 12 }}>
        <CheckCircle2 className="w-3.5 h-3.5" /> prêt
      </span>
    );
  }
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: '#d9b26a', fontSize: 12 }}>
      <Clock className="w-3.5 h-3.5" /> en cours
    </span>
  );
};

export default function AdminLectureComplete({ token }) {
  const [orders, setOrders] = useState([]);
  const [stats, setStats] = useState(null);
  const [abStats, setAbStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [redispatching, setRedispatching] = useState(null);
  const [refunding, setRefunding] = useState(null);
  const [expandedTimeline, setExpandedTimeline] = useState(null);

  // Modal refund state
  const [refundModalOpen, setRefundModalOpen] = useState(false);
  const [refundTarget, setRefundTarget] = useState(null);  // {sid, email, amount, admin_bypass}
  const [refundReason, setRefundReason] = useState('');
  const [refundSkipStripe, setRefundSkipStripe] = useState(false);
  const [refundError, setRefundError] = useState(null);
  const [refundSuccess, setRefundSuccess] = useState(null);

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const [ordersRes, abRes] = await Promise.all([
        axios.get(`${API}/api/lecture-complete/admin/orders`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        axios.get(`${API}/api/lecture-complete/admin/ab-stats`, {
          headers: { Authorization: `Bearer ${token}` },
        }).catch(() => ({ data: null })),
      ]);
      setOrders(ordersRes.data?.orders || []);
      setStats(ordersRes.data?.stats || null);
      setAbStats(abRes.data || null);
    } catch (e) {
      setError(e.response?.data?.detail || 'Chargement impossible.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const redispatch = async (sid) => {
    if (!window.confirm(`Relancer la génération du bundle ${sid} ? (Les 5 PDFs seront régénérés)`)) return;
    setRedispatching(sid);
    try {
      await axios.post(`${API}/api/lecture-complete/admin/redispatch/${sid}`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      await load();
    } catch (e) {
      alert(e.response?.data?.detail || 'Erreur redispatch');
    } finally {
      setRedispatching(null);
    }
  };

  const openRefundModal = (order) => {
    setRefundTarget({
      sid: order.session_id,
      email: order.email,
      amount: order.amount,
      admin_bypass: order.admin_bypass,
    });
    setRefundReason('');
    setRefundSkipStripe(!!order.admin_bypass);  // pas de Stripe a rembourser pour les bypass
    setRefundError(null);
    setRefundSuccess(null);
    setRefundModalOpen(true);
  };

  const confirmRefund = async () => {
    if (!refundTarget) return;
    setRefunding(refundTarget.sid);
    setRefundError(null);
    try {
      const r = await axios.post(
        `${API}/api/lecture-complete/admin/refund/${refundTarget.sid}`,
        { reason: refundReason || undefined, skip_stripe: refundSkipStripe },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRefundSuccess(r.data);
      await load();
      // Auto-fermeture apres 1.5s
      setTimeout(() => {
        setRefundModalOpen(false);
        setRefundTarget(null);
        setRefundSuccess(null);
      }, 1500);
    } catch (e) {
      setRefundError(e.response?.data?.detail || 'Erreur refund');
    } finally {
      setRefunding(null);
    }
  };

  return (
    <div data-testid="admin-lecture-complete-panel">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2 style={{ fontSize: 22, color: '#d9b26a', margin: 0 }}>
          Lecture Complète — Commandes 97€
        </h2>
        <button
          onClick={load}
          disabled={loading}
          data-testid="admin-lc-refresh"
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            padding: '8px 14px', borderRadius: 20,
            background: 'rgba(217,178,106,0.12)',
            color: '#d9b26a',
            border: '1px solid rgba(217,178,106,0.35)',
            cursor: 'pointer', fontSize: 12, letterSpacing: '.1em',
            textTransform: 'uppercase',
          }}
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Rafraîchir
        </button>
      </div>

      {error && (
        <div style={{ padding: 12, background: 'rgba(248,113,113,0.1)', border: '1px solid rgba(248,113,113,0.3)', borderRadius: 8, color: '#f87171', marginBottom: 16, fontSize: 13 }}>
          {error}
        </div>
      )}

      {stats && (
        <div
          data-testid="admin-lc-stats"
          style={{
            display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 16,
            padding: 12, background: 'rgba(255,255,255,0.02)',
            border: '1px solid rgba(217,178,106,0.15)', borderRadius: 10,
          }}
        >
          <span style={{ fontSize: 12, color: 'rgba(184,180,201,0.75)' }}>
            Payés (hors bypass) : <strong style={{ color: '#e8e6f0' }}>{stats.total_paid}</strong>
          </span>
          <span style={{ fontSize: 12, color: 'rgba(184,180,201,0.75)' }}>
            Remboursés : <strong style={{ color: '#f87171' }}>{stats.total_refunded}</strong>
          </span>
          <span style={{ fontSize: 12, color: 'rgba(184,180,201,0.75)' }}>
            Taux de refund : <strong data-testid="admin-lc-stats-refund-rate" style={{ color: stats.refund_rate_pct > 5 ? '#f87171' : '#4ADE80' }}>{stats.refund_rate_pct}%</strong>
          </span>
        </div>
      )}

      {abStats && (
        <div
          data-testid="admin-lc-ab-panel"
          style={{
            marginBottom: 16, padding: 12,
            background: 'linear-gradient(135deg, rgba(167,139,250,0.08), rgba(217,178,106,0.05))',
            border: '1px solid rgba(167,139,250,0.25)', borderRadius: 10,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <span style={{ fontSize: 11, letterSpacing: '.12em', textTransform: 'uppercase', color: '#A78BFA' }}>
              A/B Test J+30 Upsell
            </span>
            <span style={{ fontSize: 11, color: 'rgba(184,180,201,0.65)' }}>
              · {abStats.total} envois {abStats.total >= 50 ? '· prêt à décider' : `· ${50 - abStats.total} à attendre`}
            </span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            {['question', 'invitation'].map((v) => {
              const n = abStats[v] || 0;
              const pct = abStats.total ? Math.round((n / abStats.total) * 100) : 0;
              const isLeader = abStats.total >= 20 && n > (abStats[v === 'question' ? 'invitation' : 'question'] || 0);
              return (
                <div
                  key={v}
                  data-testid={`admin-lc-ab-${v}`}
                  style={{
                    padding: 10, borderRadius: 8,
                    background: 'rgba(11,16,32,0.5)',
                    border: `1px solid ${isLeader ? 'rgba(74,222,128,0.4)' : 'rgba(255,255,255,0.06)'}`,
                  }}
                >
                  <div style={{ fontSize: 12, color: '#e8e6f0', marginBottom: 4, display: 'flex', justifyContent: 'space-between' }}>
                    <span>
                      {v === 'question' ? '❓ Question ouverte' : '✉️ Invitation directe'}
                      {isLeader && <span style={{ color: '#4ADE80', marginLeft: 6, fontSize: 10 }}>· leader</span>}
                    </span>
                    <span style={{ color: '#d9b26a', fontWeight: 600 }}>{n}</span>
                  </div>
                  <div style={{ height: 6, background: 'rgba(255,255,255,0.05)', borderRadius: 3, overflow: 'hidden' }}>
                    <div
                      style={{
                        height: '100%', width: `${pct}%`,
                        background: v === 'question' ? '#A78BFA' : '#d9b26a',
                        transition: 'width .3s ease',
                      }}
                    />
                  </div>
                  <div style={{ fontSize: 10, color: 'rgba(184,180,201,0.55)', marginTop: 4 }}>
                    {pct}% du volume
                  </div>
                </div>
              );
            })}
          </div>
          {abStats.total < 50 && (
            <div style={{ fontSize: 10, color: 'rgba(184,180,201,0.5)', marginTop: 8, fontStyle: 'italic' }}>
              Décision statistiquement fiable à partir de 50 envois. Vérifier le CTR dans Resend via les email_ids stockés.
            </div>
          )}
        </div>
      )}

      {orders.length === 0 && !loading && (
        <p style={{ color: 'rgba(184,180,201,0.7)', fontSize: 14 }}>Aucune commande 97€ pour l&apos;instant.</p>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        {orders.map((o) => (
          <div
            key={o.session_id}
            data-testid={`admin-lc-order-${o.session_id}`}
            style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(217,178,106,0.15)',
              borderRadius: 12, padding: 16,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, flexWrap: 'wrap' }}>
              <div style={{ flex: 1, minWidth: 260 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
                  <strong style={{ color: '#e8e6f0', fontSize: 15 }}>{o.email || '(sans email)'}</strong>
                  {o.admin_bypass && (
                    <span style={{ padding: '2px 8px', borderRadius: 10, background: 'rgba(167,139,250,0.15)', color: '#a78bfa', fontSize: 10, letterSpacing: '.1em', textTransform: 'uppercase' }}>Admin</span>
                  )}
                  <span style={{ padding: '2px 8px', borderRadius: 10, background: o.payment_status === 'paid' ? 'rgba(74,222,128,0.15)' : 'rgba(248,113,113,0.15)', color: o.payment_status === 'paid' ? '#4ADE80' : '#f87171', fontSize: 10, letterSpacing: '.1em', textTransform: 'uppercase' }}>
                    {o.payment_status}
                  </span>
                  {!o.bundle_dispatched && o.payment_status === 'paid' && (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: '#fbbf24', fontSize: 11 }}>
                      <AlertTriangle className="w-3 h-3" /> non dispatché
                    </span>
                  )}
                </div>
                <div style={{ fontSize: 11, color: 'rgba(184,180,201,0.65)', fontFamily: 'monospace' }}>
                  {o.session_id} · {o.created_at ? new Date(o.created_at).toLocaleString('fr-FR') : ''}
                </div>
                {o.bundle_error && (
                  <div style={{ marginTop: 4, fontSize: 11, color: '#f87171' }}>Erreur bundle : {o.bundle_error}</div>
                )}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11, color: 'rgba(184,180,201,0.75)' }}>
                  <Mail className="w-3 h-3" />
                  J+1 <span style={{ color: o.sequence?.j1 ? '#4ADE80' : 'rgba(184,180,201,0.4)' }}>●</span>
                  {' '}J+7 <span style={{ color: o.sequence?.j7 ? '#4ADE80' : 'rgba(184,180,201,0.4)' }}>●</span>
                  {' '}J+13 <span style={{ color: o.sequence?.j13 ? '#4ADE80' : 'rgba(184,180,201,0.4)' }}>●</span>
                  {' '}J+30 <span style={{ color: o.sequence?.j30 ? '#4ADE80' : 'rgba(184,180,201,0.4)' }}>●</span>
                </div>
                <button
                  onClick={() => redispatch(o.session_id)}
                  disabled={redispatching === o.session_id || !!o.refunded_at}
                  data-testid={`admin-lc-redispatch-${o.session_id}`}
                  style={{
                    padding: '6px 12px', borderRadius: 16,
                    background: 'transparent',
                    color: o.refunded_at ? 'rgba(184,180,201,0.4)' : '#d9b26a',
                    border: `1px solid ${o.refunded_at ? 'rgba(184,180,201,0.2)' : 'rgba(217,178,106,0.5)'}`,
                    fontSize: 11, cursor: o.refunded_at ? 'not-allowed' : 'pointer',
                  }}
                >
                  {redispatching === o.session_id ? '...' : 'Relancer'}
                </button>
                {!o.refunded_at ? (
                  <button
                    onClick={() => openRefundModal(o)}
                    disabled={refunding === o.session_id}
                    data-testid={`admin-lc-refund-${o.session_id}`}
                    style={{
                      padding: '6px 12px', borderRadius: 16,
                      background: 'transparent',
                      color: '#f87171',
                      border: '1px solid rgba(248,113,113,0.4)',
                      fontSize: 11, cursor: 'pointer',
                    }}
                  >
                    {refunding === o.session_id ? '...' : 'Rembourser'}
                  </button>
                ) : (
                  <span
                    data-testid={`admin-lc-refunded-${o.session_id}`}
                    style={{
                      padding: '4px 10px', borderRadius: 14,
                      background: 'rgba(248,113,113,0.15)',
                      color: '#f87171',
                      fontSize: 10, letterSpacing: '.1em', textTransform: 'uppercase',
                    }}
                    title={o.refund_reason || 'Remboursé'}
                  >
                    Remboursé
                  </span>
                )}
              </div>
            </div>

            <div style={{ marginTop: 12, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 8 }}>
              {o.children.length === 0 && (
                <div style={{ fontSize: 12, color: 'rgba(184,180,201,0.5)' }}>Aucun PDF enfant créé.</div>
              )}
              {o.children.map((c) => (
                <div
                  key={c.session_id}
                  style={{
                    padding: 10, borderRadius: 8,
                    background: 'rgba(11,16,32,0.5)',
                    border: '1px solid rgba(255,255,255,0.06)',
                  }}
                >
                  <div style={{ fontSize: 12, color: '#e8e6f0', marginBottom: 4 }}>
                    {KIND_LABEL[c.kind] || c.kind}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 11 }}>
                    <StatusPill status={c.pdf_status} ready={c.pdf_ready} error={c.pdf_error} />
                    {c.email_sent && <Mail className="w-3 h-3" style={{ color: '#4ADE80' }} />}
                  </div>
                </div>
              ))}
            </div>

            {/* Timeline actions admin */}
            {(o.admin_actions && o.admin_actions.length > 0) && (
              <div style={{ marginTop: 12 }}>
                <button
                  type="button"
                  onClick={() => setExpandedTimeline(expandedTimeline === o.session_id ? null : o.session_id)}
                  data-testid={`admin-lc-timeline-toggle-${o.session_id}`}
                  style={{
                    fontSize: 11, background: 'transparent', border: 'none',
                    color: '#A78BFA', cursor: 'pointer', padding: 0,
                    letterSpacing: '.08em', textTransform: 'uppercase',
                  }}
                >
                  {expandedTimeline === o.session_id ? '▼' : '▶'} Timeline actions ({o.admin_actions.length})
                </button>
                {expandedTimeline === o.session_id && (
                  <div
                    data-testid={`admin-lc-timeline-${o.session_id}`}
                    style={{
                      marginTop: 8, paddingLeft: 12,
                      borderLeft: '2px solid rgba(167,139,250,0.3)',
                    }}
                  >
                    {o.admin_actions.slice().reverse().map((a, i) => (
                      <div key={i} style={{ marginBottom: 6, fontSize: 11, color: 'rgba(184,180,201,0.85)' }}>
                        <span style={{
                          color: a.action.includes('refund') ? '#f87171' :
                                 a.action === 'redispatch' ? '#d9b26a' : '#A78BFA',
                          fontWeight: 600, marginRight: 6,
                        }}>{a.action}</span>
                        <span style={{ color: 'rgba(184,180,201,0.6)' }}>
                          {new Date(a.at).toLocaleString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
                        </span>
                        <span style={{ color: 'rgba(184,180,201,0.6)', marginLeft: 6 }}>
                          par <em>{a.admin_email || (a.auto ? 'auto' : 'admin')}</em>
                        </span>
                        {a.details && (
                          <div style={{ marginTop: 2, fontSize: 10, color: 'rgba(184,180,201,0.55)', paddingLeft: 8 }}>
                            {a.details}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* ═══ MODAL REFUND ═══ */}
      <Dialog open={refundModalOpen} onOpenChange={setRefundModalOpen}>
        <DialogContent
          className="max-w-md"
          data-testid="refund-modal"
          style={{ background: '#141a33', color: '#e8e6f0', border: '1px solid rgba(217,178,106,0.3)' }}
        >
          <DialogHeader>
            <DialogTitle style={{ color: '#f87171' }}>
              Rembourser la commande
            </DialogTitle>
            <DialogDescription>
              {refundTarget && (
                <>
                  <div className="text-xs opacity-70 font-mono break-all mb-2">
                    {refundTarget.sid}
                  </div>
                  <div className="text-sm">
                    <strong>{refundTarget.email}</strong>
                    {' — '}{refundTarget.amount}€
                    {refundTarget.admin_bypass && <span className="ml-2 text-purple-300">(admin bypass)</span>}
                  </div>
                </>
              )}
            </DialogDescription>
          </DialogHeader>

          {refundSuccess ? (
            <div
              data-testid="refund-modal-success"
              className="rounded-lg p-3 text-sm"
              style={{ background: 'rgba(74,222,128,0.1)', border: '1px solid rgba(74,222,128,0.3)', color: '#4ADE80' }}
            >
              ✓ Remboursement effectué{refundSuccess.stripe_refund_id ? ` · Stripe : ${refundSuccess.stripe_refund_id}` : ''}
              {refundSuccess.stripe_skipped && <div className="text-xs opacity-70 mt-1">Stripe non appelé (admin bypass ou skip demandé).</div>}
            </div>
          ) : (
            <>
              <div className="space-y-3">
                <div>
                  <label className="text-xs uppercase tracking-wider block mb-1" style={{ color: '#d9b26a' }}>
                    Raison (optionnel)
                  </label>
                  <textarea
                    data-testid="refund-modal-reason"
                    value={refundReason}
                    onChange={(e) => setRefundReason(e.target.value)}
                    placeholder="Ex : client a demandé, PDF défectueux, doublon…"
                    rows={3}
                    className="w-full rounded px-3 py-2 text-sm"
                    style={{
                      background: 'rgba(11,16,32,0.6)',
                      border: '1px solid rgba(255,255,255,0.15)',
                      color: '#e8e6f0',
                    }}
                  />
                </div>

                {refundTarget && !refundTarget.admin_bypass && (
                  <label className="flex items-center gap-2 text-xs cursor-pointer" style={{ color: 'rgba(184,180,201,0.85)' }}>
                    <input
                      type="checkbox"
                      checked={refundSkipStripe}
                      onChange={(e) => setRefundSkipStripe(e.target.checked)}
                      data-testid="refund-modal-skip-stripe"
                    />
                    Ne pas appeler Stripe (marquer localement uniquement)
                  </label>
                )}

                {refundError && (
                  <div
                    data-testid="refund-modal-error"
                    className="rounded p-2 text-xs"
                    style={{ background: 'rgba(248,113,113,0.1)', border: '1px solid rgba(248,113,113,0.3)', color: '#f87171' }}
                  >
                    {refundError}
                  </div>
                )}
              </div>

              <DialogFooter>
                <button
                  type="button"
                  onClick={() => setRefundModalOpen(false)}
                  disabled={!!refunding}
                  data-testid="refund-modal-cancel"
                  className="px-4 py-2 rounded text-xs uppercase tracking-wider"
                  style={{ background: 'transparent', color: 'rgba(184,180,201,0.75)', border: '1px solid rgba(255,255,255,0.15)' }}
                >
                  Annuler
                </button>
                <button
                  type="button"
                  onClick={confirmRefund}
                  disabled={!!refunding}
                  data-testid="refund-modal-confirm"
                  className="px-4 py-2 rounded text-xs uppercase tracking-wider inline-flex items-center gap-1.5"
                  style={{ background: '#f87171', color: '#0b1020', border: 'none', cursor: refunding ? 'not-allowed' : 'pointer', fontWeight: 600 }}
                >
                  {refunding && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  {refunding ? 'Refund…' : (refundSkipStripe || refundTarget?.admin_bypass ? 'Marquer remboursé' : 'Rembourser via Stripe')}
                </button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
