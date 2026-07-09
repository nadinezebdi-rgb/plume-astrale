"""Energie actuelle — calcule 4 sections du jour (dominante, relationnel, attention, opportunité)
en combinant transits planetaires actuels + lune transitante + theme natal de l'utilisateur.
Cache par user/jour pour eviter de spammer le LLM."""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
import os

from services.supabase_client import get_admin_client
from services import astrology_io_service as aio

logger = logging.getLogger(__name__)

ENERGY_SYSTEM_PROMPT = """Tu es Plume, la guide spirituelle de Plume Astrale.
Tu produis chaque jour une lecture energetique du jour pour un utilisateur, basee sur :
- son theme natal (signe solaire, lunaire, ascendant, planetes)
- la position planetaire actuelle du jour (transits)
- la phase lunaire et le signe transite par la Lune

Genere une lecture STRUCTUREE en EXACTEMENT 4 sections, chacune courte (2 phrases maximum) :

1. **Energie dominante** : la couleur energetique du jour (transformation, ouverture, introspection, action, ressourcement, etc.)
2. **Relationnel** : ce qui se joue dans tes liens aujourd'hui (clarification, distance, douceur, tension constructive...)
3. **Attention** : ce a quoi etre vigilant·e (decision impulsive, paroles trop vives, sur-engagement, fatigue emotionnelle...)
4. **Opportunite** : ce que cette journee offre (intuition affutee, clarte, rencontre symbolique, geste a poser...)

Style :
- 2eme personne du singulier (tu / ton / ta / tes), francais soutenu mais accessible
- Pas de signe astro nomme directement (parle de "l'energie", "ton ciel", "cette journee")
- Concret, jamais vague type "tu vas vivre quelque chose"
- Toujours emotionnel et incarne
- Aucun emoji
- N'utilise pas le mot "intelligence" ni "IA"

Format de sortie : JSON strict, rien d'autre :
{
  "dominante": {"label": "...", "text": "..."},
  "relationnel": {"label": "...", "text": "..."},
  "attention": {"label": "...", "text": "..."},
  "opportunite": {"label": "...", "text": "..."}
}

Le "label" est UN seul mot (ex: "Transformation", "Clarification", "Vigilance", "Intuition").
Le "text" fait 2 phrases.
"""


def _today_key() -> str:
    return datetime.now(timezone.utc).date().isoformat()


async def get_energy_today(user_id: str, birth_data: Dict[str, Any]) -> Dict[str, Any]:
    """Retourne l'energie du jour pour cet utilisateur. Cache par user/jour."""
    sb = get_admin_client()
    today = _today_key()

    # Cache check
    try:
        cache = sb.table('energy_cache').select('payload').eq('user_id', user_id).eq('day', today).maybe_single().execute()
        if cache and cache.data and cache.data.get('payload'):
            return {'success': True, 'cached': True, 'date': today, **cache.data['payload']}
    except Exception:
        pass  # table peut-etre absente

    # Recuperer le contexte natal succint via astrology-api.io v3
    try:
        bd = str(birth_data.get('birth_date'))[:10]
        bt = str(birth_data.get('birth_time') or '12:00')[:5]
        y, m, d = bd.split('-')
        h, mn = bt.split(':')
        bd_v3 = aio.make_birth_data(
            int(y), int(m), int(d), int(h), int(mn),
            latitude=float(birth_data.get('latitude')) if birth_data.get('latitude') is not None else None,
            longitude=float(birth_data.get('longitude')) if birth_data.get('longitude') is not None else None,
        )
        natal = await aio.natal_chart(bd_v3, name=birth_data.get('prenom') or 'Voyageur', language='fr')
        natal_summary = _summarize_natal(natal)
    except Exception as e:
        logger.warning(f'Cannot get natal: {e}')
        natal_summary = 'Donnees natales partielles.'

    # Contexte du jour : date, phase lunaire approximative
    now = datetime.now(timezone.utc)
    day_context = f"Date du jour : {now.strftime('%d/%m/%Y')}. Jour de la semaine : {['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche'][now.weekday()]}."

    prompt = f"""CONTEXTE NATAL DE L'UTILISATEUR :
{natal_summary}

CONTEXTE DU JOUR :
{day_context}

Genere maintenant l'energie du jour en JSON strict (4 sections : dominante, relationnel, attention, opportunite)."""

    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        return {'success': False, 'message': 'Service indisponible'}

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f'energy-{user_id}-{today}',
            system_message=ENERGY_SYSTEM_PROMPT,
        ).with_model('openai', 'gpt-4o-mini')
        raw = await chat.send_message(UserMessage(text=prompt))

        # Parser le JSON
        import json, re
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if not json_match:
            raise ValueError(f'No JSON found in response: {raw[:200]}')
        payload = json.loads(json_match.group(0))

        # Cache result
        try:
            sb.table('energy_cache').upsert({
                'user_id': user_id, 'day': today, 'payload': payload,
            }).execute()
        except Exception as e:
            logger.warning(f'Cache save failed: {e}')

        return {'success': True, 'cached': False, 'date': today, **payload}
    except Exception as e:
        logger.error(f'energy generation error: {e}', exc_info=True)
        return {'success': False, 'message': "L'energie d'aujourd'hui ne peut etre lue. Reessaie plus tard."}


def _summarize_natal(natal: Optional[Dict[str, Any]]) -> str:
    """Resume textuel du theme natal pour le prompt (format v3 astrology-api.io)."""
    if not natal:
        return 'Theme natal indisponible.'
    parts = []
    planets = aio.extract_planets(natal)

    for k, label in (('sun', 'Sun'), ('moon', 'Moon')):
        p = planets.get(k)
        if p and p.get('sign'):
            parts.append(f'{label} en {p.get("sign")} maison {p.get("house") or "?"}')

    asc_sign = aio.extract_ascendant_sign_en(natal)
    if asc_sign:
        parts.append(f'Ascendant {asc_sign}')

    for k, label in (('mercury', 'Mercury'), ('venus', 'Venus'), ('mars', 'Mars')):
        p = planets.get(k)
        if p and p.get('sign'):
            parts.append(f'{label} en {p.get("sign")}')

    return ' · '.join(parts) if parts else 'Theme natal partiel.'
