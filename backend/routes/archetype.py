"""Route : /api/archetype — Ton Archetype (micro-produit viral 4,99€).

Utilise l'endpoint /analysis/archetypes de astrology-api.io v3.
Cout : 15 credits (equivalent 4,99€ dans le pack Initiation).
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.supabase_client import get_admin_client
from services import astrology_io_service as aio

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/archetype', tags=['archetype'])


class ArchetypeRequest(BaseModel):
    force_refresh: Optional[bool] = False


def _require_user(request):
    """Depends helper to extract current user via Supabase JWT.
    Since routes use different auth patterns, we rely on the main server.py's
    `get_current_user` when this router is mounted."""
    pass  # implemented via Depends in mount


# ────────────────────────────────────────────────────────────────
# ARCHETYPE mapping FR (fallback si le champ description est vide)
# ────────────────────────────────────────────────────────────────
_ARCHETYPE_FR = {
    'sage':          {'title': 'Le Sage', 'desc': "Chercheur de vérité, guide par la connaissance."},
    'ruler':         {'title': 'Le Souverain', 'desc': "Batisseur d'ordre, incarnation du leadership serein."},
    'creator':       {'title': "L'Artiste", 'desc': "Chaman de l'imaginaire, celui qui donne forme au réel."},
    'innocent':      {'title': "L'Ame Pure", 'desc': "Coeur ouvert, foi enfantine dans le beau."},
    'explorer':      {'title': 'Le Voyageur', 'desc': "Ame libre en quete d'horizons neufs."},
    'rebel':         {'title': 'Le Rebelle', 'desc': "Briseur de chaines, moteur de renaissance."},
    'lover':         {'title': "L'Amoureux", 'desc': "Chercheur de fusion, mediateur du beau."},
    'hero':          {'title': 'Le Heros', 'desc': "Guerrier interieur, celui qui releve les defis."},
    'magician':      {'title': 'Le Magicien', 'desc': "Alchimiste de la transformation, faiseur de miracles."},
    'jester':        {'title': 'Le Farceur', 'desc': "Ame joyeuse, celui qui reveille par le rire."},
    'caregiver':     {'title': 'Le Gardien', 'desc': "Ame nourriciere, protecteur bienveillant."},
    'everyman':      {'title': "L'Ame Solidaire", 'desc': "Coeur commun, batisseur de liens humains."},
    'orphan':        {'title': "L'Orphelin", 'desc': "Ame en quete d'appartenance, gardien de l'humilite."},
}


def _fr_archetype(key, fallback_title: str = '') -> dict:
    """key peut etre str ou dict — normalise."""
    if isinstance(key, dict):
        name = key.get('name') or key.get('label') or ''
        desc = key.get('description') or ''
        fr = _ARCHETYPE_FR.get((name or '').lower().replace(' ', '').replace('-', '').replace('_', ''), None)
        if fr:
            return {'title': fr['title'], 'description': desc or fr['desc']}
        return {'title': fallback_title or name or "L'Ame libre", 'description': desc}
    k = (key or '').lower().replace(' ', '').replace('-', '').replace('_', '')
    fr = _ARCHETYPE_FR.get(k)
    if fr:
        return {'title': fr['title'], 'description': fr['desc']}
    return {'title': fallback_title or key or "L'Ame libre", 'description': ''}


def _format_result(data: dict, profile: dict) -> dict:
    """Reformate la reponse v3 en un objet lisible pour le frontend."""
    if not data:
        return {'success': False, 'message': 'Reponse vide de l\'API'}

    result = data.get('data', data) if isinstance(data, dict) else data
    profile_name = result.get('profile_name', '')
    balance_type = result.get('balance_type', '')
    dominant = result.get('dominant_archetypes', []) or []
    shadow = result.get('shadow_archetype', '') or ''
    spectrum = result.get('spectrum', {}) or {}
    core_message = result.get('core_message', '') or result.get('description', '')

    # Enrichissement FR
    dominant_fr = []
    for a in dominant[:3]:
        if isinstance(a, dict):
            fr = _fr_archetype(a.get('name', ''), a.get('label', ''))
            dominant_fr.append({
                'name': a.get('name'),
                'title': fr['title'],
                'description': a.get('description') or fr.get('description') or '',
                'score': a.get('score'),
            })
        elif isinstance(a, str):
            fr = _fr_archetype(a)
            dominant_fr.append({'name': a, 'title': fr['title'], 'description': fr.get('description', '')})

    shadow_fr = _fr_archetype(shadow) if shadow else None

    return {
        'success': True,
        'archetype': {
            'prenom': profile.get('prenom') or 'Voyageur',
            'profile_name': profile_name,
            'balance_type': balance_type,
            'dominant': dominant_fr,
            'shadow': shadow_fr,
            'spectrum': spectrum,
            'core_message': core_message,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
        }
    }


def make_router(get_current_user, use_credits_fn):
    """Factory pour eviter les imports circulaires avec server.py."""

    @router.post('/generate')
    async def generate_archetype(
        body: ArchetypeRequest,
        current_user: dict = Depends(get_current_user),
    ):
        """Genere l'analyse archetypale de l'utilisateur (15 credits)."""
        # get_current_user renvoie {id, email, token, claims} — il faut recharger le profil
        try:
            sb = get_admin_client()
            res = sb.table('profiles').select('*').eq('id', current_user['id']).single().execute()
            profile = res.data or {}
        except Exception as e:
            logger.warning(f'Cannot load profile: {e}')
            raise HTTPException(500, 'Impossible de charger ton profil.')

        profile['id'] = current_user['id']
        profile.setdefault('prenom', profile.get('prenom') or 'Voyageur')

        if not profile.get('birth_date') or not profile.get('birth_time'):
            raise HTTPException(400, 'Date et heure de naissance requises. Complete ton profil pour decouvrir ton archetype.')

        birth_data = aio.parse_profile(profile, default_name=profile.get('prenom') or 'Voyageur')
        if not birth_data:
            raise HTTPException(400, 'Impossible de calculer ton archetype avec les donnees actuelles. Verifie ta date et ton heure de naissance.')

        # Deduire les credits (15 = archetype)
        try:
            wallet_result = await use_credits_fn(profile['id'], 'archetype')
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f'use_credits archetype error: {e}')
            raise HTTPException(500, 'Impossible de deduire les credits.')

        # Appel API
        data = await aio.archetypes(birth_data, name=profile.get('prenom') or 'Voyageur', language='fr')
        if not data:
            # Rembourser
            try:
                sb = get_admin_client()
                sb.rpc('add_credits', {
                    'p_user_id': profile['id'],
                    'p_amount': 15,
                    'p_reason': 'archetype_refund',
                }).execute()
            except Exception:
                pass
            raise HTTPException(502, "L'oracle est un instant hors ligne. Tes credits t'ont ete rendus. Reessaie dans quelques minutes.")

        response = _format_result(data, profile)

        # Persister le resultat pour l'utilisateur
        try:
            sb = get_admin_client()
            sb.table('archetype_readings').insert({
                'user_id': profile['id'],
                'result': response.get('archetype'),
                'created_at': datetime.utcnow().isoformat() + 'Z',
            }).execute()
        except Exception as e:
            logger.warning(f'Could not persist archetype reading: {e}')

        response['credit_balance'] = wallet_result.get('credit_balance') if isinstance(wallet_result, dict) else None
        return response

    @router.get('/history')
    async def get_archetype_history(current_user: dict = Depends(get_current_user)):
        """Historique des lectures d'archetypes de l'utilisateur."""
        try:
            sb = get_admin_client()
            res = sb.table('archetype_readings').select('*').eq(
                'user_id', current_user['id']
            ).order('created_at', desc=True).limit(5).execute()
            return {'success': True, 'readings': res.data or []}
        except Exception as e:
            logger.warning(f'archetype history error: {e}')
            return {'success': True, 'readings': []}

    return router