-- Oddiy SQLite: DB Browser yoki sqlite3 CLI da ishga tushiring.
-- Fayl: data/bba.sqlite (yoki o‘zingiz tanlagan .sqlite fayl)
--
--   sqlite3 data/bba.sqlite < scripts/sqlite-setup.sql
--
-- Admin: admin / admin123 | O'quvchi: demo / demo123

CREATE TABLE IF NOT EXISTS bba_state (
  id INTEGER PRIMARY KEY,
  data TEXT NOT NULL DEFAULT '{}',
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

INSERT INTO bba_state (id, data, updated_at)
SELECT
  1,
  '{"adm":{"u":"admin","p":"admin123"},"st":[{"login":"demo","pass":"demo123","name":"Namuna O''quvchi","sid":1}],"qs":[],"res":[],"dur":90,"vars":[],"act":null}',
  datetime('now')
WHERE NOT EXISTS (SELECT 1 FROM bba_state WHERE id = 1);

UPDATE bba_state
SET
  data = '{"adm":{"u":"admin","p":"admin123"},"st":[{"login":"demo","pass":"demo123","name":"Namuna O''quvchi","sid":1}],"qs":[],"res":[],"dur":90,"vars":[],"act":null}',
  updated_at = datetime('now')
WHERE id = 1
  AND (
    data = '{}'
    OR data IS NULL
    OR (instr(data, '"adm"') = 0 AND (json_array_length(json_extract(data, '$.st')) IS NULL OR json_array_length(json_extract(data, '$.st')) = 0))
  );
