/**
 * Générateurs de textures de cartes V2 — dessinées en canvas 2D à la volée.
 * Retourne des data-URLs à utiliser comme background-image CSS.
 *
 * Deux faces :
 *   - VERSO : noir → violet profond radial, double bordure d'or fine, étoile 6-branches
 *   - RECTO : "L'Étoile Intérieure" — étoile 7 rayons + cercle pointillé + numérotation XVII
 */

const W = 400;
const H = 600;

function makeBackTexture() {
  if (typeof document === 'undefined') return '';
  const c = document.createElement('canvas');
  c.width = W; c.height = H;
  const ctx = c.getContext('2d');

  // Fond radial noir → violet profond
  const bg = ctx.createRadialGradient(W / 2, H / 2, 0, W / 2, H / 2, H * 0.7);
  bg.addColorStop(0, '#17102E');
  bg.addColorStop(0.6, '#0C0918');
  bg.addColorStop(1, '#060314');
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, W, H);

  // Vignette sombre en bordure
  const vig = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.75);
  vig.addColorStop(0, 'rgba(0,0,0,0)');
  vig.addColorStop(1, 'rgba(0,0,0,0.7)');
  ctx.fillStyle = vig;
  ctx.fillRect(0, 0, W, H);

  // Double bordure d'or à 8px et 14px
  ctx.strokeStyle = 'rgba(216, 183, 106, 0.6)';
  ctx.lineWidth = 1;
  ctx.strokeRect(8, 8, W - 16, H - 16);
  ctx.strokeStyle = 'rgba(216, 183, 106, 0.28)';
  ctx.strokeRect(14, 14, W - 28, H - 28);

  // Étoile 6 branches au centre (trait or fin)
  ctx.save();
  ctx.translate(W / 2, H / 2);
  ctx.strokeStyle = 'rgba(216, 183, 106, 0.7)';
  ctx.lineWidth = 1.2;
  const R = 60;
  const r = 22;
  ctx.beginPath();
  for (let i = 0; i < 12; i++) {
    const angle = (Math.PI * 2 * i) / 12 - Math.PI / 2;
    const radius = i % 2 === 0 ? R : r;
    const x = Math.cos(angle) * radius;
    const y = Math.sin(angle) * radius;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.stroke();

  // Petit cercle central
  ctx.beginPath();
  ctx.arc(0, 0, 4, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(232, 199, 102, 0.85)';
  ctx.fill();
  ctx.restore();

  return c.toDataURL('image/png');
}

function makeFaceTexture() {
  if (typeof document === 'undefined') return '';
  const c = document.createElement('canvas');
  c.width = W; c.height = H;
  const ctx = c.getContext('2d');

  // Fond navy profond
  const bg = ctx.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, '#0F0B26');
  bg.addColorStop(1, '#060314');
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, W, H);

  // Vignette
  const vig = ctx.createRadialGradient(W / 2, H / 2, H * 0.25, W / 2, H / 2, H * 0.75);
  vig.addColorStop(0, 'rgba(216, 183, 106, 0.10)');
  vig.addColorStop(1, 'rgba(0,0,0,0.65)');
  ctx.fillStyle = vig;
  ctx.fillRect(0, 0, W, H);

  // Double bordure d'or
  ctx.strokeStyle = 'rgba(216, 183, 106, 0.55)';
  ctx.lineWidth = 1;
  ctx.strokeRect(8, 8, W - 16, H - 16);
  ctx.strokeStyle = 'rgba(216, 183, 106, 0.22)';
  ctx.strokeRect(14, 14, W - 28, H - 28);

  // Numérotation romaine "XVII" en haut
  ctx.fillStyle = 'rgba(232, 199, 102, 0.75)';
  ctx.textAlign = 'center';
  ctx.font = 'italic 500 22px "Cormorant Garamond", Georgia, serif';
  ctx.fillText('XVII', W / 2, 44);

  // ─── Illustration : étoile 7 rayons + cercle pointillé ───
  ctx.save();
  ctx.translate(W / 2, H / 2 - 20);

  // Cercle extérieur pointillé
  ctx.strokeStyle = 'rgba(216, 183, 106, 0.35)';
  ctx.lineWidth = 1;
  ctx.setLineDash([2, 4]);
  ctx.beginPath();
  ctx.arc(0, 0, 110, 0, Math.PI * 2);
  ctx.stroke();
  ctx.setLineDash([]);

  // Rayons partant du centre (7 rayons pour l'Étoile Intérieure)
  ctx.strokeStyle = 'rgba(232, 199, 102, 0.7)';
  ctx.lineWidth = 1.4;
  for (let i = 0; i < 7; i++) {
    const angle = (Math.PI * 2 * i) / 7 - Math.PI / 2;
    ctx.beginPath();
    ctx.moveTo(Math.cos(angle) * 15, Math.sin(angle) * 15);
    ctx.lineTo(Math.cos(angle) * 90, Math.sin(angle) * 90);
    ctx.stroke();
  }

  // Petites étoiles secondaires sur le cercle
  for (let i = 0; i < 7; i++) {
    const angle = (Math.PI * 2 * i) / 7 - Math.PI / 2;
    const x = Math.cos(angle) * 110;
    const y = Math.sin(angle) * 110;
    ctx.beginPath();
    ctx.arc(x, y, 2.2, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 246, 220, 0.9)';
    ctx.fill();
  }

  // Étoile centrale (halo doux)
  const halo = ctx.createRadialGradient(0, 0, 0, 0, 0, 20);
  halo.addColorStop(0, 'rgba(255, 246, 220, 1)');
  halo.addColorStop(0.4, 'rgba(232, 199, 102, 0.7)');
  halo.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = halo;
  ctx.fillRect(-25, -25, 50, 50);
  // Cœur brillant
  ctx.beginPath();
  ctx.arc(0, 0, 5, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(255, 246, 220, 1)';
  ctx.fill();

  ctx.restore();

  // ─── Nom de la carte ───
  ctx.fillStyle = 'rgba(232, 199, 102, 0.95)';
  ctx.textAlign = 'center';
  ctx.font = 'italic 500 26px "Cormorant Garamond", Georgia, serif';
  ctx.fillText("L'Étoile Intérieure", W / 2, H - 78);

  // Tagline
  ctx.fillStyle = 'rgba(244, 239, 230, 0.55)';
  ctx.font = '400 10.5px "Inter", sans-serif';
  ctx.textAlign = 'center';
  const tagline = 'CE QUI VOUS ÉCLAIRE QUAND TOUT S\'ÉTEINT';
  ctx.fillText(tagline, W / 2, H - 54);

  // Petit ornement doré en bas
  ctx.strokeStyle = 'rgba(216, 183, 106, 0.5)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(W / 2 - 30, H - 38);
  ctx.lineTo(W / 2 + 30, H - 38);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(W / 2, H - 38, 2.5, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(232, 199, 102, 0.85)';
  ctx.fill();

  return c.toDataURL('image/png');
}

let _backCache = null;
let _faceCache = null;

export function getCardBackTexture() {
  if (_backCache === null) _backCache = makeBackTexture();
  return _backCache;
}

export function getCardFaceTexture() {
  if (_faceCache === null) _faceCache = makeFaceTexture();
  return _faceCache;
}
