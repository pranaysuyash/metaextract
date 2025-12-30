#!/usr/bin/env python3
"""
Exception Handler Fixer

This script identifies bare exception handlers (except: or except Exception:)
and suggests improvements. Run with --fix to automatically fix simple cases.

Usage:
    python scripts/fix_exceptions.py                    # Analyze only
    python scripts/fix_exceptions.py --fix             # Fix and create backup
    python scripts/fix_exceptions.py --file path.py   # Analyze specific file
"""

import ast
import sys
import os
import re
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ExceptionIssue:
    """Represents a found exception handling issue."""
    file: str
    line: int
    col: int
    issue_type: str
    context: str
    suggestion: str
    can_auto_fix: bool


class ExceptionAnalyzer(ast.NodeVisitor):
    """AST visitor to find exception handling issues."""

    def __init__(self, filename: str, source: str):
        self.filename = filename
        self.source = source
        self.lines = source.splitlines()
        self.issues: List[ExceptionIssue] = []

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # Check for bare except
        if node.type is None:
            self.issues.append(ExceptionIssue(
                file=self.filename,
                line=node.lineno,
                col=node.col_offset,
                issue_type="bare_except",
                context=self._get_context(node.lineno),
                suggestion="Add specific exception type: except Exception as e:",
                can_auto_fix=False
            ))

        # Check for except Exception with pass
        elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
            body_is_pass = (
                len(node.body) == 1 and isinstance(node.body[0], ast.Pass)
            )
            body_is_none_return = (
                len(node.body) == 1 and
                isinstance(node.body[0], ast.Return) and
                node.body[0].value is None
            )

            if body_is_pass:
                self.issues.append(ExceptionIssue(
                    file=self.filename,
                    line=node.lineno,
                    col=node.col_offset,
                    issue_type="exception_pass",
                    context=self._get_context(node.lineno),
                    suggestion="Add logging: logger.debug(f'Handled exception: {e}')",
                    can_auto_fix=True
                ))
            elif body_is_none_return:
                self.issues.append(ExceptionIssue(
                    file=self.filename,
                    line=node.lineno,
                    col=node.col_offset,
                    issue_type="exception_return_none",
                    context=self._get_context(node.lineno),
                    suggestion="Consider logging before returning None",
                    can_auto_fix=False
                ))
            elif not node.name:
                self.issues.append(ExceptionIssue(
                    file=self.filename,
                    line=node.lineno,
                    col=node.col_offset,
                    issue_type="exception_no_name",
                    context=self._get_context(node.lineno),
                    suggestion="Capture exception: except Exception as e:",
                    can_auto_fix=True
                ))

        self.generic_visit(node)

    def _get_context(self, lineno: int) -> str:
        """Get surrounding code context."""
        start = max(0, lineno - 2)
        end = min(len(self.lines), lineno + 2)
        context_lines = self.lines[start:end]
        return "\n".join(f"  {start + i + 1}: {line}" for i, line in enumerate(context_lines))


def analyze_file(filepath: str) -> List[ExceptionIssue]:
    """Analyze a single Python file for exception handling issues."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}")
        return []

    analyzer = ExceptionAnalyzer(filepath, source)
    analyzer.visit(tree)
    return analyzer.issues


def analyze_directory(directory: str, exclude_dirs: Optional[List[str]] = None) -> List[ExceptionIssue]:
    """Analyze all Python files in a directory."""
    if exclude_dirs is None:
        exclude_dirs = ["venv", "node_modules", "__pycache__", ".git", "dist"]

    all_issues = []
    path = Path(directory)

    for py_file in path.rglob("*.py"):
        # Skip excluded directories
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue

        issues = analyze_file(str(py_file))
        all_issues.extend(issues)

    return all_issues


def fix_file(filepath: str, issues: List[ExceptionIssue], create_backup: bool = True) -> int:
    """
    Fix auto-fixable issues in a file.

    Returns:
        Number of fixes applied.
    """
    fixable = [i for i in issues if i.can_auto_fix and i.file == filepath]
    if not fixable:
        return 0

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Create backup
    if create_backup:
        backup_path = filepath + ".bak"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    fixes_applied = 0

    # Sort by line number descending to fix from bottom up (avoids line number shifts)
    fixable.sort(key=lambda i: i.line, reverse=True)

    for issue in fixable:
        line_idx = issue.line - 1
        if line_idx >= len(lines):
            continue

        line = lines[line_idx]

        if issue.issue_type == "exception_pass":
            # Add logging instead of pass
            indent = len(line) - len(line.lstrip())
            indent_str = " " * indent

            # Check if exception variable exists
            match = re.match(r"(\s*)except\s+Exception\s*(as\s+\w+)?:", line)
            if match:
                var_name = "e"
                if match.group(2):
                    var_match = re.match(r"as\s+(\w+)", match.group(2))
                    if var_match:
                        var_name = var_match.group(1)
                else:
                    # Need to add variable name
                    line = re.sub(r"except Exception:", f"except Exception as {var_name}:", line)
                    lines[line_idx] = line

                # Find the pass statement and replace it
                for i in range(line_idx + 1, min(line_idx + 5, len(lines))):
                    if re.match(r"\s*pass\s*$", lines[i]):
                        inner_indent = len(lines[i]) - len(lines[i].lstrip())
                        lines[i] = " " * inner_indent + f"pass  # TODO: Consider logging: logger.debug(f'Handled exception: {{{var_name}}}')\n"
                        fixes_applied += 1
                        break

        elif issue.issue_type == "exception_no_name":
            # Add exception variable
            new_line = re.sub(r"except Exception:", "except Exception as e:", line)
            if new_line != line:
                lines[line_idx] = new_line
                fixes_applied += 1

    # Write fixed file
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return fixes_applied


def print_report(issues: List[ExceptionIssue]):
    """Print a formatted report of issues."""
    if not issues:
        print("No exception handling issues found!")
        return

    print(f"\n{'='*80}")
    print(f"EXCEPTION HANDLING ISSUES REPORT")
    print(f"{'='*80}\n")

    # Group by file
    by_file = {}
    for issue in issues:
        if issue.file not in by_file:
            by_file[issue.file] = []
        by_file[issue.file].append(issue)

    # Statistics
    total = len(issues)
    by_type = {}
    auto_fixable = 0
    for issue in issues:
        by_type[issue.issue_type] = by_type.get(issue.issue_type, 0) + 1
        if issue.can_auto_fix:
            auto_fixable += 1

    print("SUMMARY")
    print("-" * 40)
    print(f"Total issues found: {total}")
    print(f"Auto-fixable: {auto_fixable}")
    print(f"Files affected: {len(by_file)}")
    print("\nBy type:")
    for issue_type, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {issue_type}: {count}")

    print(f"\n{'='*80}")
    print("DETAILED ISSUES")
    print(f"{'='*80}\n")

    for filepath, file_issues in sorted(by_file.items()):
        print(f"\n{filepath}")
        print("-" * len(filepath))

        for issue in sorted(file_issues, key=lambda i: i.line):
            fix_indicator = "[AUTO-FIXABLE] " if issue.can_auto_fix else ""
            print(f"\n  {fix_indicator}Line {issue.line}: {issue.issue_type}")
            print(f"  Suggestion: {issue.suggestion}")
            print(f"\n  Context:")
            print(issue.context)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and fix exception handling issues in Python files"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Specific file to analyze (default: analyze entire server/extractor directory)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix simple issues (creates backup files)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create backup files when fixing"
    )
    parser.add_argument(
        "--directory",
        type=str,
        default="server/extractor",
        help="Directory to analyze (default: server/extractor)"
    )

    args = parser.parse_args()

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    if args.file:
        filepath = Path(args.file)
        if not filepath.is_absolute():
            filepath = project_root / filepath
        issues = analyze_file(str(filepath))
    else:
        directory = project_root / args.directory
        if not directory.exists():
            print(f"Error: Directory {directory} not found")
            sys.exit(1)
        issues = analyze_directory(str(directory))

    print_report(issues)

    if args.fix and issues:
        print(f"\n{'='*80}")
        print("APPLYING FIXES")
        print(f"{'='*80}\n")

        total_fixes = 0
        files_fixed = set()

        for issue in issues:
            if issue.can_auto_fix:
                if issue.file not in files_fixed:
                    file_issues = [i for i in issues if i.file == issue.file]
                    fixes = fix_file(
                        issue.file,
                        file_issues,
                        create_backup=not args.no_backup
                    )
                    if fixes > 0:
                        total_fixes += fixes
                        files_fixed.add(issue.file)
                        print(f"Fixed {fixes} issues in {issue.file}")

        print(f"\nTotal fixes applied: {total_fixes}")
        print(f"Files modified: {len(files_fixed)}")

        if not args.no_backup and files_fixed:
            print("\nBackup files created with .bak extension")


if __name__ == "__main__":
    main()
