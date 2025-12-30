#!/usr/bin/env bash
set -euo pipefail

# Developer environment setup script
# Creates a venv and installs the package in editable mode with dev extras
VENV_DIR=".venv"
python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
python -m pip install -e .[dev]

# Install pre-commit hooks if available
if command -v pre-commit >/dev/null 2>&1; then
    pre-commit install || true
fi

echo "\nDev environment ready. Activate with: source $VENV_DIR/bin/activate"
