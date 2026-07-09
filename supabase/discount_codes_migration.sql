-- =====================================================================
-- Migration : Codes de réduction Plume Astrale
-- Ajoute des codes promo pour les clientes + un code ADMIN26 (accès total).
-- À exécuter dans le Supabase SQL Editor : https://supabase.com/dashboard/project/ebwicqvbkwogxneipaxh/sql/new
-- Idempotent : safe à réexécuter (ON CONFLICT DO UPDATE).
-- =====================================================================

-- ─────────────────────────────────────────────────────────────────────
-- 1) CODE ADMIN26 — accès total & illimité (pour toi uniquement)
--    999 999 crédits + 3650 jours Premium (10 ans) + max_uses = 1
--    Effet : plus jamais aucune déduction, tous les produits sont
--    accessibles gratuitement via /api/access/free.
-- ─────────────────────────────────────────────────────────────────────
INSERT INTO public.promo_codes (code, credits, premium_days, description, active, max_uses)
VALUES ('ADMIN26', 999999, 3650, 'Accès admin total — Plume Astrale', true, 1)
ON CONFLICT (code) DO UPDATE
  SET credits = EXCLUDED.credits,
      premium_days = EXCLUDED.premium_days,
      description = EXCLUDED.description,
      active = EXCLUDED.active,
      max_uses = EXCLUDED.max_uses;

-- ─────────────────────────────────────────────────────────────────────
-- 2) CODES DE RÉDUCTION CLIENTES — offrent crédits + accès gratuit
--    Chaque code valide = 100% de réduction sur n'importe quel produit.
--    Ex: si la cliente saisit "LUNE20" au checkout, elle débloque le
--    produit gratuitement (une seule fois par compte).
-- ─────────────────────────────────────────────────────────────────────

-- Codes de bienvenue (petits volumes de crédits, forte quantité de rachats)
INSERT INTO public.promo_codes (code, credits, premium_days, description, active, max_uses)
VALUES
  ('BIENVENUE10', 10, 0, 'Bienvenue chez Plume Astrale — 10 crédits', true, 500),
  ('LUNE20',      20, 0, 'Cycle lunaire — 20 crédits offerts',        true, 300),
  ('SOLENA30',    30, 0, 'Cadeau de Solena — 30 crédits',              true, 200)
ON CONFLICT (code) DO UPDATE
  SET credits = EXCLUDED.credits,
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
      description = EXCLUDED.description,
      active = EXCLUDED.active,
      max_uses = EXCLUDED.max_uses;

-- ─────────────────────────────────────────────────────────────────────
-- 3) Vérification — liste tous les codes actifs
-- ─────────────────────────────────────────────────────────────────────
SELECT code, credits, premium_days, description, active, max_uses, used_count
FROM public.promo_codes
WHERE active = true
ORDER BY
  CASE WHEN code = 'ADMIN26' THEN 0 ELSE 1 END,
  created_at DESC;
