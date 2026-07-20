-- ============================================================================
-- Table narrative_cache — cache d'enrichissement narratif OpenAI
-- ============================================================================
-- Utilisée par services/enrich_narrative.py pour éviter de re-générer
-- l'enrichissement long+question sur des textes identiques.
-- ============================================================================

create table if not exists public.narrative_cache (
    key text primary key,
    source_text text not null,
    enriched_text text not null,
    context text,
    first_name text,
    created_at timestamptz not null default now()
);

create index if not exists idx_narrative_cache_context on public.narrative_cache (context);
create index if not exists idx_narrative_cache_created_at on public.narrative_cache (created_at desc);

comment on table public.narrative_cache is
    'Cache OpenAI pour enrich_narrative.py (texte long + question finale). Clé = SHA-256[:32] de context|first_name|source_text.';
