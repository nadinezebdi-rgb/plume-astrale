import { useUserProfile } from './useUserProfile';
import { useEffect } from 'react';

/**
 * Hook pour pré-remplir automatiquement un formulaire avec les données du profil.
 * Utilisation: const form = useFormWithProfile();
 *              form.prenom -> données du profil
 */
export const useFormWithProfile = () => {
    const { profile, isProfileComplete } = useUserProfile();

    return {
          // Données du profil
          prenom: profile.prenom || '',
          fullName: profile.fullName || '',
          birthDate: profile.birthDate || '',
          birthTime: profile.birthTime || '',
          birthPlace: profile.birthPlace || '',
          birthCountry: profile.birthCountry || 'France',
          latitude: profile.latitude || '',
          longitude: profile.longitude || '',
          gender: profile.gender || 'female',
          email: profile.email || '',

          // Statut
          isComplete: isProfileComplete,
          hasProfile: !!profile.prenom,
    };
};
