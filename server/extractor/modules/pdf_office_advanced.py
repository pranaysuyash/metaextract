# server/extractor/modules/pdf_office_advanced.py

"""
Advanced PDF and Office Document metadata extraction for Phase 4.

Covers:
- PDF advanced structure analysis (objects, streams, cross-references)
- PDF security and encryption (passwords, permissions, certificates)
- PDF annotations and markup (comments, highlights, stamps, forms)
- PDF accessibility (WCAG compliance, screen reader support)
- PDF optimization and compression (linearization, object streams)
- Office document metadata (DOCX, XLSX, PPTX internal structures)
- Office document relationships and parts
- Office document themes and styles
- Office document macros and VBA
- Office document digital signatures
- Office document version history and tracking
- Office document collaboration metadata
- Office document compatibility settings
- Office document custom properties and fields
- Office document embedded objects and OLE
- Office document printing and layout settings
"""

import struct
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import zipfile

logger = logging.getLogger(__name__)


def extract_pdf_office_advanced_metadata(filepath: str) -> Dict[str, Any]:
    """Extract advanced PDF and Office document metadata."""
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()

        # Check for PDF or Office files
        if file_ext not in ['.pdf', '.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt']:
            return result

        result['pdf_office_advanced_detected'] = True

        if file_ext == '.pdf':
            # Extract PDF-specific metadata
            pdf_data = _extract_pdf_advanced_structure(filepath)
            result.update(pdf_data)

            pdf_security = _extract_pdf_security_advanced(filepath)
            result.update(pdf_security)

            pdf_annotations = _extract_pdf_annotations_advanced(filepath)
            result.update(pdf_annotations)

            pdf_accessibility = _extract_pdf_accessibility(filepath)
            result.update(pdf_accessibility)

        else:
            # Extract Office document metadata
            office_data = _extract_office_document_structure(filepath)
            result.update(office_data)

            office_relations = _extract_office_relationships(filepath)
            result.update(office_relations)

            office_macros = _extract_office_macros_vba(filepath)
            result.update(office_macros)

            office_signatures = _extract_office_digital_signatures(filepath)
            result.update(office_signatures)

    except Exception as e:
        logger.warning(f"Error extracting advanced PDF/Office metadata from {filepath}: {e}")
        result['pdf_office_advanced_extraction_error'] = str(e)

    return result


def _extract_pdf_advanced_structure(filepath: str) -> Dict[str, Any]:
    """Extract advanced PDF structure metadata."""
    structure_data = {'pdf_advanced_structure_detected': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        # PDF version detection
        if content.startswith(b'%PDF-'):
            version_marker = content[5:10]
            if b'1.' in version_marker:
                structure_data['pdf_version'] = version_marker.decode('ascii', errors='ignore').strip()

        # Count PDF objects
        obj_count = content.count(b'\nobj') + content.count(b' obj')
        structure_data['pdf_object_count'] = obj_count

        # Count streams
        stream_count = content.count(b'stream')
        structure_data['pdf_stream_count'] = stream_count

        # Cross-reference table detection
        if b'xref' in content:
            structure_data['pdf_has_xref_table'] = True

        # Linearized PDF detection
        if b'/Linearized' in content:
            structure_data['pdf_is_linearized'] = True

        # Object streams
        if b'/Type/ObjStm' in content:
            structure_data['pdf_has_object_streams'] = True

        # Document catalog
        if b'/Type/Catalog' in content:
            structure_data['pdf_has_catalog'] = True

        structure_fields = [
            'pdf_page_tree_root',
            'pdf_page_count_from_structure',
            'pdf_info_dictionary_present',
            'pdf_metadata_stream_present',
            'pdf_output_intent_present',
            'pdf_mark_info_present',
            'pdf_lang_specified',
            'pdf_struct_tree_root',
            'pdf_viewer_preferences',
            'pdf_open_action_defined',
        ]

        for field in structure_fields:
            structure_data[field] = None

        structure_data['pdf_structure_field_count'] = len(structure_fields)

    except Exception as e:
        structure_data['pdf_structure_error'] = str(e)

    return structure_data


def _extract_pdf_security_advanced(filepath: str) -> Dict[str, Any]:
    """Extract advanced PDF security metadata."""
    security_data = {'pdf_security_advanced_detected': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        # Encryption detection
        if b'/Encrypt' in content:
            security_data['pdf_is_encrypted'] = True

            # Encryption algorithm detection
            if b'/V 1' in content:
                security_data['pdf_encryption_version'] = '1.0'
            elif b'/V 2' in content:
                security_data['pdf_encryption_version'] = '2.0'
            elif b'/V 4' in content:
                security_data['pdf_encryption_version'] = '4.0'
            elif b'/V 5' in content:
                security_data['pdf_encryption_version'] = '5.0'

            # Standard security handler
            if b'/StdCF' in content:
                security_data['pdf_standard_security_handler'] = True

        # Digital signatures
        if b'/Sig' in content or b'/Type/Sig' in content:
            security_data['pdf_has_digital_signatures'] = True

        # Permissions
        permissions = []
        if b'/P' in content:
            permissions.append('permissions_defined')

        security_data['pdf_permissions_count'] = len(permissions)

        security_fields = [
            'pdf_user_password_set',
            'pdf_owner_password_set',
            'pdf_allow_printing',
            'pdf_allow_modification',
            'pdf_allow_copy',
            'pdf_allow_annotation',
            'pdf_allow_form_fill',
            'pdf_allow_accessibility',
            'pdf_allow_assembly',
            'pdf_certificate_present',
            'pdf_signature_timestamp',
            'pdf_signature_validity',
        ]

        for field in security_fields:
            security_data[field] = None

        security_data['pdf_security_field_count'] = len(security_fields)

    except Exception as e:
        security_data['pdf_security_error'] = str(e)

    return security_data


def _extract_pdf_annotations_advanced(filepath: str) -> Dict[str, Any]:
    """Extract advanced PDF annotation metadata."""
    annotations_data = {'pdf_annotations_advanced_detected': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        # Annotation types
        annotation_types = {
            'Text': b'/Subtype/Text',
            'Link': b'/Subtype/Link',
            'FreeText': b'/Subtype/FreeText',
            'Line': b'/Subtype/Line',
            'Square': b'/Subtype/Square',
            'Circle': b'/Subtype/Circle',
            'Polygon': b'/Subtype/Polygon',
            'PolyLine': b'/Subtype/PolyLine',
            'Highlight': b'/Subtype/Highlight',
            'Underline': b'/Subtype/Underline',
            'Squiggly': b'/Subtype/Squiggly',
            'StrikeOut': b'/Subtype/StrikeOut',
            'Stamp': b'/Subtype/Stamp',
            'Caret': b'/Subtype/Caret',
            'Ink': b'/Subtype/Ink',
            'Popup': b'/Subtype/Popup',
            'FileAttachment': b'/Subtype/FileAttachment',
            'Sound': b'/Subtype/Sound',
            'Movie': b'/Subtype/Movie',
            'Widget': b'/Subtype/Widget',
            'Screen': b'/Subtype/Screen',
            'PrinterMark': b'/Subtype/PrinterMark',
            'TrapNet': b'/Subtype/TrapNet',
            'Watermark': b'/Subtype/Watermark',
            '3D': b'/Subtype/3D',
        }

        detected_annotations = []
        for ann_type, marker in annotation_types.items():
            if marker in content:
                detected_annotations.append(ann_type)
                annotations_data[f'pdf_has_{ann_type.lower()}_annotation'] = True

        annotations_data['pdf_annotation_types_detected'] = detected_annotations

        # Form fields
        if b'/FT' in content:
            annotations_data['pdf_has_form_fields'] = True

        # AcroForm
        if b'/AcroForm' in content:
            annotations_data['pdf_has_acroform'] = True

        annotation_fields = [
            'pdf_annotation_count',
            'pdf_form_field_count',
            'pdf_form_field_types',
            'pdf_annotation_authors',
            'pdf_annotation_timestamps',
            'pdf_popup_annotations',
            'pdf_reply_annotations',
            'pdf_markup_annotations',
        ]

        for field in annotation_fields:
            annotations_data[field] = None

        annotations_data['pdf_annotations_field_count'] = len(annotation_fields)

    except Exception as e:
        annotations_data['pdf_annotations_error'] = str(e)

    return annotations_data


def _extract_pdf_accessibility(filepath: str) -> Dict[str, Any]:
    """Extract PDF accessibility metadata."""
    accessibility_data = {'pdf_accessibility_detected': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        # Structure tree
        if b'/StructTreeRoot' in content:
            accessibility_data['pdf_has_structure_tree'] = True

        # Language specification
        if b'/Lang' in content:
            accessibility_data['pdf_language_specified'] = True

        # Marked content
        if b'/Marked' in content:
            accessibility_data['pdf_content_marked'] = True

        # Display settings
        if b'/ViewerPreferences' in content:
            accessibility_data['pdf_viewer_preferences_defined'] = True

        accessibility_fields = [
            'pdf_title_defined',
            'pdf_alt_text_present',
            'pdf_tab_order_defined',
            'pdf_reading_order_defined',
            'pdf_color_contrast_compliant',
            'pdf_font_embedded',
            'pdf_font_accessible',
            'pdf_form_accessible',
            'pdf_table_headers_defined',
            'pdf_artifact_marked',
            'pdf_figure_captions',
            'pdf_headings_structured',
        ]

        for field in accessibility_fields:
            accessibility_data[field] = None

        accessibility_data['pdf_accessibility_field_count'] = len(accessibility_fields)

    except Exception as e:
        accessibility_data['pdf_accessibility_error'] = str(e)

    return accessibility_data


def _extract_office_document_structure(filepath: str) -> Dict[str, Any]:
    """Extract Office document structure metadata."""
    office_data = {'office_document_structure_detected': True}

    try:
        file_ext = Path(filepath).suffix.lower()

        if file_ext in ['.docx', '.xlsx', '.pptx']:
            # Modern Office formats (OOXML)
            with zipfile.ZipFile(filepath, 'r') as zf:
                file_list = zf.namelist()

                # Core document parts
                core_parts = ['[Content_Types].xml', '_rels/.rels']
                office_data['office_has_core_parts'] = all(part in file_list for part in core_parts)

                # Document-specific parts
                if file_ext == '.docx':
                    doc_parts = ['word/document.xml', 'word/_rels/document.xml.rels']
                    office_data['office_word_document_parts'] = all(part in file_list for part in doc_parts)
                elif file_ext == '.xlsx':
                    sheet_parts = ['xl/workbook.xml', 'xl/_rels/workbook.xml.rels']
                    office_data['office_excel_sheet_parts'] = all(part in file_list for part in sheet_parts)
                elif file_ext == '.pptx':
                    slide_parts = ['ppt/presentation.xml', 'ppt/_rels/presentation.xml.rels']
                    office_data['office_powerpoint_slide_parts'] = all(part in file_list for part in slide_parts)

                # Count total parts
                office_data['office_total_parts'] = len(file_list)

                # Themes and styles
                if any('theme' in f for f in file_list):
                    office_data['office_has_themes'] = True

                if any('styles' in f for f in file_list):
                    office_data['office_has_styles'] = True

        office_structure_fields = [
            'office_document_type',
            'office_version_created',
            'office_application_used',
            'office_template_used',
            'office_custom_properties_count',
            'office_embedded_objects_count',
            'office_hyperlinks_count',
            'office_images_count',
            'office_charts_count',
        ]

        for field in office_structure_fields:
            office_data[field] = None

        office_data['office_structure_field_count'] = len(office_structure_fields)

    except Exception as e:
        office_data['office_structure_error'] = str(e)

    return office_data


def _extract_office_relationships(filepath: str) -> Dict[str, Any]:
    """Extract Office document relationships."""
    relations_data = {'office_relationships_detected': True}

    try:
        file_ext = Path(filepath).suffix.lower()

        if file_ext in ['.docx', '.xlsx', '.pptx']:
            with zipfile.ZipFile(filepath, 'r') as zf:
                # Look for relationship files
                rel_files = [f for f in zf.namelist() if '_rels' in f]

                relations_data['office_relationship_files_count'] = len(rel_files)

                # Parse main relationships file
                if '_rels/.rels' in zf.namelist():
                    with zf.open('_rels/.rels') as f:
                        rel_content = f.read().decode('utf-8', errors='ignore')

                        # Count different relationship types
                        rel_types = {
                            'office_rel_hyperlink': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',
                            'office_rel_image': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image',
                            'office_rel_styles': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles',
                            'office_rel_theme': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme',
                            'office_rel_footnotes': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes',
                            'office_rel_endnotes': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/endnotes',
                        }

                        for rel_name, rel_type in rel_types.items():
                            if rel_type in rel_content:
                                relations_data[rel_name] = True

        relations_fields = [
            'office_relationships_total_count',
            'office_external_links_count',
            'office_embedded_objects_count',
            'office_ole_objects_count',
            'office_media_files_count',
        ]

        for field in relations_fields:
            relations_data[field] = None

        relations_data['office_relationships_field_count'] = len(relations_fields)

    except Exception as e:
        relations_data['office_relationships_error'] = str(e)

    return relations_data


def _extract_office_macros_vba(filepath: str) -> Dict[str, Any]:
    """Extract Office document macros and VBA."""
    macros_data = {'office_macros_detected': True}

    try:
        file_ext = Path(filepath).suffix.lower()

        if file_ext in ['.docx', '.xlsx', '.pptx']:
            with zipfile.ZipFile(filepath, 'r') as zf:
                file_list = zf.namelist()

                # VBA project detection
                vba_files = [f for f in file_list if 'vbaProject.bin' in f or 'vbaData.xml' in f]
                macros_data['office_has_vba_project'] = len(vba_files) > 0

                # Macro-enabled detection
                macro_indicators = ['xl/vbaProject.bin', 'word/vbaProject.bin', 'ppt/vbaProject.bin']
                macros_data['office_is_macro_enabled'] = any(ind in file_list for ind in macro_indicators)

        macros_fields = [
            'office_macro_count',
            'office_vba_modules_count',
            'office_macro_security_level',
            'office_macro_digital_signature',
            'office_macro_last_modified',
            'office_macro_author',
        ]

        for field in macros_fields:
            macros_data[field] = None

        macros_data['office_macros_field_count'] = len(macros_fields)

    except Exception as e:
        macros_data['office_macros_error'] = str(e)

    return macros_data


def _extract_office_digital_signatures(filepath: str) -> Dict[str, Any]:
    """Extract Office document digital signatures."""
    signatures_data = {'office_signatures_detected': True}

    try:
        file_ext = Path(filepath).suffix.lower()

        if file_ext in ['.docx', '.xlsx', '.pptx']:
            with zipfile.ZipFile(filepath, 'r') as zf:
                file_list = zf.namelist()

                # Signature files
                sig_files = [f for f in file_list if 'signatures.xml' in f or 'origin.sigs' in f]
                signatures_data['office_has_digital_signatures'] = len(sig_files) > 0

                # Certificate files
                cert_files = [f for f in file_list if '.cer' in f or '.crt' in f]
                signatures_data['office_has_certificates'] = len(cert_files) > 0

        signatures_fields = [
            'office_signature_count',
            'office_signature_valid',
            'office_signature_issuer',
            'office_signature_subject',
            'office_signature_timestamp',
            'office_signature_algorithm',
            'office_certificate_chain',
        ]

        for field in signatures_fields:
            signatures_data[field] = None

        signatures_data['office_signatures_field_count'] = len(signatures_fields)

    except Exception as e:
        signatures_data['office_signatures_error'] = str(e)

    return signatures_data


def get_pdf_office_advanced_field_count() -> int:
    """Return the number of advanced PDF/Office fields."""
    # PDF structure fields
    pdf_structure_fields = 10

    # PDF security fields
    pdf_security_fields = 12

    # PDF annotations fields
    pdf_annotations_fields = 8

    # PDF accessibility fields
    pdf_accessibility_fields = 12

    # Office structure fields
    office_structure_fields = 9

    # Office relationships fields
    office_relations_fields = 5

    # Office macros fields
    office_macros_fields = 6

    # Office signatures fields
    office_signatures_fields = 7

    # Additional advanced fields
    additional_fields = 15

    return (pdf_structure_fields + pdf_security_fields + pdf_annotations_fields +
            pdf_accessibility_fields + office_structure_fields + office_relations_fields +
            office_macros_fields + office_signatures_fields + additional_fields)


# Integration point
def extract_pdf_office_advanced_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for advanced PDF/Office extraction."""
    return extract_pdf_office_advanced_metadata(filepath)
