# Audit du dépôt — 12 octobre 2026

## Synthèse

Audit de `nadinezebdi-rgb/plume-astrale` au SHA `47d815c5a09e7d0d3df388163283012711e3f78a` (`main`). Les 12 branches visibles au début de l’audit étaient toutes non protégées.

- Neuf des onze branches autres que `main` sont intégrées à `main` ou n’apportent aucun patch inédit. Leur retard n’est pas un signe de branche cassée.
- Les deux branches Copilot liées au code promo sont en retard, contiennent respectivement 2 et 4 commits uniques et entrent en conflit avec `main`. La PR #167 est toujours ouverte et en brouillon; ne pas fusionner ces branches telles quelles.
- Le dernier run Smoke API observé sur `main` est réussi. Dans les dix derniers runs Smoke terminés sur `main` consultés, huit réussissent et deux échouent sur une importation `Optional` manquante; ce défaut a été corrigé ensuite dans la restauration du routeur Composer par #168.
- Les dix derniers runs du cron de journal consultés sont en échec. Les deux journaux examinés retournent HTTP 403 et montrent que le secret `CRON_SECRET` est vide côté Actions. Le dernier run précède aussi le correctif d’authentification du cron de #169. Une vérification après ce correctif manque; la configuration du secret doit être contrôlée manuellement.
- Le build strict frontend et les 14 tests Jest passent après les corrections ciblées de cette PR. Le backend ne peut pas être testé intégralement dans ce sandbox: ses dépendances sont absentes et les index pip sont injoignables.

Aucun déploiement n’a été lancé, aucun service de production interrogé directement, aucun paiement réalisé et aucun secret modifié.

## 1. Périmètre et configuration

### Stack et commandes repérées

- Frontend React 19, React Router 7 et CRACO (`frontend/package.json`); le dépôt fournit `npm run build` et `npm test`, mais aucun script frontend `lint`.
- Backend FastAPI/Python, dépendances déclarées dans `backend/requirements.txt`; smoke local documenté par `python tests/smoke_api_compat.py --suite quick` et `--suite pdf`.
- Workflows actifs pertinents: `Smoke API Compatibility` et `Daily Journal Cron`. Le premier installe le backend et exécute seulement les deux suites smoke; il ne lance ni Jest/build frontend ni la suite pytest backend.
- Déploiements déclarés: `vercel.json`, `backend/railway.toml`, `frontend/railway.toml` et les Dockerfiles sous `deploy/`. La présence de ces fichiers ne prouve pas quel service sert actuellement le site.

### Comparaison exhaustive des branches initiales

Les compteurs sont ceux de `git rev-list --left-right --count origin/main...origin/<branche>`: **en retard / en avance**. La comparaison a été faite après récupération de l’historique complet. Les conclusions de fusion proviennent d’un `git merge-tree --write-tree` non appliqué au worktree.

| Branche | HEAD | Retard / avance | PR associée | Conclusion par rapport à `main` |
|---|---|---:|---|---|
| `UPDATE-110` | `eb2a21eebaefa278de971987bf0f8f241e49092e` | 75 / 0 | #165, fermée | Déjà intégrée; fusion propre. |
| `chore/migration-guide-redact` | `eb0db5685b3e41f6b57b504e39ad92824843e73d` | 9 / 0 | #173, fermée | Déjà intégrée; fusion propre. |
| `copilot/copilotsec-004-remove-tout2026` | `ba5737a0760282442d4d97f5322531d168241562` | 20 / 4 | Aucune trouvée | Divergente; conflits reproduits, voir ci-dessous. |
| `copilot/sec-004-remove-tout2026` | `4b1bca6c03c8e17686163b019f46e71a4d4ef792` | 28 / 2 | #167, ouverte/brouillon | Divergente; conflits reproduits, voir ci-dessous. |
| `emergent-sync-v2` | `4d264ac0ddf92b870296e9fffb460cf90a11e084` | 28 / 0 | Aucune trouvée | Déjà intégrée; fusion propre. |
| `fix/audit-checkout-webhook-pdf` | `2d8c704a5492b48bdc17787826b1bee02ab7bb6a` | 15 / 0 | #170, fermée | Déjà intégrée; fusion propre. |
| `livre-backend-livraison` | `26c19d4b15998ba42f0f58a384c0d14090886e51` | 98 / 0 | #163, fermée | Déjà intégrée; fusion propre. |
| `livre-frontend-configurateur` | `386ed1b6601ae8790ace03a5eebbb15f58ad6014` | 99 / 0 | #164, fermée | Déjà intégrée; fusion propre. |
| `main` | `47d815c5a09e7d0d3df388163283012711e3f78a` | 0 / 0 | Branche par défaut | Base de l’audit. |
| `railway-deploy-check` | `c86de9fa347917c4efc43dc31a3d8d948c21faa1` | 84 / 0 | Aucune trouvée | Déjà intégrée; fusion propre. |
| `update-99` | `c54f14a4a226a9f1ed0b54725d2505f30d9aa907` | 584 / 0 | #157 et #159, fermées | Déjà intégrée; fusion propre. |
| `update-100` | `a8c23e4000cc33e7091e9e750d3f51eb83f7fb2e` | 120 / 1 | #160, fermée | Le seul commit en avance est équivalent à un patch déjà dans `main` (`git log --cherry-pick`: zéro commit unique); fusion propre. |

Les 12 branches listées par GitHub indiquaient `protected: false`. La branche `copilot/audit-depot-nadine` et la PR #178 ont été créées pour ce travail; elles ne font pas partie de cet instantané historique.

### Conflits reproduits et résolution proposée

La fusion a été simulée uniquement contre le `main` actuel. Aucun résultat n’a été appliqué et aucun historique de branche n’a été réécrit.

| Branche | Fichiers en conflit | Cause observée et traitement prudent |
|---|---|---|
| `copilot/sec-004-remove-tout2026` (PR #167) | `backend/.env.example`, `backend/routes/composer.py`, `frontend/src/components/AdminGenerateReadings.js`, `frontend/src/pages/ComposerPage.jsx` | La PR cible encore l’ancien SHA de base `4d264ac0…`; `main` a depuis intégré #168 et plusieurs changements ultérieurs. Garder l’implémentation courante de Composer et ne reprendre que des éléments de bypass encore nécessaires, réconciliés et testés contre `main`. Le statut Vercel vert de la tête de PR ne supprime pas ces conflits. |
| `copilot/copilotsec-004-remove-tout2026` | `backend/.env.example`, `backend/routes/composer.py`, `backend/services/promo_bypass.py`, `backend/tests/test_promo_bypass_unit.py` (conflit add/add), `frontend/src/pages/ComposerPage.jsx` | Cette branche ajoute encore une restauration volumineuse et se heurte au routeur actuellement intégré. Ne pas fusionner son diff entier; examiner séparément toute validation de session utile sur la base actuelle. Aucun PR associé n’a été trouvé. |

Le code promo a déjà fait l’objet de #168 (`fix/sec-004-promo-composer`), puis #169 et #170. Ces deux branches ne doivent donc pas être qualifiées de cassées uniquement à cause de leur retard; elles sont simplement conflictuelles et non prêtes à intégrer.

## 2. CI, déploiement et couverture

### Smoke API Compatibility

Dans les dix dernières exécutions terminées sur `main` retournées pour ce workflow, huit sont réussies et deux échouent:

- Runs `38133161001` (`9b88679`) et `38133939196` (`7e3c06c`): les jobs quick et PDF s’arrêtent à l’import serveur avec `name 'Optional' is not defined`. Les logs montrent que les dépendances ont été installées; il s’agit donc d’une erreur de code, pas d’un secret ou service manquant.
- #168 a ensuite restauré `backend/routes/composer.py` avec `from __future__ import annotations` et `from typing import List, Optional`. Le run le plus récent sur le `main` actuel, `38150256698` (SHA `47d815c5…`), a ses deux jobs quick et PDF réussis.

Le workflow smoke couvre quelques routes de compatibilité et la génération de PDF locale/mokée; il ne vérifie pas un paiement Stripe réel, les courriels de livraison en production, l’ensemble des tests backend, ni le frontend.

### Cron du journal

Les dix derniers runs du workflow `Daily Journal Cron` consultés (runs 74 à 83) sont en échec. Dans les logs des runs `38049715257` et `38137640278`, `curl` reçoit HTTP 403 et la variable `CRON_SECRET` est vide dans le contexte Actions. Le code historique n’acceptait pas non plus l’en-tête Authorization envoyé par le workflow; #169 a ajouté cette prise en charge après le run #83. Aucun run postérieur à #169 n’était visible lors de l’audit.

**Action manuelle requise:** vérifier que le secret GitHub Actions `CRON_SECRET` est configuré et correspond à celui du backend, puis observer le prochain run planifié. Ne pas inscrire ni copier sa valeur dans le dépôt ou les logs. L’audit n’a pas consulté les logs Railway/Supabase et n’a pas déclenché cet endpoint.

## 3. Anomalies et correctifs

| Gravité | Fait vérifié | État |
|---|---|---|
| Moyenne — opérationnel | Le cron journal échoue avec HTTP 403; secret Actions vide sur les logs examinés. Le dernier run précède #169. | Non modifié: configuration secrète et production hors périmètre; vérifier manuellement après correction du secret. |
| Moyenne — build | `CI=true npm run build` échouait sur quatre avertissements `react-hooks/exhaustive-deps` dans `PdfFlipbook`, `ExperienceRoot`, `Blog` et `MonCompte`. | Corrigé: callback stabilisé dans le flipbook et dépendances manquantes déclarées dans les hooks. |
| Moyenne — tests | `npm test` ne pouvait pas charger la suite: utilitaires Testing Library absents; le Jest de CRA ne résolvait pas le point d’export CommonJS de React Router v7 et `TextEncoder` n’était pas disponible dans jsdom. | Corrigé: devDependencies contrôlées, setup Jest, mappings de test-only vers les entrées CommonJS. Les deux assertions anciennes de `NewHome.test.js` attendaient un rendu paresseux synchrone et vérifiaient les styles calculés; elles attendent désormais le composant et contrôlent ses styles inline réels. |
| Faible — configuration | `frontend/railway.toml` sélectionnait Node 18 tandis que `frontend/package.json` déclare `node >=20`. Cela établit une incohérence de config, pas que ce service Railway sert actuellement le site. | Corrigé à Node 20; test de non-régression ajouté. |
| Faible — build | Après correction, le build réussit mais signale un fichier source map absent dans `@mediapipe/tasks-vision` et un bundle principal compressé de 573,27 kB. | Avertissements non bloquants, préexistants aux correctifs fonctionnels; optimisation non entreprise. |
| Historique | Deux runs smoke échouaient auparavant sur `Optional` manquant. | Corrigé sur `main` par #168; run actuel réussi. |

Les journaux Jest contiennent aussi un avertissement React non bloquant sur l’attribut `jsx`; aucun test ne l’échoue. Aucune preuve locale ne justifie de signaler une régression actuelle auth/profil/checkout/promo/webhook/PDF. La couverture locale de ces zones reste limitée par l’indisponibilité des dépendances backend et l’absence de services de test configurés.

## 4. Vérifications exécutées

Depuis la racine du dépôt, sauf mention contraire:

| Commande | Résultat |
|---|---|
| `git rev-list --left-right --count origin/main...origin/<branche>` et `git log --cherry-pick` | Succès; comparaison des 11 branches autres que `main`, patch équivalent de `update-100` identifié. |
| `git merge-tree --write-tree origin/main origin/<branche>` | Succès sans conflit pour les branches intégrées/équivalentes; conflits reproduits sur les deux branches promo. |
| Scan des marqueurs `<<<<<<<` / `>>>>>>>` | Aucun marqueur de conflit accidentel trouvé. |
| `python -m compileall -q backend tests` | Réussi. |
| `python tests/smoke_api_compat.py --suite quick` local | Non exécuté jusqu’aux routes: arrêt à l’import faute de `fastapi` dans l’environnement. |
| `python -m pip install -r backend/requirements.txt` dans `/tmp` | Bloqué par l’échec DNS vers les index pip configurés; aucun test pytest backend n’a été déclaré réussi. |
| `cd frontend && npm ci --no-audit --no-fund` | Réussi depuis `frontend/`; le lockfile est reproductible. Plusieurs dépendances transitives émettent des avis de dépréciation. |
| `cd frontend && CI=true npm test -- --watchAll=false` | Réussi: 1 suite, 14 tests. |
| `cd frontend && CI=true npm run build` | Réussi avec les avertissements source map et taille du bundle décrits ci-dessus. |
| `python -m unittest tests.test_frontend_railway_runtime -v` | Réussi: 1 test. |
| `git diff --check` | Réussi. |

## 5. Limites et étapes manuelles

- Les comparaisons Git établissent ancestry, changements de patch et conflits de fusion, pas le fonctionnement de chaque branche; aucun build/test n’a été lancé sur les branches anciennes.
- Les dépendances backend n’ont pas pu être installées dans le sandbox, donc les tests backend locaux et l’import complet du serveur n’ont pas été reproduits. Le run CI actuel du smoke backend réussit néanmoins.
- Aucun paiement, webhook externe, email, endpoint de production, appel Railway/Supabase, déploiement ou rotation de secret n’a été effectué.
- Confirmer côté propriétaire la configuration du secret `CRON_SECRET` pour Actions et le service backend, puis vérifier le prochain run planifié. Vérifier séparément quel frontend (Vercel ou Railway) est réellement en service avant toute action de déploiement.
