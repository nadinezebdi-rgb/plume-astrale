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
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()

from middleware.auth import get_optional_user
from services.supabase_client import get_admin_client
from services.app_settings import get_setting, set_setting

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
    exchange_uid: Optional[str] = None


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
        try:
            from services.app_settings import record_llm_call
            record_llm_call('chat_support', tokens_estimate=len(reply) // 3)
        except Exception:
            pass
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

    # Chat analytics : log chaque échange, retour d'un UID stable (safe après troncature)
    exchange_uid = _log_chat_exchange(
        session_id=session_id,
        user_message=payload.message[:1000],
        assistant_reply=reply[:1500],
        escalate=escalate,
    )

    # Slack ping proactif si escalade — fire-and-forget
    if escalate:
        try:
            import asyncio as _asyncio
            _asyncio.create_task(_notify_slack_escalation(
                session_id=session_id,
                user_message=payload.message[:600],
                assistant_reply=reply[:400],
            ))
        except Exception as e:
            logger.warning(f'[chat] escalation notify schedule fail: {e}')

    return ChatResponse(
        reply=reply,
        escalate=escalate,
        session_id=session_id,
        support_email=SUPPORT_EMAIL,
        exchange_uid=exchange_uid,
    )


async def _notify_slack_escalation(session_id: str, user_message: str,
                                   assistant_reply: str) -> None:
    """Slack (best effort) + log_alert quand l'IA escalade une conversation."""
    import httpx as _httpx
    from services.app_settings import log_alert as _log_alert
    webhook = os.environ.get('SLACK_WEBHOOK_URL', '').strip()
    slack_ok = False
    if webhook:
        try:
            async with _httpx.AsyncClient(timeout=6.0) as client:
                r = await client.post(webhook, json={
                    'text': f'🚨 Chat IA escaladé — session {session_id}',
                    'blocks': [
                        {'type': 'header', 'text': {'type': 'plain_text',
                            'text': '🚨 Chat IA — Escalade utilisateur'}},
                        {'type': 'section', 'text': {'type': 'mrkdwn',
                            'text': f'*Message utilisateur*\n>{user_message}\n\n'
                                    f'*Réponse IA*\n>{assistant_reply}\n\n'
                                    f'_Session_ `{session_id}`'}},
                        {'type': 'actions', 'elements': [{
                            'type': 'button',
                            'text': {'type': 'plain_text', 'text': 'Voir analytics'},
                            'url': 'https://plume-astrale.fr/admin',
                            'style': 'primary',
                        }]},
                    ],
                })
                slack_ok = r.status_code in (200, 204)
        except Exception as e:
            logger.warning(f'[chat escalation] slack fail: {e}')
    try:
        _log_alert(
            kind='chat_escalation',
            title=f'Escalade IA — session {session_id[:12]}',
            details=user_message[:180],
            channels=['slack'] if slack_ok else [],
        )
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
# Analytics + FAQ Bridge feedback
# ═══════════════════════════════════════════════════════════════

MAX_LOG_ENTRIES = 500


def _log_chat_exchange(session_id: str, user_message: str, assistant_reply: str,
                       escalate: bool) -> str:
    """Log un échange dans app_settings.chat_analytics (deque bornée).
    Retourne l'exchange_uid stable (persiste malgré la troncature)."""
    entries = get_setting('chat_analytics') or []
    uid = uuid.uuid4().hex[:12]
    entries.append({
        'uid': uid,
        'session_id': session_id,
        'user_message': user_message,
        'assistant_reply': assistant_reply,
        'escalate': bool(escalate),
        'helpful': None,  # sera set via /feedback
        'created_at': datetime.now(timezone.utc).isoformat(),
    })
    # Cap : garde les 500 dernières entrées (uid reste stable)
    if len(entries) > MAX_LOG_ENTRIES:
        entries = entries[-MAX_LOG_ENTRIES:]
    set_setting('chat_analytics', entries)
    return uid


class ChatFeedback(BaseModel):
    session_id: str
    exchange_uid: str
    helpful: bool


@router.post('/feedback')
async def chat_feedback(payload: ChatFeedback):
    """FAQ Bridge : le user clique 👍/👎 sur une réponse IA. On stocke le feedback."""
    entries = get_setting('chat_analytics') or []
    updated = False
    for e in entries:
        if e.get('session_id') == payload.session_id and e.get('uid') == payload.exchange_uid:
            e['helpful'] = bool(payload.helpful)
            e['feedback_at'] = datetime.now(timezone.utc).isoformat()
            updated = True
            break
    if not updated:
        raise HTTPException(status_code=404, detail='Échange introuvable.')
    set_setting('chat_analytics', entries)
    return {'ok': True}


@router.get('/analytics')
async def chat_analytics(current_user: Optional[dict] = Depends(get_optional_user)):
    """Analytics chat — admin only. Renvoie stats agrégées + 50 derniers échanges."""
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    prof = sb.table('profiles').select('is_admin').eq(
        'id', current_user['id']).maybe_single().execute()
    if not prof or not prof.data or not prof.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')

    entries = get_setting('chat_analytics') or []
    total = len(entries)
    escalated = sum(1 for e in entries if e.get('escalate'))
    positive = sum(1 for e in entries if e.get('helpful') is True)
    negative = sum(1 for e in entries if e.get('helpful') is False)
    scored = positive + negative
    helpful_rate = round((positive / scored * 100), 1) if scored else None
    escalate_rate = round((escalated / total * 100), 1) if total else 0.0
    unique_sessions = len({e.get('session_id') for e in entries if e.get('session_id')})

    # Top 10 messages notes negatifs (FAQ gaps)
    gaps: List[Dict[str, Any]] = []
    for e in reversed(entries):
        if e.get('helpful') is False:
            gaps.append({
                'user_message': (e.get('user_message') or '')[:200],
                'assistant_reply': (e.get('assistant_reply') or '')[:200],
                'escalate': bool(e.get('escalate')),
                'created_at': e.get('created_at'),
            })
            if len(gaps) >= 10:
                break

    # Sessions escaladees non encore repondues par Soléna (pour admin reply widget)
    admin_replies = get_setting('chat_admin_replies') or {}
    resolved = get_setting('chat_resolved_escalations') or {}
    escalated_sessions: Dict[str, Dict[str, Any]] = {}
    for e in entries:
        if not e.get('escalate'):
            continue
        sid = e.get('session_id')
        if not sid:
            continue
        # On garde le message le plus recent par session
        existing = escalated_sessions.get(sid)
        if not existing or (e.get('created_at') or '') > (existing.get('created_at') or ''):
            res = resolved.get(sid) or {}
            escalated_sessions[sid] = {
                'session_id': sid,
                'last_user_message': (e.get('user_message') or '')[:400],
                'last_ai_reply': (e.get('assistant_reply') or '')[:300],
                'created_at': e.get('created_at'),
                'admin_replies_count': len(admin_replies.get(sid) or []),
                'last_admin_reply_at': (admin_replies.get(sid) or [{}])[-1].get('at') if admin_replies.get(sid) else None,
                'resolved': bool(res.get('resolved_at')),
                'resolved_at': res.get('resolved_at'),
                'resolved_by': res.get('by'),
            }
    escalations = sorted(escalated_sessions.values(),
                         key=lambda x: x.get('created_at') or '', reverse=True)[:40]

    return {
        'total_exchanges': total,
        'unique_sessions': unique_sessions,
        'escalate_rate_pct': escalate_rate,
        'helpful_rate_pct': helpful_rate,
        'positive_feedback': positive,
        'negative_feedback': negative,
        'faq_gaps': gaps,
        'recent': list(reversed(entries[-50:])),
        'escalations': escalations,
    }


# ═══════════════════════════════════════════════════════════════
# Escalation Reply Widget — Soléna repond depuis l'admin
# ═══════════════════════════════════════════════════════════════

class AdminReplyPayload(BaseModel):
    session_id: str
    message: str = Field(..., min_length=2, max_length=1500)


@router.post('/admin-reply')
async def chat_admin_reply(
    payload: AdminReplyPayload,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Admin poste une reponse humaine dans une session de chat escaladee.
    Le user verra le message apparaitre par polling GET /session-updates."""
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    prof = sb.table('profiles').select('is_admin,email').eq(
        'id', current_user['id']).maybe_single().execute()
    if not prof or not prof.data or not prof.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')

    replies = get_setting('chat_admin_replies') or {}
    entry = {
        'message': payload.message.strip(),
        'author_email': prof.data.get('email'),
        'at': datetime.now(timezone.utc).isoformat(),
    }
    replies.setdefault(payload.session_id, []).append(entry)
    # Cap : garde 20 replies par session, et 200 sessions max
    if len(replies[payload.session_id]) > 20:
        replies[payload.session_id] = replies[payload.session_id][-20:]
    if len(replies) > 200:
        # Drop les sessions les plus anciennes (celles avec last_at le plus ancien)
        sorted_keys = sorted(replies.keys(),
            key=lambda k: (replies[k][-1].get('at') if replies[k] else ''))
        for k in sorted_keys[:len(replies) - 200]:
            replies.pop(k, None)
    set_setting('chat_admin_replies', replies)
    try:
        from services.app_settings import log_alert
        log_alert(
            kind='chat_admin_reply',
            title=f'Reponse humaine envoyee (session {payload.session_id[:12]})',
            details=payload.message.strip()[:180],
            channels=[],
        )
    except Exception:
        pass
    return {'ok': True, 'at': entry['at']}


@router.get('/session-updates')
async def chat_session_updates(session_id: str, since: Optional[str] = None):
    """Public : polling pour recuperer les nouvelles reponses admin dans une session.
    Filtre par 'since' (ISO timestamp) pour ne renvoyer que ce qui est plus recent."""
    replies = get_setting('chat_admin_replies') or {}
    all_msgs = replies.get(session_id) or []
    if since:
        filtered = [m for m in all_msgs if (m.get('at') or '') > since]
    else:
        filtered = list(all_msgs)
    # Format sortie public (masque email admin)
    return {
        'session_id': session_id,
        'messages': [{
            'message': m.get('message'),
            'at': m.get('at'),
            'author': 'Soléna',  # Toujours "Soléna" côté public
        } for m in filtered],
    }


async def _require_admin(current_user: Optional[dict]) -> dict:
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    prof = sb.table('profiles').select('is_admin,email').eq(
        'id', current_user['id']).maybe_single().execute()
    if not prof or not prof.data or not prof.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')
    return prof.data


@router.post('/escalation/{session_id}/resolve')
async def chat_escalation_resolve(
    session_id: str,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Admin : marque une escalade comme resolue (sort de la queue par default)."""
    prof = await _require_admin(current_user)
    resolved = get_setting('chat_resolved_escalations') or {}
    resolved[session_id] = {
        'resolved_at': datetime.now(timezone.utc).isoformat(),
        'by': prof.get('email'),
    }
    set_setting('chat_resolved_escalations', resolved)
    try:
        from services.app_settings import log_alert
        log_alert(
            kind='chat_resolved',
            title=f'Escalade resolue — session {session_id[:12]}',
            details=f'Par {prof.get("email")}',
            channels=[],
        )
    except Exception:
        pass
    return {'ok': True, 'resolved': True, 'session_id': session_id}


@router.post('/escalation/{session_id}/reopen')
async def chat_escalation_reopen(
    session_id: str,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Admin : reouvre une escalade (retour dans la queue)."""
    await _require_admin(current_user)
    resolved = get_setting('chat_resolved_escalations') or {}
    if session_id in resolved:
        resolved.pop(session_id, None)
        set_setting('chat_resolved_escalations', resolved)
    return {'ok': True, 'resolved': False, 'session_id': session_id}
