"""
Orchestrateur d'enrichissement du PDF Synastrie (Option A du user).

Pour 8 pages cles, on genere du contenu personnalise via :
1. astrology-api.io v3 -> positions natales + aspects + score compatibilite
2. GPT-4o-mini via Emergent LLM Key -> texte narratif de 200-350 mots par page

Pages enrichies : 3, 4, 5, 6, 7, 8, 9, 11, 12, 22
Pages statiques (inchangees) : 1, 2, 10, 13-21, 23-25

Coût estime par rapport : ~0.02€ (10 LLM calls x ~500 tokens)
Temps genere : ~15-25s (parallel où possible)
"""
import os
import asyncio
import logging
from typing import Any, Dict, List, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
from services.astrology_io_service import (
    make_birth_data, get_positions, synastry_chart,
    relationship_compatibility_score,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# 1. Fetch data astrologique
# ═══════════════════════════════════════════════════════════
def _parse_birth(person: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Convertit person dict -> birth_data v3."""
    bd = person.get('birth_date')
    bt = person.get('birth_time') or '12:00'
    if not bd:
        return None
    try:
        y, m, d = str(bd)[:10].split('-')
        h, mn = str(bt)[:5].split(':')
        return make_birth_data(
            int(y), int(m), int(d), int(h), int(mn),
            latitude=person.get('latitude'),
            longitude=person.get('longitude'),
            city=(person.get('birth_place') or '').split(',')[0].strip() or None,
        )
    except Exception as e:
        logger.warning(f'[enrich] parse birth: {e}')
        return None


async def fetch_astro_data(p1: Dict[str, Any], p2: Dict[str, Any]) -> Dict[str, Any]:
    """Recupere positions + synastrie + score. Best-effort : retourne dict partiel si erreur."""
    bd1 = _parse_birth(p1)
    bd2 = _parse_birth(p2)
    n1 = (p1.get('prenom') or 'Personne 1').strip()
    n2 = (p2.get('prenom') or 'Personne 2').strip()

    data: Dict[str, Any] = {'p1_name': n1, 'p2_name': n2}
    if not bd1 or not bd2:
        return data

    try:
        results = await asyncio.gather(
            get_positions(bd1, name=n1),
            get_positions(bd2, name=n2),
            synastry_chart(bd1, bd2, name_1=n1, name_2=n2),
            relationship_compatibility_score(bd1, bd2, name_1=n1, name_2=n2),
            return_exceptions=True,
        )
        data['p1_positions'] = results[0] if not isinstance(results[0], Exception) else None
        data['p2_positions'] = results[1] if not isinstance(results[1], Exception) else None
        data['synastry'] = results[2] if not isinstance(results[2], Exception) else None
        data['score'] = results[3] if not isinstance(results[3], Exception) else None
    except Exception as e:
        logger.warning(f'[enrich] fetch_astro_data: {e}')

    return data


# ═══════════════════════════════════════════════════════════
# 2. Format helpers (extraire les infos-cles des reponses API)
# ═══════════════════════════════════════════════════════════
def _extract_planet(positions: Optional[Dict], planet: str) -> Optional[Dict]:
    """Extrait une planete depuis un payload get_positions."""
    if not positions:
        return None
    # Format v3 : positions.subject.planets = { sun: {...}, moon: {...} }
    planets = None
    if isinstance(positions, dict):
        subj = positions.get('subject') or positions
        planets = subj.get('planets') if isinstance(subj, dict) else None
        if not planets and 'data' in positions:
            planets = positions['data'].get('planets') if isinstance(positions['data'], dict) else None
    if not planets or not isinstance(planets, dict):
        return None
    key = planet.lower()
    return planets.get(key)


def _planet_summary(pos: Optional[Dict]) -> str:
    if not pos:
        return "position non calculée"
    sign = pos.get('sign') or pos.get('sign_name') or '?'
    house = pos.get('house') or pos.get('house_number')
    deg = pos.get('degree') or pos.get('longitude')
    parts = [str(sign)]
    if deg is not None:
        try:
            parts.append(f"{float(deg):.1f}°")
        except Exception:
            pass
    if house:
        parts.append(f"maison {house}")
    return " · ".join(parts)


def _synastry_aspects(synastry: Optional[Dict]) -> List[Dict]:
    """Retourne la liste des aspects synastrie (avec type, planetes, orbe)."""
    if not synastry:
        return []
    if isinstance(synastry, dict):
        aspects = synastry.get('aspects')
        if not aspects and 'data' in synastry:
            aspects = synastry['data'].get('aspects') if isinstance(synastry['data'], dict) else None
        if isinstance(aspects, list):
            return aspects[:20]
    return []


def _compat_score(score_payload: Optional[Dict]) -> Optional[int]:
    if not score_payload:
        return None
    if isinstance(score_payload, dict):
        s = score_payload.get('score')
        if s is None and 'data' in score_payload:
            s = score_payload['data'].get('score') if isinstance(score_payload['data'], dict) else None
        try:
            return int(s) if s is not None else None
        except Exception:
            return None
    return None


# ═══════════════════════════════════════════════════════════
# 3. LLM prompts (10 pages enrichies)
# ═══════════════════════════════════════════════════════════
SYSTEM_MSG = """Tu es Plume, oracle astrologique francais. Tu ecris des passages riches et personnalises
pour un rapport de synastrie premium (49€). Chaque texte doit :
- Faire entre 220 et 320 mots.
- Etre en francais soutenu, poetique mais precis, jamais fataliste.
- Citer les donnees astrologiques reelles fournies (signes, positions, aspects, orbes).
- Alterner : (a) une lecture symbolique, (b) une observation psychologique, (c) une invitation concrete.
- N'inventer aucune donnee astronomique non fournie.
- Aucune salutation, aucun emoji, aucune liste a puces. Un ou deux paragraphes fluides.
- Terminer par une image evocatrice."""


async def _gpt(prompt: str, session_id: str) -> str:
    """Appel GPT-4o-mini via Emergent LLM Key. Retourne texte brut."""
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        return ""
    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=SYSTEM_MSG,
        ).with_model('openai', 'gpt-4o-mini')
        r = await chat.send_message(UserMessage(text=prompt))
        return (r or "").strip()
    except Exception as e:
        logger.warning(f'[enrich] gpt call failed: {e}')
        return ""


def _fmt_position_line(name: str, positions: Optional[Dict]) -> str:
    """Ligne synthétique 'Sun in Taurus 24°, Moon in Virgo 12°, ...'"""
    if not positions:
        return f"{name} : positions non calculées."
    labels = [
        ("sun", "Soleil"), ("moon", "Lune"), ("mercury", "Mercure"),
        ("venus", "Venus"), ("mars", "Mars"), ("jupiter", "Jupiter"),
        ("saturn", "Saturne"), ("ascendant", "Ascendant"),
    ]
    parts = []
    for key, label in labels:
        p = _extract_planet(positions, key)
        if p:
            parts.append(f"{label} en {_planet_summary(p)}")
    if not parts:
        return f"{name} : positions non calculées."
    return f"{name} : " + " ; ".join(parts)


async def enrich_pages(astro: Dict[str, Any], only_pages: Optional[List[int]] = None) -> Dict[int, str]:
    """Genere les textes enrichis en parallel (Option A du user).
    only_pages : liste optionnelle de numeros de page a enrichir (pour reduire le temps).
    Par defaut, enrichit les 10 pages : 3,4,5,6,7,8,9,11,12,22."""
    n1 = astro.get('p1_name', 'L\'un')
    n2 = astro.get('p2_name', 'L\'autre')
    p1_pos = astro.get('p1_positions')
    p2_pos = astro.get('p2_positions')
    aspects = _synastry_aspects(astro.get('synastry'))
    score = _compat_score(astro.get('score'))

    p1_pos_line = _fmt_position_line(n1, p1_pos)
    p2_pos_line = _fmt_position_line(n2, p2_pos)

    def _aspects_str(filter_types: Optional[List[str]] = None, limit: int = 10) -> str:
        out = []
        for a in aspects[:20]:
            atype = (a.get('aspect') or a.get('type') or '').lower()
            if filter_types and atype not in filter_types:
                continue
            p_a = a.get('planet1') or a.get('body1') or a.get('p1')
            p_b = a.get('planet2') or a.get('body2') or a.get('p2')
            orb = a.get('orb')
            if p_a and p_b and atype:
                s = f"{p_a} ({n1}) {atype} {p_b} ({n2})"
                if orb is not None:
                    try:
                        s += f" à {float(orb):.1f}° d'orbe"
                    except Exception:
                        pass
                out.append(s)
            if len(out) >= limit:
                break
        return "\n".join(f"- {x}" for x in out) if out else "aucun aspect majeur transmis par l'API"

    prompts = {
        3: f"""Page 3 - Portrait natal de {n1}.
Donnees reelles :
{p1_pos_line}

Redige un portrait astrologique personnel de {n1}, en citant explicitement 3 planetes majeures (Soleil, Lune, Ascendant si dispo) avec leur signe et maison. Contexte : ce texte ouvre un rapport de synastrie de 25 pages destine a un couple. Le portrait doit rester digne, subtil, non-caricatural.""",

        4: f"""Page 4 - Portrait natal de {n2}.
Donnees reelles :
{p2_pos_line}

Redige un portrait astrologique personnel de {n2}, avec les memes exigences que pour {n1}. Ne repete pas les formules utilisees precedemment - trouve un angle different.""",

        5: f"""Page 5 - Soleils en miroir entre {n1} et {n2}.
Donnees reelles :
{p1_pos_line}
{p2_pos_line}

Aspects synastrie (extraits) :
{_aspects_str(limit=8)}

Analyse la rencontre des deux Soleils en tenant compte de leurs signes et de leurs eventuels aspects. Explique ce que la difference d'element apporte, ou au contraire ce que la conjonction d'element concentre. Conclus par une invitation pratique pour honorer la lumiere de l'autre.""",

        6: f"""Page 6 - Lunes en miroir entre {n1} et {n2}.
Donnees reelles :
{p1_pos_line}
{p2_pos_line}

Aspects synastrie :
{_aspects_str(limit=8)}

Explore les deux Lunes : besoins emotionnels, memoire affective, refuge interieur. Cite les signes et si possible un aspect Lune-Lune ou Lune-Soleil entre les deux. Termine par un geste concret que le couple peut experimenter cette semaine.""",

        7: f"""Page 7 - Mercure & Mercure entre {n1} et {n2}.
{p1_pos_line}
{p2_pos_line}
Aspects :
{_aspects_str(limit=8)}

Analyse la circulation de la parole et de la pensee entre eux. Cite leurs deux Mercures. Si un aspect Mercure-Mercure ou Mercure-Lune apparait, exploite-le. Propose un rituel de conversation concret.""",

        8: f"""Page 8 - Venus en miroir entre {n1} et {n2}.
{p1_pos_line}
{p2_pos_line}
Aspects synastrie :
{_aspects_str(limit=8)}

Redige un passage sur le langage d'amour astrologique du couple, en citant les deux Venus et tout aspect Venus-Venus / Venus-Mars / Venus-Lune reel. Invitation : un exercice pour decouvrir la langue amoureuse de l'autre.""",

        9: f"""Page 9 - Mars en miroir entre {n1} et {n2}.
{p1_pos_line}
{p2_pos_line}
Aspects synastrie :
{_aspects_str(limit=8)}

Ecris sur le desir, l'action, la sensualite, la maniere de se battre pour ce qu'ils aiment. Cite les deux Mars et tout aspect Mars pertinent. Termine par une invitation a nommer ce qu'ils desirent chacun.""",

        11: f"""Page 11 - Aspects harmonieux entre {n1} et {n2}.
Aspects reels (harmoniques : trigones, sextiles, conjonctions consonantes) :
{_aspects_str(filter_types=['trine', 'sextile', 'conjunction', 'trigone', 'sextil', 'conjonction'], limit=10)}

Redige un texte qui deroule les 3 aspects harmonieux les plus significatifs, en les nommant precisement (planete + type + orbe). Pour chaque aspect, explique la benediction concrete qu'il apporte dans le quotidien du couple. Ne survalorise pas : les trigones sont des routes ouvertes qu'il faut savoir emprunter.""",

        12: f"""Page 12 - Aspects de tension entre {n1} et {n2}.
Aspects reels (dissonants : carres, oppositions) :
{_aspects_str(filter_types=['square', 'opposition', 'carre', 'carré'], limit=10)}

Redige un texte sur 2 ou 3 aspects de tension majeurs, en citant precisement les planetes et l'orbe. Pour chaque aspect, explique la croissance qu'il propose (jamais comme malediction). Ferme sur l'idee qu'un couple sans tension s'endort.""",

        22: f"""Page 22 - Forces relationnelles.
Score de compatibilite : {score if score is not None else 'non calcule'}/100.
{p1_pos_line}
{p2_pos_line}
Aspects (extraits) :
{_aspects_str(limit=10)}

Redige un texte identifiant les 3 forces uniques de ce couple, en s'appuyant sur le score de compatibilite s'il est fourni, et sur les configurations astrologiques les plus favorables. Le texte doit donner de la fierte a lire, sans flagornerie."""
    }

    # Appelle GPT en parallel pour toutes les pages (filtrees si only_pages)
    keys = [k for k in prompts.keys() if not only_pages or k in only_pages]
    tasks = [_gpt(prompts[k], session_id=f'synastrie-p{k}') for k in keys]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    out: Dict[int, str] = {}
    for k, r in zip(keys, results):
        if isinstance(r, Exception) or not r:
            logger.warning(f'[enrich] page {k} failed')
            continue
        out[k] = r

    logger.info(f'[enrich] generated {len(out)}/{len(keys)} pages via GPT')
    return out
