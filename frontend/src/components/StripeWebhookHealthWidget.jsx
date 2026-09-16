import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { CheckCircle2, XCircle, RefreshCw, Loader2, Copy, AlertTriangle } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Widget admin — Stripe Webhook Health
 * Feb 2026 : ajout suite au déploiement Stripe live pour vérifier que
 * STRIPE_WEBHOOK_SECRET est bien configuré côté prod sans le révéler.
 */
export default function StripeWebhookHealthWidget({ token }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const r = await axios.get(`${API}/api/admin/stripe-webhook-health`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setData(r.data);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const ready = data?.ready === true;
  const bg = ready ? 'rgba(16,185,129,0.08)' : 'rgba(239,68,68,0.08)';
  const border = ready ? 'rgba(16,185,129,0.35)' : 'rgba(239,68,68,0.35)';
  const accent = ready ? '#10B981' : '#EF4444';

  return (
    <div
      className="rounded-2xl p-4 mb-6"
      style={{ background: bg, border: `1px solid ${border}` }}
      data-testid="stripe-webhook-health-widget"
    >
      <div className="flex items-center justify-between gap-3 flex-wrap mb-3">
        <div className="flex items-center gap-2">
          {ready ? (
            <CheckCircle2 className="w-4 h-4" style={{ color: accent }} strokeWidth={2} />
          ) : (
            <XCircle className="w-4 h-4" style={{ color: accent }} strokeWidth={2} />
          )}
          <span
            className="text-xs uppercase tracking-widest"
            style={{ color: accent, letterSpacing: '0.1em', fontWeight: 600 }}
          >
            Stripe Webhook · {ready ? 'Opérationnel' : (data ? 'Non configuré' : 'Vérification…')}
          </span>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1 text-[10px] uppercase tracking-widest rounded-full"
          style={{
            border: `1px solid ${border}`,
            color: accent,
            letterSpacing: '0.1em',
          }}
          data-testid="stripe-webhook-refresh"
        >
          {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
          Rafraîchir
        </button>
      </div>

      {error && (
        <div className="text-xs mb-2" style={{ color: '#EF4444' }}>
          Erreur : {error}
        </div>
      )}

      {data && (
        <div className="space-y-2 text-xs" style={{ color: 'var(--pa-body, rgba(247,245,240,0.85))' }}>
          <div className="grid grid-cols-2 gap-2">
            <Row label="Secret configuré" value={data.secret?.configured} />
            <Row label="Format valide (whsec_)" value={data.secret?.format_valid} />
            <Row
              label="Longueur"
              raw={`${data.secret?.length || 0} chars`}
              value={data.secret?.length > 20}
            />
            <Row
              label="Empreinte"
              raw={data.secret?.fingerprint || '—'}
              copyable={data.secret?.fingerprint}
            />
            <Row label="API Key configurée" value={data.api_key?.configured} />
            <Row
              label="Mode Stripe"
              raw={data.api_key?.mode || '—'}
              value={data.api_key?.mode === 'live'}
            />
          </div>

          {data.webhook_events?.last_24h && (
            <div
              className="mt-3 pt-3"
              style={{ borderTop: `1px solid ${border}` }}
            >
              <div className="text-[10px] uppercase tracking-widest mb-2" style={{ color: accent, letterSpacing: '0.1em' }}>
                Webhooks reçus (24h)
              </div>
              <div className="flex items-center gap-4 flex-wrap">
                <span>
                  Total : <b style={{ color: 'var(--pa-heading, #F5EEE0)' }}>{data.webhook_events.last_24h.total}</b>
                </span>
                {Object.entries(data.webhook_events.last_24h.by_status || {}).map(([status, count]) => (
                  <span key={status} className="text-[11px]">
                    {status} : <b style={{ color: 'var(--pa-heading, #F5EEE0)' }}>{count}</b>
                  </span>
                ))}
              </div>
            </div>
          )}

          {data.hints?.length > 0 && (
            <div className="mt-3 space-y-1">
              {data.hints.map((h, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 text-[11px] p-2 rounded-lg"
                  style={{ background: 'rgba(239,68,68,0.08)', color: '#EF4444' }}
                >
                  <AlertTriangle className="w-3 h-3 flex-shrink-0 mt-0.5" />
                  <span>{h}</span>
                </div>
              ))}
            </div>
          )}

          <div className="text-[10px] mt-2" style={{ color: 'var(--pa-muted, rgba(247,245,240,0.4))' }}>
            Vérifié à {new Date(data.checked_at).toLocaleString('fr-FR')}
          </div>
        </div>
      )}
    </div>
  );
}

function Row({ label, value, raw, copyable }) {
  const ok = value === true;
  const ko = value === false;
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    if (!copyable) return;
    try {
      await navigator.clipboard.writeText(copyable);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {}
  };

  return (
    <div className="flex items-center justify-between gap-2 py-1">
      <span style={{ color: 'var(--pa-muted, rgba(247,245,240,0.6))' }}>{label}</span>
      {copyable ? (
        <button
          onClick={copy}
          className="flex items-center gap-1 font-mono text-xs"
          style={{ color: 'var(--pa-heading, #F5EEE0)', cursor: 'pointer' }}
          title="Copier"
        >
          {raw}
          <Copy className="w-3 h-3" style={{ color: copied ? '#10B981' : 'var(--pa-muted)' }} />
        </button>
      ) : raw ? (
        <span
          className="font-mono text-xs"
          style={{ color: value === false ? '#EF4444' : 'var(--pa-heading, #F5EEE0)' }}
        >
          {raw}
        </span>
      ) : ok ? (
        <span style={{ color: '#10B981' }}>✓</span>
      ) : ko ? (
        <span style={{ color: '#EF4444' }}>✗</span>
      ) : (
        <span style={{ color: 'var(--pa-muted)' }}>—</span>
      )}
    </div>
  );
}
