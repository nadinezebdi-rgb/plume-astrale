import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

/* ═══════════════════════════════════════════════════════════════════════════
   PLUME ASTRALE — LANDING v3 (scroll-story alternée sombre ↔ claire)
   Cible : femmes 35-70 · promesse guidance de vie · lecture complète 97€
   Principes :
     - Alternance visuelle sombre (nuit) / claire (crème) = rythme + respiration
     - Un seul style CTA doré rempli = action principale ; contour = secondaire
     - Visuels humains réels (portrait Soléna) plutôt que texte sur aplat
     - Réassurance crédible ; suppression des artefacts de fausse urgence
   ═══════════════════════════════════════════════════════════════════════════ */

const SOLENA_PORTRAIT = 'https://customer-assets-0z36b82j.emergentagent.net/job_consultation-astro/artifacts/72jssj5l_IMG01_portrait_femme_mystique_corrigee_2.png';
const SOLENA_LIFESTYLE = 'https://customer-assets-0z36b82j.emergentagent.net/job_consultation-astro/artifacts/l6a6ew17_photos%20Sol%C3%A9na.webp';
const SOLENA_MYSTIQUE = 'https://customer-assets-0z36b82j.emergentagent.net/job_consultation-astro/artifacts/htvnb1ej_PHOTOS%20SOLENA%202.webp';
const SOLENA_PDF = 'https://customer-assets-0z36b82j.emergentagent.net/job_consultation-astro/artifacts/ib324e70_PHOTOS%20SOLENA%203.webp';
const HERO_PORTRAITS = [SOLENA_PORTRAIT, SOLENA_LIFESTYLE, SOLENA_MYSTIQUE];
const MANIFESTO_VIDEO = 'https://customer-assets-0z36b82j.emergentagent.net/job_consultation-astro/artifacts/ly63ciw5_Le%20Manifeste%20Plume%20Astrale_1080p.mp4';
const LOGO = 'https://customer-assets-0z36b82j.emergentagent.net/job_consultation-astro/artifacts/ryuhr45s_logo%20plume%20%20%28250%20x%20250%20px%29.png';

/* A/B hero headline — stable per visitor via localStorage. */
const AB_KEY = 'plume_hero_variant';
const HERO_HEADLINES = {
  A: { key: 'A', pre: 'Ton ciel de naissance contient ', em: 'une carte', post: '.' },
  B: { key: 'B', pre: 'La lecture que ton ', em: 'ciel', post: ' attendait.' },
};

function pickHeroVariant() {
  try {
    const stored = localStorage.getItem(AB_KEY);
    if (stored === 'A' || stored === 'B') return stored;
    const v = Math.random() < 0.5 ? 'A' : 'B';
    localStorage.setItem(AB_KEY, v);
    return v;
  } catch (_e) {
    return Math.random() < 0.5 ? 'A' : 'B';
  }
}

function trackAB(variant, event) {
  try {
    const body = JSON.stringify({ variant, event });
    const url = `${API}/api/landing/ab/track`;
    if (navigator.sendBeacon) {
      navigator.sendBeacon(url, new Blob([body], { type: 'application/json' }));
    } else {
      fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body, keepalive: true }).catch(() => {});
    }
  } catch (_e) { /* fire-and-forget */ }
}

const styles = `
  :root{
    --pa-night-1:#0b0f24;
    --pa-night-2:#141a33;
    --pa-night-3:#1f1746;
    --pa-cream-1:#f6efdf;
    --pa-cream-2:#faf6ea;
    --pa-ink:#2b2540;
    --pa-gold:#c9a24b;
    --pa-gold-soft:#e2c07c;
    --pa-text-light:#e8e6f0;
    --pa-text-dim:#b8b4c9;
    --pa-text-dark:#3a3450;
  }
  .pa-page{margin:0;min-height:100vh;background:var(--pa-night-1);color:var(--pa-text-light);
    font-family:Georgia,'Times New Roman',serif;line-height:1.65;}
  .pa-wrap{max-width:1080px;margin:0 auto;padding:0 24px;}
  .pa-wrap-narrow{max-width:760px;margin:0 auto;padding:0 24px;}

  /* Section base */
  .pa-sec{padding:88px 0;position:relative;}
  .pa-sec-dark{background:var(--pa-night-1);color:var(--pa-text-light);}
  .pa-sec-dark-2{background:var(--pa-night-2);color:var(--pa-text-light);}
  .pa-sec-cream{background:var(--pa-cream-1);color:var(--pa-text-dark);}
  .pa-sec-cream-2{background:var(--pa-cream-2);color:var(--pa-text-dark);}

  /* Étoiles pour hero + clôture */
  .pa-starry{position:relative;overflow:hidden;
    background:radial-gradient(ellipse at 30% 20%,rgba(107,86,201,.35),transparent 55%),
               radial-gradient(ellipse at 70% 80%,rgba(217,178,106,.15),transparent 60%),
               linear-gradient(180deg,#080c1f 0%,#141a33 100%);}
  .pa-starry::before{content:'';position:absolute;inset:0;
    background-image:
      radial-gradient(1px 1px at 15% 22%,rgba(255,255,255,.75) 100%,transparent),
      radial-gradient(1px 1px at 42% 38%,rgba(255,255,255,.5) 100%,transparent),
      radial-gradient(1.5px 1.5px at 78% 18%,rgba(217,178,106,.7) 100%,transparent),
      radial-gradient(1px 1px at 25% 68%,rgba(255,255,255,.6) 100%,transparent),
      radial-gradient(1px 1px at 60% 82%,rgba(255,255,255,.55) 100%,transparent),
      radial-gradient(2px 2px at 88% 55%,rgba(226,192,124,.55) 100%,transparent),
      radial-gradient(1px 1px at 8% 46%,rgba(255,255,255,.4) 100%,transparent);
    background-size:600px 600px;
    animation:pa-twinkle 8s ease-in-out infinite;
    pointer-events:none;}
  @keyframes pa-twinkle{0%,100%{opacity:.7}50%{opacity:1}}

  /* Titres */
  .pa-h1{font-size:clamp(2rem,4.5vw,3.4rem);line-height:1.15;margin:0 0 22px;
    font-weight:400;letter-spacing:-.01em;}
  .pa-h1 em, .pa-h1 .pa-gold{font-style:italic;color:var(--pa-gold-soft);}
  .pa-h2{font-size:clamp(1.6rem,3vw,2.2rem);line-height:1.25;margin:0 0 20px;
    font-weight:400;color:inherit;}
  .pa-h2 .pa-gold{color:var(--pa-gold);}
  .pa-eyebrow{font-size:11px;letter-spacing:.24em;text-transform:uppercase;
    color:var(--pa-gold);margin:0 0 14px;font-family:Georgia,serif;}
  .pa-sec-cream .pa-eyebrow{color:#7a5f2a;}
  .pa-lead{font-size:1.1rem;color:inherit;opacity:.9;margin:0 0 16px;}
  .pa-sec-dark .pa-lead,.pa-sec-dark-2 .pa-lead{color:var(--pa-text-dim);}
  .pa-mini{font-size:.86rem;color:var(--pa-text-dim);margin-top:10px;}
  .pa-sec-cream .pa-mini{color:#6b6480;}

  /* CTA */
  .pa-cta{display:inline-flex;align-items:center;justify-content:center;gap:8px;
    background:linear-gradient(135deg,var(--pa-gold) 0%,var(--pa-gold-soft) 100%);
    color:#1a1030;font-weight:600;text-decoration:none;
    padding:16px 32px;border-radius:999px;font-size:1rem;letter-spacing:.02em;
    border:none;cursor:pointer;
    box-shadow:0 4px 20px rgba(201,162,75,.35),inset 0 1px 0 rgba(255,255,255,.35);
    transition:transform .18s ease,box-shadow .18s ease;font-family:Georgia,serif;}
  .pa-cta:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(201,162,75,.5);}
  .pa-cta:disabled{opacity:.6;cursor:not-allowed;transform:none;}
  .pa-cta-outline{display:inline-flex;align-items:center;justify-content:center;gap:8px;
    background:transparent;color:var(--pa-gold);text-decoration:none;
    padding:14px 28px;border-radius:999px;font-size:.95rem;letter-spacing:.02em;
    border:1.5px solid rgba(201,162,75,.6);cursor:pointer;
    transition:all .18s ease;font-family:Georgia,serif;}
  .pa-cta-outline:hover{border-color:var(--pa-gold);background:rgba(201,162,75,.08);}
  .pa-sec-cream .pa-cta-outline{color:#7a5f2a;border-color:rgba(122,95,42,.5);}
  .pa-sec-cream .pa-cta-outline:hover{background:rgba(122,95,42,.06);border-color:#7a5f2a;}

  /* Barre supérieure */
  .pa-topbar{background:var(--pa-night-2);border-bottom:1px solid rgba(255,255,255,.05);
    display:flex;justify-content:space-between;align-items:center;
    padding:12px 24px;font-size:12px;color:var(--pa-text-dim);}
  .pa-topbar-brand{display:inline-flex;align-items:center;gap:10px;text-decoration:none;
    color:var(--pa-text-light);font-weight:600;letter-spacing:.06em;
    text-transform:uppercase;font-size:12px;
    transition:opacity .18s ease;}
  .pa-topbar-brand:hover{opacity:.85;}
  .pa-topbar-logo{width:32px;height:32px;object-fit:contain;border-radius:6px;
    filter:drop-shadow(0 2px 8px rgba(201,162,75,.35));}
  .pa-topbar-account{display:inline-flex;align-items:center;gap:6px;text-decoration:none;
    color:var(--pa-gold);font-size:12px;letter-spacing:.08em;text-transform:uppercase;
    padding:6px 14px;border:1px solid rgba(201,162,75,.35);border-radius:999px;
    transition:all .18s ease;font-family:Georgia,serif;}
  .pa-topbar-account:hover{background:rgba(201,162,75,.1);border-color:var(--pa-gold);}
  .pa-topbar-account span{transition:transform .2s ease;}
  .pa-topbar-account:hover span{transform:translateX(3px);}

  /* Hero */
  .pa-hero-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:56px;align-items:center;
    position:relative;z-index:1;}
  .pa-hero-portrait{position:relative;border-radius:24px;overflow:hidden;
    box-shadow:0 30px 80px rgba(0,0,0,.55);
    border:1px solid rgba(201,162,75,.25);aspect-ratio:3/4;background:#141a33;}
  .pa-hero-slide{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;
    transform-origin:center 40%;will-change:opacity, transform;
    animation:pa-ken-burns 16s ease-in-out infinite alternate both;}
  @keyframes pa-ken-burns{
    0%{transform:scale(1.02);}
    100%{transform:scale(1.10);}
  }
  .pa-hero-portrait::after{content:'';position:absolute;inset:0;z-index:1;
    background:linear-gradient(180deg,transparent 40%,rgba(11,15,36,.55) 100%);pointer-events:none;}
  .pa-hero-badge{position:absolute;bottom:20px;left:20px;right:20px;
    background:rgba(11,15,36,.75);backdrop-filter:blur(10px);
    border:1px solid rgba(201,162,75,.3);border-radius:14px;padding:12px 16px;
    display:flex;justify-content:space-between;align-items:center;font-size:12px;color:var(--pa-text-light);}
  .pa-hero-badge strong{color:var(--pa-gold-soft);}

  /* Trust bar */
  .pa-trust-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;text-align:center;}
  .pa-trust-item{display:flex;flex-direction:column;align-items:center;gap:10px;
    padding:14px 8px;}
  .pa-trust-icon{width:44px;height:44px;display:flex;align-items:center;justify-content:center;
    border-radius:50%;background:rgba(122,95,42,.1);color:#7a5f2a;font-size:20px;
    border:1px solid rgba(122,95,42,.2);}
  .pa-trust-label{font-size:.85rem;color:#5a5470;letter-spacing:.02em;line-height:1.4;}
  .pa-trust-label strong{color:#3a3450;}

  /* Section Soléna */
  .pa-solena-grid{display:grid;grid-template-columns:.85fr 1.15fr;gap:56px;align-items:center;}
  .pa-solena-portrait{border-radius:20px;overflow:hidden;
    border:1px solid rgba(201,162,75,.2);aspect-ratio:4/5;
    box-shadow:0 20px 60px rgba(0,0,0,.5);}
  .pa-solena-portrait img{width:100%;height:100%;object-fit:cover;display:block;
    filter:brightness(1.02) saturate(1.05);}
  .pa-signature{margin-top:22px;padding-top:22px;border-top:1px solid rgba(201,162,75,.2);
    display:flex;align-items:center;gap:12px;font-size:.95rem;color:var(--pa-gold);}
  .pa-signature-stars{color:var(--pa-gold);}

  /* Cartes éclairées (Section 4) */
  .pa-cards-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;}
  .pa-card-light{background:#fff;border:1px solid rgba(122,95,42,.15);
    border-radius:16px;padding:24px;text-align:left;
    transition:transform .2s ease,box-shadow .2s ease;
    box-shadow:0 4px 20px rgba(58,52,80,.06);}
  .pa-card-light:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(58,52,80,.12);}
  .pa-card-icon{width:44px;height:44px;display:flex;align-items:center;justify-content:center;
    border-radius:12px;background:linear-gradient(135deg,#f5e8c8,#e6d1a0);color:#7a5f2a;
    font-size:22px;margin-bottom:16px;}
  .pa-card-light h3{margin:0 0 8px;font-size:1.05rem;color:var(--pa-text-dark);font-weight:600;}
  .pa-card-light p{margin:0;font-size:.9rem;color:#6b6480;line-height:1.55;}

  /* Value stack */
  .pa-value-wrap{background:linear-gradient(180deg,rgba(31,23,70,.85),rgba(20,26,51,.85));
    border:1px solid rgba(201,162,75,.3);border-radius:20px;padding:36px;
    box-shadow:0 30px 80px rgba(0,0,0,.5);}
  .pa-value-list{list-style:none;margin:0;padding:0;}
  .pa-value-item{display:grid;grid-template-columns:44px 1fr auto;gap:14px;align-items:center;
    padding:16px 0;border-bottom:1px solid rgba(255,255,255,.06);}
  .pa-value-item:last-child{border-bottom:none;}
  .pa-value-icon{width:36px;height:36px;display:flex;align-items:center;justify-content:center;
    border-radius:10px;background:rgba(201,162,75,.12);color:var(--pa-gold);font-size:16px;
    border:1px solid rgba(201,162,75,.25);}
  .pa-value-title{color:var(--pa-text-light);font-size:1rem;line-height:1.35;}
  .pa-value-title small{display:block;color:var(--pa-text-dim);font-size:.82rem;margin-top:3px;font-family:inherit;}
  .pa-value-old{color:#8a86a0;text-decoration:line-through;font-size:.95rem;text-align:right;min-width:60px;}
  .pa-value-total{margin-top:26px;padding-top:22px;border-top:1px solid rgba(201,162,75,.3);
    display:grid;grid-template-columns:1fr auto;gap:14px;align-items:end;}
  .pa-value-total-label{color:var(--pa-text-dim);font-size:.9rem;letter-spacing:.05em;text-transform:uppercase;}
  .pa-value-total-old{color:#8a86a0;text-decoration:line-through;font-size:1.2rem;}
  .pa-value-today{margin-top:14px;text-align:center;}
  .pa-value-today-amt{font-size:2.6rem;color:var(--pa-gold);font-weight:400;letter-spacing:-.02em;
    display:inline-block;}
  .pa-value-today-amt::before{content:'Aujourd\\'hui : ';font-size:.9rem;color:var(--pa-text-dim);
    letter-spacing:.04em;text-transform:uppercase;display:block;margin-bottom:6px;font-weight:400;}

  /* Bonus cards */
  .pa-bonus-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px;}
  .pa-bonus-card{background:#fff;border:1px solid rgba(122,95,42,.15);
    border-radius:14px;padding:20px;position:relative;
    box-shadow:0 4px 16px rgba(58,52,80,.06);}
  .pa-bonus-card::before{content:'CADEAU';position:absolute;top:-8px;left:16px;
    background:linear-gradient(135deg,#c9a24b,#e2c07c);color:#1a1030;
    font-size:9px;letter-spacing:.16em;padding:3px 10px;border-radius:8px;font-weight:700;}
  .pa-bonus-icon{font-size:24px;margin-bottom:10px;color:#7a5f2a;}
  .pa-bonus-card h4{margin:0 0 6px;font-size:.98rem;color:var(--pa-text-dark);}
  .pa-bonus-card p{margin:0;font-size:.85rem;color:#6b6480;}
  .pa-bonus-old{display:inline-block;text-decoration:line-through;color:#8a86a0;
    font-size:.82rem;margin-top:8px;}

  .pa-share-link{color:#7a5f2a;text-decoration:none;font-weight:600;
    border-bottom:1px dashed rgba(122,95,42,.4);transition:opacity .18s ease;}
  .pa-share-link:hover{opacity:.75;}

  /* Manifeste vidéo — cadrage portrait (video verticale) */
  .pa-video-wrap{position:relative;border-radius:18px;overflow:hidden;
    border:1px solid rgba(201,162,75,.25);
    box-shadow:0 20px 60px rgba(0,0,0,.5);background:#000;
    aspect-ratio:9/16;max-width:360px;margin:0 auto;}
  .pa-video-wrap video{width:100%;height:100%;display:block;object-fit:contain;background:#000;}
  .pa-video-overlay{position:absolute;inset:0;pointer-events:none;
    background:radial-gradient(circle at center,rgba(11,15,36,.25),rgba(11,15,36,.6) 70%);
    display:flex;align-items:center;justify-content:center;
    transition:opacity .3s ease;}
  .pa-video-playing .pa-video-overlay{opacity:0;}
  .pa-video-play{width:76px;height:76px;border-radius:50%;
    background:linear-gradient(135deg,var(--pa-gold),var(--pa-gold-soft));color:#1a1030;
    display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:600;
    box-shadow:0 8px 30px rgba(201,162,75,.5),inset 0 1px 0 rgba(255,255,255,.35);
    animation:pa-pulse 2.2s ease-in-out infinite;}
  @keyframes pa-pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}
  .pa-video-unmute{position:absolute;top:14px;right:14px;z-index:2;
    display:inline-flex;align-items:center;gap:6px;
    background:rgba(11,15,36,.75);backdrop-filter:blur(10px);
    border:1px solid rgba(201,162,75,.4);color:var(--pa-gold-soft);
    padding:8px 14px;border-radius:999px;cursor:pointer;
    font-family:Georgia,serif;font-size:.85rem;letter-spacing:.02em;
    transition:all .18s ease;
    animation:pa-chip-in .3s ease-out;}
  .pa-video-unmute:hover{background:rgba(11,15,36,.9);border-color:var(--pa-gold);
    color:#fff;transform:translateY(-1px);}
  @keyframes pa-chip-in{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}

  /* Sparkline */
  .pa-sparkline{display:block;max-width:110px;}

  /* Sticky mobile CTA */
  .pa-sticky-cta{position:fixed;bottom:16px;left:16px;right:16px;z-index:80;
    display:none;justify-content:center;pointer-events:none;
    animation:pa-sticky-in .3s ease-out;}
  .pa-sticky-cta .pa-cta{pointer-events:auto;width:100%;max-width:400px;padding:14px 22px;
    font-size:.95rem;
    box-shadow:0 8px 30px rgba(201,162,75,.45),0 2px 8px rgba(0,0,0,.5);}
  @keyframes pa-sticky-in{from{transform:translateY(60px);opacity:0}to{transform:translateY(0);opacity:1}}
  @media(max-width:768px){
    .pa-sticky-cta{display:flex;}
  }

  /* Garantie */
  .pa-guarantee-grid{display:grid;grid-template-columns:.9fr 1.1fr;gap:56px;align-items:center;}
  .pa-guarantee-photo{position:relative;border-radius:20px;overflow:hidden;
    border:1px solid rgba(201,162,75,.2);aspect-ratio:4/5;
    box-shadow:0 20px 60px rgba(0,0,0,.5);}
  .pa-guarantee-photo img{width:100%;height:100%;object-fit:cover;display:block;
    filter:brightness(1.02) saturate(1.03);}
  .pa-guarantee-photo-caption{position:absolute;bottom:0;left:0;right:0;
    background:linear-gradient(180deg,transparent,rgba(11,15,36,.9));
    padding:24px 20px 16px;color:var(--pa-text-light);
    font-size:.82rem;font-style:italic;text-align:center;}
  .pa-guarantee{max-width:520px;position:relative;}
  .pa-seal{width:112px;height:112px;margin:0 auto 24px;position:relative;
    display:flex;align-items:center;justify-content:center;
    background:radial-gradient(circle at 30% 30%,rgba(226,192,124,.35),rgba(201,162,75,.08) 70%);
    border-radius:50%;
    border:2px solid var(--pa-gold);
    box-shadow:0 0 0 4px rgba(201,162,75,.15),inset 0 0 20px rgba(201,162,75,.2);}
  .pa-seal-inner{text-align:center;color:var(--pa-gold-soft);}
  .pa-seal-inner div:first-child{font-size:11px;letter-spacing:.18em;text-transform:uppercase;
    line-height:1.2;font-weight:600;}
  .pa-seal-inner div:last-child{font-size:9px;letter-spacing:.1em;margin-top:4px;color:var(--pa-text-dim);}

  /* Témoignages */
  .pa-testis{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:22px;}
  .pa-testi{background:#fff;border:1px solid rgba(122,95,42,.15);border-radius:16px;padding:24px;
    box-shadow:0 4px 16px rgba(58,52,80,.06);}
  .pa-testi-head{display:flex;align-items:center;gap:12px;margin-bottom:14px;}
  .pa-testi-avatar{width:52px;height:52px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;font-size:22px;
    background:linear-gradient(135deg,#f5e8c8,#e6d1a0);color:#7a5f2a;border:2px solid #fff;
    box-shadow:0 2px 8px rgba(0,0,0,.1);}
  .pa-testi-meta{flex:1;}
  .pa-testi-name{font-size:.95rem;color:var(--pa-text-dark);font-weight:600;}
  .pa-testi-sub{font-size:.8rem;color:#6b6480;margin-top:2px;}
  .pa-testi-stars{color:var(--pa-gold);font-size:.9rem;letter-spacing:.05em;margin-top:2px;}
  .pa-testi-quote{font-size:.92rem;color:#4a4560;line-height:1.55;font-style:italic;
    padding-left:14px;border-left:2px solid var(--pa-gold);}
  .pa-testi-transform{margin-top:14px;padding-top:12px;border-top:1px dashed rgba(122,95,42,.2);
    font-size:.82rem;color:#6b6480;}
  .pa-testi-transform strong{color:#7a5f2a;}

  /* Section clôture avec photo mystique */
  .pa-final-grid{display:grid;grid-template-columns:1.15fr .85fr;gap:56px;align-items:center;
    position:relative;z-index:1;}
  .pa-final-photo{position:relative;border-radius:20px;overflow:hidden;
    border:1px solid rgba(201,162,75,.25);aspect-ratio:3/4;
    box-shadow:0 30px 80px rgba(0,0,0,.55);max-width:380px;margin:0 auto;}
  .pa-final-photo img{width:100%;height:100%;object-fit:cover;display:block;}
  .pa-final-photo::after{content:'';position:absolute;inset:0;
    background:linear-gradient(180deg,transparent 60%,rgba(11,15,36,.4) 100%);pointer-events:none;}

  /* FAQ */
  .pa-faq{margin:14px 0;border-bottom:1px solid rgba(255,255,255,.08);padding-bottom:14px;}
  .pa-faq summary{cursor:pointer;color:var(--pa-gold);font-size:1.05rem;padding:12px 0;
    list-style:none;display:flex;justify-content:space-between;align-items:center;gap:12px;
    font-weight:500;}
  .pa-faq summary::-webkit-details-marker{display:none;}
  .pa-faq summary::after{content:'+';font-size:1.4rem;color:var(--pa-gold);
    transition:transform .2s ease;font-weight:300;}
  .pa-faq[open] summary::after{transform:rotate(45deg);}
  .pa-faq p{margin:8px 0 0;color:var(--pa-text-dim);font-size:.95rem;padding-left:2px;}

  /* Formulaire */
  .pa-form{display:flex;flex-direction:column;gap:14px;margin:24px auto 0;max-width:520px;text-align:left;}
  .pa-input{background:rgba(11,15,36,.7);border:1px solid rgba(201,162,75,.2);color:var(--pa-text-light);
    padding:14px 18px;border-radius:12px;font-family:Georgia,serif;font-size:1rem;width:100%;box-sizing:border-box;}
  .pa-input:focus{outline:none;border-color:var(--pa-gold);
    box-shadow:0 0 0 3px rgba(201,162,75,.15);}
  .pa-label{font-size:.8rem;color:var(--pa-text-dim);letter-spacing:.08em;
    text-transform:uppercase;margin-bottom:6px;display:block;}
  .pa-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
  .pa-error{color:#f87171;font-size:.9rem;margin-top:8px;}

  /* Footer */
  .pa-footer{background:#050813;color:#7d7a90;padding:36px 24px;font-size:.8rem;
    border-top:1px solid rgba(255,255,255,.05);}
  .pa-footer-wrap{max-width:1080px;margin:0 auto;display:grid;
    grid-template-columns:1.2fr 1fr;gap:32px;align-items:start;}
  .pa-footer strong{color:#a09cb0;}
  .pa-footer a{color:var(--pa-gold);text-decoration:none;margin-right:14px;}
  .pa-footer a:hover{text-decoration:underline;}
  .pa-footer-mentions{font-size:.75rem;line-height:1.7;}
  .pa-footer-brand{font-size:.85rem;color:#a09cb0;}
  .pa-footer-brand::before{content:'✦ ';color:var(--pa-gold);}

  /* Responsive */
  @media(max-width:900px){
    .pa-hero-grid,.pa-solena-grid,.pa-guarantee-grid,.pa-final-grid{grid-template-columns:1fr;gap:36px;}
    .pa-hero-portrait,.pa-guarantee-photo{max-width:420px;margin:0 auto;}
    .pa-solena-portrait{max-width:340px;margin:0 auto;}
    .pa-trust-grid{grid-template-columns:repeat(2,1fr);gap:14px;}
    .pa-footer-wrap{grid-template-columns:1fr;}
    .pa-sec{padding:64px 0;}
    .pa-topbar{padding:10px 16px;}
    .pa-topbar-brand{font-size:11px;gap:8px;}
    .pa-topbar-logo{width:28px;height:28px;}
    .pa-topbar-account{font-size:10px;padding:5px 10px;letter-spacing:.06em;}
    .pa-guarantee{max-width:none;margin:0 auto;text-align:center;}
    .pa-final-grid > div:first-child{text-align:center;}
    .pa-final-grid > div:first-child > div:nth-child(4){justify-content:center;}
  }
  @media(max-width:520px){
    .pa-wrap,.pa-wrap-narrow{padding:0 18px;}
    .pa-row{grid-template-columns:1fr;}
    .pa-value-wrap{padding:22px 18px;}
    .pa-value-item{grid-template-columns:36px 1fr auto;gap:10px;}
    .pa-value-today-amt{font-size:2.2rem;}
  }
`;

const CheckoutForm = ({ onSubmit, loading, error }) => {
  const [form, setForm] = useState({
    email: '', first_name: '', birth_date: '', birth_time: '',
    birth_city: 'Paris', birth_country: 'FR',
  });
  const upd = (k, v) => setForm((s) => ({ ...s, [k]: v }));
  const handle = (e) => { e.preventDefault(); onSubmit(form); };
  return (
    <form className="pa-form" onSubmit={handle} data-testid="lecture-complete-form">
      <div>
        <span className="pa-label">Prénom</span>
        <input className="pa-input" value={form.first_name}
          onChange={(e) => upd('first_name', e.target.value)} required
          data-testid="lecture-first-name" />
      </div>
      <div>
        <span className="pa-label">Email</span>
        <input className="pa-input" type="email" value={form.email}
          onChange={(e) => upd('email', e.target.value)} required
          data-testid="lecture-email" />
      </div>
      <div className="pa-row">
        <div>
          <span className="pa-label">Date de naissance</span>
          <input className="pa-input" type="date" value={form.birth_date}
            onChange={(e) => upd('birth_date', e.target.value)} required
            data-testid="lecture-birth-date" />
        </div>
        <div>
          <span className="pa-label">Heure de naissance</span>
          <input className="pa-input" type="time" value={form.birth_time}
            onChange={(e) => upd('birth_time', e.target.value)}
            data-testid="lecture-birth-time" />
        </div>
      </div>
      <div>
        <span className="pa-label">Ville de naissance</span>
        <input className="pa-input" value={form.birth_city}
          onChange={(e) => upd('birth_city', e.target.value)}
          data-testid="lecture-birth-city" />
      </div>
      <button type="submit" className="pa-cta" disabled={loading}
        data-testid="lecture-checkout-btn" style={{ marginTop: 8 }}>
        {loading ? 'Redirection…' : 'Recevoir ma lecture complète · 97€'}
      </button>
      {error && <div className="pa-error" data-testid="lecture-error">{error}</div>}
    </form>
  );
};

const TrustItem = ({ icon, children }) => (
  <div className="pa-trust-item">
    <div className="pa-trust-icon">{icon}</div>
    <div className="pa-trust-label">{children}</div>
  </div>
);

/** Sparkline SVG basique : montre la tendance count sur N jours */
const Sparkline = ({ points, width = 96, height = 22 }) => {
  if (!points || points.length < 2) return null;
  const values = points.map((p) => p.count || 0);
  const max = Math.max(1, ...values);
  const step = width / (points.length - 1);
  const path = values.map((v, i) => {
    const x = i * step;
    const y = height - (v / max) * (height - 3) - 2;
    return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}
      className="pa-sparkline" role="img" aria-label={`Tendance ${points.length}j`}
      data-testid="trust-sparkline">
      <defs>
        <linearGradient id="pa-spark-grad" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#c9a24b" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#c9a24b" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={`${path} L${width},${height} L0,${height} Z`}
        fill="url(#pa-spark-grad)" stroke="none" />
      <path d={path} fill="none" stroke="#c9a24b" strokeWidth="1.6"
        strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

const IlluminationCard = ({ icon, title, children }) => (
  <div className="pa-card-light">
    <div className="pa-card-icon">{icon}</div>
    <h3>{title}</h3>
    <p>{children}</p>
  </div>
);

const ValueItem = ({ icon, title, sub, price }) => (
  <li className="pa-value-item">
    <div className="pa-value-icon">{icon}</div>
    <div className="pa-value-title"><strong>{title}</strong>{sub && <small>{sub}</small>}</div>
    <div className="pa-value-old">{price}€</div>
  </li>
);

const BonusCard = ({ icon, title, children, old }) => (
  <div className="pa-bonus-card">
    <div className="pa-bonus-icon">{icon}</div>
    <h4>{title}</h4>
    <p>{children}</p>
    {old && <span className="pa-bonus-old">Valeur {old}€</span>}
  </div>
);

const Testimonial = ({ initial, name, sign, city, quote, transformBefore, transformAfter }) => (
  <div className="pa-testi">
    <div className="pa-testi-head">
      <div className="pa-testi-avatar">{initial}</div>
      <div className="pa-testi-meta">
        <div className="pa-testi-name">{name}</div>
        <div className="pa-testi-sub">{sign} · {city}</div>
        <div className="pa-testi-stars">★★★★★</div>
      </div>
    </div>
    <div className="pa-testi-quote">« {quote} »</div>
    {transformBefore && (
      <div className="pa-testi-transform">
        <strong>Avant :</strong> {transformBefore}<br />
        <strong>Après :</strong> {transformAfter}
      </div>
    )}
  </div>
);

export default function Index() {
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [heroVariant, setHeroVariant] = useState('A');
  const [testimonials, setTestimonials] = useState(null);
  const [trustStats, setTrustStats] = useState(null);
  const [ratingSeries, setRatingSeries] = useState(null);
  const [showStickyCTA, setShowStickyCTA] = useState(false);
  const [videoPlaying, setVideoPlaying] = useState(false);
  const [videoMuted, setVideoMuted] = useState(true);
  const [autoplayed, setAutoplayed] = useState(false);
  const [heroPhotoIdx, setHeroPhotoIdx] = useState(0);
  const videoRef = React.useRef(null);

  // Photo rotator hero — crossfade lent toutes les 6s (pause si tab en background)
  React.useEffect(() => {
    if (typeof document !== 'undefined' && document.hidden) return;
    const id = setInterval(() => {
      if (document.hidden) return;
      setHeroPhotoIdx((i) => (i + 1) % HERO_PORTRAITS.length);
    }, 6000);
    return () => clearInterval(id);
  }, []);

  // A/B pick + impression tracking. Interroge d'abord le backend pour honorer un lock manuel/auto.
  React.useEffect(() => {
    let cancel = false;
    (async () => {
      let v = null;
      try {
        const r = await fetch(`${API}/api/landing/ab/serve-variant`);
        const d = await r.json();
        if (d && (d.variant === 'A' || d.variant === 'B')) {
          v = d.variant;
          try { localStorage.setItem(AB_KEY, v); } catch (_e) { /* ok */ }
        }
      } catch (_e) { /* fallback silencieux */ }
      if (cancel) return;
      if (!v) v = pickHeroVariant();
      setHeroVariant(v);
      trackAB(v, 'impression');
    })();
    return () => { cancel = true; };
  }, []);

  // Live testimonials fetch (fallback silencieux)
  React.useEffect(() => {
    let cancel = false;
    fetch(`${API}/api/landing/testimonials`)
      .then((r) => r.json())
      .then((d) => { if (!cancel && d?.testimonials?.length) setTestimonials(d.testimonials); })
      .catch(() => {});
    return () => { cancel = true; };
  }, []);

  // Trust stats live (badge hero + trust bar)
  React.useEffect(() => {
    let cancel = false;
    fetch(`${API}/api/landing/trust-stats`)
      .then((r) => r.json())
      .then((d) => { if (!cancel && d) setTrustStats(d); })
      .catch(() => {});
    fetch(`${API}/api/landing/rating-timeseries?days=30`)
      .then((r) => r.json())
      .then((d) => { if (!cancel && d?.points) setRatingSeries(d.points); })
      .catch(() => {});
    return () => { cancel = true; };
  }, []);

  // Sticky mobile CTA : apparait quand on scrolle au-delà du hero
  React.useEffect(() => {
    const onScroll = () => {
      const scrolled = (window.scrollY || document.documentElement.scrollTop || 0) > 620;
      setShowStickyCTA(scrolled);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Manifesto autoplay muted quand la vidéo entre dans le viewport (desktop uniquement)
  React.useEffect(() => {
    const isDesktop = typeof window !== 'undefined' && window.matchMedia
      && window.matchMedia('(min-width: 900px)').matches;
    if (!isDesktop || !videoRef.current) return;
    const el = videoRef.current;
    let didAutoplay = false;
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting && e.intersectionRatio >= 0.5 && !didAutoplay) {
          didAutoplay = true;
          el.muted = true;
          el.play().then(() => {
            setVideoPlaying(true);
            setAutoplayed(true);
            setVideoMuted(true);
          }).catch(() => { /* iOS/blocked = no-op */ });
        }
      });
    }, { threshold: [0, 0.25, 0.5, 0.75, 1] });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  const unmuteVideo = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = false;
    videoRef.current.volume = 1.0;
    setVideoMuted(false);
  };

  const startCheckout = async (form) => {
    setError(null); setLoading(true);
    try {
      const res = await fetch(`${API}/api/lecture-complete/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ ...form, origin_url: window.location.origin }),
      });
      const data = await res.json();
      if (data.url) { window.location.href = data.url; }
      else { setError(data.detail || 'Impossible de créer la session.'); setLoading(false); }
    } catch (e) {
      setError('Erreur de connexion. Réessaie dans quelques instants.'); setLoading(false);
    }
  };

  const scrollToForm = () => {
    setShowForm(true);
    setTimeout(() => {
      document.getElementById('checkout')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 60);
  };

  const signupPath = user ? '/mon-compte' : '/inscription';

  return (
    <>
      <SEO
        path="/"
        title="Plume Astrale · La Lecture Complète de ton Ciel"
        description="Une lecture personnelle de ton thème natal par Soléna. Guidance symbolique pour les femmes qui cherchent à comprendre le présent — sans horoscope générique."
      />
      <style>{styles}</style>

      <div className="pa-page" data-testid="landing-v2">

        {/* ═══ SECTION 0 · BARRE SUPÉRIEURE ═══ */}
        <div className="pa-topbar" data-testid="landing-topbar">
          <Link to="/" className="pa-topbar-brand" data-testid="landing-topbar-brand">
            <img src={LOGO} alt="Plume Astrale" className="pa-topbar-logo" />
            <span>Plume Astrale</span>
          </Link>
          <Link to={signupPath} className="pa-topbar-account" data-testid="landing-topbar-account">
            {user ? 'Mon compte' : 'Mon compte'} <span aria-hidden="true">→</span>
          </Link>
        </div>

        {/* ═══ SECTION 1 · HÉROS (sombre, immersif, avec portrait + A/B headline) ═══ */}
        <section className="pa-sec pa-sec-dark pa-starry" data-testid="landing-hero"
          data-hero-variant={heroVariant}>
          <div className="pa-wrap">
            <div className="pa-hero-grid">
              <div>
                <h1 className="pa-h1" data-testid={`hero-headline-${heroVariant}`}>
                  {HERO_HEADLINES[heroVariant].pre}
                  <em>{HERO_HEADLINES[heroVariant].em}</em>
                  {HERO_HEADLINES[heroVariant].post}
                </h1>
                <p className="pa-lead">
                  Une lecture personnelle de ton thème natal par Soléna — les cycles,
                  les répétitions, les tournants. Pas d'horoscope générique.
                </p>
                <Link to={signupPath} className="pa-cta" data-testid="landing-hero-signup"
                  onClick={() => trackAB(heroVariant, 'signup_click')}
                  style={{ marginTop: 8 }}>
                  Recevoir ma lecture · 20 crédits offerts
                </Link>
                <p className="pa-mini">
                  Sans carte bancaire · Première réponse en 2 minutes
                </p>
              </div>
              <div className="pa-hero-portrait" data-testid="hero-portrait-rotator">
                {HERO_PORTRAITS.map((src, i) => (
                  <img
                    key={src}
                    src={src}
                    alt="Soléna, la voix de Plume Astrale"
                    className="pa-hero-slide"
                    loading={i === 0 ? 'eager' : 'lazy'}
                    data-testid={`hero-portrait-${i}`}
                    style={{
                      opacity: i === heroPhotoIdx ? 1 : 0,
                      transition: 'opacity 1.4s ease-in-out',
                    }}
                  />
                ))}
                <div className="pa-hero-badge">
                  <span>Soléna, la voix de Plume Astrale</span>
                  <strong data-testid="hero-badge-rating">
                    {trustStats?.average_rating ? `${trustStats.average_rating}/5` : '4,9/5'} ★
                  </strong>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ═══ SECTION 1.5 · MANIFESTE VIDEO (transition sombre → clair) ═══ */}
        <section className="pa-sec pa-sec-dark-2 pa-video-sec" data-testid="landing-manifesto"
          style={{ padding: '56px 0' }}>
          <div className="pa-wrap-narrow">
            <div style={{ textAlign: 'center', marginBottom: 20 }}>
              <div className="pa-eyebrow">Le Manifeste Plume Astrale</div>
              <h2 className="pa-h2" style={{ fontSize: 'clamp(1.4rem,2.4vw,1.8rem)' }}>
                45 secondes pour comprendre <em className="pa-gold">ce que je fais avec toi</em>
              </h2>
            </div>
            <div className={`pa-video-wrap ${videoPlaying ? 'pa-video-playing' : ''}`}
              data-testid="landing-manifesto-video">
              <video
                ref={videoRef}
                src={MANIFESTO_VIDEO}
                poster={SOLENA_MYSTIQUE}
                preload="metadata"
                playsInline
                controls
                muted
                onPlay={() => setVideoPlaying(true)}
                onPause={() => setVideoPlaying(false)}
                data-testid="landing-manifesto-player"
              />
              {!videoPlaying && (
                <div className="pa-video-overlay" aria-hidden="true">
                  <div className="pa-video-play">▶</div>
                </div>
              )}
              {autoplayed && videoPlaying && videoMuted && (
                <button
                  type="button"
                  onClick={unmuteVideo}
                  className="pa-video-unmute"
                  data-testid="landing-manifesto-unmute"
                  aria-label="Activer le son"
                >
                  <span aria-hidden="true">🔊</span>
                  <span>Activer le son</span>
                </button>
              )}
            </div>
          </div>
        </section>

        {/* ═══ SECTION 2 · BANDE DE CONFIANCE (claire) ═══ */}
        <section className="pa-sec pa-sec-cream-2" style={{ padding: '48px 0' }}
          data-testid="landing-trust">
          <div className="pa-wrap">
            <div className="pa-trust-grid">
              <TrustItem icon="✦"><strong>Données astro réelles</strong><br />éphémérides pro</TrustItem>
              <TrustItem icon="◆"><strong>Calcul à la minute</strong><br />ton vrai thème natal</TrustItem>
              <TrustItem icon="⌂"><strong>Paiement sécurisé</strong><br />Stripe · 3-D Secure</TrustItem>
              <TrustItem icon="★">
                <strong data-testid="trust-avg-rating">
                  {trustStats?.average_rating ? `${trustStats.average_rating}/5` : '4,9/5'}
                </strong><br />
                <span data-testid="trust-count">
                  {trustStats?.display_count || '+2 000'} lectures livrées
                </span>
                {ratingSeries && ratingSeries.length > 1 && (
                  <div style={{ marginTop: 6, opacity: .85 }}>
                    <Sparkline points={ratingSeries} />
                    <div style={{ fontSize: 9, color: '#8a7f4a', letterSpacing: '.1em',
                      textTransform: 'uppercase', marginTop: 2 }}>
                      30 derniers jours
                    </div>
                  </div>
                )}
              </TrustItem>
            </div>
          </div>
        </section>

        {/* ═══ SECTION 3 · L'HISTOIRE DE SOLÉNA (sombre, intime) ═══ */}
        <section className="pa-sec pa-sec-dark-2" data-testid="landing-solena">
          <div className="pa-wrap">
            <div className="pa-solena-grid">
              <div className="pa-solena-portrait">
                <img src={SOLENA_LIFESTYLE} alt="Soléna, portrait lifestyle chaleureux"
                  loading="lazy" />
              </div>
              <div>
                <div className="pa-eyebrow">L'histoire de Soléna</div>
                <h2 className="pa-h2">Bonjour, je suis <span className="pa-gold">Soléna</span>.</h2>
                <p className="pa-lead">
                  Je suis la voix et le visage de Plume Astrale. Je suis là pour vous
                  guider dans la découverte de votre thème, de vos cycles et de vos
                  tirages afin de vous aider à mieux <strong>comprendre ce que vous traversez</strong>.
                </p>
                <p className="pa-lead">
                  Mon rôle n'est pas de décider à votre place, mais de vous accompagner
                  dans vos réflexions grâce à l'astrologie, au tarot et à la numérologie.
                </p>
                <div className="pa-signature">
                  <span className="pa-testi-avatar" style={{ width: 40, height: 40, fontSize: 16 }}>S</span>
                  <span>— Soléna · <span className="pa-signature-stars">★★★★★</span> 4,9/5</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ═══ SECTION 4 · CE QUE SOLÉNA ÉCLAIRE (claire, respiration) ═══ */}
        <section className="pa-sec pa-sec-cream" data-testid="landing-illuminations">
          <div className="pa-wrap">
            <div style={{ textAlign: 'center', maxWidth: 620, margin: '0 auto 40px' }}>
              <div className="pa-eyebrow">5 dimensions de ta vie</div>
              <h2 className="pa-h2">Ce que Soléna éclaire pour toi</h2>
            </div>
            <div className="pa-cards-grid">
              <IlluminationCard icon="♥" title="Tes liens du cœur">
                Comprendre tes relations, ce qui se rejoue, ce qui peut s'apaiser.
              </IlluminationCard>
              <IlluminationCard icon="⌂" title="Famille & racines">
                Les héritages, les nœuds, les réconciliations possibles.
              </IlluminationCard>
              <IlluminationCard icon="↗" title="Ton chemin de vie">
                Les transitions, les grands passages, le sens de cette période.
              </IlluminationCard>
              <IlluminationCard icon="∞" title="Ta trame karmique">
                Pourquoi certaines épreuves reviennent, et comment les traverser.
              </IlluminationCard>
              <IlluminationCard icon="☾" title="Tes cycles à venir">
                Les fenêtres favorables des prochains mois, mois par mois.
              </IlluminationCard>
            </div>
            <div style={{ textAlign: 'center', marginTop: 36 }}>
              <Link to={signupPath} className="pa-cta-outline" data-testid="landing-illum-signup">
                Commencer gratuitement · 20 crédits offerts
              </Link>
            </div>
          </div>
        </section>

        {/* ═══ SECTION 5 · L'OFFRE / VALUE STACK (sombre, moment fort) ═══ */}
        <section className="pa-sec pa-sec-dark" id="checkout" data-testid="landing-offer">
          <div className="pa-wrap-narrow">
            <div style={{ textAlign: 'center', marginBottom: 32 }}>
              <div className="pa-eyebrow">L'offre complète</div>
              <h2 className="pa-h2">La Lecture Complète de <em className="pa-gold">ton</em> Ciel</h2>
              <p className="pa-lead">Tout réuni pour la première fois.</p>
            </div>
            <div className="pa-value-wrap">
              <ul className="pa-value-list">
                <ValueItem icon="✦" title="Ton Thème Natal décodé"
                  sub="La carte complète de ton ciel de naissance" price="29" />
                <ValueItem icon="☾" title="Ton Guide de Cycles 2026"
                  sub="Mois par mois, tes périodes clés" price="34,99" />
                <ValueItem icon="∞" title="Ta Lecture Karmique + Arbre de Vie"
                  sub="La racine de ce qui se répète" price="39" />
                <ValueItem icon="♥" title="Ton Analyse des Liens"
                  sub="Comprendre tes relations proches" price="24" />
                <ValueItem icon="◆" title="Tes 12 fenêtres favorables 2026"
                  sub="Le calendrier de tes bons moments" price="29" />
                <ValueItem icon="☆" title="Soléna à tes côtés · 90 jours"
                  sub="Pose tes questions, le jour où elles viennent" price="59" />
              </ul>
              <div className="pa-value-total">
                <span className="pa-value-total-label">Valeur totale</span>
                <span className="pa-value-total-old">214€</span>
              </div>
              <div className="pa-value-today">
                <span className="pa-value-today-amt">97€</span>
              </div>
              <div style={{ textAlign: 'center', marginTop: 24 }}>
                {!showForm ? (
                  <button className="pa-cta" onClick={() => { trackAB(heroVariant, 'cta_click'); scrollToForm(); }}
                    data-testid="landing-open-form-btn">
                    Recevoir ma lecture complète · 97€
                  </button>
                ) : (
                  <CheckoutForm onSubmit={startCheckout} loading={loading} error={error} />
                )}
                <p className="pa-mini" style={{ marginTop: 14 }}>
                  Paiement unique · Garantie 14 jours «&nbsp;Clarté ou remboursée&nbsp;»
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ═══ SECTION 6 · BONUS (claire) ═══ */}
        <section className="pa-sec pa-sec-cream-2" data-testid="landing-bonus">
          <div className="pa-wrap">
            <div style={{ textAlign: 'center', maxWidth: 640, margin: '0 auto 40px' }}>
              <div className="pa-eyebrow">4 présents inclus · Valeur 90€</div>
              <h2 className="pa-h2">Parce que tu commences aujourd'hui</h2>
            </div>
            <div className="pa-bonus-grid">
              <BonusCard icon="✿" title="Le Rituel du Soir apaisant" old="27">
                Pour les nuits où tout remonte.
              </BonusCard>
              <BonusCard icon="♥" title="Ta Carte des Liens" old="19">
                Comment aimer et te faire comprendre, selon ton profil.
              </BonusCard>
              <BonusCard icon="◇" title="Calendrier des 12 fenêtres 2026" old="29">
                Imprimable, à garder près de toi.
              </BonusCard>
              <BonusCard icon="✎" title="Question longue prioritaire" old="15">
                Une vraie réponse posée, prise à cœur par Soléna.
              </BonusCard>
            </div>
          </div>
        </section>

        {/* ═══ SECTION 7 · GARANTIE (sombre, rassurante avec sceau + photo produit) ═══ */}
        <section className="pa-sec pa-sec-dark-2" data-testid="landing-guarantee">
          <div className="pa-wrap">
            <div className="pa-guarantee-grid">
              <div className="pa-guarantee-photo">
                <img src={SOLENA_PDF} alt="Soléna présente une lecture personnalisée imprimée"
                  loading="lazy" />
                <div className="pa-guarantee-photo-caption">Une vraie lecture, un vrai document — pas un email générique.</div>
              </div>
              <div className="pa-guarantee">
                <div className="pa-seal" aria-hidden="true">
                  <div className="pa-seal-inner">
                    <div>Clarté<br/>ou remboursée</div>
                    <div>14 jours</div>
                  </div>
                </div>
                <h2 className="pa-h2">Le risque est pour <em className="pa-gold">moi</em>.</h2>
                <p className="pa-lead">
                  Reçois ta lecture. Si dans les 14 jours elle ne t'a pas apporté au moins
                  une vraie clarté sur ce que tu traverses — tu écris un mot à Soléna, et
                  on te rembourse intégralement, sans avoir à te justifier.
                </p>
                <p className="pa-mini" style={{ color: 'var(--pa-gold-soft)', fontStyle: 'italic', marginTop: 20 }}>
                  La tranquillité est pour toi.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ═══ SECTION 8 · PREUVE SOCIALE INCARNÉE (claire) ═══ */}
        <section className="pa-sec pa-sec-cream" data-testid="landing-testimonials">
          <div className="pa-wrap">
            <div style={{ textAlign: 'center', maxWidth: 620, margin: '0 auto 40px' }}>
              <div className="pa-eyebrow">Témoignages vérifiés</div>
              <h2 className="pa-h2">Des femmes qui ont enfin vu clair</h2>
            </div>
            <div className="pa-testis">
              {(testimonials || [
                { initial: 'L', name: 'Léa M.', sign: 'Poissons', city: 'Lyon',
                  quote: "Rien de générique, rien de flou. Soléna m'a expliqué pourquoi je revivais toujours le même schéma — et comment le comprendre.",
                  transform_before: 'Je tournais en rond avec la même relation depuis 3 ans.',
                  transform_after: "J'ai enfin compris le nœud, et posé un vrai choix." },
                { initial: 'S', name: 'Sarah T.', sign: 'Cancer', city: 'Bordeaux',
                  quote: "J'étais sceptique. La finesse de la lecture m'a scotchée. Ça m'a aidée à faire la paix avec une histoire de famille.",
                  transform_before: 'Un secret familial que je portais depuis toujours.',
                  transform_after: 'Une paix nouvelle avec mes racines.' },
                { initial: 'M', name: 'Manon D.', sign: 'Lion', city: 'Marseille',
                  quote: 'Je relis ma lecture chaque semaine. Plus apaisant que trois ans à ressasser toute seule.',
                  transform_before: 'Nuits blanches à retourner les mêmes questions.',
                  transform_after: "Un cap clair pour l'année, et le sommeil revenu." },
              ]).slice(0, 6).map((t, i) => (
                <Testimonial key={t.id || i}
                  initial={t.initial}
                  name={t.name}
                  sign={t.sign || ''}
                  city={t.city || ''}
                  quote={t.quote}
                  transformBefore={t.transform_before}
                  transformAfter={t.transform_after}
                />
              ))}
            </div>
            <div style={{ textAlign: 'center', marginTop: 40 }}>
              <button className="pa-cta" onClick={() => { trackAB(heroVariant, 'cta_click'); scrollToForm(); }}
                data-testid="landing-testi-cta">
                Recevoir ma lecture · 97€
              </button>
              <p className="pa-mini" style={{ marginTop: 18 }}>
                Déjà accompagnée par Soléna ?{' '}
                <Link to="/temoignage" className="pa-share-link"
                  data-testid="landing-testi-share">
                  Partage ton témoignage →
                </Link>
              </p>
            </div>
          </div>
        </section>

        {/* ═══ SECTION 9 · FAQ (sombre, lever d'objections) ═══ */}
        <section className="pa-sec pa-sec-dark-2" data-testid="landing-faq">
          <div className="pa-wrap-narrow">
            <div style={{ textAlign: 'center', marginBottom: 32 }}>
              <div className="pa-eyebrow">Questions fréquentes</div>
              <h2 className="pa-h2">Ce que les femmes nous demandent</h2>
            </div>
            <details className="pa-faq" data-testid="faq-sceptique">
              <summary>Est-ce que ça marche si je suis sceptique ?</summary>
              <p>C'est même souvent là que la lecture surprend le plus. Soléna ne te demande pas d'y croire — juste de lire ce que ton ciel révèle. Beaucoup arrivent sceptiques et repartent troublées de justesse.</p>
            </details>
            <details className="pa-faq" data-testid="faq-avenir">
              <summary>Est-ce que Soléna prédit l'avenir ?</summary>
              <p>Non. Soléna offre une guidance symbolique et personnalisée : elle éclaire les cycles, les tendances, le sens — pas un destin figé. Les choix restent les tiens.</p>
            </details>
            <details className="pa-faq" data-testid="faq-tech">
              <summary>Je ne suis pas très à l'aise avec la technologie.</summary>
              <p>Tout se fait en quelques clics, et Soléna te guide pas à pas. Si tu sais envoyer un message, tu sais lui parler.</p>
            </details>
            <details className="pa-faq" data-testid="faq-retour">
              <summary>Et si ça ne me correspond pas ?</summary>
              <p>La garantie «&nbsp;Clarté ou remboursée&nbsp;» de 14 jours existe exactement pour ça. Tu écris un mot à Soléna, et on te rembourse intégralement.</p>
            </details>
            <div style={{ textAlign: 'center', marginTop: 32 }}>
              <Link to={signupPath} className="pa-cta-outline" data-testid="landing-faq-signup">
                Commencer avec 20 crédits offerts
              </Link>
            </div>
          </div>
        </section>

        {/* ═══ SECTION 10 · CLÔTURE ÉMOTIONNELLE + CTA FINAL (sombre étoilé, boucle) ═══ */}
        <section className="pa-sec pa-sec-dark pa-starry" data-testid="landing-final">
          <div className="pa-wrap">
            <div className="pa-final-grid">
              <div style={{ position: 'relative', zIndex: 1 }}>
                <div className="pa-eyebrow">La nuit est bonne conseillère</div>
                <h2 className="pa-h2">La nuit est le bon moment pour <em className="pa-gold">écouter</em>.</h2>
                <p className="pa-lead">
                  Tu peux refermer cette page et continuer à porter tes questions seule…
                  ou laisser Soléna t'aider à lire ce qui se joue vraiment, dès maintenant.
                </p>
                <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginTop: 20 }}>
                  <button className="pa-cta" onClick={() => { trackAB(heroVariant, 'cta_click'); scrollToForm(); }}
                    data-testid="landing-final-cta">
                    Ma lecture complète · 97€
                  </button>
                  <Link to={signupPath} className="pa-cta-outline"
                    onClick={() => trackAB(heroVariant, 'signup_click')}
                    data-testid="landing-final-signup">
                    Ou commencer gratuitement
                  </Link>
                </div>
                <p className="pa-mini" style={{ marginTop: 24 }}>
                  ✓ Réponse sous 2h · ✓ Sans engagement · ✓ Garantie 14 jours
                </p>
              </div>
              <div className="pa-final-photo">
                <img src={SOLENA_MYSTIQUE} alt="Soléna sous la voûte étoilée" loading="lazy" />
              </div>
            </div>
          </div>
        </section>

        {/* ═══ STICKY MOBILE CTA ═══ */}
        {showStickyCTA && (
          <div className="pa-sticky-cta" data-testid="landing-sticky-cta">
            <button
              className="pa-cta"
              onClick={() => { trackAB(heroVariant, 'cta_click'); scrollToForm(); }}
              data-testid="landing-sticky-cta-btn"
            >
              Ma lecture · 97€
            </button>
          </div>
        )}

        {/* ═══ SECTION 11 · PIED DE PAGE ═══ */}
        <footer className="pa-footer">
          <div className="pa-footer-wrap">
            <div>
              <div className="pa-footer-brand">Plume Astrale</div>
              <p className="pa-footer-mentions" style={{ marginTop: 10 }}>
                Guidance symbolique à visée de <strong>divertissement</strong> et de développement personnel.
                Soléna est un guide incarné par un avatar. Les lectures ne constituent ni un avis médical,
                ni psychologique, ni financier.
              </p>
            </div>
            <div>
              <div style={{ marginBottom: 10, color: '#a09cb0' }}>Liens utiles</div>
              <Link to="/notre-cadre">Notre cadre</Link>
              <Link to="/charte-confiance">Charte de confiance</Link>
              <Link to="/contact">Contact</Link>
              <div style={{ marginTop: 18, fontSize: '.72rem', color: '#5f5c72' }}>
                © {new Date().getFullYear()} Plume Astrale · Tous droits réservés
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
