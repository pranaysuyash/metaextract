"""
Scientific DICOM/FITS Ultimate Advanced Extension LIX - Industrial Imaging

This module provides comprehensive extraction of Industrial Imaging parameters
including non-destructive testing, materials science imaging, aerospace inspection,
manufacturing quality control, and failure analysis.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LIX_AVAILABLE = True

INDUSTRIAL_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "component_id",
    (0x0010, 0x1020): "component_part_number",
    (0x0010, 0x1030): "component_serial_number",
    (0x0010, 0x21B0): "additional_part_history",
    (0x0010, 0x2203): "manufacturer_name",
    (0x0010, 0x2204): "model_number",
    (0x0010, 0x2205): "batch_number",
    (0x0010, 0x2206): "heat_number",
    (0x0010, 0x2207): "lot_number",
    (0x0010, 0x2208): "date_of_manufacture",
    (0x0010, 0x2209): "inspection_date",
    (0x0010, 0x2210): "inspection_location",
    (0x0010, 0x2211): "inspection_standard",
    (0x0010, 0x2212): "acceptance_criteria",
    (0x0010, 0x2213): "material_type",
    (0x0010, 0x2214): "material_grade",
    (0x0010, 0x2215): "material_specification",
    (0x0010, 0x2216): "process_specification",
    (0x0010, 0x2217): "component_weight_kg",
    (0x0010, 0x2218): "component_dimensions",
    (0x0010, 0x2219): "surface_condition",
    (0x0010, 0x2220): "coating_type",
    (0x0010, 0x2221): "coating_thickness",
    (0x0010, 0x2222): "operating_temperature_c",
    (0x0010, 0x2223): "operating_pressure_mpa",
    (0x0010, 0x2224): "cycle_count",
    (0x0010, 0x2225): "service_hours",
    (0x0010, 0x2226): "environment_type",
    (0x0010, 0x2227): "exposure_history",
    (0x0010, 0x2228): "maintenance_history",
    (0x0010, 0x2229): "repair_history",
    (0x0010, 0x2230): "modification_history",
}

NON_DESTRUCTIVE_TESTING_TAGS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xB001): "ndt_method_type",
    (0x0018, 0xB002): "radiography_type",
    (0x0018, 0xB003): "xray_energy_kev",
    (0x0018, 0xB004): "xray_current_ma",
    (0x0018, 0xB005): "exposure_time_s",
    (0x0018, 0xB006): "source_to_object_distance_mm",
    (0x0018, 0xB007): "film_type",
    (0x0018, 0xB008): "film_density",
    (0x0018, 0xB009): "geometric_unsharpness",
    (0x0018, 0xB010): "sensitivity_level",
    (0x0018, 0xB011): "wire_penetrameter_number",
    (0x0018, 0xB012): "hole_penetrameter_size",
    (0x0018, 0xB013): "image_quality_indicator",
    (0x0018, 0xB014): "digital_detector_type",
    (0x0018, 0xB015): "detector_pixel_size",
    (0x0018, 0xB016): "spatial_resolution_lp_mm",
    (0x0018, 0xB017): "contrast_sensitivity",
    (0x0018, 0xB018): "signal_to_noise_ratio",
    (0x0018, 0xB019): "dynamic_range",
    (0x0018, 0xB020): "ultrasonic_frequency_mhz",
    (0x0018, 0xB021): "ultrasonic_probe_type",
    (0x0018, 0xB022): "ultrasonic_probe_angle",
    (0x0018, 0xB023): "couplant_type",
    (0x0018, 0xB024): "scan_type",
    (0x0018, 0xB025): "scan_speed_mm_s",
    (0x0018, 0xB026): "pulse_repetition_frequency",
    (0x0018, 0xB027): "gain_db",
    (0x0018, 0xB028): "time_corrected_gain",
    (0x0018, 0xB029): "rectification_type",
    (0x0018, 0xB030): "filter_type",
    (0x0018, 0xB031): "eddy_current_frequency_hz",
    (0x0018, 0xB032): "eddy_current_probe_type",
    (0x0018, 0xB033): "lift_off_compensation",
    (0x0018, 0xB034): "phase_analysis_enable",
    (0x0018, 0xB035): "magnetic_particle_type",
    (0x0018, 0xB036): "magnetization_method",
    (0x0018, 0xB037): "magnetic_field_strength",
    (0x0018, 0xB038): "penetrant_type",
    (0x0018, 0xB039): "penetrant_dwell_time",
    (0x0018, 0xB040): "developer_time",
}

MATERIALS_SCIENCE_TAGS = {
    (0x0020, 0x0010): "series_number",
    (0x0020, 0x0011): "instance_number",
    (0x0020, 0x0032): "image_position_patient",
    (0x0020, 0x0037): "image_orientation_patient",
    (0x0020, 0x0050): "location",
    (0x0020, 0x0100): "temporal_position_identifier",
    (0x0020, 0x0105): "number_of_temporal_positions",
    (0x0020, 0x0200): "temporal_reconstruction_type",
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
    (0x0018, 0xC001): "materials_analysis_type",
    (0x0018, 0xC002): "microstructure_phase",
    (0x0018, 0xC003): "grain_size_microns",
    (0x0018, 0xC004): "grain_size_distribution",
    (0x0018, 0xC005): "phase_fraction_percentage",
    (0x0018, 0xC006): "precipitate_size",
    (0x0018, 0xC007): "precipitate_distribution",
    (0x0018, 0xC008): "void_content",
    (0x0018, 0xC009): "void_size_distribution",
    (0x0018, 0xC010): "crack_length_mm",
    (0x0018, 0xC011): "crack_width_microns",
    (0x0018, 0xC012): "crack_density",
    (0x0018, 0xC013): "crack_orientation",
    (0x0018, 0xC014): "porosity_percentage",
    (0x0018, 0xC015): "inclusion_content",
    (0x0018, 0xC016): "inclusion_type",
    (0x0018, 0xC017): "inclusion_size",
    (0x0018, 0xC018): "segregation_zones",
    (0x0018, 0xC019): "texture_orientation",
    (0x0018, 0xC020): "residual_stress_mpa",
    (0x0018, 0xC021): "hardness_value",
    (0x0018, 0xC022): "microhardness_hv",
    (0x0018, 0xC023): "tensile_strength_mpa",
    (0x0018, 0xC024): "yield_strength_mpa",
    (0x0018, 0xC025): "elongation_percentage",
    (0x0018, 0xC026): "fracture_toughness_mpa_sqrtm",
    (0x0018, 0xC027): "fatigue_life_cycles",
    (0x0018, 0xC028): "corrosion_rate_mm_year",
    (0x0018, 0xC029): "oxidation_layer_thickness",
    (0x0018, 0xC030): "coating_adhesion_strength",
}

QUALITY_CONTROL_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xD001): "qc_inspection_type",
    (0x0018, 0xD002): "inspection_level",
    (0x0018, 0xD003): "sampling_plan",
    (0x0018, 0xD004): "acceptance_number",
    (0x0018, 0xD005): "rejection_number",
    (0x0018, 0xD006): "aql_level",
    (0x0018, 0xD007): "defect_classification",
    (0x0018, 0xD008): "critical_defect",
    (0x0018, 0xD009): "major_defect",
    (0x0018, 0xD010): "minor_defect",
    (0x0018, 0xD011): "defect_count",
    (0x0018, 0xD012): "defect_location",
    (0x0018, 0xD013): "defect_size",
    (0x0018, 0xD014): "defect_depth",
    (0x0018, 0xD015): "verification_status",
    (0x0018, 0xD016): "disposition_decision",
    (0x0018, 0xD017): "accept_indicator",
    (0x0018, 0xD018): "reject_indicator",
    (0x0018, 0xD019): "rework_indicator",
    (0x0018, 0xD020): "concession_indicator",
    (0x0018, 0xD021): "certificate_of_conformance",
    (0x0018, 0xD022): "test_report_number",
    (0x0018, 0xD023): "calibration_status",
    (0x0018, 0xD024): "calibration_due_date",
    (0x0018, 0xD025): "equipment_id",
    (0x0018, 0xD026): "operator_id",
    (0x0018, 0xD027): "supervisor_id",
    (0x0018, 0xD028): "digital_signature",
    (0x0018, 0xD029): "audit_trail",
    (0x0018, 0xD030): "data_integrity_check",
}

FAILURE_ANALYSIS_TAGS = {
    (0x0008, 0x0060): "modality",
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0020): "sequence_name",
    (0x0018, 0xE001): "failure_mode",
    (0x0018, 0xE002): "failure_mechanism",
    (0x0018, 0xE003): "failure_cause",
    (0x0018, 0xE004): "failure_origin",
    (0x0018, 0xE005): "crack_initiation_site",
    (0x0018, 0xE006): "crack_propagation_direction",
    (0x0018, 0xE007): "fracture_surface_features",
    (0x0018, 0xE008): "beach_mark_appearance",
    (0x0018, 0xE009): "striation_spacing",
    (0x0018, 0xE010): "overload_fracture",
    (0x0018, 0xE011): "fatigue_fracture",
    (0x0018, 0xE012): "stress_corrosion_crack",
    (0x0018, 0xE013): "hydrogen_embrittlement",
    (0x0018, 0xE014): "creep_damage",
    (0x0018, 0xE015): "thermal_fatigue",
    (0x0018, 0xE016): "corrosion_type",
    (0x0018, 0xE017): "wear_pattern",
    (0x0018, 0xE018): "erosion_damage",
    (0x0018, 0xE019): "microbiologically_influenced_corrosion",
    (0x0018, 0xE020): "intergranular_attack",
    (0x0018, 0xE021): "transgranular_attack",
    (0x0018, 0xE022): "pitting_corrosion",
    (0x0018, 0xE023): "crevice_corrosion",
    (0x0018, 0xE024): "galvanic_corrosion",
    (0x0018, 0xE025): "embrittlement_mechanism",
    (0x0018, 0xE026): "temperature_exposure",
    (0x0018, 0xE027): "chemical_exposure",
    (0x0018, 0xE028): "mechanical_stress",
    (0x0018, 0xE029): "residual_stress_contribution",
    (0x0018, 0xE030): "design_deficiency",
    (0x0018, 0xE031): "manufacturing_defect",
    (0x0018, 0xE032): "material_selection_error",
    (0x0018, 0xE033): "service_misuse",
    (0x0018, 0xE034): "maintenance_deficiency",
    (0x0018, 0xE035): "recommendation_status",
}

TOTAL_TAGS_LIX = (
    INDUSTRIAL_PATIENT_PARAMETERS | 
    NON_DESTRUCTIVE_TESTING_TAGS | 
    MATERIALS_SCIENCE_TAGS | 
    QUALITY_CONTROL_TAGS | 
    FAILURE_ANALYSIS_TAGS
)


def _extract_tags_lix(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LIX.items():
        try:
            if hasattr(ds, '__getitem__'):
                elem = ds.get(tag)
                if elem is not None:
                    try:
                        value = elem.value
                        if isinstance(value, bytes):
                            value = value.decode('utf-8', errors='replace')
                        extracted[name] = value
                    except Exception:
                        extracted[name] = str(elem)
        except Exception:
            pass
    return extracted


def _is_industrial_imaging_file(file_path: str) -> bool:
    industrial_indicators = [
        'industrial', 'ndt', 'non_destructive', 'nondestructive', 'radiography',
        'ultrasonic', 'eddy_current', 'magnetic_particle', 'penetrant',
        'materials_science', 'quality_control', 'qc_inspection', 'failure_analysis',
        'aerospace', 'manufacturing', 'weld_inspection', 'castings', 'forgings'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in industrial_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lix(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lix_detected": False,
        "fields_extracted": 0,
        "extension_lix_type": "industrial_imaging",
        "extension_lix_version": "2.0.0",
        "industrial_patient_parameters": {},
        "non_destructive_testing": {},
        "materials_science": {},
        "quality_control": {},
        "failure_analysis": {},
        "extraction_errors": [],
    }

    try:
        if not _is_industrial_imaging_file(file_path):
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

        result["extension_lix_detected"] = True

        industrial_data = _extract_tags_lix(ds)

        result["industrial_patient_parameters"] = {
            k: v for k, v in industrial_data.items()
            if k in INDUSTRIAL_PATIENT_PARAMETERS.values()
        }
        result["non_destructive_testing"] = {
            k: v for k, v in industrial_data.items()
            if k in NON_DESTRUCTIVE_TESTING_TAGS.values()
        }
        result["materials_science"] = {
            k: v for k, v in industrial_data.items()
            if k in MATERIALS_SCIENCE_TAGS.values()
        }
        result["quality_control"] = {
            k: v for k, v in industrial_data.items()
            if k in QUALITY_CONTROL_TAGS.values()
        }
        result["failure_analysis"] = {
            k: v for k, v in industrial_data.items()
            if k in FAILURE_ANALYSIS_TAGS.values()
        }

        result["fields_extracted"] = len(industrial_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lix_field_count() -> int:
    return len(TOTAL_TAGS_LIX)


def get_scientific_dicom_fits_ultimate_advanced_extension_lix_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lix_description() -> str:
    return (
        "Industrial Imaging metadata extraction. Provides comprehensive coverage of "
        "non-destructive testing, materials science imaging, aerospace inspection, "
        "manufacturing quality control, and failure analysis for industrial applications."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lix_modalities() -> List[str]:
    return ["CT", "CR", "DR", "XA", "RG", "RF"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lix_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lix_category() -> str:
    return "Industrial Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_lix_keywords() -> List[str]:
    return [
        "industrial imaging", "non-destructive testing", "NDT", "radiography",
        "ultrasonic testing", "eddy current", "magnetic particle", "penetrant testing",
        "materials science", "quality control", "failure analysis", "aerospace inspection",
        "manufacturing", "weld inspection", "castings", "forgings", "materials characterization"
    ]
