#!/usr/bin/env python3
"""
Script to scan Python files for imports and identify potentially missing packages.
"""

import os
import ast
import sys
import importlib.util

def find_imports_in_file(filepath):
    """Extract all import statements from a Python file using AST parsing."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse the AST to find imports
        tree = ast.parse(content, filepath)
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])

        return imports
    except Exception as e:
        print(f'Error parsing {filepath}: {e}', file=sys.stderr)
        return set()

def get_stdlib_modules():
    """Get list of standard library modules for Python 3.11."""
    try:
        import stdlib_list
        return set(stdlib_list.stdlib_list('3.11'))
    except ImportError:
        # Fallback list of common stdlib modules
        return {
            'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections', 'contextlib',
            'copy', 'csv', 'datetime', 'decimal', 'enum', 'functools', 'hashlib', 'heapq',
            'hmac', 'html', 'http', 'inspect', 'io', 'itertools', 'json', 'logging',
            'math', 'multiprocessing', 'operator', 'os', 'pathlib', 'pickle', 'platform',
            'queue', 'random', 're', 'shutil', 'socket', 'sqlite3', 'ssl', 'stat',
            'string', 'struct', 'subprocess', 'sys', 'tempfile', 'threading', 'time',
            'traceback', 'typing', 'unittest', 'urllib', 'uuid', 'warnings', 'weakref',
            'xml', 'zipfile', 'zlib'
        }

def is_package_available(package_name):
    """Check if a package is available for import."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def main():
    # Find all Python files
    py_files = []
    for root, dirs, files in os.walk('.'):
        if any(skip in root for skip in ['.venv', 'node_modules', '__pycache__', '.git']):
            continue
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))

    print(f'Found {len(py_files)} Python files')

    # Collect all imports
    all_imports = set()
    for py_file in py_files:
        imports = find_imports_in_file(py_file)
        all_imports.update(imports)

    print(f'Total unique imports found: {len(all_imports)}')

    # Get standard library modules
    stdlib_modules = get_stdlib_modules()

    # Known packages that should be available or are already in dependencies
    known_packages = {
        'torch', 'PIL', 'numpy', 'cv2', 'sklearn', 'pydicom', 'fitz', 'pypdf',
        'requests', 'psutil', 'memory_profiler', 'pytest', 'asyncio', 'pytest_asyncio',
        'ImageHash', 'scipy', 'matplotlib', 'pandas', 'flask', 'fastapi', 'uvicorn',
        'joblib', 'threadpoolctl', 'opencv_python', 'PyMuPDF'
    }

    # Find potentially missing packages
    potential_missing = all_imports - stdlib_modules - known_packages

    # Check which ones are actually missing
    missing_packages = []
    available_packages = []

    for package in sorted(potential_missing):
        if is_package_available(package):
            available_packages.append(package)
        else:
            missing_packages.append(package)

    print(f'\nAvailable packages: {len(available_packages)}')
    for pkg in available_packages[:10]:  # Show first 10
        print(f'  ✓ {pkg}')
    if len(available_packages) > 10:
        print(f'  ... and {len(available_packages) - 10} more')

    print(f'\nPotentially missing packages: {len(missing_packages)}')
    for pkg in missing_packages:
        print(f'  ✗ {pkg}')

    if missing_packages:
        print(f'\nTo install missing packages, run:')
        print(f'  uv add {" ".join(missing_packages)}')
        print(f'  uv lock')
        print(f'  uv sync --locked')

if __name__ == '__main__':
    main()