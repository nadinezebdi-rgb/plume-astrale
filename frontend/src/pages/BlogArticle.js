import React, { useEffect } from 'react';
import { Link, useParams, Navigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import SEO from '@/components/SEO';
import PsPageShell from '@/components/PsPageShell';
import { BLOG_ARTICLES, getArticleBySlug } from '@/config/blogArticles';

/**
 * BlogArticle · route /blog/:slug — SEO P2 concours 2026-02.
 *
 * Chaque article a maintenant :
 *   • Sa propre URL propre (/blog/slug au lieu de /blog?post=slug)
 *   • Un canonical auto-référent
 *   • Un H1 unique
 *   • Une meta description dédiée
 *   • Un JSON-LD BlogPosting
 *
 * Le CORPS de l'article est servi par Soro embed. Cette page enveloppe
 * juste ce contenu tiers dans le bon shell SEO.
 */

export default function BlogArticle() {
  const { slug } = useParams();
  const article = getArticleBySlug(slug);

  useEffect(() => {
    // Slug inconnu → skip le chargement du widget
    if (!article) return;
    // Charge le widget Soro pour afficher le contenu de l'article
    const existing = document.querySelector('script[data-soro-blog]');
    if (existing) existing.remove();
    const script = document.createElement('script');
    script.src = 'https://app.trysoro.com/api/embed/c6fc9156-b0ab-4311-a39b-8d0c736cc367';
    script.defer = true;
    script.setAttribute('data-soro-blog', '1');
    document.body.appendChild(script);
    return () => { if (script.parentNode) document.body.removeChild(script); };
  }, [slug, article]);

  // Slug inconnu → renvoie sur /blog (rules-of-hooks : return APRÈS useEffect)
  if (!article) {
    return <Navigate to="/blog" replace />;
  }

  const currentIdx = BLOG_ARTICLES.findIndex((a) => a.slug === slug);
  const prev = currentIdx > 0 ? BLOG_ARTICLES[currentIdx - 1] : null;
  const next = currentIdx < BLOG_ARTICLES.length - 1 ? BLOG_ARTICLES[currentIdx + 1] : null;

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: article.title,
    description: article.description,
    articleSection: article.tag,
    datePublished: article.date,
    dateModified: article.date,
    inLanguage: 'fr-FR',
    author: { '@type': 'Organization', name: 'Plume Astrale', url: 'https://plume-astrale.fr' },
    publisher: {
      '@type': 'Organization',
      name: 'Plume Astrale',
      url: 'https://plume-astrale.fr',
      logo: { '@type': 'ImageObject', url: 'https://plume-astrale.fr/logo512.png', width: 512, height: 512 },
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': `https://plume-astrale.fr/blog/${slug}`,
    },
  };

  return (
    <PsPageShell background="light">
      <SEO
        path={`/blog/${slug}`}
        title={`${article.title} · Blog Plume Astrale`}
        description={article.description}
        jsonLd={jsonLd}
      />

      <section className="ps-section ps-section-light" data-testid={`blog-article-${slug}`}>
        <div className="ps-container">
          {/* Breadcrumb */}
          <div style={{ marginBottom: 32, fontSize: 13, fontFamily: 'Inter, sans-serif' }}>
            <Link to="/blog" data-testid="article-back-link"
              style={{
                color: '#6B7280', textDecoration: 'none',
                display: 'inline-flex', alignItems: 'center', gap: 6,
              }}
            >
              <ArrowLeft style={{ width: 14, height: 14 }} strokeWidth={2} />
              Retour au blog
            </Link>
          </div>

          {/* Header article */}
          <div style={{ maxWidth: 720, marginBottom: 40 }}>
            <p style={{
              fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 500,
              letterSpacing: '0.28em', textTransform: 'uppercase',
              color: '#B8935A', marginBottom: 16,
            }}>
              {article.tag}
            </p>
            <h1
              data-testid="article-h1"
              style={{
                fontFamily: 'Playfair Display, serif',
                fontSize: 'clamp(2rem, 4.2vw, 3rem)',
                fontWeight: 400,
                lineHeight: 1.2,
                color: '#0F1A3C',
                marginBottom: 20,
              }}
            >
              {article.title}
            </h1>
            <p style={{
              fontFamily: 'Playfair Display, serif',
              fontStyle: 'italic',
              fontSize: 'clamp(17px, 1.8vw, 20px)',
              lineHeight: 1.55,
              color: '#5A5D6B',
              margin: 0,
            }}>
              {article.excerpt}
            </p>
          </div>

          {/* Corps de l'article — servi par Soro */}
          <div
            id="soro-blog"
            data-testid="soro-article-widget"
            style={{
              background: '#FFFFFF',
              border: '1px solid #E3E1DC',
              borderRadius: 12,
              padding: 32,
              minHeight: 400,
              color: '#232323',
            }}
          />

          {/* Navigation article précédent/suivant */}
          {(prev || next) && (
            <div style={{
              marginTop: 56,
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
              gap: 20,
            }}>
              {prev && (
                <Link
                  to={`/blog/${prev.slug}`}
                  data-testid="article-prev"
                  style={{
                    padding: 24,
                    border: '1px solid #E3E1DC',
                    borderRadius: 12,
                    background: '#fff',
                    textDecoration: 'none',
                    color: '#0F1A3C',
                    transition: 'border-color 220ms, transform 220ms',
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#C9A24B'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#E3E1DC'; e.currentTarget.style.transform = 'translateY(0)'; }}
                >
                  <div style={{ fontSize: 10, color: '#6B7280', letterSpacing: '0.2em', textTransform: 'uppercase', marginBottom: 6 }}>
                    ← Article précédent
                  </div>
                  <div style={{ fontFamily: 'Playfair Display, serif', fontSize: 17, lineHeight: 1.35, fontStyle: 'italic' }}>
                    {prev.title}
                  </div>
                </Link>
              )}
              {next && (
                <Link
                  to={`/blog/${next.slug}`}
                  data-testid="article-next"
                  style={{
                    padding: 24,
                    border: '1px solid #E3E1DC',
                    borderRadius: 12,
                    background: '#fff',
                    textDecoration: 'none',
                    color: '#0F1A3C',
                    textAlign: 'right',
                    transition: 'border-color 220ms, transform 220ms',
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#C9A24B'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#E3E1DC'; e.currentTarget.style.transform = 'translateY(0)'; }}
                >
                  <div style={{ fontSize: 10, color: '#6B7280', letterSpacing: '0.2em', textTransform: 'uppercase', marginBottom: 6 }}>
                    Article suivant →
                  </div>
                  <div style={{ fontFamily: 'Playfair Display, serif', fontSize: 17, lineHeight: 1.35, fontStyle: 'italic' }}>
                    {next.title}
                  </div>
                </Link>
              )}
            </div>
          )}

          {/* CTA Cercle */}
          <div style={{ marginTop: 56, textAlign: 'center', fontSize: 14, fontFamily: 'Inter, sans-serif', color: '#6B7280' }}>
            Envie d&apos;approfondir votre lecture personnelle ?{' '}
            <Link to="/decouvrir" style={{ color: '#C9A24B', textDecoration: 'underline', textUnderlineOffset: 3, fontWeight: 500 }}>
              Découvrir mon parcours <ArrowRight style={{ width: 14, height: 14, display: 'inline', marginLeft: 4, verticalAlign: 'middle' }} strokeWidth={2} />
            </Link>
          </div>
        </div>
      </section>
    </PsPageShell>
  );
}
