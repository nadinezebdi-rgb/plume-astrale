import {useCallback, useEffect, useRef, useState} from 'react';
import { Link } from 'react-router-dom';
import { event as trackEvent } from '../lib/analytics';
import CelestialBackdrop from './CelestialBackdrop';
import './AstralBookEditorial.css';

const publicPath = process.env.PUBLIC_URL || '';
const poster = `${publicPath}/images/editorial/livre-astral-video-poster.webp`;
const movie = `${publicPath}/videos/editorial/livre-astral-15s.mp4`;
const previewPdf = process.env.REACT_APP_NATAL_BOOK_PREVIEW_URL;

export function AstralBookVideo() {
  const video = useRef(null);
  const container = useRef(null);
  const visible = useRef(false);
  const manualPause = useRef(false);
  const [playing, setPlaying] = useState(false);
  const [failed, setFailed] = useState(false);

  const play = useCallback(() => {
    const element = video.current;
    if (!element) return;
    if (!element.getAttribute('src')) element.src = movie;
    element.muted = true;
    const request = element.play();
    if (request?.catch) request.catch(() => setPlaying(false));
  }, []);

  useEffect(() => {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const mobile = window.matchMedia('(max-width: 800px)');
    const connection = navigator.connection;
    const update = () => {
      if (!visible.current || document.hidden || reduced.matches || mobile.matches || connection?.saveData || manualPause.current) {
        video.current?.pause();
      } else {
        play();
      }
    };
    const observer = typeof IntersectionObserver === 'function' ? new IntersectionObserver(([entry]) => {
      visible.current = entry.isIntersecting;
      update();
    }, { threshold: 0.25 }) : null;
    if (observer && container.current) observer.observe(container.current);
    // Without IntersectionObserver, keep the poster and explicit play button.
    document.addEventListener('visibilitychange', update);
    reduced.addEventListener?.('change', update);
    mobile.addEventListener?.('change', update);
    connection?.addEventListener?.('change', update);
    const element = video.current;
    return () => {
      observer?.disconnect();
      document.removeEventListener('visibilitychange', update);
      reduced.removeEventListener?.('change', update);
      mobile.removeEventListener?.('change', update);
      connection?.removeEventListener?.('change', update);
      element?.pause();
    };
  }, [play]);

  const toggle = () => {
    if (playing) {
      manualPause.current = true;
      video.current?.pause();
    } else {
      manualPause.current = false;
      play();
    }
  };

  return <figure className="pa-book-film" ref={container}>
    <div className="pa-book-film__screen">
      {failed ? <img src={poster} alt="Maquette du Livre Astral ouvert sur une carte du ciel illustrative, dans un décor bleu nuit et or" width="1440" height="810" /> : <video
        ref={video} poster={poster} muted playsInline loop preload="none"
        aria-label="Présentation illustrative du Livre Astral : couverture, intérieur, carte du ciel et dos. Vidéo muette de 15 secondes."
        onPlay={() => setPlaying(true)} onPause={() => setPlaying(false)}
        onError={() => { setFailed(true); setPlaying(false); }}
      />}
      <span className="pa-book-film__duration">LE LIVRE ASTRAL · 15 S</span>
      {!failed && <button type="button" className="pa-book-film__control" onClick={toggle} aria-label={playing ? 'Mettre la vidéo en pause' : 'Lire la vidéo de présentation'} aria-pressed={playing}>
        <span aria-hidden="true">{playing ? 'Ⅱ' : '▷'}</span>{playing ? 'Pause' : 'Voir le livre'}
      </button>}
    </div>
    <figcaption>Maquette de présentation <span>Intérieur et carte illustratifs · sans son</span></figcaption>
  </figure>;
}

export function AstralBookHero({ onStart, price }) {
  // Scroll vers la section « Par où commencer » (AstralPathways) qui liste les
  // services par besoin. ScrollIntoView natif + scroll-margin-top CSS gèrent le
  // décalage du menu fixe.
  const scrollToPathways = useCallback(() => {
    const target = document.getElementById('pa-book-pathways');
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      // Focus accessible : donne la main au titre pour les lecteurs d'écran
      const h2 = target.querySelector('h2');
      if (h2) {
        h2.setAttribute('tabindex', '-1');
        setTimeout(() => h2.focus({ preventScroll: true }), 400);
      }
    }
    try {
      import('../lib/abTracking').then(({ trackABEvent }) => {
        trackABEvent('home_hero_h1', 'reset', 'cta_click', { destination: 'pathways' });
      });
    } catch { /* noop */ }
  }, []);

  // « Découvrir un exemple » → ouvre le PDF démo réel (anonymisé, service Thème
  // Natal). URL fournie par REACT_APP_NATAL_BOOK_PREVIEW_URL, par défaut un
  // extrait local servi par le front.
  const samplePdfUrl = process.env.REACT_APP_NATAL_BOOK_PREVIEW_URL
    || '/demos/theme-natal-sample.pdf';
  const onSampleClick = useCallback(() => {
    try {
      trackEvent('pdf_preview_click', {
        cta_location: 'hero_v4',
        pdf_url: samplePdfUrl,
        destination: 'natal_book_sample',
      });
    } catch { /* noop */ }
  }, [samplePdfUrl]);

  // Variante « offer » (bouton livre payant) conservée pour les pages où
  // AstralBookHero est réutilisé avec onStart (checkout direct).
  const onPrimaryClick = useCallback(() => {
    if (onStart) onStart();
    else scrollToPathways();
  }, [onStart, scrollToPathways]);

  return (
    <section className="pa-book-hero" aria-labelledby="pa-book-title" data-testid="pa-book-hero-v4">
      <CelestialBackdrop density={70} shootingStars interval={14000} />
      <div className="pa-book-hero__copy">
        <p className="pa-book-eyebrow" data-testid="hero-eyebrow">
          <span aria-hidden="true">✦</span> ASTROLOGIE · TAROT · NUMÉROLOGIE
        </p>
        <h1 id="pa-book-title" data-testid="hero-h1">
          <span className="pa-book-h1__line">Mieux te comprendre.</span>
          <span className="pa-book-h1__line">Savoir ce que tu veux.</span>
          <span className="pa-book-h1__line pa-book-h1__line--accent">Choisir ta direction.</span>
        </h1>
        <p className="pa-book-lead" data-testid="hero-lead">
          Ton thème astral, tes nombres et les cartes deviennent des supports
          de réflexion pour explorer tes forces, tes relations et les questions
          qui comptent aujourd&apos;hui.
        </p>
        <div className="pa-book-actions">
          {onStart ? (
            <button
              type="button"
              className="pa-book-button"
              onClick={onPrimaryClick}
              data-testid="hero-primary-cta"
            >
              Créer mon livre astral{price ? ` — ${price} €` : ''}
              <span aria-hidden="true">↗</span>
            </button>
          ) : (
            <button
              type="button"
              className="pa-book-button"
              onClick={scrollToPathways}
              data-testid="hero-primary-cta"
            >
              Trouver ma lecture
              <span aria-hidden="true">↓</span>
            </button>
          )}
          <a
            className="pa-book-text-link pa-book-text-link--secondary"
            href={samplePdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            onClick={onSampleClick}
            data-testid="hero-secondary-cta"
            aria-label="Découvrir un exemple de lecture Thème Natal anonymisé (PDF)"
          >
            Découvrir un exemple <span aria-hidden="true">↗</span>
          </a>
        </div>
        <p className="pa-book-hint" data-testid="hero-hint">
          Pour mieux te connaître · Comprendre tes liens · Explorer une nouvelle direction
        </p>
      </div>
      <AstralBookVideo />
    </section>
  );
}

export function AstralPathways() {
  const paths = [
    ['01', 'Mieux me connaître', 'Thème natal et numérologie pour explorer tes forces et tes élans.', '/theme-natal'],
    ['02', 'Comprendre mes relations', 'Compatibilité et synastrie pour éclairer la rencontre de deux ciels.', '/synastrie'],
    ['03', 'Explorer une question', 'Le tarot pour mettre une question en lumière, simplement.', '/services/tarot/oui-non'],
    ['04', 'Prendre du recul sur ma période', 'Révolution solaire et lectures de cycles pour relire tes mois à venir.', '/services/revolution-solaire'],
  ];
  return (
    <section
      id="pa-book-pathways"
      className="pa-book-pathways"
      aria-labelledby="pa-pathways-title"
      data-testid="pa-book-pathways"
    >
      <p className="pa-book-eyebrow">PAR OÙ COMMENCER ?</p>
      <h2 id="pa-pathways-title">Choisis ta lecture.</h2>
      <div>
        {paths.map(([number, title, description, to]) => (
          <Link key={number} to={to} data-testid={`pathway-${number}`}>
            <span>{number}</span>
            <h3>{title}</h3>
            <p>{description}</p>
            <span className="pa-pathways-arrow" aria-hidden="true">↗</span>
          </Link>
        ))}
      </div>
    </section>
  );
}

export function AstralBookDiscovery() {
  return <section id="pa-book-discover" className="pa-book-discover" aria-labelledby="pa-book-discover-title"><header><p className="pa-book-eyebrow">À CHAQUE LECTURE, SA PLACE</p><h2 id="pa-book-discover-title">À lire aujourd’hui.<br /><em>À retrouver demain.</em></h2><p>Découvre les options et le contenu de chaque édition avant de choisir.</p></header><div className="pa-book-editions"><article><span>01 / LIRE</span><h3>L’édition numérique</h3><p>Ta lecture personnelle en PDF, à parcourir sur ton ordinateur ou ta tablette.</p><Link to="/theme-natal">Découvrir le PDF ↗</Link></article><article><span>02 / CONSERVER</span><h3>Le livre imprimé</h3><p>Le plaisir du papier et d’une couverture à ton prénom. Découvre les éditions brochée et reliée.</p><Link to="/livres">Explorer les éditions papier ↗</Link></article></div>{previewPdf && <a className="pa-book-preview-cta" href={previewPdf} target="_blank" rel="noopener noreferrer" data-testid="natal-book-preview-cta" onClick={() => trackEvent('pdf_preview_click', { cta_location: 'home_bump_discover', pdf_url: previewPdf, destination: 'natal_book_sample' })}>
  <span className="pa-book-preview-cta__icon" aria-hidden="true">
    <svg width="22" height="26" viewBox="0 0 22 26" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 1h11l6 6v16a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2Z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/>
      <path d="M14 1v6h6" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/>
      <text x="11" y="20" textAnchor="middle" fontSize="6.4" fontWeight="700" fontFamily="Inter, Arial, sans-serif" fill="currentColor" letterSpacing="0.3">PDF</text>
    </svg>
  </span>
  <span className="pa-book-preview-cta__body">
    <span className="pa-book-preview-cta__title">Feuilleter un extrait du livre</span>
    <span className="pa-book-preview-cta__meta">Aperçu PDF · 32 pages · lecture dans ton navigateur</span>
  </span>
  <span className="pa-book-preview-cta__arrow" aria-hidden="true">↗</span>
</a>}<ol className="pa-book-process"><li><h3>Ta naissance</h3><p>Renseigne tes informations et choisis ton édition.</p></li><li><h3>Ta lecture</h3><p>Explore ton ciel dans une démarche symbolique et personnelle.</p></li><li><h3>Ton chemin</h3><p>Reviens aux chapitres à ton rythme, avec ta liberté d’interprétation.</p></li></ol></section>;
}
