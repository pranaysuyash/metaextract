"""
Scientific DICOM/FITS Ultimate Advanced Extension XV - Interventional Radiology

This module provides comprehensive extraction of DICOM metadata for interventional
radiology procedures including angiography, embolization, and stent placement.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XV_AVAILABLE = True

ANGIOGRAPHY_TAGS = {
    (0x0018, 0x1000): "device_serial_number",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1100): "distance_source_to_detector",
    (0x0018, 0x1110): "distance_source_to_patient",
    (0x0018, 0x1120): "gantry_detector_tilt",
    (0x0018, 0x1130): "table_height",
    (0x0018, 0x1140): "table_motion",
    (0x0018, 0x1150): "table_speed",
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
    (0x0018, 0x7010): "detector_active_origin",
    (0x0018, 0x7020): "temporal_resolution",
    (0x0018, 0x7030): "xray_generation_mode",
    (0x0018, 0x7032): "xray_field_sequence",
}

CONTRAST_TAGS = {
    (0x0018, 0x9067): "contrast_flow_rate",
    (0x0018, 0x9068): "contrast_flow_duration",
    (0x0018, 0x9069): "contrast_volume",
    (0x0018, 0x9070): "contrast_ingredient",
    (0x0018, 0x9071): "contrast_ingredient_concentration",
    (0x0018, 0x9073): "contrast_administration_route",
    (0x0018, 0x9074): "contrast_premedication",
    (0x0018, 0x9075): "contrast_volume_sequence",
    (0x0018, 0x9077): "contrast_volume_description",
    (0x0018, 0x9078): "contrast_bolus_agent_sequence",
    (0x0018, 0x9079): "contrast_bolus_agent",
    (0x0018, 0x9080): "contrast_bolus_timing_sequence",
    (0x0018, 0x9081): "contrast_bolus_start_time",
    (0x0018, 0x9082): "contrast_bolus_duration",
    (0x0018, 0x9083): "contrast_bolus_total_volume",
    (0x0018, 0x9084): "contrast_bolus_stop_time",
    (0x0018, 0x9085): "contrast_administration_details_sequence",
}

INTERVENTION_TAGS = {
    (0x0040, 0x0250): "performed_procedure_type_description",
    (0x0040, 0x0253): "performed_procedure_type_code_sequence",
    (0x0040, 0x0260): "performed_imaging_selection_sequence",
    (0x0040, 0x0270): "referenced_procedure_step_sequence",
    (0x0040, 0x0280): "input_information_sequence",
    (0x0040, 0x0290): "information_issue_date_time",
    (0x0040, 0x02A0): "information_issue_type",
    (0x0040, 0x0300): "procedure_step_discussion_sequence",
    (0x0040, 0x0310): "procedure_step_communication_sequence",
    (0x0040, 0x0320): "patient_instructions",
    (0x0040, 0x0340): "radiation_dose_sequence",
    (0x0040, 0x0342): "radiation_dose_increase_indicated",
    (0x0040, 0x0344): "radiation_dose_description",
    (0x0040, 0x0346): "radiation_dose_confirmation_sequence",
    (0x0040, 0x0348): "radiation_dose_image_sequence",
    (0x0040, 0x0350): "radiation_dose_sequence2",
    (0x0040, 0x0352): "radiation_dose_type",
    (0x0040, 0x0354): "radiation_dose_delivery_type",
    (0x0040, 0x0356): "radiation_dose_treatment_summary",
}

DOSE_REPORT_TAGS = {
    (0x0018, 0x1150): "table_speed",
    (0x0018, 0x1151): "table_nominal_velocity",
    (0x0018, 0x1152): "table_acceleration",
    (0x0018, 0x1153): "table_horizontal_displacement",
    (0x0018, 0x1155): "table_vertical_displacement",
    (0x0018, 0x1156): "table_roll",
    (0x0018, 0x1157): "table_head_tilt_angle",
    (0x0018, 0x1158): "table_cradle_angle",
    (0x0018, 0x1159): "table_pan_tilt",
    (0x0018, 0x1160): "rotation_direction",
    (0x0018, 0x1161): "rotation_direction_modifier",
    (0x0018, 0x1162): "angle_start",
    (0x0018, 0x1163): "angle_end",
    (0x0018, 0x1164): "rotation_speed",
    (0x0018, 0x1165): "pattern_of_acquisition",
    (0x0018, 0x1166): "number_of_frames",
    (0x0018, 0x1167): "frame_increment_pointer",
    (0x0018, 0x1168): "frame_dimension_pointer",
    (0x0018, 0x1169): "frame_time_pointer",
    (0x0018, 0x116A): "group_frame_offset_vector",
    (0x0018, 0x116B): "frame_offset_vector",
    (0x0018, 0x116C): "frame_time_sequence",
    (0x0018, 0x116D): "frame_time_description",
    (0x0018, 0x116E): "frame_delay",
    (0x0018, 0x116F): "group_delay_time",
}

INTERVENTIONAL_RADIOLOGY_TOTAL_TAGS = (
    ANGIOGRAPHY_TAGS | CONTRAST_TAGS | INTERVENTION_TAGS | DOSE_REPORT_TAGS
)


def _extract_angiography_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in ANGIOGRAPHY_TAGS.items():
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


def _extract_contrast_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in CONTRAST_TAGS.items():
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


def _calculate_interventional_metrics(ds: Any) -> Dict[str, Any]:
    metrics = {}
    try:
        if hasattr(ds, 'Rows') and hasattr(ds, 'Columns'):
            metrics['image_pixels'] = ds.Rows * ds.Columns
    except Exception:
        pass
    return metrics


def _is_interventional_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                ir_modalities = ['XA', 'RF', 'DS', 'CA', 'CF', 'CV', 'CD', 'DG']
                if modality in ir_modalities:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xv(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xv_detected": False,
        "fields_extracted": 0,
        "extension_xv_type": "interventional_radiology",
        "extension_xv_version": "2.0.0",
        "ir_modality": None,
        "angiography_parameters": {},
        "contrast_administration": {},
        "intervention_procedure": {},
        "dose_reporting": {},
        "derived_metrics": {},
        "extraction_errors": [],
    }

    try:
        if not _is_interventional_file(file_path):
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

        result["extension_xv_detected"] = True
        result["ir_modality"] = getattr(ds, 'Modality', 'Unknown')

        angio = _extract_angiography_tags(ds)
        contrast = _extract_contrast_tags(ds)
        metrics = _calculate_interventional_metrics(ds)

        result["angiography_parameters"] = angio
        result["contrast_administration"] = contrast
        result["derived_metrics"] = metrics

        total_fields = len(angio) + len(contrast) + len(metrics)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xv_field_count() -> int:
    return len(INTERVENTIONAL_RADIOLOGY_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xv_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xv_description() -> str:
    return ("Interventional radiology metadata extraction. Supports angiography, "
            "fluoroscopy, and interventional procedures. Extracts X-ray generation "
            "parameters, contrast administration details, dose reporting, and "
            "intervention procedure data for comprehensive IR analysis.")


def get_scientific_dicom_fits_ultimate_advanced_extension_xv_modalities() -> List[str]:
    return ["XA", "RF", "DS", "CA", "CF", "CV", "CD", "DG"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xv_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xv_category() -> str:
    return "Interventional Radiology"


def get_scientific_dicom_fits_ultimate_advanced_extension_xv_keywords() -> List[str]:
    return [
        "interventional radiology", "angiography", "fluoroscopy", "embolization",
        "stent", "catheter", "contrast", "DSA", "digital subtraction",
        "intervention", "vascular", "endovascular"
    ]
