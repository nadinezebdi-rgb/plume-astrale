-- ═══════════════════════════════════════════════════════════════════
-- Migration : Journal Email tracking + Email Verification flag
-- Date : 2026-08-02
-- Contexte : Bundle Lecture Complete 97€ — daily journal automatique
-- ═══════════════════════════════════════════════════════════════════

-- 1) profiles.email_verified : flag utilise par le batch daily-journal
--    pour filtrer les utilisateurs qui n'ont pas confirme leur email.
--    Note : historiquement pas utilise, tous les users existants sont
--    consideres verifies par defaut.
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT true NOT NULL;

CREATE INDEX IF NOT EXISTS idx_profiles_email_verified
    ON public.profiles(email_verified)
    WHERE email_verified = true;


-- 2) journal_email_logs : trace les envois quotidiens pour deduplication
--    et pour le dashboard admin (taux d'ouverture, opt-out).
CREATE TABLE IF NOT EXISTS public.journal_email_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT,                         -- profile.id (uuid) ou 'guest:{email}'
    email TEXT NOT NULL,
    sent_date DATE NOT NULL DEFAULT CURRENT_DATE,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    email_provider_id TEXT,               -- id Resend pour tracking
    variant TEXT,                         -- optionnel : pour A/B test futur
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_journal_email_logs_email_date
    ON public.journal_email_logs(email, sent_date);

CREATE INDEX IF NOT EXISTS idx_journal_email_logs_user_date
    ON public.journal_email_logs(user_id, sent_date);

-- Empeche l'envoi de 2 emails a la meme personne le meme jour.
CREATE UNIQUE INDEX IF NOT EXISTS uq_journal_email_logs_email_day
    ON public.journal_email_logs(email, sent_date);

-- RLS : lecture reservee au service role (l'app utilise get_admin_client)
ALTER TABLE public.journal_email_logs ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'journal_email_logs' AND policyname = 'jel_service_all'
    ) THEN
        CREATE POLICY jel_service_all ON public.journal_email_logs
            FOR ALL TO service_role
            USING (true) WITH CHECK (true);
    END IF;
END $$;
