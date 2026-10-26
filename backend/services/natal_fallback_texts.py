"""natal_fallback_texts — Textes de repli pour les sections LLM du Thème Natal.

Contexte : chaque livre contient ~20 sections rédigées par GPT. Si une
génération échoue ou renvoie une chaîne vide, la page du PDF devenait
blanche. Ce module fournit un texte éditorial neutre mais signifiant,
rédigé dans la voix Soléna, pour chaque section — jamais de "Lorem ipsum"
ni de placeholder visible.

Usage :
    from services.natal_fallback_texts import with_fallback

    body = with_fallback(book_data.get('element_analysis'), 'element_analysis',
                         prenom=prenom, element='Feu')
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _p(text: str) -> str:
    """Marque un texte de repli → log + wrap paragraphe HTML."""
    return f'<p>{text}</p>'


FALLBACKS = {
    'dedication': (
        "À {prenom}, dont le ciel singulier mérite d'être lu avec attention. "
        "Que ces pages soient une porte entrouverte sur ta nature profonde — "
        "non pour la fixer, mais pour la célébrer dans ce qu'elle a d'unique."
    ),
    'element_analysis': (
        "Ton élément dominant trace la couleur de ta façon d'être au monde. "
        "C'est le filtre premier à travers lequel tu reçois les impressions "
        "et à travers lequel tu réponds. Comprendre son action, c'est "
        "reconnaître ce qui vient de toi avant même la réflexion."
    ),
    'modality_analysis': (
        "Ta modalité dominante décrit la cadence de ton mouvement intérieur. "
        "Elle dit comment tu démarres, comment tu persistes, comment tu "
        "adaptes. Nommer cette cadence, c'est apprendre à ne plus se "
        "reprocher ce qui est, chez toi, un juste rythme."
    ),
    'trio_synthesis': (
        "Ton Soleil, ta Lune et ton Ascendant forment un triangle "
        "fondamental : ce que tu cherches à devenir, ce dont tu as besoin "
        "pour te sentir en sécurité, et la porte par laquelle tu entres dans "
        "le monde. Chacun joue sa partition, et c'est leur dialogue qui "
        "fait ta musique."
    ),
    'aspects_harmonieux_body': (
        "Les aspects dits « harmonieux » ne sont pas des facilités : ce "
        "sont des évidences. Des zones où quelque chose circule sans que tu "
        "aies à y penser. Les reconnaître, c'est apprendre à t'appuyer "
        "dessus plutôt que de les tenir pour acquis."
    ),
    'aspects_tensions_body': (
        "Les tensions de ton thème ne sont pas des défauts à corriger — ce "
        "sont des muscles. Elles exigent un effort qui, à la longue, "
        "sculpte. Ce que tu n'arrives pas à faire sans peine, tu finis "
        "souvent par le faire mieux que ceux à qui c'était donné."
    ),
    'rare_aspect_body': (
        "Il existe dans ton ciel une configuration peu commune : une note "
        "rare, une couleur que peu portent. Elle ne te rend pas supérieur, "
        "elle te rend singulier — et c'est précisément cette singularité "
        "que tu portes au monde comme contribution."
    ),
    'houses_intro': (
        "Les douze maisons sont les domaines concrets où tes planètes "
        "s'incarnent. Si les planètes disent « quoi » et les signes "
        "« comment », les maisons disent « où ». Elles ancrent le ciel "
        "dans ta vie quotidienne : relations, travail, foyer, apprentissage, "
        "mystères. Ce chapitre détaille, pour chaque maison active, le "
        "terrain de vie qu'elle colore chez toi."
    ),
    'year_ahead': (
        "L'année qui vient porte, pour chaque thème, des accents propres. "
        "Les transits en cours — Jupiter qui ouvre, Saturne qui structure, "
        "les lunaisons qui rythment — viennent dialoguer avec ton ciel de "
        "naissance. Garde en mémoire que l'astrologie n'enferme pas : elle "
        "éclaire. Ce qui est écrit n'est jamais ce qui est dû, c'est ce "
        "qui est possible si tu t'y engages consciemment."
    ),
    'conclusion': (
        "Ce livre n'épuise pas ton ciel. Il en pose les contours principaux, "
        "pour que tu puisses y revenir — à des moments charnières, pour "
        "comprendre ce qui bouge, ou simplement pour te rappeler qui tu es "
        "quand tu doutes."
    ),
}

# Headlines de repli (quand le LLM ne fournit même pas un titre)
FALLBACKS_HEADLINES = {
    'aspects_harmonieux_headline': 'La grâce en toi',
    'aspects_tensions_headline': 'Le nœud qui te forge',
    'rare_aspect_headline': 'Ta note rare',
}


def with_fallback(body: Any, section: str, **ctx: Any) -> str:
    """Retourne `body` si non-vide, sinon le texte de repli de la section.

    Formate les placeholders `{prenom}`, `{element}`, etc. du fallback
    avec les kwargs fournis. Si le fallback n'existe pas pour la section,
    retourne la chaîne originale (potentiellement vide) sans crasher.
    """
    if body:
        s = str(body).strip()
        if len(s) >= 20:
            return str(body)
    tmpl = FALLBACKS.get(section)
    if not tmpl:
        return str(body or '')
    try:
        text = tmpl.format(prenom=ctx.get('prenom', 'cher lecteur'), **{
            k: v for k, v in ctx.items() if k != 'prenom'
        })
    except (KeyError, ValueError):
        text = tmpl  # format fail → raw template
    logger.info(f'[natal_fallback] used fallback for section={section!r}')
    return _p(text)


def headline_with_fallback(headline: Any, section: str, default: str = '') -> str:
    """Idem pour les titres de section."""
    if headline and str(headline).strip():
        return str(headline)
    return FALLBACKS_HEADLINES.get(section, default)


__all__ = ['with_fallback', 'headline_with_fallback', 'FALLBACKS']
