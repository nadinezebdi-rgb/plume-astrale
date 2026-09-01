"""prose_generator — Génération anti-slop de la prose éditoriale.

Génère les blocs éditoriaux d'un chapitre du Livre Astral en s'appuyant
sur les données astrologiques précises extraites du thème natal.

Chaine de prompts par chapitre (`generate_chapter_iv_love` pour Chapitre IV,
extensible aux 11 autres). Chaque prompt :

  1. Injecte les données EXACTES (degré · minute · signe · maison · rétrograde)
     — jamais de généralités "en général les Vénus en X…"
  2. Impose une BLACKLIST stricte de tournures AI-slop
  3. Impose une STRUCTURE éditoriale fixe (H2, paragraphes, encart, citation)
  4. Retourne du JSON strict → dispatché en `ChapterBlock` typés

Modèle : Claude Sonnet 4-6 (recommandé pour prose FR éditoriale premium).
Playbook : emergentintegrations avec EMERGENT_LLM_KEY.
"""
from __future__ import annotations
import json
import logging
import os
import re
from typing import Any, Optional

from emergentintegrations.llm.chat import LlmChat, UserMessage

from .domain import ChapterBlock, BlockKind

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# BLACKLIST — tournures interdites (matchées case-insensitive)
# Ces mots signent un AI-slop et cassent la voix éditoriale Plume.
# ═══════════════════════════════════════════════════════════════
BLACKLIST = (
    'il est important de noter',
    'il est intéressant de noter',
    'invite à',
    'invitent à',
    'invite vous à',
    'révèle',
    'révèlent',
    "l'univers",
    'cosmique',
    'énergie cosmique',
    'énergies cosmiques',
    'vibratoire',
    'vibrations',
    'destinée',
    'destin',
    'magie',
    'magique',
    'prédiction',
    'prédit',
    'voyance',
    'karma vous',
    'en effet,',
    'par ailleurs,',
    "d'une part",
    "d'autre part",
    'en conclusion',
    'pour conclure',
    'chers lecteurs',
    'chère lectrice',
    'plongée',
    'plongeons',
    'plonger',
    'explorer',
    'exploration',
    'découvrir',
    'découvrez',
    'fascinant',
    'fascinante',
    'merveilleux',
    'merveille',
    'incroyable',
    'extraordinaire',
    'unique en son genre',
    'sans équivoque',
    'sans nul doute',
    'il convient de',
    'il faut souligner',
    'gardez à l\'esprit',
    'n\'oubliez pas que',
    'rappelez-vous que',
)


def contains_slop(text: str) -> list[str]:
    """Renvoie la liste des expressions blacklistées trouvées dans le texte."""
    if not text:
        return []
    low = text.lower()
    return [b for b in BLACKLIST if b in low]


# ═══════════════════════════════════════════════════════════════
# Signature astro — extrait d'astro_data les variables du chapitre
# ═══════════════════════════════════════════════════════════════
def _fmt_deg(degree: Any) -> str:
    """Formatte un degré décimal en '11° 08′'. Accepte float ou dict {deg,min}."""
    if degree is None:
        return '—'
    if isinstance(degree, dict):
        d = int(degree.get('deg') or degree.get('degree') or 0)
        m = int(degree.get('min') or degree.get('minute') or 0)
        return f'{d}° {m:02d}′'
    try:
        d = float(degree)
        deg = int(d)
        minutes = int(round((d - deg) * 60))
        if minutes == 60:
            deg += 1
            minutes = 0
        return f'{deg}° {minutes:02d}′'
    except (TypeError, ValueError):
        return str(degree)


def _fmt_sign_fr(sign_en_or_fr: str) -> str:
    """Traduit signe anglais → majuscules françaises. Passe-plat si déjà FR."""
    mapping = {
        'aries': 'BÉLIER', 'taurus': 'TAUREAU', 'gemini': 'GÉMEAUX',
        'cancer': 'CANCER', 'leo': 'LION', 'virgo': 'VIERGE',
        'libra': 'BALANCE', 'scorpio': 'SCORPION', 'sagittarius': 'SAGITTAIRE',
        'capricorn': 'CAPRICORNE', 'aquarius': 'VERSEAU', 'pisces': 'POISSONS',
    }
    s = (sign_en_or_fr or '').strip().lower()
    return mapping.get(s, (sign_en_or_fr or '').upper())


def _fmt_house(h: Any) -> str:
    """Formate un numéro de maison en 'MAISON V' (romain)."""
    if h is None:
        return ''
    romans = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI',
              7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'}
    try:
        return f"MAISON {romans[int(h)]}"
    except (KeyError, ValueError, TypeError):
        return f'MAISON {h}'


def extract_venus_signature(astro_data: dict) -> dict:
    """Extrait les 6-8 données EXACTES nécessaires au Chapitre IV.

    astro_data attendu : sortie de extract_planets(natal_chart(...)) enrichie
    avec extract_ascendant_sign_en et éventuellement les aspects.

    Retourne un dict prêt à injecter dans le prompt :
      { venus: {sign, sign_fr, house, house_fr, degree, retrograde, aspects: [...]}
      , mars: idem
      , lune: {sign, sign_fr, house, house_fr, degree, aspects: [...]}
      , house_v: 'MAISON V' (label) + master planet + sign of cusp if available
      , house_vii: idem }
    """
    planets = astro_data.get('planets') or {}
    if not planets and 'positions' in astro_data:
        # Format legacy list → dict
        planets = {(p.get('name') or '').lower(): p for p in astro_data['positions']}

    def _p(name: str) -> dict:
        p = planets.get(name.lower()) or {}
        sign = p.get('sign') or ''
        return {
            'sign': sign,
            'sign_fr': _fmt_sign_fr(sign),
            'house': p.get('house'),
            'house_fr': _fmt_house(p.get('house')),
            'degree': _fmt_deg(p.get('degree')),
            'retrograde': bool(p.get('retrograde') or p.get('is_retrograde')),
            'aspects': p.get('aspects') or [],
        }

    return {
        'venus': _p('venus'),
        'mars': _p('mars'),
        'lune': _p('moon'),
        'soleil': _p('sun'),
        'ascendant': _p('ascendant'),
        'house_v_master': astro_data.get('house_v_master', ''),
        'house_vii_master': astro_data.get('house_vii_master', ''),
    }


# ═══════════════════════════════════════════════════════════════
# System prompt — voix éditoriale Plume Astrale
# ═══════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """Tu écris pour Plume Astrale, marque française premium de développement personnel.

Voix : sobre, tendre, adulte. Ton d'une amie très cultivée qui a lu Yourcenar et Colette. JAMAIS "invitation cosmique", JAMAIS "l'univers vous". Tu parles à UNE personne, jamais à "vous tous". Le TU/VOUS est le VOUS de courtoisie française — pas celui du coach américain.

Règles absolues :
- Chaque affirmation s'ancre dans une donnée astrologique EXACTE fournie (degré, signe, maison). Pas de généralité.
- Phrases variables (7 mots · 22 mots · 4 mots · 18 mots). Pas de mécanique.
- Zéro emoji, zéro majuscule dramatique, zéro exclamation.
- Jamais d'énumération à trois "X, Y et Z" (signature ChatGPT). Préférer deux termes ou une phrase développée.
- Interdit d'utiliser : « il est important de noter », « invite à », « révèle », « cosmique », « vibratoire », « destinée », « prédiction », « explorer », « découvrir », « fascinant », « merveilleux », « en effet », « par ailleurs », « chers lecteurs », « plonger », « n'oubliez pas que », « gardez à l'esprit ».
- Autorisé : phrases courtes coupantes, ellipses (…), semi-colons pour la respiration, italiques rares.
- Ton : tendresse ferme. Comme une lettre.

Format de sortie : JSON strict, aucun texte hors du JSON."""


# ═══════════════════════════════════════════════════════════════
# Chapitre IV — Votre façon d'aimer
# ═══════════════════════════════════════════════════════════════
CHAPTER_IV_USER_PROMPT = """Rédige le CHAPITRE IV « Votre façon d'aimer » du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES (obligatoires à ancrer dans le texte) :

- Vénus : {venus_sign_fr} · {venus_house_fr} · {venus_degree}{venus_retro_label}
- Mars : {mars_sign_fr} · {mars_house_fr} · {mars_degree}{mars_retro_label}
- Lune : {lune_sign_fr} · {lune_house_fr} · {lune_degree}
- Soleil : {soleil_sign_fr} · {soleil_house_fr}

Structure IMPÉRATIVE (10 pages A5, ~2200 mots) :

1. `dropcap` — Paragraphe d'ouverture 100-140 mots. Commence par « Vénus, chez vous, s'est posée en {venus_sign_fr} — {venus_degree} de {venus_sign_fr}. » Puis développe ce que cela dit précisément (sans jargon).
2. `h2` — « Ce que Vénus en {venus_sign_fr} dit de vos gestes »
3. `paragraph` × 2 (~150 mots chacun) — le premier ancré dans le degré exact, le second dans la maison.
4. `encart` — Label « VOTRE FORCE EN AMOUR », 40-55 mots italique, phrase intime.
5. `h2` — « Le rendez-vous entre Vénus et Mars »
6. `paragraph` × 2 — analyse du rapport Vénus/Mars (harmonie ou tension selon signes/aspects). Cite les deux positions exactes.
7. `quote_literary` — Citation d'un auteur classique français (Colette, Yourcenar, Duras, Barthes fragments d'un discours amoureux) qui résonne avec {venus_sign_fr}. Attribue-la correctement.
8. `h2` — « Votre Lune et vos besoins tendres »
9. `paragraph` × 2 — la Lune en {lune_sign_fr}, ses besoins de repli, comment cela cohabite avec Vénus.
10. `encart` — Label « VOTRE DÉFI EN AMOUR », 40-55 mots italique.
11. `h2` — « La Maison V et la joie »
12. `paragraph` × 2 — la maison de la joie, du jeu, de ce qui donne envie. Ancré dans {venus_house_fr} si Vénus y est, sinon dans le placement.
13. `paragraph` — court, 60-90 mots, transition douce.
14. `encart` — Label « VOTRE CLÉ », 40-55 mots, la phrase que {first_name} devrait garder en tête.
15. `quote_breath` — 12-18 mots, tenue par le blanc, très éditoriale.

FORMAT DE SORTIE (JSON strict, aucun texte hors du JSON) :
{{
  "blocks": [
    {{"kind": "paragraph_dropcap", "data": {{"text": "..."}}}},
    {{"kind": "h2", "data": {{"text": "..."}}}},
    {{"kind": "paragraph", "data": {{"text": "..."}}}},
    {{"kind": "paragraph", "data": {{"text": "..."}}}},
    {{"kind": "encart", "data": {{"label": "VOTRE FORCE EN AMOUR", "text": "..."}}}},
    {{"kind": "h2", "data": {{"text": "..."}}}},
    {{"kind": "paragraph", "data": {{"text": "..."}}}},
    {{"kind": "paragraph", "data": {{"text": "..."}}}},
    {{"kind": "quote_literary", "data": {{"text": "...", "source": "Auteur, Œuvre"}}}},
    {{"kind": "h2", "data": {{"text": "..."}}}},
    {{"kind": "paragraph", "data": {{"text": "..."}}}},
    {{"kind": "paragraph", "data": {{"text": "..."}}}},
    {{"kind": "encart", "data": {{"label": "VOTRE DÉFI EN AMOUR", "text": "..."}}}},
    {{"kind": "h2", "data": {{"text": "..."}}}},
    {{"kind": "paragraph", "data": {{"text": "..."}}}},
    {{"kind": "paragraph", "data": {{"text": "..."}}}},
    {{"kind": "paragraph", "data": {{"text": "..."}}}},
    {{"kind": "encart", "data": {{"label": "VOTRE CLÉ", "text": "..."}}}},
    {{"kind": "quote_breath", "data": {{"text": "..."}}}}
  ]
}}
"""


async def _call_claude(system: str, user: str, session_id: str) -> str:
    """Appel Claude Sonnet 4-6 via EMERGENT_LLM_KEY. Non-stream (JSON strict).

    IMPORTANT : `emergentintegrations` utilise `litellm.completion()` synchrone
    à l'intérieur de `send_message` async → l'appel bloque le event loop.
    On enveloppe donc dans `asyncio.to_thread` pour libérer la boucle.
    """
    import asyncio as _a
    key = os.environ.get('EMERGENT_LLM_KEY')
    if not key:
        raise RuntimeError('EMERGENT_LLM_KEY absent de .env')

    def _sync_call() -> str:
        # Recréer une nouvelle boucle interne pour l'appel bloquant
        loop = _a.new_event_loop()
        try:
            chat = (
                LlmChat(api_key=key, session_id=session_id, system_message=system)
                .with_model('anthropic', 'claude-sonnet-4-6')
            )
            resp = loop.run_until_complete(chat.send_message(UserMessage(text=user)))
            if isinstance(resp, str):
                return resp.strip()
            text = getattr(resp, 'text', None) or getattr(resp, 'content', None) or str(resp)
            return text.strip()
        finally:
            loop.close()

    return await _a.to_thread(_sync_call)


def _parse_json_blocks(raw: str) -> list[dict]:
    """Extrait le premier objet JSON valide de la réponse du LLM.

    Tolérant : accepte markdown code fences, préambules, texte parasite.
    """
    # Retire code fences
    m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
    if m:
        raw = m.group(1)
    # Trouve le premier { ...  } équilibré
    start = raw.find('{')
    if start < 0:
        raise ValueError(f'Aucun JSON trouvé dans la réponse LLM. raw={raw[:200]!r}')
    depth = 0
    end = -1
    for i in range(start, len(raw)):
        if raw[i] == '{':
            depth += 1
        elif raw[i] == '}':
            depth -= 1
            if depth == 0:
                end = i
                break
    if end < 0:
        raise ValueError('JSON non balancé dans la réponse LLM')
    obj = json.loads(raw[start:end + 1])
    blocks = obj.get('blocks')
    if not isinstance(blocks, list):
        raise ValueError('Champ `blocks` manquant ou invalide')
    return blocks


def _blocks_to_chapter_blocks(dicts: list[dict]) -> list[ChapterBlock]:
    """Convertit les dicts JSON en `ChapterBlock` typés + validation slop."""
    out: list[ChapterBlock] = []
    for d in dicts:
        kind_str = d.get('kind') or ''
        data = d.get('data') or {}
        try:
            kind = BlockKind(kind_str)
        except ValueError:
            logger.warning(f'[prose_gen] Kind invalide ignoré : {kind_str!r}')
            continue
        # Audit anti-slop (log-only, on ne bloque pas — laisser choix éditorial)
        text = data.get('text') or ''
        slop = contains_slop(text)
        if slop:
            logger.warning(f'[prose_gen] SLOP détecté ({kind_str}) : {slop[:3]}')
        out.append(ChapterBlock(kind=kind, data=data))
    return out


async def generate_chapter_iv_love(
    *,
    first_name: str,
    astro_data: dict,
    session_id: str,
) -> list[ChapterBlock]:
    """Génère les blocs du Chapitre IV « Votre façon d'aimer ».

    Retourne une liste `ChapterBlock` prête à ajouter à un `Chapter`.
    En cas d'échec LLM, retourne une chaîne de blocs fallback minimale
    pour ne jamais casser le PDF.
    """
    sig = extract_venus_signature(astro_data)
    v = sig['venus']
    m = sig['mars']
    l = sig['lune']
    s = sig['soleil']

    user = CHAPTER_IV_USER_PROMPT.format(
        first_name=first_name,
        venus_sign_fr=v['sign_fr'] or 'un signe non calculable',
        venus_house_fr=v['house_fr'] or 'MAISON —',
        venus_degree=v['degree'],
        venus_retro_label=' · en rétrogradation' if v['retrograde'] else '',
        mars_sign_fr=m['sign_fr'] or 'un signe non calculable',
        mars_house_fr=m['house_fr'] or 'MAISON —',
        mars_degree=m['degree'],
        mars_retro_label=' · en rétrogradation' if m['retrograde'] else '',
        lune_sign_fr=l['sign_fr'] or 'un signe non calculable',
        lune_house_fr=l['house_fr'] or 'MAISON —',
        lune_degree=l['degree'],
        soleil_sign_fr=s['sign_fr'] or 'un signe non calculable',
        soleil_house_fr=s['house_fr'] or 'MAISON —',
    )

    try:
        raw = await _call_claude(SYSTEM_PROMPT, user, session_id=f'chapter_iv_{session_id}')
        dicts = _parse_json_blocks(raw)
        blocks = _blocks_to_chapter_blocks(dicts)
        if not blocks:
            raise ValueError('Aucun bloc valide généré')
        return blocks
    except Exception as e:
        logger.error(f'[prose_gen] Chapitre IV LLM failed: {e}')
        # Fallback éditorial minimal — JAMAIS de PDF cassé
        return _fallback_chapter_iv(first_name, sig)


def _fallback_chapter_iv(first_name: str, sig: dict) -> list[ChapterBlock]:
    """Chaîne de blocs minimale si le LLM échoue. Anti-slop garanti manuellement."""
    v = sig['venus']
    return [
        ChapterBlock(BlockKind.PARAGRAPH_DROPCAP, {
            'text': (
                f"Vénus, chez vous, s'est posée en {v['sign_fr'] or 'un signe rare'} — "
                f"{v['degree']} de {v['sign_fr'] or ''}. C'est la manière dont vous "
                "aimez, et c'est aussi la manière dont vous voulez être aimé{fem}. "
                "Le degré compte : chaque minute d'arc trace une inflexion différente. "
                "Ce chapitre lit la vôtre."
            ).format(fem='e' if first_name and first_name.endswith(('a', 'e')) else '')
        }),
        ChapterBlock(BlockKind.H2, {'text': f"Ce que Vénus en {v['sign_fr']} dit de vos gestes"}),
        ChapterBlock(BlockKind.PARAGRAPH, {
            'text': (
                "La génération de ce chapitre a temporairement échoué. "
                "Le manuscrit sera régénéré automatiquement dans quelques minutes. "
                "Aucune action de votre part n'est requise."
            )
        }),
    ]
