# Git Hooks Documentation - File Regression Prevention System

## Overview

This system prevents accidental file truncations and suspicious deletions that can occur during:

- AI agent refactoring (the most common cause)
- Merge conflict resolution
- Large file edits
- Automated code generation

## Installation

### Quick Install

```bash
# From project root
bash .githooks/install-hooks.sh
```

### Manual Install

```bash
# Copy hooks to .git/hooks
cp .githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## What It Checks

### 1. **Critical Errors** (Blocks Commit)

These will **prevent the commit** from proceeding:

#### Empty File Detection

- **Trigger**: File that had content becomes 0 lines
- **Example**: `comprehensive_metadata_engine.py` (3,801 → 0 lines)

#### Severe Truncation

- **Trigger**: File > 500 lines becomes < 50 lines
- **Example**: `db.ts` (1,127 → 3 lines)
- **Threshold**: File reduced to < 50 lines when it was > 500 lines

#### Massive Deletion

- **Trigger**: > 80% of file deleted
- **Example**: File loses 3,700+ out of 3,800 lines (97% deletion)

### 2. **Warnings** (Allows Commit with Review)

These will **warn but allow** the commit after a 3-second delay:

#### Significant Deletion

- **Trigger**: > 50% of file deleted
- **Example**: File goes from 1,000 → 400 lines (60% reduction)

## Hook Output Examples

### ✅ No Issues

```bash
🔍 Running pre-commit regression checks...

📊 Analyzing 5 staged files...

✅ Pre-commit checks passed
```

### ❌ Critical Issue (Blocked)

```bash
🔍 Running pre-commit regression checks...

❌ CRITICAL: Large file severely truncated
   File: server/extractor/comprehensive_metadata_engine.py
   Was: 3801 lines → Now: 83 lines
   Lost: 3718 lines (97%)

═══════════════════════════════════════════════════════════════

📋 SUMMARY:
   Critical issues: 1

🚫 COMMIT BLOCKED

Critical file truncations detected. This usually indicates:
  • Accidental file deletion/truncation
  • AI agent edit failure (common with large files)
  • Merge conflict resolution error

Affected files:
  - server/extractor/comprehensive_metadata_engine.py

To review the changes:
  git diff --cached server/extractor/comprehensive_metadata_engine.py

To restore from previous commit:
  git checkout HEAD -- server/extractor/comprehensive_metadata_engine.py

To bypass this check (NOT RECOMMENDED):
  git commit --no-verify
```

### ⚠️ Warning (Allowed with Delay)

```bash
🔍 Running pre-commit regression checks...

⚠️  WARNING: Significant deletion
   File: server/routes/extraction.ts
   Was: 1200 lines → Now: 550 lines
   Lost: 650 lines (54%)

═══════════════════════════════════════════════════════════════

📋 SUMMARY:
   Warnings: 1

⚠️  Warnings detected but commit allowed

Please review these files carefully before pushing:
  - server/routes/extraction.ts

Press Ctrl+C to cancel, or wait 3 seconds to continue...

✅ Pre-commit checks passed
```

## Configuration

Edit thresholds in `.githooks/pre-commit`:

```bash
# Thresholds
MIN_LINES_TO_CHECK=100    # Only check files >= 100 lines
DELETION_THRESHOLD=50     # Warn if > 50% deleted
CRITICAL_SIZE=50          # Error if becomes < 50 lines (when was > 500)
SUSPICIOUS_RATIO=80       # Error if > 80% deleted
```

## Common Scenarios

### Scenario 1: AI Agent Truncation (Most Common)

**What happened**: AI tried to edit a large file but truncated it instead, leaving a comment like "rest of file will be preserved"

**Detection**:

```
❌ CRITICAL: Large file severely truncated
   File: comprehensive_metadata_engine.py
   Was: 3801 lines → Now: 83 lines
```

**Resolution**:

```bash
# Restore the file
git checkout HEAD -- server/extractor/comprehensive_metadata_engine.py

# Or restore from specific commit
git show bc9c57d:server/extractor/comprehensive_metadata_engine.py > server/extractor/comprehensive_metadata_engine.py
```

### Scenario 2: Legitimate Large Refactor

**What happened**: You actually want to delete/refactor a large portion of a file

**Detection**:

```
⚠️  WARNING: Significant deletion
   File: old-implementation.ts
   Was: 2000 lines → Now: 800 lines
```

**Resolution**:

```bash
# Review the changes carefully
git diff --cached old-implementation.ts

# If intentional, wait 3 seconds and commit proceeds
# Or bypass: git commit --no-verify (use sparingly)
```

### Scenario 3: File Replacement

**What happened**: Replacing implementation with newer, smaller version

**Options**:

1. **Split the commit**: Delete old file, add new file separately
2. **Bypass hook**: Use `--no-verify` with good commit message
3. **Adjust thresholds**: Lower `DELETION_THRESHOLD` temporarily

## Bypassing the Hook

### When to Bypass

- ✅ Intentional large refactoring
- ✅ Replacing implementation with better approach
- ✅ Removing deprecated code
- ❌ **Never** bypass for unreviewed changes
- ❌ **Never** bypass if you're unsure why files changed

### How to Bypass

```bash
# Skip all pre-commit hooks
git commit --no-verify -m "Intentional refactor"

# Or disable temporarily
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled
git commit -m "Your message"
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
```

## Testing the Hook

### Test 1: Simulate Truncation

```bash
# Create a large test file
seq 1 1000 > test-large.txt
git add test-large.txt
git commit -m "Add large file"

# Truncate it
echo "truncated" > test-large.txt
git add test-large.txt
git commit -m "Test truncation"
# Should BLOCK with critical error
```

### Test 2: Simulate Warning

```bash
# Create file with 200 lines
seq 1 200 > test-medium.txt
git add test-medium.txt
git commit -m "Add medium file"

# Remove 60% (keep 80 lines)
seq 1 80 > test-medium.txt
git add test-medium.txt
git commit -m "Test warning"
# Should WARN but allow after 3 seconds
```

## Troubleshooting

### Hook Not Running

```bash
# Check if hook is installed
ls -la .git/hooks/pre-commit

# Reinstall
bash .githooks/install-hooks.sh

# Verify it's executable
chmod +x .git/hooks/pre-commit
```

### Hook Running Slowly

- The hook only checks **modified** files > 100 lines
- Typical runtime: < 1 second for 10-20 files
- If slow, increase `MIN_LINES_TO_CHECK` threshold

### False Positives

**Problem**: Hook blocks legitimate changes

**Solutions**:

1. Review the specific file: `git diff --cached <file>`
2. Adjust thresholds in `.githooks/pre-commit`
3. Use `--no-verify` with detailed commit message
4. Split large refactors into smaller commits

## Integration with CI/CD

You can run the same checks in CI:

```yaml
# .github/workflows/check-regressions.yml
name: Check for File Regressions

on: [pull_request]

jobs:
  check-regressions:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0 # Need full history

      - name: Run regression check
        run: |
          # Get changed files in PR
          git diff --name-only origin/main...HEAD > changed_files.txt

          # Run similar checks
          bash .githooks/pre-commit
```

## Maintenance

### Regular Reviews

- Monthly: Review hook effectiveness
- After incidents: Adjust thresholds if needed
- Team feedback: Gather developer feedback on false positives

### Updating Thresholds

Based on your codebase:

- **Large codebase**: Increase `MIN_LINES_TO_CHECK` to 200-500
- **Strict protection**: Lower `DELETION_THRESHOLD` to 30-40%
- **Lenient**: Increase `CRITICAL_SIZE` to 100

## Best Practices

### For Developers

1. ✅ **Always review hook output** - Don't blindly bypass
2. ✅ **Use `git diff --cached`** - Check what's actually staged
3. ✅ **Smaller commits** - Easier to review and less likely to trigger
4. ✅ **Document bypasses** - If using `--no-verify`, explain in commit message
5. ❌ **Never auto-commit** large refactors without review

### For AI Agents

1. **Limit edit scope** - Edit small sections at a time
2. **Verify line counts** - Check file size before and after
3. **Use replace tools carefully** - Include sufficient context
4. **Test incrementally** - Commit working changes frequently
5. **Flag large edits** - Warn user before attempting large file edits

## Statistics & Monitoring

Track hook effectiveness:

```bash
# Count blocked commits (from git reflog)
git reflog | grep "commit (blocked)" | wc -l

# List files frequently triggering warnings
git log --all --grep="Significant deletion" --oneline
```

## Support

If you encounter issues:

1. Check this documentation
2. Review `.githooks/pre-commit` script
3. Test with `git commit --no-verify` to isolate issue
4. Report persistent problems to team lead

## Version History

- **v1.0** (Jan 6, 2026): Initial implementation
  - Detects file truncations
  - Blocks critical issues
  - Warns on significant deletions
