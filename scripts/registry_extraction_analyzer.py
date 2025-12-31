#!/usr/bin/env python3
"""
Registry vs Extraction Gap Analyzer
Identifies modules with registry definitions but missing extraction implementations
"""

import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class RegistryExtractionAnalyzer:
    def __init__(self):
        self.modules_dir = Path("/Users/pranay/Projects/metaextract/server/extractor/modules")
        self.registry_modules = {}
        self.extraction_modules = {}
        self.gap_analysis = {
            'registry_only': [],      # Has registry, no extraction
            'extraction_only': [],    # Has extraction, no registry
            'both': [],               # Has both
            'neither': [],            # Has neither
            'implementation_candidates': []  # Priority targets for implementation
        }

    def analyze_registry_extraction_gap(self):
        """Analyze gap between registry definitions and extraction implementations"""
        print("="*80)
        print("REGISTRY VS EXTRACTION GAP ANALYSIS")
        print("="*80)

        # Step 1: Identify all registry modules
        print("\n[1/4] IDENTIFYING REGISTRY MODULES...")
        self._identify_registry_modules()

        # Step 2: Identify all extraction modules
        print("\n[2/4] IDENTIFYING EXTRACTION MODULES...")
        self._identify_extraction_modules()

        # Step 3: Analyze the gap
        print("\n[3/4] ANALYZING GAPS...")
        self._analyze_gaps()

        # Step 4: Generate implementation plan
        print("\n[4/4] GENERATING IMPLEMENTATION PLAN...")
        self._generate_implementation_plan()

    def _identify_registry_modules(self):
        """Identify modules that contain registry definitions"""
        registry_indicators = [
            r'registry',
            r'_fields.*=.*\{',
            r'get_.*_registry_fields',
            r'STANDARD_.*TAGS',
            r'METADATA_.*DEFINITIONS'
        ]

        for py_file in self.modules_dir.rglob("*.py"):
            try:
                content = py_file.read_text()

                # Check for registry indicators
                registry_score = 0
                registry_details = {
                    'file': py_file.name,
                    'field_count': 0,
                    'registry_functions': [],
                    'has_get_field_count': False,
                    'has_extract_function': False
                }

                for pattern in registry_indicators:
                    matches = len(re.findall(pattern, content, re.IGNORECASE))
                    registry_score += matches

                # Count registry fields (large dictionaries)
                dict_matches = re.findall(r'(\w+)\s*=\s*\{([^}]+)\}', content, re.DOTALL)
                for dict_name, dict_content in dict_matches:
                    field_count = len(re.findall(r'["\']?\w+["\']?\s*:', dict_content))
                    if field_count > 20:  # Likely a registry
                        registry_details['field_count'] += field_count

                # Find registry functions
                registry_funcs = re.findall(r'def (get_\w+_registry_fields|get_\w+_fields)\(', content)
                registry_details['registry_functions'] = registry_funcs

                # Check for field count function
                if re.search(r'def get_\w+_field_count\(', content):
                    registry_details['has_get_field_count'] = True

                # Check for extract function
                if re.search(r'def extract_\w+.*\(.*filepath.*\)', content):
                    registry_details['has_extract_function'] = True

                # Determine if this is a registry module
                if registry_score > 0 or registry_details['field_count'] > 50 or registry_details['registry_functions']:
                    self.registry_modules[py_file.name] = registry_details
                    print(f"  Found registry: {py_file.name} ({registry_details['field_count']} fields)")

            except Exception as e:
                continue

        print(f"\nTotal registry modules: {len(self.registry_modules)}")
        total_registry_fields = sum(m['field_count'] for m in self.registry_modules.values())
        print(f"Total registry fields: {total_registry_fields:,}")

    def _identify_extraction_modules(self):
        """Identify modules that have extraction functions"""
        for py_file in self.modules_dir.rglob("*.py"):
            try:
                content = py_file.read_text()

                # Find extraction functions
                extract_funcs = re.findall(r'def (extract_\w+.*?)\(([^)]*)\):', content, re.MULTILINE)

                if extract_funcs:
                    self.extraction_modules[py_file.name] = {
                        'file': py_file.name,
                        'extract_functions': [(name, args) for name, args in extract_funcs],
                        'function_count': len(extract_funcs)
                    }
                    print(f"  Found extraction: {py_file.name} ({len(extract_funcs)} functions)")

            except Exception as e:
                continue

        print(f"\nTotal extraction modules: {len(self.extraction_modules)}")
        total_extract_funcs = sum(len(m['extract_functions']) for m in self.extraction_modules.values())
        print(f"Total extraction functions: {total_extract_funcs}")

    def _analyze_gaps(self):
        """Analyze gaps between registry and extraction"""
        all_modules = set(self.registry_modules.keys()) | set(self.extraction_modules.keys())

        for module_name in all_modules:
            has_registry = module_name in self.registry_modules
            has_extraction = module_name in self.extraction_modules

            if has_registry and has_extraction:
                self.gap_analysis['both'].append(module_name)
            elif has_registry and not has_extraction:
                self.gap_analysis['registry_only'].append(module_name)
            elif not has_registry and has_extraction:
                self.gap_analysis['extraction_only'].append(module_name)
            else:
                self.gap_analysis['neither'].append(module_name)

        # Prioritize registry-only modules by field count
        registry_only_sorted = sorted(
            self.gap_analysis['registry_only'],
            key=lambda m: self.registry_modules[m]['field_count'],
            reverse=True
        )

        for module_name in registry_only_sorted:
            module_info = self.registry_modules[module_name]
            self.gap_analysis['implementation_candidates'].append({
                'module': module_name,
                'field_count': module_info['field_count'],
                'registry_functions': module_info['registry_functions'],
                'priority': 'HIGH' if module_info['field_count'] > 500 else 'MEDIUM' if module_info['field_count'] > 100 else 'LOW'
            })

        print(f"\nGAP ANALYSIS RESULTS:")
        print(f"  Both registry & extraction: {len(self.gap_analysis['both'])}")
        print(f"  Registry only: {len(self.gap_analysis['registry_only'])}")
        print(f"  Extraction only: {len(self.gap_analysis['extraction_only'])}")
        print(f"  Neither: {len(self.gap_analysis['neither'])}")

        print(f"\nTOP 10 REGISTRY-ONLY MODULES (Priority for implementation):")
        for i, candidate in enumerate(self.gap_analysis['implementation_candidates'][:10], 1):
            print(f"  {i}. {candidate['module']} - {candidate['field_count']:,} fields [{candidate['priority']}]")

    def _generate_implementation_plan(self):
        """Generate detailed implementation plan"""
        total_missing_fields = sum(c['field_count'] for c in self.gap_analysis['implementation_candidates'])

        print(f"\n" + "="*80)
        print("IMPLEMENTATION PLAN")
        print("="*80)

        print(f"""
SUMMARY:
• {len(self.gap_analysis['implementation_candidates'])} modules need extraction implementation
• {total_missing_fields:,} registry fields lack extraction (the gap)
• Average {total_missing_fields // len(self.gap_analysis['implementation_candidates']):,} fields per module

PRIORITY CATEGORIES:""")

        high_priority = [c for c in self.gap_analysis['implementation_candidates'] if c['priority'] == 'HIGH']
        medium_priority = [c for c in self.gap_analysis['implementation_candidates'] if c['priority'] == 'MEDIUM']
        low_priority = [c for c in self.gap_analysis['implementation_candidates'] if c['priority'] == 'LOW']

        print(f"""
  HIGH Priority (>500 fields): {len(high_priority)} modules
    - These represent the biggest coverage gaps
    - Implementing these will add ~{sum(c['field_count'] for c in high_priority):,} extractable fields

  MEDIUM Priority (100-500 fields): {len(medium_priority)} modules
    - Moderate coverage improvements
    - Implementing these will add ~{sum(c['field_count'] for c in medium_priority):,} extractable fields

  LOW Priority (<100 fields): {len(low_priority)} modules
    - Niche or specialized formats
    - Implementing these will add ~{sum(c['field_count'] for c in low_priority):,} extractable fields
""")

        print("TOP 5 HIGH-PRIORITY TARGETS:")
        for i, candidate in enumerate(high_priority[:5], 1):
            print(f"  {i}. {candidate['module']}")
            print(f"     Fields: {candidate['field_count']:,}")
            print(f"     Registry functions: {', '.join(candidate['registry_functions'][:3])}")
            print()

def main():
    analyzer = RegistryExtractionAnalyzer()
    analyzer.analyze_registry_extraction_gap()

if __name__ == "__main__":
    main()