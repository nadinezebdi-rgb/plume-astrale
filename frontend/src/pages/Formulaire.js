import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, ArrowLeft } from 'lucide-react';

const Formulaire = () => {
  const navigate = useNavigate();
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
  const [errors, setErrors] = useState({});

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
    setIsSubmitting(false);
    const premiumRedirect = localStorage.getItem('plume_astrale_premium_redirect');
    if (premiumRedirect) {
      localStorage.removeItem('plume_astrale_premium_redirect');
      navigate('/premium/experience');
    } else {
      navigate('/apercu');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleNext();
  };

  return (
    <div className="min-h-screen relative">
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
