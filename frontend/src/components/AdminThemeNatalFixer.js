import React, { useState } from 'react';
import axios from 'axios';
import { Loader2, MapPin, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Panneau admin "Correction Thème Natal" — sans commande curl à taper.
 *
 * Flow :
 * 1) Saisie session_id → clic "Inspecter" → affiche les données actuelles
 * 2) Correction de la ville : soit géocodage auto, soit lat/lon/tz manuels
 * 3) Bouton "Régénérer PDF" → lance en arrière-plan et poll toutes les 3s
 * 4) Affiche le diagnostic final (is_ultra, pdf_pages, ai_source…)
 */
const AdminThemeNatalFixer = ({ token }) => {
  const [sessionId, setSessionId] = useState('admin-natal-6684bc835ba7448c');
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);
  const [msg, setMsg] = useState(null);

  const [cityQuery, setCityQuery] = useState('');
  const [latManual, setLatManual] = useState('');
  const [lonManual, setLonManual] = useState('');
  const [tzManual, setTzManual] = useState('Europe/Paris');

  const [regenPolling, setRegenPolling] = useState(false);
  const [diag, setDiag] = useState(null);

  const headers = { Authorization: `Bearer ${token}` };

  const inspect = async () => {
    setErr(null); setMsg(null); setDiag(null);
    if (!sessionId) return;
    setLoading(true);
    try {
      const r = await axios.get(`${API}/api/admin/theme-natal/inspect/${sessionId}`, { headers });
      setInfo(r.data);
      if (r.data.regenerate_diag) setDiag(r.data.regenerate_diag);
    } catch (e) {
      setErr(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  };

  const patchByCity = async () => {
    setErr(null); setMsg(null);
    if (!cityQuery.trim()) return setErr('Tape le nom d’une ville (ex : "Saint-Avold, France")');
    setLoading(true);
    try {
      const r = await axios.patch(
        `${API}/api/admin/theme-natal/${sessionId}/birth-data`,
        { city: cityQuery },
        { headers },
      );
      setMsg(`✅ Ville corrigée : ${r.data.resolved?.display_name || cityQuery} (${r.data.resolved?.lat}, ${r.data.resolved?.lon}, tz=${r.data.resolved?.tz})`);
      await inspect();
    } catch (e) {
      setErr(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  };

  const patchManual = async () => {
    setErr(null); setMsg(null);
    const lat = parseFloat(latManual), lon = parseFloat(lonManual);
    if (isNaN(lat) || isNaN(lon)) return setErr('Latitude/Longitude invalides');
    setLoading(true);
    try {
      await axios.patch(
        `${API}/api/admin/theme-natal/${sessionId}/birth-data`,
        { latitude: lat, longitude: lon, timezone: tzManual },
        { headers },
      );
      setMsg(`✅ Coordonnées manuelles enregistrées : ${lat}, ${lon}, tz=${tzManual}`);
      await inspect();
    } catch (e) {
      setErr(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  };

  const regenerate = async () => {
    setErr(null); setMsg(null); setDiag(null); setRegenPolling(true);
    try {
      await axios.post(`${API}/api/admin/theme-natal/regenerate/${sessionId}`, {}, { headers });
      setMsg('⏳ Régénération lancée en arrière-plan. Attends 30-90 secondes…');
      // Poll toutes les 3s pendant 3 minutes max
      const t0 = Date.now();
      const poll = async () => {
        try {
          const r = await axios.get(`${API}/api/admin/theme-natal/inspect/${sessionId}`, { headers });
          setInfo(r.data);
          if (r.data.regenerate_diag) {
            setDiag(r.data.regenerate_diag);
            setMsg('✅ Régénération terminée !');
            setRegenPolling(false);
            return;
          }
          if (r.data.regenerate_error) {
            setErr(`Régénération échouée : ${r.data.regenerate_error}`);
            setRegenPolling(false);
            return;
          }
          if (Date.now() - t0 > 180000) {
            setErr('Timeout après 3 minutes — regarde les logs backend');
            setRegenPolling(false);
            return;
          }
          setTimeout(poll, 3000);
        } catch (e) {
          setErr(e.response?.data?.detail || e.message);
          setRegenPolling(false);
        }
      };
      setTimeout(poll, 3000);
    } catch (e) {
      setErr(e.response?.data?.detail || e.message);
      setRegenPolling(false);
    }
  };

  const bd = info?.birth_data_source;

  return (
    <div className="space-y-6" data-testid="admin-theme-natal-fixer">
      <div className="rounded-2xl p-5" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.18)' }}>
        <h3 className="text-base mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>
          Session Thème Natal à corriger
        </h3>
        <div className="flex gap-3">
          <input
            data-testid="fixer-session-id"
            value={sessionId}
            onChange={e => setSessionId(e.target.value.trim())}
            placeholder="admin-natal-... ou cs_live_..."
            className="flex-1 px-4 py-3 rounded-lg text-sm font-mono"
            style={{ background: 'rgba(0,0,0,0.35)', border: '1px solid rgba(212,175,55,0.25)', color: '#F5EEE0' }}
          />
          <button
            data-testid="fixer-inspect-btn"
            onClick={inspect}
            disabled={loading}
            className="px-5 py-3 rounded-lg text-xs uppercase tracking-widest"
            style={{ background: '#D4AF37', color: '#111625', letterSpacing: '0.1em', fontWeight: 500 }}
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Inspecter'}
          </button>
        </div>
      </div>

      {err && (
        <div className="rounded-lg p-4 flex items-start gap-2" style={{ background: 'rgba(248,113,113,0.10)', border: '1px solid rgba(248,113,113,0.35)', color: '#FCA5A5' }}>
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" /> <span className="text-sm">{err}</span>
        </div>
      )}
      {msg && (
        <div className="rounded-lg p-4 flex items-start gap-2" style={{ background: 'rgba(74,222,128,0.10)', border: '1px solid rgba(74,222,128,0.35)', color: '#86EFAC' }}>
          <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" /> <span className="text-sm">{msg}</span>
        </div>
      )}

      {bd && (
        <div className="rounded-2xl p-5" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.18)' }}>
          <h3 className="text-base mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>
            Données actuelles en base
          </h3>
          <table className="text-sm w-full" style={{ color: 'rgba(227,215,255,0.85)' }}>
            <tbody>
              <tr><td className="py-1 pr-4 opacity-60">Prénom</td><td className="font-mono">{bd.first_name}</td></tr>
              <tr><td className="py-1 pr-4 opacity-60">Date naissance</td><td className="font-mono">{bd.birth_date_iso} {bd.hour}:{String(bd.minute).padStart(2, '0')}</td></tr>
              <tr><td className="py-1 pr-4 opacity-60">Ville stockée</td><td className="font-mono">{bd.city || '—'}</td></tr>
              <tr>
                <td className="py-1 pr-4 opacity-60">Latitude / Longitude</td>
                <td className="font-mono">
                  {bd.latitude} / {bd.longitude}
                  {Math.abs(bd.latitude - 48.8566) < 0.01 && Math.abs(bd.longitude - 2.3522) < 0.01 && (
                    <span className="ml-2 text-xs" style={{ color: '#FCA5A5' }}>⚠ coordonnées de Paris</span>
                  )}
                </td>
              </tr>
              <tr>
                <td className="py-1 pr-4 opacity-60">Timezone</td>
                <td className="font-mono">
                  {bd.timezone || <span style={{ color: '#FCA5A5' }}>null ⚠</span>}
                </td>
              </tr>
              <tr><td className="py-1 pr-4 opacity-60">PDF généré à</td><td className="font-mono text-xs">{info.pdf_generated_at || '—'}</td></tr>
            </tbody>
          </table>
        </div>
      )}

      {info && (
        <>
          <div className="rounded-2xl p-5" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.18)' }}>
            <h3 className="text-base mb-2 flex items-center gap-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>
              <MapPin className="w-4 h-4" /> Corriger la ville (géocodage automatique)
            </h3>
            <p className="text-xs opacity-60 mb-3" style={{ color: 'var(--pa-muted)' }}>Tape &quot;Saint-Avold, France&quot; → l&apos;endpoint récupère latitude, longitude et timezone tout seul via OpenStreetMap.</p>
            <div className="flex gap-3">
              <input
                data-testid="fixer-city-input"
                value={cityQuery}
                onChange={e => setCityQuery(e.target.value)}
                placeholder="Ex : Saint-Avold, France"
                className="flex-1 px-4 py-3 rounded-lg text-sm"
                style={{ background: 'rgba(0,0,0,0.35)', border: '1px solid rgba(212,175,55,0.25)', color: '#F5EEE0' }}
              />
              <button
                data-testid="fixer-city-apply"
                onClick={patchByCity}
                disabled={loading || !cityQuery.trim()}
                className="px-5 py-3 rounded-lg text-xs uppercase tracking-widest"
                style={{ background: '#D4AF37', color: '#111625', letterSpacing: '0.1em', fontWeight: 500 }}
              >
                Corriger via ville
              </button>
            </div>
          </div>

          <details className="rounded-2xl p-5" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.18)' }}>
            <summary className="cursor-pointer text-sm opacity-80" style={{ color: 'var(--pa-body)' }}>
              Ou saisir manuellement lat / lon / timezone
            </summary>
            <div className="grid grid-cols-3 gap-3 mt-4">
              <input data-testid="fixer-lat" value={latManual} onChange={e => setLatManual(e.target.value)} placeholder="Latitude (ex 49.1057)" className="px-3 py-2 rounded-lg text-sm font-mono" style={{ background: 'rgba(0,0,0,0.35)', border: '1px solid rgba(212,175,55,0.25)', color: '#F5EEE0' }} />
              <input data-testid="fixer-lon" value={lonManual} onChange={e => setLonManual(e.target.value)} placeholder="Longitude (ex 6.7075)" className="px-3 py-2 rounded-lg text-sm font-mono" style={{ background: 'rgba(0,0,0,0.35)', border: '1px solid rgba(212,175,55,0.25)', color: '#F5EEE0' }} />
              <input data-testid="fixer-tz" value={tzManual} onChange={e => setTzManual(e.target.value)} placeholder="Timezone" className="px-3 py-2 rounded-lg text-sm font-mono" style={{ background: 'rgba(0,0,0,0.35)', border: '1px solid rgba(212,175,55,0.25)', color: '#F5EEE0' }} />
            </div>
            <button
              data-testid="fixer-manual-apply"
              onClick={patchManual}
              disabled={loading || !latManual || !lonManual}
              className="mt-3 px-5 py-2 rounded-lg text-xs uppercase tracking-widest"
              style={{ background: '#D4AF37', color: '#111625', letterSpacing: '0.1em', fontWeight: 500 }}
            >
              Appliquer les coordonnées manuelles
            </button>
          </details>

          <div className="rounded-2xl p-5 text-center" style={{ background: 'rgba(212,175,55,0.06)', border: '1px solid rgba(212,175,55,0.35)' }}>
            <h3 className="text-base mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>Étape finale — Régénérer le PDF</h3>
            <p className="text-xs opacity-70 mb-4" style={{ color: 'var(--pa-body)' }}>Lance le pipeline complet : API v3 + GPT-5.4 + génération PDF + upload Supabase. Le job tourne en arrière-plan, l&apos;écran se met à jour tout seul.</p>
            <button
              data-testid="fixer-regenerate-btn"
              onClick={regenerate}
              disabled={loading || regenPolling}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full text-xs uppercase tracking-widest"
              style={{ background: '#D4AF37', color: '#111625', letterSpacing: '0.15em', fontWeight: 500 }}
            >
              {regenPolling ? <><Loader2 className="w-4 h-4 animate-spin" /> Génération en cours…</> : <><RefreshCw className="w-4 h-4" /> Régénérer le PDF</>}
            </button>
          </div>

          {diag && (
            <div className="rounded-2xl p-5" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.30)' }}>
              <h3 className="text-base mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>Diagnostic de la régénération</h3>
              <table className="text-sm w-full" style={{ color: 'rgba(227,215,255,0.9)' }}>
                <tbody>
                  <DiagRow label="Mode" value={diag.is_ultra ? 'ULTRA (11 planètes)' : 'LEGACY (5 planètes) ⚠'} highlight={!diag.is_ultra} />
                  <DiagRow label="Pages PDF" value={diag.pdf_pages ?? '—'} highlight={diag.pdf_pages && diag.pdf_pages < 20} />
                  <DiagRow label="Taille PDF" value={diag.pdf_bytes ? `${(diag.pdf_bytes / 1024 / 1024).toFixed(2)} Mo` : '—'} />
                  <DiagRow label="Source IA" value={diag.ai_source} highlight={diag.ai_source === 'none'} />
                  <DiagRow label="Planètes GPT enrichies" value={diag.ai_planet_count} />
                  <DiagRow label="Planètes API v3 (fallback)" value={diag.v3_raw_count} />
                  <DiagRow label="Interpretations API v3" value={diag.interpretations_count} highlight={!diag.interpretations_count} />
                  {diag.ai_error && <DiagRow label="Erreur GPT" value={diag.ai_error} highlight={true} />}
                  {diag.error && <DiagRow label="Erreur" value={diag.error} highlight={true} />}
                  {info.pdf_supabase_url && (
                    <tr>
                      <td className="py-1 pr-4 opacity-60">Télécharger le nouveau PDF</td>
                      <td>
                        <a href={info.pdf_supabase_url} target="_blank" rel="noopener noreferrer" style={{ color: '#D4AF37', textDecoration: 'underline' }} data-testid="fixer-download-link">
                          Ouvrir le PDF frais
                        </a>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
};

const DiagRow = ({ label, value, highlight }) => (
  <tr>
    <td className="py-1 pr-4 opacity-60">{label}</td>
    <td className="font-mono" style={{ color: highlight ? '#FCA5A5' : undefined }}>{String(value)}</td>
  </tr>
);

export default AdminThemeNatalFixer;
