import React from 'react';
import { HelpCircle, Sparkles, Shield, Clock } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';
import { CreditsInfoContent } from '@/components/CreditsInfoModal';

/**
 * Page /credits — explication publique du système de crédits Plume Astrale.
 * Réutilise <CreditsInfoContent /> pour éviter la duplication (même contenu que le modal).
 * SEO-friendly, ancre du footer et lien depuis les icônes "?" du site.
 */
export default function CreditsInfo() {
  return (
    <PsPageShell background="light">
      <SEO path="/credits" />

      {/* ═══ HERO ═══ */}
      <section
        data-testid="credits-info-hero"
        style={{
          padding: '96px 24px 48px',
          maxWidth: 960,
          margin: '0 auto',
          textAlign: 'center',
        }}
      >
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            padding: '6px 14px',
            borderRadius: 999,
            background: 'rgba(201,162,75,0.10)',
            border: '1px solid rgba(201,162,75,0.30)',
            color: '#C9A24B',
            fontFamily: 'Inter, sans-serif',
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: '0.18em',
            textTransform: 'uppercase',
            marginBottom: 20,
          }}
        >
          <Sparkles style={{ width: 12, height: 12 }} strokeWidth={2} />
          Comprendre les crédits
        </div>
        <h1
          className="ps-h1"
          style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: 'clamp(36px, 6vw, 56px)',
            color: '#0F1A3C',
            fontWeight: 500,
            lineHeight: 1.15,
            marginBottom: 20,
          }}
        >
          Un crédit,{' '}
          <span style={{ fontStyle: 'italic', color: '#C9A24B' }}>
            une intention posée à Soléna.
          </span>
        </h1>
        <p
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 17,
            lineHeight: 1.65,
            color: '#232323',
            maxWidth: 640,
            margin: '0 auto',
          }}
        >
          Plume Astrale n&apos;est ni un abonnement rigide, ni un catalogue de PDF
          hors de prix. C&apos;est un espace vivant, où tes <strong>crédits</strong>{' '}
          te permettent de revenir aussi souvent que ton ciel le demande —
          sans jamais repayer l&apos;accès complet.
        </p>
      </section>

      {/* ═══ CONTENU (partagé avec le modal) ═══ */}
      <section
        style={{
          padding: '32px 24px 64px',
          maxWidth: 960,
          margin: '0 auto',
        }}
      >
        <div
          style={{
            background: '#FFFFFF',
            border: '1px solid #E3E1DC',
            borderRadius: 20,
            padding: 'clamp(28px, 5vw, 48px)',
            boxShadow: '0 20px 40px -20px rgba(15,26,60,0.08)',
          }}
        >
          <CreditsInfoContent />
        </div>
      </section>

      {/* ═══ TROIS PROMESSES ═══ */}
      <section
        style={{
          padding: '32px 24px 96px',
          maxWidth: 1100,
          margin: '0 auto',
        }}
      >
        <p
          className="ps-eyebrow"
          style={{
            textAlign: 'center',
            marginBottom: 24,
          }}
        >
          Nos engagements
        </p>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: 20,
          }}
        >
          {[
            {
              icon: Clock,
              title: 'Sans expiration',
              desc: "Tes crédits restent valables tant que ton compte est actif. Aucune date limite, aucune pression.",
            },
            {
              icon: Shield,
              title: 'Sans engagement',
              desc: "Pas d'abonnement, pas de prélèvement caché. Tu recharges quand tu en ressens le besoin — jamais avant.",
            },
            {
              icon: HelpCircle,
              title: 'Sans mauvaise surprise',
              desc: "Chaque service affiche son coût avant que tu ne le lances. Tu gardes la main de bout en bout.",
            },
          ].map((it) => {
            const Icon = it.icon;
            return (
              <div
                key={it.title}
                data-testid={`credits-promise-${it.title.replace(/[^a-z]/gi, '-').toLowerCase()}`}
                style={{
                  background: '#FFFFFF',
                  border: '1px solid #E3E1DC',
                  borderRadius: 14,
                  padding: 24,
                }}
              >
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: 12,
                    background: 'rgba(201,162,75,0.10)',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: 14,
                  }}
                >
                  <Icon
                    style={{ width: 22, height: 22, color: '#C9A24B' }}
                    strokeWidth={1.6}
                  />
                </div>
                <div
                  style={{
                    fontFamily: 'Playfair Display, serif',
                    fontSize: 20,
                    color: '#0F1A3C',
                    fontWeight: 500,
                    marginBottom: 8,
                  }}
                >
                  {it.title}
                </div>
                <p
                  style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 14,
                    lineHeight: 1.6,
                    color: '#6B7280',
                    margin: 0,
                  }}
                >
                  {it.desc}
                </p>
              </div>
            );
          })}
        </div>
      </section>
    </PsPageShell>
  );
}
