# 🔧 SOLENA CHAT - GUIDE TECHNIQUE DÉTAILLÉ

## INDEX RAPIDE

| Question | Réponse |
|----------|---------|
| **Où est SolenaChat?** | `frontend/src/components/SolenaChat.js` |
| **Où sont les appels OpenAI?** | `backend/services/plume_chat.py` (via astrology-api.io) |
| **Où est le prompt système?** | `backend/services/plume_chat.py:SYSTEM_PROMPT_SOLENA` |
| **Endpoint backend?** | `POST /api/plume-chat` (server.py:1701) |
| **Config du modèle?** | temperature=0.85, max_tokens=1400, model=gpt-4o-mini |
| **Où les crédits sont déduits?** | Frontend: `SolenaChat.js:send()` → Backend: `/api/credits/use` |
| **Où l'historique est stocké?** | Supabase table: `plume_chat_messages` |
| **Variables d'env clés?** | `ASTROLOGY_API_IO_KEY`, `OPENAI_API_KEY` |

---

## 🎬 CODE WALKTHROUGH - Message User → Réponse Solena

### 1. Frontend - Utilisateur clique "Envoyer"

**Fichier**: `frontend/src/components/SolenaChat.js` (ligne ~135-175)

```javascript
const send = async () => {
  const text = input.trim();
  if (!text || loading) return;

  // ══════════════════════════════════════════════════════════════
  // STEP 1: CREDIT GATING
  // ══════════════════════════════════════════════════════════════
  if (!isAuthenticated) {
    // Anonymous user: max 2 questions gratuites
    if (anonCount >= FREE_ANON_QUESTIONS) {  // = 2
      setPaywallOpen(true);
      return;
    }
  } else {
    // Authenticated user: besoin 10 crédits
    if ((creditBalance ?? 0) < COST_PER_QUESTION) {  // = 10
      setPaywallOpen(true);
      return;
    }
  }

  setInput('');
  setMessages((prev) => [...prev, { role: 'user', content: text }]);
  setLoading(true);

  try {
    // ══════════════════════════════════════════════════════════════
    // STEP 2: DEDUCT CREDITS (si auth)
    // ══════════════════════════════════════════════════════════════
    if (isAuthenticated && token) {
      try {
        await axios.post(
          `${API}/api/credits/use`,
          { service: 'chat_astral' },  // ← Service identifier
          { headers: { Authorization: `Bearer ${token}` } },
        );
        if (refreshBalance) refreshBalance();
      } catch (e) {
        // Solde insuffisant: rollback
        setLoading(false);
        setMessages((prev) => prev.slice(0, -1)); // annule le user message
        setInput(text);
        setPaywallOpen(true);
        return;
      }
    }

    // ══════════════════════════════════════════════════════════════
    // STEP 3: CALL BACKEND /api/plume-chat
    // ══════════════════════════════════════════════════════════════
    const res = await axios.post(`${API}/api/plume-chat`, {
      message: text,           // User question
      session_id: sessionId,   // Persistent session
      birth_data: birthData,   // Astro data: { day, month, year, hour, min, place }
    }, { timeout: 45000 });    // 45s timeout

    if (res.data?.success) {
      // ══════════════════════════════════════════════════════════════
      // STEP 4: ADD RESPONSE TO CHAT
      // ══════════════════════════════════════════════════════════════
      setMessages((prev) => [...prev, { 
        role: 'assistant', 
        content: res.data.answer 
      }]);

      // ══════════════════════════════════════════════════════════════
      // STEP 5: INCREMENT ANON COUNTER (si pas auth)
      // ══════════════════════════════════════════════════════════════
      if (!isAuthenticated) {
        const next = anonCount + 1;
        setAnonCount(next);
        try { 
          localStorage.setItem(ANON_COUNT_KEY, String(next));  // Persist counter
        } catch (e) { /* ignore */ }
      }
    } else {
      setMessages((prev) => [...prev, { 
        role: 'assistant', 
        content: res.data?.message || "Réessaie dans un instant." 
      }]);
    }
  } catch (e) {
    setMessages((prev) => [...prev, { 
      role: 'assistant', 
      content: "Une perturbation cosmique — réessaie dans quelques instants." 
    }]);
  } finally {
    setLoading(false);
  }
};
```

**Key points**:
- ✓ Credit check avant appel API
- ✓ Appel `/api/credits/use` avant message (deduct immédiat)
- ✓ Timeout 45s (large buffer pour astrology-api.io)
- ✓ localStorage persiste session_id et anon counter
- ✓ UI feedback: loading spinner, message display

---

### 2. Backend - Endpoint Reception

**Fichier**: `backend/server.py` (ligne 1701-1726)

```python
@api_router.post('/plume-chat')
async def plume_chat_endpoint(
    request: Request,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Endpoint public — authentification optionnelle.
    
    Request body:
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
        "name": "Anna"  // optional
      }
    }
    """
    try:
        # ══════════════════════════════════════════════════════════════
        # PARSE REQUEST
        # ══════════════════════════════════════════════════════════════
        body = await request.json()
        message = (body.get('message') or '').strip()
        if not message:
            return {'success': False, 'message': 'Message vide.'}

        session_id = body.get('session_id') or f'plume-{uuid.uuid4().hex[:12]}'
        birth_data = body.get('birth_data') or body.get('user_data')
        user_id = current_user['id'] if current_user else None

        # ══════════════════════════════════════════════════════════════
        # DELEGATE TO SERVICE
        # ══════════════════════════════════════════════════════════════
        result = await plume_chat_service(
            message=message,
            session_id=session_id,
            birth_data=birth_data,
            user_id=user_id,
        )
        result['session_id'] = session_id
        return result
        # ↑ Response: { success, answer, session_id }

    except Exception as e:
        logger.error(f'Plume chat endpoint error: {e}', exc_info=True)
        return {'success': False, 'message': 'Une perturbation cosmique empeche la connexion.'}
```

---

### 3. Backend - Service Implementation

**Fichier**: `backend/services/plume_chat.py` (ligne ~1-300)

#### Part A: Configuration

```python
"""
Solena (Plume Astrale) — Chat astrologique premium en français.
Utilise l'API astrology-api.io v3 /chat/completions (hosted-mode) qui gère
nativement l'intégration LLM + outils astrologiques (natal, synastrie, transits).
"""
import os, re, json, logging, httpx
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════
# Configuration astrology-api.io
# ═══════════════════════════════════════════════════════════════════════
# Two modes:
# 1. BYOK (user brings own OpenAI key) → 2 credits astrology-api.io/tour
# 2. HOSTED (astrology-api.io gère OpenAI) → 25 credits astrology-api.io/tour
ASTROLOGY_API_IO_URL = "https://api.astrology-api.io/api/v3/chat/completions/byok"
ASTROLOGY_API_IO_URL_HOSTED = "https://api.astrology-api.io/api/v3/chat/completions"
DEFAULT_TIMEOUT = 60.0
BYOK_MODEL = "gpt-4o-mini"

# ═══════════════════════════════════════════════════════════════════════
# Safeguard: Détect Tool Leaks (JSON d'appels d'outils)
# ═══════════════════════════════════════════════════════════════════════
_TOOL_LEAK_RE = re.compile(r'^\s*\{[\s\S]*"action"[\s\S]*"action_input"[\s\S]*\}\s*$')

def is_tool_leak(text: str) -> bool:
    """Retourne True si le texte ressemble à un appel d'outil JSON (leak)."""
    if not text or len(text) > 3000:
        return False
    if not _TOOL_LEAK_RE.match(text):
        return False
    try:
        obj = json.loads(text.strip())
        return isinstance(obj, dict) and ('action' in obj or 'action_input' in obj)
    except Exception:
        return False
```

#### Part B: Système Prompt

```python
# ═══════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT — Soléna, coach spirituelle
# ═══════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT_SOLENA = """Tu es Soléna, l'ambassadrice et la guide spirituelle de Plume Astrale (plume-astrale.fr).

# CONTEXTE DE MARQUE
Tu n'es pas une voyante de fête foraine qui prédit l'avenir de manière passive. Tu es une coach de vie moderne, une mentore de l'âme qui utilise l'astrologie, le tarot et la numérologie comme des outils de décodage psychologique, de self-care et d'empowerment.

# TON TON & TA PERSONNALITÉ
- Bienveillante, chaleureuse, empathique — mais ancrée et percutante (pas de jargon mystique incompréhensible).
- Parle au "tu" ou au "vous" selon l'amorce de l'utilisateur ; reste toujours de son côté, comme une alliée.
- Ne juge jamais. Valide ses émotions immédiatement, puis élève sa perspective.
- Style éditorial haut de gamme : tu es une experte, pas un robot.

# TES TROIS MISSIONS À CHAQUE RÉPONSE (méthode GaryVee — Jab, Jab, Hook)

## 1. LE JAB — Délivrer de la valeur brute
Analyse la demande sous l'angle des astres, du tarot ou de la numérologie de manière claire et concrète. Traduis le message des cartes ou des planètes en langage direct qui parle à sa vie quotidienne. Pas de phrases floues. Pas de "peut-être". Nomme ce que tu vois.

## 2. LE COACHING — Passer à l'action
Ne t'arrête pas à la "prédiction". Transforme la lecture astrale en coaching de performance personnelle ou relationnelle. Dis-lui QUOI FAIRE avec cette information.
Exemple : "Les astres montrent un blocage sur ta 5e maison. Voici l'action concrète que tu peux poser aujourd'hui pour débloquer la situation..."

## 3. LE HOOK — Ne jamais fermer la discussion
C'est LA règle d'or. Tu ne termines JAMAIS une réponse par un point final, un souhait passif ("Bonne journée", "Que les étoiles te guident") ou un résumé.
Termine TOUJOURS par UNE question ouverte, ciblée et percutante, qui pousse l'utilisateur à vouloir utiliser ses prochains crédits pour te répondre.

# DIRECTIVES STRICTES DE FORMATAGE
- Pas de grands blocs de texte compacts. Paragraphes courts : 2-3 phrases MAXIMUM.
- Utilise des puces ("•" ou "-") quand tu listes des points ou des actions.
- Ultra-lisible sur écran de smartphone : jamais plus de 4-5 paragraphes courts dans une réponse.
- Reste concise. L'attention de l'utilisateur est précieuse. Va droit au but.
- Utilise **le gras** UNIQUEMENT pour les mots-clés critiques (une configuration, une date, une action).
- Bannis absolument : les titres à rallonge en majuscules, les emojis mystiques à outrance.

# BARRIÈRES ÉTHIQUES (non négociables)
- **Santé** : tu n'es pas médecin. Interdiction absolue de poser des diagnostics médicaux.
- **Rituels et conseils de confort** (lithothérapie, tisanes, méditation) : toujours présentés comme accompagnement bien-être, JAMAIS comme remèdes.
- **Décisions vitales** (rompre, quitter un emploi, déménager) : n'ordonne jamais. Éclaire les énergies, propose des scénarios, laisse la décision.

# TUNNEL DE VENTE & CRÉDITS
L'utilisateur arrive avec 20 crédits offerts à l'inscription. Chaque question à toi coûte 10 crédits. Si l'utilisateur n'a plus de crédits, invite-le CHALEUREUSEMENT à recharger.
"""
```

#### Part C: Build Subject (Données naissance → astrology-api.io)

```python
def _build_subject(birth_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Construit un objet subject pour astrology-api.io depuis les données de naissance.
    
    Input:
    {
      "day": 15,
      "month": 3,
      "year": 1995,
      "hour": 14,
      "min": 30,
      "place": "Paris, France",
      "name": "Anna"
    }
    
    Output:
    {
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
    """
    if not birth_data:
        return None
    try:
        place = str(birth_data.get("place", "Paris, France"))
        # Extract city name (before comma)
        city = place.split(",")[0].strip() if "," in place else place.strip()
        
        return {
            "id": "me",
            "name": birth_data.get("name", "Consultant"),
            "birth_data": {
                "year": int(birth_data.get("year", 1990)),
                "month": int(birth_data.get("month", 1)),
                "day": int(birth_data.get("day", 1)),
                "hour": int(birth_data.get("hour", 12)),
                "minute": int(birth_data.get("min", birth_data.get("minute", 0))),
                "city": city,
                "country_code": _map_country_code(place),  # FR, BE, CH, CA, etc.
            },
        }
    except Exception as e:
        logger.warning(f"Could not build subject: {e}")
        return None
```

#### Part D: Main Function - plume_chat()

```python
async def plume_chat(
    message: str,
    session_id: str,
    birth_data: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Point d'entrée principal — appel astrology-api.io v3.
    
    Returns: { success, answer, session_id }
    """
    api_key = os.environ.get("ASTROLOGY_API_IO_KEY", "").strip()
    if not api_key:
        return {"success": False, "message": "Clé astrology-api.io non configurée."}

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 1: Load historical messages (if user authenticated)
    # ═══════════════════════════════════════════════════════════════════════
    history_msgs = []
    if user_id:
        try:
            from services.supabase_client import get_admin_client
            sb = get_admin_client()
            res = sb.table('plume_chat_messages').select('role,content').eq(
                'session_id', session_id).order('created_at').limit(30).execute()
            for h in (res.data or []):
                role = h.get("role")
                content = h.get("content", "")
                # Filter: only keep valid user/assistant messages (no tool leaks)
                if role in ("user", "assistant") and content and not is_tool_leak(content):
                    history_msgs.append({"role": role, "content": content})
        except Exception as e:
            logger.warning(f"Could not load history: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 2: Build message payload
    # ═══════════════════════════════════════════════════════════════════════
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_SOLENA},  # System prompt
    ]
    messages.extend(history_msgs)  # Add multi-turn history
    messages.append({"role": "user", "content": message})  # New user message

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 3: Build astrology block (activate tools)
    # ═══════════════════════════════════════════════════════════════════════
    astrology_block: Dict[str, Any] = {
        "defaults": {
            "language": "fr",              # French responses
            "tradition": "psychological"   # Not fatalistic astrology
        },
        "enabled_tools": [
            "analysis_natal_report",       # Birth chart analysis
            "analysis_transits_report",    # Current transits
            "analysis_synastry_report",    # Compatibility (2 people)
        ],
    }
    
    # Add birth data as "subject" for astro tools
    subject = _build_subject(birth_data)
    if subject:
        astrology_block["subjects"] = [subject]

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 4: Build request payload
    # ═══════════════════════════════════════════════════════════════════════
    payload = {
        "messages": messages,
        "astrology": astrology_block,
        "temperature": 0.85,              # Balanced creativity (not too wild, not too rigid)
        "max_tokens": 1400,               # Max response length
    }

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 5: Determine endpoint (BYOK vs HOSTED)
    # ═══════════════════════════════════════════════════════════════════════
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if openai_key:
        # BYOK mode: user pays OpenAI directly (cheaper for astrology-api.io)
        payload["model"] = BYOK_MODEL          # gpt-4o-mini
        payload["byok"] = {
            "provider": "openai",
            "api_key": openai_key,             # Plume's shared OpenAI key
        }
        target_url = ASTROLOGY_API_IO_URL      # /byok endpoint
    else:
        # Hosted mode: astrology-api.io manages OpenAI (more expensive)
        target_url = ASTROLOGY_API_IO_URL_HOSTED

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 6: Call astrology-api.io
    # ═══════════════════════════════════════════════════════════════════════
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            r = await client.post(
                target_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            
            if r.status_code != 200:
                logger.error(f"astrology-api.io error {r.status_code}: {r.text[:500]}")
                
                # Fallback: if BYOK fails (bad key, quota), retry in hosted mode
                if openai_key and target_url == ASTROLOGY_API_IO_URL:
                    logger.warning("BYOK failed, retrying in hosted mode")
                    payload.pop("byok", None)
                    payload.pop("model", None)
                    r = await client.post(
                        ASTROLOGY_API_IO_URL_HOSTED,
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                        },
                        json=payload,
                    )
                    if r.status_code != 200:
                        logger.error(f"hosted fallback failed {r.status_code}: {r.text[:500]}")
                        return {"success": False, "message": "Les astres traversent une zone d'ombre. Réessaie dans un instant."}
                else:
                    return {"success": False, "message": "Les astres traversent une zone d'ombre. Réessaie dans un instant."}
            
            data = r.json()

        # ═══════════════════════════════════════════════════════════════════════
        # STEP 7: Extract response (OpenAI-compatible format)
        # ═══════════════════════════════════════════════════════════════════════
        choices = data.get("choices") or []
        if not choices:
            return {"success": False, "message": "Réponse vide des astres."}
        
        response_text = (choices[0].get("message") or {}).get("content", "").strip()
        if not response_text:
            return {"success": False, "message": "Solena a perdu le fil des étoiles. Réessaie."}

        # ═══════════════════════════════════════════════════════════════════════
        # STEP 8: Safeguard - Detect tool leaks
        # ═══════════════════════════════════════════════════════════════════════
        if is_tool_leak(response_text):
            logger.warning(f"[plume_chat] tool leak detected: {response_text[:100]}")
            response_text = (
                "Je perds un instant le fil des astres. Peux-tu me redire "
                "en une phrase ce qui t'a amené(e) à Plume aujourd'hui ?"
            )

        # ═══════════════════════════════════════════════════════════════════════
        # STEP 9: Persist messages (if user authenticated)
        # ═══════════════════════════════════════════════════════════════════════
        if user_id:
            try:
                from services.supabase_client import get_admin_client
                sb = get_admin_client()
                sb.table('plume_chat_messages').insert([
                    {
                        "session_id": session_id,
                        "user_id": user_id,
                        "role": "user",
                        "content": message
                    },
                    {
                        "session_id": session_id,
                        "user_id": user_id,
                        "role": "assistant",
                        "content": response_text
                    },
                ]).execute()
            except Exception as e:
                logger.warning(f"Could not persist messages: {e}")

        # ═══════════════════════════════════════════════════════════════════════
        # STEP 10: Return to frontend
        # ═══════════════════════════════════════════════════════════════════════
        return {"success": True, "answer": response_text, "session_id": session_id}

    except httpx.TimeoutException:
        logger.error("astrology-api.io timeout")
        return {"success": False, "message": "Les astres prennent du temps à répondre. Réessaie dans un instant."}
    except Exception as e:
        logger.error(f"Plume chat error: {e}", exc_info=True)
        return {"success": False, "message": "Une perturbation cosmique empêche la connexion."}
```

---

## 📋 Configuration Files Reference

### Backend - `config.py`

```python
SERVICE_COSTS = {
    'chat_astral': 10,           # 1 Solena question = 10 credits
    'tarot_oui_non': 5,
    'tarot_marseille': 30,
    'theme_natal_pdf': 60,
    # ...
}

PACKS = {
    'initiation': {
        'name': 'Initiation',
        'credits': 15,
        'bonus': 0,
        'amount': 4.99,
        'currency': 'eur',
    },
    'astro_amour': {
        'name': 'Clarté',
        'credits': 50,
        'bonus': 10,
        'amount': 14.99,
        'currency': 'eur',
        'badge': 'Le plus choisi',
    },
    'flammes_jumelles': {
        'name': 'Flammes Jumelles',
        'credits': 100,
        'bonus': 30,
        'amount': 29.99,
        'currency': 'eur',
        'badge': 'Meilleure valeur',
    },
}
```

### Frontend - `lib/solena.js`

```javascript
export const SOLENA = {
  name: 'Solena',
  title: 'Astrologue & guide spirituelle',
  tagline: 'La voix de Plume Astrale',
  bio_short: "Je suis Solena, ta guide chez Plume Astrale...",
  bio_long: [
    "Astrologue, tarologue et médium formée par la tradition...",
    "Ma méthode est holistique...",
    // ...
  ],
  specialities: [
    "Thème natal et carte du ciel personnalisée",
    "Compatibilité amoureuse (synastrie et karmique)",
    "Prévisions par transits et fenêtres de rencontre",
    // ...
  ],
  portrait: asset('brand/solena.png'),  // CDN portrait
  videos: {
    primary: 'https://customer-assets.emergentagent.com/...',
    secondary: 'https://customer-assets.emergentagent.com/...',
  },
};
```

---

## 🔌 Database Schema - Supabase

### Table: `plume_chat_messages`

```sql
CREATE TABLE plume_chat_messages (
  id BIGSERIAL PRIMARY KEY,
  session_id TEXT NOT NULL,          -- Session identifier
  user_id UUID REFERENCES users(id), -- User (nullable for anon)
  role TEXT NOT NULL,                -- 'user' or 'assistant'
  content TEXT NOT NULL,             -- Message text
  created_at TIMESTAMP DEFAULT NOW(),
  
  FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

-- Index for fast retrieval
CREATE INDEX idx_plume_chat_session_id ON plume_chat_messages(session_id);
CREATE INDEX idx_plume_chat_user_id ON plume_chat_messages(user_id);
```

---

## 🔐 Environment Variables

### Backend - `.env`

```env
# ══════════════════════════════════════════════════════════
# Supabase — Storage + Auth
# ══════════════════════════════════════════════════════════
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ0eXAiOiJKV1QiLCJhbGc...
SUPABASE_ANON_KEY=eyJ0eXAiOiJKV1QiLCJhbGc...
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_JWT_ALGORITHM=HS256

# ══════════════════════════════════════════════════════════
# astrology-api.io v3 — LLM + Astrology Tools
# ══════════════════════════════════════════════════════════
ASTROLOGY_API_IO_KEY=sk-astrology-api-io-bearer-token
# Endpoints:
#   BYOK: https://api.astrology-api.io/api/v3/chat/completions/byok (2 credits/turn)
#   HOSTED: https://api.astrology-api.io/api/v3/chat/completions (25 credits/turn)

# ══════════════════════════════════════════════════════════
# OpenAI — BYOK Mode
# ══════════════════════════════════════════════════════════
OPENAI_API_KEY=sk-proj-your-openai-secret-key
# Model: gpt-4o-mini
# Temperature: 0.85
# Max tokens: 1400

# ══════════════════════════════════════════════════════════
# Stripe — Payment Processing
# ══════════════════════════════════════════════════════════
STRIPE_API_KEY=sk_test_... (dev) ou sk_live_... (prod)
```

### Frontend - `.env.local`

```env
REACT_APP_BACKEND_URL=https://api.plume-astrale.fr
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## ✅ Checklist - Modification d'un Aspect

### Pour modifier le SYSTÈME PROMPT:
1. **Fichier**: `backend/services/plume_chat.py` (variable `SYSTEM_PROMPT_SOLENA`)
2. **Impact**: Toutes les réponses futures (immédiat)
3. **Test**: Envoyer un message de test → vérifier le ton/style/hook
4. **Redéploiement**: Redémarrer le backend FastAPI

### Pour changer le MODÈLE LLM:
1. **Fichier**: `backend/services/plume_chat.py` (variable `BYOK_MODEL`)
2. **Exemple**: Changer `gpt-4o-mini` → `gpt-4`
3. **Impact**: Coût OpenAI + performance
4. **Test**: Vérifier latence + qualité réponse

### Pour modifier TEMPÉRATURE ou MAX_TOKENS:
1. **Fichier**: `backend/services/plume_chat.py` (payload construction)
2. **Temperature**: 0 (répétitif) ↔ 1 (créatif) — actuellement 0.85
3. **Max_tokens**: Plus grand = plus long (actuellement 1400)
4. **Impact**: Qualité + latence + coût

### Pour changer les CRÉDITS:
1. **Fichier**: `backend/config.py` (dictionnaire `SERVICE_COSTS`)
2. **Exemple**: `'chat_astral': 10` → `'chat_astral': 15`
3. **Impact**: Pricing pour users
4. **Redéploiement**: Changement immédiat côté backend

### Pour ajouter une QUESTION DE HOOK personnalisée:
**Actuellement**: Généré automatiquement par Solena (prompt-driven)
**Pour forcer**: Ajouter une instruction dans `SYSTEM_PROMPT_SOLENA`
```
# Example modification:
"Termine TOUJOURS avec une des questions suivantes (varier):
- 'Quand tu penses à [topic], est-ce plutôt [option A] ou [option B]?'
- 'Sur une échelle 1-10, où tu te situes sur [dimension]?'"
```

---

## 🚀 Deployment Checklist

- [ ] `.env` variables configurées (Supabase, astrology-api.io, OpenAI)
- [ ] `SYSTEM_PROMPT_SOLENA` finalisé et testé
- [ ] Database schema créé (`plume_chat_messages` table)
- [ ] Frontend `/api/plume-chat` endpoint pointé correctement
- [ ] Stripe packs configurés (si paiements activés)
- [ ] Credit gating en place (frontend + backend)
- [ ] Monitoring logs (check API errors)
- [ ] SSL certificate (production)

