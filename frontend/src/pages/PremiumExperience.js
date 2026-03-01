import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, ArrowLeft, Download, Loader2, Star, Sparkles, Eye, BookOpen, TrendingUp, Check, ChevronRight } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const STEP_META = [
  { key: 'step_1_fondement', label: 'Fondement', icon: Star, num: 'I' },
  { key: 'step_2_chemin_ame', label: 'Chemin d\'Ame', icon: Sparkles, num: 'II' },
  { key: 'step_3_cycle', label: 'Cycle Actuel', icon: Eye, num: 'III' },
  { key: 'step_4_schemas', label: 'Schemas', icon: BookOpen, num: 'IV' },
  { key: 'step_5_projection', label: 'Projection', icon: TrendingUp, num: 'V' },
];

const PremiumExperience = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [premiumData, setPremiumData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingStep, setLoadingStep] = useState('');
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState(new Set());
  const [allRevealed, setAllRevealed] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const data = localStorage.getItem('plume_astrale_data');
    if (!data) {
      navigate('/formulaire');
      return;
    }
    setUserData(JSON.parse(data));
  }, [navigate]);

  const generateContent = useCallback(async (data) => {
    setLoading(true);
    setLoadingStep('Connexion aux astres...');
    try {
      const cached = localStorage.getItem('plume_premium_data');
      if (cached) {
        const parsed = JSON.parse(cached);
        if (parsed.prenom === data.prenom && parsed.date_naissance === data.dateNaissance) {
          setPremiumData(parsed);
          setLoading(false);
          return;
        }
      }
      setLoadingStep('Calcul de votre theme natal...');
      const res = await fetch(`${API_URL}/api/premium/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prenom: data.prenom || 'Voyageur',
          dateNaissance: data.dateNaissance,
          heureNaissance: data.heureNaissance || '12:00',
          ville: data.ville || 'Paris',
        }),
      });
      if (!res.ok) throw new Error('Erreur serveur');
      const result = await res.json();
      if (result.success && result.data) {
        setPremiumData(result.data);
        localStorage.setItem('plume_premium_data', JSON.stringify(result.data));
      } else {
        throw new Error('Donnees invalides');
      }
    } catch (err) {
      setError(`Impossible de generer votre lecture: ${err.message}`);
    }
    setLoading(false);
    setLoadingStep('');
  }, []);

  useEffect(() => {
    if (userData) {
      generateContent(userData);
    }
  }, [userData, generateContent]);

  const handleStepComplete = () => {
    const newCompleted = new Set(completedSteps);
    newCompleted.add(currentStep);
    setCompletedSteps(newCompleted);
    if (newCompleted.size === STEP_META.length) {
      setAllRevealed(true);
    }
    if (currentStep < STEP_META.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleStepClick = (index) => {
    if (allRevealed || index <= Math.max(...completedSteps, 0) + 1) {
      setCurrentStep(index);
    }
  };

  const handleDownloadPDF = async () => {
    if (!premiumData) return;
    setPdfLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/premium/pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: premiumData }),
      });
      if (!res.ok) throw new Error('Erreur PDF');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `cartographie_premium_${premiumData.prenom || 'plume'}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF download error:', err);
    }
    setPdfLoading(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-6 relative z-10" data-testid="premium-loading">
        <Loader2 className="w-8 h-8 animate-spin mb-6" style={{ color: 'var(--pa-accent)' }} />
        <p className="text-sm" style={{ color: 'var(--pa-body)' }}>{loadingStep || 'Preparation...'}</p>
        <p className="text-xs mt-2" style={{ color: 'var(--pa-muted)' }}>Cela peut prendre quelques instants</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-6 relative z-10" data-testid="premium-error">
        <p className="text-sm text-red-400/80 mb-4">{error}</p>
        <button onClick={() => { setError(''); if (userData) generateContent(userData); }} className="btn-editorial text-xs">
          Reessayer
        </button>
      </div>
    );
  }

  if (!premiumData) return null;

  const stepData = premiumData.steps?.[STEP_META[currentStep].key];
  const StepIcon = STEP_META[currentStep].icon;
  const isStepCompleted = completedSteps.has(currentStep);
  const isLastStep = currentStep === STEP_META.length - 1;

  return (
    <div className="min-h-screen relative z-10 flex" data-testid="premium-experience">
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col w-72 flex-shrink-0 fixed top-0 left-0 h-screen pt-20 pb-8 px-5" style={{ background: 'rgba(8,6,20,0.95)', borderRight: '1px solid var(--pa-divider)', zIndex: 40 }} data-testid="premium-sidebar">
        <div className="mb-8">
          <p className="text-xs tracking-widest uppercase mb-1" style={{ color: 'var(--pa-accent)', letterSpacing: '0.15em' }}>Experience Premium</p>
          <p className="text-sm" style={{ color: 'var(--pa-heading)', fontFamily: 'Cormorant Garamond, serif' }}>{premiumData.prenom} &mdash; {premiumData.signe}</p>
        </div>
        <nav className="flex-1 space-y-1" data-testid="premium-nav">
          {STEP_META.map((step, i) => {
            const Icon = step.icon;
            const isActive = i === currentStep;
            const isCompleted = completedSteps.has(i);
            const isAccessible = allRevealed || i <= Math.max(...completedSteps, -1) + 1;
            return (
              <button
                key={step.key}
                onClick={() => handleStepClick(i)}
                disabled={!isAccessible}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all duration-300 ${isActive ? '' : 'hover:bg-white/[0.02]'}`}
                style={{
                  background: isActive ? 'rgba(197,160,89,0.08)' : 'transparent',
                  borderLeft: isActive ? '2px solid var(--pa-accent)' : '2px solid transparent',
                  opacity: isAccessible ? 1 : 0.35,
                  cursor: isAccessible ? 'pointer' : 'not-allowed',
                }}
                data-testid={`premium-nav-step-${i}`}
              >
                <div className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0" style={{ border: `1px solid ${isCompleted ? 'var(--pa-accent)' : 'var(--pa-divider)'}`, background: isCompleted ? 'rgba(197,160,89,0.15)' : 'transparent' }}>
                  {isCompleted ? <Check className="w-3.5 h-3.5" style={{ color: 'var(--pa-accent)' }} strokeWidth={2} /> : <Icon className="w-3.5 h-3.5" style={{ color: isActive ? 'var(--pa-accent)' : 'var(--pa-muted)' }} strokeWidth={1.5} />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs" style={{ color: isActive ? 'var(--pa-accent)' : 'var(--pa-muted)', letterSpacing: '0.05em' }}>{step.num}</p>
                  <p className="text-sm truncate" style={{ color: isActive ? 'var(--pa-heading)' : 'var(--pa-body)' }}>{step.label}</p>
                </div>
              </button>
            );
          })}
        </nav>
        {allRevealed && (
          <button onClick={handleDownloadPDF} disabled={pdfLoading} className="btn-editorial-filled w-full justify-center text-xs mt-4" data-testid="premium-download-sidebar">
            {pdfLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Download className="w-4 h-4" strokeWidth={1.5} /> Telecharger le PDF</>}
          </button>
        )}
      </aside>

      {/* Mobile step indicator */}
      <div className="md:hidden fixed top-16 left-0 right-0 z-40 px-4 py-3" style={{ background: 'rgba(8,6,20,0.95)', borderBottom: '1px solid var(--pa-divider)' }} data-testid="premium-mobile-nav">
        <div className="flex items-center gap-2 overflow-x-auto">
          {STEP_META.map((step, i) => {
            const isActive = i === currentStep;
            const isCompleted = completedSteps.has(i);
            return (
              <button
                key={step.key}
                onClick={() => handleStepClick(i)}
                className="flex items-center gap-1.5 flex-shrink-0 px-3 py-1.5 rounded-full transition-all"
                style={{
                  background: isActive ? 'rgba(197,160,89,0.12)' : 'transparent',
                  border: `1px solid ${isActive ? 'var(--pa-accent)' : 'var(--pa-divider)'}`,
                  opacity: (allRevealed || i <= Math.max(...completedSteps, -1) + 1) ? 1 : 0.35,
                }}
                data-testid={`premium-mobile-step-${i}`}
              >
                {isCompleted && <Check className="w-3 h-3" style={{ color: 'var(--pa-accent)' }} strokeWidth={2} />}
                <span className="text-xs" style={{ color: isActive ? 'var(--pa-accent)' : 'var(--pa-muted)' }}>{step.num}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main content */}
      <main className="flex-1 md:ml-72 pt-32 md:pt-20 pb-20 px-6 md:px-12 lg:px-16" data-testid="premium-main-content">
        <div className="max-w-2xl mx-auto">
          {/* Step header */}
          <div className="mb-10" data-testid="premium-step-header">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ border: '1px solid var(--pa-divider)', background: 'rgba(197,160,89,0.05)' }}>
                <StepIcon className="w-5 h-5" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.5} />
              </div>
              <div>
                <p className="text-xs" style={{ color: 'var(--pa-accent)', letterSpacing: '0.1em' }}>Etape {STEP_META[currentStep].num}</p>
                <h1 className="text-2xl md:text-3xl" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
                  {stepData?.title}
                </h1>
              </div>
            </div>
            <p className="text-sm" style={{ color: 'var(--pa-body)' }}>{stepData?.subtitle}</p>
          </div>

          {/* Step data cards */}
          {(stepData?.signe || stepData?.chemin_de_vie || stepData?.annee_personnelle) && (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-8" data-testid="premium-step-data">
              {stepData.signe && (
                <div className="card-editorial p-4 text-center">
                  <p className="text-xs mb-1" style={{ color: 'var(--pa-muted)' }}>Signe</p>
                  <p className="text-base" style={{ color: 'var(--pa-heading)', fontFamily: 'Cormorant Garamond, serif' }}>{stepData.signe}</p>
                </div>
              )}
              {stepData.element && (
                <div className="card-editorial p-4 text-center">
                  <p className="text-xs mb-1" style={{ color: 'var(--pa-muted)' }}>Element</p>
                  <p className="text-base" style={{ color: 'var(--pa-heading)', fontFamily: 'Cormorant Garamond, serif' }}>{stepData.element}</p>
                </div>
              )}
              {stepData.modalite && (
                <div className="card-editorial p-4 text-center">
                  <p className="text-xs mb-1" style={{ color: 'var(--pa-muted)' }}>Modalite</p>
                  <p className="text-base" style={{ color: 'var(--pa-heading)', fontFamily: 'Cormorant Garamond, serif' }}>{stepData.modalite}</p>
                </div>
              )}
              {stepData.chemin_de_vie && (
                <div className="card-editorial p-4 text-center">
                  <p className="text-xs mb-1" style={{ color: 'var(--pa-muted)' }}>Chemin de vie</p>
                  <p className="text-2xl" style={{ color: 'var(--pa-accent)', fontFamily: 'Cormorant Garamond, serif' }}>{stepData.chemin_de_vie}</p>
                  {stepData.titre_chemin && <p className="text-xs mt-0.5" style={{ color: 'var(--pa-body)' }}>{stepData.titre_chemin}</p>}
                </div>
              )}
              {stepData.nombre_expression && (
                <div className="card-editorial p-4 text-center">
                  <p className="text-xs mb-1" style={{ color: 'var(--pa-muted)' }}>Expression</p>
                  <p className="text-2xl" style={{ color: 'var(--pa-accent)', fontFamily: 'Cormorant Garamond, serif' }}>{stepData.nombre_expression}</p>
                </div>
              )}
              {stepData.nombre_ame && (
                <div className="card-editorial p-4 text-center">
                  <p className="text-xs mb-1" style={{ color: 'var(--pa-muted)' }}>Ame</p>
                  <p className="text-2xl" style={{ color: 'var(--pa-accent)', fontFamily: 'Cormorant Garamond, serif' }}>{stepData.nombre_ame}</p>
                </div>
              )}
              {stepData.annee_personnelle && (
                <div className="card-editorial p-4 text-center">
                  <p className="text-xs mb-1" style={{ color: 'var(--pa-muted)' }}>Annee personnelle</p>
                  <p className="text-2xl" style={{ color: 'var(--pa-accent)', fontFamily: 'Cormorant Garamond, serif' }}>{stepData.annee_personnelle}</p>
                </div>
              )}
              {stepData.periode && (
                <div className="card-editorial p-4 text-center">
                  <p className="text-xs mb-1" style={{ color: 'var(--pa-muted)' }}>Periode</p>
                  <p className="text-base" style={{ color: 'var(--pa-heading)', fontFamily: 'Cormorant Garamond, serif' }}>{stepData.periode}</p>
                </div>
              )}
            </div>
          )}

          {/* Forces / Tensions */}
          {(stepData?.forces || stepData?.tensions) && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8" data-testid="premium-forces-tensions">
              {stepData.forces && (
                <div className="card-editorial p-5">
                  <p className="text-xs tracking-widest uppercase mb-3" style={{ color: 'var(--pa-accent)', letterSpacing: '0.15em' }}>Forces</p>
                  <div className="space-y-2">
                    {stepData.forces.map((f, i) => (
                      <div key={i} className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--pa-accent)' }} />
                        <span className="text-sm" style={{ color: 'var(--pa-heading)' }}>{f}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {stepData.tensions && (
                <div className="card-editorial p-5">
                  <p className="text-xs tracking-widest uppercase mb-3" style={{ color: 'var(--pa-muted)', letterSpacing: '0.15em' }}>Tensions</p>
                  <div className="space-y-2">
                    {stepData.tensions.map((t, i) => (
                      <div key={i} className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--pa-muted)' }} />
                        <span className="text-sm" style={{ color: 'var(--pa-body)' }}>{t}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Interpretation */}
          {stepData?.interpretation && (
            <div className="mb-8" data-testid="premium-interpretation">
              <div className="w-8 h-px mb-6" style={{ background: 'var(--pa-accent)', opacity: 0.3 }} />
              <div className="space-y-4 text-base" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
                {stepData.interpretation.split('\n').filter(p => p.trim()).map((para, i) => (
                  <p key={i}>{para}</p>
                ))}
              </div>
            </div>
          )}

          {/* Reflection */}
          {stepData?.reflection && (
            <div className="card-editorial p-6 mb-10 text-center" style={{ background: 'rgba(197,160,89,0.04)', borderColor: 'rgba(197,160,89,0.15)' }} data-testid="premium-reflection">
              <p className="text-xs tracking-widest uppercase mb-3" style={{ color: 'var(--pa-accent)', letterSpacing: '0.15em' }}>Question de reflexion</p>
              <p className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)', fontStyle: 'italic' }}>
                "{stepData.reflection}"
              </p>
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between pt-4" style={{ borderTop: '1px solid var(--pa-divider)' }} data-testid="premium-step-nav">
            <button
              onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
              className={`link-editorial text-xs ${currentStep === 0 ? 'invisible' : ''}`}
              data-testid="premium-prev-step"
            >
              <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Etape precedente
            </button>
            {!isLastStep ? (
              <button onClick={handleStepComplete} className="btn-editorial text-xs" data-testid="premium-next-step">
                {isStepCompleted ? 'Etape suivante' : 'Valider et continuer'} <ChevronRight className="w-4 h-4" strokeWidth={1.5} />
              </button>
            ) : (
              <button onClick={allRevealed ? handleDownloadPDF : handleStepComplete} className="btn-editorial-filled text-xs" data-testid="premium-complete">
                {allRevealed ? (
                  <>{pdfLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" strokeWidth={1.5} />} Telecharger le PDF</>
                ) : (
                  <>Terminer le parcours <Check className="w-4 h-4" strokeWidth={1.5} /></>
                )}
              </button>
            )}
          </div>

          {/* Completion banner */}
          {allRevealed && (
            <div className="mt-10 card-editorial p-6 text-center" style={{ background: 'rgba(197,160,89,0.06)', borderColor: 'rgba(197,160,89,0.2)' }} data-testid="premium-complete-banner">
              <Sparkles className="w-6 h-6 mx-auto mb-3" style={{ color: 'var(--pa-accent)' }} strokeWidth={1.5} />
              <h3 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
                Parcours termine
              </h3>
              <p className="text-sm mb-4" style={{ color: 'var(--pa-body)' }}>
                Vous pouvez maintenant naviguer librement entre les etapes et telecharger votre PDF Premium.
              </p>
              <button onClick={handleDownloadPDF} disabled={pdfLoading} className="btn-editorial-filled text-xs mx-auto" data-testid="premium-download-final">
                {pdfLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Download className="w-4 h-4" strokeWidth={1.5} /> Telecharger le PDF Premium</>}
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default PremiumExperience;
