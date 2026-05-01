const CHAT_API_URL = "https://json-chat.astrologyapi.com/api/chat";

function getAuthHeader() {
  const userId = Netlify.env.get("ASTROLOGY_API_USER_ID");
  const apiKey = Netlify.env.get("ASTROLOGY_API_KEY");
  if (!userId || !apiKey) {
    throw new Error("Astrology API credentials not configured");
  }
  return "Basic " + btoa(`${userId}:${apiKey}`);
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
    const { message, name, day, month, year, hour, min, lat, lon, tzone, lang } = body;

    if (!message) {
      return Response.json({ error: "Missing 'message' field" }, { status: 400 });
    }

    const chatBody = {
      message,
      ...(name && { name }),
      day: parseInt(day || 1),
      month: parseInt(month || 1),
      year: parseInt(year || 2000),
      hour: parseInt(hour || 12),
      min: parseInt(min || 0),
      lat: parseFloat(lat || 48.8566),
      lon: parseFloat(lon || 2.3522),
      tzone: parseFloat(tzone || 1),
      lang: lang || "fr",
    };

    const res = await fetch(CHAT_API_URL, {
      method: "POST",
      headers: {
        "Authorization": getAuthHeader(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify(chatBody),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Chat API error ${res.status}: ${text}`);
    }

    const data = await res.json();

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
  path: "/api/astrology/chat",
};
