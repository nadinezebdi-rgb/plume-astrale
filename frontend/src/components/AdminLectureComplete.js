import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { RefreshCw, CheckCircle2, XCircle, Clock, AlertTriangle, Mail } from 'lucide-react';

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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [redispatching, setRedispatching] = useState(null);
  const [refunding, setRefunding] = useState(null);

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const r = await axios.get(`${API}/api/lecture-complete/admin/orders`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setOrders(r.data?.orders || []);
      setStats(r.data?.stats || null);
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

  const refund = async (sid) => {
    const reason = window.prompt('Raison du remboursement (optionnel) :');
    if (reason === null) return; // annulé
    if (!window.confirm(`Marquer la commande ${sid} comme remboursée ? (Ne déclenche pas le refund Stripe — à faire manuellement dans le dashboard Stripe)`)) return;
    setRefunding(sid);
    try {
      await axios.post(`${API}/api/lecture-complete/admin/refund/${sid}`, { reason: reason || undefined }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      await load();
    } catch (e) {
      alert(e.response?.data?.detail || 'Erreur refund');
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
            Taux de refund : <strong data-testid="admin-lc-refund-rate" style={{ color: stats.refund_rate_pct > 5 ? '#f87171' : '#4ADE80' }}>{stats.refund_rate_pct}%</strong>
          </span>
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
                    onClick={() => refund(o.session_id)}
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
          </div>
        ))}
      </div>
    </div>
  );
}
