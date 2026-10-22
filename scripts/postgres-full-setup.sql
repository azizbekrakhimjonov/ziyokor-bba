-- PostgreSQL: jadval + boshlang'ich loginlar (Supabase kerak emas).
-- Admin: admin / admin123 | Namuna o'quvchi: demo / demo123

create table if not exists public.bba_state (
  id int primary key,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

insert into public.bba_state (id, data, updated_at)
select
  1,
  '{
    "adm": {"u": "admin", "p": "admin123"},
    "st": [
      {"login": "demo", "pass": "demo123", "name": "Namuna O''quvchi", "sid": 1}
    ],
    "qs": [],
    "res": [],
    "dur": 90,
    "vars": [],
    "act": null
  }'::jsonb,
  now()
where not exists (select 1 from public.bba_state where id = 1);

update public.bba_state
set
  data = '{
    "adm": {"u": "admin", "p": "admin123"},
    "st": [
      {"login": "demo", "pass": "demo123", "name": "Namuna O''quvchi", "sid": 1}
    ],
    "qs": [],
    "res": [],
    "dur": 90,
    "vars": [],
    "act": null
  }'::jsonb,
  updated_at = now()
where id = 1
  and (
    data = '{}'::jsonb
    or data is null
    or (not (data ? 'adm') and coalesce(jsonb_array_length(data -> 'st'), 0) = 0)
  );
