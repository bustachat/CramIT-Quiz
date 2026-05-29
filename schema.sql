-- ============================================================
--  CramIT — Supabase Schema
--  Run this in your Supabase SQL Editor (Dashboard → SQL Editor)
--  Last updated: May 2026 — added explicit grants (Supabase requirement Oct 2026)
-- ============================================================


-- ── 1. PROFILES (extends Supabase auth.users) ──────────────
create table if not exists public.profiles (
  id              uuid primary key references auth.users(id) on delete cascade,
  email           text,
  full_name       text,
  created_at      timestamptz default now()
);

-- Auto-create profile when a user signs up
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.profiles (id, email, full_name)
  values (
    new.id,
    new.email,
    new.raw_user_meta_data->>'full_name'
  );
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();


-- ── 2. SUBSCRIPTIONS ───────────────────────────────────────
create table if not exists public.subscriptions (
  id                    uuid primary key default gen_random_uuid(),
  user_id               uuid not null references public.profiles(id) on delete cascade,

  -- Stripe identifiers
  stripe_customer_id    text unique,
  stripe_subscription_id text unique,
  stripe_price_id       text,

  -- Plan state
  plan                  text not null default 'free',
  -- 'free' | 'base' | 'unlimited' | 'flex'

  subject_count         int  not null default 1,
  -- actual number of subjects currently selected (1–15)

  flex_extras           int  not null default 0,
  -- subjects above 7 on the flex plan

  status                text not null default 'active',
  -- 'active' | 'cancelled' | 'past_due' | 'trialing'

  current_period_start  timestamptz,
  current_period_end    timestamptz,
  cancel_at_period_end  boolean default false,

  updated_at            timestamptz default now(),
  created_at            timestamptz default now(),

  unique(user_id)
);


-- ── 3. SUBJECT SELECTIONS ──────────────────────────────────
create table if not exists public.subject_selections (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references public.profiles(id) on delete cascade,
  subject_id  text not null,
  -- e.g. 'mathematics-standard-2', 'vet-construction'
  added_at    timestamptz default now(),

  unique(user_id, subject_id)
);


-- ── 4. PRICING CONFIG (edit here to change prices) ─────────
create table if not exists public.pricing_config (
  key   text primary key,
  value text not null
);

insert into public.pricing_config (key, value) values
  ('base_price_aud',     '7.99'),
  ('extra_price_aud',    '2.99'),
  ('cap_price_aud',      '19.99'),
  ('cap_subject_limit',  '7'),
  ('base_includes',      '2'),
  ('free_subjects',      '1')
on conflict (key) do nothing;


-- ── 5. ROW LEVEL SECURITY ──────────────────────────────────
alter table public.profiles           enable row level security;
alter table public.subscriptions      enable row level security;
alter table public.subject_selections enable row level security;

-- Profiles: users can only read/update their own
create policy "Users can view own profile"
  on public.profiles for select using (auth.uid() = id);
create policy "Users can update own profile"
  on public.profiles for update using (auth.uid() = id);

-- Subscriptions: users can read their own; only service role can write
create policy "Users can view own subscription"
  on public.subscriptions for select using (auth.uid() = user_id);

-- Subject selections: users manage their own
create policy "Users can view own subjects"
  on public.subject_selections for select using (auth.uid() = user_id);
create policy "Users can insert own subjects"
  on public.subject_selections for insert with check (auth.uid() = user_id);
create policy "Users can delete own subjects"
  on public.subject_selections for delete using (auth.uid() = user_id);

-- Pricing config: anyone can read
create policy "Anyone can read pricing"
  on public.pricing_config for select using (true);


-- ── 6. COMPUTED PRICE FUNCTION ─────────────────────────────
-- Call this from your app: select * from calculate_price(5, 'swap')
create or replace function public.calculate_price(
  n_subjects int,
  plan_type  text default 'swap'  -- 'swap' | 'flex'
)
returns table (
  price_aud     numeric,
  plan_name     text,
  breakdown     text
) language plpgsql as $$
declare
  v_base    numeric := 7.99;
  v_extra   numeric := 2.99;
  v_cap     numeric := 19.99;
  v_cap_lim int     := 7;
  v_price   numeric;
  v_plan    text;
  v_desc    text;
begin
  if n_subjects <= 1 then
    v_price := 0; v_plan := 'free';
    v_desc  := '1 subject — free forever';
  elsif n_subjects = 2 then
    v_price := v_base; v_plan := 'base';
    v_desc  := '2 subjects — base plan';
  elsif v_base + (n_subjects - 2) * v_extra < v_cap then
    v_price := v_base + (n_subjects - 2) * v_extra;
    v_plan  := 'base_plus';
    v_desc  := '$' || v_base || ' + ' || (n_subjects-2) || ' × $' || v_extra;
  elsif n_subjects <= v_cap_lim then
    v_price := v_cap; v_plan := 'unlimited';
    v_desc  := '$19.99 cap — ' || n_subjects || ' subjects';
  elsif plan_type = 'swap' then
    v_price := v_cap; v_plan := 'unlimited';
    v_desc  := '$19.99 cap (swap mode — max 7 subjects)';
  else
    v_price := v_cap + (n_subjects - v_cap_lim) * v_extra;
    v_plan  := 'flex';
    v_desc  := '$19.99 + ' || (n_subjects - v_cap_lim) || ' × $' || v_extra || ' flex';
  end if;

  return query select
    round(v_price, 2)::numeric,
    v_plan::text,
    v_desc::text;
end;
$$;


-- ── 7. SUBJECT ACCESS CHECK ────────────────────────────────
-- Returns true if the user can access a given subject
create or replace function public.can_access_subject(
  p_user_id  uuid,
  p_subject  text
)
returns boolean language plpgsql security definer as $$
declare
  v_plan   text;
  v_status text;
  v_count  int;
begin
  -- Get subscription state
  select plan, status into v_plan, v_status
  from public.subscriptions
  where user_id = p_user_id;

  -- No subscription = free plan (1 subject only)
  if v_plan is null then v_plan := 'free'; end if;
  if v_status not in ('active', 'trialing') then return false; end if;

  -- Check if subject is in their selections
  select count(*) into v_count
  from public.subject_selections
  where user_id = p_user_id and subject_id = p_subject;

  return v_count > 0;
end;
$$;


-- ── 8. EXPLICIT GRANTS (required from Oct 2026 for PostgREST) ──────────────
-- These allow supabase-js / the Data API to access your tables.
-- anon      = unauthenticated visitors (landing page pricing display)
-- authenticated = logged-in students (RLS policies further restrict what they see)
-- service_role  = your backend functions + Edge Function (bypasses RLS, full access)

-- profiles
grant select, update                    on public.profiles           to authenticated;
grant select, insert, update, delete    on public.profiles           to service_role;

-- subscriptions
grant select                            on public.subscriptions      to authenticated;
grant select, insert, update, delete    on public.subscriptions      to service_role;

-- subject_selections
grant select, insert, delete            on public.subject_selections to authenticated;
grant select, insert, update, delete    on public.subject_selections to service_role;

-- pricing_config
grant select                            on public.pricing_config     to anon;
grant select                            on public.pricing_config     to authenticated;
grant select, insert, update, delete    on public.pricing_config     to service_role;


-- ── 9. AI MARKING QUOTA — Migration (run once) ─────────────────
-- Add AI quota columns to subscriptions table.
-- Run this in Supabase SQL Editor → Dashboard → SQL Editor.

alter table public.subscriptions
  add column if not exists ai_marks_used    integer     not null default 0,
  add column if not exists ai_marks_reset_at timestamptz default now();

-- Safe increment RPC (avoids race conditions when concurrent tabs submit answers)
create or replace function public.increment_ai_marks(p_user_id uuid)
returns void language sql security definer as $$
  update public.subscriptions
  set    ai_marks_used = ai_marks_used + 1,
         updated_at    = now()
  where  user_id = p_user_id;
$$;
