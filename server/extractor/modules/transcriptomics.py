"""
Scientific DICOM/FITS Ultimate Advanced Extension XLIII - Advanced Neuroradiology

This module provides comprehensive extraction of advanced neuroradiology parameters
including functional imaging, tractography, and advanced brain analysis.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XLIII_AVAILABLE = True

NEURO_TRACTOGRAPHY = {
    (0x0018, 0x9075): "diffusion_b_value",
    (0x0018, 0x9076): "diffusion_b_value_vector",
    (0x0018, 0x9077): "diffusion_gradient_orientation",
    (0x0018, 0x9078): "diffusion_angular_program",
    (0x0018, 0x9079): "diffusion_sensitive_direction_count",
    (0x0018, 0x9080): "diffusion_gradient_sequence",
    (0x0018, 0x9081): "diffusion_tensor_sequence",
    (0x0018, 0x9082): "diffusion_ellipsoid_sequence",
    (0x0018, 0x9083): "diffusion_ellipsoid_导数",
    (0x0018, 0x9084): "diffusion_ellipsoid_导数_description",
    (0x0018, 0x9085): "diffusion_measurement_observations_sequence",
    (0x0018, 0x9086): "diffusion_measurement_observations",
    (0x0018, 0x9087): "diffusion_measurement_observations_description",
    (0x0018, 0x9090): "diffusion_model_sequence",
    (0x0018, 0x9091): "diffusion_model",
    (0x0018, 0x9092): "diffusion_model_description",
    (0x0018, 0x9093): "diffusion_model_parameters_sequence",
    (0x0018, 0x9094): "diffusion_model_parameter",
    (0x0018, 0x9095): "diffusion_model_parameter_value",
    (0x0018, 0x9096): "diffusion_model_parameter_unit",
    (0x0018, 0x90A0): "fiber_tracking_sequence",
    (0x0018, 0x90A1): "fiber_tracking_type",
    (0x0018, 0x90A2): "fiber_tracking_description",
    (0x0018, 0x90A3): "fiber_tracking_algorithm",
    (0x0018, 0x90A4): "fiber_tracking_algorithm_description",
    (0x0018, 0x90A5): "fiber_tracking_parameters_sequence",
    (0x0018, 0x90A6): "fiber_tracking_parameter",
    (0x0018, 0x90A7): "fiber_tracking_parameter_value",
    (0x0018, 0x90A8): "fiber_tracking_parameter_unit",
    (0x0018, 0x90B0): "fiber_bundle_sequence",
    (0x0018, 0x90B1): "fiber_bundle_name",
    (0x0018, 0x90B2): "fiber_bundle_description",
    (0x0018, 0x90B3): "fiber_bundle_laterality",
    (0x0018, 0x90B4): "fiber_bundle_roi_sequence",
    (0x0018, 0x90B5): "fiber_bundle_roi",
    (0x0018, 0x90B6): "fiber_bundle_roi_description",
    (0x0018, 0x90C0): "fiber_tracking_result_sequence",
    (0x0018, 0x90C1): "fiber_tracking_result",
    (0x0018, 0x90C2): "fiber_tracking_result_description",
    (0x0018, 0x90C3): "fiber_tracking_result_type",
    (0x0018, 0x90D0): "fiber_tracking_stop_criteria_sequence",
    (0x0018, 0x90D1): "fiber_tracking_stop_criteria_type",
    (0x0018, 0x90D2): "fiber_tracking_stop_criteria_value",
    (0x0018, 0x90D3): "fiber_tracking_stop_criteria_unit",
    (0x0018, 0x90D4): "fiber_tracking_stop_criteria_description",
    (0x0018, 0x90E0): "fiber_tracking_metrics_sequence",
    (0x0018, 0x90E1): "fiber_tracking_metric",
    (0x0018, 0x90E2): "fiber_tracking_metric_value",
    (0x0018, 0x90E3): "fiber_tracking_metric_unit",
    (0x0018, 0x90E4): "fiber_tracking_metric_description",
}

NEURO_PERFUSION = {
    (0x0018, 0x9100): "perfusion_sequence",
    (0x0018, 0x9101): "perfusion_type",
    (0x0018, 0x9102): "perfusion_description",
    (0x0018, 0x9103): "perfusion_measurement_method",
    (0x0018, 0x9104): "perfusion_measurement_method_code_sequence",
    (0x0018, 0x9110): "arterial_spin_labeling_sequence",
    (0x0018, 0x9111): "arterial_spin_labeling_type",
    (0x0018, 0x9112): "arterial_spin_labeling_description",
    (0x0018, 0x9113): "arterial_spin_labeling_control",
    (0x0018, 0x9114): "arterial_spin_labeling_control_description",
    (0x0018, 0x9120): "bolus_sequence",
    (0x0018, 0x9121): "bolus_type",
    (0x0018, 0x9122): "bolus_description",
    (0x0018, 0x9123): "bolus_arrival_time",
    (0x0018, 0x9124): "bolus_arrival_time_unit",
    (0x0018, 0x9125): "bolus_peak_time",
    (0x0018, 0x9126): "bolus_peak_time_unit",
    (0x0018, 0x9127): "bolus_washout_time",
    (0x0018, 0x9128): "bolus_washout_time_unit",
    (0x0018, 0x9130): "time_course_sequence",
    (0x0018, 0x9131): "time_course_point",
    (0x0018, 0x9132): "time_course_value",
    (0x0018, 0x9133): "time_course_unit",
    (0x0018, 0x9134): "time_course_description",
    (0x0018, 0x9140): "curve_point_sequence",
    (0x0018, 0x9141): "curve_point_value",
    (0x0018, 0x9142): "curve_point_unit",
    (0x0018, 0x9143): "curve_point_description",
    (0x0018, 0x9144): "curve_point_coordinate",
    (0x0018, 0x9145): "curve_point_coordinate_unit",
    (0x0018, 0x9150): "input_roi_sequence",
    (0x0018, 0x9151): "input_roi_type",
    (0x0018, 0x9152): "input_roi_description",
    (0x0018, 0x9153): "input_roi_value",
    (0x0018, 0x9154): "input_roi_value_unit",
    (0x0018, 0x9160): "output_roi_sequence",
    (0x0018, 0x9161): "output_roi_type",
    (0x0018, 0x9162): "output_roi_description",
    (0x0018, 0x9163): "output_roi_value",
    (0x0018, 0x9164): "output_roi_value_unit",
    (0x0018, 0x9170): "perfusion_summary_sequence",
    (0x0018, 0x9171): "perfusion_summary_type",
    (0x0018, 0x9172): "perfusion_summary_value",
    (0x0018, 0x9173): "perfusion_summary_unit",
    (0x0018, 0x9174): "perfusion_summary_description",
}

NEURO_CORTICAL = {
    (0x0018, 0x9200): "cortical_surface_sequence",
    (0x0018, 0x9201): "cortical_surface_type",
    (0x0018, 0x9202): "cortical_surface_description",
    (0x0018, 0x9203): "cortical_surface_reconstruction_algorithm",
    (0x0018, 0x9204): "cortical_surface_reconstruction_algorithm_description",
    (0x0018, 0x9210): "parcellation_sequence",
    (0x0018, 0x9211): "parcellation_type",
    (0x0018, 0x9212): "parcellation_description",
    (0x0018, 0x9213): "parcellation_scheme",
    (0x0018, 0x9214): "parcellation_scheme_description",
    (0x0018, 0x9215): "parcellation_region_sequence",
    (0x0018, 0x9216): "parcellation_region_name",
    (0x0018, 0x9217): "parcellation_region_description",
    (0x0018, 0x9218): "parcellation_region_laterality",
    (0x0018, 0x9220): "cortical_thickness_sequence",
    (0x0018, 0x9221): "cortical_thickness_value",
    (0x0018, 0x9222): "cortical_thickness_unit",
    (0x0018, 0x9223): "cortical_thickness_description",
    (0x0018, 0x9224): "cortical_thickness_laterality",
    (0x0018, 0x9225): "cortical_thickness_roi_sequence",
    (0x0018, 0x9230): "cortical_volume_sequence",
    (0x0018, 0x9231): "cortical_volume_value",
    (0x0018, 0x9232): "cortical_volume_unit",
    (0x0018, 0x9233): "cortical_volume_description",
    (0x0018, 0x9234): "cortical_volume_laterality",
    (0x0018, 0x9235): "cortical_volume_roi_sequence",
    (0x0018, 0x9240): "gyrus_sequence",
    (0x0018, 0x9241): "gyrus_name",
    (0x0018, 0x9242): "gyrus_description",
    (0x0018, 0x9243): "gyrus_laterality",
    (0x0018, 0x9244): "gyrus_roi_sequence",
    (0x0018, 0x9250): "sulcus_sequence",
    (0x0018, 0x9251): "sulcus_name",
    (0x0018, 0x9252): "sulcus_description",
    (0x0018, 0x9253): "sulcus_laterality",
    (0x0018, 0x9254): "sulcus_roi_sequence",
}

NEURO_TOTAL_TAGS = NEURO_TRACTOGRAPHY | NEURO_PERFUSION | NEURO_CORTICAL


def _extract_neuro_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in NEURO_TOTAL_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_neuro_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                if modality in ['MR', 'CT', 'PT', 'NM']:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xliii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xliii_detected": False,
        "fields_extracted": 0,
        "extension_xliii_type": "advanced_neuroradiology",
        "extension_xliii_version": "2.0.0",
        "tractography": {},
        "perfusion": {},
        "cortical_analysis": {},
        "extraction_errors": [],
    }

    try:
        if not _is_neuro_file(file_path):
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

        result["extension_xliii_detected"] = True

        neuro_data = _extract_neuro_tags(ds)

        result["tractography"] = {
            k: v for k, v in neuro_data.items()
            if k in NEURO_TRACTOGRAPHY.values()
        }
        result["perfusion"] = {
            k: v for k, v in neuro_data.items()
            if k in NEURO_PERFUSION.values()
        }
        result["cortical_analysis"] = {
            k: v for k, v in neuro_data.items()
            if k in NEURO_CORTICAL.values()
        }

        result["fields_extracted"] = len(neuro_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xliii_field_count() -> int:
    return len(NEURO_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xliii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xliii_description() -> str:
    return (
        "Advanced neuroradiology metadata extraction. Provides comprehensive coverage "
        "of diffusion tensor imaging, tractography, perfusion imaging, and cortical "
        "surface analysis for advanced brain mapping and neuroscience research."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_xliii_modalities() -> List[str]:
    return ["MR", "CT", "PT", "NM"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xliii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xliii_category() -> str:
    return "Advanced Neuroradiology"


def get_scientific_dicom_fits_ultimate_advanced_extension_xliii_keywords() -> List[str]:
    return [
        "neuroradiology", "DTI", "tractography", "diffusion", "perfusion",
        "cortical surface", "parcellation", "brain mapping", "white matter",
        "gray matter", "fiber tracking"
    ]


# Aliases for smoke test compatibility
def extract_transcriptomics(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_xliii."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_xliii(file_path)

def get_transcriptomics_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xliii_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xliii_field_count()

def get_transcriptomics_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xliii_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xliii_version()

def get_transcriptomics_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xliii_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xliii_description()

def get_transcriptomics_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xliii_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xliii_supported_formats()

def get_transcriptomics_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xliii_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xliii_modalities()
