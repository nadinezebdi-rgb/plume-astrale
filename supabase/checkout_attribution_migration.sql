-- ============================================================
-- TABLE: checkout_attribution
-- ============================================================
-- Signaux d'attribution Meta capturés au moment du checkout, pour TOUS les
-- produits (packs de crédits ET produits one-shot).
-- ============================================================

create table if not exists public.checkout_attribution (
    session_id        text primary key,
    event_id          text,
    fbp               text,
    fbc               text,
    client_ip         text,
    client_user_agent text,
    event_source_url  text,
    capi_sent_at      timestamptz,
    created_at        timestamptz default now()
);

create index if not exists checkout_attribution_created_idx
    on public.checkout_attribution(created_at);

alter table public.checkout_attribution enable row level security;
