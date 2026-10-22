#!/usr/bin/env sh
# Builddan keyin serverga yuklash uchun release/ papkasini yig‘adi.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -f .output/server/index.mjs ]; then
  echo "Avval build: bun run build"
  exit 1
fi

OUT="$ROOT/release/bba-server"
rm -rf "$OUT"
mkdir -p "$OUT"

cp -R .output "$OUT/.output"
cp scripts/start-server.sh "$OUT/start-server.sh"
chmod +x "$OUT/start-server.sh"
cp .env.example "$OUT/.env.example"
mkdir -p "$OUT/data"

cat > "$OUT/README-DEPLOY.txt" <<'EOF'
Serverga joylash (Linux tavsiya etiladi)

1) release/bba-server papkasini serverga nusxalang (scp/rsync).
2) Serverda Node.js 20+ o‘rnating.
3) cp .env.example .env  — kerak bo‘lsa PORT va BBA_SQLITE_PATH ni o‘zgartiring.
4) ./start-server.sh

MUHIM:
- Faqat .output ni alohida olib ketmang: ichida public/ ham kerak (.output/public).
- Mac/Windows da build qilib Linux serverga qo‘ysangiz, start-server.sh better-sqlite3 ni
  qayta yig‘ishga urinadi; eng ishonchli yo‘l — kodni serverga clone qilib u yerda
  bun install && bun run build && ./start-server.sh.
- data/bba.sqlite — barcha ma’lumot; backup qiling va o‘chirib yubormang.

Docker: loyiha ildizida  docker build -t bba .  &&  docker run -p 8080:8080 -v bba-data:/app/data bba
EOF

echo "Tayyor: $OUT"
echo "Serverga: rsync -av release/bba-server/ user@server:/opt/bba/"
