-- Boshlang'ich ma'lumot: admin login, namuna o'quvchi va bo'sh imtihon holati (id=1).
-- Mavjud to'liq ma'lumotni ustiga yozmaydi — faqat qator yo'q yoki data bo'sh bo'lsa.

insert into public.bba_state (id, data, updated_at)
select
  1,
  jsonb_build_object(
    'adm', jsonb_build_object('u', 'admin', 'p', 'admin123'),
    'st', jsonb_build_array(
      jsonb_build_object(
        'login', 'demo',
        'pass', 'demo123',
        'name', 'Namuna O''quvchi',
        'sid', 1
      )
    ),
    'qs', '[]'::jsonb,
    'res', '[]'::jsonb,
    'dur', 90,
    'vars', '[]'::jsonb,
    'act', null
  ),
  now()
where not exists (select 1 from public.bba_state where id = 1);

update public.bba_state
set
  data = jsonb_build_object(
    'adm', jsonb_build_object('u', 'admin', 'p', 'admin123'),
    'st', jsonb_build_array(
      jsonb_build_object(
        'login', 'demo',
        'pass', 'demo123',
        'name', 'Namuna O''quvchi',
        'sid', 1
      )
    ),
    'qs', '[]'::jsonb,
    'res', '[]'::jsonb,
    'dur', 90,
    'vars', '[]'::jsonb,
    'act', null
  ),
  updated_at = now()
where id = 1
  and (
    data = '{}'::jsonb
    or data is null
    or (not (data ? 'adm') and coalesce(jsonb_array_length(data -> 'st'), 0) = 0)
  );
