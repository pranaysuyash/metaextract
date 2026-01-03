#!/usr/bin/env python3

# Test if the basic structure works
print("Testing basic structure...")

# Test the problematic part
plugin_name = "test_plugin"
readme_content = f"""# {plugin_name.capitalize()} Plugin for MetaExtract

Simple test content
"""

print("✅ Basic f-string works")
print(f"Content length: {len(readme_content)}")
