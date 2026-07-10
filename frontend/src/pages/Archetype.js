import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Crown, Sparkles, Shield, ArrowRight, Loader2, RefreshCw } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import { useAuth } from '@/context/AuthContext';
import SafeEmptyState from '@/components/design/SafeEmptyState';

const API = process.env.REACT_APP_BACKEND_URL;
const COST = 15;

const Archetype = () => {
  const nav = useNavigate();
  const { token, user, creditBalance, refreshBalance, isAuthenticated } = useAuth();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Détection safe : le résultat a-t-il au moins un champ affichable ?
  const hasAnyArchetypeContent = Boolean(
    result && (
      result.profile_name ||
      result.core_message ||
      (Array.isArray(result.dominant) && result.dominant.length) ||
      result.shadow ||
      result.balance_type
    )
  );

  // Charger l'historique au montage (dernier résultat)
  useEffect(() => {
    if (!token) return;
    axios.get(`${API}/api/archetype/history`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => {
        const readings = r.data?.readings || [];
        if (readings.length > 0) setResult(readings[0].result);
      })
      .catch(() => {});
  }, [token]);

  const handleGenerate = async () => {
    if (!isAuthenticated) { nav('/connexion'); return; }
    if (creditBalance < COST) { nav('/acheter-credits'); return; }
    setLoading(true); setError(null);
    try {
      const r = await axios.post(`${API}/api/archetype/generate`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (r.data?.success) {
        setResult(r.data.archetype);
        refreshBalance();
      } else {
        setError(r.data?.detail || 'Une erreur est survenue');
      }
    } catch (e) {
      setError(e.response?.data?.detail || 'Impossible de générer ton archétype');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen relative" style={{ padding: '110px 20px 140px' }} data-testid="archetype-page">
      <SEO path="/archetype" title="Ton Archétype · Plume Astrale" description="Découvre ton archétype dominant, ton ombre et ton équilibre intérieur — analyse jungienne personnalisée." />

      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <p className="text-[10px] uppercase mb-5" style={{ color: '#D4AF37', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}>
            ✦ Analyse Jungienne ✦
          </p>
          <h1 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 300, lineHeight: 1.05,
            fontSize: 'clamp(38px, 6vw, 62px)',
            color: '#F5EEE0', marginBottom: 18,
          }}>
            Ton <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>Archétype</em>
          </h1>
          <p className="text-base md:text-lg max-w-2xl mx-auto" style={{ color: 'rgba(227,215,255,0.8)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic', lineHeight: 1.6 }}>
            Trois archétypes dominants, une ombre à intégrer, un équilibre à révéler.
            Le portrait psychologique le plus profond que ton ciel de naissance puisse tracer.
          </p>
        </div>

        {/* CTA + result */}
        {!result ? (
          <div className="plume-glass p-8 md:p-12 text-center" data-testid="archetype-empty">
            <Sparkles className="w-10 h-10 mx-auto mb-6" style={{ color: '#D4AF37' }} strokeWidth={1.2} />
            <h2 className="text-2xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>
              Prête à te découvrir vraiment ?
            </h2>
            <p className="text-sm mb-8 max-w-lg mx-auto" style={{ color: 'rgba(227,215,255,0.7)', lineHeight: 1.7 }}>
              L&apos;analyse combine ton thème natal complet, la position des planètes personnelles, et les 12 archétypes universels
              de Jung — pour te livrer un miroir précis de ta psyché.
            </p>
            <p className="text-xs mb-6" style={{ color: 'rgba(227,215,255,0.5)', letterSpacing: '0.1em' }}>
              Coût : <span style={{ color: '#D4AF37', fontWeight: 500 }}>{COST} crédits</span>
              {isAuthenticated && <> · Solde : <span style={{ color: '#D4AF37' }}>{creditBalance ?? 0} crédits</span></>}
            </p>
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="plume-btn-primary"
              data-testid="archetype-generate-btn"
            >
              {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Analyse en cours...</> :
                        <>Découvrir mon archétype <ArrowRight className="w-4 h-4" strokeWidth={1.5} /></>}
            </button>
            {error && <p className="mt-4 text-sm" style={{ color: '#F87171' }} data-testid="archetype-error">{error}</p>}
          </div>
        ) : hasAnyArchetypeContent ? (
          <div data-testid="archetype-result">
            {/* Profile name */}
            <div className="plume-glass p-8 md:p-12 text-center mb-8">
              <p className="text-[10px] uppercase mb-4" style={{ color: '#D4AF37', letterSpacing: '0.3em' }}>
                Tu es
              </p>
              <h2 style={{
                fontFamily: 'Cormorant Garamond, serif',
                fontWeight: 300, lineHeight: 1.05,
                fontSize: 'clamp(30px, 5vw, 48px)',
                color: '#D4AF37', fontStyle: 'italic', marginBottom: 12,
              }}>
                {result.profile_name}
              </h2>
              <p className="text-sm uppercase" style={{ color: 'rgba(227,215,255,0.55)', letterSpacing: '0.2em' }}>
                Équilibre <span style={{ color: '#E3D7FF' }}>{result.balance_type}</span>
              </p>
              {result.core_message && (
                <p className="mt-6 text-base max-w-xl mx-auto" style={{ color: 'rgba(227,215,255,0.85)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic', lineHeight: 1.7 }}>
                  « {result.core_message} »
                </p>
              )}
            </div>

            {/* Dominant archetypes */}
            <div className="mb-8">
              <h3 className="text-xl mb-6 text-center" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>
                Tes 3 archétypes dominants
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {result.dominant.map((a, i) => (
                  <div key={i} className="plume-glass p-6" data-testid={`archetype-dominant-${i}`}>
                    <Crown className="w-6 h-6 mb-3" style={{ color: '#D4AF37' }} strokeWidth={1.2} />
                    <div className="flex items-baseline justify-between mb-2">
                      <h4 className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>
                        {a.title}
                      </h4>
                      {a.score != null && (
                        <span className="text-xs" style={{ color: '#D4AF37', letterSpacing: '0.08em' }}>
                          {typeof a.score === 'number' ? a.score.toFixed(1) : a.score}
                        </span>
                      )}
                    </div>
                    <p className="text-sm" style={{ color: 'rgba(227,215,255,0.75)', lineHeight: 1.6 }}>
                      {a.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Shadow */}
            {result.shadow && (
              <div className="plume-glass p-8 mb-8" data-testid="archetype-shadow">
                <div className="flex items-start gap-4">
                  <Shield className="w-8 h-8 flex-shrink-0" style={{ color: '#7BA5D9' }} strokeWidth={1.2} />
                  <div>
                    <p className="text-[10px] uppercase mb-2" style={{ color: 'rgba(227,215,255,0.5)', letterSpacing: '0.28em' }}>
                      Ton archétype ombre
                    </p>
                    <h4 className="text-xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#E3D7FF', fontWeight: 400 }}>
                      {result.shadow.title}
                    </h4>
                    <p className="text-sm" style={{ color: 'rgba(227,215,255,0.75)', lineHeight: 1.7 }}>
                      {result.shadow.description || "Cette part de toi que tu tends à ignorer — mais qui, une fois reconnue, devient une source de puissance."}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* CTA follow-up */}
            <div className="text-center mt-10">
              <p className="text-sm mb-5" style={{ color: 'rgba(227,215,255,0.7)' }}>
                Envie d&apos;aller plus loin dans ton exploration ?
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Link to="/consultation" className="plume-btn-primary" data-testid="archetype-cta-chat">
                  Parler à Solena <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
                </Link>
                <button onClick={handleGenerate} disabled={loading} className="plume-btn-secondary" data-testid="archetype-regenerate">
                  <RefreshCw className="w-4 h-4" strokeWidth={1.5} /> Régénérer ({COST} cr)
                </button>
              </div>
              <p className="text-[10px] uppercase mt-4" style={{ color: 'rgba(227,215,255,0.4)', letterSpacing: '0.25em' }}>
                Solde : {creditBalance ?? 0} crédits
              </p>
            </div>
          </div>
        ) : (
          <SafeEmptyState
            productName="votre Archétype"
            onRetry={handleGenerate}
          />
        )}
      </div>
    </div>
  );
};

export default Archetype;
