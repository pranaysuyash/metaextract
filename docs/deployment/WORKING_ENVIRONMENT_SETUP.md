# MetaExtract Working Environment Setup

## 🎯 Quick Start Guide

This guide ensures you're using the **existing project venv** and proper environment setup for MetaExtract development and testing.

## ✅ **Prerequisites Check**

### 1. Verify Venv Exists
```bash
cd /Users/pranay/Projects/metaextract
ls -la .venv/bin/python
# Should show: lrwxr-xr-x 1 pranay staff 85 [date] .venv/bin/python -> /Users/pranay/.local/share/uv/python/cpython-3.11.9-macos-aarch64-none/bin/python3.11
```

### 2. Verify Python Version
```bash
source .venv/bin/activate
python --version
# Should show: Python 3.11.9
```

## 🔧 **Proper Environment Setup**

### Step 1: Activate the Project Venv (CRITICAL)
```bash
# Navigate to project root
cd /Users/pranay/Projects/metaextract

# Activate the EXISTING project venv
source .venv/bin/activate

# Verify activation
which python
# Should show: /Users/pranay/Projects/metaextract/.venv/bin/python
```

### Step 2: Install Dependencies (If Needed)
```bash
# With venv activated
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install
```

### Step 3: Environment Variables
```bash
# Copy environment template if needed
cp .env.example .env.local

# Edit with your configuration
nano .env.local
```

### Step 4: Database Setup (If Needed)
```bash
# With venv activated
source .venv/bin/activate

# Run database migrations
psql $DATABASE_URL -f server/db/schema.sql

# Or use the improved setup
psql $DATABASE_URL -f server/db/quota-schema.sql
```

## 🚀 **Development Workflow**

### Starting the Development Server
```bash
# ALWAYS activate venv first
source .venv/bin/activate

# Start backend server
npm run dev:server

# In another terminal, start frontend
npm run dev
```

### Testing Authentication (With Venv)
```bash
# Activate venv
source .venv/bin/activate

# Run authentication tests
node test_auth_endpoints.js

# Or comprehensive test suite
npm test
```

### Python Testing (With Venv)
```bash
# Activate venv
source .venv/bin/activate

# Run Python tests
pytest tests/ -v

# Run specific auth tests
pytest tests/unit/test_complete_authentication_system.py -v
```

## 🧪 **Current Authentication Testing**

### Quick Auth Test (Verified Working)
```bash
# With venv activated and server running
source .venv/bin/activate

# Test registration
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "password": "TestPass123!"}'

# Test login  
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}'

# Test profile (use token from login response)
curl -X GET http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📊 **Environment Verification**

### Check Current Status
```bash
# With venv activated
source .venv/bin/activate

# Check server health
curl -s http://localhost:3000/health | jq .

# Check database connection
node -e "console.log('Database:', process.env.DATABASE_URL ? 'Connected' : 'Not configured')"

# Check Redis connection  
node -e "console.log('Redis:', process.env.REDIS_URL ? 'Connected' : 'Using memory')"
```

### Check Authentication Status
```bash
# With venv activated
source .venv/bin/activate

# Check auth system mode
node -e "
const { db } = require('./server/db');
console.log('Auth Mode:', db ? 'Database Authentication' : 'Mock Authentication');
"
```

## 🔍 **Troubleshooting**

### Venv Not Working
```bash
# If venv is corrupted, recreate it
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Server Not Starting
```bash
# Check logs
tail -f server.log

# Check environment
source .venv/bin/activate
node -e "console.log('JWT_SECRET:', process.env.JWT_SECRET ? 'Set' : 'Missing')"
```

### Database Issues
```bash
# Test database connection
source .venv/bin/activate
psql $DATABASE_URL -c "SELECT current_database(), current_user;"

# Check database schema
psql $DATABASE_URL -c "\\dt"
```

### Authentication Issues
```bash
# Check auth routes
curl -s http://localhost:3000/api/auth/me | head -20

# Test with verbose output
curl -v http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "debug@example.com", "username": "debug", "password": "DebugPass123!"}'
```

## 📁 **File Structure (Current)**

### Authentication Files
```
server/auth.ts              # Main authentication system (ACTIVE)
server/auth-enhanced.ts     # Advanced features (2FA, etc.)
server/auth-mock.ts         # Development mock system
client/src/lib/auth.tsx     # React auth context
client/src/components/auth-modal.tsx  # Auth UI
```

### Test Files
```
test_complete_authentication_system.py    # Comprehensive auth tests
test_quota_enforcement.js                 # Quota system tests
final_verification.js                     # System verification
debug_quota.js                           # Debug utilities
```

### Documentation
```
CURRENT_AUTH_STATUS_REPORT.md            # Current status (LIVE)
AUTH_SYSTEM_TODOS.md                     # Future improvements
QUOTA_ENFORCEMENT_IMPLEMENTATION.md      # Quota system docs
```

## 🎯 **Current Working Features**

### ✅ **Verified Working**
- [x] User registration with JWT tokens
- [x] User login with secure authentication
- [x] Profile access via `/api/auth/me`
- [x] Token refresh functionality
- [x] Logout with cookie clearing
- [x] Database authentication (not mock)
- [x] Rate limiting with Redis
- [x] Quota enforcement system

### 🔧 **Development Commands**
```bash
# With venv activated ALWAYS
source .venv/bin/activate

# Development
npm run dev                 # Start both frontend and backend
npm run dev:server          # Backend only
npm run dev:client          # Frontend only

# Testing
npm test                    # Run all tests
pytest tests/              # Python tests
node test_token_cookie.js  # Auth tests

# Linting & Formatting
npm run lint               # JavaScript/TypeScript linting
npm run lint:fix           # Auto-fix linting issues
```

---

## ⚠️ **CRITICAL REMINDERS**

1. **ALWAYS activate venv first**: `source .venv/bin/activate`
2. **Check server logs** if issues arise: `tail -f server.log`
3. **Verify auth system mode**: Should show "Database authentication system"
4. **Test authentication** before assuming it works
5. **Keep documentation updated** with your changes

**Status**: 🎯 **ENVIRONMENT CONFIGURED & READY FOR DEVELOPMENT**