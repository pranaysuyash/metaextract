#!/usr/bin/env bash
set -euo pipefail

FRONTEND=0
BACKEND=0

if [ "$#" -eq 0 ]; then
  FRONTEND=1
  BACKEND=1
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --frontend)
      FRONTEND=1
      ;;
    --backend)
      BACKEND=1
      ;;
    -h|--help)
      echo "Usage: $0 [--frontend] [--backend]"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1"
      exit 1
      ;;
  esac
  shift
done

if [ "$FRONTEND" -eq 1 ]; then
  echo "== Frontend =="
  npm ci --prefer-offline --no-audit
  npm run check
  npm run lint
  npm run test:ci
  npm run build
fi

if [ "$BACKEND" -eq 1 ]; then
  echo "== Backend =="
  python -m pip install --upgrade pip
  python -m pip install uv
  # Use frozen sync; try dev group then fall back
  uv sync --frozen --dev || uv sync --frozen
  uv run ruff check . || true
  uv run pytest -q
fi
