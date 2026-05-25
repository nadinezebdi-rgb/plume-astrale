-- ============================================================
-- Plume Astrale — Supabase Schema (idempotent)
-- ============================================================
-- A executer dans l'editeur SQL de ton projet Supabase :
-- https://supabase.com/dashboard/project/ebwicqvbkwogxneipaxh/sql/new
-- Copie-colle TOUT ce fichier puis clique "Run"
-- ============================================================

-- ============================================================
-- TABLE: profiles (donnees astrologiques)
-- (utilise la table existante, ajoute les colonnes manquantes)
-- ============================================================
create table if not exists public.profiles (
    id uuid not null references auth.users(id) on delete cascade,
    updated_at timestamptz default now(),
    primary key (id)
);

alter table public.profiles add column if not exists email text;
alter table public.profiles add column if not exists prenom text;
alter table public.profiles add column if not exists full_name text;
alter table public.profiles add column if not exists birth_date date;
alter table public.profiles add column if not exists birth_time time;
alter table public.profiles add column if not exists birth_place text;
alter table public.profiles add column if not exists birth_country text default 'France';
alter table public.profiles add column if not exists latitude numeric;
alter table public.profiles add column if not exists longitude numeric;
alter table public.profiles add column if not exists gender text;
alter table public.profiles add column if not exists created_at timestamptz default now();

alter table public.profiles enable row level security;

drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own" on public.profiles
    for select to authenticated using (auth.uid() = id);

drop policy if exists "profiles_insert_own" on public.profiles;
create policy "profiles_insert_own" on public.profiles
    for insert to authenticated with check (auth.uid() = id);

drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own" on public.profiles
    for update to authenticated using (auth.uid() = id) with check (auth.uid() = id);

-- ============================================================
-- TABLE: wallets (solde de credits)
-- ============================================================
create table if not exists public.wallets (
    user_id uuid not null references auth.users(id) on delete cascade,
    credit_balance integer not null default 0,
    free_tarot_used boolean not null default false,
    created_at timestamptz default now(),
    updated_at timestamptz default now(),
    primary key (user_id)
);

alter table public.wallets enable row level security;

drop policy if exists "wallets_select_own" on public.wallets;
create policy "wallets_select_own" on public.wallets
    for select to authenticated using (auth.uid() = user_id);

-- ============================================================
-- TABLE: credit_transactions
-- ============================================================
create table if not exists public.credit_transactions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    tx_type text not null,
    amount integer not null,
    description text,
    created_at timestamptz default now()
);

create index if not exists credit_tx_user_created_idx
    on public.credit_transactions(user_id, created_at desc);

alter table public.credit_transactions enable row level security;

drop policy if exists "credit_tx_select_own" on public.credit_transactions;
create policy "credit_tx_select_own" on public.credit_transactions
    for select to authenticated using (auth.uid() = user_id);

-- ============================================================
-- TABLE: payment_transactions (Stripe)
-- ============================================================
create table if not exists public.payment_transactions (
    session_id text primary key,
    user_id uuid references auth.users(id) on delete set null,
    user_email text,
    pack_id text not null,
    amount numeric not null,
    currency text not null default 'eur',
    credits integer not null,
    status text not null default 'initiated',
    payment_status text default 'unpaid',
    credits_granted boolean not null default false,
    metadata jsonb,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create index if not exists payment_tx_user_idx on public.payment_transactions(user_id);

alter table public.payment_transactions enable row level security;

drop policy if exists "payment_tx_select_own" on public.payment_transactions;
create policy "payment_tx_select_own" on public.payment_transactions
    for select to authenticated using (auth.uid() = user_id);

-- ============================================================
-- TABLE: promo_codes
-- ============================================================
create table if not exists public.promo_codes (
    code text primary key,
    credits integer not null,
    description text,
    active boolean not null default true,
    max_uses integer,
    used_count integer not null default 0,
    created_at timestamptz default now()
);

create table if not exists public.promo_code_redemptions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    code text not null references public.promo_codes(code) on delete cascade,
    redeemed_at timestamptz default now(),
    unique(user_id, code)
);

alter table public.promo_codes enable row level security;
alter table public.promo_code_redemptions enable row level security;

drop policy if exists "promo_codes_read_active" on public.promo_codes;
create policy "promo_codes_read_active" on public.promo_codes
    for select to authenticated using (active = true);

drop policy if exists "redemptions_select_own" on public.promo_code_redemptions;
create policy "redemptions_select_own" on public.promo_code_redemptions
    for select to authenticated using (auth.uid() = user_id);

insert into public.promo_codes (code, credits, description, active) values
    ('PLUMEASTRALE', 100, '100 credits offerts', true),
    ('TESTPLUME', 200, 'Code de test - 200 credits', true),
    ('BIENVENUE', 50, 'Bonus de bienvenue - 50 credits', true)
on conflict (code) do nothing;

-- ============================================================
-- TABLE: streaks
-- ============================================================
create table if not exists public.streaks (
    user_id uuid primary key references auth.users(id) on delete cascade,
    current_streak integer not null default 0,
    longest_streak integer not null default 0,
    last_checkin_date date,
    total_checkins integer not null default 0,
    updated_at timestamptz default now()
);

alter table public.streaks enable row level security;

drop policy if exists "streaks_select_own" on public.streaks;
create policy "streaks_select_own" on public.streaks
    for select to authenticated using (auth.uid() = user_id);

-- ============================================================
-- TABLE: plume_chat_messages
-- ============================================================
create table if not exists public.plume_chat_messages (
    id uuid primary key default gen_random_uuid(),
    session_id text not null,
    user_id uuid references auth.users(id) on delete cascade,
    role text not null,
    content text not null,
    created_at timestamptz default now()
);

create index if not exists chat_session_idx on public.plume_chat_messages(session_id, created_at);

alter table public.plume_chat_messages enable row level security;

drop policy if exists "chat_select_own" on public.plume_chat_messages;
create policy "chat_select_own" on public.plume_chat_messages
    for select to authenticated using (auth.uid() = user_id);

-- ============================================================
-- TABLE: journal_entries
-- ============================================================
create table if not exists public.journal_entries (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    mood text,
    content text,
    created_at timestamptz default now()
);

create index if not exists journal_user_created_idx on public.journal_entries(user_id, created_at desc);

alter table public.journal_entries enable row level security;

drop policy if exists "journal_select_own" on public.journal_entries;
create policy "journal_select_own" on public.journal_entries
    for select to authenticated using (auth.uid() = user_id);

-- ============================================================
-- TRIGGER: auto-create profile + wallet on signup
-- ============================================================
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.profiles (id, email)
    values (new.id, new.email)
    on conflict (id) do update set email = excluded.email;

    insert into public.wallets (user_id, credit_balance)
    values (new.id, 20)
    on conflict (user_id) do nothing;

    insert into public.credit_transactions (user_id, tx_type, amount, description)
    values (new.id, 'signup_bonus', 20, '20 credits offerts a l''inscription');

    return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute function public.handle_new_user();

-- ============================================================
-- FIN — verifie dans Database -> Tables que tout est cree
-- ============================================================
