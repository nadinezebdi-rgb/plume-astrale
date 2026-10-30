import {useEffect} from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle2, ArrowRight, Sparkles, Mail } from 'lucide-react';
import SEO from '@/components/SEO';
import { event as trackEvent } from '../lib/analytics';

/**
 * /synastrie/extrait-envoye — page de remerciement après envoi du lead magnet.
 * Rôle : rassurer sur la livraison + upsell "Synastrie complète 25 pages · 49€".
 */
export default function SynastrieLeadThanks() {
  useEffect(() => {
    try {
      trackEvent('view_lead_thanks', { source: 'synastrie' });
      localStorage.setItem('plume_syn_lead_sent', String(Date.now()));
    } catch { /* noop */ }
  }, []);

  return (
    <>
      <SEO
        path="/synastrie/extrait-envoye"
        title="Votre extrait est en route · Plume Astrale"
        description="Votre extrait de synastrie 3 pages a été envoyé par email. Découvrez aussi notre analyse complète 25 pages."
      />
      <main
        data-testid="synastrie-thanks-page"
        style={{
          minHeight: '80vh',
          padding: '80px 20px',
          background: 'linear-gradient(180deg, #0F1A3A 0%, #0C132E 100%)',
          color: '#F5EEE0',
        }}
      >
        <div style={{ maxWidth: 720, margin: '0 auto' }}>
          {/* Hero merci */}
          <section
            data-testid="synastrie-thanks-hero"
            style={{
              textAlign: 'center',
              padding: '48px 32px',
              background: 'rgba(11,26,46,0.65)',
              border: '1px solid rgba(74,222,128,0.3)',
              borderRadius: 10,
              backdropFilter: 'blur(8px)',
              marginBottom: 36,
            }}
          >
            <div style={{
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              width: 68, height: 68, borderRadius: '50%',
              background: 'rgba(74,222,128,0.12)', border: '1px solid rgba(74,222,128,0.4)',
              marginBottom: 20,
            }}>
              <CheckCircle2 size={32} style={{ color: '#4ADE80' }} strokeWidth={1.5} />
            </div>
            <p style={{
              fontFamily: '"Cinzel", serif', fontSize: 11, letterSpacing: '0.3em',
              textTransform: 'uppercase', color: '#D4AF37', margin: '0 0 14px',
            }}>
              Extrait envoyé · 3 pages
            </p>
            <h1 style={{
              fontFamily: '"Fraunces", "Playfair Display", serif',
              fontVariationSettings: "'opsz' 144, 'SOFT' 50",
              fontWeight: 400,
              fontSize: 'clamp(28px, 4vw, 42px)',
              lineHeight: 1.15,
              letterSpacing: '-0.015em',
              margin: '0 0 18px',
            }}>
              Votre extrait est en route.
            </h1>
            <p style={{
              fontSize: 15.5, lineHeight: 1.65,
              color: 'rgba(244,239,230,0.78)',
              maxWidth: 480, margin: '0 auto',
            }}>
              <Mail size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 6, color: 'rgba(212,175,55,0.75)' }} strokeWidth={1.6} />
              Un email avec le lien vers vos 3 pages vient d&apos;être envoyé. Vérifiez vos spams si rien n&apos;arrive sous 5 minutes.
            </p>
          </section>

          {/* Upsell */}
          <section
            data-testid="synastrie-thanks-upsell"
            style={{
              padding: '36px 32px',
              background: 'linear-gradient(135deg, rgba(212,175,55,0.08), rgba(232,165,185,0.05))',
              border: '1px solid rgba(212,175,55,0.3)',
              borderRadius: 10,
            }}
          >
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
              <Sparkles size={16} style={{ color: '#D4AF37' }} strokeWidth={1.5} />
              <span style={{ fontFamily: '"Cinzel", serif', fontSize: 10.5, letterSpacing: '0.28em', textTransform: 'uppercase', color: '#D4AF37' }}>
                Pour aller plus loin
              </span>
            </div>
            <h2 style={{
              fontFamily: '"Fraunces", "Playfair Display", serif',
              fontVariationSettings: "'opsz' 144, 'SOFT' 50",
              fontWeight: 400,
              fontSize: 'clamp(22px, 3vw, 28px)',
              lineHeight: 1.2,
              letterSpacing: '-0.01em',
              margin: '0 0 14px',
            }}>
              La synastrie complète, <em style={{ fontStyle: 'italic', color: '#E8A5B9' }}>pour vraiment comprendre</em>.
            </h2>
            <p style={{ fontSize: 14.5, lineHeight: 1.65, color: 'rgba(244,239,230,0.78)', margin: '0 0 20px' }}>
              L&apos;extrait vous donne un avant-goût des Soleils croisés. Le rapport complet (25 pages) décrypte
              aussi vos Lunes, Vénus × Mars, aspects majeurs, karma relationnel, composite et un rituel du couple.
            </p>

            <ul style={{
              listStyle: 'none', padding: 0, margin: '0 0 28px',
              display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 10,
            }}>
              {[
                'Vos deux Lunes · tendresse quotidienne',
                'Vénus × Mars · chimie amoureuse',
                'Aspects croisés majeurs',
                'Karma relationnel · Nœuds lunaires',
                'Composite (5e planète) · signature d\'âme',
                'Rituel du couple hebdomadaire',
              ].map((it, i) => (
                <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, fontSize: 13.5, color: 'rgba(244,239,230,0.82)', lineHeight: 1.5 }}>
                  <span style={{ color: '#D4AF37', marginTop: 1 }}>✦</span>
                  <span>{it}</span>
                </li>
              ))}
            </ul>

            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
              <div>
                <div style={{ fontFamily: '"Fraunces", serif', fontSize: 32, color: '#D4AF37', fontWeight: 400 }}>
                  49€
                </div>
                <div style={{ fontSize: 11, letterSpacing: '0.15em', color: 'rgba(244,239,230,0.6)', textTransform: 'uppercase' }}>
                  Paiement unique · 25 pages · 10 min
                </div>
              </div>
              <Link
                to="/synastrie/checkout"
                data-testid="synastrie-thanks-upsell-cta"
                onClick={() => { try { trackEvent('upsell_click', { source: 'synastrie_thanks', product: 'synastrie' }); } catch { /* noop */ } }}
                style={{
                  display: 'inline-flex', alignItems: 'center', gap: 8,
                  padding: '14px 28px',
                  background: 'linear-gradient(135deg, #D4AF37, #E8C766)',
                  color: '#0F1A3C', textDecoration: 'none',
                  border: 'none', borderRadius: 4,
                  fontFamily: '"Cinzel", serif', fontSize: 13, letterSpacing: '0.2em',
                  textTransform: 'uppercase', fontWeight: 600,
                  transition: 'transform 180ms ease',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-1px)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; }}
              >
                Analyser notre lien complet
                <ArrowRight size={14} strokeWidth={1.8} />
              </Link>
            </div>
          </section>

          <p style={{ textAlign: 'center', marginTop: 32, fontSize: 13, color: 'rgba(244,239,230,0.55)' }}>
            Pas prêt·e ? <Link to="/" style={{ color: '#D4AF37', textDecoration: 'none' }}>Retour à l&apos;accueil</Link> · ou <Link to="/blog" style={{ color: '#D4AF37', textDecoration: 'none' }}>explorer le journal</Link>
          </p>
        </div>
      </main>
    </>
  );
}
