"""
Nouvelles routes astrology-api.io — toutes catégories manquantes
Préfixe : /api/astrology/v3
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

from middleware.auth import get_current_user
from services import astrology_io_service as aio

router = APIRouter(prefix='/astrology/v3', tags=['astrology-v3-extended'])


# ─── Modèles communs ───────────────────────────────────────────────

class PersonInput(BaseModel):
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
    person: Optional[PersonInput] = None


class DuoRequest(BaseModel):
    person1: Optional[PersonInput] = None
    person2: PersonInput


class NameRequest(BaseModel):
    name: str


async def _resolve_person(user_id: str, person: Optional[PersonInput]) -> Optional[dict]:
    """Résout les données natales : données envoyées OU profil utilisateur."""
    if person:
        return person.to_birth_data()
    try:
        from services.wallet_service import get_admin_client
        sb = get_admin_client()
        r = sb.table('profiles').select('*').eq('id', user_id).maybe_single().execute()
        if r and r.data:
            return aio.parse_profile(r.data)
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════════════════════
# ASTROLOGIE VÉDIQUE
# ═══════════════════════════════════════════════════════════════════

@router.post('/vedic/natal')
async def vedic_natal(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Thème natal védique (Kundli) avec Shadbala, Dasha, Ayanamsa."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.vedic_natal(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API védique")
    return result


@router.post('/vedic/nakshatra')
async def vedic_nakshatra(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Nakshatra de naissance (mansion lunaire védique)."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.vedic_nakshatra(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API védique")
    return result


@router.post('/vedic/dasha')
async def vedic_dasha(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Timeline Vimshottari Dasha (10 Mahadashas + sous-périodes)."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.vedic_dasha(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API védique")
    return result


@router.post('/vedic/navamsa')
async def vedic_navamsa(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Chart Navamsa (D9) — mariage & âme."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.vedic_navamsa(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API védique")
    return result


@router.post('/vedic/divisional-charts')
async def vedic_divisional(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """16 charts divisionnels védiques (D1-D60) en un appel."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.vedic_divisional_charts(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API védique")
    return result


# ═══════════════════════════════════════════════════════════════════
# ASTROLOGIE CHINOISE
# ═══════════════════════════════════════════════════════════════════

@router.post('/chinese/zodiac')
async def chinese_zodiac(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Animal du zodiaque chinois + caractéristiques."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.chinese_zodiac(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API chinoise")
    return result


@router.post('/chinese/bazi')
async def chinese_bazi(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """BaZi (4 piliers du destin) — Wu Xing complet."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.chinese_bazi(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API chinoise")
    return result


@router.post('/chinese/elements')
async def chinese_elements(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Wu Xing (5 éléments) — analyse de l'équilibre élémentaire."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.chinese_elements(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API chinoise")
    return result


@router.post('/chinese/zi-wei')
async def chinese_zi_wei(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Zi Wei Dou Shu (Purple Star Astrology) — 108 étoiles."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.zi_wei_dou_shu(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API chinoise")
    return result


@router.post('/chinese/feng-shui')
async def chinese_feng_shui(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Feng Shui — numéro Kua, étoiles volantes, directions favorables."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.feng_shui(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API chinoise")
    return result


@router.post('/chinese/compatibility')
async def chinese_compat(payload: DuoRequest, current_user: dict = Depends(get_current_user)):
    """Compatibilité zodiaque chinois entre 2 personnes."""
    bd1 = await _resolve_person(current_user['id'], payload.person1)
    bd2 = payload.person2.to_birth_data()
    if not bd1 or not bd2:
        raise HTTPException(422, "Données natales requises")
    n1 = (payload.person1.name if payload.person1 else None) or current_user.get('prenom', 'Personne 1')
    n2 = payload.person2.name or 'Personne 2'
    result = await aio.chinese_compatibility(bd1, bd2, n1, n2)
    if not result:
        raise HTTPException(502, "Erreur API chinoise")
    return result


# ═══════════════════════════════════════════════════════════════════
# PRÉDICTIONS AVANCÉES
# ═══════════════════════════════════════════════════════════════════

@router.post('/lunar-return')
async def lunar_return(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Retour Lunaire mensuel."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.lunar_return(bd, name=name)
    if not result:
        raise HTTPException(502, "Erreur API retour lunaire")
    return result


@router.post('/venus-return')
async def venus_return(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Retour de Vénus (amour & finances)."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.venus_return(bd, name=name)
    if not result:
        raise HTTPException(502, "Erreur API retour Vénus")
    return result


@router.post('/progressions')
async def progressions(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Progressions secondaires (jour-pour-année)."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.secondary_progressions(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API progressions")
    return result


@router.post('/profections')
async def profections(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Profections hellénistiques — seigneur de l'année."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.profections(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API profections")
    return result


@router.post('/firdaria')
async def firdaria(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Firdaria (time-lord persan) — cycle de 75 ans."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.firdaria(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API firdaria")
    return result


@router.post('/solar-arc')
async def solar_arc(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Directions solaires (Solar Arc)."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.solar_arc_planets(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API solar arc")
    return result


# ═══════════════════════════════════════════════════════════════════
# TECHNIQUES TRADITIONNELLES
# ═══════════════════════════════════════════════════════════════════

@router.post('/traditional/arabic-parts')
async def arabic_parts(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """97+ Parts arabes (Part de Fortune, Part d'Esprit, etc.)."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.arabic_parts(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API parts arabes")
    return result


@router.post('/traditional/fixed-stars')
async def fixed_stars(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """50+ Étoiles fixes avec influences sur les planètes natales."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.fixed_stars(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API étoiles fixes")
    return result


@router.post('/traditional/dignities')
async def dignities(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Dignités planétaires essentielles."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.dignities(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API dignités")
    return result


@router.post('/traditional/sabian-symbols')
async def sabian_symbols(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """360 Symboles Sabians — image symbolique pour chaque degré planétaire."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.sabian_symbols(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API symboles sabians")
    return result


@router.get('/traditional/planetary-hours')
async def planetary_hours():
    """Heures planétaires du jour (timing traditionnel)."""
    result = await aio.planetary_hours()
    if not result:
        raise HTTPException(502, "Erreur API heures planétaires")
    return result


@router.post('/traditional/midpoints')
async def midpoints(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Points médians (midpoints) + cosmobiologie."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.midpoints(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API midpoints")
    return result


@router.post('/traditional/asteroids')
async def asteroids(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Astéroïdes (Chiron, Cérès, Pallas, Junon, Vesta)."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.asteroids(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API astéroïdes")
    return result


@router.post('/traditional/eclipses')
async def eclipses(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Éclipses proches + impact sur le thème natal."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.eclipse_data(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API éclipses")
    return result


@router.post('/traditional/draconic')
async def draconic(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Chart draconique — thème de l'âme / karmique."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.draconic_chart(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API draconique")
    return result


@router.post('/traditional/human-design')
async def human_design(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Human Design — type, profil, centres, canaux, portes."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.human_design(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API Human Design")
    return result


@router.post('/traditional/kabbalah')
async def kabbalah(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Kabbale — Sephiroth, 72 anges, gématrie."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.kabbalah(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API Kabbale")
    return result


# ═══════════════════════════════════════════════════════════════════
# TAROT AVANCÉ
# ═══════════════════════════════════════════════════════════════════

@router.post('/tarot/birth')
async def tarot_birth(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Tarot de naissance basé sur le thème natal."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.tarot_birth(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API tarot naissance")
    return result


@router.post('/tarot/houses')
async def tarot_houses(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Tarot & 12 maisons astrologiques."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.tarot_houses(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API tarot maisons")
    return result


@router.post('/tarot/transit')
async def tarot_transit(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Tarot synchronisé avec les transits planétaires du jour."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.tarot_transit(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API tarot transit")
    return result


class TarotSpreadRequest(BaseModel):
    spread_type: str = 'celtic_cross'
    question: Optional[str] = None


@router.post('/tarot/spread')
async def tarot_spread(payload: TarotSpreadRequest):
    """15+ tirages professionnels (celtic_cross, three_card, horseshoe…)."""
    result = await aio.tarot_spread(payload.spread_type, payload.question)
    if not result:
        raise HTTPException(502, "Erreur API tirage tarot")
    return result


@router.post('/tarot/synastry')
async def tarot_synastry(payload: DuoRequest, current_user: dict = Depends(get_current_user)):
    """Tarot synastronie — compatibilité entre 2 personnes."""
    bd1 = await _resolve_person(current_user['id'], payload.person1)
    bd2 = payload.person2.to_birth_data()
    if not bd1 or not bd2:
        raise HTTPException(422, "Données natales requises")
    n1 = (payload.person1.name if payload.person1 else None) or current_user.get('prenom', 'Personne 1')
    n2 = payload.person2.name or 'Personne 2'
    result = await aio.tarot_synastry(bd1, bd2, n1, n2)
    if not result:
        raise HTTPException(502, "Erreur API tarot synastrie")
    return result


@router.post('/tarot/tree-of-life')
async def tarot_tree():
    """Tirage sur l'Arbre de Vie Kabbalistique."""
    result = await aio.tarot_tree_of_life()
    if not result:
        raise HTTPException(502, "Erreur API arbre de vie")
    return result


# ═══════════════════════════════════════════════════════════════════
# NUMÉROLOGIE AVANCÉE
# ═══════════════════════════════════════════════════════════════════

@router.post('/numerology/name')
async def numerology_name(payload: NameRequest):
    """Analyse numérologique du prénom/nom."""
    result = await aio.numerology_name(payload.name)
    if not result:
        raise HTTPException(502, "Erreur API numérologie prénom")
    return result


@router.post('/numerology/personal-year')
async def numerology_personal_year(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Année personnelle + cycles de vie."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.numerology_personal_year(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API année personnelle")
    return result


@router.post('/numerology/forecast')
async def numerology_forecast(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Prévision numérologique IA."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.numerology_forecast(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API prévision numérologique")
    return result


@router.post('/numerology/lo-shu')
async def numerology_lo_shu(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Carré Magique Lo Shu — numérologie chinoise."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.numerology_lo_shu(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API Lo Shu")
    return result


@router.post('/numerology/compatibility')
async def numerology_compat(payload: DuoRequest, current_user: dict = Depends(get_current_user)):
    """Compatibilité numérologique entre 2 personnes."""
    bd1 = await _resolve_person(current_user['id'], payload.person1)
    bd2 = payload.person2.to_birth_data()
    if not bd1 or not bd2:
        raise HTTPException(422, "Données natales requises")
    n1 = (payload.person1.name if payload.person1 else None) or current_user.get('prenom', 'Personne 1')
    n2 = payload.person2.name or 'Personne 2'
    result = await aio.numerology_compatibility(bd1, bd2, n1, n2)
    if not result:
        raise HTTPException(502, "Erreur API compatibilité numérologique")
    return result


@router.post('/numerology/kabbalah')
async def kabbalah_numerology(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Numérologie kabbalistique (Gématrie + 72 anges)."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.kabbalah_numerology(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API Kabbale numérologie")
    return result


# ═══════════════════════════════════════════════════════════════════
# INSIGHTS SPÉCIALISÉS
# ═══════════════════════════════════════════════════════════════════

@router.post('/insights/biorhythms')
async def insights_biorhythms(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Biorythmes (physique, émotionnel, intellectuel, intuitif)."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.biorhythms(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API biorythmes")
    return result


@router.post('/insights/moon-wellness')
async def insights_moon_wellness(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Bien-être selon les cycles lunaires."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.moon_wellness(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API bien-être lunaire")
    return result


@router.post('/insights/body-health')
async def insights_body_health(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Santé & corps astral — influences planétaires."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.body_health(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API santé")
    return result


@router.post('/insights/career')
async def insights_career(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Astrologie de carrière — vocation, timing professionnel."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.career_astrology(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API carrière")
    return result


@router.post('/insights/archetypes')
async def insights_archetypes(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """12 archétypes Jungiens depuis le thème natal."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.archetypes_jungian(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API archétypes")
    return result


@router.post('/insights/personality')
async def insights_personality(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Analyse de personnalité astrologique."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.personality_analysis(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API personnalité")
    return result


@router.post('/insights/energy-cycles')
async def insights_energy_cycles(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Cycles d'énergie personnelle — optimisation quotidienne."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.energy_cycles(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API cycles d'énergie")
    return result


# ═══════════════════════════════════════════════════════════════════
# ASTROCARTOGRAPHIE (Ultra+ requis)
# ═══════════════════════════════════════════════════════════════════

@router.post('/astrocartography')
async def astrocartography_map(payload: NatalRequest, current_user: dict = Depends(get_current_user)):
    """Astrocartographie — carte mondiale des zones de puissance planétaire."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.astrocartography(bd, name)
    if not result:
        raise HTTPException(502, "Erreur API astrocartographie")
    return result


class AstrocartoCityRequest(BaseModel):
    person: Optional[PersonInput] = None
    city: str
    country_code: str = 'FR'


@router.post('/astrocartography/city')
async def astrocartography_city(payload: AstrocartoCityRequest, current_user: dict = Depends(get_current_user)):
    """Analyse astrocartographique pour une ville spécifique."""
    bd = await _resolve_person(current_user['id'], payload.person)
    if not bd:
        raise HTTPException(422, "Données natales requises")
    name = (payload.person.name if payload.person else None) or current_user.get('prenom', 'Voyageur')
    result = await aio.astrocartography_city(bd, payload.city, payload.country_code, name)
    if not result:
        raise HTTPException(502, "Erreur API astrocartographie ville")
    return result


# ═══════════════════════════════════════════════════════════════════
# PDF AVANCÉS (Ultra+ + addon)
# ═══════════════════════════════════════════════════════════════════

@router.post('/pdf/synastry')
async def pdf_synastry(payload: DuoRequest, current_user: dict = Depends(get_current_user)):
    """Génère un PDF de compatibilité synastronie (Ultra+ requis)."""
    bd1 = await _resolve_person(current_user['id'], payload.person1)
    bd2 = payload.person2.to_birth_data()
    if not bd1 or not bd2:
        raise HTTPException(422, "Données natales requises")
    n1 = (payload.person1.name if payload.person1 else None) or current_user.get('prenom', 'Partenaire 1')
    n2 = payload.person2.name or 'Partenaire 2'
    pdf_bytes = await aio.pdf_synastry(bd1, bd2, n1, n2)
    if not pdf_bytes:
        raise HTTPException(502, "Erreur génération PDF synastrie")
    return Response(
        content=pdf_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="synastronie-{n1}-{n2}.pdf"'},
    )
