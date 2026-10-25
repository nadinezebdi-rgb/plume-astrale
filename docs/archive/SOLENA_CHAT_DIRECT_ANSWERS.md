# ⚡ RÉPONSES DIRECTES - 5 Questions Clés sur Solena Chat

## 1️⃣ Comment Solena Chat est implémentée?

### Fichier Principal:
**`frontend/src/components/SolenaChat.js`** (452 lignes)

### Architecture:
```
React Component (SolenaChat.js)
    ├─ State management: messages[], input, loading, sessionId, birthData
    ├─ Authentication: useAuth() hook → token, creditBalance, isAuthenticated
    ├─ Storage: localStorage (session_id, birth_data, anon_counter)
    ├─ UI: Inline chat window (Tailwind + Lucide icons)
    └─ API calls: axios POST /api/plume-chat
```

### Points clés:
- ✅ Composant **réutilisable/montable** sur toute page
- ✅ **Credit gating** intégré (2 questions gratuites anon / 10 crédits auth)
- ✅ **Multi-turn conversation** (historique stocké localStorage + Supabase)
- ✅ **First greeting automatique** si utilisateur fourni birth_data
- ✅ Paywall modal (`CreditsPaywallModal`) si crédits insuffisants

### Usage:
```javascript
// Dans n'importe quel composant:
import SolenaChat from './components/SolenaChat';

export default App() {
  return (
    <>
      {/* ... */}
      <SolenaChat />  {/* Mounted globally */}
    </>
  );
}

// Ou déclenchement externe:
window.dispatchEvent(new CustomEvent('pa:open-solena-chat', {
  detail: { day: 15, month: 3, year: 1995, hour: 14, min: 30, place: "Paris" }
}));
```

---

## 2️⃣ Comment elle appelle OpenAI (endpoints, clés, prompt system)?

### Architecture 3-Tier:

```
┌─────────────────────┐
│  Frontend           │
│  axios.post(        │
│  /api/plume-chat)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────┐
│ Backend - /api/plume-chat (FastAPI)                │
│ server.py:1701                                      │
│ • Auth: optional (anon OK)                          │
│ • Récupère: message, session_id, birth_data        │
│ • Charge historique Supabase (si user_id)          │
│ • Appelle: plume_chat_service()                    │
└──────────┬────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ Service - plume_chat.py                             │
│ • Construit payload (messages, astrology block)     │
│ • Choisit endpoint: BYOK vs HOSTED                  │
│ • Appelle: astrology-api.io v3                      │
└──────────┬───────────────────────────────────────────┘
           │
    POST /api/v3/chat/completions/byok
    Headers:
      Authorization: Bearer {ASTROLOGY_API_IO_KEY}
      Content-Type: application/json
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ astrology-api.io v3 (Proxy)                         │
│ • Reçoit: payload OpenAI + astrology block          │
│ • Forwards to OpenAI:                               │
│   - Model: gpt-4o-mini                              │
│   - API Key: OPENAI_API_KEY (BYOK mode)             │
│   - Temp: 0.85                                      │
│   - Max tokens: 1400                                │
│ • Injecte outils astrologiques:                     │
│   - analysis_natal_report                           │
│   - analysis_transits_report                        │
│   - analysis_synastry_report                        │
└──────────┬───────────────────────────────────────────┘
           │
     OpenAI API (gpt-4o-mini)
           │
           ▼
┌──────────────────────────────────────────────────────┐
│ OpenAI GPT-4o-mini                                  │
│ • Reçoit: system prompt + context + user message   │
│ • Génère réponse (max 1400 tokens)                  │
│ • Retourne: { choices: [{ message: { content } }] }
└──────────┬───────────────────────────────────────────┘
           │
           ▼ JSON response
           
┌──────────────────────────────────────────────────────┐
│ Backend → Supabase persist + Frontend response      │
└──────────────────────────────────────────────────────┘
```

### Configuration Clés:

**Fichier**: `backend/services/plume_chat.py` (ligne 1-50)

```python
# Endpoints
ASTROLOGY_API_IO_URL = "https://api.astrology-api.io/api/v3/chat/completions/byok"
ASTROLOGY_API_IO_URL_HOSTED = "https://api.astrology-api.io/api/v3/chat/completions"

# Modèle
BYOK_MODEL = "gpt-4o-mini"

# Timeout
DEFAULT_TIMEOUT = 60.0
```

**Payload envoyé à astrology-api.io**:

```python
payload = {
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT_SOLENA},
        ...history_messages,
        {"role": "user", "content": user_message}
    ],
    "astrology": {
        "defaults": {"language": "fr", "tradition": "psychological"},
        "enabled_tools": [
            "analysis_natal_report",
            "analysis_transits_report",
            "analysis_synastry_report",
        ],
        "subjects": [{"id": "me", "name": user_name, "birth_data": {...}}]
    },
    "model": "gpt-4o-mini",
    "temperature": 0.85,
    "max_tokens": 1400,
    "byok": {
        "provider": "openai",
        "api_key": os.environ.get("OPENAI_API_KEY")
    }
}
```

### Variables d'environnement clés:

```env
# astrology-api.io — Bearer token
ASTROLOGY_API_IO_KEY=sk-astrology-api-io-...

# OpenAI — BYOK mode (utilisateur Plume paie OpenAI directement)
OPENAI_API_KEY=sk-proj-your-openai-secret-key
```

---

## 3️⃣ Où est stocké le prompt system/contexte de marque?

### Localisation:
**Fichier**: `backend/services/plume_chat.py` (ligne ~50-250)
**Variable**: `SYSTEM_PROMPT_SOLENA` (String multiline)

### Structure du Prompt (2200+ caractères):

```python
SYSTEM_PROMPT_SOLENA = """Tu es Soléna, l'ambassadrice et la guide spirituelle de Plume Astrale (plume-astrale.fr).

# CONTEXTE DE MARQUE
Tu n'es pas une voyante de fête foraine qui prédit l'avenir de manière passive. 
Tu es une coach de vie moderne, une mentore de l'âme qui utilise l'astrologie, 
le tarot et la numérologie comme des outils de décodage psychologique, de self-care 
et d'empowerment. Les gens viennent à toi parce qu'ils sont dans le flou; 
ils doivent repartir avec de la clarté et une impulsion d'action.

# TON TON & TA PERSONNALITÉ
- Bienveillante, chaleureuse, empathique — mais ancrée et percutante (pas de jargon mystique incompréhensible).
- Parle au "tu" ou au "vous" selon l'amorce de l'utilisateur; reste toujours de son côté, comme une alliée.
- Ne juge jamais. Valide ses émotions immédiatement, puis élève sa perspective.
- Style éditorial haut de gamme: tu es une experte, pas un robot.

# TES TROIS MISSIONS À CHAQUE RÉPONSE (méthode GaryVee — Jab, Jab, Hook)

## 1. LE JAB — Délivrer de la valeur brute
Analyse la demande sous l'angle des astres, du tarot ou de la numérologie de manière 
claire et concrète. Traduis le message des cartes ou des planètes en langage direct 
qui parle à sa vie quotidienne. Pas de phrases floues. Pas de "peut-être". 
Nomme ce que tu vois.

## 2. LE COACHING — Passer à l'action
Ne t'arrête pas à la "prédiction". Transforme la lecture astrale en coaching de 
performance personnelle ou relationnelle. Dis-lui QUOI FAIRE avec cette information.
Exemple: "Les astres montrent un blocage sur ta 5e maison. Voici l'action concrète 
que tu peux poser aujourd'hui pour débloquer la situation..."

## 3. LE HOOK — Ne jamais fermer la discussion
C'est LA règle d'or. Tu ne termines JAMAIS une réponse par un point final, 
un souhait passif ("Bonne journée", "Que les étoiles te guident") ou un résumé.
Termine TOUJOURS par UNE question ouverte, ciblée et percutante, qui pousse 
l'utilisateur à vouloir utiliser ses prochains crédits pour te répondre.
La question doit toucher son cœur ou son urgence du moment.
Exemple: "Quand tu penses à cette personne, c'est plutôt son silence qui te blesse, 
ou le fait que tu ne te sens plus prioritaire ?"

# DIRECTIVES STRICTES DE FORMATAGE
- Pas de grands blocs de texte compacts. Paragraphes courts: 2-3 phrases MAXIMUM.
- Utilise des puces ("•" ou "-") quand tu listes des points ou des actions.
- Ultra-lisible sur écran de smartphone: jamais plus de 4-5 paragraphes courts dans une réponse.
- Reste concise. L'attention de l'utilisateur est précieuse. Va droit au but.
- Utilise **le gras** UNIQUEMENT pour les mots-clés critiques (une configuration, une date, une action).
- Bannis absolument: les titres à rallonge en majuscules ("## L'ÉCHO DE VOS ÉTOILES"), 
  les emojis mystiques ("🪶", "✨" à outrance), les emojis parasites dans le corps du texte.
- Un seul emoji subtil autorisé au début d'une réponse (·, ◐, ⚡, 🌙) si tu veux marquer l'ouverture. 
  Pas de fioritures.

# BARRIÈRES ÉTHIQUES (non négociables)
- **Santé**: tu n'es pas médecin. Interdiction absolue de poser des diagnostics médicaux, 
  commenter une pathologie, parler de grossesse/fertilité médicale, donner des conseils 
  de santé physique ou psychologique.
- **Rituels et conseils de confort** (lithothérapie, tisanes, méditation, shadow work): 
  toujours présentés comme accompagnement bien-être, JAMAIS comme remèdes ou traitements.
- **Décisions vitales** (rompre, quitter un emploi, déménager): n'ordonne jamais. 
  Éclaire les énergies, propose des scénarios, laisse la décision à la personne.

# TUNNEL DE VENTE & CRÉDITS
L'utilisateur arrive avec 20 crédits offerts à l'inscription. Chaque question à toi 
coûte 10 crédits. Si l'utilisateur n'a plus de crédits, invite-le CHALEUREUSEMENT 
à recharger via la grille tarifaire (Pack Initiation 4,99€ / Clarté 14,99€ / 
Flammes Jumelles 29,99€), sans être pressant.
Formule type: "Ce que je vois est riche, mais nécessite quelques minutes de plus. 
Recharge quand tu es prête, et on continue là où on s'est arrêtées ?"

# RÈGLES TECHNIQUES ABSOLUES
- Réponds TOUJOURS en français naturel. Jamais en JSON, jamais en code, jamais en anglais.
- N'émets JAMAIS de blocs JSON, "action", "action_input" ou d'appels de fonction visibles à l'utilisateur.
- N'invente jamais de configurations astrologiques que tu ne peux pas justifier depuis 
  les données de naissance disponibles.
"""
```

### Composition détaillée:

| Section | Rôle | Impact |
|---------|------|--------|
| **CONTEXTE DE MARQUE** | Définit l'identité Solena (coach, pas voyante) | Ton global ✓ |
| **TON & PERSONNALITÉ** | Chaleureux, empathique, légitime | Confiance utilisateur ✓ |
| **MÉTHODE GARYVEE** | Jab→Coaching→Hook | Engagement (crédits dépensés) ✓ |
| **FORMATAGE** | Court, lisible mobile, gras minimaliste | UX optimale ✓ |
| **BARRIÈRES ÉTHIQUES** | Santé/rituels/décisions — limites strictes | Complaisance réglementaire ✓ |
| **TUNNEL VENTE** | Mention packs premium quand crédit épuisé | Monetization ✓ |
| **RÈGLES TECH** | Pas de JSON, pas de code leak | Sécurité ✓ |

### Astrology block (injecté dynamiquement):

Le prompt système est complété par un **astrology block** qui active des outils:

```python
astrology_block = {
    "defaults": {
        "language": "fr",              # Réponses en français
        "tradition": "psychological"   # Astrologie psychologique (empowerment)
    },
    "enabled_tools": [
        "analysis_natal_report",       # Thème natal (birth chart)
        "analysis_transits_report",    # Transits actuels (what's happening now)
        "analysis_synastry_report",    # Compatibilité (avec qui?)
    ],
    "subjects": [{
        "id": "me",
        "name": user_name,
        "birth_data": {
            "year": 1995,
            "month": 3,
            "day": 15,
            "hour": 14,
            "minute": 30,
            "city": "Paris",
            "country_code": "FR"
        }
    }]
}
```

---

## 4️⃣ Configuration du modèle OpenAI (température, max_tokens, etc)?

### Fichier: `backend/services/plume_chat.py` (ligne ~180-200)

### Configuration complète:

```python
payload = {
    # ════════════════════════════════════════════════════════════
    # LLM Configuration
    # ════════════════════════════════════════════════════════════
    "model": "gpt-4o-mini",                  # ← Modèle (léger, rapide, 4K tokens)
    
    "temperature": 0.85,                     # ← Créativité/determinism
                                              #   0.0 = répétitif, déterministe
                                              #   0.85 = équilibré (actuellement)
                                              #   1.0 = maximal créativité
    
    "max_tokens": 1400,                      # ← Limite réponse
                                              #   ~400-500 mots typiquement
                                              #   Buffer pour pauses/réflexions
    
    # ════════════════════════════════════════════════════════════
    # Messages (multi-turn context)
    # ════════════════════════════════════════════════════════════
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT_SOLENA},
        ...historical_messages,  # Max 30 derniers messages
        {"role": "user", "content": current_user_message}
    ],
    
    # ════════════════════════════════════════════════════════════
    # Astrology-specific
    # ════════════════════════════════════════════════════════════
    "astrology": {
        "defaults": {"language": "fr", "tradition": "psychological"},
        "enabled_tools": [
            "analysis_natal_report",
            "analysis_transits_report",
            "analysis_synastry_report",
        ],
        "subjects": [birth_data_subject]
    },
    
    # ════════════════════════════════════════════════════════════
    # BYOK (Bring Your Own Key) Configuration
    # ════════════════════════════════════════════════════════════
    "byok": {
        "provider": "openai",                # ← OpenAI (not Claude, Gemini)
        "api_key": os.environ.get("OPENAI_API_KEY")
    }
}
```

### Rationale des paramètres:

| Paramètre | Valeur | Rationale | Impact |
|-----------|--------|-----------|--------|
| **Model** | gpt-4o-mini | Léger + rapide. gpt-4o coûte 2x. | ✓ Coût bas, latence faible |
| **Temperature** | 0.85 | Pas trop rigide (0.0) ni trop créatif (1.0). Idéal coaching. | ✓ Réponses variées + cohérentes |
| **Max_tokens** | 1400 | ~400-500 mots réelles. Buffer pour pauses/ponctuations. | ✓ Réponses longues suffisantes |
| **Messages** | [system, history, user] | Context pour multi-turn. Max 30 messages. | ✓ Conversation fluide |
| **Tradition** | psychological | Pas fataliste (vs "vedic" ou "western"). Empowerment. | ✓ Marque alignée |
| **Language** | fr | Astrology tools output français. | ✓ Cohérence linguistique |

### Comment modifier:

**Pour plus de créativité** (réponses plus variées):
```python
"temperature": 1.0  # Max créativité
# ✓ Pros: Réponses plus surprenantes, moins répétitives
# ✗ Cons: Parfois trop fantaisiste, incohérent
```

**Pour plus de stabilité** (réponses déterministes):
```python
"temperature": 0.3  # Réponses stables, prévisibles
# ✓ Pros: Cohérent, reproductible
# ✗ Cons: Répétitif, ennuyeux
```

**Pour réponses plus courtes**:
```python
"max_tokens": 800  # ~250 mots
# ✓ Pros: Plus rapide, moins coûteux
# ✗ Cons: Moins de détail, peut couper en milieu de réponse
```

**Pour réponses plus longues**:
```python
"max_tokens": 2000  # ~600 mots
# ✓ Pros: Plus de détail, nuance
# ✗ Cons: Plus lent, plus coûteux OpenAI
```

### Coûts associés:

**OpenAI (BYOK mode)**:
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens
- Réponse moyenne 500 mots (~600 tokens output) = ~$0.00036

**astrology-api.io (BYOK mode)**:
- 2 crédits par tour (vs 25 en hosted mode)
- Plume paie pour les crédits astrology-api.io

---

## 5️⃣ Si un prompt est envoyé au backend, trouver le fichier correspondant

### Architecture: Qui appelle Qui?

```
Frontend
  └─ SolenaChat.js:send()
       │ POST /api/plume-chat
       │ { message, session_id, birth_data }
       │
       ▼
Backend
  ├─ server.py:plume_chat_endpoint() [ligne 1701]
  │   └─ Reçoit request, extrait body
  │   └─ Appelle: plume_chat_service()
  │
  └─ services/plume_chat.py:plume_chat() [main function]
       │
       ├─ Étape 1: Load historique Supabase
       │   └─ sb.table('plume_chat_messages').select(...)
       │
       ├─ Étape 2: Build messages (system + history + user)
       │   └─ SYSTEM_PROMPT_SOLENA injecté ici
       │
       ├─ Étape 3: Build astrology_block (outils)
       │
       ├─ Étape 4: Build payload
       │   └─ temperature, max_tokens, byok config
       │
       ├─ Étape 5: POST to astrology-api.io
       │   └─ httpx.AsyncClient().post()
       │
       ├─ Étape 6: Parse OpenAI response
       │   └─ choices[0].message.content
       │
       ├─ Étape 7: Check tool leaks (regex)
       │   └─ is_tool_leak(response_text)
       │
       ├─ Étape 8: Persist to Supabase
       │   └─ sb.table('plume_chat_messages').insert()
       │
       └─ Étape 9: Return to frontend
           └─ { success, answer, session_id }

Frontend
  └─ setMessages([...prev, assistant_response])
       └─ Display in chat UI
```

### Fichiers Impliqués:

| Étape | Fichier | Fonction | Responsabilité |
|-------|---------|----------|-----------------|
| 1 | **SolenaChat.js** | `send()` | Déclenche API call, crédit check |
| 2 | **server.py** | `plume_chat_endpoint()` | Route HTTP, parse JSON |
| 3 | **plume_chat.py** | `plume_chat()` main | Orchestration complète |
| 4 | **plume_chat.py** | (builtin) | Build messages + payload |
| 5 | **plume_chat.py** | (async) | HTTP call to astrology-api.io |
| 6 | **plume_chat.py** | (builtin) | Parse response JSON |
| 7 | **plume_chat.py** | `is_tool_leak()` | Regex safeguard |
| 8 | **supabase_client.py** | (implicit) | Persist history |
| 9 | **plume_chat.py** | (return) | Send back to frontend |

### Flux complet avec filepaths:

```
┌────────────────────────────────────────────────────────────────┐
│ 1. User types "Quand rencontrer mon âme sœur?"                │
│    File: frontend/src/components/SolenaChat.js:send()         │
│    → Credit check, axios.post()                                │
└────────────────────┬──────────────────────────────────────────┘
                     │ HTTP POST /api/plume-chat
                     │ { message, session_id, birth_data }
                     │
┌────────────────────▼──────────────────────────────────────────┐
│ 2. Backend receives request                                    │
│    File: backend/server.py:plume_chat_endpoint() [L1701]      │
│    → Parses JSON, extracts user_id (optional)                  │
│    → Calls: plume_chat_service()                               │
└────────────────────┬──────────────────────────────────────────┘
                     │
                     │ await plume_chat(...)
                     │
┌────────────────────▼──────────────────────────────────────────┐
│ 3. Service orchestration                                       │
│    File: backend/services/plume_chat.py:plume_chat()          │
│                                                                │
│    3a. Load history (if user_id)                              │
│        File: backend/services/supabase_client.py              │
│        → sb.table('plume_chat_messages').select(...)          │
│                                                                │
│    3b. Build messages                                          │
│        • Inject SYSTEM_PROMPT_SOLENA                           │
│        • Add historical messages (max 30)                      │
│        • Add current user message                              │
│                                                                │
│    3c. Build astrology block                                  │
│        • Activate tools: natal, transits, synastry             │
│        • Convert birth_data to astrology-api.io format        │
│                                                                │
│    3d. Build payload (temperature, max_tokens, etc)           │
│                                                                │
│    3e. Determine endpoint (BYOK vs HOSTED)                    │
│        if OPENAI_API_KEY → /byok endpoint                     │
│        else → /hosted endpoint                                │
│                                                                │
│    3f. HTTP POST to astrology-api.io                          │
│        await httpx.AsyncClient().post(                        │
│            "https://api.astrology-api.io/api/v3/.../byok"    │
│            headers: { Authorization: Bearer {...} }           │
│            json: payload                                       │
│        )                                                       │
│                                                                │
│    3g. Parse response                                          │
│        response_text = choices[0].message.content             │
│                                                                │
│    3h. Check for tool leaks (regex)                           │
│        if is_tool_leak(response_text) → replace               │
│                                                                │
│    3i. Persist to Supabase                                    │
│        sb.table('plume_chat_messages').insert([               │
│            {role: user, content: message},                    │
│            {role: assistant, content: response_text}          │
│        ])                                                      │
│                                                                │
│    3j. Return to frontend                                     │
│        return { success: true, answer, session_id }           │
└────────────────────┬──────────────────────────────────────────┘
                     │ JSON response
                     │ { success: true, answer: "..." }
                     │
┌────────────────────▼──────────────────────────────────────────┐
│ 4. Frontend receives & displays                               │
│    File: frontend/src/components/SolenaChat.js:send()         │
│    → setMessages([...prev, { role: assistant, content }])    │
│    → Display in chat UI                                        │
└────────────────────────────────────────────────────────────────┘
```

### Variables d'environnement nécessaires:

```bash
# backend/.env

# For step 3f: HTTP auth to astrology-api.io
ASTROLOGY_API_IO_KEY=sk-astrology-api-io-your-bearer-token

# For step 3e: Check if BYOK mode available
OPENAI_API_KEY=sk-proj-your-openai-secret-key

# For step 3i: Supabase persist
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

---

## 📊 SUMMARY TABLE

| Question | Réponse | Fichier(s) Clés |
|----------|---------|-----------------|
| **1. Implémentation?** | React Component (SolenaChat.js) avec state management, localStorage, axios API calls | `SolenaChat.js`, `useAuth()` hook |
| **2. Appels OpenAI?** | Via astrology-api.io v3 proxy (BYOK mode). Model: gpt-4o-mini. Temp: 0.85, max_tokens: 1400 | `plume_chat.py:plume_chat()`, server.py:1701 |
| **3. Prompt système?** | `SYSTEM_PROMPT_SOLENA` multiline string. Contexte marque + GaryVee method (Jab→Coaching→Hook) + barrières éthiques | `plume_chat.py` ligne ~50-250 |
| **4. Config modèle?** | temperature=0.85 (équilibré), max_tokens=1400 (~400-500 mots), model=gpt-4o-mini (léger) | `plume_chat.py` payload construction |
| **5. Backend endpoint?** | POST `/api/plume-chat` → server.py:1701 → plume_chat_service() → astrology-api.io → OpenAI → Supabase persist | server.py + plume_chat.py + supabase_client.py |

---

## 🔗 Quick Navigation

### For Development:
- **Modify Solena's tone**: Edit `SYSTEM_PROMPT_SOLENA` in `plume_chat.py`
- **Change LLM model**: Edit `BYOK_MODEL` constant in `plume_chat.py`
- **Adjust temperature/max_tokens**: Edit payload in `plume_chat.py:plume_chat()`
- **Change credit cost**: Edit `SERVICE_COSTS['chat_astral']` in `config.py`
- **Add new astrology tool**: Modify `enabled_tools` in astrology_block

### For Debugging:
- **Check API logs**: `backend/logs/` or CloudWatch (if deployed)
- **Test endpoint**: `curl -X POST http://localhost:8000/api/plume-chat -H "Content-Type: application/json" -d '{"message":"Test","session_id":"test-123","birth_data":{...}}'`
- **Monitor astrology-api.io**: Check dashboard for credit usage + response times
- **Supabase history**: SELECT * FROM plume_chat_messages WHERE session_id='...'

### For Deployment:
- Ensure all `.env` variables are set
- Test BYOK vs HOSTED mode fallback
- Configure Supabase permissions (RLS)
- Set up monitoring/alerting
