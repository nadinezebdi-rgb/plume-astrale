const ASTROLOGY_API_BASE = "https://json.astrologyapi.com/v1";

function getAuthHeader() {
  const userId = Netlify.env.get("ASTROLOGY_API_USER_ID");
  const apiKey = Netlify.env.get("ASTROLOGY_API_KEY");
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

function getTodayParams(tzone = 1) {
  const now = new Date();
  return {
    day: now.getDate(),
    month: now.getMonth() + 1,
    year: now.getFullYear(),
    hour: now.getHours(),
    min: now.getMinutes(),
    lat: 48.8566,
    lon: 2.3522,
    tzone,
  };
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
    const { day, month, year, hour, min, lat, lon, tzone, period } = body;

    const params = {
      day: parseInt(day || new Date().getDate()),
      month: parseInt(month || new Date().getMonth() + 1),
      year: parseInt(year || new Date().getFullYear()),
      hour: parseInt(hour || 12),
      min: parseInt(min || 0),
      lat: parseFloat(lat || 48.8566),
      lon: parseFloat(lon || 2.3522),
      tzone: parseFloat(tzone || 1),
    };

    let endpoint = "/sun_sign_prediction/daily";
    if (period === "weekly") {
      endpoint = "/sun_sign_prediction/weekly";
    } else if (period === "monthly") {
      endpoint = "/sun_sign_prediction/monthly";
    }

    const [prediction, planets] = await Promise.all([
      callAPI(endpoint, params),
      callAPI("/planets/tropical", params),
    ]);

    const sunPlanet = planets.find((p) => p.name === "Sun");
    const signe = sunPlanet ? getZodiacSignFr(sunPlanet.sign) : "Inconnu";

    const result = {
      success: true,
      data: {
        signe,
        period: period || "daily",
        prediction: prediction.prediction || prediction,
        sun_sign: sunPlanet ? sunPlanet.sign : null,
        planets_summary: planets
          .filter((p) => ["Sun", "Moon", "Venus", "Mars", "Mercury", "Jupiter"].includes(p.name))
          .map((p) => ({
            nom: p.name,
            signe: getZodiacSignFr(p.sign),
            retrograde: p.isRetro === "true",
          })),
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
  path: "/api/astrology/horoscope-prediction",
};
