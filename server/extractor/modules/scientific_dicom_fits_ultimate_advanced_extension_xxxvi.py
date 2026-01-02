"""
Scientific DICOM/FITS Ultimate Advanced Extension XXXVI - Radiation Therapy Simulation

This module provides comprehensive extraction of radiation therapy simulation
parameters including CT simulation, virtual simulation, and treatment planning.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXXVI_AVAILABLE = True

RT_SIMULATION = {
    (0x300A, 0x0001): "rt_plan_geometry",
    (0x300A, 0x0002): "rt_prescription_description",
    (0x300A, 0x0004): "rt_dose_reference_sequence",
    (0x300A, 0x0010): "rt_dose_reference_type",
    (0x300A, 0x0012): "rt_dose_reference_structure_type",
    (0x300A, 0x0014): "rt_dose_reference_precedence",
    (0x300A, 0x0016): "rt_dose_reference_hours_of_covered_time",
    (0x300A, 0x0018): "rt_dose_reference_point_coordinates_sequence",
    (0x300A, 0x001A): "rt_dose_reference_point_name",
    (0x300A, 0x001B): "rt_dose_reference_point_prescription_dose",
    (0x300A, 0x001C): "rt_dose_reference_point_meterset_weight",
    (0x300A, 0x001D): "rt_dose_reference_point_order",
    (0x300A, 0x0020): "rt_dose_reference_structure_type",
    (0x300A, 0x0021): "rt_dose_volume_histogram_sequence",
    (0x300A, 0x0022): "rt_dvh_roi_sequence",
    (0x300A, 0x0024): "rt_dvh_roi_identification",
    (0x300A, 0x0026): "rt_dvh_dose_scaling",
    (0x300A, 0x0028): "rt_dvh_volume_units",
    (0x300A, 0x002A): "rt_dvh_number_of_bins",
    (0x300A, 0x002C): "rt_dvh_data_sequence",
    (0x300A, 0x002E): "rt_dvh_dose_value",
    (0x300A, 0x0030): "rt_dvh_volume_value",
    (0x300A, 0x0040): "rt_beam_sequence",
    (0x300A, 0x0042): "rt_beam_name",
    (0x300A, 0x0044): "rt_beam_description",
    (0x300A, 0x0046): "rt_beam_type",
    (0x300A, 0x0048): "rt_beam_primitive",
    (0x300A, 0x004A): "rt_beam_delivery_instruction_sequence",
    (0x300A, 0x004C): "rt_beam_delivery_instruction",
    (0x300A, 0x004E): "rt_beam_sequence_parameter",
    (0x300A, 0x0050): "rt_beam_radiation_type",
    (0x300A, 0x0054): "rt_beam_energy",
    (0x300A, 0x0056): "rt_beam_energy_unit",
    (0x300A, 0x0058): "rt_beam_delivery_duration",
    (0x300A, 0x005A): "rt_beam_dose",
    (0x300A, 0x005C): "rt_beam_dose_unit",
    (0x300A, 0x0060): "rt_beam_wedge_sequence",
    (0x300A, 0x0062): "rt_beam_wedge_number",
    (0x300A, 0x0064): "rt_beam_wedge_type",
    (0x300A, 0x0066): "rt_beam_wedge_angle",
    (0x300A, 0x0068): "rt_beam_wedge_factor",
    (0x300A, 0x0070): "rt_beam_block_sequence",
    (0x300A, 0x0072): "rt_beam_block_type",
    (0x300A, 0x0074): "rt_beam_block_thickness",
    (0x300A, 0x0076): "rt_beam_block_number_of_points",
    (0x300A, 0x0078): "rt_beam_block_data_sequence",
    (0x300A, 0x007A): "rt_beam_block_data",
    (0x300A, 0x0080): "rt_beam_applicator_sequence",
    (0x300A, 0x0082): "rt_beam_applicator_type",
    (0x300A, 0x0084): "rt_beam_applicator_description",
    (0x300A, 0x0090): "rt_beam_compensator_sequence",
    (0x300A, 0x0092): "rt_beam_compensator_number",
    (0x300A, 0x0094): "rt_beam_compensator_type",
    (0x300A, 0x0096): "rt_beam_compensator_tray",
    (0x300A, 0x0098): "rt_beam_compensator_source_to_surface_distance",
    (0x300A, 0x009A): "rt_beam_compensator_milling_tool_diameter",
    (0x300A, 0x00A0): "rt_beam_bolus_sequence",
    (0x300A, 0x00A2): "rt_beam_bolus_number",
    (0x300A, 0x00A4): "rt_beam_bolus_type",
    (0x300A, 0x00A6): "rt_beam_bolus_description",
    (0x300A, 0x00B0): "rt_beam_modifier_sequence",
    (0x300A, 0x00B2): "rt_beam_modifier_type",
    (0x300A, 0x00B4): "rt_beam_modifier_number",
    (0x300A, 0x00B6): "rt_beam_modifier_description",
    (0x300A, 0x00C0): "rt_treatment_machine_sequence",
    (0x300A, 0x00C2): "rt_treatment_machine_name",
    (0x300A, 0x00C4): "rt_treatment_machine_manufacturer",
    (0x300A, 0x00C6): "rt_treatment_machine_version",
    (0x300A, 0x00D0): "rt_primary_dosimeter_unit",
    (0x300A, 0x00D2): "rt_source_axis_distance",
    (0x300A, 0x00E0): "rt_beam Limiting Device Sequence",
    (0x300A, 0x00E2): "rt_beam_limiting_device_type",
    (0x300A, 0x00E4): "rt_beam_limiting_device_number",
    (0x300A, 0x00E6): "rt_beam_limiting_device_name",
    (0x300A, 0x00E8): "rt_beam_limiting_device_leaves_sequence",
    (0x300A, 0x00EA): "rt_beam_limiting_device_leaf_position",
    (0x300A, 0x00EC): "rt_beam_limiting_device_leaf_width",
}

RT_TREATMENT = {
    (0x300A, 0x0100): "rt_fraction_group_sequence",
    (0x300A, 0x0102): "rt_fraction_group_number",
    (0x300A, 0x0104): "rt_fraction_group_description",
    (0x300A, 0x0108): "rt_number_of_fractions",
    (0x300A, 0x010A): "rt_number_of_beams",
    (0x300A, 0x010C): "rt_number_of_denominators",
    (0x300A, 0x0110): "rt_beam_dose_info_sequence",
    (0x300A, 0x0112): "rt_beam_dose",
    (0x300A, 0x0114): "rt_beam_dose_unit",
    (0x300A, 0x0116): "rt_beam_dose_specification_point",
    (0x300A, 0x0118): "rt_beam_dose_meterset",
    (0x300A, 0x011A): "rt_beam_dose_control_point_sequence",
    (0x300A, 0x011C): "rt_beam_meterset_value",
    (0x300A, 0x0120): "rt_fraction_group_summary_sequence",
    (0x300A, 0x0122): "rt_fraction_group_summary_fraction_number",
    (0x300A, 0x0124): "rt_fraction_group_summary_start_dateTime",
    (0x300A, 0x0126): "rt_fraction_group_summary_end_dateTime",
    (0x300A, 0x0128): "rt_fraction_group_summary_number_of_fractions",
    (0x300A, 0x012A): "rt_fraction_group_summary_number_of_beams",
    (0x300A, 0x012C): "rt_fraction_group_summary_number_of_denominators",
    (0x300A, 0x012E): "rt_fraction_group_summary_measured_dose_sequence",
    (0x300A, 0x0130): "rt_fraction_group_summary_measured_dose_value",
    (0x300A, 0x0132): "rt_fraction_group_summary_measured_dose_unit",
    (0x300A, 0x0140): "rt_tolerance_table_sequence",
    (0x300A, 0x0142): "rt_tolerance_table_number",
    (0x300A, 0x0144): "rt_tolerance_table_description",
    (0x300A, 0x0146): "rt_tolerance_table_器械",
    (0x300A, 0x0148): "rt_tolerance_table_value",
    (0x300A, 0x014A): "rt_tolerance_table_parameter_sequence",
    (0x300A, 0x014C): "rt_tolerance_table_parameter_type",
    (0x300A, 0x014E): "rt_tolerance_table_parameter_value",
}

RT_STRUCTURE_SET = {
    (0x3006, 0x0001): "rt_structure_set_roi_sequence",
    (0x3006, 0x0002): "roi_number",
    (0x3006, 0x0004): "roi_name",
    (0x3006, 0x0006): "roi_description",
    (0x3006, 0x0008): "roi_volume",
    (0x3006, 0x000A): "roi_generation_algorithm_type",
    (0x3006, 0x000C): "roi_generation_algorithm_description",
    (0x3006, 0x000E): "roi_contour_sequence",
    (0x3006, 0x0010): "contour_number",
    (0x3006, 0x0012): "contour_primitive_sequence",
    (0x3006, 0x0014): "contour_geometry_type",
    (0x3006, 0x0016): "contour_description",
    (0x3006, 0x0018): "contour_data_sequence",
    (0x3006, 0x001A): "contour_data",
    (0x3006, 0x0020): "roi_display_color",
    (0x3006, 0x0024): "roi_interpolated_slice_sequence",
    (0x3006, 0x0026): "contour_aperture_level",
    (0x3006, 0x0028): "contour_aperture_value",
    (0x3006, 0x0030): "rt_roi_observations_sequence",
    (0x3006, 0x0032): "observation_number",
    (0x3006, 0x0034): "roi_observation_description",
    (0x3006, 0x0036): "roi_observation_roi_creator",
    (0x3006, 0x0040): "rt_roi_derived_from_roi_sequence",
    (0x3006, 0x0042): "derived_from_roi_number",
    (0x3006, 0x0044): "roi_derived_from_roi_description",
    (0x3006, 0x0050): "rt_referenced_roi_sequence",
    (0x3006, 0x0052): "rt_referenced_roi_number",
    (0x3006, 0x0054): "rt_referenced_roi_modality",
    (0x3006, 0x0056): "rt_referenced_roi_frame_of_reference",
    (0x3006, 0x0058): "rt_referenced_roi_contour_sequence",
    (0x3006, 0x005A): "rt_referenced_contour_number",
    (0x3006, 0x0060): "rt_structure_set_label",
    (0x3006, 0x0062): "rt_structure_set_name",
    (0x3006, 0x0064): "rt_structure_set_description",
    (0x3006, 0x0068): "rt_structure_set_date",
    (0x3006, 0x006A): "rt_structure_set_time",
    (0x3006, 0x006C): "rt_structure_set_creator",
    (0x3006, 0x006E): "rt_structure_set_originator",
}

RT_TOTAL_TAGS = RT_SIMULATION | RT_TREATMENT | RT_STRUCTURE_SET


def _extract_rt_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in RT_TOTAL_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_rt_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                sop_class = getattr(ds, 'SOPClassUID', '')
                if 'RT' in sop_class or 'Radiation' in sop_class:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xxxvi(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xxxvi_detected": False,
        "fields_extracted": 0,
        "extension_xxxvi_type": "radiation_therapy_simulation",
        "extension_xxxvi_version": "2.0.0",
        "rt_simulation": {},
        "rt_treatment": {},
        "rt_structure_set": {},
        "extraction_errors": [],
    }

    try:
        if not _is_rt_file(file_path):
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

        result["extension_xxxvi_detected"] = True

        rt_data = _extract_rt_tags(ds)

        result["rt_simulation"] = {
            k: v for k, v in rt_data.items()
            if k in RT_SIMULATION.values()
        }
        result["rt_treatment"] = {
            k: v for k, v in rt_data.items()
            if k in RT_TREATMENT.values()
        }
        result["rt_structure_set"] = {
            k: v for k, v in rt_data.items()
            if k in RT_STRUCTURE_SET.values()
        }

        result["fields_extracted"] = len(rt_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxvi_field_count() -> int:
    return len(RT_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxvi_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxvi_description() -> str:
    return (
        "Radiation therapy simulation metadata extraction. Provides comprehensive "
        "coverage of RT simulation parameters, treatment planning, beam delivery, "
        "structure set definitions, and dose reference for radiation oncology."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxvi_modalities() -> List[str]:
    return ["RT", "CT", "MR", "PT"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxvi_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxvi_category() -> str:
    return "Radiation Therapy Simulation"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxvi_keywords() -> List[str]:
    return [
        "radiation therapy", "RT", "treatment planning", "IMRT", "VMAT",
        "brachytherapy", "dose calculation", "beam delivery", "structure set"
    ]
