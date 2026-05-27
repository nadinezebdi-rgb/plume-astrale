-- =====================================================================
-- Migration : Premium Codes (codes promo donnant des jours Premium gratuits)
-- À exécuter dans le Supabase SQL Editor.
-- Idempotent : safe à réexécuter.
-- =====================================================================

-- 1) Ajouter colonne premium_days à la table promo_codes (NULL = code crédits classique)
ALTER TABLE public.promo_codes
  ADD COLUMN IF NOT EXISTS premium_days INTEGER;

-- 2) Garantir : si premium_days > 0, alors credits peut être 0 (les 2 ne sont pas mutuellement exclusifs mais en pratique on choisit l'un)
ALTER TABLE public.promo_codes
  ALTER COLUMN credits DROP NOT NULL;

ALTER TABLE public.promo_codes
  ALTER COLUMN credits SET DEFAULT 0;

-- 3) Seed : créer un code Premium d'exemple (1 mois gratuit) — désactivé par défaut, l'admin l'activera depuis le dashboard
INSERT INTO public.promo_codes (code, credits, premium_days, description, active, max_uses)
VALUES ('PREMIUM30', 0, 30, 'Premium offert 30 jours', false, 10)
ON CONFLICT (code) DO NOTHING;

INSERT INTO public.promo_codes (code, credits, premium_days, description, active, max_uses)
VALUES ('PREMIUM7', 0, 7, 'Premium offert 7 jours (dédommagement)', false, 50)
ON CONFLICT (code) DO NOTHING;

INSERT INTO public.promo_codes (code, credits, premium_days, description, active, max_uses)
VALUES ('FAMILLE2026', 0, 90, 'Acces Premium 3 mois — proches & famille', false, 10)
ON CONFLICT (code) DO NOTHING;

-- 4) Vérification
SELECT code, credits, premium_days, description, active, max_uses, used_count
FROM public.promo_codes
ORDER BY created_at DESC;
