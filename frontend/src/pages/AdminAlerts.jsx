import React, { useEffect, useState, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import { AlertTriangle, RefreshCw, Loader2, CheckCircle2, Database } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';
import { useAuth } from '@/context/AuthContext';

/**
 * /admin/alerts — Historique des alertes système envoyées via Resend.
 * Table Supabase : public.admin_alerts (migration /app/backend/migrations/2026_02_admin_alerts.sql).
 *
 * - Chaque ligne = 1 alerte envoyée (astrology-api.io 401, 5xx streak, etc.)
 * - Bouton "Marquer résolu" → POST /api/admin/alerts/{id}/resolve
 * - Si la table n'existe pas encore, affiche un hint de migration.
 */
export default function AdminAlerts() {
  const { user, session, loading: authLoading } = useAuth();
  const isAdmin =
    user?.is_admin || user?.role === 'admin' || user?.email === 'admin@plume-astrale.fr';

  const [state, setState] = useState({
    items: [],
    migrationNeeded: false,
    loading: true,
    error: null,
  });
  const [resolvingId, setResolvingId] = useState(null);
  const backend = process.env.REACT_APP_BACKEND_URL;
  const token = session?.access_token || null;

  const load = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const res = await fetch(`${backend}/api/admin/alerts?limit=100`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      const data = await res.json();
      setState({
        items: data.items || [],
        migrationNeeded: !!data.migration_needed,
        loading: false,
        error: null,
      });
    } catch (e) {
      setState({ items: [], migrationNeeded: false, loading: false, error: e.message });
    }
  }, [backend, token]);

  const resolve = async (id) => {
    setResolvingId(id);
    try {
      await fetch(`${backend}/api/admin/alerts/${id}/resolve`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      await load();
    } finally {
      setResolvingId(null);
    }
  };

  useEffect(() => { if (isAdmin) load(); }, [isAdmin, load]);

  if (authLoading) return null;
  if (!user || !isAdmin) return <Navigate to="/" replace />;

  const openCount = state.items.filter((a) => !a.resolved_at).length;

  return (
    <PsPageShell background="dark">
      <div
        data-testid="admin-alerts-page"
        style={{ padding: '48px 24px', maxWidth: 1100, margin: '0 auto', color: 'var(--plume-ivory)' }}
      >
        <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32, flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <AlertTriangle size={22} style={{ color: 'var(--plume-gold)' }} strokeWidth={1.5} />
              <span style={{ fontFamily: 'Cinzel, serif', fontSize: 11, letterSpacing: '0.25em', textTransform: 'uppercase', color: 'var(--plume-gold)' }}>Monitoring</span>
            </div>
            <h1 style={{ fontFamily: '"Fraunces", "Playfair Display", serif', fontWeight: 400, fontSize: 32, margin: 0, letterSpacing: '-0.01em' }}>
              Alertes système
            </h1>
            <p style={{ color: 'rgba(244,239,230,0.65)', fontSize: 14, margin: '6px 0 0' }}>
              {openCount} alerte{openCount > 1 ? 's' : ''} ouverte{openCount > 1 ? 's' : ''} · {state.items.length} total
            </p>
          </div>
          <button onClick={load} data-testid="admin-alerts-refresh" style={refreshBtn}>
            {state.loading ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
            Rafraîchir
          </button>
        </header>

        {state.migrationNeeded && (
          <div data-testid="admin-alerts-migration-hint" style={hintBox}>
            <Database size={18} style={{ color: '#F6C77A', flexShrink: 0 }} strokeWidth={1.6} />
            <div>
              <strong>Migration requise.</strong> La table <code>public.admin_alerts</code> n&apos;existe pas encore.
              Exécute <code>/app/backend/migrations/2026_02_admin_alerts.sql</code> dans le SQL Editor Supabase
              pour activer l&apos;historisation des alertes.
            </div>
          </div>
        )}

        {state.error && (
          <div style={errorBox}>Erreur : {state.error}</div>
        )}

        {!state.loading && !state.migrationNeeded && state.items.length === 0 && (
          <div data-testid="admin-alerts-empty" style={emptyBox}>
            <CheckCircle2 size={28} style={{ color: '#4ADE80', marginBottom: 8 }} strokeWidth={1.5} />
            <p style={{ margin: 0, fontSize: 15, color: 'rgba(244,239,230,0.78)' }}>
              Aucune alerte enregistrée. Tout va bien.
            </p>
          </div>
        )}

        {state.items.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }} data-testid="admin-alerts-list">
            {state.items.map((a) => {
              const resolved = !!a.resolved_at;
              return (
                <article
                  key={a.id}
                  data-testid={`admin-alert-${a.id}`}
                  style={{
                    ...cardStyle,
                    opacity: resolved ? 0.55 : 1,
                    borderColor: resolved ? 'rgba(74,222,128,0.3)' : 'rgba(239,68,68,0.35)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, flexWrap: 'wrap' }}>
                    <div style={{ flex: 1, minWidth: 240 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                        <span style={{ ...typePill, background: resolved ? 'rgba(74,222,128,0.12)' : 'rgba(239,68,68,0.12)', color: resolved ? '#4ADE80' : '#F87171' }}>
                          {a.alert_type}
                        </span>
                        <span style={severityPill}>sev · {a.severity}</span>
                        {a.http_status && <span style={severityPill}>HTTP {a.http_status}</span>}
                      </div>
                      <h3 style={{ fontFamily: '"Fraunces", serif', fontWeight: 400, fontSize: 18, margin: '2px 0 6px' }}>
                        {a.subject}
                      </h3>
                      <p style={{ fontSize: 13, color: 'rgba(244,239,230,0.65)', margin: 0, lineHeight: 1.5 }}>
                        {a.error_detail || '(no detail)'}
                      </p>
                      <div style={metaRow}>
                        <span>{new Date(a.created_at).toLocaleString('fr-FR')}</span>
                        {a.recipient && <span>· {a.recipient}</span>}
                        {a.resend_id && <span>· resend {a.resend_id.slice(0, 10)}…</span>}
                        {resolved && <span style={{ color: '#4ADE80' }}>· résolu {new Date(a.resolved_at).toLocaleDateString('fr-FR')}</span>}
                      </div>
                    </div>
                    {!resolved && (
                      <button
                        onClick={() => resolve(a.id)}
                        disabled={resolvingId === a.id}
                        data-testid={`admin-alert-resolve-${a.id}`}
                        style={resolveBtn}
                      >
                        {resolvingId === a.id ? <Loader2 size={13} className="animate-spin" /> : <CheckCircle2 size={13} />}
                        Marquer résolu
                      </button>
                    )}
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </div>
    </PsPageShell>
  );
}

const refreshBtn = {
  display: 'inline-flex', alignItems: 'center', gap: 6,
  padding: '8px 14px',
  background: 'rgba(212,175,55,0.1)', border: '1px solid rgba(212,175,55,0.4)',
  borderRadius: 4, color: 'var(--plume-gold)',
  fontSize: 12, letterSpacing: '0.08em', textTransform: 'uppercase',
  fontFamily: 'Inter, sans-serif', cursor: 'pointer',
};
const hintBox = {
  display: 'flex', alignItems: 'flex-start', gap: 12,
  padding: '16px 18px', marginBottom: 24,
  background: 'rgba(246,199,122,0.08)', border: '1px solid rgba(246,199,122,0.3)',
  borderRadius: 6, color: 'rgba(244,239,230,0.9)', fontSize: 13.5, lineHeight: 1.55,
};
const errorBox = {
  padding: '14px 18px', marginBottom: 24,
  background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.35)',
  borderRadius: 6, color: '#F87171', fontSize: 13,
};
const emptyBox = {
  textAlign: 'center', padding: '48px 20px',
  background: 'rgba(255,255,255,0.03)', border: '1px dashed rgba(244,239,230,0.15)',
  borderRadius: 8,
};
const cardStyle = {
  padding: '18px 20px',
  background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(244,239,230,0.1)',
  borderRadius: 6,
};
const typePill = {
  display: 'inline-flex', padding: '3px 10px', borderRadius: 999,
  fontSize: 11, fontWeight: 500, letterSpacing: '0.04em', fontFamily: 'JetBrains Mono, monospace',
};
const severityPill = {
  display: 'inline-flex', padding: '3px 10px', borderRadius: 999,
  background: 'rgba(255,255,255,0.05)', color: 'rgba(244,239,230,0.68)',
  fontSize: 11, fontFamily: 'Inter, sans-serif', letterSpacing: '0.03em',
};
const metaRow = {
  display: 'flex', gap: 8, flexWrap: 'wrap',
  marginTop: 10, fontSize: 11.5, color: 'rgba(244,239,230,0.5)',
  fontFamily: 'Inter, sans-serif', letterSpacing: '0.02em',
};
const resolveBtn = {
  display: 'inline-flex', alignItems: 'center', gap: 6,
  padding: '8px 14px', background: 'transparent',
  border: '1px solid rgba(74,222,128,0.4)', borderRadius: 4, color: '#4ADE80',
  fontSize: 11.5, letterSpacing: '0.08em', textTransform: 'uppercase',
  fontFamily: 'Inter, sans-serif', cursor: 'pointer', whiteSpace: 'nowrap',
};
