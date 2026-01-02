#!/usr/bin/env python3

with open('scripts/manage_plugins.py', 'r') as f:
    lines = f.readlines()
    
    # Find the README template
    start_line = None
    end_line = None
    for i, line in enumerate(lines):
        if 'readme_content = f"""' in line:
            start_line = i
        elif start_line is not None and line.strip() == '"""':
            end_line = i
            break
    
    print(f'README template: lines {start_line+1} to {end_line+1}')
    if end_line is None:
        print('❌ README template not closed!')
    else:
        print(f'✅ README template properly closed')
        print(f'Template length: {end_line - start_line} lines')