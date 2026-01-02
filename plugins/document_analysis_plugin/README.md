# Document Analysis Plugin for MetaExtract

## 📄 Overview

The **Document Analysis Plugin** provides comprehensive document metadata extraction and analysis capabilities for MetaExtract. It extends the core system with advanced document-specific features including format detection, structure analysis, and content characterization.

## 📁 Plugin Structure

```
document_analysis_plugin/
├── __init__.py          # Main plugin file
└── README.md           # This documentation
```

## 🔧 Installation

1. **Place the plugin** in one of the plugin directories:
   - `plugins/` (default)
   - `external_plugins/` (alternative)
   - Or any custom path configured in your system

2. **Enable plugins** in your code:
   ```python
   from server.extractor.module_discovery import enable_plugins_global
   enable_plugins_global(True)
   ```

3. **Load plugins** automatically:
   ```python
   from server.extractor.module_discovery import discover_and_load_plugins_global
   discover_and_load_plugins_global()
   ```

## 📋 Plugin Metadata

```python
# Static metadata
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "MetaExtract Team"
PLUGIN_DESCRIPTION = "Advanced document analysis and metadata extraction"
PLUGIN_LICENSE = "MIT"

# Dynamic metadata function
def get_plugin_metadata():
    return {
        "version": PLUGIN_VERSION,
        "author": PLUGIN_AUTHOR,
        "description": PLUGIN_DESCRIPTION,
        "license": PLUGIN_LICENSE,
        "website": "https://metaextract.com",
        "documentation": "https://metaextract.com/docs/plugins/document-analysis"
    }
```

## 🔧 Extraction Functions

### 1. `extract_document_metadata()`

Extracts comprehensive document metadata:
- **File information**: Size, extension, name
- **Document format**: Detailed format identification
- **Document type**: Portable document, word processing, spreadsheet, etc.
- **Format-specific metadata**: Feature support, capabilities
- **Processing information**: Timestamp, plugin version

**Supported formats**: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, RTF, ODT, ODS, ODP, CSV, JSON, XML, HTML, MD, EPUB, MOBI

### 2. `analyze_document_structure()`

Performs document structure analysis:
- **Complexity score**: 0.0 to 1.0 rating
- **Size category**: Small, medium, large
- **Likely structure**: Simple, moderate, complex
- **Estimated content length**: Lines or pages estimation
- **Format complexity**: Low, medium, high

### 3. `detect_document_features()`

Detects document content and features:
- **Content detection**: Reports, legal documents, financial documents, presentations
- **Document purpose**: Informational, legal, financial, educational, etc.
- **Accessibility features**: Screen reader support, navigation aids, etc.
- **Format-specific features**: Metadata support, embedded objects, collaboration
- **Feature flags**: Metadata presence, structure info, processing status

## 🔗 Dependencies

```python
MODULE_DEPENDENCIES = ["base_metadata", "document"]
```

This plugin depends on:
- **base_metadata**: For core file metadata
- **document**: For basic document metadata extraction

## 📊 Integration

The plugin integrates seamlessly with MetaExtract:

- **Automatic discovery** during system initialization
- **Dependency-aware execution** respecting module dependencies
- **Parallel execution** support for performance
- **Hot reloading** for development
- **Statistics tracking** and monitoring

## 🚀 Usage Example

```python
from server.extractor.comprehensive_metadata_engine import ComprehensiveMetadataExtractor

# Create extractor (automatically loads plugins)
extractor = ComprehensiveMetadataExtractor()

# Extract metadata from a document file (includes plugin results)
result = extractor.extract_comprehensive_metadata("test.pdf", "super")

# Access plugin results
document_data = result.get("document_analysis", {})
document_structure = result.get("document_structure", {})
document_features = result.get("document_features", {})

print(f"Document format: {document_data.get('document_format')}")
print(f"Document type: {document_data.get('document_type')}")
print(f"Complexity score: {document_structure.get('complexity_score')}")
print(f"Estimated content length: {document_structure.get('estimated_content_length')}")
print(f"Document purpose: {document_features.get('document_purpose')}")
```

## 📈 Expected Output

When processing a document file, the plugin adds metadata like:

```json
{
  "document_analysis": {
    "processed": true,
    "timestamp": 1712345678.9,
    "file_size": 8584000,
    "file_extension": ".pdf",
    "file_name": "test.pdf",
    "plugin_version": "1.0.0",
    "processing_time_ms": 18.3,
    "document_format": "Portable Document Format",
    "document_type": "portable_document",
    "pdf_specific": {
      "supports_metadata": true,
      "supports_embedded_fonts": true,
      "supports_images": true,
      "supports_forms": true,
      "supports_annotations": true,
      "common_versions": ["1.4", "1.5", "1.6", "1.7", "2.0"]
    }
  },
  "document_structure": {
    "complexity_score": 0.7,
    "size_category": "medium",
    "likely_structure": "moderate",
    "estimated_content_length": "10-100 pages",
    "format_complexity": "high"
  },
  "document_features": {
    "has_metadata": true,
    "has_structure_info": true,
    "is_processed": true,
    "plugin_compatible": true,
    "likely_contains": ["report"],
    "document_purpose": "informational",
    "accessibility_features": [
      "tagged_content_support",
      "screen_reader_compatible",
      "text_extraction_support",
      "searchable_text"
    ],
    "format_specific": {
      "supports_metadata": true,
      "supports_embedded_fonts": true,
      "supports_images": true,
      "supports_forms": true,
      "supports_annotations": true,
      "supports_digital_signatures": true,
      "common_use": "portable document exchange"
    }
  }
}
```

## 📄 Supported Document Formats

| Extension | Format Name | Document Type |
|-----------|-------------|---------------|
| `.pdf` | Portable Document Format | portable_document |
| `.doc` | Microsoft Word Document | word_processing |
| `.docx` | Microsoft Word Open XML | word_processing |
| `.xls` | Microsoft Excel Spreadsheet | spreadsheet |
| `.xlsx` | Microsoft Excel Open XML | spreadsheet |
| `.ppt` | Microsoft PowerPoint Presentation | presentation |
| `.pptx` | Microsoft PowerPoint Open XML | presentation |
| `.txt` | Plain Text | plain_text |
| `.rtf` | Rich Text Format | rich_text |
| `.odt` | OpenDocument Text | word_processing |
| `.ods` | OpenDocument Spreadsheet | spreadsheet |
| `.odp` | OpenDocument Presentation | presentation |
| `.csv` | Comma-Separated Values | data |
| `.json` | JavaScript Object Notation | data |
| `.xml` | eXtensible Markup Language | data |
| `.html` | HyperText Markup Language | web |
| `.htm` | HyperText Markup Language | web |
| `.md` | Markdown | markup |
| `.epub` | Electronic Publication | ebook |
| `.mobi` | Mobipocket eBook | ebook |

## 🔧 Customization

To extend this plugin:

1. **Add more format detection** - Expand the document_formats dictionary
2. **Enhance structure analysis** - Add actual document parsing libraries
3. **Improve content detection** - Use machine learning for content classification
4. **Add document fingerprinting** - Implement document hashing algorithms
5. **Support more metadata standards** - Add support for additional document metadata formats
6. **Add actual document parsing** - Use libraries like PyPDF2, python-docx, or BeautifulSoup

## 📚 Best Practices

1. **Follow naming conventions** - Use `extract_*`, `analyze_*`, `detect_*` patterns
2. **Include comprehensive metadata** - Helps with plugin management
3. **Declare dependencies** - Ensures correct execution order
4. **Handle errors gracefully** - Prevents plugin failures from crashing the system
5. **Document your plugin** - Helps other developers understand its purpose

## 🎯 Benefits

- **Extensibility** - Add custom document functionality without modifying core
- **Isolation** - Plugins run in their own context
- **Maintainability** - Easy to update and replace
- **Performance** - Integrates with parallel execution
- **Compatibility** - Works with all MetaExtract features

## 🔮 Future Enhancements

This plugin can be extended with:
- **Actual document parsing** using libraries like PyPDF2, python-docx, or BeautifulSoup
- **Text extraction** and content analysis
- **Natural language processing** for content understanding
- **Document similarity** comparison
- **Machine learning** based content classification
- **Optical character recognition** (OCR) for scanned documents
- **Document fingerprinting** for content identification
- **Metadata validation** and quality checking
- **Accessibility analysis** and improvement suggestions
- **Document security** analysis (encryption, signatures)
- **Content summarization** and keyword extraction