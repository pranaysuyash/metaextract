#!/usr/bin/env python3

with open('scripts/manage_plugins.py', 'r') as f:
    content = f.read()
    
    # Find epilog area
    epilog_start = content.find('epilog="""')
    if epilog_start == -1:
        print('❌ Epilog not found')
        exit(1)
    
    # Find the next triple quotes
    pos = epilog_start + len('epilog="""')
    triple_quotes = []
    while pos < len(content):
        if content.startswith('"""', pos):
            triple_quotes.append(pos)
            if len(triple_quotes) >= 2:
                break
            pos += 3
        else:
            pos += 1
    
    print(f'Epilog starts at: {epilog_start}')
    print(f'Found {len(triple_quotes)} triple quotes after epilog start')
    
    if len(triple_quotes) >= 2:
        epilog_end = triple_quotes[1]
        epilog_content = content[epilog_start:epilog_end+3]
        print(f'Epilog ends at: {epilog_end}')
        print(f'Epilog length: {len(epilog_content)}')
        
        # Check for intermediate triple quotes
        epilog_content_only = content[epilog_start+len('epilog="""'):epilog_end]
        intermediate = epilog_content_only.count('"""')
        print(f'Intermediate triple quotes: {intermediate}')
        
        if intermediate > 0:
            print('❌ Found intermediate triple quotes in epilog!')
        else:
            print('✅ Epilog looks good')
    else:
        print('❌ Epilog not properly closed')