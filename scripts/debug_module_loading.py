#!/usr/bin/env python3
"""
Debug script to test the module discovery system and find actual syntax errors
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging to see detailed errors
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_module_discovery():
    """Test the module discovery system."""
    
    from server.extractor.module_discovery import ModuleRegistry
    
    print("Testing module discovery system...")
    print("=" * 60)
    
    registry = ModuleRegistry()
    
    # Test discovery
    try:
        registry.discover_modules("server/extractor/modules/")
        
        print(f"\nDiscovery completed:")
        print(f"  Total discovered: {registry.discovered_count}")
        print(f"  Successfully loaded: {registry.loaded_count}")
        print(f"  Failed to load: {registry.failed_count}")
        print(f"  Discovery time: {registry.discovery_time:.3f}s")
        
        if registry.disabled_modules:
            print(f"\nDisabled modules ({len(registry.disabled_modules)}):")
            for module in sorted(registry.disabled_modules):
                print(f"  - {module}")
                
        # Test DICOM extensions specifically
        print(f"\nDICOM Extensions:")
        dicom_modules = [name for name in registry.modules.keys() if 'dicom' in name.lower()]
        print(f"  Found {len(dicom_modules)} DICOM-related modules")
        
        # Check for specific DICOM extension modules
        dicom_extensions = [name for name in registry.modules.keys() if any(ext in name for ext in [
            'mammography', 'cardiology', 'ultrasound', 'angiography', 'ct_', 'mri', 'pet_', 'xray'
        ])]
        print(f"  Found {len(dicom_extensions)} DICOM specialty modules")
        
        return registry
        
    except Exception as e:
        print(f"Error during module discovery: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_dicom_extension_discovery():
    """Test DICOM extension discovery specifically."""
    
    from server.extractor.modules.dicom_extensions.registry import DICOMExtensionRegistry
    
    print("\n\nTesting DICOM extension discovery...")
    print("=" * 60)
    
    registry = DICOMExtensionRegistry()
    
    try:
        registry.auto_discover_extensions("server.extractor.modules.dicom_extensions")
        
        specialties = registry.get_all_specialties()
        print(f"DICOM specialties discovered: {len(specialties)}")
        
        for specialty in specialties:
            info = registry.get_extension_info(specialty)
            if info:
                print(f"  - {specialty}: {info.get('field_count', 0)} fields")
        
        total_fields = registry.get_total_field_capacity()
        print(f"\nTotal DICOM field capacity: {total_fields}")
        
        return registry
        
    except Exception as e:
        print(f"Error during DICOM extension discovery: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Test main module discovery
    registry = test_module_discovery()
    
    # Test DICOM extension discovery
    dicom_registry = test_dicom_extension_discovery()
    
    if registry and dicom_registry:
        print("\nModule discovery test completed successfully!")
    else:
        print("\nModule discovery test failed!")
        sys.exit(1)