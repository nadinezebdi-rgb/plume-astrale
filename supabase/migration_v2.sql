-- Migration: energy_cache + premium subscription
-- A executer dans Supabase SQL Editor

-- Cache des energies du jour pour eviter de re-generer
create table if not exists public.energy_cache (
    user_id uuid not null references auth.users(id) on delete cascade,
    day date not null,
    payload jsonb not null,
    created_at timestamptz default now(),
    primary key (user_id, day)
);

alter table public.energy_cache enable row level security;

drop policy if exists "energy_cache_select_own" on public.energy_cache;
create policy "energy_cache_select_own" on public.energy_cache
    for select to authenticated using (auth.uid() = user_id);

-- Abonnement Premium (14,99 EUR/mois via Stripe)
alter table public.profiles add column if not exists premium_status text default 'free';
alter table public.profiles add column if not exists premium_until timestamptz;
alter table public.profiles add column if not exists stripe_customer_id text;
alter table public.profiles add column if not exists stripe_subscription_id text;

-- Table des subscriptions Stripe pour suivi
create table if not exists public.subscriptions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    stripe_subscription_id text unique,
    stripe_customer_id text,
    status text not null default 'incomplete',
    current_period_start timestamptz,
    current_period_end timestamptz,
    cancel_at_period_end boolean default false,
    plan text default 'premium_monthly',
    amount numeric default 14.99,
    currency text default 'eur',
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create index if not exists subscriptions_user_idx on public.subscriptions(user_id);
create index if not exists subscriptions_stripe_idx on public.subscriptions(stripe_subscription_id);

alter table public.subscriptions enable row level security;

drop policy if exists "subscriptions_select_own" on public.subscriptions;
create policy "subscriptions_select_own" on public.subscriptions
    for select to authenticated using (auth.uid() = user_id);
