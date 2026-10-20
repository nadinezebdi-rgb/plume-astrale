import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
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
  return <section className="pa-book-hero" aria-labelledby="pa-book-title">
    <div className="pa-book-hero__copy">
      <p className="pa-book-eyebrow"><span aria-hidden="true">✦</span> PLUME ASTRALE · VOTRE LIVRE PERSONNEL</p>
      <h1 id="pa-book-title">Votre ciel.<br /><em>Votre histoire.</em><br />En livre.</h1>
      <p className="pa-book-lead">Explorez vos élans, vos liens et vos possibilités dans une lecture de votre ciel de naissance. Un livre à parcourir, à garder et à retrouver au fil de votre vie.</p>
      <div className="pa-book-actions">
        {onStart ? <button type="button" className="pa-book-button" onClick={onStart}>Créer mon livre astral{price ? ` — ${price} €` : ''}<span aria-hidden="true">↗</span></button> : <Link className="pa-book-button" to="/theme-natal" data-testid="home-gateway-primary-cta">Créer mon livre astral <span aria-hidden="true">↗</span></Link>}
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
  return <section id="pa-book-discover" className="pa-book-discover" aria-labelledby="pa-book-discover-title"><header><p className="pa-book-eyebrow">À CHAQUE LECTURE, SA PLACE</p><h2 id="pa-book-discover-title">À lire aujourd’hui.<br /><em>À retrouver demain.</em></h2><p>Découvrez les options et le contenu de chaque édition avant de choisir.</p></header><div className="pa-book-editions"><article><span>01 / LIRE</span><h3>L’édition numérique</h3><p>Votre lecture personnelle en PDF, à parcourir sur votre ordinateur ou votre tablette.</p><Link to="/theme-natal">Découvrir le PDF ↗</Link></article><article><span>02 / CONSERVER</span><h3>Le livre imprimé</h3><p>Le plaisir du papier et d’une couverture à votre prénom. Découvrez les éditions brochée et reliée.</p><Link to="/composer?edition=brochee">Explorer les éditions papier ↗</Link></article></div>{previewPdf && <a className="pa-book-text-link pa-book-preview" href={previewPdf} target="_blank" rel="noopener noreferrer">Feuilleter un extrait réel du PDF ↗</a>}<ol className="pa-book-process"><li><h3>Votre naissance</h3><p>Renseignez vos informations et choisissez votre édition.</p></li><li><h3>Votre lecture</h3><p>Explorez votre ciel dans une démarche symbolique et personnelle.</p></li><li><h3>Votre chemin</h3><p>Revenez aux chapitres à votre rythme, avec votre liberté d’interprétation.</p></li></ol></section>;
}
