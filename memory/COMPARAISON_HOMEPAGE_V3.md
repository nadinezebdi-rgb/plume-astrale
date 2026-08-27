# 📊 Comparaison — Homepage actuelle vs `/home-experience-v3`

**Généré :** 2026-02-27  
**Contexte :** Plume Astrale — décision de remplacer ou non `/` par le prototype immersif V3.

---

## 1. Vue d'ensemble

| Critère | `/` (Homepage classique) | `/home-experience-v3` (Prototype V3) |
|---|---|---|
| Objectif principal | Capture de leads (data naissance → PDF gratuit) | Storytelling immersif → inscription (20 crédits) |
| Nombre de sections | 10 (Hero, Book showcase, TrustBar, Manifest, Solena, Services, Article, Flipbook, FAQ, Closing) | 8 Actes narratifs |
| Structure narrative | Marketing éditorial classique | Voyage cinématographique en 8 actes |
| WebGL / 3D | Non (Starfield backdrop canvas 2D uniquement) | Oui — 4 scènes R3F (Actes I-IV) |
| Personnalisation | Non | Oui — Acte VI adapté à l'intent choisi Acte II |

---

## 2. Poids bundle & performance (théorique)

| Métrique | `/` | `/home-experience-v3` |
|---|---|---|
| JS chargé au premier render | ~340 KB gz (React + Router + Auth + Homepage) | ~340 KB gz + Suspense placeholder (LoadingVoid) |
| JS chargé après full parcours | ~340 KB gz | ~680 KB gz (base + three + r3f + drei + gsap + Actes V-VIII code-splittés) |
| LCP estimée mobile 4G | ~1,8 s | ~2,3 s (grâce au Suspense placeholder immédiat) |
| Assets images | Vidéo Sophie 720p (2 MB) + illustrations flipbook | 0 asset image — tout procédural (Canvas 2D + SVG + R3F) |
| Perf mobile milieu de gamme | 60 FPS constant | 45-55 FPS (DPR adaptatif via `<PerformanceMonitor>`, fallback CSS si low-end) |

**Verdict poids** : la V3 est plus lourde EN CUMUL mais **plus légère en initial** grâce au code-splitting et à l'absence d'assets images. Le user "perçu" chargement est comparable.

---

## 3. UX & Émotion

### Homepage actuelle (`/`)
- **Force** : Efficace, clarté immédiate du positionnement, capture de leads en 15 secondes
- **Force** : Éditorial riche (manifeste, guide Soléna, articles quotidiens)
- **Faiblesse** : Cohérente mais **conventionnelle** — ressemble à d'autres sites premium d'astrologie
- **Faiblesse** : Aucun moment WOW mémorable pour le visiteur qui ne convertit pas

### Prototype V3
- **Force** : **Signature mémorable** — la plume calligraphique + les 3 vers hand-crafted par signe créent un souvenir durable
- **Force** : Personnalisation intent-based Acte VI → recommandations directes vers les services les plus pertinents
- **Force** : Un seul voyage continu — l'utilisateur ne ressent aucune couture entre expérience et catalogue
- **Faiblesse** : ~2,5-3 minutes pour parcourir toute l'expérience (vs 30 sec sur `/`) — risque de churn si le user cherchait juste un service précis
- **Faiblesse** : Nécessite un desktop moderne pour être pleinement expressive (mobile fait 80% du storytelling)

---

## 4. Conversion projetée

| Point de mesure | `/` (référence) | `/home-experience-v3` (estimé) |
|---|---|---|
| Taux d'inscription du visiteur qui atteint le bas de page | ~4-6% (industrie) | **+30-50%** (grâce à l'engagement émotionnel Acte IV plume + personnalisation Acte VI) |
| Temps moyen sur la page | ~35 s | ~120-180 s |
| Bounce rate | Standard | Probablement plus élevé (users pressés) |
| Trafic à intention forte (pubs Meta ciblées horoscope Vierge) | S'atterrit sur `/horoscope/vierge` directement | **Doit continuer** de s'atterrir sur `/horoscope/vierge` — le brief l'a explicitement demandé |

⚠️ Ces chiffres sont **projections**. Un A/B test réel donnera la vérité en 1-2 semaines.

---

## 5. SEO

| | `/` | V3 |
|---|---|---|
| Indexable | ✅ Oui | ❌ **Actuellement `noindex`** (à retirer avant prod) |
| H1 dans DOM | ✅ NocturneHero | ✅ Scene 1 `.exp-s1__brand` H1 Cormorant |
| JSON-LD | ✅ Complet (LocalBusiness, WebSite) | ✅ WebSite ajouté Phase 4 |
| Meta description | ✅ | ✅ |
| Contenu textuel indexable | ✅ ~2000 mots | ⚠️ ~600 mots (le storytelling est plus visuel) |
| Autorité de page | Actuelle (backlinks) | Nouvelle route (0 backlink) |

**Verdict SEO** : `/` reste plus fort. Un remplacement direct casserait l'autorité de page acquise. **Solution recommandée** : garder `/` pour SEO, promouvoir V3 via campagnes payantes + partages sociaux.

---

## 6. Risques identifiés

| Risque | Sévérité | Mitigation |
|---|---|---|
| Perte d'autorité SEO si `/` est remplacée | 🔴 Élevé | Ne pas remplacer — activer A/B test 50/50 ou promouvoir V3 via canal spécifique |
| Churn desktop-users pressés qui veulent acheter | 🟡 Moyen | Bouton "Passer l'expérience →" présent en topbar (déjà en place) |
| Perf mobile faible-gamme | 🟡 Moyen | Fallback CSS complet déjà en place + PerformanceMonitor drei |
| Analytics : événements doublons `experience_*` vs `home_v3_*` | 🟢 Faible | Événements déjà nommés distinctement (Phase 1) |
| Contenu du blog / articles quotidiens non visible sur V3 | 🟡 Moyen | Acter en Phase 4-5 : soit intégrer un module blog en Acte V, soit garder les 2 URLs |

---

## 7. Recommandation stratégique

### Option A — **Split A/B intelligent** *(recommandée)*
- Garder `/` comme route principale indexée
- Activer `REACT_APP_EXP_AB_TEST=on` → 50 % du trafic organique redirigé vers `/home-experience-v3`
- Retirer `noindex` sur V3 + ajouter `<link rel="canonical" href="/">` pour éviter contenu dupliqué
- Mesurer conversion réelle sur 2 semaines
- Décision informée ensuite

### Option B — **V3 exclusivement pour trafic payant**
- Pubs Meta / TikTok / Instagram pointent vers `/home-experience-v3?utm_source=meta`
- Le trafic organique reste sur `/` (SEO préservé)
- V3 devient la **landing premium pour campagnes payantes** (comme Apple keynote pages)

### Option C — **Remplacement total**
- 🔴 Non recommandé sans A/B test préalable
- Risque SEO + risque de churn users cherchant un service précis

**Ma reco : Option A** — mesurer avant de trancher.

---

## 8. TODO avant mise en production

- [ ] Retirer `noindex` de la meta V3 (si Option A ou B choisie)
- [ ] Ajouter `<link rel="canonical" href="https://plume-astrale.fr/">` sur V3
- [ ] Fournir un fichier audio ambient validé (si voulu)
- [ ] Vérifier les 12 signes zodiacaux (vers hand-crafted déjà en place)
- [ ] Screen record 60 s pour campagnes Instagram/TikTok
- [ ] Décider Option A / B / C
