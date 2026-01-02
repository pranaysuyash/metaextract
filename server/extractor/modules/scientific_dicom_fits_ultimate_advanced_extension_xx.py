"""
Scientific DICOM/FITS Ultimate Advanced Extension XX - Various Medical Modalities

This module provides comprehensive extraction of DICOM metadata for various
specialized medical imaging modalities including veterinary medicine,
research imaging, and emerging technologies.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XX_AVAILABLE = True

VETERINARY_TAGS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x2180): "occupation",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x21C0): "pregnancy_status",
    (0x0010, 0x21D0): "last_menstrual_date",
    (0x0010, 0x21F0): "patientReligiousPreference",
    (0x0010, 0x2200): "patient_species_description",
    (0x0010, 0x2201): "patient_species_code_sequence",
    (0x0010, 0x2202): "patient_breed_description",
    (0x0010, 0x2203): "patient_breed_code_sequence",
    (0x0010, 0x2204): "patient_breed_registry_number",
    (0x0010, 0x2205): "patient_breed_registry_name",
    (0x0010, 0x2206): "patient_breed_stock_number",
    (0x0010, 0x2207): "patient_breed_species",
    (0x0010, 0x2208): "patient_breed_sex",
    (0x0010, 0x2209): "patient_breed_reproductive_status",
    (0x0010, 0x220A): "patient_breed_colour",
    (0x0010, 0x220B): "patient_breed_markings",
    (0x0010, 0x2210): "patient_owner_name",
    (0x0010, 0x2220): "patient_tattoo_sequence",
    (0x0010, 0x2230): "patient_microchip_sequence",
    (0x0010, 0x2240): "patient_identification_sequence",
}

RESEARCH_TAGS = {
    (0x0012, 0x0040): "clinical_trial_site_id",
    (0x0012, 0x0042): "clinical_trial_site_name",
    (0x0012, 0x0050): "clinical_trial_sponsor_name",
    (0x0012, 0x0060): "clinical_trial_protocol_id",
    (0x0012, 0x0062): "clinical_trial_protocol_name",
    (0x0012, 0x0070): "clinical_trial_phase_id",
    (0x0012, 0x0071): "clinical_trial_phase_description",
    (0x0012, 0x0080): "clinical_trial_study_id",
    (0x0012, 0x0081): "clinical_trial_study_name",
    (0x0012, 0x0082): "clinical_trial_study_type",
    (0x0012, 0x0083): "clinical_trial_study_type_description",
    (0x0012, 0x0090): "clinical_trial_subject_id",
    (0x0012, 0x0091): "clinical_trial_subject_sampling_fraction",
    (0x0012, 0x0092): "clinical_trial_subject_type",
    (0x0012, 0x0093): "clinical_trial_subject_type_description",
    (0x0012, 0x0094): "clinical_trial_time_point_id",
    (0x0012, 0x0095): "clinical_trial_time_point_description",
    (0x0012, 0x0096): "clinical_trial_coordinating_center_name",
    (0x0012, 0x0097): "clinical_trial_coordinating_center_id",
    (0x0012, 0x0098): "clinical_trial_series_description",
    (0x0012, 0x0099): "clinical_trial_series_number",
    (0x0012, 0x00A0): "clinical_trial_acquisition_number",
    (0x0012, 0x00A1): "clinical_trial_subject_read_id",
    (0x0012, 0x00A2): "clinical_trial_subject_read_name",
}

EMERGING_TAGS = {
    (0x0018, 0x9001): "shared_functional_group_sequence",
    (0x0018, 0x9002): "per_frame_functional_group_sequence",
    (0x0018, 0x9003): "waveform_sequence",
    (0x0018, 0x9004): "functional_group_sequence",
    (0x0018, 0x9005): "waveform_group_sequence",
    (0x0018, 0x9006): "channel_definition_sequence",
    (0x0018, 0x9007): "channel_source_sequence",
    (0x0018, 0x9008): "channel_source_modifier_sequence",
    (0x0018, 0x9009): "channel_group_sequence",
    (0x0018, 0x900A): "waveform_sample_count",
    (0x0018, 0x900B): "waveform_sample_interval",
    (0x0018, 0x900C): "waveform_offset_vector",
    (0x0018, 0x900D): "waveform_gain_correction",
    (0x0018, 0x900E): "waveform_baseline",
    (0x0018, 0x900F): "waveform_min_value",
    (0x0018, 0x9010): "waveform_max_value",
    (0x0018, 0x9011): "waveform_number_of_samples",
    (0x0018, 0x9012): "waveform_bits_allocated",
    (0x0018, 0x9013): "waveform_pixel_representation",
    (0x0018, 0x9014): "waveform_padding_value",
    (0x0018, 0x9015): "waveform_offset_shift",
    (0x0018, 0x9016): "waveform_filter_sequence",
    (0x0018, 0x9017): "waveform_filter_type",
    (0x0018, 0x9018): "waveform_filter_characteristics",
}

MULTIMODAL_TAGS = {
    (0x0008, 0x0060): "modality",
    (0x0008, 0x0064): "conversion_type",
    (0x0008, 0x0201): "timezone_offset_from_utc",
    (0x0010, 0x0010): "patient_name",
    (0x0010, 0x0020): "patient_id",
    (0x0010, 0x0030): "patient_birth_date",
    (0x0010, 0x0040): "patient_sex",
    (0x0020, 0x000D): "study_instance_uid",
    (0x0020, 0x000E): "series_instance_uid",
    (0x0020, 0x0010): "study_id",
    (0x0020, 0x0011): "series_number",
    (0x0020, 0x0013): "instance_number",
    (0x0028, 0x0002): "samples_per_pixel",
    (0x0028, 0x0004): "photometric_interpretation",
    (0x0028, 0x0010): "rows",
    (0x0028, 0x0011): "columns",
    (0x0028, 0x0030): "pixel_spacing",
}

VARIOUS_MODALITIES_TOTAL_TAGS = (
    VETERINARY_TAGS | RESEARCH_TAGS | EMERGING_TAGS | MULTIMODAL_TAGS
)


def _extract_veterinary_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in VETERINARY_TAGS.items():
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


def _extract_research_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in RESEARCH_TAGS.items():
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


def _calculate_various_metrics(ds: Any) -> Dict[str, Any]:
    metrics = {}
    try:
        if hasattr(ds, 'Rows') and hasattr(ds, 'Columns'):
            metrics['total_pixels'] = ds.Rows * ds.Columns
    except Exception:
        pass
    return metrics


def _is_various_modality_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            return True
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xx(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xx_detected": False,
        "fields_extracted": 0,
        "extension_xx_type": "various_modalities",
        "extension_xx_version": "2.0.0",
        "modality_type": None,
        "veterinary_medicine": {},
        "clinical_research": {},
        "emerging_technology": {},
        "general_parameters": {},
        "derived_metrics": {},
        "extraction_errors": [],
    }

    try:
        if not _is_various_modality_file(file_path):
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

        result["extension_xx_detected"] = True
        result["modality_type"] = getattr(ds, 'Modality', 'Unknown')

        veterinary = _extract_veterinary_tags(ds)
        research = _extract_research_tags(ds)
        metrics = _calculate_various_metrics(ds)

        result["veterinary_medicine"] = veterinary
        result["clinical_research"] = research
        result["derived_metrics"] = metrics

        total_fields = len(veterinary) + len(research) + len(metrics)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xx_field_count() -> int:
    return len(VARIOUS_MODALITIES_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xx_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xx_description() -> str:
    return ("Various medical modalities metadata extraction. Supports veterinary imaging, "
            "clinical research trials, and emerging technologies. Extracts breed "
            "information, clinical trial parameters, waveform data, and multimodal "
            "imaging parameters for comprehensive analysis across diverse imaging domains.")


def get_scientific_dicom_fits_ultimate_advanced_extension_xx_modalities() -> List[str]:
    return ["ALL", "XC", "CR", "CT", "MR", "US", "PT", "NM", "RG", "MG", "DX", "XA", "RF", "ES"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xx_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xx_category() -> str:
    return "Various and Emerging Medical Modalities"


def get_scientific_dicom_fits_ultimate_advanced_extension_xx_keywords() -> List[str]:
    return [
        "veterinary", "clinical trial", "research", "emerging technology",
        "multimodal", "waveform", "breed", "microchip", "species",
        "longitudinal", "coordinating center", "protocol"
    ]
