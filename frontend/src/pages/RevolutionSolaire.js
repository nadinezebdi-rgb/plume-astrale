import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowLeft, Loader2, Sun, Moon, Star, Flame, Heart, Compass, ArrowRight } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

/** Composant affichant les transits du jour appliques au theme natal de l'utilisateur. */
const TransitsToday = () => {
  const { isAuthenticated, user, token } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated || !user?.birth_date) return;
    let cancel = false;
    (async () => {
      setLoading(true); setError('');
      try {
        const res = await axios.post(`${API_URL}/api/astrology/v3/transits/today`, {},
          { headers: { Authorization: `Bearer ${token}` } });
        if (!cancel && res.data?.success) setData(res.data);
      } catch (e) {
        if (!cancel) setError('Transits indisponibles aujourd\'hui.');
      }
      if (!cancel) setLoading(false);
    })();
    return () => { cancel = true; };
  }, [isAuthenticated, user?.birth_date, token]);

  if (!isAuthenticated || !user?.birth_date) return null;

  const aspects = (() => {
    const chart = data?.chart || {};
    const arr = chart.aspects || chart.synastry_aspects || (chart.chart_data || {}).aspects || [];
    return (Array.isArray(arr) ? arr : []).slice(0, 5);
  })();

  const report = data?.report || {};
  const reportText = report.summary || report.text || (report.life_areas || {}).summary || '';

  return (
    <section className="card-mystical mb-8" data-testid="transits-today">
      <div className="flex items-center gap-2 mb-4">
        <Compass className="w-5 h-5 text-[#C5A059]" strokeWidth={1.5} />
        <h2 className="text-xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
          Transits du jour sur votre thème
        </h2>
      </div>
      <p className="text-[#B8B0C8]/70 text-sm mb-5 font-light">
        Comment les planètes actuelles activent votre carte natale, en temps réel.
      </p>

      {loading && (
        <div className="flex items-center gap-2 text-[#C5A059]/70 text-sm" data-testid="transits-loading">
          <Loader2 className="w-4 h-4 animate-spin" /> Calcul des transits...
        </div>
      )}
      {error && <p className="text-amber-300/70 text-sm" data-testid="transits-error">{error}</p>}

      {data && (
        <div>
          {aspects.length > 0 && (
            <ul className="space-y-3 mb-5" data-testid="transits-aspects">
              {aspects.map((a, i) => (
                <li key={i} className="flex items-start gap-3 text-sm">
                  <Sparkles className="w-4 h-4 text-[#C5A059] mt-0.5" strokeWidth={1.5} />
                  <div>
                    <span className="text-[#F0E6D3]">
                      {(a.point_1 || a.planet_1 || a.first_planet || '')} {(a.aspect_name || a.aspect || a.type || '')} {(a.point_2 || a.planet_2 || a.second_planet || '')}
                    </span>
                    {(a.orb !== undefined || a.orb_value !== undefined) && (
                      <span className="text-[#B8B0C8]/50 ml-2 text-xs">
                        orbe {Number(a.orb || a.orb_value).toFixed(2)}°
                      </span>
                    )}
                    {a.description && <p className="text-[#B8B0C8]/70 mt-0.5 text-xs">{a.description}</p>}
                  </div>
                </li>
              ))}
            </ul>
          )}
          {reportText && (
            <p className="text-[#F0E6D3]/90 leading-relaxed" style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: '16px', lineHeight: '1.85' }} data-testid="transits-report">
              {reportText}
            </p>
          )}
        </div>
      )}
    </section>
  );
};


const RevolutionSolaire = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, token } = useAuth();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [unlocked, setUnlocked] = useState(false);

  const handleGenerate = async () => {
    if (!isAuthenticated) { navigate('/connexion?next=/revolution-solaire'); return; }
    if (!user?.birth_date) {
      setError('Renseignez vos données natales depuis Mon Compte.');
      return;
    }
    setError(''); setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/api/astrology/v3/solar-return`, {},
        { headers: { Authorization: `Bearer ${token}` } });
      if (res.data?.success) setResult(res.data);
      else setError('Service astrologique indisponible.');
    } catch (e) {
      const status = e.response?.status;
      if (status === 402) {
        navigate('/acheter-credits');
        return;
      }
      setError(e.response?.data?.detail || 'Erreur lors du calcul de la révolution solaire.');
    }
    setLoading(false);
  };

  const report = result?.report || {};
  const chart = result?.chart || {};
  const lifeAreas = report.life_areas || {};
  const themes = report.themes || report.major_themes || [];

  return (
    <div className="min-h-screen px-6 md:px-8 py-20 md:py-28" data-testid="revolution-page">
      <div className="max-w-3xl mx-auto">
        <button onClick={() => navigate(-1)} className="link-editorial text-xs mb-10 flex items-center gap-2">
          <ArrowLeft className="w-3.5 h-3.5" /> Retour
        </button>

        <div className="mb-10">
          <p className="text-[#C5A059] uppercase tracking-[0.3em] text-sm mb-3 font-light">
            Rituel Annuel · Swiss Ephemeris
          </p>
          <h1 className="text-3xl md:text-5xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
            Votre Révolution Solaire
          </h1>
          <p className="text-base text-[#B8B0C8]/70 font-light">
            La carte précise des énergies qui vous accompagnent de votre prochain anniversaire au suivant.
          </p>
        </div>

        {!result && (
          <div className="card-mystical text-center py-10" data-testid="revolution-gate">
            <Sun className="w-10 h-10 text-[#C5A059] mx-auto mb-4" strokeWidth={1.3} />
            <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
              Découvrez votre prochaine année
            </h2>
            <p className="text-[#B8B0C8]/60 text-sm mb-5 max-w-md mx-auto">
              Rapport complet basé sur la position exacte du Soleil au moment de votre prochain anniversaire — 20 crédits.
            </p>
            {error && <p className="text-amber-300 text-sm mb-4" data-testid="revolution-error">{error}</p>}
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="btn-mystical-filled rounded-full px-8 py-3 inline-flex items-center gap-2 disabled:opacity-60"
              data-testid="btn-generate-revolution"
            >
              {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Calcul en cours...</> : <><Sparkles className="w-4 h-4" /> Générer mon rapport</>}
            </button>
          </div>
        )}

        {result && (
          <div className="space-y-6" data-testid="revolution-result">
            <div className="card-mystical">
              <div className="flex items-center gap-3 mb-3">
                <Sun className="w-6 h-6 text-[#C5A059]" strokeWidth={1.4} />
                <h2 className="text-xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                  Année {result.return_year} · {result.name}
                </h2>
              </div>
              {(report.overview || report.summary) && (
                <p className="text-[#F0E6D3]/90 leading-relaxed" style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: '16px', lineHeight: '1.9' }} data-testid="revolution-overview">
                  {report.overview || report.summary}
                </p>
              )}
            </div>

            {Array.isArray(themes) && themes.length > 0 && (
              <div className="card-mystical" data-testid="revolution-themes">
                <h3 className="text-lg mb-4 flex items-center gap-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                  <Star className="w-5 h-5 text-[#C5A059]" strokeWidth={1.5} /> Thèmes majeurs
                </h3>
                <ul className="space-y-2">
                  {themes.slice(0, 6).map((t, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <span className="text-[#C5A059] mt-1">·</span>
                      <span className="text-[#B8B0C8]">{typeof t === 'string' ? t : (t.title || t.name || JSON.stringify(t))}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {Object.keys(lifeAreas).length > 0 && (
              <div className="grid md:grid-cols-2 gap-4" data-testid="revolution-life-areas">
                {Object.entries(lifeAreas).slice(0, 8).map(([key, val]) => {
                  if (typeof val !== 'string' && !val?.text && !val?.description) return null;
                  return (
                    <div key={key} className="card-mystical">
                      <p className="text-[#C5A059] uppercase tracking-widest text-xs mb-2">{key.replace(/_/g, ' ')}</p>
                      <p className="text-sm text-[#F0E6D3]/85 leading-relaxed">
                        {typeof val === 'string' ? val : (val.text || val.description)}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}

            <div className="flex justify-center gap-3 pt-4">
              <button onClick={() => { setResult(null); setUnlocked(true); }}
                className="btn-mystical rounded-full px-6 py-2.5">
                Recommencer
              </button>
              <button onClick={() => navigate('/horoscope')}
                className="btn-mystical-filled rounded-full px-6 py-2.5 flex items-center gap-2">
                Mon horoscope <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export { TransitsToday };
export default RevolutionSolaire;
