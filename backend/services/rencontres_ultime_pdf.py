"""
Generateur PDF "Guide de Compatibilite Ultime & Calendrier de Rencontres" — 15 pages.
Produit one-shot 29,99€ (pack `rencontres_ultime`).

Structure (15 pages) :
   1. Couverture — Guide de Compatibilite Ultime
   2. Sommaire poetique
   3. Ta boussole cosmique amoureuse (resume)
   4. Ton Soleil en amour
   5. Ta Lune — le besoin emotionnel intime
   6. Ta Venus — comment tu aimes
   7. Ta Mars — comment tu seduis
   8. Ta Maison V — le langage du desir
   9. Ta Maison VII — le miroir du partenaire
  10. Le Portrait-Robot de ton ame soeur
  11. Fenetre de rencontre #1 (0-2 mois)
  12. Fenetre de rencontre #2 (2-4 mois)
  13. Fenetre de rencontre #3 (4-6 mois)
  14. Rituels energetiques d'attraction (bougies, lithotherapie, meditation)
  15. Benediction de Solena + question ouverte

Design : style "Mix" — couverture sombre doree, pages interieures fond creme.
"""
from __future__ import annotations
import io
import os
import calendar
from datetime import datetime, timedelta, timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Police Unicode pour glyphes zodiacaux
_UNICODE_FONT = "Helvetica"
try:
    _FREESERIF = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
    if os.path.exists(_FREESERIF):
        pdfmetrics.registerFont(TTFont("FreeSerif", _FREESERIF))
        _UNICODE_FONT = "FreeSerif"
except Exception:
    pass

# ═══════════════════════════════ Palette ═══════════════════════════════
DEEP_PURPLE = HexColor('#0C0918')
DEEP_INDIGO = HexColor('#1a1147')
GOLD        = HexColor('#C5A059')
GOLD_LIGHT  = HexColor('#E7C97A')
CREAM_BG    = HexColor('#F7F1E4')
INK         = HexColor('#231a19')
INK_SOFT    = HexColor('#5a4a44')

W, H = A4
MARGIN = 2.2 * cm

# ═══════════════════════════════ Sign data ═══════════════════════════════
SIGN_GLYPH = {
    'Belier': '♈', 'Taureau': '♉', 'Gemeaux': '♊', 'Cancer': '♋',
    'Lion': '♌', 'Vierge': '♍', 'Balance': '♎', 'Scorpion': '♏',
    'Sagittaire': '♐', 'Capricorne': '♑', 'Verseau': '♒', 'Poissons': '♓',
}

SIGN_ELEMENT = {
    'Belier': 'Feu', 'Taureau': 'Terre', 'Gemeaux': 'Air', 'Cancer': 'Eau',
    'Lion': 'Feu', 'Vierge': 'Terre', 'Balance': 'Air', 'Scorpion': 'Eau',
    'Sagittaire': 'Feu', 'Capricorne': 'Terre', 'Verseau': 'Air', 'Poissons': 'Eau',
}

# Portrait des signes en amour (Venus + Mars combines)
LOVE_ARCHETYPE = {
    'Belier': ("Amant conquerant", "passionne, direct, impatient — tu aimes en te lançant sans reserve"),
    'Taureau': ("Amant sensuel", "gourmand des plaisirs simples, patient et fidele quand le cœur s'est pose"),
    'Gemeaux': ("Amant intellectuel", "seducteur par la parole, tu aimes l'eveil mental autant que le corps"),
    'Cancer': ("Amant tendre", "protecteur et intime, tu batis un nid emotionnel autour de l'autre"),
    'Lion': ("Amant flamboyant", "genereux, theatrical, tu aimes qu'on te reconnaisse et tu offres en retour"),
    'Vierge': ("Amant devoue", "attentif aux details, tu prouves ton amour par le service et le raffinement"),
    'Balance': ("Amant harmonieux", "esthete, diplomate, tu cherches la beaute et l'equilibre dans le lien"),
    'Scorpion': ("Amant transformateur", "intense, magnetique, tu ne connais pas les demi-mesures — tout ou rien"),
    'Sagittaire': ("Amant aventurier", "libre, philosophe, tu aimes ceux qui elargissent ton horizon"),
    'Capricorne': ("Amant loyal", "serieux, patient, tu construis pour la duree et l'engagement"),
    'Verseau': ("Amant libre", "originaux, tu aimes l'amitie amoureuse, la liberte et l'inattendu"),
    'Poissons': ("Amant reveur", "romantique, intuitif, tu aimes en fusion et en poesie"),
}

# ═══════════════════════════════ Helpers ═══════════════════════════════

def _sign_from_iso_date(date_str: str) -> str:
    """YYYY-MM-DD → nom du signe solaire."""
    if not date_str or len(date_str) < 10:
        return 'Poissons'
    try:
        _, m, d = date_str[:10].split('-')
        m, d = int(m), int(d)
    except Exception:
        return 'Poissons'
    ranges = [
        ((3, 21), (4, 19), 'Belier'), ((4, 20), (5, 20), 'Taureau'),
        ((5, 21), (6, 20), 'Gemeaux'), ((6, 21), (7, 22), 'Cancer'),
        ((7, 23), (8, 22), 'Lion'), ((8, 23), (9, 22), 'Vierge'),
        ((9, 23), (10, 22), 'Balance'), ((10, 23), (11, 21), 'Scorpion'),
        ((11, 22), (12, 21), 'Sagittaire'), ((12, 22), (12, 31), 'Capricorne'),
        ((1, 1), (1, 19), 'Capricorne'), ((1, 20), (2, 18), 'Verseau'),
        ((2, 19), (3, 20), 'Poissons'),
    ]
    for (m1, d1), (m2, d2), name in ranges:
        if (m, d) >= (m1, d1) and (m, d) <= (m2, d2):
            return name
    return 'Poissons'


def _date_fr(d=None):
    if d is None:
        d = datetime.now()
    fr_months = ['janvier','fevrier','mars','avril','mai','juin',
                 'juillet','aout','septembre','octobre','novembre','decembre']
    return f"{d.day} {fr_months[d.month - 1]} {d.year}"


def _wrap_text(c, text, x, y, w, font, size, leading, color=INK):
    """Draw wrapped paragraph. Retourne y final."""
    c.setFillColor(color)
    c.setFont(font, size)
    words = text.split()
    line = ''
    for word in words:
        test = f"{line} {word}".strip()
        if c.stringWidth(test, font, size) < w:
            line = test
        else:
            c.drawString(x, y, line)
            y -= leading
            line = word
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


# ═══════════════════════════════ Pages ═══════════════════════════════

def _p_cover(c, sun_sign: str, first_name: str):
    """Page 1 — Couverture sombre doree."""
    c.setFillColor(DEEP_PURPLE)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Halo dore diffus
    c.setFillColorRGB(0.77, 0.63, 0.35, alpha=0.10)
    for r in (170, 130, 90, 60):
        c.circle(W / 2, H * 0.62, r, fill=1, stroke=0)

    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.line(W / 2 - 90, H - 3 * cm, W / 2 + 90, H - 3 * cm)

    # Ornement top
    c.setFillColor(GOLD)
    c.setFont(_UNICODE_FONT, 20)
    c.drawCentredString(W / 2, H - 4 * cm, "✦  ✧  ✦")

    # Titre principal
    c.setFillColor(GOLD_LIGHT)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(W / 2, H - 6 * cm, "GUIDE DE COMPATIBILITE")
    c.drawCentredString(W / 2, H - 6.9 * cm, "ULTIME")
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Oblique", 14)
    c.drawCentredString(W / 2, H - 8 * cm, "& Calendrier de Rencontres")

    # Prenom
    c.setFillColor(HexColor('#F4E8D2'))
    c.setFont("Helvetica-Oblique", 16)
    c.drawCentredString(W / 2, H * 0.44, f"Prepare pour {first_name.strip().title() if first_name else 'toi'}")

    # Glyphe zodiacal + signe
    c.setFillColor(GOLD)
    c.setFont(_UNICODE_FONT, 60)
    c.drawCentredString(W / 2, H * 0.30, SIGN_GLYPH.get(sun_sign, '✦'))
    c.setFont("Helvetica", 13)
    c.setFillColor(GOLD_LIGHT)
    c.drawCentredString(W / 2, H * 0.24, f"Soleil en {sun_sign}")

    # Signature bas
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(HexColor('#8B7355'))
    c.drawCentredString(W / 2, 3 * cm, "— Solena, la voix de Plume Astrale")
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, 2.3 * cm, "PLUME  ASTRALE  ·  " + _date_fr().upper())


def _p_interior_bg(c, page_num: int):
    """Fond creme + ornement de page pour les pages interieures."""
    c.setFillColor(CREAM_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    # Ligne dore en haut
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.3)
    c.line(MARGIN, H - 1.6 * cm, W - MARGIN, H - 1.6 * cm)
    # Numero de page en bas
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, 1.2 * cm, f"— {page_num} —")
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColor(INK_SOFT)
    c.drawRightString(W - MARGIN, 1.2 * cm, "Guide de Compatibilite Ultime")


def _p_title(c, kicker: str, title: str):
    """Titre standard interieur — retourne y de depart pour le corps."""
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, H - 3.2 * cm, kicker.upper())
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(MARGIN, H - 4.5 * cm, title)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.4)
    c.line(MARGIN, H - 5 * cm, MARGIN + 3 * cm, H - 5 * cm)
    return H - 6.5 * cm


def _p_sommaire(c, first_name: str):
    _p_interior_bg(c, 2)
    y = _p_title(c, "Sommaire", "Ton chemin vers l'amour")
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica-Oblique", 10)
    y = _wrap_text(c, f"Voici les 13 revelations qui t'attendent, {first_name.strip().title() if first_name else 'chere ame'}. Prends ton temps. Reviens-y quand ton cœur en aura besoin.",
                   MARGIN, y, W - 2 * MARGIN, "Helvetica-Oblique", 10, 14, INK_SOFT)
    y -= 8
    sommaire = [
        ("03", "Ta boussole cosmique amoureuse"),
        ("04", "Ton Soleil en amour"),
        ("05", "Ta Lune — le besoin emotionnel intime"),
        ("06", "Ta Venus — comment tu aimes"),
        ("07", "Ta Mars — comment tu seduis"),
        ("08", "Ta Maison V — le langage du desir"),
        ("09", "Ta Maison VII — le miroir du partenaire"),
        ("10", "Portrait-Robot de ton ame sœur"),
        ("11", "Fenetre de rencontre #1"),
        ("12", "Fenetre de rencontre #2"),
        ("13", "Fenetre de rencontre #3"),
        ("14", "Rituels energetiques d'attraction"),
        ("15", "Benediction de Solena"),
    ]
    c.setFillColor(INK)
    for page, label in sommaire:
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(GOLD)
        c.drawString(MARGIN, y, page)
        c.setFillColor(INK)
        c.setFont("Helvetica", 11)
        c.drawString(MARGIN + 1.3 * cm, y, label)
        y -= 20


def _p_boussole(c, page_num, sun_sign, m7_sign, venus_sign, mars_sign, first_name):
    _p_interior_bg(c, page_num)
    y = _p_title(c, "Chapitre 1", "Ta boussole cosmique amoureuse")

    text = (
        f"Cher(e) {first_name.strip().title() if first_name else 'ami(e)'}, ton ciel de naissance est une carte "
        f"amoureuse unique. Il ne dicte rien : il eclaire tes ressorts, tes elans, tes points de resistance. "
        f"C'est un langage — le tien — que tu es sur le point de decoder."
    )
    y = _wrap_text(c, text, MARGIN, y, W - 2 * MARGIN, "Helvetica", 11, 16)
    y -= 14

    # Trois grandes portes
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "TES QUATRE PILIERS AMOUREUX")
    y -= 20
    pillars = [
        ("Soleil", sun_sign, "Ta signature d'amant"),
        ("Venus", venus_sign or sun_sign, "Ta maniere d'aimer"),
        ("Mars", mars_sign or sun_sign, "Ta maniere de seduire"),
        ("Maison VII", m7_sign or sun_sign, "Le miroir du partenaire"),
    ]
    for label, sign, desc in pillars:
        c.setFillColor(INK)
        c.setFont(_UNICODE_FONT, 16)
        c.drawString(MARGIN, y, SIGN_GLYPH.get(sign, '✦'))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN + 0.9 * cm, y + 2, f"{label} en {sign}")
        c.setFillColor(INK_SOFT)
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(MARGIN + 0.9 * cm, y - 11, desc)
        y -= 30

    y -= 6
    c.setFillColor(INK)
    text = (
        "Dans les pages qui suivent, chaque planete devoile un pan de ta verite amoureuse. "
        "Puis, Solena decrypte ton Portrait-Robot ideal et te livre trois fenetres precises "
        "ou l'univers joue pour toi dans les 6 prochains mois."
    )
    _wrap_text(c, text, MARGIN, y, W - 2 * MARGIN, "Helvetica", 11, 16)


def _p_soleil(c, page_num, sign, first_name):
    _p_interior_bg(c, page_num)
    y = _p_title(c, "Chapitre 2", "Ton Soleil en amour")
    arch, desc = LOVE_ARCHETYPE.get(sign, ("Amant unique", "une signature amoureuse rare"))

    c.setFillColor(GOLD)
    c.setFont(_UNICODE_FONT, 38)
    c.drawCentredString(W / 2, y, SIGN_GLYPH.get(sign, '☉'))
    y -= 45
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, y, f"Soleil en {sign}")
    y -= 20
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(W / 2, y, f"« {arch} »")
    y -= 28

    text = (
        f"Ton Soleil en {sign} imprime ta signature vitale d'amant. Tu es {desc}. "
        f"En amour, cette configuration te pousse vers un besoin de reconnaissance authentique : "
        f"tu veux etre vu(e) pour qui tu es reellement, pas pour un role que tu joues."
    )
    y = _wrap_text(c, text, MARGIN, y, W - 2 * MARGIN, "Helvetica", 11, 16)
    y -= 8
    text2 = (
        "Element {elem}. Tu portes en toi une temperature emotionnelle particuliere — sache la reconnaitre "
        "chez l'autre, et evite les personnes qui l'etouffent au lieu de l'accueillir.".format(elem=SIGN_ELEMENT.get(sign, 'Feu'))
    )
    _wrap_text(c, text2, MARGIN, y, W - 2 * MARGIN, "Helvetica", 11, 16, INK_SOFT)


def _p_planete(c, page_num, planet_label, sign, kicker, title, intro, bullets):
    _p_interior_bg(c, page_num)
    y = _p_title(c, kicker, title)

    c.setFillColor(GOLD)
    c.setFont(_UNICODE_FONT, 30)
    c.drawString(MARGIN, y, SIGN_GLYPH.get(sign, '✦'))
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(MARGIN + 1.5 * cm, y + 8, f"{planet_label} en {sign}")
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(MARGIN + 1.5 * cm, y - 6, f"Element : {SIGN_ELEMENT.get(sign, 'Feu')}")
    y -= 35

    y = _wrap_text(c, intro, MARGIN, y, W - 2 * MARGIN, "Helvetica", 11, 16)
    y -= 6
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "CE QUE ÇA VEUT DIRE POUR TOI")
    y -= 16
    c.setFillColor(INK)
    c.setFont("Helvetica", 11)
    for b in bullets:
        c.setFillColor(GOLD)
        c.drawString(MARGIN, y, "✦")
        c.setFillColor(INK)
        y = _wrap_text(c, b, MARGIN + 0.6 * cm, y, W - 2 * MARGIN - 0.6 * cm, "Helvetica", 11, 15)
        y -= 4


VENUS_INTRO = {
    'Belier': "Tu aimes vite et fort. Ton cœur cherche la conquete, l'elan, la vibration immediate.",
    'Taureau': "Tu aimes par les sens. Ton cœur cherche la stabilite, la douceur du contact, la fidelite.",
    'Gemeaux': "Tu aimes par l'esprit. Ton cœur cherche l'echange, la parole, le jeu mental.",
    'Cancer': "Tu aimes en couveuse. Ton cœur cherche la protection reciproque, le nid, l'intimite.",
    'Lion': "Tu aimes en grand. Ton cœur cherche la reconnaissance, la scene, la generosite theatrale.",
    'Vierge': "Tu aimes par le detail. Ton cœur cherche l'attention discrete, le service, le raffinement.",
    'Balance': "Tu aimes en harmonie. Ton cœur cherche la beaute partagee, l'equilibre, l'esthetique.",
    'Scorpion': "Tu aimes en profondeur. Ton cœur cherche la fusion, la verite crue, la transformation.",
    'Sagittaire': "Tu aimes en aventure. Ton cœur cherche l'horizon partage, la philosophie, la liberte.",
    'Capricorne': "Tu aimes en construction. Ton cœur cherche la duree, l'engagement, la loyaute.",
    'Verseau': "Tu aimes en amitie. Ton cœur cherche l'originalite, la liberte, l'echange atypique.",
    'Poissons': "Tu aimes en reve. Ton cœur cherche la fusion romantique, la poesie, la magie.",
}
VENUS_BULLETS = {
    'Belier': ["Tu es a l'aise avec l'initiative et la conquete.",
               "Tu supportes mal la lenteur ou la tiedeur emotionnelle.",
               "Ta blessure : la routine qui eteint le feu."],
    'Taureau': ["Tu construis la confiance par la constance et le toucher.",
                "Tu as besoin d'une securite materielle et sensorielle.",
                "Ta blessure : les changements brusques."],
    'Gemeaux': ["La conversation te met en desir avant le contact.",
                "Tu t'ennuies vite si l'esprit ne dialogue plus.",
                "Ta blessure : le silence lourd, l'incapacite a se dire."],
    'Cancer': ["Tu poses ton cœur avec pudeur, apres t'etre assure de la securite.",
               "Tu es d'une loyaute rare quand tu as choisi.",
               "Ta blessure : le rejet emotionnel ou l'indifference."],
    'Lion': ["Tu aimes qu'on te reconnaisse et tu offres a la hauteur.",
             "Ta genereosite doit etre honoree — sinon tu te retires.",
             "Ta blessure : l'ingratitude, l'absence de reconnaissance."],
    'Vierge': ["Tu prouves ton amour par les gestes concrets et le service.",
               "Tu peux paraitre distant(e) alors que tu te dedies en secret.",
               "Ta blessure : etre pris(e) pour acquis."],
    'Balance': ["Tu portes tes elans a la beaute partagee et la delicatesse.",
                "Tu evites les conflits, quitte a t'oublier.",
                "Ta blessure : la brusquerie ou l'inelegance."],
    'Scorpion': ["Tu aimes tout ou rien — les demi-mesures te blessent.",
                 "Ta profondeur peut effrayer les cœurs superficiels.",
                 "Ta blessure : la trahison ou le mensonge."],
    'Sagittaire': ["Tu aimes ceux qui elargissent ton horizon.",
                   "L'enfermement affectif t'insupporte.",
                   "Ta blessure : la routine possessive."],
    'Capricorne': ["Tu batis pour la duree et tu tests le temps.",
                   "Ton engagement est rare et precieux.",
                   "Ta blessure : la frivolite ou l'instabilite."],
    'Verseau': ["Tu aimes en amitie amoureuse, sans contrainte.",
                "L'originalite et l'independance t'attirent.",
                "Ta blessure : la possessivite."],
    'Poissons': ["Tu aimes en fusion poetique et intuitive.",
                 "Ta sensibilite capte tout, y compris ce qui n'est pas dit.",
                 "Ta blessure : le manque de tendresse ou la brutalite."],
}


def _p_venus(c, page_num, sign):
    intro = VENUS_INTRO.get(sign, "Ton Venus imprime ta signature amoureuse.")
    bullets = VENUS_BULLETS.get(sign, [])
    _p_planete(c, page_num, "Venus", sign, "Chapitre 4", "Ta Venus — comment tu aimes", intro, bullets)


MARS_INTRO = {
    'Belier': "Tu seduis par l'audace et la franchise. Tu ne perds pas de temps.",
    'Taureau': "Tu seduis par la constance et la sensualite lente.",
    'Gemeaux': "Tu seduis par les mots et l'humour vif.",
    'Cancer': "Tu seduis par la tendresse et la protection subtile.",
    'Lion': "Tu seduis par la presence lumineuse et la generosite.",
    'Vierge': "Tu seduis par le raffinement et l'attention concrete.",
    'Balance': "Tu seduis par le charme, l'esthetique, la diplomatie.",
    'Scorpion': "Tu seduis par le magnetisme silencieux et la profondeur.",
    'Sagittaire': "Tu seduis par la vision, l'humour et le grand horizon.",
    'Capricorne': "Tu seduis par le serieux, la position et la promesse d'avenir.",
    'Verseau': "Tu seduis par l'originalite et la liberte d'esprit.",
    'Poissons': "Tu seduis par l'aura poetique et l'ecoute infinie.",
}
MARS_BULLETS = {
    'Belier': ["Tu prends l'initiative sans hesiter.",
               "Ta drague est directe, parfois brusque.",
               "A cultiver : la patience du desir de l'autre."],
    'Taureau': ["Tu prends ton temps — tu inscris ton desir dans la duree.",
                "Ton toucher parle avant tes mots.",
                "A cultiver : oser bousculer un peu la routine."],
    'Gemeaux': ["Ton verbe declenche le desir chez l'autre.",
                "Tu joues, tu piques, tu enchantes.",
                "A cultiver : la profondeur au-dela du jeu."],
    'Cancer': ["Ta drague est indirecte, protectrice.",
               "Tu prepares un cocon avant meme d'oser.",
               "A cultiver : la franchise du desir clair."],
    'Lion': ["Tu ne demandes pas — tu offres et attends la reponse eblouie.",
             "Tu es a l'aise en scene et brillant(e) en public.",
             "A cultiver : accueillir l'humilite de l'autre."],
    'Vierge': ["Ta drague passe par des gestes precis et utiles.",
               "Tu observes plus que tu ne parles.",
               "A cultiver : oser exprimer ton desir directement."],
    'Balance': ["Ta drague est un art de l'equilibre : ni trop, ni trop peu.",
                "Tu evites tout ce qui heurte le raffinement.",
                "A cultiver : la clarte, meme au risque du desaccord."],
    'Scorpion': ["Ton regard suffit souvent — tu n'as pas besoin de mots.",
                 "Ta seduction est intense et engagante.",
                 "A cultiver : la legerete par moments."],
    'Sagittaire': ["Tu drague en propose : voyages, idees, aventures.",
                   "Ta gaiete est un aimant.",
                   "A cultiver : l'ancrage dans la duree."],
    'Capricorne': ["Ta drague est mesuree et strategique.",
                   "Tu proposes du solide, pas de l'ephemere.",
                   "A cultiver : la surprise, le grain de folie."],
    'Verseau': ["Ta drague est originale et non-conventionnelle.",
                "Tu apparais et tu disparais avec grace.",
                "A cultiver : l'engagement quand le lien s'approfondit."],
    'Poissons': ["Ta drague est intuitive et poetique.",
                 "Tu captes ce que l'autre ne dit pas — tu y reponds.",
                 "A cultiver : la clarte du contour, pour ne pas te dissoudre."],
}


def _p_mars(c, page_num, sign):
    intro = MARS_INTRO.get(sign, "Ton Mars imprime ta signature de seduction.")
    bullets = MARS_BULLETS.get(sign, [])
    _p_planete(c, page_num, "Mars", sign, "Chapitre 5", "Ta Mars — comment tu seduis", intro, bullets)


def _p_lune(c, page_num, sun_sign):
    """La Lune n'est pas connue au reveal — on interprete via le Soleil (fallback)."""
    _p_interior_bg(c, page_num)
    y = _p_title(c, "Chapitre 3", "Ta Lune — le besoin emotionnel intime")
    text = (
        "Ta Lune est le siege de ta sensibilite la plus intime. Elle guide ton besoin de reconfort, "
        "ta maniere d'etre nourri(e) affectivement. Meme sans son signe exact, sache que ta Lune "
        "cherche a etre reconnue et respectee au meme titre que ton Soleil."
    )
    y = _wrap_text(c, text, MARGIN, y, W - 2 * MARGIN, "Helvetica", 11, 16)
    y -= 12
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "TROIS INDICES POUR TOI")
    y -= 18
    tips = [
        "Ecoute ce qui, chez l'autre, apaise ton systeme nerveux — c'est un signal de compatibilite lunaire.",
        "Repere ce qui te fait sentir en securite : c'est la voix de ta Lune qui parle.",
        f"Ton Soleil en {sun_sign} donne un ton — mais ta Lune peut nuancer en profondeur. Sois attentif(ve).",
    ]
    for t in tips:
        c.setFillColor(GOLD)
        c.drawString(MARGIN, y, "✦")
        c.setFillColor(INK)
        y = _wrap_text(c, t, MARGIN + 0.6 * cm, y, W - 2 * MARGIN - 0.6 * cm, "Helvetica", 11, 15)
        y -= 4


HOUSE5_INTRO = {
    'Belier': "impulsif et flamboyant", 'Taureau': "sensoriel et gourmand",
    'Gemeaux': "malicieux et joueur", 'Cancer': "sentimental et intime",
    'Lion': "theatral et genereux", 'Vierge': "raffine et discret",
    'Balance': "harmonique et esthetique", 'Scorpion': "magnetique et intense",
    'Sagittaire': "aventureux et joyeux", 'Capricorne': "serieux et durable",
    'Verseau': "libre et original", 'Poissons': "poetique et fusionnel",
}
HOUSE7_INTRO = {
    'Belier': "un partenaire fougueux, initiateur, direct",
    'Taureau': "un partenaire stable, patient, sensuel",
    'Gemeaux': "un partenaire vif, curieux, communiquant",
    'Cancer': "un partenaire protecteur, tendre, familial",
    'Lion': "un partenaire lumineux, genereux, magnetique",
    'Vierge': "un partenaire attentif, raffine, structure",
    'Balance': "un partenaire harmonieux, esthete, diplomate",
    'Scorpion': "un partenaire intense, profond, transformateur",
    'Sagittaire': "un partenaire libre, philosophe, aventureux",
    'Capricorne': "un partenaire loyal, ambitieux, ancre",
    'Verseau': "un partenaire original, independant, atypique",
    'Poissons': "un partenaire reveur, intuitif, poete",
}


def _p_maison_v(c, page_num, sign):
    _p_interior_bg(c, page_num)
    y = _p_title(c, "Chapitre 6", "Ta Maison V — le langage du desir")
    intro = HOUSE5_INTRO.get(sign, "unique et singulier")
    text = (
        "La Maison V est le secteur du desir, du jeu, de la creativite, de la romance. "
        f"Chez toi, ton langage du desir est {intro}. C'est la que tu prends du plaisir dans la relation."
    )
    y = _wrap_text(c, text, MARGIN, y, W - 2 * MARGIN, "Helvetica", 11, 16)
    y -= 10
    tips = [
        "Ce qui t'anime le plus dans un debut de relation : le jeu, la surprise, la mise en scene.",
        "Fais-toi confiance : le desir authentique passe par le plaisir, pas par le calcul.",
        "Une relation qui ne laisse aucune place au jeu et a la creativite ne peut pas te nourrir sur la duree.",
    ]
    for t in tips:
        c.setFillColor(GOLD)
        c.drawString(MARGIN, y, "✦")
        c.setFillColor(INK)
        y = _wrap_text(c, t, MARGIN + 0.6 * cm, y, W - 2 * MARGIN - 0.6 * cm, "Helvetica", 11, 15)
        y -= 4


def _p_maison_vii(c, page_num, m7_sign):
    _p_interior_bg(c, page_num)
    y = _p_title(c, "Chapitre 7", "Ta Maison VII — le miroir du partenaire")
    intro = HOUSE7_INTRO.get(m7_sign, "un partenaire unique, taille pour toi")
    text = (
        "La Maison VII est le miroir : elle designe le type de partenaire vers lequel ton ame est attiree "
        f"pour se completer. Ta Maison VII est en {m7_sign}, ce qui signifie que ton ame appelle {intro}."
    )
    y = _wrap_text(c, text, MARGIN, y, W - 2 * MARGIN, "Helvetica", 11, 16)
    y -= 10
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "POURQUOI CE COMPLEMENT ?")
    y -= 18
    c.setFillColor(INK_SOFT)
    y = _wrap_text(c,
        "En astrologie, la Maison VII decrit ce que nous cherchons chez l'autre pour equilibrer notre carte. "
        "Ce n'est pas un ordre, mais une invitation : cette resonance ouvre a des relations plus fecondes.",
        MARGIN, y, W - 2 * MARGIN, "Helvetica-Oblique", 10, 14, INK_SOFT)


def _p_portrait_robot(c, page_num, m7_sign, first_name):
    _p_interior_bg(c, page_num)
    y = _p_title(c, "Chapitre 8", "Portrait-Robot de ton ame sœur")
    element = SIGN_ELEMENT.get(m7_sign, 'Feu')
    portraits = {
        'Belier': ("Une personne au regard vif, aux gestes rapides", "sourire assure, energie de conquerant(e), corps tonique"),
        'Taureau': ("Une personne au regard chaud et pose", "voix grave et rassurante, mains douces, silhouette solide"),
        'Gemeaux': ("Une personne au regard mobile et curieux", "sourire vif, gestes expressifs, silhouette souple"),
        'Cancer': ("Une personne au regard tendre et emotif", "voix enveloppante, presence maternelle/paternelle discrete"),
        'Lion': ("Une personne au regard lumineux", "presence eclatante, sourire genereux, tenue soignee"),
        'Vierge': ("Une personne au regard discret et precis", "silhouette elancee, ordre naturel, attention aux details"),
        'Balance': ("Une personne au visage harmonieux", "sourire diplomate, style raffine, presence apaisante"),
        'Scorpion': ("Une personne au regard magnetique", "presence intense, sourire rare mais puissant, aura mysterieuse"),
        'Sagittaire': ("Une personne au regard rieur", "silhouette large, sourire ouvert, allure sportive/aventuriere"),
        'Capricorne': ("Une personne au regard grave et ancree", "posture droite, tenue sobre, presence sculptee par le temps"),
        'Verseau': ("Une personne au regard atypique", "style original, aura decalee, presence non-conforme"),
        'Poissons': ("Une personne au regard reveur", "gestes doux, aura poetique, presence flottante"),
    }
    p_intro, p_desc = portraits.get(m7_sign, ("Une personne singuliere", "reconnaissable a une aura unique"))
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    y = _wrap_text(c, p_intro + ".", MARGIN, y, W - 2 * MARGIN, "Helvetica-Bold", 13, 18)
    y -= 4
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica-Oblique", 11)
    y = _wrap_text(c, f"Signes distinctifs : {p_desc}.", MARGIN, y, W - 2 * MARGIN, "Helvetica-Oblique", 11, 15, INK_SOFT)
    y -= 14
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "SES TROIS QUALITES DOMINANTES")
    y -= 16
    qualities = {
        'Feu': ["Enthousiasme et passion", "Courage face aux defis", "Genereosite naturelle"],
        'Terre': ["Fiabilite et parole tenue", "Sens du concret et du geste", "Presence chaleureuse et stable"],
        'Air': ["Intelligence relationnelle vive", "Curiosite et humour", "Capacite d'ecoute et d'echange"],
        'Eau': ["Sensibilite profonde", "Empathie et intuition", "Loyaute silencieuse"],
    }
    for q in qualities.get(element, []):
        c.setFillColor(GOLD)
        c.drawString(MARGIN, y, "✦")
        c.setFillColor(INK)
        y = _wrap_text(c, q, MARGIN + 0.6 * cm, y, W - 2 * MARGIN - 0.6 * cm, "Helvetica", 11, 15)
        y -= 4


def _p_fenetre(c, page_num, n, start_month, end_month, sign_venus_move, ritual):
    """Fenetre de rencontre — page 11/12/13."""
    _p_interior_bg(c, page_num)
    y = _p_title(c, f"Fenetre #{n}", f"Ta fenetre de rencontre : {start_month} → {end_month}")
    c.setFillColor(GOLD)
    c.setFont(_UNICODE_FONT, 24)
    c.drawString(MARGIN, y, "◐")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN + 1.2 * cm, y + 5, f"Transit clef : Venus en {sign_venus_move}")
    y -= 25
    text = (
        f"Durant cette periode, l'univers dispose ton champ energetique pour que la rencontre se produise. "
        f"Venus en {sign_venus_move} active un aspect particulierement fertile de ton thème pour l'amour. "
        f"Ta magnetisme naturelle est boostee — ose sortir, croiser, engager la conversation."
    )
    y = _wrap_text(c, text, MARGIN, y, W - 2 * MARGIN, "Helvetica", 11, 16)
    y -= 12
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "LES 3 GESTES A POSER")
    y -= 18
    actions = [
        "Accepte les invitations sociales, meme celles qui semblent anodines.",
        "Sois visible : porte ce qui met en valeur ta lumiere naturelle.",
        f"Pose l'intention chaque matin : 'Je m'ouvre aux rencontres alignees'.",
    ]
    for a in actions:
        c.setFillColor(GOLD)
        c.drawString(MARGIN, y, "✦")
        c.setFillColor(INK)
        y = _wrap_text(c, a, MARGIN + 0.6 * cm, y, W - 2 * MARGIN - 0.6 * cm, "Helvetica", 11, 15)
        y -= 4
    y -= 6
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Oblique", 10)
    _wrap_text(c, f"Rituel de la fenetre : {ritual}", MARGIN, y, W - 2 * MARGIN, "Helvetica-Oblique", 10, 14, GOLD)


def _p_rituels(c, page_num):
    _p_interior_bg(c, page_num)
    y = _p_title(c, "Chapitre 12", "Rituels energetiques d'attraction")
    intro = (
        "Ces rituels sont proposes comme des conseils de confort. Ils ne remplacent aucun soin medical. "
        "Ils accompagnent ta meteo emotionnelle et te reconnectent a ta puissance interieure."
    )
    y = _wrap_text(c, intro, MARGIN, y, W - 2 * MARGIN, "Helvetica-Oblique", 10, 14, INK_SOFT)
    y -= 12
    sections = [
        ("Lithotherapie", "Quartz rose (ouverture du cœur), rhodochrosite (guerison affective), pierre de lune (feminin sacre). Porte l'une d'elles pres du cœur pendant tes fenetres de rencontre."),
        ("Bougies", "Bougie rose (amour doux) ou dore (magnetisme). Allume-la 21 minutes chaque soir de la fenetre, en visualisant ta rencontre."),
        ("Meditation guidée", "5 minutes chaque matin : visualise une lumiere dore autour de toi qui rayonne vers la personne alignee. Ne cherche pas son visage — offre ta presence."),
        ("Shadow work", "Ecris chaque semaine : 'Ce qui, dans mes anciennes relations, m'a montre que je meritais mieux, c'est...' Cet exercice libere l'ancien pour ouvrir l'espace au nouveau."),
    ]
    for title, desc in sections:
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN, y, "✦  " + title.upper())
        y -= 14
        c.setFillColor(INK)
        y = _wrap_text(c, desc, MARGIN + 0.5 * cm, y, W - 2 * MARGIN - 0.5 * cm, "Helvetica", 10, 14)
        y -= 8


def _p_benediction(c, page_num, first_name):
    _p_interior_bg(c, page_num)
    y = _p_title(c, "Le mot final", "Benediction de Solena")
    text = (
        f"Cher(e) {first_name.strip().title() if first_name else 'ami(e)'}, "
        "tu detiens maintenant les clefs. Non pas pour forcer ton destin, mais pour t'aligner. "
        "L'amour aligne ne se conquiert pas — il se reconnait."
    )
    y = _wrap_text(c, text, MARGIN, y, W - 2 * MARGIN, "Helvetica", 12, 18)
    y -= 12
    text2 = (
        "Reviens a ce guide chaque fois que ton cœur doute. Les astres n'ecrivent pas ton histoire : "
        "ils te rappellent que tu es co-auteur(e) de ta rencontre."
    )
    y = _wrap_text(c, text2, MARGIN, y, W - 2 * MARGIN, "Helvetica-Oblique", 11, 16, INK_SOFT)
    y -= 20
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(W / 2, y, "« L'univers ne demande qu'a se ranger de ton cote —")
    y -= 16
    c.drawCentredString(W / 2, y, "encore faut-il que tu lui laisses l'espace de le faire. »")
    y -= 40
    c.setFillColor(INK)
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W / 2, y, "Alors, quel est le premier geste que tu vas poser cette semaine")
    y -= 14
    c.drawCentredString(W / 2, y, "pour honorer cette guidance ?")
    y -= 40
    c.setFillColor(GOLD_LIGHT)
    c.setFont("Helvetica-Oblique", 14)
    c.drawCentredString(W / 2, y, "— Solena")
    c.setFont("Helvetica", 8)
    c.setFillColor(INK_SOFT)
    c.drawCentredString(W / 2, y - 16, "La voix de Plume Astrale")


# ═══════════════════════════════ Synastrie 12 domaines ═══════════════════════════════

def _p_synastry_intro(c, page_num, first_name, partner_name, synastry):
    """Page d'ouverture du chapitre synastrie : score global + dynamique du lien."""
    _p_interior_bg(c, page_num)
    n1 = (first_name or 'Toi').strip().title()
    n2 = (partner_name or 'Ton partenaire').strip().title()
    y = _p_title(c, "Votre synastrie", f"Vous deux — {n1} & {n2}")

    score = synastry.get('overall_score') or 0
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 42)
    c.drawCentredString(W / 2, y - 30, f"{score} / 100")
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W / 2, y - 46, "SCORE DE COMPATIBILITE GLOBAL")
    y -= 80

    dyn = synastry.get('dynamic_type') or ''
    if dyn:
        c.setFillColor(INK)
        c.setFont("Helvetica-Oblique", 12)
        c.drawCentredString(W / 2, y, f"Dynamique du lien : {dyn}")
        y -= 22

    harmony = synastry.get('harmony')
    tension = synastry.get('tension')
    if harmony is not None:
        bar_w = W - 2 * MARGIN
        c.setFillColor(HexColor('#e7ddc9'))
        c.roundRect(MARGIN, y - 10, bar_w, 10, 5, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.roundRect(MARGIN, y - 10, bar_w * max(0.02, min(1.0, harmony / 100.0)), 10, 5, fill=1, stroke=0)
        c.setFillColor(INK_SOFT)
        c.setFont("Helvetica", 8)
        c.drawString(MARGIN, y - 24, f"Harmonie {harmony}%")
        c.drawRightString(W - MARGIN, y - 24, f"Tension {tension}%")
        y -= 48

    summary = synastry.get('summary_fr') or ''
    if summary:
        y = _wrap_text(c, summary, MARGIN, y, W - 2 * MARGIN, "Helvetica", 10.5, 15)
        y -= 16

    c.setFillColor(GOLD)
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W / 2, max(y, 3 * cm), "Les 12 domaines de votre vie a deux, decodes dans les pages suivantes.")


def _p_synastry_areas(c, page_num, areas_chunk):
    """Rend jusqu'a 3 domaines de vie par page (titre + barre de score + texte FR)."""
    _p_interior_bg(c, page_num)
    y = _p_title(c, "Votre synastrie", "Les 12 domaines de vie")
    for a in areas_chunk:
        name = a.get('name_fr') or ''
        score = a.get('score') or 0
        text = a.get('text_fr') or ''
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(MARGIN, y, name)
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(W - MARGIN, y, f"{score}/100")
        y -= 10
        bar_w = W - 2 * MARGIN
        c.setFillColor(HexColor('#e7ddc9'))
        c.roundRect(MARGIN, y - 5, bar_w, 5, 2.5, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.roundRect(MARGIN, y - 5, bar_w * max(0.02, min(1.0, score / 100.0)), 5, 2.5, fill=1, stroke=0)
        y -= 18
        if text:
            y = _wrap_text(c, text, MARGIN, y, W - 2 * MARGIN, "Helvetica", 9.5, 13.5)
        y -= 20
        if y < 4 * cm:
            break


# ═══════════════════════════════ Fenetres calendrier ═══════════════════════════════
FR_MONTHS = ['janvier','fevrier','mars','avril','mai','juin',
             'juillet','aout','septembre','octobre','novembre','decembre']

_VENUS_TRANSIT_SIGNS = ['Belier','Taureau','Gemeaux','Cancer','Lion','Vierge',
                        'Balance','Scorpion','Sagittaire','Capricorne','Verseau','Poissons']

def _compute_windows(now=None):
    """Retourne 3 fenetres de rencontre sur 6 mois. Approximation calendaire — pas d'ephemerides."""
    now = now or datetime.now(timezone.utc)
    windows = []
    for i, (start_delta, end_delta) in enumerate([(0, 2), (2, 4), (4, 6)]):
        s = now + timedelta(days=start_delta * 30)
        e = now + timedelta(days=end_delta * 30)
        start_label = f"{FR_MONTHS[s.month - 1]} {s.year}".title()
        end_label = f"{FR_MONTHS[e.month - 1]} {e.year}".title()
        # Signe de Venus (approximation lineaire — 1 signe/mois)
        venus_offset = (s.month - 1 + i) % 12
        venus_sign = _VENUS_TRANSIT_SIGNS[venus_offset]
        rituals = [
            "Allume une bougie rose chaque vendredi soir, 21 minutes.",
            "Porte du quartz rose 3 jours consecutifs a chaque nouvelle lune de la periode.",
            "Ecris 3 gratitudes amoureuses avant de dormir, 7 jours d'affilee.",
        ]
        windows.append({
            'start': start_label,
            'end': end_label,
            'venus_sign': venus_sign,
            'ritual': rituals[i],
        })
    return windows


# ═══════════════════════════════ Generation principale ═══════════════════════════════

class RencontresUltimePDFGenerator:
    def generate(self, birth_date_iso: str, first_name: str, m7_sign: str,
                 venus_sign: str, mars_sign: str,
                 partner_name: str = '', synastry: dict | None = None) -> bytes:
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        c.setTitle("Guide de Compatibilite Ultime — Plume Astrale")
        c.setAuthor("Solena · Plume Astrale")

        sun_sign = _sign_from_iso_date(birth_date_iso)

        # 1. Couverture
        _p_cover(c, sun_sign, first_name); c.showPage()
        # 2. Sommaire
        _p_sommaire(c, first_name); c.showPage()
        # 3. Boussole
        _p_boussole(c, 3, sun_sign, m7_sign, venus_sign, mars_sign, first_name); c.showPage()
        # 4. Soleil en amour
        _p_soleil(c, 4, sun_sign, first_name); c.showPage()
        # 5. Lune
        _p_lune(c, 5, sun_sign); c.showPage()
        # 6. Venus
        _p_venus(c, 6, venus_sign or sun_sign); c.showPage()
        # 7. Mars
        _p_mars(c, 7, mars_sign or sun_sign); c.showPage()
        # 8. Maison V (approximee par le signe solaire — nuance)
        _p_maison_v(c, 8, sun_sign); c.showPage()
        # 9. Maison VII (donnee par le reveal)
        _p_maison_vii(c, 9, m7_sign or sun_sign); c.showPage()
        # 10. Portrait-Robot
        _p_portrait_robot(c, 10, m7_sign or sun_sign, first_name); c.showPage()

        page = 11
        # 11+. Chapitre Synastrie — 12 domaines de vie (si partenaire fourni)
        if synastry and synastry.get('areas'):
            _p_synastry_intro(c, page, first_name, partner_name, synastry); c.showPage(); page += 1
            areas = synastry['areas']
            for i in range(0, len(areas), 3):
                _p_synastry_areas(c, page, areas[i:i + 3]); c.showPage(); page += 1

        # Fenetres de rencontre
        windows = _compute_windows()
        for i, w in enumerate(windows):
            _p_fenetre(c, page, i + 1, w['start'], w['end'], w['venus_sign'], w['ritual'])
            c.showPage(); page += 1
        # Rituels
        _p_rituels(c, page); c.showPage(); page += 1
        # Benediction
        _p_benediction(c, page, first_name); c.showPage()

        c.save()
        return buf.getvalue()


def generate_rencontres_ultime_pdf(birth_date_iso: str, first_name: str, m7_sign: str,
                                    venus_sign: str, mars_sign: str,
                                    partner_name: str = '', synastry: dict | None = None) -> bytes:
    """Point d'entree public."""
    return RencontresUltimePDFGenerator().generate(
        birth_date_iso=birth_date_iso,
        first_name=first_name or 'Ami(e)',
        m7_sign=m7_sign or 'Balance',
        venus_sign=venus_sign or _sign_from_iso_date(birth_date_iso),
        mars_sign=mars_sign or _sign_from_iso_date(birth_date_iso),
        partner_name=partner_name or '',
        synastry=synastry,
    )
