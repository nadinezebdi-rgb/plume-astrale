import React, { useEffect, useRef, useState } from 'react';
import { Sparkles } from 'lucide-react';

/**
 * PdfBookOpen — Aperçu 3D d'un livre relié qui s'ouvre au scroll.
 *
 * Justifie visuellement le prix 49€ en montrant l'objet fini (couverture cuir
 * + tranche dorée + double page intérieure) avant même le checkout.
 *
 *  ─ Fermé : couverture nuit + ornement doré, tranche 3D visible
 *  ─ Au scroll-into-view : la couverture pivote sur -160deg
 *  ─ Puis reveal des 2 pages intérieures avec une carte planétaire
 *    à gauche et un extrait "Ligne Vénus" à droite.
 *
 *  CSS 3D pur (aucune dépendance). Réagit au hover pour rouvrir/fermer.
 */

// ─────────────────────────────────────────────────────────────
// THÈMES : chaque produit a sa propre double-page intérieure + copie
// ─────────────────────────────────────────────────────────────
const API = process.env.REACT_APP_BACKEND_URL;
const IMG = (p) => `${API}/api/assets/library/${p}`;

const THEMES = {
  astrocarto: {
    label: 'Astrocartographie',
    coverTitle: 'Ton\nAstrocartographie',
    coverSignature: 'Prénom · Naissance · 18 pages sur mesure',
    coverImage: IMG('planets/jupiter_512.png'),
    heroSub: 'PDF premium, 18 pages sur ta géographie astrale. Ce que tu vois est ce que tu reçois par email.',
    footerHint: 'Passe la souris pour rouvrir · Livraison PDF instantanée · 18 pages',
  },
  kabbale: {
    label: 'Arbre de Vie',
    coverTitle: 'Ton\nArbre de Vie',
    coverSignature: 'Prénom · Naissance · 15 pages kabbalistiques',
    coverImage: IMG('tarot/17_l_etoile_512.png'),
    heroSub: 'PDF premium, 15 pages qui cartographient ton âme sur les 10 Sephiroth et 22 chemins de l\'Arbre de Vie.',
    footerHint: 'Passe la souris pour rouvrir · Livraison PDF instantanée · 15 pages',
  },
  karmique: {
    label: 'Pack Karmique',
    coverTitle: 'Ton\nPack Karmique',
    coverSignature: 'Prénom · Naissance · 40 pages sur mesure',
    coverImage: IMG('tarot/19_le_soleil_512.png'),
    heroSub: 'L\'écrin le plus profond de Plume Astrale. 40 pages qui unissent ton empreinte karmique, ton Arbre de Vie et ta synthèse d\'âme.',
    footerHint: 'Passe la souris pour rouvrir · Livraison PDF instantanée · 40 pages',
  },
  natal: {
    label: 'Thème Natal',
    coverTitle: 'Ton\nThème Natal',
    coverSignature: 'Prénom · Naissance · 49 pages sur mesure',
    coverImage: IMG('planets/sun_512.png'),
    heroSub: 'PDF premium, 49 pages où 11 planètes racontent qui tu es vraiment — 73 dimensions astrologiques analysées et écrites dans un style éditorial signé Plume Astrale.',
    footerHint: 'Passe la souris pour rouvrir · Livraison PDF instantanée · 49 pages',
  },
  synastry: {
    label: 'Astrologie relationnelle',
    coverTitle: 'Votre\nAstrologie relationnelle',
    coverSignature: 'Deux prénoms · Deux ciels · 25 pages croisées',
    coverImage: IMG('tarot/06_les_amoureux_512.png'),
    heroSub: 'L\'aspectarium de votre lien — 25 pages où vos deux ciels dansent ensemble. Aspects planétaires croisés, langages d\'amour et points de tendresse à cultiver.',
    footerHint: 'Passe la souris pour rouvrir · Livraison PDF instantanée · 25 pages',
  },
};

// ─────────────────────────────────────────────────────────────
// Intérieurs (double-page) par thème
// ─────────────────────────────────────────────────────────────
const InteriorAstrocarto = () => (
  <div className="pbo-spread" aria-hidden="true">
    <div className="pbo-page pbo-page-left">
      <div className="pbo-header">✦ CARTE DU MONDE ✦</div>
      <div className="pbo-map">
        <div className="pbo-line pbo-line-1" />
        <div className="pbo-line pbo-line-2" />
        <div className="pbo-line pbo-line-3" />
        <div className="pbo-city" style={{ top: '32%', left: '22%' }} />
        <div className="pbo-city" style={{ top: '58%', left: '52%' }} />
        <div className="pbo-city" style={{ top: '46%', left: '76%' }} />
        <div className="pbo-city-label" style={{ top: '26%', left: '20%' }}>Lisbonne</div>
        <div className="pbo-city-label" style={{ top: '52%', left: '50%' }}>Bali</div>
      </div>
      <div className="pbo-caption">Tes 7 lignes planétaires cartographiées</div>
      <div className="pbo-para" style={{ width: '92%' }} />
      <div className="pbo-para" style={{ width: '78%' }} />
      <div className="pbo-para" style={{ width: '85%' }} />
      <div className="pbo-folio">— 8 —</div>
    </div>
    <div className="pbo-page pbo-page-right">
      <div className="pbo-header">♀ &nbsp;LIGNE VÉNUS</div>
      <div className="pbo-quote">
        « Ta ligne Vénus traverse&nbsp;
        <span style={{ color: '#D4AF37', fontWeight: 500 }}>Lisbonne</span>
        &nbsp;— là où l&apos;amour s&apos;y révèle plus doux, plus vrai. »
      </div>
      <div className="pbo-para" style={{ width: '96%' }} />
      <div className="pbo-para" style={{ width: '90%' }} />
      <div className="pbo-para" style={{ width: '82%' }} />
      <div className="pbo-para" style={{ width: '92%' }} />
      <div className="pbo-para" style={{ width: '70%' }} />
      <div className="pbo-boxed">
        <div className="pbo-boxed-label">✦ Rituel de terrain</div>
        <div className="pbo-para" style={{ width: '90%', background: 'rgba(212,175,55,0.55)' }} />
        <div className="pbo-para" style={{ width: '78%', background: 'rgba(212,175,55,0.45)' }} />
      </div>
      <div className="pbo-folio">— 9 —</div>
    </div>
  </div>
);

const InteriorKabbale = () => (
  <div className="pbo-spread" aria-hidden="true">
    {/* PAGE GAUCHE : Arbre de Vie miniature */}
    <div className="pbo-page pbo-page-left">
      <div className="pbo-header">✦ TON ARBRE DE VIE ✦</div>
      <div className="pbo-tree">
        {/* 10 Sephiroth positionnées */}
        <div className="pbo-seph pbo-seph-1" title="Kether" />
        <div className="pbo-seph pbo-seph-2" title="Chokmah" />
        <div className="pbo-seph pbo-seph-3" title="Binah" />
        <div className="pbo-seph pbo-seph-4" title="Chesed" />
        <div className="pbo-seph pbo-seph-5" title="Geburah" />
        <div className="pbo-seph pbo-seph-6" title="Tiphareth" />
        <div className="pbo-seph pbo-seph-7" title="Netzach" />
        <div className="pbo-seph pbo-seph-8" title="Hod" />
        <div className="pbo-seph pbo-seph-9" title="Yesod" />
        <div className="pbo-seph pbo-seph-10" title="Malkuth" />
        {/* Quelques chemins */}
        <svg className="pbo-tree-paths" viewBox="0 0 100 130" preserveAspectRatio="none" aria-hidden="true">
          <line x1="50" y1="12" x2="20" y2="30" /><line x1="50" y1="12" x2="80" y2="30" />
          <line x1="20" y1="30" x2="80" y2="30" /><line x1="20" y1="30" x2="20" y2="55" />
          <line x1="80" y1="30" x2="80" y2="55" /><line x1="20" y1="55" x2="50" y2="70" />
          <line x1="80" y1="55" x2="50" y2="70" /><line x1="50" y1="70" x2="20" y2="90" />
          <line x1="50" y1="70" x2="80" y2="90" /><line x1="20" y1="90" x2="80" y2="90" />
          <line x1="20" y1="90" x2="50" y2="110" /><line x1="80" y1="90" x2="50" y2="110" />
          <line x1="50" y1="110" x2="50" y2="125" />
        </svg>
      </div>
      <div className="pbo-caption">Tes 10 Sephiroth · Tes 22 chemins</div>
      <div className="pbo-para" style={{ width: '92%' }} />
      <div className="pbo-para" style={{ width: '80%' }} />
      <div className="pbo-folio">— 6 —</div>
    </div>
    {/* PAGE DROITE : Sephira dominante */}
    <div className="pbo-page pbo-page-right">
      <div className="pbo-header">✡  TIPHARETH · BEAUTÉ</div>
      <div className="pbo-quote">
        « Ta Sephira dominante est&nbsp;
        <span style={{ color: '#D4AF37', fontWeight: 500 }}>Tiphareth</span>
        &nbsp;— le cœur du Christ intérieur, la lumière qui rayonne sans forcer. »
      </div>
      <div className="pbo-para" style={{ width: '96%' }} />
      <div className="pbo-para" style={{ width: '88%' }} />
      <div className="pbo-para" style={{ width: '82%' }} />
      <div className="pbo-para" style={{ width: '92%' }} />
      <div className="pbo-boxed">
        <div className="pbo-boxed-label">✦ Ton axe d&apos;âme</div>
        <div className="pbo-para" style={{ width: '90%', background: 'rgba(212,175,55,0.55)' }} />
        <div className="pbo-para" style={{ width: '76%', background: 'rgba(212,175,55,0.45)' }} />
      </div>
      <div className="pbo-folio">— 7 —</div>
    </div>
  </div>
);

const InteriorKarmique = () => (
  <div className="pbo-spread" aria-hidden="true">
    {/* PAGE GAUCHE : Nœuds Lunaires axis */}
    <div className="pbo-page pbo-page-left">
      <div className="pbo-header">☊ &nbsp;NŒUDS LUNAIRES</div>
      <div className="pbo-karma">
        {/* Roue zodiacale simplifiée */}
        <div className="pbo-karma-wheel">
          <div className="pbo-karma-axis" />
          <div className="pbo-karma-node pbo-karma-node-n">☊</div>
          <div className="pbo-karma-node pbo-karma-node-s">☋</div>
          <div className="pbo-karma-glyph pbo-karma-glyph-1">♌</div>
          <div className="pbo-karma-glyph pbo-karma-glyph-2">♒</div>
          <div className="pbo-karma-glyph pbo-karma-glyph-3">♎</div>
          <div className="pbo-karma-glyph pbo-karma-glyph-4">♈</div>
        </div>
      </div>
      <div className="pbo-caption">Nœud Nord Lion · Nœud Sud Verseau</div>
      <div className="pbo-para" style={{ width: '92%' }} />
      <div className="pbo-para" style={{ width: '78%' }} />
      <div className="pbo-para" style={{ width: '85%' }} />
      <div className="pbo-folio">— 14 —</div>
    </div>
    {/* PAGE DROITE : Mission d'âme */}
    <div className="pbo-page pbo-page-right">
      <div className="pbo-header">✦ TA MISSION D&apos;ÂME ✦</div>
      <div className="pbo-quote">
        « Tu es venue pour&nbsp;
        <span style={{ color: '#D4AF37', fontWeight: 500 }}>oser briller</span>
        &nbsp;— quitter la fuite collective pour incarner ton feu solaire personnel. »
      </div>
      <div className="pbo-para" style={{ width: '96%' }} />
      <div className="pbo-para" style={{ width: '90%' }} />
      <div className="pbo-para" style={{ width: '84%' }} />
      <div className="pbo-para" style={{ width: '92%' }} />
      <div className="pbo-para" style={{ width: '78%' }} />
      <div className="pbo-boxed">
        <div className="pbo-boxed-label">✦ Pratique d&apos;intégration</div>
        <div className="pbo-para" style={{ width: '90%', background: 'rgba(212,175,55,0.55)' }} />
        <div className="pbo-para" style={{ width: '78%', background: 'rgba(212,175,55,0.45)' }} />
      </div>
      <div className="pbo-folio">— 15 —</div>
    </div>
  </div>
);

const InteriorNatal = () => (
  <div className="pbo-spread" aria-hidden="true">
    {/* PAGE GAUCHE : Roue astro miniature avec 11 planètes */}
    <div className="pbo-page pbo-page-left">
      <div className="pbo-header">✦ TA ROUE NATALE ✦</div>
      <div className="pbo-natal-wheel">
        <div className="pbo-natal-ring" />
        <div className="pbo-natal-cross-h" />
        <div className="pbo-natal-cross-v" />
        {/* 12 signes autour de la roue */}
        {['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓'].map((s, i) => {
          const angle = (i * 30) - 90;
          const rad = (angle * Math.PI) / 180;
          const r = 46;
          const cx = 50 + r * Math.cos(rad);
          const cy = 50 + r * Math.sin(rad);
          return (
            <div key={i} className="pbo-natal-sign" style={{ left: `${cx}%`, top: `${cy}%` }}>{s}</div>
          );
        })}
        {/* Planètes disposées dans la roue */}
        <div className="pbo-natal-planet" style={{ top: '32%', left: '68%' }}>☉</div>
        <div className="pbo-natal-planet" style={{ top: '62%', left: '30%' }}>☽</div>
        <div className="pbo-natal-planet" style={{ top: '48%', left: '78%' }}>☿</div>
        <div className="pbo-natal-planet" style={{ top: '25%', left: '50%' }}>♀</div>
        <div className="pbo-natal-planet" style={{ top: '75%', left: '55%' }}>♂</div>
        <div className="pbo-natal-planet" style={{ top: '40%', left: '25%' }}>♃</div>
        <div className="pbo-natal-planet" style={{ top: '58%', left: '70%' }}>♄</div>
      </div>
      <div className="pbo-caption">11 planètes lues, 73 interprétations synthétisées</div>
      <div className="pbo-para" style={{ width: '92%' }} />
      <div className="pbo-para" style={{ width: '80%' }} />
      <div className="pbo-folio">— 12 —</div>
    </div>
    {/* PAGE DROITE : Extrait Soleil */}
    <div className="pbo-page pbo-page-right">
      <div className="pbo-header">☉ &nbsp;TON SOLEIL EN GÉMEAUX</div>
      <div className="pbo-quote">
        « Chez toi, l&apos;identité se fabrique en marchant, en parlant jusqu&apos;à faire tomber les&nbsp;
        <span style={{ color: '#D4AF37', fontWeight: 500 }}>masques d&apos;une idée</span>. »
      </div>
      <div className="pbo-para" style={{ width: '96%' }} />
      <div className="pbo-para" style={{ width: '90%' }} />
      <div className="pbo-para" style={{ width: '84%' }} />
      <div className="pbo-para" style={{ width: '92%' }} />
      <div className="pbo-para" style={{ width: '76%' }} />
      <div className="pbo-boxed">
        <div className="pbo-boxed-label">✦ Dialogue de Soléna</div>
        <div className="pbo-para" style={{ width: '90%', background: 'rgba(212,175,55,0.55)' }} />
        <div className="pbo-para" style={{ width: '78%', background: 'rgba(212,175,55,0.45)' }} />
      </div>
      <div className="pbo-folio">— 13 —</div>
    </div>
  </div>
);

const InteriorSynastry = () => (
  <div className="pbo-spread" aria-hidden="true">
    {/* PAGE GAUCHE : 2 cercles zodiacaux entrelacés */}
    <div className="pbo-page pbo-page-left">
      <div className="pbo-header">♀ &nbsp;VOS DEUX CIELS ✦ ♂</div>
      <div className="pbo-syn-duo">
        <div className="pbo-syn-wheel pbo-syn-wheel-a" />
        <div className="pbo-syn-wheel pbo-syn-wheel-b" />
        <div className="pbo-syn-heart">✧</div>
        <div className="pbo-syn-glyph pbo-syn-glyph-l">♀</div>
        <div className="pbo-syn-glyph pbo-syn-glyph-r">♂</div>
      </div>
      <div className="pbo-caption">Vos aspects planétaires croisés, dans les deux sens</div>
      <div className="pbo-para" style={{ width: '92%' }} />
      <div className="pbo-para" style={{ width: '80%' }} />
      <div className="pbo-para" style={{ width: '85%' }} />
      <div className="pbo-folio">— 10 —</div>
    </div>
    {/* PAGE DROITE : Aspect central */}
    <div className="pbo-page pbo-page-right">
      <div className="pbo-header">✦ VOTRE LIEN D&apos;ÂME ✦</div>
      <div className="pbo-quote">
        « Sa Vénus enveloppe votre Lune —&nbsp;
        <span style={{ color: '#D4AF37', fontWeight: 500 }}>quand il/elle parle</span>, quelque chose en vous se souvient d&apos;être aimée. »
      </div>
      <div className="pbo-para" style={{ width: '96%' }} />
      <div className="pbo-para" style={{ width: '90%' }} />
      <div className="pbo-para" style={{ width: '82%' }} />
      <div className="pbo-para" style={{ width: '92%' }} />
      <div className="pbo-boxed">
        <div className="pbo-boxed-label">✦ Point de tendresse</div>
        <div className="pbo-para" style={{ width: '90%', background: 'rgba(212,175,55,0.55)' }} />
        <div className="pbo-para" style={{ width: '78%', background: 'rgba(212,175,55,0.45)' }} />
      </div>
      <div className="pbo-folio">— 11 —</div>
    </div>
  </div>
);

const INTERIORS = {
  astrocarto: InteriorAstrocarto,
  kabbale: InteriorKabbale,
  karmique: InteriorKarmique,
  natal: InteriorNatal,
  synastry: InteriorSynastry,
};

const BookCover = ({ theme }) => {
  const t = THEMES[theme] || THEMES.astrocarto;
  const [line1, line2] = t.coverTitle.split('\n');
  return (
    <div className="pbo-cover-face" aria-hidden="true">
      <div className="pbo-cover-frame" />
      <div className="pbo-cover-flourish">✦</div>
      <div className="pbo-cover-title">{line1}<br/>{line2}</div>
      <div className="pbo-cover-sub">✦ Édition Plume Astrale ✦</div>
      <div className="pbo-cover-medallion">
        {t.coverImage ? (
          <img
            src={t.coverImage}
            alt=""
            className="pbo-cover-medallion-img"
            style={{
              position: 'absolute', inset: 0,
              width: '100%', height: '100%', objectFit: 'contain',
              borderRadius: '50%',
              opacity: 0.92,
              filter: 'drop-shadow(0 0 12px rgba(212,175,55,0.35))',
            }}
            loading="lazy"
          />
        ) : (
          <>
            <div className="pbo-cover-medallion-inner" />
            <div className="pbo-cover-cross-h" />
            <div className="pbo-cover-cross-v" />
          </>
        )}
      </div>
      <div className="pbo-cover-signature">{t.coverSignature}</div>
      <div className="pbo-cover-flourish pbo-cover-flourish-bot">✦</div>
    </div>
  );
};

const PdfBookOpen = ({ testId = 'pdf-book-open', theme = 'astrocarto' }) => {
  const stageRef = useRef(null);
  const [open, setOpen] = useState(false);
  const t = THEMES[theme] || THEMES.astrocarto;
  const Interior = INTERIORS[theme] || INTERIORS.astrocarto;

  // Ouvre le livre quand il apparaît dans le viewport
  useEffect(() => {
    if (!stageRef.current) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            setTimeout(() => setOpen(true), 550);
            io.disconnect();
          }
        });
      },
      { threshold: 0.4 }
    );
    io.observe(stageRef.current);
    return () => io.disconnect();
  }, []);

  return (
    <section className="mb-16" data-testid={testId}>
      <div className="text-center mb-8">
        <p
          className="text-[10px] uppercase mb-3"
          style={{
            color: '#D4AF37',
            letterSpacing: '0.35em',
            fontFamily: 'Cinzel, serif',
          }}
        >
          ✦ Aperçu du livre ✦
        </p>
        <h2
          style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 300,
            fontSize: 'clamp(26px, 3.2vw, 36px)',
            color: '#F5EEE0',
            marginBottom: 6,
            lineHeight: 1.15,
          }}
        >
          Regarde{' '}
          <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>
            ton exemplaire s&apos;ouvrir
          </em>
        </h2>
        <p
          className="text-sm max-w-xl mx-auto"
          style={{
            color: 'rgba(227,215,255,0.68)',
            fontFamily: 'Cormorant Garamond, serif',
            fontStyle: 'italic',
          }}
        >
          {t.heroSub}
        </p>
      </div>

      <div
        ref={stageRef}
        className={`pbo-stage ${open ? 'is-open' : ''}`}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onClick={() => setOpen((v) => !v)}
        data-testid={`${testId}-stage`}
        role="button"
        tabIndex={0}
        aria-label="Aperçu animé du livre — cliquer pour ouvrir/fermer"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') setOpen((v) => !v);
        }}
      >
        {/* Ombre au sol */}
        <div className="pbo-shadow" />

        <div className="pbo-book">
          {/* Pages intérieures visibles quand ouvert */}
          <Interior />

          {/* Couverture (pivote) */}
          <div className="pbo-cover">
            <BookCover theme={theme} />
            <div className="pbo-cover-back" aria-hidden="true">
              <div className="pbo-cover-back-inner" />
            </div>
          </div>

          <div className="pbo-spine" aria-hidden="true" />
        </div>
      </div>

      <div
        className="text-center mt-6 text-[11px]"
        style={{
          color: 'rgba(212,175,55,0.75)',
          letterSpacing: '0.18em',
          fontFamily: 'Cinzel, serif',
        }}
      >
        <Sparkles className="w-3 h-3 inline mr-1.5" />
        {t.footerHint}
      </div>

      <style>{`
        .pbo-stage {
          position: relative;
          max-width: 880px;
          margin: 0 auto;
          padding: 32px 0 24px;
          perspective: 2400px;
          perspective-origin: 50% 30%;
          cursor: pointer;
          user-select: none;
        }
        .pbo-shadow {
          position: absolute;
          left: 50%;
          bottom: 6px;
          width: 60%;
          height: 24px;
          transform: translateX(-50%);
          background: radial-gradient(ellipse at center, rgba(0,0,0,0.55) 0%, transparent 70%);
          filter: blur(6px);
          transition: width 1.1s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.6s;
        }
        .pbo-stage.is-open .pbo-shadow {
          width: 82%;
          opacity: 0.85;
        }

        .pbo-book {
          position: relative;
          width: min(88vw, 720px);
          aspect-ratio: 1.42 / 1;
          margin: 0 auto;
          transform-style: preserve-3d;
          transition: transform 1.1s cubic-bezier(0.22, 1, 0.36, 1);
          transform: rotateX(6deg) rotateY(-4deg);
        }
        .pbo-stage.is-open .pbo-book {
          transform: rotateX(8deg) rotateY(0deg);
        }

        /* ── Tranche dorée ─────────────────────────── */
        .pbo-spine {
          position: absolute;
          left: 50%;
          top: 2%;
          width: 10px;
          height: 96%;
          transform: translateX(-50%) translateZ(1px);
          background: linear-gradient(180deg,
            #8a6d1a 0%, #D4AF37 20%, #f5e19a 50%, #D4AF37 80%, #6d5514 100%);
          box-shadow: inset 0 0 6px rgba(0,0,0,0.55);
          border-radius: 2px;
          z-index: 3;
        }

        /* ── Double page intérieure ────────────────── */
        .pbo-spread {
          position: absolute;
          inset: 0;
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 0;
          border-radius: 4px;
          overflow: hidden;
          box-shadow:
            inset 0 0 60px rgba(0,0,0,0.6),
            0 30px 80px -30px rgba(0,0,0,0.7);
        }
        .pbo-page {
          position: relative;
          background:
            linear-gradient(180deg, rgba(255,255,255,0.02), rgba(0,0,0,0.15)),
            linear-gradient(160deg, #0F1A3C 0%, #0e0a1e 100%);
          padding: 26px 30px 30px;
          font-family: 'Cormorant Garamond', serif;
          color: #F5EEE0;
          overflow: hidden;
        }
        .pbo-page-left {
          border-right: 1px solid rgba(212,175,55,0.35);
          background:
            radial-gradient(circle at 100% 50%, rgba(0,0,0,0.4), transparent 40%),
            linear-gradient(160deg, #0F1A3C 0%, #0e0a1e 100%);
        }
        .pbo-page-right {
          background:
            radial-gradient(circle at 0% 50%, rgba(0,0,0,0.4), transparent 40%),
            linear-gradient(200deg, #0F1A3C 0%, #0e0a1e 100%);
        }

        .pbo-header {
          font-family: 'Cinzel', serif;
          font-size: 10px;
          color: #D4AF37;
          letter-spacing: 0.32em;
          text-align: center;
          margin-bottom: 14px;
          padding-bottom: 8px;
          border-bottom: 1px solid rgba(212,175,55,0.28);
        }
        .pbo-map {
          position: relative;
          height: 120px;
          margin-bottom: 12px;
          border: 1px solid rgba(212,175,55,0.25);
          border-radius: 3px;
          background:
            radial-gradient(ellipse at 25% 45%, rgba(212,175,55,0.14), transparent 55%),
            radial-gradient(ellipse at 72% 60%, rgba(167,139,250,0.18), transparent 55%);
        }
        .pbo-line {
          position: absolute;
          left: 6%;
          right: 6%;
          height: 1px;
          background: linear-gradient(90deg, transparent, #E8C766, transparent);
          filter: drop-shadow(0 0 3px rgba(212,175,55,0.6));
        }
        .pbo-line-1 { top: 30%; transform: rotate(-8deg); }
        .pbo-line-2 { top: 55%; transform: rotate(11deg);
          background: linear-gradient(90deg, transparent, #A78BFA, transparent); }
        .pbo-line-3 { top: 72%; transform: rotate(-4deg); }
        .pbo-city {
          position: absolute;
          width: 5px;
          height: 5px;
          border-radius: 50%;
          background: #D4AF37;
          box-shadow: 0 0 8px rgba(212,175,55,0.9);
        }
        .pbo-city-label {
          position: absolute;
          font-family: 'Cinzel', serif;
          font-size: 8px;
          letter-spacing: 0.15em;
          color: rgba(245,238,224,0.75);
        }

        /* ─ Arbre de Vie (thème kabbale) ─ */
        .pbo-tree {
          position: relative;
          height: 145px;
          margin-bottom: 10px;
          border: 1px solid rgba(212,175,55,0.22);
          border-radius: 3px;
          background:
            radial-gradient(ellipse at 50% 50%, rgba(212,175,55,0.10), transparent 60%);
        }
        .pbo-tree-paths {
          position: absolute; inset: 0; width: 100%; height: 100%;
          stroke: rgba(212,175,55,0.55); stroke-width: 0.4; fill: none;
        }
        .pbo-seph {
          position: absolute; width: 12px; height: 12px; border-radius: 50%;
          background: radial-gradient(circle at 30% 30%, #F5E19A, #D4AF37 60%, #8a6d1a 100%);
          box-shadow: 0 0 8px rgba(212,175,55,0.7);
          transform: translate(-50%, -50%);
        }
        .pbo-seph-1 { top: 9%; left: 50%; }   /* Kether */
        .pbo-seph-2 { top: 23%; left: 80%; }  /* Chokmah */
        .pbo-seph-3 { top: 23%; left: 20%; }  /* Binah */
        .pbo-seph-4 { top: 42%; left: 80%; }  /* Chesed */
        .pbo-seph-5 { top: 42%; left: 20%; }  /* Geburah */
        .pbo-seph-6 { top: 54%; left: 50%;    /* Tiphareth — plus brillant */
          width: 15px; height: 15px;
          box-shadow: 0 0 14px rgba(212,175,55,1); }
        .pbo-seph-7 { top: 70%; left: 80%; }  /* Netzach */
        .pbo-seph-8 { top: 70%; left: 20%; }  /* Hod */
        .pbo-seph-9 { top: 82%; left: 50%; }  /* Yesod */
        .pbo-seph-10 { top: 95%; left: 50%; } /* Malkuth */

        /* ─ Roue karmique (thème karmique) ─ */
        .pbo-karma {
          position: relative;
          height: 140px;
          margin-bottom: 10px;
          border: 1px solid rgba(212,175,55,0.22);
          border-radius: 3px;
          background: radial-gradient(ellipse at 50% 50%, rgba(212,175,55,0.08), transparent 70%);
        }
        .pbo-karma-wheel {
          position: absolute; inset: 8px;
          border: 1px solid rgba(212,175,55,0.5);
          border-radius: 50%;
        }
        .pbo-karma-wheel::before {
          content: '';
          position: absolute; inset: 8px;
          border: 1px solid rgba(212,175,55,0.25);
          border-radius: 50%;
        }
        .pbo-karma-axis {
          position: absolute; top: 8%; bottom: 8%; left: 50%;
          width: 1px;
          background: linear-gradient(180deg,
            rgba(212,175,55,0.05), #D4AF37 20%, #D4AF37 80%, rgba(212,175,55,0.05));
          transform: translateX(-50%) rotate(28deg);
          transform-origin: center;
          filter: drop-shadow(0 0 3px rgba(212,175,55,0.7));
        }
        .pbo-karma-node {
          position: absolute;
          font-family: 'Cinzel', serif;
          font-size: 14px;
          color: #D4AF37;
          text-shadow: 0 0 6px rgba(212,175,55,0.8);
        }
        .pbo-karma-node-n { top: 8%; left: 68%; }
        .pbo-karma-node-s { bottom: 8%; left: 22%; }
        .pbo-karma-glyph {
          position: absolute;
          font-family: 'Cinzel', serif;
          font-size: 11px;
          color: rgba(245,238,224,0.6);
        }
        .pbo-karma-glyph-1 { top: 50%; right: -2px; transform: translateY(-50%); }
        .pbo-karma-glyph-2 { top: 50%; left: -2px; transform: translateY(-50%); }
        .pbo-karma-glyph-3 { top: -2px; left: 50%; transform: translateX(-50%); }
        .pbo-karma-glyph-4 { bottom: -2px; left: 50%; transform: translateX(-50%); }

        /* ─ Roue natale (thème natal) ─ */
        .pbo-natal-wheel {
          position: relative;
          height: 155px;
          margin-bottom: 10px;
          border: 1px solid rgba(212,175,55,0.22);
          border-radius: 3px;
          background: radial-gradient(ellipse at 50% 50%, rgba(212,175,55,0.09), transparent 65%);
        }
        .pbo-natal-ring {
          position: absolute; inset: 6px;
          border: 1px solid rgba(212,175,55,0.5);
          border-radius: 50%;
        }
        .pbo-natal-ring::before {
          content: '';
          position: absolute; inset: 10px;
          border: 1px solid rgba(212,175,55,0.22);
          border-radius: 50%;
        }
        .pbo-natal-cross-h,
        .pbo-natal-cross-v {
          position: absolute;
          background: rgba(212,175,55,0.28);
        }
        .pbo-natal-cross-h { top: 50%; left: 15%; right: 15%; height: 1px; }
        .pbo-natal-cross-v { left: 50%; top: 15%; bottom: 15%; width: 1px; }
        .pbo-natal-sign {
          position: absolute;
          transform: translate(-50%, -50%);
          font-family: 'Cinzel', serif;
          font-size: 9px;
          color: rgba(245,238,224,0.55);
        }
        .pbo-natal-planet {
          position: absolute;
          transform: translate(-50%, -50%);
          font-size: 12px;
          color: #D4AF37;
          text-shadow: 0 0 8px rgba(212,175,55,0.9);
          font-family: 'Cinzel', serif;
        }

        /* ─ Astrologie relationnelle (deux cercles entrelacés) ─ */
        .pbo-syn-duo {
          position: relative;
          height: 145px;
          margin-bottom: 10px;
          border: 1px solid rgba(212,175,55,0.22);
          border-radius: 3px;
          background: radial-gradient(ellipse at 50% 50%, rgba(212,175,55,0.10), transparent 70%);
        }
        .pbo-syn-wheel {
          position: absolute;
          width: 95px; height: 95px;
          top: 20px;
          border-radius: 50%;
          border: 1.5px solid rgba(212,175,55,0.6);
          box-shadow: 0 0 12px rgba(212,175,55,0.15);
        }
        .pbo-syn-wheel::before {
          content: '';
          position: absolute; inset: 6px;
          border: 1px solid rgba(212,175,55,0.28);
          border-radius: 50%;
        }
        .pbo-syn-wheel-a { left: 25%; }
        .pbo-syn-wheel-b { right: 25%; }
        .pbo-syn-heart {
          position: absolute;
          top: 50%; left: 50%;
          transform: translate(-50%, -50%);
          font-family: 'Cinzel', serif;
          font-size: 24px;
          color: #F5EEE0;
          text-shadow: 0 0 14px rgba(212,175,55,0.9);
        }
        .pbo-syn-glyph {
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
          font-family: 'Cinzel', serif;
          font-size: 20px;
          color: #D4AF37;
          text-shadow: 0 0 8px rgba(212,175,55,0.6);
        }
        .pbo-syn-glyph-l { left: calc(25% + 47.5px - 10px); transform: translate(-50%, -50%); top: calc(20px + 47.5px); }
        .pbo-syn-glyph-r { right: calc(25% + 47.5px - 10px); transform: translate(50%, -50%); top: calc(20px + 47.5px); }

        .pbo-caption {
          font-style: italic;
          font-size: 11px;
          text-align: center;
          color: rgba(227,215,255,0.6);
          margin-bottom: 14px;
        }
        .pbo-para {
          height: 6px;
          background: rgba(245,238,224,0.28);
          border-radius: 2px;
          margin-bottom: 6px;
          filter: blur(0.4px);
        }
        .pbo-quote {
          font-family: 'Cormorant Garamond', serif;
          font-style: italic;
          font-size: 15px;
          line-height: 1.4;
          color: #F5EEE0;
          margin-bottom: 14px;
          padding-left: 10px;
          border-left: 2px solid rgba(212,175,55,0.6);
        }
        .pbo-boxed {
          margin-top: 14px;
          padding: 10px 12px;
          border: 1px solid rgba(212,175,55,0.55);
          border-radius: 3px;
          background: rgba(212,175,55,0.06);
        }
        .pbo-boxed-label {
          font-family: 'Cinzel', serif;
          font-size: 9px;
          letter-spacing: 0.24em;
          color: #D4AF37;
          margin-bottom: 6px;
        }
        .pbo-folio {
          position: absolute;
          bottom: 10px;
          left: 0;
          right: 0;
          text-align: center;
          font-family: 'Cinzel', serif;
          font-size: 9px;
          letter-spacing: 0.3em;
          color: rgba(212,175,55,0.55);
        }

        /* ── Couverture qui pivote ─────────────────── */
        .pbo-cover {
          position: absolute;
          top: 0;
          left: 0;
          width: 50%;
          height: 100%;
          transform-origin: right center;
          transform-style: preserve-3d;
          transform: rotateY(0deg);
          transition: transform 1.4s cubic-bezier(0.7, 0, 0.3, 1);
          z-index: 4;
          box-shadow: 0 30px 60px -20px rgba(0,0,0,0.8);
        }
        .pbo-stage.is-open .pbo-cover {
          transform: rotateY(-168deg);
        }

        .pbo-cover-face,
        .pbo-cover-back {
          position: absolute;
          inset: 0;
          border-radius: 4px 0 0 4px;
          backface-visibility: hidden;
        }

        /* Recto (visible fermé) : cuir nuit + dorures */
        .pbo-cover-face {
          background:
            radial-gradient(circle at 30% 20%, rgba(212,175,55,0.08), transparent 50%),
            radial-gradient(circle at 70% 80%, rgba(167,139,250,0.06), transparent 55%),
            linear-gradient(150deg, #0F1A3C 0%, #0F1A3C 55%, #06040f 100%);
          padding: 28px 24px;
          overflow: hidden;
          border: 1px solid rgba(212,175,55,0.4);
        }
        .pbo-cover-frame {
          position: absolute;
          inset: 12px;
          border: 1px solid rgba(212,175,55,0.55);
          border-radius: 3px;
          box-shadow:
            inset 0 0 30px rgba(212,175,55,0.08),
            inset 0 0 0 3px transparent;
        }
        .pbo-cover-flourish {
          position: absolute;
          top: 32px;
          left: 0;
          right: 0;
          text-align: center;
          font-family: 'Cinzel', serif;
          font-size: 20px;
          color: #D4AF37;
          letter-spacing: 0.4em;
          text-shadow: 0 0 12px rgba(212,175,55,0.5);
        }
        .pbo-cover-flourish-bot {
          top: auto;
          bottom: 32px;
        }
        .pbo-cover-title {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -110%);
          font-family: 'Cormorant Garamond', serif;
          font-weight: 300;
          font-style: italic;
          font-size: clamp(20px, 3.4vw, 32px);
          line-height: 1.05;
          color: #F5EEE0;
          text-align: center;
          letter-spacing: 0.02em;
          text-shadow: 0 2px 20px rgba(0,0,0,0.6);
          width: 90%;
        }
        .pbo-cover-sub {
          position: absolute;
          top: 50%;
          left: 0;
          right: 0;
          transform: translateY(70%);
          text-align: center;
          font-family: 'Cinzel', serif;
          font-size: 10px;
          color: rgba(212,175,55,0.85);
          letter-spacing: 0.32em;
        }
        .pbo-cover-medallion {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 92px;
          height: 92px;
          border-radius: 50%;
          border: 1px solid rgba(212,175,55,0.6);
          box-shadow: 0 0 20px rgba(212,175,55,0.15);
        }
        .pbo-cover-medallion-inner {
          position: absolute;
          inset: 10px;
          border-radius: 50%;
          border: 1px solid rgba(212,175,55,0.35);
        }
        .pbo-cover-cross-h,
        .pbo-cover-cross-v {
          position: absolute;
          background: rgba(212,175,55,0.5);
        }
        .pbo-cover-cross-h { top: 50%; left: 8%; right: 8%; height: 1px; }
        .pbo-cover-cross-v { left: 50%; top: 8%; bottom: 8%; width: 1px; }

        .pbo-cover-signature {
          position: absolute;
          bottom: 80px;
          left: 0;
          right: 0;
          text-align: center;
          font-family: 'Cormorant Garamond', serif;
          font-style: italic;
          font-size: 12px;
          color: rgba(227,215,255,0.55);
          letter-spacing: 0.08em;
        }

        /* Dos de la couverture (visible pendant le flip) */
        .pbo-cover-back {
          transform: rotateY(180deg);
          background:
            radial-gradient(circle at 50% 50%, rgba(255,255,255,0.02), transparent 60%),
            linear-gradient(180deg, #14102a 0%, #0a0813 100%);
          border: 1px solid rgba(212,175,55,0.25);
        }
        .pbo-cover-back-inner {
          position: absolute;
          inset: 16px;
          border: 1px solid rgba(212,175,55,0.18);
          border-radius: 3px;
        }

        /* ─ Responsive ─ */
        @media (max-width: 640px) {
          .pbo-book {
            aspect-ratio: 1 / 1.15;
          }
          .pbo-page { padding: 16px 14px 20px; }
          .pbo-quote { font-size: 12px; padding-left: 8px; }
          .pbo-map { height: 90px; }
          .pbo-cover-signature { bottom: 50px; font-size: 10px; }
          .pbo-cover-title { font-size: 22px; }
        }
      `}</style>
    </section>
  );
};

export default PdfBookOpen;
