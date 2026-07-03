-- ═══════════════════════════════════════════════════════════════════
-- Subject entitlement enforcement — run in Supabase SQL Editor
-- (Dashboard → SQL Editor → New query → paste → Run)
--
-- WHY: subject_selections was only guarded by "insert your own rows"
-- RLS. Nothing compared the number of selections to the paid
-- subject_count, so a $7.99 base subscriber could self-insert all
-- subjects from the browser console. This trigger enforces the limit
-- in the database, where the client can't bypass it.
--
-- Allowed selections by plan:
--   no active/trialing subscription → 0  (trial mode is localStorage-only,
--                                         it never writes selection rows)
--   unlimited                       → 7  (swap freely within the cap)
--   flex                            → paid subject_count (min 7)
--   base / base_plus                → paid subject_count
-- ═══════════════════════════════════════════════════════════════════

create or replace function public.enforce_subject_entitlement()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  sub record;
  sel_count int;
  allowed int;
begin
  select plan, status, subject_count
    into sub
    from public.subscriptions
   where user_id = new.user_id;

  select count(*) into sel_count
    from public.subject_selections
   where user_id = new.user_id;

  if sub is null or sub.status not in ('active', 'trialing') then
    allowed := 0;
  elsif sub.plan = 'unlimited' then
    allowed := 7;
  elsif sub.plan = 'flex' then
    allowed := greatest(coalesce(sub.subject_count, 7), 7);
  else
    allowed := coalesce(sub.subject_count, 0);
  end if;

  if sel_count + 1 > allowed then
    raise exception 'Subject limit reached: your plan covers % subject(s), you have % selected',
      allowed, sel_count
      using errcode = 'P0001';
  end if;

  return new;
end;
$$;

drop trigger if exists trg_enforce_subject_entitlement on public.subject_selections;

create trigger trg_enforce_subject_entitlement
  before insert on public.subject_selections
  for each row
  execute function public.enforce_subject_entitlement();

-- Hardening: one row per user+subject (the client checks before inserting,
-- but nothing enforced it). If this fails with a duplicate-key error, run
-- the SELECT below first to find and delete duplicates, then re-run.
--
--   select user_id, subject_id, count(*)
--     from public.subject_selections
--    group by user_id, subject_id having count(*) > 1;
--
create unique index if not exists uniq_subject_selection
  on public.subject_selections (user_id, subject_id);

-- ── Verify (optional) ────────────────────────────────────────────────
-- As a logged-in user with a base (2-subject) plan, running this in the
-- browser console should now FAIL with "Subject limit reached":
--   await sbClient.from('subject_selections').insert({
--     user_id: currentUser.id, subject_id: 'biology' })
