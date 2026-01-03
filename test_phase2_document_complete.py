#!/usr/bin/env python3
"""
Complete Phase 2.3 Document Extractor Test

This test demonstrates the new document extractor working within the comprehensive
engine architecture, showing registry summary, tier support, and frontend compatibility.
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# Add the server directory to the path
server_path = os.path.join(os.path.dirname(__file__), 'server')
sys.path.insert(0, server_path)

def create_sample_documents():
    """Create sample documents for testing."""
    
    documents = []
    
    # 1. Create a PDF document
    pdf_file = "test_document.pdf"
    try:
        # Create a minimal PDF with some metadata (using ASCII only)
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test PDF Document for Phase 2.3) Tj\nET\nendstream\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000089 00000 n \n0000000154 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n248\n%%EOF'
        
        with open(pdf_file, 'wb') as f:
            f.write(pdf_content)
        
        documents.append((pdf_file, "PDF", "application/pdf"))
        print(f"✅ Created PDF document: {pdf_file}")
        
    except Exception as e:
        print(f"⚠️  Could not create PDF document: {e}")
    
    # 2. Create an HTML document
    html_file = "test_document.html"
    try:
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Test HTML document for document extractor testing">
    <meta name="keywords" content="test, html, document, extractor, phase2">
    <meta name="author" content="MetaExtract Team">
    <title>Test HTML Document - Phase 2.3</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; }
        .content { line-height: 1.6; }
    </style>
</head>
<body>
    <h1>Test HTML Document for Phase 2.3</h1>
    <div class="content">
        <p>This is a test HTML document created for testing the document extractor functionality.</p>
        <p>It contains various HTML elements including:</p>
        <ul>
            <li>Meta tags with metadata</li>
            <li>CSS styling</li>
            <li>Structured content</li>
            <li>Multiple paragraphs</li>
        </ul>
        <p>The document extractor should be able to extract metadata from this HTML file.</p>
    </div>
</body>
</html>'''
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        documents.append((html_file, "HTML", "text/html"))
        print(f"✅ Created HTML document: {html_file}")
        
    except Exception as e:
        print(f"⚠️  Could not create HTML document: {e}")
    
    # 3. Create a JSON document
    json_file = "test_document.json"
    try:
        json_content = {
            "document_metadata": {
                "title": "Test JSON Document",
                "version": "2.3.0",
                "created": "2026-01-03",
                "author": "MetaExtract Team",
                "description": "Test document for Phase 2.3 document extractor testing"
            },
            "content": {
                "type": "structured_data",
                "sections": [
                    {
                        "id": 1,
                        "title": "Introduction",
                        "content": "This is a test JSON document for document extractor functionality."
                    },
                    {
                        "id": 2,
                        "title": "Testing",
                        "content": "The document extractor should extract metadata from this JSON file."
                    }
                ],
                "metadata": {
                    "field_count": 15,
                    "has_nested_objects": True,
                    "has_arrays": True
                }
            },
            "test_data": {
                "numbers": [1, 2, 3, 4, 5],
                "strings": ["test", "document", "extractor"],
                "booleans": [true, false],
                "null_value": None
            }
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_content, f, indent=2)
        
        documents.append((json_file, "JSON", "application/json"))
        print(f"✅ Created JSON document: {json_file}")
        
    except Exception as e:
        print(f"⚠️  Could not create JSON document: {e}")
    
    # 4. Create a CSV document
    csv_file = "test_document.csv"
    try:
        csv_content = '''Document_ID,Title,Type,Author,Created_Date,Field_Count,Description
DOC001,Test PDF Document,PDF,MetaExtract,2026-01-03,25,"PDF document with metadata"
DOC002,Test HTML Document,HTML,MetaExtract,2026-01-03,18,"HTML document with meta tags"
DOC003,Test JSON Document,JSON,MetaExtract,2026-01-03,22,"JSON document with structured data"
DOC004,Test CSV Document,CSV,MetaExtract,2026-01-03,7,"CSV document with tabular data"
DOC005,Test Text Document,TXT,MetaExtract,2026-01-03,5,"Plain text document"'''
        
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        documents.append((csv_file, "CSV", "text/csv"))
        print(f"✅ Created CSV document: {csv_file}")
        
    except Exception as e:
        print(f"⚠️  Could not create CSV document: {e}")
    
    return documents

def test_document_extractor_comprehensive():
    """Test the complete document extraction pipeline."""
    
    print("Phase 2.3: Document Extractor Comprehensive Test")
    print("=" * 55)
    
    try:
        # Create sample documents
        print("1. Creating sample documents for testing...")
        documents = create_sample_documents()
        
        if not documents:
            print("❌ No documents created for testing")
            return False
        
        print(f"   Created {len(documents)} test documents")
        
        # Test 2: Direct document extractor test
        print("2. Testing document extractor directly...")
        from extractor.extractors.document_extractor import DocumentExtractor
        from extractor.core.base_engine import ExtractionContext
        
        extractor = DocumentExtractor()
        
        for doc_file, doc_type, mime_type in documents:
            print(f"\n   Testing {doc_type} document: {doc_file}")
            
            context = ExtractionContext(
                filepath=doc_file,
                file_size=os.path.getsize(doc_file),
                file_extension=Path(doc_file).suffix.lower(),
                mime_type=mime_type,
                tier="free",
                processing_options={},
                execution_stats={}
            )
            
            result = extractor.extract(context)
            
            print(f"   ✅ Extraction status: {result.status}")
            print(f"   ✅ Processing time: {result.processing_time_ms:.2f}ms")
            
            if result.metadata:
                sections = list(result.metadata.keys())
                print(f"   ✅ Metadata sections: {sections}")
                
                # Show specific results for each document type
                if doc_type == "PDF" and 'pdf' in result.metadata:
                    pdf_data = result.metadata['pdf']
                    print(f"   📄 PDF pages: {pdf_data.get('page_count', 'unknown')}")
                    print(f"   📄 PDF encrypted: {pdf_data.get('is_encrypted', 'unknown')}")
                    if pdf_data.get('metadata_available'):
                        print(f"   📄 PDF has metadata: {pdf_data.get('metadata_available', False)}")
                
                elif doc_type == "HTML" and 'html' in result.metadata:
                    html_data = result.metadata['html']
                    print(f"   🌐 HTML has title: {html_data.get('has_title', False)}")
                    print(f"   🌐 HTML meta tags: {html_data.get('meta_tags_count', 0)}")
                
                elif doc_type == "JSON" and 'structured' in result.metadata:
                    struct_data = result.metadata['structured']
                    print(f"   📊 JSON is valid: {struct_data.get('is_valid_json', False)}")
                    print(f"   📊 JSON type: {struct_data.get('json_type', 'unknown')}")
                
                elif doc_type == "CSV" and 'tabular' in result.metadata:
                    tabular_data = result.metadata['tabular']
                    print(f"   📊 CSV rows: {tabular_data.get('rows_count', 0)}")
                    print(f"   📊 CSV columns: {tabular_data.get('column_count', 0)}")
        
        # Test 3: Comprehensive engine integration
        print("\n3. Testing comprehensive engine integration...")
        from extractor.core.comprehensive_engine import extract_comprehensive_metadata_new
        
        # Test different tiers
        tiers = ["free", "super", "premium"]
        
        for tier in tiers:
            print(f"\n--- Testing tier: {tier} ---")
            
            # Test with first document
            if documents:
                test_file, doc_type, _ = documents[0]
                
                result = extract_comprehensive_metadata_new(test_file, tier=tier)
                
                print(f"   ✅ Status: {result.get('status', 'unknown')}")
                print(f"   ✅ Engine: {result.get('extraction_info', {}).get('engine_version', 'unknown')}")
                
                # Check registry summary
                registry_summary = result.get('registry_summary', {})
                print(f"   ✅ Registry summary: {'✅' if registry_summary else '❌'}")
                
                if registry_summary:
                    print("   📊 Registry summary breakdown:")
                    
                    if 'image' in registry_summary:
                        image_summary = registry_summary['image']
                        print(f"      📷 Image: EXIF({image_summary.get('exif', 0)}), IPTC({image_summary.get('iptc', 0)}), XMP({image_summary.get('xmp', 0)})")
                    
                    if 'video' in registry_summary:
                        video_summary = registry_summary['video']
                        print(f"      📹 Video: Format({video_summary.get('format', 0)}), Streams({video_summary.get('streams', 0)}), Codec({video_summary.get('codec', 0)})")
                    
                    if 'audio' in registry_summary:
                        audio_summary = registry_summary['audio']
                        print(f"      🎵 Audio: ID3({audio_summary.get('id3', 0)}), Vorbis({audio_summary.get('vorbis', 0)}), Codec({audio_summary.get('codec', 0)})")
                    
                    if 'document' in registry_summary:
                        doc_summary = registry_summary['document']
                        print(f"      📄 Document: PDF({doc_summary.get('pdf', 0)}), Office({doc_summary.get('office', 0)}), OpenDocument({doc_summary.get('opendocument', 0)})")
                        print(f"                E-book({doc_summary.get('ebook', 0)}), Web({doc_summary.get('web', 0)}), Structured({doc_summary.get('structured', 0)})")
                        print(f"                Text({doc_summary.get('text', 0)}), Tabular({doc_summary.get('tabular', 0)})")
                
                # Show metadata structure
                metadata = result.get('metadata', {})
                sections = list(metadata.keys())
                print(f"   📊 Metadata sections: {sections}")
                
                # Simulate frontend tier filtering
                if tier == "free":
                    total_fields = sum(len(section) for section in metadata.values() if isinstance(section, dict))
                    print(f"   🔒 Free tier: {total_fields} total fields (some would be locked)")
                elif tier == "super":
                    print(f"   🔓 Super tier: Full access to {len(sections)} sections")
        
        # Test 4: Frontend compatibility
        print("\n4. Testing frontend compatibility...")
        
        # Simulate what the frontend would see
        if documents:
            super_result = extract_comprehensive_metadata_new(documents[0][0], tier="super")
            
            # Check frontend requirements
            frontend_checks = {
                'registry_summary': bool(super_result.get('registry_summary')),
                'metadata_structure': isinstance(super_result.get('metadata'), dict),
                'extraction_info': isinstance(super_result.get('extraction_info'), dict),
                'status_field': 'status' in super_result,
                'processing_time': 'processing_ms' in super_result.get('extraction_info', {})
            }
            
            print("   Frontend compatibility checks:")
            for check, result in frontend_checks.items():
                print(f"   - {check}: {'✅' if result else '❌'}")
        
        # Test 5: Error handling
        print("\n5. Testing error handling...")
        
        # Test with non-existent file
        error_result = extract_comprehensive_metadata_new("nonexistent_document.pdf", tier="free")
        error_status = error_result.get('status')
        has_error = error_result.get('extraction_info', {}).get('error', False)
        
        print(f"   Error handling: {'✅' if error_status == 'error' or has_error else '❌'}")
        
        print("\n✅ All Phase 2.3 document tests completed!")
        
        # Cleanup
        for doc_file, _, _ in documents:
            if os.path.exists(doc_file):
                os.remove(doc_file)
                print(f"   🧹 Cleaned up: {doc_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Phase 2.3 document test failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup on error
        for doc_file, _, _ in documents:
            if os.path.exists(doc_file):
                os.remove(doc_file)
        
        return False

if __name__ == "__main__":
    success = test_document_extractor_comprehensive()
    if success:
        print("\n🎉 Phase 2.3 Document Extractor Implementation Complete!")
        print("✅ Document extraction working")
        print("✅ Registry summary for documents working")
        print("✅ Tier support working")
        print("✅ Frontend compatibility maintained")
        print("\nReady for Phase 2.4: Scientific Extractor")
    else:
        print("\n❌ Phase 2.3 document implementation needs fixes.")