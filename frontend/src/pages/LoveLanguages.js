import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, Sparkles, ArrowLeft, Loader2, Download, Share2, ArrowRight } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import SEO from '@/components/SEO';
import SEOServiceEnrich from '@/components/SEOServiceEnrich';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const LoveLanguages = () => {
  const navigate = useNavigate();
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
        const res = await axios.post(`${API_URL}/api/astrology/v3/love-languages`, {},
          { headers: { Authorization: `Bearer ${token}` } });
        if (!cancel && res.data?.success) setData(res.data);
        else if (!cancel) setError('Service indisponible.');
      } catch (e) {
        if (!cancel) {
          if (e.response?.status === 402) {
            navigate('/acheter-credits');
            return;
          }
          setError(e.response?.data?.detail || 'Erreur lors du calcul.');
        }
      }
      if (!cancel) setLoading(false);
    })();
    return () => { cancel = true; };
  }, [isAuthenticated, user?.birth_date, token, navigate]);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen px-6 py-20 flex items-center justify-center" data-testid="ll-auth-gate">
        <div className="card-mystical text-center max-w-md">
          <Heart className="w-10 h-10 text-[#D4AF37] mx-auto mb-4" strokeWidth={1.3} />
          <h1 className="text-2xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
            Vos Langages d'Amour
          </h1>
          <p className="text-[#B8B0C8]/70 text-sm mb-5">Connectez-vous pour découvrir votre signature affective.</p>
          <button onClick={() => navigate('/connexion?next=/love-languages')}
            className="btn-mystical-filled rounded-full px-6 py-2.5">
            Se connecter
          </button>
        </div>
      </div>
    );
  }

  if (!user?.birth_date) {
    return (
      <div className="min-h-screen px-6 py-20 flex items-center justify-center" data-testid="ll-no-natal">
        <div className="card-mystical text-center max-w-md">
          <p className="text-[#F5EEE0] mb-3">Vos données natales sont requises.</p>
          <button onClick={() => navigate('/mon-compte')} className="btn-mystical-filled rounded-full px-6 py-2.5">
            Compléter mon profil
          </button>
        </div>
      </div>
    );
  }

  const d = data?.data || {};
  const primary = d.primary_language || d.primary || d.dominant || {};
  const secondary = d.secondary_language || d.secondary || d.supporting_languages || [];
  const advice = d.advice || d.recommendations || d.guidance || [];
  const summary = d.summary || d.description || d.overview || '';

  return (
    <div className="min-h-screen px-6 md:px-8 py-20 md:py-28" data-testid="love-languages-page">
      <div className="max-w-3xl mx-auto">
        <button onClick={() => navigate(-1)} className="link-editorial text-xs mb-10 flex items-center gap-2">
          <ArrowLeft className="w-3.5 h-3.5" /> Retour
        </button>

        <div className="mb-10 text-center">
          <p className="text-[#D4AF37] uppercase tracking-[0.3em] text-sm mb-3 font-light">
            Signature Affective · Vénus · Mars · Lune
          </p>
          <h1 className="text-3xl md:text-5xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
            Vos Langages de l'Amour
          </h1>
          <p className="text-base text-[#B8B0C8]/70 font-light max-w-xl mx-auto">
            Comment vous donnez et recevez l'amour, selon votre carte natale.
          </p>
        </div>

        {loading && (
          <div className="text-center py-10" data-testid="ll-loading">
            <Loader2 className="w-7 h-7 text-[#D4AF37] mx-auto animate-spin" />
          </div>
        )}
        {error && <p className="text-amber-300 text-center mb-4" data-testid="ll-error">{error}</p>}

        {data && (
          <div className="space-y-6 animate-fade-in" data-testid="ll-result">
            <div className="card-mystical text-center glow-gold">
              <Heart className="w-9 h-9 text-pink-400 mx-auto mb-3 animate-pulse" strokeWidth={1.4} />
              <p className="text-[#D4AF37] uppercase tracking-widest text-xs mb-2">Langage Principal</p>
              <h2 className="text-3xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }} data-testid="ll-primary-name">
                {primary.name || primary.label || primary.title || 'Tendresse'}
              </h2>
              {(primary.description || primary.text) && (
                <p className="text-[#F5EEE0]/85 leading-relaxed max-w-lg mx-auto" style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: '16px', lineHeight: '1.85' }}>
                  {primary.description || primary.text}
                </p>
              )}
            </div>

            {Array.isArray(secondary) && secondary.length > 0 && (
              <div className="card-mystical" data-testid="ll-secondary">
                <h3 className="text-lg mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                  Langages secondaires
                </h3>
                <ul className="grid sm:grid-cols-2 gap-3">
                  {secondary.slice(0, 4).map((s, i) => (
                    <li key={i} className="bg-[#15112A]/40 rounded-lg p-3 border border-[#D4AF37]/15" data-testid={`ll-secondary-${i}`}>
                      <p className="text-[#D4AF37] text-sm mb-1">{s.name || s.label || s.title}</p>
                      {(s.description || s.text) && (
                        <p className="text-[#B8B0C8]/75 text-xs leading-relaxed">{s.description || s.text}</p>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {summary && (
              <div className="card-mystical">
                <p className="text-[#F5EEE0]/85 leading-relaxed" style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: '16px', lineHeight: '1.9' }} data-testid="ll-summary">
                  {summary}
                </p>
              </div>
            )}

            {Array.isArray(advice) && advice.length > 0 && (
              <div className="card-mystical" data-testid="ll-advice">
                <h3 className="text-lg mb-3 flex items-center gap-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0' }}>
                  <Sparkles className="w-5 h-5 text-[#D4AF37]" strokeWidth={1.5} /> Pistes pour vous
                </h3>
                <ul className="space-y-2">
                  {advice.slice(0, 5).map((a, i) => (
                    <li key={i} className="flex gap-2 text-sm text-[#B8B0C8] leading-relaxed">
                      <span className="text-[#D4AF37] mt-1">·</span>
                      <span>{typeof a === 'string' ? a : (a.text || a.description || JSON.stringify(a))}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="flex flex-col sm:flex-row justify-center gap-3 pt-4">
              <button onClick={() => navigate('/compatibilite')}
                className="btn-mystical-filled rounded-full px-6 py-2.5 flex items-center gap-2 justify-center"
                data-testid="ll-cta-compat">
                Tester ma compatibilité <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
      <SEOServiceEnrich slug="love-languages" />
    </div>
  );
};

export default LoveLanguages;
