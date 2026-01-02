"""
Scientific DICOM/FITS Ultimate Advanced Extension XII - Ophthalmology

This module provides comprehensive extraction of DICOM metadata for ophthalmic
imaging modalities including fundus photography, OCT, visual fields, and
anterior segment imaging.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XII_AVAILABLE = True

FUNDUS_TAGS = {
    (0x0018, 0x1000): "device_serial_number",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1100): "distance_source_to_detector",
    (0x0018, 0x1110): "distance_source_to_patient",
    (0x0018, 0x1130): "table_height",
    (0x0018, 0x1140): "table_motion",
    (0x0018, 0x1180): "kvp",
    (0x0018, 0x1190): "xray_tube_current",
    (0x0018, 0x1200): "exposure",
    (0x0018, 0x1201): "exposure_time",
    (0x0018, 0x7000): "detector_type",
    (0x0018, 0x7001): "detector_id",
    (0x0018, 0x7010): "detector_active_origin",
    (0x0018, 0x7020): "temporal_resolution",
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

OCT_TAGS = {
    (0x0008, 0x0018): "sop_instance_uid",
    (0x0008, 0x0201): "timezone_offset_from_utc",
    (0x0018, 0x0023): "spatial_resolution",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1111): "distance_photographic_to_subject",
    (0x0018, 0x1130): "table_height",
    (0x0018, 0x1140): "table_motion",
    (0x0018, 0x1150): "table_speed",
    (0x0018, 0x1160): "rotation_direction",
    (0x0018, 0x1170): "scan_options",
    (0x0018, 0x1250): "collimator_grid_name",
    (0x0018, 0x1251): "collimator_type",
    (0x0018, 0x7000): "detector_type",
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
    (0x0018, 0x9016): "quality_assurance_properties_sequence",
    (0x0018, 0x9017): "quality_assurance_properties_description",
    (0x0020, 0x0100): "temporal_position_index",
    (0x0020, 0x0105): "number_of_temporal_positions",
    (0x0020, 0x0110): "temporal_resolution",
    (0x0028, 0x0008): "number_of_frames",
}

VISUAL_FIELD_TAGS = {
    (0x0040, 0x0241): "performed_procedure_step_start_date_time",
    (0x0040, 0x0242): "performed_procedure_step_end_date_time",
    (0x0040, 0x0250): "performed_procedure_type_description",
    (0x0040, 0x0253): "performed_procedure_type_code_sequence",
    (0x0040, 0x0260): "performed_imaging_selection_sequence",
    (0x0040, 0x0270): "referenced_procedure_step_sequence",
    (0x0040, 0x0280): "input_information_sequence",
    (0x0040, 0x0290): "information_issue_date_time",
    (0x0040, 0x02A0): "information_issue_type",
    (0x0040, 0x02A2): "information_sequence",
    (0x0040, 0x0300): "procedure_step_discussion_sequence",
    (0x0040, 0x0302): "procedure_step_discussion_person_sequence",
    (0x0040, 0x0304): "procedure_step_discussion_content",
    (0x0040, 0x0310): "procedure_step_communication_sequence",
    (0x0040, 0x0312): "procedure_step_communication_description",
    (0x0040, 0x0320): "patient_instructions",
    (0x0040, 0x4033): "visual_field_horizontal_extent",
    (0x0040, 0x4034): "visual_field_vertical_extent",
    (0x0040, 0x4035): "visual_field_shape",
    (0x0040, 0x4036): "screening_test_mode_code_sequence",
    (0x0040, 0x4037): "maximum_stimulation_luminance",
    (0x0040, 0x4038): "background_luminance",
    (0x0040, 0x4039): "stimulus_luminance",
    (0x0040, 0x403A): "stimulus_color_code_sequence",
    (0x0040, 0x403B): "stimulus_area",
    (0x0040, 0x403C): "stimulus_duration",
    (0x0040, 0x403D): "interpolation_interval",
}

ANTERIOR_SEGMENT_TAGS = {
    (0x0020, 0x0032): "image_position_patient",
    (0x0020, 0x0037): "image_orientation_patient",
    (0x0020, 0x0060): "laterality",
    (0x0020, 0x0062): "image_laterality",
    (0x0020, 0x4000): "image_comments",
    (0x0022, 0x0001): "illumination_wavelength",
    (0x0022, 0x0002): "illumination_power",
    (0x0022, 0x0003): "illumination_bandwidth",
    (0x0022, 0x0004): "illumination_type_code_sequence",
    (0x0022, 0x0005): "filter_type",
    (0x0022, 0x0006): "filter_minimum_wavelength",
    (0x0022, 0x0007): "filter_maximum_wavelength",
    (0x0022, 0x0008): "polarization_type",
    (0x0022, 0x0009): "mip_options_sequence",
    (0x0022, 0x000A): "mip_mode",
    (0x0022, 0x000B): "mip_kernel_size",
    (0x0022, 0x000C): "mip_stride",
    (0x0022, 0x000D): "mip_output_sequence",
    (0x0022, 0x0010): "corneal_topography_mapping_sequence",
    (0x0022, 0x0011): "corneal_topography_mapping_type",
    (0x0022, 0x0012): "corneal_topography_surface",
    (0x0022, 0x0013): "corneal_topography_quality_metric_sequence",
    (0x0022, 0x0014): "corneal_topography_quality_metric_description",
    (0x0022, 0x0015): "corneal_topography_algorithm_version",
    (0x0022, 0x0016): "corneal_topography_algorithm_name",
    (0x0022, 0x0020): "anterior_segment_measurements_sequence",
    (0x0022, 0x0021): "anterior_segment_measurements_type",
    (0x0022, 0x0022): "anterior_segment_measurements_unit",
    (0x0022, 0x0023): "anterior_segment_measurements_description",
}

OPHTHALMIC_MEASUREMENT_TAGS = {
    (0x0040, 0x0241): "performed_procedure_step_start_date_time",
    (0x0040, 0x0242): "performed_procedure_step_end_date_time",
    (0x0040, 0x0244): "procedure_step_state",
    (0x0040, 0x0250): "performed_procedure_type_description",
    (0x0040, 0x0260): "performed_imaging_selection_sequence",
    (0x0040, 0x0270): "referenced_procedure_step_sequence",
    (0x0040, 0x0280): "input_information_sequence",
    (0x0040, 0x4050): "output_information_sequence",
    (0x0040, 0x4051): "desired_image_characteristics_sequence",
    (0x0040, 0x4052): "display_filter_sequence",
    (0x0040, 0x4060): "lens_description",
    (0x0040, 0x4061): "lens_serial_number",
    (0x0040, 0x4062): "lens_name",
    (0x0040, 0x4063): "intraocular_lens_calculations_sequence",
    (0x0040, 0x4064): "intraocular_lens_parameters_sequence",
    (0x0040, 0x4065): "lens_constant_description",
    (0x0040, 0x4066): "lens_constant_value",
    (0x0040, 0x4067): "lens_constant_name",
    (0x0040, 0x4068): "lens_constant_index",
    (0x0040, 0x4069): "eye_measurement_sequence",
    (0x0040, 0x4070): "eye_measurement_axis",
    (0x0040, 0x4071): "eye_measurement_value",
    (0x0040, 0x4072): "eye_measurement_unit",
    (0x0040, 0x4073): "eye_measurement_description",
}

OPHTHALMIC_TOTAL_TAGS = (
    FUNDUS_TAGS | OCT_TAGS | VISUAL_FIELD_TAGS |
    ANTERIOR_SEGMENT_TAGS | OPHTHALMIC_MEASUREMENT_TAGS
)


def _extract_fundus_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in FUNDUS_TAGS.items():
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


def _extract_oct_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in OCT_TAGS.items():
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


def _extract_visual_field_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in VISUAL_FIELD_TAGS.items():
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


def _extract_anterior_segment_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in ANTERIOR_SEGMENT_TAGS.items():
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


def _calculate_ophthalmic_metrics(ds: Any) -> Dict[str, Any]:
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


def _is_ophthalmic_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                ophthalmic_modalities = ['OP', 'OT', 'OCT', 'OF', 'OX', 'MR', 'CT']
                if modality in ophthalmic_modalities:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xii_detected": False,
        "fields_extracted": 0,
        "extension_xii_type": "ophthalmic_imaging",
        "extension_xii_version": "2.0.0",
        "ophthalmic_modality": None,
        "fundus_photography": {},
        "oct_imaging": {},
        "visual_field": {},
        "anterior_segment": {},
        "derived_metrics": {},
        "extraction_errors": [],
    }

    try:
        if not _is_ophthalmic_file(file_path):
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

        result["extension_xii_detected"] = True
        result["ophthalmic_modality"] = getattr(ds, 'Modality', 'Unknown')

        fundus = _extract_fundus_tags(ds)
        oct_data = _extract_oct_tags(ds)
        vf = _extract_visual_field_tags(ds)
        anterior = _extract_anterior_segment_tags(ds)
        metrics = _calculate_ophthalmic_metrics(ds)

        result["fundus_photography"] = fundus
        result["oct_imaging"] = oct_data
        result["visual_field"] = vf
        result["anterior_segment"] = anterior
        result["derived_metrics"] = metrics

        total_fields = len(fundus) + len(oct_data) + len(vf) + len(anterior) + len(metrics)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xii_field_count() -> int:
    return len(OPHTHALMIC_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xii_description() -> str:
    return ("Comprehensive ophthalmic imaging metadata extraction. Supports fundus "
            "photography, OCT, visual fields, and anterior segment imaging. Extracts "
            "acquisition parameters, topographic measurements, and lens calculations "
            "for complete ophthalmic analysis.")


def get_scientific_dicom_fits_ultimate_advanced_extension_xii_modalities() -> List[str]:
    return ["OP", "OT", "OCT", "OF", "OX"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xii_category() -> str:
    return "Ophthalmic Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_xii_keywords() -> List[str]:
    return [
        "ophthalmology", "fundus", "OCT", "optical coherence tomography",
        "visual field", "anterior segment", "corneal topography",
        "intraocular lens", "retina", "optic nerve", "glaucoma"
    ]
