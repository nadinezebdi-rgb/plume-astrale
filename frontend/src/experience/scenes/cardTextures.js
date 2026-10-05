/**
 * Générateurs de textures de cartes V2 — dessinées en canvas 2D à la volée.
 * Retourne des data-URLs à utiliser comme background-image CSS.
 *
 * Deux faces : verso personnalisé et recto illustré depuis la bibliothèque tarot.
 */

const W = 400;
const H = 600;
const CARD_BACK_TEXTURE = '/api/library/file/tarot/plume-astrale-card-back.jpg';
const CARD_FACE_ASSETS = [
  '00_le_mat', '01_le_bateleur', '02_la_papesse', '03_l_imperatrice',
  '04_l_empereur', '05_le_pape', '06_les_amoureux', '07_le_chariot',
  '08_la_force', '09_l_hermite', '10_la_roue_de_fortune', '11_la_justice',
  '12_le_pendu', '13_la_mort', '14_la_temperance', '15_le_diable',
  '16_la_maison_dieu', '17_l_etoile', '18_la_lune', '19_le_soleil',
  '20_le_jugement', '21_le_monde',
];
const CARD_FACE_BASE_URL = 'https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/library/tarot';
const ROMAN_ARCANA = [
  '0', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
  'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX', 'XXI',
];

function makeFaceTexture(card = {}) {
  if (typeof document === 'undefined') return '';
  const c = document.createElement('canvas');
  c.width = W; c.height = H;
  const ctx = c.getContext('2d');
  const number = Number(card.numero ?? card.number);
  const cardName = typeof card.nom === 'string'
    ? card.nom
    : typeof card.name === 'string'
      ? card.name
      : card.name?.fr || card.name?.en || 'Arcane du jour';

  // A pale face keeps the drawn arcana visibly distinct from the dark card back.
  const bg = ctx.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, '#F3EADB');
  bg.addColorStop(1, '#D9CBB4');
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, W, H);

  ctx.strokeStyle = 'rgba(121, 87, 15, 0.82)';
  ctx.lineWidth = 2;
  ctx.strokeRect(12, 12, W - 24, H - 24);
  ctx.strokeStyle = 'rgba(121, 87, 15, 0.42)';
  ctx.lineWidth = 1;
  ctx.strokeRect(19, 19, W - 38, H - 38);

  ctx.fillStyle = '#59452B';
  ctx.textAlign = 'center';
  ctx.font = '500 24px "Cormorant Garamond", Georgia, serif';
  ctx.fillText(ROMAN_ARCANA[number] || '✦', W / 2, 52);

  ctx.save();
  ctx.translate(W / 2, H / 2 - 20);

  // A bespoke geometric emblem stands in for missing source artwork.
  ctx.strokeStyle = 'rgba(89, 69, 43, 0.78)';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.arc(0, 0, 112, 0, Math.PI * 2);
  ctx.stroke();

  ctx.strokeStyle = 'rgba(121, 87, 15, 0.75)';
  for (let i = 0; i < 8; i++) {
    const angle = (Math.PI * 2 * i) / 8 - Math.PI / 2;
    ctx.beginPath();
    ctx.moveTo(Math.cos(angle) * 22, Math.sin(angle) * 22);
    ctx.lineTo(Math.cos(angle) * 94, Math.sin(angle) * 94);
    ctx.stroke();
  }

  ctx.beginPath();
  ctx.arc(0, 0, 38 + (Number.isFinite(number) ? number % 16 : 0), 0, Math.PI * 2);
  ctx.strokeStyle = 'rgba(89, 69, 43, 0.7)';
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(0, 0, 8, 0, Math.PI * 2);
  ctx.fillStyle = '#79570F';
  ctx.fill();
  ctx.restore();

  ctx.fillStyle = '#3A3026';
  ctx.textAlign = 'center';
  ctx.font = '500 27px "Cormorant Garamond", Georgia, serif';
  let title = cardName;
  while (ctx.measureText(title).width > W - 48 && title.length > 8) title = `${title.slice(0, -2)}…`;
  ctx.fillText(title, W / 2, H - 72);

  ctx.fillStyle = 'rgba(58, 48, 38, 0.72)';
  ctx.font = '400 10px "Inter", sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('TAROT DE MARSEILLE', W / 2, H - 48);

  return c.toDataURL('image/png');
}

const _faceCache = new Map();

export function getCardBackTexture() {
  return CARD_BACK_TEXTURE;
}

export function getCardFaceTexture(card = {}) {
  if (typeof card === 'string') card = { nom: card };
  if (card.image_url) return card.image_url;
  const number = Number(card.numero ?? card.number);
  const artSlug = Number.isInteger(number) ? CARD_FACE_ASSETS[number] : null;
  if (artSlug) return `${CARD_FACE_BASE_URL}/${artSlug}_512.png`;

  const name = card.nom || card.name?.fr || card.name?.en || card.name || 'Arcane du jour';
  const cacheKey = `${number}:${name}`;
  if (!_faceCache.has(cacheKey)) _faceCache.set(cacheKey, makeFaceTexture({ ...card, numero: number, nom: name }));
  return _faceCache.get(cacheKey);
}
