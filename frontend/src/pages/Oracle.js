import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { EnrichedBadge } from "../components/EnrichedBadge";

export default function Oracle() {
  const { creditBalance } = useAuth();

  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [enriched, setEnriched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askOracle = async () => {
    if (!question) return;

    if (creditBalance <= 0) {
      window.location.href = "/acheter-credits";
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await fetch("/api/oracle", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
        }),
      });

      const data = await res.json();

      setResponse(data.answer || "Réponse indisponible");
      setEnriched(!!data.enrichi);

    } catch (err) {
      setError("Erreur Oracle");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center px-4">

      <h1 className="text-3xl mb-6">Ton Oracle personnel</h1>

      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Pose ta question..."
        className="border p-3 w-full max-w-md mb-4"
      />

      <button
        onClick={askOracle}
        className="bg-black text-white px-6 py-3"
      >
        {loading ? "Consultation..." : "Recevoir ma réponse"}
      </button>

      {response && (
        <div className="mt-6 max-w-md">
          <EnrichedBadge variant="compact" visible={enriched} align="center" />
          <p style={{ whiteSpace: 'pre-wrap' }}>{response}</p>

          <button
            className="mt-4 text-yellow-500"
            onClick={() => window.location.href = "/acheter-credits"}
          >
            Continuer la discussion →
          </button>
        </div>
      )}

      {error && <p className="text-red-500">{error}</p>}
    </div>
  );
}
