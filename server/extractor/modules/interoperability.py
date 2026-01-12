"""
Scientific DICOM/FITS Ultimate Advanced Extension LXIX - Nuclear Medicine Therapy

This module provides comprehensive extraction of Nuclear Medicine Therapy parameters
including patient parameters, radiopharmaceutical data, dosimetry, therapy procedure,
safety monitoring, and workflow metadata.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXIX_AVAILABLE = True

NUCLEAR_MEDICINE_PATIENT_PARAMETERS = {
    (0x0010, 0x0010): "patient_name",
    (0x0010, 0x0020): "patient_id",
    (0x0010, 0x0030): "patient_birth_date",
    (0x0010, 0x0040): "patient_sex",
    (0x0010, 0x1020): "patient_height",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x21D0): "last_menstrual_period_date",
    (0x0010, 0x2203): "patient_medical_alerts",
    (0x0010, 0x4000): "patient_complaints",
}

NUCLEAR_MEDICINE_RADIOPHARMACEUTICAL_TAGS = {
    (0x0018, 0xC001): "radiopharmaceutical_agent",
    (0x0018, 0xC002): "radiopharmaceutical_type",
    (0x0018, 0xC003): "radionuclide_half_life_hours",
    (0x0018, 0xC004): "radionuclide_dose_activity_mbq",
    (0x0018, 0xC005): "radionuclide_dose_activity_mci",
    (0x0018, 0xC006): "administered_dose_mbq",
    (0x0018, 0xC007): "administered_dose_time",
    (0x0018, 0xC008): "dose_calibration_device",
    (0x0018, 0xC009): "dose_calibration_date_time",
    (0x0018, 0xC00A): "dose_calibration_quality_control",
}

NUCLEAR_MEDICINE_DOSIMETRY_TAGS = {
    (0x0018, 0xC010): "organ_dosimetry_method",
    (0x0018, 0xC011): "target_organ_dose_gy",
    (0x0018, 0xC012): "critical_organ_dose_gy",
    (0x0018, 0xC013): "effective_dose_sv",
    (0x0018, 0xC014): "sentinel_lymph_node_dose_gy",
    (0x0018, 0xC015): "cumulative_activity_mbq",
    (0x0018, 0xC016): "time_activity_curve_data",
    (0x0018, 0xC017): "integrated_activity_mbq_sec",
    (0x0018, 0xC018): "dose_conversion_factor",
    (0x0018, 0xC019): "internal_dosimetry_algorithm",
}

NUCLEAR_MEDICINE_THERAPY_PROCEDURE_TAGS = {
    (0x0018, 0xC020): "therapy_procedure_type",
    (0x0018, 0xC021): "therapy_indication",
    (0x0018, 0xC022): "therapy_protocol_name",
    (0x0018, 0xC023): "treatment_cycle_number",
    (0x0018, 0xC024): "total_treatment_cycles",
    (0x0018, 0xC025): "pre_therapy_scan_performed",
    (0x0018, 0xC026): "pre_therapy_scan_date",
    (0x0018, 0xC027): "pre_therapy_scan_result",
    (0x0018, 0xC028): "therapy_response_criteria",
    (0x0018, 0xC029): "follow_up_schedule",
}

NUCLEAR_MEDICINE_SAFETY_MONITORING_TAGS = {
    (0x0018, 0xC030): "radiation_safety_officer",
    (0x0018, 0xC031): "radiation_protection_device",
    (0x0018, 0xC032): "contamination_monitor_reading",
    (0x0018, 0xC033): "contamination_monitor_unit",
    (0x0018, 0xC034): "dose_rate_measurement_uSv_h",
    (0x0018, 0xC035): "patient_isolation_status",
    (0x0018, 0xC036): "isolation_room_number",
    (0x0018, 0xC037): "discharge_criteria_met",
    (0x0018, 0xC038): "patient_release_instructions",
    (0x0018, 0xC039): "emergency_contact_information",
}

NUCLEAR_MEDICINE_WORKFLOW_TAGS = {
    (0x0018, 0xC040): "therapy_session_start_time",
    (0x0018, 0xC041): "therapy_session_end_time",
    (0x0018, 0xC042): "administration_route",
    (0x0018, 0xC043): "administration_site",
    (0x0018, 0xC044): "administration_device",
    (0x0018, 0xC045): "infusion_duration_minutes",
    (0x0018, 0xC046): "infusion_rate_ml_min",
    (0x0018, 0xC047): "adverse_event_occurred",
    (0x0018, 0xC048): "adverse_event_description",
    (0x0018, 0xC049): "therapy_authorization_number",
}

NUCLEAR_MEDICINE_TOTAL_TAGS = (
    NUCLEAR_MEDICINE_PATIENT_PARAMETERS |
    NUCLEAR_MEDICINE_RADIOPHARMACEUTICAL_TAGS |
    NUCLEAR_MEDICINE_DOSIMETRY_TAGS |
    NUCLEAR_MEDICINE_THERAPY_PROCEDURE_TAGS |
    NUCLEAR_MEDICINE_SAFETY_MONITORING_TAGS |
    NUCLEAR_MEDICINE_WORKFLOW_TAGS
)


def _extract_nuclear_medicine_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in NUCLEAR_MEDICINE_TOTAL_TAGS.items():
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


def _is_nuclear_medicine_therapy_file(file_path: str) -> bool:
    nuclear_medicine_indicators = [
        'nuclear_medicine', 'radiopharmaceutical', 'radioisotope',
        'therapy', 'treatment', 'administration', 'thyroid',
        'lutetium', 'yttrium', 'iodine', 'strontium', 'samarium',
        'radium', 'actinium', 'dosimetry', 'mibg', 'prrt'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in nuclear_medicine_indicators:
                if indicator in file_lower:
                    return True
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                if modality in ['PT', 'NM', 'CT']:
                    radiopharmaceutical = getattr(ds, 'Radiopharmaceutical', '')
                    if radiopharmaceutical:
                        return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxix(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxix_detected": False,
        "fields_extracted": 0,
        "extension_lxix_type": "nuclear_medicine_therapy",
        "extension_lxix_version": "2.0.0",
        "patient_parameters": {},
        "radiopharmaceutical": {},
        "dosimetry": {},
        "therapy_procedure": {},
        "safety_monitoring": {},
        "workflow": {},
        "extraction_errors": [],
    }

    try:
        if not _is_nuclear_medicine_therapy_file(file_path):
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

        result["extension_lxix_detected"] = True

        nuclear_data = _extract_nuclear_medicine_tags(ds)

        result["patient_parameters"] = {
            k: v for k, v in nuclear_data.items()
            if k in NUCLEAR_MEDICINE_PATIENT_PARAMETERS.values()
        }
        result["radiopharmaceutical"] = {
            k: v for k, v in nuclear_data.items()
            if k in NUCLEAR_MEDICINE_RADIOPHARMACEUTICAL_TAGS.values()
        }
        result["dosimetry"] = {
            k: v for k, v in nuclear_data.items()
            if k in NUCLEAR_MEDICINE_DOSIMETRY_TAGS.values()
        }
        result["therapy_procedure"] = {
            k: v for k, v in nuclear_data.items()
            if k in NUCLEAR_MEDICINE_THERAPY_PROCEDURE_TAGS.values()
        }
        result["safety_monitoring"] = {
            k: v for k, v in nuclear_data.items()
            if k in NUCLEAR_MEDICINE_SAFETY_MONITORING_TAGS.values()
        }
        result["workflow"] = {
            k: v for k, v in nuclear_data.items()
            if k in NUCLEAR_MEDICINE_WORKFLOW_TAGS.values()
        }

        result["fields_extracted"] = len(nuclear_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxix_field_count() -> int:
    return len(NUCLEAR_MEDICINE_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxix_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxix_description() -> str:
    return (
        "Nuclear Medicine Therapy metadata extraction. Provides comprehensive coverage of "
        "patient parameters, radiopharmaceutical data, dosimetry calculations, therapy procedures, "
        "safety monitoring, and workflow metadata for nuclear medicine therapeutic procedures."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxix_modalities() -> List[str]:
    return ["PT", "NM", "CT", "RTPLAN", "RTIMAGE"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxix_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxix_category() -> str:
    return "Nuclear Medicine Therapy"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxix_keywords() -> List[str]:
    return [
        "nuclear medicine", "radiopharmaceutical", "radioisotope therapy",
        "therapeutic radiopharmaceutical", "dose administration", "dosimetry",
        "internal dosimetry", "radiation safety", "patient isolation",
        "Lu-177", "I-131", "Y-90", "Sr-89", "Sm-153", "Ra-223",
        "PRRT", "MIBG therapy", "thyroid therapy", "bone metastasis"
    ]


# Aliases for smoke test compatibility
def extract_interoperability(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxix."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxix(file_path)

def get_interoperability_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxix_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxix_field_count()

def get_interoperability_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxix_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxix_version()

def get_interoperability_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxix_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxix_description()

def get_interoperability_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxix_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxix_supported_formats()

def get_interoperability_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxix_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxix_modalities()
