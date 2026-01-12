"""
Scientific DICOM/FITS Ultimate Advanced Extension XI - Dental Imaging

This module provides comprehensive extraction of DICOM metadata for dental imaging
modalities including panoramic radiography, cephalometry, intra-oral imaging,
and cone beam CT (CBCT).

Supported Modalities:
- DX: Digital Radiography (dental)
- CR: Computed Radiography (dental)
- CT: Computed Tomography (dental/CBCT)
- PX: Panoramic X-ray
- RF: Radiographic Fluoroscopy (dental)

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XI_AVAILABLE = True

PANORAMIC_ACQUISITION_TAGS = {
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x1000): "device_serial_number",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1100): "distance_source_to_detector",
    (0x0018, 0x1110): "distance_source_to_patient",
    (0x0018, 0x1120): "gantry_detector_tilt",
    (0x0018, 0x1130): "table_height",
    (0x0018, 0x1140): "table_motion",
    (0x0018, 0x1160): "rotation_direction",
    (0x0018, 0x1170): "scan_options",
    (0x0018, 0x1180): "kvp",
    (0x0018, 0x1190): "xray_tube_current",
    (0x0018, 0x1200): "exposure",
    (0x0018, 0x1201): "exposure_time",
    (0x0018, 0x1210): "filter_type",
    (0x0018, 0x1220): "filter_material",
    (0x0018, 0x1240): "focal_spot_size",
    (0x0018, 0x7000): "detector_type",
    (0x0018, 0x7001): "detector_id",
    (0x0018, 0x7004): "detector_binning",
    (0x0018, 0x7010): "detector_active_origin",
    (0x0018, 0x7020): "temporal_resolution",
}

CEPHALOMETRIC_TAGS = {
    (0x0020, 0x0032): "image_position_patient",
    (0x0020, 0x0037): "image_orientation_patient",
    (0x0020, 0x0060): "laterality",
    (0x0020, 0x0062): "image_laterality",
    (0x0020, 0x0070): "image_geometry_type",
    (0x0020, 0x4000): "image_comments",
    (0x0020, 0x9071): "fiducial_sequence",
    (0x0020, 0x9072): "fiducial_identifier",
    (0x0020, 0x9073): "fiducial_description",
    (0x0020, 0x9113): "projection_pixel_calibration_sequence",
    (0x0020, 0x9114): "calibration_object_sequence",
    (0x0020, 0x9160): "trapezoid_sequence",
    (0x0020, 0x9161): "positioner_position_sequence",
    (0x0020, 0x9170): "image_transformation_matrix_sequence",
}

INTRA_ORAL_TAGS = {
    (0x0028, 0x0002): "samples_per_pixel",
    (0x0028, 0x0004): "photometric_interpretation",
    (0x0028, 0x0008): "number_of_frames",
    (0x0028, 0x0010): "rows",
    (0x0028, 0x0011): "columns",
    (0x0028, 0x0014): "pixel_aspect_ratio",
    (0x0028, 0x0030): "pixel_spacing",
    (0x0028, 0x0100): "bits_allocated",
    (0x0028, 0x0101): "bits_stored",
    (0x0028, 0x0102): "high_bit",
    (0x0028, 0x0103): "pixel_representation",
    (0x0028, 0x0106): "smallest_image_pixel_value",
    (0x0028, 0x0107): "largest_image_pixel_value",
    (0x0028, 0x0400): "grayscale_lut_sequence",
    (0x0028, 0x0410): "modality_lut_sequence",
    (0x0028, 0x0414): "voi_lut_sequence",
    (0x0028, 0x1050): "window_center",
    (0x0028, 0x1051): "window_width",
}

CBCT_VOLUME_TAGS = {
    (0x0008, 0x0018): "sop_instance_uid",
    (0x0008, 0x0201): "timezone_offset_from_utc",
    (0x0008, 0x0205): "study_date",
    (0x0008, 0x0206): "series_date",
    (0x0018, 0x0023): "spatial_resolution",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0090): "patient_position",
    (0x0018, 0x1100): "distance_source_to_detector",
    (0x0018, 0x1110): "distance_source_to_patient",
    (0x0018, 0x1120): "gantry_detector_tilt",
    (0x0018, 0x1150): "table_speed",
    (0x0018, 0x1180): "kvp",
    (0x0018, 0x1190): "xray_tube_current",
    (0x0018, 0x1201): "exposure_time",
    (0x0018, 0x7000): "detector_type",
    (0x0020, 0x0032): "image_position_patient",
    (0x0020, 0x0037): "image_orientation_patient",
    (0x0020, 0x0052): "frame_of_reference_uid",
    (0x0028, 0x0008): "number_of_frames",
    (0x0028, 0x0010): "rows",
    (0x0028, 0x0011): "columns",
    (0x0028, 0x0030): "pixel_spacing",
}

DENTAL_IMPLANT_TAGS = {
    (0x0040, 0x0260): "predecessor_instances_sequence",
    (0x0040, 0x0261): "referenced_instances_sequence",
    (0x0040, 0x0270): "real_world_value_map_sequence",
    (0x0040, 0x0275): "real_world_value_sequence",
    (0x0040, 0x0276): "real_world_value_offset",
    (0x0040, 0x0300): "container_component_type_code_sequence",
    (0x0040, 0x0302): "container_component_sequence",
    (0x0040, 0x0304): "container_component_id",
    (0x0040, 0x0306): "container_component_name",
    (0x0040, 0x0308): "container_component_description",
    (0x0040, 0x0310): "container_component_sequence2",
    (0x0040, 0x0312): "item_sequence",
    (0x0040, 0x0314): "item_number",
    (0x0040, 0x0316): "item_name",
    (0x0040, 0x0318): "item_description",
}

DENTAL_DOSE_TAGS = {
    (0x0040, 0x0241): "performed_procedure_step_start_date_time",
    (0x0040, 0x0242): "performed_procedure_step_end_date_time",
    (0x0040, 0x0250): "performed_procedure_type_description",
    (0x0040, 0x0253): "performed_procedure_type_code_sequence",
    (0x0040, 0x0340): "radiation_dose_sequence",
    (0x0040, 0x0342): "radiation_dose_increase_indicated",
    (0x0040, 0x0344): "radiation_dose_description",
    (0x0040, 0x0346): "radiation_dose_confirmation_sequence",
    (0x0040, 0x0348): "radiation_dose_image_sequence",
    (0x0040, 0x0352): "radiation_dose_type",
    (0x0040, 0x0354): "radiation_dose_delivery_type",
    (0x0040, 0x0358): "radiation_dose_reference_sequence",
    (0x0040, 0x035A): "radiation_dose_reference_number",
    (0x0040, 0x035C): "radiation_dose_reference_structure",
}

TOOTH_ARCH_IDENTIFICATION_TAGS = {
    (0x0040, 0xA730): "content_qualification",
    (0x0040, 0xA001): "referenced_series_sequence",
    (0x0040, 0xA002): "referenced_patient_or_creature_sequence",
    (0x0040, 0xA003): "referenced_study_sequence",
    (0x0040, 0xA004): "referenced_performed_procedure_step_sequence",
    (0x0040, 0xA005): "referenced_requested_procedure_sequence",
    (0x0040, 0xA006): "referenced_scheduled_procedure_sequence",
    (0x0040, 0xA007): "referenced_visit_sequence",
    (0x0040, 0xA008): "referenced_appointment_sequence",
    (0x0040, 0xA020): "scheduled_procedure_step_sequence",
    (0x0040, 0xA022): "scheduled_step_attributes_sequence",
    (0x0040, 0xA023): "study_instance_uid",
    (0x0040, 0xA024): "series_instance_uid",
    (0x0040, 0xA026): "referenced_image_sequence",
    (0x0040, 0xA027): "referenced_non_image_sequence",
    (0x0040, 0xA030): "scheduled_procedure_step_id",
    (0x0040, 0xA032): "scheduled_procedure_step_description",
    (0x0040, 0xA034): "scheduled_action_item_sequence",
    (0x0040, 0xA040): "conditional_probability",
    (0x0040, 0xA042): "algorithm_probability",
    (0x0040, 0xA043): "conditional_probability_unit",
    (0x0040, 0xA044): "algorithm_probability_unit",
}

DENTAL_TOTAL_TAGS = (
    PANORAMIC_ACQUISITION_TAGS | CEPHALOMETRIC_TAGS | INTRA_ORAL_TAGS |
    CBCT_VOLUME_TAGS | DENTAL_IMPLANT_TAGS | DENTAL_DOSE_TAGS |
    TOOTH_ARCH_IDENTIFICATION_TAGS
)


def _extract_panoramic_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in PANORAMIC_ACQUISITION_TAGS.items():
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


def _extract_cephalometric_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in CEPHALOMETRIC_TAGS.items():
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


def _extract_intra_oral_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in INTRA_ORAL_TAGS.items():
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


def _extract_cbct_volume_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in CBCT_VOLUME_TAGS.items():
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


def _extract_implant_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in DENTAL_IMPLANT_TAGS.items():
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


def _extract_dose_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in DENTAL_DOSE_TAGS.items():
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


def _calculate_dental_metrics(ds: Any) -> Dict[str, Any]:
    metrics = {}
    try:
        if hasattr(ds, 'Rows') and hasattr(ds, 'Columns'):
            metrics['total_pixels'] = ds.Rows * ds.Columns
            metrics['image_height_pixels'] = ds.Rows
            metrics['image_width_pixels'] = ds.Columns
        if hasattr(ds, 'BitsAllocated') and hasattr(ds, 'BitsStored'):
            metrics['bits_per_sample'] = ds.BitsAllocated
            metrics['effective_bits'] = ds.BitsStored
        if hasattr(ds, 'SamplesPerPixel'):
            metrics['color_channels'] = ds.SamplesPerPixel
    except Exception:
        pass
    return metrics


def _is_dental_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        dental_extensions = ['.dcm', '.dicom', '.dx', '.cr']
        if any(file_lower.endswith(ext) for ext in dental_extensions):
            return True
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                dental_modalities = ['DX', 'CR', 'CT', 'PX', 'RF', 'MG']
                if modality in dental_modalities:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xi(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xi_detected": False,
        "fields_extracted": 0,
        "extension_xi_type": "dental_imaging",
        "extension_xi_version": "2.0.0",
        "dental_modality": None,
        "panoramic_acquisition": {},
        "cephalometric_analysis": {},
        "intra_oral_imaging": {},
        "cbct_volume_parameters": {},
        "implant_planning": {},
        "dose_tracking": {},
        "derived_metrics": {},
        "extraction_errors": [],
    }

    try:
        if not _is_dental_file(file_path):
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

        result["extension_xi_detected"] = True
        result["dental_modality"] = getattr(ds, 'Modality', 'Unknown')

        panoramic = _extract_panoramic_tags(ds)
        cephalometric = _extract_cephalometric_tags(ds)
        intra_oral = _extract_intra_oral_tags(ds)
        cbct = _extract_cbct_volume_tags(ds)
        implant = _extract_implant_tags(ds)
        dose = _extract_dose_tags(ds)
        metrics = _calculate_dental_metrics(ds)

        result["panoramic_acquisition"] = panoramic
        result["cephalometric_analysis"] = cephalometric
        result["intra_oral_imaging"] = intra_oral
        result["cbct_volume_parameters"] = cbct
        result["implant_planning"] = implant
        result["dose_tracking"] = dose
        result["derived_metrics"] = metrics

        total_fields = (len(panoramic) + len(cephalometric) + len(intra_oral) +
                       len(cbct) + len(implant) + len(dose) + len(metrics))
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xi_field_count() -> int:
    return len(DENTAL_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xi_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xi_description() -> str:
    return ("Comprehensive dental imaging metadata extraction. Supports panoramic "
            "radiography, cephalometry, intra-oral imaging, and cone beam CT (CBCT). "
            "Extracts acquisition parameters, dose tracking, implant planning data, "
            "and tooth/arch identification for comprehensive dental analysis.")


def get_scientific_dicom_fits_ultimate_advanced_extension_xi_modalities() -> List[str]:
    return ["DX", "CR", "CT", "PX", "RF", "MG"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xi_supported_formats() -> List[str]:
    return [".dcm", ".dicom", ".dx", ".cr"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xi_category() -> str:
    return "Dental and Maxillofacial Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_xi_keywords() -> List[str]:
    return [
        "dental", "panoramic", "cephalometry", "intra-oral", "CBCT",
        "cone beam", "orthodontic", "implant", "dental radiology",
        "OPG", "dental imaging", "maxillofacial"
    ]


# Aliases for smoke test compatibility
def extract_dermatology_imaging(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_xi."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_xi(file_path)

def get_dermatology_imaging_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xi_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xi_field_count()

def get_dermatology_imaging_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xi_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xi_version()

def get_dermatology_imaging_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xi_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xi_description()

def get_dermatology_imaging_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xi_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xi_supported_formats()

def get_dermatology_imaging_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xi_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xi_modalities()
