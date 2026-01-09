#!/usr/bin/env bash
set -euo pipefail

BASE_REF="${BASE_REF:-origin/main}"

MAX_FILES="${MAX_FILES:-60}"
MAX_ADDED="${MAX_ADDED:-800}"
MAX_DELETED="${MAX_DELETED:-800}"
MAX_CHURN="${MAX_CHURN:-1200}"

EXCLUDE_REGEX="${EXCLUDE_REGEX:-^(package-lock\\.json|yarn\\.lock|pnpm-lock\\.yaml|dist/|build/|coverage/|node_modules/|.*\\.snap)$}"

echo "LOC guard against $BASE_REF"
echo "Limits: files=$MAX_FILES added=$MAX_ADDED deleted=$MAX_DELETED churn=$MAX_CHURN"
echo "Exclude regex: $EXCLUDE_REGEX"

CHANGED_FILES=$(
  git diff --name-only "$BASE_REF"...HEAD \
    | grep -Ev "$EXCLUDE_REGEX" || true
)

FILE_COUNT=0
if [ -n "${CHANGED_FILES// }" ]; then
  FILE_COUNT=$(echo "$CHANGED_FILES" | sed '/^\s*$/d' | wc -l | tr -d ' ')
fi

ADDED=0
DELETED=0

while IFS=$'\t' read -r a d path; do
  [ -z "${path:-}" ] && continue
  echo "$path" | grep -Eq "$EXCLUDE_REGEX" && continue

  if [ "$a" != "-" ]; then ADDED=$((ADDED + a)); fi
  if [ "$d" != "-" ]; then DELETED=$((DELETED + d)); fi
done < <(git diff --numstat "$BASE_REF"...HEAD)

CHURN=$((ADDED + DELETED))

echo "Changed files: $FILE_COUNT"
echo "Added lines: $ADDED"
echo "Deleted lines: $DELETED"
echo "Churn: $CHURN"

HEAD_SHA=$(git rev-parse HEAD)
if [ "${CI:-false}" != "true" ] && [ "${ALLOW_BIG_CHANGE:-0}" = "1" ] && [ "${ALLOW_BIG_CHANGE_SHA:-}" = "$HEAD_SHA" ]; then
  echo "OVERRIDE: ALLOW_BIG_CHANGE=1 for HEAD $HEAD_SHA. LOC guard bypassed."
  exit 0
fi

FAILED=0
if [ "$FILE_COUNT" -gt "$MAX_FILES" ]; then
  echo "FAIL: too many files changed"
  FAILED=1
fi
if [ "$ADDED" -gt "$MAX_ADDED" ]; then
  echo "FAIL: too many lines added"
  FAILED=1
fi
if [ "$DELETED" -gt "$MAX_DELETED" ]; then
  echo "FAIL: too many lines deleted"
  FAILED=1
fi
if [ "$CHURN" -gt "$MAX_CHURN" ]; then
  echo "FAIL: too much churn"
  FAILED=1
fi

if [ "$FAILED" -ne 0 ]; then
  echo ""
  echo "Action: split the PR or get explicit override (label large-change + extra approval)."
  exit 1
fi

echo "OK: LOC guard passed."
