-- Table : experiment_locks
-- Objectif : verrouille la variante gagnante d'une expérience A/B après
-- analyse automatique hebdomadaire (si N≥500 vues par variante + lift ≥10%).
--
-- Alimenté par services/experiment_auto_lock.py.
-- Lu par /api/experiments/{experiment}/variant pour servir la variante
-- gagnante au frontend (plutôt qu'un pick aléatoire).
create table if not exists public.experiment_locks (
  experiment     text primary key,
  variant        text not null,
  locked_at      timestamptz not null default now(),
  reason         text
);

comment on table public.experiment_locks is
  'Variantes A/B verrouillées après auto-analyse (lift >=10% + N>=500 par variante).';
