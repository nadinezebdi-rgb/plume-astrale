import React, { useState, useMemo } from 'react';
import { Copy, ExternalLink, Sparkles, Check } from 'lucide-react';

const BASE_URL = process.env.REACT_APP_BACKEND_URL || 'https://plume-astrale.fr';

// Presets de campagnes courantes
const PRESETS = [
  { key: 'tiktok_rencontres', label: 'TikTok — Rencontres', params: { utm_source: 'tiktok', utm_medium: 'social', utm_campaign: 'rencontres' }, path: '/rencontres-astrales' },
  { key: 'tiktok_astrosexo',  label: 'TikTok — AstroSexo',  params: { utm_source: 'tiktok', utm_medium: 'social', utm_campaign: 'astrosexo' }, path: '/astrosexo' },
  { key: 'insta_rencontres',  label: 'Instagram — Rencontres', params: { utm_source: 'instagram', utm_medium: 'social', utm_campaign: 'rencontres' }, path: '/rencontres-astrales' },
  { key: 'insta_story',       label: 'Instagram Story', params: { utm_source: 'instagram', utm_medium: 'story', utm_campaign: 'rencontres' }, path: '/rencontres-astrales' },
  { key: 'newsletter',        label: 'Newsletter Resend', params: { utm_source: 'resend', utm_medium: 'email', utm_campaign: 'nurture' }, path: '/rencontres-astrales' },
  { key: 'custom',            label: '✎ Personnalisé', params: {}, path: '/rencontres-astrales' },
];

/**
 * Small admin utility — builds a tracked campaign URL to paste in TikTok/social.
 * Standalone panel usable in /admin or /bibliotheque.
 */
export default function UtmBuilder() {
  const [presetKey, setPresetKey] = useState('tiktok_rencontres');
  const [source, setSource] = useState('tiktok');
  const [medium, setMedium] = useState('social');
  const [campaign, setCampaign] = useState('rencontres');
  const [content, setContent] = useState('');
  const [path, setPath] = useState('/rencontres-astrales');
  const [copied, setCopied] = useState(false);

  const applyPreset = (key) => {
    setPresetKey(key);
    const p = PRESETS.find(x => x.key === key);
    if (p && key !== 'custom') {
      setSource(p.params.utm_source || '');
      setMedium(p.params.utm_medium || '');
      setCampaign(p.params.utm_campaign || '');
      setPath(p.path || '/rencontres-astrales');
      setContent('');
    }
  };

  const url = useMemo(() => {
    const base = (typeof window !== 'undefined' ? window.location.origin : BASE_URL);
    const qs = new URLSearchParams();
    if (source) qs.set('utm_source', source);
    if (medium) qs.set('utm_medium', medium);
    if (campaign) qs.set('utm_campaign', campaign);
    if (content) qs.set('utm_content', content);
    const p = path.startsWith('/') ? path : '/' + path;
    const q = qs.toString();
    return `${base}${p}${q ? '?' + q : ''}`;
  }, [source, medium, campaign, content, path]);

  const copyUrl = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) { /* ignore */ }
  };

  return (
    <div className="rounded-2xl p-6"
      style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.20)', backdropFilter: 'blur(12px)' }}
      data-testid="utm-builder">

      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-4 h-4" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
        <h2 className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>
          Générateur de liens de campagne
        </h2>
      </div>
      <p className="text-xs opacity-70 mb-5" style={{ color: '#F5EEE0' }}>
        Choisis un preset, ajuste au besoin, copie le lien et colle-le dans ta bio TikTok / Instagram.
        Chaque acheteur sera automatiquement attribué à sa campagne.
      </p>

      {/* Presets */}
      <div className="flex flex-wrap gap-2 mb-5" data-testid="utm-presets">
        {PRESETS.map(p => (
          <button key={p.key} onClick={() => applyPreset(p.key)}
            className="text-[10px] uppercase px-3 py-1.5 rounded-full transition-all"
            style={{
              border: '1px solid',
              borderColor: presetKey === p.key ? '#D4AF37' : 'rgba(212,175,55,0.25)',
              color: presetKey === p.key ? '#111625' : '#D4AF37',
              background: presetKey === p.key ? '#D4AF37' : 'transparent',
              letterSpacing: '0.1em',
            }}
            data-testid={`utm-preset-${p.key}`}>
            {p.label}
          </button>
        ))}
      </div>

      {/* Fields */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
        <Field label="Path" value={path} onChange={setPath} testid="utm-path" placeholder="/rencontres-astrales" />
        <Field label="utm_source" value={source} onChange={setSource} testid="utm-source" placeholder="tiktok" />
        <Field label="utm_medium" value={medium} onChange={setMedium} testid="utm-medium" placeholder="social" />
        <Field label="utm_campaign" value={campaign} onChange={setCampaign} testid="utm-campaign" placeholder="rencontres" />
        <Field label="utm_content (optionnel)" value={content} onChange={setContent} testid="utm-content"
          placeholder="video_01_hook_a" fullWidth />
      </div>

      {/* Result */}
      <div className="rounded-xl p-4 mb-3" style={{ background: 'rgba(0,0,0,0.35)', border: '1px solid rgba(212,175,55,0.25)' }}>
        <div className="text-[10px] uppercase mb-2 opacity-60" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>
          URL trackée
        </div>
        <div className="text-xs break-all font-mono" style={{ color: '#F5EEE0' }} data-testid="utm-url">
          {url}
        </div>
      </div>

      <div className="flex gap-2">
        <button onClick={copyUrl}
          className="flex-1 px-4 py-2.5 rounded-full text-xs uppercase transition-all flex items-center justify-center gap-2"
          style={{
            background: copied ? '#8FEBB4' : '#D4AF37',
            color: '#111625',
            letterSpacing: '0.15em', fontWeight: 600,
          }}
          data-testid="utm-copy-btn">
          {copied ? <><Check className="w-4 h-4" /> Copié !</> : <><Copy className="w-4 h-4" /> Copier le lien</>}
        </button>
        <a href={url} target="_blank" rel="noreferrer"
          className="px-4 py-2.5 rounded-full text-xs uppercase transition-all flex items-center gap-2"
          style={{ border: '1px solid #D4AF37', color: '#D4AF37', letterSpacing: '0.15em' }}
          data-testid="utm-preview-btn">
          <ExternalLink className="w-4 h-4" /> Prévisualiser
        </a>
      </div>

      <p className="text-[10px] opacity-50 mt-4" style={{ color: '#F5EEE0' }}>
        💡 Astuce : varie `utm_content` (ex: <code>video_01</code>, <code>video_02</code>) pour comparer plusieurs
        versions de la même campagne (A/B testing).
      </p>
    </div>
  );
}

function Field({ label, value, onChange, placeholder, fullWidth, testid }) {
  return (
    <div className={fullWidth ? 'md:col-span-2' : ''}>
      <label className="text-[10px] uppercase mb-1.5 block" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>
        {label}
      </label>
      <input value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder}
        className="w-full py-2 px-3 rounded-lg text-sm outline-none"
        style={{ background: 'rgba(255,255,255,0.05)', color: '#F5EEE0', border: '1px solid rgba(212,175,55,0.20)' }}
        data-testid={testid} />
    </div>
  );
}
