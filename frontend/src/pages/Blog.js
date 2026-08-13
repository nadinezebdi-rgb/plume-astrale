import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';

/**
 * Blog Plume Astrale — page SEO dédiée · Charte v3 (light).
 *
 * Le widget Soro est monté dans <div id="soro-blog"></div>.
 * Fond blanc cassé pour que le contenu Soro (souvent texte sombre)
 * soit LISIBLE, contrairement à l'ancienne version doré-sur-violet.
 */
export default function Blog() {
  useEffect(() => {
    const prevTitle = document.title;
    document.title = 'Blog Plume Astrale · Astrologie, Karma, Tarot, Numérologie';

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
      "Articles de fond sur l'astrologie karmique, le tarot, la numérologie et la Kabbale. Écrits par Soléna pour t'accompagner dans ton chemin d'évolution.");
    upsertMeta('name', 'author', 'Soléna · Plume Astrale');
    upsertMeta('name', 'keywords', 'astrologie, karma, numérologie, tarot, kabbale, thème natal, Soléna, plume astrale');
    upsertMeta('property', 'og:title', 'Blog Plume Astrale');
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
      author: { '@type': 'Person', name: 'Soléna', jobTitle: 'Voix de Plume Astrale' },
      publisher: {
        '@type': 'Organization',
        name: 'Plume Astrale',
        url: 'https://plume-astrale.fr',
        logo: { '@type': 'ImageObject', url: 'https://plume-astrale.fr/logo512.png', width: 512, height: 512 },
      },
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
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Le journal de Soléna</p>
            <h1 className="ps-h1" style={{ color: '#0F1A3C', marginBottom: 20 }}>
              Le <span className="ps-italic">Blog</span> Plume Astrale
            </h1>
            <p className="ps-body" style={{ color: '#232323', marginBottom: 24 }}>
              Articles de fond sur l&apos;astrologie karmique, le tarot, la numérologie et la Kabbale.
              Écrits pour t&apos;accompagner dans ton chemin d&apos;évolution.
            </p>
            <Link to="/inscription" className="ps-btn ps-btn-primary" data-testid="blog-cta-signup">
              Recevoir mes 20 crédits offerts
              <Sparkles style={{ width: 16, height: 16 }} strokeWidth={2} />
            </Link>
          </div>

          {/* Widget Soro — fond blanc, texte sombre → LISIBLE */}
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
            }}>
              Découvre les lectures personnalisées de Soléna
              <ArrowRight style={{ width: 14, height: 14, display: 'inline', marginLeft: 4, verticalAlign: 'middle' }} strokeWidth={2} />
            </Link>
          </div>
        </div>
      </section>
    </PsPageShell>
  );
}
