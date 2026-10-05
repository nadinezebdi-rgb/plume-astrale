import React, { useState } from 'react';
import axios from 'axios';
import { Loader2, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;
const PROMO = 'TOUT2026';

// Villes de démonstration pour l'astrocartographie (3 villes exactement).
const ASTRO_CITIES = [
  { city: 'Lisbonne', country: 'Portugal', country_code: 'PT', latitude: 38.7223, longitude: -9.1393 },
  { city: 'New York', country: 'États-Unis', country_code: 'US', latitude: 40.7128, longitude: -74.006 },
  { city: 'Tokyo', country: 'Japon', country_code: 'JP', latitude: 35.6762, longitude: 139.6503 },
];

const PRODUCTS = [
  { key: 'natal', label: 'Thème Natal', path: '/api/theme-natal-oneshot/checkout' },
  { key: 'numerologie', label: 'Numérologie sacrée', path: '/api/numerologie/checkout' },
  { key: 'kabbale', label: 'Arbre de Vie · Kabbale', path: '/api/kabbale/checkout' },
  { key: 'karma', label: 'Karma & Destin', path: '/api/karma-destin/checkout' },
  { key: 'voyage', label: 'Voyage karmique', path: '/api/voyage-karmique/checkout' },
  { key: 'pack', label: 'Pack Karmique', path: '/api/pack-karmique/checkout' },
  { key: 'astrocarto', label: 'Astrocartographie', path: '/api/astrocartographie/checkout', extra: () => ({ chosen_cities: ASTRO_CITIES }) },
  { key: 'synastrie', label: 'Astrologie relationnelle (synastrie)', path: '/api/synastrie/checkout' },
];

const inputStyle = {
  width: '100%', padding: '10px 12px', borderRadius: 8, background: 'rgba(12,9,24,0.6)',
  border: '1px solid rgba(212,175,55,0.25)', color: '#F4E8D2', fontSize: 14,
};

const Field = ({ label, children }) => (
  <label className="block text-xs" style={{ color: 'var(--pa-muted)' }}>
    <span className="block mb-1 uppercase" style={{ letterSpacing: '0.1em' }}>{label}</span>
    {children}
  </label>
);

/**
 * Admin : génère un PDF de chaque lecture sans paiement (code TOUT2026, compte admin)
 * et l'envoie par e-mail. Les PDF apparaissent aussi dans l'onglet « PDFs envoyés ».
 */
export default function AdminGenerateReadings({ token, defaultEmail = '' }) {
  const [form, setForm] = useState({
    email: defaultEmail, first_name: '', birth_date: '', birth_time: '12:00',
    birth_city: '', birth_country: 'FR',
  });
  const [partner, setPartner] = useState({ prenom: '', birth_date: '', birth_time: '12:00', birth_place: '' });
  const [selected, setSelected] = useState(() => PRODUCTS.map((p) => p.key));
  const [results, setResults] = useState({});
  const [running, setRunning] = useState(false);

  const upd = (k, v) => setForm((f) => ({ ...f, [k]: v }));
  const toggle = (key) => setSelected((s) => (s.includes(key) ? s.filter((k) => k !== key) : [...s, key]));

  const buildPayload = (product) => {
    if (product.key === 'synastrie') {
      return {
        person1: {
          prenom: form.first_name, birth_date: form.birth_date, birth_time: form.birth_time,
          birth_place: form.birth_city, birth_country: form.birth_country,
        },
        person2: {
          prenom: partner.prenom || 'Partenaire', birth_date: partner.birth_date, birth_time: partner.birth_time,
          birth_place: partner.birth_place || form.birth_city, birth_country: form.birth_country,
        },
        email: form.email,
        origin_url: window.location.origin,
        promo_code: PROMO,
      };
    }
    return {
      ...form,
      latitude: null,
      longitude: null,
      origin_url: window.location.origin,
      promo_code: PROMO,
      ...(product.extra ? product.extra() : {}),
    };
  };

  const valid = form.email.includes('@') && form.first_name.trim() && form.birth_date && form.birth_time && form.birth_city.trim();

  const run = async () => {
    setRunning(true);
    setResults({});
    for (const product of PRODUCTS.filter((p) => selected.includes(p.key))) {
      setResults((r) => ({ ...r, [product.key]: { status: 'running' } }));
      try {
        const res = await axios.post(`${API}${product.path}`, buildPayload(product), {
          headers: { Authorization: `Bearer ${token}` },
          timeout: 60000,
        });
        const d = res.data || {};
        // Une redirection Stripe signifie que le bypass admin n'a pas été appliqué.
        const paid = d.url && String(d.session_id || '').startsWith('cs_') && !d.admin_bypass;
        setResults((r) => ({
          ...r,
          [product.key]: paid
            ? { status: 'error', message: 'Paiement demandé : le bypass admin n\u2019a pas été appliqué (compte non admin ?).' }
            : { status: 'ok', sessionId: d.session_id },
        }));
      } catch (e) {
        const detail = e.response?.data?.detail;
        setResults((r) => ({
          ...r,
          [product.key]: { status: 'error', message: typeof detail === 'string' ? detail : (e.message || 'Erreur') },
        }));
      }
    }
    setRunning(false);
  };

  return (
    <div className="rounded-2xl p-6" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.15)' }} data-testid="admin-generate-readings">
      <h2 className="text-lg mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#D4AF37' }}>
        <Sparkles className="inline w-4 h-4 mr-2" />Générer les lectures (sans paiement)
      </h2>
      <p className="text-xs mb-6" style={{ color: 'var(--pa-muted)' }}>
        Le code {PROMO} est appliqué avec votre session administrateur. Chaque PDF est généré en arrière-plan (quelques minutes)
        puis envoyé à l&apos;e-mail ci-dessous, et listé dans l&apos;onglet « PDFs envoyés ».
      </p>

      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <Field label="E-mail de réception"><input style={inputStyle} type="email" value={form.email} onChange={(e) => upd('email', e.target.value)} data-testid="gen-email" /></Field>
        <Field label="Prénom"><input style={inputStyle} value={form.first_name} onChange={(e) => upd('first_name', e.target.value)} data-testid="gen-first-name" /></Field>
        <Field label="Date de naissance"><input style={inputStyle} type="date" value={form.birth_date} onChange={(e) => upd('birth_date', e.target.value)} data-testid="gen-birth-date" /></Field>
        <Field label="Heure de naissance"><input style={inputStyle} type="time" value={form.birth_time} onChange={(e) => upd('birth_time', e.target.value)} data-testid="gen-birth-time" /></Field>
        <Field label="Ville de naissance"><input style={inputStyle} value={form.birth_city} onChange={(e) => upd('birth_city', e.target.value)} data-testid="gen-birth-city" /></Field>
        <Field label="Pays (code)"><input style={inputStyle} value={form.birth_country} onChange={(e) => upd('birth_country', e.target.value.toUpperCase())} maxLength={2} /></Field>
      </div>

      {selected.includes('synastrie') && (
        <div className="mb-6">
          <p className="text-xs uppercase mb-2" style={{ color: '#D4AF37', letterSpacing: '0.1em' }}>Partenaire (synastrie)</p>
          <div className="grid md:grid-cols-2 gap-4">
            <Field label="Prénom"><input style={inputStyle} value={partner.prenom} onChange={(e) => setPartner((p) => ({ ...p, prenom: e.target.value }))} /></Field>
            <Field label="Date de naissance"><input style={inputStyle} type="date" value={partner.birth_date} onChange={(e) => setPartner((p) => ({ ...p, birth_date: e.target.value }))} data-testid="gen-partner-date" /></Field>
            <Field label="Heure"><input style={inputStyle} type="time" value={partner.birth_time} onChange={(e) => setPartner((p) => ({ ...p, birth_time: e.target.value }))} /></Field>
            <Field label="Ville"><input style={inputStyle} value={partner.birth_place} onChange={(e) => setPartner((p) => ({ ...p, birth_place: e.target.value }))} placeholder="Par défaut : même ville" /></Field>
          </div>
        </div>
      )}

      <ul className="mb-6 space-y-2">
        {PRODUCTS.map((p) => {
          const r = results[p.key];
          return (
            <li key={p.key} className="flex items-center gap-3 text-sm" style={{ color: '#F4E8D2' }} data-testid={`gen-row-${p.key}`}>
              <input type="checkbox" checked={selected.includes(p.key)} onChange={() => toggle(p.key)} disabled={running} />
              <span className="flex-1">{p.label}{p.key === 'astrocarto' ? ' (Lisbonne, New York, Tokyo)' : ''}</span>
              {r?.status === 'running' && <Loader2 className="w-4 h-4 animate-spin" style={{ color: '#D4AF37' }} />}
              {r?.status === 'ok' && (
                <span className="flex items-center gap-1 text-xs" style={{ color: '#4ADE80' }}>
                  <CheckCircle2 className="w-4 h-4" /> Lancée
                </span>
              )}
              {r?.status === 'error' && (
                <span className="flex items-center gap-1 text-xs" style={{ color: '#F87171' }} data-testid={`gen-error-${p.key}`}>
                  <AlertCircle className="w-4 h-4" /> {r.message}
                </span>
              )}
            </li>
          );
        })}
      </ul>

      <button
        type="button"
        onClick={run}
        disabled={running || !valid || selected.length === 0}
        data-testid="gen-run"
        style={{
          padding: '12px 24px', borderRadius: 999, background: '#D4AF37', color: '#0C0918', fontWeight: 600,
          opacity: running || !valid || selected.length === 0 ? 0.5 : 1, cursor: running ? 'wait' : 'pointer',
        }}
      >
        {running ? 'Génération en cours…' : 'Générer les PDF sélectionnés'}
      </button>
    </div>
  );
}
