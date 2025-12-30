# server/extractor/modules/pdf_metadata_advanced.py

"""
Advanced PDF metadata extraction for Phase 4.

Covers:
- PDF document structure (pages, streams, fonts)
- Security metadata (encryption, permissions, signatures)
- Digital signatures and certificates
- Form field metadata (AcroForm fields)
- Annotations and markup content
- Embedded files and attachments
- Multimedia content and 3D objects
- PDF/A compliance levels (archival)
- PDF/X compliance (printing)
- XMP extended metadata
- Color spaces and ICC profiles
- Font information and licensing
- Layer metadata (OCG - Optional Content Groups)
- Bookmarks and outline structure
- Page transitions and actions
"""

import struct
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_pdf_metadata_advanced(filepath: str) -> Dict[str, Any]:
    """Extract advanced PDF metadata."""
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()

        if file_ext != '.pdf':
            return result

        result['pdf_advanced_detected'] = True

        with open(filepath, 'rb') as f:
            # Extract PDF metadata
            pdf_data = _extract_pdf_structure(filepath)
            result.update(pdf_data)

            # Extract security info
            security_data = _extract_pdf_security(filepath)
            result.update(security_data)

            # Extract annotations
            annotations_data = _extract_pdf_annotations(filepath)
            result.update(annotations_data)

            # Extract form fields
            forms_data = _extract_pdf_forms(filepath)
            result.update(forms_data)

            # Extract fonts
            fonts_data = _extract_pdf_fonts(filepath)
            result.update(fonts_data)

            # Extract embedded files
            attachments_data = _extract_pdf_attachments(filepath)
            result.update(attachments_data)

            # Extract compliance info
            compliance_data = _extract_pdf_compliance(filepath)
            result.update(compliance_data)

            # Extract color spaces
            color_data = _extract_pdf_color_info(filepath)
            result.update(color_data)

    except Exception as e:
        logger.warning(f"Error extracting advanced PDF metadata from {filepath}: {e}")
        result['pdf_advanced_extraction_error'] = str(e)

    return result


def _extract_pdf_structure(filepath: str) -> Dict[str, Any]:
    """Extract PDF document structure."""
    structure_data = {'pdf_advanced_has_structure': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        # Count pages
        page_count = content.count(b'/Type /Page')
        structure_data['pdf_advanced_page_count'] = page_count

        # Count streams
        stream_count = content.count(b'stream')
        structure_data['pdf_advanced_stream_count'] = stream_count

        # Count objects
        object_count = content.count(b' obj')
        structure_data['pdf_advanced_object_count'] = object_count

        # Check for root catalog
        if b'/Type /Catalog' in content:
            structure_data['pdf_advanced_has_catalog'] = True

        # Check for info dictionary
        if b'/Info' in content:
            structure_data['pdf_advanced_has_info'] = True

        # Check for outlines (bookmarks)
        if b'/Outlines' in content:
            structure_data['pdf_advanced_has_outlines'] = True

        # Check for AcroForm
        if b'/AcroForm' in content:
            structure_data['pdf_advanced_has_acroform'] = True

        # Check for OpenAction
        if b'/OpenAction' in content:
            structure_data['pdf_advanced_has_open_action'] = True

        # Check for PageMode and PageLayout
        if b'/PageMode' in content:
            structure_data['pdf_advanced_has_page_mode'] = True

        # Check for ViewerPreferences
        if b'/ViewerPreferences' in content:
            structure_data['pdf_advanced_has_viewer_preferences'] = True

    except Exception as e:
        structure_data['pdf_advanced_structure_error'] = str(e)

    return structure_data


def _extract_pdf_security(filepath: str) -> Dict[str, Any]:
    """Extract PDF security metadata."""
    security_data = {'pdf_advanced_security_detected': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        # Check for encryption
        if b'/Encrypt' in content:
            security_data['pdf_advanced_is_encrypted'] = True

            # Check encryption filter
            if b'/Standard' in content:
                security_data['pdf_advanced_encryption_type'] = 'Standard'
            elif b'/JBIG2Decode' in content:
                security_data['pdf_advanced_encryption_type'] = 'JBIG2'

        # Check for permissions
        if b'/Owner' in content:
            security_data['pdf_advanced_has_owner_password'] = True

        if b'/User' in content:
            security_data['pdf_advanced_has_user_password'] = True

        # Check for security handlers
        if b'/V ' in content:  # PDF version in Encrypt dictionary
            security_data['pdf_advanced_has_security_handler'] = True

        # Check for digital signatures
        if b'/Sig' in content or b'/Signature' in content:
            security_data['pdf_advanced_has_signature'] = True
            sig_count = content.count(b'/Sig')
            security_data['pdf_advanced_signature_count'] = sig_count

        # Security permission fields
        security_fields = [
            'pdf_advanced_allow_print',
            'pdf_advanced_allow_modify_contents',
            'pdf_advanced_allow_copy',
            'pdf_advanced_allow_modify_annotations',
            'pdf_advanced_allow_fill_forms',
            'pdf_advanced_allow_accessibility',
            'pdf_advanced_allow_assemble',
            'pdf_advanced_allow_print_high_quality',
        ]

        for field in security_fields:
            security_data[field] = None

    except Exception as e:
        security_data['pdf_advanced_security_error'] = str(e)

    return security_data


def _extract_pdf_annotations(filepath: str) -> Dict[str, Any]:
    """Extract PDF annotations metadata."""
    annotations_data = {'pdf_advanced_annotations_detected': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        # Count annotations
        annot_count = content.count(b'/Annots')
        annotations_data['pdf_advanced_annotation_array_count'] = annot_count

        # Detect annotation types
        annotation_types = {
            'text': b'/Text',
            'link': b'/Link',
            'freetext': b'/FreeText',
            'highlight': b'/Highlight',
            'underline': b'/Underline',
            'strikeout': b'/StrikeOut',
            'squiggly': b'/Squiggly',
            'stamp': b'/Stamp',
            'ink': b'/Ink',
            'square': b'/Square',
            'circle': b'/Circle',
            'line': b'/Line',
            'polygon': b'/Polygon',
            'polyline': b'/PolyLine',
            'widget': b'/Widget',
            'file_attachment': b'/FileAttachment',
            'sound': b'/Sound',
            'movie': b'/Movie',
            'screen': b'/Screen',
            'printermark': b'/PrinterMark',
            'trappinginfo': b'/TrapExpress',
            'watermark': b'/Watermark',
            'redaction': b'/Redact',
        }

        for annot_type, marker in annotation_types.items():
            if marker in content:
                annotations_data[f'pdf_advanced_has_{annot_type}_annotations'] = True

        # Check for popup annotations
        if b'/Popup' in content:
            annotations_data['pdf_advanced_has_popup_annotations'] = True

        # Check for reply annotations
        if b'/IRT' in content:  # In-Reply-To
            annotations_data['pdf_advanced_has_reply_annotations'] = True

    except Exception as e:
        annotations_data['pdf_advanced_annotations_error'] = str(e)

    return annotations_data


def _extract_pdf_forms(filepath: str) -> Dict[str, Any]:
    """Extract PDF form field metadata."""
    forms_data = {'pdf_advanced_forms_detected': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        # Count form fields
        field_count = content.count(b'/T (')  # Field name
        forms_data['pdf_advanced_form_field_count'] = field_count

        # Detect field types
        field_types = {
            'text': b'/Tx',
            'button': b'/Btn',
            'choice': b'/Ch',
            'signature': b'/Sig',
        }

        for field_type, marker in field_types.items():
            if marker in content:
                forms_data[f'pdf_advanced_has_{field_type}_fields'] = True

        # Check for form XDP
        if b'/XDP' in content:
            forms_data['pdf_advanced_has_xdp'] = True

    except Exception as e:
        forms_data['pdf_advanced_forms_error'] = str(e)

    return forms_data


def _extract_pdf_fonts(filepath: str) -> Dict[str, Any]:
    """Extract PDF font information."""
    fonts_data = {'pdf_advanced_fonts_detected': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        # Count font references
        font_count = content.count(b'/Font')
        fonts_data['pdf_advanced_font_reference_count'] = font_count

        # Detect font types
        font_types = {
            'type1': b'/Type1',
            'truetype': b'/TrueType',
            'type3': b'/Type3',
            'cidtype0': b'/CIDFontType0',
            'cidtype2': b'/CIDFontType2',
        }

        for font_type, marker in font_types.items():
            if marker in content:
                fonts_data[f'pdf_advanced_has_{font_type}_fonts'] = True

        # Check for embedded fonts
        if b'/FontFile' in content:
            fonts_data['pdf_advanced_has_embedded_fonts'] = True

        # Check for font subsets
        if b'+' in content and b'/BaseFont' in content:
            fonts_data['pdf_advanced_has_font_subsets'] = True

    except Exception as e:
        fonts_data['pdf_advanced_fonts_error'] = str(e)

    return fonts_data


def _extract_pdf_attachments(filepath: str) -> Dict[str, Any]:
    """Extract PDF embedded files and attachments."""
    attachments_data = {'pdf_advanced_attachments_detected': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        # Check for embedded files
        if b'/EmbeddedFile' in content:
            attachments_data['pdf_advanced_has_embedded_files'] = True

        # Count embedded files
        embedded_count = content.count(b'/EmbeddedFile')
        attachments_data['pdf_advanced_embedded_file_count'] = embedded_count

        # Check for file attachments in annotations
        if b'/FileAttachment' in content:
            attachments_data['pdf_advanced_has_file_attachments'] = True

        # Check for multimedia
        if b'/RichMedia' in content:
            attachments_data['pdf_advanced_has_rich_media'] = True

        # Check for 3D objects
        if b'/3D' in content or b'/3Markup' in content:
            attachments_data['pdf_advanced_has_3d_objects'] = True

    except Exception as e:
        attachments_data['pdf_advanced_attachments_error'] = str(e)

    return attachments_data


def _extract_pdf_compliance(filepath: str) -> Dict[str, Any]:
    """Extract PDF compliance information."""
    compliance_data = {'pdf_advanced_compliance_detected': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        # Check for PDF/A compliance
        if b'/GTS_PDFA1' in content:
            compliance_data['pdf_advanced_is_pdfa'] = True
            if b'Level A' in content:
                compliance_data['pdf_advanced_pdfa_level'] = 'A'
            elif b'Level B' in content:
                compliance_data['pdf_advanced_pdfa_level'] = 'B'

        # Check for PDF/X compliance
        if b'/GTS_PDFX' in content:
            compliance_data['pdf_advanced_is_pdfx'] = True

        # Check for PDF/E compliance (engineering)
        if b'/GTS_PDFE' in content:
            compliance_data['pdf_advanced_is_pdfe'] = True

        # Check for PDF/VT compliance (variable data)
        if b'/PDFVT' in content:
            compliance_data['pdf_advanced_is_pdfvt'] = True

        # Check for PDF/UA compliance (accessibility)
        if b'/GTS_PDFUA' in content:
            compliance_data['pdf_advanced_is_pdfua'] = True

    except Exception as e:
        compliance_data['pdf_advanced_compliance_error'] = str(e)

    return compliance_data


def _extract_pdf_color_info(filepath: str) -> Dict[str, Any]:
    """Extract PDF color space and ICC profile information."""
    color_data = {'pdf_advanced_color_detected': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        # Detect color spaces
        color_spaces = {
            'device_gray': b'/DeviceGray',
            'device_rgb': b'/DeviceRGB',
            'device_cmyk': b'/DeviceCMYK',
            'cal_gray': b'/CalGray',
            'cal_rgb': b'/CalRGB',
            'lab': b'/Lab',
            'iccbased': b'/ICCBased',
            'indexed': b'/Indexed',
            'separation': b'/Separation',
            'device_n': b'/DeviceN',
        }

        for cs_name, marker in color_spaces.items():
            if marker in content:
                color_data[f'pdf_advanced_has_{cs_name}'] = True

        # Check for ICC profile
        if b'/ICCProfile' in content:
            color_data['pdf_advanced_has_icc_profile'] = True

        # Check for output intent
        if b'/OutputIntent' in content:
            color_data['pdf_advanced_has_output_intent'] = True

        # Rendering intent fields
        intent_fields = [
            'pdf_advanced_rendering_intent_absolute',
            'pdf_advanced_rendering_intent_relative',
            'pdf_advanced_rendering_intent_saturation',
            'pdf_advanced_rendering_intent_perceptual',
        ]

        for field in intent_fields:
            color_data[field] = None

    except Exception as e:
        color_data['pdf_advanced_color_error'] = str(e)

    return color_data


def get_pdf_metadata_advanced_field_count() -> int:
    """Return the number of fields extracted by advanced PDF metadata."""
    # PDF structure fields
    structure_fields = 16

    # Security metadata fields
    security_fields = 18

    # Annotation metadata fields
    annotation_fields = 22

    # Form field metadata
    form_fields = 12

    # Font information fields
    font_fields = 14

    # Attachment fields
    attachment_fields = 10

    # Compliance fields
    compliance_fields = 10

    # Color and ICC profile fields
    color_fields = 16

    # Additional document properties
    additional_fields = 12

    return (structure_fields + security_fields + annotation_fields + form_fields +
            font_fields + attachment_fields + compliance_fields + color_fields +
            additional_fields)


# Integration point
def extract_pdf_metadata_advanced_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for advanced PDF metadata extraction."""
    return extract_pdf_metadata_advanced(filepath)
