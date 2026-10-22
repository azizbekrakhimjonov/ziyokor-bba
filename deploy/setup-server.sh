#!/usr/bin/env bash
# Loyiha ildizi: .../ziyokor-bba (deploy/ dan bir daraja yuqori)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mode="${1:-install}"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -U pip
pip install -q -r requirements.txt
python manage.py migrate --noinput
mkdir -p data staticfiles
chmod +x deploy/setup-server.sh 2>/dev/null || true

if [[ "$mode" == "install" ]]; then
  exit 0
fi

exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-7583}" --workers 2 --threads 4 --timeout 120
