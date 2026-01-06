#!/usr/bin/env python3
"""
Fix DICOM syntax errors in scientific modules

This script fixes invalid hexadecimal literals like "0xL001" 
that should be "0x1001" in the DICOM extension modules.
"""

import os
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fix_hexadecimal_syntax(content: str) -> str:
    """
    Fix invalid hexadecimal syntax patterns in the content.
    
    The main issue is patterns like (0x0010, 0xL001) which should be (0x0010, 0x1001)
    Also handles other invalid patterns like 0xJ001, 0xH001, 0xI001, 0xM001, 0xN001
    """
    # Pattern to match invalid hex literals with letters in them
    # This matches patterns like 0xL001, 0xJ001, 0xH001, 0xI001, 0xM001, 0xN001, etc.
    invalid_hex_patterns = [
        (r'0xL([0-9A-Fa-f]+)', '0x1'),     # L -> 1
        (r'0xJ([0-9A-Fa-f]+)', '0x1'),     # J -> 1  
        (r'0xH([0-9A-Fa-f]+)', '0x1'),     # H -> 1
        (r'0xI([0-9A-Fa-f]+)', '0x1'),     # I -> 1
        (r'0xM([0-9A-Fa-f]+)', '0x1'),     # M -> 1
        (r'0xN([0-9A-Fa-f]+)', '0x1'),     # N -> 1
        (r'0xO([0-9A-Fa-f]+)', '0x0'),     # O -> 0 (less common)
        (r'0xP([0-9A-Fa-f]+)', '0x1'),     # P -> 1
        (r'0xQ([0-9A-Fa-f]+)', '0x1'),     # Q -> 1
        (r'0xR([0-9A-Fa-f]+)', '0x1'),     # R -> 1
        (r'0xS([0-9A-Fa-f]+)', '0x1'),     # S -> 1
        (r'0xT([0-9A-Fa-f]+)', '0x1'),     # T -> 1
        (r'0xU([0-9A-Fa-f]+)', '0x1'),     # U -> 1
        (r'0xV([0-9A-Fa-f]+)', '0x1'),     # V -> 1
        (r'0xW([0-9A-Fa-f]+)', '0x1'),     # W -> 1
        (r'0xX([0-9A-Fa-f]+)', '0x1'),     # X -> 1
        (r'0xY([0-9A-Fa-f]+)', '0x1'),     # Y -> 1
        (r'0xZ([0-9A-Fa-f]+)', '0x1'),     # Z -> 1
    ]
    
    corrected_content = content
    
    for pattern, replacement in invalid_hex_patterns:
        def replace_invalid_hex(match):
            hex_digits = match.group(1)
            corrected = f'{replacement}{hex_digits}'
            logger.debug(f"Corrected hex literal: {match.group(0)} -> {corrected}")
            return corrected
        
        corrected_content = re.sub(pattern, replace_invalid_hex, corrected_content)
    
    # Also fix any tuple patterns
    tuple_pattern = r'\(0x[0-9A-Fa-f]+,\s*0x[A-Z][0-9A-Fa-f]+\)'
    
    def replace_tuple_hex(match):
        # Extract the tuple and fix invalid hex literals
        tuple_str = match.group(0)
        # Replace all invalid hex patterns in the tuple
        corrected_tuple = tuple_str
        for pattern, replacement in invalid_hex_patterns:
            corrected_tuple = re.sub(pattern, f'{replacement}\\1', corrected_tuple)
        logger.debug(f"Corrected tuple: {tuple_str} -> {corrected_tuple}")
        return corrected_tuple
    
    corrected_content = re.sub(tuple_pattern, replace_tuple_hex, corrected_content)
    
    return corrected_content


def fix_dicom_module_file(file_path: Path) -> bool:
    """
    Fix syntax errors in a single DICOM module file.
    
    Args:
        file_path: Path to the Python file to fix
        
    Returns:
        True if file was modified, False otherwise
    """
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Fix syntax errors
        corrected_content = fix_hexadecimal_syntax(original_content)
        
        # Check if content changed
        if corrected_content != original_content:
            # Write back the corrected content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(corrected_content)
            
            logger.info(f"Fixed syntax errors in: {file_path}")
            return True
        else:
            logger.debug(f"No syntax errors found in: {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return False


def find_and_fix_dicom_modules():
    """
    Find all DICOM modules with syntax errors and fix them.
    """
    modules_dir = Path("server/extractor/modules")
    
    if not modules_dir.exists():
        logger.error(f"Modules directory not found: {modules_dir}")
        return
    
    # Find files with potential syntax errors
    problematic_files = []
    
    # First, find files that contain the invalid pattern
    for py_file in modules_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for invalid hex patterns
            if re.search(r'0xL[0-9A-Fa-f]+', content):
                problematic_files.append(py_file)
                logger.info(f"Found syntax errors in: {py_file.name}")
                
        except Exception as e:
            logger.error(f"Error reading file {py_file}: {e}")
    
    logger.info(f"Found {len(problematic_files)} files with potential syntax errors")
    
    # Fix the problematic files
    fixed_count = 0
    for file_path in problematic_files:
        if fix_dicom_module_file(file_path):
            fixed_count += 1
    
    logger.info(f"Fixed syntax errors in {fixed_count} files")
    
    # Test if the files can now be imported
    test_import_results(file_path.parent for file_path in problematic_files)


def test_import_results(fixed_dirs):
    """
    Test if the fixed files can be imported without syntax errors.
    """
    import sys
    import importlib.util
    import traceback
    
    logger.info("Testing import of fixed modules...")
    
    success_count = 0
    failure_count = 0
    
    for modules_dir in fixed_dirs:
        for py_file in modules_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            try:
                # Try to import the module
                spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
                if spec is None:
                    logger.error(f"Could not create spec for {py_file.name}")
                    failure_count += 1
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                logger.debug(f"Successfully imported: {py_file.name}")
                success_count += 1
                
            except SyntaxError as e:
                logger.error(f"Syntax error in {py_file.name}: {e}")
                logger.error(f"  Line {e.lineno}: {e.text}")
                failure_count += 1
                
            except ImportError as e:
                # Import errors might be due to missing dependencies, not syntax
                logger.warning(f"Import error in {py_file.name}: {e}")
                success_count += 1  # Consider syntax-fixed even if dependencies are missing
                
            except Exception as e:
                logger.error(f"Other error in {py_file.name}: {e}")
                failure_count += 1
    
    logger.info(f"Import test results: {success_count} successful, {failure_count} failed")
    return success_count, failure_count


def main():
    """Main function to fix DICOM syntax errors."""
    logger.info("Starting DICOM syntax error fix...")
    
    # Find and fix DICOM modules
    find_and_fix_dicom_modules()
    
    logger.info("DICOM syntax error fix completed!")


if __name__ == "__main__":
    main()