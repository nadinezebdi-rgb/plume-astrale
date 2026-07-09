import React, { useState, useEffect } from 'react';
import { X, Loader2, Check } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const COUNTRIES = [
  'France', 'Belgique', 'Suisse', 'Canada', 'Luxembourg', 'Monaco',
  'Algérie', 'Maroc', 'Tunisie', 'Sénégal', "Côte d'Ivoire",
  'États-Unis', 'Royaume-Uni', 'Allemagne', 'Espagne', 'Italie', 'Portugal', 'Autre',
];

export default function NatalDataModal({ open, onClose, onSuccess }) {
  const { user, updateProfile } = useAuth();
  const [form, setForm] = useState({
    prenom: '', gender: 'female',
    birth_date: '', birth_time: '',
    birth_place: '', birth_country: 'France',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (open && user) {
      setForm({
        prenom: user.prenom || '',
        gender: user.gender || 'female',
        birth_date: user.birth_date || '',
        birth_time: user.birth_time || '',
        birth_place: user.birth_place || '',
        birth_country: user.birth_country || 'France',
      });
      setError(null);
      setSuccess(false);
    }
  }, [open, user]);

  if (!open) return null;

  const handleChange = (field, value) => {
    setForm((f) => ({ ...f, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.birth_date || !form.birth_place) {
      setError('La date et le lieu de naissance sont obligatoires.');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await updateProfile(form);
      setSuccess(true);
      setTimeout(() => { onSuccess?.(); onClose(); }, 900);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Erreur lors de la mise à jour.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      data-testid="natal-modal"
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 100,
        background: 'rgba(6,8,26,0.78)', backdropFilter: 'blur(8px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: 16, animation: 'fadeIn 0.25s ease-out',
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: 'linear-gradient(180deg, rgba(20,24,60,0.97) 0%, rgba(11,14,40,0.97) 100%)',
          border: '1px solid rgba(212,175,55,0.3)',
          borderRadius: 18, padding: '28px 24px',
          maxWidth: 480, width: '100%', maxHeight: '90vh', overflowY: 'auto',
          boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
        }}
      >
        <style>{`@keyframes fadeIn { from {opacity:0} to {opacity:1} }`}</style>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
          <div>
            <h3 style={{
              fontFamily: 'Cormorant Garamond, serif', fontSize: 24, color: '#F4E4BC',
              fontWeight: 400, margin: 0, lineHeight: 1.15,
            }}>
              Mes données natales
            </h3>
            <p style={{ fontSize: 12, color: 'rgba(255,255,255,0.55)', margin: '6px 0 0' }}>
              Modifie tes informations pour affiner toutes tes lectures.
            </p>
          </div>
          <button onClick={onClose} aria-label="Fermer" data-testid="natal-modal-close"
            style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.5)', padding: 4 }}>
            <X style={{ width: 18, height: 18 }} strokeWidth={1.5} />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* Prenom */}
          <Field label="Prénom (facultatif)">
            <input type="text" value={form.prenom} onChange={(e) => handleChange('prenom', e.target.value)}
              data-testid="natal-prenom" style={inputStyle} placeholder="Votre prenom" />
          </Field>

          {/* Genre */}
          <Field label="Genre">
            <div style={{ display: 'flex', gap: 8 }}>
              {[{ v: 'female', l: 'Féminin' }, { v: 'male', l: 'Masculin' }, { v: 'other', l: 'Autre' }].map((opt) => (
                <button key={opt.v} type="button"
                  onClick={() => handleChange('gender', opt.v)}
                  data-testid={`natal-gender-${opt.v}`}
                  style={{
                    flex: 1, padding: '9px 8px', borderRadius: 10,
                    border: form.gender === opt.v ? '1px solid #D4AF37' : '1px solid rgba(212,175,55,0.25)',
                    background: form.gender === opt.v ? 'rgba(212,175,55,0.15)' : 'rgba(255,255,255,0.03)',
                    color: form.gender === opt.v ? '#F4E4BC' : 'rgba(255,255,255,0.7)',
                    fontSize: 12, cursor: 'pointer', transition: 'all 0.2s',
                    fontFamily: 'Cinzel, serif', letterSpacing: '0.06em',
                  }}>{opt.l}</button>
              ))}
            </div>
          </Field>

          {/* Date naissance */}
          <Field label="Date de naissance *">
            <input type="date" value={form.birth_date} onChange={(e) => handleChange('birth_date', e.target.value)}
              data-testid="natal-birth-date" style={inputStyle} required
              max={new Date().toISOString().split('T')[0]} />
          </Field>

          {/* Heure */}
          <Field label="Heure de naissance (recommandé pour l'ascendant)">
            <input type="time" value={form.birth_time} onChange={(e) => handleChange('birth_time', e.target.value)}
              data-testid="natal-birth-time" style={inputStyle} placeholder="12:00" />
          </Field>

          {/* Lieu */}
          <Field label="Ville de naissance *">
            <input type="text" value={form.birth_place} onChange={(e) => handleChange('birth_place', e.target.value)}
              data-testid="natal-birth-place" style={inputStyle} placeholder="Paris, Casablanca, Tunis..." required />
          </Field>

          {/* Pays */}
          <Field label="Pays">
            <select value={form.birth_country} onChange={(e) => handleChange('birth_country', e.target.value)}
              data-testid="natal-birth-country" style={inputStyle}>
              {COUNTRIES.map((c) => <option key={c} value={c} style={{ background: '#0F1230', color: '#fff' }}>{c}</option>)}
            </select>
          </Field>

          {error && (
            <div style={{
              padding: 10, borderRadius: 8, fontSize: 12, textAlign: 'center',
              background: 'rgba(255,100,100,0.12)', border: '1px solid rgba(255,100,100,0.35)', color: '#fca5a5',
            }}>{error}</div>
          )}
          {success && (
            <div style={{
              padding: 10, borderRadius: 8, fontSize: 12, textAlign: 'center',
              background: 'rgba(124,184,138,0.15)', border: '1px solid rgba(124,184,138,0.4)', color: '#A3D6AC',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
            }}>
              <Check style={{ width: 14, height: 14 }} strokeWidth={2} /> Données mises à jour.
            </div>
          )}

          <button type="submit" disabled={saving} data-testid="natal-modal-save"
            style={{
              marginTop: 6, padding: '13px 24px', borderRadius: 999, border: 'none',
              background: '#D4AF37', color: '#0F1230', cursor: saving ? 'wait' : 'pointer',
              fontFamily: 'Cinzel, serif', fontSize: 12, fontWeight: 600,
              letterSpacing: '0.16em', textTransform: 'uppercase',
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              opacity: saving ? 0.7 : 1,
            }}>
            {saving ? (<><Loader2 className="animate-spin" style={{ width: 14, height: 14 }} /> Enregistrement</>) : 'Enregistrer'}
          </button>
        </form>
      </div>
    </div>
  );
}

const inputStyle = {
  width: '100%',
  padding: '11px 14px',
  borderRadius: 10,
  border: '1px solid rgba(212,175,55,0.25)',
  background: 'rgba(255,255,255,0.03)',
  color: '#F4E4BC',
  fontSize: 14,
  fontFamily: 'Inter, system-ui, sans-serif',
  outline: 'none',
};

function Field({ label, children }) {
  return (
    <label style={{ display: 'block' }}>
      <span style={{
        display: 'block', marginBottom: 6,
        fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase',
        color: 'rgba(212,175,55,0.85)', fontFamily: 'Cinzel, serif',
      }}>{label}</span>
      {children}
    </label>
  );
}
