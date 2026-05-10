#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8010}"
HOST="${2:-127.0.0.1}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker-compose.yml"
HEALTH_URL="http://${HOST}:${PORT}/health"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "docker-compose.yml introuvable: $COMPOSE_FILE" >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker n'est pas disponible dans le PATH." >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Le démon Docker n'est pas disponible. Démarrez Docker Desktop puis relancez ce script." >&2
  exit 1
fi

if command -v curl >/dev/null 2>&1 && curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
  echo "Backend déjà actif sur $HEALTH_URL"
  exit 0
fi

echo "Démarrage du backend SmartClasse via Docker sur $HEALTH_URL"
docker compose -f "$COMPOSE_FILE" up --build -d backend

for _ in $(seq 1 60); do
  sleep 1
  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    echo "Backend prêt sur $HEALTH_URL"
    exit 0
  fi
done

echo "Le backend a été lancé mais n'a pas répondu dans le délai attendu." >&2
exit 1