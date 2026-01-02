#!/bin/bash

# Trial System Verification Script
# Tests the trial system implementation without requiring full Python imports

echo "=========================================================================="
echo "TRIAL SYSTEM VERIFICATION"
echo "=========================================================================="

# Test 1: Check migration script exists and is valid
echo ""
echo "=== Test 1: Migration Script ==="
if [ -f "server/migrations/002_add_trial_usage_tracking.sql" ]; then
    echo "✅ Migration script exists"

    # Check for required SQL elements
    if grep -q "CREATE TABLE IF NOT EXISTS trial_usages" server/migrations/002_add_trial_usage_tracking.sql; then
        echo "✅ Contains trial_usages table creation"
    else
        echo "❌ Missing trial_usages table creation"
    fi

    if grep -q "email TEXT NOT NULL UNIQUE" server/migrations/002_add_trial_usage_tracking.sql; then
        echo "✅ Contains email unique constraint"
    else
        echo "❌ Missing email unique constraint"
    fi

    if grep -q "CREATE INDEX.*trial_usages" server/migrations/002_add_trial_usage_tracking.sql; then
        echo "✅ Contains performance indexes"
    else
        echo "❌ Missing performance indexes"
    fi
else
    echo "❌ Migration script not found"
fi

# Test 2: Check schema definition
echo ""
echo "=== Test 2: Schema Definition ==="
if grep -q "export const trialUsages" shared/schema.ts; then
    echo "✅ trialUsages table defined in schema"
else
    echo "❌ trialUsages table not found in schema"
fi

if grep -q "email.*text.*notNull.*unique" shared/schema.ts; then
    echo "✅ Email has unique constraint in schema"
else
    echo "❌ Email unique constraint missing in schema"
fi

# Test 3: Check storage interface
echo ""
echo "=== Test 3: Storage Interface ==="
if grep -q "hasTrialUsage" server/storage.ts; then
    echo "✅ hasTrialUsage method defined"
else
    echo "❌ hasTrialUsage method not found"
fi

if grep -q "recordTrialUsage" server/storage.ts; then
    echo "✅ recordTrialUsage method defined"
else
    echo "❌ recordTrialUsage method not found"
fi

if grep -q "getTrialUsageByEmail" server/storage.ts; then
    echo "✅ getTrialUsageByEmail method defined"
else
    echo "❌ getTrialUsageByEmail method not found"
fi

# Test 4: Check route integration
echo ""
echo "=== Test 4: Route Integration ==="
if grep -q "storage.hasTrialUsage" server/routes/extraction.ts; then
    echo "✅ Routes use storage.hasTrialUsage()"
else
    echo "❌ Routes don't use storage.hasTrialUsage()"
fi

if ! grep -q "trialUsageByEmail.set" server/routes/extraction.ts; then
    echo "✅ In-memory trial map removed"
else
    echo "❌ In-memory trial map still in use"
fi

if grep -q "storage.recordTrialUsage" server/routes/extraction.ts; then
    echo "✅ Routes use storage.recordTrialUsage()"
else
    echo "❌ Routes don't use storage.recordTrialUsage()"
fi

# Test 5: Check imports and exports
echo ""
echo "=== Test 5: Module Imports/Exports ==="
if grep -q "trialUsages" shared/schema.ts; then
    echo "✅ trialUsages exported from schema"
else
    echo "❌ trialUsages not exported from schema"
fi

# Summary
echo ""
echo "=========================================================================="
echo "VERIFICATION COMPLETE"
echo "=========================================================================="

# Count successes
total_tests=13
passed_tests=0

# Simple counter based on the checks above
[ -f "server/migrations/002_add_trial_usage_tracking.sql" ] && ((passed_tests++))
grep -q "CREATE TABLE IF NOT EXISTS trial_usages" server/migrations/002_add_trial_usage_tracking.sql && ((passed_tests++))
grep -q "email TEXT NOT NULL UNIQUE" server/migrations/002_add_trial_usage_tracking.sql && ((passed_tests++))
grep -q "CREATE INDEX.*trial_usages" server/migrations/002_add_trial_usage_tracking.sql && ((passed_tests++))
grep -q "export const trialUsages" shared/schema.ts && ((passed_tests++))
grep -q "email.*text.*notNull.*unique" shared/schema.ts && ((passed_tests++))
grep -q "hasTrialUsage" server/storage.ts && ((passed_tests++))
grep -q "recordTrialUsage" server/storage.ts && ((passed_tests++))
grep -q "getTrialUsageByEmail" server/storage.ts && ((passed_tests++))
grep -q "storage.hasTrialUsage" server/routes/extraction.ts && ((passed_tests++))
! grep -q "trialUsageByEmail.set" server/routes/extraction.ts && ((passed_tests++))
grep -q "storage.recordTrialUsage" server/routes/extraction.ts && ((passed_tests++))
grep -q "trialUsages" shared/schema.ts && ((passed_tests++))

echo "Results: $passed_tests/$total_tests checks passed"

if [ $passed_tests -eq $total_tests ]; then
    echo "🎉 All verification checks passed!"
    echo ""
    echo "The trial system implementation is complete and ready for testing."
    exit 0
else
    echo "⚠️  Some checks failed - review implementation"
    exit 1
fi