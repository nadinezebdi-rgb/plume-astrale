import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, ArrowLeft } from 'lucide-react';
import SEO from '@/components/SEO';
import { useAuth } from '@/context/AuthContext';

const Formulaire = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, updateProfile } = useAuth();

  // Si user déjà connecté avec données natales -> rediriger vers son compte (pas de re-onboarding)
  useEffect(() => {
    if (isAuthenticated && user?.birth_date) {
      navigate('/mon-compte', { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  const [step, setStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    prenom: '',
    genre: '',
    email: '',
    dateNaissance: '',
    heureNaissance: '',
    ville: '',
    pays: ''
  });
  // Etats locaux pour les selects Date / Heure — necessaire pour pouvoir cliquer
  // dans n'importe quel ordre sans que le state global ne reinitialise les parts
  const [dDay, setDDay] = useState('');
  const [dMonth, setDMonth] = useState('');
  const [dYear, setDYear] = useState('');
  const [tHour, setTHour] = useState('');
  const [tMin, setTMin] = useState('');
  const [errors, setErrors] = useState({});
  const [didPrefill, setDidPrefill] = useState(false);

  useEffect(() => {
    if (didPrefill) return;

    let source = null;
    if (isAuthenticated && user) {
      source = {
        prenom: user.prenom || '',
        genre: user.gender || '',
        email: user.email || '',
        dateNaissance: user.birth_date || '',
        heureNaissance: user.birth_time || '',
        ville: user.birth_place || '',
        pays: user.birth_country || '',
      };
    } else {
      try {
        const raw = localStorage.getItem('plume_astrale_data');
        source = raw ? JSON.parse(raw) : null;
      } catch {
        source = null;
      }
    }

    if (source) {
      setFormData(prev => ({
        ...prev,
        prenom: source.prenom || prev.prenom,
        genre: source.genre || prev.genre,
        email: source.email || prev.email,
        dateNaissance: source.dateNaissance || prev.dateNaissance,
        heureNaissance: source.heureNaissance || prev.heureNaissance,
        ville: source.ville || prev.ville,
        pays: source.pays || prev.pays,
      }));

      if (source.dateNaissance) {
        const [y, m, d] = String(source.dateNaissance).split('-');
        setDYear(y || '');
        setDMonth(m ? String(parseInt(m, 10)) : '');
        setDDay(d ? String(parseInt(d, 10)) : '');
      }
      if (source.heureNaissance) {
        const [h, mn] = String(source.heureNaissance).split(':');
        setTHour(h ? String(parseInt(h, 10)) : '');
        setTMin(mn ? String(parseInt(mn, 10)) : '');
      }
    }

    setDidPrefill(true);
  }, [didPrefill, isAuthenticated, user]);

  const steps = [
    {
      id: 'prenom',
      title: 'Quel est votre prenom ?',
      subtitle: 'Le nom que porte votre ame en cette vie',
      field: 'prenom',
      type: 'text',
      placeholder: 'Votre prenom',
      required: false
    },
    {
      id: 'genre',
      title: 'Quel est votre genre ?',
      subtitle: 'Les energies influencent votre theme',
      field: 'genre',
      type: 'gender',
      required: true
    },
    {
      id: 'email',
      title: 'Votre adresse email',
      subtitle: 'Pour recevoir votre manuscrit',
      field: 'email',
      type: 'email',
      placeholder: 'votre@email.com',
      required: true
    },
    {
      id: 'date',
      title: 'Quand etes-vous ne(e) ?',
      subtitle: 'Le jour ou les etoiles se sont alignees pour vous',
      field: 'dateNaissance',
      type: 'date',
      required: true
    },
    {
      id: 'heure',
      title: 'A quelle heure ?',
      subtitle: 'Essentiel pour calculer votre ascendant',
      field: 'heureNaissance',
      type: 'time',
      required: true
    },
    {
      id: 'lieu',
      title: 'Ou etes-vous ne(e) ?',
      subtitle: 'Le lieu de votre premiere respiration',
      field: 'ville',
      type: 'text',
      placeholder: 'Ville de naissance',
      required: true,
      extra: {
        field: 'pays',
        placeholder: 'Pays',
        required: true
      }
    }
  ];

  const MONTHS_FR = [
    'Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin',
    'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre',
  ];
  const CURRENT_YEAR = new Date().getFullYear();
  const YEARS = Array.from({ length: 100 }, (_, i) => CURRENT_YEAR - i);

  // Met à jour formData.dateNaissance seulement quand les 3 parts sont remplies
  const updateDate = (y, m, d) => {
    setDYear(y);
    setDMonth(m);
    setDDay(d);
    const date = (y && m && d) ? `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}` : '';
    setFormData(prev => ({ ...prev, dateNaissance: date }));
  };
  const updateTime = (h, m) => {
    setTHour(h);
    setTMin(m);
    const t = (h !== '' && m !== '') ? `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}` : '';
    setFormData(prev => ({ ...prev, heureNaissance: t }));
  };

  const currentStep = steps[step];

  const validateStep = () => {
    const newErrors = {};
    if (currentStep.required && !formData[currentStep.field]) {
      newErrors[currentStep.field] = 'Ce champ est requis';
    }
    if (currentStep.field === 'email' && formData.email) {
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        newErrors.email = 'Format d\'email invalide';
      }
    }
    if (currentStep.extra?.required && !formData[currentStep.extra.field]) {
      newErrors[currentStep.extra.field] = 'Ce champ est requis';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep()) {
      if (step < steps.length - 1) {
        setStep(step + 1);
      } else {
        handleSubmit();
      }
    }
  };

  const handleBack = () => {
    if (step > 0) setStep(step - 1);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    await new Promise(resolve => setTimeout(resolve, 1500));
    const dataToStore = {
      prenom: formData.prenom || '',
      genre: formData.genre || 'female',
      email: formData.email,
      dateNaissance: formData.dateNaissance,
      heureNaissance: formData.heureNaissance,
      ville: formData.ville,
      pays: formData.pays
    };
    localStorage.setItem('plume_astrale_data', JSON.stringify(dataToStore));

    if (isAuthenticated) {
      try {
        await updateProfile({
          prenom: formData.prenom || undefined,
          birth_date: formData.dateNaissance || undefined,
          birth_time: formData.heureNaissance || undefined,
          birth_place: formData.ville || undefined,
          birth_country: formData.pays || undefined,
          gender: formData.genre || undefined,
        });
      } catch {
        // Keep local fallback to avoid blocking the user flow.
      }
    }

    setIsSubmitting(false);
    const premiumRedirect = localStorage.getItem('plume_astrale_premium_redirect');
    if (premiumRedirect) {
      localStorage.removeItem('plume_astrale_premium_redirect');
      navigate('/premium/experience');
    } else if (isAuthenticated) {
      navigate('/mon-compte');
    } else {
      navigate('/apercu');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleNext();
  };

  return (
    <div className="min-h-screen relative">
      <SEO path="/formulaire" />
      <div className="relative z-10 flex flex-col justify-center px-6 md:px-8 py-12" style={{ minHeight: '100vh' }}>
      <div className="max-w-lg mx-auto w-full">

        {/* Progress */}
        <div className="flex items-center justify-between mb-16">
          <button
            onClick={handleBack}
            className={`link-editorial text-xs ${step === 0 ? 'invisible' : ''}`}
            data-testid="btn-back"
          >
            <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} />
            Retour
          </button>
          <span className="text-xs" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>
            {step + 1} / {steps.length}
          </span>
        </div>

        {/* Progress bar */}
        <div className="h-px mb-16 relative" style={{ background: 'var(--pa-divider)' }}>
          <div
            className="h-px absolute left-0 top-0 transition-all duration-700"
            style={{ width: `${((step + 1) / steps.length) * 100}%`, background: 'var(--pa-accent)' }}
          />
        </div>

        {/* Question */}
        <div className="text-center mb-12">
          <img src="https://customer-assets.emergentagent.com/job_6ebe2661-1b82-4742-afc5-632bf29dfcc5/artifacts/xb75bltg_img3.png" alt="" className="w-16 md:w-20 mx-auto mb-6 opacity-70" style={{ filter: 'drop-shadow(0 0 15px rgba(197,160,89,0.12))' }} />
          <h1
            className="text-2xl md:text-4xl mb-4"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
          >
            {currentStep.title}
          </h1>
          <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
            {currentStep.subtitle}
          </p>
        </div>

        {/* Input */}
        <div className="mb-12">
          {currentStep.type === 'gender' ? (
            <div className="flex gap-4 justify-center">
              {[{ val: 'female', label: 'Femme' }, { val: 'male', label: 'Homme' }].map(g => (
                <button
                  key={g.val}
                  onClick={() => setFormData({...formData, genre: g.val})}
                  className={`px-10 py-4 text-sm tracking-widest uppercase transition-all duration-300 ${
                    formData.genre === g.val
                      ? 'border-[#C5A059] bg-[#C5A059]/10 text-[#F0E6D3]'
                      : 'border-[#C5A059]/15 text-[#B8B0C8] hover:border-[#C5A059]/30'
                  }`}
                  style={{ border: `1px solid`, borderColor: formData.genre === g.val ? 'var(--pa-accent)' : 'var(--pa-divider)', letterSpacing: '0.12em' }}
                  data-testid={`genre-${g.val}`}
                >
                  {g.label}
                </button>
              ))}
            </div>
          ) : currentStep.type === 'date' ? (
            <div className="grid grid-cols-3 gap-3 max-w-md mx-auto">
              <select
                value={dDay}
                onChange={(e) => updateDate(dYear, dMonth, e.target.value)}
                className="input-editorial w-full text-center"
                data-testid="input-jour"
              >
                <option value="">Jour</option>
                {Array.from({ length: 31 }, (_, i) => i + 1).map((d) => (
                  <option key={d} value={String(d)}>{d}</option>
                ))}
              </select>
              <select
                value={dMonth}
                onChange={(e) => updateDate(dYear, e.target.value, dDay)}
                className="input-editorial w-full text-center"
                data-testid="input-mois"
              >
                <option value="">Mois</option>
                {MONTHS_FR.map((mLabel, idx) => (
                  <option key={idx} value={String(idx + 1)}>{mLabel}</option>
                ))}
              </select>
              <select
                value={dYear}
                onChange={(e) => updateDate(e.target.value, dMonth, dDay)}
                className="input-editorial w-full text-center"
                data-testid="input-annee"
              >
                <option value="">Annee</option>
                {YEARS.map((y) => (
                  <option key={y} value={String(y)}>{y}</option>
                ))}
              </select>
            </div>
          ) : currentStep.type === 'time' ? (
            <div className="grid grid-cols-2 gap-3 max-w-xs mx-auto">
              <select
                value={tHour}
                onChange={(e) => updateTime(e.target.value, tMin)}
                className="input-editorial w-full text-center"
                data-testid="input-heure"
              >
                <option value="">Heure</option>
                {Array.from({ length: 24 }, (_, i) => i).map((h) => (
                  <option key={h} value={String(h)}>{String(h).padStart(2, '0')} h</option>
                ))}
              </select>
              <select
                value={tMin}
                onChange={(e) => updateTime(tHour, e.target.value)}
                className="input-editorial w-full text-center"
                data-testid="input-minute"
              >
                <option value="">Minute</option>
                {Array.from({ length: 60 }, (_, i) => i).map((m) => (
                  <option key={m} value={String(m)}>{String(m).padStart(2, '0')}</option>
                ))}
              </select>
            </div>
          ) : (
            <input
              type={currentStep.type}
              value={formData[currentStep.field]}
              onChange={(e) => setFormData({...formData, [currentStep.field]: e.target.value})}
              onKeyPress={handleKeyPress}
              placeholder={currentStep.placeholder}
              className="input-editorial text-center text-lg w-full"
              autoFocus
              data-testid={`input-${currentStep.field}`}
            />
          )}
          {errors[currentStep.field] && (
            <p className="text-red-400/70 text-xs text-center mt-3">{errors[currentStep.field]}</p>
          )}

          {currentStep.extra && (
            <div className="mt-6">
              <input
                type="text"
                value={formData[currentStep.extra.field]}
                onChange={(e) => setFormData({...formData, [currentStep.extra.field]: e.target.value})}
                onKeyPress={handleKeyPress}
                placeholder={currentStep.extra.placeholder}
                className="input-editorial text-center text-lg w-full"
                data-testid={`input-${currentStep.extra.field}`}
              />
              {errors[currentStep.extra.field] && (
                <p className="text-red-400/70 text-xs text-center mt-3">{errors[currentStep.extra.field]}</p>
              )}
            </div>
          )}
        </div>

        {/* Action */}
        <div className="text-center">
          <button
            onClick={handleNext}
            disabled={isSubmitting}
            className="btn-editorial mx-auto"
            data-testid="btn-next"
          >
            {isSubmitting ? (
              <span>Calcul en cours...</span>
            ) : step === steps.length - 1 ? (
              <>
                <span>Reveler mon apercu</span>
                <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
              </>
            ) : (
              <>
                <span>Continuer</span>
                <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
              </>
            )}
          </button>

          {step === steps.length - 1 && (
            <p className="text-xs mt-6" style={{ color: 'var(--pa-muted)' }}>
              En continuant, vous acceptez nos conditions d'utilisation
            </p>
          )}
        </div>
      </div>
      </div>
    </div>
  );
};

export default Formulaire;
