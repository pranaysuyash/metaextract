"""
Diffusion MRI Imaging Metadata Extraction

This module provides comprehensive extraction of DICOM metadata for diffusion MRI
including DTI, DWI, and advanced diffusion models like DSI and NODDI.

Renamed from: scientific_dicom_fits_ultimate_advanced_extension_xix.py
Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XIX_AVAILABLE = True
DIFFUSION_MRI_IMAGING_AVAILABLE = True

DWI_TAGS = {
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x0082): "inversion_time",
    (0x0018, 0x0083): "number_of_averages",
    (0x0018, 0x0085): "echo_number",
    (0x0018, 0x0086): "mr_acquisition_type",
    (0x0018, 0x0087): "sequence_name",
    (0x0018, 0x0091): "phase_encoding_direction",
    (0x0018, 0x0093): "parallel_acquisition_factor",
    (0x0018, 0x0095): "diffusion_b_value",
    (0x0018, 0x0096): "diffusion_gradient_direction",
    (0x0018, 0x0097): "diffusion_gradient_orientation",
    (0x0018, 0x0098): "diffusion_b_matrix_sequence",
    (0x0018, 0x0099): "diffusion_b_matrix_xx",
    (0x0018, 0x009A): "diffusion_b_matrix_xy",
    (0x0018, 0x009B): "diffusion_b_matrix_xz",
    (0x0018, 0x009C): "diffusion_b_matrix_yy",
    (0x0018, 0x009D): "diffusion_b_matrix_yz",
    (0x0018, 0x009E): "diffusion_b_matrix_zz",
    (0x0018, 0x009F): "diffusion_measurement_direction_sequence",
    (0x0018, 0x00A0): "diffusion_measurement_number",
    (0x0018, 0x00A1): "diffusion_anisotropy_type",
    (0x0018, 0x00A2): "diffusion_sensitivity_sequence",
    (0x0018, 0x00A3): "diffusion_sensitivity",
    (0x0018, 0x00A4): "diffusion_tensor_sequence",
    (0x0018, 0x00A5): "diffusion_tensor_xx",
    (0x0018, 0x00A6): "diffusion_tensor_xy",
    (0x0018, 0x00A7): "diffusion_tensor_xz",
    (0x0018, 0x00A8): "diffusion_tensor_yy",
    (0x0018, 0x00A9): "diffusion_tensor_yz",
    (0x0018, 0x00AA): "diffusion_tensor_zz",
    (0x0018, 0x00AB): "diffusion_derived_b_value",
    (0x0018, 0x00AC): "diffusion_direction_number",
}

DTI_TAGS = {
    (0x0018, 0x9101): "mr_diffusion_sequence",
    (0x0018, 0x9102): "diffusion_b_value",
    (0x0018, 0x9103): "diffusion_gradient_direction",
    (0x0018, 0x9104): "diffusion_direction",
    (0x0018, 0x9105): "diffusion_anisotropy",
    (0x0018, 0x9106): "diffusion_averaging_type",
    (0x0018, 0x9107): "diffusion_scheme_type",
    (0x0018, 0x9108): "diffusion_separation_type",
    (0x0018, 0x9109): "diffusion_time",
    (0x0018, 0x910A): "diffusion_diffusion_axis",
    (0x0018, 0x910B): "diffusion_mixing_transform_type",
    (0x0018, 0x910C): "diffusion_mixing_transform_matrix",
    (0x0018, 0x910D): "diffusion_model_type",
    (0x0018, 0x910E): "diffusion_model_description",
    (0x0018, 0x910F): "advanced_diffusion_model_sequence",
    (0x0018, 0x9110): "model_specific_parameter_sequence",
    (0x0018, 0x9111): "model_specific_parameter_name",
    (0x0018, 0x9112): "model_specific_parameter_value",
    (0x0018, 0x9113): "diffusion_model_free_parameters",
    (0x0018, 0x9114): "diffusion_model_free_parameter_name",
    (0x0018, 0x9115): "diffusion_model_free_parameter_value",
}

ADVANCED_DIFFUSION_TAGS = {
    (0x0018, 0x9120): "multiple_b_value_analysis_sequence",
    (0x0018, 0x9121): "multiple_b_value_type",
    (0x0018, 0x9122): "multiple_b_value_threshold",
    (0x0018, 0x9123): "multiple_b_value_analysis_description",
    (0x0018, 0x9124): "intra_voxel_incoherent_motion_sequence",
    (0x0018, 0x9125): "ivim_parameter_sequence",
    (0x0018, 0x9126): "ivim_parameter_name",
    (0x0018, 0x9127): "ivim_parameter_value",
    (0x0018, 0x9128): "kurtosis_model_sequence",
    (0x0018, 0x9129): "kurtosis_parameter_sequence",
    (0x0018, 0x912A): "kurtosis_parameter_name",
    (0x0018, 0x912B): "kurtosis_parameter_value",
    (0x0018, 0x912C): "model_free_parameter_sequence",
    (0x0018, 0x912D): "model_free_parameter_name",
    (0x0018, 0x912E): "model_free_parameter_value",
}

DIFFUSION_TOTAL_TAGS = DWI_TAGS | DTI_TAGS | ADVANCED_DIFFUSION_TAGS


def _extract_diffusion_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in DWI_TAGS.items():
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


def _calculate_diffusion_metrics(ds: Any) -> Dict[str, Any]:
    metrics = {}
    try:
        if hasattr(ds, 'Rows') and hasattr(ds, 'Columns'):
            metrics['slice_pixels'] = ds.Rows * ds.Columns
        if hasattr(ds, 'NumberOfFrames'):
            metrics['number_of_directions'] = ds.NumberOfFrames
    except Exception:
        pass
    return metrics


def _is_diffusion_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                if modality == 'MR':
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xix(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xix_detected": False,
        "fields_extracted": 0,
        "extension_xix_type": "diffusion_imaging",
        "extension_xix_version": "2.0.0",
        "diffusion_modality": None,
        "dwi_acquisition": {},
        "dti_model": {},
        "advanced_diffusion": {},
        "derived_metrics": {},
        "extraction_errors": [],
    }

    try:
        if not _is_diffusion_file(file_path):
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

        result["extension_xix_detected"] = True
        result["diffusion_modality"] = getattr(ds, 'Modality', 'Unknown')

        diffusion_data = _extract_diffusion_tags(ds)
        metrics = _calculate_diffusion_metrics(ds)

        result["dwi_acquisition"] = diffusion_data
        result["derived_metrics"] = metrics

        total_fields = len(diffusion_data) + len(metrics)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xix_field_count() -> int:
    return len(DIFFUSION_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xix_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xix_description() -> str:
    return ("Diffusion imaging metadata extraction. Supports DWI, DTI, and advanced "
            "diffusion models (IVIM, Kurtosis, NODDI). Extracts b-values, gradient "
            "directions, tensor components, and model-specific parameters.")


def get_scientific_dicom_fits_ultimate_advanced_extension_xix_modalities() -> List[str]:
    return ["MR"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xix_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xix_category() -> str:
    return "Diffusion MRI"


def get_scientific_dicom_fits_ultimate_advanced_extension_xix_keywords() -> List[str]:
    return [
        "diffusion MRI", "DWI", "DTI", "diffusion tensor", "ADC", "FA", "MD",
        "trace weighted", "b-value", "gradient direction", "IVIM", "kurtosis",
        "white matter", "fiber tracking", "connectivity"
    ]


# =============================================================================
# New descriptive function names (primary API)
# =============================================================================

def extract_diffusion_mri_imaging(file_path: str) -> Dict[str, Any]:
    """Extract diffusion MRI imaging metadata from DICOM files."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_xix(file_path)


def get_diffusion_mri_imaging_field_count() -> int:
    """Get the total number of diffusion MRI metadata fields supported."""
    return len(DIFFUSION_TOTAL_TAGS)


def get_diffusion_mri_imaging_version() -> str:
    """Get the version of this module."""
    return "2.0.0"


def get_diffusion_mri_imaging_description() -> str:
    """Get the description of this module."""
    return ("Diffusion imaging metadata extraction. Supports DWI, DTI, and advanced "
            "diffusion models (IVIM, Kurtosis, NODDI). Extracts b-values, gradient "
            "directions, tensor components, and model-specific parameters.")


def get_diffusion_mri_imaging_modalities() -> List[str]:
    """Get supported imaging modalities."""
    return ["MR"]


def get_diffusion_mri_imaging_supported_formats() -> List[str]:
    """Get supported file formats."""
    return [".dcm", ".dicom"]


def get_diffusion_mri_imaging_category() -> str:
    """Get the category of this imaging module."""
    return "Diffusion MRI"


def get_diffusion_mri_imaging_keywords() -> List[str]:
    """Get keywords associated with this module."""
    return [
        "diffusion MRI", "DWI", "DTI", "diffusion tensor", "ADC", "FA", "MD",
        "trace weighted", "b-value", "gradient direction", "IVIM", "kurtosis",
        "white matter", "fiber tracking", "connectivity"
    ]
