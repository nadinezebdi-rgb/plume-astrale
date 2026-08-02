"""
Chat AI de support client — Plume Astrale.

Endpoint POST /api/chat/support :
  Body: { session_id?: str, message: str, history?: [{role, content}] }
  Response: { reply: str, escalate: bool, session_id: str }

Utilise emergentintegrations (Emergent LLM Key, OpenAI gpt-5.4 par default).
Le modele est instruit avec le contexte Plume Astrale et sait declencher
`escalate=true` si la demande sort de son perimetre.
"""
from __future__ import annotations
import logging
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/chat', tags=['chat'])

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '').strip()
SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'contact@plume-astrale.fr').strip()
CHAT_MODEL_PROVIDER = 'openai'
CHAT_MODEL_NAME = 'gpt-5.4'

SYSTEM_PROMPT = f"""Tu es l'assistante virtuelle de Plume Astrale, un service premium
d'astrologie personnalisée guidé par Soléna. Ton rôle : répondre aux questions
des visiteuses et clientes avec chaleur, clarté et sans jargon.

CONTEXTE PRODUIT :
- Plume Astrale propose des lectures astrologiques personnalisées (thème natal,
  cycles, karmique) pour femmes 35-70 ans.
- L'offre phare est la « Lecture Complète » à 97€ (valeur totale 214€).
  Elle inclut : thème natal décodé, guide de cycles 2026, lecture karmique + arbre
  de vie, analyse des liens, 12 fenêtres favorables, Soléna à tes côtés 90 jours.
- 4 bonus offerts : rituel du soir, carte des liens, calendrier 12 fenêtres, question longue prioritaire.
- Garantie « Clarté ou remboursée » 14 jours, sans avoir à se justifier.
- Paiement sécurisé Stripe (3-D Secure), sans engagement.
- Compte gratuit avec 20 crédits offerts pour tester.
- Livraison des PDFs par email dans les 2h après paiement (souvent en quelques minutes).

RÈGLES DE RÉPONSE :
1. Sois brève (2-4 phrases max sauf si le sujet demande précision).
2. Réponds en français, tutoiement chaleureux (comme Soléna).
3. N'invente jamais de prix, de délais, de garantie ou de fonctionnalité non listée
   ci-dessus. Si tu n'es pas sûre, dis-le et propose l'escalade.
4. Ne prétends jamais être Soléna (humaine). Tu es l'assistante virtuelle.
5. Ne donne pas de conseil médical / psychologique / financier. Rappelle que
   la guidance astrologique est à visée de développement personnel.

QUAND ESCALADER (répondre en préfixant ta réponse par le token [ESCALATE]) :
- Demande de remboursement personnalisée / réclamation
- Problème technique bloquant (paiement, PDF non reçu après 24h)
- Question hors périmètre (partenariat, presse, RGPD, données perso)
- Demande de contact humain / Soléna directe
- Toute situation où tu n'es pas sûre à 80%

Format d'escalade : commence ta réponse par exactement « [ESCALATE] » puis
donne 1 phrase d'accueil + invite à contacter {SUPPORT_EMAIL}.

Exemple non-escalade :
Utilisateur : « C'est quoi la garantie ? »
Toi : « La garantie Clarté ou Remboursée court sur 14 jours après la livraison
de ta lecture. Si tu n'y trouves pas au moins une vraie clarté, tu écris un mot,
on te rembourse intégralement. Aucune justification à donner. »

Exemple escalade :
Utilisateur : « J'ai payé hier et je n'ai rien reçu. »
Toi : « [ESCALATE] Je suis désolée pour ce contretemps — un humain est mieux
placé pour vérifier ta commande. Envoie un mail à {SUPPORT_EMAIL} avec ton
adresse de commande, on te répond dans l'heure. »
"""


class ChatMessage(BaseModel):
    role: str  # user | assistant
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    reply: str
    escalate: bool
    session_id: str
    support_email: str


@router.post('/support', response_model=ChatResponse)
async def chat_support(payload: ChatRequest):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=503, detail='Chat indisponible pour le moment.')
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
    except Exception as e:
        logger.error(f'[chat] import fail: {e}')
        raise HTTPException(status_code=503, detail='Chat indisponible.')

    session_id = payload.session_id or f'sup-{uuid.uuid4().hex[:16]}'
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message=SYSTEM_PROMPT,
    ).with_model(CHAT_MODEL_PROVIDER, CHAT_MODEL_NAME)

    # Rejoue l'historique côté serveur (stateless entre requêtes → on relit tout à chaque tour)
    if payload.history:
        for m in payload.history[-8:]:  # cap 8 derniers messages
            if m.role == 'user':
                try:
                    await chat.send_message(UserMessage(text=m.content[:1000]))
                except Exception as e:
                    logger.warning(f'[chat] history replay fail: {e}')
                    break

    try:
        reply_raw = await chat.send_message(UserMessage(text=payload.message[:1000]))
        reply = (reply_raw or '').strip()
    except Exception as e:
        logger.error(f'[chat] LLM call fail: {e}')
        return ChatResponse(
            reply=f"Je n'arrive pas à te répondre pour le moment. Écris-nous à {SUPPORT_EMAIL}, "
                  "on te répond en quelques heures.",
            escalate=True,
            session_id=session_id,
            support_email=SUPPORT_EMAIL,
        )

    escalate = False
    if reply.startswith('[ESCALATE]'):
        escalate = True
        reply = reply[len('[ESCALATE]'):].strip()

    return ChatResponse(
        reply=reply,
        escalate=escalate,
        session_id=session_id,
        support_email=SUPPORT_EMAIL,
    )
