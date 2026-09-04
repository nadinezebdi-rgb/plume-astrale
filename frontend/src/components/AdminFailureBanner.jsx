import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { AlertTriangle, RefreshCw, Loader2, X, ChevronDown, ChevronUp } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Silent Failure Radar (Feb 2026)
 * Bannière admin qui liste toutes les sessions dont le PDF a échoué dans les
 * dernières 24h. Bouton « Régénérer » par ligne. Refresh manuel.
 *
 * Props :
 *   token       : Bearer JWT admin (nécessaire pour /api/admin/*)
 *   dismissable : si true, affiche un X pour cacher jusqu'à la prochaine visite
 */
export default function AdminFailureBanner({ token, dismissable = false }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [hidden, setHidden] = useState(false);
  const [regenerating, setRegenerating] = useState({});
  const [regenMsg, setRegenMsg] = useState('');

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const r = await axios.get(`${API}/api/admin/pdf-failures/last-24h`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setItems(r.data.items || []);
    } catch (e) {
      // silencieux : n'affiche pas de bannière si l'endpoint échoue
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const regenerate = async (sessionId) => {
    setRegenerating((s) => ({ ...s, [sessionId]: true }));
    setRegenMsg('');
    try {
      await axios.post(
        `${API}/api/admin/theme-natal/regenerate/${sessionId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRegenMsg(`Régénération lancée pour ${sessionId.slice(-12)} — suivre dans quelques secondes.`);
      setTimeout(load, 4000);
    } catch (e) {
      setRegenMsg(`Erreur : ${e?.response?.data?.detail || e.message}`);
    } finally {
      setRegenerating((s) => ({ ...s, [sessionId]: false }));
    }
  };

  if (hidden || items.length === 0) return null;

  return (
    <div
      className="rounded-2xl p-4 mb-6"
      style={{
        background: 'rgba(239, 68, 68, 0.08)',
        border: '1px solid rgba(239, 68, 68, 0.35)',
      }}
      data-testid="admin-failure-banner"
    >
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" style={{ color: '#EF4444' }} strokeWidth={2} />
          <span
            className="text-xs uppercase tracking-widest"
            style={{ color: '#EF4444', letterSpacing: '0.1em', fontWeight: 600 }}
            data-testid="admin-failure-banner-title"
          >
            {items.length} PDF{items.length > 1 ? 's' : ''} en échec dans les dernières 24h
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={load}
            className="flex items-center gap-1.5 px-3 py-1 text-[10px] uppercase tracking-widest rounded-full"
            style={{
              border: '1px solid rgba(239, 68, 68, 0.35)',
              color: '#EF4444',
              letterSpacing: '0.1em',
            }}
            data-testid="admin-failure-banner-refresh"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            Rafraîchir
          </button>
          <button
            onClick={() => setExpanded((v) => !v)}
            className="flex items-center gap-1.5 px-3 py-1 text-[10px] uppercase tracking-widest rounded-full"
            style={{
              border: '1px solid rgba(239, 68, 68, 0.35)',
              color: '#EF4444',
              letterSpacing: '0.1em',
            }}
            data-testid="admin-failure-banner-toggle"
          >
            {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            {expanded ? 'Masquer' : 'Détails'}
          </button>
          {dismissable && (
            <button
              onClick={() => setHidden(true)}
              className="p-1 rounded-full"
              style={{ color: '#EF4444' }}
              data-testid="admin-failure-banner-close"
              aria-label="Fermer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {expanded && (
        <div className="mt-3 space-y-2" data-testid="admin-failure-banner-list">
          {items.map((it) => (
            <div
              key={it.session_id}
              className="rounded-xl p-3 flex items-start justify-between gap-3 flex-wrap"
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(239, 68, 68, 0.18)',
              }}
              data-testid={`admin-failure-item-${it.session_id.slice(-12)}`}
            >
              <div className="text-xs min-w-0 flex-1" style={{ color: 'var(--pa-body)' }}>
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <span
                    style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 15, color: 'var(--pa-heading)' }}
                  >
                    {it.first_name || 'Sans prénom'}
                  </span>
                  <span style={{ color: 'var(--pa-muted)' }}>·</span>
                  <span style={{ color: 'var(--pa-muted)' }}>{it.user_email}</span>
                  <span style={{ color: 'var(--pa-muted)' }}>·</span>
                  <span
                    className="px-2 py-0.5 rounded-full text-[10px] uppercase tracking-wider"
                    style={{
                      background: 'rgba(212,175,55,0.12)',
                      color: '#D4AF37',
                      letterSpacing: '0.05em',
                    }}
                  >
                    {it.kind}
                  </span>
                </div>
                <div style={{ color: 'var(--pa-muted)', wordBreak: 'break-word' }}>
                  <code style={{ fontSize: 10 }}>{it.session_id}</code>
                </div>
                <div className="mt-1" style={{ color: '#EF4444', fontSize: 11 }}>
                  {it.pdf_error || 'Erreur non renseignée'}
                </div>
                {it.planets_core_missing?.length > 0 && (
                  <div className="mt-1" style={{ color: 'var(--pa-muted)', fontSize: 10 }}>
                    Planètes core manquantes : {it.planets_core_missing.join(', ')}
                  </div>
                )}
                <div className="mt-1" style={{ color: 'var(--pa-muted)', fontSize: 10 }}>
                  Échec : {it.pdf_failed_at ? new Date(it.pdf_failed_at).toLocaleString('fr-FR') : '—'}
                </div>
              </div>
              <button
                onClick={() => regenerate(it.session_id)}
                disabled={regenerating[it.session_id] || it.regenerate_in_progress}
                className="flex items-center gap-2 px-4 py-2 text-xs uppercase tracking-widest rounded-full flex-shrink-0"
                style={{
                  background: regenerating[it.session_id] || it.regenerate_in_progress
                    ? 'rgba(212,175,55,0.15)'
                    : '#D4AF37',
                  color: regenerating[it.session_id] || it.regenerate_in_progress
                    ? 'rgba(212,175,55,0.8)'
                    : '#111625',
                  letterSpacing: '0.1em',
                  cursor: regenerating[it.session_id] || it.regenerate_in_progress ? 'wait' : 'pointer',
                }}
                data-testid={`admin-failure-regenerate-${it.session_id.slice(-12)}`}
              >
                {regenerating[it.session_id] || it.regenerate_in_progress ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <RefreshCw className="w-3.5 h-3.5" />
                )}
                {it.regenerate_in_progress ? 'En cours…' : 'Régénérer'}
              </button>
            </div>
          ))}
          {regenMsg && (
            <div
              className="text-xs px-3 py-2 rounded-lg"
              style={{ color: 'var(--pa-body)', background: 'rgba(212,175,55,0.08)' }}
              data-testid="admin-failure-banner-message"
            >
              {regenMsg}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
