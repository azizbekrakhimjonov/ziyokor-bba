create table if not exists public.bba_state (id int primary key, data jsonb not null default '{}'::jsonb, updated_at timestamptz not null default now());
grant all on public.bba_state to service_role;
alter table public.bba_state enable row level security;