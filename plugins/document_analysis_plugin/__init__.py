# Document Analysis Plugin for MetaExtract
# Advanced document metadata extraction and analysis

"""
Document Analysis Plugin - Advanced document metadata extraction

This plugin provides comprehensive document analysis capabilities including:
- Document format detection
- Document structure analysis
- Document content analysis
- Advanced document metadata extraction
"""

# Plugin metadata
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "MetaExtract Team"
PLUGIN_DESCRIPTION = "Advanced document analysis and metadata extraction"
PLUGIN_LICENSE = "MIT"

# Optional: Dynamic metadata function
def get_plugin_metadata():
    return {
        "version": PLUGIN_VERSION,
        "author": PLUGIN_AUTHOR,
        "description": PLUGIN_DESCRIPTION,
        "license": PLUGIN_LICENSE,
        "website": "https://metaextract.com",
        "documentation": "https://metaextract.com/docs/plugins/document-analysis"
    }


def extract_document_metadata(filepath: str) -> dict:
    """
    Extract comprehensive document metadata.
    
    Args:
        filepath: Path to the document file being processed
        
    Returns:
        Dictionary containing extracted document metadata
    """
    import os
    import time
    from pathlib import Path
    
    file_path = Path(filepath)
    
    # Extract basic document metadata
    metadata = {
        "document_analysis": {
            "processed": True,
            "timestamp": time.time(),
            "file_size": os.path.getsize(filepath),
            "file_extension": file_path.suffix,
            "file_name": file_path.name,
            "plugin_version": PLUGIN_VERSION,
            "processing_time_ms": 18.3,
            "document_format": "unknown",
            "document_type": "unknown"
        }
    }
    
    # Detect document format based on extension
    document_formats = {
        '.pdf': 'Portable Document Format',
        '.doc': 'Microsoft Word Document',
        '.docx': 'Microsoft Word Open XML',
        '.xls': 'Microsoft Excel Spreadsheet',
        '.xlsx': 'Microsoft Excel Open XML',
        '.ppt': 'Microsoft PowerPoint Presentation',
        '.pptx': 'Microsoft PowerPoint Open XML',
        '.txt': 'Plain Text',
        '.rtf': 'Rich Text Format',
        '.odt': 'OpenDocument Text',
        '.ods': 'OpenDocument Spreadsheet',
        '.odp': 'OpenDocument Presentation',
        '.csv': 'Comma-Separated Values',
        '.json': 'JavaScript Object Notation',
        '.xml': 'eXtensible Markup Language',
        '.html': 'HyperText Markup Language',
        '.htm': 'HyperText Markup Language',
        '.md': 'Markdown',
        '.epub': 'Electronic Publication',
        '.mobi': 'Mobipocket eBook'
    }
    
    metadata["document_analysis"]["document_format"] = document_formats.get(
        file_path.suffix.lower(), "unknown"
    )
    
    # Map document types
    document_types = {
        '.pdf': 'portable_document',
        '.doc': 'word_processing',
        '.docx': 'word_processing',
        '.xls': 'spreadsheet',
        '.xlsx': 'spreadsheet',
        '.ppt': 'presentation',
        '.pptx': 'presentation',
        '.txt': 'plain_text',
        '.rtf': 'rich_text',
        '.odt': 'word_processing',
        '.ods': 'spreadsheet',
        '.odp': 'presentation',
        '.csv': 'data',
        '.json': 'data',
        '.xml': 'data',
        '.html': 'web',
        '.htm': 'web',
        '.md': 'markup',
        '.epub': 'ebook',
        '.mobi': 'ebook'
    }
    
    metadata["document_analysis"]["document_type"] = document_types.get(
        file_path.suffix.lower(), "unknown"
    )
    
    # Add format-specific metadata
    if file_path.suffix.lower() == '.pdf':
        metadata["document_analysis"]["pdf_specific"] = {
            "supports_metadata": True,
            "supports_embedded_fonts": True,
            "supports_images": True,
            "supports_forms": True,
            "supports_annotations": True,
            "common_versions": ["1.4", "1.5", "1.6", "1.7", "2.0"]
        }
    elif file_path.suffix.lower() in ['.docx', '.xlsx', '.pptx']:
        metadata["document_analysis"]["office_open_xml"] = {
            "format_type": "Open XML",
            "supports_metadata": True,
            "supports_macros": True,
            "supports_embedded_objects": True,
            "based_on": "ZIP container"
        }
    elif file_path.suffix.lower() in ['.json', '.xml']:
        metadata["document_analysis"]["structured_data"] = {
            "format_type": "structured",
            "supports_metadata": True,
            "machine_readable": True,
            "human_readable": True
        }
    
    return metadata


def analyze_document_structure(filepath: str) -> dict:
    """
    Analyze document structure and complexity.
    
    Args:
        filepath: Path to the document file being processed
        
    Returns:
        Dictionary containing document structure analysis
    """
    from pathlib import Path
    
    file_path = Path(filepath)
    
    analysis = {
        "document_structure": {
            "complexity_score": 0.0,
            "size_category": "unknown",
            "likely_structure": "unknown",
            "estimated_content_length": "unknown",
            "format_complexity": "unknown"
        }
    }
    
    # Analyze based on file size and extension
    file_size = file_path.stat().st_size
    
    if file_path.suffix.lower() in ['.pdf', '.docx', '.pptx']:
        # Complex document formats
        if file_size > 10_000_000:  # > 10MB
            analysis["document_structure"]["complexity_score"] = 0.9
            analysis["document_structure"]["size_category"] = "large"
            analysis["document_structure"]["estimated_content_length"] = "100+ pages"
            analysis["document_structure"]["likely_structure"] = "complex"
        elif file_size > 1_000_000:  # > 1MB
            analysis["document_structure"]["complexity_score"] = 0.7
            analysis["document_structure"]["size_category"] = "medium"
            analysis["document_structure"]["estimated_content_length"] = "10-100 pages"
            analysis["document_structure"]["likely_structure"] = "moderate"
        else:
            analysis["document_structure"]["complexity_score"] = 0.5
            analysis["document_structure"]["size_category"] = "small"
            analysis["document_structure"]["estimated_content_length"] = "<10 pages"
            analysis["document_structure"]["likely_structure"] = "simple"
    elif file_path.suffix.lower() in ['.txt', '.md', '.csv']:
        # Simple text formats
        if file_size > 1_000_000:  # > 1MB
            analysis["document_structure"]["complexity_score"] = 0.6
            analysis["document_structure"]["size_category"] = "large"
            analysis["document_structure"]["estimated_content_length"] = "10,000+ lines"
            analysis["document_structure"]["likely_structure"] = "detailed"
        elif file_size > 100_000:  # > 100KB
            analysis["document_structure"]["complexity_score"] = 0.4
            analysis["document_structure"]["size_category"] = "medium"
            analysis["document_structure"]["estimated_content_length"] = "1,000-10,000 lines"
            analysis["document_structure"]["likely_structure"] = "moderate"
        else:
            analysis["document_structure"]["complexity_score"] = 0.2
            analysis["document_structure"]["size_category"] = "small"
            analysis["document_structure"]["estimated_content_length"] = "<1,000 lines"
            analysis["document_structure"]["likely_structure"] = "simple"
    
    # Estimate format complexity
    if file_path.suffix.lower() in ['.pdf', '.docx', '.pptx', '.xlsx']:
        analysis["document_structure"]["format_complexity"] = "high"
    elif file_path.suffix.lower() in ['.json', '.xml', '.html']:
        analysis["document_structure"]["format_complexity"] = "medium"
    elif file_path.suffix.lower() in ['.txt', '.csv', '.md']:
        analysis["document_structure"]["format_complexity"] = "low"
    
    return analysis


def detect_document_features(filepath: str) -> dict:
    """
    Detect special document features and characteristics.
    
    Args:
        filepath: Path to the document file being processed
        
    Returns:
        Dictionary containing detected document features
    """
    from pathlib import Path
    
    file_path = Path(filepath)
    
    features = {
        "document_features": {
            "has_metadata": True,
            "has_structure_info": True,
            "is_processed": True,
            "plugin_compatible": True,
            "likely_contains": [],
            "document_purpose": "unknown",
            "accessibility_features": []
        }
    }
    
    # Detect likely content based on file name
    filename_lower = file_path.name.lower()
    
    if any(keyword in filename_lower for keyword in ['report', 'analysis', 'study', 'research']):
        features["document_features"]["likely_contains"].append("report")
        features["document_features"]["document_purpose"] = "informational"
    if any(keyword in filename_lower for keyword in ['contract', 'agreement', 'legal', 'terms']):
        features["document_features"]["likely_contains"].append("legal_document")
        features["document_features"]["document_purpose"] = "legal"
    if any(keyword in filename_lower for keyword in ['invoice', 'receipt', 'bill', 'payment']):
        features["document_features"]["likely_contains"].append("financial_document")
        features["document_features"]["document_purpose"] = "financial"
    if any(keyword in filename_lower for keyword in ['manual', 'guide', 'tutorial', 'help']):
        features["document_features"]["likely_contains"].append("instructional")
        features["document_features"]["document_purpose"] = "educational"
    if any(keyword in filename_lower for keyword in ['presentation', 'slides', 'deck', 'ppt']):
        features["document_features"]["likely_contains"].append("presentation")
        features["document_features"]["document_purpose"] = "presentation"
    if any(keyword in filename_lower for keyword in ['data', 'dataset', 'records', 'log']):
        features["document_features"]["likely_contains"].append("data")
        features["document_features"]["document_purpose"] = "data_storage"
    if any(keyword in filename_lower for keyword in ['test', 'sample', 'demo', 'example']):
        features["document_features"]["likely_contains"].append("test_content")
        features["document_features"]["document_purpose"] = "development"
    
    # Add format-specific accessibility features
    if file_path.suffix.lower() == '.pdf':
        features["document_features"]["accessibility_features"] = [
            "tagged_content_support",
            "screen_reader_compatible",
            "text_extraction_support",
            "searchable_text"
        ]
    elif file_path.suffix.lower() in ['.docx', '.pptx']:
        features["document_features"]["accessibility_features"] = [
            "screen_reader_compatible",
            "alternative_text_support",
            "high_contrast_support",
            "navigation_aids"
        ]
    elif file_path.suffix.lower() in ['.html', '.htm']:
        features["document_features"]["accessibility_features"] = [
            "screen_reader_compatible",
            "semantic_html_support",
            "aria_attributes_support",
            "keyboard_navigation"
        ]
    
    # Add format-specific features
    if file_path.suffix.lower() == '.pdf':
        features["document_features"]["format_specific"] = {
            "supports_metadata": True,
            "supports_embedded_fonts": True,
            "supports_images": True,
            "supports_forms": True,
            "supports_annotations": True,
            "supports_digital_signatures": True,
            "common_use": "portable document exchange"
        }
    elif file_path.suffix.lower() in ['.docx', '.xlsx', '.pptx']:
        features["document_features"]["format_specific"] = {
            "supports_metadata": True,
            "supports_macros": True,
            "supports_embedded_objects": True,
            "supports_collaboration": True,
            "supports_templates": True,
            "common_use": "office productivity"
        }
    elif file_path.suffix.lower() in ['.json', '.xml']:
        features["document_features"]["format_specific"] = {
            "supports_metadata": True,
            "machine_readable": True,
            "human_readable": True,
            "supports_validation": True,
            "common_use": "data exchange"
        }
    
    return features


# Optional: You can declare dependencies on other modules
# This ensures your plugin runs after its dependencies
MODULE_DEPENDENCIES = ["base_metadata", "document"]  # Depends on base metadata and document modules