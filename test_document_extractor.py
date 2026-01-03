#!/usr/bin/env python3
"""
Test script for the new document extractor.
"""

import sys
import os
from pathlib import Path

# Add the server directory to the path
server_path = os.path.join(os.path.dirname(__file__), 'server')
sys.path.insert(0, server_path)

def test_document_extractor():
    """Test the document extractor."""
    
    print("Testing Document Extractor")
    print("=" * 30)
    
    try:
        # Test 1: Import document extractor
        print("1. Testing document extractor import...")
        from extractor.extractors.document_extractor import DocumentExtractor
        from extractor.core.base_engine import ExtractionContext
        
        extractor = DocumentExtractor()
        print(f"   ✅ Document extractor created: {extractor.name}")
        print(f"   ✅ Supported formats: {len(extractor.supported_formats)} formats")
        print(f"   ✅ First few formats: {extractor.supported_formats[:8]}")
        
        # Test 2: Test with non-existent file (should handle gracefully)
        print("2. Testing with non-existent file...")
        context = ExtractionContext(
            filepath="nonexistent.pdf",
            file_size=1024,
            file_extension=".pdf",
            mime_type="application/pdf",
            tier="free",
            processing_options={},
            execution_stats={}
        )
        
        result = extractor.extract(context)
        print(f"   ✅ Extraction status: {result.status}")
        print(f"   ✅ Processing time: {result.processing_time_ms}ms")
        
        if result.metadata:
            print(f"   ✅ Metadata sections: {list(result.metadata.keys())}")
        
        # Test 3: Test extractor info
        print("3. Testing extractor info...")
        info = extractor.get_extraction_info()
        print(f"   ✅ Extractor info: {info}")
        
        # Test 4: Test with a real document if available
        print("4. Testing with sample documents...")
        
        # Create simple test documents
        test_files = []
        
        # Test PDF
        pdf_file = "test_sample.pdf"
        try:
            # Create a minimal PDF
            pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF'
            
            with open(pdf_file, 'wb') as f:
                f.write(pdf_content)
            
            test_files.append((pdf_file, "PDF"))
            
        except Exception as e:
            print(f"   ⚠️  Could not create PDF test file: {e}")
        
        # Test HTML
        html_file = "test_sample.html"
        try:
            html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Test Document</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>Test HTML Document</h1>
    <p>This is a test HTML document for document extractor testing.</p>
</body>
</html>'''
            
            with open(html_file, 'w') as f:
                f.write(html_content)
            
            test_files.append((html_file, "HTML"))
            
        except Exception as e:
            print(f"   ⚠️  Could not create HTML test file: {e}")
        
        # Test JSON
        json_file = "test_sample.json"
        try:
            import json
            json_content = {
                "title": "Test Document",
                "version": "1.0",
                "content": {
                    "type": "test",
                    "data": [1, 2, 3, 4, 5]
                }
            }
            
            with open(json_file, 'w') as f:
                json.dump(json_content, f, indent=2)
            
            test_files.append((json_file, "JSON"))
            
        except Exception as e:
            print(f"   ⚠️  Could not create JSON test file: {e}")
        
        # Test each file
        for test_file, file_type in test_files:
            if os.path.exists(test_file):
                print(f"\n   Testing {file_type} file: {test_file}")
                
                context = ExtractionContext(
                    filepath=test_file,
                    file_size=os.path.getsize(test_file),
                    file_extension=Path(test_file).suffix.lower(),
                    mime_type=_get_mime_type(test_file),
                    tier="free",
                    processing_options={},
                    execution_stats={}
                )
                
                result = extractor.extract(context)
                
                print(f"   ✅ Status: {result.status}")
                print(f"   ✅ Processing time: {result.processing_time_ms}ms")
                
                if result.metadata:
                    sections = list(result.metadata.keys())
                    print(f"   ✅ Metadata sections: {sections}")
                    
                    # Show some specific results
                    if 'pdf' in result.metadata:
                        pdf_data = result.metadata['pdf']
                        print(f"   📄 PDF pages: {pdf_data.get('page_count', 'unknown')}")
                    if 'html' in result.metadata:
                        html_data = result.metadata['html']
                        print(f"   🌐 HTML has title: {html_data.get('has_title', False)}")
                    if 'structured' in result.metadata:
                        struct_data = result.metadata['structured']
                        print(f"   📊 Structured data format: {struct_data.get('format', 'unknown')}")
        
        print("\n✅ Document extractor tests completed!")
        
        # Cleanup
        for test_file, _ in test_files:
            if os.path.exists(test_file):
                os.remove(test_file)
                print(f"   🧹 Cleaned up: {test_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Document extractor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
def _get_mime_type(filepath: str) -> str:
    """Get MIME type for test file."""
    ext = Path(filepath).suffix.lower()
    mime_map = {
        '.pdf': 'application/pdf',
        '.html': 'text/html',
        '.htm': 'text/html',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.txt': 'text/plain',
        '.csv': 'text/csv'
    }
    return mime_map.get(ext, 'application/octet-stream')

if __name__ == "__main__":
    success = test_document_extractor()
    if success:
        print("\n🎉 Document extractor ready!")
    else:
        print("\n❌ Document extractor needs fixes.")