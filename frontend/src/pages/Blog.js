import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';

/**
 * Blog Plume Astrale — page SEO dédiée.
 *
 * Le widget Soro (trysoro.com) est monté dans <div id="soro-blog"></div>.
 * Le script embed est injecté dynamiquement au montage (defer) et retiré au
 * démontage pour ne pas polluer les autres pages ni doubler l'affichage.
 *
 * Balises SEO : title, description, Open Graph, JSON-LD Blog schema —
 * cruciales pour le référencement Google/Bing.
 */
export default function Blog() {
  useEffect(() => {
    // ─── SEO metadata (dynamic) ──────────────────────────
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

    const metaDesc = upsertMeta(
      'name',
      'description',
      "Articles de fond sur l'astrologie karmique, le tarot, la numérologie et la Kabbale. Écrits par Soléna pour t'accompagner dans ton chemin d'évolution."
    );
    const metaAuthor = upsertMeta('name', 'author', 'Soléna · Plume Astrale');
    const metaKeywords = upsertMeta('name', 'keywords', 'astrologie, karma, numérologie, tarot, kabbale, chemin de vie, thème natal, horoscope personnalisé, Soléna, plume astrale');
    const ogTitle = upsertMeta('property', 'og:title', 'Blog Plume Astrale');
    const ogType = upsertMeta('property', 'og:type', 'blog');
    const ogUrl = upsertMeta('property', 'og:url', 'https://plume-astrale.fr/blog');
    const ogImage = upsertMeta('property', 'og:image', 'https://plume-astrale.fr/logo512.png');
    const ogSite = upsertMeta('property', 'og:site_name', 'Plume Astrale');
    const twCard = upsertMeta('name', 'twitter:card', 'summary_large_image');
    const twTitle = upsertMeta('name', 'twitter:title', 'Blog Plume Astrale');
    const twDesc = upsertMeta('name', 'twitter:description', metaDesc.getAttribute('content'));
    const canonical = (() => {
      let el = document.querySelector('link[rel="canonical"]');
      if (!el) {
        el = document.createElement('link');
        el.setAttribute('rel', 'canonical');
        document.head.appendChild(el);
      }
      el.setAttribute('href', 'https://plume-astrale.fr/blog');
      return el;
    })();

    // JSON-LD Blog schema + Publisher (aide Google E-A-T)
    const ld = document.createElement('script');
    ld.type = 'application/ld+json';
    ld.text = JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Blog',
      name: 'Blog Plume Astrale',
      url: 'https://plume-astrale.fr/blog',
      description: metaDesc.getAttribute('content'),
      inLanguage: 'fr-FR',
      author: {
        '@type': 'Person',
        name: 'Soléna',
        jobTitle: 'Astrologue · Numérologue · Kabbaliste',
        url: 'https://plume-astrale.fr',
      },
      publisher: {
        '@type': 'Organization',
        name: 'Plume Astrale',
        url: 'https://plume-astrale.fr',
        logo: {
          '@type': 'ImageObject',
          url: 'https://plume-astrale.fr/logo512.png',
          width: 512,
          height: 512,
        },
      },
      mainEntityOfPage: {
        '@type': 'WebPage',
        '@id': 'https://plume-astrale.fr/blog',
      },
    });
    document.head.appendChild(ld);

    // ─── Soro embed script (defer) ───────────────────────
    const script = document.createElement('script');
    script.src = 'https://app.trysoro.com/api/embed/c6fc9156-b0ab-4311-a39b-8d0c736cc367';
    script.defer = true;
    document.body.appendChild(script);

    return () => {
      document.title = prevTitle;
      document.body.removeChild(script);
      document.head.removeChild(ld);
      // On laisse les metas description/OG en place — pas critiques à nettoyer
    };
  }, []);

  return (
    <div
      data-testid="blog-page"
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #0a0a1a 0%, #111625 100%)',
        color: '#F5EEE0',
        padding: '80px 24px 120px',
      }}
    >
      <div style={{ maxWidth: 900, margin: '0 auto' }}>
        {/* Hero header */}
        <div style={{ textAlign: 'center', marginBottom: 60 }}>
          <div
            style={{
              fontSize: 13,
              letterSpacing: '.22em',
              textTransform: 'uppercase',
              color: '#E8C766',
              fontWeight: 600,
              marginBottom: 12,
            }}
          >
            ✦ Le journal de Soléna ✦
          </div>
          <h1
            style={{
              fontFamily: '"Cormorant Garamond", "Playfair Display", serif',
              fontSize: 'clamp(36px, 6vw, 56px)',
              fontWeight: 500,
              margin: 0,
              lineHeight: 1.1,
              color: '#F5EEE0',
            }}
          >
            Le Blog Plume Astrale
          </h1>
          <p
            style={{
              fontSize: 16,
              lineHeight: 1.7,
              color: 'rgba(232,230,240,0.75)',
              marginTop: 20,
              maxWidth: 560,
              marginLeft: 'auto',
              marginRight: 'auto',
            }}
          >
            Articles de fond sur l&rsquo;astrologie karmique, le tarot, la numérologie
            et la Kabbale. Écrits pour t&rsquo;accompagner dans ton chemin d&rsquo;évolution.
          </p>
          <div style={{ marginTop: 28 }}>
            <Link
              to="/inscription"
              data-testid="blog-cta-signup"
              style={{
                display: 'inline-block',
                padding: '12px 28px',
                background: 'linear-gradient(135deg, #E8C766 0%, #D4AF37 100%)',
                color: '#111625',
                borderRadius: 30,
                fontSize: 14,
                fontWeight: 700,
                letterSpacing: '.08em',
                textDecoration: 'none',
                textTransform: 'uppercase',
              }}
            >
              Recevoir mes 20 crédits offerts
            </Link>
          </div>
        </div>

        {/* Soro widget mount point */}
        <div
          id="soro-blog"
          data-testid="soro-blog-widget"
          style={{
            background: 'rgba(255,255,255,0.02)',
            border: '1px solid rgba(232,199,102,0.15)',
            borderRadius: 16,
            padding: 32,
            minHeight: 400,
          }}
        />

        {/* Footer teaser */}
        <div
          style={{
            marginTop: 60,
            textAlign: 'center',
            fontSize: 13,
            color: 'rgba(232,230,240,0.5)',
            lineHeight: 1.7,
          }}
        >
          Envie d&rsquo;aller plus loin ?{' '}
          <Link
            to="/"
            style={{ color: '#E8C766', textDecoration: 'underline' }}
          >
            Découvre les lectures personnalisées de Soléna
          </Link>
        </div>
      </div>
    </div>
  );
}
