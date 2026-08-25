-- Migration 2026-02-26 : QR Referral Tracker (tables analytics)
--
-- À exécuter manuellement dans le SQL editor Supabase du projet
-- (Dashboard → SQL Editor → New query → coller ce fichier → Run).
--
-- Ces tables activent le compteur de scans QR côté colophon PDF :
--   • referral_scans          : journal append-only de chaque scan (audit)
--   • referral_scan_counters  : agrégat rapide {code, count} pour /admin/qr-stats
--
-- Sans ces tables, l'endpoint /api/admin/referral-scan-stats retourne
-- {ok:true, top_codes:[]} (empty state — pas d'erreur).

CREATE TABLE IF NOT EXISTS referral_scans (
    id BIGSERIAL PRIMARY KEY,
    code TEXT NOT NULL,
    ua TEXT,
    ip TEXT,
    scanned_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_referral_scans_code_time
    ON referral_scans (code, scanned_at DESC);

CREATE TABLE IF NOT EXISTS referral_scan_counters (
    code TEXT PRIMARY KEY,
    count INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS : lecture réservée au service_role (admin backend). Aucun accès public.
ALTER TABLE referral_scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE referral_scan_counters ENABLE ROW LEVEL SECURITY;

-- Optionnel : purger les scans > 180 jours (garder les compteurs, retirer le détail)
-- CREATE OR REPLACE FUNCTION purge_old_referral_scans() RETURNS void AS $$
--   DELETE FROM referral_scans WHERE scanned_at < NOW() - INTERVAL '180 days';
-- $$ LANGUAGE sql;
