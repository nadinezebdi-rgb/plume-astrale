import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Package, RefreshCw, Loader2, ExternalLink, AlertCircle, CheckCircle2 } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';
import { useAuth } from '@/context/AuthContext';

/**
 * /admin/lulu-orders — tableau des commandes "livre relié" Lulu bump 79€.
 *
 * Lit `GET /api/natal-print-bump/admin/orders?status=...` avec JWT admin.
 * Filtre : toutes / initiated (payé en attente) / fulfilled (print job envoyé)
 *          / IN_PRODUCTION / SHIPPED / REJECTED / cancelled.
 */

const STATUS_FILTERS = [
  { key: 'all', label: 'Toutes', param: '' },
  { key: 'initiated', label: 'Payé — en attente', param: 'initiated' },
  { key: 'fulfilled', label: 'Envoyé à Lulu', param: 'fulfilled' },
  { key: 'cancelled', label: 'Annulé', param: 'cancelled' },
];

const LULU_STATUS_LABEL = {
  CREATED: 'Créé',
  UNPAID: 'Non payé',
  PAYMENT_IN_PROGRESS: 'Paiement en cours',
  PRODUCTION_READY: 'Prêt impression',
  PRODUCTION_DELAYED: 'Impression retardée',
  IN_PRODUCTION: 'En production',
  ERROR: 'Erreur',
  SHIPPED: 'Expédié',
  REJECTED: 'Rejeté',
  CANCELED: 'Annulé',
};

function lulePill(status) {
  const label = LULU_STATUS_LABEL[status] || status || '—';
  const palette = {
    SHIPPED:        { bg: 'rgba(34, 139, 34, 0.15)', fg: '#2d7a2d', border: 'rgba(34, 139, 34, 0.4)' },
    IN_PRODUCTION:  { bg: 'rgba(168, 130, 63, 0.18)', fg: '#A8823F', border: 'rgba(168, 130, 63, 0.45)' },
    PRODUCTION_READY: { bg: 'rgba(168, 130, 63, 0.12)', fg: '#A8823F', border: 'rgba(168, 130, 63, 0.35)' },
    ERROR:          { bg: 'rgba(179, 44, 44, 0.15)', fg: '#B32C2C', border: 'rgba(179, 44, 44, 0.4)' },
    REJECTED:       { bg: 'rgba(179, 44, 44, 0.15)', fg: '#B32C2C', border: 'rgba(179, 44, 44, 0.4)' },
    CANCELED:       { bg: 'rgba(107, 114, 128, 0.15)', fg: '#525b6b', border: 'rgba(107, 114, 128, 0.4)' },
  };
  const colors = palette[status] || { bg: 'rgba(107, 114, 128, 0.1)', fg: '#525b6b', border: 'rgba(107, 114, 128, 0.3)' };
  return { label, ...colors };
}

export default function AdminLuluOrders() {
  const { user, session, loading: authLoading } = useAuth();
  const isAdmin =
    user?.is_admin || user?.role === 'admin' || user?.email === 'admin@plume-astrale.fr';

  const [filter, setFilter] = useState('all');
  const [state, setState] = useState({ orders: [], loading: true, error: null });
  const backend = process.env.REACT_APP_BACKEND_URL;
  const token = session?.access_token || null;

  const load = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const filterCfg = STATUS_FILTERS.find((f) => f.key === filter) || STATUS_FILTERS[0];
      const params = new URLSearchParams({ limit: '200' });
      if (filterCfg.param) params.set('status', filterCfg.param);
      const res = await fetch(`${backend}/api/natal-print-bump/admin/orders?${params}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setState({ orders: data.orders || [], loading: false, error: null });
    } catch (e) {
      setState({ orders: [], loading: false, error: e.message || String(e) });
    }
  }, [backend, token, filter]);

  useEffect(() => {
    if (isAdmin) load();
  }, [isAdmin, load]);

  const stats = useMemo(() => {
    const total = state.orders.length;
    const paid = state.orders.filter((o) => o.status === 'initiated').length;
    const sent = state.orders.filter((o) => o.status === 'fulfilled').length;
    const shipped = state.orders.filter((o) => o.lulu_status === 'SHIPPED').length;
    const revenue_eur = state.orders.reduce((sum, o) => sum + (o.amount_eur || 0), 0);
    return { total, paid, sent, shipped, revenue_eur };
  }, [state.orders]);

  if (authLoading) return null;
  if (!user || !isAdmin) return <Navigate to="/" replace />;

  return (
    <PsPageShell>
      <div data-testid="admin-lulu-orders" style={{ maxWidth: 1200, margin: '0 auto', padding: '24px 20px 80px' }}>
        <header style={{ marginBottom: 28 }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 14,
            marginBottom: 6,
          }}>
            <Package size={28} style={{ color: '#A8823F' }} />
            <h1 style={{
              fontFamily: '"Cormorant Garamond", serif', fontWeight: 300, fontSize: 32,
              color: '#F7F5F0', margin: 0, letterSpacing: '-0.01em',
            }}>
              Commandes <em style={{ color: '#A8823F' }}>Livre Relié</em>
            </h1>
          </div>
          <p style={{ color: 'rgba(247, 245, 240, 0.6)', fontSize: 14, margin: 0, maxWidth: 720, lineHeight: 1.5 }}>
            Tableau de bord des bumps Lulu (livre hardcover 79€ ou + selon destination).
            Statut Stripe + statut Lulu + lien tracking.
          </p>
        </header>

        {/* Stats */}
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: 14, marginBottom: 28,
        }}>
          <StatCard label="Total commandes" value={stats.total} testid="stat-total"/>
          <StatCard label="Payé — en attente" value={stats.paid} tint="#D4AF37" testid="stat-paid"/>
          <StatCard label="Envoyé à Lulu" value={stats.sent} tint="#A8823F" testid="stat-sent"/>
          <StatCard label="Expédié" value={stats.shipped} tint="#2d7a2d" testid="stat-shipped"/>
          <StatCard label="Revenu brut" value={`${stats.revenue_eur.toFixed(0)} €`} testid="stat-revenue"/>
        </div>

        {/* Filters */}
        <div style={{
          display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 20, alignItems: 'center',
        }}>
          {STATUS_FILTERS.map((f) => (
            <button key={f.key}
              type="button"
              onClick={() => setFilter(f.key)}
              data-testid={`filter-${f.key}`}
              style={{
                padding: '8px 16px', borderRadius: 999,
                border: filter === f.key ? '1px solid #A8823F' : '1px solid rgba(247, 245, 240, 0.15)',
                background: filter === f.key ? 'rgba(168, 130, 63, 0.12)' : 'transparent',
                color: filter === f.key ? '#A8823F' : 'rgba(247, 245, 240, 0.7)',
                fontSize: 12, letterSpacing: '0.08em', textTransform: 'uppercase',
                cursor: 'pointer', fontWeight: 600,
                transition: 'all 220ms ease',
              }}>
              {f.label}
            </button>
          ))}
          <div style={{ flex: 1 }} />
          <button type="button" onClick={load} data-testid="btn-refresh"
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 7,
              padding: '8px 16px', borderRadius: 999,
              border: '1px solid rgba(168, 130, 63, 0.4)',
              background: 'transparent', color: '#A8823F',
              fontSize: 12, letterSpacing: '0.08em', textTransform: 'uppercase',
              cursor: 'pointer', fontWeight: 600,
            }}>
            <RefreshCw size={13} /> Actualiser
          </button>
        </div>

        {/* Error */}
        {state.error && (
          <div data-testid="error-banner" style={{
            padding: '12px 16px', background: 'rgba(179, 44, 44, 0.12)',
            border: '1px solid rgba(179, 44, 44, 0.35)', borderRadius: 10,
            color: '#f3a8a8', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10,
          }}>
            <AlertCircle size={16} /> {state.error}
          </div>
        )}

        {/* Table */}
        <div style={{
          background: 'rgba(247, 245, 240, 0.03)',
          border: '1px solid rgba(168, 130, 63, 0.18)',
          borderRadius: 14, overflow: 'hidden',
        }}>
          {state.loading ? (
            <div style={{ padding: 60, textAlign: 'center', color: 'rgba(247, 245, 240, 0.5)' }}>
              <Loader2 size={28} className="animate-spin" style={{ marginBottom: 10 }} />
              <div style={{ fontSize: 13 }}>Chargement…</div>
            </div>
          ) : state.orders.length === 0 ? (
            <div data-testid="empty-state" style={{ padding: 60, textAlign: 'center', color: 'rgba(247, 245, 240, 0.45)' }}>
              <Package size={32} style={{ marginBottom: 10, opacity: 0.5 }} />
              <div style={{ fontSize: 14, fontFamily: '"Cormorant Garamond", serif', fontStyle: 'italic' }}>
                Aucune commande pour ce filtre.
              </div>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{
                width: '100%', borderCollapse: 'collapse', fontSize: 13,
                fontFamily: 'Inter, sans-serif', color: '#F7F5F0',
              }}>
                <thead>
                  <tr style={{ background: 'rgba(168, 130, 63, 0.08)' }}>
                    <Th>Date</Th>
                    <Th>Client</Th>
                    <Th>Destination</Th>
                    <Th align="right">Montant</Th>
                    <Th>Stripe</Th>
                    <Th>Lulu</Th>
                    <Th>Tracking</Th>
                  </tr>
                </thead>
                <tbody>
                  {state.orders.map((o) => {
                    const pill = lulePill(o.lulu_status);
                    return (
                      <tr key={o.session_id} data-testid="order-row"
                        style={{ borderTop: '1px solid rgba(247, 245, 240, 0.06)' }}>
                        <Td>
                          <div style={{ fontSize: 12, color: 'rgba(247, 245, 240, 0.6)' }}>
                            {o.created_at ? new Date(o.created_at).toLocaleString('fr-FR', {
                              dateStyle: 'short', timeStyle: 'short',
                            }) : '—'}
                          </div>
                        </Td>
                        <Td>
                          <div style={{ fontWeight: 500 }}>{o.first_name || '—'}</div>
                          <div style={{ fontSize: 11, color: 'rgba(247, 245, 240, 0.5)' }}>{o.email || ''}</div>
                        </Td>
                        <Td>
                          {o.city ? <span>{o.city}, </span> : null}
                          <span style={{ fontSize: 11, color: 'rgba(247, 245, 240, 0.55)' }}>
                            {o.country || '—'}
                          </span>
                          {o.quote_mocked ? (
                            <span style={{ fontSize: 10, color: '#D4AF37',
                              display: 'block', fontStyle: 'italic', marginTop: 2 }}>
                              devis MOCK
                            </span>
                          ) : null}
                        </Td>
                        <Td align="right">
                          <strong style={{ fontFamily: '"Cormorant Garamond", serif', fontSize: 15 }}>
                            {o.amount_eur?.toFixed(0)} €
                          </strong>
                        </Td>
                        <Td>
                          {o.status === 'fulfilled' ? (
                            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: '#2d7a2d' }}>
                              <CheckCircle2 size={13} /> {o.status}
                            </span>
                          ) : (
                            <span style={{ color: 'rgba(247, 245, 240, 0.65)' }}>{o.status}</span>
                          )}
                        </Td>
                        <Td>
                          <span style={{
                            padding: '3px 10px', borderRadius: 999, fontSize: 11,
                            background: pill.bg, color: pill.fg,
                            border: `1px solid ${pill.border}`, fontWeight: 600,
                            letterSpacing: '0.03em',
                          }}>
                            {pill.label}
                          </span>
                        </Td>
                        <Td>
                          {o.tracking_urls && o.tracking_urls.length > 0 ? (
                            <a href={o.tracking_urls[0]} target="_blank" rel="noreferrer"
                              style={{ color: '#A8823F', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                              Suivre <ExternalLink size={11} />
                            </a>
                          ) : (
                            <span style={{ color: 'rgba(247, 245, 240, 0.35)' }}>—</span>
                          )}
                        </Td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div style={{
          marginTop: 20, fontSize: 11, color: 'rgba(247, 245, 240, 0.4)',
          fontStyle: 'italic',
        }}>
          Mode mock Lulu actif tant que `LULU_MOCK=1` dans `backend/.env`. Les commandes marquées « devis MOCK » n'ont PAS été envoyées à l'imprimeur réel.
        </div>
      </div>
    </PsPageShell>
  );
}

function StatCard({ label, value, tint, testid }) {
  return (
    <div data-testid={testid} style={{
      padding: 18, borderRadius: 12,
      background: 'rgba(247, 245, 240, 0.03)',
      border: '1px solid rgba(168, 130, 63, 0.18)',
    }}>
      <div style={{
        fontSize: 10, letterSpacing: '0.14em', textTransform: 'uppercase',
        color: 'rgba(247, 245, 240, 0.55)', marginBottom: 6, fontWeight: 600,
      }}>
        {label}
      </div>
      <div style={{
        fontSize: 26, fontFamily: '"Cormorant Garamond", serif',
        color: tint || '#F7F5F0', fontWeight: 400, lineHeight: 1,
      }}>
        {value}
      </div>
    </div>
  );
}

function Th({ children, align = 'left' }) {
  return (
    <th style={{
      padding: '12px 14px', textAlign: align, fontSize: 10,
      letterSpacing: '0.14em', textTransform: 'uppercase',
      color: 'rgba(247, 245, 240, 0.55)', fontWeight: 600,
    }}>
      {children}
    </th>
  );
}

function Td({ children, align = 'left' }) {
  return (
    <td style={{ padding: '14px', textAlign: align, verticalAlign: 'top' }}>
      {children}
    </td>
  );
}
