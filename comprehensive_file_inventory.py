#!/usr/bin/env python3
"""
Comprehensive File Analysis for MetaExtract
Creates a detailed inventory of all files with problematic naming patterns
for review before any implementation decisions.
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import json

class FileInventoryAnalyzer:
    def __init__(self, base_path="/Users/pranay/Projects/metaextract"):
        self.base_path = Path(base_path)
        self.inventory = defaultdict(list)
        
    def analyze_all_files(self):
        """Analyze all Python files in the codebase."""
        
        python_files = list(self.base_path.rglob("*.py"))
        print(f"Analyzing {len(python_files)} Python files...")
        
        for py_file in python_files:
            relative_path = py_file.relative_to(self.base_path)
            filename = py_file.name
            
            # Categorize by different problematic patterns
            self.categorize_file(py_file, relative_path, filename)
        
        return self.inventory
    
    def categorize_file(self, filepath, relative_path, filename):
        """Categorize a file based on its naming patterns."""
        
        # Roman Numeral Placeholders
        if re.search(r'ultimate_advanced_extension_[ivxlcdm]+\.py$', filename):
            self.inventory['roman_numeral_placeholders'].append({
                'path': str(relative_path),
                'filename': filename,
                'category': 'roman_numeral',
                'roman_numeral': re.search(r'ultimate_advanced_extension_([ivxlcdm]+)\.py$', filename).group(1)
            })
        
        # Excessive Superlatives
        superlatives = ['ultimate', 'complete', 'mega', 'ultra', 'massive', 'universal', 
                       'comprehensive', 'enhanced', 'master', 'special', 'absolute', 
                       'total', 'perfect', 'maximum', 'extreme', 'super', 'hyper']
        
        if any(sup in filename.lower() for sup in superlatives):
            found_sup = [sup for sup in superlatives if sup in filename.lower()]
            self.inventory['excessive_superlatives'].append({
                'path': str(relative_path),
                'filename': filename,
                'category': 'superlative',
                'superlatives_found': found_sup
            })
        
        # Contradictory Names
        contradictions = [
            (r'simple.*massive', 'simple_massive'),
            (r'quick.*final', 'quick_final'),
            (r'rapid.*implementer', 'rapid_implementer'),
            (r'easy.*complex', 'easy_complex'),
            (r'basic.*advanced', 'basic_advanced')
        ]
        
        for pattern, desc in contradictions:
            if re.search(pattern, filename.lower()):
                self.inventory['contradictory_names'].append({
                    'path': str(relative_path),
                    'filename': filename,
                    'category': 'contradictory',
                    'contradiction_type': desc
                })
        
        # Field Count Duplicates
        if 'field_count' in filename.lower():
            self.inventory['field_count_duplicates'].append({
                'path': str(relative_path),
                'filename': filename,
                'category': 'field_count'
            })
        
        # Excessive Length
        if len(filename) > 50:
            self.inventory['excessive_length'].append({
                'path': str(relative_path),
                'filename': filename,
                'category': 'long_name',
                'length': len(filename)
            })
        
        # Test Files in Production
        if filename.startswith('test_') and 'tests' not in str(relative_path):
            self.inventory['test_files_production'].append({
                'path': str(relative_path),
                'filename': filename,
                'category': 'test_in_prod'
            })
        
        # Final/Temp Files
        if re.search(r'(final|temp|tmp|backup|old|new)\.py$', filename.lower()):
            self.inventory['temp_final_files'].append({
                'path': str(relative_path),
                'filename': filename,
                'category': 'temp_final'
            })
        
        # Numbered Sequences (not Roman)
        if re.search(r'_[0-9]+\.py$', filename):
            self.inventory['numbered_sequences'].append({
                'path': str(relative_path),
                'filename': filename,
                'category': 'numbered'
            })
        
        # Inventory Files (domain-specific)
        if filename.startswith('inventory_'):
            domain = filename.replace('inventory_', '').replace('.py', '')
            self.inventory['inventory_files'].append({
                'path': str(relative_path),
                'filename': filename,
                'category': 'inventory',
                'domain': domain
            })
    
    def analyze_file_content(self):
        """Analyze content of problematic files to determine implementation status."""
        
        content_analysis = {}
        
        for category, files in self.inventory.items():
            if category in ['roman_numeral_placeholders', 'excessive_superlatives']:
                content_analysis[category] = []
                
                for file_info in files[:20]:  # Analyze first 20 of each category
                    filepath = self.base_path / file_info['path']
                    
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                        
                        lines = len(content.split('\n'))
                        
                        # Check for placeholder indicators
                        placeholder_indicators = [
                            'placeholder module',
                            'real extraction logic not yet implemented',
                            'placeholder_field_count',
                            'extraction_status": "placeholder"',
                            'this is a placeholder'
                        ]
                        
                        is_placeholder = any(indicator in content.lower() for indicator in placeholder_indicators)
                        
                        # Check for implementation indicators
                        implementation_indicators = [
                            'def extract_',
                            'import ',
                            'class ',
                            'try:',
                            'except:',
                            'with open(',
                            'struct.unpack',
                            'json.loads',
                            'subprocess.run'
                        ]
                        
                        has_implementation = any(indicator in content for indicator in implementation_indicators)
                        
                        content_analysis[category].append({
                            **file_info,
                            'lines': lines,
                            'is_placeholder': is_placeholder,
                            'has_implementation': has_implementation,
                            'implementation_status': 'placeholder' if is_placeholder else ('implemented' if has_implementation else 'unknown')
                        })
                        
                    except Exception as e:
                        content_analysis[category].append({
                            **file_info,
                            'lines': 0,
                            'is_placeholder': True,
                            'has_implementation': False,
                            'implementation_status': 'error',
                            'error': str(e)
                        })
        
        return content_analysis
    
    def generate_priority_report(self):
        """Generate a priority-based report for implementation decisions."""
        
        content_analysis = self.analyze_file_content()
        
        priority_report = {
            'high_priority_implementation': [],  # Real functionality, bad names
            'medium_priority_review': [],        # Some implementation, needs review
            'low_priority_placeholders': [],     # Pure placeholders
            'immediate_rename': [],              # Just need renaming
            'consolidation_candidates': []       # Similar functionality
        }
        
        # Analyze Roman numeral files
        for file_info in content_analysis.get('roman_numeral_placeholders', []):
            if file_info['implementation_status'] == 'implemented':
                priority_report['high_priority_implementation'].append(file_info)
            elif file_info['implementation_status'] == 'placeholder':
                priority_report['low_priority_placeholders'].append(file_info)
            else:
                priority_report['medium_priority_review'].append(file_info)
        
        # Analyze superlative files
        for file_info in content_analysis.get('excessive_superlatives', []):
            if file_info['implementation_status'] == 'implemented':
                priority_report['immediate_rename'].append(file_info)
            elif file_info['implementation_status'] == 'placeholder':
                priority_report['low_priority_placeholders'].append(file_info)
            else:
                priority_report['medium_priority_review'].append(file_info)
        
        return priority_report
    
    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report."""
        
        self.analyze_all_files()
        content_analysis = self.analyze_file_content()
        priority_report = self.generate_priority_report()
        
        report = f"""
# MetaExtract File Inventory Analysis Report

## Executive Summary

This report provides a comprehensive analysis of {sum(len(files) for files in self.inventory.values())} Python files 
with problematic naming patterns that need review for implementation decisions.

## File Categories Analysis

"""
        
        # Category summaries
        for category, files in self.inventory.items():
            report += f"### {category.replace('_', ' ').title()}\n"
            report += f"- **Total Files**: {len(files)}\n"
            
            if category in content_analysis:
                implemented = sum(1 for f in content_analysis[category] if f.get('implementation_status') == 'implemented')
                placeholders = sum(1 for f in content_analysis[category] if f.get('implementation_status') == 'placeholder')
                report += f"- **Implemented**: {implemented}\n"
                report += f"- **Placeholders**: {placeholders}\n"
            
            # Show first 5 examples
            if files:
                report += "- **Examples**:\n"
                for file_info in files[:5]:
                    report += f"  - `{file_info['filename']}`\n"
                if len(files) > 5:
                    report += f"  - ... and {len(files) - 5} more\n"
            report += "\n"
        
        # Priority recommendations
        report += """## Implementation Priority Recommendations

### 🔴 High Priority - Implement and Rename
These files have real functionality but terrible names:

"""
        
        for file_info in priority_report['high_priority_implementation']:
            report += f"- **{file_info['filename']}** ({file_info['lines']} lines)\n"
            report += f"  - Path: `{file_info['path']}`\n"
            report += f"  - Status: {file_info['implementation_status']}\n\n"
        
        report += """### 🟡 Medium Priority - Review Content
These files need content review to determine if they should be implemented:

"""
        
        for file_info in priority_report['medium_priority_review'][:10]:  # Show first 10
            report += f"- **{file_info['filename']}** ({file_info['lines']} lines)\n"
            report += f"  - Path: `{file_info['path']}`\n"
            report += f"  - Status: {file_info['implementation_status']}\n\n"
        
        report += """### 🟢 Low Priority - Pure Placeholders
These files are pure placeholders and can be removed or replaced:

"""
        
        placeholder_count = len(priority_report['low_priority_placeholders'])
        report += f"- **Total Placeholder Files**: {placeholder_count}\n"
        report += "- **Examples**:\n"
        for file_info in priority_report['low_priority_placeholders'][:10]:
            report += f"  - `{file_info['filename']}` ({file_info['lines']} lines)\n"
        if placeholder_count > 10:
            report += f"  - ... and {placeholder_count - 10} more\n"
        
        report += """\n### 🔵 Immediate Rename
These files just need better names (they already work):

"""
        
        for file_info in priority_report['immediate_rename'][:10]:
            report += f"- **{file_info['filename']}** ({file_info['lines']} lines)\n"
            report += f"  - Path: `{file_info['path']}`\n"
            report += f"  - Suggested rename: Remove superlatives\n\n"
        
        # Roman numeral analysis
        roman_files = self.inventory.get('roman_numeral_placeholders', [])
        if roman_files:
            report += f"""## Roman Numeral Placeholder Analysis

**Total Roman Numeral Files**: {len(roman_files)}

Numeral Distribution:
"""
            
            numeral_counts = defaultdict(int)
            for file_info in roman_files:
                numeral = file_info.get('roman_numeral', 'unknown')
                numeral_counts[numeral] += 1
            
            # Show distribution
            for numeral, count in sorted(numeral_counts.items()):
                report += f"- {numeral.upper()}: {count} files\n"
        
        report += """\n## Recommendations

### Immediate Actions
1. **Review High Priority Files**: Implement the 4 valuable Roman numeral files
2. **Rename Working Files**: Fix names for files with real functionality
3. **Consolidate Placeholders**: Remove or replace pure placeholder files

### Implementation Strategy
1. **Phase 1**: Preserve and rename the 4 high-value Roman numeral files
2. **Phase 2**: Review medium priority files for implementation potential
3. **Phase 3**: Clean up pure placeholder files
4. **Phase 4**: Establish naming conventions for future files

### Expected Outcomes
- **Cleaner codebase** with descriptive file names
- **Preserved functionality** from valuable files
- **Reduced confusion** about which files contain real code
- **Better maintainability** through consistent naming
"""
        
        return report
    
    def export_json_inventory(self):
        """Export complete inventory as JSON for programmatic access."""
        
        inventory_data = {
            'file_inventory': dict(self.inventory),
            'content_analysis': self.analyze_file_content(),
            'priority_recommendations': self.generate_priority_report(),
            'metadata': {
                'total_files_analyzed': sum(len(files) for files in self.inventory.values()),
                'base_path': str(self.base_path),
                'analysis_date': '2024-01-12'
            }
        }
        
        return inventory_data

if __name__ == "__main__":
    analyzer = FileInventoryAnalyzer()
    
    print("Analyzing codebase for problematic file names...")
    report = analyzer.generate_comprehensive_report()
    
    print("\n" + "="*60)
    print("COMPREHENSIVE FILE INVENTORY REPORT")
    print("="*60 + "\n")
    
    # Print summary first
    inventory = analyzer.inventory
    total_problematic = sum(len(files) for files in inventory.values())
    
    print(f"📊 PROBLEMATIC FILES SUMMARY:")
    print(f"Total files with naming issues: {total_problematic}")
    print(f"Roman numeral placeholders: {len(inventory.get('roman_numeral_placeholders', []))}")
    print(f"Excessive superlatives: {len(inventory.get('excessive_superlatives', []))}")
    print(f"Excessive length: {len(inventory.get('excessive_length', []))}")
    print(f"Field count duplicates: {len(inventory.get('field_count_duplicates', []))}")
    print(f"Inventory files: {len(inventory.get('inventory_files', []))}")
    
    # Save full report
    with open("/Users/pranay/Projects/metaextract/comprehensive_file_inventory_report.md", "w") as f:
        f.write(report)
    
    # Export JSON for programmatic access
    json_data = analyzer.export_json_inventory()
    with open("/Users/pranay/Projects/metaextract/file_inventory_data.json", "w") as f:
        json.dump(json_data, f, indent=2)
    
    print(f"\n✅ Reports saved:")
    print(f"- comprehensive_file_inventory_report.md")
    print(f"- file_inventory_data.json")
    print(f"\n📋 Next steps: Review the reports to decide which files to implement vs remove.")