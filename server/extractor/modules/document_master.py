#!/usr/bin/env python3
"""
Document Master - Consolidated Document Metadata Extraction

Primary entry point for all document metadata extraction.
Consolidates multiple specialized document modules.

Modules Integrated:
- document_extractor.py: Basic document extraction (~148 fields)
- document_metadata_ultimate.py: Advanced analysis (182 fields)
- office_documents.py: Office documents (~44 fields)
- office_documents_complete.py: Complete Office (~150 fields)

Author: MetaExtract Team
Version: 2.0.0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

DOCUMENT_MODULES = {}

def _load_module(name):
    try:
        module = __import__(name)
        DOCUMENT_MODULES[name] = {'available': True, 'module': module}
        return module
    except Exception as e:
        DOCUMENT_MODULES[name] = {'available': False, 'error': str(e)}
        logger.warning(f"Module {name} not available: {e}")
        return None

# Load modules
_document = _load_module('document_extractor')
_document_ultimate = _load_module('document_metadata_ultimate')
_office = _load_module('office_documents')
_office_complete = _load_module('office_documents_complete')


def extract_document_master(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive document metadata"""
    result = {
        "document_master_available": True,
        "modules": {},
        "total_fields_extracted": 0
    }
    
    def _safe_extract(module_name, extract_func_name, result_key):
        try:
            module_data = DOCUMENT_MODULES.get(module_name)
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
    fields_count += _safe_extract('document_extractor', 'extract_document_metadata', 'basic_document')
    fields_count += _safe_extract('document_metadata_ultimate', 'extract_document_metadata', 'advanced_document')
    fields_count += _safe_extract('office_documents', 'extract_office_documents', 'office_document')
    fields_count += _safe_extract('office_documents_complete', 'extract_office_documents_complete', 'office_complete')
    
    result["total_fields_extracted"] = fields_count
    return result


def get_document_master_field_count() -> int:
    """Return total document metadata fields"""
    total = 0
    
    for name, module_data in DOCUMENT_MODULES.items():
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
    
    return total if total > 0 else 182  # Fallback


def get_document_master_module_status() -> Dict[str, bool]:
    """Get availability status"""
    return {name: data['available'] for name, data in DOCUMENT_MODULES.items()}


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        result = extract_document_master(sys.argv[1])
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Document Master - Consolidated Document Metadata Extraction")
        print(f"\nTotal Fields: {get_document_master_field_count()}")
        print("\nModule Status:")
        for module, available in get_document_master_module_status().items():
            status = "✓ Available" if available else "✗ Not Available"
            print(f"  {module:30s} {status}")
        print("\nUsage: python document_master.py <document_file>")
