-- Migration 2026-03-01 : book_chapters (pivot L'Atelier /composer)
--
-- À exécuter dans le SQL Editor Supabase.
-- Contexte : pivot produit majeur — le Thème Natal devient l'UNIQUE base
-- (3 éditions : Numérique 24€ / Broché 69€ / Relié 119€) et tous les autres
-- rapports deviennent des "chapitres" optionnels ajoutés au livre.
--
-- Règle de pricing serveur (source de vérité, jamais depuis le front) :
--   - +29€ pour le 1er chapitre choisi
--   - +19€ pour chaque chapitre suivant
--   - Plafond 99€ pour la totalité des chapitres (base + édition en sus)

CREATE TABLE IF NOT EXISTS book_chapters (
    slug TEXT PRIMARY KEY,                          -- ex: 'arbre_de_vie', 'astrocartographie'
    name TEXT NOT NULL,                             -- Titre affiché ("L'Arbre de Vie")
    subtitle TEXT,                                  -- Sous-titre éditorial
    price_unit_eur INTEGER NOT NULL DEFAULT 19,     -- Prix unitaire indicatif (info)
    pages_added INTEGER NOT NULL DEFAULT 12,        -- Pages ajoutées au livre final
    api_endpoint TEXT,                              -- Endpoint Astrology API v3 associé (nullable)
    is_active BOOLEAN NOT NULL DEFAULT TRUE,        -- Toggle sans redéploiement
    requires_no_birth_time BOOLEAN NOT NULL DEFAULT FALSE,  -- Chapitre "L'Heure Retrouvée" uniquement si heure absente
    sort_order INTEGER NOT NULL DEFAULT 0,          -- Ordre d'affichage /composer étape 2
    tagline TEXT,                                   -- Phrase courte de vente
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_book_chapters_active_sort
    ON book_chapters (is_active, sort_order);

ALTER TABLE book_chapters ENABLE ROW LEVEL SECURITY;

-- Lecture publique autorisée (les chapitres sont un catalogue non-sensible)
DROP POLICY IF EXISTS book_chapters_read_public ON book_chapters;
CREATE POLICY book_chapters_read_public ON book_chapters
    FOR SELECT USING (TRUE);

-- ── Seed 6 chapitres ────────────────────────────────────────────
INSERT INTO book_chapters (slug, name, subtitle, price_unit_eur, pages_added, api_endpoint, is_active, requires_no_birth_time, sort_order, tagline)
VALUES
    (
        'arbre_de_vie',
        'L''Arbre de Vie',
        'Les 10 Séphiroth appliquées à votre ciel',
        29,
        12,
        NULL,
        TRUE,
        FALSE,
        10,
        'La kabbale hébraïque traduit votre thème en dix stations d''âme.'
    ),
    (
        'astrocartographie',
        'Astrocartographie',
        'Où votre ciel s''allume dans le monde',
        29,
        14,
        '/api/astrology-v3/astrocartography',
        TRUE,
        FALSE,
        20,
        'Vos lignes planétaires tracées sur la carte du monde, ville par ville.'
    ),
    (
        'karma_destin',
        'Voyage Karmique',
        'Nœuds lunaires, Saturne, Chiron, Pluton',
        29,
        16,
        '/api/astrology-v3/karma',
        TRUE,
        FALSE,
        30,
        'Ce que votre âme a apporté avec elle — et ce qu''elle vient dénouer.'
    ),
    (
        'heure_retrouvee',
        'L''Heure Retrouvée',
        'Rectification symbolique de votre heure de naissance',
        29,
        10,
        '/api/astrology-v3/rectification',
        TRUE,
        TRUE,
        40,
        'Vous n''avez pas votre heure exacte ? Nous cherchons son écho dans votre biographie.'
    ),
    (
        'etoiles_fixes',
        'Étoiles Fixes',
        'Les étoiles millénaires qui touchent vos planètes',
        29,
        10,
        '/api/astrology-v3/fixed-stars',
        TRUE,
        FALSE,
        50,
        'Régulus, Sirius, Aldébaran… lesquelles vous éclairent, et où.'
    ),
    (
        'symboles_sabiens',
        'Symboles Sabiens',
        '360 images pour lire chaque degré de votre thème',
        29,
        12,
        '/api/astrology-v3/sabian-symbols',
        TRUE,
        FALSE,
        60,
        'Chaque degré du zodiaque porte une image. Voici celles qui vous concernent.'
    )
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    subtitle = EXCLUDED.subtitle,
    price_unit_eur = EXCLUDED.price_unit_eur,
    pages_added = EXCLUDED.pages_added,
    api_endpoint = EXCLUDED.api_endpoint,
    is_active = EXCLUDED.is_active,
    requires_no_birth_time = EXCLUDED.requires_no_birth_time,
    sort_order = EXCLUDED.sort_order,
    tagline = EXCLUDED.tagline,
    updated_at = NOW();
