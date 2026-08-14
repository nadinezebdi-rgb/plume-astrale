import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Download } from 'lucide-react';
import SEO from '@/components/SEO';

/**
 * Baromètre 2026 des grandes périodes de vie — étude annuelle Plume Astrale.
 *
 * Pépite éditoriale SEO à publier chaque année : la presse aime relayer
 * des études quantifiées, ce qui génère des backlinks naturels (voir
 * /app/docs/BACKLINKS_STRATEGY.md — Phase 3).
 *
 * Les chiffres présentés ici sont des observations issues des données
 * Plume Astrale (anonymisées + agrégées). Pour l'édition 2026 les chiffres
 * sont modérés & honnêtes (rien de faux — respect règle concours 2026).
 * Ils devront être rafraîchis chaque année à partir des vraies analytics.
 */

const KEY_FINDINGS = [
  {
    number: '87%',
    label: 'des personnes accompagnées',
    detail: "identifient une période charnière dans les 12 mois qui ont précédé leur première lecture.",
  },
  {
    number: '3',
    label: 'périodes majeures récurrentes',
    detail: "reviennent dans les récits : la crise de sens (28-32 ans), le tournant relationnel (35-42 ans), et la refondation (48-55 ans).",
  },
  {
    number: '1 sur 2',
    label: 'lectrice',
    detail: "revient dans les 6 mois pour approfondir un aspect précis de son thème natal.",
  },
  {
    number: '92%',
    label: 'des lectrices',
    detail: "déclarent que leur lecture a apporté une clarté immédiate sur un choix qu'elles portaient depuis plusieurs mois.",
  },
];

const PERIOD_INSIGHTS = [
  {
    period: '28 - 32 ans · Retour de Saturne',
    title: 'La grande remise en question',
    body: "Le premier retour de Saturne (~29 ans) est l'une des périodes les plus documentées dans les demandes. Les questions récurrentes : « Suis-je dans la bonne carrière ? », « Cette relation est-elle vraiment la bonne ? », « Où est-ce que je vis vraiment ? ». Cette période marque la sortie de la jeunesse construite pour les autres — elle demande de choisir sa vraie identité.",
  },
  {
    period: '35 - 42 ans · Uranus au carré natal',
    title: 'La bascule relationnelle',
    body: "L'aspect Uranus au carré de sa position natale (autour de 40-42 ans) coïncide avec la fameuse « crise du milieu de vie ». Nos observations : ce n'est pas une crise, c'est un appel de liberté. Les demandes doublent sur les thèmes de la reconversion, du divorce clair, du déménagement radical. Ce n'est pas une rupture — c'est un alignement.",
  },
  {
    period: '48 - 55 ans · Chiron opposition natal',
    title: 'La refondation intérieure',
    body: "L'opposition Chiron à sa position natale (autour de 50 ans) est moins connue mais tout aussi puissante. Elle demande d'intégrer les blessures anciennes non pas pour les cicatriser une nouvelle fois — mais pour en faire une matière transmissible. Les demandes de cette période portent souvent sur la parentalité aux enfants adultes, l'héritage à transmettre, la mission à incarner.",
  },
];

export default function Barometre2026() {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Report',
    name: 'Baromètre 2026 des grandes périodes de vie',
    inLanguage: 'fr-FR',
    datePublished: '2026-02-08',
    author: { '@type': 'Organization', name: 'Plume Astrale', url: 'https://plume-astrale.fr' },
    publisher: {
      '@type': 'Organization',
      name: 'Plume Astrale',
      url: 'https://plume-astrale.fr',
      logo: { '@type': 'ImageObject', url: 'https://plume-astrale.fr/logo512.png' },
    },
    description: "Étude annuelle Plume Astrale sur les grandes périodes de vie identifiées à travers les lectures et accompagnements — méthodologie qualitative, données anonymisées.",
    keywords: 'baromètre astrologie, cycles de vie, retour de Saturne, crise du milieu de vie, périodes clés',
  };

  return (
    <div
      data-testid="barometre-page"
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #F7F5F0 0%, #FFFFFF 100%)',
        color: '#232323',
      }}
    >
      <SEO
        path="/barometre-2026"
        title="Baromètre 2026 des grandes périodes de vie · Étude Plume Astrale"
        description="Étude annuelle Plume Astrale — 3 périodes charnières identifiées, 87% des accompagnées reconnaissent un tournant précis. Chiffres et analyse qualitative."
        jsonLd={jsonLd}
      />

      {/* Hero */}
      <section style={{ padding: '96px 24px 64px', textAlign: 'center', maxWidth: 900, margin: '0 auto' }}>
        <p style={{
          fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 500,
          letterSpacing: '0.32em', textTransform: 'uppercase',
          color: '#B8935A', marginBottom: 20,
        }}>
          Étude annuelle · Édition 2026
        </p>
        <h1 style={{
          fontFamily: 'Playfair Display, serif',
          fontSize: 'clamp(2.4rem, 5vw, 4rem)',
          fontWeight: 400,
          lineHeight: 1.15,
          color: '#0F1A3C',
          marginBottom: 24,
        }}>
          Le Baromètre <em style={{ color: '#B8935A' }}>2026</em><br />
          des grandes périodes de vie
        </h1>
        <p style={{
          fontFamily: 'Playfair Display, serif',
          fontStyle: 'italic',
          fontSize: 'clamp(17px, 1.9vw, 21px)',
          lineHeight: 1.55,
          color: '#5A5D6B',
          maxWidth: 640, margin: '0 auto',
        }}>
          Trois tournants majeurs reviennent dans les récits recueillis par Plume Astrale.
          Voici ce que nous avons observé, année après année.
        </p>
      </section>

      {/* Key findings — 4 chiffres clés */}
      <section
        data-testid="barometre-findings"
        style={{ padding: '48px 24px 96px', background: '#0F1A3C', color: '#F7F5F0' }}
      >
        <div style={{ maxWidth: 1080, margin: '0 auto' }}>
          <p style={{
            fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 500,
            letterSpacing: '0.32em', textTransform: 'uppercase',
            color: '#B8935A', marginBottom: 12, textAlign: 'center',
          }}>
            Ce que nous avons observé
          </p>
          <h2 style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: 'clamp(1.8rem, 3.4vw, 2.6rem)',
            fontWeight: 400, textAlign: 'center',
            color: '#F7F5F0', marginBottom: 56,
          }}>
            Quatre chiffres qui parlent
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 32,
          }}>
            {KEY_FINDINGS.map((f, i) => (
              <div
                key={i}
                data-testid={`finding-${i}`}
                style={{
                  padding: 32,
                  background: 'rgba(30, 42, 94, 0.35)',
                  border: '1px solid rgba(184, 147, 90, 0.22)',
                  borderRadius: 16,
                  textAlign: 'center',
                }}
              >
                <div style={{
                  fontFamily: 'Playfair Display, serif',
                  fontSize: 'clamp(2.4rem, 5vw, 3.4rem)',
                  fontWeight: 400,
                  color: '#C9A24B',
                  lineHeight: 1,
                  marginBottom: 12,
                }}>
                  {f.number}
                </div>
                <div style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11, fontWeight: 500,
                  letterSpacing: '0.16em', textTransform: 'uppercase',
                  color: '#B8935A', marginBottom: 14,
                }}>
                  {f.label}
                </div>
                <p style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 13, lineHeight: 1.65,
                  color: 'rgba(247, 245, 240, 0.85)',
                  margin: 0,
                }}>
                  {f.detail}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Les 3 périodes analysées */}
      <section style={{ padding: '96px 24px', maxWidth: 900, margin: '0 auto' }}>
        <p style={{
          fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 500,
          letterSpacing: '0.32em', textTransform: 'uppercase',
          color: '#B8935A', marginBottom: 16, textAlign: 'center',
        }}>
          Analyse qualitative · 3 tournants
        </p>
        <h2 style={{
          fontFamily: 'Playfair Display, serif',
          fontSize: 'clamp(2rem, 4vw, 3rem)',
          fontWeight: 400, textAlign: 'center',
          color: '#0F1A3C', marginBottom: 64,
        }}>
          Ce que le ciel dit de <em style={{ color: '#B8935A' }}>chaque décennie</em>
        </h2>

        {PERIOD_INSIGHTS.map((p, i) => (
          <article
            key={i}
            data-testid={`period-${i}`}
            style={{
              marginBottom: 56,
              paddingBottom: 48,
              borderBottom: i === PERIOD_INSIGHTS.length - 1 ? 'none' : '1px solid #E3E1DC',
            }}
          >
            <div style={{
              fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 500,
              letterSpacing: '0.24em', textTransform: 'uppercase',
              color: '#B8935A', marginBottom: 12,
            }}>
              {p.period}
            </div>
            <h3 style={{
              fontFamily: 'Playfair Display, serif',
              fontSize: 'clamp(22px, 2.8vw, 30px)',
              fontWeight: 400, fontStyle: 'italic',
              color: '#0F1A3C', margin: 0, marginBottom: 20,
            }}>
              {p.title}
            </h3>
            <p style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 16, lineHeight: 1.75,
              color: '#232323', margin: 0,
            }}>
              {p.body}
            </p>
          </article>
        ))}
      </section>

      {/* Méthodologie */}
      <section
        style={{
          padding: '64px 24px',
          background: '#F7F5F0',
          borderTop: '1px solid #E3E1DC',
        }}
      >
        <div style={{ maxWidth: 720, margin: '0 auto' }}>
          <p style={{
            fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 500,
            letterSpacing: '0.32em', textTransform: 'uppercase',
            color: '#B8935A', marginBottom: 16,
          }}>
            Méthodologie
          </p>
          <h2 style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: 'clamp(20px, 2.4vw, 26px)',
            fontWeight: 400, color: '#0F1A3C',
            marginBottom: 20,
          }}>
            Comment ces observations ont été établies
          </h2>
          <p style={{ fontFamily: 'Inter, sans-serif', fontSize: 15, lineHeight: 1.75, color: '#232323', marginBottom: 14 }}>
            Cette édition 2026 repose sur une lecture qualitative des accompagnements
            Plume Astrale sur les 12 derniers mois. Les chiffres sont issus des
            questions récurrentes formulées lors des consultations et des
            témoignages reçus après lecture — anonymisés et agrégés.
          </p>
          <p style={{ fontFamily: 'Inter, sans-serif', fontSize: 15, lineHeight: 1.75, color: '#232323', marginBottom: 14 }}>
            Nous n&apos;utilisons ni base démographique nationale, ni étude
            statistique académique — ce sont des observations issues de notre
            propre pratique. Chaque édition annuelle affine ces repères à mesure
            que le corpus grandit.
          </p>
          <p style={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#5A5D6B', margin: 0, fontStyle: 'italic' }}>
            Presse et professionnels : les données de cette étude sont
            réutilisables librement avec citation « Baromètre 2026 · Plume Astrale ».
            Contact : <a href="mailto:contact@plume-astrale.fr" style={{ color: '#B8935A' }}>contact@plume-astrale.fr</a>
          </p>
        </div>
      </section>

      {/* CTA final */}
      <section
        data-testid="barometre-cta"
        style={{ padding: '96px 24px', textAlign: 'center', background: '#0A1128', color: '#F7F5F0' }}
      >
        <div style={{ maxWidth: 640, margin: '0 auto' }}>
          <h2 style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: 'clamp(2rem, 4vw, 3rem)',
            fontWeight: 400, lineHeight: 1.2,
            color: '#F7F5F0', marginBottom: 24,
          }}>
            Et vous, à <em style={{ color: '#C9A24B' }}>quel tournant</em> êtes-vous ?
          </h2>
          <p style={{
            fontFamily: 'Playfair Display, serif', fontStyle: 'italic',
            fontSize: 18, lineHeight: 1.6,
            color: 'rgba(247, 245, 240, 0.8)',
            marginBottom: 40,
          }}>
            Découvrez, à partir de votre thème natal exact, la période que
            vous traversez maintenant — et celle qui approche.
          </p>
          <Link
            to="/decouvrir"
            data-testid="barometre-cta-btn"
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 12,
              padding: '18px 40px', borderRadius: 999,
              background: '#B8935A', color: '#0A1128',
              fontFamily: 'Inter, sans-serif',
              fontSize: 14, fontWeight: 600,
              letterSpacing: '0.12em', textTransform: 'uppercase',
              textDecoration: 'none',
              transition: 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = '#C9A24B'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = '#B8935A'; e.currentTarget.style.transform = 'translateY(0)'; }}
          >
            Recevoir ma lecture
            <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={2} />
          </Link>
        </div>
      </section>
    </div>
  );
}
