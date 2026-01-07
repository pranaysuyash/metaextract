#!/usr/bin/env python3
"""
Comprehensive Field Counter - Count all fields from all modules
"""

import sys
import os
from pathlib import Path
import importlib.util

# Add server to path
server_root = Path(__file__).parent.absolute() / "server"
sys.path.insert(0, str(server_root))
sys.path.insert(1, str(server_root / "extractor"))

print("=" * 80)
print("COMPREHENSIVE METAFIELD COUNT - ALL MODULES")
print("=" * 80)
print()

modules_dir = server_root / "extractor" / "modules"

total_fields = 0
module_counts = {}
failed_imports = []
no_field_count = []

# Find all Python modules in modules directory
for py_file in sorted(modules_dir.glob("*.py")):
    if py_file.name.startswith("__") or py_file.name.endswith(".bak"):
        continue

    module_name = py_file.stem
    full_module_path = f"extractor.modules.{module_name}"

    try:
        # Try to import the module
        module = importlib.import_module(full_module_path)

        # Look for field count function
        field_count_func_name = f"get_{module_name}_field_count"

        # Try common variations
        for func_name in [
            field_count_func_name,
            f"get_{module_name.replace('_', '')}_field_count",
            "get_field_count",
            "count_fields"
        ]:
            if hasattr(module, func_name):
                try:
                    field_count = getattr(module, func_name)()
                    module_counts[module_name] = field_count
                    total_fields += field_count
                    print(f"✓ {module_name:60} {field_count:6} fields")
                    break
                except Exception as e:
                    print(f"✗ {module_name:60} ERROR in field count: {e}")
                    break
        else:
            no_field_count.append(module_name)

    except Exception as e:
        failed_imports.append((module_name, str(e)))

print()
print("=" * 80)
print(f"TOTAL FIELDS ACROSS ALL MODULES: {total_fields:,}")
print("=" * 80)
print()

if failed_imports:
    print(f"Failed imports ({len(failed_imports)}):")
    for module_name, error in failed_imports[:10]:  # Show first 10
        print(f"  - {module_name}: {error[:100]}")
    if len(failed_imports) > 10:
        print(f"  ... and {len(failed_imports) - 10} more")
    print()

if no_field_count:
    print(f"Modules without field count function ({len(no_field_count)}):")
    for module_name in no_field_count[:10]:  # Show first 10
        print(f"  - {module_name}")
    if len(no_field_count) > 10:
        print(f"  ... and {len(no_field_count) - 10} more")
    print()

print(f"Successfully counted fields from {len(module_counts)} modules")
