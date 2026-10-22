#!/usr/bin/env sh
set -e
cd "$(dirname "$0")/.."
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8080}"
exec sh "$(dirname "$0")/start-server.sh"
