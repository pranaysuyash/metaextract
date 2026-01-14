#!/usr/bin/env bash
set -euo pipefail

BRANCH_NAME="${BRANCH_NAME:-}"

if [ -z "$BRANCH_NAME" ]; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    BRANCH_NAME="$(git rev-parse --abbrev-ref HEAD)"
  fi
fi

if [ -z "$BRANCH_NAME" ]; then
  echo "Unable to determine branch name."
  exit 1
fi

if [ "$BRANCH_NAME" = "main" ] || [ "$BRANCH_NAME" = "master" ]; then
  echo "FAIL: direct work on '$BRANCH_NAME' is not allowed."
  exit 1
fi

if [[ ! "$BRANCH_NAME" =~ ^(feat|chore|audit|fix|hotfix)/[a-z0-9._-]+$ ]]; then
  echo "FAIL: branch name '$BRANCH_NAME' does not match required pattern."
  echo "Expected: feat/<area>-<change>, chore/<area>-<change>, or audit/<reason>"
  exit 1
fi

echo "OK: branch name '$BRANCH_NAME' is valid."
