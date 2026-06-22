import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Heart, Sparkles, Download, Shield, Mail, Loader2, ArrowRight, Check } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import SEO from '@/components/SEO';
import { event as trackEvent } from '@/lib/analytics';

const API = process.env.REACT_APP_BACKEND_URL;

const PERSON_DEFAULT = {
  prenom: '',
  birth_date: '',
  birth_time: '',
  birth_place: '',
};

const FEATURES = [
  { icon: Heart, title: '25 pages de pure synastrie', desc: 'Aspects planetaires, dynamiques relationnelles, langages d\'amour croises.' },
  { icon: Sparkles, title: 'Calcule sur vos vraies ephemerides', desc: 'Swiss Ephemeris. Aucun template generique.' },
  { icon: Download, title: 'PDF a garder pour toujours', desc: 'Recu par email, telechargeable a tout moment.' },
  { icon: Shield, title: 'Vos donnees restent vos donnees', desc: 'Stockage securise, aucun partage tiers.' },
];

const PersonForm = ({ label, value, onChange, testid }) => (
  <div className="rounded-2xl p-5" style={{ background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(212,180,106,0.18)' }} data-testid={testid}>
    <p className="text-[10px] uppercase tracking-widest mb-3" style={{ color: '#D4B46A', letterSpacing: '0.16em', fontFamily: 'Cinzel, serif' }}>{label}</p>
    <div className="space-y-3">
      <div>
        <label className="text-[10px] uppercase block mb-1" style={{ color: 'rgba(184,176,200,0.65)', letterSpacing: '0.1em' }}>Prenom</label>
        <input value={value.prenom} onChange={e => onChange({ ...value, prenom: e.target.value })} required className="w-full bg-transparent border-b py-1.5 text-sm outline-none" style={{ borderColor: 'rgba(212,180,106,0.25)', color: '#F0E6D3' }} data-testid={`${testid}-prenom`} />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-[10px] uppercase block mb-1" style={{ color: 'rgba(184,176,200,0.65)', letterSpacing: '0.1em' }}>Naissance</label>
          <input type="date" value={value.birth_date} onChange={e => onChange({ ...value, birth_date: e.target.value })} required className="w-full bg-transparent border-b py-1.5 text-sm outline-none" style={{ borderColor: 'rgba(212,180,106,0.25)', color: '#F0E6D3' }} data-testid={`${testid}-date`} />
        </div>
        <div>
          <label className="text-[10px] uppercase block mb-1" style={{ color: 'rgba(184,176,200,0.65)', letterSpacing: '0.1em' }}>Heure</label>
          <input type="time" value={value.birth_time} onChange={e => onChange({ ...value, birth_time: e.target.value })} className="w-full bg-transparent border-b py-1.5 text-sm outline-none" style={{ borderColor: 'rgba(212,180,106,0.25)', color: '#F0E6D3' }} data-testid={`${testid}-time`} />
        </div>
      </div>
      <div>
        <label className="text-[10px] uppercase block mb-1" style={{ color: 'rgba(184,176,200,0.65)', letterSpacing: '0.1em' }}>Ville de naissance</label>
        <input value={value.birth_place} onChange={e => onChange({ ...value, birth_place: e.target.value })} placeholder="ex. Paris" className="w-full bg-transparent border-b py-1.5 text-sm outline-none" style={{ borderColor: 'rgba(212,180,106,0.25)', color: '#F0E6D3' }} data-testid={`${testid}-place`} />
      </div>
    </div>
  </div>
);

export default function SynastrieSales() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [person1, setPerson1] = useState({ ...PERSON_DEFAULT, prenom: user?.prenom || '', birth_date: user?.birth_date || '', birth_time: user?.birth_time || '', birth_place: user?.birth_place || '' });
  const [person2, setPerson2] = useState(PERSON_DEFAULT);
  const [email, setEmail] = useState(user?.email || '');
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  const valid =
    person1.prenom && person1.birth_date &&
    person2.prenom && person2.birth_date &&
    (token || (email && email.includes('@')));

  const handleCheckout = async () => {
    setErr(null);
    if (!valid) {
      setErr('Merci de renseigner prenom + date de naissance pour les deux personnes.');
      return;
    }
    setLoading(true);
    trackEvent('synastrie_checkout_started', { price: 49 });
    try {
      const r = await axios.post(`${API}/api/synastrie/checkout`, {
        person1, person2,
        email: token ? undefined : email,
        origin_url: window.location.origin,
      }, token ? { headers: { Authorization: `Bearer ${token}` } } : {});
      if (r.data?.checkout_url) {
        window.location.href = r.data.checkout_url;
      } else {
        setErr('Impossible de creer la session de paiement.');
        setLoading(false);
      }
    } catch (e) {
      setErr(e.response?.data?.detail || 'Erreur lors de la creation de la session.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen pt-24 pb-24 px-4" data-testid="synastrie-sales-page">
      <SEO path="/synastrie" />
      <div className="max-w-3xl mx-auto">

        {/* Hero */}
        <div className="text-center mb-12">
          <p className="text-[10px] uppercase tracking-widest mb-3" style={{ color: '#D4B46A', letterSpacing: '0.3em', fontFamily: 'Cinzel, serif' }}>
            Rapport haut-ticket
          </p>
          <h1 className="text-4xl sm:text-5xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3', fontWeight: 300, lineHeight: 1.05 }}>
            La <em style={{ fontStyle: 'italic', color: '#D4B46A' }}>Synastrie</em><br />
            de votre lien
          </h1>
          <p className="text-base sm:text-lg max-w-xl mx-auto mb-6" style={{ color: 'rgba(184,176,200,0.85)', lineHeight: 1.6 }}>
            Un rapport de 25 pages, ecrit avec soin a partir de vos deux themes natals.
            Pour comprendre ce qui se joue, ce qui vous nourrit et ce qui demande attention.
          </p>
          <div className="inline-flex items-baseline gap-2 px-6 py-2.5 rounded-full" style={{ background: 'rgba(212,180,106,0.1)', border: '1px solid rgba(212,180,106,0.3)' }}>
            <span className="text-3xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F4D98C', fontWeight: 400 }}>49€</span>
            <span className="text-xs" style={{ color: 'rgba(184,176,200,0.65)' }}>paiement unique</span>
          </div>
        </div>

        {/* Features */}
        <div className="grid sm:grid-cols-2 gap-4 mb-12">
          {FEATURES.map((f, i) => {
            const Icon = f.icon;
            return (
              <div key={i} className="rounded-2xl p-5 flex items-start gap-4" style={{ background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(212,180,106,0.15)' }} data-testid={`synastrie-feature-${i}`}>
                <div className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: 'rgba(212,180,106,0.12)', border: '1px solid rgba(212,180,106,0.3)' }}>
                  <Icon className="w-4 h-4" strokeWidth={1.5} style={{ color: '#D4B46A' }} />
                </div>
                <div>
                  <h3 className="text-base mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>{f.title}</h3>
                  <p className="text-xs leading-relaxed" style={{ color: 'rgba(184,176,200,0.75)', lineHeight: 1.6 }}>{f.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Formulaire des 2 personnes */}
        <div className="mb-6">
          <h2 className="text-2xl text-center mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3', fontWeight: 300 }}>
            Vos donnees natales
          </h2>
          <div className="grid sm:grid-cols-2 gap-4">
            <PersonForm label="Personne 1" value={person1} onChange={setPerson1} testid="person1" />
            <PersonForm label="Personne 2" value={person2} onChange={setPerson2} testid="person2" />
          </div>
        </div>

        {/* Email pour les invites */}
        {!token && (
          <div className="rounded-2xl p-5 mb-6 flex items-center gap-4" style={{ background: 'rgba(167,139,250,0.06)', border: '1px solid rgba(167,139,250,0.2)' }}>
            <Mail className="w-4 h-4 flex-shrink-0" strokeWidth={1.5} style={{ color: '#A78BFA' }} />
            <div className="flex-1">
              <label className="text-[10px] uppercase block mb-1" style={{ color: 'rgba(184,176,200,0.65)', letterSpacing: '0.1em' }}>Votre email — pour recevoir le PDF</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="vous@email.fr" className="w-full bg-transparent border-b py-1 text-sm outline-none" style={{ borderColor: 'rgba(167,139,250,0.3)', color: '#F0E6D3' }} data-testid="synastrie-email" />
            </div>
          </div>
        )}

        {/* CTA Stripe */}
        <div className="text-center mt-8">
          <button
            onClick={handleCheckout}
            disabled={!valid || loading}
            className="inline-flex items-center justify-center gap-3 px-10 py-4 rounded-full transition-all"
            style={{
              background: valid && !loading ? 'linear-gradient(135deg, #D4B46A, #C5A059)' : 'rgba(255,255,255,0.05)',
              color: valid && !loading ? '#0C0918' : 'rgba(184,176,200,0.5)',
              fontFamily: 'Cinzel, serif', fontSize: 13, letterSpacing: '0.16em', textTransform: 'uppercase', fontWeight: 600,
              cursor: valid && !loading ? 'pointer' : 'not-allowed',
              boxShadow: valid && !loading ? '0 6px 24px rgba(212,180,106,0.35)' : 'none',
              minWidth: 280,
            }}
            data-testid="synastrie-checkout-btn"
          >
            {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Redirection</> : <>✦ Composer mon rapport — 49€ <ArrowRight className="w-4 h-4" /></>}
          </button>
          {err && (
            <p className="mt-4 text-sm" style={{ color: '#FCA5A5' }} data-testid="synastrie-error">{err}</p>
          )}
          <p className="text-xs mt-5" style={{ color: 'rgba(184,176,200,0.55)' }}>
            <Check className="inline w-3 h-3 mr-1" strokeWidth={2} /> Paiement securise Stripe ·
            <Check className="inline w-3 h-3 mx-1" strokeWidth={2} /> PDF envoye par email immediatement apres paiement
          </p>
        </div>

        <button onClick={() => navigate('/')} className="block mx-auto mt-10 text-xs" style={{ color: 'rgba(184,176,200,0.5)' }}>← Retour</button>
      </div>
    </div>
  );
}
