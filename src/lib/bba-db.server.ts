import fs from "node:fs";
import path from "node:path";

import Database from "better-sqlite3";

const DEFAULT_SEED = {
  adm: { u: "admin", p: "admin123" },
  st: [{ login: "demo", pass: "demo123", name: "Namuna O'quvchi", sid: 1 }],
  qs: [] as unknown[],
  res: [] as unknown[],
  dur: 90,
  vars: [] as unknown[],
  act: null as null,
};

let db: Database.Database | undefined;

function sqlitePath(): string {
  const raw =
    process.env.BBA_SQLITE_PATH ||
    process.env.DATABASE_URL ||
    "./data/bba.sqlite";
  if (raw.startsWith("postgresql://") || raw.startsWith("postgres://")) {
    throw new Error("PostgreSQL o‘rniga SQLite fayl yo‘lini qo‘ying (masalan: ./data/bba.sqlite).");
  }
  return path.resolve(raw.replace(/^file:/, ""));
}

function getDb(): Database.Database {
  if (db) return db;
  const file = sqlitePath();
  fs.mkdirSync(path.dirname(file), { recursive: true });
  db = new Database(file);
  db.pragma("journal_mode = WAL");
  db.exec(`
    CREATE TABLE IF NOT EXISTS bba_state (
      id INTEGER PRIMARY KEY,
      data TEXT NOT NULL DEFAULT '{}',
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);
  seedIfNeeded(db);
  return db;
}

function seedIfNeeded(database: Database.Database): void {
  const row = database.prepare("SELECT data FROM bba_state WHERE id = 1").get() as
    | { data: string }
    | undefined;
  if (!row) {
    database
      .prepare("INSERT INTO bba_state (id, data, updated_at) VALUES (1, ?, datetime('now'))")
      .run(JSON.stringify(DEFAULT_SEED));
    return;
  }
  let parsed: Record<string, unknown>;
  try {
    parsed = JSON.parse(row.data || "{}") as Record<string, unknown>;
  } catch {
    parsed = {};
  }
  const st = parsed.st as unknown[] | undefined;
  const empty =
    !parsed.adm && (!Array.isArray(st) || st.length === 0);
  if (empty || row.data === "{}" || !row.data) {
    database
      .prepare(
        "UPDATE bba_state SET data = ?, updated_at = datetime('now') WHERE id = 1",
      )
      .run(JSON.stringify(DEFAULT_SEED));
  }
}

function parseData(raw: string | undefined): unknown | null {
  if (raw == null) return null;
  try {
    return JSON.parse(raw) as unknown;
  } catch {
    return null;
  }
}

export async function bbaGetData(id: number): Promise<unknown | null> {
  const row = getDb().prepare("SELECT data FROM bba_state WHERE id = ?").get(id) as
    | { data: string }
    | undefined;
  return row ? parseData(row.data) : null;
}

export async function bbaUpsertData(id: number, data: unknown): Promise<void> {
  getDb()
    .prepare(
      `INSERT INTO bba_state (id, data, updated_at) VALUES (?, ?, datetime('now'))
       ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at`,
    )
    .run(id, JSON.stringify(data));
}

export async function bbaDeleteId(id: number): Promise<void> {
  getDb().prepare("DELETE FROM bba_state WHERE id = ?").run(id);
}

export async function bbaDeleteFromId(minId: number): Promise<void> {
  getDb().prepare("DELETE FROM bba_state WHERE id >= ?").run(minId);
}

export async function bbaListDataFromId(minId: number): Promise<{ data: unknown }[]> {
  const rows = getDb()
    .prepare("SELECT data FROM bba_state WHERE id >= ?")
    .all(minId) as { data: string }[];
  return rows.map((r) => ({ data: parseData(r.data) }));
}
