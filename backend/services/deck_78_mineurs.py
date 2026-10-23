"""
Deck 78 cartes — Arcanes Mineurs (56 cartes) du Tarot de Marseille.

Les 22 Arcanes Majeurs sont déjà définis dans `tarot_premium.ARCANES_MAJEURS`
(peints à la main, visuels Supabase). Les Mineurs sont servis ici en format
texte seul : nom FR, mots-clés, interprétations droit/renversé par domaine.

Les significations suivent le Tarot de Marseille classique (Wirth / Jodorowsky
simplifié). L'IA (`enrich_narrative.enrich_and_ask`) les rallonge à la volée.
"""
from __future__ import annotations
from typing import Dict, List

# ──────────────────────────────────────────────────────────────────────
# Les 4 suites (couleurs) du Tarot de Marseille
# ──────────────────────────────────────────────────────────────────────

SUITES: Dict[str, Dict[str, str]] = {
    'coupes': {
        'nom': 'Coupes',   'element': 'Eau',    'planete': 'Lune',
        'theme': 'Émotions, amour, relations, intuition, vie intérieure',
        'couleur': '#7DD3FC', 'symbole': '♥',
    },
    'deniers': {
        'nom': 'Deniers',  'element': 'Terre',  'planete': 'Vénus',
        'theme': 'Matière, finances, travail, santé, ancrage',
        'couleur': '#D4A574', 'symbole': '◆',
    },
    'epees': {
        'nom': 'Épées',    'element': 'Air',    'planete': 'Mercure',
        'theme': 'Pensée, parole, décisions, conflits, vérité',
        'couleur': '#B8A9E8', 'symbole': '✦',
    },
    'batons': {
        'nom': 'Bâtons',   'element': 'Feu',    'planete': 'Mars',
        'theme': 'Action, passion, créativité, projets, élan',
        'couleur': '#F4845F', 'symbole': '✧',
    },
}

# ──────────────────────────────────────────────────────────────────────
# 10 rangs numériques (1 = As, 2-10) + 4 figures (Valet, Cavalier, Reine, Roi)
# Chaque rang a sa signification de base, qu'on adapte au thème de la suite.
# ──────────────────────────────────────────────────────────────────────

RANGS: Dict[int, Dict[str, str]] = {
    1:  {'nom': 'As',       'mots': ['germe', 'commencement', 'potentiel pur']},
    2:  {'nom': 'Deux',     'mots': ['dualité', 'choix', 'équilibre']},
    3:  {'nom': 'Trois',    'mots': ['création', 'fécondité', 'première récolte']},
    4:  {'nom': 'Quatre',   'mots': ['stabilité', 'structure', 'pause']},
    5:  {'nom': 'Cinq',     'mots': ['épreuve', 'remise en question', 'bascule']},
    6:  {'nom': 'Six',      'mots': ['harmonie', 'victoire', 'partage']},
    7:  {'nom': 'Sept',     'mots': ['passage', 'réflexion', 'épreuve initiatique']},
    8:  {'nom': 'Huit',     'mots': ['travail', 'régulation', 'maîtrise technique']},
    9:  {'nom': 'Neuf',     'mots': ['solitude féconde', 'maturation', 'sagesse']},
    10: {'nom': 'Dix',      'mots': ['accomplissement', 'cycle terminé', 'ouverture']},
    11: {'nom': 'Valet',    'mots': ['messager', 'apprentissage', 'enfance']},
    12: {'nom': 'Cavalier', 'mots': ['mouvement', 'quête', 'adolescence']},
    13: {'nom': 'Reine',    'mots': ['réceptivité', 'incarnation féminine', 'maturité']},
    14: {'nom': 'Roi',      'mots': ['autorité', 'incarnation masculine', 'souveraineté']},
}

# ──────────────────────────────────────────────────────────────────────
# Interprétations croisées (rang × suite) — droit + renversé + conseil
# ──────────────────────────────────────────────────────────────────────

_INTERP: Dict[tuple, Dict[str, Dict[str, str]]] = {
    # ─────────── COUPES (Eau — émotions) ───────────
    (1, 'coupes'): {
        'droit': {'general': "L'amour nouveau afflue. Une émotion neuve, un coup de cœur, un cœur qui s'ouvre.",
                   'amour': "Une rencontre bouleversante ou un renouveau profond du cœur.",
                   'travail': "Un projet qui vous passionne arrive : écoutez vos émotions, pas vos peurs.",
                   'conseil': "Accueillez cette émotion sans vouloir la contenir — elle est votre boussole."},
        'renverse': {'general': "Cœur fermé ou blessé, difficulté à ressentir vraiment.",
                      'amour': "Déception amoureuse à digérer, ou peur de s'engager.",
                      'travail': "Désamour pour ce que vous faites ; cherchez où est votre vraie joie.",
                      'conseil': "Laissez le trop-plein s'écouler avant d'attendre d'être rempli à nouveau."}
    },
    (2, 'coupes'): {
        'droit': {'general': "Union, lien d'âme à âme, réconciliation.",
                   'amour': "Mariage, pacte amoureux, deux cœurs qui se trouvent.",
                   'travail': "Collaboration fluide, partenariat équilibré.",
                   'conseil': "Dites oui à ce lien, il vous grandit tous les deux."},
        'renverse': {'general': "Lien déséquilibré, promesse non tenue, miroir brisé.",
                      'amour': "Rupture ou tension dans le couple ; qui donne, qui reçoit ?",
                      'travail': "Associé peu fiable, promesse qui tarde à se concrétiser.",
                      'conseil': "Reparlez clairement — ou éloignez-vous un temps."}
    },
    (3, 'coupes'): {
        'droit': {'general': "Fête, amitié, célébration d'une joie partagée.",
                   'amour': "Entouré(e) par ceux qui vous aiment, bonheur simple.",
                   'travail': "Succès partagé, équipe soudée.",
                   'conseil': "Dansez cette joie — elle est méritée."},
        'renverse': {'general': "Excès, superficialité, dispersion.",
                      'amour': "Trop de monde autour, intimité qui manque.",
                      'travail': "Fête trop vite déclarée, mal gérée.",
                      'conseil': "Revenez à l'essentiel, protégez l'intime."}
    },
    (4, 'coupes'): {
        'droit': {'general': "Lassitude, saturation, besoin de recul.",
                   'amour': "Routine, lassitude amoureuse à nommer.",
                   'travail': "Fatigue, ennui, il manque un sens.",
                   'conseil': "Prenez du recul avant de décider."},
        'renverse': {'general': "L'énergie remonte, la motivation revient.",
                      'amour': "Vous reconnectez à ce qui vous fait vibrer.",
                      'travail': "Un nouveau souffle, une offre inattendue.",
                      'conseil': "Dites oui à cette main qui se tend."}
    },
    (5, 'coupes'): {
        'droit': {'general': "Deuil, regret, ce qui est parti ne reviendra pas.",
                   'amour': "Rupture, séparation, chagrin à honorer.",
                   'travail': "Projet perdu, échec à digérer.",
                   'conseil': "Pleurez ce qui doit l'être — puis regardez ce qu'il reste."},
        'renverse': {'general': "Vous relevez la tête, la peine se transforme en force.",
                      'amour': "Pardon offert ou reçu, chapitre refermé.",
                      'travail': "Rebond, nouvelle piste.",
                      'conseil': "Avancez, l'horizon s'éclaircit."}
    },
    (6, 'coupes'): {
        'droit': {'general': "Souvenirs doux, enfance, nostalgie bienveillante.",
                   'amour': "Un amour du passé réapparaît, ou l'innocence retrouvée.",
                   'travail': "Retour à une activité qui vous plaisait enfant.",
                   'conseil': "Honorez cette tendresse sans vous y perdre."},
        'renverse': {'general': "Enfermement dans le passé, nostalgie qui paralyse.",
                      'amour': "Fantôme d'ex, idéalisation.",
                      'travail': "Peur de grandir, de prendre vos responsabilités.",
                      'conseil': "Le passé est un socle, pas une prison."}
    },
    (7, 'coupes'): {
        'droit': {'general': "Rêves, visions, imagination fertile.",
                   'amour': "Un amour idéalisé, attention à ne pas rêver trop loin.",
                   'travail': "Beaucoup de projets, peu de focus.",
                   'conseil': "Choisissez UN rêve et donnez-lui corps."},
        'renverse': {'general': "Illusions brisées, retour au réel.",
                      'amour': "Vous voyez enfin l'autre tel qu'il est.",
                      'travail': "Fin d'une chimère, place à l'action concrète.",
                      'conseil': "Le réel n'est pas une défaite, c'est un cadeau."}
    },
    (8, 'coupes'): {
        'droit': {'general': "Vous partez, vous laissez derrière ce qui ne vous nourrit plus.",
                   'amour': "Départ, abandon d'un lien devenu stérile.",
                   'travail': "Démission, départ vers un ailleurs plus juste.",
                   'conseil': "Partir n'est pas fuir — c'est se choisir."},
        'renverse': {'general': "Vous restez par peur, alors que tout vous dit de partir.",
                      'amour': "Vous êtes dans une relation que vous n'habitez plus.",
                      'travail': "Travail qui vide, mais que vous gardez par sécurité.",
                      'conseil': "Posez-vous la vraie question : qu'est-ce que je protège vraiment ?"}
    },
    (9, 'coupes'): {
        'droit': {'general': "Vœu exaucé, satisfaction profonde, abondance émotionnelle.",
                   'amour': "Amour plein, cœur comblé.",
                   'travail': "Reconnaissance, prime, projet qui aboutit.",
                   'conseil': "Savourez — vous avez le droit d'être heureuse."},
        'renverse': {'general': "Vœu différé, satisfaction égoïste.",
                      'amour': "Vous attendez de l'autre ce que vous ne vous donnez pas.",
                      'travail': "Succès qui laisse un goût amer.",
                      'conseil': "Commencez par vous combler vous-même."}
    },
    (10, 'coupes'): {
        'droit': {'general': "Famille unie, bonheur paisible, foyer rayonnant.",
                   'amour': "Couple heureux, projet de famille, harmonie durable.",
                   'travail': "Équipe comme une famille, lieu où vous vous sentez chez vous.",
                   'conseil': "C'est votre vraie place — protégez-la."},
        'renverse': {'general': "Tensions familiales, foyer dissonant.",
                      'amour': "Désaccords sur les valeurs profondes.",
                      'travail': "Mauvaise ambiance, besoin de changer de tribu.",
                      'conseil': "Soignez les liens — ou osez les redessiner."}
    },
    (11, 'coupes'): {
        'droit': {'general': "Nouvelle émotionnelle, message tendre, invitation du cœur.",
                   'amour': "Déclaration, lettre, SMS qui change la donne.",
                   'travail': "Proposition créative, idée artistique.",
                   'conseil': "Ouvrez la lettre — elle vous attend depuis longtemps."},
        'renverse': {'general': "Nouvelle qui déçoit, message mal interprété.",
                      'amour': "Promesse creuse, flirt sans suite.",
                      'travail': "Projet artistique mal lancé.",
                      'conseil': "Vérifiez l'intention avant de vous enthousiasmer."}
    },
    (12, 'coupes'): {
        'droit': {'general': "Quête amoureuse, offrande, romantisme en mouvement.",
                   'amour': "Rencontre amoureuse qui vient à vous.",
                   'travail': "Projet artistique qui chemine.",
                   'conseil': "Avancez — mais sans vous perdre dans l'autre."},
        'renverse': {'general': "Fuite émotionnelle, promesses sans action.",
                      'amour': "Il/elle parle beaucoup, agit peu.",
                      'travail': "Vous rêvez votre projet au lieu de le faire.",
                      'conseil': "La parole doit se poser quelque part."}
    },
    (13, 'coupes'): {
        'droit': {'general': "Femme intuitive, cœur sage, écoute profonde.",
                   'amour': "Partenaire tendre, émotionnellement disponible.",
                   'travail': "Mentor ou alliée bienveillante.",
                   'conseil': "Fiez-vous à votre intuition — elle a raison."},
        'renverse': {'general': "Émotion débordante, dépendance affective.",
                      'amour': "Jalousie, possessivité.",
                      'travail': "Difficulté à mettre des limites.",
                      'conseil': "Protégez votre monde intérieur."}
    },
    (14, 'coupes'): {
        'droit': {'general': "Homme sensible, pouvoir émotionnel maîtrisé, charisme tranquille.",
                   'amour': "Partenaire mature, qui aime sans peur.",
                   'travail': "Leader humain, patron juste.",
                   'conseil': "Soyez souverain(e) de vos émotions sans les étouffer."},
        'renverse': {'general': "Froideur, manipulation émotionnelle.",
                      'amour': "Partenaire fuyant, amour cérébral.",
                      'travail': "Chef distant, décisions prises sans écoute.",
                      'conseil': "Ne confondez pas maîtrise et répression."}
    },
    # ─────────── DENIERS (Terre — matière) ───────────
    (1, 'deniers'): {
        'droit': {'general': "Opportunité matérielle, graine d'abondance, nouvelle entrée d'argent.",
                   'amour': "Base solide pour une relation durable.",
                   'travail': "Offre concrète, promotion, projet rentable qui démarre.",
                   'conseil': "Saisissez — mais plantez-la, ne la gaspillez pas."},
        'renverse': {'general': "Opportunité manquée, mauvais placement.",
                      'amour': "Attirance basée sur l'intérêt matériel.",
                      'travail': "Projet qui s'enlise par manque de moyens.",
                      'conseil': "Attendez un meilleur terrain avant de semer."}
    },
    (2, 'deniers'): {
        'droit': {'general': "Jonglerie, adaptation, deux projets en parallèle.",
                   'amour': "Hésitation entre deux personnes, ou vie à distance.",
                   'travail': "Deux missions, besoin d'organisation.",
                   'conseil': "Dansez avec les flux — vous êtes plus souple que vous ne croyez."},
        'renverse': {'general': "Déséquilibre, surcharge, chute si vous continuez à tout porter.",
                      'amour': "Vous ne pouvez plus mentir à l'un ou l'autre.",
                      'travail': "Burn-out en vue si vous ne tranchez pas.",
                      'conseil': "Lâchez une balle — vous ne pouvez pas tout tenir."}
    },
    (3, 'deniers'): {
        'droit': {'general': "Travail d'équipe, compétence reconnue, mise en œuvre concrète.",
                   'amour': "Projet construit à deux, maison, enfant.",
                   'travail': "Vos compétences sont vues et payées.",
                   'conseil': "Montrez votre travail — il mérite d'être vu."},
        'renverse': {'general': "Mauvaise coordination, travail mal fait, dévalorisation.",
                      'amour': "Un des deux porte seul la relation.",
                      'travail': "On s'approprie votre travail.",
                      'conseil': "Posez-vous : avec qui est-ce que je construis vraiment ?"}
    },
    (4, 'deniers'): {
        'droit': {'general': "Épargne, sécurité, patrimoine qui se construit.",
                   'amour': "Couple stable, parfois un peu trop prudent.",
                   'travail': "CDI, sécurité financière.",
                   'conseil': "Protégez — mais ne vous enfermez pas dans un coffre."},
        'renverse': {'general': "Avarice, blocage, peur de manquer qui paralyse.",
                      'amour': "Vous tenez l'autre trop serré.",
                      'travail': "Vous refusez une opportunité par peur du changement.",
                      'conseil': "L'argent gelé perd sa valeur. Faites-le circuler."}
    },
    (5, 'deniers'): {
        'droit': {'general': "Précarité, difficulté matérielle, période maigre.",
                   'amour': "Couple traverse une épreuve financière ou de santé.",
                   'travail': "Perte, baisse de revenus, doute profond.",
                   'conseil': "Demandez de l'aide — ce n'est pas une honte."},
        'renverse': {'general': "Sortie de crise, l'aide arrive, le vent tourne.",
                      'amour': "Vous retrouvez un équilibre matériel ensemble.",
                      'travail': "Nouveau contrat, embellie financière.",
                      'conseil': "L'épreuve vous a appris votre vraie force."}
    },
    (6, 'deniers'): {
        'droit': {'general': "Générosité, don juste, abondance partagée.",
                   'amour': "Équilibre dans les élans de chacun.",
                   'travail': "Prime, mentorat, échange gagnant-gagnant.",
                   'conseil': "Donnez — mais mesurez pour ne pas vous vider."},
        'renverse': {'general': "Déséquilibre dans l'échange, dette qui pèse.",
                      'amour': "Un donne tout, l'autre reçoit sans retour.",
                      'travail': "Vous êtes sous-payé(e) ou vous surpayez.",
                      'conseil': "Rééquilibrez — la gratitude ne doit pas remplacer la justice."}
    },
    (7, 'deniers'): {
        'droit': {'general': "Patience, récolte à venir, labeur qui porte fruit.",
                   'amour': "Relation qui mûrit dans la durée.",
                   'travail': "Projet lent mais sûr, investissement sur le long terme.",
                   'conseil': "Résistez à l'impatience — la récolte viendra."},
        'renverse': {'general': "Impatience, labeur stérile, mauvais placement.",
                      'amour': "Vous attendez un retour qui ne viendra pas.",
                      'travail': "Projet qui ne décolle pas malgré vos efforts.",
                      'conseil': "Changez de champ — celui-ci est épuisé."}
    },
    (8, 'deniers'): {
        'droit': {'general': "Apprentissage, maîtrise technique, travail d'orfèvre.",
                   'amour': "Vous apprenez à aimer avec soin, précision.",
                   'travail': "Formation, expertise qui se bâtit.",
                   'conseil': "Soyez l'artisan de votre vie — un détail à la fois."},
        'renverse': {'general': "Travail bâclé, perfectionnisme qui bloque.",
                      'amour': "Vous voulez trop bien faire et étouffez l'autre.",
                      'travail': "Procrastination par peur de mal faire.",
                      'conseil': "Fini vaut mieux que parfait."}
    },
    (9, 'deniers'): {
        'droit': {'general': "Autonomie, abondance personnelle, jardin fleuri.",
                   'amour': "Vous êtes bien seul(e) — l'autre viendra en bonus.",
                   'travail': "Indépendance financière, projet qui vous rend libre.",
                   'conseil': "Jouissez de ce que vous avez construit."},
        'renverse': {'general': "Solitude dorée mais stérile, luxe sans joie.",
                      'amour': "Vous attendez l'autre dans une tour d'ivoire.",
                      'travail': "Succès sans sens.",
                      'conseil': "L'abondance se partage, sinon elle se pétrifie."}
    },
    (10, 'deniers'): {
        'droit': {'general': "Patrimoine, héritage, abondance qui se transmet.",
                   'amour': "Famille au complet, projet qui engage les générations.",
                   'travail': "Entreprise familiale, succession heureuse.",
                   'conseil': "Vous êtes un chaînon — vénérez ceux d'avant, préparez ceux d'après."},
        'renverse': {'general': "Conflits d'héritage, patrimoine qui pèse.",
                      'amour': "Famille toxique qui s'immisce dans le couple.",
                      'travail': "Entreprise qui s'enlise dans la tradition.",
                      'conseil': "Osez couper si la transmission vous détruit."}
    },
    (11, 'deniers'): {
        'droit': {'general': "Message financier, bonne nouvelle, opportunité à étudier.",
                   'amour': "Nouvelle rencontre fiable, discrète mais sincère.",
                   'travail': "Petit boulot qui ouvre une grande porte.",
                   'conseil': "Étudiez l'offre — elle est plus solide qu'elle n'y paraît."},
        'renverse': {'general': "Mauvaise nouvelle financière, retard.",
                      'amour': "Rencontre superficielle.",
                      'travail': "Promesse d'embauche qui tarde.",
                      'conseil': "Vérifiez les engagements écrits."}
    },
    (12, 'deniers'): {
        'droit': {'general': "Travail méthodique, voyage utile, mise en œuvre lente mais sûre.",
                   'amour': "Partenaire fiable, qui construit dans la durée.",
                   'travail': "Chantier long, mission en déplacement.",
                   'conseil': "Faites un pas chaque jour — c'est ainsi qu'on avance loin."},
        'renverse': {'general': "Stagnation, routine, voyage qui n'arrive pas.",
                      'amour': "Routine qui éteint l'étincelle.",
                      'travail': "Projet immobile, démotivation.",
                      'conseil': "Secouez le quotidien — un détail suffit."}
    },
    (13, 'deniers'): {
        'droit': {'general': "Femme généreuse, gestionnaire, ancrée dans le réel.",
                   'amour': "Partenaire maternelle, nourrissante.",
                   'travail': "Patronne juste, gestionnaire avisée.",
                   'conseil': "Incarnez cette abondance tranquille."},
        'renverse': {'general': "Matérialisme, possessivité, étouffement.",
                      'amour': "Jalousie liée à la peur de perdre.",
                      'travail': "Gestion rigide, contrôle excessif.",
                      'conseil': "Lâchez prise — la vraie richesse circule."}
    },
    (14, 'deniers'): {
        'droit': {'general': "Homme solide, bâtisseur, succès patrimonial.",
                   'amour': "Partenaire fiable, prêt à construire.",
                   'travail': "Entrepreneur, chef d'entreprise, succès durable.",
                   'conseil': "Vous êtes votre propre fondation — tenez bon."},
        'renverse': {'general': "Rigidité, matérialisme, pouvoir qui écrase.",
                      'amour': "Partenaire autoritaire, qui achète l'amour.",
                      'travail': "Patron tyrannique, succès vide.",
                      'conseil': "La vraie souveraineté est sans violence."}
    },
    # ─────────── ÉPÉES (Air — pensée, parole) ───────────
    (1, 'epees'): {
        'droit': {'general': "Clarté, décision tranchée, vérité qui se lève.",
                   'amour': "Vous voyez enfin la situation telle qu'elle est.",
                   'travail': "Décision stratégique, idée géniale.",
                   'conseil': "Tranchez — la clarté vaut mieux que le confort."},
        'renverse': {'general': "Confusion, mensonge, vérité étouffée.",
                      'amour': "Non-dits qui empoisonnent.",
                      'travail': "Information cachée, décision biaisée.",
                      'conseil': "Cherchez l'angle mort — il y a quelque chose à dire."}
    },
    (2, 'epees'): {
        'droit': {'general': "Choix à faire, dilemme, équilibre fragile.",
                   'amour': "Hésitation profonde entre deux voies amoureuses.",
                   'travail': "Négociation délicate, armistice.",
                   'conseil': "Retirez le bandeau — regardez vraiment."},
        'renverse': {'general': "Impasse levée, décision prise.",
                      'amour': "Vous choisissez enfin.",
                      'travail': "La négociation aboutit.",
                      'conseil': "Félicitations — le choix était la seule issue."}
    },
    (3, 'epees'): {
        'droit': {'general': "Chagrin, blessure du cœur, trahison, séparation.",
                   'amour': "Rupture, infidélité, cœur brisé.",
                   'travail': "Trahison professionnelle, licenciement.",
                   'conseil': "Pleurez — la douleur nommée se transforme."},
        'renverse': {'general': "Guérison lente, pardon en chemin.",
                      'amour': "Vous commencez à vous relever.",
                      'travail': "Vous digérez l'injustice.",
                      'conseil': "La cicatrice sera votre force."}
    },
    (4, 'epees'): {
        'droit': {'general': "Repos, retraite, convalescence nécessaire.",
                   'amour': "Pause dans la relation, besoin de silence.",
                   'travail': "Arrêt maladie, vacances salvatrices.",
                   'conseil': "Dormez — c'est aussi un acte spirituel."},
        'renverse': {'general': "Reprise d'activité, retour au front.",
                      'amour': "Vous êtes prêt(e) à ré-aimer.",
                      'travail': "Retour en poste, nouvelle énergie.",
                      'conseil': "Reprenez — mais plus sage qu'avant."}
    },
    (5, 'epees'): {
        'droit': {'general': "Conflit, victoire amère, orgueil blessé.",
                   'amour': "Dispute, mots qui dépassent la pensée.",
                   'travail': "Lutte de pouvoir, victoire qui laisse seul(e).",
                   'conseil': "Est-ce vraiment une victoire si tout est détruit autour ?"},
        'renverse': {'general': "Réconciliation, apaisement.",
                      'amour': "Vous faites la paix.",
                      'travail': "Le conflit se résout.",
                      'conseil': "Faites le premier pas — c'est le plus courageux."}
    },
    (6, 'epees'): {
        'droit': {'general': "Traversée, voyage réparateur, passage d'une rive à l'autre.",
                   'amour': "Vous quittez une relation toxique vers plus de paix.",
                   'travail': "Changement de poste, déménagement professionnel.",
                   'conseil': "Partez — l'autre rive existe."},
        'renverse': {'general': "Voyage bloqué, retour en arrière.",
                      'amour': "Vous retournez vers l'ex, est-ce vraiment sage ?",
                      'travail': "Projet de départ qui échoue.",
                      'conseil': "Pourquoi reculer ? Qu'est-ce qui vous retient vraiment ?"}
    },
    (7, 'epees'): {
        'droit': {'general': "Stratégie, ruse, parfois mensonge nécessaire.",
                   'amour': "Jeu de séduction, non-dits stratégiques.",
                   'travail': "Négociation habile, parfois à la limite de l'éthique.",
                   'conseil': "La ruse n'est pas la sagesse. Visez juste."},
        'renverse': {'general': "Vérité qui éclate, masque qui tombe.",
                      'amour': "L'infidélité est découverte.",
                      'travail': "Fraude dévoilée.",
                      'conseil': "La transparence coûte cher mais libère."}
    },
    (8, 'epees'): {
        'droit': {'general': "Blocage mental, prison intérieure, impuissance perçue.",
                   'amour': "Vous vous sentez piégé(e) sans l'être vraiment.",
                   'travail': "Vous ne voyez plus les options possibles.",
                   'conseil': "Ouvrez les yeux — le bandeau est à vous de retirer."},
        'renverse': {'general': "Libération, vous reprenez votre pouvoir.",
                      'amour': "Vous reconnaissez votre valeur.",
                      'travail': "Vous osez enfin partir ou négocier.",
                      'conseil': "Vous n'avez jamais été vraiment prisonnier(ère)."}
    },
    (9, 'epees'): {
        'droit': {'general': "Angoisse, insomnie, cauchemars, culpabilité.",
                   'amour': "Jalousie dévorante, scénarios noirs.",
                   'travail': "Stress intense, peur de l'échec.",
                   'conseil': "Nommez la peur à voix haute — elle rétrécit."},
        'renverse': {'general': "L'angoisse se dissipe, le jour se lève.",
                      'amour': "Vous retrouvez la confiance.",
                      'travail': "Le stress baisse.",
                      'conseil': "Vous avez traversé la nuit — honorez votre courage."}
    },
    (10, 'epees'): {
        'droit': {'general': "Fin, chute, trahison ultime — mais la pire est passée.",
                   'amour': "Rupture définitive.",
                   'travail': "Licenciement, projet effondré.",
                   'conseil': "Touchez le fond — c'est là qu'on se repousse."},
        'renverse': {'general': "Reconstruction, renaissance.",
                      'amour': "Vous commencez à reconstruire.",
                      'travail': "Nouvelle vie professionnelle.",
                      'conseil': "L'aube arrive toujours. Préparez-vous."}
    },
    (11, 'epees'): {
        'droit': {'general': "Nouvelle, information, vigilance mentale.",
                   'amour': "Lettre inattendue, mail à bien lire.",
                   'travail': "Veille stratégique, email important.",
                   'conseil': "Soyez attentif(ve) aux détails."},
        'renverse': {'general': "Rumeur, information biaisée, commérage.",
                      'amour': "Jalousie fondée sur du vent.",
                      'travail': "Fuite d'info, bruit de couloir.",
                      'conseil': "Vérifiez avant de réagir."}
    },
    (12, 'epees'): {
        'droit': {'general': "Charge mentale rapide, débat, bataille d'idées.",
                   'amour': "Dispute vive mais fertile.",
                   'travail': "Projet qui s'emballe, décisions rapides.",
                   'conseil': "Avancez vite — mais pas sans réfléchir."},
        'renverse': {'general': "Précipitation, décisions regrettées.",
                      'amour': "Mots qui blessent, prononcés trop vite.",
                      'travail': "Erreur stratégique par impatience.",
                      'conseil': "Ralentissez — un battement de cœur avant de parler."}
    },
    (13, 'epees'): {
        'droit': {'general': "Femme lucide, intellect tranchant, justice.",
                   'amour': "Partenaire qui vous aime pour votre esprit.",
                   'travail': "Juriste, consultante, décideuse claire.",
                   'conseil': "Faites confiance à votre tranchant."},
        'renverse': {'general': "Froideur, cynisme, parole blessante.",
                      'amour': "Jugements durs qui épuisent.",
                      'travail': "Mode critique qui démotive.",
                      'conseil': "La vérité peut se dire avec douceur."}
    },
    (14, 'epees'): {
        'droit': {'general': "Homme stratège, autorité intellectuelle, justice.",
                   'amour': "Partenaire juste, honnête, parfois trop rationnel.",
                   'travail': "Décideur, juriste, dirigeant lucide.",
                   'conseil': "Tranchez — mais écoutez le cœur aussi."},
        'renverse': {'general': "Tyrannie intellectuelle, manipulation.",
                      'amour': "Partenaire qui domine par la parole.",
                      'travail': "Chef manipulateur.",
                      'conseil': "Ne confondez pas intelligence et violence."}
    },
    # ─────────── BÂTONS (Feu — action) ───────────
    (1, 'batons'): {
        'droit': {'general': "Élan créateur, inspiration, feu nouveau.",
                   'amour': "Désir qui s'allume, étincelle.",
                   'travail': "Idée brillante, lancement de projet.",
                   'conseil': "Agissez tant que le feu brûle."},
        'renverse': {'general': "Élan étouffé, inspiration bloquée.",
                      'amour': "Désir qui s'éteint.",
                      'travail': "Projet qui ne décolle pas.",
                      'conseil': "Ranimez le feu — ou acceptez qu'il soit fini."}
    },
    (2, 'batons'): {
        'droit': {'general': "Vision, décision stratégique, horizon large.",
                   'amour': "Choix entre sécurité et aventure.",
                   'travail': "Expansion, nouveau marché à explorer.",
                   'conseil': "Osez voir plus grand."},
        'renverse': {'general': "Hésitation, peur d'oser.",
                      'amour': "Vous restez au port par peur.",
                      'travail': "Projet d'expansion ajourné.",
                      'conseil': "Les grandes décisions se prennent avec le cœur serré."}
    },
    (3, 'batons'): {
        'droit': {'general': "Projets lancés, horizons qui s'ouvrent, attente féconde.",
                   'amour': "Relation qui s'épanouit.",
                   'travail': "Collaboration à l'international.",
                   'conseil': "Attendez — vos bateaux arrivent."},
        'renverse': {'general': "Projet qui tarde, patience à retrouver.",
                      'amour': "Relation à distance qui use.",
                      'travail': "Collaboration en pause.",
                      'conseil': "Occupez-vous — l'attente n'est pas vide."}
    },
    (4, 'batons'): {
        'droit': {'general': "Fête, mariage, foyer réussi.",
                   'amour': "Mariage, PACS, emménagement.",
                   'travail': "Succès célébré en équipe.",
                   'conseil': "Célébrez à voix haute."},
        'renverse': {'general': "Fête ratée, foyer en désordre.",
                      'amour': "Projet de mariage reporté.",
                      'travail': "Événement d'équipe raté.",
                      'conseil': "Posez les bases avant de célébrer."}
    },
    (5, 'batons'): {
        'droit': {'general': "Compétition, dispute créative, désaccord stimulant.",
                   'amour': "Tensions utiles qui font évoluer.",
                   'travail': "Compétition saine entre collègues.",
                   'conseil': "Le conflit n'est pas la fin — il fait grandir."},
        'renverse': {'general': "Querelle stérile, chaos.",
                      'amour': "Disputes qui tournent en rond.",
                      'travail': "Équipe en guerre interne.",
                      'conseil': "Posez les règles du jeu — ou sortez du jeu."}
    },
    (6, 'batons'): {
        'droit': {'general': "Victoire, reconnaissance publique, honneurs.",
                   'amour': "Couple reconnu, triomphe public.",
                   'travail': "Promotion, prix, succès célébré.",
                   'conseil': "Savourez — vous l'avez mérité."},
        'renverse': {'general': "Victoire différée, vanité.",
                      'amour': "Besoin de validation extérieure.",
                      'travail': "Succès contesté.",
                      'conseil': "Votre valeur n'attend pas d'être validée."}
    },
    (7, 'batons'): {
        'droit': {'general': "Résistance, défense de sa position, courage.",
                   'amour': "Vous défendez votre couple contre l'extérieur.",
                   'travail': "Vous tenez votre poste face à la pression.",
                   'conseil': "Tenez bon — vous avez raison."},
        'renverse': {'general': "Fatigue de combat, abandon.",
                      'amour': "Vous ne défendez plus votre couple.",
                      'travail': "Vous cédez face aux attaques.",
                      'conseil': "Récupérez — puis repartez au combat."}
    },
    (8, 'batons'): {
        'droit': {'general': "Mouvement rapide, nouvelles qui pleuvent, accélération.",
                   'amour': "Coup de foudre, événements rapides.",
                   'travail': "Projet qui s'accélère, voyage.",
                   'conseil': "Montez dans le train — il ne repassera pas."},
        'renverse': {'general': "Blocage, retards, lenteur frustrante.",
                      'amour': "Relation qui piétine.",
                      'travail': "Projet qui s'enlise.",
                      'conseil': "Patience — ou changez de train."}
    },
    (9, 'batons'): {
        'droit': {'general': "Résilience, dernière épreuve avant la paix.",
                   'amour': "Vous tenez face aux difficultés.",
                   'travail': "Dernier effort avant le succès.",
                   'conseil': "Ne lâchez pas si près du but."},
        'renverse': {'general': "Épuisement, lassitude profonde.",
                      'amour': "Couple à bout.",
                      'travail': "Burn-out imminent.",
                      'conseil': "Reposez-vous ou tout va s'écrouler."}
    },
    (10, 'batons'): {
        'droit': {'general': "Charge lourde mais portée, responsabilités assumées.",
                   'amour': "Vous portez la relation à bout de bras.",
                   'travail': "Trop sur les épaules — mais vous tenez.",
                   'conseil': "Déléguez — vous n'avez pas à tout porter."},
        'renverse': {'general': "Lâcher-prise, délestage.",
                      'amour': "Vous arrêtez de porter l'autre.",
                      'travail': "Vous apprenez à déléguer.",
                      'conseil': "Félicitations — vous respirez enfin."}
    },
    (11, 'batons'): {
        'droit': {'general': "Nouvelle enthousiaste, inspiration, aventure.",
                   'amour': "Flirt audacieux, rencontre énergique.",
                   'travail': "Opportunité créative.",
                   'conseil': "Dites oui à cette étincelle."},
        'renverse': {'general': "Nouvelle décevante, feu de paille.",
                      'amour': "Flirt sans profondeur.",
                      'travail': "Projet mal lancé.",
                      'conseil': "Vérifiez la solidité avant de courir."}
    },
    (12, 'batons'): {
        'droit': {'general': "Voyage, aventure, projet qui prend son envol.",
                   'amour': "Rencontre lors d'un voyage, relation vive.",
                   'travail': "Mission à l'étranger, projet en expansion.",
                   'conseil': "Partez — l'aventure vous attend."},
        'renverse': {'general': "Précipitation, imprudence.",
                      'amour': "Coup de tête amoureux à regretter.",
                      'travail': "Décision précipitée.",
                      'conseil': "Prenez un battement de cœur avant d'agir."}
    },
    (13, 'batons'): {
        'droit': {'general': "Femme passionnée, créatrice, charismatique.",
                   'amour': "Partenaire vive, inspirante.",
                   'travail': "Leader créative, entrepreneuse.",
                   'conseil': "Embrasez votre monde."},
        'renverse': {'general': "Jalousie, caprice, passion destructrice.",
                      'amour': "Scènes dramatiques.",
                      'travail': "Caprices de direction.",
                      'conseil': "Transformez le feu avant qu'il ne brûle tout."}
    },
    (14, 'batons'): {
        'droit': {'general': "Homme charismatique, bâtisseur de vision.",
                   'amour': "Partenaire inspirant, qui pousse à grandir.",
                   'travail': "Leader visionnaire, entrepreneur.",
                   'conseil': "Soyez le phare — mais ne brûlez personne."},
        'renverse': {'general': "Tyrannie passionnelle, autoritarisme.",
                      'amour': "Partenaire possessif.",
                      'travail': "Chef impulsif, décisions à chaud.",
                      'conseil': "La passion doit se discipliner."}
    },
}


def build_minor_card(rang: int, suite_key: str) -> Dict:
    """Construit une carte mineure complète (format homogène avec les Majeurs)."""
    suite = SUITES[suite_key]
    rang_info = RANGS[rang]
    interp = _INTERP.get((rang, suite_key), {})
    droit = interp.get('droit', {}) if isinstance(interp.get('droit'), dict) else {}
    renverse = interp.get('renverse', {}) if isinstance(interp.get('renverse'), dict) else {}
    nom = f"{rang_info['nom']} de {suite['nom']}"
    return {
        'nom': nom,
        'suite': suite['nom'],
        'rang': rang_info['nom'],
        'mots_cles': rang_info['mots'] + [suite['nom']],
        'element': suite['element'],
        'planete': suite['planete'],
        'couleur': suite['couleur'],
        'symbole': suite['symbole'],
        'description': f"{rang_info['nom']} de {suite['nom']} — énergie de « {', '.join(rang_info['mots'])} » appliquée au domaine {suite['theme'].lower()}.",
        'droit': droit,
        'renverse': renverse,
    }


def all_minor_cards() -> List[Dict]:
    """Les 56 arcanes mineurs sous forme de liste homogène."""
    return [build_minor_card(r, s) for s in SUITES.keys() for r in RANGS.keys()]


ALL_MINEURS = all_minor_cards()
