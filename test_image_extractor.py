#!/usr/bin/env python3
"""
Test script for the new image extractor.
"""

import sys
import os
from pathlib import Path

# Add the server directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from extractor.extractors.image_extractor import ImageExtractor
from extractor.core.base_engine import ExtractionContext

def test_image_extractor():
    """Test the image extractor with a sample image."""
    
    # Create an image extractor instance
    extractor = ImageExtractor()
    
    print(f"Image Extractor Info: {extractor.get_extraction_info()}")
    
    # Test with a sample image if available
    test_files = [
        "test_ultra_comprehensive.jpg",
        "test_images/20251225_44810PMByGPSMapCamera_A27, Santhosapuram, Kudremukh Colony, Koramangala_Bengaluru_Karnataka_India_12_923974_77_6254197J4VWJFG+H5GMT_+05_30.jpg",
        "test_images/sample.jpg",
        "test_images/test.jpg", 
        "sample-files/sample.jpg",
        "tests/fixtures/test.jpg"
    ]
    
    test_file = None
    for file_path in test_files:
        if os.path.exists(file_path):
            test_file = file_path
            break
    
    if not test_file:
        print("No test image file found. Creating a minimal test...")
        # Create a minimal extraction context
        context = ExtractionContext(
            filepath="nonexistent.jpg",
            file_size=1024,
            file_extension=".jpg",
            mime_type="image/jpeg",
            tier="free",
            processing_options={},
            execution_stats={}
        )
        
        # Test if extractor can handle the file
        can_extract = extractor.can_extract("test.jpg")
        print(f"Can extract test.jpg: {can_extract}")
        
        # Test extraction (should fail gracefully)
        try:
            result = extractor.extract(context)
            print(f"Extraction result status: {result.status}")
            print(f"Extraction result metadata keys: {list(result.metadata.keys()) if result.metadata else 'None'}")
        except Exception as e:
            print(f"Extraction failed as expected: {e}")
        
        return
    
    print(f"Testing with file: {test_file}")
    
    # Create extraction context
    context = ExtractionContext(
        filepath=test_file,
        file_size=os.path.getsize(test_file),
        file_extension=Path(test_file).suffix.lower(),
        mime_type="image/jpeg",
        tier="free",
        processing_options={},
        execution_stats={}
    )
    
    # Test extraction
    try:
        result = extractor.extract(context)
        print(f"Extraction status: {result.status}")
        print(f"Processing time: {result.processing_time_ms}ms")
        
        if result.metadata:
            print(f"Extracted metadata sections: {list(result.metadata.keys())}")
            
            # Show some sample metadata
            if 'file_info' in result.metadata:
                print(f"File info: {result.metadata['file_info']}")
            if 'exif' in result.metadata:
                exif_keys = list(result.metadata['exif'].keys())[:5]  # First 5 EXIF keys
                print(f"Sample EXIF keys: {exif_keys}")
            if 'gps' in result.metadata:
                print(f"GPS data: {result.metadata['gps']}")
        
        if result.error_message:
            print(f"Error: {result.error_message}")
            
    except Exception as e:
        print(f"Extraction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_extractor()