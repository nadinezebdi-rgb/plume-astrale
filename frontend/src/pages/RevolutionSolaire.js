import use3DTilt from '@/hooks/use3DTilt';
import React, { useState, useEffect } from 'react';
import PageHero from '@/components/PageHero';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowLeft, Loader2, Sun, Star, Compass, ArrowRight } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import SafeEmptyState from '../components/design/SafeEmptyState';


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
  // Vrai schéma astrology-api.io v3 : report.events est une liste d'événements interprétés
  const events = Array.isArray(report.events) ? report.events : [];
  const reportText = report.summary || report.text || '';


  return (
    <section className="card-mystical mb-8" data-testid="transits-today">
      <div className="flex items-center gap-2 mb-4">
        <Compass className="w-5 h-5 text-[#C9A24B]" strokeWidth={1.5} />
        <h2 className="text-xl" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>
          Transits du jour sur votre thème
        </h2>
      </div>
      <p className="text-[#232323]/70 text-sm mb-5 font-light">
        Comment les planètes actuelles activent votre carte natale, en temps réel.
      </p>


      {loading && (
        <div className="flex items-center gap-2 text-[#C9A24B]/70 text-sm" data-testid="transits-loading">
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
                  <Sparkles className="w-4 h-4 text-[#C9A24B] mt-0.5" strokeWidth={1.5} />
                  <div>
                    <span className="text-[#0F1A3C]">
                      {(a.point_1 || a.planet_1 || a.first_planet || '')} {(a.aspect_name || a.aspect || a.type || '')} {(a.point_2 || a.planet_2 || a.second_planet || '')}
                    </span>
                    {(a.orb !== undefined || a.orb_value !== undefined) && (
                      <span className="text-[#0F1A3C]/50 ml-2 text-xs">
                        orbe {Number(a.orb || a.orb_value).toFixed(2)}°
                      </span>
                    )}
                    {a.description && <p className="text-[#232323]/70 mt-0.5 text-xs">{a.description}</p>}
                  </div>
                </li>
              ))}
            </ul>
          )}
          {events.length > 0 && (
            <ul className="space-y-3 mb-5" data-testid="transits-events">
              {events.slice(0, 6).map((ev, i) => (
                <li key={i} className="flex items-start gap-3">
                  <Sparkles className="w-4 h-4 text-[#C9A24B] mt-1 flex-shrink-0" strokeWidth={1.5} />
                  <div>
                    {ev.title && (
                      <p className="text-[#0F1A3C] text-sm mb-1" style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600, letterSpacing: '0.05em' }}>
                        {ev.title}
                      </p>
                    )}
                    {ev.interpretation && (
                      <p className="text-[#232323]/80 text-sm leading-relaxed" style={{ fontFamily: 'Playfair Display, serif' }}>
                        {ev.interpretation}
                      </p>
                    )}
                    {ev.date && (
                      <p className="text-[#C9A24B]/60 text-xs mt-1" style={{ letterSpacing: '0.15em' }}>
                        {ev.date}
                      </p>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
          {reportText && (
            <p className="text-[#232323] leading-relaxed" style={{ fontFamily: 'Playfair Display, serif', fontSize: '16px', lineHeight: '1.85' }} data-testid="transits-report">
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
  const revTilt = use3DTilt({ max: 9, scale: 1.03 });


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
  // Vrai schéma astrology-api.io v3 :
  //  - report.interpretations  → list de {title, text}
  //  - report.life_areas       → list de {area_key, theme, prediction}
  //  - report.sr_to_natal_aspects → list d'aspects entre Solar Return et natal
  //  - report.overview / report.summary → optionnel, résumé narratif
  const interpretations = Array.isArray(report.interpretations) ? report.interpretations : [];
  const lifeAreas = Array.isArray(report.life_areas) ? report.life_areas : [];
  const srAspects = Array.isArray(report.sr_to_natal_aspects) ? report.sr_to_natal_aspects : [];
  const overview = report.overview || report.summary || '';


  // Détection safe : si l'API a répondu 200 mais qu'aucune section n'a de contenu
  // affichable, on montre le SafeEmptyState au lieu d'une page vide.
  const hasAnyContent = Boolean(
    overview || interpretations.length || lifeAreas.length || srAspects.length
  );


  return (
    <div className="min-h-screen px-6 md:px-8 py-20 md:py-28" data-testid="revolution-page">
      <PageHero
        image="/images/astrale/image-astrale2.jpg"
        title="Révolution Solaire"
        subtitle="Votre thème de l'année à venir — rituel d'anniversaire astral"
      />
      <div className="max-w-3xl mx-auto">
        <button onClick={() => navigate(-1)} className="link-editorial text-xs mb-10 flex items-center gap-2">
          <ArrowLeft className="w-3.5 h-3.5" /> Retour
        </button>


        <div className="mb-10">
          <p className="text-[#C9A24B] uppercase tracking-[0.3em] text-sm mb-3 font-light">
            Rituel Annuel · Swiss Ephemeris
          </p>
          <h1 className="text-3xl md:text-5xl mb-3" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>
            Votre Révolution Solaire
          </h1>
          <p className="text-base text-[#232323]/70 font-light">
            La carte précise des énergies qui vous accompagnent de votre prochain anniversaire au suivant.
          </p>
        </div>


        {!result && (
          <div
            ref={revTilt.ref}
            onMouseMove={revTilt.onMouseMove}
            onMouseLeave={revTilt.onMouseLeave}
            className="card-mystical rs-3d-tilt text-center py-10"
            data-testid="revolution-gate"
          >
            <Sun className="w-10 h-10 text-[#D4AF37] mx-auto mb-4" strokeWidth={1.3} />
            <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
              Découvrez votre prochaine année
            </h2>
            <p className="text-[#232323]/60 text-sm mb-5 max-w-md mx-auto">
              Rapport complet basé sur la position exacte du Soleil au moment de votre prochain anniversaire — 20 crédits.
            </p>
            {error && <p className="text-amber-300 text-sm mb-4" data-testid="revolution-error">{error}</p>}
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="btn-mystical-filled rs-3d-lift rounded-full px-8 py-3 inline-flex items-center gap-2 disabled:opacity-60"
              data-testid="btn-generate-revolution"
            >
              {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Calcul en cours...</> : <><Sparkles className="w-4 h-4" /> Générer mon rapport</>}
            </button>
          </div>
        )}


        {result && !hasAnyContent && (
          <SafeEmptyState
            productName="votre Révolution Solaire"
            onRetry={handleGenerate}
            extraContext={`Année visée : ${result.return_year || '—'}`}
          />
        )}


        {result && hasAnyContent && (
          <div className="space-y-6" data-testid="revolution-result">
            <div className="card-mystical">
              <div className="flex items-center gap-3 mb-3">
                <Sun className="w-6 h-6 text-[#C9A24B]" strokeWidth={1.4} />
                <h2 className="text-xl" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>
                  Année {result.return_year} · {result.name}
                </h2>
              </div>
              {overview && (
                <p className="text-[#232323] leading-relaxed" style={{ fontFamily: 'Playfair Display, serif', fontSize: '16px', lineHeight: '1.9' }} data-testid="revolution-overview">
                  {overview}
                </p>
              )}
            </div>


            {interpretations.length > 0 && (
              <div className="card-mystical" data-testid="revolution-interpretations">
                <h3 className="text-lg mb-4 flex items-center gap-2" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>
                  <Star className="w-5 h-5 text-[#C9A24B]" strokeWidth={1.5} /> Thèmes majeurs de l&apos;année
                </h3>
                <div className="space-y-5">
                  {interpretations.slice(0, 6).map((it, i) => (
                    <div key={i} className="pb-4" style={{ borderBottom: i < 5 ? '1px solid rgba(201,162,75,0.15)' : 'none' }}>
                      {it.title && (
                        <p className="text-[#C9A24B] uppercase tracking-widest text-xs mb-2" style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
                          {it.title}
                        </p>
                      )}
                      <p className="text-sm md:text-base text-[#232323] leading-relaxed" style={{ fontFamily: 'Playfair Display, serif' }}>
                        {it.text || it.interpretation || it.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}


            {lifeAreas.length > 0 && (
              <div className="grid md:grid-cols-2 gap-4" data-testid="revolution-life-areas">
                {lifeAreas.slice(0, 12).map((la, i) => (
                  <div key={i} className="card-mystical">
                    <p className="text-[#C9A24B] uppercase tracking-widest text-xs mb-2" style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
                      {la.theme || (la.area_key || '').replace(/_/g, ' ')}
                    </p>
                    <p className="text-sm text-[#0F1A3C]/85 leading-relaxed" style={{ fontFamily: 'Playfair Display, serif' }}>
                      {la.prediction || la.text || la.description || ''}
                    </p>
                  </div>
                ))}
              </div>
            )}


            {srAspects.length > 0 && (
              <div className="card-mystical" data-testid="revolution-sr-aspects">
                <h3 className="text-lg mb-4 flex items-center gap-2" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>
                  <Compass className="w-5 h-5 text-[#C9A24B]" strokeWidth={1.5} /> Résonances avec votre thème natal
                </h3>
                <ul className="space-y-3">
                  {srAspects.slice(0, 6).map((a, i) => (
                    <li key={i} className="text-sm">
                      <span className="text-[#0F1A3C]">
                        {(a.point_1 || a.planet_1 || '')} {(a.aspect_name || a.aspect || '')} {(a.point_2 || a.planet_2 || '')}
                      </span>
                      {a.interpretation && (
                        <p className="text-[#232323]/75 mt-1 text-xs md:text-sm leading-relaxed" style={{ fontFamily: 'Playfair Display, serif' }}>
                          {a.interpretation}
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
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
