#!/usr/bin/env python3

with open('scripts/manage_plugins.py', 'rb') as f:
    content = f.read()
    
    # Find the epilog closing
    epilog_start = content.find(b'epilog="""')
    if epilog_start == -1:
        print('Epilog not found')
        exit(1)
    
    print(f'Epilog starts at byte position: {epilog_start}')
    
    # Look for closing triple quotes
    pos = epilog_start + len(b'epilog="""')
    found_closing = False
    while pos < len(content):
        if content.startswith(b'"""', pos):
            print(f'Found triple quote at byte position {pos}')
            # Check what comes after
            next_chars = content[pos+3:pos+10]
            print(f'After triple quote: {repr(next_chars)}')
            found_closing = True
            break
        pos += 1
    
    if not found_closing:
        print('No closing triple quote found')
        # Show what's at the end
        print(f'Content from {pos}: {repr(content[pos:pos+50])}')