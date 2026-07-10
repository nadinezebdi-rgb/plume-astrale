# 🌐 Configuration Custom Domain Emergent pour Plume Astrale

## État Actuel
- **Domain:** plume-astrale.fr
- **Pointeur actuel:** Vercel (INCORRECT)
- **À pointer vers:** Emergent (notre serveur principal)

## 3 OPTIONS DE CONFIGURATION

### **OPTION 1: Nameservers Emergent (RECOMMANDÉE)**

Si Emergent propose des nameservers dédiés:

1. **Sur Emergent Dashboard:**
   - Aller à App → Settings → Domains → Add Domain
   - Entrer: `plume-astrale.fr`
   - Copier les **4 nameservers Emergent** proposés

2. **Chez ton registrar (ex: OVH, GoDaddy, Namecheap):**
   - Connexion domain → DNS Settings
   - Remplacer les nameservers Vercel par ceux d'Emergent
   - Sauvegarder
   - Attendre propagation (5-30 min)

3. **Vérifier:**
   ```bash
   nslookup plume-astrale.fr
   # Résultat: doit afficher nameservers Emergent
   ```

### **OPTION 2: CNAME (si Emergent n'a pas de nameservers)**

Si Emergent fourni une URL de type `app-xyz.emergent.sh`:

1. **Chez ton registrar:**
   - DNS Settings → Records
   - Créer un CNAME:
     ```
     Type: CNAME
     Host: plume-astrale.fr (ou vide = root)
     Target: app-xyz.emergent.sh
     TTL: 3600
     ```
   - Sauvegarder

2. **Attention:** Les enregistrements CNAME ne peuvent pas être au domaine root
   - **Mieux:** utiliser `app.plume-astrale.fr` → CNAME → Emergent
   - **Ou:** Utiliser "ALIAS" record si ton registrar le supporte

### **OPTION 3: A Record (IP statique)**

Si tu connais l'IP de ton serveur Emergent:

1. **Obtenir l'IP:**
   ```bash
   nslookup app-xyz.emergent.sh
   # Copier l'IP (ex: 123.45.67.89)
   ```

2. **Chez ton registrar:**
   - DNS Settings → A Record
   - ```
     Type: A
     Host: @ (ou plume-astrale.fr)
     Value: 123.45.67.89
     TTL: 3600
     ```

## CHECKLIST POST-CONFIGURATION

- [ ] Vérifier que `plume-astrale.fr` charge depuis Emergent (pas Vercel)
- [ ] Vérifier que le certificat SSL s'active automatiquement
- [ ] Tester toutes les routes API: `https://plume-astrale.fr/api/...`
- [ ] Tester la page d'accueil: `https://plume-astrale.fr/`
- [ ] Vérifier que pas de "mixed content" warnings (HTTP vs HTTPS)
- [ ] Revalider la propagation DNS: https://www.whatsmydns.net/

## 🚨 SI PROBLÈMES

### Problème: Site indisponible après changement
**Solution:**
1. Revert nameservers/CNAME à Vercel (rollback rapide)
2. Vérifier que ton app Emergent est running
3. Vérifier CORS_ORIGINS dans Emergent env vars

### Problème: SSL certificate non activé
**Solution:**
- Attendre 15-20 min après changement DNS
- Recharger le dashboard Emergent
- Si toujours pas actif: contacter support Emergent

### Problème: Certificat "mismatch" (domain not matching)
**Solution:**
- Vérifier que le domain dans Emergent Settings = `plume-astrale.fr` exactement
- Pas d'espaces, pas de typo

## 📋 VARIABLES D'ENV À VÉRIFIER DANS EMERGENT

Avant de finaliser le domain, vérifier dans Emergent Settings → Environment Variables:

- [ ] `OPENAI_API_KEY` = sk-... (non vide)
- [ ] `ASTROLOGY_API_IO_KEY` = ask_... (non vide)  
- [ ] `ASTROLOGY_API_USER_ID` = 649448
- [ ] `ASTROLOGY_API_ACCESS_TOKEN` = (si applicable)
- [ ] `EMERGENT_LLM_KEY` = clé universelle (si besoin)
- [ ] `JWT_SECRET` = (long secret, au moins 32 chars)
- [ ] `CORS_ORIGINS` = inclut https://plume-astrale.fr
- [ ] `DATABASE_URL` ou équivalent pour Supabase = https://ebwicqvbkwogxneipaxh.supabase.co

## ✅ APRÈS CONFIGURATION

```bash
# Test rapide depuis terminal:
curl -I https://plume-astrale.fr/
# Attendu: HTTP/2 200 ou 301 (redirect)

curl -I https://plume-astrale.fr/api/health
# Attendu: HTTP/2 200 + body JSON
```
