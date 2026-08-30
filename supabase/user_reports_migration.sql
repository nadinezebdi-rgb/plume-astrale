-- Migration : table user_reports pour archivage des rapports PDF par utilisateur
-- Bucket Supabase Storage 'reports' doit déjà exister (utilisé par karma_destin.py etc.)

CREATE TABLE IF NOT EXISTS public.user_reports (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    type        TEXT NOT NULL,          -- ex: 'karma-destin', 'numerologie', 'theme-natal'
    titre       TEXT NOT NULL,          -- ex: 'Karma & Destin — Marie'
    inputs      JSONB DEFAULT '{}',     -- données d'entrée utilisées pour la génération
    pdf_path    TEXT DEFAULT '',        -- chemin dans bucket Storage 'reports'
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour requêtes par utilisateur (triées par date décroissante)
CREATE INDEX IF NOT EXISTS user_reports_user_id_created_at_idx
    ON public.user_reports (user_id, created_at DESC);

-- RLS : chaque utilisateur ne voit que ses propres rapports
ALTER TABLE public.user_reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "user_reports_select_own" ON public.user_reports
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "user_reports_insert_own" ON public.user_reports
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Le service_role (backend) bypasse la RLS automatiquement.
