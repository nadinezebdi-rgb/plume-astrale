import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { Sparkles, Heart, Moon, Star, Loader2, Mail, Lock, ArrowRight, CheckCircle2 } from 'lucide-react';
import SEO from '@/components/SEO';
import useUtmTracking from '@/hooks/useUtmTracking';
import { SOLENA } from '@/lib/solena';
import { useAuth } from '@/context/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL;

const MONTHS_FR = ['Janvier','Fevrier','Mars','Avril','Mai','Juin','Juillet','Aout','Septembre','Octobre','Novembre','Decembre'];

/**
 * Rencontres Astrales — Decodeur du Destin Amoureux
 * Landing page conversion : form → free reveal → email gate → 3 windows → CTA 29,99€
 */
export default function RencontresAstrales() {
  const navigate = useNavigate();
  const utm = useUtmTracking();
  const { token } = useAuth();
  const [step, setStep] = useState('form'); // form | reveal | windows
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Birth form
  const [day, setDay] = useState('');
  const [month, setMonth] = useState('');
  const [year, setYear] = useState('');
  const [hour, setHour] = useState('12');
  const [minute, setMinute] = useState('00');
  const [place, setPlace] = useState('');
  const [firstName, setFirstName] = useState('');

  // Reveal state
  const [reveal, setReveal] = useState(null);
  const [email, setEmail] = useState('');
  const [consent, setConsent] = useState(true);
  const [windows, setWindows] = useState(null);
  const [ctaLoading, setCtaLoading] = useState(false);
  const [promoCode, setPromoCode] = useState('');

  // Personne qui t'intéresse — requise pour la synastrie 12 domaines
  const [partnerFirstName, setPartnerFirstName] = useState('');
  const [partnerBirthDate, setPartnerBirthDate] = useState('');
  const [partnerBirthTime, setPartnerBirthTime] = useState('');

  const submitForm = async (e) => {
    e.preventDefault();
    setError('');
    if (!day || !month || !year || !place) {
      setError('Renseigne au moins ta date et ton lieu de naissance.');
      return;
    }
    setLoading(true);
    try {
      const r = await axios.post(`${API}/api/rencontres/reveal`, {
        day: Number(day), month: Number(month), year: Number(year),
        hour: Number(hour), minute: Number(minute),
        place, country: 'France',
        first_name: firstName || null,
        utm,
      });
      setReveal(r.data);
      setStep('reveal');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setError(err.response?.data?.detail || 'Impossible de calculer ton theme. Reessaie dans un instant.');
    } finally {
      setLoading(false);
    }
  };

  const submitEmail = async (e) => {
    e.preventDefault();
    setError('');
    if (!email || !email.includes('@')) {
      setError('Un email valide s\'il te plait.');
      return;
    }
    setLoading(true);
    try {
      const r = await axios.post(`${API}/api/rencontres/capture`, {
        reveal_id: reveal.reveal_id,
        email,
        consent_marketing: consent,
        utm,
      });
      setWindows(r.data);
      setStep('windows');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur, reessaie.');
    } finally {
      setLoading(false);
    }
  };

  const buyPremium = async () => {
    setError('');
    if (!partnerFirstName.trim() || !partnerBirthDate) {
      setError('Renseigne le prénom et la date de naissance de la personne qui t\'intéresse — ton guide inclut votre synastrie complète.');
      return;
    }
    setCtaLoading(true);
    try {
      const r = await axios.post(
        `${API}/api/rencontres/checkout`,
        {
          origin_url: window.location.origin,
          reveal_id: reveal?.reveal_id,
          email,
          utm,
          promo_code: promoCode.trim() || undefined,
        partner_first_name: partnerFirstName.trim(),
        partner_birth_date: partnerBirthDate,
        partner_birth_time: partnerBirthTime || undefined,
        },
        token ? { headers: { Authorization: `Bearer ${token}` } } : {},
      );
      if (r.data?.url) window.location.href = r.data.url;
      else { setCtaLoading(false); setError('Paiement indisponible pour l\'instant.'); }
    } catch (err) {
      setCtaLoading(false);
      setError(err.response?.data?.detail || 'Erreur paiement.');
    }
  };

  const renderPortrait = (portrait) => {
    if (!portrait) return null;
    // parse **bold** → <strong>
    const parts = portrait.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((p, i) =>
      p.startsWith('**') && p.endsWith('**')
        ? <strong key={i} style={{ color: '#D4AF37', fontWeight: 600 }}>{p.slice(2, -2)}</strong>
        : <span key={i}>{p}</span>
    );
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'radial-gradient(ellipse at top, #1A2035 0%, #141A2C 50%, #111625 100%)',
      color: '#F5EEE0',
      overflow: 'hidden',
      position: 'relative',
    }}>
      <SEO title="Rencontres Astrales — Décode ta prochaine histoire d&apos;amour" description="Découvre l'identité astrale de ton futur partenaire et tes fenêtres de rencontre gravées dans ton ciel." path="/rencontres-astrales" />

      {/* Fond céleste (repositionnement Phase 4) — lune dorée + constellation en filigrane
          remplace l'ancien portrait Soléna en fullbleed. Soléna reste guide discrète (avatar 60x60 plus bas). */}
      {step === 'form' && (
        <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', zIndex: 0 }} aria-hidden="true">
          {/* Aurore dorée diffuse */}
          <div style={{
            position: 'absolute', inset: 0,
            background: 'radial-gradient(ellipse at 50% 30%, rgba(184,147,90,0.18) 0%, rgba(184,147,90,0.06) 30%, transparent 55%)',
          }} />
          {/* Lune dorée centrale */}
          <svg viewBox="0 0 800 800" preserveAspectRatio="xMidYMid slice"
            style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '90%', height: '90%', opacity: 0.55 }}>
            <defs>
              <radialGradient id="moonBody" cx="0.42" cy="0.42" r="0.55">
                <stop offset="0%" stopColor="#F7F5F0" />
                <stop offset="55%" stopColor="#E8D9B4" />
                <stop offset="100%" stopColor="#B8935A" />
              </radialGradient>
              <radialGradient id="moonHalo" cx="0.5" cy="0.5" r="0.5">
                <stop offset="0%" stopColor="rgba(184,147,90,0.35)" />
                <stop offset="100%" stopColor="rgba(184,147,90,0)" />
              </radialGradient>
            </defs>
            {/* Halo diffus */}
            <circle cx="400" cy="380" r="280" fill="url(#moonHalo)" />
            {/* Corps lunaire */}
            <circle cx="400" cy="380" r="115" fill="url(#moonBody)" opacity="0.85" />
            {/* Constellation filigrane — 5 étoiles reliées, façon Cassiopée */}
            <g stroke="#B8935A" strokeWidth="0.8" fill="none" opacity="0.45">
              <line x1="180" y1="180" x2="260" y2="140" />
              <line x1="260" y1="140" x2="340" y2="200" />
              <line x1="340" y1="200" x2="420" y2="150" />
              <line x1="420" y1="150" x2="510" y2="210" />
            </g>
            {[
              [180, 180], [260, 140], [340, 200], [420, 150], [510, 210],
              [620, 520], [560, 610], [640, 630], [700, 560],
              [140, 560], [110, 640], [200, 640],
            ].map(([x, y], i) => (
              <circle key={i} cx={x} cy={y} r={i % 3 === 0 ? 2.4 : 1.6} fill="#F7F5F0" opacity="0.75" />
            ))}
          </svg>
          {/* Vignettage doux pour lisibilité du contenu */}
          <div style={{
            position: 'absolute', inset: 0,
            background: 'radial-gradient(ellipse at center, rgba(17,22,37,0.35) 0%, rgba(17,22,37,0.75) 65%, #111625 100%)',
          }} />
        </div>
      )}

      {/* Starfield decorative dots */}
      <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none', zIndex: 1 }}>
        {[...Array(50)].map((_, i) => {
          const s = 1 + Math.random() * 2;
          return (
            <div key={i} style={{
              position: 'absolute',
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              width: s, height: s,
              background: '#F5EEE0',
              borderRadius: '50%',
              opacity: 0.15 + Math.random() * 0.5,
              boxShadow: '0 0 6px rgba(244,232,210,0.6)',
            }} />
          );
        })}
      </div>

      <div className="relative max-w-3xl mx-auto px-4 md:px-8 py-12 md:py-20">

        {/* STEP 1 — FORMULAIRE */}
        {step === 'form' && (
          <div>
            {/* Solena — credibility hero */}
            <div className="flex items-center justify-center gap-3 mb-6 animate-fade-up" data-testid="solena-hero">
              <img src={SOLENA.portrait} alt="Soléna — voix éditoriale Plume Astrale"                loading="eager"
                style={{
                  width: 60, height: 60, borderRadius: '50%',
                  objectFit: 'cover', objectPosition: 'center 25%',
                  border: '2px solid rgba(212,175,55,0.55)',
                  boxShadow: '0 0 24px rgba(212,175,55,0.30)',
                }} />
              <div className="text-left">
                <div className="text-[10px] uppercase" style={{ color: '#D4AF37', letterSpacing: '0.25em' }}>
                  Guidée par
                </div>
                <div className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                  Solena
                </div>
              </div>
            </div>

            {/* Hook */}
            <div className="text-center mb-10 animate-fade-up">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-6"
                style={{ background: 'rgba(212,175,55,0.10)', border: '1px solid rgba(212,175,55,0.35)' }}>
                <Sparkles className="w-3.5 h-3.5" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
                <span className="text-[10px] uppercase" style={{ color: '#D4AF37', letterSpacing: '0.25em' }}>
                  Décodeur du Destin Amoureux
                </span>
              </div>

              <h1 className="text-4xl md:text-6xl mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, lineHeight: 1.1 }}>
                Qui est écrit<br />
                <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>dans vos étoiles ?</em>
              </h1>

              <p className="text-base md:text-lg opacity-80 max-w-xl mx-auto leading-relaxed">
                Découvrez le portrait de votre âme sœur et les périodes clés
                de rencontres amoureuses gravées dans votre ciel pour les prochains mois.
              </p>
            </div>

            {/* FORM */}
            <form onSubmit={submitForm} className="rounded-3xl p-6 md:p-10"
              style={{
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(212,175,55,0.25)',
                backdropFilter: 'blur(16px)',
              }} data-testid="rencontres-form">

              <div className="grid grid-cols-3 gap-3 mb-5">
                <FieldInput label="Jour" placeholder="15" value={day} onChange={setDay} maxLength={2} testid="input-day" />
                <FieldSelect label="Mois" value={month} onChange={setMonth} options={MONTHS_FR.map((m, i) => [String(i + 1), m])} testid="input-month" />
                <FieldInput label="Année" placeholder="1990" value={year} onChange={setYear} maxLength={4} testid="input-year" />
              </div>

              <div className="grid grid-cols-2 gap-3 mb-5">
                <FieldInput label="Heure" placeholder="12" value={hour} onChange={setHour} maxLength={2} testid="input-hour" hint="approximative si inconnue" />
                <FieldInput label="Minutes" placeholder="00" value={minute} onChange={setMinute} maxLength={2} testid="input-minute" />
              </div>

              <div className="mb-5">
                <FieldInput label="Lieu de naissance" placeholder="Paris" value={place} onChange={setPlace} testid="input-place" fullWidth />
              </div>

              <div className="mb-6">
                <FieldInput label="Prénom (facultatif)" placeholder="Julie" value={firstName} onChange={setFirstName} testid="input-firstname" fullWidth />
              </div>

              {error && (
                <div className="mb-4 p-3 rounded-lg text-sm text-center"
                  style={{ background: 'rgba(255,80,80,0.12)', color: '#ffb0b0', border: '1px solid rgba(255,80,80,0.3)' }}>
                  {error}
                </div>
              )}

              <button type="submit" disabled={loading}
                className="w-full py-4 rounded-full text-sm uppercase transition-all hover:scale-[1.01] disabled:opacity-50 flex items-center justify-center gap-2"
                style={{
                  background: 'linear-gradient(135deg, #D4AF37, #E8C766)',
                  color: '#111625',
                  letterSpacing: '0.22em',
                  fontWeight: 600,
                  boxShadow: '0 20px 60px rgba(212,175,55,0.25)',
                }} data-testid="submit-reveal-btn">
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <>
                  <Heart className="w-4 h-4" strokeWidth={2} /> Révéler mes prochaines rencontres
                </>}
              </button>

              <p className="text-[10px] text-center mt-4 opacity-50" style={{ letterSpacing: '0.1em' }}>
                Aucune carte bancaire · Résultat instantané
              </p>
            </form>

            {/* Trust indicators */}
            <div className="grid grid-cols-3 gap-6 mt-10 text-center">
              <TrustItem icon={Star} title="12 000+" subtitle="lectures livrées" />
              <TrustItem icon={Heart} title="4.8/5" subtitle="satisfaction" />
              <TrustItem icon={Lock} title="100%" subtitle="confidentiel" />
            </div>

            {/* Solena — link to bio */}
            <div className="text-center mt-8">
              <Link to="/solena"
                className="inline-flex items-center gap-2 text-xs uppercase opacity-70 hover:opacity-100 transition-all"
                style={{ color: '#D4AF37', letterSpacing: '0.2em' }}
                data-testid="solena-bio-link">
                Découvrir Solena <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
          </div>
        )}

        {/* STEP 2 — REVEAL (portrait immédiat) */}
        {step === 'reveal' && reveal && (
          <div className="animate-fade-up">
            <div className="text-center mb-8">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-4"
                style={{ background: 'rgba(212,175,55,0.10)', border: '1px solid rgba(212,175,55,0.35)' }}>
                <Sparkles className="w-3.5 h-3.5" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
                <span className="text-[10px] uppercase" style={{ color: '#D4AF37', letterSpacing: '0.25em' }}>
                  Votre lecture
                </span>
              </div>
              <h2 className="text-3xl md:text-5xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}>
                Le portrait de ton <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>âme sœur</em>
              </h2>
              <p className="text-sm opacity-70">Basé sur ta Maison VII — la maison des unions</p>
            </div>

            {/* Portrait */}
            <div className="rounded-3xl p-6 md:p-10 mb-8"
              style={{
                background: 'linear-gradient(160deg, rgba(212,175,55,0.10), rgba(255,255,255,0.02))',
                border: '1px solid rgba(212,175,55,0.35)',
                backdropFilter: 'blur(16px)',
              }} data-testid="reveal-portrait">
              <p className="text-lg md:text-xl leading-relaxed" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 400 }}>
                {renderPortrait(reveal.portrait)}
              </p>
              {reveal.complement && (
                <p className="text-base md:text-lg leading-relaxed mt-6 opacity-90" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                  {renderPortrait(reveal.complement)}
                </p>
              )}
            </div>

            {/* Email gate */}
            <div className="rounded-3xl p-6 md:p-10 relative"
              style={{
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(212,175,55,0.35)',
                backdropFilter: 'blur(16px)',
              }} data-testid="email-gate">

              <div className="text-center mb-6">
                <Moon className="w-8 h-8 mx-auto mb-3" style={{ color: '#D4AF37' }} strokeWidth={1.2} />
                <h3 className="text-2xl md:text-3xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}>
                  Débloque tes <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>3 fenêtres</em> de rencontre
                </h3>
                <p className="text-sm opacity-70 max-w-md mx-auto">
                  Les 3 périodes précises des 6 prochains mois où l&apos;univers joue pour toi.
                  Envoyées gratuitement par email.
                </p>
              </div>

              <form onSubmit={submitEmail} className="space-y-4">
                <div className="relative">
                  <Mail className="w-4 h-4 absolute top-1/2 -translate-y-1/2 left-4 opacity-40" style={{ color: '#D4AF37' }} />
                  <input type="email" required placeholder="ton.email@exemple.fr"
                    value={email} onChange={e => setEmail(e.target.value)}
                    className="w-full py-4 px-4 pl-12 rounded-full text-sm outline-none transition-all"
                    style={{ background: 'rgba(255,255,255,0.05)', color: '#F5EEE0', border: '1px solid rgba(212,175,55,0.25)' }}
                    data-testid="input-email" />
                </div>

                <label className="flex items-start gap-2 text-xs opacity-70 cursor-pointer">
                  <input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)}
                    className="mt-0.5" data-testid="checkbox-consent" />
                  <span>
                    Je souhaite recevoir les conseils astro & offres exclusives de Plume (facultatif, désinscription en 1 clic).
                  </span>
                </label>

                {error && (
                  <div className="p-3 rounded-lg text-sm text-center"
                    style={{ background: 'rgba(255,80,80,0.12)', color: '#ffb0b0' }}>
                    {error}
                  </div>
                )}

                <button type="submit" disabled={loading}
                  className="w-full py-4 rounded-full text-sm uppercase transition-all hover:scale-[1.01] disabled:opacity-50 flex items-center justify-center gap-2"
                  style={{ background: 'linear-gradient(135deg, #D4AF37, #E8C766)', color: '#111625', letterSpacing: '0.2em', fontWeight: 600 }}
                  data-testid="submit-email-btn">
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <>
                    <ArrowRight className="w-4 h-4" strokeWidth={2} /> Voir mes fenêtres de rencontre
                  </>}
                </button>
              </form>
            </div>
          </div>
        )}

        {/* STEP 3 — WINDOWS + CTA 29€ */}
        {step === 'windows' && windows && (
          <div className="animate-fade-up">
            <div className="text-center mb-8">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-4"
                style={{ background: 'rgba(52,199,89,0.12)', border: '1px solid rgba(52,199,89,0.35)' }}>
                <CheckCircle2 className="w-3.5 h-3.5" style={{ color: '#8FEBB4' }} strokeWidth={1.5} />
                <span className="text-[10px] uppercase" style={{ color: '#8FEBB4', letterSpacing: '0.25em' }}>
                  Envoyé par email
                </span>
              </div>
              <h2 className="text-3xl md:text-5xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}>
                Tes 3 fenêtres sont <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>ouvertes</em>
              </h2>
              <p className="text-sm opacity-70">Les zones cosmiques où l&apos;univers joue pour toi</p>
            </div>

            {/* Windows */}
            <div className="space-y-4 mb-10">
              {windows.windows.map((w, i) => (
                <div key={i} className="rounded-2xl p-6"
                  style={{
                    background: 'rgba(212,175,55,0.06)',
                    borderLeft: '3px solid #D4AF37',
                    border: '1px solid rgba(212,175,55,0.20)',
                  }} data-testid={`window-${i}`}>
                  <div className="text-[10px] uppercase mb-1" style={{ color: '#D4AF37', letterSpacing: '0.25em' }}>
                    {w.kind}
                  </div>
                  <div className="text-2xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 400 }}>
                    Fenêtre <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>{w.period}</em>
                  </div>
                  <p className="text-sm opacity-80 leading-relaxed">{w.text}</p>
                </div>
              ))}
            </div>

            {/* CTA 29€ */}
            <div className="rounded-3xl p-6 md:p-10 relative overflow-hidden"
              style={{
                background: 'linear-gradient(135deg, #111625, #1A2035)',
                border: '2px solid #D4AF37',
                boxShadow: '0 40px 100px rgba(212,175,55,0.25)',
              }} data-testid="cta-premium">
              <div className="absolute -top-16 -right-16 w-64 h-64 rounded-full opacity-20"
                style={{ background: 'radial-gradient(circle, #D4AF37, transparent)' }} />

              <div className="relative z-10 text-center">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-5"
                  style={{ background: 'rgba(212,175,55,0.15)', border: '1px solid rgba(212,175,55,0.4)' }}>
                  <Star className="w-3.5 h-3.5" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
                  <span className="text-[10px] uppercase" style={{ color: '#D4AF37', letterSpacing: '0.25em' }}>
                    Aller plus loin
                  </span>
                </div>

                <h3 className="text-3xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300 }}>
                  Ton Guide de Compatibilité <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>Ultime</em>
                </h3>

                <p className="text-sm md:text-base opacity-80 max-w-lg mx-auto mb-6 leading-relaxed">
                  15 pages d&apos;analyse holistique complète : l&apos;identité astrale précise de ton futur partenaire,
                  vos 12 points de compatibilité, le calendrier détaillé des 6 prochains mois, et les rituels
                  énergétiques pour attirer cette relation à toi.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-lg mx-auto mb-8 text-left">
                  {windows.cta?.features?.map((f, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs">
                      <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
                      <span className="opacity-90">{f}</span>
                    </div>
                  ))}
                </div>

                <div className="mb-4">
                  <span className="text-4xl md:text-5xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#D4AF37', fontWeight: 400 }}>
                    29,99 €
                  </span>
                  <span className="ml-2 text-xs opacity-60 line-through">49,99 €</span>
                </div>

                {error && (
                  <div className="mb-4 p-3 rounded-lg text-sm text-center"
                    style={{ background: 'rgba(255,80,80,0.12)', color: '#ffb0b0' }}>
                    {error}
                  </div>
                )}

                {/* ── La personne qui t'intéresse (synastrie 12 domaines) ── */}
                <div className="mb-6 max-w-md mx-auto text-left p-5 rounded-2xl"
                  style={{ background: 'rgba(17,22,37,0.55)', border: '1px solid rgba(212,175,55,0.25)' }}
                  data-testid="partner-fields">
                  <p className="text-[10px] uppercase mb-1 text-center" style={{ color: '#D4AF37', letterSpacing: '0.25em' }}>
                    La personne qui t&apos;intéresse
                  </p>
                  <p className="text-xs opacity-70 mb-4 text-center leading-relaxed">
                    Ton guide inclut votre <strong>synastrie complète sur 12 domaines de vie</strong> — il nous faut sa date de naissance.
                  </p>
                  <div className="space-y-3">
                    <input
                      type="text"
                      value={partnerFirstName}
                      onChange={e => setPartnerFirstName(e.target.value)}
                      placeholder="Son prénom *"
                      data-testid="partner-firstname"
                      className="w-full px-4 py-3 rounded-xl text-sm"
                      style={{ background: 'rgba(17,22,37,0.7)', border: '1px solid rgba(212,175,55,0.2)', color: '#F5EEE0' }}
                    />
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-[9px] uppercase block mb-1" style={{ color: 'rgba(212,175,55,0.7)', letterSpacing: '0.15em' }}>Sa date de naissance *</label>
                        <input
                          type="date"
                          value={partnerBirthDate}
                          onChange={e => setPartnerBirthDate(e.target.value)}
                          data-testid="partner-birthdate"
                          className="w-full px-3 py-3 rounded-xl text-sm"
                          style={{ background: 'rgba(17,22,37,0.7)', border: '1px solid rgba(212,175,55,0.2)', color: '#F5EEE0' }}
                        />
                      </div>
                      <div>
                        <label className="text-[9px] uppercase block mb-1" style={{ color: 'rgba(212,175,55,0.7)', letterSpacing: '0.15em' }}>Son heure (si connue)</label>
                        <input
                          type="time"
                          value={partnerBirthTime}
                          onChange={e => setPartnerBirthTime(e.target.value)}
                          data-testid="partner-birthtime"
                          className="w-full px-3 py-3 rounded-xl text-sm"
                          style={{ background: 'rgba(17,22,37,0.7)', border: '1px solid rgba(212,175,55,0.2)', color: '#F5EEE0' }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mb-4 max-w-sm mx-auto">
                  <input
                    type="text"
                    value={promoCode}
                    onChange={e => setPromoCode(e.target.value.toUpperCase())}
                    placeholder="Code promo (optionnel)"
                    data-testid="rencontres-promo"
                    className="w-full px-4 py-3 rounded-full text-center text-sm"
                    style={{
                      background: 'rgba(17,22,37,0.60)',
                      border: '1px solid rgba(212,175,55,0.20)',
                      color: '#F5EEE0',
                      letterSpacing: '0.2em',
                      fontFamily: 'Cinzel, serif',
                      textTransform: 'uppercase',
                    }}
                  />
                </div>

                <button onClick={buyPremium} disabled={ctaLoading}
                  className="w-full md:w-auto md:min-w-[320px] py-4 px-8 rounded-full text-sm uppercase transition-all hover:scale-[1.02] disabled:opacity-50 flex items-center justify-center gap-2 mx-auto"
                  style={{
                    background: 'linear-gradient(135deg, #D4AF37, #E8C766)',
                    color: '#111625',
                    letterSpacing: '0.22em',
                    fontWeight: 700,
                    boxShadow: '0 20px 60px rgba(212,175,55,0.35)',
                  }} data-testid="buy-premium-btn">
                  {ctaLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <>
                    <Heart className="w-4 h-4" /> {promoCode.trim() ? 'Déverrouiller mon guide' : 'Révéler mon guide complet'}
                  </>}
                </button>

                <p className="text-[10px] mt-4 opacity-50" style={{ letterSpacing: '0.1em' }}>
                  Paiement sécurisé Stripe · PDF envoyé sous 24h · Sans engagement
                </p>
              </div>
            </div>

            <div className="text-center mt-8">
              <button onClick={() => navigate('/')}
                className="text-xs uppercase opacity-50 hover:opacity-80 transition-all"
                style={{ letterSpacing: '0.15em' }}
                data-testid="back-home-btn">
                Retour à l&apos;accueil
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Small sub-components
// ═══════════════════════════════════════════════════════════════════
function FieldInput({ label, value, onChange, placeholder, maxLength, hint, fullWidth, testid }) {
  return (
    <div className={fullWidth ? '' : ''}>
      <label className="text-[10px] uppercase mb-2 block" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>
        {label}
      </label>
      <input type="text" value={value} onChange={e => onChange(e.target.value)}
        placeholder={placeholder} maxLength={maxLength}
        className="w-full py-3 px-4 rounded-xl text-sm outline-none transition-all focus:border-opacity-60"
        style={{ background: 'rgba(255,255,255,0.05)', color: '#F5EEE0', border: '1px solid rgba(212,175,55,0.20)' }}
        data-testid={testid} />
      {hint && <p className="text-[10px] opacity-50 mt-1">{hint}</p>}
    </div>
  );
}

function FieldSelect({ label, value, onChange, options, testid }) {
  return (
    <div>
      <label className="text-[10px] uppercase mb-2 block" style={{ color: '#D4AF37', letterSpacing: '0.2em' }}>
        {label}
      </label>
      <select value={value} onChange={e => onChange(e.target.value)}
        className="w-full py-3 px-4 rounded-xl text-sm outline-none"
        style={{ background: 'rgba(255,255,255,0.05)', color: '#F5EEE0', border: '1px solid rgba(212,175,55,0.20)' }}
        data-testid={testid}>
        <option value="" style={{ background: '#111625' }}>—</option>
        {options.map(([v, l]) => (
          <option key={v} value={v} style={{ background: '#111625' }}>{l}</option>
        ))}
      </select>
    </div>
  );
}

function TrustItem({ icon: Icon, title, subtitle }) {
  return (
    <div>
      <Icon className="w-6 h-6 mx-auto mb-1" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
      <div className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>{title}</div>
      <div className="text-[10px] uppercase opacity-60" style={{ letterSpacing: '0.2em' }}>{subtitle}</div>
    </div>
  );
}
