"""
PDF Office Forensics Metadata Extraction

This module provides comprehensive extraction of PDF and Office document metadata
for forensic analysis including version history, collaboration conflicts,
digital signatures, and embedded media provenance.

Renamed from: pdf_office_ultimate_advanced_extension_vii.py
Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
PDF_OFFICE_FORENSICS_AVAILABLE = True
PDF_OFFICE_ULTIMATE_ADVANCED_EXTENSION_VII_AVAILABLE = True  # Backward compat

# PDF Document Structure Tags
PDF_STRUCTURE_TAGS = {
    "pdf_version": "pdf_version",
    "pdf_producer": "pdf_producer",
    "pdf_creator": "pdf_creator",
    "pdf_creation_date": "creation_date",
    "pdf_modification_date": "modification_date",
    "pdf_title": "title",
    "pdf_author": "author",
    "pdf_subject": "subject",
    "pdf_keywords": "keywords",
    "pdf_trapped": "trapped",
    "pdf_page_count": "page_count",
    "pdf_page_layout": "page_layout",
    "pdf_page_mode": "page_mode",
    "pdf_language": "language",
    "pdf_tagged": "is_tagged",
    "pdf_linearized": "is_linearized",
    "pdf_encrypted": "is_encrypted",
    "pdf_encryption_method": "encryption_method",
    "pdf_permissions": "permissions",
}

# Digital Signature Tags
SIGNATURE_TAGS = {
    "signature_count": "number_of_signatures",
    "signature_valid": "all_signatures_valid",
    "signature_reason": "signature_reason",
    "signature_location": "signing_location",
    "signature_date": "signing_date",
    "signature_name": "signer_name",
    "signature_contact": "signer_contact",
    "signature_certificate_issuer": "certificate_issuer",
    "signature_certificate_subject": "certificate_subject",
    "signature_certificate_serial": "certificate_serial",
    "signature_certificate_validity": "certificate_validity",
    "signature_timestamp_authority": "timestamp_authority",
    "signature_ltv_enabled": "ltv_enabled",
}

# Version History Tags
VERSION_HISTORY_TAGS = {
    "version_history_id": "version_history_id",
    "version_count": "number_of_versions",
    "initial_version_date": "initial_creation_date",
    "latest_version_date": "latest_modification_date",
    "version_author_list": "version_authors",
    "version_comments": "version_comments",
    "incremental_saves": "incremental_save_count",
    "revision_history": "revision_history",
}

# Collaboration Tags
COLLABORATION_TAGS = {
    "collaboration_conflicts": "collaboration_conflicts",
    "conflict_resolution": "conflict_resolution_status",
    "merge_history": "merge_history",
    "co_authors": "co_authors",
    "last_editor": "last_edited_by",
    "edit_duration_total": "total_edit_duration_minutes",
    "review_cycle_count": "review_cycle_count",
    "comments_count": "total_comments",
    "tracked_changes": "tracked_changes_count",
}

# Embedded Media Tags
EMBEDDED_MEDIA_TAGS = {
    "embedded_files_count": "embedded_files_count",
    "embedded_images_count": "embedded_images_count",
    "embedded_fonts_count": "embedded_fonts_count",
    "embedded_javascript": "has_javascript",
    "embedded_forms": "has_forms",
    "embedded_multimedia": "has_multimedia",
    "attachment_names": "attachment_filenames",
    "attachment_sizes": "attachment_sizes",
    "attachment_types": "attachment_mime_types",
    "media_provenance": "embedded_media_provenance",
}

# Office Document Tags
OFFICE_DOCUMENT_TAGS = {
    "office_application": "creating_application",
    "office_version": "application_version",
    "office_template": "template_used",
    "office_company": "company",
    "office_manager": "manager",
    "office_category": "category",
    "office_content_status": "content_status",
    "office_last_printed": "last_printed_date",
    "office_revision_number": "revision_number",
    "office_total_editing_time": "total_editing_time_minutes",
    "office_word_count": "word_count",
    "office_page_count": "page_count",
    "office_paragraph_count": "paragraph_count",
    "office_line_count": "line_count",
    "office_character_count": "character_count",
    "office_slide_count": "slide_count",
    "office_hidden_slides": "hidden_slide_count",
    "office_notes_count": "notes_count",
}

# Forensic Analysis Tags
FORENSIC_TAGS = {
    "metadata_inconsistencies": "metadata_inconsistencies",
    "timestamp_anomalies": "timestamp_anomalies",
    "hidden_data": "hidden_data_detected",
    "redaction_analysis": "redaction_completeness",
    "steganography_indicators": "steganography_indicators",
    "exif_remnants": "exif_remnants_in_images",
    "gps_coordinates_found": "gps_data_in_embedded_images",
    "software_artifacts": "software_artifacts",
    "operating_system_hints": "operating_system_indicators",
    "printer_metadata": "printer_metadata_found",
}

PDF_OFFICE_FORENSICS_TOTAL_TAGS = (
    PDF_STRUCTURE_TAGS | SIGNATURE_TAGS | VERSION_HISTORY_TAGS |
    COLLABORATION_TAGS | EMBEDDED_MEDIA_TAGS | OFFICE_DOCUMENT_TAGS |
    FORENSIC_TAGS
)


def _is_pdf_office_file(file_path: str) -> bool:
    """Check if file is a PDF or Office document."""
    try:
        file_lower = file_path.lower()
        pdf_extensions = ['.pdf']
        office_extensions = ['.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt', '.odt', '.ods', '.odp']
        return any(file_lower.endswith(ext) for ext in pdf_extensions + office_extensions)
    except Exception:
        return False


def _extract_pdf_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from PDF files."""
    extracted = {}
    try:
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                info = reader.metadata
                if info:
                    if info.title:
                        extracted['title'] = str(info.title)
                    if info.author:
                        extracted['author'] = str(info.author)
                    if info.subject:
                        extracted['subject'] = str(info.subject)
                    if info.creator:
                        extracted['pdf_creator'] = str(info.creator)
                    if info.producer:
                        extracted['pdf_producer'] = str(info.producer)
                    if info.creation_date:
                        extracted['creation_date'] = str(info.creation_date)
                    if info.modification_date:
                        extracted['modification_date'] = str(info.modification_date)
                
                extracted['page_count'] = len(reader.pages)
                extracted['is_encrypted'] = reader.is_encrypted
        except ImportError:
            extracted['extraction_note'] = 'PyPDF2 not available'
    except Exception as e:
        extracted['extraction_error'] = str(e)
    return extracted


def _extract_office_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from Office documents."""
    extracted = {}
    try:
        try:
            from docx import Document
            if file_path.lower().endswith('.docx'):
                doc = Document(file_path)
                props = doc.core_properties
                if props.title:
                    extracted['title'] = props.title
                if props.author:
                    extracted['author'] = props.author
                if props.subject:
                    extracted['subject'] = props.subject
                if props.created:
                    extracted['creation_date'] = str(props.created)
                if props.modified:
                    extracted['modification_date'] = str(props.modified)
                if props.last_modified_by:
                    extracted['last_edited_by'] = props.last_modified_by
                if props.revision:
                    extracted['revision_number'] = props.revision
                if props.category:
                    extracted['category'] = props.category
                if props.comments:
                    extracted['comments'] = props.comments
        except ImportError:
            pass
        
        try:
            from openpyxl import load_workbook
            if file_path.lower().endswith('.xlsx'):
                wb = load_workbook(file_path, read_only=True, data_only=True)
                props = wb.properties
                if props.title:
                    extracted['title'] = props.title
                if props.creator:
                    extracted['author'] = props.creator
                if props.created:
                    extracted['creation_date'] = str(props.created)
                if props.modified:
                    extracted['modification_date'] = str(props.modified)
                if props.lastModifiedBy:
                    extracted['last_edited_by'] = props.lastModifiedBy
                wb.close()
        except ImportError:
            pass
            
    except Exception as e:
        extracted['extraction_error'] = str(e)
    return extracted


def extract_pdf_office_forensics(file_path: str) -> Dict[str, Any]:
    """Extract PDF and Office document forensics metadata."""
    result = {
        "pdf_office_forensics_detected": False,
        "fields_extracted": 0,
        "module_type": "pdf_office_forensics",
        "module_version": "2.0.0",
        "document_type": None,
        "pdf_structure": {},
        "digital_signatures": {},
        "version_history": {},
        "collaboration": {},
        "embedded_media": {},
        "office_metadata": {},
        "forensic_analysis": {},
        "extraction_errors": [],
    }

    try:
        if not _is_pdf_office_file(file_path):
            return result

        result["pdf_office_forensics_detected"] = True
        file_lower = file_path.lower()
        
        if file_lower.endswith('.pdf'):
            result["document_type"] = "PDF"
            pdf_data = _extract_pdf_metadata(file_path)
            result["pdf_structure"] = pdf_data
            result["fields_extracted"] = len(pdf_data)
        else:
            result["document_type"] = "Office"
            office_data = _extract_office_metadata(file_path)
            result["office_metadata"] = office_data
            result["fields_extracted"] = len(office_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def extract_pdf_office_ultimate_advanced_extension_vii(file_path: str) -> Dict[str, Any]:
    """Legacy function name for backward compatibility."""
    return extract_pdf_office_forensics(file_path)


def get_pdf_office_forensics_field_count() -> int:
    """Get the total number of PDF/Office forensics metadata fields supported."""
    return len(PDF_OFFICE_FORENSICS_TOTAL_TAGS)


def get_pdf_office_ultimate_advanced_extension_vii_field_count() -> int:
    """Legacy function name for backward compatibility."""
    return get_pdf_office_forensics_field_count()


def get_pdf_office_forensics_version() -> str:
    """Get the version of this module."""
    return "2.0.0"


def get_pdf_office_forensics_description() -> str:
    """Get the description of this module."""
    return ("PDF and Office document forensics metadata extraction. Supports version "
            "history analysis, digital signature verification, collaboration tracking, "
            "embedded media provenance, and forensic anomaly detection.")


def get_pdf_office_forensics_modalities() -> List[str]:
    """Get supported document types."""
    return ["PDF", "DOCX", "XLSX", "PPTX", "DOC", "XLS", "PPT", "ODT", "ODS", "ODP"]


def get_pdf_office_forensics_supported_formats() -> List[str]:
    """Get supported file formats."""
    return [".pdf", ".docx", ".xlsx", ".pptx", ".doc", ".xls", ".ppt", ".odt", ".ods", ".odp"]


def get_pdf_office_forensics_category() -> str:
    """Get the category of this module."""
    return "Document Forensics"


def get_pdf_office_forensics_keywords() -> List[str]:
    """Get keywords associated with this module."""
    return [
        "PDF", "Office", "forensics", "digital signature", "version history",
        "collaboration", "embedded media", "provenance", "metadata analysis",
        "document integrity", "redaction", "steganography"
    ]
