"""
Generateur PDF Synastrie 25 pages — Plume Astrale (haut-ticket 49€).

Style "Mix" (choix utilisateur 5C) :
  - Page 1 : couverture sombre doree (DEEP_PURPLE + GOLD)
  - Pages 2-25 : fond creme + encre profonde (lisibilite optimale)

Structure (25 pages exactes — choix utilisateur 4C+1a) :
   1. Couverture
   2. Sommaire poetique
   3. Theme de [Personne 1]
   4. Theme de [Personne 2]
   5. Soleils en miroir
   6. Lunes en miroir
   7. Mercure & Mercure
   8. Venus en miroir
   9. Mars en miroir
  10. Jupiter & Saturne
  11. Aspects harmonieux
  12. Aspects de tension
  13. Conjonctions notables
  14. Maisons croisees
  15. Langages d'amour (Venus)
  16. Sexualite & sensualite
  17. Communication quotidienne
  18. Vie commune & projets
  19. Enfants & creativite
  20. Argent & valeurs partagees
  21. Voyages & horizons
  22. Forces relationnelles
  23. 3 invitations concretes
  24. Transits du mois
  25. Benediction de la Plume

Placeholder images : si une image existe dans /app/backend/assets/synastrie_pdf/page-XX.{png,jpg},
elle est inseree automatiquement. Sinon, un cadre dore vide tient lieu de placeholder
(en attendant que l'utilisateur fournisse les illustrations).
"""
import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ───────────────────── Police Unicode (zodiac glyphs) ─────────────────────
_UNICODE_FONT = "Helvetica"  # fallback
try:
    _FREESANS = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
    if os.path.exists(_FREESANS):
        pdfmetrics.registerFont(TTFont("FreeSerif", _FREESANS))
        _UNICODE_FONT = "FreeSerif"
except Exception:
    pass

# ───────────────────── Palette ─────────────────────
DEEP_PURPLE = HexColor('#0C0918')
MEDIUM_PURPLE = HexColor('#1E1A33')
GOLD = HexColor('#D4B46A')
GOLD_LIGHT = HexColor('#F4D98C')
CREAM = HexColor('#F5EFE0')       # Fond pages interieures
INK = HexColor('#2A2233')         # Texte principal interieur
INK_SOFT = HexColor('#5C5168')    # Texte secondaire
ROSE = HexColor('#C97878')
TWILIGHT = HexColor('#A78BFA')

# ───────────────────── Donnees astro (reutilisees) ─────────────────────
SIGNS = {
    "Bélier":      {"el": "Feu",   "mod": "Cardinal", "ruler": "Mars",    "glyph": "♈", "trait": "courageux, direct, pionnier"},
    "Taureau":     {"el": "Terre", "mod": "Fixe",     "ruler": "Vénus",   "glyph": "♉", "trait": "sensuel, stable, fidèle"},
    "Gémeaux":     {"el": "Air",   "mod": "Mutable",  "ruler": "Mercure", "glyph": "♊", "trait": "curieux, vif, adaptable"},
    "Cancer":      {"el": "Eau",   "mod": "Cardinal", "ruler": "Lune",    "glyph": "♋", "trait": "protecteur, intuitif, nourrissant"},
    "Lion":        {"el": "Feu",   "mod": "Fixe",     "ruler": "Soleil",  "glyph": "♌", "trait": "rayonnant, généreux, loyal"},
    "Vierge":      {"el": "Terre", "mod": "Mutable",  "ruler": "Mercure", "glyph": "♍", "trait": "attentionné, précis, dévoué"},
    "Balance":     {"el": "Air",   "mod": "Cardinal", "ruler": "Vénus",   "glyph": "♎", "trait": "harmonieux, esthète, diplomate"},
    "Scorpion":    {"el": "Eau",   "mod": "Fixe",     "ruler": "Pluton",  "glyph": "♏", "trait": "intense, passionné, transformateur"},
    "Sagittaire":  {"el": "Feu",   "mod": "Mutable",  "ruler": "Jupiter", "glyph": "♐", "trait": "aventurier, philosophe, optimiste"},
    "Capricorne":  {"el": "Terre", "mod": "Cardinal", "ruler": "Saturne", "glyph": "♑", "trait": "ambitieux, structuré, fiable"},
    "Verseau":     {"el": "Air",   "mod": "Fixe",     "ruler": "Uranus",  "glyph": "♒", "trait": "original, humaniste, libre"},
    "Poissons":    {"el": "Eau",   "mod": "Mutable",  "ruler": "Neptune", "glyph": "♓", "trait": "empathique, rêveur, créatif"},
}

ELEMENT_PAIR = {
    frozenset(["Feu", "Feu"]):     ("Brasier partagé", "Vous nourrissez ensemble une flamme qui se réchauffe au contact de l'autre."),
    frozenset(["Feu", "Terre"]):   ("Volcan et roc", "Le Feu inspire ce que la Terre concrétise. Patience et respect des rythmes."),
    frozenset(["Feu", "Air"]):     ("Souffle qui attise", "L'Air donne au Feu de l'espace pour s'étendre. Combinaison vibrante."),
    frozenset(["Feu", "Eau"]):     ("Vapeur et passion", "Tension féconde si chacun honore le langage de l'autre."),
    frozenset(["Terre", "Terre"]): ("Fondations jumelles", "Sécurité, fiabilité, construction. Veillez à ne pas vous endormir."),
    frozenset(["Terre", "Air"]):   ("Le vent sur la montagne", "L'Air conceptualise, la Terre concrétise. Complémentarité productive."),
    frozenset(["Terre", "Eau"]):   ("Jardin fertile", "L'Eau nourrit la Terre. Foyer chaleureux et stable."),
    frozenset(["Air", "Air"]):     ("Dialogue d'esprits", "Stimulation intellectuelle infinie. Cultivez l'ancrage émotionnel."),
    frozenset(["Air", "Eau"]):     ("Brume et révélation", "L'Air met des mots sur ce que l'Eau ressent. Délicate alchimie."),
    frozenset(["Eau", "Eau"]):     ("Océan partagé", "Profondeur émotionnelle, intuition mutuelle. Gardez un cadre."),
}

# ───────────────────── Helpers ─────────────────────
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'synastrie_pdf')


def _sign_from_date(date_str):
    """Retourne le signe solaire francais a partir d'une date YYYY-MM-DD."""
    try:
        d = datetime.fromisoformat(date_str).date()
        m, day = d.month, d.day
    except Exception:
        return "Bélier"
    if (m == 3 and day >= 21) or (m == 4 and day <= 19): return "Bélier"
    if (m == 4 and day >= 20) or (m == 5 and day <= 20): return "Taureau"
    if (m == 5 and day >= 21) or (m == 6 and day <= 20): return "Gémeaux"
    if (m == 6 and day >= 21) or (m == 7 and day <= 22): return "Cancer"
    if (m == 7 and day >= 23) or (m == 8 and day <= 22): return "Lion"
    if (m == 8 and day >= 23) or (m == 9 and day <= 22): return "Vierge"
    if (m == 9 and day >= 23) or (m == 10 and day <= 22): return "Balance"
    if (m == 10 and day >= 23) or (m == 11 and day <= 21): return "Scorpion"
    if (m == 11 and day >= 22) or (m == 12 and day <= 21): return "Sagittaire"
    if (m == 12 and day >= 22) or (m == 1 and day <= 19): return "Capricorne"
    if (m == 1 and day >= 20) or (m == 2 and day <= 18): return "Verseau"
    return "Poissons"


def _element_pair(s1, s2):
    e1 = SIGNS.get(s1, {}).get('el', 'Feu')
    e2 = SIGNS.get(s2, {}).get('el', 'Feu')
    return e1, e2, ELEMENT_PAIR.get(frozenset([e1, e2]), ("Rencontre", "Une alchimie singulière à explorer."))


def _find_page_image(page_num):
    """Cherche /app/backend/assets/synastrie_pdf/page-XX.{png,jpg,jpeg}."""
    if not os.path.isdir(ASSETS_DIR):
        return None
    for ext in ('png', 'jpg', 'jpeg', 'webp'):
        path = os.path.join(ASSETS_DIR, f'page-{page_num:02d}.{ext}')
        if os.path.exists(path):
            return path
    return None


_MONTHS_FR = ['', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
              'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']


def _date_fr(d=None):
    d = d or datetime.now()
    return f"{d.day} {_MONTHS_FR[d.month]} {d.year}"


# ───────────────────── Generateur ─────────────────────
class SynastriePDFGenerator:
    def __init__(self):
        self.w, self.h = A4
        self.margin = 2.2 * cm
        self.body_top = self.h - 2.5 * cm
        self.body_bottom = 2.2 * cm

    # ── Backgrounds ──
    def _bg_cover(self, c):
        """Fond couverture : illustration de fond si presente, sinon halo dore."""
        c.setFillColor(DEEP_PURPLE)
        c.rect(0, 0, self.w, self.h, fill=1, stroke=0)

        # Si page-01.{png,jpg,...} existe -> on l'utilise comme fond plein-cadre
        cover_img = _find_page_image(1)
        if cover_img:
            try:
                # Plein cadre, tamise pour laisser respirer le titre par-dessus
                c.saveState()
                c.drawImage(cover_img, 0, 0, self.w, self.h,
                            preserveAspectRatio=True, anchor='c', mask='auto')
                c.restoreState()
                # Voile sombre haut/bas pour le contraste du texte
                c.setFillColor(DEEP_PURPLE)
                c.setFillAlpha(0.55)
                c.rect(0, 0, self.w, self.h, fill=1, stroke=0)
                c.setFillAlpha(1.0)
                return
            except Exception:
                pass

        # Fallback : halo dore + illustration hero locale (cœurs entrelaces)
        for i, alpha in enumerate([0.04, 0.08, 0.12, 0.16, 0.20]):
            c.setFillColor(GOLD)
            c.setFillAlpha(alpha)
            r = 12 * cm - i * 2 * cm
            c.circle(self.w / 2, self.h - 9 * cm, r, fill=1, stroke=0)
        c.setFillAlpha(1.0)

        # Injection du hero V3 (deux cœurs entrelacés) — au centre haut
        from pathlib import Path as _P
        _hero = _P('/app/backend/assets/pdf_covers/synastrie_hero.png')
        if _hero.exists():
            try:
                size = 10 * cm
                x = (self.w - size) / 2
                y = self.h - 4.5 * cm - size
                c.drawImage(str(_hero), x, y, size, size,
                            preserveAspectRatio=True, anchor='c', mask='auto')
            except Exception:
                pass

    def _bg_cream(self, c):
        """Fond pages interieures : creme + cadre or pointille + filets dores."""
        c.setFillColor(CREAM)
        c.rect(0, 0, self.w, self.h, fill=1, stroke=0)
        # Cadre or pointille (charte prestige unifiee)
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.35)
        c.setDash([0.6, 2.4], 0)
        c.rect(1.2 * cm, 1.2 * cm, self.w - 2.4 * cm, self.h - 2.4 * cm, fill=0, stroke=1)
        c.setDash([], 0)
        # Filet superieur dore (repere de tete de page)
        c.setLineWidth(0.4)
        c.line(self.margin, self.h - 1.5 * cm, self.w - self.margin, self.h - 1.5 * cm)
        # Filet inferieur
        c.line(self.margin, 1.5 * cm, self.w - self.margin, 1.5 * cm)
        # Soleil ornemental discret en haut au centre
        c.setFillColor(GOLD)
        c.circle(self.w / 2, self.h - 1.55 * cm, 0.10 * cm, fill=1, stroke=0)

    # ── Footer (sauf couverture) ──
    def _footer(self, c, page_num, total=25):
        c.setFillColor(INK_SOFT)
        c.setFont("Helvetica", 6.5)
        c.drawString(2 * cm, 0.75 * cm, "PLUME ASTRALE · SYNASTRIE")
        c.drawRightString(self.w - 2 * cm, 0.75 * cm, f"— {page_num} —")

    # ── Wrapping helpers ──
    def _wrap(self, text, font, size, max_w, c):
        if not text:
            return []
        out, line = [], ""
        for word in text.split():
            test = (line + " " + word).strip()
            if c.stringWidth(test, font, size) <= max_w:
                line = test
            else:
                if line:
                    out.append(line)
                line = word
        if line:
            out.append(line)
        return out

    def _text_block(self, c, text, x, y, max_w, font="Helvetica", size=10, color=INK, leading=1.55):
        if not text:
            return y
        c.setFillColor(color)
        c.setFont(font, size)
        lines = self._wrap(text, font, size, max_w, c)
        lh = size * leading / 28.35 * cm
        for ln in lines:
            c.drawString(x, y, ln)
            y -= lh
        return y - lh * 0.2

    def _centered_text(self, c, text, y, font="Helvetica", size=10, color=INK):
        c.setFillColor(color)
        c.setFont(font, size)
        c.drawCentredString(self.w / 2, y, text)

    # ── Header pour pages interieures ──
    def _interior_header(self, c, kicker, title, subtitle=None):
        """Kicker dore + titre serif + sous-titre italique."""
        y = self.h - 3 * cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(self.w / 2, y, kicker.upper())
        y -= 0.9 * cm
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 19)
        c.drawCentredString(self.w / 2, y, title)
        y -= 0.7 * cm
        if subtitle:
            c.setFillColor(INK_SOFT)
            c.setFont("Helvetica-Oblique", 10.5)
            c.drawCentredString(self.w / 2, y, subtitle)
            y -= 0.4 * cm
        # Filet dore court sous le titre
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.8)
        c.line(self.w / 2 - 1.5 * cm, y, self.w / 2 + 1.5 * cm, y)
        return y - 1 * cm

    def _illustration_slot(self, c, page_num, y, h=8 * cm):
        """Insere une illustration si presente, sinon cadre placeholder dore.
        L'image preserve son ratio et est centree dans le slot avec un cadre dore subtil.
        Retourne le nouveau y (apres le slot)."""
        img_path = _find_page_image(page_num)
        slot_w = self.w - 2 * self.margin - 1 * cm
        slot_h = h
        x = (self.w - slot_w) / 2
        bottom = y - slot_h

        if img_path:
            try:
                # Detecte les dimensions reelles de l'image pour bien la centrer
                from reportlab.lib.utils import ImageReader
                ir = ImageReader(img_path)
                iw, ih = ir.getSize()
                ratio = iw / ih if ih else 1
                # Scale pour fit dans le slot en preservant le ratio
                if slot_w / slot_h > ratio:
                    # Limite par hauteur
                    draw_h = slot_h
                    draw_w = draw_h * ratio
                else:
                    draw_w = slot_w
                    draw_h = draw_w / ratio
                draw_x = x + (slot_w - draw_w) / 2
                draw_y = bottom + (slot_h - draw_h) / 2
                # Cadre fin dore autour de l'image (elegance editoriale)
                c.setStrokeColor(GOLD)
                c.setLineWidth(0.4)
                c.rect(draw_x - 2, draw_y - 2, draw_w + 4, draw_h + 4, fill=0, stroke=1)
                c.drawImage(img_path, draw_x, draw_y, draw_w, draw_h, mask='auto')
                return bottom - 0.6 * cm
            except Exception:
                self._draw_placeholder(c, x, bottom, slot_w, slot_h, page_num)
        else:
            self._draw_placeholder(c, x, bottom, slot_w, slot_h, page_num)
        return bottom - 0.6 * cm

    def _draw_placeholder(self, c, x, y, w, h, page_num):
        """Cadre dore subtil avec mention 'illustration page XX'."""
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.5)
        c.setDash(3, 3)
        c.roundRect(x, y, w, h, 6, fill=0, stroke=1)
        c.setDash()  # reset
        c.setFillColor(GOLD)
        c.setFillAlpha(0.5)
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(x + w / 2, y + h / 2, f"illustration · page {page_num}")
        c.setFillAlpha(1.0)

    # ════════════════════════════════════════
    #  PAGE 1 — COUVERTURE
    # ════════════════════════════════════════
    def _page_01_cover(self, c, p1, p2, s1, s2):
        self._bg_cover(c)

        # Header brand
        y = self.h - 4 * cm
        c.setFillColor(GOLD)
        c.setFont(_UNICODE_FONT, 9)
        c.drawCentredString(self.w / 2, y, "✦  PLUME ASTRALE  ✦")
        y -= 0.8 * cm
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.5)
        c.line(self.w / 2 - 2 * cm, y, self.w / 2 + 2 * cm, y)
        y -= 2 * cm

        # Glyphes signes
        c.setFillColor(GOLD_LIGHT)
        c.setFont(_UNICODE_FONT, 50)
        glyph1 = SIGNS.get(s1, {}).get('glyph', '*')
        glyph2 = SIGNS.get(s2, {}).get('glyph', '*')
        c.drawCentredString(self.w / 2, y, f"{glyph1}     {glyph2}")
        y -= 2.5 * cm

        # Titre principal
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(self.w / 2, y, "Astrologie")
        y -= 0.95 * cm
        c.drawCentredString(self.w / 2, y, "Relationnelle")
        y -= 1 * cm
        c.setFillColor(GOLD_LIGHT)
        c.setFont("Helvetica-Oblique", 14)
        c.drawCentredString(self.w / 2, y, "le rapport de votre lien")
        y -= 3 * cm

        # Noms — dorure gaufrée façon livre imprimé (édition personnelle pour un couple)
        n1 = (p1.get('prenom') or '').strip().title()
        n2 = (p2.get('prenom') or '').strip().title()

        # Petit filet + label "ÉDITION PERSONNELLE"
        c.setFillColor(GOLD)
        c.setFont("Helvetica", 6)
        c.drawCentredString(self.w / 2, y, "·   ·   ·")
        y -= 0.5 * cm
        c.setFillColor(INK_SOFT)
        c.setFont("Helvetica", 7)
        c.drawCentredString(self.w / 2, y, "É D I T I O N  ·  P E R S O N N E L L E  ·  P O U R")
        y -= 1.1 * cm

        # Prénom 1 (or vif, letter-spacé via espaces)
        c.setFillColor(GOLD_LIGHT)
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(self.w / 2, y, ' '.join(n1.upper()))
        y -= 1.1 * cm
        # &
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Oblique", 15)
        c.drawCentredString(self.w / 2, y, "&")
        y -= 1.1 * cm
        # Prénom 2
        c.setFillColor(GOLD_LIGHT)
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(self.w / 2, y, ' '.join(n2.upper()))
        y -= 0.5 * cm
        # Filet doré final
        c.setFillColor(GOLD)
        c.setFont("Helvetica", 6)
        c.drawCentredString(self.w / 2, y, "·   ·   ·")
        y -= 2.0 * cm

        # Footer date
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.3)
        c.line(self.w / 2 - 3 * cm, y, self.w / 2 + 3 * cm, y)
        y -= 0.8 * cm
        c.setFillColor(CREAM)
        c.setFillAlpha(0.7)
        c.setFont("Helvetica", 9.5)
        c.drawCentredString(self.w / 2, y, f"Composé le {_date_fr()}")
        y -= 0.5 * cm
        c.drawCentredString(self.w / 2, y, "Document personnel et confidentiel")
        c.setFillAlpha(1.0)

    # ════════════════════════════════════════
    #  PAGE 2 — SOMMAIRE
    # ════════════════════════════════════════
    def _page_02_toc(self, c):
        self._bg_cream(c)
        y = self._interior_header(c, "Au fil des pages", "Sommaire poétique",
                                   "Ce que vous découvrirez dans ce rapport")
        sections = [
            ("I. Le vivant en vous deux", [(3, "Votre thème natal individuel"), (4, "Le thème de l'autre")]),
            ("II. Les sept lumières en miroir", [(5, "Soleils — l'identité profonde"), (6, "Lunes — les besoins intimes"),
                                                  (7, "Mercures — la pensée partagée"), (8, "Vénus — le langage d'amour"),
                                                  (9, "Mars — le désir et l'action"), (10, "Jupiter & Saturne — grandir ensemble")]),
            ("III. Les aspects de votre lien", [(11, "Aspects harmonieux"), (12, "Aspects de tension"),
                                                 (13, "Conjonctions notables"), (14, "Maisons croisées")]),
            ("IV. Les territoires de l'amour", [(15, "Langages amoureux (Vénus)"), (16, "Sensualité"),
                                                 (17, "Communication quotidienne")]),
            ("V. Bâtir ensemble", [(18, "Vie commune & projets"), (19, "Enfants & créativité"),
                                    (20, "Argent & valeurs partagées"), (21, "Voyages & horizons")]),
            ("VI. Le chemin", [(22, "Vos forces relationnelles"), (23, "Trois invitations concrètes"),
                                (24, "Transits du mois"), (25, "Bénédiction de la Plume")]),
        ]
        x_left = self.margin + 0.5 * cm
        max_w = self.w - 2 * self.margin - 1 * cm
        for section_title, items in sections:
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x_left, y, section_title.upper())
            y -= 0.55 * cm
            for page_num, label in items:
                c.setFillColor(INK)
                c.setFont("Helvetica", 9.5)
                c.drawString(x_left + 0.3 * cm, y, label)
                # Dots
                dots_x_start = x_left + 0.3 * cm + c.stringWidth(label, "Helvetica", 9.5) + 0.2 * cm
                dots_x_end = x_left + max_w - 0.8 * cm
                c.setFillColor(INK_SOFT)
                c.drawString(dots_x_start, y, '·' * int((dots_x_end - dots_x_start) / 3.5))
                c.setFillColor(GOLD)
                c.setFont("Helvetica-Bold", 9.5)
                c.drawRightString(x_left + max_w, y, str(page_num))
                y -= 0.42 * cm
            y -= 0.3 * cm
        self._footer(c, 2)

    # ════════════════════════════════════════
    #  PAGE 3-4 — THEMES NATALS INDIVIDUELS
    # ════════════════════════════════════════
    def _page_personal_theme(self, c, page_num, person, sign, enriched_text=None):
        self._bg_cream(c)
        n = (person.get('prenom') or '').strip().title()
        info = SIGNS.get(sign, {})
        glyph = info.get('glyph', '')
        # Subtitle avec glyph en police Unicode (composé séparément)
        sub_main = f"{sign}    —    {info.get('el', '')} · {info.get('mod', '')} · {info.get('ruler', '')}"
        y = self._interior_header(c, f"Page {page_num} · Portrait natal", f"Le thème de {n}", sub_main)
        # Glyph dore au-dessus de l'illustration (police Unicode)
        if glyph:
            c.setFillColor(GOLD)
            c.setFont(_UNICODE_FONT, 24)
            c.drawCentredString(self.w / 2, y + 0.2 * cm, glyph)
            y -= 1 * cm

        y = self._illustration_slot(c, page_num, y, h=5 * cm)

        x_left = self.margin + 0.5 * cm
        max_w = self.w - 2 * self.margin - 1 * cm

        # Date + naissance
        birth = person.get('birth_date', '')
        time = person.get('birth_time') or '—'
        place = person.get('birth_place') or '—'

        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(x_left, y, "Naissance")
        y -= 0.5 * cm
        c.setFillColor(INK)
        c.setFont("Helvetica", 9.5)
        c.drawString(x_left, y, f"{birth}  ·  {time}  ·  {place}")
        y -= 0.8 * cm

        # Resume (enriched via LLM si dispo)
        if enriched_text:
            paragraphs = [p.strip() for p in enriched_text.split('\n\n') if p.strip()]
            for para in paragraphs:
                y = self._text_block(c, para, x_left, y, max_w, size=9.5, leading=1.5)
                y -= 0.15 * cm
                if y < 2.5 * cm:
                    break
        else:
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 9.5)
            c.drawString(x_left, y, "L'empreinte céleste")
            y -= 0.5 * cm
            intro = (
                f"{n} est né(e) sous le signe du {sign}, gouverné par {info.get('ruler', '')}. "
                f"C'est un signe de {info.get('el', '')}, de modalité {info.get('mod', '')}. "
                f"Au cœur de sa personnalité résonnent ces qualités : {info.get('trait', '')}. "
                "Ces traits ne définissent pas son destin, mais éclairent la couleur de son énergie de base — "
                "le sol sur lequel sa relation va se déployer."
            )
            y = self._text_block(c, intro, x_left, y, max_w, size=10.5, leading=1.6)

        self._footer(c, page_num)

    # ════════════════════════════════════════
    #  Generic "miroir" page (Soleils, Lunes, etc.)
    # ════════════════════════════════════════
    def _page_miroir(self, c, page_num, kicker, title, subtitle, intro_text, body_paragraphs, illu_h=6 * cm):
        self._bg_cream(c)
        y = self._interior_header(c, kicker, title, subtitle)
        y = self._illustration_slot(c, page_num, y, h=illu_h)
        x_left = self.margin + 0.5 * cm
        max_w = self.w - 2 * self.margin - 1 * cm
        # Intro citation
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Oblique", 10)
        for line in self._wrap(intro_text, "Helvetica-Oblique", 10, max_w - 1 * cm, c):
            c.drawCentredString(self.w / 2, y, line)
            y -= 0.5 * cm
        y -= 0.4 * cm
        # Body paragraphs
        for para in body_paragraphs:
            y = self._text_block(c, para, x_left, y, max_w, size=10, leading=1.55)
            y -= 0.2 * cm
        self._footer(c, page_num)

    # ════════════════════════════════════════
    #  PAGES 5-10 : 7 lumières en miroir
    # ════════════════════════════════════════
    def _page_05_soleils(self, c, n1, n2, s1, s2, enriched_text=None):
        e1, e2, pair = _element_pair(s1, s2)
        self._page_miroir_enriched(c, 5, "V · Les sept lumières", "Soleils en miroir",
            "L'identité profonde, le cœur rayonnant",
            "« Le Soleil est ce que nous donnons au monde. »",
            fallback_paragraphs=[
                f"{n1} brille en {s1}, {n2} brille en {s2}. Vos deux identités essentielles se reconnaissent à travers les éléments {e1} et {e2} — une rencontre que les astres nomment « {pair[0]} ».",
                pair[1],
                f"Concrètement : ce qui rayonne chez {n1} (l'esprit du {s1}) et ce qui rayonne chez {n2} (l'esprit du {s2}) sont les deux pôles d'une même boussole. Honorer le Soleil de l'autre, c'est laisser l'autre exister pleinement à côté de soi, sans chercher à le redessiner.",
                "Invitation : prenez chaque semaine un moment pour reconnaître à voix haute ce que vous aimez chez l'autre tel qu'il est, dans ce qu'il a d'irréductible."
            ], enriched_text=enriched_text)

    def _page_06_lunes(self, c, n1, n2, enriched_text=None):
        self._page_miroir_enriched(c, 6, "V · Les sept lumières", "Lunes en miroir",
            "Les besoins intimes, la mémoire émotionnelle",
            "« La Lune est ce qui nous apaise. »",
            fallback_paragraphs=[
                f"La Lune dit comment {n1} et {n2} se sentent en sécurité dans le lien. Elle évoque l'enfant intérieur, les habitudes émotionnelles, la façon de nourrir et d'être nourri(e).",
                "Quand deux Lunes s'entendent, le foyer émotionnel devient un refuge naturel : les mots ne sont plus nécessaires pour comprendre. Quand elles divergent, l'apprentissage est de traduire un langage émotionnel dans celui de l'autre, sans interprétation.",
                f"Demandez-vous : qu'est-ce qui apaise {n1} en fin de journée ? Qu'est-ce qui restaure {n2} après un moment difficile ? Souvent, les réponses sont simples — un mot, un geste, un silence — mais elles changent tout."
            ], enriched_text=enriched_text)

    def _page_07_mercure(self, c, n1, n2, enriched_text=None):
        self._page_miroir_enriched(c, 7, "V · Les sept lumières", "Mercure & Mercure",
            "La pensée partagée, le rythme de la parole",
            "« Mercure est ce qui circule entre vous. »",
            fallback_paragraphs=[
                f"Mercure gouverne la conversation, l'humour, la rapidité d'esprit. Entre {n1} et {n2}, la pensée peut danser à la même vitesse — ou différer, l'un préférant la nuance lente, l'autre les éclairs rapides.",
                "Aucun rythme n'est meilleur que l'autre. Le défi est d'apprendre où vos pensées se rencontrent et où elles divergent — non pour s'aligner, mais pour s'enrichir.",
                "Pratique : essayez une fois par mois un « tour de table » sans interruption. Chacun parle trois minutes, l'autre écoute sans répondre. Mercure adore la lenteur quand elle est consentie."
            ], enriched_text=enriched_text)

    def _page_08_venus(self, c, n1, n2, enriched_text=None):
        self._page_miroir_enriched(c, 8, "V · Les sept lumières", "Vénus en miroir",
            "Le langage d'amour, ce qui touche le cœur",
            "« Vénus est ce qui vous attire et ce que vous offrez. »",
            fallback_paragraphs=[
                f"Vénus dit comment {n1} aime et comment {n2} aime — souvent dans deux dialectes différents. L'un peut offrir l'amour par les mots, l'autre par les gestes, le troisième par la présence silencieuse.",
                "L'amour mal reçu n'est pas un amour mal donné — c'est souvent un amour traduit dans le mauvais idiome. La carte de Vénus dans votre thème commun est une grammaire à apprendre ensemble.",
                "Ce mois-ci, essayez de remarquer : quel geste de l'autre vous touche le plus ? Et inversement, lequel des vôtres semble le plus reçu ? Vous découvrirez vos langues maternelles amoureuses."
            ], enriched_text=enriched_text)

    def _page_09_mars(self, c, n1, n2, enriched_text=None):
        self._page_miroir_enriched(c, 9, "V · Les sept lumières", "Mars en miroir",
            "Le désir, l'action, la flamme",
            "« Mars est ce que vous voulez vraiment. »",
            fallback_paragraphs=[
                f"Mars dit l'élan, le désir, la manière de se battre pour ce qu'on aime. Entre {n1} et {n2}, Mars peut s'allier — projet commun, passion partagée — ou se confronter, créant des étincelles à apprivoiser.",
                "La sexualité, l'ambition, la colère, l'audace : tout cela appartient à Mars. Le couple qui sait nommer ce qu'il désire, sans culpabilité, est un couple où Mars chante au lieu de gronder.",
                "Invitation : exprimez chacun, en une phrase, ce que vous désirez profondément en ce moment dans la relation. Pas un reproche — un désir. Mars adore les désirs énoncés."
            ], enriched_text=enriched_text)

    def _page_10_jup_sat(self, c, n1, n2):
        self._page_miroir(c, 10, "V · Les sept lumières", "Jupiter & Saturne",
            "Grandir ensemble, traverser les saisons",
            "« Jupiter ouvre, Saturne enseigne. »",
            [
                "Ces deux planètes lentes orchestrent la croissance et la maturation d'un couple. Jupiter apporte la chance, l'expansion, la foi en ce qui est possible. Saturne apporte la patience, la responsabilité, ce qui dure.",
                f"Entre {n1} et {n2}, l'équilibre Jupiter/Saturne se joue sur des années. Trop de Jupiter et vous vous éparpillez ; trop de Saturne et vous vous figez. Le couple qui dure sait alterner les saisons.",
                "Question à explorer : qu'est-ce que ce lien vous demande de construire à long terme (Saturne) ? Et qu'est-ce qu'il vous offre comme horizon (Jupiter) ? Les deux réponses tracent votre chemin."
            ])

    # ════════════════════════════════════════
    #  PAGES 11-14 — Aspects + Maisons
    # ════════════════════════════════════════
    def _page_11_aspects_harm(self, c, n1, n2, enriched_text=None):
        self._page_miroir_enriched(c, 11, "VI · Les aspects", "Aspects harmonieux",
            "Trigones, sextiles — ce qui circule sans effort",
            "« Les aspects harmonieux sont les routes ouvertes. »",
            fallback_paragraphs=[
                f"Les trigones (120°) et sextiles (60°) entre vos planètes sont les zones où l'énergie circule librement entre {n1} et {n2}. Là, vous n'avez pas besoin de pousser : les choses s'arrangent presque seules.",
                "Mais attention : ce qui est facile peut être tenu pour acquis. Les couples qui durent honorent leurs trigones — ils s'arrêtent pour remarquer ce qui fonctionne, au lieu de ne voir que ce qui résiste.",
                "Cette semaine, listez trois domaines où votre relation est fluide. Nommez-les, célébrez-les, remerciez-les. Les routes ouvertes ne le restent que si on les emprunte avec gratitude."
            ], enriched_text=enriched_text)

    def _page_12_aspects_tension(self, c, n1, n2, enriched_text=None):
        self._page_miroir_enriched(c, 12, "VI · Les aspects", "Aspects de tension",
            "Carrés, oppositions — ce qui éveille",
            "« La tension n'est pas l'ennemie. Elle est l'éveilleuse. »",
            fallback_paragraphs=[
                f"Les carrés (90°) et oppositions (180°) entre vos thèmes ne sont pas des malédictions. Ce sont les points où la croissance vous appelle — là où {n1} et {n2} sont invités à dépasser leurs automatismes.",
                "Sans tension, pas de transformation. Les couples sans aspects difficiles s'endorment. Les couples qui apprennent à danser avec leurs tensions deviennent profonds.",
                "Quand un sujet revient en boucle entre vous, c'est souvent un aspect de tension qui parle. La question utile n'est pas « comment éviter ce sujet ? » mais « qu'est-ce qu'il essaie de nous enseigner ? »"
            ], enriched_text=enriched_text)

    def _page_13_conjonctions(self, c, n1, n2):
        self._page_miroir(c, 13, "VI · Les aspects", "Conjonctions notables",
            "Là où vos énergies fusionnent",
            "« Une conjonction, c'est une planète qui se reconnaît dans l'autre. »",
            [
                f"Les conjonctions (0°) sont les points où une planète de {n1} touche une planète de {n2}. À cet endroit, vos énergies se mélangent et deviennent presque indissociables.",
                "C'est puissant : vous pensez ensemble, vous désirez ensemble, vous rêvez ensemble. C'est aussi exigeant : il devient difficile de distinguer ce qui appartient à l'un et à l'autre.",
                "L'invitation est de cultiver des espaces individuels là où la conjonction est forte — pour que la fusion reste choisie, et non subie."
            ])

    def _page_14_maisons(self, c, n1, n2):
        self._page_miroir(c, 14, "VI · Les aspects", "Maisons croisées",
            "Où l'autre éclaire votre vie",
            "« Chacun éclaire douze secteurs de la vie de l'autre. »",
            [
                f"Quand les planètes de {n2} tombent dans les maisons de {n1} (et inversement), elles éclairent des zones précises de la vie : le foyer, le travail, les enfants, la spiritualité, l'argent, la santé.",
                "Cette cartographie est précieuse : elle révèle où vous êtes catalyseurs l'un pour l'autre. Parfois, votre partenaire active sans le vouloir un secteur de votre vie qui dormait — un talent, une peur, un appel.",
                "Question à poser : depuis que vous êtes ensemble, dans quel domaine avez-vous le plus changé ? La réponse pointe souvent une maison activée."
            ])

    # ════════════════════════════════════════
    #  PAGES 15-17 — Vie amoureuse
    # ════════════════════════════════════════
    def _page_15_langages(self, c, n1, n2):
        self._page_miroir(c, 15, "VII · Les territoires de l'amour", "Langages d'amour",
            "Selon Vénus, votre dialecte amoureux",
            "« Aimer, c'est apprendre la langue de l'autre. »",
            [
                "Selon la position de Vénus, chacun de vous parle un dialecte amoureux particulier. Les cinq grands langages — paroles valorisantes, gestes attentionnés, cadeaux, temps de qualité, contact physique — sont colorés par votre Vénus astrologique.",
                f"L'enjeu n'est pas que {n1} et {n2} parlent la même langue, mais qu'ils découvrent celle de l'autre et la pratiquent volontairement.",
                "Pratique des deux semaines à venir : chacun écrit sur un papier ses trois gestes d'amour préférés (qu'il aime recevoir). Échangez les papiers. Pendant 14 jours, offrez consciemment à l'autre ce qu'il a noté."
            ])

    def _page_16_sensualite(self, c, n1, n2):
        self._page_miroir(c, 16, "VII · Les territoires de l'amour", "Sensualité",
            "Mars, Vénus, la huitième maison",
            "« Le corps a sa propre langue. »",
            [
                f"L'intimité physique entre {n1} et {n2} est sculptée par Mars (le désir), Vénus (la tendresse) et la huitième maison (l'intensité partagée).",
                "Chaque couple a son propre rythme et sa propre carte du corps. Ce qui apaise l'un peut éveiller l'autre. Ce qui semble évident peut nécessiter d'être nommé.",
                "Le couple qui dure cultive la curiosité corporelle : non comme une performance, mais comme un dialogue. Le geste juste se trouve plus souvent dans le silence partagé que dans la technique apprise."
            ])

    def _page_17_communication(self, c, n1, n2):
        self._page_miroir(c, 17, "VII · Les territoires de l'amour", "Communication quotidienne",
            "Mercure, la troisième maison",
            "« Ce qu'on ne se dit pas devient ce qu'on s'inflige. »",
            [
                f"Au quotidien, comment circulent les mots entre {n1} et {n2} ? Les automatismes (« ça va », « rien de spécial ») peuvent ensevelir la rencontre véritable.",
                "Mercure, dans le thème commun, indique vos points de friction et vos points d'élégance dans la parole. Certains couples ont besoin de beaucoup de mots, d'autres de très peu — l'important est que les non-dits ne s'accumulent pas.",
                "Rituel suggéré : chaque dimanche, dix minutes pour partager une chose qui vous a touchés cette semaine (positif ou difficile). Pas de débat, juste l'écoute. Ce simple rendez-vous transforme un couple."
            ])

    # ════════════════════════════════════════
    #  PAGES 18-21 — Construire ensemble
    # ════════════════════════════════════════
    def _page_18_vie_commune(self, c, n1, n2):
        self._page_miroir(c, 18, "VIII · Bâtir ensemble", "Vie commune & projets",
            "La quatrième maison, la dixième, Saturne",
            "« Bâtir, c'est choisir ce qui restera. »",
            [
                "La quatrième maison parle du foyer, du nid, de l'intimité partagée. La dixième parle du couple comme projet visible, de ce que vous accomplissez ensemble dans le monde.",
                f"Entre {n1} et {n2}, ces deux pôles méritent d'être nourris consciemment. Un couple qui ne soigne que son intériorité s'étouffe. Un couple qui ne se vit que dans l'extérieur s'épuise.",
                "Saturne, le grand architecte, demande : quelle structure votre amour veut-il prendre ? Un foyer ? Un projet commun ? Un mode de vie partagé ? Plus vous nommez votre architecture, plus elle tient debout."
            ])

    def _page_19_enfants(self, c, n1, n2):
        self._page_miroir(c, 19, "VIII · Bâtir ensemble", "Enfants & créativité",
            "La cinquième maison, la Lune, Jupiter",
            "« Tout ce que vous créez ensemble est un enfant. »",
            [
                "La cinquième maison ne parle pas seulement des enfants biologiques. Elle parle de tout ce qui naît de votre rencontre : un projet artistique, une entreprise, un rituel, un voyage marquant, un acte de générosité partagé.",
                f"Que vous ayez ou non des enfants, {n1} et {n2}, votre couple génère. Demandez-vous : qu'est-ce que notre lien a créé que ni l'un ni l'autre n'aurait fait seul(e) ?",
                "Si la question des enfants se pose concrètement, regardez ce qu'éveille la cinquième maison entre vous : énergie joyeuse, énergie hésitante, énergie d'urgence ? La réponse est précieuse."
            ])

    def _page_20_argent(self, c, n1, n2):
        self._page_miroir(c, 20, "VIII · Bâtir ensemble", "Argent & valeurs partagées",
            "Deuxième et huitième maisons, Vénus",
            "« L'argent dans un couple est un miroir des valeurs. »",
            [
                "La deuxième maison parle de ce que chacun possède en propre — ressources, talents, sécurité. La huitième parle de ce qui est mis en commun, et de ce qui est transformé par l'union.",
                f"Beaucoup de tensions de couple naissent d'une confusion entre ces deux maisons. Quand {n1} et {n2} clarifient ce qui appartient à chacun et ce qui est mis en commun, l'argent devient un outil au lieu d'un enjeu.",
                "Question utile : si votre couple disposait d'une somme inattendue ce mois-ci, qu'en feriez-vous d'un commun accord ? La réponse révèle vos valeurs partagées plus que vos comptes."
            ])

    def _page_21_voyages(self, c, n1, n2):
        self._page_miroir(c, 21, "VIII · Bâtir ensemble", "Voyages & horizons",
            "La neuvième maison, Jupiter",
            "« Voyager ensemble, c'est se redécouvrir hors du quotidien. »",
            [
                "La neuvième maison parle des voyages, des études, des philosophies de vie, des grands horizons. Jupiter, son maître, demande : quelle est votre vision commune du monde ?",
                "Un couple qui voyage, qui apprend, qui s'expose au plus grand qu'eux-mêmes, est un couple qui grandit. Cela ne signifie pas forcément traverser des continents — cela peut être un livre lu à deux, un mentor partagé, un changement de perspective accepté ensemble.",
                "Invitation pour cette année : choisissez ensemble une chose plus grande que vous-mêmes que vous explorerez à deux. Un lieu, un savoir, un engagement. Jupiter récompense ceux qui osent."
            ])

    # ════════════════════════════════════════
    #  PAGES 22-25 — Le chemin
    # ════════════════════════════════════════
    def _page_22_forces(self, c, n1, n2, s1, s2, enriched_text=None):
        e1, e2, pair = _element_pair(s1, s2)
        self._page_miroir_enriched(c, 22, "IX · Le chemin", "Vos forces relationnelles",
            "Les trois atouts qui vous appartiennent",
            "« Connaître ses forces, c'est pouvoir s'y appuyer. »",
            fallback_paragraphs=[
                f"En tenant compte de l'alliance « {pair[0]} » entre vos éléments ({e1} et {e2}), trois forces se dessinent comme vous appartenant en propre.",
                f"Première force : la complémentarité naturelle entre l'énergie de {n1} et celle de {n2}. Ce qui peut sembler une différence est souvent une coopération en germe — chacun fait ce que l'autre ne ferait pas spontanément.",
                "Deuxième force : la capacité de votre couple à apprendre de ses tensions. Vos désaccords ne vous séparent pas — ils vous éveillent. Peu de couples savent transformer le conflit en compréhension.",
                "Troisième force : votre lien possède une fonction propre, qui dépasse le simple cumul de vos personnalités. Vous générez quelque chose qui n'existerait pas sans vous deux. Honorez cette troisième entité."
            ], enriched_text=enriched_text)

    def _page_23_invitations(self, c, n1, n2):
        self._page_miroir(c, 23, "IX · Le chemin", "Trois invitations concrètes",
            "À pratiquer dès cette semaine",
            "« L'amour se cultive par des gestes, pas par des concepts. »",
            [
                "Première invitation — Le rituel du soir : chaque soir, prenez trois minutes pour partager une chose que l'autre a faite ce jour et qui vous a touché(e). Pas de « merci » performatif — une observation précise.",
                "Deuxième invitation — Le rendez-vous sacré : une fois par mois, deux heures dédiées à vous deux. Pas d'écrans, pas d'enfants, pas d'invités. Choisissez à tour de rôle l'activité. C'est court, mais sacré.",
                "Troisième invitation — La conversation impossible : tous les trimestres, abordez ensemble un sujet que vous évitez. Avec lenteur, avec curiosité, sans chercher de solution immédiate. Les couples qui durent osent ces conversations."
            ])

    def _page_24_transits(self, c, n1, n2):
        self._page_miroir(c, 24, "IX · Le chemin", "Transits du mois",
            "Les énergies à venir pour votre couple",
            "« Les transits sont la météo de votre lien. »",
            [
                f"Ce mois-ci, certaines énergies planétaires invitent {n1} et {n2} à des mouvements précis. Les transits ne dictent pas votre relation — ils colorent les jours.",
                "Profitez des trigones lunaires pour les conversations sensibles. Honorez les carrés saturniens en clarifiant vos engagements. Quand Vénus avance dans votre thème commun, célébrez par un geste tendre — Vénus aime être remerciée.",
                "Notre conseil : consultez chaque dimanche soir l'éphéméride de la semaine à venir. Un couple qui anticipe les énergies traverse les vagues au lieu de les subir."
            ])

    def _page_25_benediction(self, c, n1, n2):
        self._bg_cream(c)
        # En-tete decoratif
        y = self.h - 3.5 * cm
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.6)
        c.line(self.w / 2 - 3 * cm, y, self.w / 2 + 3 * cm, y)
        y -= 0.8 * cm
        c.setFillColor(GOLD)
        c.setFont(_UNICODE_FONT, 9)
        c.drawCentredString(self.w / 2, y, "✦  BÉNÉDICTION DE LA PLUME  ✦")
        y -= 0.6 * cm
        c.line(self.w / 2 - 3 * cm, y, self.w / 2 + 3 * cm, y)
        y -= 1.5 * cm

        # Illustration centrale (page 25)
        y = self._illustration_slot(c, 25, y, h=6 * cm)
        y -= 0.5 * cm

        # Message
        msg = [
            f"À {n1} & {n2},",
            "",
            "Les étoiles n'ont jamais imposé un destin à un couple.",
            "Elles ont seulement chuchoté des possibilités.",
            "",
            "Votre lien est unique dans l'univers entier.",
            "Aucun autre couple, dans aucune autre vie, ne se compose exactement comme le vôtre.",
            "",
            "Ce rapport n'est pas une carte du futur.",
            "C'est un miroir tendu vers votre présent —",
            "pour que vous puissiez voir, choisir, et aimer en conscience.",
            "",
            "Que la curiosité demeure entre vous.",
            "Que la tendresse résiste aux saisons.",
            "Que vous sachiez vous quitter du regard pour mieux vous retrouver.",
        ]
        c.setFillColor(INK)
        c.setFont("Helvetica-Oblique", 11)
        for line in msg:
            if line:
                c.drawCentredString(self.w / 2, y, line)
            y -= 0.55 * cm

        y -= 1 * cm
        # Signature dorée
        c.setStrokeColor(GOLD)
        c.line(self.w / 2 - 2.5 * cm, y, self.w / 2 + 2.5 * cm, y)
        y -= 0.7 * cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-BoldOblique", 13)
        c.drawCentredString(self.w / 2, y, "Plume")
        y -= 0.5 * cm
        c.setFillColor(INK_SOFT)
        c.setFont("Helvetica", 8.5)
        c.drawCentredString(self.w / 2, y, "plume-astrale.fr")
        self._footer(c, 25)

    # ════════════════════════════════════════
    #  Version enrichie generique (utilise enriched_text si dispo)
    # ════════════════════════════════════════
    def _page_miroir_enriched(self, c, page_num, kicker, title, subtitle, intro_text,
                              fallback_paragraphs, enriched_text=None, illu_h=6 * cm):
        """Comme _page_miroir mais utilise enriched_text quand fourni (Option A user)."""
        self._bg_cream(c)
        y = self._interior_header(c, kicker, title, subtitle)
        y = self._illustration_slot(c, page_num, y, h=illu_h)
        x_left = self.margin + 0.5 * cm
        max_w = self.w - 2 * self.margin - 1 * cm
        # Intro citation
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Oblique", 10)
        for line in self._wrap(intro_text, "Helvetica-Oblique", 10, max_w - 1 * cm, c):
            c.drawCentredString(self.w / 2, y, line)
            y -= 0.5 * cm
        y -= 0.4 * cm
        # Body : si texte enrichi dispo, on l'utilise (split par double-newline en paragraphes)
        if enriched_text:
            paragraphs = [p.strip() for p in enriched_text.split('\n\n') if p.strip()]
        else:
            paragraphs = fallback_paragraphs
        for para in paragraphs:
            y = self._text_block(c, para, x_left, y, max_w, size=9.5, leading=1.5)
            y -= 0.15 * cm
            if y < 2.5 * cm:
                break  # protection debordement
        self._footer(c, page_num)


    # ════════════════════════════════════════
    #  Entry point
    # ════════════════════════════════════════
    def generate(self, p1, p2, enriched: dict = None):
        enriched = enriched or {}
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)

        s1 = _sign_from_date(p1.get('birth_date', ''))
        s2 = _sign_from_date(p2.get('birth_date', ''))
        n1 = (p1.get('prenom') or 'L\'un').strip().title()
        n2 = (p2.get('prenom') or 'L\'autre').strip().title()

        # Page 1 — Couverture
        self._page_01_cover(c, p1, p2, s1, s2)
        c.showPage()

        # Page 2 — Sommaire
        self._page_02_toc(c)
        c.showPage()

        # Page 3-4 — Thèmes personnels (enrichis si dispo)
        self._page_personal_theme(c, 3, p1, s1, enriched.get(3))
        c.showPage()
        self._page_personal_theme(c, 4, p2, s2, enriched.get(4))
        c.showPage()

        # Pages 5-10 — 7 lumières (5-9 enrichis)
        self._page_05_soleils(c, n1, n2, s1, s2, enriched.get(5)); c.showPage()
        self._page_06_lunes(c, n1, n2, enriched.get(6)); c.showPage()
        self._page_07_mercure(c, n1, n2, enriched.get(7)); c.showPage()
        self._page_08_venus(c, n1, n2, enriched.get(8)); c.showPage()
        self._page_09_mars(c, n1, n2, enriched.get(9)); c.showPage()
        self._page_10_jup_sat(c, n1, n2); c.showPage()

        # Pages 11-14 — Aspects (11-12 enrichis)
        self._page_11_aspects_harm(c, n1, n2, enriched.get(11)); c.showPage()
        self._page_12_aspects_tension(c, n1, n2, enriched.get(12)); c.showPage()
        self._page_13_conjonctions(c, n1, n2); c.showPage()
        self._page_14_maisons(c, n1, n2); c.showPage()

        # Pages 15-17 — Vie amoureuse
        self._page_15_langages(c, n1, n2); c.showPage()
        self._page_16_sensualite(c, n1, n2); c.showPage()
        self._page_17_communication(c, n1, n2); c.showPage()

        # Pages 18-21 — Bâtir ensemble
        self._page_18_vie_commune(c, n1, n2); c.showPage()
        self._page_19_enfants(c, n1, n2); c.showPage()
        self._page_20_argent(c, n1, n2); c.showPage()
        self._page_21_voyages(c, n1, n2); c.showPage()

        # Pages 22-25 — Le chemin (22 enrichi)
        self._page_22_forces(c, n1, n2, s1, s2, enriched.get(22)); c.showPage()
        self._page_23_invitations(c, n1, n2); c.showPage()
        self._page_24_transits(c, n1, n2); c.showPage()
        self._page_25_benediction(c, n1, n2)

        c.save()
        buf.seek(0)
        return buf.getvalue()

    # ════════════════════════════════════════
    #  EXTRAIT GRATUIT 3 pages (lead magnet)
    # ════════════════════════════════════════
    def generate_extract(self, p1, p2, enriched: dict = None):
        """Genere un mini-PDF de 3 pages :
        1. Couverture identique au rapport complet
        2. Soleils en miroir (enrichi avec vraies data astro si dispo)
        3. CTA "Le rapport complet 25 pages a 49€" + teaser de 3 forces
        """
        enriched = enriched or {}
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)

        s1 = _sign_from_date(p1.get('birth_date', ''))
        s2 = _sign_from_date(p2.get('birth_date', ''))
        n1 = (p1.get('prenom') or 'L\'un').strip().title()
        n2 = (p2.get('prenom') or 'L\'autre').strip().title()

        # Page 1 - Couverture (avec badge "Extrait gratuit")
        self._page_01_cover(c, p1, p2, s1, s2)
        # Badge "Extrait gratuit" superpose en bas
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.w / 2, 2.5 * cm, "✦  APERCU GRATUIT — 3 PAGES  ✦")
        c.showPage()

        # Page 2 - Soleils en miroir (enrichi)
        self._page_05_soleils(c, n1, n2, s1, s2, enriched.get(5))
        c.showPage()

        # Page 3 - CTA + teaser
        self._page_extract_cta(c, n1, n2)
        c.save()
        buf.seek(0)
        return buf.getvalue()

    def _page_extract_cta(self, c, n1, n2):
        """Page finale de l'extrait : CTA vers le rapport complet."""
        self._bg_cream(c)
        y = self._interior_header(c, "L'aperçu s'arrête ici", "Le rapport complet",
                                   "vous attend en 22 pages supplémentaires")

        x_left = self.margin + 0.5 * cm
        max_w = self.w - 2 * self.margin - 1 * cm

        intro = (
            f"Ce que vous venez de lire n'est qu'une porte entrouverte sur l'univers "
            f"astrologique que composent {n1} et {n2}. Le rapport complet vous emmène "
            f"beaucoup plus loin, dans les zones les plus intimes de votre lien."
        )
        y = self._text_block(c, intro, x_left, y, max_w, size=10.5, leading=1.65)
        y -= 0.5 * cm

        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_left, y, "DANS LE RAPPORT COMPLET, VOUS DÉCOUVRIREZ :")
        y -= 0.8 * cm

        bullets = [
            ("Vos 7 lumières en miroir", "Soleils, Lunes, Mercure, Vénus, Mars, Jupiter, Saturne"),
            ("Vos aspects majeurs", "Trigones, carrés, oppositions — avec orbes précis"),
            ("Vos maisons croisées", "Où l'autre éclaire votre vie (foyer, travail, spiritualité)"),
            ("Vos langages d'amour", "Sensualité, communication, sexualité"),
            ("Bâtir ensemble", "Vie commune, enfants, argent, voyages"),
            ("Le chemin à deux", "Vos forces, 3 invitations, transits du mois"),
            ("Bénédiction personnalisée", "Un message final, unique à votre couple"),
        ]
        for title, desc in bullets:
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x_left, y, f"✦  {title}")
            y -= 0.45 * cm
            c.setFillColor(INK_SOFT)
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(x_left + 0.5 * cm, y, desc)
            y -= 0.55 * cm

        # Bandeau prix + CTA
        y -= 0.5 * cm
        c.setFillColor(DEEP_PURPLE)
        c.roundRect(x_left, y - 3 * cm, max_w, 3 * cm, 8, fill=1, stroke=0)
        # Titre
        c.setFillColor(GOLD_LIGHT)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(self.w / 2, y - 1 * cm, "49€")
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(self.w / 2, y - 1.6 * cm, "paiement unique — 25 pages personnalisées à vos deux thèmes")
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(self.w / 2, y - 2.4 * cm, "plume-astrale.fr/synastrie")

        # Footer
        c.setFillColor(INK_SOFT)
        c.setFont("Helvetica-Oblique", 8.5)
        c.drawCentredString(self.w / 2, 1.5 * cm, "Merci d'avoir laissé Plume vous accompagner ce jour.")
        self._footer(c, 3, total=3)


def generate_synastrie_extract(person1: dict, person2: dict, enriched: dict = None) -> bytes:
    """Point d'entrée pour l'extrait gratuit 3 pages (lead magnet)."""
    return SynastriePDFGenerator().generate_extract(person1, person2, enriched=enriched)


def generate_synastrie_pdf(person1: dict, person2: dict, enriched: dict = None) -> bytes:
    """Point d'entrée pour le webhook synastrie.
    person1/person2 : {prenom, birth_date (YYYY-MM-DD), birth_time, birth_place, latitude, longitude, gender}
    enriched : optional dict {page_number: text} pour surcharger les paragraphes des pages 3-9, 11-12, 22.
    """
    return SynastriePDFGenerator().generate(person1, person2, enriched=enriched)
