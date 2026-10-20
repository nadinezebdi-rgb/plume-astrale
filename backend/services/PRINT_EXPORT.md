# Livre natal : lecture et impression

Le paiement du PDF seul reçoit le même manuscrit enrichi que l'édition imprimée.
`theme_natal_oneshot_service` exige les interprétations de toutes les planètes
annoncées et les sections enrichies. Un échec de l'enrichissement est signalé,
sans PDF générique de remplacement. `BOOK_MODE_ENABLED` et `USE_V2_ENGINE`
ne peuvent plus réduire ce produit à une édition courte.

## Fichiers

- Lecture : couverture bleue nominative, verso, titre, préface, sommaire calculé,
  introduction, chapitres, conclusion. Format fini A5 (148 × 210 mm).
- Intérieur Lulu : les deux feuillets de couverture numérique sont retirés;
  mêmes textes et même pagination intérieure. Canevas 154,35 × 216,35 mm,
  soit fond perdu de 3,175 mm sur chaque bord. Marges de texte 17/21 mm
  alternées, minimum 20 mm en haut et 23 mm en bas. Polices TrueType incorporées.
- Couverture Lulu : un PDF séparé d'une page, arrière + dos + avant.
  Largeur/hauteur calculées par l'API Lulu avec le nombre réel de pages.
  Aucune largeur de dos estimée. Aucun texte sur le dos.

Le nombre de pages dépend du texte. Les exports sont testés avec des intérieurs
de 42 et de 150 pages. Aucun paragraphe n'est tronqué pour atteindre
une cible de 45–50 pages, et aucun remplissage artificiel n'est ajouté. Un verso
blanc final peut être ajouté pour rendre l'intérieur pair. Les moins de 32 pages
ne sont pas étiquetés comme un intérieur imprimable de ce produit.

## Configuration

L'enrichissement utilise `OPENAI_API_KEY` et éventuellement `NATAL_OPENAI_MODEL`.
Il n'exige pas le crédit IA Emergent. Les positions restent fournies par le
service astrologique; changer de fournisseur de prose ne répare pas une clé
astrologique rejetée.

Lulu exige `LULU_BASE_URL`, `LULU_POD_PACKAGE_ID`, `LULU_TOKEN_URL`,
`LULU_CLIENT_KEY`, `LULU_CLIENT_SECRET` et `LULU_MOCK=0` (valeur par défaut).
Le produit Lulu doit correspondre au format A5 et à la reliure commercialisée.

`LULU_COVER_TEMPLATE_JSON` contient les panneaux de couverture du **gabarit
Lulu correspondant à la reliure choisie**, en millimètres :

```json
{"width_mm": "largeur totale du gabarit", "height_mm": "hauteur totale du gabarit", "front_box_mm": ["x", "y", "largeur", "hauteur"], "back_box_mm": ["x", "y", "largeur", "hauteur"]}
```

Remplacer les chaînes par les nombres du gabarit. L'origine est le coin inférieur
gauche du PDF complet; panneaux avant/arrière hors replis et charnières.
Ne pas utiliser des coordonnées d'un broché pour une édition cartonnée.
Le panneau avant est décalé automatiquement si le nombre de pages change, selon
la variation exacte de largeur retournée par Lulu.
La couverture ne peut pas être envoyée à l'impression en l'absence du gabarit.
L'API de validation Lulu doit accepter l'intérieur et la couverture avant la
création du paiement puis d'une commande réelle. Le mode simulé ne confirme jamais une impression.

Les métadonnées de paiement distinguent `pdf_supabase_url` (lecture),
`pdf_lulu_interior_url`, `pdf_lulu_page_count`, `pdf_lulu_status`,
`pdf_design_version`. Une régénération admin avec `force=True` invalide les caches
de prose et fournit de nouvelles URLs versionnées. Les anciens PDF déjà envoyés
ne sont pas remplacés sans régénération.

## Vérification

```sh
PYTHONPATH=backend python -m pytest -q backend/tests/test_print_book_renderer.py backend/tests/test_lulu_preflight.py
```

Ces tests vérifient le texte long, l'ordre des sections, la séparation des
fichiers, les dimensions, les polices incorporées et l'utilisation du compte
réel de pages. Ils ne passent aucune commande ni paiement Lulu.

Référence : https://help.lulu.com/en/support/solutions/articles/64000255519-pdf-creation-settings
