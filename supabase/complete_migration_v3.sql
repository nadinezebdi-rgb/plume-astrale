-- =====================================================================
-- Plume Astrale Migration v3.0 (Archetype + Discount Codes)
-- Exécute dans: https://supabase.com/dashboard/project/ebwicqvbkwogxneipaxh/sql/new
-- Date: 10 Juillet 2026
-- =====================================================================

-- ─────────────────────────────────────────────────────────────────────
-- PHASE 1: Ajouter la colonne premium_days à promo_codes (si manquante)
-- ─────────────────────────────────────────────────────────────────────
ALTER TABLE public.promo_codes ADD COLUMN IF NOT EXISTS premium_days integer DEFAULT 0;

-- ─────────────────────────────────────────────────────────────────────
-- PHASE 2: Créer la table archetype_readings (MANQUANTE)
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.archetype_readings (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  result      jsonb NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- Index pour l'historique (5 dernières lectures par user, tri desc)
CREATE INDEX IF NOT EXISTS archetype_readings_user_created_idx
  ON public.archetype_readings (user_id, created_at DESC);

-- RLS : chaque user ne voit que ses propres lectures ; service_role a full access
ALTER TABLE public.archetype_readings ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "archetype_readings_select_own" ON public.archetype_readings;
CREATE POLICY "archetype_readings_select_own"
  ON public.archetype_readings
  FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "archetype_readings_service_all" ON public.archetype_readings;
CREATE POLICY "archetype_readings_service_all"
  ON public.archetype_readings
  FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- ─────────────────────────────────────────────────────────────────────
-- PHASE 3: Insérer/Mettre à jour les codes promo
-- ─────────────────────────────────────────────────────────────────────

-- CODE ADMIN26 — accès total & illimité (999 999 crédits + 3650 jours Premium)
INSERT INTO public.promo_codes (code, credits, premium_days, description, active, max_uses)
VALUES ('ADMIN26', 999999, 3650, 'Accès admin total — Plume Astrale', true, 1)
ON CONFLICT (code) DO UPDATE
  SET credits = EXCLUDED.credits,
      premium_days = EXCLUDED.premium_days,
      description = EXCLUDED.description,
      active = EXCLUDED.active,
      max_uses = EXCLUDED.max_uses;

-- Codes de bienvenue (petits volumes de crédits)
INSERT INTO public.promo_codes (code, credits, premium_days, description, active, max_uses)
VALUES
  ('BIENVENUE10', 10, 0, 'Bienvenue chez Plume Astrale — 10 crédits', true, 500),
  ('LUNE20',      20, 0, 'Cycle lunaire — 20 crédits offerts',        true, 300),
  ('SOLENA30',    30, 0, 'Cadeau de Solena — 30 crédits',              true, 200)
ON CONFLICT (code) DO UPDATE
  SET credits = EXCLUDED.credits,
      premium_days = EXCLUDED.premium_days,
      description = EXCLUDED.description,
      active = EXCLUDED.active,
      max_uses = EXCLUDED.max_uses;

-- Codes premium (offrent des jours Premium au lieu de crédits)
INSERT INTO public.promo_codes (code, credits, premium_days, description, active, max_uses)
VALUES
  ('DECOUVERTE7',  0,  7,  'Premium 7 jours pour découvrir',    true, 200),
  ('CADEAU30',     0,  30, 'Premium 1 mois offert',              true, 100),
  ('FIDELITE90',   0,  90, 'Premium 3 mois — fidélité',          true, 50)
ON CONFLICT (code) DO UPDATE
  SET credits = EXCLUDED.credits,
      premium_days = EXCLUDED.premium_days,
      description = EXCLUDED.description,
      active = EXCLUDED.active,
      max_uses = EXCLUDED.max_uses;

-- Codes produits (déverrouillent 100% d'un produit high-ticket)
INSERT INTO public.promo_codes (code, credits, premium_days, description, active, max_uses)
VALUES
  ('KABBALE100',       50, 0, 'Kabbale offerte — 50 crédits bonus', true, 30),
  ('RENCONTRES100',    40, 0, 'Rencontres Ultime offerte',           true, 30),
  ('ARCHETYPE100',     20, 0, 'Ton Archétype offert',                 true, 100)
ON CONFLICT (code) DO UPDATE
  SET credits = EXCLUDED.credits,
      premium_days = EXCLUDED.premium_days,
      description = EXCLUDED.description,
      active = EXCLUDED.active,
      max_uses = EXCLUDED.max_uses;

-- ─────────────────────────────────────────────────────────────────────
-- PHASE 4: Vérification — liste tous les codes actifs
-- ─────────────────────────────────────────────────────────────────────
SELECT 'Migration complete ✅' as status,
       code, credits, premium_days, description, active, max_uses, used_count
FROM public.promo_codes
WHERE active = true
ORDER BY
  CASE WHEN code = 'ADMIN26' THEN 0 ELSE 1 END,
  created_at DESC;

-- ─────────────────────────────────────────────────────────────────────
-- PHASE 5: Vérification — archetype_readings table created
-- ─────────────────────────────────────────────────────────────────────
SELECT 'archetype_readings table ✅' as status,
       COUNT(*) as total_readings
FROM public.archetype_readings;
