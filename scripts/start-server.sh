#!/usr/bin/env sh
# Production server (loyiha ildizi yoki release/bba-server papkasidan ishga tushiring).
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/.output/server/index.mjs" ]; then
  ROOT="$SCRIPT_DIR"
elif [ -f "$SCRIPT_DIR/../.output/server/index.mjs" ]; then
  ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
else
  echo "Xato: .output/server/index.mjs topilmadi ($SCRIPT_DIR)."
  exit 1
fi
cd "$ROOT"

if [ -f "$ROOT/.env" ]; then
  # shellcheck disable=SC1091
  set -a
  . "$ROOT/.env"
  set +a
fi

export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8080}"
export BBA_SQLITE_PATH="${BBA_SQLITE_PATH:-./data/bba.sqlite}"

if [ ! -f "$ROOT/.output/server/index.mjs" ]; then
  echo "Xato: .output/server/index.mjs topilmadi."
  echo "  Loyiha kodidan: bun run build"
  echo "  Yoki serverda to‘liq repodan build qiling (Mac build → Linux server ishlamaydi)."
  exit 1
fi

case "$BBA_SQLITE_PATH" in
  ./*) SQLITE_ABS="$ROOT/${BBA_SQLITE_PATH#./}" ;;
  /*) SQLITE_ABS="$BBA_SQLITE_PATH" ;;
  *) SQLITE_ABS="$ROOT/$BBA_SQLITE_PATH" ;;
esac
mkdir -p "$(dirname "$SQLITE_ABS")"

SQLITE_MOD="$ROOT/.output/server/node_modules/better-sqlite3"
if ! node -e "require('$SQLITE_MOD')(':memory:').close()" 2>/dev/null; then
  echo "better-sqlite3 bu mashinada yuklanmadi (boshqa OS/archda build qilingan bo‘lishi mumkin)."
  if command -v npm >/dev/null 2>&1; then
    echo "Qayta yig‘ish: cd .output/server && npm rebuild better-sqlite3"
    (cd "$ROOT/.output/server" && npm rebuild better-sqlite3) || {
      echo "Rebuild muvaffaqiyatsiz. Serverda build-essential/python3 o‘rnating yoki repodan qayta build qiling."
      exit 1
    }
  else
    echo "npm topilmadi. Serverda loyihani qayta build qiling: bun install && bun run build"
    exit 1
  fi
fi

echo "BBA: http://${HOST}:${PORT}  SQLite: ${BBA_SQLITE_PATH}"
exec node "$ROOT/.output/server/index.mjs"
