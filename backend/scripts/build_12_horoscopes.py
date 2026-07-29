"""
Génère 12 horoscopes journaliers PDFs (un par signe zodiacal).

Réutilise `build_horoscope_journalier_pdf()` du script de base, mais en
paramétrant le signe, ses dates, sa citation, ses conseils et ses infos
pratiques.
"""
from __future__ import annotations
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage,
    Table, TableStyle,
)
from reportlab.lib.colors import HexColor

from services.pdf_theme import font, GOLD, GOLD_LIGHT, CREAM, LAVENDER, MUTED
from services.pdf_luxury_theme import (
    luxury_bg, luxury_styles, illustration_url, _dl_image,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    pdfmetrics.registerFont(TTFont('Symbola', '/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf'))
    _SF = 'Symbola'
except Exception:
    _SF = 'Helvetica'


def _sym(t: str) -> str:
    return f'<font name="{_SF}">{t}</font>'


OUT_DIR = Path('/app/frontend/public/marketing/horoscopes')
OUT_DIR.mkdir(parents=True, exist_ok=True)

_MOIS_FR = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
_JOURS_FR = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']


# ─── Contenus par signe (12) — script Soléna, ton haut de gamme, zéro *
SIGNES = [
    {
        'slug': 'belier', 'nom': 'Bélier', 'sym': '♈', 'dates': '21 mars — 19 avril',
        'ouverture': "Aujourd'hui, ta première impulsion est la plus juste. Écoute-la avant que le mental n'arrive.",
        'energie': "Mars, ton maître, entre en dialogue avec le Soleil. Une clarté brute te traverse : ce qui doit avancer, tu le sais déjà. Ne débat plus, agis.",
        'amour': "Sois direct sans être brutal. Ton partenaire attend une vraie parole, pas une performance.",
        'carriere': "Une porte s'ouvre sur un projet qui te ressemble. Fonce, quitte à corriger la trajectoire ensuite.",
        'bien_etre': "Le corps a besoin de mouvement intense en début de journée. Ne le sédent pas.",
        'guidance': "Ne demande plus la permission pour être ce que tu es.",
        'pierre': 'Jaspe rouge', 'couleur': 'Rouge écarlate', 'aromate': 'Poivre noir',
        'heure': '6h — 10h', 'chiffre': '9',
        'question': "Que fais-tu encore par obligation<br/>alors que ton âme t'appelle ailleurs ?",
    },
    {
        'slug': 'taureau', 'nom': 'Taureau', 'sym': '♉', 'dates': '20 avril — 20 mai',
        'ouverture': "Aujourd'hui, ce qui semble lent construit ton essentiel. Le rythme est ton allié.",
        'energie': "Vénus caresse ton signe. Une douceur revient dans ce qui te tenait à cœur. Reconnecte-toi à la beauté simple.",
        'amour': "Tu attires par la profondeur, pas par la rapidité. Laisse la personne juste faire ses pas vers toi.",
        'carriere': "Une négociation te sera favorable si tu restes ancré et ne cèdes pas sur ta valeur.",
        'bien_etre': "Ton corps réclame de la nature. Marche pieds nus dix minutes si tu peux.",
        'guidance': "Ce que tu construis lentement dure. Ce qui explose vite s'éteint aussi vite.",
        'pierre': 'Émeraude', 'couleur': 'Vert forêt', 'aromate': 'Rose',
        'heure': '10h — 14h', 'chiffre': '6',
        'question': "Qu'est-ce que tu retiens<br/>alors qu'il faudrait déjà lâcher ?",
    },
    {
        'slug': 'gemeaux', 'nom': 'Gémeaux', 'sym': '♊', 'dates': '21 mai — 20 juin',
        'ouverture': "Aujourd'hui, ta pensée doit se poser sur UNE chose. Sinon tout t'échappe.",
        'energie': "Mercure envoie des signes clairs. Une conversation clé te révèle une info que tu cherchais depuis longtemps.",
        'amour': "L'esprit vif d'un(e) inconnu(e) te séduit. Vérifie que le cœur suit avant de t'emballer.",
        'carriere': "Écris ce que tu penses avant de le dire à voix haute. Tu gagnerais en poids.",
        'bien_etre': "Trop de stimulations te fatiguent. Coupe tes notifications deux heures.",
        'guidance': "Ce qui compte n'est pas de tout savoir, mais de choisir ce que tu veux vraiment approfondir.",
        'pierre': 'Agate', 'couleur': 'Jaune citron', 'aromate': 'Menthe',
        'heure': '14h — 18h', 'chiffre': '5',
        'question': "Sur combien de sujets es-tu en surface<br/>alors qu'un seul mériterait ta profondeur ?",
    },
    {
        'slug': 'cancer', 'nom': 'Cancer', 'sym': '♋', 'dates': '21 juin — 22 juillet',
        'ouverture': "Aujourd'hui, ta sensibilité est un radar, pas une faiblesse.",
        'energie': "La Lune, ta maîtresse, éclaire tes émotions cachées. Ce que tu refoulais depuis un moment demande à être vu, pas jugé.",
        'amour': "Ta tendresse est ton super-pouvoir. Ne t'excuse jamais d'aimer avec autant d'intensité.",
        'carriere': "Un collègue va confier quelque chose d'important. Écoute vraiment, cela renforcera votre lien.",
        'bien_etre': "Un bain chaud ou un moment près de l'eau apaisera un système nerveux surchargé.",
        'guidance': "Ta sensibilité n'est pas un défaut à corriger. C'est ta boussole.",
        'pierre': 'Pierre de Lune', 'couleur': 'Blanc nacré', 'aromate': 'Camomille',
        'heure': '20h — 23h', 'chiffre': '2',
        'question': "Quelle émotion refuses-tu de sentir<br/>parce que tu la juges 'trop' ?",
    },
    {
        'slug': 'lion', 'nom': 'Lion', 'sym': '♌', 'dates': '23 juillet — 22 août',
        'ouverture': "Aujourd'hui, ton éclat n'a besoin de personne pour exister.",
        'energie': "Le Soleil, ton maître, forme un trigone à Jupiter. Une vague de confiance douce te traverse — pas l'ego bruyant, la certitude tranquille de mériter ta place.",
        'amour': "Vénus favorise la sincérité. Dis ce que tu penses vraiment — sans travestir. Ton authenticité est magnétique aujourd'hui.",
        'carriere': "Un projet longtemps mis de côté demande à ressurgir. Il revient transformé, parce que toi aussi tu as changé.",
        'bien_etre': "Ton corps a besoin de mouvement solaire : marche à l'extérieur, danse, chaleur.",
        'guidance': "Ne cherche pas à convaincre. Sois. Ceux qui doivent te suivre le feront sans qu'il faille les tirer.",
        'pierre': 'Citrine', 'couleur': 'Doré antique', 'aromate': 'Cannelle',
        'heure': '11h — 15h', 'chiffre': '3',
        'question': "Que rayonnerais-tu aujourd'hui<br/>si tu n'attendais l'approbation de personne ?",
    },
    {
        'slug': 'vierge', 'nom': 'Vierge', 'sym': '♍', 'dates': '23 août — 22 septembre',
        'ouverture': "Aujourd'hui, la perfection est un piège. La simplicité est ta libération.",
        'energie': "Mercure t'incite à faire le tri : ce qui reste dans ta vie doit y avoir sa place. Pas d'exception.",
        'amour': "Arrête de vouloir tout contrôler dans l'échange. Une part doit rester mystère — c'est ce qui te maintient vivant(e).",
        'carriere': "Un détail que personne ne voit va sauver un dossier important. Fais confiance à ton œil.",
        'bien_etre': "Ton système digestif porte tes contrariétés. Mange plus doucement, en pleine présence.",
        'guidance': "Fais de la place à ce qui compte vraiment. Le reste te parasite.",
        'pierre': 'Amazonite', 'couleur': 'Vert sauge', 'aromate': 'Basilic',
        'heure': '15h — 19h', 'chiffre': '7',
        'question': "Qu'es-tu prêt(e) à laisser derrière toi<br/>pour avancer plus léger ?",
    },
    {
        'slug': 'balance', 'nom': 'Balance', 'sym': '♎', 'dates': '23 septembre — 22 octobre',
        'ouverture': "Aujourd'hui, choisir n'est pas trahir. C'est enfin exister.",
        'energie': "Vénus favorise la clarté relationnelle. Ce que tu évitais de nommer va trouver une expression juste.",
        'amour': "Cesse de plaire pour être aimé(e). L'authenticité attire toujours plus fort que la performance.",
        'carriere': "Un partenariat gagne à être renégocié. Ta valeur a monté depuis le dernier accord.",
        'bien_etre': "Les reins te demandent hydratation. Une infusion tiède plutôt qu'un café de plus.",
        'guidance': "Trouver ta paix intérieure n'est pas égoïste. C'est ce qui rend possible ta paix avec les autres.",
        'pierre': 'Quartz rose', 'couleur': 'Rose poudré', 'aromate': 'Rose de Damas',
        'heure': '16h — 20h', 'chiffre': '6',
        'question': "Où as-tu accepté un compromis<br/>qui te coûte plus qu'il ne te donne ?",
    },
    {
        'slug': 'scorpion', 'nom': 'Scorpion', 'sym': '♏', 'dates': '23 octobre — 21 novembre',
        'ouverture': "Aujourd'hui, ce qui doit mourir cède la place à ce qui veut naître.",
        'energie': "Pluton t'offre une lucidité rare. Tu vois ce que d'autres ne voient pas — utilise-le pour libérer, pas pour dominer.",
        'amour': "Une vérité doit être dite. Elle brûlera à court terme, elle sauvera à long terme.",
        'carriere': "Un jeu de pouvoir se joue autour de toi. Reste transparent(e), tu seras plus fort que tous les stratèges.",
        'bien_etre': "Un rituel de libération avant le coucher (écrit ce que tu abandonnes puis le déchire).",
        'guidance': "Tu n'as pas à porter ce que d'autres n'ont pas eu le courage de regarder en face.",
        'pierre': 'Obsidienne', 'couleur': 'Bordeaux profond', 'aromate': 'Patchouli',
        'heure': '22h — 2h', 'chiffre': '8',
        'question': "Quelle vérité tu connais<br/>mais que tu refuses de nommer ?",
    },
    {
        'slug': 'sagittaire', 'nom': 'Sagittaire', 'sym': '♐', 'dates': '22 novembre — 21 décembre',
        'ouverture': "Aujourd'hui, ta liberté commence par un OUI radical à toi-même.",
        'energie': "Jupiter, ton maître, élargit tes horizons. Un signe t'invite à sortir de ta zone connue — accepte l'invitation.",
        'amour': "Ne confonds pas la peur d'être enfermé(e) avec l'appel de l'aventure. Parfois rester est l'aventure la plus courageuse.",
        'carriere': "Une opportunité à l'étranger, une formation, une reconversion : le vent souffle vers le nouveau.",
        'bien_etre': "Bouge en grand : trekking, danse, sport de plein air. L'énergie est là.",
        'guidance': "La vérité te fera libre, mais la ta vérité doit d'abord être dite avec bienveillance.",
        'pierre': 'Turquoise', 'couleur': 'Violet profond', 'aromate': 'Sauge',
        'heure': '17h — 21h', 'chiffre': '9',
        'question': "Vers quel horizon<br/>as-tu peur de tendre la main ?",
    },
    {
        'slug': 'capricorne', 'nom': 'Capricorne', 'sym': '♑', 'dates': '22 décembre — 19 janvier',
        'ouverture': "Aujourd'hui, ce que tu bâtis est plus grand que ce que tu vois.",
        'energie': "Saturne, ton maître, récompense la constance. Un effort ancien commence à porter ses fruits — reste patient(e), la maturation est en cours.",
        'amour': "Laisse-toi être vulnérable une seconde. C'est là que la vraie intimité commence.",
        'carriere': "Reconnaissance en vue. Prépare-toi à recevoir sans minimiser tes accomplissements.",
        'bien_etre': "Les articulations et les genoux portent tes tensions. Étirements profonds recommandés.",
        'guidance': "Le succès sans intimité est solitaire. N'oublie pas de tendre la main.",
        'pierre': 'Onyx noir', 'couleur': 'Anthracite', 'aromate': 'Bois de cèdre',
        'heure': '5h — 9h', 'chiffre': '8',
        'question': "Qui as-tu tenu à distance<br/>pour ne pas paraître vulnérable ?",
    },
    {
        'slug': 'verseau', 'nom': 'Verseau', 'sym': '♒', 'dates': '20 janvier — 18 février',
        'ouverture': "Aujourd'hui, être différent(e) est ton plus grand cadeau, pas ton fardeau.",
        'energie': "Uranus déclenche une inspiration soudaine. Une idée que tu croyais folle est en fait ton chemin — note-la vite avant qu'elle ne s'envole.",
        'amour': "Ton besoin d'espace n'est pas un rejet. Explique-le, ne le fais pas subir.",
        'carriere': "Un projet collectif où tu bousculeras un statu quo. Assume ton rôle de pionnier(e).",
        'bien_etre': "Le mental tourne trop. Un exercice de respiration en pleine conscience (4-7-8) te reconnectera.",
        'guidance': "Le monde a besoin de ta vision, pas de ta conformité.",
        'pierre': 'Améthyste', 'couleur': 'Bleu électrique', 'aromate': 'Lavande',
        'heure': '19h — 23h', 'chiffre': '4',
        'question': "Quelle idée 'folle'<br/>as-tu enterrée par peur d'être jugé(e) ?",
    },
    {
        'slug': 'poissons', 'nom': 'Poissons', 'sym': '♓', 'dates': '19 février — 20 mars',
        'ouverture': "Aujourd'hui, ton intuition n'est pas une illusion. C'est ta vraie langue maternelle.",
        'energie': "Neptune amplifie ton empathie et ta créativité. Écoute ce que ton corps ressent avant même que ton mental n'ait le temps de rationaliser.",
        'amour': "Un rêve, une synchronicité te guide vers une réponse que tu attendais. Reste ouvert(e).",
        'carriere': "L'art, la musique, la spiritualité — quelque chose dans le domaine créatif frappe à ta porte.",
        'bien_etre': "L'eau te régénère. Bain, natation, marche près d'un cours d'eau : tout est bon.",
        'guidance': "Ton intuition n'est pas naïve. C'est le mental des sages.",
        'pierre': 'Aigue-marine', 'couleur': 'Bleu turquoise', 'aromate': 'Ylang-ylang',
        'heure': '3h — 7h', 'chiffre': '7',
        'question': "Quel signe as-tu reçu récemment<br/>que tu refuses de prendre au sérieux ?",
    },
]


def _build(path: Path, story: list):
    doc = SimpleDocTemplate(
        str(path), pagesize=A4,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    doc.build(story, onFirstPage=luxury_bg, onLaterPages=luxury_bg)
    return path


def build_pdf_for_signe(s: dict) -> Path:
    styles = luxury_styles()
    story = []
    today = date.today()
    date_fr = f"{_JOURS_FR[today.weekday()]} {today.day} {_MOIS_FR[today.month - 1]} {today.year}"

    # Page 1 — cover
    story.append(Spacer(1, 1.4 * cm))
    story.append(Paragraph(f'{_sym("✦")}  HOROSCOPE JOURNALIER  {_sym("✦")}', styles['section_tag']))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(date_fr, ParagraphStyle(
        'date_top', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
        fontSize=14, textColor=MUTED, alignment=TA_CENTER, spaceAfter=18,
    )))
    img = _dl_image(illustration_url('roue_zodiaque', 800))
    if img:
        story.append(RLImage(img, width=6.5 * cm, height=6.5 * cm, mask='auto'))
        story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph(s['nom'], ParagraphStyle(
        'sign_title', fontName=font('Cormorant', 'Helvetica'),
        fontSize=56, leading=64, textColor=CREAM, alignment=TA_CENTER,
    )))
    story.append(Paragraph(
        f'{_sym(s["sym"])}   {s["dates"]}',
        ParagraphStyle('sign_dates', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=11, textColor=GOLD, alignment=TA_CENTER, spaceAfter=20),
    ))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        f'« &nbsp;{s["ouverture"]}&nbsp; »',
        ParagraphStyle('opener', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                       fontSize=17, leading=26, textColor=GOLD_LIGHT,
                       alignment=TA_CENTER, leftIndent=1 * cm, rightIndent=1 * cm),
    ))
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph('Lu par Soléna', styles['signature']))
    story.append(PageBreak())

    # Page 2 — Details
    body = ParagraphStyle('body_hor', fontName=font('Cormorant', 'Helvetica'),
                          fontSize=11.5, leading=18, textColor=CREAM,
                          alignment=TA_LEFT, spaceAfter=8)
    section_h = ParagraphStyle('sec_hor', fontName=font('Cinzel', 'Helvetica'),
                                fontSize=11, leading=16, textColor=GOLD_LIGHT,
                                alignment=TA_LEFT, spaceAfter=4, spaceBefore=6)

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("L'ÉNERGIE DU JOUR", styles['section_tag']))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(s['energie'], body))

    story.append(Paragraph(f'{_sym("♥")}  AMOUR', section_h))
    story.append(Paragraph(s['amour'], body))
    story.append(Paragraph(f'{_sym("◆")}  CARRIÈRE', section_h))
    story.append(Paragraph(s['carriere'], body))
    story.append(Paragraph(f'{_sym("☾")}  BIEN-ÊTRE', section_h))
    story.append(Paragraph(s['bien_etre'], body))

    # Guidance héros
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        f'{_sym("✦")}  LA GUIDANCE DU JOUR  {_sym("✦")}',
        ParagraphStyle('guidance_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=11, textColor=GOLD, alignment=TA_CENTER, spaceAfter=8),
    ))
    story.append(Paragraph(
        f'« &nbsp;{s["guidance"]}&nbsp; »',
        ParagraphStyle('gb', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                       fontSize=15, leading=24, textColor=GOLD_LIGHT,
                       alignment=TA_CENTER, leftIndent=0.5 * cm, rightIndent=0.5 * cm, spaceAfter=8),
    ))
    story.append(Paragraph('— Soléna', ParagraphStyle(
        'sig', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
        fontSize=11, textColor=MUTED, alignment=TA_CENTER, spaceAfter=14,
    )))

    # Tips table
    tips = [
        [Paragraph(_sym('◈') + '  Pierre du jour', body), Paragraph(s['pierre'], body)],
        [Paragraph(_sym('❦') + '  Couleur', body), Paragraph(s['couleur'], body)],
        [Paragraph(_sym('❋') + '  Aromate', body), Paragraph(s['aromate'], body)],
        [Paragraph(_sym('☉') + '  Heure favorable', body), Paragraph(s['heure'], body)],
        [Paragraph(_sym('✧') + '  Chiffre', body), Paragraph(s['chiffre'], body)],
    ]
    tbl = Table(tips, colWidths=[7 * cm, 8.5 * cm], style=TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'), ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, HexColor('#3a2f5a')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(tbl)

    story.append(Spacer(1, 0.35 * cm))
    story.append(Paragraph(f"{_sym('✦')}  question de réflexion  {_sym('✦')}",
        ParagraphStyle('q_i', fontName=font('Cinzel', 'Helvetica'), fontSize=9,
                       textColor=GOLD, alignment=TA_CENTER, spaceAfter=4)))
    story.append(Paragraph(f'« &nbsp;{s["question"]}&nbsp; »',
        ParagraphStyle('q_b', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                       fontSize=13, leading=20, textColor=CREAM, alignment=TA_CENTER,
                       leftIndent=0.8 * cm, rightIndent=0.8 * cm, spaceAfter=10)))
    story.append(Paragraph('plume-astrale.fr', ParagraphStyle(
        'url', fontName=font('Cinzel', 'Helvetica'), fontSize=8,
        textColor=MUTED, alignment=TA_CENTER)))

    out = OUT_DIR / f'horoscope_journalier_{s["slug"]}.pdf'
    _build(out, story)
    return out


if __name__ == '__main__':
    for s in SIGNES:
        p = build_pdf_for_signe(s)
        print(f'✓ {p.name}  ({p.stat().st_size // 1024} KB)')
