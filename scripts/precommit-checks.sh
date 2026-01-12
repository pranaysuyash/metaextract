#!/usr/bin/env bash
set -euo pipefail

# Ensure all changes are staged
git add -A

# Count total staged line changes (added + removed)
staged_lines=$(git diff --cached --numstat | awk '{added+=$1; removed+=$2} END{print added+removed+0}')
threshold=200

echo "Precommit: staged change lines = ${staged_lines} (threshold ${threshold})"

# Always run typecheck + unit tests first
echo "Running TypeScript check..."
npm run check --silent || { echo "TypeScript check failed"; exit 1; }

echo "Running unit tests..."
npx jest --runInBand --silent || { echo "Unit tests failed"; exit 1; }

if [ "${staged_lines}" -ge "${threshold}" ]; then
  echo "Large change detected; running functional Playwright smoke tests..."
  # Run a focused Playwright test (dropzone + quick smoke tests)
  npx playwright test tests/e2e/images-mvp.dropzone.spec.ts --workers=1 --timeout=60000 || {
    echo "Functional (Playwright) smoke tests failed"; exit 1;
  }
fi

echo "Precommit checks passed."