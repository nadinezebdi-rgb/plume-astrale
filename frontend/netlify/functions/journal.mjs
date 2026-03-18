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
      ? `Rédige une analyse approfondie et détaillée. Le texte doit être long et riche, au moins 800 mots. Chaque section doit contenir des interprétations précises et des recommandations concrètes basées sur les données astrologiques. Ce rapport est exclusivement destiné à ${name}.`
      : `Rédige une analyse concise mais précise, environ 300 mots.`;

    const prompt = `Tu es un astrologue professionnel reconnu. Tu rédiges des analyses astrales basées sur des calculs astronomiques précis issus d'éphémérides certifiées.

Rédige l'analyse astrale personnalisée du jour.

Données du consultant :
- Prénom : ${name}
- Signe solaire : ${sign}
- Chemin de vie numérologique : ${lifePath || 'non renseigné'}
- Arcane majeur du jour : ${tarotCard || 'Le Soleil'}
- Indice vibratoire : ${energyScore || 75}%

Structure OBLIGATOIRE du rapport :

1. Introduction personnalisée (adresse-toi à ${name} avec respect et bienveillance)
2. Analyse des énergies planétaires du jour (en lien avec le signe ${sign})
3. Lecture émotionnelle et affective (basée sur les transits actuels)
4. Interprétation de l'arcane majeur (${tarotCard || 'Le Soleil'} et sa signification pour aujourd'hui)
5. Guidance numérologique (conseil d'action lié au chemin de vie)
6. Affirmation vibratoire du jour
7. Synthèse et perspective

Style d'écriture :
- Professionnel et bienveillant
- Vocabulaire astrologique précis
- Ton chaleureux mais expert
- Fluide et immersif

RÈGLES IMPÉRATIVES :
- Rédige en prose continue, jamais de listes à puces
- Ne mentionne JAMAIS l'intelligence artificielle, le machine learning, ou le fait que ce texte est généré
- Écris comme un astrologue humain expérimenté qui a étudié la carte du ciel
- Utilise des références aux positions planétaires, aux maisons astrales, aux aspects et transits
- Français uniquement
- ${premiumInstruction}
- Ce rapport est rédigé exclusivement pour ${name}, personnalise chaque interprétation.`;

    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'Tu es un astrologue professionnel avec 30 ans d\'expérience. Tu rédiges des analyses astrales personnalisées basées sur les éphémérides astronomiques et les calculs de la plateforme Astrology API. Tu ne mentionnes jamais l\'intelligence artificielle. Tu écris avec l\'expertise et la précision d\'un professionnel de l\'astrologie.' },
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
