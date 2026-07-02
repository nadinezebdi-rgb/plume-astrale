import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { useCallback } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Hook pour accéder et gérer les données du profil utilisateur.
 * Permet de lire et mettre à jour les informations de naissance de l'utilisateur.
 */
export const useUserProfile = () => {
    const { user, token, setUser } = useAuth();

    // Lire les données du profil
    const profile = {
          prenom: user?.prenom || '',
          fullName: user?.full_name || '',
          email: user?.email || '',
          birthDate: user?.birth_date || '',
          birthTime: user?.birth_time || '',
          birthPlace: user?.birth_place || '',
          birthCountry: user?.birth_country || 'France',
          latitude: user?.latitude || null,
          longitude: user?.longitude || null,
          gender: user?.gender || 'female',
    };

    // Vérifier si le profil est complet
    const isProfileComplete = Boolean(
          profile.prenom &&
          profile.birthDate &&
          profile.birthTime &&
          profile.birthPlace &&
          profile.latitude &&
          profile.longitude
        );

    // Mettre à jour le profil
    const updateProfile = useCallback(async (updates) => {
          if (!token) throw new Error('Utilisateur non authentifié');

                                          try {
                                                  const response = await axios.put(
                                                            `${API}/api/auth/profile`,
                                                            updates,
                                                    {
                                                                headers: { Authorization: `Bearer ${token}` },
                                                    }
                                                          );

            // Mettre à jour le contexte avec les nouvelles données
            if (setUser) {
                      setUser((prev) => ({ ...prev, ...response.data.user }));
            }

            return response.data.user;
                                          } catch (error) {
                                                  console.error('Erreur lors de la mise à jour du profil:', error);
                                                  throw error;
                                          }
    }, [token, setUser]);

    return {
          profile,
          isProfileComplete,
          updateProfile,
          isAuthenticated: !!user,
    };
};
