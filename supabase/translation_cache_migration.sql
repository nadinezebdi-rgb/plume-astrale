-- ============================================================================
-- Table translation_cache — cache OpenAI pour post-processing FR
-- ============================================================================
-- Utilisée par services/french_polish.py pour éviter de re-traduire du contenu
-- identique. Persistante entre redémarrages backend.
-- ============================================================================

create table if not exists public.translation_cache (
    key text primary key,
    source_text text not null,
    fr_text text not null,
    context text,
    created_at timestamptz not null default now()
);

create index if not exists idx_translation_cache_context on public.translation_cache (context);
create index if not exists idx_translation_cache_created_at on public.translation_cache (created_at desc);

comment on table public.translation_cache is
    'Cache des traductions FR OpenAI (french_polish.py). Évite de re-appeler GPT sur du contenu identique. Clé = SHA-256[:32] de context|source_text.';
