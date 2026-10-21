-- ============================================================
-- 2026-02 — Anti-farming : lier les 20 crédits à la vérification email
-- ============================================================
-- But : empêcher le farming de comptes avec emails jetables.
-- Avant : les 20 crédits étaient donnés sur INSERT auth.users
--         → un farmer peut créer N comptes fake sans jamais confirmer l'email
--         et consommer N × 20 crédits.
-- Après : la ligne wallet + profile est bien créée sur INSERT
--         mais les 20 crédits ne sont posés QUE quand email_confirmed_at
--         passe de NULL → NOT NULL (= clic sur le lien de confirmation).
--
-- Les comptes existants (déjà avec 20 crédits) ne sont PAS touchés.
-- Idempotent : relancer ce script n'a aucun effet secondaire.
-- ============================================================

-- 1) handle_new_user : crée profile + wallet VIDE à l'INSERT
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

    -- Wallet créé à 0 crédit (était 20) — on attendra la confirmation d'email
    insert into public.wallets (user_id, credit_balance)
    values (new.id, 0)
    on conflict (user_id) do nothing;

    return new;
end;
$$;

-- 2) handle_user_email_confirmed : donne les 20 crédits à la vérification
create or replace function public.handle_user_email_confirmed()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    -- Déclenche seulement quand email_confirmed_at passe de NULL -> NOT NULL
    if new.email_confirmed_at is not null
       and (old.email_confirmed_at is null) then

        -- Idempotence : ne crédite qu'une fois par user
        if not exists (
            select 1 from public.credit_transactions
            where user_id = new.id
              and description = '20 credits offerts a l''inscription'
        ) then
            update public.wallets
               set credit_balance = credit_balance + 20
             where user_id = new.id;

            insert into public.credit_transactions (user_id, tx_type, amount, description)
            values (new.id, 'signup_bonus', 20, '20 credits offerts a l''inscription');
        end if;
    end if;

    return new;
end;
$$;

-- 3) Trigger sur l'UPDATE auth.users
drop trigger if exists on_auth_user_email_confirmed on auth.users;
create trigger on_auth_user_email_confirmed
    after update of email_confirmed_at on auth.users
    for each row execute function public.handle_user_email_confirmed();

-- ============================================================
-- VÉRIFICATIONS APRÈS EXÉCUTION
-- ============================================================
-- 1) Dans Supabase → Authentication → Providers → Email :
--    S'assurer que "Confirm email" est ACTIVÉ (devrait l'être par défaut).
-- 2) Tester : créer un compte test → wallet doit être à 0 crédit
-- 3) Cliquer sur le lien dans l'email → wallet doit passer à 20 crédits
-- 4) Vérifier credit_transactions : une seule ligne 'signup_bonus' / user
-- ============================================================
