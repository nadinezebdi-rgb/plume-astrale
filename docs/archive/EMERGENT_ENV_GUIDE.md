# 🌐 Guide: Configuration Emergent pour Plume Astrale

## 📍 Vue d'Ensemble

Ce guide explique comment configurer votre application **consultation-astro** sur Emergent avec les variables d'environnement requises.

---

## 1️⃣ Accéder à Votre Application sur Emergent

### Étape 1: Se Connecter
1. Allez sur https://app.emergent.sh
2. Entrez vos identifiants
3. Vous arrivez sur le **Home Dashboard**

### Étape 2: Trouver Votre App
1. Cherchez l'onglet **"Deployed Apps"** ou **"Applications Déployées"**
   - Généralement en haut ou sur le côté gauche
2. Cliquez dessus
3. Vous verrez une liste de vos applications déployées

### Étape 3: Sélectionner "consultation-astro"
1. Trouvez **"consultation-astro"** dans la liste
2. Cliquez sur l'application
3. Vous arrivez sur le **dashboard de l'app**

---

## 2️⃣ Accéder aux Variables d'Environnement

### Trouver l'Option
Une fois sur le dashboard de l'app, cherchez l'une de ces options:

| Nom Possible | Emplacement |
|--------------|-------------|
| **"Environment Variables"** | Menu principal |
| **"Configure"** | Onglet ou bouton |
| **"Settings"** | Onglet latéral |
| **"Env Variables"** | Sous "Configuration" |
| **"Environment"** | Section admin |

**Conseil:** Regardez les onglets en haut de la page ou les menus latéraux.

### Cliquer sur Configuration
Une fois trouvée, cliquez sur **"Environment Variables"** ou **"Edit"**.

Vous devriez voir:
- [ ] Un formulaire vide OU
- [ ] Une liste de variables existantes

---

## 3️⃣ Ajouter Vos Clés API

### Variable 1: OPENAI_API_KEY

```
Nom: OPENAI_API_KEY
Valeur: sk-... (votre clé OpenAI)
Environnement: Production
Cliquez: "Add" ou "Save"
```

**Où l'obtenir:**
1. Allez sur https://platform.openai.com/api-keys
2. Connectez-vous avec votre compte OpenAI
3. Cliquez sur **"Create new secret key"**
4. **Copiez** la clé générée (commence par `sk-`)
5. **Collez-la** dans le champ Emergent

### Variable 2: ASTROLOGY_API_IO_KEY

```
Nom: ASTROLOGY_API_IO_KEY
Valeur: ask_... (votre clé Astrology API)
Environnement: Production
Cliquez: "Add" ou "Save"
```

**Où l'obtenir:**
1. Allez sur https://www.astrology-api.io
2. Connectez-vous à votre compte
3. Allez dans **"Settings"** ou **"API Keys"**
4. **Copiez** votre clé API (commence par `ask_`)
5. **Collez-la** dans le champ Emergent

### Variable 3: STRIPE_API_KEY (Optionnel - pour Paiements)

```
Nom: STRIPE_API_KEY
Valeur: sk_live_... (votre clé Stripe)
Environnement: Production
Cliquez: "Add" ou "Save"
```

**Où l'obtenir:**
1. Allez sur https://dashboard.stripe.com
2. Allez dans **"Developers"** → **"API Keys"**
3. **Copiez** la clé **"Secret"** (commence par `sk_live_`)
4. **Collez-la** dans le champ Emergent

### Variable 4: JWT_SECRET

```
Nom: JWT_SECRET
Valeur: un_secret_aleatoire_tres_long
Environnement: Production
Cliquez: "Add" ou "Save"
```

**Générer une clé:**
```bash
# Sur votre ordinateur, dans un terminal:
openssl rand -base64 32

# Cela génère quelque chose comme:
# xY7fK9mL0pQr5sT8uV1wX2yZ3aB4cD5eF6gH7iJ8k
```

### Variable 5 (Optionnel): EMERGENT_LLM_KEY

Seulement si vous utilisez l'intégration legacy Emergent.

```
Nom: EMERGENT_LLM_KEY
Valeur: votre_cle_universelle_emergent
Environnement: Production
Cliquez: "Add" ou "Save"
```

**Où l'obtenir:**
1. Cliquez sur l'**icône de profil** (haut droit de la page)
2. Sélectionnez **"Universal Key"** ou **"Clé Universelle"**
3. **Copiez** la clé affichée
4. **Collez-la** dans le champ Emergent

---

## 4️⃣ Vérifier les Variables (Avant Redéploiement)

Avant de redéployer, vérifiez:

- [ ] **OPENAI_API_KEY** présente et non vide
- [ ] **ASTROLOGY_API_IO_KEY** présente et non vide
- [ ] **STRIPE_API_KEY** présente (si paiements activés)
- [ ] **JWT_SECRET** présente et suffisamment longue
- [ ] Aucune **typo** dans les noms de variables
- [ ] Aucun **espace** avant/après les valeurs

---

## 5️⃣ Redéployer l'Application

Après avoir ajouté toutes les variables:

### Étape 1: Trouver le Bouton Redeploy
1. Retournez sur le dashboard de l'app
2. Cherchez le bouton **"Redeploy"** ou **"Redéployer"**
   - Souvent en haut droit de la page
   - Ou dans le menu "Actions"

### Étape 2: Cliquer sur Redeploy
1. Cliquez sur **"Redeploy"**
2. Confirmez si une popup apparaît

### Étape 3: Attendre le Déploiement
- **Durée:** 10-15 minutes généralement
- **Vous verrez:** Un indicateur de progression
- **Les logs** s'affichent en direct

### Étape 4: Vérifier Que Ça Démarre
Pendant le redéploiement, vous devriez voir:
```
✅ Building image...
✅ Pushing to registry...
✅ Starting containers...
✅ Application ready
```

**Si vous voyez des erreurs:**
- Allez à la section [Dépannage](#dépannage)

---

## 6️⃣ Vérifier Que Tout Fonctionne

### Tester l'API

Une fois le déploiement terminé:

```bash
# Tester que l'API répond
curl https://your-app-url.com/api/health

# Vous devriez voir une réponse comme:
# {"status": "ok"}
```

### Tester Depuis le Navigateur

1. Allez sur votre app: `https://your-app-url.com`
2. Testez les principales fonctionnalités:
   - [ ] La page se charge sans erreur
   - [ ] Le chat LLM fonctionne
   - [ ] Les calculs d'astrologie répondent
   - [ ] Les paiements Stripe fonctionnent (si activés)

### Vérifier les Logs

Pour voir les détails du déploiement:

1. Sur le dashboard Emergent
2. Cherchez **"Logs"** ou **"View Logs"**
3. Vous verrez les logs en temps réel
4. Cherchez des **erreurs** (en rouge)

---

## 🔍 Dépannage

### Erreur: "OPENAI_API_KEY manquante"

**Symptôme:**
```
Error: OPENAI_API_KEY env var manquante
Application failed to start
```

**Solution:**
1. Allez à **Environment Variables**
2. Vérifiez que `OPENAI_API_KEY` est présente
3. Vérifiez que la valeur n'est pas vide
4. Vérifiez qu'il n'y a pas d'espace avant/après
5. **Redéployez**

### Erreur: "Invalid API Key"

**Symptôme:**
```
Response 401: Invalid credentials
LLM service unavailable
```

**Solution:**
1. Vérifiez votre clé auprès du service (OpenAI, Astrology, etc.)
2. Assurez-vous que la clé n'est pas expirée
3. Régénérez la clé si nécessaire
4. **Copiez** la nouvelle clé **exactement** (sans espaces)
5. Mettez à jour dans Emergent
6. **Redéployez**

### Erreur: "Cannot connect to service"

**Symptôme:**
```
Connection timeout: api.astrology-api.io
Service unreachable
```

**Solution:**
1. Vérifiez que l'IP du serveur Emergent peut atteindre l'API externe
2. Vérifiez les pare-feu
3. Testez directement depuis le terminal:
   ```bash
   curl -H "Authorization: Bearer $ASTROLOGY_API_IO_KEY" \
        https://api.astrology-api.io/health
   ```
4. Si ça échoue, il y a un problème avec la clé ou le réseau

### L'app prend très longtemps à déployer

**Symptôme:**
- Redéploiement qui prend 20+ minutes
- Indicateur de progression bloqué

**Solution:**
1. **Attendez** (parfois c'est normal)
2. Rafraîchissez la page Emergent (F5)
3. Cherchez les **logs d'erreur**
4. Essayez un **redéploiement** à nouveau
5. Si ça persiste, **contactez le support Emergent**

---

## ⚡ Raccourcis Pratiques

### Redéploiement Rapide (Après Changement de Variables)
1. Dashboard Emergent → Deployed Apps → consultation-astro
2. Onglet Environment Variables → Vérifiez les changements
3. Bouton Redeploy → Confirmez
4. Attendez 10-15 min
5. Vérifiez que ça démarre sans erreurs

### Copier une Variable Depuis une Autre App
Si vous avez une autre app avec les mêmes clés:
1. Ouvrez l'autre app dans Emergent
2. Allez à Environment Variables
3. **Copiez** la valeur
4. Allez à consultation-astro
5. **Collez** dans la variable correspondante
6. Redéployez

---

## 📝 Notes Importantes

### À Faire ✅
- ✅ Garder les clés API **privées** et **sécurisées**
- ✅ **Jamais** partager les clés par email ou chat
- ✅ Tester localement avant de déployer en prod
- ✅ Documenter les changements de variables
- ✅ Vérifier que l'app démarre après un changement

### À NE PAS FAIRE ❌
- ❌ Mettre les clés dans le code
- ❌ Commit des clés sur GitHub
- ❌ Partager les clés avec des personnes non autorisées
- ❌ Utiliser les mêmes clés pour test et production
- ❌ Laisser les anciennes clés configurées (les régénérer si compromise)

---

## 📞 Support

Si vous rencontrez des problèmes:

1. **Consultez la documentation:** [ENV_SETUP.md](./ENV_SETUP.md)
2. **Vérifiez les logs Emergent:** Logs Tab
3. **Testez localement:** `docker-compose up`
4. **Contactez le support:**
   - Emergent: https://app.emergent.sh → Help/Support
   - OpenAI: https://help.openai.com
   - Stripe: https://support.stripe.com

---

**Dernière mise à jour:** 2026-07-07

