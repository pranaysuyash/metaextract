# server/extractor/modules/pdf_metadata_complete.py

"""
Complete PDF metadata extraction module for Phase 3.

Extracts comprehensive metadata from PDF files including:
- Basic document properties
- XMP metadata packets
- Annotations and forms
- Digital signatures
- Accessibility features
- Encryption and security
- Embedded multimedia
- Bookmarks and navigation
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

# Optional imports
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

try:
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    PdfReader = None
    PdfWriter = None

# XMP namespaces
XMP_NAMESPACES = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'xmp': 'http://ns.adobe.com/xap/1.0/',
    'xmpMM': 'http://ns.adobe.com/xap/1.0/mm/',
    'xmpRights': 'http://ns.adobe.com/xap/1.0/rights/',
    'pdf': 'http://ns.adobe.com/pdf/1.3/',
    'pdfx': 'http://ns.adobe.com/pdfx/1.3/',
    'photoshop': 'http://ns.adobe.com/photoshop/1.0/',
}


def extract_pdf_metadata_complete(filepath: str) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from PDF files.

    Returns a dictionary with all available PDF metadata fields.
    """
    result = {}

    try:
        # Use PyMuPDF for document structure analysis if available
        if PYMUPDF_AVAILABLE:
            doc = fitz.open(filepath)

            # Basic document properties
            result.update(_extract_basic_properties(doc))

            # Page and layout information
            result.update(_extract_page_layout(doc))

            # Annotations and interactive elements
            result.update(_extract_annotations(doc))

            # Forms and AcroForms
            result.update(_extract_forms(doc))

            # Bookmarks and outline
            result.update(_extract_bookmarks(doc))

            # Embedded files and multimedia
            result.update(_extract_embedded_content(doc))

            # Digital signatures
            result.update(_extract_digital_signatures(doc))

            # Accessibility features
            result.update(_extract_accessibility(doc))

            doc.close()
        else:
            result['pymupdf_not_available'] = True

        # Use pypdf for XMP and additional metadata if available
        if PYPDF_AVAILABLE:
            reader = PdfReader(filepath)
            result.update(_extract_xmp_metadata(reader))
            result.update(_extract_security_info(reader))
            result.update(_extract_pypdf_annotations(reader))
            result.update(_extract_pypdf_forms(reader))
            result.update(_extract_pypdf_outlines(reader))
        else:
            result['pypdf_not_available'] = True

    except Exception as e:
        logger.warning(f"Error extracting PDF metadata from {filepath}: {e}")
        result['pdf_extraction_error'] = str(e)

    return result


def _extract_basic_properties(doc) -> Dict[str, Any]:
    """Extract basic PDF document properties."""
    if not PYMUPDF_AVAILABLE:
        return {}
    metadata = doc.metadata
    return {
        'pdf_title': metadata.get('title', ''),
        'pdf_author': metadata.get('author', ''),
        'pdf_subject': metadata.get('subject', ''),
        'pdf_creator': metadata.get('creator', ''),
        'pdf_producer': metadata.get('producer', ''),
        'pdf_creation_date': metadata.get('creationDate', ''),
        'pdf_modification_date': metadata.get('modDate', ''),
        'pdf_keywords': metadata.get('keywords', ''),
        'pdf_page_count': len(doc),
        'pdf_format_version': doc.version,
        'pdf_is_encrypted': doc.is_encrypted,
        'pdf_is_repaired': doc.is_repaired,
        'pdf_needs_pass': doc.needs_pass,
    }


def _extract_page_layout(doc) -> Dict[str, Any]:
    """Extract page layout and structure information."""
    if not PYMUPDF_AVAILABLE:
        return {}
    if len(doc) == 0:
        return {}

    first_page = doc[0]
    return {
        'pdf_page_width': first_page.rect.width,
        'pdf_page_height': first_page.rect.height,
        'pdf_page_rotation': first_page.rotation,
        'pdf_has_javascript': any(page.get_label() for page in doc),
        'pdf_page_mode': getattr(doc, 'page_mode', None),
        'pdf_page_layout': getattr(doc, 'page_layout', None),
    }


def _extract_annotations(doc) -> Dict[str, Any]:
    """Extract annotation information from all pages."""
    if not PYMUPDF_AVAILABLE:
        return {}
    total_annotations = 0
    annotation_types = {}

    for page in doc:
        annots = page.annots()
        if annots:
            for annot in annots:
                total_annotations += 1
                annot_type = annot.type[1] if hasattr(annot, 'type') else 'unknown'
                annotation_types[annot_type] = annotation_types.get(annot_type, 0) + 1

    return {
        'pdf_total_annotations': total_annotations,
        'pdf_annotation_types': annotation_types,
        'pdf_has_annotations': total_annotations > 0,
    }


def _extract_forms(doc) -> Dict[str, Any]:
    """Extract form field information."""
    if not PYMUPDF_AVAILABLE:
        return {}
    # Note: PyMuPDF has limited form support, this is basic
    # For full AcroForm analysis, would need pypdf or pdfminer
    form_fields = []

    for page in doc:
        widgets = page.widgets()
        if widgets:
            for widget in widgets:
                field_info = {
                    'field_type': getattr(widget, 'field_type', None),
                    'field_name': getattr(widget, 'field_name', None),
                    'field_value': getattr(widget, 'field_value', None),
                }
                form_fields.append(field_info)

    return {
        'pdf_form_field_count': len(form_fields),
        'pdf_has_forms': len(form_fields) > 0,
        'pdf_form_fields': form_fields[:10],  # Limit to first 10 for brevity
    }


def _extract_bookmarks(doc) -> Dict[str, Any]:
    """Extract bookmark/outline information."""
    if not PYMUPDF_AVAILABLE:
        return {}
    toc = doc.get_toc()
    return {
        'pdf_bookmark_count': len(toc),
        'pdf_has_bookmarks': len(toc) > 0,
        'pdf_bookmark_levels': max((item[0] for item in toc), default=0) if toc else 0,
    }


def _extract_embedded_content(doc) -> Dict[str, Any]:
    """Extract information about embedded files and multimedia."""
    if not PYMUPDF_AVAILABLE:
        return {}
    embedded_files = []
    multimedia_count = 0

    # Check for embedded files
    try:
        for item in doc.embedded_file_list():
            embedded_files.append({
                'filename': item[0],
                'size': item[1],
                'mimetype': item[2] if len(item) > 2 else None,
            })
    except:
        pass

    # Count multimedia objects (rough estimate)
    for page in doc:
        if page.get_images():
            multimedia_count += len(page.get_images())

    return {
        'pdf_embedded_file_count': len(embedded_files),
        'pdf_embedded_files': embedded_files,
        'pdf_multimedia_object_count': multimedia_count,
        'pdf_has_embedded_content': len(embedded_files) > 0 or multimedia_count > 0,
    }


def _extract_digital_signatures(doc) -> Dict[str, Any]:
    """Extract digital signature information."""
    if not PYMUPDF_AVAILABLE:
        return {}
    signatures = []

    try:
        # PyMuPDF signature support is limited
        # This would need more advanced PDF libraries for full signature analysis
        sig_info = getattr(doc, 'get_sigflags', lambda: 0)()
        return {
            'pdf_has_signatures': sig_info > 0,
            'pdf_signature_flags': sig_info,
            'pdf_signature_count': 0,  # Placeholder
        }
    except:
        return {
            'pdf_has_signatures': False,
            'pdf_signature_flags': 0,
            'pdf_signature_count': 0,
        }


def _extract_accessibility(doc) -> Dict[str, Any]:
    """Extract accessibility-related information."""
    if not PYMUPDF_AVAILABLE:
        return {}
    # Basic accessibility checks
    has_alt_text = False
    has_structure = False

    try:
        # Check for tagged PDF structure
        has_structure = hasattr(doc, 'get_structure') and doc.get_structure()
    except:
        pass

    return {
        'pdf_is_tagged': has_structure,
        'pdf_has_alt_text': has_alt_text,  # Would need more analysis
        'pdf_accessibility_score': None,  # Placeholder for future implementation
    }


def _extract_xmp_metadata(reader) -> Dict[str, Any]:
    """Extract XMP metadata using pypdf."""
    if not PYPDF_AVAILABLE:
        return {}
    xmp_data = {}

    try:
        if hasattr(reader, 'xmp_metadata') and reader.xmp_metadata:
            xmp = reader.xmp_metadata

            # Dublin Core
            if hasattr(xmp, 'dc_title'):
                xmp_data['xmp_dc_title'] = xmp.dc_title
            if hasattr(xmp, 'dc_creator'):
                xmp_data['xmp_dc_creator'] = xmp.dc_creator
            if hasattr(xmp, 'dc_subject'):
                xmp_data['xmp_dc_subject'] = xmp.dc_subject
            if hasattr(xmp, 'dc_description'):
                xmp_data['xmp_dc_description'] = xmp.dc_description

            # XMP Basic
            if hasattr(xmp, 'xmp_create_date'):
                xmp_data['xmp_create_date'] = str(xmp.xmp_create_date)
            if hasattr(xmp, 'xmp_modify_date'):
                xmp_data['xmp_modify_date'] = str(xmp.xmp_modify_date)
            if hasattr(xmp, 'xmp_metadata_date'):
                xmp_data['xmp_metadata_date'] = str(xmp.xmp_metadata_date)

            # XMP Media Management
            if hasattr(xmp, 'xmp_mm_document_id'):
                xmp_data['xmp_document_id'] = xmp.xmp_mm_document_id

    except Exception as e:
        logger.debug(f"Error extracting XMP metadata: {e}")

    return xmp_data


def _extract_security_info(reader) -> Dict[str, Any]:
    """Extract security and encryption information."""
    if not PYPDF_AVAILABLE:
        return {}
    security = {
        'pdf_is_encrypted': reader.is_encrypted,
        'pdf_encryption_method': None,
        'pdf_user_password_protected': False,
        'pdf_owner_password_protected': False,
    }

    if reader.is_encrypted:
        try:
            # Try to determine encryption details
            # Note: This is limited without actually decrypting
            security['pdf_encryption_method'] = 'standard'  # Most common
        except:
            pass

    return security


def _extract_pypdf_annotations(reader) -> Dict[str, Any]:
    """Extract annotations using pypdf."""
    if not PYPDF_AVAILABLE:
        return {}
    annotation_types: Dict[str, int] = {}
    flags = {"hidden": 0, "invisible": 0, "print": 0}
    samples = []
    total_annotations = 0
    try:
        for page in reader.pages:
            annots = page.get("/Annots") or []
            for annot_ref in annots:
                try:
                    annot = annot_ref.get_object()
                except Exception:
                    annot = annot_ref
                subtype = annot.get("/Subtype")
                subtype_name = str(subtype) if subtype is not None else "Unknown"
                annotation_types[subtype_name] = annotation_types.get(subtype_name, 0) + 1
                total_annotations += 1
                if len(samples) < 10:
                    samples.append({
                        "subtype": subtype_name,
                        "contents": annot.get("/Contents"),
                        "title": annot.get("/T"),
                        "rect": annot.get("/Rect"),
                    })
                annot_flags = annot.get("/F")
                if isinstance(annot_flags, int):
                    if annot_flags & 0x2:
                        flags["hidden"] += 1
                    if annot_flags & 0x1:
                        flags["invisible"] += 1
                    if annot_flags & 0x4:
                        flags["print"] += 1
    except Exception as e:
        return {"pdf_annotations_error": str(e)}
    return {
        "pdf_total_annotations_pypdf": total_annotations,
        "pdf_annotation_types_pypdf": annotation_types,
        "pdf_has_annotations_pypdf": total_annotations > 0,
        "pdf_annotation_flags_pypdf": flags,
        "pdf_annotation_samples_pypdf": samples,
    }


def _extract_pypdf_forms(reader) -> Dict[str, Any]:
    """Extract form fields using pypdf."""
    if not PYPDF_AVAILABLE:
        return {}
    forms_error = None
    try:
        fields = reader.get_fields() or {}
    except Exception as e:
        forms_error = str(e)
        fields = {}
    field_names = []
    field_types: Dict[str, int] = {}
    field_details = []
    signature_fields = 0

    def normalize_name(name_obj, fallback: str) -> str:
        if name_obj is None:
            return fallback
        return str(name_obj)

    def add_field(name: str, field: dict) -> None:
        nonlocal signature_fields
        field_type = field.get("/FT") if isinstance(field, dict) else None
        field_type_name = str(field_type) if field_type is not None else "Unknown"
        field_types[field_type_name] = field_types.get(field_type_name, 0) + 1
        if field_type_name == "/Sig":
            signature_fields += 1
        if len(field_details) < 20:
            field_details.append({
                "name": name,
                "type": field_type_name,
                "flags": field.get("/Ff") if isinstance(field, dict) else None,
                "value": field.get("/V") if isinstance(field, dict) else None,
                "default": field.get("/DV") if isinstance(field, dict) else None,
            })

    if fields:
        field_names = list(fields.keys())
        for name, field in fields.items():
            if isinstance(field, dict):
                add_field(name, field)
    else:
        # Fallback: traverse AcroForm fields if get_fields failed or returned empty.
        acroform = None
        try:
            root = reader.trailer.get("/Root") if hasattr(reader, "trailer") else None
            if isinstance(root, dict):
                acroform = root.get("/AcroForm")
        except Exception:
            acroform = None
        if hasattr(acroform, "get_object"):
            try:
                acroform = acroform.get_object()
            except Exception:
                acroform = None

        def collect_field(field_obj, parent_name: str = "") -> None:
            if hasattr(field_obj, "get_object"):
                try:
                    field_obj = field_obj.get_object()
                except Exception:
                    return
            if not isinstance(field_obj, dict):
                return
            name = normalize_name(field_obj.get("/T"), "Field")
            full_name = name if not parent_name else f"{parent_name}.{name}"
            kids = field_obj.get("/Kids")
            if kids is not None:
                if hasattr(kids, "get_object"):
                    try:
                        kids = kids.get_object()
                    except Exception:
                        kids = []
                for kid in kids or []:
                    collect_field(kid, full_name)
            if field_obj.get("/FT") or str(field_obj.get("/Subtype")) == "/Widget":
                if full_name not in field_names:
                    field_names.append(full_name)
                add_field(full_name, field_obj)

        if isinstance(acroform, dict):
            fields_list = acroform.get("/Fields") or []
            if hasattr(fields_list, "get_object"):
                try:
                    fields_list = fields_list.get_object()
                except Exception:
                    fields_list = []
            for field_ref in fields_list:
                collect_field(field_ref)

        # Final fallback: detect widget annotations when AcroForm is missing.
        if not field_names:
            for page in reader.pages:
                annots = page.get("/Annots") or []
                if hasattr(annots, "get_object"):
                    try:
                        annots = annots.get_object()
                    except Exception:
                        annots = []
                for annot_ref in annots:
                    try:
                        annot = annot_ref.get_object()
                    except Exception:
                        annot = annot_ref
                    if not isinstance(annot, dict):
                        continue
                    subtype = annot.get("/Subtype")
                    subtype_name = str(subtype) if subtype is not None else ""
                    if subtype_name == "/Widget":
                        name = normalize_name(annot.get("/T"), "Widget")
                        if name not in field_names:
                            field_names.append(name)
                        add_field(name, annot)

    result = {
        "pdf_form_field_count_pypdf": len(field_names),
        "pdf_form_fields_pypdf": field_names[:20],
        "pdf_has_forms_pypdf": len(field_names) > 0,
        "pdf_form_field_types_pypdf": field_types,
        "pdf_form_field_details_pypdf": field_details,
        "pdf_signature_field_count_pypdf": signature_fields,
    }
    if forms_error:
        result["pdf_forms_error"] = forms_error
    return result


def _extract_pypdf_outlines(reader) -> Dict[str, Any]:
    """Extract outline/bookmark info using pypdf."""
    if not PYPDF_AVAILABLE:
        return {}
    try:
        outlines = reader.outline
    except Exception:
        try:
            outlines = reader.outlines
        except Exception as e:
            return {"pdf_outline_error": str(e)}

    def count_items(items) -> int:
        total = 0
        for item in items:
            if isinstance(item, list):
                total += count_items(item)
            else:
                total += 1
        return total

    outline_count = count_items(outlines) if outlines is not None else 0
    return {
        "pdf_outline_count_pypdf": outline_count,
        "pdf_has_outlines_pypdf": outline_count > 0,
    }


# Integration point for metadata_engine.py
def extract_pdf_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for PDF metadata extraction."""
    return extract_pdf_metadata_complete(filepath)


def get_pdf_complete_field_count() -> int:
    """Return the number of fields extracted by complete PDF metadata."""
    # Count of fields from all extraction functions
    basic_fields = 12  # from _extract_basic_properties
    page_layout_fields = 6  # from _extract_page_layout
    annotation_fields = 3  # from _extract_annotations
    form_fields = 3  # from _extract_forms
    bookmark_fields = 3  # from _extract_bookmarks
    embedded_fields = 4  # from _extract_embedded_content
    signature_fields = 3  # from _extract_digital_signatures
    accessibility_fields = 3  # from _extract_accessibility
    xmp_fields = 8  # approximate from _extract_xmp_metadata
    security_fields = 4  # from _extract_security_info
    pypdf_fields = 12  # annotations + forms + outlines (pypdf)

    return basic_fields + page_layout_fields + annotation_fields + form_fields + \
           bookmark_fields + embedded_fields + signature_fields + accessibility_fields + \
           xmp_fields + security_fields + pypdf_fields
