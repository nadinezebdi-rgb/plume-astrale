# Legacy PDF Migration — Roadmap v2 (Feb 2026)

Ce document scope la migration des générateurs PDF legacy (Kabbale,
Astrocartographie) vers le moteur `book_engine_v2` (Chromium + Jinja + CSS).

## Contexte

Aujourd'hui, `book_engine_v2` couvre uniquement le Thème Natal premium.
Les autres produits utilisent encore ReportLab :
- `services/kabbale_pdf.py` (627 lignes) → utilisé par 3 produits en prod
- `services/astrocartographie_pdf.py` (569 lignes) → utilisé par pdf_luxury_wrap

Migration = uniformiser tous les livres sur le look premium (ivoire,
Cormorant Garamond, Noto Sans Symbols 2, wheel SVG carré, etc.).

## Complexité estimée

| Bloc | Kabbale | Astrocarto |
|---|---|---|
| Réécrire templates HTML/CSS/Jinja | 4-5h | 3-4h |
| Adapter les données (Sephiroth, chemins, villes) | 2h | 2h |
| Intégrer aux 3 (resp. 1) endpoints consommateurs | 1-2h | 1h |
| Tests QA + validation visuelle | 2h | 1-2h |
| **Total** | **9-11h** | **7-9h** |

Migration complète : **16-20h de travail**.

## Ordre recommandé

**Phase 1 — Kabbale (prioritaire)** :
1. Créer `book_engine_v2/templates/_kabbale_body.html` (10 Sephiroth × 22 chemins)
2. Adapter `book_engine_v2/kabbale_wheel.py` pour le SVG de l'Arbre de Vie
3. Ajouter des prompts spécifiques à Kabbale dans `chapter_prompts.py`
4. Créer `kabbale_pipeline_v2.py` qui remplace `kabbale_pdf.py`
5. Migrer les 3 endpoints consommateurs :
   - `pack_karmique.py` (pack premium)
   - `mediumnite_pdf.py` (rapport médiumnité)
   - `pdf_luxury_wrap.py` (wrapper luxe)
6. Tests QA visuels (`pdf_qa.py` étoffé)
7. Feature flag `USE_V2_KABBALE=1` pour activer progressivement en prod
8. Suppression `services/kabbale_pdf.py` après 2 semaines sans régression

**Phase 2 — Astrocartographie** :
1. Créer `book_engine_v2/templates/_astrocarto_body.html`
2. Intégrer une carte du monde SVG (utiliser `natural-earth-vector` ou `d3-geo`)
3. Créer `astrocarto_pipeline_v2.py`
4. Migrer endpoint `pdf_luxury_wrap.py` (seul consommateur)
5. Tests + feature flag `USE_V2_ASTROCARTO=1`

**Phase 3 — Cleanup** :
1. Vérifier que book_engine_v2 est autonome (imports internes uniquement)
2. Migrer `book_engine_v2/renderer.py` pour ne plus dépendre de `book_engine/domain.py`
3. Supprimer `services/book_engine/` (v1) — dernier reliquat de ReportLab

## Risques identifiés

**Élevé** :
- Régression sur pack karmique (produit à 199€ — impact revenus direct)
- Régression sur rapport médiumnité (utilise kabbale_pdf pour Sephiroth)
- Bugs de mise en page sur la carte du monde astrocarto (SVG complexe)

**Moyen** :
- Perte de fidélité visuelle si les templates Jinja ne matchent pas
  exactement le rendu ReportLab
- Cases edge non couverts par les tests actuels

**Faible** :
- Performance : Chromium est plus lent que ReportLab (+3-5s par PDF)

## Plan de mitigation

1. **Feature flags** : chaque produit migré est protégé par `USE_V2_<PRODUCT>`.
   Défaut = 0 (v1 legacy) → activation progressive en prod après validation.
2. **Suite de tests régression** : capture les 5 PDF v1 comme référence,
   compare pixel-diff avec les v2 correspondants (SSIM ≥ 0.85).
3. **Rollback rapide** : revenir sur v1 = flipper le flag, pas de rebuild.
4. **Monitoring** : logs structurés sur `pdf_engine_version` dans chaque
   webhook pour détecter les régressions par comparaison A/B.

## Estimation coût

- Développeur senior à 500€/j : **2 000-2 500€** pour les 16-20h de travail
- Ou 1 semaine de dev consacrée à cette migration exclusivement

## Ce qu'il faut décider AVANT de lancer

1. **Ordre** : Kabbale d'abord ou Astrocarto d'abord ?
   → Recommandation : Kabbale (utilisé par 3 produits, ROI plus grand).
2. **Feature flag ou switch total** ?
   → Recommandation : feature flag pour rollback rapide.
3. **Fenêtre calendrier** : quand a-t-on 1 semaine sans autre priorité ?
   → À bloquer sur calendrier avant démarrage.
4. **Fidélité visuelle** : match pixel-perfect avec v1, ou refonte assumée ?
   → Recommandation : refonte assumée (livre v2 = nouveau look premium).

## Prochaine étape suggérée

Ouvrir un ticket dédié « Migration Kabbale v2 » avec ce roadmap en pièce
jointe. Bloquer 5 jours dans le calendrier. Créer une branche Git
`feature/kabbale-v2`. Suivre l'ordre Phase 1 → tests → feature flag.

**Fichier créé : Feb 2026 pour préparer une itération dédiée future.**
