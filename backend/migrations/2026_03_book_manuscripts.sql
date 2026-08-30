-- Migration 2026-03-15 : book_manuscripts (Plume Astrale Book Rendering Engine)
--
-- SOURCE UNIQUE DE VÉRITÉ pour chaque livre généré.
--
-- Principe : les analyses IA sont persistées comme DONNÉES STRUCTURÉES
-- (JSONB par chapitre) et non comme PDF. Si nous refondons le design l'année
-- prochaine, nous pouvons régénérer tous les livres depuis leurs manuscrits
-- SANS refaire les appels LLM (coût zéro).
--
-- Un manuscript = un livre. Il évolue par phases :
--   status='draft'      → créé, en attente de génération de chapitres
--   status='chapters_ready' → tous les chapitres écrits (JSON complet)
--   status='pdf_ready'  → PDF numérique généré et stocké
--   status='delivered'  → email envoyé au client
--   status='print_ready'→ (option) PDF PRINT + cover print prêts pour Lulu

CREATE TABLE IF NOT EXISTS book_manuscripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Lien commerce
    session_id TEXT UNIQUE,                     -- Stripe session (peut être NULL pour aperçus internes)
    payment_transaction_id UUID,                -- FK vers payment_transactions (nullable)

    -- Identité destinataire
    user_email TEXT NOT NULL,
    first_name TEXT NOT NULL,

    -- Données natales complètes (immuables)
    birth_data JSONB NOT NULL,                  -- {date, time, city, country, latitude, longitude, no_birth_time}
    astro_data JSONB,                           -- Positions Swiss Ephemeris v3 (planètes, aspects, houses)

    -- Manuscrit = chapitres structurés
    -- Format : {"cover": {...}, "chapter_1": {"title":"...", "blocks":[...]}, ...}
    chapters JSONB DEFAULT '{}'::jsonb,

    -- Configuration commerciale et éditoriale
    edition TEXT NOT NULL CHECK (edition IN ('numerique', 'brochee', 'reliee')),
    selected_add_ons TEXT[] DEFAULT ARRAY[]::TEXT[],  -- slugs de book_chapters
    total_pages INTEGER,
    total_price_eur INTEGER,

    -- Versioning DESIGN (permet de régénérer avec un nouveau design sans perdre contenu)
    design_version TEXT NOT NULL DEFAULT 'plume-astrale-v1',

    -- État du pipeline
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'chapters_ready', 'pdf_ready', 'delivered', 'print_ready', 'failed')),

    -- Stockage des artéfacts (chemins ou URLs de storage)
    pdf_digital_url TEXT,                       -- PDF client A5 numérique
    pdf_print_url TEXT,                         -- PDF PRINT Lulu (bleed + trimbox)
    cover_print_url TEXT,                       -- Cover Lulu (dos + tranche + face)
    cover_digital_url TEXT,                     -- Face avant seule pour flipbook web

    -- Cover Nano Banana : image générée personnalisée (URL Emergent Object Storage)
    cover_image_url TEXT,
    cover_generation_prompt TEXT,               -- Prompt utilisé (audit)

    -- Traces
    generation_error TEXT,                      -- Dernière erreur de génération (si status='failed')
    metadata JSONB DEFAULT '{}'::jsonb,         -- extension libre

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    delivered_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_book_manuscripts_email ON book_manuscripts (user_email);
CREATE INDEX IF NOT EXISTS idx_book_manuscripts_session ON book_manuscripts (session_id);
CREATE INDEX IF NOT EXISTS idx_book_manuscripts_status ON book_manuscripts (status);
CREATE INDEX IF NOT EXISTS idx_book_manuscripts_created ON book_manuscripts (created_at DESC);

-- Trigger updated_at
CREATE OR REPLACE FUNCTION set_book_manuscripts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_book_manuscripts_updated_at ON book_manuscripts;
CREATE TRIGGER trg_book_manuscripts_updated_at
    BEFORE UPDATE ON book_manuscripts
    FOR EACH ROW EXECUTE FUNCTION set_book_manuscripts_updated_at();

-- RLS : lecture uniquement propriétaire + admin
ALTER TABLE book_manuscripts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS book_manuscripts_admin_all ON book_manuscripts;
CREATE POLICY book_manuscripts_admin_all ON book_manuscripts
    FOR ALL USING (auth.role() = 'service_role');
