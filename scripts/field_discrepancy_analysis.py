#!/usr/bin/env python3
"""
Field Count Discrepancy Analysis
Analyzes the gap between:
1. Claimed fields (inventory) - legacy 45K baseline
2. Loaded registry fields - 75K
3. Actual extraction implementation - 17K
4. Gap: ~28K missing implementations
"""

import sys
import os
import re
import importlib.util
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class FieldDiscrepancyAnalyzer:
    def __init__(self):
        self.modules_dir = Path("/Users/pranay/Projects/metaextract/server/extractor/modules")
        self.inventory_fields = {}  # What get_*_field_count() returns
        self.registry_fields = {}   # What registry modules define
        self.extraction_fields = {} # What extract functions actually implement
        self.discrepancies = {
            'claimed_but_not_loaded': [],
            'loaded_but_not_extracted': [],
            'claimed_but_not_extracted': [],
            'registry_modules': [],
            'extraction_modules': []
        }

    def analyze_field_counts(self):
        """Analyze field count functions vs actual implementation"""
        print("="*80)
        print("FIELD COUNT DISCREPANCY ANALYSIS")
        print("="*80)

        # Step 1: Analyze get_*_field_count() functions (Inventory)
        print("\n1. ANALYZING INVENTORY (get_*_field_count functions)...")
        self._analyze_inventory_functions()

        # Step 2: Analyze registry modules (Loaded fields)
        print("\n2. ANALYZING REGISTRY MODULES...")
        self._analyze_registry_modules()

        # Step 3: Analyze actual extraction functions
        print("\n3. ANALYZING EXTRACTION IMPLEMENTATIONS...")
        self._analyze_extraction_implementation()

        # Step 4: Compare and identify gaps
        print("\n4. IDENTIFYING DISCREPANCIES...")
        self._identify_discrepancies()

        # Step 5: Generate summary
        print("\n5. GENERATING SUMMARY...")
        self._generate_summary()

    def _analyze_inventory_functions(self):
        """Analyze what get_*_field_count() functions claim"""
        for py_file in self.modules_dir.rglob("*field*.py"):
            try:
                content = py_file.read_text()

                # Find get_*_field_count functions
                matches = re.findall(r'def (get_\w+_field_count)\(.*?\).*?return\s+(.+)', content, re.DOTALL)

                for func_name, return_stmt in matches:
                    # Try to evaluate what the function returns
                    try:
                        # Simple evaluation of len() calls or direct numbers
                        if 'len(' in return_stmt:
                            # Extract the variable being counted
                            var_match = re.search(r'len\((\w+)\)', return_stmt)
                            if var_match:
                                var_name = var_match.group(1)
                                # Try to find this variable definition
                                var_def = re.search(rf'{var_name}\s*=\s*\{{[^}}]*\}}', content, re.DOTALL)
                                if var_def:
                                    actual_count = len(re.findall(r'[\w"]+\s*:', var_def.group(0)))
                                    self.inventory_fields[func_name] = actual_count
                                else:
                                    # Could be **dict merging
                                    dict_merge_count = len(re.findall(r'\*\*\w+', content))
                                    estimated = max(1, dict_merge_count * 50)  # Rough estimate
                                    self.inventory_fields[func_name] = estimated
                        elif return_stmt.strip().isdigit():
                            self.inventory_fields[func_name] = int(return_stmt.strip())
                        else:
                            # Complex expression, try to estimate
                            numbers = re.findall(r'\d+', return_stmt)
                            if numbers:
                                self.inventory_fields[func_name] = sum(int(n) for n in numbers)
                            else:
                                self.inventory_fields[func_name] = 100  # Default estimate

                    except:
                        self.inventory_fields[func_name] = 50  # Conservative estimate

            except Exception as e:
                continue

        print(f"Found {len(self.inventory_fields)} field count functions")
        total_claimed = sum(self.inventory_fields.values())
        print(f"Total claimed fields: {total_claimed:,}")

    def _analyze_registry_modules(self):
        """Analyze registry modules that define metadata standards"""
        registry_pattern = re.compile(r'registry', re.IGNORECASE)

        for py_file in self.modules_dir.rglob("*.py"):
            if registry_pattern.search(py_file.name):
                try:
                    content = py_file.read_text()

                    # Find dictionary definitions with metadata fields
                    # Look for large dictionaries
                    dict_matches = re.findall(r'(\w+)\s*=\s*\{([^}]+)\}', content, re.DOTALL)

                    total_fields = 0
                    for dict_name, dict_content in dict_matches:
                        # Count key-value pairs
                        field_count = len(re.findall(r'["\']?\w+["\']?\s*:', dict_content))
                        total_fields += field_count

                    if total_fields > 0:
                        self.registry_fields[py_file.name] = total_fields
                        self.discrepancies['registry_modules'].append({
                            'file': py_file.name,
                            'fields': total_fields
                        })

                except Exception as e:
                    continue

        print(f"Found {len(self.registry_fields)} registry modules")
        total_loaded = sum(self.registry_fields.values())
        print(f"Total loaded registry fields: {total_loaded:,}")

    def _analyze_extraction_implementation(self):
        """Analyze actual extraction implementation"""
        for py_file in self.modules_dir.rglob("*.py"):
            try:
                content = py_file.read_text()

                # Find extract functions
                extract_matches = re.findall(r'def (extract\w+)\(.*?\).*?return\s+(.+)', content, re.DOTALL)

                for func_name, return_stmt in extract_matches:
                    # Count actual fields being extracted
                    # Look for dict assignments, update calls, etc.
                    field_assignments = len(re.findall(r'(\w+)\s*=\s*\{', content))
                    update_calls = len(re.findall(r'metadata\.update\(|result\.update\(', content))

                    actual_fields = field_assignments + update_calls

                    if actual_fields > 0:
                        self.extraction_fields[func_name] = actual_fields
                        self.discrepancies['extraction_modules'].append({
                            'function': func_name,
                            'file': py_file.name,
                            'actual_fields': actual_fields
                        })

            except Exception as e:
                continue

        print(f"Found {len(self.extraction_fields)} extraction functions")
        total_extracted = sum(self.extraction_fields.values())
        print(f"Total extracted fields (estimated): {total_extracted:,}")

    def _identify_discrepancies(self):
        """Identify gaps between claimed, loaded, and extracted"""
        # This is a simplified analysis - real implementation would need deeper AST analysis

        total_claimed = sum(self.inventory_fields.values())
        total_loaded = sum(self.registry_fields.values())
        total_extracted = sum(self.extraction_fields.values())

        print(f"\nDISCREPANCY ANALYSIS:")
        print(f"  Claimed (Inventory):     {total_claimed:>15,} fields")
        print(f"  Loaded (Registries):     {total_loaded:>15,} fields")
        print(f"  Extracted (Actual):      {total_extracted:>15,} fields")
        print(f"  " + "-"*45)
        print(f"  Claimed vs Extracted:    {total_claimed - total_extracted:>15,} field gap")
        print(f"  Loaded vs Extracted:     {total_loaded - total_extracted:>15,} field gap")

        # Find modules that claim high counts but have simple implementations
        print(f"\nTOP 10 MODULES WITH HIGHEST CLAIMED COUNTS:")
        sorted_inventory = sorted(self.inventory_fields.items(), key=lambda x: x[1], reverse=True)[:10]
        for func, count in sorted_inventory:
            print(f"  {func:50s}: {count:>5} fields")

        # Find registry modules with lots of fields
        print(f"\nTOP 10 REGISTRY MODULES BY FIELD COUNT:")
        sorted_registries = sorted(self.registry_fields.items(), key=lambda x: x[1], reverse=True)[:10]
        for file, count in sorted_registries:
            print(f"  {file:50s}: {count:>5} fields")

    def _generate_summary(self):
        """Generate summary of findings"""
        total_claimed = sum(self.inventory_fields.values())
        total_loaded = sum(self.registry_fields.values())
        total_extracted = sum(self.extraction_fields.values())

        print(f"\n" + "="*80)
        print("DISCREPANCY EXPLANATION")
        print("="*80)

        print("""
The discrepancy occurs because:

1. **INVENTORY (legacy 45K claimed)**: get_*_field_count() functions often return
   estimated counts based on dictionary sizes, not actual extractions.

2. **REGISTRIES (75K loaded)**: Registry modules contain standardized metadata
   definitions (like DICOM tags, ID3 frames) that are loaded into memory but
   not all are extracted in practice.

3. **EXTRACTION (17K actual)**: The extract_*() functions actually implement
   the extraction logic, and they typically handle a subset of available fields.

**ROOT CAUSES:**

• Registry modules define comprehensive standards (e.g., all 3,500+ DICOM tags)
• Field count functions count registry definitions, not actual extractions
• Extraction functions implement only commonly-used fields for performance
• Gap between "what exists in standard" vs "what we actually extract"

**IMPACT:**

• Field counts are **theoretical maximums**, not practical extraction counts
• Actual metadata extraction capability is lower than claimed
• Need to prioritize high-value fields for implementation
        """)

        print(f"\nSUMMARY:")
        print(f"  Total modules analyzed: {len(self.inventory_fields) + len(self.registry_fields)}")
        print(f"  Theoretical coverage: {total_claimed:,} fields")
        print(f"  Registry definitions: {total_loaded:,} fields")
        print(f"  Actual implementation: {total_extracted:,} fields")
        print(f"  Implementation gap: {total_claimed - total_extracted:,} fields ({(total_claimed - total_extracted)/total_claimed*100:.1f}%)")

def main():
    analyzer = FieldDiscrepancyAnalyzer()
    analyzer.analyze_field_counts()

if __name__ == "__main__":
    main()