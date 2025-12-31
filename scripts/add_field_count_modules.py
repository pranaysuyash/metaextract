#!/usr/bin/env python3
"""Script to add new module imports to field_count.py"""

import re

FIELD_COUNT_PATH = '/Users/pranay/Projects/metaextract/field_count.py'

NEW_IMPORTS = '''
# Phase 3 modules - COMPLETE (NEW)
try:
    from pdf_complete_ultimate import get_pdf_complete_ultimate_field_count
    PDF_COMPLETE_ULTIMATE_AVAILABLE = True
except:
    PDF_COMPLETE_ULTIMATE_AVAILABLE = False

try:
    from office_documents_complete import get_office_documents_complete_field_count
    OFFICE_DOCUMENTS_COMPLETE_AVAILABLE = True
except:
    OFFICE_DOCUMENTS_COMPLETE_AVAILABLE = False

try:
    from id3_frames_complete import get_id3_frames_field_count
    ID3_FRAMES_COMPLETE_AVAILABLE = True
except:
    ID3_FRAMES_COMPLETE_AVAILABLE = False
'''

NEW_COUNTING_SECTION = '''
if PDF_COMPLETE_ULTIMATE_AVAILABLE:
    pdf_complete_ultimate_count = get_pdf_complete_ultimate_field_count()
    print(f'{"PDF Complete Ultimate":30s}: {pdf_complete_ultimate_count:>5} fields')
    total += pdf_complete_ultimate_count
    phase3_total += pdf_complete_ultimate_count
else:
    print(f'{"PDF Complete Ultimate":30s}: {0:>5} fields (pending)')

if OFFICE_DOCUMENTS_COMPLETE_AVAILABLE:
    office_complete_count = get_office_documents_complete_field_count()
    print(f'{"Office Documents Complete":30s}: {office_complete_count:>5} fields')
    total += office_complete_count
    phase3_total += office_complete_count
else:
    print(f'{"Office Documents Complete":30s}: {0:>5} fields (pending)')

if ID3_FRAMES_COMPLETE_AVAILABLE:
    id3_complete_count = get_id3_frames_field_count()
    print(f'{"ID3 Frames Complete":30s}: {id3_complete_count:>5} fields')
    total += id3_complete_count
    phase3_total += id3_complete_count
else:
    print(f'{"ID3 Frames Complete":30s}: {0:>5} fields (pending)')
'''

def main():
    with open(FIELD_COUNT_PATH, 'r') as f:
        content = f.read()
    
    # Check if imports already exist
    if 'PDF_COMPLETE_ULTIMATE_AVAILABLE' in content:
        print("PDF_COMPLETE_ULTIMATE_AVAILABLE already exists, skipping import addition")
    else:
        # Find the end of Phase 3 modules section and insert new imports
        # Look for "if EMAIL_AVAILABLE:" block ending
        pattern = r'(try:\n    from email_metadata import get_email_field_count\n    EMAIL_AVAILABLE = True\nexcept:\n    EMAIL_AVAILABLE = False)'
        match = re.search(pattern, content)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + NEW_IMPORTS + content[insert_pos:]
            print("Added new imports")
        else:
            print("Could not find insertion point for imports")
            return
    
    # Add counting section
    if 'Office Documents Complete' in content:
        print("Office Documents Complete counting already exists, skipping")
    else:
        # Find the Office Documents counting section
        pattern = r'(if OFFICE_DOCUMENTS_AVAILABLE:\n    office_count = get_office_field_count\(\)\n    print\(f\'\{"Office Documents":30s\}: \{office_count:>5\} fields\'\)\n    total \+= office_count\n    phase3_total \+= office_count\nelse:\n    print\(f\'\{"Office Documents":30s\}: \{0:>5\} fields \(pending\)\'\))'
        match = re.search(pattern, content)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + NEW_COUNTING_SECTION + content[insert_pos:]
            print("Added new counting section")
        else:
            print("Could not find insertion point for counting section")
            # Try a simpler pattern
            simple_pattern = r'(if OFFICE_DOCUMENTS_AVAILABLE:\n    office_count = get_office_field_count\(\))'
            match = re.search(simple_pattern, content)
            if match:
                insert_pos = match.end()
                # Find the end of this block
                end_pattern = r'(\n    print\(f\'\{".*":30s\}: \{0:>5\} fields \(pending\)\'\))'
                end_match = re.search(end_pattern, content[insert_pos:])
                if end_match:
                    insert_pos = insert_pos + end_match.end()
                    content = content[:insert_pos] + NEW_COUNTING_SECTION + content[insert_pos:]
                    print("Added new counting section (simple pattern)")
                else:
                    print("Could not find end of Office Documents block")
            else:
                print("Could not find Office Documents counting section")
    
    with open(FIELD_COUNT_PATH, 'w') as f:
        f.write(content)
    
    print("Done!")

if __name__ == '__main__':
    main()
