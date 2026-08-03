"""
Service transverse d'enrichissement IA pour tous les PDFs Plume Astrale.

Prend en entree :
  - report_type : 'karma_destin' | 'numerology' | 'mediumnite' | 'kabbale' | 'tarot' | 'pack_karmique' | ...
  - context : dict de donnees brutes issues d'astrology-io ou services internes
  - prenom / birth_date_iso
Retourne :
  - dict de sections narratives (chaque cle = section, chaque valeur = 2-4 paragraphes prêts à insérer)

Chaque generateur PDF appelle enrich_report(report_type, context, prenom, birth_date_iso)
et injecte les paragraphes narratifs à la place de textes generiques hardcodes.

Design :
  - GPT-5.4 via Emergent LLM key (emergentintegrations)
  - System prompt specialisé par report_type (voix Solena, français impeccable)
  - Cache disque par hash(context) — evite regenerer 2x le meme rapport
  - Timeout dur 90s → fallback texte generique si echec (jamais bloquant)
  - JSON structure : chaque section demandee est un champ, garanti par prompt strict
"""
from __future__ import annotations
import hashlib
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

CACHE_DIR = Path('/app/backend/.state/report_ai_cache')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# System prompt commun (voix Solena)
# ═══════════════════════════════════════════════════════════════

BASE_VOICE = """Tu es Soléna, guide astrologue de Plume Astrale. Ta voix est chaleureuse,
sensible, précise, écrite pour des femmes 35-70 ans. Tu ne fais JAMAIS d'horoscope
générique — tu écris des paragraphes qui semblent "écrits pour elle". Règles absolues :

1. TUTOIEMENT chaleureux systématique (« tu », « toi », jamais « vous »).
2. Français impeccable, pas d'anglicismes, pas d'astro-jargon non expliqué.
3. Chaque section fait 2-4 paragraphes, JAMAIS 1 phrase courte.
4. Cite les données précises (signes, degrés, dates) quand disponibles.
5. Ne réutilise pas 2 fois le même adjectif dans un même paragraphe.
6. Zéro cliché ésotérique creux ("les étoiles t'accompagnent"). Sois concrète.
7. Termine chaque section par une réflexion ou une invitation, jamais un mode d'emploi.
8. Style : phrases moyennes, ton intime, alternance de rythmes.
9. RENVOIE UNIQUEMENT du JSON valide correspondant aux clés demandées, rien d'autre.
"""

# ═══════════════════════════════════════════════════════════════
# Templates par type de rapport
# ═══════════════════════════════════════════════════════════════

REPORT_SPECS: Dict[str, Dict[str, Any]] = {
    'karma_destin': {
        'title': 'Analyse Karmique & Destinée',
        'sections': {
            'introduction': "Introduction personnelle 3 paragraphes : ce que ton karma révèle globalement",
            'noeud_nord': "Nœud Nord (destinée) 3 paragraphes : chemin d'évolution concret",
            'noeud_sud': "Nœud Sud (héritage) 2-3 paragraphes : ce que tu as déjà maîtrisé et dois lâcher",
            'saturne': "Saturne (leçons) 3 paragraphes : test principal, âge du retour de Saturne, ce qui se joue",
            'chiron': "Chiron (blessure sacrée) 3 paragraphes : la faille, la guérison, ce que tu apportes aux autres",
            'pluton': "Pluton (transformation) 2-3 paragraphes : là où tu meurs et renais",
            'karma_generationnel': "Karma générationnel 3 paragraphes : héritage familial, patterns à guérir",
            'dates_cles': "3-4 dates-clés karmiques à venir (retour Saturne, retour Chiron, transits majeurs)",
            'invitation_finale': "Invitation finale 2 paragraphes : ce que tu es venue accomplir dans cette vie",
        },
    },
    'numerology': {
        'title': 'Code Numérologique',
        'sections': {
            'introduction': "Introduction 2-3 paragraphes : ce que ton code numérique dit de toi",
            'chemin_de_vie': "Chemin de vie (life_path) 3 paragraphes : ta trajectoire d'âme",
            'destinee': "Destinée (expression) 2-3 paragraphes : ce que tu es venue exprimer",
            'ame': "Nombre d'âme (soul urge) 2-3 paragraphes : ce que tu désires profondément",
            'personnalite': "Nombre de personnalité 2 paragraphes : l'image que tu projettes",
            'jour_naissance': "Nombre du jour de naissance 2 paragraphes : ton talent inné",
            'annee_personnelle': "Année personnelle en cours 3 paragraphes : thème et invitations concrètes des 12 prochains mois",
            'lo_shu': "Carré Lo-Shu (numérologie chinoise) 2-3 paragraphes : forces et faiblesses selon la grille",
            'biorythmes': "Biorythmes 90 jours 2 paragraphes : fenêtres physiques/émotionnelles/intellectuelles",
            'invitation_finale': "Invitation finale 2 paragraphes",
        },
    },
    'mediumnite': {
        'title': 'Éveil Médiumnique',
        'sections': {
            'introduction': "Introduction 3 paragraphes : ta sensibilité vibratoire",
            'clairs': "Tes quatre clairs (clairvoyance, clairaudience, clairsentience, claircognisance) : 1 paragraphe chacun avec exemples concrets",
            'guides': "Tes guides et protecteurs 3 paragraphes",
            'blocages': "Blocages énergétiques 2-3 paragraphes",
            'pratiques': "Pratiques d'éveil 3 paragraphes concrets — sans clichés",
            'invitation_finale': "Invitation finale 2 paragraphes",
        },
    },
    'kabbale': {
        'title': 'Kabbale & Arbre de Vie',
        'sections': {
            'introduction': "Introduction 3 paragraphes : ton arbre intérieur",
            'sephiroth_principales': "Tes 3 séphiroth dominantes 3 paragraphes : équilibre entre elles",
            'chemin_kabbalistique': "Ton chemin kabbalistique 3 paragraphes",
            'gematria_nom': "Gematria de ton nom 2-3 paragraphes",
            'lettres_hebraiques': "3 lettres hébraïques clés associées à ton profil 2-3 paragraphes",
            'invitation_finale': "Invitation finale 2 paragraphes",
        },
    },
    'pack_karmique': {
        'title': 'Pack Karmique',
        'sections': {
            'synthese': "Synthèse 3 paragraphes",
            'axe_karmique_principal': "Axe karmique principal 3 paragraphes",
            'liens_karmiques': "Liens karmiques avec ton entourage 3 paragraphes",
            'invitation_finale': "Invitation finale 2 paragraphes",
        },
    },
    'tarot_natal': {
        'title': 'Tarot de Naissance',
        'sections': {
            'introduction': "Introduction 2-3 paragraphes",
            'carte_ame': "Ta carte d'âme (arcane majeur) 3 paragraphes",
            'carte_personnalite': "Ta carte de personnalité 3 paragraphes",
            'carte_annee': "Ta carte de l'année en cours 3 paragraphes",
            'invitation_finale': "Invitation finale 2 paragraphes",
        },
    },
}


# ═══════════════════════════════════════════════════════════════
# Cache
# ═══════════════════════════════════════════════════════════════

def _cache_key(report_type: str, prenom: str, birth_date_iso: str,
               context: Dict[str, Any]) -> str:
    payload = json.dumps({
        'r': report_type, 'p': prenom, 'd': birth_date_iso, 'c': context,
    }, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def _cache_read(key: str) -> Optional[Dict[str, str]]:
    path = CACHE_DIR / f'{key}.json'
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def _cache_write(key: str, data: Dict[str, str]) -> None:
    try:
        path = CACHE_DIR / f'{key}.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f'[report_ai] cache write fail: {e}')


# ═══════════════════════════════════════════════════════════════
# LLM call
# ═══════════════════════════════════════════════════════════════

async def _call_gpt(system_msg: str, user_msg: str, session_id: str,
                    timeout_s: float = 90.0) -> Optional[str]:
    api_key = os.environ.get('EMERGENT_LLM_KEY', '').strip()
    if not api_key:
        logger.warning('[report_ai] EMERGENT_LLM_KEY manquante')
        return None
    import asyncio as _asyncio
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_msg,
        ).with_model('openai', 'gpt-5.4')
        return await _asyncio.wait_for(
            chat.send_message(UserMessage(text=user_msg)),
            timeout=timeout_s,
        )
    except _asyncio.TimeoutError:
        logger.error(f'[report_ai] LLM TIMEOUT après {timeout_s}s (session={session_id})')
        return None
    except Exception as e:
        logger.exception(f'[report_ai] LLM call failed: {e}')
        return None


def _parse_json_response(text: str) -> Optional[Dict[str, str]]:
    if not text:
        return None
    t = text.strip()
    if t.startswith('```'):
        t = re.sub(r'^```(?:json)?\s*', '', t)
        t = re.sub(r'```\s*$', '', t)
    try:
        d = json.loads(t)
        if isinstance(d, dict):
            return d
    except Exception:
        pass
    # dernier recours
    try:
        s = t.find('{'); e = t.rfind('}')
        if s >= 0 and e > s:
            d = json.loads(t[s:e + 1])
            if isinstance(d, dict):
                return d
    except Exception:
        pass
    return None


def _build_prompt(report_type: str, prenom: str, birth_date_iso: str,
                  context: Dict[str, Any]) -> tuple[str, str]:
    spec = REPORT_SPECS.get(report_type, {})
    title = spec.get('title', report_type)
    sections = spec.get('sections') or {}
    sections_desc = '\n'.join(f'  - "{k}" : {v}' for k, v in sections.items())

    system_msg = f"{BASE_VOICE}\n\nTu écris un rapport de type « {title} »."

    # Contexte compact pour ne pas exploser les tokens
    context_json = json.dumps(context, ensure_ascii=False, default=str, indent=2)
    if len(context_json) > 8000:
        context_json = context_json[:8000] + '\n... (tronqué)'

    user_msg = f"""Prénom de la personne : **{prenom}**
Date de naissance : {birth_date_iso}

Données brutes disponibles (à interpréter, pas à recopier) :
```json
{context_json}
```

Rédige un rapport avec EXACTEMENT ces sections (chaque clé JSON = 1 section) :
{sections_desc}

CONTRAINTES DE FORMAT :
- Réponds UNIQUEMENT par un objet JSON valide, sans autre texte autour.
- Chaque valeur = texte HTML simple avec balises <b>, <i>, <br/> autorisées.
- Chaque section fait au minimum 2 paragraphes séparés par <br/><br/>.
- Cite les données précises quand pertinent (signes, degrés, dates, nombres).
- Voix de Soléna : chaleureuse, précise, sans clichés."""

    return system_msg, user_msg


# ═══════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════

async def enrich_report(
    report_type: str,
    prenom: str,
    birth_date_iso: str,
    context: Dict[str, Any],
    use_cache: bool = True,
) -> Dict[str, str]:
    """
    Enrichit un rapport avec du contenu narratif IA.

    Returns:
        Dict[section_name -> HTML narrative content], ou dict vide si echec.
        Le PDF generator doit avoir un fallback texte generique par section.
    """
    if report_type not in REPORT_SPECS:
        logger.warning(f'[report_ai] type inconnu: {report_type}')
        return {}

    key = _cache_key(report_type, prenom, birth_date_iso, context)
    if use_cache:
        cached = _cache_read(key)
        if cached:
            logger.info(f'[report_ai] cache hit {report_type} pour {prenom} ({key[:8]})')
            return cached

    system_msg, user_msg = _build_prompt(report_type, prenom, birth_date_iso, context)
    session_id = f'report-{report_type}-{key[:12]}'

    logger.info(f'[report_ai] génération {report_type} pour {prenom} ({key[:8]})')
    raw = await _call_gpt(system_msg, user_msg, session_id, timeout_s=90.0)
    if not raw:
        return {}

    parsed = _parse_json_response(raw)
    if not parsed:
        logger.warning(f'[report_ai] parse JSON échec pour {report_type}')
        return {}

    # Filtre sur les cles attendues + nettoyage
    expected = REPORT_SPECS[report_type]['sections'].keys()
    result: Dict[str, str] = {}
    for k in expected:
        v = parsed.get(k)
        if isinstance(v, str) and v.strip():
            # Nettoie markdown ** en <b>
            v = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', v)
            result[k] = v.strip()

    if result:
        _cache_write(key, result)
    return result


def get_expected_sections(report_type: str) -> List[str]:
    """Utile pour le PDF generator qui veut savoir quelles clés demander."""
    spec = REPORT_SPECS.get(report_type, {})
    return list((spec.get('sections') or {}).keys())
