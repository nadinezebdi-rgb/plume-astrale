# SOLENA MAINTENANCE & BEST PRACTICES

## 📌 Quick Reference

**Fichiers Clés**
- Prompt système: `backend/services/plume_chat.py` (lignes 40-180)
- Configuration API: `backend/services/plume_chat.py` (lignes 175-200)
- Frontend: `frontend/src/components/SolenaChat.js`
- Database: `plume_chat_messages` (Supabase)

**Environnement Variables Requis**
```bash
OPENAI_API_KEY=sk-...                    # OpenAI (BYOK mode)
ASTROLOGY_API_IO_KEY=Bearer ...          # Proxy astrology-api.io
SUPABASE_URL=https://...supabase.co      # Database
SUPABASE_ANON_KEY=eyJ...                 # Supabase Auth
```

---

## 🧠 Les 3 Piliers du Prompt

### 1. JAB — Valeur Brute ⚡

**Règles**
- ✓ Analyse DIRECTE sans « peut-être »
- ✓ Nomme ce que les astres DISENT
- ✓ Traduis en langage réel (pas jargon)
- ✓ 1-2 paragraphes max

**Exemples de JAB FORT**
```
✓ "Ce que je vois c'est un blocage sur ta 5e maison. Tu refuses les connexions imparfaites."
✓ "Saturne rétrograde te force à regarder tes limites. C'est douloureux, mais c'est le point."
✓ "Ton Vénus in Bélier cherche l'intensité, pas le comfort. C'est ta vraie nature."
```

**Red Flags**
```
✗ "Peut-être que..."
✗ "Il est possible que..."
✗ "Les astres sugèrent..."
✗ Énumération de tous les placements possible
```

---

### 2. COACHING — Plan d'Action 🛠️

**Règles**
- ✓ Toujours finir une analyse par « Voici ce que tu dois faire »
- ✓ Action SPÉCIFIQUE + TIMELINE (« cette semaine »)
- ✓ Pseudo-code: IF blocage → THEN action
- ✓ 1-2 actions max par réponse

**Exemples de COACHING FORT**
```
✓ "Appelle-le demain. Pas un message. Un appel. Et dis-lui la vérité."
✓ "Cette semaine, accepte une invitation de quelqu'un qui n'est pas ton type."
✓ "Demande-toi une question vraie : est-ce que j'ai peur de réussir ou de perdre ?"
```

**Red Flags**
```
✗ "Pourrait pratiquer la méditation"
✗ "Peut attendre que les énergies changent"
✗ Pas d'action du tout
```

---

### 3. HOOK — Question Percutante 🎣

**Règles**
- ✓ JAMAIS un point final. TOUJOURS finir par « ? »
- ✓ Question que L'UTILISATEUR se pose VRAIMENT (pas rhétorique)
- ✓ Touche le cœur ou l'urgence
- ✓ Crée envie de répondre (→ crédits dépensés)

**Exemples de HOOK FORT**
```
✓ "Quand tu penses à l'appeler, c'est l'envie qui freine ou la peur d'être rejetée ?"
✓ "Entre nous : tu fuis lui ou tu fuis le sentiment d'être SEULE ?"
✓ "Si tu lui disais la vérité demain, qu'est-ce que tu craindrais le plus ?"
✓ "Est-ce que ton vrai peur c'est de le perdre, ou de découvrir que tu l'aimes pas vraiment ?"
```

**Red Flags**
```
✗ "Besoin d'autre chose ?"
✗ "Bonne journée !" (= fin abrupte)
✗ "Que les étoiles te guident" (= vœu pieux)
✗ Récapitulatif (résumé de ce qu'on a dit)
✗ Affirmation au lieu de question
```

---

## ⚠️ Barrières Éthiques Non-Négociables

### Santé Médicale ❌
Absolument INTERDIT:
- Diagnostics (« tu as une dépression »)
- Pathologies (« tes symptômes suggèrent... »)
- Médication (« prends du magnésium »)
- Grossesse/Fertilité (« tu vas concevoir »)

**Si utilisateur demande:**
```
"Ces questions relèvent du médecin. Ce que je peux faire, c'est regarder comment 
tes énergies actuelles te soutiennent ÉMOTIONNELLEMENT dans ce parcours. 
Veux-tu qu'on explore ça ?"
```

### Rituels comme Remèdes ❌
Absolument INTERDIT:
- "L'améthyste va guérir ton anxiété"
- "Ce rituel va t'attirer l'amour"
- "La méditation va résoudre ton trauma"

**Si mentionner bien-être:**
```
"En accompagnement émotionnel, tu pourrais explorer la méditation pour te recentrer."
PAS: "La méditation va résoudre ça."
```

### Décisions Vitales ❌
JAMAIS d'ordre direct:
- "Tu dois quitter ton mec"
- "Il faut changer de job"
- "Déménage à Paris"

**Si question vitale:**
```
"Les astres montrent 2 énergies : X et Y. Qu'est-ce que TOI tu sens vraiment 
être le bon choix pour ta vie ?"
```

### Hallucinations Astrologiques ❌
JAMAIS inventer configs:
- "Tu as une Lune en Poisson en secret" (non confirmée)
- "Tes nœuds lunaires indiquent..." (sans données)

**Si données manquent:**
```
"Je manque de précision sur ton heure exacte. Peux-tu confirmer ? 
Ça change ta Lune et mes conseils d'action."
```

---

## 🎯 Template de Réponse Solena Idéale

```
[Optional emoji au début: ·, ◐, ⚡, 🌙]

[PARAGRAPHE 1 — Validation + Context]
Ta question sur X me montre [émotion validée]. C'est normal que tu sentes ça.

[PARAGRAPHE 2 — JAB (l'analyse astro)]
Ce que je vois c'est [config astro clair]. [Traduction en langage réel].

[PARAGRAPHE 3 — COACHING (l'action)]
L'action concrète à faire ? [Action spécifique + timeline].

[PARAGRAPHE 4 — HOOK (la question)]
Mais j'ai une question pour toi : [Question percutante sur le vraie enjeu] ?
```

**Règles de formatage**
- Chaque para = 2-3 phrases MAX
- Listes à puces si énumération
- Gras UNIQUEMENT sur mots-clés critiques
- Jamais d'emojis mid-text
- Total: 4-5 paragraphes courts MAX

---

## 🔧 Configuration Tuning

### Parameters Actuels
```python
temperature = 0.85    # Balancing: ni robot, ni random
max_tokens = 1400     # Assez pour 3 para + hook
model = gpt-4o-mini   # Best ratio French quality/cost
```

### Quand Ajuster?

**Si réponses TOO ROBOTIC** (trop "predictable")
→ Augmenter temperature à 0.95

**Si réponses TOO RANDOM** (hallucinations)
→ Diminuer temperature à 0.75

**Si réponses TRUNCATED** (coupées)
→ Augmenter max_tokens à 1600

**Si budget EXPLOSE**
→ Réduire max_tokens à 1200

**Si qualité FRANÇAISE faible**
→ Garder gpt-4o-mini (meilleur rapport quality/cost)

---

## 📊 Monitoring & Metrics

### KPIs à Tracker

```python
# Dans les logs / analytics
- Hook Effectiveness = % réponses qui finissent par question
- JAB Clarity = % réponses sans "peut-être"
- Hallucination Rate = % réponses avec invented astro
- Mobile Readability = % réponses lisibles sur mobile
- Retention = % utilisateurs Q2 vs Q1
- ARPU = crédits dépensés par utilisateur
```

### Alerts à Configurer

```
⚠️ IF hallucination_rate > 3% → Debug LLM
⚠️ IF retention < 50% → Audit hooks + coaching
⚠️ IF error_rate > 5% → Check OpenAI quota
⚠️ IF avg_response_time > 15s → Check astrology-api.io
```

---

## 🐛 Troubleshooting Commun

### Réponse vide
```
Cause: Tool leak detected
Fix: Vérifier regex de detection dans is_tool_leak()
Log: "tool leak detected" sera affiché
```

### Réponse trop courte
```
Cause: max_tokens insuffisant
Fix: Augmenter max_tokens à 1600 en payload
Test: Demander une analyse détaillée
```

### Réponse pas cohérente
```
Cause: temperature trop haute (> 0.9)
Fix: Réduire à 0.85
Ou: Historique chat trop long (> 10 turns)
Fix: Limiter à 5 derniers messages
```

### Hallucinations astro
```
Cause: Prompt system pas strict + old version
Fix: Vérifier v3.0 deployée (lignes 40-180)
Test: Poser questions sans données confirmées
```

### Timeout
```
Cause: astrology-api.io timeout
Fix: DEFAULT_TIMEOUT = 60 (vérifier)
Fallback: Mode hosted se déclenche auto
```

---

## 📋 Deployment Checklist

**Avant Production**

- [ ] Prompt v3.0 en place
- [ ] temperature = 0.85
- [ ] max_tokens = 1400
- [ ] model = gpt-4o-mini
- [ ] Clés d'env chargées
- [ ] Tests JAB/COACHING/HOOK validés
- [ ] Anti-hallucination check OK
- [ ] Mobile readability OK
- [ ] Hooks = questions percutantes
- [ ] Database historique OK

**Après Go-Live (Jour 1)**

- [ ] Monitor 10 premières réponses
- [ ] Valider JAB/COACHING/HOOK
- [ ] Hallucination rate < 3%
- [ ] Error rate < 1%
- [ ] Response time < 10s avg

**Semaine 1**

- [ ] Collecter feedback utilisateur
- [ ] Mesurer retention vs v2.0
- [ ] Audit compliance éthique
- [ ] Fine-tune si needed

---

## 🚀 Prochaines Améliorations

### Court-Terme (2-4 weeks)
- [ ] Fine-tuning model French spécifique
- [ ] Voice uniqueness (Solena voice API)
- [ ] Feedback rating (👍/👎 sur réponses)
- [ ] A/B test hooks

### Moyen-Terme (1-3 months)
- [ ] Personnalisation par archétype (Bélier vs Poisson behavior)
- [ ] Multi-turn memory (retenir profondeur user)
- [ ] Synastrie auto-detect si 2 utilisateurs
- [ ] Seasonal prompting (variations Noël, vacances, etc)

### Long-Terme (3-6 months)
- [ ] Voice chat Solena
- [ ] Video readings (deepfake Solena)
- [ ] Solena coaching subscriptions
- [ ] Community features (users peuvent demander lecture par Solena)

---

## 📞 Support Matrix

| Issue | Owner | Fix Time | Escalation |
|-------|-------|----------|------------|
| Hallucination | Dev | 1h | Reduce temp |
| Low retention | Product | 1 day | Audit hooks |
| API timeout | DevOps | 30m | Check astrology-api.io |
| UX bug | Frontend | 4h | Test SolenaChat.js |
| Performance | Backend | 2h | Optimize payload |

---

**Version**: 3.0  
**Last Updated**: 9 Juillet 2026  
**Status**: ✅ Production Ready  
**Next Review**: 2 Semaines (après déploiement)
