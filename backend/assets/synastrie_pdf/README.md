# Illustrations du PDF Synastrie 25 pages

## Où déposer les images

Toutes les illustrations doivent être déposées dans **ce répertoire** :
```
/app/backend/assets/synastrie_pdf/
```

## Nomenclature des fichiers

Les images sont **automatiquement détectées** par numéro de page. Nommez-les ainsi :

| Page | Nom du fichier              | Thème                                     |
|------|-----------------------------|-------------------------------------------|
| 3    | `page-03.png` (ou .jpg)     | Portrait natal — Personne 1               |
| 4    | `page-04.png`               | Portrait natal — Personne 2               |
| 5    | `page-05.png`               | Soleils en miroir                         |
| 6    | `page-06.png`               | Lunes en miroir                           |
| 7    | `page-07.png`               | Mercure & Mercure (communication)         |
| 8    | `page-08.png`               | Vénus en miroir (langage d'amour)         |
| 9    | `page-09.png`               | Mars en miroir (désir, action)            |
| 10   | `page-10.png`               | Jupiter & Saturne (croissance)            |
| 11   | `page-11.png`               | Aspects harmonieux                        |
| 12   | `page-12.png`               | Aspects de tension                        |
| 13   | `page-13.png`               | Conjonctions notables                     |
| 14   | `page-14.png`               | Maisons croisées                          |
| 15   | `page-15.png`               | Langages d'amour (5 langages)             |
| 16   | `page-16.png`               | Sensualité (Mars + Vénus)                 |
| 17   | `page-17.png`               | Communication quotidienne                 |
| 18   | `page-18.png`               | Vie commune & projets                     |
| 19   | `page-19.png`               | Enfants & créativité                      |
| 20   | `page-20.png`               | Argent & valeurs partagées                |
| 21   | `page-21.png`               | Voyages & horizons                        |
| 22   | `page-22.png`               | Forces relationnelles                     |
| 23   | `page-23.png`               | Trois invitations concrètes               |
| 25   | `page-25.png`               | Bénédiction de la Plume                   |

> **Pages 1, 2, 24** n'ont pas d'illustration (couverture, sommaire, transits — design textuel).

## Formats acceptés
- **PNG**, **JPG**, **JPEG**, **WEBP**
- **Ratio recommandé** : 16:9 (paysage) — le slot du PDF mesure ~16cm × ~6-8cm selon les pages
- **Résolution minimum** : 1200 × 800 px (300 DPI pour un rendu net)
- **Style suggéré** : illustrations vectorielles, aquarelles, photos artistiques ou symboles astrologiques

## Comment ça marche

Le générateur de PDF cherche **automatiquement** une image au nom `page-XX.{png,jpg,jpeg,webp}` pour chaque page numérotée. Si l'image existe, elle est insérée dans le slot dédié (avec préservation du ratio). Sinon, un cadre doré pointillé "illustration · page XX" est affiché à la place (utile pour visualiser la mise en page avant d'avoir les images).

## Tester après ajout d'images

1. Déposez vos fichiers dans `/app/backend/assets/synastrie_pdf/`
2. Ouvrez `https://consultation-astro.preview.emergentagent.com/synastrie`
3. Cliquez sur **"✦ Aperçu gratuit du rapport (PDF)"** en bas de page
4. Le PDF s'ouvre dans un nouvel onglet avec vos illustrations intégrées

Aucun redéploiement nécessaire — les images sont lues à chaque génération.
