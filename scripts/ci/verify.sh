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
  # Assumes workflow already ran `npm ci` — verify script only runs checks
  npm run check
  npm run lint
  npm run test:ci
  npm run build
fi

if [ "$BACKEND" -eq 1 ]; then
  echo "== Backend =="
  # Assumes workflow already installed deps via `uv sync` — verify script only runs checks/tests
  if [ -d server ]; then
    pushd server >/dev/null
    uv run ruff check . || true
    uv run pytest -q
    popd >/dev/null
  else
    uv run ruff check . || true
    uv run pytest -q
  fi
fi
