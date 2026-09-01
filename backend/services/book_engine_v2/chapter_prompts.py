"""chapter_prompts — Chaîne anti-slop pour les 12 chapitres du socle.

Chaque chapitre expose :
  - `signature_extractor(astro_data, first_name) -> dict` : les variables astro
    EXACTES à injecter dans le prompt (degrés, signes, maisons, aspects).
  - `USER_PROMPT` : le template Jinja-like avec placeholders `{var}`.
  - `structure_notes` : documentation interne (nombre de sections, etc.)

La fonction publique `generate_chapter_blocks(slug, ...)` route vers la bonne
spec et appelle Claude Sonnet 4-6 via emergentintegrations (LlmChat).

Toutes les prompts partagent :
  - Le même SYSTEM_PROMPT (voix Plume Astrale, blacklist)
  - Le même format JSON de sortie (`{blocks: [...]}`)

Voir /app/backend/services/book_engine/prose_generator.py pour l'infrastructure
LLM (déjà en place — on la réutilise).
"""
from __future__ import annotations
import logging
from typing import Callable, Optional

from services.book_engine.domain import ChapterBlock
from services.book_engine.prose_generator import (
    SYSTEM_PROMPT,
    _call_claude,
    _parse_json_blocks,
    _blocks_to_chapter_blocks,
    _fallback_chapter_iv,
    extract_venus_signature,
    _fmt_sign_fr,
    _fmt_house,
    _fmt_deg,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Signature extractors — extraient les variables spécifiques
# ═══════════════════════════════════════════════════════════════════
def _planet(astro: dict, name: str) -> dict:
    """Retourne {sign_fr, house_fr, degree, retrograde} pour une planète EN lowercase."""
    p = (astro.get('planets') or {}).get(name.lower()) or {}
    return {
        'sign_fr': _fmt_sign_fr(p.get('sign', '')) or '—',
        'house_fr': _fmt_house(p.get('house')),
        'degree': _fmt_deg(p.get('degree')),
        'retrograde': bool(p.get('retrograde') or p.get('is_retrograde')),
    }


def sig_generic(astro: dict, first_name: str) -> dict:
    """Signature « toutes planètes » — utilisable par presque tous les chapitres."""
    planets = ('sun','moon','mercury','venus','mars','jupiter','saturn','uranus','neptune','pluto','chiron')
    out: dict = {'first_name': first_name}
    for p in planets:
        d = _planet(astro, p)
        out[p] = d
        out[f'{p}_sign'] = d['sign_fr']
        out[f'{p}_house'] = d['house_fr']
        out[f'{p}_deg'] = d['degree']
        out[f'{p}_retro'] = ' · en rétrogradation' if d['retrograde'] else ''
    # Ascendant depuis houses[0]
    houses = astro.get('houses') or []
    if houses and isinstance(houses, list):
        from .wheel import _to_longitude_deg, _SIGN_ORDER
        asc_lon = _to_longitude_deg(houses[0])
        if asc_lon is not None:
            out['asc_sign'] = _SIGN_ORDER[int(asc_lon // 30) % 12].upper()
            out['mc_sign'] = _SIGN_ORDER[int(_to_longitude_deg(houses[9]) // 30) % 12].upper() if houses[9] else '—'
        else:
            out['asc_sign'] = out['mc_sign'] = '—'
    else:
        out['asc_sign'] = out['mc_sign'] = '—'
    return out


# ═══════════════════════════════════════════════════════════════════
# Prompts par chapitre (11 restants après Chapitre IV déjà fait)
# ═══════════════════════════════════════════════════════════════════

# Chaque prompt suit la MÊME structure minimale :
#   1. paragraph_dropcap ouverture
#   2. h2 + 2 paragraphes
#   3. encart
#   4. h2 + 2 paragraphes
#   5. quote_literary
#   6. h2 + 1-2 paragraphes
#   7. encart final "VOTRE CLÉ"
#   8. quote_breath

_STRUCTURE_JSON = """
FORMAT DE SORTIE (JSON strict, aucun texte hors du JSON) :
{{
  "blocks": [
    {{"kind": "paragraph_dropcap", "data": {{"text": "..."}}}},
    {{"kind": "h2", "data": {{"text": "..."}}}},
    {{"kind": "paragraph", "data": {{"text": "..."}}}},
    {{"kind": "paragraph", "data": {{"text": "..."}}}},
    {{"kind": "encart", "data": {{"label": "...", "text": "..."}}}},
    {{"kind": "h2", "data": {{"text": "..."}}}},
    {{"kind": "paragraph", "data": {{"text": "..."}}}},
    {{"kind": "paragraph", "data": {{"text": "..."}}}},
    {{"kind": "quote_literary", "data": {{"text": "...", "source": "Auteur, Œuvre"}}}},
    {{"kind": "h2", "data": {{"text": "..."}}}},
    {{"kind": "paragraph", "data": {{"text": "..."}}}},
    {{"kind": "encart", "data": {{"label": "VOTRE CLÉ", "text": "..."}}}},
    {{"kind": "quote_breath", "data": {{"text": "..."}}}}
  ]
}}
"""


CHAPTER_PROMPTS: dict[str, str] = {
    # ─── Chapitre II — Les grandes lignes ───
    'grandes_lignes': """Rédige le CHAPITRE II « Les grandes lignes de vous » du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES :
- Soleil : {sun_sign} · {sun_house} · {sun_deg}
- Lune : {moon_sign} · {moon_house} · {moon_deg}
- Ascendant : {asc_sign}

STRUCTURE (10 pages A5, ~2200 mots) :
Commence par « Ce qui vous constitue tient en trois lignes : {sun_sign} qui allume, {moon_sign} qui apaise, {asc_sign} qui accueille. » Puis développe l'articulation de ces trois voix, l'élément dominant, le mode dominant (cardinal/fixe/mutable), les hémisphères Nord/Sud/Est/Ouest. Pas de généralité "en général les Soleil en X".
Cite une auteur classique française (Yourcenar, Colette, Duras, Beauvoir) qui résonne avec {sun_sign}.
""" + _STRUCTURE_JSON,

    # ─── Chapitre III — Trio identitaire ───
    'trio_identitaire': """Rédige le CHAPITRE III « Votre trio identitaire » du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES :
- Soleil : {sun_sign} · {sun_house} · {sun_deg}{sun_retro}
- Lune : {moon_sign} · {moon_house} · {moon_deg}
- Ascendant : {asc_sign}

STRUCTURE (14 pages A5, ~3000 mots — trois voix analysées séparément puis mises en dialogue) :
Trois sections principales : Le Soleil (ce qui rayonne), la Lune (ce qui a besoin d'ombre), l'Ascendant (ce qui accueille le monde). Chaque section ancrée dans le degré et la maison exacte. Ne pas dire « le Soleil en Lion est solaire », dire « à {sun_deg} de {sun_sign}, votre Soleil se pose en {sun_house}. Cela se joue dans [domaine concret de la maison] ».
Cite une auteur classique française qui résonne avec l'Ascendant {asc_sign}.
""" + _STRUCTURE_JSON,

    # ─── Chapitre V — Vos façons d'entrer en relation ───
    'facons_relations': """Rédige le CHAPITRE V « Vos façons d'entrer en relation » du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES :
- Vénus : {venus_sign} · {venus_house} · {venus_deg}{venus_retro}
- Mars : {mars_sign} · {mars_house} · {mars_deg}{mars_retro}
- Lune : {moon_sign} · {moon_house} · {moon_deg}
- Descendant (opposé Ascendant) : opposé de {asc_sign}

STRUCTURE (10 pages A5) :
Sections : ce que vous cherchez chez l'autre (Descendant), comment vous entrez en lien (Vénus), comment vous défendez (Mars), les besoins tendres (Lune). Le Descendant est l'axe crucial ici.
Cite une lettre ou un fragment (Barthes, Fragments d'un discours amoureux, ou Duras, Hiroshima).
""" + _STRUCTURE_JSON,

    # ─── Chapitre VI — Vos forces naturelles ───
    'forces_naturelles': """Rédige le CHAPITRE VI « Vos forces naturelles » du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES :
- Jupiter : {jupiter_sign} · {jupiter_house} · {jupiter_deg}{jupiter_retro}
- Soleil : {sun_sign} · {sun_house} · {sun_deg}
- Mercure : {mercury_sign} · {mercury_house} · {mercury_deg}{mercury_retro}

STRUCTURE (10 pages A5) :
Ce que {first_name} sait faire sans y penser. Jupiter en {jupiter_sign} = domaine de facilité (les 3-4 gestes qui viennent naturellement dans ce signe). Soleil + Mercure = comment ces forces s'expriment.
Pas de « vous êtes doué·e pour X » vague — donner deux gestes CONCRETS dérivés des positions.
Cite un moraliste classique (La Rochefoucauld, La Bruyère) ou Camus.
""" + _STRUCTURE_JSON,

    # ─── Chapitre VII — Vos passages étroits ───
    'passages_etroits': """Rédige le CHAPITRE VII « Vos passages étroits » du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES :
- Saturne : {saturn_sign} · {saturn_house} · {saturn_deg}{saturn_retro}
- Chiron : {chiron_sign} · {chiron_house} · {chiron_deg}
- Pluton : {pluto_sign} · {pluto_house} · {pluto_deg}{pluto_retro}

STRUCTURE (12 pages A5 — plus long car sujet dense) :
Les endroits où le ciel demande courage. Saturne = la contrainte structurante, Chiron = la blessure devenue don, Pluton = la mue profonde. Sans complaisance dans la difficulté, sans consolation faible. Ton tendre-ferme.
Cite Rilke (Lettres à un jeune poète) ou Cioran (dans une forme apaisée).
""" + _STRUCTURE_JSON,

    # ─── Chapitre VIII — Votre travail dans le monde ───
    'travail_monde': """Rédige le CHAPITRE VIII « Votre travail dans le monde » du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES :
- Milieu du Ciel (cusp Maison X) : {mc_sign}
- Saturne : {saturn_sign} · {saturn_house} · {saturn_deg}
- Jupiter : {jupiter_sign} · {jupiter_house}
- Soleil : {sun_sign} · {sun_house}

STRUCTURE (10 pages A5) :
Ce que {first_name} est venue faire. MC en {mc_sign} = orientation vocationnelle. Pas de « métier idéal » — parler d'une POSTURE au monde, d'un rythme de contribution. Deux paragraphes ancrés dans la Maison X, un paragraphe sur ce que Saturne y ajoute.
Cite Hannah Arendt (Condition de l'homme moderne) ou Simone Weil (L'Enracinement).
""" + _STRUCTURE_JSON,

    # ─── Chapitre IX — Grandes dynamiques ───
    'dynamiques_vie': """Rédige le CHAPITRE IX « Vos grandes dynamiques de vie » du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES :
- Nœud Nord (direction) : à ancrer dans le sujet
- Axe Ascendant/Descendant : {asc_sign} / opposé
- Axe MC/FC : {mc_sign} / opposé
- Soleil : {sun_sign} · {sun_house}

STRUCTURE (10 pages A5) :
Les axes qui traversent chaque année de la vie. Deux axes majeurs (AS/DS = individu/relation, MC/FC = accomplir/racines) + Nœud Nord = direction évolutive. Traiter cela comme une géographie intime, pas comme un horoscope.
Cite Colette (La Naissance du jour) ou Yourcenar (Mémoires d'Hadrien).
""" + _STRUCTURE_JSON,

    # ─── Chapitre X — Le temps qui vous traverse ───
    'temps_traverse': """Rédige le CHAPITRE X « Le temps qui vous traverse » du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES :
- Saturne : {saturn_sign} · {saturn_house} · {saturn_deg}
- Jupiter : {jupiter_sign} · {jupiter_house}
- Lune : {moon_sign} (cycle mensuel)
- Retour de Saturne (29-30 ans, puis 58-59 ans)

STRUCTURE (10 pages A5) :
Les cycles que {first_name} n'a pas choisis mais qu'elle habite. Le retour de Saturne (rite de passage 29-30 ans), le cycle jupitérien de 12 ans, le retour lunaire chaque mois. Sujet dense mais à traiter en langage humain concret.
Cite Bachelard (La Poétique du temps) ou Marc Aurèle.
""" + _STRUCTURE_JSON,

    # ─── Chapitre XI — Chemin personnel ───
    'chemin_personnel': """Rédige le CHAPITRE XI « Votre chemin personnel » du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES :
- Nœud Nord : direction évolutive
- Chiron : {chiron_sign} · {chiron_house} · {chiron_deg}
- Pluton évolutif : {pluto_sign} · {pluto_house}

STRUCTURE (10 pages A5) :
Ce vers quoi l'âme incline. Le Nœud Nord (direction d'évolution) — parler de ce que {first_name} est en train de devenir, non de ce qu'elle est. Chiron = la blessure devenue don. Pluton = la mue profonde. Un chapitre à la fois plus mystique et plus ancré.
Cite Ricœur (Soi-même comme un autre) ou Simone Weil.
""" + _STRUCTURE_JSON,

    # ─── Chapitre XII — Portrait astral (synthèse) ───
    'synthese_portrait': """Rédige le CHAPITRE XII « Portrait astral » — la SYNTHÈSE finale du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES :
- Soleil : {sun_sign} · {sun_house}
- Lune : {moon_sign} · {moon_house}
- Ascendant : {asc_sign}
- Vénus : {venus_sign} · {venus_house}
- Mars : {mars_sign} · {mars_house}
- Saturne : {saturn_sign} · {saturn_house}

STRUCTURE (8 pages A5 — plus dense, moins de blocs, plus de blanc) :
Trois pages pour se souvenir de tout. Un texte plus court, plus dense, plus poétique. Reprend les 3-4 signatures les plus fortes du thème et les tresse en un portrait tenu. Pas de récapitulatif scolaire — une lettre de conclusion.
Cite Rilke, Rimbaud, ou Louise Glück (poétesse Nobel 2020).
""" + _STRUCTURE_JSON,

    # ─── Chapitre I — Votre ciel de naissance (ouverture + prose supplémentaire au-delà de la roue) ───
    'ciel_naissance': """Rédige le prologue prose du CHAPITRE I « Votre ciel de naissance » du Livre Astral de {first_name}.

DONNÉES ASTRALES :
- Soleil : {sun_sign} · {sun_house} · {sun_deg}
- Lune : {moon_sign} · {moon_house} · {moon_deg}
- Ascendant : {asc_sign}
- Milieu du Ciel : {mc_sign}

CONTEXTE : ce chapitre inclut DÉJÀ la roue céleste graphique en page 2 et un tableau positions/aspects en page 3. Ta prose vient APRÈS ces éléments visuels. Elle doit accompagner le lecteur devant sa roue, lui expliquer ce qu'il voit, sans redondance avec le tableau. 6 pages A5, ~1400 mots.

STRUCTURE : ouverture qui parle du moment de la naissance (pas de "au moment fatidique"), puis explication de ce qu'est la roue céleste, puis un premier zoom sur le trio Soleil/Lune/Ascendant sans tout dévoiler (le chapitre III le fera).
Cite Bachelard, Colette, ou Camus.
""" + _STRUCTURE_JSON,

    # ═══════════════════════════════════════════════════════════════════
    # ADD-ONS (Deuxième partie du livre — chapitres facultatifs)
    # ═══════════════════════════════════════════════════════════════════

    # ─── Add-on I — L'Arbre de Vie (Kabbale) ───
    'arbre_de_vie': """Rédige le CHAPITRE ADDITIONNEL I « L'Arbre de Vie » du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES :
- Soleil : {sun_sign} · {sun_house} · {sun_deg}
- Lune : {moon_sign} · {moon_house}
- Mercure : {mercury_sign} · {mercury_house}
- Vénus : {venus_sign} · {venus_house}
- Mars : {mars_sign} · {mars_house}
- Jupiter : {jupiter_sign} · {jupiter_house}
- Saturne : {saturn_sign} · {saturn_house}

STRUCTURE (12 pages A5, ~2600 mots) :
La Kabbale propose 10 stations (les Séphiroth) sur l'Arbre de Vie, chacune correspondant à une qualité de conscience. Traite l'appariement CLASSIQUE : Kether/Neptune (couronne), Chokhmah/Uranus (sagesse), Binah/Saturne (compréhension), Chesed/Jupiter (grâce), Guévourah/Mars (rigueur), Tiphéreth/Soleil (beauté, cœur), Netzach/Vénus (victoire), Hod/Mercure (splendeur), Yesod/Lune (fondation), Malkhouth/Terre (royaume).

Ton ferme et sobre — pas d'ésotérisme creux, pas de "vibrations séphirothiques". Ancre chaque Séphirah dans la position exacte de la planète correspondante chez {first_name}, en donnant UNE image concrète issue de sa vie possible (par ex. "Saturne en {saturn_sign} dessine Binah comme un savoir lent, celui qu'on n'accepte qu'après trois hivers").

Cite Gershom Scholem (La Kabbale et sa symbolique) OU Emmanuel Levinas.
""" + _STRUCTURE_JSON,

    # ─── Add-on II — L'Ailleurs qui vous appelle (Astrocartographie) ───
    'astrocartographie': """Rédige le CHAPITRE ADDITIONNEL II « L'Ailleurs qui vous appelle » du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES :
- Soleil : {sun_sign} · {sun_house} · {sun_deg}
- Lune : {moon_sign} · {moon_house}
- Jupiter : {jupiter_sign} · {jupiter_house}
- Vénus : {venus_sign} · {venus_house}
- Ascendant : {asc_sign}
- Milieu du Ciel : {mc_sign}

STRUCTURE (14 pages A5, ~3000 mots) :
L'astrocartographie projette les axes planétaires (AS/DS/MC/IC) sur une mappemonde. Chaque planète trace 4 lignes autour du globe. Sous chaque ligne, le thème de {first_name} s'exprime différemment.

Traite quatre GRANDS AXES humains :
1. Ligne Soleil-MC : là où on veut être reconnu·e → parle de l'endroit où {first_name} apparaîtrait dans sa lumière (métaphore de ville sans NOMMER de ville — chaque signe correspond à un archétype de lieu : {sun_sign} = quel type de paysage ?)
2. Ligne Lune-IC : là où on veut poser sa tête → refuge
3. Ligne Vénus-DS : là où l'amour vient plus facilement
4. Ligne Jupiter-AS : là où la croissance s'ouvre

Ton adulte, jamais "consultez votre carte" — plutôt inviter à SENTIR quel pays a réveillé quelque chose.
Cite Nicolas Bouvier (L'Usage du monde) OU Sylvain Tesson.
""" + _STRUCTURE_JSON,

    # ─── Add-on III — Voyage Karmique (Nœuds lunaires · Saturne · Chiron · Pluton) ───
    'karma_destin': """Rédige le CHAPITRE ADDITIONNEL III « Voyage Karmique » du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES :
- Nœud Nord : ancré au chapitre (direction évolutive)
- Nœud Sud : opposé du Nœud Nord (bagage porté)
- Saturne : {saturn_sign} · {saturn_house} · {saturn_deg}
- Chiron : {chiron_sign} · {chiron_house} · {chiron_deg}
- Pluton : {pluto_sign} · {pluto_house} · {pluto_deg}{pluto_retro}

STRUCTURE (16 pages A5, ~3400 mots) — sujet dense, plus long :
Le mot "karma" est piégé. Ici, on l'entend au sens de "ce que l'âme a apporté" — pas de dette moralisatrice, pas de réincarnation littérale. C'est une manière de lire les axes du thème qui parlent d'héritage.

Sections :
1. Le Nœud Sud comme bagage — ce que {first_name} sait déjà faire "trop bien" et qui l'endort
2. Le Nœud Nord comme apprentissage — ce vers quoi ça tire, avec inconfort
3. Saturne comme structure — le seuil qu'on ne franchit qu'à 29-30 ans
4. Chiron comme blessure originelle — non pas à guérir mais à habiter
5. Pluton comme mue — les transformations qu'on ne choisit pas

Ton tendre-ferme. Zéro jargon new age. Cite Rilke (Lettres à un jeune poète) OU Etty Hillesum.
""" + _STRUCTURE_JSON,

    # ─── Add-on IV — L'Heure Retrouvée (rectification symbolique) ───
    'heure_retrouvee': """Rédige le CHAPITRE ADDITIONNEL IV « L'Heure Retrouvée » du Livre Astral de {first_name}.

CONTEXTE PARTICULIER : ce chapitre s'adresse à quelqu'un qui NE CONNAÎT PAS son heure exacte de naissance. On ne peut donc pas donner de position d'Ascendant ni de maison précise. On travaille en SYMBOLIQUE : chercher dans les faits de sa vie l'écho d'une heure.

DONNÉES ASTRALES (utilisables sans heure) :
- Soleil : {sun_sign} · {sun_deg}
- Lune : {moon_sign} · {moon_deg}
- Vénus : {venus_sign}
- Mars : {mars_sign}

STRUCTURE (10 pages A5, ~2200 mots) :
1. Ouverture : "Il y a une heure que vous ne connaissez pas. Ce chapitre ne prétend pas la retrouver — il prétend l'écouter."
2. Les 12 Ascendants possibles → très brève évocation de chacun (12 paragraphes courts de 3-4 lignes, un par signe). Chaque Ascendant est une hypothèse de vie, non un diagnostic.
3. Comment sentir : la première chose qu'on voit dans un miroir le matin, l'endroit du corps qui parle en premier quand on est fatigué·e, le sujet d'obsession dans les vingt premières années.
4. Un exercice : demander à trois personnes proches quel mot elles utiliseraient pour vous décrire — souvent leurs mots pointent l'Ascendant.

Ton humble, laisse le mystère. Cite Christian Bobin OU Pierre Michon.
""" + _STRUCTURE_JSON,

    # ─── Add-on V — Étoiles Fixes ───
    'etoiles_fixes': """Rédige le CHAPITRE ADDITIONNEL V « Étoiles Fixes » du Livre Astral de {first_name}.

DONNÉES ASTRALES (traitement symbolique — on ne fait pas de calcul d'orbe fine ici) :
- Soleil : {sun_sign} · {sun_deg}
- Lune : {moon_sign} · {moon_deg}
- Ascendant : {asc_sign}
- Milieu du Ciel : {mc_sign}

STRUCTURE (10 pages A5, ~2200 mots) :
Les étoiles fixes sont les vraies étoiles du ciel (contrairement aux planètes qui se déplacent). Quatre grandes étoiles royales portent des noms qui résonnent dans toutes les cultures :
- Regulus (au cœur du Lion, la royauté) — 29° Lion
- Aldébaran (l'œil du Taureau, la force calme) — 9° Gémeaux
- Antarès (le cœur du Scorpion, la passion consumée) — 9° Sagittaire
- Fomalhaut (la bouche du Poisson, la parole poétique) — 3° Poissons

Traite chacune : ce qu'elle apporte quand elle est proche d'une planète du thème. Précise que pour {first_name}, il faudrait un calcul d'orbe fine — ce chapitre est un guide pour SENTIR laquelle des quatre l'appelle. Puis évoque Sirius (l'étoile du chien, la loyauté antique), Vega, Aldébaran (déjà cité) et Régulus comme les autres phares.

Cite Alain (Propos sur le bonheur) OU Marguerite Yourcenar (Mémoires d'Hadrien, passage sur Antinoüs et les astres).
""" + _STRUCTURE_JSON,

    # ─── Add-on VI — Symboles Sabiens ───
    'symboles_sabiens': """Rédige le CHAPITRE ADDITIONNEL VI « Symboles Sabiens » du Livre Astral de {first_name}.

DONNÉES ASTRALES EXACTES :
- Soleil : {sun_sign} · {sun_deg}  (arrondir au degré supérieur pour trouver le Sabien : ex. 24°25 = 25e degré)
- Lune : {moon_sign} · {moon_deg}
- Ascendant : {asc_sign}
- Milieu du Ciel : {mc_sign}

CONTEXTE : les 360 Symboles Sabiens (Marc Edmund Jones, 1925) attribuent une IMAGE à chaque degré du zodiaque. Chaque image est une scène concrète, souvent surprenante ("Un vieil homme portant du bois pour l'hiver", "Une femme qui rêve devant sa fenêtre").

STRUCTURE (12 pages A5, ~2600 mots) :
1. Ouverture : présentation courte des Sabiens et de leur origine.
2. Zoom sur le degré du Soleil de {first_name} : à {sun_deg} de {sun_sign}, si tu cites un Sabien authentique, cite-le en italiques puis développe l'écho. Si tu ne connais pas le Sabien exact, INVENTE une image dans le style (une scène concrète en une phrase avec un article défini "Une", "Un") mais SIGNALE-le honnêtement ("Le Sabien de ce degré, tel qu'il pourrait être formulé aujourd'hui...").
3. Idem pour la Lune, l'Ascendant, le Milieu du Ciel.
4. Une clôture : ce que ces quatre images ensemble racontent de {first_name}.

Ton poétique-concret, jamais abstrait. Cite Dane Rudhyar (An Astrological Mandala) OU Julien Gracq.
""" + _STRUCTURE_JSON,
}


# ═══════════════════════════════════════════════════════════════════
# API publique
# ═══════════════════════════════════════════════════════════════════
async def generate_chapter_blocks(
    *,
    slug: str,
    first_name: str,
    astro_data: dict,
    session_id: str,
) -> list[ChapterBlock]:
    """Génère la liste de `ChapterBlock` pour un chapitre donné.

    Route selon `slug`. Réutilise la chaîne Claude Sonnet 4-6 existante.
    En cas d'échec LLM, retourne un fallback minimal (jamais de PDF cassé).
    """
    if slug == 'facon_aimer':
        # Déjà géré par le module historique — on garde la même route
        from services.book_engine.prose_generator import generate_chapter_iv_love
        return await generate_chapter_iv_love(
            first_name=first_name, astro_data=astro_data, session_id=session_id,
        )

    prompt_template = CHAPTER_PROMPTS.get(slug)
    if not prompt_template:
        logger.warning(f'[chapter_prompts] no prompt for slug={slug} — fallback')
        return []

    sig = sig_generic(astro_data, first_name)
    try:
        user = prompt_template.format(**sig)
    except KeyError as e:
        logger.error(f'[chapter_prompts] missing key in signature for {slug}: {e}')
        return []

    try:
        raw = await _call_claude(
            SYSTEM_PROMPT, user, session_id=f'chapter_{slug}_{session_id}',
        )
        dicts = _parse_json_blocks(raw)
        blocks = _blocks_to_chapter_blocks(dicts)
        if not blocks:
            raise ValueError('no valid blocks')
        return blocks
    except Exception as e:
        logger.error(f'[chapter_prompts] LLM failed for {slug}: {e}')
        return []  # renderer utilisera un placeholder léger
