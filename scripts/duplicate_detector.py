#!/usr/bin/env python3
"""
Comprehensive Duplicate Detection Script for MetaExtract
Scans all metadata extraction modules to identify:
1. Duplicate field names across modules
2. Duplicate code patterns
3. Similar function definitions
4. Overlapping metadata categories
"""

import os
import re
import ast
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
import hashlib


class DuplicateDetector:
    def __init__(self, modules_dir: str):
        self.modules_dir = Path(modules_dir)
        self.all_modules = []
        self.field_definitions = defaultdict(list)  # field_name -> [(module, line_number, context)]
        self.function_definitions = defaultdict(list)  # function_name -> [(module, line_number, args)]
        self.class_definitions = defaultdict(list)  # class_name -> [(module, line_number)]
        self.import_statements = defaultdict(list)  # import -> [modules]
        self.string_literals = defaultdict(list)  # string -> [(module, line_number)]
        self.code_blocks = []  # For structural similarity
        self.duplicates_report = {
            "duplicate_fields": {},
            "duplicate_functions": {},
            "duplicate_classes": {},
            "duplicate_imports": {},
            "similar_code_blocks": [],
            "summary": {}
        }

    def scan_all_modules(self):
        """Scan all Python modules in the directory"""
        print(f"Scanning modules in: {self.modules_dir}")
        python_files = list(self.modules_dir.rglob("*.py"))
        print(f"Found {len(python_files)} Python files to scan")

        for py_file in python_files:
            self._scan_module(py_file)

    def _scan_module(self, file_path: Path):
        """Scan a single module for duplicates"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

            module_name = file_path.name
            self.all_modules.append(module_name)

            # Parse AST
            try:
                tree = ast.parse(content)
                self._extract_ast_info(tree, module_name, file_path, lines)
            except SyntaxError:
                print(f"Warning: Could not parse {module_name} - skipping AST analysis")

            # Extract field definitions (metadata fields)
            self._extract_field_definitions(content, module_name, file_path, lines)

            # Extract string literals for potential duplicate keys
            self._extract_string_literals(content, module_name, file_path, lines)

            # Extract code blocks for similarity analysis
            self._extract_code_blocks(content, module_name, file_path)

        except Exception as e:
            print(f"Error scanning {file_path}: {e}")

    def _extract_ast_info(self, tree: ast.AST, module_name: str, file_path: Path, lines: List[str]):
        """Extract information from AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function signature
                args = [arg.arg for arg in node.args.args]
                self.function_definitions[node.name].append({
                    'module': module_name,
                    'line': node.lineno,
                    'args': args,
                    'file': str(file_path)
                })
            elif isinstance(node, ast.ClassDef):
                self.class_definitions[node.name].append({
                    'module': module_name,
                    'line': node.lineno,
                    'file': str(file_path)
                })
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.import_statements[alias.name].append(module_name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        import_key = f"{node.module}.{alias.name}"
                        self.import_statements[import_key].append(module_name)

    def _extract_field_definitions(self, content: str, module_name: str, file_path: Path, lines: List[str]):
        """Extract metadata field definitions"""
        # Pattern 1: Dictionary keys with field names
        dict_key_pattern = r'["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']\s*:'
        for i, line in enumerate(lines, 1):
            matches = re.findall(dict_key_pattern, line)
            for match in matches:
                # Filter out common non-field keys
                if not self._is_common_key(match):
                    self.field_definitions[match].append({
                        'module': module_name,
                        'line': i,
                        'context': line.strip()[:100],
                        'file': str(file_path)
                    })

        # Pattern 2: Field definitions in common patterns
        field_patterns = [
            r'(\w+)\s*=\s*\{',  # Variable assignments with dicts
            r'["\'](\w+)["\']\s*:\s*\{',  # Nested dict keys
            r'fields?\s*\[\s*["\'](\w+)["\']',  # Field array access
        ]

        for pattern in field_patterns:
            for i, line in enumerate(lines, 1):
                matches = re.findall(pattern, line)
                for match in matches:
                    if not self._is_common_key(match):
                        self.field_definitions[match].append({
                            'module': module_name,
                            'line': i,
                            'context': line.strip()[:100],
                            'file': str(file_path)
                        })

    def _extract_string_literals(self, content: str, module_name: str, file_path: Path, lines: List[str]):
        """Extract string literals that might be duplicate metadata keys"""
        string_pattern = r'["\']([a-zA-Z_][a-zA-Z0-9_]{2,})["\']'
        for i, line in enumerate(lines, 1):
            matches = re.findall(string_pattern, line)
            for match in matches:
                # Only capture strings that look like metadata fields
                if len(match) >= 3 and match.islower() or '_' in match:
                    self.string_literals[match].append({
                        'module': module_name,
                        'line': i,
                        'file': str(file_path)
                    })

    def _extract_code_blocks(self, content: str, module_name: str, file_path: Path):
        """Extract code blocks for similarity analysis"""
        # Remove comments and strings to focus on code structure
        content_clean = re.sub(r'#.*', '', content)
        content_clean = re.sub(r'["\'].*?["\']', '', content_clean)

        # Extract function-sized blocks (10-50 lines)
        lines = content_clean.split('\n')
        for i in range(0, len(lines) - 10, 5):
            block = '\n'.join(lines[i:i+15])
            if len(block.strip()) > 100:  # Minimum size
                block_hash = hashlib.md5(block.encode()).hexdigest()
                self.code_blocks.append({
                    'hash': block_hash,
                    'module': module_name,
                    'start_line': i + 1,
                    'file': str(file_path),
                    'content': block[:200]  # Store sample for comparison
                })

    def _is_common_key(self, key: str) -> bool:
        """Filter out common non-field keys"""
        common_keys = {
            'name', 'type', 'value', 'data', 'content', 'result', 'error',
            'id', 'version', 'format', 'size', 'length', 'width', 'height',
            'file', 'path', 'url', 'src', 'dest', 'source', 'target',
            'if', 'else', 'for', 'while', 'return', 'def', 'class', 'import',
            'from', 'as', 'in', 'is', 'not', 'and', 'or', 'True', 'False',
            'None', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
            'get', 'set', 'add', 'remove', 'find', 'search', 'update',
            'key', 'val', 'item', 'element', 'index', 'count', 'total',
            'self', 'cls', 'super', 'init', 'main', 'args', 'kwargs'
        }
        return key in common_keys or key.isdigit() or len(key) < 3

    def analyze_duplicates(self):
        """Analyze collected data for duplicates"""
        print("\n" + "="*80)
        print("DUPLICATE ANALYSIS REPORT")
        print("="*80)

        # 1. Duplicate field names
        print("\n1. ANALYZING DUPLICATE FIELD NAMES...")
        self._analyze_duplicate_fields()

        # 2. Duplicate functions
        print("\n2. ANALYZING DUPLICATE FUNCTIONS...")
        self._analyze_duplicate_functions()

        # 3. Duplicate classes
        print("\n3. ANALYZING DUPLICATE CLASSES...")
        self._analyze_duplicate_classes()

        # 4. Duplicate imports
        print("\n4. ANALYZING DUPLICATE IMPORTS...")
        self._analyze_duplicate_imports()

        # 5. Similar code blocks
        print("\n5. ANALYZING SIMILAR CODE BLOCKS...")
        self._analyze_similar_code_blocks()

        # Generate summary
        self._generate_summary()

    def _analyze_duplicate_fields(self):
        """Analyze duplicate field definitions"""
        duplicates = {
            name: locations for name, locations in self.field_definitions.items()
            if len(locations) > 1
        }

        # Sort by occurrence count
        sorted_duplicates = sorted(
            duplicates.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        print(f"Found {len(duplicates)} duplicate field definitions")
        print(f"Top 20 most duplicated fields:")

        for field, locations in sorted_duplicates[:20]:
            print(f"  '{field}': {len(locations)} occurrences")
            modules = [loc['module'] for loc in locations]
            module_counts = Counter(modules)
            print(f"    Modules: {dict(module_counts.most_common(5))}")
            print(f"    First occurrence: {locations[0]['module']}:{locations[0]['line']}")

        self.duplicates_report['duplicate_fields'] = {
            name: locations for name, locations in sorted_duplicates[:50]
        }

    def _analyze_duplicate_functions(self):
        """Analyze duplicate function definitions"""
        duplicates = {
            name: defs for name, defs in self.function_definitions.items()
            if len(defs) > 1
        }

        print(f"Found {len(duplicates)} duplicate function definitions")
        print(f"Top 10 most duplicated functions:")

        sorted_duplicates = sorted(
            duplicates.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        for func, defs in sorted_duplicates[:10]:
            print(f"  '{func}': {len(defs)} definitions")
            for def_info in defs[:3]:
                print(f"    {def_info['module']}:{def_info['line']} - args: {def_info['args']}")

        self.duplicates_report['duplicate_functions'] = {
            name: defs for name, defs in sorted_duplicates[:20]
        }

    def _analyze_duplicate_classes(self):
        """Analyze duplicate class definitions"""
        duplicates = {
            name: defs for name, defs in self.class_definitions.items()
            if len(defs) > 1
        }

        print(f"Found {len(duplicates)} duplicate class definitions")
        print(f"Top 10 most duplicated classes:")

        sorted_duplicates = sorted(
            duplicates.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        for cls, defs in sorted_duplicates[:10]:
            print(f"  '{cls}': {len(defs)} definitions")
            for def_info in defs:
                print(f"    {def_info['module']}:{def_info['line']}")

        self.duplicates_report['duplicate_classes'] = {
            name: defs for name, defs in sorted_duplicates
        }

    def _analyze_duplicate_imports(self):
        """Analyze duplicate import patterns"""
        all_imports = defaultdict(list)
        for import_stmt, modules in self.import_statements.items():
            if len(modules) > 1:
                all_imports[import_stmt] = modules

        print(f"Found {len(all_imports)} commonly used imports")
        print(f"Top 20 most shared imports:")

        sorted_imports = sorted(
            all_imports.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        for import_stmt, modules in sorted_imports[:20]:
            print(f"  '{import_stmt}': {len(modules)} modules")

        self.duplicates_report['duplicate_imports'] = {
            stmt: modules for stmt, modules in sorted_imports[:30]
        }

    def _analyze_similar_code_blocks(self):
        """Analyze similar code blocks using hash comparison"""
        # Group blocks by hash
        hash_groups = defaultdict(list)
        for block in self.code_blocks:
            hash_groups[block['hash']].append(block)

        # Find duplicates
        duplicates = {
            hash_val: blocks for hash_val, blocks in hash_groups.items()
            if len(blocks) > 1
        }

        print(f"Found {len(duplicates)} identical code blocks")
        print(f"Top 10 most duplicated code blocks:")

        sorted_duplicates = sorted(
            duplicates.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        for hash_val, blocks in sorted_duplicates[:10]:
            print(f"  Hash {hash_val[:8]}: {len(blocks)} identical blocks")
            print(f"    Sample: {blocks[0]['content'][:100]}...")
            print(f"    Locations: {[(b['module'], b['start_line']) for b in blocks[:3]]}")

        self.duplicates_report['similar_code_blocks'] = [
            {'hash': h, 'blocks': b} for h, b in sorted_duplicates[:15]
        ]

    def _generate_summary(self):
        """Generate summary statistics"""
        print("\n" + "="*80)
        print("SUMMARY STATISTICS")
        print("="*80)

        total_fields = len(self.field_definitions)
        duplicate_fields = len([f for f in self.field_definitions.values() if len(f) > 1])

        total_functions = len(self.function_definitions)
        duplicate_functions = len([f for f in self.function_definitions.values() if len(f) > 1])

        total_classes = len(self.class_definitions)
        duplicate_classes = len([c for c in self.class_definitions.values() if len(c) > 1])

        total_code_blocks = len(self.code_blocks)

        # Calculate duplicate blocks properly
        hash_groups = defaultdict(list)
        for block in self.code_blocks:
            hash_groups[block['hash']].append(block)
        duplicate_blocks = len([blocks for blocks in hash_groups.values() if len(blocks) > 1])

        summary = {
            'total_modules': len(self.all_modules),
            'total_unique_fields': total_fields,
            'duplicate_field_definitions': duplicate_fields,
            'total_function_definitions': total_functions,
            'duplicate_function_definitions': duplicate_functions,
            'total_class_definitions': total_classes,
            'duplicate_class_definitions': duplicate_classes,
            'total_code_blocks_analyzed': total_code_blocks,
            'identical_code_blocks': len([b for b in
                defaultdict(list, [(block['hash'], []) for block in self.code_blocks]).values()
                if len(b) > 1])
        }

        print(f"Total modules scanned: {summary['total_modules']}")
        print(f"Total unique field names: {summary['total_unique_fields']}")
        print(f"Duplicate field definitions: {summary['duplicate_field_definitions']}")
        print(f"Total function definitions: {summary['total_function_definitions']}")
        print(f"Duplicate function definitions: {summary['duplicate_function_definitions']}")
        print(f"Total class definitions: {summary['total_class_definitions']}")
        print(f"Duplicate class definitions: {summary['duplicate_class_definitions']}")
        print(f"Total code blocks analyzed: {summary['total_code_blocks_analyzed']}")
        print(f"Identical code blocks: {duplicate_blocks}")

        self.duplicates_report['summary'] = summary

    def save_report(self, output_file: str):
        """Save detailed report to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.duplicates_report, f, indent=2, default=str)
        print(f"\nDetailed report saved to: {output_file}")


def main():
    """Main execution function"""
    modules_dir = "/Users/pranay/Projects/metaextract/server/extractor/modules"
    output_file = "/Users/pranay/Projects/metaextract/docs/duplicate_analysis_report.json"

    detector = DuplicateDetector(modules_dir)

    print("Starting comprehensive duplicate detection...")
    print("="*80)

    detector.scan_all_modules()
    detector.analyze_duplicates()
    detector.save_report(output_file)

    print("\n" + "="*80)
    print("Duplicate detection complete!")
    print("="*80)


if __name__ == "__main__":
    main()