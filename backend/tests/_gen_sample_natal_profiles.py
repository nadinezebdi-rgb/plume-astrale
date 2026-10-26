"""Génère les 4 profils de test demandés par la spec Feb 2026 :
  1. avec heure de naissance
  2. sans heure de naissance
  3. prénom long / nom composé
  4. profil avec enrichissement chapitres additionnels

Pour chaque profil : run QA + sauvegarde PDF + sauvegarde rapport JSON.
Usage : cd /app/backend && python tests/_gen_sample_natal_profiles.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, '/app/backend')

from services.natal_pdf_v2 import build_natal_pdf_v2
from services.natal_pdf_qa import qa_check_natal_pdf
from services.pdf_strip_blanks import strip_blank_pages

OUTPUT_DIR = Path('/app/sample_preview/qa_profiles')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Dataset riche réutilisable ────────────────────────────────────
PLANETS_RICH = [
    {'name': 'Soleil', 'sign': 'Cancer',
     'analysis': 'Tu portes la sensibilité du Cancer avec une profondeur rare. '
                 'Ton rapport au foyer et à la mémoire est viscéral. Ce qui te distingue : '
                 'une capacité à sentir ce que les autres n’osent dire.\n\n'
                 'Tu es un refuge sans le savoir, et ta force s’exprime dans l’attention aux détails. '
                 'Ta créativité se nourrit des émotions, des souvenirs, des atmosphères familières. '
                 'Tu avances rarement en ligne droite : tu suis les courants, tu ressens les marées intérieures, '
                 'tu reconnais les saisons de l’âme. Cette sensibilité est ta signature.'},
    {'name': 'Lune', 'sign': 'Poissons',
     'analysis': 'Lune en Poissons : tes émotions circulent sans frontière. Tu absorbes ce qui t’entoure '
                 'comme une éponge sensible. Ton besoin fondamental : des espaces de silence pour redevenir toi. '
                 'Les Poissons apportent une empathie quasi-médiumnique : tu lis les non-dits, tu devines les secrets. '
                 'Attention à ne pas te perdre dans les émotions des autres — apprends à distinguer ta musique intérieure.'},
    {'name': 'Mercure', 'sign': 'Cancer',
     'analysis': 'Mercure en Cancer : tu penses avec le cœur avant la raison. Tes mots sont teintés d’affect '
                 'et d’intuition. Tu te souviens des mots que les autres oublient. '
                 'Ta parole porte, car elle est tissée de vécu. Tu es une conteuse-née, une archiviste de l’intime.'},
    {'name': 'Vénus', 'sign': 'Lion',
     'analysis': 'Vénus en Lion : tu aimes avec panache. Ton amour est théâtral mais sincère. '
                 'Tu veux être vue, pas simplement acceptée. Tu offres beaucoup, mais tu attends la reconnaissance. '
                 'Ce n’est pas de l’orgueil, c’est de la justice : tu donnes et tu veux savoir que c’est reçu.'},
    {'name': 'Mars', 'sign': 'Taureau',
     'analysis': 'Mars en Taureau : ton action est lente mais inarrêtable. Tu construis dans la patience. '
                 'Tu ne te précipites jamais, mais une fois lancée tu ne lâches pas. Cette endurance est ton arme.'},
    {'name': 'Jupiter', 'sign': 'Scorpion',
     'analysis': 'Jupiter en Scorpion : tu grandis dans l’intensité et les transformations profondes. '
                 'Les crises sont tes meilleurs maîtres. Chaque mue te révèle une version plus puissante de toi.'},
    {'name': 'Saturne', 'sign': 'Verseau',
     'analysis': 'Saturne en Verseau : ta discipline s’apprend par l’indépendance. '
                 'Tu refuses les cadres imposés, mais tu construis les tiens avec rigueur. Ta liberté est travaillée.'},
    {'name': 'Uranus', 'sign': 'Capricorne',
     'analysis': 'Uranus en Capricorne : tu portes une rébellion méthodique. '
                 'Tu bouscules les institutions sans les détruire — tu les transformes de l’intérieur.'},
    {'name': 'Neptune', 'sign': 'Capricorne',
     'analysis': 'Neptune en Capricorne : ton imaginaire s’ancre dans le concret. '
                 'Tu rêves pour bâtir, pas pour fuir. C’est une qualité rare, précieuse, à cultiver.'},
    {'name': 'Pluton', 'sign': 'Scorpion',
     'analysis': 'Pluton en Scorpion : tu traverses des morts symboliques pour renaître plus forte. '
                 'Ta puissance intérieure est magnétique — les gens le sentent sans comprendre pourquoi.'},
    {'name': 'Ascendant', 'sign': 'Vierge',
     'analysis': 'Ascendant Vierge : tu abordes le monde avec clarté, précision, discernement. '
                 'On te perçoit d’abord comme réservée, puis on découvre ta profondeur. Ta modestie cache un empire intérieur.'},
]


def _book_data(dom_element='Eau', dom_modality='Fixe'):
    return {
        '_source': 'cache',
        '_em': {
            'dominant_element': dom_element, 'dominant_element_count': 5,
            'dominant_modality': dom_modality, 'dominant_modality_count': 4,
        },
        'dedication': ('À toi qui ouvres ce livre, puisse-t-il devenir compagnon des heures '
                       'claires et des heures troubles.'),
        'element_analysis': ("Ton eau domine : tu te meus dans un monde d’impressions avant les mots. "
                             "C’est une richesse rare — et une invitation à poser des berges autour de "
                             "ta sensibilité pour ne pas te laisser submerger. Cette prédominance aquatique "
                             "t’offre une mémoire émotionnelle longue, où chaque rencontre laisse une empreinte. "
                             "Tu perçois les atmosphères avant que les paroles ne soient prononcées."),
        'modality_analysis': ("Ta modalité fixe te donne une colonne vertébrale. Tu tiens là où d’autres "
                              "plient. Attention cependant au prix de l’obstination — parfois, ce que tu "
                              "nommes fidélité est en réalité une peur du changement déguisée."),
        'trio_synthesis': ("Ton Soleil Cancer, ta Lune Poissons et ton Ascendant Vierge forment un dialogue "
                           "entre la mer et la rive. L’émotion fluide trouve dans la Vierge sa structure. "
                           "Tu ne te noies jamais complètement parce qu’une part de toi observe, analyse, trie."),
        'aspects_harmonieux_headline': 'La grâce en toi',
        'aspects_harmonieux_body': ("Tes trigones et sextiles ouvrent des zones de fluidité où tout circule "
                                    "sans effort. Ce sont les talents que tu n’as pas eu besoin d’apprendre : "
                                    "la justesse émotionnelle, le sens du soin, l’intuition créative."),
        'aspects_tensions_headline': 'Le nœud qui te forge',
        'aspects_tensions_body': ("Tes carrés et oppositions te confrontent — ils sont tes meilleurs maîtres. "
                                  "Chaque friction intérieure t’oblige à inventer, à créer un troisième chemin."),
        'rare_aspect_headline': 'Ta note rare',
        'rare_aspect_body': ("Il existe dans ton ciel une signature peu commune, qui te singularise. "
                             "Elle ne te rend pas supérieure, elle te rend reconnaissable. Cette note rare "
                             "est le filigrane de ton œuvre."),
        'houses_intro': ("Les douze maisons sont les terrains où tes planètes s’incarnent dans ta vie quotidienne. "
                         "Elles traduisent l’énergie céleste en expérience vécue."),
        'house_1': 'Maison I — Ta présence dans le monde. C’est l’enveloppe que tu offres aux autres, '
                   'la première impression que tu laisses, la silhouette que ton corps dessine dans l’espace.',
        'house_2': 'Maison II — Tes ressources matérielles et ton rapport à la valeur. Argent, biens, '
                   'talents monnayables : tout cela te parle moins du compte en banque que de l’estime que tu te portes.',
        'house_3': 'Maison III — Ton esprit vif, tes mots, tes trajets quotidiens, tes frères et sœurs d’âme.',
        'house_4': 'Maison IV — Ton foyer intérieur, tes racines, ta lignée. C’est la fondation invisible '
                   'sur laquelle tout le reste s’élève.',
        'house_5': 'Maison V — Tes créations, tes amours, tes enfants intérieurs. C’est le lieu du jeu sacré.',
        'house_6': 'Maison VI — Ton quotidien et ton artisanat de soi. Santé, routines, service rendu.',
        'house_7': 'Maison VII — Les autres, le miroir, les partenariats. Ce que tu rencontres chez l’autre '
                   'te révèle ce que tu portes toi-même.',
        'house_8': 'Maison VIII — Les transformations profondes, les tabous, l’intimité, les ressources partagées.',
        'house_9': 'Maison IX — L’horizon et le sens, les grands voyages, la philosophie, la foi.',
        'house_10': 'Maison X — Ta vocation publique, ta signature professionnelle, la place que tu occupes.',
        'house_11': 'Maison XI — La tribu choisie, les amitiés électives, les projets collectifs.',
        'house_12': 'Maison XII — Le sanctuaire intérieur, l’invisible, les rêves, les retraites.',
        'year_ahead': ("L’année qui vient ouvre un cycle de Jupiter nouveau pour toi — la porte s’entrouvre "
                       "là où tu insistes depuis des mois. C’est une saison d’expansion mesurée : non pas une "
                       "explosion mais un épanouissement patient. Tu récolteras ce que tu as semé en silence "
                       "durant les saisons précédentes. Attends-toi à des rencontres déterminantes, à des "
                       "propositions qui te feront douter tant elles dépassent ce que tu croyais mériter — "
                       "accepte-les tout de même. Les transits de Saturne, en parallèle, te demanderont "
                       "de choisir : certaines fidélités anciennes devront être revisitées, certains engagements "
                       "renouvelés plus consciemment. Ce n’est pas une année facile mais une année juste — celle "
                       "où ta vérité intérieure et ta vie extérieure commencent enfin à s’aligner. Garde une "
                       "pratique régulière de retour à toi : journal, marche, silence. Elle sera ta boussole "
                       "dans les décisions importantes qui ponctueront les douze mois à venir."),
    }


PROFILES = [
    {
        'id': 'profile_1_avec_heure',
        'label': 'Avec heure de naissance (Clara, Cancer, Vierge Asc)',
        'prenom': 'Clara',
        'birth_date': '1992-07-14',
        'natal_data': {
            'sun_sign': 'Cancer', 'moon_sign': 'Poissons', 'ascendant_sign': 'Vierge',
            'no_birth_time': False, 'tier': 'ultra',
            'birth_time': '14h30', 'birth_place': 'Paris',
            'planets': PLANETS_RICH,
            'synthese_aspects': 'Tes aspects dessinent un portrait de profondeur et de réserve.',
            'houses': [{'num': i, 'sign': 'Vierge', 'planets_in_house': []} for i in range(1, 13)],
            'enhanced_personal_analysis': {},
        },
        'book_data': _book_data(),
        'mode': 'rich',
    },
    {
        'id': 'profile_2_sans_heure',
        'label': 'Sans heure de naissance (édition Planètes)',
        'prenom': 'Marie',
        'birth_date': '1988-03-21',
        'natal_data': {
            'sun_sign': 'Bélier', 'moon_sign': 'Taureau', 'ascendant_sign': '',
            'no_birth_time': True, 'tier': 'ultra',
            'planets': [p for p in PLANETS_RICH if p['name'] != 'Ascendant'],
            'synthese_aspects': 'Aspects riches, dynamique Bélier/Taureau.',
            'houses': [],
            'enhanced_personal_analysis': {},
        },
        'book_data': None,  # pas de livre riche sans heure
        'mode': 'planets',
    },
    {
        'id': 'profile_3_prenom_long',
        'label': 'Prénom composé long',
        'prenom': 'Marie-Alexandrine du Chastelier',
        'birth_date': '1995-11-02',
        'natal_data': {
            'sun_sign': 'Scorpion', 'moon_sign': 'Vierge', 'ascendant_sign': 'Lion',
            'no_birth_time': False, 'tier': 'ultra',
            'birth_time': '03h45', 'birth_place': 'Marseille',
            'planets': [{**p, 'sign': 'Scorpion' if p['name'] == 'Soleil' else p['sign']}
                        for p in PLANETS_RICH],
            'synthese_aspects': 'Trine Pluton-Soleil : grande transformation intérieure.',
            'houses': [{'num': i, 'sign': 'Lion', 'planets_in_house': []} for i in range(1, 13)],
            'enhanced_personal_analysis': {},
        },
        'book_data': _book_data(dom_element='Feu', dom_modality='Mutable'),
        'mode': 'rich',
    },
    {
        'id': 'profile_4_tier_ultra_enrichi',
        'label': 'Thème Natal Ultra avec enrichissement complet',
        'prenom': 'Alix',
        'birth_date': '1990-05-15',
        'natal_data': {
            'sun_sign': 'Taureau', 'moon_sign': 'Capricorne', 'ascendant_sign': 'Capricorne',
            'no_birth_time': False, 'tier': 'ultra',
            'birth_time': '10h20', 'birth_place': 'Lyon',
            'planets': PLANETS_RICH,
            'synthese_aspects': 'Grand trigone de terre : stabilité remarquable.',
            'houses': [{'num': i, 'sign': 'Capricorne', 'planets_in_house': []} for i in range(1, 13)],
            'enhanced_personal_analysis': {
                'lunar_phase': {'phase_name': 'waxing_gibbous', 'illumination_percent': 72, 'moon_age_days': 10},
            },
        },
        'book_data': _book_data(dom_element='Terre', dom_modality='Cardinale'),
        'mode': 'rich',
    },
]


def main() -> None:
    print(f'Génération des 4 profils de test → {OUTPUT_DIR}\n')
    results = []
    for p in PROFILES:
        print(f'─── {p["id"]} : {p["label"]} ───')
        pdf = build_natal_pdf_v2(
            prenom=p['prenom'],
            birth_date=p['birth_date'],
            natal_data=p['natal_data'],
            book_data=p['book_data'],
        )
        pdf = strip_blank_pages(pdf)
        out = OUTPUT_DIR / f'{p["id"]}.pdf'
        out.write_bytes(pdf)
        # QA
        r = qa_check_natal_pdf(pdf, prenom=p['prenom'], mode=p['mode'])
        rpt = r.to_dict()
        (OUTPUT_DIR / f'{p["id"]}_qa.json').write_text(
            json.dumps(rpt, indent=2, ensure_ascii=False), encoding='utf-8')
        status = '✓ PASS' if r.passed else '✗ FAIL'
        print(f'  {status} — {rpt["page_count"]} pages, {rpt["word_count"]} mots, '
              f'{len(rpt["blank_pages"])} vides, {len(rpt["low_density_pages"])} sous-remplies')
        for issue in rpt['blocking_issues']:
            print(f'    ! {issue}')
        results.append({'id': p['id'], 'passed': r.passed, **rpt})
    # Synthèse globale
    (OUTPUT_DIR / 'all_qa.json').write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'\n→ Rapports JSON et PDFs dans {OUTPUT_DIR}')


if __name__ == '__main__':
    main()
