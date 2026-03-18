import { jsonResponse } from '../lib/auth-helpers.mjs';

const CREDIT_PACKS = {
  decouverte: {
    name: 'Pack Découverte',
    credits: 10,
    amount: 9.00,
    currency: 'eur',
    description: '10 crédits pour explorer nos services',
  },
  exploration: {
    name: 'Pack Exploration',
    credits: 50,
    amount: 24.99,
    currency: 'eur',
    description: '50 crédits — notre meilleur rapport qualité-prix',
  },
  premium: {
    name: 'Pack Premium',
    credits: 100,
    amount: 44.99,
    currency: 'eur',
    description: '100 crédits pour un accès complet',
  },
};

export default async () => {
  const packs = Object.entries(CREDIT_PACKS).map(([id, pack]) => ({
    id,
    ...pack,
  }));
  return jsonResponse({ packs });
};

export const config = {
  path: '/api/credits/packs',
  method: 'GET',
};
