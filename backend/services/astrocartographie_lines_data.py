"""Interprétations statiques FR des lignes planétaires d'astrocartographie.

Format : PLANETARY_LINES[planet][line_type] = {'headline': str, 'body': str}

Line types :
  - AC : Ascendant   → identité, apparence, corps, énergie personnelle
  - DC : Descendant  → relations, mariage, partenariats, autres
  - MC : Milieu du Ciel → carrière, image publique, réputation, vocation
  - IC : Fond du Ciel   → racines, intimité, famille, foyer profond
"""
from __future__ import annotations

PLANETARY_LINES: dict[str, dict[str, dict[str, str]]] = {
    'Sun': {
        'AC': {'headline': "Ta lumière propre",
               'body': "Ta ligne Soleil-Ascendant révèle qui tu es quand tu ne joues aucun rôle. Sur cette ligne, tu rayonnes ta version la plus vraie : les gens te voient enfin sans filtre. C'est un lieu de vitalité, de leadership tranquille, où ton identité solaire trouve sa forme la plus juste."},
        'DC': {'headline': "L'autre comme miroir",
               'body': "Le Soleil au Descendant : les partenariats deviennent centraux. Tu attires des figures charismatiques, autoritaires, souvent inspirantes. Elles te renvoient à ta propre puissance. Parfois épuisant, toujours révélateur — c'est une ligne de vie à deux."},
        'MC': {'headline': "La couronne visible",
               'body': "Ta vocation trouve son théâtre. Ici, ton travail te met en lumière : reconnaissance, promotions, visibilité publique. Le Soleil au Milieu du Ciel offre un terrain d'ambition légitime, où l'on t'attribue ce que tu accomplis vraiment."},
        'IC': {'headline': "La maison où tu respires",
               'body': "Ici tu poses tes racines. Le Soleil au Fond du Ciel est une ligne de recueillement, de foyer solide, d'intimité radieuse. Idéale pour élever une famille, écrire un livre, ou simplement se retrouver soi-même."},
    },
    'Moon': {
        'AC': {'headline': "Ta peau devient poreuse",
               'body': "La Lune-Ascendant te rend sensible, réceptive, très intuitive. Les émotions des lieux te traversent. Beau pour l'inspiration artistique et le lien maternel, à surveiller si tu es hypersensible."},
        'DC': {'headline': "L'intimité qui déborde",
               'body': "Les relations deviennent nourricières, fusionnelles, parfois enveloppantes. Tu croises des âmes qui savent te consoler — et qui parfois te dévorent. Ligne d'amour tendre et vulnérable."},
        'MC': {'headline': "Un métier de cœur",
               'body': "Ta vocation s'exprime dans le soin, l'écoute, la nourriture, l'accompagnement. La Lune au Milieu du Ciel te donne une popularité tendre : les gens te confient ce qu'ils ne disent à personne."},
        'IC': {'headline': "Le vrai chez-toi",
               'body': "L'endroit le plus émotionnellement juste pour habiter. La Lune au Fond du Ciel est une ligne de refuge profond, d'ancrage familial, de guérison lente. Une adresse pour la vie."},
    },
    'Mercury': {
        'AC': {'headline': "Ta parole trouve son rythme",
               'body': "Mercure-Ascendant aiguise ton esprit. Tu penses vite, tu écris juste, tu apprends une nouvelle langue plus facilement. C'est une ligne d'intelligence en mouvement, idéale pour les étudiants, journalistes, éditeurs."},
        'DC': {'headline': "Les rencontres qui parlent",
               'body': "Les gens que tu croises stimulent ton mental. Débats vifs, échanges féconds, collaborations intellectuelles. Attention aux relations superficielles — cherche ceux qui pensent aussi profondément qu'ils parlent."},
        'MC': {'headline': "Communiquer pour vivre",
               'body': "Ta carrière passe par les mots : écriture, enseignement, marketing, formation. Mercure-MC est une ligne d'expertise reconnue dès qu'on prend la parole publiquement."},
        'IC': {'headline': "Un foyer d'idées",
               'body': "Ta maison devient un lieu de conversations, de livres, de projets rédigés à la table. Mercure au Fond du Ciel favorise le travail intellectuel à domicile."},
    },
    'Venus': {
        'AC': {'headline': "Le charme incarné",
               'body': "Vénus-Ascendant embellit ton apparence, adoucit ton visage, rend ton sourire irrésistible. Les gens te trouvent belle, gracieuse. C'est une ligne d'art, d'esthétique, de séduction naturelle."},
        'DC': {'headline': "La rencontre amoureuse",
               'body': "L'une des lignes les plus romantiques de l'astrocartographie. Vénus au Descendant favorise les rencontres marquantes, les histoires d'amour intenses, les mariages heureux. À visiter avec le cœur ouvert."},
        'MC': {'headline': "Créer beau, gagner bien",
               'body': "Ta carrière prospère dans les arts, la mode, le luxe, le design, la relation client. Vénus-MC attire l'argent avec grâce et sans conflit. Une ligne d'abondance esthétique."},
        'IC': {'headline': "Un chez-soi qui apaise",
               'body': "Une maison qui devient un havre de beauté, de plaisir, de tendresse. Vénus au Fond du Ciel favorise une vie familiale harmonieuse, un intérieur soigné, des amours durables."},
    },
    'Mars': {
        'AC': {'headline': "L'énergie pure",
               'body': "Mars-Ascendant décuple ta vitalité, ton audace, ton corps. Tu deviens plus active, plus sportive, plus assumée. Attention à l'irritabilité — cette ligne exige que tu bouges pour ne pas t'enflammer."},
        'DC': {'headline': "Le feu dans les relations",
               'body': "Les relations sont passionnées, intenses, parfois conflictuelles. Tu attires des partenaires puissants qui te confrontent. À explorer si tu sens que tu t'endors — à éviter si tu es déjà en tension."},
        'MC': {'headline': "L'ambition qui gagne",
               'body': "Ta carrière prend une dimension guerrière, entrepreneuriale, compétitive. Mars-MC est une ligne pour ceux qui veulent conquérir un marché, monter une entreprise, se battre pour un idéal."},
        'IC': {'headline': "Un foyer en tension",
               'body': "Attention : Mars au Fond du Ciel peut créer des conflits familiaux ou une agitation domestique. À éviter comme lieu de vie longue durée, sauf si tu es en quête d'action permanente."},
    },
    'Jupiter': {
        'AC': {'headline': "L'expansion joyeuse",
               'body': "Jupiter-Ascendant est LA ligne de la chance. Tu es plus optimiste, plus ouverte, plus attirante. Les opportunités arrivent. C'est une ligne de croissance, d'aventure, de générosité."},
        'DC': {'headline': "Le partenaire providentiel",
               'body': "Une rencontre qui change ta vie t'attend ici. Jupiter au Descendant favorise les mentors, les mariages avec des étrangers, les alliances qui te propulsent socialement."},
        'MC': {'headline': "Le succès qui déborde",
               'body': "L'une des lignes les plus favorables à la carrière. Jupiter-MC attire les grandes opportunités, les postes de leadership, la visibilité internationale. Une adresse pour réussir en grand."},
        'IC': {'headline': "L'abondance à la maison",
               'body': "Un foyer prospère, spacieux, accueillant. Jupiter au Fond du Ciel favorise l'agrandissement de la famille, l'achat d'une belle propriété, la générosité familiale."},
    },
    'Saturn': {
        'AC': {'headline': "La discipline te grandit",
               'body': "Saturne-Ascendant t'invite à te structurer, à te tenir droit, à mûrir. Ligne d'apprentissage sérieux — pas la plus légère, mais l'une des plus formatrices sur le long terme."},
        'DC': {'headline': "Des relations qui durent",
               'body': "Tu attires des partenaires plus âgés, sérieux, engagés. Saturne au Descendant favorise les mariages stables, les collaborations professionnelles solides. Peu de fantaisie, beaucoup de solidité."},
        'MC': {'headline': "La reconnaissance méritée",
               'body': "Ta carrière se construit lentement mais sûrement. Saturne-MC est une ligne d'autorité gagnée par le travail : experts, dirigeants, institutions. Exigeant, mais durable."},
        'IC': {'headline': "Des racines à assumer",
               'body': "Ligne de confrontation familiale, de responsabilité envers les parents ou les enfants. Saturne au Fond du Ciel demande de la maturité intérieure — un lieu où l'on grandit vite."},
    },
    'Uranus': {
        'AC': {'headline': "Devenir libre",
               'body': "Uranus-Ascendant fait de toi une personne originale, magnétique, imprévisible. Tu casses des codes, tu changes de style. Ligne de liberté intérieure — instable pour certains, libératrice pour d'autres."},
        'DC': {'headline': "Rencontres électriques",
               'body': "Des rencontres soudaines, hors-normes, qui bouleversent ta vie. Uranus au Descendant favorise les histoires atypiques et les ruptures nécessaires. Rien ne reste comme avant."},
        'MC': {'headline': "L'innovation reconnue",
               'body': "Ta carrière prend une tournure technologique, avant-gardiste, indépendante. Uranus-MC attire les créatifs, les entrepreneurs, les inventeurs. Instable mais brillant."},
        'IC': {'headline': "Un foyer changeant",
               'body': "Uranus au Fond du Ciel rime avec instabilité domestique, déménagements fréquents, famille non-conventionnelle. À éviter si tu cherches la stabilité."},
    },
    'Neptune': {
        'AC': {'headline': "L'aura spirituelle",
               'body': "Neptune-Ascendant t'ouvre à la spiritualité, à l'art, à la musique, à la méditation. Ton aura devient mystique. Ligne d'inspiration profonde — attention à l'évasion, aux illusions, aux dépendances."},
        'DC': {'headline': "L'amour idéalisé",
               'body': "Tu tombes amoureuse d'âmes mystérieuses, artistes, spirituelles. Neptune au Descendant offre des relations sublimes ou des désillusions cruelles — reste lucide."},
        'MC': {'headline': "Une vocation d'âme",
               'body': "Ta carrière prend une dimension artistique, spirituelle, thérapeutique ou humanitaire. Neptune-MC est idéal pour les créateurs, les soignants, les guides spirituels."},
        'IC': {'headline': "Un refuge sacré",
               'body': "Un foyer contemplatif, artistique, spirituel — au bord de l'eau si possible. Neptune au Fond du Ciel te ramène à l'essentiel. Idéal pour méditer, écrire, guérir."},
    },
    'Pluto': {
        'AC': {'headline': "Ta transformation profonde",
               'body': "Pluton-Ascendant amorce une métamorphose totale. Tu deviens plus intense, plus magnétique, plus vraie. Ligne de renaissance — parfois brutale, toujours puissante. À vivre en conscience."},
        'DC': {'headline': "Des amours qui transforment",
               'body': "Rencontres fusionnelles, obsessions, passions qui te retournent l'âme. Pluton au Descendant est la ligne de l'amour-tabou et de l'amour-vérité. Rien de tiède ici."},
        'MC': {'headline': "Le pouvoir gagné",
               'body': "Ta carrière prend une dimension d'influence, de pouvoir, parfois de politique ou de finance. Pluton-MC attire les postes-clés, souvent après une renaissance professionnelle."},
        'IC': {'headline': "Le nœud familial",
               'body': "Pluton au Fond du Ciel confronte aux non-dits familiaux, aux blessures ancestrales, aux transformations profondes du foyer. À visiter pour guérir, à quitter si trop lourd."},
    },
}


LINE_TYPE_FR = {
    'AC': 'Ascendant',
    'DC': 'Descendant',
    'MC': 'Milieu du Ciel',
    'IC': 'Fond du Ciel',
    'ASC': 'Ascendant',
    'DESC': 'Descendant',
}


PLANET_FR = {
    'Sun': 'Soleil', 'Moon': 'Lune', 'Mercury': 'Mercure', 'Venus': 'Vénus',
    'Mars': 'Mars', 'Jupiter': 'Jupiter', 'Saturn': 'Saturne',
    'Uranus': 'Uranus', 'Neptune': 'Neptune', 'Pluto': 'Pluton',
}


def get_line_interpretation(planet: str, line_type: str) -> dict[str, str] | None:
    """Retourne {'planet_fr','line_fr','headline','body'} ou None."""
    line_type = (line_type or '').upper()
    if line_type in ('ASC',):
        line_type = 'AC'
    if line_type in ('DESC',):
        line_type = 'DC'
    interp = PLANETARY_LINES.get(planet, {}).get(line_type)
    if not interp:
        return None
    return {
        'planet_fr': PLANET_FR.get(planet, planet),
        'line_fr': LINE_TYPE_FR.get(line_type, line_type),
        'headline': interp['headline'],
        'body': interp['body'],
    }


def dedupe_lines(lines: list) -> list:
    """Retire les doublons (planet+line_type) et ne garde que les 10 planètes principales."""
    seen = set()
    keep = set(PLANETARY_LINES.keys())
    out = []
    for line in (lines or []):
        if not isinstance(line, dict):
            continue
        p = line.get('planet')
        lt = (line.get('line_type') or line.get('angle') or '').upper()
        if p not in keep:
            continue
        k = (p, lt)
        if k in seen:
            continue
        seen.add(k)
        out.append({'planet': p, 'line_type': lt})
    # Ordre : par planète (ordre astro classique) puis par line_type
    planet_order = list(PLANETARY_LINES.keys())
    line_order = ['AC', 'MC', 'DC', 'IC']
    out.sort(key=lambda x: (
        planet_order.index(x['planet']) if x['planet'] in planet_order else 99,
        line_order.index(x['line_type']) if x['line_type'] in line_order else 99,
    ))
    return out
