"""
Bibliotheque visuelle Plume Astrale — prompts de generation.

Chaque asset a un identifiant unique (slug), une categorie, un titre lisible,
et un prompt specifique qui vient s'ajouter au STYLE_ANCHOR global.
"""

# ═══════════════════════════════════════════════════════════════════════════
# STYLE ANCHOR — colle a chaque prompt pour garantir la coherence visuelle
# ═══════════════════════════════════════════════════════════════════════════

STYLE_ANCHOR = (
    "highly detailed ornate luxury illustration, deep midnight navy blue background "
    "with subtle starfield, rich metallic gold linework and filigree, sacred geometry "
    "patterns, ethereal purple and teal accents, painterly fantasy realism, "
    "mystical celestial atmosphere, symmetrical framing, high detail 8k, "
    "premium tarot card aesthetic, matching the provided reference style exactly, "
    "deep saturated colors with luminous gold highlights, art nouveau meets modern "
    "digital painting, no text, no watermark, no border, square 1:1 composition"
)

NEGATIVE = (
    "no text, no letters, no words, no watermark, no signature, no logo, "
    "no photograph, no realistic photo, no 3d render, no cartoon, no anime, no children illustration"
)


def _p(subject: str) -> str:
    """Compose un prompt final subject + style."""
    return f"{subject}. Style: {STYLE_ANCHOR}. Constraints: {NEGATIVE}."


# ═══════════════════════════════════════════════════════════════════════════
# 12 SIGNES DU ZODIAQUE (portraits totem style crabe)
# ═══════════════════════════════════════════════════════════════════════════

SIGNS = [
    {
        "slug": "aries",
        "category": "signs",
        "title": "Belier",
        "prompt": _p(
            "A majestic golden ram with spiraling ornate horns, blue and gold "
            "geometric scales on its body, standing on a bed of flames, surrounded "
            "by fire wisps in orange and red, Aries constellation stars behind, "
            "cardinal fire zodiac totem"
        ),
    },
    {
        "slug": "taurus",
        "category": "signs",
        "title": "Taureau",
        "prompt": _p(
            "A powerful bull with intricate gold-etched hide and emerald-inlaid horns, "
            "grounded in a mystical earth landscape with blooming florals and roots, "
            "Taurus constellation glowing above, fixed earth zodiac totem, "
            "deep greens and blues with abundant gold"
        ),
    },
    {
        "slug": "gemini",
        "category": "signs",
        "title": "Gemeaux",
        "prompt": _p(
            "Twin ethereal figures rendered as intertwined mirrored silhouettes "
            "of gold filigree and starlight, connected by a luminous ribbon, "
            "swirling winds and celestial threads, Gemini constellation above, "
            "mutable air zodiac totem, indigo and violet with gold"
        ),
    },
    {
        "slug": "cancer",
        "category": "signs",
        "title": "Cancer",
        "prompt": _p(
            "A magnificent ornate crab with deep sapphire blue mosaic shell etched "
            "with gold filigree, oversized claws with intricate gold patterns, "
            "positioned before a glowing crescent moon and rippling waves of water, "
            "purple ethereal smoke, Cancer constellation stars, cardinal water zodiac totem"
        ),
    },
    {
        "slug": "leo",
        "category": "signs",
        "title": "Lion",
        "prompt": _p(
            "A regal lion with a flowing mane of golden fire and sun rays, "
            "ornate gold crown and jewelry, standing proud in the center of a "
            "radiant solar mandala, Leo constellation stars, fixed fire zodiac totem, "
            "warm golds and deep reds against navy"
        ),
    },
    {
        "slug": "virgo",
        "category": "signs",
        "title": "Vierge",
        "prompt": _p(
            "An elegant celestial maiden holding a golden wheat sheaf, robes flowing "
            "in indigo and gold with intricate embroidery, harvest florals around her, "
            "Virgo constellation stars, mutable earth zodiac totem, "
            "muted greens and golds against midnight blue"
        ),
    },
    {
        "slug": "libra",
        "category": "signs",
        "title": "Balance",
        "prompt": _p(
            "An ornate golden balance scale suspended in cosmic space, each pan "
            "holding a luminous celestial orb, pink and rose gold accents, "
            "surrounded by ethereal ribbons and lotus flowers, Libra constellation "
            "above, cardinal air zodiac totem"
        ),
    },
    {
        "slug": "scorpio",
        "category": "signs",
        "title": "Scorpion",
        "prompt": _p(
            "A powerful mystical scorpion with obsidian black and gold-armored "
            "carapace, tail arched with a glowing venomous stinger, deep crimson "
            "and violet mists swirling, Scorpio constellation above, fixed water "
            "zodiac totem, dramatic dark tones with gold highlights"
        ),
    },
    {
        "slug": "sagittarius",
        "category": "signs",
        "title": "Sagittaire",
        "prompt": _p(
            "A noble centaur archer drawing a golden bow, arrow shaft made of "
            "starlight aimed at the cosmos, ornate gold armor and violet cape, "
            "Sagittarius constellation and shooting stars, mutable fire zodiac totem, "
            "royal purple and gold against navy"
        ),
    },
    {
        "slug": "capricorn",
        "category": "signs",
        "title": "Capricorne",
        "prompt": _p(
            "A mythical sea-goat with ornate spiraling horns of gold and a "
            "serpentine fish tail covered in blue and teal scales, standing on a "
            "mountain peak while the tail dips into starlit waves, Capricorn "
            "constellation, cardinal earth zodiac totem"
        ),
    },
    {
        "slug": "aquarius",
        "category": "signs",
        "title": "Verseau",
        "prompt": _p(
            "A serene cosmic water bearer pouring luminous liquid starlight from "
            "an ornate golden amphora, geometric silver and gold patterns on their "
            "robe, waves of water dissolving into cosmic dust, Aquarius constellation, "
            "fixed air zodiac totem, cyan and silver against midnight"
        ),
    },
    {
        "slug": "pisces",
        "category": "signs",
        "title": "Poissons",
        "prompt": _p(
            "Two ethereal fish swimming in opposite directions connected by a "
            "silver cord, iridescent scales with pearlescent and gold accents, "
            "surrounded by luminous underwater flora and bioluminescent bubbles, "
            "Pisces constellation, mutable water zodiac totem, "
            "deep sea blues and lavender with gold"
        ),
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# 10 PLANETES (spheres celestes style fleurs violettes)
# ═══════════════════════════════════════════════════════════════════════════

PLANETS = [
    {
        "slug": "sun",
        "category": "planets",
        "title": "Soleil",
        "prompt": _p(
            "A radiant central sun sphere with intricate golden solar flares and "
            "ancient sun ray patterns, surrounded by warm bloom of golden petals "
            "with pollen dust rising, alchemical solar mandala, sun glyph "
            "subtly integrated in the center"
        ),
    },
    {
        "slug": "moon",
        "category": "planets",
        "title": "Lune",
        "prompt": _p(
            "A luminous crescent moon sphere with a pearlescent silver-blue surface "
            "showing detailed craters as sacred geometry, surrounded by white and "
            "lavender lotus petals opening, ethereal mist and dewdrops, "
            "crescent moon glyph faintly visible"
        ),
    },
    {
        "slug": "mercury",
        "category": "planets",
        "title": "Mercure",
        "prompt": _p(
            "A metallic silver-gold planet sphere wrapped in flowing ribbons of "
            "quicksilver, ornate wing motifs, surrounded by swift-blooming yellow "
            "and violet flowers with gold pollen, alchemical mercury glyph subtle"
        ),
    },
    {
        "slug": "venus",
        "category": "planets",
        "title": "Venus",
        "prompt": _p(
            "A soft rose-gold planet sphere adorned with pearl inlays and pink "
            "mother-of-pearl swirls, blooming with lush pink roses and white "
            "camellias, honey-gold light emanating, Venus glyph subtly integrated"
        ),
    },
    {
        "slug": "mars",
        "category": "planets",
        "title": "Mars",
        "prompt": _p(
            "A fierce crimson-red planet sphere with sharp obsidian and gold "
            "geometric ridges, surrounded by burning red and orange dahlias, "
            "sparks and flames, Mars glyph subtly integrated"
        ),
    },
    {
        "slug": "jupiter",
        "category": "planets",
        "title": "Jupiter",
        "prompt": _p(
            "A grand royal-purple and gold gas giant with regal banded patterns, "
            "surrounded by abundant blooming purple asters and golden coins "
            "cascading, feeling of prosperity and expansion, Jupiter glyph subtle"
        ),
    },
    {
        "slug": "saturn",
        "category": "planets",
        "title": "Saturne",
        "prompt": _p(
            "A stately dark-slate planet with ornate golden rings inlaid with "
            "geometric runes, surrounded by dark irises and black roses with gold "
            "veining, hourglass motifs, Saturn glyph subtly integrated"
        ),
    },
    {
        "slug": "uranus",
        "category": "planets",
        "title": "Uranus",
        "prompt": _p(
            "An electric cyan-turquoise planet sphere fractured with lightning "
            "veins of gold, tilted on its axis, surrounded by blue orchids and "
            "electric arcs, unconventional geometric patterns, Uranus glyph subtle"
        ),
    },
    {
        "slug": "neptune",
        "category": "planets",
        "title": "Neptune",
        "prompt": _p(
            "A dreamy deep-teal planet sphere with rippling oceanic patterns and "
            "iridescent gold currents, surrounded by underwater lotus and coral "
            "in blue-violet, foamy waves, Neptune glyph subtly integrated"
        ),
    },
    {
        "slug": "pluto",
        "category": "planets",
        "title": "Pluton",
        "prompt": _p(
            "A dark mysterious planet sphere with obsidian-black surface veined "
            "with molten gold, surrounded by black lilies and phoenix-fire, "
            "transformation motifs of ash and rebirth flames, Pluto glyph subtle"
        ),
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# 12 MAISONS ASTROLOGIQUES (scenes symboliques style roue astro)
# ═══════════════════════════════════════════════════════════════════════════

HOUSES = [
    ("house1", "Maison I - Soi", "roman numeral I in gold at center, a lone luminous figure emerging from a golden dawn horizon, self-discovery"),
    ("house2", "Maison II - Valeurs", "roman numeral II in gold, ornate gold treasure chest overflowing with gems and coins, roots and fertile ground"),
    ("house3", "Maison III - Communication", "roman numeral III in gold, twin ancient scrolls and quill pens, gold letters swirling in the air, messengers"),
    ("house4", "Maison IV - Foyer", "roman numeral IV in gold, an ornate golden hearth and moonlit home, ancestral roots descending into earth"),
    ("house5", "Maison V - Creativite", "roman numeral V in gold, a golden lion cub playing, blooming roses, stage curtains and theatrical masks in gold"),
    ("house6", "Maison VI - Sante", "roman numeral VI in gold, herbal garden with mortar and pestle, snake of wisdom coiled around a staff"),
    ("house7", "Maison VII - Relations", "roman numeral VII in gold, two intertwined golden hands and ornate wedding bands, mirrored lovers silhouettes"),
    ("house8", "Maison VIII - Transformation", "roman numeral VIII in gold, phoenix rising from golden ashes, ouroboros serpent, symbolic death and rebirth"),
    ("house9", "Maison IX - Voyages", "roman numeral IX in gold, an ancient golden compass and map, sailing ship among stars, distant temples"),
    ("house10", "Maison X - Carriere", "roman numeral X in gold, an ornate golden throne on a mountain peak, laurel crown, achievement banners"),
    ("house11", "Maison XI - Amitie", "roman numeral XI in gold, a circle of luminous joined hands, doves and violet blossoms, community aura"),
    ("house12", "Maison XII - Spiritualite", "roman numeral XII in gold, a meditating cosmic figure dissolving into stardust, sleeping temple and dreams"),
]

HOUSES = [{"slug": s, "category": "houses", "title": t, "prompt": _p(p)} for s, t, p in HOUSES]


# ═══════════════════════════════════════════════════════════════════════════
# 22 ARCANES MAJEURS DU TAROT
# ═══════════════════════════════════════════════════════════════════════════

TAROT = [
    ("00_le_mat", "Le Mat", "a young wanderer at the edge of a starlit cliff with a small white dog, satchel over shoulder, carefree gaze, sun rising"),
    ("01_le_bateleur", "Le Bateleur", "a magician with raised wand channeling cosmic energy, all four suit symbols on his table (cup, sword, coin, wand), infinity halo"),
    ("02_la_papesse", "La Papesse", "a serene high priestess seated between two pillars, crescent moon at feet, ornate scroll of hidden wisdom, veil of stars"),
    ("03_l_imperatrice", "L'Imperatrice", "a lush enthroned empress in a garden of golden wheat and roses, crown of twelve stars, fertile abundance"),
    ("04_l_empereur", "L'Empereur", "an authoritative emperor seated on a stone throne with ram heads, holding golden scepter and orb, red mountains behind"),
    ("05_le_pape", "Le Pape", "a spiritual hierophant in ornate robes blessing two acolytes, triple crown of gold, keys crossed at his feet"),
    ("06_les_amoureux", "Les Amoureux", "two lovers standing hand in hand under a radiant angel with wings of gold, garden of Eden, choice between two paths"),
    ("07_le_chariot", "Le Chariot", "a triumphant charioteer in golden armor pulled by two sphinxes (one dark, one light), starry canopy, victory"),
    ("08_la_force", "La Force", "a gentle woman calmly closing the jaws of a golden lion, infinity halo above her head, floral crown"),
    ("09_l_hermite", "L'Hermite", "a solitary hermit in gray robes holding a golden lantern with a six-pointed star, walking staff, snowy mountaintop"),
    ("10_la_roue_de_fortune", "La Roue de Fortune", "an ornate golden wheel of fortune with mythical creatures at its corners (bull, lion, eagle, angel), cosmic swirl"),
    ("11_la_justice", "La Justice", "a stern figure enthroned holding a golden scale in one hand and an upright sword in the other, ornate crown"),
    ("12_le_pendu", "Le Pendu", "a serene man hanging upside down by one foot from a golden tau cross, glowing halo, tree of life roots"),
    ("13_la_mort", "La Mort", "a skeletal knight in ornate black-gold armor on a pale horse holding a banner of white rose, sunrise horizon"),
    ("14_la_temperance", "La Temperance", "an angel with fiery wings pouring golden water between two chalices, one foot in a stream, iris blooms"),
    ("15_le_diable", "Le Diable", "a horned figure enthroned on a black altar with two chained lovers at its feet, inverted torch, dark forest"),
    ("16_la_maison_dieu", "La Maison Dieu", "an ornate golden tower struck by lightning, crumbling stones, two figures falling, storm clouds and stars"),
    ("17_l_etoile", "L'Etoile", "a nude serene figure kneeling by a still pond pouring water from two urns, a great eight-pointed star above with seven smaller ones"),
    ("18_la_lune", "La Lune", "a full luminous moon with a face, two towers, a wolf and a dog howling, a crayfish emerging from water, path leading into mist"),
    ("19_le_soleil", "Le Soleil", "a radiant sun with a face, a joyful child riding a white horse under sunflowers, golden light bathing everything"),
    ("20_le_jugement", "Le Jugement", "an angel with golden trumpet in the clouds, three figures rising from open graves with arms raised in awe, resurrection light"),
    ("21_le_monde", "Le Monde", "a dancing figure in the center of a laurel wreath, four elemental beings at the corners (lion, bull, eagle, angel), completion"),
]

TAROT = [{"slug": s, "category": "tarot", "title": t, "prompt": _p(p)} for s, t, p in TAROT]


# ═══════════════════════════════════════════════════════════════════════════
# CATALOGUE COMPLET
# ═══════════════════════════════════════════════════════════════════════════

ALL_ASSETS = SIGNS + PLANETS + HOUSES + TAROT

# Reference images utilisees comme style anchor pour Nano Banana
STYLE_REF_FILES = [
    "cancer_ref.png",   # matriculaire — le crabe = style totem parfait
    "flowers_ref.png",  # matriculaire — planetes/tarot florales
    "wheel_ref.png",    # matriculaire — teinte generale et roue
]


def get_asset(slug: str):
    """Retrouve un asset par son slug."""
    for a in ALL_ASSETS:
        if a["slug"] == slug:
            return a
    return None


def list_by_category(category: str):
    return [a for a in ALL_ASSETS if a["category"] == category]
