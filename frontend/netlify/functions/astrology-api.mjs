const ASTROLOGY_API_BASE = "https://json.astrologyapi.com/v1";

function getAuthHeader() {
  const userId = Netlify.env.get("ASTROLOGY_API_USER_ID");
  const apiKey = Netlify.env.get("ASTROLOGY_API_KEY");
  if (!userId || !apiKey) {
    throw new Error("Astrology API credentials not configured");
  }
  return "Basic " + btoa(`${userId}:${apiKey}`);
}

async function callAstrologyAPI(endpoint, body) {
  const res = await fetch(`${ASTROLOGY_API_BASE}${endpoint}`, {
    method: "POST",
    headers: {
      "Authorization": getAuthHeader(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Astrology API error ${res.status}: ${text}`);
  }

  return res.json();
}

function parseRequestBody(body) {
  const { day, month, year, hour, min, lat, lon, tzone, lang } = body;
  return {
    day: parseInt(day),
    month: parseInt(month),
    year: parseInt(year),
    hour: parseInt(hour),
    min: parseInt(min),
    lat: parseFloat(lat),
    lon: parseFloat(lon),
    tzone: parseFloat(tzone),
    ...(lang && { lang }),
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
    const { endpoint } = body;

    if (!endpoint) {
      return Response.json({ error: "Missing 'endpoint' field" }, { status: 400 });
    }

    const allowedEndpoints = [
      "/planets",
      "/planets/tropical",
      "/natal_wheel_chart",
      "/horoscope_prediction/daily/sun",
      "/horoscope_prediction/daily/moon",
      "/horoscope_prediction/weekly/sun",
      "/horoscope_prediction/monthly/sun",
      "/general_house_report/tropical",
      "/general_ascendant_report",
      "/general_nakshatra_report",
      "/sun_sign_prediction/daily",
      "/sun_sign_prediction/weekly",
      "/sun_sign_prediction/monthly",
      "/western_horoscope",
      "/numero_table",
      "/astro_details",
    ];

    if (!allowedEndpoints.includes(endpoint)) {
      return Response.json({ error: "Endpoint not allowed" }, { status: 403 });
    }

    const apiBody = parseRequestBody(body);
    const data = await callAstrologyAPI(endpoint, apiBody);

    return Response.json({ success: true, data }, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
      },
    });
  } catch (err) {
    return Response.json(
      { success: false, error: err.message },
      {
        status: 500,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
      }
    );
  }
};

export const config = {
  path: "/api/astrology-proxy",
};
