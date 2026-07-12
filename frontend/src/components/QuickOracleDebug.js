/**
 * QuickOracleDebug - Version avec logging exhaustif pour déboguer le CTA
 * Trace chaque étape du flux utilisateur
 */
import React, { useState, useEffect } from 'react';
import { Sparkles, ArrowRight, X } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const ZODIACS = [
  'Bélier', 'Taureau', 'Gémeaux', 'Cancer',
  'Lion', 'Vierge', 'Balance', 'Scorpion',
  'Sagittaire', 'Capricorne', 'Verseau', 'Poisson'
];

const log = (message, data = null) => {
  const timestamp = new Date().toLocaleTimeString();
  const logMsg = `[${timestamp}] [QuickOracle] ${message}`;
  console.log(logMsg, data || '');
  // Aussi logger dans localStorage pour persistance
  try {
    const logs = JSON.parse(localStorage.getItem('qo_logs') || '[]');
    logs.push({ msg: message, data, time: timestamp });
    localStorage.setItem('qo_logs', JSON.stringify(logs.slice(-50))); // Keep last 50
  } catch (e) { /* ignore */ }
};

export default function QuickOracleDebug({ onClose, onSelectPack }) {
  const [step, setStep] = useState(1);
  const [selectedSign, setSelectedSign] = useState(null);
  const [oracleData, setOracleData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [debugInfo, setDebugInfo] = useState({});

  useEffect(() => {
    log('Component mounted', { onClose: !!onClose, onSelectPack: !!onSelectPack });
  }, []);

  const handleSelectSign = async (sign) => {
    log(`Step 1: Sign selected`, { sign });
    setSelectedSign(sign);
    setLoading(true);
    setDebugInfo(prev => ({ ...prev, selectedSign: sign, step1Time: new Date() }));

    setTimeout(() => {
      const oracleText = `Oracle pour ${sign}: Moment de révélation astrologique...`;
      log(`Step 2: Oracle generated`, { sign, textLength: oracleText.length });
      
      setOracleData({
        sign,
        daily: oracleText,
        generatedAt: new Date().toLocaleString('fr-FR'),
      });
      setStep(2);
      setLoading(false);
      setDebugInfo(prev => ({ ...prev, step2Time: new Date(), oracleGenerated: true }));
    }, 1000);
  };

  const proceedToUpsell = () => {
    log(`Step 3: Proceeding to upsell`, { currentStep: step });
    setStep(3);
    setDebugInfo(prev => ({ ...prev, step3Time: new Date(), proceedToUpsellCalled: true }));
  };

  const handlePackSelect = (packId) => {
    log(`Step 4: Pack selected`, { packId });
    setDebugInfo(prev => ({ ...prev, selectedPackId: packId, step4Time: new Date() }));
    
    if (typeof onSelectPack !== 'function') {
      log(`ERROR: onSelectPack is not a function`, { type: typeof onSelectPack });
      return;
    }
    
    log(`Step 5: Calling onSelectPack callback`, { packId });
    try {
      onSelectPack(packId);
      log(`Step 5: onSelectPack called successfully`);
    } catch (error) {
      log(`ERROR in onSelectPack:`, { error: error.message });
    }
  };

  const handleClose = () => {
    log(`Close button clicked`);
    if (typeof onClose !== 'function') {
      log(`ERROR: onClose is not a function`, { type: typeof onClose });
      return;
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[10000] flex items-center justify-center px-4 py-6"
      style={{
        background: 'linear-gradient(135deg, rgba(6,3,20,0.95), rgba(20,10,40,0.98))',
        backdropFilter: 'blur(8px)',
      }}>
      <div className="w-full max-w-2xl relative">
        {/* Close button */}
        <button
          onClick={handleClose}
          className="absolute -top-8 right-0 text-white opacity-60 hover:opacity-100 transition"
          style={{ zIndex: 10001 }}
          data-testid="qo-close-btn"
        >
          <X size={24} strokeWidth={1.5} />
        </button>

        {/* STEP 1: SELECT ZODIAC */}
        {step === 1 && (
          <div className="rounded-2xl p-8 md:p-12 text-center"
            style={{
              background: 'linear-gradient(135deg, rgba(212,175,55,0.08), rgba(20,15,40,0.6))',
              border: '1px solid rgba(212,175,55,0.25)',
              backdropFilter: 'blur(12px)',
            }}>
            <div className="mb-6">
              <Sparkles size={36} style={{ color: '#D4AF37', margin: '0 auto' }} />
            </div>
            <h2 className="text-2xl md:text-3xl mb-3" style={{
              fontFamily: 'Cormorant Garamond, serif',
              color: '#F4E8D2',
              fontWeight: 300,
            }}>
              Votre oracle du jour
            </h2>
            <p className="text-sm mb-8" style={{ color: 'rgba(244,232,210,0.7)' }}>
              Sélectionnez votre signe pour une guidance gratuite personnalisée.
            </p>

            {/* Zodiac grid */}
            <div className="grid grid-cols-3 md:grid-cols-4 gap-3 md:gap-4 mb-8">
              {ZODIACS.map((sign) => (
                <button
                  key={sign}
                  onClick={() => {
                    log(`Zodiac button clicked`, { sign });
                    handleSelectSign(sign);
                  }}
                  disabled={loading}
                  className="p-4 rounded-lg transition transform hover:scale-110 active:scale-95"
                  style={{
                    background: 'rgba(212,175,55,0.12)',
                    border: '1px solid rgba(212,175,55,0.25)',
                    color: '#D4AF37',
                    fontFamily: 'Cormorant Garamond, serif',
                    fontSize: '0.9rem',
                    fontWeight: 300,
                    cursor: loading ? 'not-allowed' : 'pointer',
                    opacity: loading ? 0.5 : 1,
                  }}
                  data-testid={`zodiac-${sign}`}
                >
                  {sign}
                </button>
              ))}
            </div>

            <p className="text-[11px] uppercase" style={{
              color: 'rgba(212,175,55,0.5)',
              letterSpacing: '0.15em',
              fontWeight: 300,
            }}>
              Aucune inscription nécessaire
            </p>

            {/* Debug info */}
            <div className="mt-6 p-3 rounded" style={{
              background: 'rgba(0,0,0,0.3)',
              border: '1px solid rgba(212,175,55,0.15)',
              fontSize: '10px',
              color: 'rgba(244,232,210,0.5)',
              fontFamily: 'monospace',
              textAlign: 'left',
            }}>
              <div>Step: 1</div>
              <div>Loading: {loading ? 'true' : 'false'}</div>
              <div>selectedSign: {selectedSign || 'null'}</div>
            </div>
          </div>
        )}

        {/* STEP 2: SHOW ORACLE */}
        {step === 2 && oracleData && (
          <div className="rounded-2xl p-8 md:p-12 text-center"
            style={{
              background: 'linear-gradient(135deg, rgba(212,175,55,0.12), rgba(167,139,250,0.08))',
              border: '1px solid rgba(212,175,55,0.35)',
              backdropFilter: 'blur(12px)',
            }}>
            <h3 className="text-2xl mb-2" style={{
              fontFamily: 'Cormorant Garamond, serif',
              color: '#D4AF37',
              fontWeight: 300,
            }}>
              {selectedSign}
            </h3>

            {/* Oracle text */}
            <div className="mb-10 p-6 rounded-lg"
              style={{
                background: 'rgba(212,175,55,0.08)',
                border: '1px solid rgba(212,175,55,0.18)',
                fontFamily: 'Cormorant Garamond, serif',
                fontSize: '1.1rem',
                lineHeight: 1.8,
                color: '#F4E8D2',
                fontStyle: 'italic',
              }}>
              « {oracleData.daily} »
            </div>

            {/* CTA buttons */}
            <div className="space-y-3">
              <button
                onClick={() => {
                  log(`CTA "Voir la lecture COMPLÈTE" clicked`);
                  proceedToUpsell();
                }}
                className="w-full py-3 rounded-lg font-medium text-sm uppercase transition"
                style={{
                  background: 'linear-gradient(135deg, #D4AF37, #E8C766)',
                  color: '#0C0918',
                  letterSpacing: '0.2em',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
                data-testid="qo-upsell-cta"
              >
                Voir la lecture COMPLÈTE
                <ArrowRight size={14} className="inline ml-2" strokeWidth={2} />
              </button>

              <button
                onClick={() => {
                  log(`"Peut-être plus tard" clicked`);
                  handleClose();
                }}
                className="w-full py-3 rounded-lg text-sm uppercase transition"
                style={{
                  background: 'transparent',
                  color: 'rgba(212,175,55,0.7)',
                  border: '1px solid rgba(212,175,55,0.3)',
                  letterSpacing: '0.2em',
                  cursor: 'pointer',
                }}
              >
                Peut-être plus tard
              </button>
            </div>

            {/* Debug info */}
            <div className="mt-6 p-3 rounded" style={{
              background: 'rgba(0,0,0,0.3)',
              border: '1px solid rgba(212,175,55,0.15)',
              fontSize: '10px',
              color: 'rgba(244,232,210,0.5)',
              fontFamily: 'monospace',
              textAlign: 'left',
            }}>
              <div>Step: 2</div>
              <div>oracleData: {oracleData ? 'yes' : 'no'}</div>
              <div>selectedSign: {selectedSign}</div>
            </div>
          </div>
        )}

        {/* STEP 3: SHOW UPSELL PACKS */}
        {step === 3 && (
          <CreditsUpsellPanelDebug onSelectPack={handlePackSelect} onBack={() => setStep(2)} />
        )}
      </div>

      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}

function CreditsUpsellPanelDebug({ onSelectPack, onBack }) {
  const PACKS = [
    {
      id: 'initiation',
      name: 'Initiation',
      price: '4,99 €',
      credits: 15,
      features: ['Oracle du jour', '1 thème rapide'],
      cta: 'Essayer',
    },
    {
      id: 'clarte',
      name: 'Clarté',
      price: '14,99 €',
      credits: 60,
      features: ['50 + 10 crédits', 'Thème complet'],
      badge: 'Bestseller',
      highlight: true,
      cta: 'Débloquer',
    },
    {
      id: 'flammes',
      name: 'Flammes',
      price: '29,99 €',
      credits: 130,
      features: ['100 + 30 crédits', 'Accès illimité'],
      cta: 'Accéder',
    },
  ];

  return (
    <div className="space-y-4 rounded-2xl p-8 md:p-12"
      style={{
        background: 'linear-gradient(135deg, rgba(212,175,55,0.08), rgba(20,15,40,0.6))',
        border: '1px solid rgba(212,175,55,0.25)',
        backdropFilter: 'blur(12px)',
      }}>
      <div className="text-center mb-8">
        <h3 className="text-xl md:text-2xl mb-2" style={{
          fontFamily: 'Cormorant Garamond, serif',
          color: '#F4E8D2',
          fontWeight: 300,
        }}>
          Accédez à votre profondeur cosmique
        </h3>
      </div>

      {/* Packs */}
      <div className="grid md:grid-cols-3 gap-4">
        {PACKS.map((pack) => (
          <div
            key={pack.id}
            className="rounded-xl p-6 transition transform hover:scale-105"
            style={{
              background: pack.highlight ? 'linear-gradient(135deg, rgba(232,199,102,0.15), rgba(212,175,55,0.08))' : 'rgba(212,175,55,0.08)',
              border: pack.highlight ? '2px solid rgba(232,199,102,0.4)' : '1px solid rgba(212,175,55,0.2)',
            }}>
            {pack.badge && (
              <div style={{
                background: '#D4AF37',
                color: '#0C0918',
                padding: '4px 8px',
                borderRadius: '4px',
                fontSize: '8px',
                fontWeight: 700,
                marginBottom: '8px',
              }}>
                {pack.badge}
              </div>
            )}

            <h4 className="text-lg font-semibold mb-2" style={{ color: '#D4AF37' }}>
              {pack.name}
            </h4>
            <div className="text-2xl font-bold mb-4" style={{ color: '#F4E8D2' }}>
              {pack.price}
            </div>

            <button
              onClick={() => {
                log(`Pack CTA clicked`, { packId: pack.id });
                onSelectPack(pack.id);
              }}
              className="w-full py-2 rounded-lg text-sm font-bold uppercase transition"
              style={{
                background: pack.highlight ? 'linear-gradient(135deg, #D4AF37, #E8C766)' : 'rgba(212,175,55,0.2)',
                color: pack.highlight ? '#0C0918' : '#D4AF37',
                border: pack.highlight ? 'none' : '1px solid rgba(212,175,55,0.3)',
                cursor: 'pointer',
                letterSpacing: '0.1em',
              }}
              data-testid={`pack-cta-${pack.id}`}
            >
              {pack.cta}
            </button>
          </div>
        ))}
      </div>

      <button
        onClick={() => {
          log(`Back button clicked`);
          onBack();
        }}
        className="w-full py-2 text-sm uppercase"
        style={{
          background: 'transparent',
          color: 'rgba(212,175,55,0.6)',
          border: '1px solid rgba(212,175,55,0.2)',
          borderRadius: '8px',
          cursor: 'pointer',
          letterSpacing: '0.1em',
        }}>
        ← Retour
      </button>

      {/* Debug info */}
      <div className="mt-6 p-3 rounded" style={{
        background: 'rgba(0,0,0,0.3)',
        border: '1px solid rgba(212,175,55,0.15)',
        fontSize: '10px',
        color: 'rgba(244,232,210,0.5)',
        fontFamily: 'monospace',
        textAlign: 'left',
      }}>
        <div>Step: 3 (Upsell)</div>
        <div>Packs count: {PACKS.length}</div>
        <div>onSelectPack type: {typeof onSelectPack}</div>
      </div>
    </div>
  );
}
