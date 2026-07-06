# Intégration des Profils Utilisateur

## Overview

Nouvelle fonctionnalité: Les utilisateurs entrent une fois leurs données de naissance (date, heure, lieu, coordonnées) et ces données sont **automatiquement préremplies** dans tous les formulaires.

## Fichiers Créés

### 1. `src/hooks/useUserProfile.js`
Hook principal pour accéder/mettre à jour le profil utilisateur.

```javascript
const { profile, isProfileComplete, updateProfile } = useUserProfile();
```

### 2. `src/hooks/useFormWithProfile.js`
Hook utilitaire pour pré-remplir des formulaires automatiquement.

```javascript
const form = useFormWithProfile();
// form.prenom, form.birthDate, etc.
```

### 3. `src/context/AuthContext.js` (modifié)
Ajout de `setUser` au contexte pour permettre les mises à jour en temps réel.

## Utilisation dans les Formulaires

### Avant (ancien code)
```javascript
const [prenom, setPrenom] = useState('');
const [birthDate, setBirthDate] = useState('');
// ... champs vides à chaque chargement
```

### Après (nouveau code)
```javascript
import { useFormWithProfile } from '@/hooks/useFormWithProfile';

const form = useFormWithProfile();

useEffect(() => {
  setPrenom(form.prenom);
    setBirthDate(form.birthDate);
      // ...
      }, [form]);
      ```

      ## Prochaines Étapes

      1. ✅ Créer hook `useUserProfile`
      2. ✅ Créer hook `useFormWithProfile`  
      3. ⏳ Créer page `Profile.js` pour éditer le profil
      4. ⏳ Modifier `Horoscope.js` pour utiliser le hook
      5. ⏳ Modifier `Tarot.js` pour utiliser le hook
      6. ⏳ Modifier `LaQuestionDuMoment.js` pour utiliser le hook

      ## Backend Required

      S'assurer que `PUT /api/auth/profile` existe et accepte:
      ```json
      {
        "prenom": "string",
          "full_name": "string",
            "birth_date": "YYYY-MM-DD",
              "birth_time": "HH:MM",
                "birth_place": "string",
                  "birth_country": "string",
                    "latitude": "number",
                      "longitude": "number",
                        "gender": "string"
                        }
                        ```
