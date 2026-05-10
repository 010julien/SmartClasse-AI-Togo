#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(dirname "$(dirname "${BASH_SOURCE[0]}")")
exec python "$ROOT_DIR/scripts/package_submission.py"
