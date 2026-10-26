# Nettoyage repo & RGPD — Procédure à exécuter en local

> Document créé le 2026-02-25 après l'audit externe du 25/10.
> **À exécuter en local sur ta machine, pas depuis Emergent.**
> Emergent n'a pas le droit de réécrire l'historique git ni de push-force
> (ça pète les forks, les PR en cours et les releases taguées).

## Pré-requis

```bash
# Clone propre du repo (ou utiliser ton clone existant)
git clone git@github.com:nadinezebdi-rgb/plume-astrale.git
cd plume-astrale

# Installer git-filter-repo (meilleur outil que BFG)
pip install git-filter-repo
# ou brew install git-filter-repo (mac)
```

## 1. Détacher les fichiers du tracking (sans supprimer du disque)

Déjà fait côté `.gitignore` dans ce lot. Il reste à retirer du tracking :

```bash
# Les 4 Go de cache + tmp_video + PDFs clients
git rm -r --cached backend/cache/ tmp_video/ 2>/dev/null || true
git rm --cached backend/assets/theme_natal/*.pdf 2>/dev/null || true
git rm --cached backend/assets/kabbale/*.pdf 2>/dev/null || true
git rm --cached backend/assets/pack_karmique/*.pdf 2>/dev/null || true

git commit -m "chore: untrack caches, tmp_video & client PDFs (RGPD + repo size)"
git push origin main
```

À ce stade le repo pèse encore 4 Go parce que les fichiers restent dans l'**historique**.
Les futurs clones seront déjà plus légers si tu fais `git clone --depth=1`.

## 2. Purger l'historique (DESTRUCTIF — à faire une seule fois, bien tester avant)

**Avant** : préviens tous les contributeurs qu'ils devront re-cloner. Bloque les PR
en cours. Fais un backup du repo (`git clone --mirror` ailleurs).

```bash
# Backup
git clone --mirror . ../plume-astrale.backup.git

# Purge des 4 Go d'historique — git-filter-repo
git filter-repo \
  --path backend/cache/ \
  --path tmp_video/ \
  --path-glob 'backend/assets/theme_natal/*.pdf' \
  --path-glob 'backend/assets/kabbale/*.pdf' \
  --path-glob 'backend/assets/pack_karmique/*.pdf' \
  --invert-paths

# Re-attache l'origin (filter-repo le retire par sécurité)
git remote add origin git@github.com:nadinezebdi-rgb/plume-astrale.git

# Force-push (SEUL cas où force-push est acceptable)
git push origin --force --all
git push origin --force --tags
```

Après ça le repo devrait peser **< 200 Mo**.

## 3. Migrer les PDFs vers Supabase Storage (étape dédiée, pas urgent)

Les PDFs servis via `/api/assets/pack_karmique/*.pdf` fonctionnent toujours
depuis le disque. Pour les migrer vers Supabase Storage :

1. Créer un bucket `client-pdfs` (private) sur Supabase.
2. Dans chaque service (`services/pack_karmique_service.py:191`,
   `services/kabbale_service.py:105`, `services/theme_natal_oneshot_service.py:265`) :
   remplacer l'écriture disque par `sb.storage.from_('client-pdfs').upload(...)`.
3. Dans l'endpoint `/api/assets/<dir>/{filename}` : rediriger 302 vers l'URL
   signée Supabase (`sb.storage.from_('client-pdfs').create_signed_url(..., 3600)`).
4. **Pas de breaking change** pour les liens déjà envoyés par email : l'URL
   publique reste la même, c'est juste la redirection qui change.

Cette étape est un sprint à part — compter 1-2 jours.

## 4. Décision Railway long-terme

Trois options :

| Option | Avantage | Inconvénient |
|---|---|---|
| **Pause Railway** (dashboard → Settings → Pause) | Backup gelé, redémarrable en 1 clic si Emergent tombe | Payes toujours le minimum ($5/mois) |
| **Supprime le projet Railway** | 0 € | Pas de backup instantané — doit redéployer from scratch si urgence |
| **Garde Railway actif avec kill-switch** | Backup chaud, 0 risque d'emails doublés (déjà en place) | Payes la facture normale même sans trafic |

**Recommandation : Pause Railway** pour les 2-3 prochains mois le temps de
valider que Emergent tient la charge, puis supprime si tout va bien.

## 5. PR Thème Natal

Dans le chat Emergent, barre d'écriture → bouton **« Save to GitHub »** →
sélectionner la branche `fix/natal-theme-coherence` → ouvrir la PR vers
`main` depuis GitHub.
