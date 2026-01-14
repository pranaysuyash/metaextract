# File Regression Prevention System

## Quick Start

```bash
# Install the hooks (one-time setup)
bash .githooks/install-hooks.sh

# That's it! The hook will now run automatically on every commit
```

## What This Prevents

This system prevents the **exact regression that happened to your codebase** where AI agents truncated critical files:

- ✅ **`comprehensive_metadata_engine.py`** - 3,801 lines → 83 lines ❌ (PREVENTED)
- ✅ **`db.ts`** - 1,127 lines → 3 lines ❌ (PREVENTED)

## How It Works

### Pre-Commit Hook

Runs automatically before each commit and checks for:

| Issue                    | Threshold                           | Action                           |
| ------------------------ | ----------------------------------- | -------------------------------- |
| **Empty file**           | File becomes 0 lines                | 🚫 Block commit                  |
| **Severe truncation**    | File > 500 lines becomes < 50 lines | 🚫 Block commit                  |
| **Massive deletion**     | > 80% of file deleted               | 🚫 Block commit                  |
| **Significant deletion** | > 50% of file deleted               | ⚠️ Warn (allows commit after 3s) |

### Example Output

```bash
❌ CRITICAL: Large file severely truncated
   File: server/extractor/comprehensive_metadata_engine.py
   Was: 3801 lines → Now: 83 lines
   Lost: 3718 lines (97%)

🚫 COMMIT BLOCKED

To restore from previous commit:
  git checkout HEAD -- server/extractor/comprehensive_metadata_engine.py
```

## Files Created

```
.githooks/
├── pre-commit              # Main hook script
├── install-hooks.sh        # Installation script
└── README.md              # This file

docs/
└── GIT_HOOKS_DOCUMENTATION.md  # Detailed documentation

client/src/components/
├── animated-theme-provider.tsx  # Now implemented
└── dashboard-layout.tsx         # Now implemented
```

## Testing the Hook

### Test 1: Create and Truncate a File

```bash
# Create a large test file
seq 1 1000 > test-truncation.txt
git add test-truncation.txt
git commit -m "Add test file"

# Truncate it (this should be blocked)
echo "oops" > test-truncation.txt
git add test-truncation.txt
git commit -m "Test truncation"

# Expected: COMMIT BLOCKED ✅
```

### Test 2: Legitimate Large Deletion

```bash
# Create medium file
seq 1 200 > test-refactor.txt
git add test-refactor.txt
git commit -m "Add medium file"

# Remove 60% (warning zone)
seq 1 80 > test-refactor.txt
git add test-refactor.txt
git commit -m "Refactor"

# Expected: WARNING (allows after 3s) ⚠️
```

## Bypassing When Needed

**Only bypass if you're CERTAIN the deletion is intentional:**

```bash
# Option 1: Skip hook for one commit
git commit --no-verify -m "Intentional refactor: removed legacy code"

# Option 2: Temporarily disable hook
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled
git commit -m "Your commit"
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
```

## Configuration

Edit `.githooks/pre-commit` to adjust thresholds:

```bash
MIN_LINES_TO_CHECK=100    # Only check files >= 100 lines
DELETION_THRESHOLD=50     # Warn if > 50% deleted
CRITICAL_SIZE=50          # Block if becomes < 50 lines (when was > 500)
SUSPICIOUS_RATIO=80       # Block if > 80% deleted
```

## What Changed

### Before (Empty Placeholders)

- `animated-theme-provider.tsx` - 0 lines
- `dashboard-layout.tsx` - 0 lines

### After (Fully Implemented)

- `animated-theme-provider.tsx` - 130 lines ✅
  - Smooth theme transitions
  - System preference detection
  - localStorage persistence
- `dashboard-layout.tsx` - 172 lines ✅
  - Responsive sidebar
  - Breadcrumb navigation
  - Mobile-friendly

## Documentation

See [docs/GIT_HOOKS_DOCUMENTATION.md](../docs/GIT_HOOKS_DOCUMENTATION.md) for:

- Detailed configuration options
- Troubleshooting guide
- CI/CD integration
- Best practices
- Common scenarios

## Statistics

Track effectiveness:

```bash
# Count prevented regressions
git reflog | grep "blocked" | wc -l

# List frequently warned files
git log --oneline | grep "WARNING"
```

## Support

If the hook blocks legitimate changes:

1. Review: `git diff --cached <file>`
2. Verify intentional: Check file history
3. Bypass if certain: `git commit --no-verify`
4. Report false positives: Adjust thresholds

## Maintenance

```bash
# Reinstall hooks (if upgraded)
bash .githooks/install-hooks.sh

# Test hook is working
git commit --allow-empty -m "Test hook"

# Check hook status
ls -la .git/hooks/pre-commit
```

---

**🎉 Regression prevention is now active!**

Your codebase is protected from accidental file truncations.
