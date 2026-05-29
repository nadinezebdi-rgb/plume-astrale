"""Endpoints v3 utilisant astrology-api.io (Swiss Ephemeris) pour:
- Theme natal precis (positions, cuspides, aspects)
- Synastrie / Compatibilite (4 types: amour, amitie, famille, travail)
- Metriques lunaires (phase, signe, mansion)

Tous les endpoints sont prefixes /api/astrology/v3 pour ne pas casser les anciens.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List

from middleware.auth import get_current_user
from services import astrology_io_service as aio
from services import wallet_service
from services.share_card_generator import generate_synastry_card


router = APIRouter(prefix='/astrology/v3', tags=['astrology-v3'])


# ─── Modeles requete ────────────────────────────────────────────────

class PersonInput(BaseModel):
    """Donnees natales d'une personne pour les endpoints v3."""
    name: Optional[str] = 'Voyageur'
    year: int
    month: int
    day: int
    hour: int = 12
    minute: int = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    country_code: Optional[str] = None

    def to_birth_data(self) -> dict:
        return aio.make_birth_data(
            self.year, self.month, self.day, self.hour, self.minute,
            latitude=self.latitude, longitude=self.longitude,
            city=self.city, country_code=self.country_code,
        )


class NatalRequest(BaseModel):
    person: Optional[PersonInput] = None  # si None et user connecte -> utilise son profil


class SynastryRequest(BaseModel):
    """Compatibilite entre 2 personnes.
    relationship_type: love | friendship | family | work
    person1 est optionnel si l'utilisateur est connecte (on prend son profil).
    """
    person1: Optional[PersonInput] = None
    person2: PersonInput
    relationship_type: str = 'love'  # love | friendship | family | work


# ─── Helpers ────────────────────────────────────────────────────────

_RELATIONSHIP_LABELS = {
    'love': 'amour',
    'friendship': 'amitié',
    'family': 'famille',
    'work': 'travail',
}


def _interpret_score(score: int, rel_type: str) -> dict:
    """Convertit un score 0-100 en label + couleur + description francaise."""
    rel_fr = _RELATIONSHIP_LABELS.get(rel_type, 'relation')
    if score >= 90:
        return {
            'level': 'Connexion Rare' if rel_type != 'love' else 'Flamme Jumelle',
            'color': 'text-pink-400',
            'description': f"Une {rel_fr} cosmique exceptionnelle. Vos ames vibrent en harmonie naturelle.",
        }
    if score >= 80:
        return {
            'level': 'Ames Soeurs',
            'color': 'text-emerald-400',
            'description': f"Une {rel_fr} fluide et profonde. Vous vous comprenez sans mots.",
        }
    if score >= 70:
        return {
            'level': 'Belle Alchimie',
            'color': 'text-[#C5A059]',
            'description': f"Une {rel_fr} riche et stimulante. Des differences qui enrichissent.",
        }
    if score >= 60:
        return {
            'level': 'Connexion Possible',
            'color': 'text-blue-400',
            'description': f"Une {rel_fr} viable avec ecoute et volonte commune.",
        }
    if score >= 50:
        return {
            'level': 'Travail Necessaire',
            'color': 'text-amber-400',
            'description': f"Une {rel_fr} qui demande des efforts mutuels pour s'epanouir.",
        }
    return {
        'level': 'Defi Karmique',
        'color': 'text-red-400',
        'description': f"Une {rel_fr} intense d'apprentissage. Des lecons profondes a integrer.",
    }


def _extract_score(api_response: dict) -> Optional[int]:
    """Extrait un score 0-100 de la reponse synastry/compatibility."""
    if not api_response:
        return None
    # Plusieurs formats possibles selon l'endpoint
    candidates = [
        api_response.get('overall_score'),
        api_response.get('compatibility_score'),
        api_response.get('score'),
        (api_response.get('summary') or {}).get('score'),
        (api_response.get('summary') or {}).get('overall_score'),
        ((api_response.get('analysis') or {}).get('overall') or {}).get('score'),
    ]
    for c in candidates:
        if c is None:
            continue
        try:
            v = float(c)
            return max(0, min(100, int(round(v if v > 1 else v * 100))))
        except (TypeError, ValueError):
            continue
    return None


def _summarize_aspects(aspects: list, max_n: int = 5) -> list:
    """Resume les aspects significatifs en francais."""
    if not aspects:
        return []
    # Tri par strength desc si disponible
    sorted_a = sorted(
        [a for a in aspects if isinstance(a, dict)],
        key=lambda a: a.get('strength') or a.get('orb_value') or 0,
        reverse=True,
    )
    out = []
    for a in sorted_a[:max_n]:
        p1 = a.get('point_1') or a.get('planet_1') or a.get('first_planet') or ''
        p2 = a.get('point_2') or a.get('planet_2') or a.get('second_planet') or ''
        aspect = a.get('aspect_name') or a.get('aspect') or a.get('type') or ''
        orb = a.get('orb') or a.get('orb_value')
        out.append({
            'planet_1': p1, 'planet_2': p2, 'aspect': aspect,
            'orb': round(float(orb), 2) if orb is not None else None,
            'description': a.get('description') or a.get('interpretation'),
        })
    return out


async def _resolve_person1(user_id: str, person1: Optional[PersonInput]) -> Optional[dict]:
    """Renvoie un birth_data v3 : depuis person1 si fourni, sinon depuis le profil de l'utilisateur."""
    if person1:
        return person1.to_birth_data()
    profile = await wallet_service.get_profile(user_id)
    return aio.parse_profile(profile)


# ─── Endpoints ──────────────────────────────────────────────────────

@router.post('/natal')
async def natal_v3(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Theme natal complet (positions, cuspides, aspects) via Swiss Ephemeris."""
    bd = None
    name = 'Voyageur'
    if payload.person:
        bd = payload.person.to_birth_data()
        name = payload.person.name or name
    else:
        profile = await wallet_service.get_profile(current_user['id'])
        bd = aio.parse_profile(profile)
        name = profile.get('prenom') or name
    if not bd:
        raise HTTPException(status_code=400, detail='Donnees natales incompletes (date, heure et lieu requis).')

    chart = await aio.natal_chart(bd, name=name, language='fr')
    if not chart:
        raise HTTPException(status_code=502, detail='Service astrologique indisponible.')
    return {'success': True, 'data': chart, 'name': name}


@router.post('/positions')
async def positions_v3(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    bd = payload.person.to_birth_data() if payload.person else aio.parse_profile(
        await wallet_service.get_profile(current_user['id'])
    )
    if not bd:
        raise HTTPException(status_code=400, detail='Donnees natales incompletes.')
    name = (payload.person.name if payload.person else None) or 'Voyageur'
    data = await aio.get_positions(bd, name=name, language='fr')
    if not data:
        raise HTTPException(status_code=502, detail='Service astrologique indisponible.')
    return {'success': True, 'data': data}


@router.post('/lunar')
async def lunar_v3(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Metriques lunaires precises : phase, signe, mansion."""
    bd = payload.person.to_birth_data() if payload.person else aio.parse_profile(
        await wallet_service.get_profile(current_user['id'])
    )
    if not bd:
        raise HTTPException(status_code=400, detail='Donnees natales incompletes.')
    data = await aio.get_lunar_metrics(bd, language='fr')
    if not data:
        raise HTTPException(status_code=502, detail='Service astrologique indisponible.')
    return {'success': True, 'data': data}


@router.post('/synastry')
async def synastry_v3(payload: SynastryRequest, current_user: dict = Depends(get_current_user)):
    """Compatibilite entre 2 personnes pour 4 types de relations (love/friendship/family/work).
    Renvoie un score 0-100 + interpretation francaise + aspects cles.
    """
    rel_type = payload.relationship_type if payload.relationship_type in _RELATIONSHIP_LABELS else 'love'

    bd1 = await _resolve_person1(current_user['id'], payload.person1)
    if not bd1:
        raise HTTPException(status_code=400, detail='Donnees natales du premier partenaire incompletes.')
    bd2 = payload.person2.to_birth_data()

    name1 = (payload.person1.name if payload.person1 else None) or 'Vous'
    name2 = payload.person2.name or 'Partenaire'

    # Paywall : 20cr (offert si Premium)
    charge_info_syn = await wallet_service.charge_or_premium(
        current_user['id'], 'synastrie', 20, f'Synastrie {rel_type}',
    )

    # 1. Score de compatibilite (numerique)
    score_data = await aio.relationship_compatibility_score(bd1, bd2, name1, name2, 'fr')
    score = _extract_score(score_data) if score_data else None

    # 2. Synastry chart complet (aspects entre les deux themes)
    synastry = await aio.synastry_chart(bd1, bd2, name1, name2, 'fr')

    # Fallback si l'API echoue completement
    if not score_data and not synastry:
        # Refund si echec API
        if charge_info_syn.get('charged'):
            try:
                await wallet_service.add_credits(current_user['id'], 20, 'Remboursement Synastrie (echec API)', tx_type='refund')
            except Exception:
                pass
        raise HTTPException(status_code=502, detail='Service astrologique indisponible.')

    # Score deduit du synastry si pas de score direct
    if score is None and synastry:
        score = _extract_score(synastry) or 65  # neutre par defaut

    if score is None:
        score = 65

    # Ajustement contextuel par type de relation : on conserve la base mais on adapte le label
    interp = _interpret_score(score, rel_type)

    # Extraire les aspects cles
    aspects_raw = []
    if isinstance(synastry, dict):
        aspects_raw = synastry.get('aspects') or (synastry.get('synastry_aspects') or [])
    key_aspects = _summarize_aspects(aspects_raw, max_n=6)

    return {
        'success': True,
        'relationship_type': rel_type,
        'relationship_label': _RELATIONSHIP_LABELS[rel_type],
        'name_1': name1,
        'name_2': name2,
        'score': score,
        'level': interp['level'],
        'color': interp['color'],
        'description': interp['description'],
        'aspects': key_aspects,
        'raw_score_data': score_data,
        'raw_synastry': synastry,
    }


class SynastryCardRequest(BaseModel):
    name_1: str = 'Vous'
    name_2: str = 'Partenaire'
    score: int
    level: Optional[str] = 'Belle Alchimie'
    relationship_type: Optional[str] = 'love'


@router.post('/synastry/share-card')
async def synastry_share_card(payload: SynastryCardRequest):
    """Genere une carte PNG 1080x1080 partageable (Instagram/WhatsApp) avec le score
    et les prenoms. Endpoint public (aucune donnee sensible)."""
    try:
        png = generate_synastry_card(
            payload.name_1, payload.name_2,
            int(payload.score), payload.level or '',
            payload.relationship_type or 'love',
        )
        return Response(
            content=png,
            media_type='image/png',
            headers={
                'Content-Disposition': f'attachment; filename="synastrie_{payload.name_1}_{payload.name_2}.png"',
                'Cache-Control': 'no-store',
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erreur generation carte: {e}')


@router.post('/natal/pdf')
async def natal_pdf_v3(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Genere un PDF complet du theme natal (chart wheel + interpretations en francais).
    Tarif : 20 credits (offert si Premium actif). Si person n'est pas fourni, utilise le profil.
    """
    bd = None
    name = 'Voyageur'
    if payload.person:
        bd = payload.person.to_birth_data()
        name = payload.person.name or name
    else:
        profile = await wallet_service.get_profile(current_user['id'])
        bd = aio.parse_profile(profile)
        name = profile.get('prenom') or name
    if not bd:
        raise HTTPException(status_code=400, detail='Donnees natales incompletes (date, heure et lieu requis).')

    # Paywall
    await wallet_service.charge_or_premium(
        current_user['id'], 'theme_natal_pdf', 20, 'Theme Natal PDF',
    )

    pdf = await aio.natal_report_pdf(bd, name=name, language='fr', chart_theme='dark')
    if not pdf:
        # Refund si echec API
        try:
            await wallet_service.add_credits(current_user['id'], 20, 'Remboursement Theme Natal PDF (echec API)', tx_type='refund')
        except Exception:
            pass
        raise HTTPException(status_code=502, detail='Service astrologique indisponible (PDF).')
    return Response(
        content=pdf,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="theme_natal_{name}.pdf"',
            'Cache-Control': 'no-store',
        },
    )


# ─── SOLAR RETURN (Revolution Solaire — rapport annuel d'anniversaire) ─────

class SolarReturnRequest(BaseModel):
    person: Optional[PersonInput] = None
    return_year: Optional[int] = None  # default: prochain anniversaire


@router.post('/solar-return')
async def solar_return_v3(payload: SolarReturnRequest, current_user: dict = Depends(get_current_user)):
    """Rapport de Revolution Solaire : themes astrologiques pour l'annee a venir
    (de votre prochain anniversaire au suivant). Produit premium type 'rituel annuel'.
    """
    from datetime import datetime as _dt
    bd = None
    name = 'Voyageur'
    if payload.person:
        bd = payload.person.to_birth_data()
        name = payload.person.name or name
    else:
        profile = await wallet_service.get_profile(current_user['id'])
        bd = aio.parse_profile(profile)
        name = profile.get('prenom') or name
    if not bd:
        raise HTTPException(status_code=400, detail='Donnees natales incompletes (date, heure et lieu requis).')

    # Annee de revolution : par defaut, prochain anniversaire (annee courante ou suivante)
    ret_year = payload.return_year
    if not ret_year:
        today = _dt.now()
        birth_month = bd.get('month')
        birth_day = bd.get('day')
        if birth_month and birth_day:
            if (today.month, today.day) >= (int(birth_month), int(birth_day)):
                ret_year = today.year + 1
            else:
                ret_year = today.year
        else:
            ret_year = today.year + 1

    chart = await aio.solar_return(bd, ret_year, name=name, language='fr')
    report = await aio.solar_return_report(bd, ret_year, name=name, language='fr')
    if not chart and not report:
        raise HTTPException(status_code=502, detail='Service astrologique indisponible.')

    # Paywall apres succes : 20cr (offert si Premium)
    await wallet_service.charge_or_premium(
        current_user['id'], 'revolution_solaire', 20, f'Revolution Solaire {ret_year}',
    )

    return {
        'success': True,
        'return_year': ret_year,
        'name': name,
        'chart': chart,
        'report': report,
    }


# ─── TRANSITS DU JOUR ─────────────────────────────────────────────────────

@router.post('/transits/today')
async def transits_today_v3(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Transits planetaires du jour appliques au theme natal.
    Renvoie chart + rapport textuel pour rituel quotidien / notification push.
    """
    bd = payload.person.to_birth_data() if payload.person else aio.parse_profile(
        await wallet_service.get_profile(current_user['id'])
    )
    if not bd:
        raise HTTPException(status_code=400, detail='Donnees natales incompletes.')
    name = (payload.person.name if payload.person else None) or 'Voyageur'

    chart = await aio.transits_today(bd, name=name, language='fr')
    report = await aio.transit_report_today(bd, name=name, language='fr')
    if not chart and not report:
        raise HTTPException(status_code=502, detail='Service astrologique indisponible.')
    return {
        'success': True,
        'chart': chart,
        'report': report,
    }


# ─── LOVE LANGUAGES ───────────────────────────────────────────────────────

@router.post('/love-languages')
async def love_languages_v3(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Langages de l'amour astrologiques selon Venus, Mars, Lune et leurs aspects.
    Renvoie un langage principal + langages secondaires + conseils.
    """
    bd = None
    name = 'Voyageur'
    if payload.person:
        bd = payload.person.to_birth_data()
        name = payload.person.name or name
    else:
        profile = await wallet_service.get_profile(current_user['id'])
        bd = aio.parse_profile(profile)
        name = profile.get('prenom') or name
    if not bd:
        raise HTTPException(status_code=400, detail='Donnees natales incompletes.')

    data = await aio.love_languages(bd, name=name, language='fr')
    if not data:
        raise HTTPException(status_code=502, detail='Service astrologique indisponible.')

    # Paywall : 10cr (offert si Premium)
    await wallet_service.charge_or_premium(
        current_user['id'], 'love_languages', 10, "Langages d'Amour",
    )

    return {'success': True, 'data': data, 'name': name}


# ─── CHAT ASTROLOGIQUE V3 (avec contexte natal natif) ────────────────────

class AstroChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    history: Optional[List[dict]] = None  # [{'role':'user'|'assistant', 'content':...}]


@router.post('/chat')
async def astro_chat_v3(payload: AstroChatRequest, current_user: dict = Depends(get_current_user)):
    """Chat AI astrologique : l'IA accede directement au theme natal de l'utilisateur
    pour repondre avec precision (positions, transits, aspects). Plus pertinent que GPT generique.
    """
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail='Message vide.')

    # Paywall : 3cr par question (offert si Premium)
    charge_info = await wallet_service.charge_or_premium(
        current_user['id'], 'chat_astral', 3, 'Chat astrologique - 1 question',
    )

    profile = await wallet_service.get_profile(current_user['id'])
    bd = aio.parse_profile(profile)
    name = profile.get('prenom') or 'Voyageur'

    # Construire l'historique de la conversation
    messages = [
        {
            'role': 'system',
            'content': (
                "Tu es Plume, guide astrologique francaise chaleureuse et poetique. Reponds en francais, "
                "avec finesse, jamais de jargon excessif. Utilise le theme natal fourni pour personnaliser. "
                "Style : phrases courtes, metaphores lumineuses, registre tutoiement bienveillant."
            ),
        }
    ]
    if payload.history:
        for m in payload.history[-10:]:  # dernieres 10 interactions max
            if m.get('role') in ('user', 'assistant') and m.get('content'):
                messages.append({'role': m['role'], 'content': m['content']})
    messages.append({'role': 'user', 'content': payload.message.strip()})

    session = payload.session_id or f'plume-{current_user["id"][:8]}'
    response = await aio.astro_chat(
        messages=messages,
        birth_data=bd,
        name=name,
        session_id=session,
        language='fr',
    )
    if not response:
        # Refund si echec API (l'utilisateur ne paie pas pour rien)
        if charge_info.get('charged'):
            try:
                await wallet_service.add_credits(current_user['id'], 3, 'Remboursement chat (echec API)', tx_type='refund')
            except Exception:
                pass
        raise HTTPException(status_code=502, detail='Service de chat astrologique indisponible.')

    # Extraire la reponse (format OpenAI-compatible)
    reply_text = ''
    try:
        choices = response.get('choices') or []
        if choices and isinstance(choices, list):
            reply_text = (choices[0].get('message') or {}).get('content', '') or ''
    except Exception:
        pass
    if not reply_text:
        reply_text = str(response)[:500]

    return {
        'success': True,
        'reply': reply_text,
        'session_id': session,
        'charged': charge_info.get('amount', 0),
        'is_premium': charge_info.get('is_premium', False),
    }
