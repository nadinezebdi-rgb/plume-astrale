"""Génère un échantillon PDF Thème Natal pour inspection visuelle.

Usage :
    cd /app/backend && python tests/_gen_sample_natal_pdf.py
Produit /app/sample_natal_lot1.pdf (à inspecter côté user).
"""
import os
import sys
sys.path.insert(0, '/app/backend')

from services.natal_pdf_v2 import build_natal_pdf_v2

# Dataset réaliste pour un rendu "mode livre riche" (bd=True)
NATAL_DATA = {
    'sun_sign': 'Cancer',
    'moon_sign': 'Poissons',
    'ascendant_sign': 'Vierge',
    'no_birth_time': False,
    'tier': 'ultra',
    'planets': [
        {'name': 'Soleil',    'sign': 'Cancer',    'analysis': 'Tu portes la sensibilité du Cancer avec une profondeur rare. Ton rapport au foyer et à la mémoire est viscéral.\n\nCe qui te distingue : une capacité à sentir ce que les autres n’osent dire. Tu es un refuge sans le savoir.'},
        {'name': 'Lune',      'sign': 'Poissons',  'analysis': 'Lune en Poissons : tes émotions circulent sans frontière. Tu absorbes ce qui t’entoure comme une éponge sensible.\n\nTon besoin fondamental : des espaces de silence pour redevenir toi, loin du bruit du monde.'},
        {'name': 'Mercure',   'sign': 'Cancer',    'analysis': 'Mercure en Cancer : tu penses avec le cœur avant la raison. Ton langage est teinté d’affect et d’intuition.\n\nTu te souviens des mots que les autres oublient — chaque phrase est une empreinte.'},
        {'name': 'Vénus',     'sign': 'Lion',      'analysis': 'Vénus en Lion : tu aimes avec panache, générosité, et un besoin de reconnaissance.\n\nTon amour est théâtral mais sincère — tu veux être vue et choisie, pas simplement acceptée.'},
        {'name': 'Mars',      'sign': 'Taureau',   'analysis': 'Mars en Taureau : ton action est lente mais inarrêtable. Tu construis dans la patience.\n\nTa colère est rare mais, quand elle vient, elle dure. Tu ne pardonnes pas facilement.'},
        {'name': 'Jupiter',   'sign': 'Scorpion',  'analysis': 'Jupiter en Scorpion : tu grandis dans l’intensité et les transformations profondes.\n\nTes plus grandes chances arrivent après des crises qui t’obligent à muer.'},
        {'name': 'Saturne',   'sign': 'Verseau',   'analysis': 'Saturne en Verseau : ta discipline s’apprend par l’indépendance. Tu structures ta vie contre les conventions.\n\nTa maturité se construit en osant ne pas appartenir.'},
        {'name': 'Uranus',    'sign': 'Capricorne','analysis': 'Uranus en Capricorne : tu portes une rébellion méthodique, un besoin de refonder les structures.\n\nTon génie est pragmatique, pas chaotique.'},
        {'name': 'Neptune',   'sign': 'Capricorne','analysis': 'Neptune en Capricorne : ton imaginaire s’ancre dans le concret. Tu rêves pour bâtir.\n\nAttention à la désillusion quand la réalité ne suit pas ton idéal strict.'},
        {'name': 'Pluton',    'sign': 'Scorpion',  'analysis': 'Pluton en Scorpion : tu traverses des morts symboliques pour renaître plus forte.\n\nTa puissance intérieure est magnétique — les gens le sentent sans comprendre pourquoi.'},
        {'name': 'Ascendant', 'sign': 'Vierge',    'analysis': 'Ascendant Vierge : tu abordes le monde avec clarté, précision, discernement.\n\nTon aura est modeste mais ta lucidité est redoutable.'},
    ],
    'synthese_aspects': 'Tes aspects dessinent un portrait de profondeur et de réserve. Le trigone Lune-Jupiter ouvre une veine de chance émotionnelle, pendant que le carré Soleil-Saturne te demande un effort permanent de légitimité.',
    'houses': [
        {'num': i, 'sign': ['Vierge','Balance','Scorpion','Sagittaire','Capricorne','Verseau','Poissons','Bélier','Taureau','Gémeaux','Cancer','Lion'][i-1], 'planets_in_house': []}
        for i in range(1, 13)
    ],
    'enhanced_personal_analysis': {},
}

BOOK_DATA = {
    '_source': 'cache',
    '_em': {
        'dominant_element': 'Eau',
        'dominant_element_count': 5,
        'dominant_modality': 'Fixe',
        'dominant_modality_count': 4,
    },
    'dedication': 'À toi qui ouvres ce livre, puisse-t-il devenir compagnon des heures claires et des heures troubles.',
    'element_analysis': "Ton eau domine : tu te meus dans un monde d’impressions avant les mots. C’est une richesse rare — et une invitation à poser des berges autour de ta sensibilité pour ne pas te laisser submerger. Cette prédominance aquatique t’offre une mémoire émotionnelle longue, où chaque rencontre laisse une empreinte. Tu perçois les atmosphères avant que les paroles ne soient prononcées, tu lis entre les lignes des silences, tu devines les secrets que les autres n’osent nommer. Mais cette porosité demande un art : celui de rentrer en toi régulièrement pour trier ce qui t’appartient de ce que tu as absorbé.",
    'modality_analysis': "Ta modalité fixe te donne une colonne vertébrale. Tu tiens là où d’autres plient, tu reviens là où d’autres s’éparpillent. C’est ta force : une loyauté viscérale envers tes engagements, tes amours, tes convictions. Attention cependant au prix de l’obstination — parfois, ce que tu nommes fidélité est en réalité une peur du changement déguisée. Apprends à distinguer les terres sacrées à défendre des sables mouvants dont il faut sortir. Ton pouvoir réside dans ce discernement patient.",
    'trio_synthesis': "Ton Soleil Cancer, ta Lune Poissons et ton Ascendant Vierge forment un dialogue subtil entre la mer et la rive. L’émotion fluide des deux premiers trouve dans la Vierge sa structure, sa clarté, son discernement. Tu ne te noies jamais complètement parce qu’une part de toi observe, analyse, trie. Ce triangle intérieur te donne une rare capacité d’empathie précise : tu sens profondément et tu nommes justement. C’est le propre des grandes consolatrices et des grandes thérapeutes — tu portes cette signature.",
    'aspects_harmonieux_headline': 'La grâce en toi',
    'aspects_harmonieux_body': "Tes trigones et sextiles ouvrent des zones de fluidité où tout circule sans effort. Ce sont les talents que tu n’as pas eu besoin d’apprendre : la justesse émotionnelle, le sens du soin, l’intuition créative. Ces dons sont si naturels que tu risques de les sous-estimer. Rappelle-toi : ce qui te coûte peu peut valoir immensément pour ceux qui en manquent. N’hésite pas à offrir ces dons comme des cadeaux délibérés plutôt que des évidences discrètes.",
    'aspects_tensions_headline': 'Le nœud qui te forge',
    'aspects_tensions_body': "Tes carrés et oppositions te confrontent — ils sont tes meilleurs maîtres, même si ce sont les plus exigeants. Chaque friction intérieure t’oblige à inventer, à créer un troisième chemin que ni l’une ni l’autre polarité n’offrait seule. C’est ainsi que ta profondeur se construit : non pas en évitant la tension mais en la transformant en architecture intérieure. Les plus belles œuvres naissent de ce travail d’alchimiste.",
    'rare_aspect_headline': 'Ta note rare',
    'rare_aspect_body': "Il existe dans ton ciel une signature peu commune, qui te singularise. Elle ne te rend pas supérieure, elle te rend reconnaissable. Cette note rare est le filigrane de ton œuvre, cette qualité étrange que tu portes depuis l’enfance et que les autres remarquent sans toujours savoir la nommer. Apprends à la revendiquer plutôt qu’à la cacher — c’est elle qui te mènera aux lieux et aux êtres qui t’attendent.",
    'houses_intro': "Les douze maisons sont les terrains où tes planètes s’incarnent dans ta vie quotidienne. Elles traduisent l’énergie céleste en expérience vécue : le corps, l’argent, les mots, le foyer, la création, le travail, l’amour, la transformation, le sens, la vocation, la tribu, le sanctuaire. Chaque maison est une pièce de ta maison intérieure, et chaque planète y pose sa lumière particulière.",
    'house_1': "Maison I — Ta présence dans le monde. C’est l’enveloppe que tu offres aux autres, la première impression que tu laisses, la silhouette que ton corps dessine dans l’espace. Cultive-la comme un vêtement choisi, pas comme un uniforme imposé.",
    'house_2': "Maison II — Tes ressources matérielles et ton rapport à la valeur. Argent, biens, talents monnayables : tout cela te parle moins du compte en banque que de l’estime que tu te portes. Enrichis-toi d’abord intérieurement, le reste suit.",
    'house_3': "Maison III — Ton esprit vif, tes mots, tes trajets quotidiens, tes frères et sœurs d’âme. C’est le royaume de la curiosité et des échanges courts. Nourris-le de lectures, de conversations, de petits voyages qui aèrent ton mental.",
    'house_4': "Maison IV — Ton foyer intérieur, tes racines, ta lignée. C’est la fondation invisible sur laquelle tout le reste s’élève. Les blessures y résident, mais aussi les forces ancestrales dont tu es héritière sans le savoir.",
    'house_5': "Maison V — Tes créations, tes amours, tes enfants intérieurs. C’est le lieu du jeu sacré, de la joie non négociable. Si tu l’abandonnes, tout le reste pâlit. Rends-lui ses droits régulièrement.",
    'house_6': "Maison VI — Ton quotidien et ton artisanat de soi. Santé, routines, service rendu : ici se forge l’art discret de prendre soin. Ta rigueur ici est la condition de ta liberté ailleurs.",
    'house_7': "Maison VII — Les autres, le miroir, les partenariats. Ce que tu rencontres chez l’autre te révèle ce que tu portes toi-même. Chaque relation significative est un enseignement déguisé.",
    'house_8': "Maison VIII — Les transformations profondes, les tabous, l’intimité, les ressources partagées. C’est la chambre des métamorphoses — on n’en sort jamais tout à fait pareille à celle qui y est entrée.",
    'house_9': "Maison IX — L’horizon et le sens, les grands voyages, la philosophie, la foi. Ici tu cherches le pourquoi derrière le comment, l’infini derrière le fini. C’est ta boussole intérieure.",
    'house_10': "Maison X — Ta vocation publique, ta signature professionnelle, la place que tu occupes dans la cité. Ce n’est pas forcément un métier : c’est la couleur que tu laisses dans la mémoire collective.",
    'house_11': "Maison XI — La tribu choisie, les amitiés électives, les projets collectifs. C’est le cercle de celles et ceux qui marchent dans la même direction que toi, même par des chemins différents.",
    'house_12': "Maison XII — Le sanctuaire intérieur, l’invisible, les rêves, les retraites. Ici réside la part de toi qui n’appartient qu’à toi — et parfois pas même à toi mais à plus grand que toi.",
    'year_ahead': "L’année qui vient ouvre un cycle de Jupiter nouveau pour toi — la porte s’entrouvre là où tu insistes depuis des mois. C’est une saison d’expansion mesurée : non pas une explosion mais un épanouissement patient. Tu récolteras ce que tu as semé en silence durant les saisons précédentes. Attends-toi à des rencontres déterminantes, à des propositions qui te feront douter tant elles dépassent ce que tu croyais mériter — accepte-les tout de même. Les transits de Saturne, en parallèle, te demanderont de choisir : certaines fidélités anciennes devront être revisitées, certains engagements renouvelés plus consciemment. Ce n’est pas une année facile mais une année juste — celle où ta vérité intérieure et ta vie extérieure commencent enfin à s’aligner. Garde une pratique régulière de retour à toi : journal, marche, silence. Elle sera ta boussole dans les décisions importantes qui ponctueront les douze mois.",
    'cloture_body': "Ce livre n’est pas une fin, c’est un seuil. Tu peux y revenir à toute saison, aux heures claires comme aux heures troubles. Les planètes ne cessent de parler — à toi désormais d’écouter avec l’oreille affûtée qui s’est aiguisée page après page. Souviens-toi : ton ciel n’est pas un destin fixé, c’est une partition. Et la musicienne, c’est toi.",
}

if __name__ == '__main__':
    pdf_bytes = build_natal_pdf_v2(
        prenom='Clara',
        birth_date='1992-07-14',
        natal_data=NATAL_DATA,
        chart_png_bytes=None,
        book_data=BOOK_DATA,
        referral_code='PLUME-CLARA-25',
        referral_link='https://plume-astrale.fr/parrainage/PLUME-CLARA-25',
    )
    out = '/app/sample_natal_lot1.pdf'
    with open(out, 'wb') as f:
        f.write(pdf_bytes)
    print(f'OK ({len(pdf_bytes)/1024:.1f} KB) → {out}')
