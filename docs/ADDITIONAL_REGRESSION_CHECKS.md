# Additional Regression Prevention Checks

Beyond file truncation detection, here are regression checks categorized by type:

## 🎯 High Priority (Recommended)

### 1. **Syntax Validation**

Prevents broken code from being committed.

```bash
# Pre-commit check
- Python: python -m py_compile
- TypeScript: tsc --noEmit
- JavaScript: eslint
```

**What it catches:**

- ❌ Syntax errors
- ❌ Type errors
- ❌ Import errors
- ❌ Undefined variables

**Implementation:**

```bash
# .githooks/pre-commit-syntax
for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$'); do
    python -m py_compile "$file" || exit 1
done

for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.tsx\?$'); do
    npx tsc --noEmit "$file" || exit 1
done
```

### 2. **Import Validation**

Catches missing/broken imports before runtime.

**What it catches:**

- ❌ Missing imports: `from missing_module import func`
- ❌ Circular dependencies
- ❌ Unused imports (code smell)

**Implementation:**

```bash
# Check Python imports
python -c "import sys; sys.path.insert(0, 'server'); import $MODULE" 2>&1 | grep -i "importerror\|modulenotfounderror"

# Check TypeScript imports
npx tsc --noEmit --skipLibCheck
```

### 3. **Test Existence Check**

Ensures tests exist for modified code.

**What it catches:**

- ❌ New features without tests
- ❌ Deleted test files
- ❌ Test files not updated with code changes

**Implementation:**

```bash
# Check if modified .py file has corresponding test
for file in $(git diff --cached --name-only | grep -E '^server/.*\.py$' | grep -v test); do
    test_file="tests/$(basename $file | sed 's/\.py$/_test.py/')"
    if [ ! -f "$test_file" ]; then
        echo "⚠️  WARNING: No test found for $file"
    fi
done
```

### 4. **Critical Function Detection**

Warns when critical functions are modified/deleted.

**What it catches:**

- ❌ Deletion of public API functions
- ❌ Breaking changes to critical paths
- ❌ Removal of error handlers

**Implementation:**

```bash
# Check for removed function definitions
git diff --cached | grep -E "^-\s*(def|function|export (function|const))" | while read line; do
    echo "⚠️  Function removed: $line"
done
```

---

## 🔧 Medium Priority (Valuable)

### 5. **Dependency Changes**

Monitors package additions/removals.

**What it catches:**

- ❌ Accidentally committed package updates
- ❌ Vulnerable dependencies
- ❌ License incompatibilities

**Implementation:**

```bash
# Check package.json changes
if git diff --cached --name-only | grep -q "package.json"; then
    echo "⚠️  WARNING: package.json modified"
    git diff --cached package.json | grep -E "^\+.*\".*\":" | head -5
    echo "Review dependency changes carefully"
fi
```

### 6. **Database Migration Check**

Ensures migrations are reversible and tested.

**What it catches:**

- ❌ Breaking schema changes
- ❌ Missing down migrations
- ❌ Data loss migrations

**Implementation:**

```bash
# Check for new migration files
for file in $(git diff --cached --name-only | grep -E 'migrations/.*\.(sql|ts)$'); do
    if ! grep -q "down\|rollback" "$file"; then
        echo "⚠️  WARNING: Migration $file may not be reversible"
    fi
done
```

### 7. **Configuration Validation**

Validates config files before commit.

**What it catches:**

- ❌ Invalid JSON/YAML
- ❌ Missing required fields
- ❌ Secrets accidentally committed

**Implementation:**

```bash
# Validate JSON files
for file in $(git diff --cached --name-only | grep '\.json$'); do
    jq empty "$file" 2>/dev/null || echo "❌ Invalid JSON: $file"
done

# Check for secrets
git diff --cached | grep -iE "(api_key|password|secret|token).*=.*['\"]" && echo "⚠️  Possible secret detected"
```

### 8. **TODO/FIXME Tracking**

Prevents accumulation of technical debt.

**What it catches:**

- ❌ New TODOs without tickets
- ❌ Unresolved FIXMEs in critical code

**Implementation:**

```bash
# Count new TODOs
NEW_TODOS=$(git diff --cached | grep -E "^\+.*TODO" | wc -l)
if [ "$NEW_TODOS" -gt 3 ]; then
    echo "⚠️  WARNING: Adding $NEW_TODOS new TODOs"
fi
```

---

## 📊 Advanced (CI/CD)

### 9. **Code Coverage Regression**

Prevents test coverage from decreasing.

**What it catches:**

- ❌ Coverage dropping below threshold
- ❌ New code without tests

**Implementation:**

```bash
# Run tests with coverage
pytest --cov=server --cov-report=json
NEW_COVERAGE=$(jq '.totals.percent_covered' coverage.json)

# Compare with main branch
git checkout main -- coverage.json
OLD_COVERAGE=$(jq '.totals.percent_covered' coverage.json)

if (( $(echo "$NEW_COVERAGE < $OLD_COVERAGE" | bc -l) )); then
    echo "❌ Coverage decreased: $OLD_COVERAGE% → $NEW_COVERAGE%"
    exit 1
fi
```

### 10. **Performance Regression**

Detects performance degradation.

**What it catches:**

- ❌ Slower API endpoints
- ❌ Memory leaks
- ❌ N+1 queries

**Implementation:**

```bash
# Run performance benchmarks
pytest tests/performance/ --benchmark-only --benchmark-json=bench.json

# Compare with baseline
python scripts/compare_benchmarks.py bench.json baseline.json
```

### 11. **API Contract Validation**

Ensures backward compatibility.

**What it catches:**

- ❌ Breaking API changes
- ❌ Changed response schemas
- ❌ Removed endpoints

**Implementation:**

```bash
# Compare OpenAPI spec
diff <(git show main:api-spec.yml) api-spec.yml | grep -E "^[<>].*paths:" && echo "⚠️  API paths changed"
```

### 12. **Bundle Size Check**

Monitors frontend bundle growth.

**What it catches:**

- ❌ Large dependency additions
- ❌ Unminified code
- ❌ Duplicated dependencies

**Implementation:**

```bash
# Build and check size
npm run build
NEW_SIZE=$(du -sh dist/ | awk '{print $1}')
echo "Bundle size: $NEW_SIZE"

# Compare with threshold
if [ "$NEW_SIZE" -gt 5000000 ]; then
    echo "⚠️  Bundle exceeds 5MB"
fi
```

---

## 🎨 Project-Specific Checks

### For MetaExtract Specifically:

### 13. **Metadata Extractor Registration**

Ensures new extractors are registered.

```bash
# Check if new extractor is registered
for file in $(git diff --cached --name-only | grep -E 'server/extractor/.*_extractor\.py$'); do
    extractor_name=$(basename "$file" _extractor.py)
    if ! grep -q "$extractor_name" server/extractor/comprehensive_metadata_engine.py; then
        echo "⚠️  WARNING: New extractor '$extractor_name' may not be registered"
    fi
done
```

### 14. **Field Schema Validation**

Verifies metadata field definitions match schema.

```bash
# Check field definitions
python scripts/validate_schema.py --check-fields
```

### 15. **Extraction Pipeline Integrity**

Ensures extraction flow isn't broken.

```bash
# Test critical extraction paths
python -c "from server.extractor.comprehensive_metadata_engine import extract_comprehensive_metadata; print('✅ Import successful')"
```

---

## 📋 Recommended Implementation Priority

### Phase 1: Immediate (This Week)

1. ✅ **File truncation** (DONE)
2. **Syntax validation** - Prevents broken commits
3. **Import validation** - Catches runtime errors early

### Phase 2: Short-term (Next Sprint)

4. **Critical function detection** - Protects core APIs
5. **Configuration validation** - Prevents config errors
6. **Dependency changes** - Monitors package updates

### Phase 3: Medium-term (This Month)

7. **Test existence check** - Improves coverage
8. **Database migration check** - Prevents schema issues
9. **Metadata extractor registration** - Project-specific

### Phase 4: Long-term (Ongoing)

10. **Code coverage regression** - CI/CD integration
11. **Performance regression** - Benchmark tracking
12. **API contract validation** - Breaking change detection

---

## 🛠️ Implementation Options

### Option A: Single Comprehensive Hook

Combine all checks into one `.githooks/pre-commit` file with flags:

```bash
#!/bin/bash
# .githooks/pre-commit

# Configuration
ENABLE_SYNTAX_CHECK=true
ENABLE_IMPORT_CHECK=true
ENABLE_TEST_CHECK=false
ENABLE_FUNCTION_CHECK=true

# Run checks based on flags...
```

### Option B: Modular Hook System

Separate hooks for different check types:

```
.githooks/
├── pre-commit                 # Master orchestrator
├── hooks.d/
│   ├── 01-file-size.sh       # Current truncation check
│   ├── 02-syntax.sh          # Syntax validation
│   ├── 03-imports.sh         # Import checks
│   ├── 04-functions.sh       # Critical function check
│   └── 05-config.sh          # Config validation
```

### Option C: CI/CD Only

Run heavier checks in GitHub Actions:

```yaml
# .github/workflows/regression-checks.yml
name: Regression Checks
on: [pull_request]

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - name: Syntax Check
        run: npm run type-check

      - name: Test Coverage
        run: npm run test:coverage

      - name: Performance Benchmark
        run: npm run bench
```

---

## 💡 Recommendations for Your Project

Based on your recent file truncation issue and project structure:

### Must Have (Week 1):

1. ✅ **File truncation check** - Already done
2. **Python syntax validation** - Prevents import errors in extraction engine
3. **TypeScript type checking** - Catches frontend errors

### Should Have (Week 2-3):

4. **Import validation** - Especially for extraction modules
5. **Critical function detection** - Protect `extract_comprehensive_metadata()`
6. **Config validation** - Validate `docker-compose.yml`, `tsconfig.json`

### Nice to Have (Month 1):

7. **Test coverage check** - Ensure extraction tests exist
8. **Database migration check** - Protect schema changes
9. **Dependency monitoring** - Track `package.json` changes

---

## 🚀 Quick Start: Add Syntax Validation Now

Want to implement syntax checking immediately?

```bash
# Add to .githooks/pre-commit (after line 167)

echo ""
echo "🔍 Running syntax checks..."

# Python syntax
PYTHON_ERRORS=0
for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$'); do
    if [ -f "$file" ]; then
        python -m py_compile "$file" 2>/dev/null || {
            echo "❌ SYNTAX ERROR: $file"
            PYTHON_ERRORS=$((PYTHON_ERRORS + 1))
        }
    fi
done

# TypeScript syntax (if tsconfig exists)
if [ -f "tsconfig.json" ]; then
    npx tsc --noEmit 2>&1 | head -20 || {
        echo "❌ TypeScript errors found"
        exit 1
    }
fi

if [ "$PYTHON_ERRORS" -gt 0 ]; then
    echo ""
    echo "❌ COMMIT BLOCKED: Fix $PYTHON_ERRORS Python syntax error(s)"
    exit 1
fi

echo "✅ Syntax checks passed"
```

Would you like me to:

1. **Implement syntax validation** (Python + TypeScript checking)
2. **Add import validation** (catch missing module errors)
3. **Create modular hook system** (separate checks in hooks.d/)
4. **Set up CI/CD checks** (GitHub Actions for heavier checks)
5. **Add project-specific checks** (metadata extractor registration)

Which checks are most important for your workflow?
