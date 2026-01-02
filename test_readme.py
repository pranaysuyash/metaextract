#!/usr/bin/env python3

# Test the README template
plugin_name = "test_plugin"
args = type('Args', (), {
    'author': 'Test Author',
    'description': 'Test Description'
})()

readme_content = f"""# {plugin_name.capitalize()} Plugin for MetaExtract

## Overview

The {plugin_name.capitalize()} Plugin provides {args.description or 'comprehensive functionality'} for MetaExtract.

## Plugin Structure

{plugin_name}/
- __init__.py          # Main plugin file
- README.md           # This documentation

## Benefits

- Extensibility: Add custom functionality
- Isolation: Plugins run in their own context
"""

print("✅ README template works")
print(f"Content length: {len(readme_content)}")
print("First 100 chars:", readme_content[:100])
