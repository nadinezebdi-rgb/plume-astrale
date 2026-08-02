-- Migration : suppression de la table `sales` inutilisée (Backlog Cleanup 2026-08).
--
-- La table `sales` a été introduite dans un ancien MVP, mais toute la logique de
-- paiement est desormais dans `payment_transactions` (avec metadata JSONB). Aucun
-- code backend/frontend ne lit ou n'ecrit dans `sales`. On peut la dropper.
--
-- IMPORTANT : à exécuter dans le SQL Editor Supabase.
-- Rollback : restaurer depuis un dump si besoin (aucune donnée métier vivante n'y est ecrite).

BEGIN;

-- Verifie que la table existe avant drop (silent no-op sinon)
DROP TABLE IF EXISTS public.sales CASCADE;

COMMIT;
