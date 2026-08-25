import React from 'react';

/**
 * Mise en scène éditoriale d'un véritable livre imprimé.
 *
 * L'illustration existante reste l'œuvre principale de la couverture. Les
 * volumes, la reliure, les pages et la lumière sont construits en CSS afin de
 * conserver des titres parfaitement lisibles et un rendu net à toute taille.
 */
export default function PhysicalBookScene({ book, coverSrc }) {
  const sceneStyle = {
    '--book-accent': book.accent,
    '--book-accent-soft': book.accentSoft,
    '--book-tilt': book.tilt,
  };

  return (
    <figure
      className="pa-book-scene"
      style={sceneStyle}
      role="img"
      aria-label={`Livre imprimé personnalisé « ${book.title} », ouvert sur une page intérieure`}
    >
      <span className="pa-book-scene__light" aria-hidden="true" />
      <span className="pa-book-scene__candle" aria-hidden="true">
        <span className="pa-book-scene__flame" />
      </span>
      <span className="pa-book-scene__stones" aria-hidden="true">
        <i />
        <i />
        <i />
      </span>

      <span className="pa-physical-book__ground-shadow" aria-hidden="true" />

      <span className="pa-physical-book" aria-hidden="true">
        <span className="pa-physical-book__under-cover" />

        <span className="pa-physical-book__cover">
          <span className="pa-physical-book__cover-stars" />
          <img
            src={coverSrc}
            alt=""
            className="pa-physical-book__cover-art"
            loading="lazy"
            decoding="async"
            onError={(event) => {
              event.currentTarget.style.opacity = '0';
            }}
          />
          <span className="pa-physical-book__cover-shade" />
          <span className="pa-physical-book__cover-copy">
            <small>Plume Astrale</small>
            <strong>{book.title}</strong>
            <em>{book.coverLabel}</em>
          </span>
          <span className="pa-physical-book__cover-corner" />
        </span>

        <span className="pa-physical-book__spine">
          <span>{book.shortTitle}</span>
        </span>

        <span className="pa-physical-book__page-block">
          <span className="pa-physical-book__page-edge" />
          <span className="pa-physical-book__page">
            <span className="pa-physical-book__page-kicker">
              Édition personnalisée
            </span>
            <span className="pa-physical-book__zodiac">
              <i>{book.symbol}</i>
            </span>
            <strong className="pa-physical-book__page-title">
              {book.title}
            </strong>
            <span className="pa-physical-book__page-subtitle">
              {book.insideLabel}
            </span>
            <span className="pa-physical-book__page-rule" />
            <span className="pa-physical-book__text-lines">
              <i />
              <i />
              <i />
              <i />
            </span>
            <span className="pa-physical-book__folio">01</span>
          </span>
        </span>
      </span>

      <figcaption className="pa-book-scene__caption">
        Couverture reliée · papier crème · impression premium
      </figcaption>
    </figure>
  );
}
