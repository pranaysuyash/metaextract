#!/usr/bin/env bash
set -euo pipefail

BASE_REF="${BASE_REF:-origin/main}"

MAX_FILE_MB="${MAX_FILE_MB:-10}"
MAX_TOTAL_MB="${MAX_TOTAL_MB:-20}"

MAX_FILE_BYTES=$((MAX_FILE_MB * 1024 * 1024))
MAX_TOTAL_BYTES=$((MAX_TOTAL_MB * 1024 * 1024))

echo "Checking PR size against $BASE_REF"
echo "Max single file: ${MAX_FILE_MB}MB, Max total changed size: ${MAX_TOTAL_MB}MB"

CHANGED_FILES=$(git diff --name-only "$BASE_REF"...HEAD)

if [ -z "$CHANGED_FILES" ]; then
  echo "No changed files."
  exit 0
fi

TOTAL_BYTES=0
FAILED=0

while IFS= read -r f; do
  if [ ! -f "$f" ]; then
    continue
  fi

  SIZE_BYTES=$(wc -c <"$f" | tr -d ' ')
  TOTAL_BYTES=$((TOTAL_BYTES + SIZE_BYTES))

  if [ "$SIZE_BYTES" -gt "$MAX_FILE_BYTES" ]; then
    echo "FAIL: $f is $(($SIZE_BYTES / 1024 / 1024))MB (limit ${MAX_FILE_MB}MB)"
    FAILED=1
  fi
done <<< "$CHANGED_FILES"

if [ "$TOTAL_BYTES" -gt "$MAX_TOTAL_BYTES" ]; then
  echo "FAIL: Total size of changed files is $(($TOTAL_BYTES / 1024 / 1024))MB (limit ${MAX_TOTAL_MB}MB)"
  FAILED=1
fi

if [ "$FAILED" -ne 0 ]; then
  echo ""
  echo "If intentional: add label allow-large-files and document the file source."
  exit 1
fi

echo "OK: PR size within limits."
