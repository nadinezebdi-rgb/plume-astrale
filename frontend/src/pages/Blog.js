import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';

/**
 * Blog Plume Astrale — page SEO dédiée · Charte v3.1 (repositionnement Phase 4).
 *
 * Éditorial : sortie du vocabulaire ésotérique (karmique / prédictions / voyance)
 * vers un vocabulaire de développement personnel universel (cycles, périodes,
 * relations, décisions, évolution). Les articles réels sont servis par Soro
 * (widget embarqué plus bas) ; cette page présente aussi une grille éditoriale
 * de sujets universels pour capter un public plus large (Headspace-like).
 */

// Grille éditoriale — titres universels de développement personnel
// (les articles matchants sont/seront publiés côté Soro dashboard)
const FEATURED_TOPICS = [
  {
    tag: 'Relations',
    title: 'Pourquoi certaines relations reviennent-elles toujours ?',
    excerpt: 'Ces personnes qui ressurgissent dans ta vie ne sont pas là par hasard. Ce que tes cycles racontent — et comment décider quoi en faire.',
  },
  {
    tag: 'Décisions',
    title: 'Comment reconnaître le bon moment pour changer de vie',
    excerpt: 'Il existe des fenêtres où tout devient plus fluide. Apprends à les repérer, à les préparer, à en tirer parti.',
  },
  {
    tag: 'Cycles',
    title: 'Les trois grandes périodes qui traversent chaque décennie',
    excerpt: 'Un décryptage clair des vagues qui reviennent tous les 7, 12 et 29 ans — et de ce qu\'elles t\'invitent à comprendre.',
  },
  {
    tag: 'Confiance',
    title: 'Retrouver la confiance après une période de doute',
    excerpt: 'Quand plus rien ne semble aligné, une méthode douce en trois temps pour renouer avec ton élan naturel.',
  },
  {
    tag: 'Équilibre',
    title: 'L\'art de traverser un moment charnière sans se perdre',
    excerpt: 'Ce qu\'il faut préserver, ce qu\'il faut lâcher : un cadre simple pour les grands tournants.',
  },
  {
    tag: 'Évolution',
    title: 'Ce que tes répétitions cherchent vraiment à te dire',
    excerpt: 'Les patterns ne sont pas des fatalités. Ils sont des invitations à comprendre — et à choisir autrement.',
  },
];

export default function Blog() {
  useEffect(() => {
    const prevTitle = document.title;
    document.title = 'Blog Plume Astrale · Comprendre les périodes de votre vie';

    const upsertMeta = (attr, key, content) => {
      let el = document.querySelector(`meta[${attr}="${key}"]`);
      if (!el) {
        el = document.createElement('meta');
        el.setAttribute(attr, key);
        document.head.appendChild(el);
      }
      el.setAttribute('content', content);
      return el;
    };

    const metaDesc = upsertMeta('name', 'description',
      "Articles pour mieux comprendre les grandes périodes de votre vie : cycles, relations, décisions, équilibre, évolution. Écrits pour vous accompagner à chaque tournant.");
    upsertMeta('name', 'author', 'Plume Astrale');
    upsertMeta('name', 'keywords', 'développement personnel, cycles de vie, relations, décisions, évolution, périodes clés, Plume Astrale');
    upsertMeta('property', 'og:title', 'Blog Plume Astrale · Comprendre les périodes de votre vie');
    upsertMeta('property', 'og:type', 'blog');
    upsertMeta('property', 'og:url', 'https://plume-astrale.fr/blog');
    upsertMeta('property', 'og:image', 'https://plume-astrale.fr/logo512.png');
    upsertMeta('property', 'og:site_name', 'Plume Astrale');
    upsertMeta('name', 'twitter:card', 'summary_large_image');
    upsertMeta('name', 'twitter:title', 'Blog Plume Astrale');
    upsertMeta('name', 'twitter:description', metaDesc.getAttribute('content'));

    let canonical = document.querySelector('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.setAttribute('rel', 'canonical');
      document.head.appendChild(canonical);
    }
    canonical.setAttribute('href', 'https://plume-astrale.fr/blog');

    const ld = document.createElement('script');
    ld.type = 'application/ld+json';
    ld.text = JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Blog',
      name: 'Blog Plume Astrale',
      url: 'https://plume-astrale.fr/blog',
      description: metaDesc.getAttribute('content'),
      inLanguage: 'fr-FR',
      publisher: {
        '@type': 'Organization',
        name: 'Plume Astrale',
        url: 'https://plume-astrale.fr',
        logo: { '@type': 'ImageObject', url: 'https://plume-astrale.fr/logo512.png', width: 512, height: 512 },
      },
      blogPost: FEATURED_TOPICS.map((t) => ({
        '@type': 'BlogPosting',
        headline: t.title,
        articleSection: t.tag,
        description: t.excerpt,
        inLanguage: 'fr-FR',
      })),
    });
    document.head.appendChild(ld);

    const script = document.createElement('script');
    script.src = 'https://app.trysoro.com/api/embed/c6fc9156-b0ab-4311-a39b-8d0c736cc367';
    script.defer = true;
    document.body.appendChild(script);

    return () => {
      document.title = prevTitle;
      if (script.parentNode) document.body.removeChild(script);
      if (ld.parentNode) document.head.removeChild(ld);
    };
  }, []);

  return (
    <PsPageShell background="light">
      <section className="ps-section ps-section-light" data-testid="blog-page">
        <div className="ps-container">
          <div style={{ maxWidth: 720, marginBottom: 48 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Le journal de Plume Astrale</p>
            <h1 className="ps-h1" style={{ color: '#0F1A3C', marginBottom: 20 }}>
              Comprendre les <span className="ps-italic">périodes</span> de votre vie
            </h1>
            <p className="ps-body" style={{ color: '#232323', marginBottom: 24 }}>
              Des articles clairs et concrets sur les cycles, les relations, les décisions et l&apos;équilibre.
              Pas de jargon — juste des repères pour éclairer les moments qui comptent.
            </p>
            <Link to="/inscription" className="ps-btn ps-btn-primary" data-testid="blog-cta-signup">
              Recevoir mes 20 crédits offerts
              <Sparkles style={{ width: 16, height: 16 }} strokeWidth={2} />
            </Link>
          </div>

          {/* Grille éditoriale — sujets universels de développement personnel */}
          <div style={{ marginBottom: 64 }} data-testid="blog-featured-topics">
            <h2 className="ps-h2" style={{ color: '#0F1A3C', marginBottom: 24, fontSize: 24 }}>
              À la une
            </h2>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: 24,
            }}>
              {FEATURED_TOPICS.map((topic, i) => (
                <article
                  key={i}
                  data-testid={`blog-topic-card-${i}`}
                  style={{
                    background: '#FFFFFF',
                    border: '1px solid #E3E1DC',
                    borderRadius: 12,
                    padding: 24,
                    transition: 'transform 220ms ease, box-shadow 220ms ease',
                    cursor: 'default',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-3px)';
                    e.currentTarget.style.boxShadow = '0 12px 32px rgba(15, 26, 60, 0.08)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <div style={{
                    display: 'inline-block',
                    fontSize: 10,
                    letterSpacing: '0.22em',
                    textTransform: 'uppercase',
                    color: '#B8935A',
                    fontFamily: 'Inter, sans-serif',
                    fontWeight: 500,
                    marginBottom: 12,
                  }}>
                    {topic.tag}
                  </div>
                  <h3 style={{
                    fontFamily: 'Playfair Display, serif',
                    fontSize: 20,
                    lineHeight: 1.3,
                    color: '#0F1A3C',
                    marginBottom: 12,
                    fontStyle: 'italic',
                  }}>
                    {topic.title}
                  </h3>
                  <p style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 14,
                    lineHeight: 1.6,
                    color: '#5A5D6B',
                    margin: 0,
                  }}>
                    {topic.excerpt}
                  </p>
                </article>
              ))}
            </div>
          </div>

          {/* Widget Soro — articles complets */}
          <h2 className="ps-h2" style={{ color: '#0F1A3C', marginBottom: 24, fontSize: 24 }}>
            Tous les articles
          </h2>
          <div
            id="soro-blog"
            data-testid="soro-blog-widget"
            style={{
              background: '#FFFFFF',
              border: '1px solid #E3E1DC',
              borderRadius: 12,
              padding: 32,
              minHeight: 400,
              color: '#232323',
            }}
          />

          <div style={{
            marginTop: 48, textAlign: 'left',
            fontFamily: 'Inter, sans-serif', fontSize: 14,
            color: '#6B7280',
          }}>
            Envie d&apos;aller plus loin ?{' '}
            <Link to="/" style={{
              color: '#C9A24B', textDecoration: 'underline',
              textUnderlineOffset: 3, fontWeight: 500,
            }} data-testid="blog-cta-home">
              Découvrir les lectures personnalisées de Plume Astrale
              <ArrowRight style={{ width: 14, height: 14, display: 'inline', marginLeft: 4, verticalAlign: 'middle' }} strokeWidth={2} />
            </Link>
          </div>
        </div>
      </section>
    </PsPageShell>
  );
}
