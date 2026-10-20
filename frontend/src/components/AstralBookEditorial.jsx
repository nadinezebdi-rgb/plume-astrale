import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { event as trackEvent } from '../lib/analytics';
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
  // A/B expérience sur le titre H1 — pick 50/50 persisté en localStorage.
  // Variantes : A (actuelle) · B (astrologie-nommée) · C (preuve-émotion)
  const VARIANTS = React.useMemo(() => ({
    A: {
      eyebrow: 'PLUME ASTRALE · VOTRE LIVRE PERSONNEL',
      titleHtml: 'Votre ciel.<br /><em>Votre histoire.</em><br />En livre.',
      lead: 'Explorez vos élans, vos liens et vos possibilités dans une lecture de votre ciel de naissance. Un livre à parcourir, à garder et à retrouver au fil de votre vie.',
    },
    B: {
      eyebrow: 'ASTROLOGIE QUI SAIT VOTRE PRÉNOM',
      titleHtml: 'L’astrologie<br /><em>qui sait</em><br />votre prénom.',
      lead: 'Un livre entièrement composé pour vous à partir de votre carte du ciel : vos besoins, vos liens, vos cycles. 46 pages à retrouver tout au long de votre vie.',
    },
    C: {
      eyebrow: 'LE LIVRE DE VOTRE CIEL DE NAISSANCE',
      titleHtml: 'Ce que votre ciel<br /><em>cherchait à vous dire.</em>',
      lead: 'Une lecture profonde et personnelle de votre thème natal, composée en 46 pages. Pour mieux comprendre ce qui vous anime, ce qui vous lie, et où vous allez.',
    },
  }), []);
  const [variantKey, setVariantKey] = useState(() => {
    try {
      const existing = localStorage.getItem('plume_hero_variant');
      if (existing && VARIANTS[existing]) return existing;
      const keys = Object.keys(VARIANTS);
      const picked = keys[Math.floor(Math.random() * keys.length)];
      localStorage.setItem('plume_hero_variant', picked);
      return picked;
    } catch {
      return 'A';
    }
  });
  // Au mount, demander au backend si une variante gagnante est verrouillée.
  // Si oui → bascule immédiatement, et persist en localStorage pour next loads.
  React.useEffect(() => {
    const api = process.env.REACT_APP_BACKEND_URL;
    if (!api) return;
    let cancelled = false;
    fetch(`${api}/api/experiments/home_hero_h1/variant`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (cancelled || !data || !data.locked || !data.variant) return;
        if (!VARIANTS[data.variant]) return;
        if (data.variant !== variantKey) {
          try { localStorage.setItem('plume_hero_variant', data.variant); } catch { /* noop */ }
          setVariantKey(data.variant);
        }
      })
      .catch(() => { /* noop */ });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const copy = VARIANTS[variantKey];

  // Track `shown` once on mount + `cta_click` sur bouton principal.
  React.useEffect(() => {
    try {
      import('../lib/abTracking').then(({ trackABEvent }) => {
        trackABEvent('home_hero_h1', variantKey, 'shown');
      });
    } catch { /* noop */ }
  }, [variantKey]);

  const onPrimaryClick = () => {
    try {
      import('../lib/abTracking').then(({ trackABEvent }) => {
        trackABEvent('home_hero_h1', variantKey, 'cta_click', { destination: 'theme-natal' });
      });
    } catch { /* noop */ }
    if (onStart) onStart();
  };

  return <section className="pa-book-hero" aria-labelledby="pa-book-title" data-ab-variant={variantKey}>
    <div className="pa-book-hero__copy">
      <p className="pa-book-eyebrow"><span aria-hidden="true">✦</span> {copy.eyebrow}</p>
      <h1 id="pa-book-title" dangerouslySetInnerHTML={{ __html: copy.titleHtml }} />
      <p className="pa-book-lead">{copy.lead}</p>
      <div className="pa-book-actions">
        {onStart ? <button type="button" className="pa-book-button" onClick={onPrimaryClick}>Créer mon livre astral{price ? ` — ${price} €` : ''}<span aria-hidden="true">↗</span></button> : <Link className="pa-book-button" to="/theme-natal" data-testid="home-gateway-primary-cta" onClick={onPrimaryClick}>Créer mon livre astral <span aria-hidden="true">↗</span></Link>}
        <a className="pa-book-text-link" href={onStart ? '#pa-book-discover' : '#home-gateway-services'}>{onStart ? 'Explorer les éditions' : 'Explorer les services'} <span aria-hidden="true">↓</span></a>
      </div>
      <ul className="pa-book-details" aria-label="Votre expérience"><li>Une lecture personnelle</li><li>PDF et éditions papier à découvrir</li></ul>
    </div>
    <AstralBookVideo />
  </section>;
}

export function AstralPathways() {
  const paths = [['01', 'Me comprendre', 'Explorer mes besoins, mes élans et ma façon d’avancer.', '/theme-natal'], ['02', 'Comprendre mes relations', 'Mettre en perspective la rencontre de deux ciels.', '/synastrie'], ['03', 'Explorer mes cycles', 'Découvrir une autre lecture de mon chemin et de mes rythmes.', '/numerologie-pdf']];
  return <section className="pa-book-pathways" aria-labelledby="pa-pathways-title"><p className="pa-book-eyebrow">PAR OÙ COMMENCER ?</p><h2 id="pa-pathways-title">Ce qui vous amène ici.</h2><div>{paths.map(([number,title,description,to]) => <Link key={number} to={to}><span>{number}</span><h3>{title}</h3><p>{description}</p><span className="pa-pathways-arrow" aria-hidden="true">↗</span></Link>)}</div></section>;
}

export function AstralBookDiscovery() {
  return <section id="pa-book-discover" className="pa-book-discover" aria-labelledby="pa-book-discover-title"><header><p className="pa-book-eyebrow">À CHAQUE LECTURE, SA PLACE</p><h2 id="pa-book-discover-title">À lire aujourd’hui.<br /><em>À retrouver demain.</em></h2><p>Découvrez les options et le contenu de chaque édition avant de choisir.</p></header><div className="pa-book-editions"><article><span>01 / LIRE</span><h3>L’édition numérique</h3><p>Votre lecture personnelle en PDF, à parcourir sur votre ordinateur ou votre tablette.</p><Link to="/theme-natal">Découvrir le PDF ↗</Link></article><article><span>02 / CONSERVER</span><h3>Le livre imprimé</h3><p>Le plaisir du papier et d’une couverture à votre prénom. Découvrez les éditions brochée et reliée.</p><Link to="/composer?edition=brochee">Explorer les éditions papier ↗</Link></article></div>{previewPdf && <a className="pa-book-preview-cta" href={previewPdf} target="_blank" rel="noopener noreferrer" data-testid="natal-book-preview-cta" onClick={() => trackEvent('pdf_preview_click', { cta_location: 'home_bump_discover', pdf_url: previewPdf, destination: 'natal_book_sample' })}>
  <span className="pa-book-preview-cta__icon" aria-hidden="true">
    <svg width="22" height="26" viewBox="0 0 22 26" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 1h11l6 6v16a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2Z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/>
      <path d="M14 1v6h6" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/>
      <text x="11" y="20" textAnchor="middle" fontSize="6.4" fontWeight="700" fontFamily="Inter, Arial, sans-serif" fill="currentColor" letterSpacing="0.3">PDF</text>
    </svg>
  </span>
  <span className="pa-book-preview-cta__body">
    <span className="pa-book-preview-cta__title">Feuilleter un extrait du livre</span>
    <span className="pa-book-preview-cta__meta">Aperçu PDF · 32 pages · lecture dans votre navigateur</span>
  </span>
  <span className="pa-book-preview-cta__arrow" aria-hidden="true">↗</span>
</a>}<ol className="pa-book-process"><li><h3>Votre naissance</h3><p>Renseignez vos informations et choisissez votre édition.</p></li><li><h3>Votre lecture</h3><p>Explorez votre ciel dans une démarche symbolique et personnelle.</p></li><li><h3>Votre chemin</h3><p>Revenez aux chapitres à votre rythme, avec votre liberté d’interprétation.</p></li></ol></section>;
}
