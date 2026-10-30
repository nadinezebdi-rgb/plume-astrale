/**
 * AdminCspReports — tableau agrégé des violations CSP sur 24h/7j.
 *
 * Backend : GET /api/admin/csp-reports?hours=24
 * Audit Nao (2026-10-30 P2-9) : surveiller 7 jours en Report-Only
 * avant de passer la CSP en Enforce.
 */
import {useEffect, useState, useCallback} from 'react';
import { Navigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { Loader2, RefreshCw, Shield, AlertTriangle, Copy, Check } from 'lucide-react';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

const SEVERITY = (count, threshold) => {
  if (count >= threshold) return { color: '#EF4444', label: '⚠︎ seuil Slack' };
  if (count >= Math.max(5, threshold / 5)) return { color: '#F59E0B', label: 'À surveiller' };
  return { color: '#4ADE80', label: 'OK' };
};

/**
 * Construit une directive CSP qui autoriserait la source bloquée.
 * Audit (2026-10-30 · Nao) : accélère le passage Report-Only → Enforce.
 */
function buildCspSuggestion(directive, blockedUri) {
  if (!directive) return null;
  // Normalise la directive (ex. "script-src-elem" → "script-src")
  const base = directive.split(' ')[0].replace(/-elem$|-attr$/, '');
  if (!blockedUri || blockedUri === 'inline' || blockedUri === 'eval') {
    const kw = blockedUri === 'eval' ? "'unsafe-eval'" : "'unsafe-inline'";
    return `${base} ${kw};`;
  }
  try {
    const u = new URL(blockedUri);
    const origin = `${u.protocol}//${u.hostname}`;
    return `${base} ${origin};`;
  } catch {
    // Schemes "data:" / "blob:" / "wasm-eval"
    const m = blockedUri.match(/^([a-z]+):/);
    if (m) return `${base} ${m[1]}:;`;
    return `${base} ${blockedUri};`;
  }
}

function CspSuggestion({ directive, blockedUri }) {
  const [copied, setCopied] = useState(false);
  const suggestion = buildCspSuggestion(directive, blockedUri);
  if (!suggestion) return <span style={{ color: 'var(--pa-muted)' }}>—</span>;
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(suggestion);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* clipboard refusé — pas critique */ }
  };
  return (
    <button
      onClick={copy}
      title="Copier cette directive à ajouter à la CSP nginx"
      className="flex items-center gap-2 px-2 py-1 rounded text-xs"
      style={{
        background: copied ? 'rgba(74,222,128,0.15)' : 'rgba(212,175,55,0.08)',
        border: `1px solid ${copied ? 'rgba(74,222,128,0.4)' : 'rgba(212,175,55,0.3)'}`,
        color: copied ? '#4ADE80' : '#D4AF37',
        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
        maxWidth: 280,
      }}
      data-testid={`csp-suggest-${directive}-${(blockedUri || '').slice(0, 40)}`}
    >
      {copied ? <Check className="w-3 h-3 flex-shrink-0"/> : <Copy className="w-3 h-3 flex-shrink-0"/>}
      <code className="truncate">{suggestion}</code>
    </button>
  );
}

export default function AdminCspReports() {
  const { user, token, loading: authLoading } = useAuth();
  const [hours, setHours] = useState(24);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  const load = useCallback(async () => {
    setLoading(true); setErr(null);
    try {
      const r = await axios.get(`${API}/api/admin/csp-reports?hours=${hours}`,
        { headers: { Authorization: `Bearer ${token}` } });
      setData(r.data);
    } catch (e) {
      setErr(e.response?.data?.detail || 'Erreur chargement.');
    } finally { setLoading(false); }
  }, [token, hours]);

  useEffect(() => { if (token) load(); }, [token, load]);

  if (authLoading) return null;
  if (!user) return <Navigate to="/connexion" replace />;

  const threshold = data?.threshold_slack || 50;

  return (
    <div className="min-h-screen py-16 px-6" style={{ background: '#0B0E1F', color: 'var(--pa-body)' }} data-testid="admin-csp-reports">
      <SEO path="/admin/csp-reports" title="CSP Reports · Plume Astrale" />
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8" style={{ color: '#D4AF37' }} strokeWidth={1.3}/>
            <h1 className="text-3xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#D4AF37' }}>
              Violations Content-Security-Policy
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <select value={hours} onChange={(e) => setHours(parseInt(e.target.value, 10))}
                    className="text-xs uppercase tracking-widest px-3 py-2 rounded-full"
                    style={{ border: '1px solid rgba(212,175,55,0.35)', background: 'transparent', color: '#D4AF37' }}
                    data-testid="hours-select">
              <option value={1}>1h</option>
              <option value={6}>6h</option>
              <option value={24}>24h</option>
              <option value={72}>3j</option>
              <option value={168}>7j</option>
              <option value={720}>30j</option>
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

        <p className="text-sm mb-6" style={{ color: 'var(--pa-muted)' }}>
          Phase actuelle : <strong style={{ color: '#F59E0B' }}>Report-Only</strong> (les violations sont loguées mais le script passe quand même).
          Au-delà de <strong>{threshold}</strong> occurrences identiques en 24h, un ping Slack est envoyé.
          Passe en mode Enforce (nginx) dès que la liste est stable sur 7 jours.
        </p>

        {err && (
          <div className="rounded-xl p-4 mb-6" style={{ background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.35)', color: '#FCA5A5' }}>
            {err}
          </div>
        )}

        {loading && !data && (
          <div className="flex justify-center py-16"><Loader2 className="w-6 h-6 animate-spin" style={{ color: '#D4AF37' }}/></div>
        )}

        {data && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="rounded-2xl p-5" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.18)' }} data-testid="kpi-total">
                <div className="text-[10px] uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)' }}>Total violations</div>
                <div className="text-3xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#D4AF37' }}>{data.total_in_window}</div>
                <div className="text-xs" style={{ color: 'var(--pa-muted)' }}>sur les {data.window_hours}h</div>
              </div>
              <div className="rounded-2xl p-5" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.18)' }} data-testid="kpi-groups">
                <div className="text-[10px] uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)' }}>Groupes (directive × URI)</div>
                <div className="text-3xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#D4AF37' }}>{data.groups?.length || 0}</div>
                <div className="text-xs" style={{ color: 'var(--pa-muted)' }}>top 100 affichés</div>
              </div>
              <div className="rounded-2xl p-5" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.18)' }} data-testid="kpi-threshold">
                <div className="text-[10px] uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)' }}>Seuil Slack</div>
                <div className="text-3xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#D4AF37' }}>{threshold}</div>
                <div className="text-xs" style={{ color: 'var(--pa-muted)' }}>violations identiques /24h</div>
              </div>
            </div>

            {!data.groups || data.groups.length === 0 ? (
              <div className="rounded-2xl p-10 text-center" style={{ background: 'rgba(74,222,128,0.08)', border: '1px solid rgba(74,222,128,0.25)' }}>
                <div className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#4ADE80' }}>
                  Aucune violation sur {data.window_hours}h
                </div>
                <div className="text-sm" style={{ color: 'var(--pa-muted)' }}>
                  Soit la CSP est bien configurée, soit personne n'a visité le site depuis le dernier changement.
                </div>
              </div>
            ) : (
              <div className="rounded-2xl overflow-hidden" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.18)' }}>
                <table className="w-full text-sm" data-testid="csp-table">
                  <thead style={{ background: 'rgba(212,175,55,0.06)' }}>
                    <tr>
                      <th className="text-left px-4 py-3 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Directive</th>
                      <th className="text-left px-4 py-3 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Blocked URI</th>
                      <th className="text-right px-4 py-3 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Count</th>
                      <th className="text-left px-4 py-3 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Sévérité</th>
                      <th className="text-left px-4 py-3 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Suggestion CSP</th>
                      <th className="text-left px-4 py-3 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-muted)' }}>Dernière</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.groups.map((g, i) => {
                      const sev = SEVERITY(g.count, threshold);
                      return (
                        <tr key={`${g.directive}:${g.blocked_uri}:${i}`} style={{ borderTop: '1px solid rgba(212,175,55,0.08)' }}>
                          <td className="px-4 py-3"><code className="text-xs" style={{ color: '#E8A5B9' }}>{g.directive || '—'}</code></td>
                          <td className="px-4 py-3 text-xs truncate" style={{ maxWidth: 300 }}>{g.blocked_uri || <em style={{ color: 'var(--pa-muted)' }}>(inline/eval)</em>}</td>
                          <td className="px-4 py-3 text-right" style={{ color: sev.color, fontFamily: 'Cormorant Garamond, serif', fontSize: 18 }}>{g.count}</td>
                          <td className="px-4 py-3">
                            <span className="text-[10px] uppercase tracking-widest px-2 py-1 rounded-full" style={{ background: `${sev.color}20`, color: sev.color }}>
                              {g.count >= threshold && <AlertTriangle className="w-3 h-3 inline mr-1"/>}
                              {sev.label}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <CspSuggestion directive={g.directive} blockedUri={g.blocked_uri}/>
                          </td>
                          <td className="px-4 py-3 text-xs" style={{ color: 'var(--pa-muted)' }}>
                            {g.last_seen?.slice(0, 16).replace('T', ' ')}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
