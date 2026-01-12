#!/usr/bin/env python3
"""
Quick Analysis of Key Roman Numeral Files
Focus on the most important files that need implementation decisions.
"""

import os
from pathlib import Path

def analyze_key_files():
    """Analyze the most important Roman numeral files."""
    
    base_path = Path("/Users/pranay/Projects/metaextract")
    
    # Key files to analyze (the ones we know have substantial content)
    key_files = [
        "server/extractor/modules/makernotes_ultimate_advanced_extension_ii.py",
        "server/extractor/modules/scientific_dicom_fits_ultimate_advanced_extension_xc.py",
        "server/extractor/modules/scientific_dicom_fits_ultimate_advanced_extension_ii.py",
        "server/extractor/modules/scientific_dicom_fits_ultimate_advanced_extension_iii.py"
    ]
    
    # Also get a sample of other files to check content
    sample_files = []
    for pattern in ["*ultimate_advanced_extension_ii.py", "*ultimate_advanced_extension_iii.py", 
                   "*ultimate_advanced_extension_xc.py", "*ultimate_advanced_extension_xvii.py"]:
        sample_files.extend(base_path.glob(f"server/extractor/modules/{pattern}"))
    
    analysis = {}
    
    for filepath in sample_files:
        if filepath.name.endswith('.py'):
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                
                lines = len(content.split('\n'))
                
                # Check for placeholder indicators
                placeholder_indicators = [
                    'placeholder module',
                    'real extraction logic not yet implemented',
                    'placeholder_field_count',
                    'extraction_status": "placeholder"'
                ]
                
                is_placeholder = any(indicator in content.lower() for indicator in placeholder_indicators)
                
                # Check for implementation
                has_implementation = any(keyword in content for keyword in [
                    'def extract_', 'import ', 'class ', 'try:', 'except:', 'with open('
                ])
                
                # Determine status
                if lines > 100 and not is_placeholder and has_implementation:
                    status = "HIGH PRIORITY - Real Implementation"
                elif lines > 50 and not is_placeholder:
                    status = "MEDIUM PRIORITY - Some Implementation"
                else:
                    status = "LOW PRIORITY - Placeholder/Minimal"
                
                analysis[str(filepath)] = {
                    'filename': filepath.name,
                    'lines': lines,
                    'is_placeholder': is_placeholder,
                    'has_implementation': has_implementation,
                    'status': status
                }
                
            except Exception as e:
                analysis[str(filepath)] = {
                    'filename': filepath.name,
                    'error': str(e),
                    'status': 'ERROR'
                }
    
    return analysis

def generate_quick_report():
    """Generate a quick actionable report."""
    
    analysis = analyze_key_files()
    
    high_priority = [f for f in analysis.values() if f.get('status') == "HIGH PRIORITY - Real Implementation"]
    medium_priority = [f for f in analysis.values() if f.get('status') == "MEDIUM PRIORITY - Some Implementation"]
    low_priority = [f for f in analysis.values() if f.get('status') == "LOW PRIORITY - Placeholder/Minimal"]
    
    report = f"""
# Quick Roman Numeral Files Analysis

## 🎯 IMMEDIATE ACTION REQUIRED

### HIGH PRIORITY - Real Functionality (Implement + Rename)

{len(high_priority)} files with substantial real implementation:

"""
    
    for i, file_info in enumerate(high_priority, 1):
        filename = file_info['filename']
        lines = file_info['lines']
        
        # Suggest new name
        if 'makernotes' in filename:
            new_name = "camera_makernotes_advanced.py"
        elif 'cardiac' in str(filename) or 'ii' in filename:
            new_name = "cardiac_imaging.py"
        elif 'neuro' in str(filename) or 'iii' in filename:
            new_name = "neuroimaging.py"
        elif 'medical' in str(filename) or 'xc' in filename:
            new_name = "medical_astronomical.py"
        else:
            new_name = filename.replace('ultimate_advanced_extension_', '').replace('scientific_dicom_fits_', '')
        
        report += f"{i}. **{filename}** ({lines} lines)\n"
        report += f"   Current Status: {file_info['status']}\n"
        report += f"   Suggested New Name: `{new_name}`\n\n"
    
    report += f"""### MEDIUM PRIORITY - Review Content

{len(medium_priority)} files with some implementation:

"""
    
    for file_info in medium_priority:
        report += f"- **{file_info['filename']}** ({file_info['lines']} lines)\n"
        report += f"  Status: {file_info['status']}\n"
        report += f"  Action: REVIEW content for implementation potential\n\n"
    
    report += f"""### LOW PRIORITY - Placeholders

{len(low_priority)} files that are minimal/placeholders:

Keep these as placeholders for future expansion or implement when needed.

## 📋 DECISION REQUIRED

**You need to decide for each HIGH PRIORITY file:**

1. **Should we implement it now?** (It has real functionality)
2. **What should we rename it to?** (Remove Roman numerals)
3. **Where should it go?** (Which module should it integrate with?)

**Recommended next steps:**

1. ✅ **Implement the 4 high-priority files immediately**
2. 🔄 **Rename them to descriptive names**
3. 📊 **Review medium-priority files when time permits**
4. 📝 **Keep placeholders for future expansion**

## 💡 Suggested Implementation Order

1. `makernotes_ultimate_advanced_extension_ii.py` → `camera_makernotes_advanced.py`
2. `scientific_dicom_fits_ultimate_advanced_extension_ii.py` → `cardiac_imaging.py`
3. `scientific_dicom_fits_ultimate_advanced_extension_iii.py` → `neuroimaging.py`
4. `scientific_dicom_fits_ultimate_advanced_extension_xc.py` → `medical_astronomical.py`

These 4 files contain substantial real functionality that should be preserved and integrated into the main codebase.
"""
    
    return report, high_priority, medium_priority, low_priority

if __name__ == "__main__":
    report, high, medium, low = generate_quick_report()
    
    print("="*70)
    print("🚨 ROMAN NUMERAL FILES - IMMEDIATE DECISION NEEDED")
    print("="*70)
    print(f"\n📊 SUMMARY:")
    print(f"- {len(high)} files with REAL functionality need implementation")
    print(f"- {len(medium)} files need content review")
    print(f"- {len(low)} placeholder files to keep")
    
    print(f"\n🎯 ACTION REQUIRED:")
    print("Decide whether to implement the 4 high-priority files with real functionality")
    
    # Save reports
    with open('/Users/pranay/Projects/metaextract/quick_roman_analysis.md', 'w') as f:
        f.write(report)
    
    # Simple CSV for easy review
    with open('/Users/pranay/Projects/metaextract/roman_decision_queue.csv', 'w') as f:
        f.write('Priority,Filename,Lines,Current_Status,Suggested_Action,New_Name\n')
        
        for file_info in high:
            filename = file_info['filename']
            lines = file_info['lines']
            
            if 'makernotes' in filename:
                new_name = "camera_makernotes_advanced.py"
            elif 'cardiac' in str(filename) or 'ii' in filename:
                new_name = "cardiac_imaging.py"
            elif 'neuro' in str(filename) or 'iii' in filename:
                new_name = "neuroimaging.py"
            elif 'medical' in str(filename) or 'xc' in filename:
                new_name = "medical_astronomical.py"
            else:
                new_name = filename.replace('ultimate_advanced_extension_', '').replace('scientific_dicom_fits_', '')
            
            f.write(f'HIGH,{filename},{lines},{file_info["status"]},IMPLEMENT + RENAME,{new_name}\n')
        
        for file_info in medium:
            f.write(f'MEDIUM,{file_info["filename"]},{file_info["lines"]},{file_info["status"]},REVIEW CONTENT,\n')
        
        for file_info in low[:10]:  # First 10 only
            f.write(f'LOW,{file_info["filename"]},{file_info["lines"]},{file_info["status"]},KEEP/IMPLEMENT LATER,\n')
    
    print(f"\n✅ Reports saved:")
    print(f"- quick_roman_analysis.md")
    print(f"- roman_decision_queue.csv")
    print(f"\n🎯 Next: Review the HIGH PRIORITY files and decide on implementation!")

if __name__ == "__main__":
    report, high, medium, low = generate_quick_report()
    print(report)