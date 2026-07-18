# 📡 Architecture Solena Chat - Plume Astrale

## 🎯 Vue d'ensemble

**Solena Chat** est un chatbot astrologique propulsé par l'IA qui fournit une guidance personnalisée basée sur:
- Date de naissance de l'utilisateur (thème natal)
- Analyse astrologique + tarot + numérologie
- Modèle d'IA avec système de prompt sophistiqué
- Mode coaching (GaryVee: Jab→Coaching→Hook)

### Stack technologique
- **Frontend**: React (TypeScript/JavaScript)
- **Backend**: FastAPI (Python)
- **LLM Infrastructure**: astrology-api.io v3 (hosted-mode + BYOK)
- **Stockage**: Supabase (PostgreSQL + Auth)
- **Paiements**: Stripe (crédits premium)

---

## 1️⃣ FRONTEND - SolenaChat.js

### Fichier: `frontend/src/components/SolenaChat.js`

#### Responsabilités principales:
1. **Interface de chat inline** (ouvrir/fermer par bouton)
2. **Gestion de l'état local** (messages, input, loading)
3. **Credit gating** (paywall pour utilisateurs anon/non-authentifiés)
4. **Appels API** à `/api/plume-chat` et `/api/credits/use`
5. **Gestion du session_id** (persistance localStorage)
6. **Affichage des données de naissance** (birth_data stockées en localStorage)

#### Constantes clés:
```javascript
const API = process.env.REACT_APP_BACKEND_URL;
const BIRTH_KEY = 'pa_birth_data';           // localStorage key pour données naissance
const SESSION_KEY = 'pa_solena_session_id';  // localStorage key pour session
const FREE_ANON_QUESTIONS = 2;               // Questions gratuites (anon users)
const COST_PER_QUESTION = 10;                // Crédits par question (auth users)
const ANON_COUNT_KEY = 'pa_solena_anon_count';
```

#### Flux utilisateur:

**1. Initialisation du chat (si pas de naissance)**
```javascript
// Affiche: "Confie-moi ta date de naissance pour lire ton ciel"
// L'utilisateur fournit sa date/heure/lieu
await sendFirstGreeting(birthData)
// Message système: "Bonjour Solena. Je viens de te confier..."
```

**2. Premier appel API** (seedMsg automatique)
```javascript
// Si birthData existe, envoie un message de contexte
const seedMsg = `Bonjour Solena. Je viens de te confier ma date de naissance : 
${bd.day}/${bd.month}/${bd.year} à ${bd.hour}h${bd.minute} à ${bd.place}. 
Que révèle mon ciel de naissance sur mes cycles d'amour à venir ?`;

const res = await axios.post(`${API}/api/plume-chat`, {
  message: seedMsg,
  session_id: sessionId,
  birth_data: bd,  // ← Data astro envoyée au backend
}, { timeout: 45000 });
```

**3. Envoi de message utilisateur**
```javascript
// Credit check (optionnel si auth user):
if (!isAuthenticated) {
  if (anonCount >= FREE_ANON_QUESTIONS) {
    setPaywallOpen(true);  // Paywall modal
    return;
  }
}

// Déduction crédits (utilisateurs authentifiés)
if (isAuthenticated && token) {
  await axios.post(`${API}/credits/use`, 
    { service: 'chat_astral' },  // ← Cost: 10 crédits (config.py:SERVICE_COSTS)
    { headers: { Authorization: `Bearer ${token}` } }
  );
}

// Appel chat
const res = await axios.post(`${API}/api/plume-chat`, {
  message: text,
  session_id: sessionId,
  birth_data: birthData,  // ← Persistance données naissance
});
```

#### Structure des messages:
```javascript
{
  role: 'user' | 'assistant',
  content: string,
  hidden?: boolean  // true = non affiché au user (ex: seedMsg)
}
```

#### Variables d'environnement frontend:
```
REACT_APP_BACKEND_URL=https://api.plume-astrale.fr
```

---

## 2️⃣ BACKEND - Routes & Services

### Fichier: `backend/server.py`

#### Endpoint: POST `/api/plume-chat` (ligne 1701)

```python
@api_router.post('/plume-chat')
async def plume_chat_endpoint(
    request: Request,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Body: { message, session_id, birth_data }
    Auth: optionnelle (utilisateurs anon acceptés)
    """
    body = await request.json()
    message = body.get('message').strip()
    session_id = body.get('session_id')
    birth_data = body.get('birth_data')  # ← { day, month, year, hour, min, place }
    user_id = current_user['id'] if current_user else None

    # Délègue au service
    result = await plume_chat_service(
        message=message,
        session_id=session_id,
        birth_data=birth_data,
        user_id=user_id,
    )
    result['session_id'] = session_id
    return result
```

#### Response format:
```json
{
  "success": true,
  "answer": "Réponse de Solena...",
  "session_id": "solena-123456-abc"
}
```

#### Endpoint historique: GET `/api/plume-chat/history/{session_id}` (ligne 1742)
```python
@api_router.get('/plume-chat/history/{session_id}')
async def plume_chat_history_endpoint(
    session_id: str,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Retourne l'historique d'une session (utilisateurs authentifiés seulement)."""
    user_id = current_user['id'] if current_user else None
    messages = await get_session_history(session_id, user_id)
    return {'success': True, 'messages': messages}
```

---

### Fichier: `backend/services/plume_chat.py`

#### Configuration LLM:

**URL d'API astrology-api.io:**
```python
ASTROLOGY_API_IO_URL = "https://api.astrology-api.io/api/v3/chat/completions/byok"          # BYOK mode (user OpenAI key)
ASTROLOGY_API_IO_URL_HOSTED = "https://api.astrology-api.io/api/v3/chat/completions"        # Hosted mode (astrology-api.io gère OpenAI)
DEFAULT_TIMEOUT = 60.0
BYOK_MODEL = "gpt-4o-mini"  # ← Modèle utilisé
```

#### Configuration du modèle:
```python
payload = {
    "messages": messages,               # [system, history..., user]
    "astrology": astrology_block,       # Outils astro activés
    "temperature": 0.85,                # ← Créativité (0.85 = équilibré)
    "max_tokens": 1400,                 # ← Limite longueur réponse
}
```

#### Payload complet envoyé à astrology-api.io:

```python
# Mode BYOK (utilise clé OpenAI utilisateur)
if openai_key:
    payload["model"] = "gpt-4o-mini"
    payload["byok"] = {
        "provider": "openai",
        "api_key": openai_key,          # ← Clé OpenAI depuis .env
    }
    target_url = ASTROLOGY_API_IO_URL   # /byok endpoint
else:
    target_url = ASTROLOGY_API_IO_URL_HOSTED  # hosted (coûte 25 crédits astrology-api.io)

# HTTP request
async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
    r = await client.post(
        target_url,
        headers={
            "Authorization": f"Bearer {api_key}",  # ← ASTROLOGY_API_IO_KEY
            "Content-Type": "application/json",
        },
        json=payload,
    )
```

#### Outils astrologiques activés:
```python
astrology_block = {
    "defaults": { 
        "language": "fr",               # Réponses en français
        "tradition": "psychological"    # Astrologie psychologique (pas fataliste)
    },
    "enabled_tools": [
        "analysis_natal_report",        # Thème natal
        "analysis_transits_report",     # Transits actuels
        "analysis_synastry_report",     # Compatibilité (synastrie)
    ],
}
```

---

## 3️⃣ PROMPT SYSTÈME - Le cœur de Solena

### Fichier: `backend/services/plume_chat.py` (ligne ~50)

**Variable**: `SYSTEM_PROMPT_SOLENA`

#### Sections clés du prompt:

**1. Contexte de marque:**
```
Tu es Soléna, l'ambassadrice et la guide spirituelle de Plume Astrale (plume-astrale.fr).

Tu n'es pas une voyante de fête foraine qui prédit l'avenir de manière passive. 
Tu es une coach de vie moderne, une mentore de l'âme qui utilise l'astrologie, 
le tarot et la numérologie comme des outils de décodage psychologique, de self-care 
et d'empowerment.
```

**2. Ton & Personnalité:**
- Bienveillante, chaleureuse, empathique — mais **ancrée et percutante**
- Parle au "tu" ou "vous" (adaptatif)
- **Ne juge jamais** — valide les émotions d'abord
- Style éditorial **haut de gamme**: pas de jargon mystique incompréhensible
- Ancrée dans la réalité (psychological astrology, pas de prédictions fatalistes)

**3. Méthode GaryVee (Jab → Coaching → Hook):**

```
JAB — Délivrer de la valeur brute
└─ Analyse astrale/tarot CONCISE et directe
└─ Traduis le message des cartes en langage quotidien
└─ Pas de "peut-être" — nomme ce que tu vois

COACHING — Passer à l'action
└─ NE T'ARRÊTE PAS à la prédiction
└─ Transforme la lecture en **ACTIONS CONCRÈTES**
└─ Exemple: "Les astres montrent un blocage sur ta 5e maison. 
           Voici l'action concrète que tu peux poser AUJOURD'HUI…"

HOOK — Ne JAMAIS fermer la discussion
└─ ⚠️  RÈGLE D'OR: Termine TOUJOURS par UNE QUESTION OUVERTE
└─ Jamais de points finaux passifs ("Bonne journée", "Que les étoiles te guident")
└─ La question doit toucher le **CŒUR ou L'URGENCE** du moment
└─ Objectif: utilisateur dépense ses crédits pour répondre
```

**Exemple de Hook:**
```
"Quand tu penses à cette personne, c'est plutôt son silence qui te blesse, 
ou le fait que tu ne te sens plus prioritaire ?"
```

**4. Directives de formatage:**

```
✓ Paragraphes courts: 2-3 phrases MAXIMUM
✓ Listes à puces (• ou -) pour structurer
✓ Ultra-lisible sur smartphone: 4-5 paragraphes court MAX par réponse
✓ Gras (**texte**) UNIQUEMENT pour mots-clés critiques
✗ Pas de titres en majuscules
✗ Pas d'emojis (sauf 1 subtil au début: ·, ◐, ⚡, 🌙)
✗ Pas de jargon mystique incompréhensible
```

**5. Barrières éthiques:**

```
SANTÉ (INTERDIT ABSOLU)
├─ Pas de diagnostics médicaux
├─ Pas de conseil grossesse/fertilité médicale
├─ Pas de conseil santé physique
├─ Si demande → redirection bienveillante: "Ces questions relèvent du corps médical. 
                 Ce que je peux faire, c'est regarder avec toi comment tes énergies 
                 actuelles te soutiennent émotionnellement…"

RITUELS & BIEN-ÊTRE
├─ Lithothérapie, tisanes, méditation: OK mais comme "accompagnement bien-être"
├─ JAMAIS présentés comme "remèdes" ou "traitements"

DÉCISIONS VITALES (PAS D'ORDRE)
├─ Rompre, quitter emploi, déménager
├─ Éclaire les énergies → propose des scénarios → **laisse la décision**
└─ N'ordonne JAMAIS
```

**6. Business rules:**

```
CRÉDITS
├─ Utilisateur arrive avec 20 crédits offerts
├─ Chaque question coûte 10 crédits
├─ Packs disponibles:
│  ├─ Initiation: 15 crédits = 4,99€
│  ├─ Clarté: 50+10 bonus crédits = 14,99€  [Plus choisi]
│  └─ Flammes Jumelles: 100+30 bonus = 29,99€  [Meilleur rapport]
└─ Si solde insuffisant → invite CHALEUREUSE:
   "Ce que je vois est riche, mais nécessite quelques minutes de plus.
    Recharge quand tu es prête, et on continue là où on s'est arrêtées ?"

RESTRICTIONS TECHNIQUES
├─ Réponds TOUJOURS en français naturel
├─ N'émets JAMAIS JSON/code/action_input visibles
├─ N'invente JAMAIS config astro sans justification depuis birth_data
└─ Pas de tool leaks (détection regex pour JSON d'appels d'outils)
```

---

## 4️⃣ FLUX COMPLET - REQUEST → RESPONSE

### Étape 1: Frontend → Backend
```
POST /api/plume-chat
{
  "message": "Quand vais-je rencontrer mon âme sœur ?",
  "session_id": "solena-abc123-def456",
  "birth_data": {
    "day": 15,
    "month": 3,
    "year": 1995,
    "hour": 14,
    "min": 30,
    "place": "Paris, France",
    "name": "Anna"  // optionnel
  }
}
```

### Étape 2: Backend - Charger l'historique
```python
# Si user_id existe (user authentifiés)
history_msgs = sb.table('plume_chat_messages').select(...)
# Récupère max 30 derniers messages de la session
```

### Étape 3: Backend - Construire le payload
```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT_SOLENA},  # Prompt système
    ...history_msgs,  # Historique multi-tour
    {"role": "user", "content": message}  # Nouveau message
]

# Subject pour outils astro
subject = {
    "id": "me",
    "name": "Anna",
    "birth_data": {
        "year": 1995,
        "month": 3,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "city": "Paris",
        "country_code": "FR"
    }
}

payload = {
    "messages": messages,
    "astrology": {
        "defaults": {"language": "fr", "tradition": "psychological"},
        "enabled_tools": ["analysis_natal_report", "analysis_transits_report", "analysis_synastry_report"],
        "subjects": [subject]
    },
    "temperature": 0.85,
    "max_tokens": 1400,
    "model": "gpt-4o-mini",
    "byok": {
        "provider": "openai",
        "api_key": os.environ.get("OPENAI_API_KEY")
    }
}
```

### Étape 4: Backend → astrology-api.io v3
```python
# POST https://api.astrology-api.io/api/v3/chat/completions/byok
# Headers:
#   Authorization: Bearer {ASTROLOGY_API_IO_KEY}
#   Content-Type: application/json
# Body: payload (ci-dessus)
```

### Étape 5: astrology-api.io → OpenAI GPT-4o-mini
astrology-api.io forward le payload à OpenAI avec:
- Système prompt (Solena)
- Contexte astrology-api.io propriétaire (pour outils astro)
- Clé OpenAI utilisateur (BYOK mode)

### Étape 6: OpenAI → Réponse
Réponse formatée selon le système prompt:
```
◐ Anna, tu es dans une phase de transition majeure selon tes transits actuels.
  Mars t'appelle à sortir de ta zone de confort — c'est là que les rencontres 
  authentiques naissent.

• Action concrète: Cette semaine, accepte UNE invitation sociale que tu aurais 
  normalement décliné. Les astres créent des rendez-vous, pas du destin figé.
  
• Dates clés: Vénus entre en Maison 7 (engagement) le 23 novembre. 
  C'est une fenêtre de 4 semaines idéale pour la rencontre.

Mais dis-moi: quand tu visualises cette future rencontre, est-ce plutôt 
l'émotion du "partage intime" qui t'appelle, ou l'idée de "ne plus être seule" ?
```

### Étape 7: Backend - Persister & Retourner
```python
# Si user_id:
sb.table('plume_chat_messages').insert([
    {"session_id": session_id, "user_id": user_id, "role": "user", "content": message},
    {"session_id": session_id, "user_id": user_id, "role": "assistant", "content": response_text},
])

# Response au frontend:
{
    "success": true,
    "answer": "◐ Anna, tu es dans...",
    "session_id": "solena-abc123-def456"
}
```

### Étape 8: Frontend - Afficher
```javascript
setMessages((prev) => [
    ...prev, 
    { role: 'assistant', content: response_text }
]);
```

---

## 5️⃣ CONFIGURATION & VARIABLES D'ENVIRONNEMENT

### Backend - `backend/.env`

```env
# Supabase (stockage messages + auth)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_ANON_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_JWT_ALGORITHM=HS256

# astrology-api.io (v3 — LLM + outils astro)
ASTROLOGY_API_IO_KEY=sk-astrology-api-io-bearer-token
# ^ Endpoint: https://api.astrology-api.io/api/v3/chat/completions/byok

# OpenAI (BYOK mode — utilisateur paie directement)
OPENAI_API_KEY=sk-your-openai-secret-key
# ^ Modèle: gpt-4o-mini
# ^ Température: 0.85
# ^ Max tokens: 1400

# Stripe (paiements crédits)
STRIPE_API_KEY=sk_test_... ou sk_live_...
```

### Frontend - `.env.local`

```env
REACT_APP_BACKEND_URL=https://api.plume-astrale.fr
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJ...
```

---

## 6️⃣ COÛTS & CRÉDITS

### Structure de coûts (fichier `backend/config.py`):

```python
SERVICE_COSTS = {
    'chat_astral': 10,  # 1 question Solena = 10 crédits
    # ...
}

PACKS = {
    'initiation': {
        'credits': 15,
        'bonus': 0,
        'amount': 4.99,
    },
    'astro_amour': {
        'name': 'Clarté',
        'credits': 50,
        'bonus': 10,
        'amount': 14.99,
    },
    'flammes_jumelles': {
        'credits': 100,
        'bonus': 30,
        'amount': 29.99,
    },
}
```

### Pricing astrology-api.io:
- **BYOK mode** (utilisateur OpenAI key): 2 crédits/tour côté astrology-api.io
- **Hosted mode** (astrology-api.io gère OpenAI): 25 crédits/tour côté astrology-api.io
- Fallback: Si BYOK échoue → retry en hosted (plus cher)

---

## 7️⃣ FICHIERS PERTINENTS - RÉSUMÉ

| Fichier | Responsabilité | Clé |
|---------|-----------------|-----|
| **frontend/src/components/SolenaChat.js** | UI chat + gating crédits | `send()`, `openChat()` |
| **frontend/src/lib/solena.js** | Configuration Solena (nom, bio, portrait) | `SOLENA` object |
| **backend/services/plume_chat.py** | Service LLM + astrology-api.io | `plume_chat()`, `SYSTEM_PROMPT_SOLENA` |
| **backend/server.py** | Route endpoint `/api/plume-chat` | `plume_chat_endpoint()` |
| **backend/config.py** | Coûts, packs, configuration | `SERVICE_COSTS`, `PACKS` |
| **backend/.env** | Clés API (Supabase, OpenAI, astrology-api.io) | `ASTROLOGY_API_IO_KEY`, `OPENAI_API_KEY` |

---

## 8️⃣ FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. USER (Browser)                                                   │
├─────────────────────────────────────────────────────────────────────┤
│ SolenaChat.js:                                                      │
│ • Input: "Quand vais-je rencontrer mon âme sœur ?"                 │
│ • Storage: birth_data (localStorage), session_id                   │
│ • Gating: 10 crédits (auth) ou 2 questions gratuites (anon)        │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                    POST /api/plume-chat
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. BACKEND FastAPI                                                  │
├─────────────────────────────────────────────────────────────────────┤
│ server.py (plume_chat_endpoint):                                    │
│ • Reçoit: message, session_id, birth_data, [user_id]              │
│ • Charge historique depuis Supabase (si auth)                       │
│ • Appelle: plume_chat_service()                                    │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                    (plume_chat.py)
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. SERVICE - plume_chat.py                                          │
├─────────────────────────────────────────────────────────────────────┤
│ • Construit payload:                                                │
│   - system_prompt: SYSTEM_PROMPT_SOLENA                            │
│   - messages: [system, history, user]                              │
│   - astrology: { subjects, tools }                                 │
│   - model: gpt-4o-mini                                             │
│   - temperature: 0.85                                              │
│   - max_tokens: 1400                                               │
│   - byok: { provider: "openai", api_key }                          │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
        POST /api/v3/chat/completions/byok
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. astrology-api.io v3 (BYOK)                                      │
├─────────────────────────────────────────────────────────────────────┤
│ • Activates astro tools:                                            │
│   - analysis_natal_report                                           │
│   - analysis_transits_report                                        │
│   - analysis_synastry_report                                        │
│ • Forwards to OpenAI (user's BYOK key)                              │
│ • Cost: 2 crédits astrology-api.io                                 │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
            OpenAI API (gpt-4o-mini)
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 5. OpenAI GPT-4o-mini                                               │
├─────────────────────────────────────────────────────────────────────┤
│ • System: SYSTEM_PROMPT_SOLENA (coaching method)                   │
│ • Context: natal chart + transits + user history                   │
│ • Generates: personalized response with Hook (open question)       │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                     Response text
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 6. BACKEND - Response handling                                      │
├─────────────────────────────────────────────────────────────────────┤
│ • Check tool_leak (prevent JSON exposure)                           │
│ • Persist to Supabase (if user_id exists)                          │
│ • Return to frontend: { success, answer, session_id }              │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                        JSON response
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 7. FRONTEND - Display                                               │
├─────────────────────────────────────────────────────────────────────┤
│ SolenaChat.js:                                                      │
│ • Add message to state                                              │
│ • Scroll to bottom                                                  │
│ • Display Solena's response                                         │
│ • Decrement credits (if authenticated)                              │
│ • Show paywall if needed                                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 9️⃣ DETECT TOOL LEAKS

Backend has safeguard contre les fuites de JSON d'appels d'outils:

```python
def is_tool_leak(text: str) -> bool:
    """Retourne True si le texte ressemble à un appel d'outil JSON."""
    if not text or len(text) > 3000:
        return False
    if not _TOOL_LEAK_RE.match(text):  # Regex: ^\s*\{[\s\S]*"action"[\s\S]*\}\s*$
        return False
    try:
        obj = json.loads(text.strip())
        return isinstance(obj, dict) and ('action' in obj or 'action_input' in obj)
    except Exception:
        return False
```

Si leak détecté:
```python
response_text = "Je perds un instant le fil des astres. Peux-tu me redire en une phrase ce qui t'a amené(e) à Plume aujourd'hui ?"
```

---

## 🔟 SECURITY & ETHICAL RULES

### Auth:
- Route `/api/plume-chat`: **optionnel** (anon OK)
- Route `/api/plume-chat/history`: **optionnel** mais filtre par user_id
- Utilisateurs anon: 2 questions gratuites max

### Prompt constraints:
- ✓ Astrologie psychologique (empowerment, pas fatalisme)
- ✓ Coaching actionnable (Jab → Action → Hook)
- ✗ Pas de conseil médical
- ✗ Pas d'ordre sur décisions vitales
- ✗ Pas de JSON/code visible

### Data persistence:
- Messages stockés dans `plume_chat_messages` table (Supabase)
- Clés API JAMAIS exposées au frontend
- OpenAI key utilisé via BYOK (astrology-api.io proxy)

---

## Summary - 1 Minute Overview

**Solena Chat** est un **chatbot astrologique IA + coaching**:

1. **Frontend** (SolenaChat.js):
   - Chat interface avec credit gating
   - Stocke birth_data et session_id en localStorage
   - 2 questions gratuites (anon) / 10 crédits (auth)

2. **Backend** (/api/plume-chat):
   - Reçoit message + birth_data + session_id
   - Charge historique depuis Supabase

3. **IA Layer** (astrology-api.io + OpenAI):
   - Envoie payload avec SYSTEM_PROMPT_SOLENA
   - Active outils astrologiques (natal, transits, synastrie)
   - Modèle: gpt-4o-mini (temp 0.85, max_tokens 1400)

4. **Prompt System**:
   - **GaryVee method**: Jab (valeur) → Coaching (action) → Hook (question)
   - Psychological astrology (pas de prédictions fatalistes)
   - Formatage court, lisible mobile
   - Barrières éthiques strictes

5. **Pricing**:
   - 10 crédits par question (utilisateurs auth)
   - Packs: Initiation 4,99€ / Clarté 14,99€ / Flammes Jumelles 29,99€

**Stack**: React ← FastAPI ← astrology-api.io ← OpenAI GPT-4o-mini
