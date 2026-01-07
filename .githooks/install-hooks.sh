#!/bin/bash
# Script to install git hooks

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$PROJECT_ROOT/.githooks"
GIT_HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

echo "Installing MetaExtract git hooks..."
echo ""

# Check if .git directory exists
if [ ! -d "$GIT_HOOKS_DIR" ]; then
    echo "Error: Not a git repository. Run this from the project root."
    exit 1
fi

# Install pre-commit hook
if [ -f "$HOOKS_DIR/pre-commit" ]; then
    echo "📋 Installing pre-commit hook..."
    cp "$HOOKS_DIR/pre-commit" "$GIT_HOOKS_DIR/pre-commit"
    chmod +x "$GIT_HOOKS_DIR/pre-commit"
    echo "✅ pre-commit hook installed"
else
    echo "⚠️  pre-commit hook not found in .githooks/"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ Git hooks installation complete!"
echo ""
echo "Installed hooks:"
echo "  • pre-commit: Detects file truncations and suspicious deletions"
echo ""
echo "To bypass hooks (not recommended):"
echo "  git commit --no-verify"
echo ""
