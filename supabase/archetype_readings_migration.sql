-- Migration: archetype_readings
-- Table manquante détectée le 2026-02-09 (utilisée par /app/backend/routes/archetype.py)
-- Feature: "Ton Archétype" (15 crédits) — stocke chaque lecture d'archétype jungien pour l'historique utilisateur.

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
