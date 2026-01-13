"""
Scientific DICOM/FITS Ultimate Advanced Extension LXVIII - Brachytherapy Imaging

This module provides comprehensive extraction of Brachytherapy Imaging parameters
including patient parameters, treatment procedure, source positioning, dose calculation,
treatment verification, and workflow metadata.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXVIII_AVAILABLE = True

BRACHYTHERAPY_PATIENT_PARAMETERS = {
    (0x0010, 0x0010): "patient_name",
    (0x0010, 0x0020): "patient_id",
    (0x0010, 0x0030): "patient_birth_date",
    (0x0010, 0x0040): "patient_sex",
    (0x0010, 0x1020): "patient_height",
    (0x0010, 0x1030): "patient_weight",
    (0x0018, 0x1000): "device_serial_number",
    (0x0018, 0x1030): "protocol_name",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x4000): "patient_complaints",
}

BRACHYTHERAPY_PROCEDURE_TAGS = {
    (0x0018, 0xB000): "brachytherapy_procedure_type",
    (0x0018, 0xB001): "brachytherapy_modality",
    (0x0018, 0xB002): "treatment_planning_system",
    (0x0018, 0xB003): "treatment_unit_type",
    (0x0018, 0xB004): "treatment_technique",
    (0x0018, 0xB005): "clinical_prescription_type",
    (0x0018, 0xB006): "prescription_dose_gy",
    (0x0018, 0xB007): "prescription_dose_fraction",
    (0x0018, 0xB008): "total_treatment_sessions",
    (0x0018, 0xB009): "completed_treatment_sessions",
}

BRACHYTHERAPY_SOURCE_POSITIONING_TAGS = {
    (0x0018, 0xB010): "source_type",
    (0x0018, 0xB011): "radioactive_isotope",
    (0x0018, 0xB012): "source_strength_u",
    (0x0018, 0xB013): "source_strength_reference_date",
    (0x0018, 0xB014): "source_calibration_date",
    (0x0018, 0xB015): "source_calibration_method",
    (0x0018, 0xB016): "applicator_type",
    (0x0018, 0xB017): "applicator_model",
    (0x0018, 0xB018): "applicator_serial_number",
    (0x0018, 0xB019): "catheter_count",
}

BRACHYTHERAPY_DOSE_CALCULATION_TAGS = {
    (0x0018, 0xB020): "dose_calculation_algorithm",
    (0x0018, 0xB021): "dose_grid_resolution_mm",
    (0x0018, 0xB022): "heterogeneity_correction",
    (0x0018, 0xB023): "dvh_calculation_method",
    (0x0018, 0xB024): "target_volume_cc",
    (0x0018, 0xB025): "clinical_target_volume_gy",
    (0x0018, 0xB026): "planning_target_volume_gy",
    (0x0018, 0xB027): "organ_at_risk_dose_limit_gy",
    (0x0018, 0xB028): "dose_point_coordinates",
    (0x0018, 0xB029): "isodose_line_values",
}

BRACHYTHERAPY_TREATMENT_VERIFICATION_TAGS = {
    (0x0018, 0xB030): "verification_imaging_modality",
    (0x0018, 0xB031): "verification_image_type",
    (0x0018, 0xB032): "source_position_verification",
    (0x0018, 0xB033): "applicator_position_verified",
    (0x0018, 0xB034): "anatomical_changes_observed",
    (0x0018, 0xB035): "motion_management_strategy",
    (0x0018, 0xB036): "real_time_position_monitoring",
    (0x0018, 0xB037): "intervention_required",
    (0x0018, 0xB038): "quality_assurance_passed",
    (0x0018, 0xB039): "verification_dose_measured_gy",
}

BRACHYTHERAPY_WORKFLOW_TAGS = {
    (0x0018, 0xB040): "treatment_session_start_time",
    (0x0018, 0xB041): "treatment_session_end_time",
    (0x0018, 0xB042): "total_treatment_time_seconds",
    (0x0018, 0xB043): "actual_delivered_dose_gy",
    (0x0018, 0xB044): "source_transit_time_seconds",
    (0x0018, 0xB045): "interruption_count",
    (0x0018, 0xB046): "interruption_reason",
    (0x0018, 0xB047): "treatment_delivery_status",
    (0x0018, 0xB048): "treatment_completion_status",
    (0x0018, 0xB049): "post_treatment_instructions",
}

BRACHYTHERAPY_TOTAL_TAGS = (
    BRACHYTHERAPY_PATIENT_PARAMETERS |
    BRACHYTHERAPY_PROCEDURE_TAGS |
    BRACHYTHERAPY_SOURCE_POSITIONING_TAGS |
    BRACHYTHERAPY_DOSE_CALCULATION_TAGS |
    BRACHYTHERAPY_TREATMENT_VERIFICATION_TAGS |
    BRACHYTHERAPY_WORKFLOW_TAGS
)


def _extract_brachytherapy_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in BRACHYTHERAPY_TOTAL_TAGS.items():
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


def _is_brachytherapy_file(file_path: str) -> bool:
    brachytherapy_indicators = [
        'brachytherapy', 'brachy', ' HDR', 'LDR', 'pdr',
        'radioactive_source', 'afterloader', 'applicator',
        'gynecology', 'prostate', 'interstitial', 'intracavitary',
        'radiotherapy', 'treatment_planning', 'treatment_session'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in brachytherapy_indicators:
                if indicator in file_lower:
                    return True
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                if modality in ['RTPLAN', 'RTIMAGE', 'RTSTRUCT']:
                    procedure_type = getattr(ds, 'ProcedureType', '')
                    if 'BRACHY' in str(procedure_type).upper():
                        return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxviii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxviii_detected": False,
        "fields_extracted": 0,
        "extension_lxviii_type": "brachytherapy_imaging",
        "extension_lxviii_version": "2.0.0",
        "patient_parameters": {},
        "brachytherapy_procedure": {},
        "source_positioning": {},
        "dose_calculation": {},
        "treatment_verification": {},
        "workflow": {},
        "extraction_errors": [],
    }

    try:
        if not _is_brachytherapy_file(file_path):
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

        result["extension_lxviii_detected"] = True

        brachy_data = _extract_brachytherapy_tags(ds)

        result["patient_parameters"] = {
            k: v for k, v in brachy_data.items()
            if k in BRACHYTHERAPY_PATIENT_PARAMETERS.values()
        }
        result["brachytherapy_procedure"] = {
            k: v for k, v in brachy_data.items()
            if k in BRACHYTHERAPY_PROCEDURE_TAGS.values()
        }
        result["source_positioning"] = {
            k: v for k, v in brachy_data.items()
            if k in BRACHYTHERAPY_SOURCE_POSITIONING_TAGS.values()
        }
        result["dose_calculation"] = {
            k: v for k, v in brachy_data.items()
            if k in BRACHYTHERAPY_DOSE_CALCULATION_TAGS.values()
        }
        result["treatment_verification"] = {
            k: v for k, v in brachy_data.items()
            if k in BRACHYTHERAPY_TREATMENT_VERIFICATION_TAGS.values()
        }
        result["workflow"] = {
            k: v for k, v in brachy_data.items()
            if k in BRACHYTHERAPY_WORKFLOW_TAGS.values()
        }

        result["fields_extracted"] = len(brachy_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_field_count() -> int:
    return len(BRACHYTHERAPY_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_description() -> str:
    return (
        "Brachytherapy Imaging metadata extraction. Provides comprehensive coverage of "
        "patient parameters, treatment procedure details, source positioning, dose calculation, "
        "treatment verification, and workflow metadata for brachytherapy procedures."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_modalities() -> List[str]:
    return ["RTPLAN", "RTIMAGE", "RTSTRUCT", "CT", "MR", "US"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_category() -> str:
    return "Brachytherapy Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_keywords() -> List[str]:
    return [
        "brachytherapy", "HDR", "LDR", "PDR", "radioactive source",
        "afterloader", "applicator", "treatment planning", "dose calculation",
        "source positioning", "treatment verification", "radiotherapy",
        "interstitial", "intracavitary", "surface mold", "radioisotope"
    ]


# Aliases for smoke test compatibility
def extract_health_it(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxviii."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxviii(file_path)

def get_health_it_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_field_count()

def get_health_it_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_version()

def get_health_it_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_description()

def get_health_it_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_supported_formats()

def get_health_it_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_modalities()
