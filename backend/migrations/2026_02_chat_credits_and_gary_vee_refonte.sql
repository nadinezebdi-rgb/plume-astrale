-- ═══════════════════════════════════════════════════════════════════
-- Migration Feb 2026 — Refonte Gary Vee (Thème Natal 29€, Cercle 2 tiers)
-- À exécuter dans Supabase Studio → SQL Editor
-- ═══════════════════════════════════════════════════════════════════

-- 1) Wallet chat_credit_balance (dédié Cercle Soléna, non fongible)
ALTER TABLE wallets
ADD COLUMN IF NOT EXISTS chat_credit_balance INT NOT NULL DEFAULT 0;

-- 2) Trace explicite de la Cercle Soléna tier (normal / premium)
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS cercle_tier TEXT
    CHECK (cercle_tier IN ('normal', 'premium'))
    DEFAULT NULL;

-- 3) Vérif : aucun abonné Cercle Soléna existant à migrer
--    (confirmé par le user 2026-02 : "IL N'Y A PAS D'ABONNÉ SOLÉNA")
--    Cette query doit renvoyer 0 :
-- SELECT COUNT(*) FROM subscriptions WHERE product = 'cercle_solena' AND status = 'active';

-- 4) Nettoyage — supprime la table `sales` si elle traîne (backlog agent)
-- DROP TABLE IF EXISTS sales;

-- ═══════════════════════════════════════════════════════════════════
-- POST-MIGRATION : STRIPE DASHBOARD
--
-- Créer 3 nouveaux Price IDs dans stripe.com/prices :
--
-- 1) Cercle Soléna Normal    → recurring 14,99€/mois → env STRIPE_CERCLE_SOLENA_PRICE_ID
--    (remplace l'ancien price 19€ — plus aucun abonné à migrer)
--
-- 2) Cercle Soléna Premium   → recurring 29€/mois    → env STRIPE_CERCLE_SOLENA_PREMIUM_PRICE_ID
--
-- 3) Thème Natal Complet     → one-shot 29€          → pas de price_id, montant en dur côté route
--
-- 4) Consultation Ultime     → one-shot 149€         → pas de price_id, montant en dur côté route
-- ═══════════════════════════════════════════════════════════════════
