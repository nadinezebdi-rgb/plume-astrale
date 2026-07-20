import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, ShieldCheck, Star, Loader2 } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import { useAuth } from '@/context/AuthContext';
import TestimonialsWidget, { TESTIMONIALS_KABBALE } from '@/components/TestimonialsWidget';
import { event as track, EVENTS } from '@/lib/analytics';

const API = process.env.REACT_APP_BACKEND_URL;

const KabbaleSales = () => {
  const { user } = useAuth();
  const nav = useNavigate();
  const [step, setStep] = useState(0); // 0: intro, 1: form
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
    track(EVENTS.KABBALE_CHECKOUT, { first_name: form.first_name });
    setLoading(true);
    try {
      const r = await axios.post(`${API}/api/kabbale/checkout`, {
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
    <div className="min-h-screen relative" style={{ padding: '110px 20px 140px' }} data-testid="kabbale-page">
      <SEO path="/kabbale" title="Ton Arbre de Vie Kabbalistique · 39€ · Plume Astrale"
           description="Un PDF unique de 15 pages : les 10 Sephiroth et 22 chemins de ton thème natal, tracés par la Kabbale. Recevable en 3 minutes." />

      <div className="max-w-4xl mx-auto">
        {/* Hero */}
        <div className="text-center mb-14">
          <p className="text-[10px] uppercase mb-5" style={{ color: '#D4AF37', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}>
            ✦ Analyse Kabbalistique Personnalisée ✦
          </p>
          <h1 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 300, lineHeight: 1.05,
            fontSize: 'clamp(38px, 6vw, 66px)',
            color: '#F5EEE0', marginBottom: 18,
          }}>
            Ton <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>Arbre de Vie</em><br />
            Kabbalistique
          </h1>
          <p className="text-base md:text-lg max-w-2xl mx-auto mb-8" style={{ color: 'rgba(227,215,255,0.85)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic', lineHeight: 1.6 }}>
            Un document intime de 15 pages qui cartographie ton thème natal sur les 10 Sephiroth
            et les 22 chemins de la Kabbale. Un miroir spirituel unique en français.
          </p>
          <div className="inline-flex items-baseline gap-2 mb-2">
            <span style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 48, fontWeight: 300, color: '#D4AF37' }}>39€</span>
            <span className="text-xs" style={{ color: 'rgba(227,215,255,0.55)', letterSpacing: '0.2em' }}>· PAIEMENT UNIQUE</span>
          </div>
          <p className="text-xs" style={{ color: 'rgba(227,215,255,0.45)', letterSpacing: '0.1em' }}>
            Livré par email dans les 3 minutes suivant le paiement
          </p>
        </div>

        {/* Arbre de Vie — image sacrée */}
        <div className="relative mx-auto mb-16" style={{ maxWidth: 720 }} data-testid="kabbale-tree-image">
          <div
            className="absolute inset-0 rounded-full blur-3xl opacity-40"
            style={{ background: 'radial-gradient(circle, rgba(212,175,55,0.35) 0%, transparent 70%)' }}
            aria-hidden="true"
          />
          <div
            className="relative rounded-2xl overflow-hidden"
            style={{
              border: '1px solid rgba(212,175,55,0.35)',
              boxShadow: '0 30px 80px -20px rgba(212,175,55,0.25), inset 0 0 40px rgba(12,17,32,0.4)',
              background: 'linear-gradient(180deg, rgba(212,175,55,0.06) 0%, rgba(12,17,32,0.4) 100%)',
            }}
          >
            <img
              src="https://customer-assets-0z36b82j.emergentagent.net/job_consultation-astro/artifacts/88y9zws0_Virginia_httpss.mj.run5r2USyGa9Qc_cre_des_arbres_hbraiques_de_a798dba8-6cc5-4940-9944-0c2e4c50fd54_1.webp"
              alt="Arbre de Vie kabbalistique — les 10 Sephiroth et les 22 chemins"
              loading="lazy"
              className="w-full h-auto block"
              style={{ display: 'block' }}
            />
            <div
              className="absolute inset-0 pointer-events-none"
              style={{ background: 'radial-gradient(ellipse at center, transparent 55%, rgba(12,17,32,0.65) 100%)' }}
              aria-hidden="true"
            />
          </div>
          <p
            className="text-center mt-5 text-xs uppercase"
            style={{ color: 'rgba(212,175,55,0.75)', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}
          >
            ✦ Les 10 Sephiroth · Les 22 Chemins ✦
          </p>
        </div>

        {/* Ce que tu vas recevoir */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
          {[
            { icon: Sparkles, title: 'Tes 10 Sephiroth', desc: 'Chaque sphère de conscience de ton âme, personnalisée à ton thème natal.' },
            { icon: Star, title: 'Tes 22 chemins activés', desc: 'Les portes zodiacales que ton ciel a ouvertes — Tarot & Lettres hébraïques.' },
            { icon: ShieldCheck, title: 'Ton équilibre des Piliers', desc: 'Rigueur · Miséricorde · Milieu — le diagnostic complet de ton axe d\'âme.' },
          ].map(({ icon: Icon, title, desc }, i) => (
            <div key={i} className="plume-glass p-6" data-testid={`kabbale-feature-${i}`}>
              <Icon className="w-7 h-7 mb-3" style={{ color: '#D4AF37' }} strokeWidth={1.2} />
              <h3 className="text-lg mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>{title}</h3>
              <p className="text-sm" style={{ color: 'rgba(227,215,255,0.72)', lineHeight: 1.6 }}>{desc}</p>
            </div>
          ))}
        </div>

        {step === 0 ? (
          <>
            <TestimonialsWidget
              testimonials={TESTIMONIALS_KABBALE}
              title="Ce que leur Arbre a révélé"
              subtitle="Trois femmes qui ont reçu leur analyse kabbalistique personnalisée"
              testIdPrefix="kabbale-testimonial"
            />
            <div className="text-center">
              <button onClick={() => setStep(1)} className="plume-btn-primary" data-testid="kabbale-cta-start">
                Recevoir mon Arbre de Vie — 39€
                <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
              </button>
              <p className="text-xs mt-4" style={{ color: 'rgba(227,215,255,0.5)', letterSpacing: '0.1em' }}>
                Paiement sécurisé Stripe · Sans engagement
              </p>
            </div>
          </>
        ) : (
          <div className="plume-glass p-8 md:p-10 max-w-xl mx-auto" data-testid="kabbale-form">
            <h2 className="text-2xl mb-6 text-center" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>
              Tes coordonnées astrales
            </h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>Email pour la livraison</label>
                <input type="email" value={form.email} onChange={e => upd('email', e.target.value)}
                       data-testid="kabbale-email"
                       className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
              </div>
              <div>
                <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>Prénom</label>
                <input type="text" value={form.first_name} onChange={e => upd('first_name', e.target.value)}
                       data-testid="kabbale-firstname"
                       className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>Date naiss.</label>
                  <input type="date" value={form.birth_date} onChange={e => upd('birth_date', e.target.value)}
                         data-testid="kabbale-birthdate"
                         className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
                </div>
                <div>
                  <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>Heure naiss.</label>
                  <input type="time" value={form.birth_time} onChange={e => upd('birth_time', e.target.value)}
                         data-testid="kabbale-birthtime"
                         className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
                </div>
              </div>
              <div>
                <label className="text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>Ville de naissance</label>
                <input type="text" value={form.birth_city} onChange={e => upd('birth_city', e.target.value)}
                       data-testid="kabbale-city"
                       className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/60 border border-plume-gold/20 text-plume-lavender focus:outline-none focus:border-plume-gold/60" />
              </div>
              <div>
                <label className="text-xs uppercase" style={{ color: 'rgba(212,175,55,0.65)', letterSpacing: '0.2em' }}>
                  Code promo (optionnel)
                </label>
                <input
                  type="text"
                  value={promoCode}
                  onChange={e => setPromoCode(e.target.value.toUpperCase())}
                  placeholder="Ex: ADMIN26"
                  data-testid="kabbale-promo"
                  className="w-full mt-2 px-4 py-3 rounded-xl bg-plume-night-soft/40 border border-plume-gold/15 text-plume-lavender focus:outline-none focus:border-plume-gold/50"
                  style={{ letterSpacing: '0.2em', fontFamily: 'Cinzel, serif', fontSize: 13 }}
                />
              </div>
              {error && <p className="text-sm text-center" style={{ color: '#F87171' }} data-testid="kabbale-error">{error}</p>}
              <button onClick={handleCheckout} disabled={loading} className="plume-btn-primary w-full justify-center" data-testid="kabbale-checkout-btn">
                {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Redirection...</> :
                          promoCode.trim() ? <>Déverrouiller mon Arbre <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></>
                                           : <>Payer 39€ et recevoir mon Arbre <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></>}
              </button>
              <p className="text-[10px] text-center mt-3" style={{ color: 'rgba(227,215,255,0.4)', letterSpacing: '0.2em' }}>
                🔒 PAIEMENT SÉCURISÉ STRIPE · TVA INCLUSE
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default KabbaleSales;
