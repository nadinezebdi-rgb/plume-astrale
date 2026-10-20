"""natal_manuscript_builder — Thème Natal en vrai livre (préface + sommaire + chapitres)
================================================================================

Produit un Manuscript multi-chapitres pour le PDF Thème Natal (A5 print blanc).

Structure éditoriale :
  Chapitre I   — Préface « Comment lire ce livre » (AI-générée, ~3 pages)
  Chapitre II  — Votre ciel en synthèse (trio + roue + synthèse exécutive)
  Chapitre III — Vos planètes (10 planètes, 2 par page = 5 pages)
  Chapitre IV  — Vos douze maisons (12 maisons, 3 par page = 4 pages)
  Chapitre V   — Vos aspects (5 groupes = 5 pages)
  Chapitre VI  — Synthèse — ce que votre ciel vous dit (voix Soléna, 1-2 pages)

Chaque chapitre a sa belle page recto. Le renderer book_engine_v2 ajoute :
  - Couverture, blanche, titre, blanche
  - Sommaire (nouveau — voir `_toc.html`)
  - Pour le Ch. II : roue céleste + tableaux positions/aspects
  - Colophon final + blanches pour multiple de 4

L'appelant fournit `natal_data` (positions, aspects, cuspides, prose IA) via
`natal_pdf_adapter.generate_manuscrit_pdf`. Les helpers d'extraction
viennent de `natal_chart_extract.py`.
"""
from __future__ import annotations
import base64
import logging
from datetime import datetime, timezone

from services.book_engine_shared.domain import (
    BirthData, BlockKind, Chapter, ChapterBlock, Edition, Manuscript,
)
from services import natal_chart_extract as nce

logger = logging.getLogger(__name__)


def _parse_birth_date(birth_date: str) -> BirthData:
    return BirthData(
        date_iso=birth_date or '',
        time_hhmm=None,
        city='',
        country_code='FR',
    )


# ─── Templates courts (fallback neutre, jamais d'excuse) ─────────────
_PLANET_HINT = {
    'Soleil':   "le cœur de votre identité, ce que vous rayonnez quand vous êtes vous-même",
    'Lune':     "votre monde intérieur, vos réflexes émotionnels, vos tendresses secrètes",
    'Mercure':  "votre façon de penser, de parler, d'apprendre",
    'Vénus':    "votre manière d'aimer, de goûter, d'embellir",
    'Mars':     "votre élan, votre colère, ce qui vous met en mouvement",
    'Jupiter':  "votre zone d'expansion, ce qui vous fait grandir et avoir confiance",
    'Saturne':  "votre colonne vertébrale, les leçons qui bâtissent votre souveraineté",
    'Uranus':   "votre liberté, vos coups de pied dans la table, vos éclats visionnaires",
    'Neptune':  "vos rêves, votre spiritualité, ce qui dissout vos contours",
    'Pluton':   "votre pouvoir, ce qui vous transforme en profondeur, votre part de nuit",
    'Ascendant': "le masque que votre âme a choisi — ce que les autres voient en premier",
}


def _house_sentence(house: dict) -> str:
    """Phrase courte pour une maison : cuspide + occupants + thème."""
    name = house['name']
    sign = house.get('sign') or ''
    cusp = house.get('cusp_degree_str') or ''
    theme = house.get('theme') or ''
    desc = house.get('theme_desc') or ''
    planets = house.get('planets') or []

    parts = []
    if sign and cusp:
        parts.append(f"La cuspide de la <b>{name.lower()}</b> tombe en <b>{sign}</b> à {cusp}.")
    elif sign:
        parts.append(f"La cuspide de la <b>{name.lower()}</b> tombe en <b>{sign}</b>.")
    else:
        parts.append(f"<b>{name}</b> — {theme.lower()}.")

    parts.append(f"Cette maison gouverne {desc}.")

    if planets:
        if len(planets) == 1:
            parts.append(f"Une planète y séjourne : <b>{planets[0]}</b>. Elle colore ce domaine de son énergie propre.")
        else:
            noms = ', '.join(f'<b>{p}</b>' for p in planets[:-1]) + f' et <b>{planets[-1]}</b>'
            parts.append(f"Plusieurs planètes y séjournent — {noms}. Ce secteur est un foyer actif de votre thème.")
    else:
        parts.append("Aucune planète n'y séjourne : vous l'habitez à votre rythme, sans projecteur astral permanent.")

    return ' '.join(parts)


def _aspect_group_paragraphs(aspects: list, nature_hint: str) -> list[str]:
    paras: list[str] = [nature_hint]
    for a in aspects:
        interp = nce.interpret_aspect(a) or (
            f"<b>{a.get('planet_a', '?')} {a.get('type_fr', '').lower()} {a.get('planet_b', '?')}</b> — "
            "ce dialogue planétaire laisse sa marque dans votre thème."
        )
        orb = a.get('orb_degrees')
        orb_part = f' <i>(orbe {orb:.1f}°)</i>' if isinstance(orb, (int, float)) else ''
        paras.append(f"<b>{a.get('planet_a', '?')} — {a.get('planet_b', '?')}</b>{orb_part}. {interp}")
    return paras


# ─── Builders de chapitres individuels ──────────────────────────────
def _chapter_preface(preface_blocks: list[dict], prenom: str) -> Chapter:
    """Chapitre I — Comment lire ce livre (préface AI-générée ou statique)."""
    blocks: list[ChapterBlock] = []
    blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': 'I',
        'title': "Comment lire ce livre",
        'kicker': 'Un mode d\'emploi tendre, pour les années à venir.',
    }))
    for b in preface_blocks:
        kind = (b.get('kind') or '').lower()
        text = (b.get('text') or '').strip()
        if not text:
            continue
        if kind == 'h2':
            blocks.append(ChapterBlock(BlockKind.H2, {'text': text}))
        else:
            blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': text, 'raw': True}))
    blocks.append(ChapterBlock(BlockKind.FEATHER, {}))
    return Chapter(
        slug='natal_preface', title="Comment lire ce livre",
        kicker='Un mode d\'emploi tendre.', roman_num='I', order=1, blocks=blocks,
    )


def _chapter_synthese(
    prenom: str, birth_date_fr: str, sun_sign: str, moon_sign: str,
    asc_sign: str, no_birth_time: bool, aspects_norm: list, houses: list,
    chart_png_bytes: bytes | None,
) -> Chapter:
    """Chapitre II — Votre ciel en synthèse (trio + roue + highlights)."""
    blocks: list[ChapterBlock] = []
    blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': 'II',
        'title': f"Le Ciel de {prenom}",
        'kicker': 'Trois signatures qui composent votre identité céleste.',
    }))

    if birth_date_fr:
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': f'<span class="lede-date">Né·e le {birth_date_fr}.</span>',
            'raw': True,
        }))

    # Trio cards
    trio: list[dict] = []
    if sun_sign:
        trio.append({'label': 'Soleil', 'sign': sun_sign})
    if moon_sign:
        trio.append({'label': 'Lune', 'sign': moon_sign})
    if asc_sign and not no_birth_time:
        trio.append({'label': 'Ascendant', 'sign': asc_sign})
    if trio:
        blocks.append(ChapterBlock(BlockKind.TRIO_CARDS, {'items': trio}))

    # Chart wheel
    if chart_png_bytes:
        try:
            b64 = base64.b64encode(chart_png_bytes).decode('ascii')
            blocks.append(ChapterBlock(BlockKind.NATAL_CHART, {
                'src': f'data:image/png;base64,{b64}',
                'alt': f'Roue du ciel de {prenom}',
            }))
        except Exception as e:
            logger.warning(f'[natal_manuscript] chart encoding failed: {e}')

    # Synthèse exécutive sur page suivante
    blocks.append(ChapterBlock(BlockKind.PAGE_BREAK, {}))
    blocks.append(ChapterBlock(BlockKind.H2, {'text': "Synthèse en un coup d'œil"}))
    if sun_sign:
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': (f"Votre Soleil brille en <b>{sun_sign}</b> — c'est le cœur de votre identité, "
                     f"ce que vous rayonnez quand vous êtes pleinement vous-même."),
            'raw': True,
        }))
    if moon_sign:
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': (f"Votre Lune se love en <b>{moon_sign}</b> — c'est votre monde intérieur, "
                     f"la façon dont vous vous apaisez, dont vous aimez, dont vous ressentez."),
            'raw': True,
        }))
    if asc_sign and not no_birth_time:
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': (f"Votre Ascendant lève en <b>{asc_sign}</b> — c'est le masque que votre âme "
                     f"a choisi, la première note que vous donnez au monde."),
            'raw': True,
        }))
    nb_aspects = len(aspects_norm)
    nb_houses = sum(1 for h in houses if h.get('planets'))
    if nb_aspects:
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': (f"Votre thème compte <b>{nb_aspects} aspects majeurs</b> entre vos planètes — "
                     f"autant de dialogues célestes qui composent votre nuance unique."),
            'raw': True,
        }))
    if nb_houses:
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': (f"<b>{nb_houses} des douze maisons</b> accueillent au moins une planète — "
                     f"ce sont vos domaines de vie les plus actifs, ceux où le ciel vous appelle à vivre."),
            'raw': True,
        }))
    blocks.append(ChapterBlock(BlockKind.FEATHER, {}))
    return Chapter(
        slug='natal_synthese', title=f"Le Ciel de {prenom}",
        kicker='Vos trois signatures.', roman_num='II', order=2, blocks=blocks,
    )


def _chapter_planets(planets_narr: list, pos_by_name: dict, no_birth_time: bool) -> Chapter:
    """Chapitre III — Vos planètes (2 planètes par page = 5 pages pleines)."""
    blocks: list[ChapterBlock] = []
    blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': 'III',
        'title': "Vos planètes",
        'kicker': 'Dix forces qui composent votre palette intérieure.',
    }))
    blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
        'text': (
            "Dix forces habitent votre ciel. Chacune vit dans un signe, à un degré précis, "
            "et occupe un territoire de votre vie — une maison. Ce chapitre les présente une à une, "
            "dans l'ordre où elles tissent votre complexité."
        ),
    }))

    # 2 planètes par page — chaque H2 planète suit un petit texte paragraphe
    valid_planets = [p for p in planets_narr
                     if (p.get('name') or '').strip() and (p.get('sign') or '').strip()]
    for i, p in enumerate(valid_planets):
        name = p['name'].strip()
        sign = p['sign'].strip()
        analysis = (p.get('analysis') or '').strip()
        # Toutes les 2 planètes, nouvelle page (sauf la première qui suit l'intro)
        if i > 0:
            blocks.append(ChapterBlock(BlockKind.PAGE_BREAK, {}))
        det = pos_by_name.get(name) or {}
        parts = [f'{name} en {sign}']
        deg_str = det.get('degree_in_sign_str') or ''
        if deg_str:
            parts.append(deg_str)
        house_num = det.get('house')
        if isinstance(house_num, int) and 1 <= house_num <= 12 and not no_birth_time:
            parts.append(f'maison {house_num}')
        if det.get('retrograde'):
            parts.append('rétrograde ℞')
        blocks.append(ChapterBlock(BlockKind.H2, {'text': ' · '.join(parts)}))
        if not analysis:
            hint = _PLANET_HINT.get(name, '')
            if hint:
                analysis = (
                    f"{name} en {sign} parle de {hint}. "
                    f"C'est une couleur à part entière de votre palette intérieure."
                )
        if analysis:
            paras = [pp.strip() for pp in analysis.split('\n\n') if pp.strip()] or [analysis]
            for para in paras:
                blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': para}))

    blocks.append(ChapterBlock(BlockKind.FEATHER, {}))
    return Chapter(
        slug='natal_planets', title="Vos planètes",
        kicker='Dix forces, dix couleurs.', roman_num='III', order=3, blocks=blocks,
    )


def _chapter_houses(houses: list) -> Chapter:
    """Chapitre IV — Vos douze maisons (3 par page = 4 pages pleines)."""
    blocks: list[ChapterBlock] = []
    blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': 'IV',
        'title': "Vos douze maisons",
        'kicker': 'Les scènes de votre vie, telles que le ciel les éclaire.',
    }))
    blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
        'text': (
            "Si les planètes sont vos acteurs intérieurs, les maisons sont les scènes où ils se produisent. "
            "Douze territoires, douze théâtres de vie. Chaque maison tient un domaine : votre apparence, "
            "votre foyer, vos liens, votre travail, vos rêves — et davantage. Celles où séjournent une "
            "ou plusieurs planètes sont vos foyers actifs ; les autres, vous les habitez plus discrètement."
        ),
    }))
    for idx, h in enumerate(houses):
        # 3 maisons par page (après l'intro)
        if idx > 0 and idx % 3 == 0:
            blocks.append(ChapterBlock(BlockKind.PAGE_BREAK, {}))
        h2 = f"{h['name']}"
        if h.get('sign'):
            h2 += f" · {h['sign']}"
        if h.get('planets'):
            n = len(h['planets'])
            h2 += f" ({n} planète{'s' if n > 1 else ''})"
        blocks.append(ChapterBlock(BlockKind.H2, {'text': h2}))
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': _house_sentence(h), 'raw': True,
        }))
    blocks.append(ChapterBlock(BlockKind.FEATHER, {}))
    return Chapter(
        slug='natal_houses', title="Vos douze maisons",
        kicker='Douze scènes, douze théâtres.', roman_num='IV', order=4, blocks=blocks,
    )


def _chapter_aspects(aspects_norm: list) -> Chapter:
    """Chapitre V — Vos aspects (5 groupes = 5 pages ou moins si certains vides)."""
    blocks: list[ChapterBlock] = []
    blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': 'V',
        'title': "Vos aspects",
        'kicker': 'La danse invisible entre vos planètes.',
    }))
    blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
        'text': (
            "Les planètes se parlent. Certaines se renforcent (<i>conjonction</i>, <i>trigone</i>, "
            "<i>sextile</i>), d'autres se frottent (<i>opposition</i>, <i>carré</i>). Chaque dialogue "
            "laisse une empreinte dans votre caractère. Voici les plus marquants, groupés par nature."
        ),
        'raw': True,
    }))
    groups = [
        ('Conjonction', "Les conjonctions fusionnent deux forces en une seule note — elles amplifient."),
        ('Opposition', "Les oppositions mettent deux pôles face à face — elles cherchent l'équilibre."),
        ('Trigone', "Les trigones font circuler l'énergie en douceur — ce sont vos talents naturels."),
        ('Carré', "Les carrés provoquent la friction nécessaire au mouvement — ce sont vos moteurs."),
        ('Sextile', "Les sextiles sont des opportunités discrètes — elles s'ouvrent si vous les saisissez."),
    ]
    # 2 types par page — place un PAGE_BREAK entre groupes impairs
    rendered_groups = 0
    for type_fr, hint in groups:
        sub = [a for a in aspects_norm if a.get('type_fr') == type_fr]
        if not sub:
            continue
        # Nouveau "folio" tous les 2 groupes (après intro + 2 groupes)
        if rendered_groups > 0 and rendered_groups % 2 == 0:
            blocks.append(ChapterBlock(BlockKind.PAGE_BREAK, {}))
        rendered_groups += 1
        blocks.append(ChapterBlock(BlockKind.H2, {'text': f'{type_fr}s — {len(sub)}'}))
        for para in _aspect_group_paragraphs(sub, hint):
            blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': para, 'raw': True}))
    blocks.append(ChapterBlock(BlockKind.FEATHER, {}))
    return Chapter(
        slug='natal_aspects', title="Vos aspects",
        kicker='Vos planètes se parlent.', roman_num='V', order=5, blocks=blocks,
    )


def _chapter_synthese_finale(synthese_text: str) -> Chapter:
    """Chapitre VI — Synthèse finale voix Soléna."""
    blocks: list[ChapterBlock] = []
    blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': 'VI',
        'title': "Ce que votre ciel vous dit",
        'kicker': 'Synthèse — à relire en période de doute.',
    }))
    paras = [p.strip() for p in synthese_text.split('\n\n') if p.strip()] or [synthese_text]
    for para in paras:
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': para}))
    blocks.append(ChapterBlock(BlockKind.FEATHER, {}))
    return Chapter(
        slug='natal_closing', title="Ce que votre ciel vous dit",
        kicker='Soléna vous parle.', roman_num='VI', order=6, blocks=blocks,
    )


# ─── Builder principal ──────────────────────────────────────────────
def build_natal_manuscript(
    *,
    prenom: str,
    birth_date: str,
    natal_data: dict,
    chart_png_bytes: bytes | None = None,
    user_email: str = '',
    session_id: str = '',
    preface_blocks: list[dict] | None = None,
    book_data: dict | None = None,
) -> Manuscript:
    """Construit un Manuscript multi-chapitres prêt à être rendu en PDF print blanc.

    `preface_blocks` optionnel : blocs AI-générés (list of {'kind', 'text'}).
    Si absent, un fallback statique de qualité est utilisé.

    `natal_data` attendus :
      sun_sign, moon_sign, ascendant_sign, no_birth_time
      planets[]        — [{name, sign, analysis}]  (per-planet AI prose)
      planets_detail[] — [{name, sign, degree_in_sign, house, retrograde}]  (facultatif)
      aspects[]        — [{planet_a, planet_b, type, orb}]  (facultatif, format API)
      house_cusps      — {num: {sign, degree}}  (facultatif)
      synthese_aspects — paragraphe Soléna optionnel
      tier             — 'ultra' ou 'legacy'
    """
    prenom = (prenom or 'Voyageuse').strip() or 'Voyageuse'

    def _fmt_date_fr(date_iso: str) -> str:
        if not date_iso:
            return ''
        try:
            y, mo, d = date_iso.split('-')[:3]
            months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                      'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
            return f'{int(d)} {months[int(mo) - 1]} {y}'
        except Exception:
            return date_iso or ''
    birth_date_fr = _fmt_date_fr(birth_date)

    no_birth_time = bool(natal_data.get('no_birth_time'))

    # Extraction/normalisation via natal_chart_extract
    extract_input = {
        'planets': natal_data.get('planets_detail') or natal_data.get('planets') or [],
        'aspects': natal_data.get('aspects') or [],
        'house_cusps': natal_data.get('house_cusps') or {},
    }
    planet_positions = nce.extract_planet_positions(extract_input)
    houses = nce.extract_houses(extract_input, planets=planet_positions) if not no_birth_time else []
    aspects_norm = nce.extract_aspects(extract_input, planets=planet_positions)
    pos_by_name = {p['name']: p for p in planet_positions}

    sun_sign = natal_data.get('sun_sign') or ''
    moon_sign = natal_data.get('moon_sign') or ''
    asc_sign = natal_data.get('ascendant_sign') or ''

    # Préface — AI blocks ou fallback statique
    if not preface_blocks:
        # Import local pour permettre un stub des tests sans réseau
        try:
            from services.natal_preface_generator import _static_fallback
            preface_blocks = _static_fallback(prenom)
        except Exception:
            preface_blocks = []

    book_data = book_data or {}

    def editorial(slug, title, text):
        blocks = [ChapterBlock(BlockKind.PARAGRAPH, {'text': paragraph})
                  for paragraph in str(text or '').split('\n\n') if paragraph.strip()]
        return Chapter(slug=slug, title=title, blocks=blocks)

    # Construction des chapitres
    chapters: list[Chapter] = []
    chapters.append(_chapter_preface(preface_blocks or [], prenom))
    chapters.append(_chapter_synthese(
        prenom, birth_date_fr, sun_sign, moon_sign, asc_sign,
        no_birth_time, aspects_norm, houses, chart_png_bytes,
    ))

    for key, title in [
        ('element_analysis', 'Votre élément dominant'),
        ('modality_analysis', 'Votre manière de vous mettre en mouvement'),
        ('trio_synthesis', 'Votre signature personnelle'),
    ]:
        if str(book_data.get(key) or '').strip():
            chapters.append(editorial(key, title, book_data[key]))

    planets_narr = natal_data.get('planets') or []
    if planets_narr:
        chapters.append(_chapter_planets(planets_narr, pos_by_name, no_birth_time))

    if houses and not no_birth_time:
        house_chapter = _chapter_houses(houses)
        # Insert the actual personalised prose after its corresponding house title.
        enriched = []
        if book_data.get('houses_intro'):
            enriched.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': book_data['houses_intro']}))
        house_index = 0
        for block in house_chapter.blocks:
            enriched.append(block)
            if block.kind == BlockKind.H2:
                house_index += 1
            if block.kind == BlockKind.PARAGRAPH and house_index:
                text = str(book_data.get(f'house_{house_index}') or '').strip()
                if text:
                    enriched.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': text}))
        house_chapter.blocks = enriched
        chapters.append(house_chapter)

    if aspects_norm:
        chapters.append(_chapter_aspects(aspects_norm))

    synthese = (natal_data.get('synthese_aspects') or '').strip()
    if synthese:
        chapters.append(_chapter_synthese_finale(synthese))

    for key, title in [
        ('aspects_harmonieux_body', book_data.get('aspects_harmonieux_headline') or 'Vos ressources et vos harmonies'),
        ('aspects_tensions_body', book_data.get('aspects_tensions_headline') or 'Vos tensions et vos chemins d’évolution'),
        ('rare_aspect_body', book_data.get('rare_aspect_headline') or 'Votre note singulière'),
        ('year_ahead', 'Mettre votre thème en perspective'),
    ]:
        if str(book_data.get(key) or '').strip():
            chapters.append(editorial(key, title, book_data[key]))

    # Renumérote le roman_num en fonction de l'ordre réel
    _ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII'}
    for i, ch in enumerate(chapters, start=1):
        ch.order = i
        new_rn = _ROMAN.get(i, str(i))
        if ch.roman_num != new_rn:
            ch.roman_num = new_rn
            if ch.blocks and ch.blocks[0].kind == BlockKind.CHAPTER_OPENING:
                ch.blocks[0].data['roman_num'] = new_rn

    manuscript = Manuscript(
        session_id=session_id or f'natal-{prenom.lower()}-{int(datetime.now(timezone.utc).timestamp())}',
        user_email=user_email,
        first_name=prenom,
        birth_data=BirthData(date_iso=birth_date or '', time_hhmm=natal_data.get('birth_time'),
                             city=natal_data.get('birth_city') or '', country_code='FR'),
        astro_data={
            'sun_sign': sun_sign,
            'moon_sign': moon_sign,
            'ascendant_sign': asc_sign,
            'tier': natal_data.get('tier', 'legacy'),
            'planet_count': len(planets_narr),
            'house_count': len(houses),
            'aspect_count': len(aspects_norm),
            'has_toc': True,
            'planets': planet_positions,
            'aspects': aspects_norm,
            'houses': houses,
            'no_birth_time': no_birth_time,
        },
        edition=Edition.NUMERIQUE,
        chapters=chapters,
        design_version='plume-book-flow-2026-10',
        created_at=datetime.now(timezone.utc),
    )
    return manuscript
