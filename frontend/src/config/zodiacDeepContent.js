/**
 * Contenu enrichi par signe — SEO P7 (concours 2026-02).
 *
 * Produit ~400 mots additionnels par signe zodiacal en combinant les
 * métadonnées (element, modality, ruler) avec des templates personnalisés.
 * Résultat : les 12 pages /horoscope/:sign passent de ~250 à ~600-800 mots,
 * ce qui rentre dans la fourchette recommandée par le bilan SEO.
 *
 * Chaque page reçoit désormais :
 *   • Amour & relations (~100 mots, personnalisé par élément + planète maîtresse)
 *   • Travail & vocation (~100 mots, personnalisé par modalité)
 *   • Croissance & équilibre (~100 mots, personnalisé par challenges)
 *   • FAQ 4 questions/réponses (structured data schema.org/FAQPage)
 */

// Textes de base par élément
const ELEMENT_LOVE = {
  Feu: "En amour, les signes de Feu cherchent l'élan, la passion, la sincérité directe. Ce qui vous éteint : l'attentisme, la routine, les jeux flous. Ce qui vous nourrit : quelqu'un qui vous voit vraiment et qui n'a pas peur de votre intensité. Vous aimez à voix haute — ne laissez jamais un doute s'installer dans les non-dits.",
  Terre: "En amour, les signes de Terre construisent lentement mais solidement. La sécurité affective, la présence physique, les gestes concrets comptent plus que les grands discours. Vous êtes rassurant·e sans y penser — restez attentif·ve à ne pas laisser la sécurité se transformer en habitude froide. Vos histoires les plus belles se déploient dans la durée.",
  Air: "En amour, les signes d'Air ont besoin d'espace, de conversations vivantes, d'un partenaire qui les surprend intellectuellement. La complicité passe pour vous par le rire et la pensée partagée avant tout. Attention à ne pas rester au stade de l'idée : incarnez, engagez-vous, laissez le lien exister ailleurs que dans les mots.",
  Eau: "En amour, les signes d'Eau aiment en profondeur. Vous ressentez les émotions de l'autre avant qu'il les formule, ce qui rend vos liens intensément justes — mais aussi fatigants si vous ne posez pas de limites claires. Vos plus belles histoires sont celles où vous osez dire ce que vous sentez sans attendre que l'autre le devine.",
};

const MODALITY_CAREER = {
  Cardinal: "Vous êtes un initiateur naturel. Les métiers qui vous conviennent le mieux impliquent de lancer, décider, ouvrir de nouvelles voies. Vous vous ennuyez vite dans les postes purement gestionnaires. Cherchez des environnements où votre parole compte dès le premier jour — et où vous pouvez poser un cap sans attendre trois validations.",
  Fixe: "Vous êtes un bâtisseur. Vos meilleures années professionnelles sont celles où vous restez assez longtemps sur un projet pour en voir la vraie profondeur. La constance est votre force — restez juste attentif·ve à ne pas confondre ténacité et enfermement. Un métier bien choisi devient chez vous une œuvre de vie.",
  Mutable: "Votre force est l'adaptabilité. Vous excellez dans les environnements changeants, les projets qui évoluent, les rôles qui demandent plusieurs casquettes. Le piège inverse : vous éparpiller au point de ne rien finir. Choisissez un fil directeur — un domaine, une compétence, une signature — et laissez votre polyvalence enrichir ce fil plutôt que le diluer.",
};

const RULER_GROWTH = {
  Mars: "Votre planète maîtresse, Mars, vous donne du feu et de la volonté. Le travail intérieur consiste à orienter cette force sans la laisser exploser en colère ou en impatience. Bougez le corps régulièrement, pratiquez un sport qui vous canalise, et apprenez à distinguer l'urgence réelle de l'urgence ressentie.",
  Vénus: "Votre planète maîtresse, Vénus, vous relie à la beauté, à l'harmonie et au plaisir. Votre croissance passe par le raffinement de votre sens du goût et par l'apprentissage du discernement dans vos plaisirs. Cultivez ce qui vous nourrit vraiment — et lâchez ce qui n'est que confort par défaut.",
  Mercure: "Votre planète maîtresse, Mercure, vous donne l'intelligence et l'aisance verbale. Votre croissance passe par la discipline de la parole : dire moins, dire mieux, dire au bon moment. Écrire régulièrement — journal, notes, correspondance — est pour vous une hygiène presque thérapeutique.",
  Lune: "Votre planète maîtresse, la Lune, vous relie à l'émotion, à l'intuition et aux cycles. Votre croissance passe par l'écoute de vos rythmes intérieurs : ce qui vous fatigue, ce qui vous ressource, ce qui vous transforme au fil des mois. Un carnet de suivi émotionnel change la donne.",
  Soleil: "Votre planète maîtresse, le Soleil, vous relie à votre identité rayonnante. Votre croissance passe par l'affirmation joyeuse de qui vous êtes — sans arrogance, mais sans dissimulation non plus. Une pratique créative régulière (art, expression, projet) est essentielle à votre équilibre.",
  Jupiter: "Votre planète maîtresse, Jupiter, vous donne l'expansion, l'optimisme et la soif de sens. Votre croissance passe par le raffinement de votre philosophie de vie — voyage, étude, transmission. Attention à l'excès : Jupiter aime le trop. Choisissez la profondeur plutôt que la quantité.",
  Saturne: "Votre planète maîtresse, Saturne, vous donne la structure, la profondeur et le sens du long terme. Votre croissance passe par l'acceptation lente de vos limites — non comme des freins, mais comme la matière même de votre puissance. Ce que vous construisez patiemment vaut plus que dix promesses rapides.",
  Uranus: "Votre planète maîtresse, Uranus, vous donne l'originalité, l'indépendance et le goût de la liberté. Votre croissance passe par l'apprentissage de la stabilité intérieure — un point d'ancrage qui vous permet de rester libre sans vous éparpiller. Une pratique corporelle régulière calme votre système nerveux.",
  Neptune: "Votre planète maîtresse, Neptune, vous relie à l'imaginaire, à l'intuition et au subtil. Votre croissance passe par l'ancrage — corps, sommeil, alimentation, limites — pour éviter de vous perdre dans le flou. La création (art, écriture, musique) est votre voie royale.",
  Pluton: "Votre planète maîtresse, Pluton, vous relie aux profondeurs, à la transformation et à la vérité brute. Votre croissance passe par le courage de regarder ce que les autres évitent — vos ombres, celles du monde. Vos vies ont des chapitres qui se ferment radicalement pour laisser place à ce qui vient.",
};

/**
 * Génère le contenu enrichi pour un signe donné.
 * @param {object} sign - Objet ZODIAC_SIGNS
 * @returns {{loveText, careerText, growthText, faq: [{q,a}]}}
 */
export function getDeepContent(sign) {
  const loveText = ELEMENT_LOVE[sign.element] || ELEMENT_LOVE.Air;
  const careerText = MODALITY_CAREER[sign.modality] || MODALITY_CAREER.Mutable;
  const growthText = RULER_GROWTH[sign.ruler] || RULER_GROWTH.Mercure;

  // Compatibilités par élément (règle astrologique classique : mêmes éléments et
  // éléments complémentaires — Feu/Air, Terre/Eau)
  const COMPAT_MAP = {
    Feu: 'les signes de Feu (Bélier, Lion, Sagittaire) et d\'Air (Gémeaux, Balance, Verseau)',
    Terre: 'les signes de Terre (Taureau, Vierge, Capricorne) et d\'Eau (Cancer, Scorpion, Poissons)',
    Air: 'les signes d\'Air (Gémeaux, Balance, Verseau) et de Feu (Bélier, Lion, Sagittaire)',
    Eau: 'les signes d\'Eau (Cancer, Scorpion, Poissons) et de Terre (Taureau, Vierge, Capricorne)',
  };

  const traitsCsv = (sign.traits || []).slice(0, 3).join(', ').toLowerCase();

  const faq = [
    {
      q: `Comment reconnaître une personne ${sign.name} ?`,
      a: `Les personnes ${sign.name} rayonnent souvent par leur ${traitsCsv}. ${sign.archetype} Elles portent l'énergie de l'élément ${sign.element}, ce qui se ressent dans leur manière d'aborder la vie : ${sign.element === 'Feu' ? 'avec élan et franchise' : sign.element === 'Terre' ? 'avec constance et ancrage' : sign.element === 'Air' ? 'avec curiosité et vivacité' : 'avec sensibilité et profondeur'}.`,
    },
    {
      q: `Quels signes sont compatibles avec le ${sign.name} ?`,
      a: `En astrologie classique, le ${sign.name} entretient les affinités les plus naturelles avec ${COMPAT_MAP[sign.element]}. Cela dit, une vraie compatibilité amoureuse se lit dans la synastrie complète des deux thèmes natals — pas dans le seul signe solaire. Vénus, Mars et la Lune racontent souvent plus que le Soleil.`,
    },
    {
      q: `Quelle est la planète maîtresse du ${sign.name} ?`,
      a: `Le ${sign.name} est gouverné par ${sign.ruler}. Cette planète colore votre manière d'aimer, de décider, de rayonner. La comprendre dans votre thème natal — sa position, ses aspects — ouvre une lecture beaucoup plus fine que celle du seul signe solaire.`,
    },
    {
      q: `Le ${sign.name} est de quel élément et quelle modalité ?`,
      a: `Le ${sign.name} est un signe d'${sign.element} de modalité ${sign.modality}. L'élément décrit votre tempérament de fond (${sign.element === 'Feu' ? 'action' : sign.element === 'Terre' ? 'concret' : sign.element === 'Air' ? 'pensée' : 'ressenti'}), la modalité décrit votre manière d'engager les cycles (${sign.modality === 'Cardinal' ? 'initier' : sign.modality === 'Fixe' ? 'consolider' : 'transformer'}).`,
    },
  ];

  return { loveText, careerText, growthText, faq };
}
