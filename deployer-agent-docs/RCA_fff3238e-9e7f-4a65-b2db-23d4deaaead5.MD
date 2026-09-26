# RCA — PDF Thème Natal toujours en fond sombre en production (plume-astrale.fr)

## Verdict court
Le fix EST bien déployé en production. Ce n'est **PAS** un problème de propagation.
Le nouveau moteur `book_engine_v2` (print / fond blanc) **s'exécute en prod mais échoue à chaque
génération** et retombe automatiquement sur l'ancien moteur `natal_pdf_v2` (fond sombre legacy),
car **le conteneur runtime de production ne contient NI Chromium NI WeasyPrint**.

## Contexte du run
- Deployment: `consultation-astro` (template farm — fastapi_react_mongo_shadcn, frontend Cloudflare)
- Run actif (LIVE): `fff3238e-9e7f-4a65-b2db-23d4deaaead5`
  - type: redeploy, trigger: agentic, status: success
  - créé 2026-09-25 16:49:17 UTC, **terminé 2026-09-25 17:08:46 UTC**
  - image: `...consultation-astro:fff3238e-...`
- Pod: `r-fff3238e-...-2zh7z`, phase Running depuis 17:05:39 UTC, ready=true, 1 restart
  (dernière terminaison: Completed / exit 0 à 17:11:51 — démarrage normal). Aucun rollout en cours.

## Réponses point par point au diagnostic demandé

### 1. Quel commit tourne en prod ? (3b2888d ou antérieur ?)
Le SHA git exact n'a **pas pu être lu directement** : le bac à sable eph a échoué en boucle
(envcore 500/504/409 — `container not found`, `exec_timeout`, `pod phase=Failed`) — indisponibilité
d'infra, sans rapport avec l'app.
**Cependant le code du fix EST prouvé présent et actif** : la prod émet la chaîne de log qui
n'existe QUE dans le nouvel adaptateur —
`ERROR:services.natal_pdf_adapter:[book_engine_v2 print] fallback to natal_pdf_v2 dark`.
L'ancien code (dark uniquement) n'aurait jamais tenté `book_engine_v2 print`.
➡️ **Le pod tourne bien la version corrigée (commit 3b2888d ou équivalent), pas un commit antérieur.**

### 2. `/app/backend/services/natal_manuscript_builder.py` présent ?
Non vérifiable au niveau fichier (eph HS), mais **fonctionnellement confirmé** : le renderer log
`INFO:services.book_engine_v2.renderer:[book_v2] 8 pages assemblées (1 chapitres)` et l'appel
`render_manuscript_to_pdf_v2(manuscript, profile='print')` s'exécutent — le manuscrit est bien
construit puis passé au renderer. La chaîne manuscript builder → book_engine_v2 est donc présente.

### 3. Chaînes dans `natal_pdf_adapter.py` (book_engine_v2_print / render_manuscript_to_pdf_v2 / natal_pdf_v2_dark_fallback)
Non grep-ables directement (eph HS). Mais l'adaptateur émet son propre message de fallback et invoque
`render_manuscript_to_pdf_v2` puis bascule sur `natal_pdf_v2` dark → la logique des 3 chaînes est
active en prod. (Vérification octet-par-octet non faite faute de sandbox.)

### 4. Fallback `[book_engine_v2 print] fallback to natal_pdf_v2 dark` présent ?
**OUI — il se déclenche à CHAQUE génération.**
`ERROR:services.natal_pdf_adapter:[book_engine_v2 print] fallback to natal_pdf_v2 dark: WeasyPrint non installé et Chromium indisponible`

### 5. Stack trace exacte du fallback (CAUSE RACINE)
Deux backends de rendu tentés, tous deux absents du conteneur prod :

```
# Tentative 1 — Chromium
File "/app/backend/services/book_engine_v2/renderer.py", line 381, in _render_pdf_chromium
    raise RuntimeError('Chromium introuvable')
RuntimeError: Chromium introuvable
WARNING:services.book_engine_v2.renderer:[book_v2] Chromium fail, fallback WeasyPrint: Chromium introuvable

# Tentative 2 — WeasyPrint
File "/app/backend/services/book_engine_v2/renderer.py", line 406, in _render_pdf_weasyprint
ModuleNotFoundError: No module named 'weasyprint'
File "/app/backend/services/book_engine_v2/renderer.py", line 408, in _render_pdf_weasyprint
    raise RuntimeError('WeasyPrint non installé et Chromium indisponible')
File "/app/backend/services/book_engine_v2/renderer.py", line 430, in render_manuscript_to_pdf_v2
RuntimeError: WeasyPrint non installé et Chromium indisponible

# Adaptateur → fallback dark legacy
ERROR:services.natal_pdf_adapter:[book_engine_v2 print] fallback to natal_pdf_v2 dark: WeasyPrint non installé et Chromium indisponible
```

**Diagnostic précis :**
- `Chromium introuvable` = le binaire Chromium n'est PAS installé dans l'image runtime de prod
  (image de base farm — ne fournit pas Chromium).
- `ModuleNotFoundError: No module named 'weasyprint'` = le paquet Python `weasyprint` n'est PAS
  installé dans l'image de prod (absent de `backend/requirements.txt`, ou non capturé par le
  `pip freeze` de la preview).

**Pourquoi ça marche en preview mais pas en prod :** l'environnement de preview (agent-env) dispose
de Chromium et/ou WeasyPrint ; l'image conteneur déployée est construite à partir de l'image de base
farm qui n'embarque aucun de ces deux moteurs. Le code est bien propagé — le *runtime de rendu* ne
l'est pas.

⚠️ Point de vigilance build : le Dockerfile farm installe les deps Python avec
`pip install --no-cache-dir --no-dependencies -r requirements.txt`. Donc même en ajoutant
`weasyprint` à requirements.txt, il faut AUSSI y épingler toutes ses dépendances transitives
(pydyf, cffi, tinycss2, cssselect2, Pyphen, fonttools, Pillow…) — un `pip install weasyprint` fait
en preview avant redéploiement les capturera via le pip freeze. Et WeasyPrint requiert en plus des
**bibliothèques système natives** (libpango-1.0-0, libpangocairo-1.0-0, libgdk-pixbuf-2.0-0,
libcairo2, libffi, polices) qui doivent être apt-installées dans l'image (Dockerfile.cloudbuild).

### 6. État du pipeline / dernière rolling update
- Dernier déploiement réussi : run `fff3238e`, **terminé 2026-09-25 17:08:46 UTC**.
- **Aucun build ni rollout en cours.** Pod stable et « ready » depuis 17:05:39 UTC.
- **ETA : sans objet** — il n'y a rien à attendre. Le rollout est déjà terminé ; l'image live sert
  déjà le code corrigé. Le PDF reste sombre non pas parce qu'un déploiement est en attente, mais
  parce que l'image ne contient pas les moteurs de rendu. Un simple redéploiement à l'identique
  ne changera rien.

## Correctif recommandé (à appliquer par E1, puis redéployer)
Fournir au conteneur prod AU MOINS un backend de rendu utilisé par `book_engine_v2` :

**Option A — WeasyPrint (recommandée, correspond au moteur ciblé) :**
1. En preview : `pip install weasyprint`, puis régénérer `backend/requirements.txt` (pip freeze) pour
   y capturer weasyprint + TOUTES ses deps transitives (obligatoire à cause de `--no-dependencies`).
2. Ajouter au build (Dockerfile.cloudbuild, stages `backend-build` ET `final-base`) une couche apt
   pour les libs natives WeasyPrint :
   `libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libcairo2 libffi8 shared-mime-info fonts-dejavu`.
3. Redéployer.

**Option B — Chromium :** installer un binaire Chromium dans l'image runtime et s'assurer que
`_render_pdf_chromium` pointe sur son chemin. Plus lourd (dépendances headless nombreuses).

Sans l'un de ces deux backends installé DANS l'image, le fallback dark continuera de se déclencher.

## Constat secondaire (non lié au PDF, mais bloquant l'envoi d'emails)
Le journal d'emails échoue en masse :
`[journal_email] Exception sending to <...>: object dict can't be used in 'await' expression`
(pour de nombreux destinataires, dont nadine.zebdi@gmail.com et admin@plume-astrale.fr).
➡️ Bug de code : on `await` une fonction qui renvoie un `dict` au lieu d'une coroutine. À corriger
séparément dans le chemin d'envoi d'email/journal.

## Ce qui n'a PAS pu être vérifié
- SHA git exact du pod, présence fichier de `natal_manuscript_builder.py`, et grep octet-par-octet
  des 3 chaînes dans `natal_pdf_adapter.py` : le bac à sable eph était en panne (échecs répétés
  d'infra). Ces points sont déduits avec un très haut niveau de confiance à partir des logs runtime,
  pas inspectés directement.
