# Mail à envoyer à support@emergent.sh

## Option rapide — lien `mailto:` prêt à cliquer

Copiez-collez ce lien dans votre navigateur (ou cliquez-le depuis votre app mail web connectée) : il ouvre votre client mail avec destinataire, objet et corps déjà remplis.

> Avant d'envoyer, remplacez `[VOTRE_JOB_ID]` dans l'objet par l'ID visible dans l'URL de votre projet Emergent (segment après `/job/`).

```
mailto:support@emergent.sh?subject=Commande%20de%20build%20personnalis%C3%A9e%20%E2%80%94%20yarn%20build%3Aseo%20%E2%80%94%20Plume%20Astrale%20%5B%5BVOTRE_JOB_ID%5D%5D&body=Bonjour%2C%0D%0A%0D%0AJe%20d%C3%A9ploie%20mon%20application%20Plume%20Astrale%20%28React%20CRA%20%2B%20FastAPI%29%20sur%20Emergent.%20Mon%20d%C3%A9p%C3%B4t%20contient%20dans%20frontend%2Fpackage.json%20un%20script%20personnalis%C3%A9%20%60build%3Aseo%60%20qui%20g%C3%A9n%C3%A8re%20le%20build%20standard%20CRA%20puis%20pr%C3%A9-rend%20mes%20routes%20pour%20le%20SEO%20et%20le%20sitemap.%0D%0A%0D%0ALe%20pipeline%20de%20d%C3%A9ploiement%20Emergent%20ex%C3%A9cute%20actuellement%20%60yarn%20build%60.%20Je%20souhaiterais%20qu%27il%20ex%C3%A9cute%20%60yarn%20build%3Aseo%60%20%C3%A0%20la%20place.%0D%0A%0D%0APouvez-vous%20me%20confirmer%20%3A%0D%0A1%29%20S%27il%20existe%20un%20fichier%20de%20configuration%20self-serve%20%28.emergent%2Fdeploy.yml%20ou%20similaire%29%20que%20je%20peux%20committer%20moi-m%C3%AAme%20pour%20surcharger%20la%20commande%20de%20build.%0D%0A2%29%20Sinon%2C%20pouvez-vous%20configurer%20manuellement%20%60yarn%20build%3Aseo%60%20comme%20commande%20de%20build%20pour%20mon%20projet%20%3F%0D%0A%0D%0ADomaine%20prod%20%3A%20plumeastrale.com%0D%0APr%C3%A9visualisation%20%3A%20https%3A%2F%2Fconsultation-astro.preview.emergentagent.com%0D%0AStack%20%3A%20React%2018%20%28CRA%29%2C%20Yarn%2C%20pr%C3%A9rendu%20via%20puppeteer-core%20%28%2B45s%29.%0D%0A%0D%0AMerci%20beaucoup%2C%0D%0APlume%20Astrale
```

**Comment récupérer votre job ID**
1. Ouvrez votre projet dans Emergent.
2. Dans l'URL, cherchez le segment après `/job/` — format `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`.
3. Remplacez `[VOTRE_JOB_ID]` dans l'objet du mail avant l'envoi.

---

## Version texte brut (si le mailto ne fonctionne pas)

**À :** support@emergent.sh
**Objet :** Commande de build personnalisée — `yarn build:seo` — Plume Astrale `[VOTRE_JOB_ID]`

Bonjour,

Je déploie mon application **Plume Astrale** (React CRA + FastAPI) sur Emergent. Mon dépôt contient dans `frontend/package.json` un script personnalisé `build:seo` qui génère le build standard CRA puis pré-rend mes routes pour le SEO et le sitemap.

Le pipeline de déploiement Emergent exécute actuellement `yarn build`. Je souhaiterais qu'il exécute **`yarn build:seo`** à la place.

Pouvez-vous me confirmer :
1. S'il existe un fichier de configuration self-serve (`.emergent/deploy.yml` ou similaire) que je peux committer moi-même pour surcharger la commande de build.
2. Sinon, pouvez-vous configurer manuellement `yarn build:seo` comme commande de build pour mon projet ?

**Domaine prod** : plumeastrale.com
**Prévisualisation** : https://consultation-astro.preview.emergentagent.com
**Stack** : React 18 (CRA), Yarn, prérendu via puppeteer-core (+45s)

Merci beaucoup,
Plume Astrale

---

### 📎 Pièce jointe recommandée
Screenshot de votre `frontend/package.json` ouvert sur la ligne `"build:seo": …` pour que le support confirme la commande d'un coup d'œil.
