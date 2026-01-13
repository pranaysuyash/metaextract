#!/usr/bin/env python3
"""
Naming Convention Validator for MetaExtract

This script validates file names and function names against the project's
naming conventions defined in NAMING_CONVENTIONS.md.

Usage:
    python scripts/validate_naming.py --all              # Validate all files
    python scripts/validate_naming.py --file <path>      # Validate single file
    python scripts/validate_naming.py --report           # Generate detailed report
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of a naming validation check."""
    file_path: str
    is_valid: bool
    violations: List[str] = field(default_factory=list)
    severity: str = "error"


FORBIDDEN_PATTERNS = [
    (r'ultimate', 'Contains "ultimate" - use descriptive names instead'),
    (r'complete', 'Contains "complete" - use version numbers if needed'),
    (r'\bmega\b', 'Contains "mega" - use descriptive adjectives'),
    (r'\bultra\b', 'Contains "ultra" - use specific descriptors'),
    (r'\bmassive\b', 'Contains "massive" - use size indicators if needed'),
    (r'advanced_extension', 'Contains "advanced_extension" - describe extension'),
    (r'extension_[ivxlcdm]+$', 'Uses Roman numerals - use descriptive names'),
]

ROMAN_NUMERAL_PATTERN = r'extension_([ivxlcdm]+)$'
MODULE_PATTERN = re.compile(r'^[a-z][a-z0-9_]*\.py$')
MAX_NAME_LENGTH = 30


class NamingValidator:
    """Validates naming conventions for files and functions."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[ValidationResult] = []

    def validate_file_name(self, file_path: str) -> ValidationResult:
        """Validate a single file name."""
        result = ValidationResult(file_path=file_path, is_valid=True)
        filename = os.path.basename(file_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        if not filename.endswith('.py'):
            return result
        
        for pattern, message in FORBIDDEN_PATTERNS:
            if re.search(pattern, name_without_ext, re.IGNORECASE):
                result.violations.append(message)
                result.is_valid = False
                result.severity = 'error'
        
        if re.search(ROMAN_NUMERAL_PATTERN, name_without_ext):
            result.violations.append('Uses Roman numerals - rename to descriptive name')
            result.is_valid = False
            result.severity = 'error'
        
        if re.search(r'[A-Z]', filename):
            result.violations.append('Contains uppercase - use lowercase with underscores')
            result.is_valid = False
            result.severity = 'error'
        
        if ' ' in filename or '-' in filename:
            result.violations.append('Contains spaces or hyphens - use underscores')
            result.is_valid = False
            result.severity = 'error'
        
        if len(name_without_ext) > MAX_NAME_LENGTH:
            result.violations.append(f'Name length ({len(name_without_ext)}) exceeds max ({MAX_NAME_LENGTH})')
            result.is_valid = False
            result.severity = 'warning'
        
        if not MODULE_PATTERN.match(filename):
            result.violations.append('Does not match pattern (lowercase with underscores)')
            result.is_valid = False
            result.severity = 'warning'
        
        return result

    def validate_file_content(self, file_path: str) -> Optional[ValidationResult]:
        """Validate function names inside a file."""
        if not os.path.exists(file_path) or not file_path.endswith('.py'):
            return None
        
        result = ValidationResult(file_path=file_path, is_valid=True)
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            function_pattern = r'def\s+(\w+)\s*\('
            for match in re.finditer(function_pattern, content):
                func_name = match.group(1)
                
                # Skip alias functions (backward compatibility aliases)
                # These are functions that contain _ultimate_advanced_extension_ or end with Roman numerals
                if '_ultimate_advanced_extension_' in func_name:
                    continue
                if re.search(r'extension_[ivxlcdm]+$', func_name):
                    continue
                
                for pattern, message in FORBIDDEN_PATTERNS:
                    if re.search(pattern, func_name, re.IGNORECASE):
                        result.violations.append(f'Function "{func_name}": {message}')
                        result.is_valid = False
                        result.severity = 'error'
                
                roman_match = re.search(ROMAN_NUMERAL_PATTERN, func_name)
                if roman_match:
                    result.violations.append(f'Function "{func_name}" uses Roman numeral')
                    result.is_valid = False
                    result.severity = 'error'
        
        except Exception:
            pass
        
        return result

    def validate_directory(self, directory: str) -> List[ValidationResult]:
        """Validate all files in a directory."""
        results = []
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'node_modules', '.git', 'venv', '.venv']]
            
            for filename in files:
                file_path = os.path.join(root, filename)
                
                file_result = self.validate_file_name(file_path)
                if file_result.violations:
                    results.append(file_result)
                
                if filename.endswith('.py'):
                    content_result = self.validate_file_content(file_path)
                    if content_result and content_result.violations:
                        results.append(content_result)
        
        return results

    def print_results(self, results: List[ValidationResult]):
        """Print validation results."""
        if not results:
            print("\n✅ No naming violations found!")
            return
        
        print(f"\n{'='*70}")
        print("📋 NAMING VALIDATION RESULTS")
        print(f"{'='*70}")
        
        error_count = sum(1 for r in results if r.severity == 'error')
        warning_count = sum(1 for r in results if r.severity == 'warning')
        
        print(f"\nTotal issues: {len(results)}")
        print(f"  ❌ Errors: {error_count}")
        print(f"  ⚠️  Warnings: {warning_count}")
        
        if self.verbose:
            for result in results:
                status = "❌" if result.severity == 'error' else "⚠️"
                print(f"\n{status} {result.file_path}")
                for violation in result.violations:
                    print(f"   - {violation}")
        
        print(f"\n{'='*70}")

    def generate_report(self, results: List[ValidationResult], output_file: str = None) -> Dict:
        """Generate a detailed JSON report."""
        report = {
            'summary': {
                'total_issues': len(results),
                'errors': sum(1 for r in results if r.severity == 'error'),
                'warnings': sum(1 for r in results if r.severity == 'warning'),
            },
            'violations': []
        }
        
        for result in results:
            report['violations'].append({
                'file': result.file_path,
                'severity': result.severity,
                'violations': result.violations
            })
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to: {output_file}")
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Validate naming conventions')
    parser.add_argument('--all', '-a', action='store_true', help='Validate all files')
    parser.add_argument('--file', '-f', type=str, help='Validate single file')
    parser.add_argument('--dir', '-d', type=str, help='Validate directory')
    parser.add_argument('--report', '-r', action='store_true', help='Generate JSON report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    parser.add_argument('--output', '-o', type=str, default='naming_report.json', help='Report output file')
    
    args = parser.parse_args()
    validator = NamingValidator(verbose=args.verbose)
    results = []
    
    if args.all:
        results = validator.validate_directory('.')
    elif args.file:
        file_result = validator.validate_file_name(args.file)
        if file_result.violations:
            results.append(file_result)
    elif args.dir:
        results = validator.validate_directory(args.dir)
    else:
        results = validator.validate_directory('server/extractor/modules')
    
    validator.print_results(results)
    
    if args.report:
        validator.generate_report(results, args.output)
    
    error_count = sum(1 for r in results if r.severity == 'error')
    if error_count > 0:
        print(f"\n❌ Found {error_count} naming convention errors!")
        sys.exit(1)
    else:
        print("\n✅ All naming conventions satisfied!")
        sys.exit(0)


if __name__ == '__main__':
    main()
