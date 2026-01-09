#!/usr/bin/env bash
set -euo pipefail

BASE_REF="${BASE_REF:-origin/main}"
ALLOW_BACKEND_CHANGES="${ALLOW_BACKEND_CHANGES:-0}"

if [ "$ALLOW_BACKEND_CHANGES" = "1" ]; then
  echo "Backend changes allowed (ALLOW_BACKEND_CHANGES=1)."
  exit 0
fi

BACKEND_PATHS_REGEX='^(server/|shared/|init\.sql$|drizzle\.config\.ts$|requirements.*\.txt$|pyproject\.toml$)'

CHANGED_BACKEND_FILES=$(
  git diff --name-only "$BASE_REF"...HEAD \
    | grep -E "$BACKEND_PATHS_REGEX" || true
)

if [ -n "$CHANGED_BACKEND_FILES" ]; then
  echo "FAIL: backend paths modified in UI-only PR."
  echo "$CHANGED_BACKEND_FILES"
  echo ""
  echo "If backend changes are intentional, set ALLOW_BACKEND_CHANGES=1"
  echo "or apply the 'backend-change' label to the PR."
  exit 1
fi

echo "OK: no backend path changes detected."
