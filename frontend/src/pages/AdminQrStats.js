import React, { useEffect, useState, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import { QrCode, RefreshCw, Loader2, TrendingUp, ExternalLink } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';
import { useAuth } from '@/context/AuthContext';

/**
 * /admin/qr-stats — dashboard analytics des scans QR de parrainage.
 * Lit `/api/admin/referral-scan-stats` et affiche le top des codes scannés
 * + un mini-histogramme visuel (barre horizontale relative au max).
 *
 * Le compteur est incrémenté quand un client scanne un QR PDF → redirection
 * `/r/{code}` avant d'arriver sur la home. Table Supabase : `referral_scan_counters`.
 */
export default function AdminQrStats() {
  const { user, session, loading: authLoading } = useAuth();
  const isAdmin =
    user?.is_admin || user?.role === 'admin' || user?.email === 'admin@plume-astrale.fr';

  const [stats, setStats] = useState({ ok: false, top_codes: [], loading: true, error: null });
  const backend = process.env.REACT_APP_BACKEND_URL;
  const token = session?.access_token || null;

  const load = useCallback(async () => {
    setStats((s) => ({ ...s, loading: true, error: null }));
    try {
      const res = await fetch(`${backend}/api/admin/referral-scan-stats?top=50`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      const data = await res.json();
      setStats({
        ok: !!data.ok,
        top_codes: data.top_codes || [],
        loading: false,
        error: data.ok ? null : data.error || null,
      });
    } catch (e) {
      setStats({ ok: false, top_codes: [], loading: false, error: e.message });
    }
  }, [backend, token]);

  useEffect(() => {
    if (isAdmin) load();
  }, [isAdmin, load]);

  if (authLoading) return null;
  if (!user || !isAdmin) return <Navigate to="/" replace />;

  const maxCount = Math.max(1, ...stats.top_codes.map((c) => c.count || 0));
  const totalScans = stats.top_codes.reduce((sum, c) => sum + (c.count || 0), 0);

  return (
    <PsPageShell background="dark">
      <div
        className="qr-stats-page"
        data-testid="admin-qr-stats-page"
        style={{
          padding: '48px 24px',
          maxWidth: 1100,
          margin: '0 auto',
          fontFamily: '"Cormorant Garamond", serif',
          color: '#F5EEE0',
        }}
      >
        {/* Header */}
        <header style={{ marginBottom: 32, display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
          <QrCode size={40} color="#D4AF37" strokeWidth={1.5} />
          <div style={{ flex: 1, minWidth: 240 }}>
            <h1
              style={{
                fontFamily: '"Playfair Display", "Cormorant Garamond", serif',
                fontSize: '2.4rem',
                margin: 0,
                color: '#F5EEE0',
                letterSpacing: '0.5px',
              }}
              data-testid="qr-stats-title"
            >
              Scans QR de parrainage
            </h1>
            <p style={{ color: '#B9B0D5', margin: '6px 0 0', fontSize: '0.98rem' }}>
              Nombre de scans par code depuis le colophon des PDFs Nocturne
            </p>
          </div>
          <button
            onClick={load}
            data-testid="qr-stats-refresh-btn"
            disabled={stats.loading}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              padding: '10px 18px',
              background: 'rgba(212, 175, 55, 0.16)',
              color: '#F5EEE0',
              border: '1px solid rgba(212, 175, 55, 0.4)',
              borderRadius: 6,
              cursor: stats.loading ? 'wait' : 'pointer',
              fontFamily: '"Cinzel", serif',
              fontSize: '0.85rem',
              letterSpacing: 2,
            }}
          >
            {stats.loading ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
            RECHARGER
          </button>
        </header>

        {/* KPI summary card */}
        <div
          data-testid="qr-stats-kpi-total"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: 16,
            marginBottom: 32,
          }}
        >
          <KpiCard label="Codes scannés" value={stats.top_codes.length} icon={<QrCode size={20} />} />
          <KpiCard label="Scans totaux" value={totalScans} icon={<TrendingUp size={20} />} />
          <KpiCard
            label="Top code"
            value={stats.top_codes[0]?.code || '—'}
            subvalue={stats.top_codes[0]?.count ? `${stats.top_codes[0].count} scans` : ''}
            icon={<Sparkle />}
          />
        </div>

        {/* Bar chart */}
        <section
          data-testid="qr-stats-chart-section"
          style={{
            background: 'rgba(15, 26, 60, 0.55)',
            border: '1px solid rgba(212, 175, 55, 0.22)',
            borderRadius: 8,
            padding: 24,
            backdropFilter: 'blur(8px)',
          }}
        >
          <h2
            style={{
              fontFamily: '"Cinzel", serif',
              fontSize: '0.9rem',
              letterSpacing: 3,
              margin: '0 0 20px',
              color: '#D4AF37',
            }}
          >
            TOP {stats.top_codes.length} CODES
          </h2>

          {stats.loading && (
            <div data-testid="qr-stats-loading" style={{ padding: 40, textAlign: 'center', color: '#B9B0D5' }}>
              <Loader2 size={22} className="animate-spin" />
              <p style={{ marginTop: 8 }}>Chargement des statistiques…</p>
            </div>
          )}

          {!stats.loading && stats.error && (
            <div
              data-testid="qr-stats-error"
              style={{
                padding: 24,
                background: 'rgba(220, 60, 60, 0.12)',
                border: '1px solid rgba(220, 60, 60, 0.4)',
                borderRadius: 6,
                color: '#F5C6C6',
              }}
            >
              <strong>Impossible de charger les stats.</strong>
              <p style={{ margin: '8px 0 0', fontSize: '0.88rem', opacity: 0.8 }}>{stats.error}</p>
              <p style={{ margin: '12px 0 0', fontSize: '0.85rem', opacity: 0.7 }}>
                Vérifier que la table Supabase <code>referral_scan_counters</code> existe.
              </p>
            </div>
          )}

          {!stats.loading && !stats.error && stats.top_codes.length === 0 && (
            <div
              data-testid="qr-stats-empty"
              style={{ padding: 40, textAlign: 'center', color: '#B9B0D5', opacity: 0.85 }}
            >
              <QrCode size={40} strokeWidth={1} style={{ opacity: 0.4 }} />
              <p style={{ marginTop: 12 }}>Aucun scan enregistré pour le moment.</p>
              <p style={{ fontSize: '0.88rem', opacity: 0.7 }}>
                Les données apparaîtront dès qu&apos;un client aura scanné un QR PDF.
              </p>
            </div>
          )}

          {!stats.loading && !stats.error && stats.top_codes.length > 0 && (
            <ul data-testid="qr-stats-list" style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {stats.top_codes.map((row) => (
                <li
                  key={row.code}
                  data-testid={`qr-stats-row-${row.code}`}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '140px 1fr 80px',
                    alignItems: 'center',
                    gap: 12,
                    padding: '10px 0',
                    borderBottom: '1px solid rgba(212, 175, 55, 0.1)',
                  }}
                >
                  <a
                    href={`/r/${row.code}`}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      fontFamily: '"Cinzel", serif',
                      letterSpacing: 2,
                      color: '#E8C766',
                      textDecoration: 'none',
                      fontSize: '0.95rem',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 6,
                    }}
                  >
                    {row.code}
                    <ExternalLink size={13} strokeWidth={1.5} />
                  </a>
                  <div
                    style={{
                      height: 10,
                      background: 'rgba(255, 255, 255, 0.06)',
                      borderRadius: 5,
                      overflow: 'hidden',
                    }}
                  >
                    <div
                      style={{
                        width: `${(row.count / maxCount) * 100}%`,
                        height: '100%',
                        background:
                          'linear-gradient(90deg, rgba(212, 175, 55, 0.6), rgba(232, 199, 102, 0.9))',
                        borderRadius: 5,
                        transition: 'width 400ms ease',
                      }}
                    />
                  </div>
                  <span
                    style={{
                      fontFamily: '"Cinzel", serif',
                      color: '#F5EEE0',
                      fontSize: '1rem',
                      textAlign: 'right',
                      fontVariantNumeric: 'tabular-nums',
                    }}
                    data-testid={`qr-stats-count-${row.code}`}
                  >
                    {row.count}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <p
          style={{
            marginTop: 28,
            fontSize: '0.85rem',
            color: '#B9B0D5',
            opacity: 0.7,
            fontStyle: 'italic',
          }}
        >
          Astuce : les scans QR sont attribués via cookie <code>ref</code> pendant 30 jours,
          puis convertis en attribution Meta CAPI si un achat suit. Compare ce compteur à
          celui des ventes attribuées pour mesurer le taux scan → conversion.
        </p>
      </div>
    </PsPageShell>
  );
}

function KpiCard({ label, value, subvalue, icon }) {
  return (
    <div
      style={{
        background: 'rgba(15, 26, 60, 0.55)',
        border: '1px solid rgba(212, 175, 55, 0.22)',
        borderRadius: 8,
        padding: '18px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: 14,
        backdropFilter: 'blur(6px)',
      }}
    >
      <div style={{ color: '#D4AF37' }}>{icon}</div>
      <div style={{ flex: 1 }}>
        <div
          style={{
            fontFamily: '"Cinzel", serif',
            fontSize: '0.75rem',
            letterSpacing: 2,
            color: '#B9B0D5',
            marginBottom: 4,
          }}
        >
          {label.toUpperCase()}
        </div>
        <div
          style={{
            fontFamily: '"Playfair Display", "Cormorant Garamond", serif',
            fontSize: '1.6rem',
            color: '#F5EEE0',
            lineHeight: 1.1,
          }}
        >
          {value}
        </div>
        {subvalue && (
          <div style={{ fontSize: '0.8rem', color: '#B9B0D5', marginTop: 2 }}>{subvalue}</div>
        )}
      </div>
    </div>
  );
}

// Little inline star icon (avoid pulling one more lucide import)
function Sparkle() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M12 2 L14 10 L22 12 L14 14 L12 22 L10 14 L2 12 L10 10 Z" />
    </svg>
  );
}
