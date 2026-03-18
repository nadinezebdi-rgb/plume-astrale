import OpenAI from 'openai';

const openai = new OpenAI();

export default async (req, context) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  }

  if (req.method !== 'POST') {
    return Response.json({ error: 'Method not allowed' }, { status: 405 });
  }

  try {
    const { name, sign, lifePath, tarotCard, energyScore, isPremium } = await req.json();

    if (!name || !sign) {
      return Response.json({ error: 'name and sign are required' }, { status: 400 });
    }

    const premiumInstruction = isPremium
      ? `Ajoute une profondeur émotionnelle, des conseils puissants et une guidance détaillée. Le texte doit être long et riche, au moins 800 mots. Ce message est destiné UNIQUEMENT à cette personne, fais-le ressentir à chaque ligne.`
      : `Version courte et simple, environ 300 mots.`;

    const prompt = `Tu es un guide spirituel poétique.

Génère un journal cosmique personnalisé.

Données utilisateur :
- Prénom : ${name}
- Signe astrologique : ${sign}
- Chemin de vie : ${lifePath || 'non renseigné'}
- Carte de tarot du jour : ${tarotCard || 'Le Soleil'}
- Score énergétique : ${energyScore || 75}%

Structure OBLIGATOIRE :

1. Introduction poétique (Bonjour belle âme… avec prénom)
2. Énergie du jour (influencée par le signe)
3. Message du cœur (émotionnel)
4. Guidance tarot (basée sur la carte)
5. Conseil action (numérologie chemin de vie)
6. Affirmation du jour
7. Clôture inspirante

Ton :
- Mystique
- Bienveillant
- Inspirant
- Fluide et naturel

IMPORTANT :
- Texte immersif
- Pas de listes à puces
- Pas de format robotique
- Français uniquement
- ${premiumInstruction}
- Ce message est écrit spécialement pour ${name}, fais-le ressentir dans chaque mot.`;

    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'Tu es un guide spirituel expert en astrologie, tarot et numérologie. Tu écris avec poésie et bienveillance.' },
        { role: 'user', content: prompt },
      ],
      temperature: 0.9,
      max_tokens: isPremium ? 2000 : 800,
    });

    const journal = completion.choices[0].message.content;

    return Response.json({ journal }, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('Journal generation error:', error);
    return Response.json(
      { error: 'Failed to generate journal' },
      { status: 500 },
    );
  }
};

export const config = {
  path: '/api/journal',
};
