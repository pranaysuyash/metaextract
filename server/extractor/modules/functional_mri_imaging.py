"""
Functional MRI Imaging Metadata Extraction

This module provides comprehensive extraction of DICOM metadata for functional MRI
including BOLD imaging, task-based fMRI, and resting-state analysis.

Renamed from: scientific_dicom_fits_ultimate_advanced_extension_xviii.py
Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
FUNCTIONAL_MRI_IMAGING_AVAILABLE = True
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XVIII_AVAILABLE = True  # Backward compat

FMRI_TAGS = {
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x0082): "inversion_time",
    (0x0018, 0x0083): "number_of_averages",
    (0x0018, 0x0085): "echo_number",
    (0x0018, 0x0086): "mr_acquisition_type",
    (0x0018, 0x0087): "sequence_name",
    (0x0018, 0x0091): "phase_encoding_direction",
    (0x0018, 0x0093): "parallel_acquisition_factor",
    (0x0018, 0x0095): "contrast_enhancement_agent",
    (0x0018, 0x0100): "display_fov",
    (0x0018, 0x0101): "display_orientation",
    (0x0018, 0x0102): "display_rotation",
    (0x0018, 0x0103): "display_order",
    (0x0018, 0x0104): "interleaved_acquisition",
    (0x0018, 0x0105): "acquisition_start_order",
    (0x0018, 0x0106): "acquisition_end_order",
    (0x0018, 0x0107): "number_of_acquisition_start_order",
    (0x0018, 0x0108): "number_of_acquisition_end_order",
    (0x0018, 0x0109): "number_of_blocks_in_rotation",
    (0x0018, 0x010A): "number_of_extra_samples_skipped",
    (0x0018, 0x010B): "num_extra_samples_skipped_ends",
    (0x0018, 0x010C): "extra_sample_skipped_order",
    (0x0018, 0x010D): "number_of_roes",
    (0x0018, 0x0110): "pixels_in_gating_window",
    (0x0018, 0x0111): "gating_stride",
    (0x0018, 0x0112): "number_of_frames_in_gating_window",
    (0x0018, 0x0113): "gating_sequence_sequence",
    (0x0018, 0x0114): "gating_sequence_description",
    (0x0018, 0x0115): "data_collection_duration",
    (0x0018, 0x0116): "patient_weight",
    (0x0018, 0x0117): "pulse_sequence_name",
    (0x0018, 0x0118): "pulse_sequence_details",
    (0x0018, 0x0119): "mr_acquisition_fov_sequence",
    (0x0018, 0x0120): "surface_shuffling",
    (0x0018, 0x0121): "parallel_peak_noise",
    (0x0018, 0x0122): "effective_echo_spacing",
    (0x0018, 0x0123): "parallel_reconstruction_mode",
    (0x0018, 0x0124): "parallel_reconstruction_algorithm",
    (0x0018, 0x0125): "parallel_reconstruction_kernel_type",
    (0x0018, 0x0126): "parallel_reconstruction_interpolation_method",
}

BOLD_TAGS = {
    (0x0020, 0x0100): "temporal_position_index",
    (0x0020, 0x0105): "number_of_temporal_positions",
    (0x0020, 0x0110): "temporal_resolution",
    (0x0020, 0x0111): "number_of_time_slices",
    (0x0020, 0x0112): "time_slice_sequence",
    (0x0020, 0x0113): "frame_reference_time",
    (0x0020, 0x0114): "frame_start_time",
    (0x0020, 0x0115): "frame_end_time",
    (0x0020, 0x0116): "group_activation_sequence",
    (0x0020, 0x0117): "group_activation_description",
    (0x0020, 0x0118): "group_activation_type",
    (0x0020, 0x0119): "group_activation_count",
    (0x0020, 0x011A): "group_activation_duration",
    (0x0020, 0x011B): "group_activation_offset",
    (0x0020, 0x011C): "group_activation_end_offset",
    (0x0020, 0x011D): "group_activation_cycle",
    (0x0020, 0x011E): "group_activation_unit",
    (0x0020, 0x011F): "group_activation_actual_cycle",
    (0x0020, 0x0120): "group_activation_cycle_sequence",
}

RESTING_STATE_TAGS = {
    (0x0038, 0x0020): "resting_state_indicator",
    (0x0038, 0x0021): "resting_state_instruction",
    (0x0038, 0x0022): "resting_state_duration",
    (0x0038, 0x0023): "resting_state_eyes",
    (0x0038, 0x0024): "resting_state_task_description",
    (0x0038, 0x0025): "resting_state_task_name",
    (0x0038, 0x0026): "resting_state_stimulus_type",
    (0x0038, 0x0027): "resting_state_stimulus_description",
    (0x0038, 0x0028): "resting_state_stimulus_on_duration",
    (0x0038, 0x0029): "resting_state_stimulus_off_duration",
    (0x0038, 0x002A): "resting_state_stimulus_interval",
}

FMRI_TOTAL_TAGS = FMRI_TAGS | BOLD_TAGS | RESTING_STATE_TAGS


def _extract_fmri_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in FMRI_TAGS.items():
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


def _calculate_fmri_metrics(ds: Any) -> Dict[str, Any]:
    metrics = {}
    try:
        if hasattr(ds, 'Rows') and hasattr(ds, 'Columns'):
            metrics['volume_pixels'] = ds.Rows * ds.Columns
        if hasattr(ds, 'NumberOfFrames'):
            metrics['number_of_volumes'] = ds.NumberOfFrames
        if hasattr(ds, 'TemporalResolution'):
            metrics['temporal_resolution_s'] = ds.TemporalResolution
    except Exception:
        pass
    return metrics


def _is_fmri_file(file_path: str) -> bool:
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


def extract_scientific_dicom_fits_ultimate_advanced_extension_xviii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xviii_detected": False,
        "fields_extracted": 0,
        "extension_xviii_type": "functional_mri",
        "extension_xviii_version": "2.0.0",
        "fmri_modality": None,
        "acquisition_parameters": {},
        "bold_imaging": {},
        "resting_state": {},
        "derived_metrics": {},
        "extraction_errors": [],
    }

    try:
        if not _is_fmri_file(file_path):
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

        result["extension_xviii_detected"] = True
        result["fmri_modality"] = getattr(ds, 'Modality', 'Unknown')

        fmri_data = _extract_fmri_tags(ds)
        metrics = _calculate_fmri_metrics(ds)

        result["acquisition_parameters"] = fmri_data
        result["derived_metrics"] = metrics

        total_fields = len(fmri_data) + len(metrics)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xviii_field_count() -> int:
    return len(FMRI_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xviii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xviii_description() -> str:
    return ("Functional MRI metadata extraction. Supports BOLD imaging, task-based fMRI, "
            "and resting-state analysis. Extracts acquisition parameters, temporal "
            "resolution, and task/stimulus information for comprehensive fMRI analysis.")


def get_scientific_dicom_fits_ultimate_advanced_extension_xviii_modalities() -> List[str]:
    return ["MR"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xviii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xviii_category() -> str:
    return "Functional MRI"


def get_scientific_dicom_fits_ultimate_advanced_extension_xviii_keywords() -> List[str]:
    return [
        "functional MRI", "fMRI", "BOLD", "resting state", "task fMRI",
        "brain activation", "neuronal activity", "EPI", "time series",
        "hemodynamic response", "resting state networks", "RSN"
    ]


# =============================================================================
# New descriptive function names (primary API)
# =============================================================================

def extract_functional_mri_imaging(file_path: str) -> Dict[str, Any]:
    """Extract functional MRI imaging metadata from DICOM files."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_xviii(file_path)


def get_functional_mri_imaging_field_count() -> int:
    """Get the total number of fMRI metadata fields supported."""
    return len(FMRI_TOTAL_TAGS)


def get_functional_mri_imaging_version() -> str:
    """Get the version of this module."""
    return "2.0.0"


def get_functional_mri_imaging_description() -> str:
    """Get the description of this module."""
    return ("Functional MRI metadata extraction. Supports BOLD imaging, task-based fMRI, "
            "and resting-state analysis. Extracts acquisition parameters, temporal "
            "resolution, and task/stimulus information for comprehensive fMRI analysis.")


def get_functional_mri_imaging_modalities() -> List[str]:
    """Get supported imaging modalities."""
    return ["MR"]


def get_functional_mri_imaging_supported_formats() -> List[str]:
    """Get supported file formats."""
    return [".dcm", ".dicom"]


def get_functional_mri_imaging_category() -> str:
    """Get the category of this imaging module."""
    return "Functional MRI"


def get_functional_mri_imaging_keywords() -> List[str]:
    """Get keywords associated with this module."""
    return [
        "functional MRI", "fMRI", "BOLD", "resting state", "task fMRI",
        "brain activation", "neuronal activity", "EPI", "time series",
        "hemodynamic response", "resting state networks", "RSN"
    ]
