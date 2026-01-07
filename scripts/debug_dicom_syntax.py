#!/usr/bin/env python3
"""
Debug script to identify syntax errors in DICOM extension modules
"""

import os
import sys
import importlib
import importlib.util
import traceback
from pathlib import Path

def test_dicom_extensions():
    """Test importing DICOM extension modules to find syntax errors."""
    
    dicom_extensions_dir = Path("server/extractor/modules/dicom_extensions")
    
    if not dicom_extensions_dir.exists():
        print(f"Directory not found: {dicom_extensions_dir}")
        return
    
    print("Testing DICOM extension modules for syntax errors...")
    print("=" * 60)
    
    failed_modules = []
    successful_modules = []
    
    # Test each Python file in the directory
    for py_file in dicom_extensions_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue
            
        module_name = py_file.stem
        print(f"\nTesting: {module_name}")
        
        try:
            # Try to import the module
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec is None:
                print(f"  ❌ Could not create spec for {module_name}")
                failed_modules.append((module_name, "Could not create spec"))
                continue
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            print(f"  ✅ Successfully imported")
            successful_modules.append(module_name)
            
        except SyntaxError as e:
            error_msg = f"Syntax error: {e}"
            print(f"  ❌ {error_msg}")
            print(f"     Line {e.lineno}: {e.text}")
            failed_modules.append((module_name, error_msg))
            
        except ImportError as e:
            error_msg = f"Import error: {e}"
            print(f"  ⚠️  {error_msg}")
            # Import errors might be due to missing dependencies, not syntax
            
        except Exception as e:
            error_msg = f"Other error: {e}"
            print(f"  ❌ {error_msg}")
            failed_modules.append((module_name, error_msg))
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Successful modules: {len(successful_modules)}")
    print(f"Failed modules: {len(failed_modules)}")
    
    if failed_modules:
        print("\nFailed modules:")
        for module_name, error in failed_modules:
            print(f"  - {module_name}: {error}")
    
    return failed_modules

if __name__ == "__main__":
    # Add the project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    failed = test_dicom_extensions()
    
    if failed:
        print(f"\nFound {len(failed)} modules with errors")
        sys.exit(1)
    else:
        print("\nAll modules imported successfully!")
        sys.exit(0)