# server/extractor/modules/office_documents.py

"""
Office document metadata extraction for Phase 3.

Supports:
- OOXML (Word/Excel/PowerPoint): .docx, .xlsx, .pptx
- ODF (OpenDocument): .odt, .ods, .odp
- Apple iWork: .pages, .numbers, .keynote (basic support)
"""

import logging
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# OOXML namespaces
OOXML_NAMESPACES = {
    'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dcterms': 'http://purl.org/dc/terms/',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'dcmitype': 'http://purl.org/dc/dcmitype/',
}

# ODF namespaces
ODF_NAMESPACES = {
    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
    'meta': 'urn:oasis:names:tc:opendocument:xmlns:meta:1.0',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
}


def extract_office_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from Office documents.

    Supports OOXML (.docx, .xlsx, .pptx) and ODF (.odt, .ods, .odp) formats.
    """
    result = {}
    ext = Path(filepath).suffix.lower()

    try:
        if ext in ['.docx', '.xlsx', '.pptx']:
            result.update(_extract_ooxml_metadata(filepath))
        elif ext in ['.odt', '.ods', '.odp']:
            result.update(_extract_odf_metadata(filepath))
        elif ext in ['.pages', '.numbers', '.keynote']:
            result.update(_extract_iwork_metadata(filepath))
        else:
            result['office_format_error'] = f'Unsupported Office format: {ext}'

    except Exception as e:
        logger.warning(f"Error extracting Office metadata from {filepath}: {e}")
        result['office_extraction_error'] = str(e)

    return result


def _extract_ooxml_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from OOXML documents (Word/Excel/PowerPoint)."""
    result = {'office_format': 'ooxml'}

    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            # Core properties
            core_props = _extract_ooxml_core_properties(zf)
            result.update(core_props)

            # Extended properties
            ext_props = _extract_ooxml_extended_properties(zf)
            result.update(ext_props)

            # Document statistics
            doc_stats = _extract_ooxml_document_stats(zf, filepath)
            result.update(doc_stats)

            # Custom properties
            custom_props = _extract_ooxml_custom_properties(zf)
            result.update(custom_props)

    except Exception as e:
        result['ooxml_error'] = str(e)

    return result


def _extract_ooxml_core_properties(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract core properties from OOXML documents."""
    props = {}

    try:
        # Read core.xml
        core_xml = zf.read('docProps/core.xml').decode('utf-8')
        root = ET.fromstring(core_xml)

        # Dublin Core elements
        dc_title = root.find('.//dc:title', OOXML_NAMESPACES)
        if dc_title is not None and dc_title.text:
            props['ooxml_title'] = dc_title.text

        dc_creator = root.find('.//dc:creator', OOXML_NAMESPACES)
        if dc_creator is not None and dc_creator.text:
            props['ooxml_author'] = dc_creator.text

        dc_subject = root.find('.//dc:subject', OOXML_NAMESPACES)
        if dc_subject is not None and dc_subject.text:
            props['ooxml_subject'] = dc_subject.text

        dc_description = root.find('.//dc:description', OOXML_NAMESPACES)
        if dc_description is not None and dc_description.text:
            props['ooxml_description'] = dc_description.text

        # Core properties
        cp_created = root.find('.//dcterms:created', OOXML_NAMESPACES)
        if cp_created is not None and cp_created.text:
            props['ooxml_created_date'] = cp_created.text

        cp_modified = root.find('.//dcterms:modified', OOXML_NAMESPACES)
        if cp_modified is not None and cp_modified.text:
            props['ooxml_modified_date'] = cp_modified.text

        cp_keywords = root.find('.//cp:keywords', OOXML_NAMESPACES)
        if cp_keywords is not None and cp_keywords.text:
            props['ooxml_keywords'] = cp_keywords.text.split(',') if ',' in cp_keywords.text else [cp_keywords.text]

        cp_category = root.find('.//cp:category', OOXML_NAMESPACES)
        if cp_category is not None and cp_category.text:
            props['ooxml_category'] = cp_category.text

        cp_version = root.find('.//cp:version', OOXML_NAMESPACES)
        if cp_version is not None and cp_version.text:
            props['ooxml_version'] = cp_version.text

    except KeyError:
        pass  # core.xml not found
    except Exception as e:
        logger.debug(f"Error parsing OOXML core properties: {e}")

    return props


def _extract_ooxml_extended_properties(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract extended properties from OOXML documents."""
    props = {}

    try:
        # Read app.xml
        app_xml = zf.read('docProps/app.xml').decode('utf-8')
        root = ET.fromstring(app_xml)

        # Application-specific properties
        app_name = root.find('.//Application')
        if app_name is not None and app_name.text:
            props['ooxml_application'] = app_name.text

        app_version = root.find('.//AppVersion')
        if app_version is not None and app_version.text:
            props['ooxml_app_version'] = app_version.text

        # Document statistics
        pages = root.find('.//Pages')
        if pages is not None and pages.text:
            props['ooxml_page_count'] = int(pages.text)

        words = root.find('.//Words')
        if words is not None and words.text:
            props['ooxml_word_count'] = int(words.text)

        characters = root.find('.//Characters')
        if characters is not None and characters.text:
            props['ooxml_character_count'] = int(characters.text)

        paragraphs = root.find('.//Paragraphs')
        if paragraphs is not None and paragraphs.text:
            props['ooxml_paragraph_count'] = int(paragraphs.text)

        lines = root.find('.//Lines')
        if lines is not None and lines.text:
            props['ooxml_line_count'] = int(lines.text)

        # Spreadsheet-specific
        sheets = root.find('.//Sheets')
        if sheets is not None and sheets.text:
            props['ooxml_sheet_count'] = int(sheets.text)

        # Presentation-specific
        slides = root.find('.//Slides')
        if slides is not None and slides.text:
            props['ooxml_slide_count'] = int(slides.text)

        notes = root.find('.//Notes')
        if notes is not None and notes.text:
            props['ooxml_notes_count'] = int(notes.text)

        hidden_slides = root.find('.//HiddenSlides')
        if hidden_slides is not None and hidden_slides.text:
            props['ooxml_hidden_slides'] = int(hidden_slides.text)

    except KeyError:
        pass  # app.xml not found
    except Exception as e:
        logger.debug(f"Error parsing OOXML extended properties: {e}")

    return props


def _extract_ooxml_document_stats(zf: zipfile.ZipFile, filepath: str) -> Dict[str, Any]:
    """Extract document statistics and structure info."""
    stats = {}
    ext = Path(filepath).suffix.lower()

    try:
        if ext == '.docx':
            # Word document - count relationships and parts
            rels_count = len([f for f in zf.namelist() if 'relationships' in f])
            stats['ooxml_relationships_count'] = rels_count

            # Check for comments, revisions, etc.
            has_comments = 'word/comments.xml' in zf.namelist()
            stats['ooxml_has_comments'] = has_comments

            has_revisions = any('revision' in name.lower() for name in zf.namelist())
            stats['ooxml_has_revisions'] = has_revisions

        elif ext == '.xlsx':
            # Excel - count worksheets
            worksheets = [f for f in zf.namelist() if f.startswith('xl/worksheets/')]
            stats['ooxml_worksheet_count'] = len(worksheets)

            # Check for macros
            has_vba = any('xl/vbaProject.bin' in name for name in zf.namelist())
            stats['ooxml_has_vba'] = has_vba

        elif ext == '.pptx':
            # PowerPoint - count slides
            slides = [f for f in zf.namelist() if f.startswith('ppt/slides/')]
            stats['ooxml_slide_count_actual'] = len(slides)

            # Check for notes and handouts
            has_notes = any('ppt/notesSlides/' in name for name in zf.namelist())
            stats['ooxml_has_notes'] = has_notes

    except Exception as e:
        logger.debug(f"Error extracting OOXML document stats: {e}")

    return stats


def _extract_ooxml_custom_properties(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """Extract custom properties from OOXML documents."""
    props = {}

    try:
        # Read custom.xml
        custom_xml = zf.read('docProps/custom.xml').decode('utf-8')
        root = ET.fromstring(custom_xml)

        custom_props = {}
        for prop in root.findall('.//property'):
            name = prop.get('name')
            if name:
                # Get the value (could be various types)
                value_elem = prop.find('.//vt:lpstr', {'vt': 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'})
                if value_elem is not None and value_elem.text:
                    custom_props[name] = value_elem.text
                else:
                    # Try other value types
                    for child in prop:
                        if child.text:
                            custom_props[name] = child.text
                            break

        if custom_props:
            props['ooxml_custom_properties'] = custom_props
            props['ooxml_custom_property_count'] = len(custom_props)

    except KeyError:
        pass  # custom.xml not found
    except Exception as e:
        logger.debug(f"Error parsing OOXML custom properties: {e}")

    return props


def _extract_odf_metadata(filepath: str) -> Dict[str, Any]:
    """Extract metadata from ODF documents (OpenDocument)."""
    result: Dict[str, Any] = {'office_format': 'odf'}

    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            # Read meta.xml
            meta_xml = zf.read('meta.xml').decode('utf-8')
            root = ET.fromstring(meta_xml)

            # Dublin Core metadata
            dc_title = root.find('.//dc:title', ODF_NAMESPACES)
            if dc_title is not None and dc_title.text:
                result['odf_title'] = dc_title.text

            dc_creator = root.find('.//dc:creator', ODF_NAMESPACES)
            if dc_creator is not None and dc_creator.text:
                result['odf_author'] = dc_creator.text

            dc_subject = root.find('.//dc:subject', ODF_NAMESPACES)
            if dc_subject is not None and dc_subject.text:
                result['odf_subject'] = dc_subject.text

            dc_description = root.find('.//dc:description', ODF_NAMESPACES)
            if dc_description is not None and dc_description.text:
                result['odf_description'] = dc_description.text

            # ODF specific metadata
            meta_generator = root.find('.//meta:generator', ODF_NAMESPACES)
            if meta_generator is not None and meta_generator.text:
                result['odf_generator'] = meta_generator.text

            meta_creation_date = root.find('.//meta:creation-date', ODF_NAMESPACES)
            if meta_creation_date is not None and meta_creation_date.text:
                result['odf_creation_date'] = meta_creation_date.text

            meta_editing_duration = root.find('.//meta:editing-duration', ODF_NAMESPACES)
            if meta_editing_duration is not None and meta_editing_duration.text:
                result['odf_editing_duration'] = meta_editing_duration.text

            # Document statistics
            meta_word_count = root.find('.//meta:document-statistic[@meta:name="word-count"]', ODF_NAMESPACES)
            if meta_word_count is not None:
                result['odf_word_count'] = int(meta_word_count.get('meta:value', 0))

            meta_page_count = root.find('.//meta:document-statistic[@meta:name="page-count"]', ODF_NAMESPACES)
            if meta_page_count is not None:
                result['odf_page_count'] = int(meta_page_count.get('meta:value', 0))

            meta_paragraph_count = root.find('.//meta:document-statistic[@meta:name="paragraph-count"]', ODF_NAMESPACES)
            if meta_paragraph_count is not None:
                result['odf_paragraph_count'] = int(meta_paragraph_count.get('meta:value', 0))

    except Exception as e:
        result['odf_error'] = str(e)

    return result


def _extract_iwork_metadata(filepath: str) -> Dict[str, Any]:
    """Extract basic metadata from Apple iWork documents."""
    result: Dict[str, Any] = {'office_format': 'iwork'}

    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            # iWork documents have metadata in various places
            # This is a basic implementation - iWork format is complex

            # Look for Index.zip or similar
            metadata_files = [f for f in zf.namelist() if 'Metadata' in f or 'index' in f.lower()]

            if metadata_files:
                # Try to extract basic info from file listing
                result['iwork_has_metadata'] = True
                result['iwork_metadata_files'] = metadata_files

                # Basic file count
                result['iwork_total_files'] = len(zf.namelist())

            # Check for QuickLook preview
            has_preview = any('QuickLook' in f for f in zf.namelist())
            result['iwork_has_preview'] = has_preview

    except Exception as e:
        result['iwork_error'] = str(e)

    return result


def get_office_field_count() -> int:
    """Return the number of fields extracted by Office document metadata."""
    # OOXML fields
    ooxml_core = 8  # title, author, subject, description, dates, keywords, category, version
    ooxml_extended = 12  # app info, document stats (pages, words, chars, etc.)
    ooxml_stats = 8  # relationships, comments, revisions, worksheets, etc.
    ooxml_custom = 2  # custom properties count and data

    # ODF fields
    odf_fields = 10  # Dublin Core + generator + dates + statistics

    # iWork fields
    iwork_fields = 4  # format info, file counts, preview info

    return ooxml_core + ooxml_extended + ooxml_stats + ooxml_custom + odf_fields + iwork_fields


# Integration point for metadata_engine.py
def extract_office_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for Office document metadata extraction."""
    return extract_office_metadata(filepath)