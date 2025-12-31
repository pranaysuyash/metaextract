#!/usr/bin/env python3
"""
Scientific Master - Consolidated Scientific Metadata Extraction

Primary entry point for all scientific metadata extraction.
Consolidates multiple specialized scientific modules.

Modules Integrated:
- scientific_data.py: Basic scientific (~320 fields)
- dicom_complete_ultimate.py: DICOM imaging (~391 fields)
- fits_extractor.py: FITS astronomy (~572 fields)
- genomic_extractor.py: Genomic data (~150 fields)

Author: MetaExtract Team
Version: 2.0.0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

SCIENTIFIC_MODULES = {}

def _load_module(name):
    try:
        module = __import__(name)
        SCIENTIFIC_MODULES[name] = {'available': True, 'module': module}
        return module
    except Exception as e:
        SCIENTIFIC_MODULES[name] = {'available': False, 'error': str(e)}
        logger.warning(f"Module {name} not available: {e}")
        return None

# Load modules
_scientific = _load_module('scientific_data')
_dicom_ultimate = _load_module('dicom_complete_ultimate')
_fits = _load_module('fits_extractor')
_genomic = _load_module('genomic_extractor')


def extract_scientific_master(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive scientific metadata"""
    result = {
        "scientific_master_available": True,
        "modules": {},
        "total_fields_extracted": 0
    }
    
    def _safe_extract(module_name, extract_func_name, result_key):
        try:
            module_data = SCIENTIFIC_MODULES.get(module_name)
            if module_data and module_data['available']:
                module = module_data['module']
                if hasattr(module, extract_func_name):
                    extract_func = getattr(module, extract_func_name)
                    data = extract_func(filepath)
                    if data and not isinstance(data, type(None)):
                        result["modules"][result_key] = data
                        result["modules"][f"{result_key}_available"] = True
                        return len([k for k in data.keys() if not k.endswith('_available')])
        except Exception as e:
            logger.error(f"Error extracting from {module_name}: {e}")
            result["modules"][f"{result_key}_error"] = str(e)
        return 0
    
    fields_count = 0
    fields_count += _safe_extract('scientific_data', 'extract_scientific_data', 'basic_scientific')
    fields_count += _safe_extract('dicom_complete_ultimate', 'extract_dicom_complete_ultimate', 'dicom_ultimate')
    fields_count += _safe_extract('fits_extractor', 'extract_fits_metadata', 'fits')
    fields_count += _safe_extract('genomic_extractor', 'extract_genomic_metadata', 'genomic')
    
    result["total_fields_extracted"] = fields_count
    return result


def get_scientific_master_field_count() -> int:
    """Return total scientific metadata fields"""
    total = 0
    
    for name, module_data in SCIENTIFIC_MODULES.items():
        if module_data['available']:
            module = module_data['module']
            for attr_name in dir(module):
                if 'field_count' in attr_name.lower() and callable(getattr(module, attr_name)):
                    try:
                        field_count_func = getattr(module, attr_name)
                        count = field_count_func()
                        total += count
                    except:
                        pass
                    break
    
    return total if total > 0 else 572  # Fallback to FITS


def get_scientific_master_module_status() -> Dict[str, bool]:
    """Get availability status"""
    return {name: data['available'] for name, data in SCIENTIFIC_MODULES.items()}


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        result = extract_scientific_master(sys.argv[1])
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Scientific Master - Consolidated Scientific Metadata Extraction")
        print(f"\nTotal Fields: {get_scientific_master_field_count()}")
        print("\nModule Status:")
        for module, available in get_scientific_master_module_status().items():
            status = "✓ Available" if available else "✗ Not Available"
            print(f"  {module:30s} {status}")
        print("\nUsage: python scientific_master.py <scientific_file>")
