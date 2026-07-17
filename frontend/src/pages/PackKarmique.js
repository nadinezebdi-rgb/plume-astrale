import React, { useState } from 'react';
import { Sparkles, ArrowRight, ShieldCheck, Star, Loader2, Flame, BookOpen } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import { useAuth } from '@/context/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL;

const inputCls = 'w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60';

const PackKarmique = () => {
  const { user } = useAuth();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    email: user?.email || '',
    first_name: user?.prenom || user?.first_name || '',
    birth_date: '',
    birth_time: '',
    birth_city: 'Paris',
    birth_country: 'FR',
    latitude: 48.8566,
    longitude: 2.3522,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [promoCode, setPromoCode] = useState('');

  const upd = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleCheckout = async () => {
    setError(null);
    if (!form.email || !form.email.includes('@')) { setError('Email invalide'); return; }
    if (!form.first_name.trim()) { setError('Prénom requis'); return; }
    if (!form.birth_date || !form.birth_time) { setError('Date et heure de naissance requises'); return; }
    setLoading(true);
    try {
      const r = await axios.post(`${API}/api/pack-karmique/checkout`, {
        ...form,
        origin_url: window.location.origin,
        promo_code: promoCode.trim() || undefined,
      });
      if (r.data?.url) window.location.href = r.data.url;
      else setError('Une erreur est survenue');
    } catch (e) {
      setError(e.response?.data?.detail || 'Impossible de créer la session');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen relative" style={{ padding: '110px 20px 140px' }} data-testid="pack-karmique-page">
      <SEO path="/pack-karmique" title="Pack Karmique + Kabbale · 89€ · Plume Astrale"
           description="Le document le plus complet de Plume Astrale : analyse karmique complète + Arbre de Vie kabbalistique + synthèse croisée. PDF ~40 pages." />

      <div className="max-w-4xl mx-auto">
        {/* Hero */}
        <div className="text-center mb-14">
          <p className="text-[10px] uppercase mb-5" style={{ color: 'var(--pa-accent)', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}>
            ✦ Édition Prestige · Karma × Kabbale ✦
          </p>
          <h1 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 300, lineHeight: 1.05,
            fontSize: 'clamp(38px, 6vw, 66px)',
            color: 'var(--pa-heading)', marginBottom: 18,
          }}>
            Le <em style={{ color: 'var(--pa-accent)', fontStyle: 'italic' }}>Pack Karmique</em><br />
            + Kabbale
          </h1>
          <p className="text-base md:text-lg max-w-2xl mx-auto mb-8" style={{ color: 'var(--pa-body)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic', lineHeight: 1.6 }}>
            Notre document le plus profond : la mémoire karmique de ton âme (Nœuds Lunaires, Saturne,
            Chiron, Pluton) croisée avec ton Arbre de Vie kabbalistique — et une synthèse unique
            rédigée pour toi seul(e). Environ 40 pages.
          </p>
          <div className="inline-flex items-baseline gap-2 mb-2">
            <span style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 48, fontWeight: 300, color: 'var(--pa-accent)' }}>89€</span>
            <span className="text-xs" style={{ color: 'var(--pa-muted)', letterSpacing: '0.2em' }}>· PAIEMENT UNIQUE</span>
          </div>
          <p className="text-xs" style={{ color: 'var(--pa-faint)', letterSpacing: '0.1em' }}>
            Livré par email dans les minutes suivant le paiement
          </p>
        </div>

        {/* Ce que tu vas recevoir */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
          {[
            { icon: Flame, title: 'Ton Empreinte Karmique', desc: '80 sections : Nœuds Lunaires, Lilith, Chiron, planètes, maisons et aspects — la mémoire complète de ton âme.' },
            { icon: Star, title: 'Ton Arbre de Vie', desc: 'Les 10 Sephiroth et 22 chemins de ton thème natal, avec Da\u2019at et l\u2019équilibre de tes trois piliers.' },
            { icon: BookOpen, title: 'La Synthèse Croisée', desc: 'Ton essence karmique, ta mission d\u2019âme et tes pratiques d\u2019intégration — rédigées par nos soins, pour toi.' },
          ].map(({ icon: Icon, title, desc }, i) => (
            <div key={i} className="plume-glass p-6" data-testid={`pack-karmique-feature-${i}`}>
              <Icon className="w-7 h-7 mb-3" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.2} />
              <h3 className="text-lg mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>{title}</h3>
              <p className="text-sm" style={{ color: 'var(--pa-body)', lineHeight: 1.6 }}>{desc}</p>
            </div>
          ))}
        </div>

        {/* Comparatif valeur */}
        <div className="plume-glass p-6 mb-12 text-center" data-testid="pack-karmique-value">
          <p className="text-sm" style={{ color: 'var(--pa-body)', lineHeight: 1.7 }}>
            <span style={{ color: 'var(--pa-accent)' }}>Analyse karmique complète</span> + <span style={{ color: 'var(--pa-accent)' }}>Arbre de Vie 39€</span> + <span style={{ color: 'var(--pa-accent)' }}>synthèse exclusive</span> — réunis dans un seul document relié.
          </p>
        </div>

        {step === 0 ? (
          <div className="text-center">
            <button onClick={() => setStep(1)} className="plume-btn-primary" data-testid="pack-karmique-cta-start">
              Recevoir mon Pack Karmique — 89€
              <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
            </button>
            <p className="text-xs mt-4" style={{ color: 'var(--pa-faint)', letterSpacing: '0.1em' }}>
              Paiement sécurisé Stripe · Sans engagement
            </p>
          </div>
        ) : (
          <div className="plume-glass p-8 md:p-10 max-w-xl mx-auto" data-testid="pack-karmique-form">
            <h2 className="text-2xl mb-6 text-center" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
              Tes coordonnées astrales
            </h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs uppercase" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>Email pour la livraison</label>
                <input type="email" value={form.email} onChange={e => upd('email', e.target.value)}
                       data-testid="pack-karmique-email" className={inputCls} />
              </div>
              <div>
                <label className="text-xs uppercase" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>Prénom</label>
                <input type="text" value={form.first_name} onChange={e => upd('first_name', e.target.value)}
                       data-testid="pack-karmique-firstname" className={inputCls} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs uppercase" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>Date naiss.</label>
                  <input type="date" value={form.birth_date} onChange={e => upd('birth_date', e.target.value)}
                         data-testid="pack-karmique-birthdate" className={inputCls} />
                </div>
                <div>
                  <label className="text-xs uppercase" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>Heure naiss.</label>
                  <input type="time" value={form.birth_time} onChange={e => upd('birth_time', e.target.value)}
                         data-testid="pack-karmique-birthtime" className={inputCls} />
                </div>
              </div>
              <div>
                <label className="text-xs uppercase" style={{ color: 'var(--pa-accent)', letterSpacing: '0.2em' }}>Ville de naissance</label>
                <input type="text" value={form.birth_city} onChange={e => upd('birth_city', e.target.value)}
                       data-testid="pack-karmique-city" className={inputCls} />
              </div>
              <div>
                <label className="text-xs uppercase" style={{ color: 'var(--pa-muted)', letterSpacing: '0.2em' }}>
                  Code promo (optionnel)
                </label>
                <input
                  type="text"
                  value={promoCode}
                  onChange={e => setPromoCode(e.target.value.toUpperCase())}
                  placeholder="Ex: ADMIN26"
                  data-testid="pack-karmique-promo"
                  className={inputCls}
                  style={{ letterSpacing: '0.2em', fontFamily: 'Cinzel, serif', fontSize: 13 }}
                />
              </div>
              {error && <p className="text-sm text-center" style={{ color: '#F87171' }} data-testid="pack-karmique-error">{error}</p>}
              <button onClick={handleCheckout} disabled={loading} className="plume-btn-primary w-full justify-center" data-testid="pack-karmique-checkout-btn">
                {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Redirection...</> :
                          promoCode.trim() ? <>Déverrouiller mon Pack <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></>
                                           : <>Payer 89€ et recevoir mon Pack <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></>}
              </button>
              <p className="text-[10px] text-center mt-3" style={{ color: 'var(--pa-faint)', letterSpacing: '0.2em' }}>
                🔒 PAIEMENT SÉCURISÉ STRIPE · TVA INCLUSE
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PackKarmique;
