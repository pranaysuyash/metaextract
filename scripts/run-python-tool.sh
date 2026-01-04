#!/usr/bin/env bash
set -euo pipefail

# run-python-tool.sh
# Detects and activates a repository venv (VIRTUAL_ENV, .venv, venv, env) or uses poetry, then runs the provided command.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage: run-python-tool.sh <command...>
Runs the given command with the repository virtualenv activated, if one is found.
Environment options:
  RUN_VENV=/path/to/venv    Use explicit venv path

Examples:
  ./run-python-tool.sh python -m pip list
  ./run-python-tool.sh npx -y pyright
USAGE
  exit 1
}

if [ "$#" -lt 1 ]; then
  usage
fi

# Allow override
if [ -n "${RUN_VENV:-}" ] && [ -f "$RUN_VENV/bin/activate" ]; then
  VENV_PATH="$RUN_VENV"
fi

# Search common venv locations
if [ -z "${VENV_PATH:-}" ]; then
  candidates=()
  [ -n "${VIRTUAL_ENV:-}" ] && candidates+=("$VIRTUAL_ENV")
  candidates+=("$REPO_ROOT/.venv" "$REPO_ROOT/venv" "$REPO_ROOT/env")

  for c in "${candidates[@]}"; do
    if [ -f "$c/bin/activate" ]; then
      VENV_PATH="$c"
      break
    fi
  done
fi

if [ -n "${VENV_PATH:-}" ]; then
  echo "Using venv: $VENV_PATH"
  # shellcheck disable=SC1090
  source "$VENV_PATH/bin/activate"
  exec "$@"
else
  # Fallback to poetry if present
  if command -v poetry >/dev/null 2>&1 && [ -f "$REPO_ROOT/pyproject.toml" ]; then
    echo "No venv found; using 'poetry run' (poetry detected)"
    exec poetry run "$@"
  fi

  echo "No venv detected; running command directly"
  exec "$@"
fi
