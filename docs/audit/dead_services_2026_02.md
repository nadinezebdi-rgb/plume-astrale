# Audit code mort — 2026-02-25

> Scan automatique des `backend/services/*.py` jamais importés dans le reste du code.
> Pas de référence par `from services.X`, `import services.X`, ou chaîne littérale.

## 11 services candidats à la suppression

| Service | Taille | Statut |
|---|---|---|
| `astro_content.py` | — | Jamais importé |
| `astrocartographie_ai.py` | — | Jamais importé |
| `fenetre_rencontre_pdf_v2.py` | — | Jamais importé (v1 utilisée) |
| `library_images.py` | — | Jamais importé |
| `natal_chart_extract.py` | — | Jamais importé |
| `openai_enrichment_service.py` | — | Jamais importé |
| `pdf_book_intro.py` | — | Jamais importé |
| `pdf_generator.py` | — | Jamais importé (v2/v3 utilisés) |
| `premium_subscription.py` | — | Jamais importé |
| `public_free_promo.py` | — | Fausse référence (clé JSON de réponse) |
| `signup_promo.py` | — | Jamais importé |

## Procédure recommandée

**Ne pas supprimer en masse** — vérifier manuellement chaque fichier pour :

1. **Appels dynamiques** (`importlib.import_module`, `__import__`) qui échappent au grep statique.
2. **Routes commentées** qui pourraient être réactivées.
3. **Code backup** laissé volontairement pour rollback rapide.

### Workflow conseillé

```bash
# Déplacer d'abord dans services/_candidates_deletion/ au lieu de rm direct
mkdir -p backend/services/_candidates_deletion
for s in astro_content astrocartographie_ai fenetre_rencontre_pdf_v2 \
         library_images natal_chart_extract openai_enrichment_service \
         pdf_book_intro pdf_generator premium_subscription \
         public_free_promo signup_promo; do
  git mv backend/services/$s.py backend/services/_candidates_deletion/
done

git commit -m "chore: quarantine 11 unused services for review (audit 2026-02)"
```

Tourner la prod 2 semaines → si zéro erreur au log → `rm -rf backend/services/_candidates_deletion/`.

## Mes notes rapides

- `pdf_generator.py` est l'original — les versions actives sont dans `backend/pdf_generator_v2.py` et `v3`. Le vrai `services/pdf_generator.py` n'est référencé nulle part.
- `premium_subscription.py` : probablement un reliquat d'un ancien modèle d'abonnement.
- `signup_promo.py` + `public_free_promo.py` : logique promo simplifiée dans `promo_bootstrap.py` + `routes/admin_promo.py`.
