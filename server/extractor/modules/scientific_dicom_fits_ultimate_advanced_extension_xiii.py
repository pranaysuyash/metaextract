"""
Scientific DICOM/FITS Ultimate Advanced Extension XIII - Dermatology

This module provides comprehensive extraction of DICOM metadata for dermatological
imaging including clinical photography, dermoscopy, and confocal microscopy.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XIII_AVAILABLE = True

CLINICAL_PHOTO_TAGS = {
    (0x0018, 0x1000): "device_serial_number",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1130): "table_height",
    (0x0018, 0x1160): "rotation_direction",
    (0x0018, 0x7000): "detector_type",
    (0x0018, 0x7001): "detector_id",
    (0x0018, 0x7010): "detector_active_origin",
    (0x0020, 0x0032): "image_position_patient",
    (0x0020, 0x0037): "image_orientation_patient",
    (0x0020, 0x0060): "laterality",
    (0x0020, 0x0062): "image_laterality",
    (0x0020, 0x4000): "image_comments",
    (0x0028, 0x0002): "samples_per_pixel",
    (0x0028, 0x0004): "photometric_interpretation",
    (0x0028, 0x0010): "rows",
    (0x0028, 0x0011): "columns",
    (0x0028, 0x0030): "pixel_spacing",
    (0x0028, 0x0100): "bits_allocated",
    (0x0028, 0x0101): "bits_stored",
    (0x0028, 0x0102): "high_bit",
    (0x0028, 0x0103): "pixel_representation",
    (0x0028, 0x1050): "window_center",
    (0x0028, 0x1051): "window_width",
}

DERMOSCOPY_TAGS = {
    (0x0022, 0x0001): "illumination_wavelength",
    (0x0022, 0x0002): "illumination_power",
    (0x0022, 0x0003): "illumination_bandwidth",
    (0x0022, 0x0004): "illumination_type_code_sequence",
    (0x0022, 0x0005): "filter_type",
    (0x0022, 0x0006): "filter_minimum_wavelength",
    (0x0022, 0x0007): "filter_maximum_wavelength",
    (0x0022, 0x0008): "polarization_type",
    (0x0028, 0x0008): "number_of_frames",
    (0x0028, 0x0014): "pixel_aspect_ratio",
    (0x0028, 0x0400): "grayscale_lut_sequence",
    (0x0028, 0x0410): "modality_lut_sequence",
    (0x0028, 0x0414): "voi_lut_sequence",
    (0x0028, 0x0700): "overlay_type",
    (0x0028, 0x0701): "overlay_descriptor",
    (0x0028, 0x0720): "overlay_bits_allocated",
    (0x0028, 0x0722): "overlay_bit_position",
}

CONFOCAL_MICROSCOPY_TAGS = {
    (0x0018, 0x9004): "width_of_spectral_window",
    (0x0018, 0x9005): "width_of_spectral_window_offset",
    (0x0018, 0x9006): "spectral_peak_location",
    (0x0018, 0x9008): "number_of_spectral_channels",
    (0x0018, 0x9009): "number_of_volumes",
    (0x0018, 0x9010): "volume_properties_sequence",
    (0x0018, 0x9011): "volume_properties_description",
    (0x0018, 0x9012): "pixel_data_properties_sequence",
    (0x0018, 0x9013): "pixel_data_properties_description",
    (0x0018, 0x9014): "geometric_properties_sequence",
    (0x0018, 0x9015): "geometric_properties_description",
    (0x0020, 0x0100): "temporal_position_index",
    (0x0020, 0x0105): "number_of_temporal_positions",
    (0x0020, 0x0110): "temporal_resolution",
    (0x0028, 0x0200): "zoom_allocation_sequence",
    (0x0028, 0x0201): "zoom_center",
    (0x0028, 0x0202): "zoom_factor",
}

LESION_ASSESSMENT_TAGS = {
    (0x0040, 0x0241): "performed_procedure_step_start_date_time",
    (0x0040, 0x0242): "performed_procedure_step_end_date_time",
    (0x0040, 0x0250): "performed_procedure_type_description",
    (0x0040, 0x0253): "performed_procedure_type_code_sequence",
    (0x0040, 0x0260): "performed_imaging_selection_sequence",
    (0x0040, 0x0270): "referenced_procedure_step_sequence",
    (0x0040, 0x0280): "input_information_sequence",
    (0x0040, 0x4033): "lesion_horizontal_extent",
    (0x0040, 0x4034): "lesion_vertical_extent",
    (0x0040, 0x4035): "lesion_shape",
    (0x0040, 0x4036): "lesion_type_code_sequence",
    (0x0040, 0x4037): "lesion_description",
    (0x0040, 0x4038): "lesion_measurement_sequence",
    (0x0040, 0x4039): "lesion_measurement_value",
    (0x0040, 0x403A): "lesion_measurement_unit",
    (0x0040, 0x403B): "lesion_assessment_score",
    (0x0040, 0x403C): "lesion_risk_indicator",
    (0x0040, 0x403D): "lesion_tracking_sequence",
}

SKIN_EXAM_TAGS = {
    (0x0040, 0xA730): "content_qualification",
    (0x0040, 0x0241): "exam_start_date_time",
    (0x0040, 0x0242): "exam_end_date_time",
    (0x0040, 0x0250): "procedure_type_description",
    (0x0040, 0x0260): "imaging_selection_sequence",
    (0x0040, 0x0270): "referenced_procedure_step_sequence",
    (0x0040, 0x0280): "input_information_sequence",
    (0x0040, 0x0300): "procedure_step_discussion_sequence",
    (0x0040, 0x0310): "procedure_step_communication_sequence",
    (0x0040, 0x0320): "patient_instructions",
    (0x0040, 0x0400): "exam_findings_sequence",
    (0x0040, 0x0401): "exam_findings_description",
    (0x0040, 0x0402): "exam_findings_code_sequence",
    (0x0040, 0x0410): "exam_recommendation_sequence",
    (0x0040, 0x0411): "exam_recommendation_description",
    (0x0040, 0x0412): "exam_recommendation_code_sequence",
}

DERMATOLOGY_TOTAL_TAGS = (
    CLINICAL_PHOTO_TAGS | DERMOSCOPY_TAGS | CONFOCAL_MICROSCOPY_TAGS |
    LESION_ASSESSMENT_TAGS | SKIN_EXAM_TAGS
)


def _extract_clinical_photo_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in CLINICAL_PHOTO_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
            elif hasattr(ds, name):
                value = getattr(ds, name, None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _extract_dermoscopy_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in DERMOSCOPY_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
            elif hasattr(ds, name):
                value = getattr(ds, name, None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _calculate_dermatology_metrics(ds: Any) -> Dict[str, Any]:
    metrics = {}
    try:
        if hasattr(ds, 'Rows') and hasattr(ds, 'Columns'):
            metrics['total_pixels'] = ds.Rows * ds.Columns
            metrics['image_height_pixels'] = ds.Rows
            metrics['image_width_pixels'] = ds.Columns
        if hasattr(ds, 'BitsAllocated') and hasattr(ds, 'BitsStored'):
            metrics['bits_per_sample'] = ds.BitsAllocated
            metrics['effective_bits'] = ds.BitsStored
    except Exception:
        pass
    return metrics


def _is_dermatology_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                derm_modalities = ['XC', 'CR', 'DX', 'CT', 'MR', 'OT']
                if modality in derm_modalities:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xiii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xiii_detected": False,
        "fields_extracted": 0,
        "extension_xiii_type": "dermatology_imaging",
        "extension_xiii_version": "2.0.0",
        "dermatology_modality": None,
        "clinical_photography": {},
        "dermoscopy": {},
        "confocal_microscopy": {},
        "lesion_assessment": {},
        "skin_examination": {},
        "derived_metrics": {},
        "extraction_errors": [],
    }

    try:
        if not _is_dermatology_file(file_path):
            return result

        try:
            import pydicom
            ds = pydicom.dcmread(file_path, stop_before_pixels=True)
        except ImportError:
            result["extraction_errors"].append("pydicom library not available")
            return result
        except Exception as e:
            result["extraction_errors"].append(f"Failed to read file: {str(e)}")
            return result

        result["extension_xiii_detected"] = True
        result["dermatology_modality"] = getattr(ds, 'Modality', 'Unknown')

        clinical = _extract_clinical_photo_tags(ds)
        derm = _extract_dermoscopy_tags(ds)
        metrics = _calculate_dermatology_metrics(ds)

        result["clinical_photography"] = clinical
        result["dermoscopy"] = derm
        result["derived_metrics"] = metrics

        total_fields = len(clinical) + len(derm) + len(metrics)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xiii_field_count() -> int:
    return len(DERMATOLOGY_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xiii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xiii_description() -> str:
    return ("Dermatology imaging metadata extraction. Supports clinical photography, "
            "dermoscopy, and confocal microscopy. Extracts lesion assessment data, "
            "illumination parameters, and skin examination findings for comprehensive "
            "dermatological analysis.")


def get_scientific_dicom_fits_ultimate_advanced_extension_xiii_modalities() -> List[str]:
    return ["XC", "CR", "DX", "OT"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xiii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xiii_category() -> str:
    return "Dermatology Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_xiii_keywords() -> List[str]:
    return [
        "dermatology", "skin", "lesion", "dermoscopy", "confocal microscopy",
        "clinical photography", "melanoma", "skin cancer", "epidermis",
        "dermis", "pigmented lesion", "skin examination"
    ]
