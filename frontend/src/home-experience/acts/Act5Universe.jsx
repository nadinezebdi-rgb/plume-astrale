/**
 * Act5Universe — Acte V : L'Univers Plume Astrale
 * ────────────────────────────────────────────────────────────
 * "Plusieurs chemins. Un seul univers."
 *
 * 6 services révélés par TRANSFORMATION VISUELLE (pas une grille SaaS).
 * Chaque service occupe sa propre bande de 60vh minimum, avec :
 *  - Un mini-SVG poétique représentant sa métaphore
 *  - Titre H2 Cormorant Garamond
 *  - Tagline courte
 *  - CTA vers sa vraie route existante
 *
 * L'utilisateur scrolle et découvre — jamais rassemblés en même temps.
 * Palette : nuit --hex3-night, or --hex3-gold, ivoire --hex3-ivory.
 */
import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import StarfieldBackdrop from '@/components/StarfieldBackdrop';
import Act5DailyArticle from './Act5DailyArticle';
import { event as trackEvent } from '@/lib/analytics';

// ─── Mini-SVG icons poétiques par service ─────────────────
const SVG = {
  card: (
    <svg viewBox="0 0 100 140" width="90" height="126" aria-hidden="true">
      <rect x="8" y="8" width="84" height="124" rx="4"
            fill="rgba(23,16,46,0.9)" stroke="rgba(216,183,106,0.55)" strokeWidth="0.8" />
      <text x="50" y="80" textAnchor="middle" fontSize="42"
            fill="rgba(216,183,106,0.75)"
            fontFamily='"Cormorant Garamond", serif' fontStyle="italic">✦</text>
      <line x1="20" y1="118" x2="80" y2="118" stroke="rgba(216,183,106,0.35)" strokeWidth="0.4" />
    </svg>
  ),
  sky: (
    <svg viewBox="0 0 140 140" width="126" height="126" aria-hidden="true">
      <circle cx="70" cy="70" r="60" fill="none" stroke="rgba(216,183,106,0.35)" strokeWidth="0.6" />
      <circle cx="70" cy="70" r="42" fill="none" stroke="rgba(216,183,106,0.25)" strokeWidth="0.4" strokeDasharray="2 3" />
      <circle cx="70" cy="70" r="22" fill="none" stroke="rgba(216,183,106,0.20)" strokeWidth="0.4" strokeDasharray="1 2" />
      {[[70,10],[130,70],[70,130],[10,70],[110,110],[30,30],[110,30],[30,110]].map(([x,y],i)=>(
        <circle key={i} cx={x} cy={y} r="2.4" fill="#F4EFE6" style={{filter:'drop-shadow(0 0 5px rgba(216,183,106,0.7))'}} />
      ))}
      <circle cx="70" cy="70" r="3" fill="#D8B76A" />
    </svg>
  ),
  numbers: (
    <svg viewBox="0 0 140 100" width="140" height="100" aria-hidden="true">
      {[
        {t:'1',x:15,y:35,o:0.85,s:32},
        {t:'7',x:55,y:60,o:0.65,s:28},
        {t:'11',x:90,y:30,o:0.9,s:36},
        {t:'22',x:118,y:85,o:0.55,s:22},
      ].map((n,i)=>(
        <text key={i} x={n.x} y={n.y} fontSize={n.s} opacity={n.o}
              fill="#F4EFE6" fontFamily='"Cormorant Garamond", serif' fontStyle="italic">
          {n.t}
        </text>
      ))}
    </svg>
  ),
  duo: (
    <svg viewBox="0 0 160 100" width="160" height="100" aria-hidden="true">
      <ellipse cx="80" cy="50" rx="60" ry="30" fill="none"
               stroke="rgba(216,183,106,0.35)" strokeWidth="0.6" strokeDasharray="2 3" />
      <circle cx="40" cy="50" r="7" fill="#D8B76A" style={{filter:'drop-shadow(0 0 8px rgba(216,183,106,0.65))'}} />
      <circle cx="120" cy="50" r="5" fill="#F4EFE6" style={{filter:'drop-shadow(0 0 8px rgba(244,239,230,0.65))'}} />
    </svg>
  ),
  zodiac: (
    <svg viewBox="0 0 140 140" width="126" height="126" aria-hidden="true">
      <circle cx="70" cy="70" r="60" fill="none" stroke="rgba(216,183,106,0.30)" strokeWidth="0.6" />
      {['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓'].map((g,i)=>{
        const a = (i/12) * Math.PI * 2 - Math.PI/2;
        const x = 70 + Math.cos(a) * 52;
        const y = 70 + Math.sin(a) * 52 + 5;
        return (
          <text key={i} x={x} y={y} textAnchor="middle" fontSize="14"
                fill="rgba(216,183,106,0.80)"
                fontFamily='"Cormorant Garamond", serif'>{g}</text>
        );
      })}
    </svg>
  ),
  cycle: (
    <svg viewBox="0 0 140 60" width="140" height="60" aria-hidden="true">
      {[0.05,0.25,0.5,0.75,0.95].map((p,i)=>{
        const cx = 10 + p*120;
        const phase = Math.sin(p*Math.PI);
        return <circle key={i} cx={cx} cy="30" r={4 + phase*4} fill="rgba(216,183,106,0.7)" />;
      })}
      <path d="M 5 30 Q 70 5 135 30" fill="none" stroke="rgba(216,183,106,0.25)" strokeWidth="0.5" strokeDasharray="2 2" />
    </svg>
  ),
};

const SERVICES = [
  { key: 'tarot',       svg: 'card',    title: 'Tarot',          tagline: 'Éclairer une question.',                     cta: 'Tirer une carte',            route: '/services/tarot' },
  { key: 'theme',       svg: 'sky',     title: 'Thème natal',    tagline: 'Comprendre le ciel de votre naissance.',     cta: 'Découvrir mon ciel',         route: '/theme-natal' },
  { key: 'numero',      svg: 'numbers', title: 'Numérologie',    tagline: 'Ce que votre date raconte de votre chemin.', cta: 'Découvrir mon chemin',       route: '/services/numerologie' },
  { key: 'compat',      svg: 'duo',     title: 'Compatibilité',  tagline: 'Certaines rencontres laissent une empreinte.', cta: 'Explorer une relation',    route: '/services/compatibilite' },
  { key: 'horoscope',   svg: 'zodiac',  title: 'Horoscope',      tagline: 'Et aujourd\u2019hui\u00a0?',                 cta: 'Voir mon horoscope',         route: '/horoscope' },
  { key: 'cycles',      svg: 'cycle',   title: 'Vos cycles',     tagline: 'Comprendre ce qui \u00e9volue maintenant.',  cta: 'Explorer mon cycle',         route: '/services/revolution-solaire' },
];

function ServiceBand({ svc, index }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) { setVisible(true); io.disconnect(); }
        });
      },
      { threshold: 0.35 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  const handleClick = () => {
    trackEvent('home_v3_service_selected', { service: svc.key });
  };

  return (
    <div
      ref={ref}
      className="hex3-service-band"
      data-testid={`home-experience-service-${svc.key}`}
      data-visible={visible}
      style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        gap: 80, padding: '90px 24px',
        flexDirection: index % 2 === 0 ? 'row' : 'row-reverse',
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateY(0)' : 'translateY(30px)',
        transition: 'opacity 1200ms cubic-bezier(0.16, 1, 0.3, 1), transform 1200ms cubic-bezier(0.16, 1, 0.3, 1)',
      }}
    >
      <div style={{ flex: '0 0 auto', display: 'flex', alignItems: 'center', justifyContent: 'center', minWidth: 160 }}>
        {SVG[svc.svg]}
      </div>
      <div style={{ flex: '0 1 480px', textAlign: index % 2 === 0 ? 'left' : 'right' }}>
        <p style={{
          fontFamily: '"Inter", sans-serif', fontSize: 11, letterSpacing: '0.32em',
          textTransform: 'uppercase', color: 'rgba(216,183,106,0.75)', margin: '0 0 14px',
        }}>SERVICE 0{index + 1}</p>
        <h2 style={{
          fontFamily: '"Cormorant Garamond", "Playfair Display", serif',
          fontWeight: 400, fontSize: 'clamp(36px, 4.8vw, 60px)', lineHeight: 1.1,
          margin: '0 0 14px', color: '#F4EFE6',
        }}>{svc.title}</h2>
        <p style={{
          fontFamily: '"Cormorant Garamond", serif', fontStyle: 'italic',
          fontSize: 'clamp(16px, 1.7vw, 20px)',
          color: 'rgba(244,239,230,0.70)', lineHeight: 1.55,
          margin: '0 0 24px', maxWidth: 460,
          marginLeft: index % 2 === 0 ? 0 : 'auto',
        }}>{svc.tagline}</p>
        <Link
          to={svc.route}
          onClick={handleClick}
          data-testid={`home-experience-service-cta-${svc.key}`}
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 12,
            padding: '13px 26px', color: '#F4EFE6', textDecoration: 'none',
            fontFamily: '"Inter", sans-serif', fontSize: 11, letterSpacing: '0.28em',
            textTransform: 'uppercase', border: '1px solid rgba(216,183,106,0.55)',
            borderRadius: 2, transition: 'letter-spacing 400ms ease, background 300ms ease',
          }}
          onMouseEnter={(e) => { e.currentTarget.style.letterSpacing = '0.34em'; }}
          onMouseLeave={(e) => { e.currentTarget.style.letterSpacing = '0.28em'; }}
        >
          {svc.cta} →
        </Link>
      </div>
    </div>
  );
}

export default function Act5Universe() {
  return (
    <section
      data-testid="home-experience-scene-5"
      className="hex3-section hex3-act-5"
      style={{
        padding: '140px 0 80px',
      }}
    >
      <StarfieldBackdrop density={90} color="216, 183, 106" fade={0.3} />
      <div style={{ position: 'relative', zIndex: 1, maxWidth: 1200, margin: '0 auto 60px', textAlign: 'center', padding: '0 24px' }}>
        <p className="hex3-eyebrow">ACTE V · L&apos;UNIVERS</p>
        <h2 className="hex3-h2" style={{ marginBottom: 12 }}>Plusieurs chemins.</h2>
        <h2 className="hex3-h2" style={{ marginBottom: 30 }}><em>Un seul univers.</em></h2>
        <p style={{
          fontFamily: '"Cormorant Garamond", serif', fontStyle: 'italic',
          fontSize: 'clamp(17px, 1.8vw, 22px)',
          color: 'var(--hex3-ivory-mute)', margin: 0,
        }}>Explorez Plume Astrale.</p>
      </div>

      <div style={{ position: 'relative', zIndex: 1, maxWidth: 1200, margin: '0 auto' }}>
        {SERVICES.map((svc, i) => (
          <React.Fragment key={svc.key}>
            <ServiceBand svc={svc} index={i} />
            {/* Article du jour entre services 3 et 4 : voix éditoriale
                quotidienne intégrée dans la trame narrative */}
            {i === 2 && <Act5DailyArticle />}
          </React.Fragment>
        ))}
      </div>
    </section>
  );
}
