/**
 * EXEMPLE: Comment ajouter la pré-remplissage automatique du profil
 * à une page existante (ex: Horoscope.js, Tarot.js, etc.)
 */

import { useFormWithProfile } from '@/hooks/useFormWithProfile';
import { useEffect, useState } from 'react';

export default function Horoscope() {
    // ✅ NOUVEAU: Ajouter ce hook
  const formProfile = useFormWithProfile();

  // États du formulaire
  const [formData, setFormData] = useState({
        prenom: '',
        email: '',
        birthDate: '',
        birthTime: '',
        birthPlace: '',
        birthCountry: 'France',
  });

  // ✅ NOUVEAU: Ajouter cet useEffect pour pré-remplir
  useEffect(() => {
        if (formProfile.hasProfile) {
                setFormData({
                          prenom: formProfile.prenom,
                          email: formProfile.email,
                          birthDate: formProfile.birthDate,
                          birthTime: formProfile.birthTime,
                          birthPlace: formProfile.birthPlace,
                          birthCountry: formProfile.birthCountry,
                });
        }
  }, [formProfile]);

  // Reste du code existant...
  const handleSubmit = (e) => {
        e.preventDefault();
        // Votre logique existante
  };

  return (
        <form onSubmit={handleSubmit}>
  {/* Vos champs de formulaire existants */}
          <input 
        value={formData.prenom}
        placeholder="Prénom"
        // ...
      />
        {/* etc */}
          </form>
  );
}
