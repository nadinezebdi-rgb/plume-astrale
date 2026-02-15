import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, ArrowLeft, Calendar, Clock, MapPin, Mail, User } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const Formulaire = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    prenom: '',
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
      title: 'Quel est votre prénom ?',
      subtitle: 'Le nom que porte votre âme en cette vie',
      icon: <User className="w-8 h-8" strokeWidth={1} />,
      field: 'prenom',
      type: 'text',
      placeholder: 'Votre prénom',
      required: false
    },
    {
      id: 'email',
      title: 'Votre adresse email',
      subtitle: 'Pour recevoir votre manuscrit céleste',
      icon: <Mail className="w-8 h-8" strokeWidth={1} />,
      field: 'email',
      type: 'email',
      placeholder: 'votre@email.com',
      required: true
    },
    {
      id: 'date',
      title: 'Quand êtes-vous né(e) ?',
      subtitle: 'Le jour où les étoiles se sont alignées pour vous',
      icon: <Calendar className="w-8 h-8" strokeWidth={1} />,
      field: 'dateNaissance',
      type: 'date',
      required: true
    },
    {
      id: 'heure',
      title: 'À quelle heure ?',
      subtitle: 'Essentiel pour calculer votre ascendant',
      icon: <Clock className="w-8 h-8" strokeWidth={1} />,
      field: 'heureNaissance',
      type: 'time',
      required: true
    },
    {
      id: 'lieu',
      title: 'Où êtes-vous né(e) ?',
      subtitle: 'Le lieu de votre première respiration terrestre',
      icon: <MapPin className="w-8 h-8" strokeWidth={1} />,
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
    if (step > 0) {
      setStep(step - 1);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    // Simuler un délai de traitement
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Stocker les données avec validation
    const dataToStore = {
      prenom: formData.prenom || '',
      email: formData.email,
      dateNaissance: formData.dateNaissance,
      heureNaissance: formData.heureNaissance,
      ville: formData.ville,
      pays: formData.pays
    };
    
    localStorage.setItem('plume_astrale_data', JSON.stringify(dataToStore));
    
    setIsSubmitting(false);
    navigate('/apercu');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleNext();
    }
  };

  const progress = ((step + 1) / steps.length) * 100;

  return (
    <div className="min-h-screen relative flex items-center justify-center px-4 py-12">
      <StarField />
      
      {/* Background */}
      <div 
        className="fixed inset-0 opacity-10"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1603669435608-eb647988e585?w=1920&auto=format&fit=crop&q=80')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      />
      
      <div className="relative z-10 w-full max-w-2xl">
        {/* Progress Bar */}
        <div className="mb-12">
          <div className="flex justify-between items-center mb-4">
            <button
              onClick={handleBack}
              className={`flex items-center gap-2 text-[#C5A059]/70 hover:text-[#C5A059] transition-colors ${step === 0 ? 'invisible' : ''}`}
              data-testid="btn-back"
            >
              <ArrowLeft className="w-4 h-4" strokeWidth={1} />
              <span className="text-sm">Retour</span>
            </button>
            <span className="text-[#E0D9F6]/50 text-sm">
              {step + 1} / {steps.length}
            </span>
          </div>
          <div className="h-1 bg-[#2D1B4E] rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-[#C5A059] to-[#FFD700] transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
        
        {/* Form Card */}
        <div className="card-mystical text-center">
          {/* Icon */}
          <div className="text-[#C5A059] mb-8 animate-float">
            {currentStep.icon}
          </div>
          
          {/* Title */}
          <h1 className="text-2xl md:text-4xl mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
            {currentStep.title}
          </h1>
          
          <p className="text-[#E0D9F6]/60 mb-12 font-light">
            {currentStep.subtitle}
          </p>
          
          {/* Input */}
          <div className="space-y-6 mb-12">
            <div className="relative">
              <input
                type={currentStep.type}
                value={formData[currentStep.field]}
                onChange={(e) => setFormData({...formData, [currentStep.field]: e.target.value})}
                onKeyPress={handleKeyPress}
                placeholder={currentStep.placeholder}
                className="input-mystical"
                autoFocus
                data-testid={`input-${currentStep.field}`}
              />
              {errors[currentStep.field] && (
                <p className="text-red-400 text-sm mt-2">{errors[currentStep.field]}</p>
              )}
            </div>
            
            {currentStep.extra && (
              <div className="relative">
                <input
                  type="text"
                  value={formData[currentStep.extra.field]}
                  onChange={(e) => setFormData({...formData, [currentStep.extra.field]: e.target.value})}
                  onKeyPress={handleKeyPress}
                  placeholder={currentStep.extra.placeholder}
                  className="input-mystical"
                  data-testid={`input-${currentStep.extra.field}`}
                />
                {errors[currentStep.extra.field] && (
                  <p className="text-red-400 text-sm mt-2">{errors[currentStep.extra.field]}</p>
                )}
              </div>
            )}
          </div>
          
          {/* Submit Button */}
          <button
            onClick={handleNext}
            disabled={isSubmitting}
            className="btn-mystical-filled rounded-full flex items-center gap-3 mx-auto"
            data-testid="btn-next"
          >
            {isSubmitting ? (
              <>
                <div className="w-5 h-5 border-2 border-[#0F0518] border-t-transparent rounded-full animate-spin" />
                <span>Calcul des astres...</span>
              </>
            ) : step === steps.length - 1 ? (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Révéler Mon Aperçu</span>
              </>
            ) : (
              <>
                <span>Continuer</span>
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
          
          {step === steps.length - 1 && (
            <p className="text-[#E0D9F6]/40 text-sm mt-6 font-light">
              En continuant, vous acceptez nos conditions d'utilisation
            </p>
          )}
        </div>
        
        {/* Security Badge */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-[#1A0B2E]/50 rounded-full border border-[#C5A059]/10">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-sm text-[#E0D9F6]/50">Connexion sécurisée</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Formulaire;
