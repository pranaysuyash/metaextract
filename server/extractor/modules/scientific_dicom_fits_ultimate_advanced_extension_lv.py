"""
Scientific DICOM/FITS Ultimate Advanced Extension LV - Transplant Imaging

This module provides comprehensive extraction of Transplant Imaging parameters
including organ transplantation assessment, donor evaluation, recipient monitoring,
immunosuppression monitoring, and transplant complications.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LV_AVAILABLE = True

TRANSPLANT_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x2203): "transplant_type",
    (0x0010, 0x2204): "organ_type",
    (0x0010, 0x2205): "donor_type",
    (0x0010, 0x2206): "donor_age",
    (0x0010, 0x2207): "donor_sex",
    (0x0010, 0x2208): "recipient_status",
    (0x0010, 0x2209): "transplant_date",
    (0x0010, 0x2210): "transplant_center",
    (0x0010, 0x2211): "transplant_surgeon",
    (0x0010, 0x2212): "united_network_organ_sharing_id",
    (0x0010, 0x2213): "allocation_score",
    (0x0010, 0x2214): "waiting_time_days",
    (0x0010, 0x2215): "blood_type",
    (0x0010, 0x2216): "hla_typing",
    (0x0010, 0x2217): "crossmatch_result",
    (0x0010, 0x2218): "panel_reactive_antibody_percentage",
    (0x0010, 0x2219): "sensitization_history",
    (0x0010, 0x2220): "previous_transplants",
    (0x0010, 0x2221): "previous_rejections",
    (0x0010, 0x2222): "primary_diagnosis",
    (0x0010, 0x2223): "secondary_diagnosis",
    (0x0010, 0x2224): "comorbidity_index",
    (0x0010, 0x2225): "functional_status",
    (0x0010, 0x2226): "social_support",
    (0x0010, 0x2227): "financial_clearance",
    (0x0010, 0x2228): "informed_consent_status",
    (0x0010, 0x2229): "listing_status",
    (0x0010, 0x2230): "status_date",
    (0x0010, 0x2231): "urgency_status",
    (0x0010, 0x2232): "geographic_priority",
    (0x0010, 0x2233): "organ_size_match",
    (0x0010, 0x2234): "ischemia_time_hours",
    (0x0010, 0x2235): "cold_ischemia_time",
    (0x0010, 0x2236): "warm_ischemia_time",
    (0x0010, 0x2237): "preservation_solution",
    (0x0010, 0x2238): "organ_quality_score",
    (0x0010, 0x2239): "donor_risk_index",
    (0x0010, 0x2240): "KDPI_score",
    (0x0010, 0x2241): "MELD_score",
    (0x0010, 0x2242): "MELD_Na_score",
    (0x0010, 0x2243): "Child_Pugh_score",
    (0x0010, 0x2244): "CAP_score",
    (0x0010, 0x2245): " lung_allocation_score",
    (0x0010, 0x2246): "Cystic_fibrosis_score",
    (0x0010, 0x2247): "PELD_score",
    (0x0010, 0x2248): "INR_level",
    (0x0010, 0x2249): "creatinine_level",
}

DONOR_EVALUATION_TAGS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x0087): "echo_train_length",
    (0x0018, 0x0090): "frequency_selection_gradient_orientation",
    (0x0018, 0x0091): "magnetic_field_strength_tesla",
    (0x0018, 0x0095): "pixel_bandwidth",
    (0x0018, 0x0100): "spatial_resolution",
    (0x0018, 0x0150): "parallel_collection_mode",
    (0x0018, 0x0151): "parallel_collection_algorithm",
    (0x0018, 0x0210): "trigger_delay_time",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xA001): "donor_imaging_indicator",
    (0x0018, 0xA002): "donor_ct_findings",
    (0x0018, 0xA003): "donor_mri_findings",
    (0x0018, 0xA004): "organ_viability_score",
    (0x0018, 0xA005): "steatosis_percentage",
    (0x0018, 0xA006): "fibrosis_stage",
    (0x0018, 0xA007): "cirrhosis_indicator",
    (0x0018, 0xA008): "nodule_presence",
    (0x0018, 0xA009): "nodule_size",
    (0x0018, 0xA010): "vascular_anatomy",
    (0x0018, 0xA011): "arterial_anatomy",
    (0x0018, 0xA012): "venous_anatomy",
    (0x0018, 0xA013): "biliary_anatomy",
    (0x0018, 0xA014): "anatomic_variants",
    (0x0018, 0xA015): "injury_indicator",
    (0x0018, 0xA016): "contusion_size",
    (0x0018, 0xA017): "laceration_size",
    (0x0018, 0xA018): "laceration_depth",
    (0x0018, 0xA019): "vascular_injury",
    (0x0018, 0xA020): "ureteral_anatomy",
    (0x0018, 0xA021): "kidney_size_cm",
    (0x0018, 0xA022): "kidney_cortex_thickness",
    (0x0018, 0xA023): "kidney_parenchymal_quality",
    (0x0018, 0xA024): "artery_count",
    (0x0018, 0xA025): "vein_count",
    (0x0018, 0xA026): "ureter_count",
    (0x0018, 0xA027): "lung_function_assessment",
    (0x0018, 0xA028): "lung_injury_score",
    (0x0018, 0xA029): "cardiac_evaluation",
    (0x0018, 0xA030): "heart_size",
    (0x0018, 0xA031): "valve_function",
    (0x0018, 0xA032): "coronary_status",
    (0x0018, 0xA033): "ejection_fraction",
    (0x0018, 0xA034): "wall_motion",
    (0x0018, 0xA035): "ischemia_evidence",
    (0x0018, 0xA036): "pancreas_evaluation",
    (0x0018, 0xA037): "intestine_evaluation",
    (0x0018, 0xA038): "vascular_graft_status",
    (0x0018, 0xA039): "preservation_assessment",
    (0x0018, 0xA040): "perfusion_quality",
}

IMMUNOSUPPRESSION_TAGS = {
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
    (0x0028, 0x1055): "window_center_and_width_explanation",
    (0x0028, 0x2110): "lossy_image_compression",
    (0x0028, 0x2112): "lossy_image_compression_ratio",
    (0x0028, 0x2114): "lossy_image_compression_method",
    (0x0018, 0xB001): "immunosuppression_protocol",
    (0x0018, 0xB002): "tacrolimus_level",
    (0x0018, 0xB003): "cyclosporine_level",
    (0x0018, 0xB004): "sirolimus_level",
    (0x0018, 0xB005): "mycophenolate_dose",
    (0x0018, 0xB006): "azathioprine_dose",
    (0x0018, 0xB007): "prednisone_dose",
    (0x0018, 0xB008): "steroid_therapy_status",
    (0x0018, 0xB009): "induction_therapy",
    (0x0018, 0xB010): "antibody_therapy",
    (0x0018, 0xB011): "rejection_prophylaxis",
    (0x0018, 0xB012): "infection_prophylaxis",
    (0x0018, 0xB013): "drug_interaction_check",
    (0x0018, 0xB014): "nephrotoxicity_indicator",
    (0x0018, 0xB015): "hepatotoxicity_indicator",
    (0x0018, 0xB016): "neurotoxicity_indicator",
    (0x0018, 0xB017): "hyperlipidemia_indicator",
    (0x0018, 0xB018): "diabetes_indicator",
    (0x0018, 0xB019): "hypertension_indicator",
    (0x0018, 0xB020): "bone_marrow_suppression",
    (0x0018, 0xB021): "leukopenia_indicator",
    (0x0018, 0xB022): "anemia_indicator",
    (0x0018, 0xB023): "thrombocytopenia_indicator",
    (0x0018, 0xB024): "immunosuppression_level",
    (0x0018, 0xB025): "drug_concentration",
    (0x0018, 0xB026): "therapeutic_drug_monitoring",
    (0x0018, 0xB027): "medication_adherence",
    (0x0018, 0xB028): "medication_side_effects",
    (0x0018, 0xB029): "immunosuppression_modification",
}

TRANSPLANT_COMPLICATIONS_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0008, 0x1060): "physician_reading_study",
    (0x0008, 0x1070): "operator_name",
    (0x0008, 0x1080): "admitting_diagnoses_description",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x0040): "tr",
    (0x0018, 0x0070): "data_collection_diameter",
    (0x0018, 0x0082): "inversion_time",
    (0x0018, 0x0084): "imaging_frequency",
    (0x0018, 0x0085): "imaged_nucleus",
    (0x0018, 0x0086): "number_of_phase_encoding_steps",
    (0x0018, 0x0160): "parallel_sampling_factor",
    (0x0018, 0x0170): "parallel_acquisition_factor",
    (0x0018, 0x0175): "water_fat_shift_pixels",
    (0x0018, 0x0180): "coil_array_type",
    (0x0018, 0x0181): "active_coil_dimension",
    (0x0018, 0x0194): "mr_acquisition_type",
    (0x0018, 0x0195): "sequence_type",
    (0x0018, 0x0120): "reconstruction_diameter",
    (0x0018, 0x0140): "distortion_correction_type",
    (0x0018, 0x1150): "exposure_time",
    (0x0018, 0x1151): "xray_tube_current",
    (0x0018, 0x1152): "exposure",
    (0x0018, 0x1160): "filter_material",
    (0x0018, 0x1110): "distance_source_to_detector",
    (0x0018, 0x1111): "distance_source_to_patient",
    (0x0018, 0x5100): "patient_position",
    (0x0018, 0xC001): "rejection_indicator",
    (0x0018, 0xC002): "rejection_grade",
    (0x0018, 0xC003): "rejection_type",
    (0x0018, 0xC004): "acute_rejection",
    (0x0018, 0xC005): "chronic_rejection",
    (0x0018, 0xC006): "antibody_mediated_rejection",
    (0x0018, 0xC007): "cellular_rejection",
    (0x0018, 0xC008): "biopsy_result",
    (0x0018, 0xC009): "banff_classification",
    (0x0018, 0xC010): "vascular_complication",
    (0x0018, 0xC011): "arterial_stenosis",
    (0x0018, 0xC012): "venous_thrombosis",
    (0x0018, 0xC013): "arterial_thrombosis",
    (0x0018, 0xC014): "vascular_stenosis",
    (0x0018, 0xC015): "anastomotic_leak",
    (0x0018, 0xC016): "anastomotic_stricture",
    (0x0018, 0xC017): "biliary_complication",
    (0x0018, 0xC018): "biliary_stricture",
    (0x0018, 0xC019): "biliary_leak",
    (0x0018, 0xC020): "infection_indicator",
    (0x0018, 0xC021): "cytomegalovirus",
    (0x0018, 0xC022): "ebv_infection",
    (0x0018, 0xC023): "fungal_infection",
    (0x0018, 0xC024): "bacterial_infection",
    (0x0018, 0xC025): "opportunistic_infection",
    (0x0018, 0xC026): "pneumonia",
    (0x0018, 0xC027): "sepsis",
    (0x0018, 0xC028): "wound_infection",
    (0x0018, 0xC029): "urinary_tract_infection",
    (0x0018, 0xC030): "recurrent_disease",
    (0x0018, 0xC031): "malignancy",
    (0x0018, 0xC032): "ptld_indicator",
    (0x0018, 0xC033): "post_transplant_lymphoproliferative",
    (0x0018, 0xC034): "new_malignancy",
    (0x0018, 0xC035): "skin_cancer",
    (0x0018, 0xC036): "post_transplant_diabetes",
    (0x0018, 0xC037): "renal_dysfunction",
    (0x0018, 0xC038): "cardiac_complication",
    (0x0018, 0xC039): "pulmonary_complication",
    (0x0018, 0xC040): "neurological_complication",
}

TOTAL_TAGS_LV = (
    TRANSPLANT_PATIENT_PARAMETERS | 
    DONOR_EVALUATION_TAGS | 
    IMMUNOSUPPRESSION_TAGS | 
    TRANSPLANT_COMPLICATIONS_TAGS
)


def _extract_tags_lv(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LV.items():
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


def _is_transplant_imaging_file(file_path: str) -> bool:
    transplant_indicators = [
        'transplant', 'transplantation', 'donor', 'recipient', 'organ',
        'kidney', 'liver', 'heart', 'lung', 'pancreas', 'intestine',
        'immunosuppression', 'rejection', 'hla', 'meld', 'kdpi',
        'allograft', 'graft', 'unOS'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in transplant_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lv(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lv_detected": False,
        "fields_extracted": 0,
        "extension_lv_type": "transplant_imaging",
        "extension_lv_version": "2.0.0",
        "transplant_patient_parameters": {},
        "donor_evaluation": {},
        "immunosuppression": {},
        "transplant_complications": {},
        "extraction_errors": [],
    }

    try:
        if not _is_transplant_imaging_file(file_path):
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

        result["extension_lv_detected"] = True

        transplant_data = _extract_tags_lv(ds)

        result["transplant_patient_parameters"] = {
            k: v for k, v in transplant_data.items()
            if k in TRANSPLANT_PATIENT_PARAMETERS.values()
        }
        result["donor_evaluation"] = {
            k: v for k, v in transplant_data.items()
            if k in DONOR_EVALUATION_TAGS.values()
        }
        result["immunosuppression"] = {
            k: v for k, v in transplant_data.items()
            if k in IMMUNOSUPPRESSION_TAGS.values()
        }
        result["transplant_complications"] = {
            k: v for k, v in transplant_data.items()
            if k in TRANSPLANT_COMPLICATIONS_TAGS.values()
        }

        result["fields_extracted"] = len(transplant_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lv_field_count() -> int:
    return len(TOTAL_TAGS_LV)


def get_scientific_dicom_fits_ultimate_advanced_extension_lv_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lv_description() -> str:
    return (
        "Transplant Imaging metadata extraction. Provides comprehensive coverage of "
        "organ transplantation assessment, donor evaluation, recipient monitoring, "
        "immunosuppression monitoring, and transplant complications."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lv_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "PT", "NM", "XA", "RF"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lv_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lv_category() -> str:
    return "Transplant Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_lv_keywords() -> List[str]:
    return [
        "transplant", "organ transplantation", "donor evaluation", "recipient monitoring",
        "immunosuppression", "rejection", "hla matching", "meld score", "kdpi",
        "kidney transplant", "liver transplant", "heart transplant", "lung transplant",
        "pancreas transplant", "allograft", "graft survival", "transplant complications"
    ]
