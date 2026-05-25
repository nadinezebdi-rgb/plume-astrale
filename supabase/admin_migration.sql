-- ============================================================
-- Plume Astrale — Migration admin (idempotent)
-- A executer dans Supabase SQL Editor
-- ============================================================

-- 1) Ajouter is_admin sur profiles
alter table public.profiles add column if not exists is_admin boolean not null default false;

-- 2) Marquer le compte admin@plume-astrale.fr comme admin
update public.profiles
set is_admin = true
where email = 'admin@plume-astrale.fr';

-- 3) Politique pour permettre aux admins de lire toutes les donnees
-- (necessaire pour le dashboard cote backend - on utilise service_role mais autant prevoir)
drop policy if exists "profiles_admin_select_all" on public.profiles;
create policy "profiles_admin_select_all" on public.profiles
    for select to authenticated
    using (
        exists(select 1 from public.profiles p2 where p2.id = auth.uid() and p2.is_admin = true)
    );

-- 4) Verifier
select id, email, is_admin from public.profiles where is_admin = true;
