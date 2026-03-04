"""
Générateur PDF de Compatibilité Astrale - Plume Astrale
Rapport riche et personnalisé pour un couple
"""
import io
import random
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

# ═══════════════════ COULEURS ═══════════════════
DEEP_PURPLE = HexColor('#0C0918')
MEDIUM_PURPLE = HexColor('#1E1A33')
GOLD = HexColor('#C5A059')
CREAM = HexColor('#F0E6D3')
LIGHT_TEXT = HexColor('#B8B0C8')
ROSE = HexColor('#E8A0BF')
SOFT_RED = HexColor('#FF9999')

# ═══════════════════ DONNÉES ASTROLOGIQUES ═══════════════════

SIGNES = {
    "Bélier": {"element": "Feu", "modalite": "Cardinal", "planete": "Mars", "qualites": ["courageux", "dynamique", "passionné", "direct"], "ombre": ["impatient", "impulsif", "dominant"]},
    "Taureau": {"element": "Terre", "modalite": "Fixe", "planete": "Vénus", "qualites": ["fidèle", "sensuel", "stable", "patient"], "ombre": ["possessif", "têtu", "résistant au changement"]},
    "Gémeaux": {"element": "Air", "modalite": "Mutable", "planete": "Mercure", "qualites": ["communicatif", "curieux", "adaptable", "spirituel"], "ombre": ["superficiel", "inconstant", "nerveux"]},
    "Cancer": {"element": "Eau", "modalite": "Cardinal", "planete": "Lune", "qualites": ["protecteur", "intuitif", "émotionnel", "nourrissant"], "ombre": ["susceptible", "possessif", "lunatique"]},
    "Lion": {"element": "Feu", "modalite": "Fixe", "planete": "Soleil", "qualites": ["généreux", "charismatique", "loyal", "créatif"], "ombre": ["orgueilleux", "autoritaire", "centré sur lui-même"]},
    "Vierge": {"element": "Terre", "modalite": "Mutable", "planete": "Mercure", "qualites": ["attentionné", "analytique", "dévoué", "fiable"], "ombre": ["critique", "anxieux", "perfectionniste"]},
    "Balance": {"element": "Air", "modalite": "Cardinal", "planete": "Vénus", "qualites": ["diplomate", "harmonieux", "esthète", "juste"], "ombre": ["indécis", "dépendant", "évite les conflits"]},
    "Scorpion": {"element": "Eau", "modalite": "Fixe", "planete": "Pluton", "qualites": ["intense", "passionné", "loyal", "perspicace"], "ombre": ["jaloux", "rancunier", "manipulateur"]},
    "Sagittaire": {"element": "Feu", "modalite": "Mutable", "planete": "Jupiter", "qualites": ["optimiste", "aventurier", "philosophe", "honnête"], "ombre": ["excessif", "impatient", "moralisateur"]},
    "Capricorne": {"element": "Terre", "modalite": "Cardinal", "planete": "Saturne", "qualites": ["ambitieux", "responsable", "persévérant", "structuré"], "ombre": ["rigide", "froid", "pessimiste"]},
    "Verseau": {"element": "Air", "modalite": "Fixe", "planete": "Uranus", "qualites": ["original", "humaniste", "indépendant", "visionnaire"], "ombre": ["détaché", "imprévisible", "rebelle"]},
    "Poissons": {"element": "Eau", "modalite": "Mutable", "planete": "Neptune", "qualites": ["empathique", "intuitif", "créatif", "spirituel"], "ombre": ["fuyant", "idéaliste", "vulnérable"]},
}

ELEMENT_COMPAT = {
    ("Feu", "Feu"): {
        "score": 85, "titre": "Union de Flammes",
        "force": "Votre relation est un brasier de passion, d'énergie et d'enthousiasme. Vous vous stimulez mutuellement et partagez un goût pour l'action, l'aventure et la spontanéité. Ensemble, vous êtes capables de grandes réalisations car vous ne manquez jamais de motivation.",
        "defi": "Le risque est la surchauffe : deux feux peuvent se consumer rapidement. Les ego peuvent s'affronter violemment. Apprenez à céder à tour de rôle et à canaliser votre énergie vers des projets communs plutôt que vers des confrontations.",
        "conseil": "Planifiez des activités physiques ou créatives ensemble pour canaliser votre énergie. Instaurez des moments de calme et de douceur pour éviter l'épuisement émotionnel."
    },
    ("Feu", "Terre"): {
        "score": 60, "titre": "La Flamme et le Roc",
        "force": "Le Feu apporte l'enthousiasme, la vision et l'audace. La Terre offre la stabilité, le réalisme et la constance. Ensemble, vous pouvez transformer les rêves en réalité. La Terre ancre le Feu, tandis que le Feu réchauffe et inspire la Terre.",
        "defi": "Le Feu peut trouver la Terre trop lente et ennuyeuse. La Terre peut juger le Feu imprudent et irresponsable. Ces différences de rythme peuvent créer de la frustration si elles ne sont pas reconnues et respectées.",
        "conseil": "Valorisez vos différences comme complémentaires. Le partenaire Feu doit apprendre la patience, le partenaire Terre doit oser sortir de sa zone de confort. Trouvez des compromis sur le rythme de vie."
    },
    ("Feu", "Air"): {
        "score": 90, "titre": "Le Souffle qui Attise la Flamme",
        "force": "C'est une des combinaisons les plus stimulantes. L'Air nourrit le Feu, le Feu illumine l'Air. Ensemble, vous créez une dynamique intellectuelle et passionnée remarquable. Communication vive, idées brillantes, projets ambitieux : vous vous amplifiez mutuellement.",
        "defi": "Le manque d'ancrage peut être un problème. Vous pouvez vous perdre dans les projets et les discussions sans jamais concrétiser. Le Feu peut être trop intense pour l'Air qui a besoin de recul.",
        "conseil": "Donnez-vous des objectifs concrets et des échéances. L'Air doit accepter l'intensité émotionnelle du Feu, le Feu doit respecter le besoin d'espace intellectuel de l'Air."
    },
    ("Feu", "Eau"): {
        "score": 50, "titre": "Vapeur et Transformation",
        "force": "Cette union est celle de la passion brute. Le Feu apporte l'action et le courage, l'Eau apporte la profondeur émotionnelle et l'intuition. Quand ces deux forces s'harmonisent, elles créent une alchimie puissante de transformation personnelle et de connexion profonde.",
        "defi": "L'Eau peut éteindre le Feu par sa sensibilité excessive, et le Feu peut faire bouillir l'Eau par son impatience. Les incompréhensions émotionnelles sont fréquentes : le Feu agit, l'Eau ressent, et ces deux langages se heurtent facilement.",
        "conseil": "Apprenez le langage émotionnel de l'autre. Le partenaire Feu doit développer son écoute et sa patience. Le partenaire Eau doit exprimer clairement ses besoins au lieu de les garder en lui."
    },
    ("Terre", "Terre"): {
        "score": 80, "titre": "Fondations Solides",
        "force": "Vous construisez ensemble sur des bases inébranlables. Fidélité, fiabilité, sens pratique et engagement : votre relation est un pilier de stabilité. Vous partagez les mêmes valeurs de sécurité et de confort matériel.",
        "defi": "Le risque est l'immobilisme et la routine. Deux Terre peuvent devenir trop prévisibles, manquer de spontanéité et résister ensemble au changement, même quand il est nécessaire.",
        "conseil": "Introduisez régulièrement de la nouveauté dans votre quotidien. Voyagez, explorez de nouvelles activités, surprenez-vous mutuellement pour éviter que la routine ne s'installe."
    },
    ("Terre", "Air"): {
        "score": 55, "titre": "Le Vent sur la Montagne",
        "force": "L'Air apporte la légèreté, les idées et la communication. La Terre offre la structure et l'ancrage. Quand ils collaborent, l'Air conceptualise et la Terre réalise. Cette complémentarité peut être extrêmement productive.",
        "defi": "L'Air peut trouver la Terre rigide et ennuyeuse. La Terre peut juger l'Air instable et peu fiable. Leurs besoins fondamentaux sont très différents : la Terre cherche la sécurité, l'Air cherche la liberté.",
        "conseil": "Respectez les besoins fondamentaux de chacun. La Terre doit accorder de l'espace à l'Air, l'Air doit montrer à la Terre qu'il est digne de confiance par des actes concrets."
    },
    ("Terre", "Eau"): {
        "score": 85, "titre": "Le Jardin Fertile",
        "force": "L'Eau nourrit la Terre, la Terre contient l'Eau. C'est une union naturellement harmonieuse. Vous créez ensemble un foyer chaleureux et sécurisant. La sensibilité de l'Eau trouve un ancrage dans la solidité de la Terre, et la Terre s'adoucit au contact de l'Eau.",
        "defi": "L'excès de confort peut mener à l'isolement du monde extérieur. La Terre peut manquer de sensibilité aux yeux de l'Eau, et l'Eau peut sembler trop émotionnelle pour la Terre pragmatique.",
        "conseil": "Ouvrez-vous aux autres et au monde extérieur. La Terre doit apprendre à exprimer ses émotions, l'Eau doit accepter que la Terre exprime son amour par des actes plutôt que par des mots."
    },
    ("Air", "Air"): {
        "score": 75, "titre": "Dialogue des Esprits",
        "force": "Communication brillante, stimulation intellectuelle permanente, ouverture d'esprit et curiosité partagée. Vous ne vous ennuyez jamais ensemble. Votre relation est un échange constant d'idées, de découvertes et de projets.",
        "defi": "Le manque d'ancrage émotionnel est le principal défi. Vous pouvez intellectualiser vos sentiments au lieu de les vivre. La superficialité menace si vous restez dans le mental sans plonger dans le cœur.",
        "conseil": "Cultivez l'intimité émotionnelle. Parlez de vos sentiments, pas seulement de vos idées. Créez des rituels de connexion émotionnelle réguliers."
    },
    ("Air", "Eau"): {
        "score": 50, "titre": "Brume et Révélation",
        "force": "L'Air peut aider l'Eau à mettre des mots sur ses émotions. L'Eau peut enseigner à l'Air la profondeur des sentiments. Quand ils se comprennent, c'est une relation d'une richesse extraordinaire, mêlant intelligence et sensibilité.",
        "defi": "L'Air rationalise ce que l'Eau ressent, ce qui peut blesser profondément le partenaire Eau. L'Eau peut submerger l'Air de ses émotions, le faisant fuir. Ces deux mondes — mental et émotionnel — semblent parfois inconciliables.",
        "conseil": "Soyez patient et apprenez à traduire entre vos deux langages. L'Air doit valider les émotions de l'Eau sans chercher à les résoudre logiquement. L'Eau doit accepter que l'Air exprime son amour différemment."
    },
    ("Eau", "Eau"): {
        "score": 80, "titre": "Océan de Sensibilité",
        "force": "Connexion émotionnelle profonde et intuitive. Vous vous comprenez sans mots. L'empathie, la tendresse et l'intimité sont au cœur de votre relation. Vous créez ensemble un cocon émotionnel d'une profondeur rare.",
        "defi": "L'excès d'émotion peut devenir étouffant. Sans ancrage terre-à-terre, vous pouvez vous noyer dans vos sentiments. La dépendance émotionnelle et la difficulté à poser des limites sont des risques réels.",
        "conseil": "Gardez chacun des activités individuelles et un cercle social propre. Développez ensemble des habitudes pratiques et structurantes pour équilibrer votre grande sensibilité."
    },
}

MODALITE_COMPAT = {
    ("Cardinal", "Cardinal"): {
        "dynamique": "Deux leaders dans le couple — c'est une force immense pour initier des projets, mais cela peut créer des luttes de pouvoir. L'un doit parfois accepter de suivre.",
        "conseil": "Alternez les rôles de leader selon les domaines (finances, loisirs, famille). Respectez les initiatives de l'autre."
    },
    ("Cardinal", "Fixe"): {
        "dynamique": "Le Cardinal initie, le Fixe maintient. C'est une complémentarité naturelle qui permet de démarrer et de tenir dans la durée. Le Cardinal apporte le mouvement, le Fixe la persévérance.",
        "conseil": "Le Cardinal doit respecter le besoin de stabilité du Fixe. Le Fixe doit accepter que le changement est parfois nécessaire."
    },
    ("Cardinal", "Mutable"): {
        "dynamique": "Le Cardinal dirige, le Mutable s'adapte. Cette combinaison est fluide et souvent harmonieuse. Le Mutable soutient les initiatives du Cardinal avec flexibilité.",
        "conseil": "Le Cardinal doit veiller à ne pas dominer. Le Mutable doit affirmer ses propres besoins et ne pas toujours céder."
    },
    ("Fixe", "Fixe"): {
        "dynamique": "Deux personnalités déterminées et tenaces. Quand vous êtes d'accord, rien ne peut vous arrêter. Mais quand vous divergez, c'est un bras de fer sans fin.",
        "conseil": "Apprenez l'art du compromis. Choisissez vos batailles. Certains sujets méritent la négociation, pas l'entêtement."
    },
    ("Fixe", "Mutable"): {
        "dynamique": "Le Fixe apporte la structure et la constance, le Mutable apporte la souplesse et l'adaptabilité. Ensemble, vous êtes à la fois stables et flexibles.",
        "conseil": "Le Fixe doit apprécier la flexibilité du Mutable au lieu de la voir comme de l'inconstance. Le Mutable peut s'inspirer de la détermination du Fixe."
    },
    ("Mutable", "Mutable"): {
        "dynamique": "Grande adaptabilité et ouverture au changement. Vous êtes flexibles et tolérants l'un envers l'autre. Le risque est le manque de direction commune.",
        "conseil": "Définissez ensemble des objectifs clairs et des projets structurants. Votre flexibilité est une force si elle est canalisée."
    },
}

CHEMIN_VIE_COMPAT = {
    (1, 1): "Deux individualistes qui doivent apprendre à faire équipe. Respectez l'indépendance de chacun.",
    (1, 2): "Complémentarité naturelle : le 1 mène, le 2 harmonise. Équilibre entre action et diplomatie.",
    (1, 3): "Duo créatif et dynamique. Communication vivante et projets enthousiasmants.",
    (1, 4): "Le 1 innove, le 4 structure. Ensemble, vous bâtissez du concret à partir d'idées audacieuses.",
    (1, 5): "Aventure et liberté ! Relation passionnante mais qui doit trouver un ancrage.",
    (1, 6): "Le 1 apporte l'ambition, le 6 l'amour du foyer. Bel équilibre entre carrière et famille.",
    (1, 7): "Union intellectuelle profonde. Le 1 agit, le 7 réfléchit. Respectez vos rythmes différents.",
    (1, 8): "Duo de pouvoir et d'ambition. Impressionnant ensemble, mais attention aux luttes d'ego.",
    (1, 9): "Le 1 est focalisé, le 9 est universel. Vous vous élargissez mutuellement les horizons.",
    (2, 2): "Harmonie douce et profonde. Sensibilité partagée et soutien mutuel constant.",
    (2, 3): "Le 2 est discret, le 3 expressif. Ensemble, vous trouvez un bel équilibre entre intériorité et communication.",
    (2, 4): "Relation stable et sécurisante. Le 2 apporte la douceur, le 4 la structure.",
    (2, 5): "Le 2 cherche la stabilité, le 5 l'aventure. Un défi qui enrichit si chacun fait un pas vers l'autre.",
    (2, 6): "Excellente compatibilité ! L'amour, la famille et l'harmonie sont au cœur de votre union.",
    (2, 7): "Connexion intuitive et spirituelle profonde. Besoin mutuel de calme et de profondeur.",
    (2, 8): "Le 2 soutient, le 8 réalise. Partenariat efficace si le 8 reconnaît la valeur du 2.",
    (2, 9): "Deux âmes sensibles et tournées vers les autres. Relation généreuse et empathique.",
    (3, 3): "Créativité débordante et joie de vivre ! Attention à ne pas fuir les responsabilités ensemble.",
    (3, 4): "Le 3 apporte la légèreté, le 4 la discipline. Complémentaires si vous respectez vos différences.",
    (3, 5): "Duo d'aventuriers sociaux. Vie excitante mais qui doit trouver un centre stable.",
    (3, 6): "Le 3 crée, le 6 nourrit. Bel équilibre entre expression personnelle et vie familiale.",
    (3, 7): "Le 3 est extraverti, le 7 introverti. Apprenez à apprécier vos mondes différents.",
    (3, 8): "Le 3 inspire, le 8 concrétise. Ensemble, vous pouvez créer des projets remarquables.",
    (3, 9): "Deux créatifs avec une vision large du monde. Relation stimulante et inspirante.",
    (4, 4): "Solidité à toute épreuve. Vous bâtissez ensemble des fondations durables.",
    (4, 5): "Le 4 veut la stabilité, le 5 la liberté. Un vrai défi qui demande des compromis constants.",
    (4, 6): "Excellente base pour un foyer stable et aimant. Responsabilité et tendresse partagées.",
    (4, 7): "Le 4 est pratique, le 7 philosophe. Relation profonde qui allie matière et esprit.",
    (4, 8): "Duo bâtisseur par excellence. Ensemble, vous réalisez des projets ambitieux et durables.",
    (4, 9): "Le 4 construit, le 9 élargit les horizons. Relation qui grandit avec le temps.",
    (5, 5): "Liberté totale ! Relation passionnante mais qui peut manquer de fondations solides.",
    (5, 6): "Le 5 cherche l'aventure, le 6 le foyer. Un défi majeur qui demande beaucoup d'amour.",
    (5, 7): "Deux esprits indépendants. Relation respectueuse de la liberté de chacun.",
    (5, 8): "Énergie et ambition ! Vie intense et productive si vous alignez vos objectifs.",
    (5, 9): "Deux voyageurs de l'âme. Relation libre, ouverte et enrichissante.",
    (6, 6): "Amour du foyer, de la famille et de la beauté. Union douce et protectrice.",
    (6, 7): "Le 6 est terrestre, le 7 céleste. Apprenez à naviguer entre ces deux mondes.",
    (6, 8): "Le 6 nourrit, le 8 réalise. Relation prospère et stable.",
    (6, 9): "Deux cœurs généreux tournés vers les autres. Relation altruiste et aimante.",
    (7, 7): "Connexion spirituelle et intellectuelle rare. Profondeur et mystère partagés.",
    (7, 8): "Le 7 cherche le sens, le 8 le pouvoir. Relation complexe mais transformatrice.",
    (7, 9): "Union spirituelle et philosophique profonde. Vous cherchez ensemble le sens de la vie.",
    (8, 8): "Pouvoir et ambition au carré. Impressionnant si vous êtes alliés, destructeur si vous êtes rivaux.",
    (8, 9): "Le 8 réalise, le 9 élève. Ensemble, vous pouvez avoir un impact majeur sur le monde.",
    (9, 9): "Deux âmes universelles. Relation profondément spirituelle et tournée vers le service.",
}


def _get_zodiac(day, month):
    """Retourne le signe du zodiaque français."""
    dates = [
        (1, 20, "Capricorne"), (2, 19, "Verseau"), (3, 20, "Poissons"),
        (4, 20, "Bélier"), (5, 21, "Taureau"), (6, 21, "Gémeaux"),
        (7, 22, "Cancer"), (8, 23, "Lion"), (9, 23, "Vierge"),
        (10, 23, "Balance"), (11, 22, "Scorpion"), (12, 22, "Sagittaire"),
    ]
    for end_month, end_day, sign in dates:
        if (month == end_month and day <= end_day) or (month == end_month - 1 and day > (dates[dates.index((end_month, end_day, sign)) - 1][1] if dates.index((end_month, end_day, sign)) > 0 else 19)):
            pass
    # Simpler approach
    if (month == 3 and day >= 21) or (month == 4 and day <= 19): return "Bélier"
    if (month == 4 and day >= 20) or (month == 5 and day <= 20): return "Taureau"
    if (month == 5 and day >= 21) or (month == 6 and day <= 20): return "Gémeaux"
    if (month == 6 and day >= 21) or (month == 7 and day <= 22): return "Cancer"
    if (month == 7 and day >= 23) or (month == 8 and day <= 22): return "Lion"
    if (month == 8 and day >= 23) or (month == 9 and day <= 22): return "Vierge"
    if (month == 9 and day >= 23) or (month == 10 and day <= 22): return "Balance"
    if (month == 10 and day >= 23) or (month == 11 and day <= 21): return "Scorpion"
    if (month == 11 and day >= 22) or (month == 12 and day <= 21): return "Sagittaire"
    if (month == 12 and day >= 22) or (month == 1 and day <= 19): return "Capricorne"
    if (month == 1 and day >= 20) or (month == 2 and day <= 18): return "Verseau"
    return "Poissons"


def _calc_life_path(day, month, year):
    t = day + month + year
    while t > 9 and t not in (11, 22, 33):
        t = sum(int(x) for x in str(t))
    return t


def _get_element_compat(e1, e2):
    key = (e1, e2) if (e1, e2) in ELEMENT_COMPAT else (e2, e1)
    return ELEMENT_COMPAT.get(key, ELEMENT_COMPAT[("Feu", "Feu")])


def _get_modalite_compat(m1, m2):
    key = (m1, m2) if (m1, m2) in MODALITE_COMPAT else (m2, m1)
    return MODALITE_COMPAT.get(key, MODALITE_COMPAT[("Cardinal", "Cardinal")])


def _get_chemin_compat(c1, c2):
    c1 = min(c1, 9)
    c2 = min(c2, 9)
    key = (min(c1, c2), max(c1, c2))
    return CHEMIN_VIE_COMPAT.get(key, "Votre combinaison numérologique unique invite à la découverte mutuelle et au respect des différences.")


class CompatibilityPDFGenerator:
    def __init__(self):
        self.width, self.height = A4
        self.margin = 2.5 * cm

    def _draw_bg(self, c):
        c.setFillColor(DEEP_PURPLE)
        c.rect(0, 0, self.width, self.height, fill=1)

    def _new_page(self, c):
        c.showPage()
        self._draw_bg(c)

    def _draw_text_block(self, c, text, y, font_size=10.5, color=LIGHT_TEXT, leading=1.5, max_width=None):
        """Dessine un bloc de texte avec retour à la ligne automatique."""
        if not text:
            return y
        if max_width is None:
            max_width = self.width - 2 * self.margin
        c.setFillColor(color)
        c.setFont("Helvetica", font_size)
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test = f"{current_line} {word}".strip()
            if c.stringWidth(test, "Helvetica", font_size) <= max_width:
                current_line = test
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        line_height = font_size * leading / 28.35 * cm
        for line in lines:
            if y < 2.5 * cm:
                self._new_page(c)
                y = self.height - 3.5 * cm
            c.drawCentredString(self.width / 2, y, line)
            y -= line_height
        y -= line_height * 0.3
        return y

    def _draw_left_block(self, c, text, y, x_start=None, font_size=10, color=LIGHT_TEXT, max_width=None):
        """Dessine un bloc aligné à gauche."""
        if not text:
            return y
        if x_start is None:
            x_start = self.margin + 0.5 * cm
        if max_width is None:
            max_width = self.width - 2 * self.margin - 1 * cm
        c.setFillColor(color)
        c.setFont("Helvetica", font_size)
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test = f"{current_line} {word}".strip()
            if c.stringWidth(test, "Helvetica", font_size) <= max_width:
                current_line = test
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        lh = font_size * 1.45 / 28.35 * cm
        for line in lines:
            if y < 2.5 * cm:
                self._new_page(c)
                y = self.height - 3.5 * cm
            c.drawString(x_start, y, line)
            y -= lh
        y -= lh * 0.2
        return y

    def _chapter_header(self, c, title, subtitle=""):
        y = self.height - 4 * cm
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.5)
        c.line(3 * cm, y + 1.2 * cm, self.width - 3 * cm, y + 1.2 * cm)
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(self.width / 2, y, title)
        y -= 0.8 * cm
        if subtitle:
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Oblique", 11)
            c.drawCentredString(self.width / 2, y, subtitle)
            y -= 1.2 * cm
        else:
            y -= 0.5 * cm
        return y

    def _sub_header(self, c, title, y, size=14, color=GOLD):
        if y < 4 * cm:
            self._new_page(c)
            y = self.height - 3.5 * cm
        y -= 0.3 * cm
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", size)
        c.drawCentredString(self.width / 2, y, title)
        y -= 0.8 * cm
        return y

    def _score_bar(self, c, score, y, label=""):
        """Dessine une barre de score visuelle."""
        if y < 4 * cm:
            self._new_page(c)
            y = self.height - 3.5 * cm
        bar_w = 10 * cm
        bar_h = 0.6 * cm
        x_start = (self.width - bar_w) / 2

        # Background bar
        c.setFillColor(MEDIUM_PURPLE)
        c.roundRect(x_start, y - bar_h, bar_w, bar_h, 5, fill=1)

        # Fill bar
        fill_w = bar_w * (score / 100)
        if score >= 70:
            fill_color = HexColor('#4CAF50')
        elif score >= 50:
            fill_color = GOLD
        else:
            fill_color = HexColor('#FF6B6B')
        c.setFillColor(fill_color)
        c.roundRect(x_start, y - bar_h, fill_w, bar_h, 5, fill=1)

        # Score text
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(self.width / 2, y - bar_h + 0.15 * cm, f"{score}%")

        y -= bar_h + 0.5 * cm
        if label:
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica-Oblique", 9)
            c.drawCentredString(self.width / 2, y, label)
            y -= 0.5 * cm
        return y

    def _footer(self, c, page_num):
        c.setFillColor(HexColor('#C5A059'))
        c.setFillAlpha(0.4)
        c.setFont("Helvetica", 8)
        c.drawCentredString(self.width / 2, 1.2 * cm, f"Compatibilité Astrale — Plume Astrale — page {page_num}")
        c.setFillAlpha(1.0)

    # ═══════════════════ PAGES ═══════════════════

    def _page_cover(self, c, p1, p2, s1, s2):
        self._draw_bg(c)
        y = self.height - 6 * cm

        # Decorative line
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        c.line(4 * cm, y + 2 * cm, self.width - 4 * cm, y + 2 * cm)

        c.setFillColor(GOLD)
        c.setFont("Helvetica", 11)
        c.drawCentredString(self.width / 2, y + 1 * cm, "PLUME ASTRALE")

        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 30)
        c.drawCentredString(self.width / 2, y, "Compatibilité Astrale")
        y -= 2 * cm

        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(self.width / 2, y, f"{p1['first_name'].upper()} & {p2['first_name'].upper()}")
        y -= 1.2 * cm

        e1 = SIGNES.get(s1, {}).get('element', '?')
        e2 = SIGNES.get(s2, {}).get('element', '?')
        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica", 14)
        c.drawCentredString(self.width / 2, y, f"{s1} ({e1}) x {s2} ({e2})")
        y -= 2 * cm

        c.setStrokeColor(GOLD)
        c.setLineWidth(0.5)
        c.line(5 * cm, y, self.width - 5 * cm, y)
        y -= 1 * cm

        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(self.width / 2, y, f"Rapport généré le {datetime.now().strftime('%d/%m/%Y')}")
        y -= 0.6 * cm
        c.drawCentredString(self.width / 2, y, "Document strictement personnel et confidentiel")

    def _page_profiles(self, c, p1, p2, s1, s2, lp1, lp2):
        self._new_page(c)
        y = self._chapter_header(c, "Vos Profils Astrologiques", "Deux univers, une rencontre")

        for person, signe, lp, label in [(p1, s1, lp1, "Partenaire 1"), (p2, s2, lp2, "Partenaire 2")]:
            info = SIGNES.get(signe, {})
            prenom = person['first_name']

            # Name box
            c.setFillColor(MEDIUM_PURPLE)
            c.setFillAlpha(0.7)
            c.roundRect(self.margin, y - 0.8 * cm, self.width - 2 * self.margin, 0.9 * cm, 8, fill=1)
            c.setFillAlpha(1.0)
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 13)
            c.drawCentredString(self.width / 2, y - 0.55 * cm, f"{prenom} — {signe}")
            y -= 1.5 * cm

            details = [
                f"Signe : {signe} | Élément : {info.get('element', '?')} | Modalité : {info.get('modalite', '?')}",
                f"Planète : {info.get('planete', '?')} | Chemin de vie : {lp}",
                f"Qualités : {', '.join(info.get('qualites', []))}",
                f"Points de vigilance : {', '.join(info.get('ombre', []))}",
            ]
            for d in details:
                c.setFillColor(LIGHT_TEXT)
                c.setFont("Helvetica", 9.5)
                c.drawCentredString(self.width / 2, y, d)
                y -= 0.45 * cm
            y -= 0.8 * cm

        # Compatibility summary box
        e1 = SIGNES.get(s1, {}).get('element', '?')
        e2 = SIGNES.get(s2, {}).get('element', '?')
        m1 = SIGNES.get(s1, {}).get('modalite', '?')
        m2 = SIGNES.get(s2, {}).get('modalite', '?')
        ec = _get_element_compat(e1, e2)

        y = self._sub_header(c, "Résumé de Compatibilité", y, size=14)
        summary_items = [
            f"Harmonie des éléments : {e1} x {e2} — Score : {ec['score']}%",
            f"Dynamique des modalités : {m1} x {m2}",
            f"Chemins de vie : {lp1} & {lp2}",
        ]
        for item in summary_items:
            c.setFillColor(CREAM)
            c.setFont("Helvetica", 10)
            c.drawCentredString(self.width / 2, y, item)
            y -= 0.5 * cm

        return y

    def _page_partner_detail(self, c, person, signe, lp, partner_num):
        """Page détaillée d'un partenaire."""
        self._new_page(c)
        info = SIGNES.get(signe, {})
        prenom = person['first_name']

        y = self._chapter_header(c, f"Portrait de {prenom}", f"Partenaire {partner_num} — {signe}")

        # Sign personality
        y = self._sub_header(c, f"{prenom}, natif(ve) du {signe}", y, size=13)

        element = info.get('element', 'Feu')
        planete = info.get('planete', 'Mars')
        modalite = info.get('modalite', 'Cardinal')

        intro = f"{prenom} est né(e) sous le signe du {signe}, gouverné par {planete}. C'est un signe de {element}, de modalité {modalite}. "

        if element == "Feu":
            intro += f"Le Feu qui anime {prenom} se manifeste par une énergie ardente, un besoin d'action et une passion qui colore toutes ses relations. En amour, {prenom} est un partenaire entier, passionné et généreux."
        elif element == "Terre":
            intro += f"La Terre qui enracine {prenom} se traduit par un besoin de sécurité, de stabilité et de confort sensoriel. En amour, {prenom} est un partenaire fidèle, patient et profondément dévoué."
        elif element == "Air":
            intro += f"L'Air qui porte {prenom} se manifeste par une intelligence vive, un besoin de communication et une curiosité insatiable. En amour, {prenom} est un partenaire stimulant, ouvert et sociable."
        else:
            intro += f"L'Eau qui habite {prenom} se traduit par une sensibilité profonde, une intuition remarquable et un besoin de connexion émotionnelle. En amour, {prenom} est un partenaire attentionné, empathique et protecteur."

        y = self._draw_text_block(c, intro, y, font_size=10.5, color=CREAM)

        # Qualities
        y = self._sub_header(c, "Forces en Amour", y, size=12)
        for q in info.get('qualites', []):
            qual_desc = {
                "courageux": f"{prenom} n'a pas peur de prendre des risques pour ceux qu'il/elle aime. Cette bravoure est un pilier de la relation.",
                "fidèle": f"La loyauté de {prenom} est inébranlable. C'est un partenaire sur qui on peut compter en toutes circonstances.",
                "communicatif": f"{prenom} exprime naturellement ses pensées et ses sentiments, créant un espace de dialogue ouvert.",
                "protecteur": f"{prenom} veille sur son partenaire avec une tendresse instinctive et un dévouement profond.",
                "généreux": f"La générosité de {prenom} se manifeste dans les gestes quotidiens autant que dans les grands moments.",
                "attentionné": f"{prenom} remarque les détails et les besoins non exprimés de son partenaire.",
                "diplomate": f"{prenom} cherche naturellement l'harmonie et sait désamorcer les tensions avec grâce.",
                "intense": f"L'intensité de {prenom} crée une connexion profonde et transformatrice dans la relation.",
                "optimiste": f"{prenom} apporte de la lumière et de l'espoir même dans les moments difficiles.",
                "ambitieux": f"{prenom} porte le couple vers le haut grâce à sa détermination et sa vision à long terme.",
                "original": f"{prenom} apporte une fraîcheur et une créativité uniques qui renouvellent la relation.",
                "empathique": f"{prenom} ressent intuitivement les émotions de son partenaire, créant une compréhension sans mots.",
            }
            desc = qual_desc.get(q, f"{prenom} possède la qualité de {q}, un atout précieux dans la relation.")
            y = self._draw_text_block(c, f"• {q.capitalize()} : {desc}", y, font_size=9.5, color=LIGHT_TEXT)

        # Shadow aspects
        y = self._sub_header(c, "Points de Vigilance", y, size=12, color=ROSE)
        for o in info.get('ombre', []):
            y = self._draw_text_block(c, f"• {o.capitalize()}", y, font_size=9.5, color=SOFT_RED)

        # Life path
        y = self._sub_header(c, f"Chemin de Vie {lp}", y, size=12)
        chemin_desc = {
            1: "Leader et innovateur. En couple, doit apprendre le compromis.",
            2: "Diplomate et sensible. Nourrit naturellement la relation.",
            3: "Créatif et expressif. Apporte joie et communication au couple.",
            4: "Bâtisseur et fiable. Construit des fondations solides pour la relation.",
            5: "Aventurier et libre. Apporte l'excitation et le renouvellement.",
            6: "Protecteur du foyer. L'amour et la famille sont sa priorité.",
            7: "Philosophe et intuitif. Apporte profondeur et spiritualité à la relation.",
            8: "Ambitieux et puissant. Porte le couple vers la réussite matérielle.",
            9: "Humaniste et généreux. Élève la relation vers une dimension universelle.",
        }
        y = self._draw_text_block(c, chemin_desc.get(min(lp, 9), ""), y, font_size=10, color=CREAM)

    def _page_elements(self, c, s1, s2, p1, p2):
        """Page analyse élémentaire."""
        self._new_page(c)
        e1 = SIGNES.get(s1, {}).get('element', 'Feu')
        e2 = SIGNES.get(s2, {}).get('element', 'Feu')
        ec = _get_element_compat(e1, e2)

        y = self._chapter_header(c, f"{ec['titre']}", f"Harmonie des Éléments : {e1} x {e2}")

        y = self._score_bar(c, ec['score'], y, f"Score de compatibilité élémentaire")
        y -= 0.3 * cm

        y = self._sub_header(c, "Vos Forces Ensemble", y, size=13)
        y = self._draw_text_block(c, ec['force'], y, font_size=10.5, color=CREAM)

        y = self._sub_header(c, "Les Défis à Surmonter", y, size=13, color=ROSE)
        y = self._draw_text_block(c, ec['defi'], y, font_size=10.5, color=LIGHT_TEXT)

        y = self._sub_header(c, "Comment Vos Différences Deviennent une Force", y, size=13)
        n1 = p1['first_name']
        n2 = p2['first_name']

        if e1 != e2:
            diff_text = f"{n1} ({e1}) et {n2} ({e2}) viennent de deux mondes élémentaires différents. C'est précisément cette différence qui enrichit votre relation. "
            if e1 == "Feu" and e2 == "Eau" or e1 == "Eau" and e2 == "Feu":
                diff_text += f"Le partenaire {e1} apporte l'élan et l'action, tandis que le partenaire {e2} apporte la profondeur et la sensibilité. Sans l'un, l'autre serait incomplet. Le Feu a besoin de l'Eau pour ne pas se consumer, et l'Eau a besoin du Feu pour ne pas stagner."
            elif e1 == "Terre" and e2 == "Air" or e1 == "Air" and e2 == "Terre":
                diff_text += f"Le partenaire Terre apporte la stabilité et le concret, tandis que le partenaire Air apporte les idées et la communication. Ensemble, vous pouvez concevoir et réaliser des projets que ni l'un ni l'autre ne pourrait accomplir seul."
            else:
                diff_text += f"Le partenaire {e1} offre ce qui manque au partenaire {e2}, et vice versa. C'est dans cet échange que votre couple trouve sa richesse et son équilibre unique."
        else:
            diff_text = f"{n1} et {n2} partagent le même élément {e1}. Cette proximité crée une compréhension instinctive et une harmonie naturelle. Vos différences se jouent ailleurs : dans vos expériences de vie, vos chemins numérologiques et vos modalités respectives."

        y = self._draw_text_block(c, diff_text, y, font_size=10.5, color=CREAM)

        y = self._sub_header(c, "Conseil Pratique", y, size=12)
        y = self._draw_text_block(c, ec['conseil'], y, font_size=10.5, color=GOLD)

    def _page_attraction(self, c, s1, s2, p1, p2):
        """Page attraction et passion."""
        self._new_page(c)
        y = self._chapter_header(c, "L'Attraction et la Passion", "Ce qui vous attire l'un vers l'autre")

        n1 = p1['first_name']
        n2 = p2['first_name']
        info1 = SIGNES.get(s1, {})
        info2 = SIGNES.get(s2, {})
        pl1 = info1.get('planete', 'Mars')
        pl2 = info2.get('planete', 'Mars')

        intro = f"L'attraction entre {n1} ({s1}) et {n2} ({s2}) est une danse cosmique entre {pl1} et {pl2}. Ce qui vous attire chez l'autre est souvent ce qui vous manque ou ce qui résonne avec une partie profonde de vous-même."
        y = self._draw_text_block(c, intro, y, font_size=10.5, color=CREAM)

        y = self._sub_header(c, f"Ce que {n1} trouve chez {n2}", y, size=12)
        q2 = info2.get('qualites', ['mystérieux'])
        attract_1_to_2 = f"{n1} est naturellement attiré(e) par le côté {q2[0]} et {q2[1] if len(q2) > 1 else 'unique'} de {n2}. Le signe du {s2} exerce une fascination sur le {s1} car il représente une qualité complémentaire. {n2} incarne ce que {n1} admire secrètement et cherche à développer."
        y = self._draw_text_block(c, attract_1_to_2, y, font_size=10, color=LIGHT_TEXT)

        y = self._sub_header(c, f"Ce que {n2} trouve chez {n1}", y, size=12)
        q1 = info1.get('qualites', ['mystérieux'])
        attract_2_to_1 = f"{n2} est touché(e) par la nature {q1[0]} et {q1[1] if len(q1) > 1 else 'authentique'} de {n1}. Le {s1} possède une énergie que le {s2} reconnaît instinctivement comme nécessaire à son propre épanouissement. C'est une attraction qui va au-delà du physique."
        y = self._draw_text_block(c, attract_2_to_1, y, font_size=10, color=LIGHT_TEXT)

        y = self._sub_header(c, "La Chimie entre Vos Signes", y, size=12)
        e1 = info1.get('element', 'Feu')
        e2 = info2.get('element', 'Feu')
        if e1 == e2:
            chimie = f"Partageant le même élément {e1}, votre attraction repose sur une reconnaissance mutuelle profonde. Vous vous comprenez intuitivement car vous vibrez sur la même fréquence élémentaire."
        elif (e1 in ("Feu", "Air") and e2 in ("Feu", "Air")):
            chimie = f"L'attraction entre {e1} et {e2} est vive et stimulante. Votre relation est marquée par l'enthousiasme, les échanges dynamiques et une énergie communicative. La passion intellectuelle nourrit la passion physique."
        elif (e1 in ("Terre", "Eau") and e2 in ("Terre", "Eau")):
            chimie = f"L'attraction entre {e1} et {e2} est douce et profonde. Votre connexion est sensorielle, émotionnelle et enracinée. Vous construisez une intimité lente mais durable."
        else:
            chimie = f"L'attraction entre {e1} et {e2} est celle des contraires qui s'attirent. Ce qui vous séduit chez l'autre est précisément ce qui est différent de vous. Cette tension créatrice est le moteur de votre passion."
        y = self._draw_text_block(c, chimie, y, font_size=10.5, color=CREAM)

    def _page_communication(self, c, s1, s2, p1, p2):
        """Page communication et complicité."""
        self._new_page(c)
        y = self._chapter_header(c, "Communication et Complicité", "Comment vous vous comprenez")

        n1 = p1['first_name']
        n2 = p2['first_name']
        info1 = SIGNES.get(s1, {})
        info2 = SIGNES.get(s2, {})
        e1 = info1.get('element', 'Feu')
        e2 = info2.get('element', 'Feu')
        m1 = info1.get('modalite', 'Cardinal')
        m2 = info2.get('modalite', 'Cardinal')

        mc = _get_modalite_compat(m1, m2)

        intro = f"La communication est le ciment de toute relation durable. Entre {n1} ({s1}) et {n2} ({s2}), le dialogue est coloré par vos éléments ({e1} et {e2}) et vos modalités ({m1} et {m2})."
        y = self._draw_text_block(c, intro, y, font_size=10.5, color=CREAM)

        y = self._sub_header(c, f"Style de communication de {n1}", y, size=12)
        comm_styles = {
            "Feu": f"{n1} communique avec passion et franchise. Les mots sont directs, énergiques, parfois brusques mais toujours sincères. En couple, {n1} a besoin d'être entendu(e) et validé(e) dans son enthousiasme.",
            "Terre": f"{n1} communique par les actes plus que par les mots. Concret et pragmatique, {n1} exprime son amour à travers des gestes tangibles. En couple, {n1} a besoin de preuves concrètes d'engagement.",
            "Air": f"{n1} communique avec aisance et intelligence. Les échanges d'idées sont essentiels. En couple, {n1} a besoin de stimulation intellectuelle et de conversations profondes.",
            "Eau": f"{n1} communique par l'émotion et l'intuition. Les non-dits sont souvent plus importants que les mots. En couple, {n1} a besoin de connexion émotionnelle et de validation de ses sentiments.",
        }
        y = self._draw_text_block(c, comm_styles.get(e1, ""), y, font_size=10, color=LIGHT_TEXT)

        y = self._sub_header(c, f"Style de communication de {n2}", y, size=12)
        y = self._draw_text_block(c, comm_styles.get(e2, "").replace(n1, n2), y, font_size=10, color=LIGHT_TEXT)

        y = self._sub_header(c, "Dynamique du Couple", y, size=12)
        y = self._draw_text_block(c, mc['dynamique'], y, font_size=10.5, color=CREAM)

        y = self._sub_header(c, "Conseils pour Mieux Communiquer", y, size=12)
        y = self._draw_text_block(c, mc['conseil'], y, font_size=10.5, color=GOLD)

    def _page_conflicts(self, c, s1, s2, p1, p2):
        """Page défis et résolution de conflits."""
        self._new_page(c)
        y = self._chapter_header(c, "Défis et Résolution de Conflits", "Transformer les tensions en croissance")

        n1 = p1['first_name']
        n2 = p2['first_name']
        info1 = SIGNES.get(s1, {})
        info2 = SIGNES.get(s2, {})
        e1 = info1.get('element', 'Feu')
        e2 = info2.get('element', 'Feu')
        o1 = info1.get('ombre', [])
        o2 = info2.get('ombre', [])

        intro = f"Chaque couple rencontre des défis. Entre {n1} ({s1}) et {n2} ({s2}), ces défis sont spécifiques et prévisibles. Les connaître, c'est déjà les apprivoiser."
        y = self._draw_text_block(c, intro, y, font_size=10.5, color=CREAM)

        # Zone de tension 1: Shadow aspects
        y = self._sub_header(c, "Les Zones de Tension", y, size=13, color=ROSE)

        tension_1 = f"Le côté {o1[0] if o1 else 'sensible'} de {n1} peut heurter {n2}, qui a tendance à être {o2[0] if o2 else 'sensible'}. Cette friction est naturelle entre {s1} et {s2} et ne signifie pas l'incompatibilité — elle signifie que vous devez apprendre à naviguer ces différences."
        y = self._draw_text_block(c, tension_1, y, font_size=10, color=LIGHT_TEXT)

        if len(o1) > 1 and len(o2) > 1:
            tension_2 = f"Quand {n1} devient {o1[1]}, {n2} peut réagir en devenant {o2[1]}. C'est un schéma réactif classique qu'il faut identifier et désamorcer consciemment."
            y = self._draw_text_block(c, tension_2, y, font_size=10, color=LIGHT_TEXT)

        # How to resolve conflicts
        y = self._sub_header(c, "Comment Régler Vos Conflits", y, size=13)

        strategies = []
        if e1 == "Feu" or e2 == "Feu":
            strategies.append("Laissez le partenaire Feu exprimer sa frustration, puis attendez 30 minutes avant de reprendre la discussion calmement. Le Feu s'éteint vite une fois qu'il a pu s'exprimer.")
        if e1 == "Terre" or e2 == "Terre":
            strategies.append("Le partenaire Terre a besoin de temps pour traiter les émotions. Ne le/la pressez pas. Proposez de revenir sur le sujet le lendemain, une fois les émotions apaisées.")
        if e1 == "Air" or e2 == "Air":
            strategies.append("Le partenaire Air a besoin de comprendre logiquement ce qui se passe. Expliquez vos sentiments avec des mots clairs. Évitez les reproches vagues — soyez précis.")
        if e1 == "Eau" or e2 == "Eau":
            strategies.append("Le partenaire Eau se sent blessé(e) facilement. Validez ses émotions avant de chercher des solutions. Un simple « je comprends que tu ressentes cela » fait des miracles.")

        strategies.append(f"Règle d'or pour {n1} et {n2} : ne jamais aller au lit en colère. Prenez 5 minutes pour vous dire une chose que vous appréciez chez l'autre, même au cœur d'un conflit.")

        for i, strat in enumerate(strategies, 1):
            y = self._draw_text_block(c, f"{i}. {strat}", y, font_size=10, color=CREAM)

        # Differences as strengths
        y = self._sub_header(c, "Vos Différences sont Votre Force", y, size=13)
        diff_force = f"Ce qui crée de la tension entre {n1} et {n2} est aussi ce qui crée de la croissance. Chaque conflit surmonté ensemble vous rend plus forts et plus proches. Vos ombres respectives ({', '.join(o1[:2])} et {', '.join(o2[:2])}) sont des invitations à évoluer — séparément et ensemble."
        y = self._draw_text_block(c, diff_force, y, font_size=10.5, color=GOLD)

    def _page_real_compatibility(self, c, s1, s2, p1, p2, lp1, lp2, question):
        """Page de compatibilité réelle."""
        self._new_page(c)
        y = self._chapter_header(c, "Votre Compatibilité Réelle", "Au-delà des clichés astrologiques")

        n1 = p1['first_name']
        n2 = p2['first_name']
        e1 = SIGNES.get(s1, {}).get('element', 'Feu')
        e2 = SIGNES.get(s2, {}).get('element', 'Feu')
        ec = _get_element_compat(e1, e2)
        score = ec['score']

        # Overall score
        y = self._sub_header(c, "Score Global de Compatibilité", y, size=14)
        y = self._score_bar(c, score, y)
        y -= 0.3 * cm

        if score >= 80:
            verdict = f"{n1} et {n2}, votre compatibilité est naturellement élevée. Vos énergies s'harmonisent avec fluidité. Cela ne signifie pas l'absence de défis, mais que votre base est solide et que vous avez les ressources cosmiques pour traverser les tempêtes ensemble."
        elif score >= 60:
            verdict = f"{n1} et {n2}, votre compatibilité est bonne et prometteuse, à condition de cultiver activement votre relation. Vous avez de vraies forces ensemble, mais certaines zones demandent de la conscience et des efforts mutuels. C'est un couple qui grandit avec le temps."
        else:
            verdict = f"{n1} et {n2}, votre compatibilité élémentaire est un défi — mais c'est justement ce qui peut rendre votre relation extraordinaire. Les couples les plus transformateurs sont souvent ceux qui doivent travailler le plus. Votre relation vous demande de grandir, et c'est un cadeau précieux."

        y = self._draw_text_block(c, verdict, y, font_size=10.5, color=CREAM)

        # Life path compatibility
        y = self._sub_header(c, f"Vos Chemins de Vie : {lp1} et {lp2}", y, size=13)
        chemin_text = _get_chemin_compat(lp1, lp2)
        y = self._draw_text_block(c, chemin_text, y, font_size=10.5, color=LIGHT_TEXT)

        # Answer the user's question
        if question and question.strip():
            y = self._sub_header(c, "Réponse à Votre Question", y, size=13, color=GOLD)
            y = self._draw_text_block(c, f"« {question} »", y, font_size=10, color=HexColor('#B8B0C8'))
            y -= 0.2 * cm

            # Generate a relevant response based on compatibility
            if score >= 70:
                answer = f"Les astres sont favorables à votre union. Votre question révèle une préoccupation légitime, mais la force de votre compatibilité ({e1} x {e2}) vous donne les outils pour y répondre ensemble. La clé est dans la communication ouverte et la confiance que vos éléments vous offrent naturellement."
            else:
                answer = f"Votre question touche au cœur de votre dynamique de couple. La tension entre {e1} et {e2} est réelle, mais elle est aussi le moteur de votre croissance. Pour avancer sur ce sujet, appuyez-vous sur vos forces respectives : la capacité de {n1} à être {SIGNES.get(s1, {}).get('qualites', ['authentique'])[0]} et celle de {n2} à être {SIGNES.get(s2, {}).get('qualites', ['authentique'])[0]}."
            y = self._draw_text_block(c, answer, y, font_size=10.5, color=CREAM)

    def _page_future(self, c, s1, s2, p1, p2, lp1, lp2):
        """Page clés de réussite et avenir."""
        self._new_page(c)
        y = self._chapter_header(c, "Les Clés de Votre Réussite", "Votre avenir ensemble")

        n1 = p1['first_name']
        n2 = p2['first_name']
        e1 = SIGNES.get(s1, {}).get('element', 'Feu')
        e2 = SIGNES.get(s2, {}).get('element', 'Feu')

        intro = f"Chaque couple possède des clés uniques pour s'épanouir. Voici les vôtres, {n1} et {n2}, basées sur l'alchimie de vos signes et de vos chemins de vie."
        y = self._draw_text_block(c, intro, y, font_size=10.5, color=CREAM)

        need_map = {"Feu": "action et d'aventure", "Terre": "calme et de stabilité", "Air": "stimulation intellectuelle", "Eau": "solitude et de rêverie"}
        need1 = need_map.get(e1, "harmonie")
        need2 = need_map.get(e2, "harmonie")

        keys = [
            ("Rituel quotidien", f"Instaurez un moment sacré chaque jour — même 10 minutes — où vous vous connectez pleinement l'un à l'autre. Pour un couple {s1}/{s2}, ce rituel pourrait être une promenade en pleine nature, une conversation sans écran, ou simplement se tenir la main en silence."),
            ("Langage de l'autre", f"{n1}, apprenez à parler le langage émotionnel de {n2}. {n2}, faites de même. Le {s1} exprime l'amour d'une manière, le {s2} d'une autre. Reconnaître ces différences transforme les malentendus en preuves d'amour."),
            ("Projets communs", f"Construisez quelque chose ensemble — un voyage, un projet créatif, un objectif familial. La dynamique {e1}/{e2} prend tout son sens quand elle est canalisée vers un but commun."),
            ("Espace individuel", f"Chacun a besoin de son propre espace pour se ressourcer. {n1} a besoin de {need1}. {n2} a besoin de {need2}. Respecter ces besoins renforce le couple."),
            ("Gratitude", f"Exprimez régulièrement votre gratitude l'un envers l'autre. La combinaison {s1}/{s2} s'épanouit quand chaque partenaire se sent reconnu et apprécié dans sa singularité."),
        ]

        for title, desc in keys:
            y = self._sub_header(c, title, y, size=12)
            y = self._draw_text_block(c, desc, y, font_size=10, color=LIGHT_TEXT)

    def _page_final(self, c, p1, p2, s1, s2):
        """Page de conclusion."""
        self._new_page(c)
        y = self.height - 8 * cm

        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        c.line(4 * cm, y + 2 * cm, self.width - 4 * cm, y + 2 * cm)

        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(self.width / 2, y, "Message de la Plume Astrale")
        y -= 1.5 * cm

        n1 = p1['first_name']
        n2 = p2['first_name']
        lines = [
            f"Cher(ère) {n1} et {n2},",
            "",
            "Les étoiles éclairent votre chemin,",
            "mais c'est votre amour qui le trace.",
            "",
            f"Votre union {s1} x {s2}",
            "est unique dans tout l'univers.",
            "",
            "Que ce rapport vous aide à mieux",
            "vous comprendre, vous respecter",
            "et vous aimer chaque jour davantage.",
            "",
            "Les astres ne décident pas de votre destin —",
            "ils vous offrent une carte.",
            "C'est vous qui choisissez le chemin.",
        ]
        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica", 12)
        for line in lines:
            c.drawCentredString(self.width / 2, y, line)
            y -= 0.55 * cm

        y -= 1 * cm
        c.setFillColor(MEDIUM_PURPLE)
        c.setFillAlpha(0.5)
        c.roundRect(3 * cm, y - 1.5 * cm, self.width - 6 * cm, 1.5 * cm, 10, fill=1)
        c.setFillAlpha(1.0)
        c.setFillColor(CREAM)
        c.setFont("Helvetica-BoldOblique", 12)
        c.drawCentredString(self.width / 2, y - 0.7 * cm, "Que les étoiles vous guident,")
        c.drawCentredString(self.width / 2, y - 1.2 * cm, "que la Plume vous éclaire.")

        y -= 3 * cm
        c.setStrokeColor(GOLD)
        c.line(5 * cm, y, self.width - 5 * cm, y)
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Oblique", 11)
        c.drawCentredString(self.width / 2, y - 0.8 * cm, "Plume Astrale")
        c.setFillAlpha(0.6)
        c.setFont("Helvetica", 9)
        c.drawCentredString(self.width / 2, y - 1.4 * cm, "www.plume-astrale.fr")
        c.setFillAlpha(1.0)

    def generate(self, person1, person2, question=""):
        """Génère le PDF complet de compatibilité."""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        s1 = _get_zodiac(person1['day'], person1['month'])
        s2 = _get_zodiac(person2['day'], person2['month'])
        lp1 = _calc_life_path(person1['day'], person1['month'], person1['year'])
        lp2 = _calc_life_path(person2['day'], person2['month'], person2['year'])

        self._page_cover(c, person1, person2, s1, s2)
        self._page_profiles(c, person1, person2, s1, s2, lp1, lp2)
        self._page_partner_detail(c, person1, s1, lp1, 1)
        self._page_partner_detail(c, person2, s2, lp2, 2)
        self._page_elements(c, s1, s2, person1, person2)
        self._page_attraction(c, s1, s2, person1, person2)
        self._page_communication(c, s1, s2, person1, person2)
        self._page_conflicts(c, s1, s2, person1, person2)
        self._page_real_compatibility(c, s1, s2, person1, person2, lp1, lp2, question)
        self._page_future(c, s1, s2, person1, person2, lp1, lp2)
        self._page_final(c, person1, person2, s1, s2)

        c.save()
        buffer.seek(0)
        return buffer.getvalue()


def generate_compatibility_pdf(person1: dict, person2: dict, question: str = "") -> bytes:
    """Point d'entrée pour générer le PDF de compatibilité."""
    gen = CompatibilityPDFGenerator()
    return gen.generate(person1, person2, question)
