/**
 * Act5DailyArticle — Bande "Article du jour" éditoriale, style cosmique.
 *
 * S'intercale entre les services 3 et 4 dans Acte V pour rappeler la voix
 * éditoriale quotidienne de Plume Astrale, sans casser la trame narrative.
 *
 * Réutilise BLOG_ARTICLES + la rotation déterministe par jour (même article
 * pour tout le monde le même jour → partageable, cache-friendly).
 * Style aligné sur --hex3-* (noir cosmique + or + Cormorant italic).
 */
import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { BLOG_ARTICLES } from '@/config/blogArticles';
import { event as trackEvent } from '@/lib/analytics';

const API = process.env.REACT_APP_BACKEND_URL || '';

function pickArticleOfTheDay() {
  if (!BLOG_ARTICLES?.length) return null;
  const start = new Date(new Date().getFullYear(), 0, 0);
  const now = new Date();
  const diff = now - start + (start.getTimezoneOffset() - now.getTimezoneOffset()) * 60 * 1000;
  const dayOfYear = Math.floor(diff / (1000 * 60 * 60 * 24));
  return BLOG_ARTICLES[dayOfYear % BLOG_ARTICLES.length];
}

export default function Act5DailyArticle() {
  const article = useMemo(pickArticleOfTheDay, []);
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('idle');

  if (!article) return null;

  const href = `/blog/${article.slug}`;

  const submitEmail = async (e) => {
    e.preventDefault();
    if (status === 'loading') return;
    setStatus('loading');
    try {
      const r = await fetch(`${API}/api/daily-article/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          slug: article.slug, title: article.title,
          excerpt: article.excerpt, tag: article.tag,
        }),
      });
      if (!r.ok) { setStatus('error'); return; }
      setStatus('sent');
      trackEvent('home_v3_daily_article_sent', { slug: article.slug });
      setTimeout(() => { window.open(href, '_blank', 'noopener'); }, 700);
    } catch { setStatus('error'); }
  };

  return (
    <div
      data-testid="home-experience-daily-article"
      style={{
        position: 'relative', zIndex: 1,
        maxWidth: 900, margin: '80px auto',
        padding: '48px 32px',
        border: '1px solid rgba(216, 183, 106, 0.28)',
        borderRadius: 3,
        background: 'rgba(23, 16, 46, 0.35)',
        backdropFilter: 'blur(6px)',
      }}
    >
      <p style={{
        fontFamily: '"Inter", sans-serif', fontSize: 10, letterSpacing: '0.32em',
        textTransform: 'uppercase', color: 'rgba(216, 183, 106, 0.75)',
        margin: '0 0 20px', display: 'inline-flex', alignItems: 'center', gap: 10,
      }}>
        <span aria-hidden="true">✦</span> Article du jour · offert
      </p>

      <div style={{
        display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) auto',
        gap: 40, alignItems: 'center',
      }}>
        <div>
          <p style={{
            fontFamily: '"Inter", sans-serif', fontSize: 11, letterSpacing: '0.24em',
            textTransform: 'uppercase', color: '#D8B76A',
            margin: '0 0 12px',
          }}>{article.tag}</p>
          <h3 style={{
            fontFamily: '"Cormorant Garamond", "Playfair Display", serif',
            fontWeight: 400, fontSize: 'clamp(24px, 3.2vw, 34px)',
            lineHeight: 1.15, color: '#F4EFE6', margin: '0 0 12px',
          }}>{article.title}</h3>
          <p style={{
            fontFamily: '"Cormorant Garamond", serif', fontStyle: 'italic',
            fontSize: 16, color: 'rgba(244, 239, 230, 0.65)',
            lineHeight: 1.55, margin: '0 0 20px',
          }}>{article.excerpt}</p>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20, alignItems: 'center' }}>
            <Link
              to={href}
              onClick={() => trackEvent('home_v3_daily_article_opened', { slug: article.slug })}
              data-testid="home-experience-daily-article-open"
              style={{
                fontFamily: '"Inter", sans-serif', fontSize: 11, letterSpacing: '0.24em',
                textTransform: 'uppercase', color: '#F4EFE6', textDecoration: 'none',
                padding: '10px 20px', border: '1px solid rgba(216, 183, 106, 0.5)',
                borderRadius: 2,
              }}
            >
              Lire maintenant →
            </Link>
            <span style={{
              fontFamily: '"Cormorant Garamond", serif', fontStyle: 'italic',
              fontSize: 14, color: 'rgba(244, 239, 230, 0.45)',
            }}>ou</span>
            <form onSubmit={submitEmail} style={{ display: 'flex', gap: 8, flex: 1, minWidth: 240 }}>
              <input
                type="email" placeholder="votre@email.com"
                value={email} onChange={(e) => setEmail(e.target.value)}
                required
                disabled={status === 'loading' || status === 'sent'}
                data-testid="home-experience-daily-article-email"
                style={{
                  flex: 1, background: 'transparent',
                  border: '1px solid rgba(216, 183, 106, 0.35)',
                  padding: '10px 14px', color: '#F4EFE6',
                  fontFamily: '"Inter", sans-serif', fontSize: 12,
                  outline: 'none', borderRadius: 2,
                }}
              />
              <button
                type="submit"
                disabled={status === 'loading' || status === 'sent'}
                data-testid="home-experience-daily-article-send"
                style={{
                  fontFamily: '"Inter", sans-serif', fontSize: 11, letterSpacing: '0.20em',
                  textTransform: 'uppercase', color: '#D8B76A',
                  background: 'transparent', border: '1px solid rgba(216, 183, 106, 0.6)',
                  padding: '10px 18px', borderRadius: 2, cursor: 'pointer',
                }}
              >
                {status === 'sent' ? 'Envoyé ✓' : status === 'loading' ? 'Envoi…' : 'Par email'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
