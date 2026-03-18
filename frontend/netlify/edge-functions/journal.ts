import type { Config, Context } from "@netlify/edge-functions";

export default async (request: Request, context: Context) => {
  const { name, sign, lifePath, tarotCard, energyScore } =
    await request.json();

  const prompt = `
Bonjour belle âme ${name} ✨

Crée un journal cosmique poétique et immersif.

Données :
- signe : ${sign}
- chemin de vie : ${lifePath}
- tarot : ${tarotCard}
- énergie : ${energyScore}%

Structure fluide :
- introduction
- énergie du jour
- message du cœur
- guidance tarot
- conseil
- affirmation
- conclusion

Ton : mystique, doux, puissant, naturel.
`;

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${Netlify.env.get("OPENAI_API_KEY")}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.9,
    }),
  });

  const data = await response.json();

  return new Response(
    JSON.stringify({
      journal: data.choices[0].message.content,
    }),
    {
      headers: { "Content-Type": "application/json" },
    }
  );
};

export const config: Config = {
  path: "/.netlify/edge-functions/journal",
  method: "POST",
};
