import type { Context, Config } from "@netlify/edge-functions";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

const TAROT_CARDS = [
  "Le Soleil",
  "La Lune",
  "L'Étoile",
  "Le Monde",
  "Le Bateleur",
  "La Roue de Fortune",
  "La Justice",
  "L'Impératrice",
  "Le Mat",
  "La Papesse",
  "L'Ermite",
  "La Force",
  "Le Pendu",
  "La Tempérance",
  "La Maison Dieu",
  "Le Jugement",
];

export default async (req: Request, context: Context) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: CORS_HEADERS });
  }

  try {
    const { name, sign, lifePath } = await req.json();

    if (!name || !sign) {
      return new Response(
        JSON.stringify({ error: "Champs 'name' et 'sign' requis." }),
        { status: 400, headers: { "Content-Type": "application/json", ...CORS_HEADERS } }
      );
    }

    // 1. ASTROLOGY API (données réelles)
    const astroUserId = Netlify.env.get("ASTROLOGY_API_USER_ID");
    const astroApiKey = Netlify.env.get("ASTROLOGY_API_KEY");

    let astroData: { prediction?: string } = {};

    if (astroUserId && astroApiKey) {
      const auth = btoa(`${astroUserId}:${astroApiKey}`);

      const astroRes = await fetch(
        "https://json.astrologyapi.com/v1/horoscope_prediction/daily/sun",
        {
          method: "POST",
          headers: {
            Authorization: "Basic " + auth,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            sign: sign.toLowerCase(),
            day: "today",
          }),
        }
      );

      if (astroRes.ok) {
        astroData = await astroRes.json();
      }
    }

    // 2. TAROT DYNAMIQUE
    const tarotCard = TAROT_CARDS[Math.floor(Math.random() * TAROT_CARDS.length)];

    // 3. SCORE ÉNERGÉTIQUE (basé sur horoscope)
    let energyScore = Math.floor(Math.random() * 30) + 70;

    if (astroData.prediction?.includes("difficult")) {
      energyScore = Math.floor(Math.random() * 30) + 40;
    }

    // 4. PROMPT IA
    const horoscopeText = astroData.prediction || "Énergie cosmique en mouvement.";

    const prompt = `Tu es un guide spirituel expert.

Données réelles :
Horoscope du jour :
${horoscopeText}

Carte de tarot : ${tarotCard}
Chemin de vie : ${lifePath || "Non précisé"}
Score énergétique : ${energyScore}%

Crée un journal cosmique personnalisé pour ${name}.

Style :
- Mystique
- Poétique
- Fluide
- Très humain

Structure naturelle :
- Introduction immersive
- Énergie du jour (basée horoscope réel)
- Message émotionnel
- Guidance tarot
- Conseil concret
- Affirmation
- Conclusion inspirante

IMPORTANT :
Ce texte doit sembler écrit UNIQUEMENT pour cette personne.`;

    // 5. APPEL OPENAI via Netlify AI Gateway
    const openaiBaseUrl = Netlify.env.get("OPENAI_BASE_URL") || "https://api.openai.com";
    const openaiKey = Netlify.env.get("OPENAI_API_KEY");

    if (!openaiKey) {
      return new Response(
        JSON.stringify({ error: "Configuration OpenAI manquante." }),
        { status: 500, headers: { "Content-Type": "application/json", ...CORS_HEADERS } }
      );
    }

    const aiRes = await fetch(`${openaiBaseUrl}/v1/chat/completions`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${openaiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [
          {
            role: "system",
            content: "Tu es un guide spirituel profond et inspirant.",
          },
          { role: "user", content: prompt },
        ],
        temperature: 0.9,
      }),
    });

    if (!aiRes.ok) {
      const errBody = await aiRes.text();
      return new Response(
        JSON.stringify({ error: "Erreur OpenAI", status: aiRes.status }),
        { status: 502, headers: { "Content-Type": "application/json", ...CORS_HEADERS } }
      );
    }

    const aiData = await aiRes.json();

    // 6. RÉPONSE STRUCTURÉE
    return new Response(
      JSON.stringify({
        journal: aiData.choices[0].message.content,
        meta: {
          tarot: tarotCard,
          energy: energyScore,
          sign: sign,
        },
      }),
      {
        headers: { "Content-Type": "application/json", ...CORS_HEADERS },
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: "Erreur backend",
        details: (error as Error).message,
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json", ...CORS_HEADERS },
      }
    );
  }
};

export const config: Config = {
  path: "/api/journal",
  method: ["POST", "OPTIONS"],
};
