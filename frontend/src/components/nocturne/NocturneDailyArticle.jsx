/* eslint-disable react/no-unescaped-entities */
import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles, MailCheck } from 'lucide-react';
import { BLOG_ARTICLES } from '@/config/blogArticles';
import './NocturneDailyArticle.css';

const API = process.env.REACT_APP_BACKEND_URL || '';

/**
 * NocturneDailyArticle · le bloc "vous repartez avec un article"
 * ------------------------------------------------------------------
 * Chaque visiteur reçoit un article éditorial du jour, tiré parmi les 9
 * articles publiés. La rotation est déterministe par jour (day-of-year
 * modulo N) — même article pour tout le monde le même jour, donc partageable.
 *
 * Deux façons d'en repartir :
 *   1. "Lire maintenant" → redirige vers /blog/{slug}
 *   2. "Me l'envoyer par email" → capture email (POST /api/daily-article/send)
 *      et redirige vers l'article dans un nouvel onglet.
 *
 * Style : magazine éditorial premium — bordure or, typo Playfair,
 * mention "L'ARTICLE DU JOUR · OFFERT" pour créer la sensation de cadeau.
 */
export default function NocturneDailyArticle() {
  const article = useMemo(pickArticleOfTheDay, []);
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('idle'); // idle | loading | sent | error
  const [errorMsg, setErrorMsg] = useState(null);

  const href = `/blog/${article.slug}`;

  const submitEmail = async (e) => {
    e.preventDefault();
    setStatus('loading');
    setErrorMsg(null);
    try {
      const r = await fetch(`${API}/api/daily-article/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          slug: article.slug,
          title: article.title,
          excerpt: article.excerpt,
          tag: article.tag,
        }),
      });
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        setErrorMsg(d.detail || "Impossible d'envoyer l'article pour le moment.");
        setStatus('error');
        return;
      }
      setStatus('sent');
      // Redirige vers l'article dans un nouvel onglet
      setTimeout(() => {
        window.open(href, '_blank', 'noopener');
      }, 700);
    } catch {
      setErrorMsg("Impossible d'envoyer l'article pour le moment.");
      setStatus('error');
    }
  };

  return (
    <section
      className="nda-section"
      data-testid="nocturne-daily-article"
      aria-labelledby="nda-title"
    >
      <div className="nda-bg" aria-hidden="true" />
      <div className="nda-container">
        <div className="nda-eyebrow">
          <Sparkles style={{ width: 14, height: 14 }} strokeWidth={1.6} />
          <span>L&apos;article du jour · offert aux visiteurs</span>
        </div>

        <div className="nda-grid">
          <div className="nda-editorial">
            <p className="nda-tag" data-testid="nda-tag">{article.tag}</p>
            <h2 className="nda-h2" id="nda-title" data-testid="nda-title">
              {article.title}
            </h2>
            <p className="nda-excerpt">{article.excerpt}</p>
            <p className="nda-meta">
              <span>Une lecture de 4 minutes</span>
              <span className="nda-sep">·</span>
              <span>{formatDateFr(article.date)}</span>
            </p>

            <div className="nda-actions">
              <Link
                to={href}
                data-testid="nda-cta-read-now"
                className="nda-cta-primary"
              >
                Lire maintenant
                <ArrowRight style={{ width: 15, height: 15 }} strokeWidth={2} />
              </Link>

              {status !== 'sent' ? (
                <form onSubmit={submitEmail} className="nda-inline-form">
                  <label htmlFor="nda-email" className="nda-inline-label">
                    ou <span>recevez-le par email</span>
                  </label>
                  <div className="nda-inline-row">
                    <input
                      id="nda-email"
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="votre@email.fr"
                      data-testid="nda-email-input"
                      className="nda-input"
                      disabled={status === 'loading'}
                    />
                    <button
                      type="submit"
                      data-testid="nda-cta-email"
                      className="nda-cta-ghost"
                      disabled={status === 'loading'}
                    >
                      {status === 'loading' ? 'Envoi…' : 'Envoyer'}
                    </button>
                  </div>
                  {errorMsg && (
                    <p className="nda-error" data-testid="nda-error">{errorMsg}</p>
                  )}
                </form>
              ) : (
                <div className="nda-sent" data-testid="nda-sent">
                  <MailCheck style={{ width: 18, height: 18 }} strokeWidth={1.8} />
                  <span>C&apos;est envoyé. Regardez votre boîte — l&apos;article s&apos;ouvre dans un instant.</span>
                </div>
              )}
            </div>
          </div>

          <aside className="nda-side" aria-label="À propos de nos articles">
            <div className="nda-side-inner">
              <p className="nda-side-eyebrow">Chaque jour, un article différent</p>
              <p className="nda-side-body">
                Nos articles n&apos;essaient de vous vendre rien. Ils prennent le temps
                d&apos;expliquer un sujet clair — vos maisons astrologiques, le retour de
                Saturne, comment lire Vénus — comme le ferait un professeur bienveillant.
              </p>
              <p className="nda-side-body">
                <b>Neuf articles rédigés.</b> Un nouveau chaque jour. Vous pouvez tous les
                lire librement, ou en emporter un dans votre boîte email.
              </p>
              <Link
                to="/blog"
                data-testid="nda-cta-all-articles"
                className="nda-side-cta"
              >
                Voir les 9 articles
                <ArrowRight style={{ width: 13, height: 13 }} strokeWidth={2} />
              </Link>
            </div>
          </aside>
        </div>
      </div>
    </section>
  );
}

// ── Helpers ──────────────────────────────────────────────────

function pickArticleOfTheDay() {
  if (!BLOG_ARTICLES?.length) return null;
  const now = new Date();
  // Day-of-year (1..366) — même article pour tous les visiteurs d'une même journée.
  const start = new Date(now.getFullYear(), 0, 0);
  const diff = (now - start) + ((start.getTimezoneOffset() - now.getTimezoneOffset()) * 60 * 1000);
  const dayOfYear = Math.floor(diff / (1000 * 60 * 60 * 24));
  const idx = dayOfYear % BLOG_ARTICLES.length;
  return BLOG_ARTICLES[idx];
}

function formatDateFr(iso) {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
  } catch {
    return iso;
  }
}
