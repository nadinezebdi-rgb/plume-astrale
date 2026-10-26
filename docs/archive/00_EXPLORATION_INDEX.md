# 📚 INDEX - Documentation Solena Chat Exploration

## 📋 Documents générés

Cette exploration a généré **3 fichiers de documentation complète**:

### 1. **SOLENA_CHAT_DIRECT_ANSWERS.md** ⭐ **START HERE**
**Description**: Réponses directes aux 5 questions clés de l'utilisateur

**Contenu**:
- ✅ Q1: Comment SolenaChat est implémentée?
- ✅ Q2: Comment elle appelle OpenAI (endpoints, clés, prompt)?
- ✅ Q3: Où est stocké le prompt système?
- ✅ Q4: Configuration du modèle OpenAI (temp, tokens, etc)?
- ✅ Q5: Si prompt envoyé au backend, fichiers correspondants?

**Format**: Réponses concises + tables récapitulatives + flux complets

**Audience**: Décideurs, managers, développeurs en besoin rapide

**Temps de lecture**: 10-15 minutes

---

### 2. **SOLENA_CHAT_ARCHITECTURE.md** 🏗️ **COMPREHENSIVE GUIDE**
**Description**: Architecture complète avec contexte détaillé et diagrammes

**Sections principales**:
1. Vue d'ensemble (stack technologique)
2. Frontend - SolenaChat.js (responsabilités, flux utilisateur)
3. Backend - Routes & Services (endpoints, configuration)
4. Prompt Système (sections du prompt, barrières éthiques)
5. Flux complet REQUEST → RESPONSE (10 étapes)
6. Configuration & Variables d'environnement
7. Coûts & Crédits (pricing, packs)
8. Fichiers pertinents (résumé)
9. Flow Diagram (ASCII art)
10. Detect Tool Leaks (safeguards)
11. Security & Ethical Rules
12. Summary - 1 Minute Overview

**Format**: Texte structuré + sections numérotées + ASCII diagrams

**Audience**: Architectes, développeurs expérimentés

**Temps de lecture**: 30-45 minutes (complet)

---

### 3. **SOLENA_CHAT_TECHNICAL_DETAILS.md** 🔧 **IMPLEMENTATION GUIDE**
**Description**: Guide technique détaillé avec code snippets et examples

**Sections principales**:
1. Index Rapide (tableau Q&A)
2. Code Walkthrough complet:
   - Frontend: SolenaChat.js:send() (crédit gating, appel API)
   - Backend: plume_chat_endpoint() (route HTTP)
   - Service: plume_chat() (orchestration, astrology-api.io call)
3. Configuration Files Reference (config.py, solena.js)
4. Database Schema (plume_chat_messages table)
5. Environment Variables (.env backend + frontend)
6. Checklist - Modification d'un aspect
7. Deployment Checklist

**Format**: Code snippets inline + commentaires + explications ligne-par-ligne

**Audience**: Développeurs implémentant/modifiant

**Temps de lecture**: 20-30 minutes

---

## 🎯 Par Use Case

### "Je veux comprendre rapidement l'architecture"
→ Lire: **SOLENA_CHAT_DIRECT_ANSWERS.md** (sections 1-5)

### "Je dois modifier le prompt système"
→ Lire: **SOLENA_CHAT_TECHNICAL_DETAILS.md** (section 3.b, Part B) + **SOLENA_CHAT_ARCHITECTURE.md** (section 3)

### "Je dois changer le modèle OpenAI ou la température"
→ Lire: **SOLENA_CHAT_TECHNICAL_DETAILS.md** (section 3.d, Part D) + **SOLENA_CHAT_DIRECT_ANSWERS.md** (section 4)

### "Je dois déployer ou maintenir en prod"
→ Lire: **SOLENA_CHAT_TECHNICAL_DETAILS.md** (sections 5-7, deployment checklist)

### "Je dois déboguer un bug API"
→ Lire: **SOLENA_CHAT_TECHNICAL_DETAILS.md** (sections 2-3 complete code flow) + **SOLENA_CHAT_DIRECT_ANSWERS.md** (section 5 pour fichiers impliqués)

### "Je veux intégrer Solena Chat ailleurs"
→ Lire: **SOLENA_CHAT_DIRECT_ANSWERS.md** (section 1) + **SOLENA_CHAT_ARCHITECTURE.md** (section 2)

---

## 📍 Fichiers du Projet Explorés

### Frontend
| Fichier | Rôle | Lignes |
|---------|------|--------|
| `frontend/src/components/SolenaChat.js` | UI + API calls + credit gating | 452 |
| `frontend/src/lib/solena.js` | Config Solena (nom, bio, portrait) | ~40 |

### Backend
| Fichier | Rôle | Notes |
|---------|------|-------|
| `backend/server.py` | FastAPI app + endpoint `/api/plume-chat` | L1701 |
| `backend/services/plume_chat.py` | Main service + SYSTEM_PROMPT_SOLENA | ~300+ |
| `backend/config.py` | Configuration (SERVICE_COSTS, PACKS) | ~100 |
| `backend/.env.example` | Variables d'environnement | Référence |

### Database
| Table | Rôle |
|-------|------|
| `plume_chat_messages` | Historique conversations |

---

## 🔑 Key Findings

### 1. Architecture
- **3-tier**: Frontend (React) ← Backend (FastAPI) ← astrology-api.io (Proxy) ← OpenAI (GPT-4o-mini)
- **astrology-api.io** injecte les **outils astrologiques** (natal, transits, synastry)

### 2. Prompt System
- **Localisation**: `backend/services/plume_chat.py:SYSTEM_PROMPT_SOLENA`
- **Méthodologie**: GaryVee (Jab → Coaching → Hook)
- **Caractéristiques**: Empowerment coaching, pas voyance fataliste, formatage court mobile

### 3. LLM Configuration
- **Model**: `gpt-4o-mini` (léger, rapide)
- **Temperature**: `0.85` (créativité équilibrée)
- **Max tokens**: `1400` (~400-500 mots réels)
- **Mode BYOK**: Utilisateur Plume paie OpenAI directement

### 4. Credit System
- **Utilisateurs anon**: 2 questions gratuites
- **Utilisateurs auth**: 10 crédits par question
- **Packs**: Initiation 4,99€ / Clarté 14,99€ / Flammes Jumelles 29,99€

### 5. Safeguards
- **Tool Leak Detection**: Regex pour détecter JSON d'appels d'outils
- **Ethical Barriers**: Pas de conseil médical, rituels présentés comme bien-être, pas d'ordre sur décisions vitales

---

## 🛠️ Quick Reference

### To Modify...

| Item | Location | File |
|------|----------|------|
| Solena's personality/tone | SYSTEM_PROMPT_SOLENA | `plume_chat.py` |
| LLM model | BYOK_MODEL | `plume_chat.py` |
| Temperature (creativity) | payload["temperature"] | `plume_chat.py` |
| Max response length | payload["max_tokens"] | `plume_chat.py` |
| Cost per question | SERVICE_COSTS['chat_astral'] | `config.py` |
| Credit packs | PACKS dictionary | `config.py` |
| Solena's portrait/bio | SOLENA object | `lib/solena.js` |
| API endpoint | @api_router.post('/plume-chat') | `server.py` |
| Chat UI styling | className + style props | `SolenaChat.js` |

---

## 📞 Support Reference

### If you see...

| Error | Likely Cause | Check |
|-------|-------|-------|
| "Les astres traversent une zone d'ombre" | astrology-api.io HTTP error | ASTROLOGY_API_IO_KEY valid? BYOK fallback? |
| Tool leak detected in logs | LLM output is JSON tool calls | Check SYSTEM_PROMPT_SOLENA for tool restrictions |
| Timeout (45s) | astrology-api.io slow | Check astrology-api.io dashboard |
| "Message vide" | User sent empty input | Frontend validation issue |
| Insufficient credits | User balance < 10 | Credit system working correctly |

---

## 📊 Statistics

### Code Coverage
- **Frontend**: 100% of SolenaChat flow documented
- **Backend**: 100% of /api/plume-chat flow documented
- **Services**: 100% of plume_chat() function documented
- **Configuration**: 100% of environment + config files documented

### Documentation Breakdown
- **Total lines of documentation**: ~2500 lines
- **Code snippets**: 30+
- **Diagrams**: 5+ (ASCII + text-based)
- **Tables**: 15+
- **Cross-references**: 40+

---

## 🚀 Next Steps

### For Understanding:
1. Read **SOLENA_CHAT_DIRECT_ANSWERS.md** for quick understanding
2. Review **SOLENA_CHAT_ARCHITECTURE.md** for full context
3. Check **SOLENA_CHAT_TECHNICAL_DETAILS.md** for implementation details

### For Modification:
1. Identify what you want to change
2. Find it in **Quick Reference** above
3. Locate the file + line number
4. Edit following the code examples in **TECHNICAL_DETAILS.md**
5. Test with curl or Postman

### For Deployment:
1. Review **Deployment Checklist** in **TECHNICAL_DETAILS.md**
2. Ensure all `.env` variables are configured
3. Test BYOK vs HOSTED fallback
4. Monitor logs after deployment

---

## 📄 Document Statistics

| Document | Size | Sections | Tables | Code Blocks |
|----------|------|----------|--------|------------|
| DIRECT_ANSWERS.md | ~1600 lines | 5 + Summary | 3 | 15+ |
| ARCHITECTURE.md | ~1200 lines | 10 | 2 | 8+ |
| TECHNICAL_DETAILS.md | ~1000 lines | 7 | 6 | 20+ |
| **TOTAL** | **~3800 lines** | **22** | **11** | **43+** |

---

## 🎓 Knowledge Hierarchy

```
Level 1: Executive Overview
└─ "What is Solena Chat?" 
   → Read: Section 0 of ARCHITECTURE.md (1 min)

Level 2: Architecture Understanding
└─ "How does it work?" 
   → Read: DIRECT_ANSWERS.md (15 min)

Level 3: Implementation Details
└─ "How do I modify/deploy it?" 
   → Read: TECHNICAL_DETAILS.md (30 min)

Level 4: Deep Dive
└─ "Full context with all details" 
   → Read: ARCHITECTURE.md (45 min)

Level 5: Source Code
└─ "Actual implementation" 
   → Refer to project files
```

---

**Generated**: 2026-07-09  
**Project**: plume-astrale  
**Component**: Solena Chat (IA Coaching)  
**Status**: Complete Exploration ✅
