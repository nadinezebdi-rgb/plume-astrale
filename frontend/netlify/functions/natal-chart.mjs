const ASTROLOGY_API_BASE = "https://json.astrologyapi.com/v1";

function getAuthHeader() {
  const env = globalThis.Netlify?.env;
  const userId = env?.get("ASTROLOGY_API_USER_ID");
  const apiKey = env?.get("ASTROLOGY_API_KEY");
  return "Basic " + btoa(`${userId}:${apiKey}`);
}

async function callAPI(endpoint, body) {
  const res = await fetch(`${ASTROLOGY_API_BASE}${endpoint}`, {
    method: "POST",
    headers: {
      "Authorization": getAuthHeader(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}`);
  }
  return res.json();
}

function getZodiacSignFr(signEn) {
  const map = {
    "Aries": "Bélier", "Taurus": "Taureau", "Gemini": "Gémeaux",
    "Cancer": "Cancer", "Leo": "Lion", "Virgo": "Vierge",
    "Libra": "Balance", "Scorpio": "Scorpion", "Sagittarius": "Sagittaire",
    "Capricorn": "Capricorne", "Aquarius": "Verseau", "Pisces": "Poissons",
  };
  return map[signEn] || signEn;
}

function getPlanetFr(name) {
  const map = {
    "Sun": "Soleil", "Moon": "Lune", "Mars": "Mars", "Mercury": "Mercure",
    "Jupiter": "Jupiter", "Venus": "Vénus", "Saturn": "Saturne",
    "Uranus": "Uranus", "Neptune": "Neptune", "Pluto": "Pluton",
    "Node": "Nœud Nord", "Ascendant": "Ascendant",
  };
  return map[name] || name;
}

export default async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });
  }

  if (req.method !== "POST") {
    return Response.json({ error: "Method not allowed" }, { status: 405 });
  }

  try {
    const body = await req.json();
    const { day, month, year, hour, min, lat, lon, tzone } = body;

    if (!day || !month || !year) {
      return Response.json({ error: "Missing birth data" }, { status: 400 });
    }

    const params = {
      day: parseInt(day),
      month: parseInt(month),
      year: parseInt(year),
      hour: parseInt(hour || 12),
      min: parseInt(min || 0),
      lat: parseFloat(lat || 48.8566),
      lon: parseFloat(lon || 2.3522),
      tzone: parseFloat(tzone || 1),
    };

    const [planets, astroDetails] = await Promise.all([
      callAPI("/planets/tropical", params),
      callAPI("/astro_details", params),
    ]);

    const formattedPlanets = planets.map((p) => ({
      nom: getPlanetFr(p.name),
      signe: getZodiacSignFr(p.sign),
      signeFull: p.fullDegree,
      maison: p.house,
      retrograde: p.isRetro === "true",
      degre: p.normDegree,
    }));

    const sunPlanet = planets.find((p) => p.name === "Sun");
    const moonPlanet = planets.find((p) => p.name === "Moon");
    const ascendant = planets.find((p) => p.name === "Ascendant");

    const result = {
      success: true,
      data: {
        soleil: sunPlanet ? { signe: getZodiacSignFr(sunPlanet.sign), degre: sunPlanet.normDegree } : null,
        lune: moonPlanet ? { signe: getZodiacSignFr(moonPlanet.sign), degre: moonPlanet.normDegree } : null,
        ascendant: ascendant ? { signe: getZodiacSignFr(ascendant.sign), degre: ascendant.normDegree } : null,
        planetes: formattedPlanets,
        details: {
          sunrise: astroDetails.sunrise,
          sunset: astroDetails.sunset,
          ayanamsha: astroDetails.ayanamsha,
        },
      },
    };

    return Response.json(result, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
      },
    });
  } catch (err) {
    return Response.json(
      { success: false, error: err.message },
      { status: 500, headers: { "Access-Control-Allow-Origin": "*" } }
    );
  }
};

export const config = {
  path: "/api/astrology/natal-chart",
};
