#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8010}"
HOST="${2:-127.0.0.1}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== SmartClasse dev launcher =="
echo "1) Démarrage du backend via Docker"
"$REPO_ROOT/scripts/start_backend.sh" "$PORT" "$HOST"

echo
echo "2) Backend prêt. Lance maintenant le client Flutter dans un autre terminal:"
echo "   cd \"$REPO_ROOT/flutter_client\""
echo "   flutter run -d chrome"
echo
echo "Si tu veux une exécution complète en une seule fenêtre, ouvre un second terminal pour Flutter après ce script."