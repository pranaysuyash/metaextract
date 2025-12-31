# CI/CD Pipeline Configuration

## Overview
This document describes the continuous integration and continuous deployment pipeline configured for the MetaExtract project. The pipeline automates testing, linting, type checking, and security scanning across both frontend and backend codebases.

## Pipeline Architecture

### Jobs

#### 1. Frontend Build and Test
**Purpose**: Validate all frontend code changes

**Steps**:
1. Checkout repository
2. Setup Node.js (v20)
3. Install dependencies (`npm ci`)
4. TypeScript compilation check (`npm run check`)
5. ESLint validation (`npm run lint`)
6. Jest tests with coverage (`npm test -- --ci --coverage`)
7. Upload coverage to Codecov

**Coverage Areas**:
- TypeScript compilation
- Code quality (ESLint)
- Unit tests (126+ tests)
- Test coverage reporting

#### 2. Backend Python Tests
**Purpose**: Validate all backend code changes

**Steps**:
1. Checkout repository
2. Setup Python (v3.11)
3. Install dependencies (`pip install -e ".[dev]"`)
4. Ruff linting
5. Pytest unit tests
6. Phase 2 integration tests
7. Upload coverage to Codecov

**Coverage Areas**:
- Python linting
- Unit tests
- Integration tests
- Coverage reporting

#### 3. Security Checks
**Purpose**: Identify security vulnerabilities early

**Steps**:
1. Checkout repository
2. Setup Node.js
3. Install dependencies
4. npm audit (high severity)
5. Snyk security scan

**Tools**:
- **npm audit**: Built-in Node.js security scanner
- **Snyk**: Advanced security scanning for known vulnerabilities

**Note**: Snyk scan uses `continue-on-error: true` to not block merges on non-critical findings.

#### 4. Integration Tests
**Purpose**: Verify frontend and backend work together

**Steps**:
1. Checkout repository
2. Setup Python and Node.js
3. Install all dependencies
4. Run integration test suite

**Dependencies**:
- Runs after frontend and backend jobs complete
- Ensures cross-stack compatibility

#### 5. Summary
**Purpose**: Generate human-readable pipeline summary

**Steps**:
1. Runs after all other jobs
2. Generates markdown summary
3. Provides overview of all checks

## Trigger Conditions

### Push Triggers
- `main` branch
- `master` branch
- `develop` branch

### Pull Request Triggers
- `main` branch
- `master` branch
- `develop` branch

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NODE_VERSION` | Node.js version (20) |
| `PYTHON_VERSION` | Python version (3.11) |
| `SNYK_TOKEN` | Authentication for Snyk security scanning |

## Caching

### Node.js Cache
- **Location**: `~/.npm`
- **Key**: Based on `package-lock.json` hash
- **Purpose**: Speed up dependency installation

### Python Cache
- **Location**: ~/.pip
- **Key**: Based on `pyproject.toml` hash
- **Purpose**: Speed up pip installation

## Test Configuration

### Frontend Tests
**Location**: `client/src/**/*.test.tsx`
**Runner**: Jest
**Command**: `npm test -- --ci --coverage --watchAll=false`

**Coverage Thresholds** (from `jest.config.cjs`):
- Branches: 50%
- Functions: 50%
- Lines: 50%
- Statements: 50%

### Backend Tests
**Location**: `tests/**/*.py`
**Runner**: pytest
**Command**: `pytest -q`

## Quality Gates

### Must Pass
1. TypeScript compilation
2. ESLint validation
3. Jest tests
4. Pytest tests

### Non-Blocking
1. Code coverage (thresholds are informational)
2. Security scans (warnings only)
3. Integration tests (informational)

## Artifact Publishing

### Coverage Reports
- **Frontend**: Codecov (`frontend-coverage` flag)
- **Backend**: Codecov (`backend-coverage` flag)

### Coverage Files
- `coverage/lcov.info` - Machine-readable coverage data
- `coverage/` - HTML coverage reports

## Troubleshooting

### Common Issues

#### Frontend Build Fails
```bash
# Run locally to debug
npm run check
npm run lint
npm test
```

#### Backend Tests Fail
```bash
# Run locally to debug
pytest -q
ruff check .
```

#### TypeScript Errors
```bash
# Check TypeScript compilation
npm run check
```

#### ESLint Errors
```bash
# Check linting
npm run lint
npm run lint:fix
```

## Adding New Jobs

### Example: Add Docker Build Job

```yaml
docker:
  name: Docker Build
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Build Docker image
      run: docker build -t metaextract:${{ github.sha }} .
```

### Example: Add Deployment Job

```yaml
deploy:
  name: Deploy to Staging
  runs-on: ubuntu-latest
  needs: [frontend, backend, integration]
  if: github.ref == 'refs/heads/main'
  steps:
    - name: Deploy to staging
      run: ./scripts/deploy.sh staging
```

## Pipeline Metrics

### Current Test Coverage
- **Frontend**: 126+ tests passing
- **Backend**: 200+ tests passing
- **Total**: 326+ tests

### Build Time Targets
- **Frontend**: < 2 minutes
- **Backend**: < 3 minutes
- **Full Pipeline**: < 5 minutes

## Related Documentation
- [Frontend Unit Tests](./FRONTEND_UNIT_TESTS.md) - Test documentation
- [TypeScript Fixes](./TYPESCRIPT_FIXES_FRONTEND.md) - TypeScript configuration
- [ESLint Setup](./ESLINT_SETUP_FRONTEND.md) - Code quality standards

## Author
CI/CD pipeline configured as part of MetaExtract quality assurance initiative.

## Date
December 31, 2025
