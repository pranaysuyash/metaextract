#!/usr/bin/env python3
"""
Test script for new domain modules in the comprehensive metadata engine
"""

import os
import sys
import json
from pathlib import Path

# Add the server directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.join(current_dir, 'server')
sys.path.insert(0, server_dir)

try:
    from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata
    print("✓ Successfully imported comprehensive metadata engine")
except ImportError as e:
    print(f"✗ Failed to import comprehensive metadata engine: {e}")
    sys.exit(1)

def test_new_domains():
    """Test the new domain modules"""
    
    # Create test files for different domains
    test_files = {
        "healthcare_test.dcm": "healthcare_medical",
        "transport_gps.gpx": "transportation_logistics", 
        "course_content.scorm": "education_academic",
        "contract_legal.pdf": "legal_compliance",
        "environmental_data.csv": "environmental_sustainability",
        "social_post.json": "social_media_digital",
        "game_save.dat": "gaming_entertainment"
    }
    
    print("\nTesting new domain modules:")
    print("=" * 50)
    
    for filename, domain in test_files.items():
        # Create a temporary test file
        test_file_path = f"/tmp/{filename}"
        
        try:
            # Create a minimal test file
            with open(test_file_path, 'w') as f:
                if filename.endswith('.json'):
                    f.write('{"test": "data", "platform": "facebook", "post_type": "status"}')
                elif filename.endswith('.csv'):
                    f.write('timestamp,temperature,humidity\n2024-01-01,25.5,60.2\n')
                elif filename.endswith('.scorm'):
                    f.write('<?xml version="1.0"?><manifest><metadata><schema>ADL SCORM</schema></metadata></manifest>')
                else:
                    f.write(f"Test content for {domain}")
            
            print(f"\nTesting {domain} with {filename}:")
            
            # Extract metadata using super tier to enable all modules
            result = extract_comprehensive_metadata(test_file_path, tier="super")
            
            if result:
                # Check if the domain-specific metadata was extracted
                if domain in result:
                    print(f"  ✓ {domain} module executed successfully")
                    domain_result = result[domain]
                    if isinstance(domain_result, dict):
                        if domain_result.get("available"):
                            print(f"  ✓ {domain} analysis completed")
                            # Print some key fields if available
                            if hasattr(domain_result, 'keys'):
                                key_count = len([k for k in domain_result.keys() if k != 'available'])
                                print(f"  ✓ Extracted {key_count} metadata categories")
                        else:
                            print(f"  ⚠ {domain} module not available: {domain_result.get('reason', 'Unknown')}")
                    else:
                        print(f"  ⚠ {domain} returned unexpected result type: {type(domain_result)}")
                else:
                    print(f"  ⚠ {domain} not found in results")
                
                # Check capabilities
                capabilities = result.get("extraction_info", {}).get("capabilities", {})
                if capabilities.get(domain):
                    print(f"  ✓ {domain} capability enabled")
                else:
                    print(f"  ⚠ {domain} capability not enabled")
                    
            else:
                print(f"  ✗ Failed to extract metadata from {filename}")
                
        except Exception as e:
            print(f"  ✗ Error testing {domain}: {e}")
        
        finally:
            # Clean up test file
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
    
    print("\n" + "=" * 50)
    print("New domain module testing completed!")

def test_module_imports():
    """Test that all new modules can be imported"""
    
    print("\nTesting module imports:")
    print("=" * 30)
    
    modules_to_test = [
        "healthcare_medical_ultimate",
        "transportation_logistics_ultimate", 
        "education_academic_ultimate",
        "legal_compliance_ultimate",
        "environmental_sustainability_ultimate",
        "social_media_digital_ultimate",
        "gaming_entertainment_ultimate"
    ]
    
    for module_name in modules_to_test:
        try:
            module_path = f"server/extractor/modules/{module_name}.py"
            if os.path.exists(module_path):
                print(f"✓ {module_name}.py exists")
                
                # Try to import the extraction function
                import importlib.util
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Check if the main extraction function exists
                    func_name = f"extract_{module_name.replace('_ultimate', '')}_metadata"
                    if hasattr(module, func_name):
                        print(f"  ✓ {func_name} function found")
                    else:
                        print(f"  ⚠ {func_name} function not found")
                else:
                    print(f"  ✗ Failed to load module spec")
            else:
                print(f"✗ {module_name}.py not found")
                
        except Exception as e:
            print(f"✗ Error importing {module_name}: {e}")

if __name__ == "__main__":
    print("MetaExtract New Domain Modules Test")
    print("=" * 40)
    
    # Test module imports first
    test_module_imports()
    
    # Test domain extraction
    test_new_domains()
    
    print("\nTest completed!")