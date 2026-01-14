#!/usr/bin/env bash
set -euo pipefail

BASE_REF="${BASE_REF:-origin/main}"

echo "== Gate starting =="
echo "Base ref: $BASE_REF"

bash scripts/ci/check-branch-name.sh
bash scripts/ci/check-pr-size.sh
bash scripts/ci/check-pr-loc.sh

if [ "${ALLOW_BACKEND_CHANGES:-0}" != "1" ]; then
  bash scripts/ci/check-backend-changes.sh || echo "WARNING: backend path changes detected (advisory in solo)."
else
  echo "ALLOW_BACKEND_CHANGES=1 set, skipping backend guard."
fi

npm test
npm run test:e2e:smoke

echo "== Gate passed =="
