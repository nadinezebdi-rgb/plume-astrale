import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowRight, TreePine, Globe2 } from 'lucide-react';
import { event as track, EVENTS } from '@/lib/analytics';

/**
 * Carte "Bundle Découverte Soléna" — Kabbale + Astrocarto ensemble.
 *
 * Stratégie post-audit Gary Vee : le tarif normal est 39€ + 49€ = 88€.
 * L'offre bundle affichée = 88€ paiement échelonné (Kabbale d'abord, puis
 * Astrocarto à 29€ via le code KABBALE20 automatiquement présenté après le
 * paiement Kabbale). Économie totale annoncée : 20€ + rituel bonus offert.
 *
 * Ce composant est un TEASER (redirection vers /kabbale). L'upsell -20€
 * se déclenche mécaniquement sur la page KabbaleSucces.
 */
const BundleCard = ({ dense = false, testId = 'bundle-card' }) => (
  <div
    className="plume-glass p-6 md:p-8 relative overflow-hidden"
    data-testid={testId}
    style={{
      border: '1px solid rgba(212,175,55,0.4)',
      boxShadow: '0 30px 80px -30px rgba(212,175,55,0.25)',
    }}
  >
    {/* Badge d'offre */}
    <div
      className="absolute top-3 right-3 px-3 py-1 rounded-full text-[10px] uppercase"
      style={{
        background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 50%, #D4AF37 100%)',
        color: '#0A0603',
        fontFamily: 'Cinzel, serif',
        letterSpacing: '0.18em',
        fontWeight: 700,
      }}
      data-testid={`${testId}-badge`}
    >
      ✦ Duo Soléna ✦
    </div>

    <p
      className="text-[10px] uppercase mb-3"
      style={{ color: '#D4AF37', letterSpacing: '0.32em', fontFamily: 'Cinzel, serif' }}
    >
      ✦ Bundle Découverte ✦
    </p>

    <h3
      style={{
        fontFamily: 'Cormorant Garamond, serif',
        fontWeight: 300,
        fontSize: dense ? 'clamp(22px, 2.6vw, 28px)' : 'clamp(26px, 3.4vw, 34px)',
        color: '#F5EEE0',
        lineHeight: 1.15,
        marginBottom: 10,
      }}
      data-testid={`${testId}-title`}
    >
      Ton <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>Arbre de Vie</em>
      {' '}+ ta <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>meilleure destination</em>
    </h3>

    <p
      className="text-sm md:text-base mb-5"
      style={{
        color: 'rgba(227,215,255,0.8)',
        fontFamily: 'Cormorant Garamond, serif',
        fontStyle: 'italic',
        lineHeight: 1.55,
      }}
    >
      Cartographie ton âme (Kabbale, 15 pages) puis découvre les lieux du monde où
      ta vie s&apos;épanouira (Astrocartographie, 18 pages). L&apos;introspection et
      le mouvement, dans un même parcours.
    </p>

    {/* Récap contenu */}
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-5">
      <div className="flex items-start gap-3 p-3 rounded-lg" style={{ background: 'rgba(212,175,55,0.05)', border: '1px solid rgba(212,175,55,0.15)' }}>
        <TreePine className="w-5 h-5 shrink-0 mt-0.5" strokeWidth={1.3} style={{ color: '#D4AF37' }} />
        <div>
          <div style={{ fontFamily: 'Cinzel, serif', fontSize: 12, color: '#F5EEE0', letterSpacing: '0.1em' }}>
            KABBALE
          </div>
          <div className="text-xs mt-0.5" style={{ color: 'rgba(227,215,255,0.6)' }}>
            10 Sephiroth · 22 chemins · <s>39€</s> <span style={{ color: '#D4AF37' }}>39€</span>
          </div>
        </div>
      </div>
      <div className="flex items-start gap-3 p-3 rounded-lg" style={{ background: 'rgba(212,175,55,0.05)', border: '1px solid rgba(212,175,55,0.15)' }}>
        <Globe2 className="w-5 h-5 shrink-0 mt-0.5" strokeWidth={1.3} style={{ color: '#D4AF37' }} />
        <div>
          <div style={{ fontFamily: 'Cinzel, serif', fontSize: 12, color: '#F5EEE0', letterSpacing: '0.1em' }}>
            ASTROCARTOGRAPHIE
          </div>
          <div className="text-xs mt-0.5" style={{ color: 'rgba(227,215,255,0.6)' }}>
            Lignes planétaires · 3 villes · <s>49€</s> <span style={{ color: '#D4AF37' }}>29€</span>
          </div>
        </div>
      </div>
    </div>

    {/* Prix ancre */}
    <div className="flex items-baseline gap-3 mb-5" data-testid={`${testId}-pricing`}>
      <span style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 36, color: '#D4AF37', fontWeight: 300 }}>
        68€
      </span>
      <span style={{ textDecoration: 'line-through', color: 'rgba(227,215,255,0.4)', fontSize: 18 }}>88€</span>
      <span className="text-xs" style={{ color: 'rgba(212,175,55,0.85)', letterSpacing: '0.15em' }}>
        · TU ÉCONOMISES 20€
      </span>
    </div>

    <p className="text-[11px] mb-5" style={{ color: 'rgba(227,215,255,0.55)', lineHeight: 1.55 }}>
      <Sparkles className="w-3 h-3 inline mr-1" style={{ color: '#D4AF37' }} />
      Commence par ta Kabbale. Une fois ton Arbre reçu, ton Astrocartographie est déverrouillée
      à 29€ (au lieu de 49€) directement depuis ta page de succès.
    </p>

    <Link
      to="/kabbale?from=bundle"
      className="plume-btn-primary w-full justify-center"
      data-testid={`${testId}-cta`}
      style={{ display: 'inline-flex' }}
      onClick={() => track(EVENTS.BUNDLE_CLICK, { source: testId })}
    >
      Commencer le duo — Kabbale 39€
      <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
    </Link>
  </div>
);

export default BundleCard;
