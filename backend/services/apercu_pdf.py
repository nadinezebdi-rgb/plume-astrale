"""
apercu_pdf — Générateur d'aperçus 3 pages pour la Bibliothèque Plume Astrale.

Chaque aperçu = Couverture + Ouverture spectaculaire + Extrait poétique.
Objectif : rassurer les visiteurs de /nos-livres sur la qualité rédactionnelle
et visuelle avant l'achat, sans révéler le contenu personnalisé complet.

Cache mémoire par book_key (les PDFs sont statiques, prénom générique).
"""
from __future__ import annotations
import io
from typing import Dict, Optional

from services.pdf_luxury_theme import (
    build_luxury_doc, luxury_styles, luxury_bg,
    cover_page, opening_page, planet_analysis_page,
)


# ─────────────────────────────────────────────────────────────
# Contenu générique par livre — 3 pages qui montrent la voix Soléna
# sans révéler le contenu personnalisé.
# ─────────────────────────────────────────────────────────────
BOOK_PREVIEWS: Dict[str, dict] = {
    'natal': {
        'title': 'Thème Natal — Ultra',
        'cover_subtitle': 'Ton ciel de naissance, dévoilé.',
        'cover_slug': 'ciel_zodiaque',
        'opening_line': "Ton ciel n'a jamais été aussi clair.",
        'extract_planet': 'Soleil',
        'extract_sign': 'Ton signe',
        'extract_dialogue': 'Ta lumière intérieure — celle que tu n\'oses pas toujours faire briller — est écrite ici.',
        'extract_body': (
            'Chez toi, l\'identité se fabrique en marchant, en lisant dans les trains, en parlant '
            'jusqu\'à faire tomber les masques d\'une idée. Il y a une faim d\'air, de mouvement, '
            'de questions ouvertes sur la table comme des cartes encore chaudes.\n\n'
            'Tu avances en comparant, en reliant, en regardant les deux faces d\'un même visage '
            'sans vouloir en sacrifier une. Ta lumière n\'aime pas les frontières étroites : elle '
            'cherche une vérité qui respire, quelque chose de plus vaste que l\'opinion du jour.\n\n'
            '<i>[Cet aperçu s\'arrête ici — dans ton livre complet, ce chapitre s\'étend sur 4 pages, '
            'et 10 autres planètes t\'attendent, chacune avec son propre dialogue psychologique.]</i>'
        ),
    },
    'synastry': {
        'title': 'Astrologie relationnelle',
        'cover_subtitle': 'Ce que vos deux ciels se disent.',
        'cover_slug': 'couple',
        'opening_line': 'Vos deux ciels dansent — écoutez ce qu\'ils se murmurent.',
        'extract_planet': 'Votre lien',
        'extract_sign': 'Aspect majeur',
        'extract_dialogue': 'Il y a quelque chose entre vous deux que le hasard n\'explique pas.',
        'extract_body': (
            'Votre rencontre n\'appartient pas au calendrier ordinaire. Quand vos deux thèmes '
            's\'entrelacent, une géométrie précise apparaît : ta Vénus effleure sa Lune, ton Mars '
            'répond à son Ascendant, et là où vous croyez sentir le mystère, l\'astrologie voit '
            'un dessin d\'une netteté rare.\n\n'
            'Ce n\'est pas de l\'attraction gratuite. C\'est un dialogue que vos étoiles ont commencé '
            'avant vous — et qu\'il vous revient maintenant d\'incarner, avec lucidité, avec grâce.\n\n'
            '<i>[Ton livre relationnel complet analyse 12 aspects croisés, tes 5 langages d\'amour '
            'communs, et vos deux fenêtres cosmiques à venir — 25 pages.]</i>'
        ),
    },
    'kabbale': {
        'title': 'Arbre de Vie — Kabbalistique',
        'cover_subtitle': 'Tes dix Sephiroth, tes vingt-deux chemins.',
        'cover_slug': 'astral_mandala',
        'opening_line': 'Ton âme a un dessin — et il porte un nom hébreu.',
        'extract_planet': 'Tiphereth',
        'extract_sign': 'La Beauté',
        'extract_dialogue': 'Il y a en toi un centre — un point d\'or que rien ne peut te retirer.',
        'extract_body': (
            'La Sephira du milieu, Tiphereth, s\'appelle la Beauté. Elle est le cœur de l\'Arbre, '
            'là où le divin descend rencontrer l\'humain, là où l\'humain s\'élève rencontrer le divin. '
            'Chez toi, cette Sephira porte une empreinte solaire : ce qui te rend rayonnante n\'est '
            'jamais ce que tu forces, c\'est ce que tu incarnes.\n\n'
            'Les kabbalistes disent : « Tiphereth accueille la lumière, la contient sans la briser. » '
            'Ta mission passe par là — apprendre à porter ta propre beauté sans la dissimuler ni '
            'l\'exhiber.\n\n'
            '<i>[Ton Arbre complet cartographie tes 10 Sephiroth et les 22 chemins hébraïques '
            'qui les relient — 15 pages reliées cuir nuit.]</i>'
        ),
    },
    'astrocarto': {
        'title': 'Astrocartographie',
        'cover_subtitle': 'Où le monde te veut vraiment.',
        'cover_slug': 'astral_ciel',
        'opening_line': 'Chaque planète a une ligne — et chaque ligne, un pays.',
        'extract_planet': 'Ta ligne de Vénus',
        'extract_sign': 'Lieu d\'harmonie',
        'extract_dialogue': 'Il existe un endroit sur cette Terre où tu es objectivement plus aimée.',
        'extract_body': (
            'Ta ligne de Vénus traverse la planète comme une écriture invisible. Là où elle passe, '
            'ton charme se dilate, ta capacité à recevoir de l\'amour s\'ouvre, ton corps se pose '
            'enfin. Ce n\'est pas une superstition : c\'est une constatation faite par des dizaines '
            'de milliers de voyageurs depuis un siècle.\n\n'
            'Certaines villes, tu ne les as jamais visitées — et pourtant leur nom te fait quelque '
            'chose. Ton livre te dit lesquelles, pourquoi, et à quelle saison de ta vie t\'y rendre '
            'peut littéralement changer ta trajectoire.\n\n'
            '<i>[Ton livre complet trace tes 7 lignes planétaires sur la carte du monde et t\'indique '
            'précisément où vivre ta meilleure vie — 18 pages.]</i>'
        ),
    },
    'karmique': {
        'title': 'Pack Karmique',
        'cover_subtitle': 'L\'écrin ultime de ton âme.',
        'cover_slug': 'astral_silhouette',
        'opening_line': 'Ton âme se souvient — même quand toi, tu as oublié.',
        'extract_planet': 'Ton Nœud Nord',
        'extract_sign': 'Ta mission d\'âme',
        'extract_dialogue': 'Là où ton Nœud Nord pointe, c\'est là que ta vie devient enfin la tienne.',
        'extract_body': (
            'Le Nœud Nord n\'est pas une planète. C\'est un point mathématique — mais spirituellement, '
            'c\'est le plus dense de ton thème. Il indique la direction que ton âme a choisie pour '
            'cette incarnation, la matière qu\'elle veut travailler, la peau qu\'elle veut construire.\n\n'
            'Chez toi, cette flèche pointe vers un territoire précis de l\'expérience humaine — un '
            'territoire souvent inconfortable au début, puis libérateur. Ton Nœud Nord est la '
            'boussole silencieuse de ta vie ; ton livre karmique te la remet enfin dans la main.\n\n'
            '<i>[Le Pack Karmique réunit ton empreinte karmique, ton Arbre de Vie et ta synthèse '
            'd\'âme dans un seul écrin — 40 pages reliées.]</i>'
        ),
    },
}


# Cache mémoire — les aperçus sont statiques, une seule génération suffit
_CACHE: Dict[str, bytes] = {}


def build_apercu(book_key: str) -> Optional[bytes]:
    """Retourne les bytes d'un aperçu PDF 3 pages pour le livre demandé.

    Args:
        book_key : 'natal', 'synastry', 'kabbale', 'astrocarto', 'karmique'

    Returns:
        PDF bytes ou None si book_key inconnu.
    """
    if book_key not in BOOK_PREVIEWS:
        return None
    if book_key in _CACHE:
        return _CACHE[book_key]

    meta = BOOK_PREVIEWS[book_key]
    buf = io.BytesIO()
    doc = build_luxury_doc(buf, title=f'Aperçu — {meta["title"]}')
    styles = luxury_styles()
    story = []

    # Page 1 : Couverture générique (pas de prénom personnel)
    cover_page(
        story, styles,
        prenom=meta['title'],
        subtitle=meta['cover_subtitle'],
        illustration_slug=meta['cover_slug'],
    )

    # Page 2 : Ouverture spectaculaire
    opening_page(
        story, styles,
        prenom='Voyageuse',
        first_line=meta['opening_line'],
    )

    # Page 3 : Extrait poétique + dialogue Soléna + note de fin d'aperçu
    # (planet_analysis_page ajoute un PageBreak final, ce qui est OK — la note
    # de fin est intégrée directement dans le corps du texte, `extract_body`.)
    planet_analysis_page(
        story, styles,
        planet_name=meta['extract_planet'],
        sign=meta['extract_sign'],
        body_html=meta['extract_body'],
        dialogue_question=meta['extract_dialogue'],
    )

    doc.build(story, onFirstPage=luxury_bg, onLaterPages=luxury_bg)
    pdf_bytes = buf.getvalue()
    _CACHE[book_key] = pdf_bytes
    return pdf_bytes
