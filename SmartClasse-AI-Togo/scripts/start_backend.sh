#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8010}"
HOST="${2:-127.0.0.1}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$REPO_ROOT/venv/bin/python"
HEALTH_URL="http://${HOST}:${PORT}/health"

if [[ ! -x "$PYTHON" ]]; then
  echo "Python introuvable dans le venv: $PYTHON" >&2
  exit 1
fi

if command -v curl >/dev/null 2>&1 && curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
  echo "Backend déjà actif sur $HEALTH_URL"
  exit 0
fi

echo "Démarrage du backend SmartClasse sur $HEALTH_URL"
"$PYTHON" -m uvicorn src.main:app --host "$HOST" --port "$PORT" &
PID=$!

for _ in $(seq 1 30); do
  sleep 0.5
  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    echo "Backend prêt sur $HEALTH_URL"
    exit 0
  fi
  if ! kill -0 "$PID" >/dev/null 2>&1; then
    wait "$PID" || true
    echo "Le processus uvicorn s'est arrêté prématurément." >&2
    exit 1
  fi
done

echo "Le backend a été lancé mais n'a pas répondu dans le délai attendu." >&2
exit 1