import React, { useEffect, useState, useRef } from 'react';

/**
 * FadeInEnrichedText — révèle le texte enrichi de façon progressive
 * (phrase-par-phrase avec fade-in doux) pour renforcer l'effet "IA magique".
 *
 * Props :
 *   - text : string à révéler
 *   - enabled : bool (default true) — si false, affiche tout d'un coup
 *   - speed : ms par phrase (default 180) — animation stagger
 *   - style : styles CSS supplémentaires
 *   - className : classe CSS
 *   - dataTestid : data-testid custom
 */
export const FadeInEnrichedText = ({
  text = '',
  enabled = true,
  speed = 180,
  style = {},
  className = '',
  dataTestid = 'fade-in-enriched',
}) => {
  const [visibleCount, setVisibleCount] = useState(enabled ? 0 : Infinity);
  const timerRef = useRef(null);

  // Split par phrases (garde le séparateur pour respecter la ponctuation)
  const chunks = React.useMemo(() => {
    if (!text) return [];
    // Split sur . ! ? suivis d'espace ou fin de ligne — on garde le séparateur
    const parts = text.split(/(?<=[.!?…])\s+/);
    // Aussi split sur les sauts de ligne
    const final = [];
    for (const p of parts) {
      const lines = p.split(/\n+/);
      for (const l of lines) {
        const s = l.trim();
        if (s) final.push(s);
      }
    }
    return final;
  }, [text]);

  useEffect(() => {
    if (!enabled) {
      setVisibleCount(chunks.length);
      return;
    }
    setVisibleCount(0);
    let i = 0;
    const step = () => {
      i += 1;
      setVisibleCount(i);
      if (i < chunks.length) {
        timerRef.current = setTimeout(step, speed);
      }
    };
    if (chunks.length > 0) timerRef.current = setTimeout(step, 80);
    return () => timerRef.current && clearTimeout(timerRef.current);
  }, [chunks, enabled, speed]);

  return (
    <div className={className} style={style} data-testid={dataTestid}>
      {chunks.map((chunk, i) => {
        const shown = i < visibleCount;
        // Détecte si dernière phrase termine par ?
        const isQuestion = i === chunks.length - 1 && chunk.trim().endsWith('?');
        return (
          <span
            key={i}
            data-testid={`fade-chunk-${i}`}
            style={{
              display: 'inline',
              opacity: shown ? 1 : 0,
              transform: shown ? 'translateY(0)' : 'translateY(6px)',
              transition: 'opacity 0.6s ease-out, transform 0.6s ease-out',
              // La question finale se démarque légèrement
              color: isQuestion ? '#D4AF37' : undefined,
              fontStyle: isQuestion ? 'italic' : undefined,
            }}
          >
            {chunk}{i < chunks.length - 1 ? ' ' : ''}
          </span>
        );
      })}
    </div>
  );
};

export default FadeInEnrichedText;
