import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { Navigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { Loader2, RefreshCw, Sparkles, Download, PlayCircle, Image as ImageIcon, AlertTriangle, CheckCircle2 } from 'lucide-react';
import SEO from '@/components/SEO';
import UtmBuilder from '@/components/UtmBuilder';

const API = process.env.REACT_APP_BACKEND_URL;

const CATEGORIES = [
  { key: 'signs',   label: 'Signes',    n: 12, hint: 'Portraits totem des 12 signes' },
  { key: 'planets', label: 'Planètes',  n: 10, hint: 'Sphères célestes ornées' },
  { key: 'houses',  label: 'Maisons',   n: 12, hint: 'Scènes symboliques des maisons I à XII' },
  { key: 'tarot',   label: 'Tarot',     n: 22, hint: 'Arcanes majeurs illustrés' },
  { key: 'glyphs',  label: 'Glyphes SVG', n: 22, hint: 'Signes + planètes vectoriels' },
];

const StatusBadge = ({ status }) => {
  if (status === 'ok') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[10px] uppercase tracking-widest rounded-full"
        style={{ background: 'rgba(52,199,89,0.12)', color: '#8FEBB4', border: '1px solid rgba(52,199,89,0.3)' }}
        data-testid="asset-status-ok">
        <CheckCircle2 className="w-3 h-3" /> Prêt
      </span>
    );
  }
  if (status === 'error') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[10px] uppercase tracking-widest rounded-full"
        style={{ background: 'rgba(255,80,80,0.12)', color: '#ff9d9d', border: '1px solid rgba(255,80,80,0.3)' }}
        data-testid="asset-status-error">
        <AlertTriangle className="w-3 h-3" /> Erreur
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[10px] uppercase tracking-widest rounded-full"
      style={{ background: 'rgba(197,160,89,0.10)', color: '#C5A059', border: '1px solid rgba(197,160,89,0.25)' }}
      data-testid="asset-status-pending">
      En attente
    </span>
  );
};

const AssetCard = ({ item, entry, onRegen, busy, token }) => {
  const status = entry?.status || 'pending';
  const url = entry?.files?.web ? `${API}${entry.files.web}` : null;
  const hqUrl = entry?.files?.hq ? `${API}${entry.files.hq}` : null;

  return (
    <div className="rounded-2xl overflow-hidden" style={{
      background: 'rgba(255,255,255,0.03)',
      border: '1px solid rgba(197,160,89,0.18)',
      backdropFilter: 'blur(12px)',
    }} data-testid={`asset-card-${item.slug}`}>
      <div className="aspect-square relative" style={{ background: 'linear-gradient(135deg,#0a0d2b,#050716)' }}>
        {url ? (
          <img src={url} alt={item.title} loading="lazy" className="w-full h-full object-cover"
               data-testid={`asset-img-${item.slug}`} />
        ) : (
          <div className="w-full h-full flex items-center justify-center opacity-60">
            <ImageIcon className="w-10 h-10" style={{ color: '#C5A059' }} strokeWidth={1} />
          </div>
        )}
        <div className="absolute top-2 left-2"><StatusBadge status={status} /></div>
      </div>
      <div className="p-3">
        <div className="text-sm mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F4E8D2' }}>{item.title}</div>
        <div className="text-[10px] opacity-60 mb-3" style={{ color: '#C5A059', letterSpacing: '0.08em' }}>{item.slug}</div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onRegen(item.slug)}
            disabled={busy}
            className="text-[10px] uppercase tracking-widest px-3 py-1.5 rounded-full transition-all disabled:opacity-40"
            style={{ border: '1px solid rgba(197,160,89,0.4)', color: '#C5A059' }}
            data-testid={`asset-regen-${item.slug}`}>
            {busy ? <Loader2 className="w-3 h-3 animate-spin" /> : 'Regénérer'}
          </button>
          {hqUrl && (
            <a href={hqUrl} target="_blank" rel="noreferrer"
               className="text-[10px] uppercase tracking-widest px-3 py-1.5 rounded-full flex items-center gap-1"
               style={{ border: '1px solid rgba(197,160,89,0.25)', color: '#C5A059' }}
               data-testid={`asset-download-${item.slug}`}>
              <Download className="w-3 h-3" /> HQ
            </a>
          )}
        </div>
      </div>
    </div>
  );
};

// ────────────────────────────────────────────────────────────
export default function Bibliotheque() {
  const { user, token, loading } = useAuth();
  const [catalog, setCatalog] = useState(null);
  const [status, setStatus] = useState(null);
  const [activeTab, setActiveTab] = useState('signs');
  const [busy, setBusy] = useState(new Set());
  const [batchRunning, setBatchRunning] = useState(false);

  const authHeaders = useMemo(() => (token ? { Authorization: `Bearer ${token}` } : {}), [token]);

  const fetchAll = useCallback(async () => {
    try {
      const [c, s] = await Promise.all([
        axios.get(`${API}/api/library/catalog`),
        axios.get(`${API}/api/library/status`),
      ]);
      setCatalog(c.data);
      setStatus(s.data);
    } catch (e) {
      console.error('[library] load failed', e);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  // Poll every 5s while a batch is running or something is still pending
  useEffect(() => {
    if (!status) return;
    const pending = status.pending > 0;
    if (!pending && !batchRunning) return;
    const iv = setInterval(fetchAll, 5000);
    return () => clearInterval(iv);
  }, [status, batchRunning, fetchAll]);

  const assetsByCat = useMemo(() => {
    const g = { signs: [], planets: [], houses: [], tarot: [] };
    (catalog?.assets || []).forEach(a => { if (g[a.category]) g[a.category].push(a); });
    return g;
  }, [catalog]);

  if (loading) return null;
  if (!user) return <Navigate to="/connexion?next=/bibliotheque" replace />;
  if (!user.is_admin) return <Navigate to="/mon-compte" replace />;

  const startBatch = async (category) => {
    setBatchRunning(true);
    try {
      const params = category ? { category } : {};
      await axios.post(`${API}/api/library/generate`, null, { headers: authHeaders, params });
      setTimeout(fetchAll, 1500);
    } catch (e) {
      alert('Erreur : ' + (e.response?.data?.detail || e.message));
      setBatchRunning(false);
    }
  };

  const regenOne = async (slug) => {
    setBusy(prev => new Set(prev).add(slug));
    try {
      const r = await axios.post(`${API}/api/library/generate/${slug}`, null, { headers: authHeaders });
      setStatus(prev => ({ ...(prev || {}), assets: { ...(prev?.assets || {}), [slug]: r.data } }));
    } catch (e) {
      alert('Regen ' + slug + ' → ' + (e.response?.data?.detail || e.message));
    } finally {
      setBusy(prev => { const n = new Set(prev); n.delete(slug); return n; });
    }
  };

  const regenGlyphs = async () => {
    try {
      await axios.post(`${API}/api/library/glyphs-svg`, null, { headers: authHeaders });
      alert('22 glyphes SVG regénérés.');
    } catch (e) {
      alert('Erreur : ' + (e.response?.data?.detail || e.message));
    }
  };

  const currentItems = activeTab === 'glyphs' ? [] : (assetsByCat[activeTab] || []);
  const done = status?.done || 0;
  const total = status?.total_planned || 56;
  const errors = status?.errors || 0;
  const progressPct = Math.round((done / total) * 100);

  return (
    <div style={{ background: 'linear-gradient(180deg,#0C0918,#12082A)', color: '#F4E8D2', minHeight: '100vh' }}>
      <SEO title="Bibliothèque visuelle — Plume Astrale" description="Studio de génération d'assets astrologiques" />

      <div className="max-w-7xl mx-auto px-4 md:px-8 py-10">

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Sparkles className="w-5 h-5" style={{ color: '#C5A059' }} strokeWidth={1.5} />
            <span className="text-xs uppercase tracking-widest" style={{ color: '#C5A059', letterSpacing: '0.2em' }}>Studio Admin</span>
          </div>
          <h1 className="text-4xl md:text-5xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}>
            Bibliothèque visuelle
          </h1>
          <p className="text-sm opacity-70 max-w-2xl">
            56 illustrations premium générées par IA (Gemini Nano Banana) + 22 glyphes vectoriels.
            Style ancré sur vos 3 références visuelles pour une cohérence parfaite.
          </p>
        </div>

        {/* KPI + Global actions */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="rounded-2xl p-5" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(197,160,89,0.18)' }} data-testid="kpi-done">
            <div className="text-xs uppercase tracking-widest opacity-60" style={{ color: '#C5A059' }}>Générés</div>
            <div className="text-3xl mt-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#C5A059' }}>{done} / {total}</div>
          </div>
          <div className="rounded-2xl p-5" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(197,160,89,0.18)' }} data-testid="kpi-errors">
            <div className="text-xs uppercase tracking-widest opacity-60" style={{ color: '#C5A059' }}>Erreurs</div>
            <div className="text-3xl mt-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: errors > 0 ? '#ff9d9d' : '#C5A059' }}>{errors}</div>
          </div>
          <div className="rounded-2xl p-5 md:col-span-2" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(197,160,89,0.18)' }} data-testid="kpi-progress">
            <div className="text-xs uppercase tracking-widest opacity-60 mb-2" style={{ color: '#C5A059' }}>Progression</div>
            <div className="w-full h-2 rounded-full overflow-hidden" style={{ background: 'rgba(197,160,89,0.12)' }}>
              <div className="h-full transition-all" style={{ width: `${progressPct}%`, background: 'linear-gradient(90deg,#C5A059,#F4E8D2)' }} />
            </div>
            <div className="mt-2 text-xs opacity-60">{progressPct}% · {status?.pending || 0} en attente</div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-3 mb-8">
          <button onClick={() => startBatch()} disabled={batchRunning}
            className="px-5 py-2.5 rounded-full text-xs uppercase tracking-widest flex items-center gap-2 disabled:opacity-50"
            style={{ background: '#C5A059', color: '#0C0918', fontWeight: 500 }}
            data-testid="btn-generate-all">
            {batchRunning ? <Loader2 className="w-4 h-4 animate-spin" /> : <PlayCircle className="w-4 h-4" />}
            Générer tout ce qui manque
          </button>
          <button onClick={fetchAll}
            className="px-5 py-2.5 rounded-full text-xs uppercase tracking-widest flex items-center gap-2"
            style={{ border: '1px solid rgba(197,160,89,0.4)', color: '#C5A059' }}
            data-testid="btn-refresh">
            <RefreshCw className="w-4 h-4" /> Rafraîchir
          </button>
          <button onClick={regenGlyphs}
            className="px-5 py-2.5 rounded-full text-xs uppercase tracking-widest flex items-center gap-2"
            style={{ border: '1px solid rgba(197,160,89,0.4)', color: '#C5A059' }}
            data-testid="btn-regen-glyphs">
            Regénérer les 22 glyphes SVG
          </button>
        </div>

        {/* Tabs */}
        <div className="flex flex-wrap gap-2 mb-6">
          {CATEGORIES.map(c => (
            <button key={c.key} onClick={() => setActiveTab(c.key)}
              className="px-4 py-2 text-xs uppercase tracking-widest rounded-full transition-all"
              style={{
                border: '1px solid',
                borderColor: activeTab === c.key ? '#C5A059' : 'rgba(197,160,89,0.25)',
                color: activeTab === c.key ? '#0C0918' : '#C5A059',
                background: activeTab === c.key ? '#C5A059' : 'transparent',
                letterSpacing: '0.1em',
              }}
              data-testid={`biblio-tab-${c.key}`}>
              {c.label} ({c.n})
            </button>
          ))}
          {activeTab !== 'glyphs' && (
            <button onClick={() => startBatch(activeTab)} disabled={batchRunning}
              className="ml-auto px-4 py-2 text-[10px] uppercase tracking-widest rounded-full disabled:opacity-40"
              style={{ border: '1px solid rgba(197,160,89,0.25)', color: '#C5A059' }}
              data-testid={`btn-generate-cat-${activeTab}`}>
              Générer seulement {CATEGORIES.find(c => c.key === activeTab)?.label}
            </button>
          )}
        </div>

        {/* Hint */}
        <p className="text-xs opacity-60 mb-6">
          {CATEGORIES.find(c => c.key === activeTab)?.hint}
        </p>

        {/* Grid */}
        {activeTab === 'glyphs' ? (
          <GlyphsGrid />
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {currentItems.map(item => (
              <AssetCard key={item.slug}
                item={item}
                entry={status?.assets?.[item.slug]}
                onRegen={regenOne}
                busy={busy.has(item.slug)}
                token={token} />
            ))}
          </div>
        )}

        {/* ═════════════ MARKETING / UTM BUILDER ═════════════ */}
        <div className="mt-16 pt-10 border-t" style={{ borderColor: 'rgba(197,160,89,0.20)' }}>
          <div className="mb-6">
            <div className="text-xs uppercase" style={{ color: '#C5A059', letterSpacing: '0.25em' }}>
              Marketing
            </div>
            <h2 className="text-3xl mt-2" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: '#F4E8D2' }}>
              Tracking des campagnes
            </h2>
          </div>
          <UtmBuilder />
        </div>
      </div>
    </div>
  );
}

// ────────────────────────────────────────────────────────────
// Grille dédiée aux glyphes SVG (les 22)
const GLYPH_SLUGS = [
  'aries','taurus','gemini','cancer','leo','virgo','libra','scorpio','sagittarius','capricorn','aquarius','pisces',
  'sun','moon','mercury','venus','mars','jupiter','saturn','uranus','neptune','pluto',
];
const GLYPH_LABELS = {
  aries:'Bélier',taurus:'Taureau',gemini:'Gémeaux',cancer:'Cancer',leo:'Lion',virgo:'Vierge',libra:'Balance',
  scorpio:'Scorpion',sagittarius:'Sagittaire',capricorn:'Capricorne',aquarius:'Verseau',pisces:'Poissons',
  sun:'Soleil',moon:'Lune',mercury:'Mercure',venus:'Vénus',mars:'Mars',jupiter:'Jupiter',saturn:'Saturne',
  uranus:'Uranus',neptune:'Neptune',pluto:'Pluton',
};

function GlyphsGrid() {
  return (
    <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-4">
      {GLYPH_SLUGS.map(slug => (
        <div key={slug} className="rounded-2xl overflow-hidden"
          style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(197,160,89,0.18)' }}
          data-testid={`glyph-card-${slug}`}>
          <div className="aspect-square" style={{ background: '#0a0d2b' }}>
            <img src={`${API}/api/library/file/glyphs-svg/${slug}.svg`} alt={GLYPH_LABELS[slug]}
                 loading="lazy" className="w-full h-full object-contain" />
          </div>
          <div className="p-2 text-center">
            <div className="text-xs" style={{ color: '#F4E8D2', fontFamily: 'Cormorant Garamond, serif' }}>{GLYPH_LABELS[slug]}</div>
            <a href={`${API}/api/library/file/glyphs-svg/${slug}.svg`} download
               className="text-[10px] uppercase tracking-widest mt-1 inline-flex items-center gap-1"
               style={{ color: '#C5A059' }}
               data-testid={`glyph-download-${slug}`}>
              <Download className="w-3 h-3" /> SVG
            </a>
          </div>
        </div>
      ))}
    </div>
  );
}
