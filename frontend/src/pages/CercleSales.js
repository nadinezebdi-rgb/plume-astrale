import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Moon, Heart, Calendar, BookOpen, Shield, ArrowRight } from 'lucide-react';
import { asset } from '../lib/assets';

const CercleSales = () => (
  <div style={{ minHeight: '100vh', padding: '120px 20px 140px', maxWidth: 760, margin: '0 auto' }} data-testid="cercle-sales-page">

    {/* Hero */}
    <div style={{ textAlign: 'center', marginBottom: 50 }}>
      <p style={{ fontSize: 11, letterSpacing: '0.3em', color: '#D4AF37', textTransform: 'uppercase', fontFamily: 'Cinzel, serif', marginBottom: 14 }}>
        L&apos;abonnement Plume Astrale
      </p>
      <h1 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 'clamp(34px, 6vw, 56px)', color: '#F5EEE0', fontWeight: 300, lineHeight: 1.05, marginBottom: 18 }}>
        Le <em style={{ fontStyle: 'italic', color: '#D4AF37' }}>Cercle</em>
      </h1>
      <p style={{ fontSize: 17, color: 'rgba(184,176,200,0.85)', maxWidth: 540, margin: '0 auto', lineHeight: 1.6 }}>
        Un rituel quotidien — le matin et le soir — pour habiter ta vie avec plus de clarté,
        plus de douceur, plus de toi.
      </p>
      <p style={{ fontSize: 13, color: '#D4AF37', marginTop: 16, letterSpacing: '0.1em' }}>
        14,90€ / mois · sans engagement · annulable en 1 clic
      </p>
    </div>

    {/* Vidéo immersive */}
    <div style={{
      maxWidth: 720, margin: '0 auto 50px', borderRadius: 22, overflow: 'hidden',
      border: '1px solid rgba(212,175,55,0.25)',
      boxShadow: '0 14px 48px rgba(0,0,0,0.5), 0 0 60px rgba(212,175,55,0.08)',
    }} data-testid="cercle-hero-video">
      <video
        src={asset('videos/cercle-hero.mp4')}
        autoPlay loop muted playsInline
        style={{ width: '100%', display: 'block', aspectRatio: '16/9', objectFit: 'cover', background: '#111625' }}
      />
    </div>

    {/* Valeur */}
    <section style={{
      background: 'rgba(255,255,255,0.025)',
      border: '1px solid rgba(212,175,55,0.18)',
      borderRadius: 20, padding: '30px 26px', marginBottom: 24,
    }} data-testid="cercle-value">
      <h2 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 24, color: '#F5EEE0', fontWeight: 400, marginBottom: 22, textAlign: 'center' }}>
        Ce que tu reçois chaque jour
      </h2>
      {[
        { icon: Sparkles, title: 'Le Conseil de la Plume', desc: 'Un message personnel chaque matin, calé sur tes transits.' },
        { icon: Moon, title: 'Tes énergies en temps réel', desc: 'Jauges Énergie · Confiance · Discipline · Intuition.' },
        { icon: Heart, title: 'Le check-in du matin', desc: 'Une intention à poser en un geste.' },
        { icon: BookOpen, title: 'La Réflexion du soir', desc: "Une question d'introspection, ton journal privé." },
        { icon: Calendar, title: 'Compatibilités illimitées', desc: "Synastries, langages d'amour, transits relationnels." },
        { icon: Shield, title: 'Pas de notifications culpabilisantes', desc: "Un jour d'oubli par mois est offert. Aucune pression." },
      ].map((v, i) => (
        <div key={i} style={{ display: 'flex', gap: 14, marginBottom: 18, alignItems: 'flex-start' }} data-testid={`cercle-value-${i}`}>
          <div style={{ flexShrink: 0, width: 36, height: 36, borderRadius: '50%', background: 'rgba(212,175,55,0.1)', border: '1px solid rgba(212,175,55,0.3)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>
            <v.icon style={{ width: 17, height: 17, color: '#D4AF37' }} strokeWidth={1.4} />
          </div>
          <div>
            <p style={{ fontSize: 16, fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', marginBottom: 4 }}>{v.title}</p>
            <p style={{ fontSize: 13, color: 'rgba(184,176,200,0.8)', lineHeight: 1.5, margin: 0 }}>{v.desc}</p>
          </div>
        </div>
      ))}
    </section>

    {/* CTA principal */}
    <div style={{ textAlign: 'center', marginBottom: 40 }}>
      <Link
        to="/premium"
        className="plume-btn-primary"
        data-testid="cercle-cta-main"
      >
        ✦ Rejoindre le Cercle — 14,90€/mois
        <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={2} />
      </Link>
      <p style={{ fontSize: 11, color: 'rgba(184,176,200,0.55)', marginTop: 12 }}>
        7 jours offerts · paiement sécurisé Stripe
      </p>
    </div>

    {/* FAQ */}
    <section data-testid="cercle-faq">
      <h2 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 24, color: '#F5EEE0', fontWeight: 400, marginBottom: 18, textAlign: 'center' }}>
        Questions fréquentes
      </h2>
      {[
        { q: "Comment annuler mon abonnement ?", a: "En 1 clic depuis Mon Compte → Abonnement. Aucun engagement, vous arrêtez quand vous voulez." },
        { q: "L'astrologie prédit-elle vraiment l'avenir ?", a: "Non — et nous le disons clairement dans Notre cadre. Plume vous offre un langage symbolique pour mieux vous écouter, pas un manuel d'exécution." },
        { q: "Que se passe-t-il si j'oublie une journée ?", a: "Rien de grave. Un jour d'oubli par mois est offert automatiquement. Aucune notification culpabilisante." },
        { q: "Mon journal du soir est-il privé ?", a: "Strictement. Personne d'autre que vous n'y a accès. Aucun humain, aucun algorithme ne les lit." },
        { q: "Le paiement est-il sécurisé ?", a: "Oui — paiement géré par Stripe (le standard mondial). Nous n'avons jamais accès à vos données bancaires." },
      ].map((f, i) => (
        <details key={i} style={{
          background: 'rgba(255,255,255,0.025)',
          border: '1px solid rgba(212,175,55,0.15)',
          borderRadius: 14, padding: '16px 20px', marginBottom: 10,
        }} data-testid={`cercle-faq-${i}`}>
          <summary style={{ cursor: 'pointer', fontSize: 15, color: '#F5EEE0', fontFamily: 'Cormorant Garamond, serif', listStyle: 'none' }}>
            {f.q}
          </summary>
          <p style={{ marginTop: 12, fontSize: 14, color: 'rgba(184,176,200,0.85)', lineHeight: 1.6, fontFamily: 'Cormorant Garamond, serif' }}>
            {f.a}
          </p>
        </details>
      ))}
    </section>

    <p style={{ textAlign: 'center', marginTop: 30, fontSize: 13, color: 'rgba(184,176,200,0.6)' }}>
      <Link to="/notre-cadre" style={{ color: '#D4AF37', textDecoration: 'underline' }}>Lire Notre cadre →</Link>
    </p>
  </div>
);

export default CercleSales;
