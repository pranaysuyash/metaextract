"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXIV - Dermatology Imaging II

This module provides comprehensive extraction of Dermatology Imaging parameters
including skin disorders, melanoma, inflammatory skin conditions, and
dermatology-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXIV_AVAILABLE = True

DERMATOLOGY_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0xH001): "dermatology_assessment_date",
    (0x0010, 0xH002): "skin_diagnosis",
    (0x0010, 0xH003): "melanoma_indicator",
    (0x0010, 0xH004): "melanoma_thickness",
    (0x0010, 0xH005): "breslow_thickness",
    (0x0010, 0xH006): "ulceration_indicator",
    (0x0010, 0xH007): "mitotic_rate",
    (0x0010, 0xH008): "clark_level",
    (0x0010, 0xH009): "melanoma_stage",
    (0x0010, 0xH010): "melanoma_in_situ",
    (0x0010, 0xH011): "lentigo_maligna",
    (0x0010, 0xH012): "superficial_spreading",
    (0x0010, 0xH013): "nodular_melanoma",
    (0x0010, 0xH014): "acral_melanoma",
    (0x0010, 0xH015): "mucosal_melanoma",
    (0x0010, 0xH016): "non_melanoma_skin_cancer",
    (0x0010, 0xH017): "basal_cell_carcinoma",
    (0x0010, 0xH018): "squamous_cell_carcinoma",
    (0x0010, 0xH019): "merkel_cell_carcinoma",
    (0x0010, 0xH020): "cutaneous_lymphoma",
    (0x0010, 0xH021): "mycosis_fungoides",
    (0x0010, 0xH022): "sezary_syndrome",
    (0x0010, 0xH023): "eczema_indicator",
    (0x0010, 0xH024): "atopic_dermatitis",
    (0x0010, 0xH025): "psoriasis_indicator",
    (0x0010, 0xH026): "plaque_psoriasis",
    (0x0010, 0xH027): "guttate_psoriasis",
    (0x0010, 0xH028): "pustular_psoriasis",
    (0x0010, 0xH029): "erythrodermic_psoriasis",
    (0x0010, 0xH030): "psoriatic_arthritis",
    (0x0010, 0xH031): "pasi_score",
    (0x0010, 0xH032): "easl_score",
    (0x0010, 0xH033): "scorad_score",
    (0x0010, 0xH034): "iga_score",
    (0x0010, 0xH035): "acne_indicator",
    (0x0010, 0xH036): "acne_severity",
    (0x0010, 0xH037): "rosacea_indicator",
    (0x0010, 0xH038): "hidradenitis",
    (0x0010, 0xH039): "lichen_planus",
    (0x0010, 0xH040): "vitiligo_indicator",
    (0x0010, 0xH041): "alopecia_indicator",
    (0x0010, 0xH042): "androgenic_alopecia",
    (0x0010, 0xH043): "alopecia_areata",
    (0x0010, 0xH044): "connective_tissue_disease",
    (0x0010, 0xH045): "discoid_lupus",
    (0x0010, 0xH046): "subacute_cutaneous_lupus",
    (0x0010, 0xH047): "dermatomyositis_skin",
    (0x0010, 0xH048): "scleroderma_skin",
    (0x0010, 0xH049): "bullous_disease",
    (0x0010, 0xH050): "pemphigus",
    (0x0010, 0xH051): "pemphigoid",
    (0x0010, 0xH052): "dermatitis_herpetiformis",
    (0x0010, 0xH053): "genodermatoses",
    (0x0010, 0xH054): "neurofibromatosis",
    (0x0010, 0xH055): "tuberous_sclerosis",
    (0x0010, 0xH056): "ichthyosis",
    (0x0010, 0xH057): "epidermolysis_bullosa",
    (0x0010, 0xH058): "skin_type_fitzpatrick",
    (0x0010, 0xH059): "family_history_melanoma",
}

DERMATOLOGY_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xH101): "lesion_size",
    (0x0018, 0xH102): "lesion_diameter",
    (0x0018, 0xH103): "lesion_elevation",
    (0x0018, 0xH104): "asymmetry_indicator",
    (0x0018, 0xH105): "border_irregularity",
    (0x0018, 0xH106): "color_variation",
    (0x0018, 0xH107): "diameter_greater_6mm",
    (0x0018, 0xH108): "evolution_indicator",
    (0x0018, 0xH109): "abcde_features",
    (0x0018, 0xH110): "ugly_duckling_sign",
    (0x0018, 0xH111): "fitzpatrick_lesion",
    (0x0018, 0xH112): "collision_lesion",
    (0x0018, 0xH113): "regression_lesion",
    (0x0018, 0xH114): "vascular_pattern",
    (0x0018, 0xH115): "pigment_network",
    (0x0018, 0xH116): "atypical_network",
    (0x0018, 0xH117): "streaks_radial",
    (0x0018, 0xH118): "pseudo_network",
    (0x0018, 0xH119): "blue_white_veil",
    (0x0018, 0xH120): "blue_white_structure",
    (0x0018, 0xH121): "regression_structures",
    (0x0018, 0xH122): "milia_like_cysts",
    (0x0018, 0xH123): "comedo_like_openings",
    (0x0018, 0xH124): "leaf_like_areas",
    (0x0018, 0xH125): "spoke_wheel_areas",
    (0x0018, 0xH126): "large_ovoid_nests",
    (0x0018, 0xH127): "multiple_brown_dots",
    (0x0018, 0xH128): "peripheral_dots",
    (0x0018, 0xH129): "targetoid_homosiderin",
    (0x0018, 0xH130): "squamous_cell_indicator",
    (0x0018, 0xH131): "keratoacanthoma",
    (0x0018, 0xH132): "actinic_keratosis",
    (0x0018, 0xH133): "bowen_disease",
    (0x0018, 0xH134): "cutaneous_horn",
    (0x0018, 0xH135): "dysplastic_nevus",
    (0x0018, 0xH136): "congenital_nevus",
    (0x0018, 0xH137): "dysplastic_nevus_syndrome",
    (0x0018, 0xH138): "epidermal_nevus",
    (0x0018, 0xH139): "seborrheic_keratosis",
    (0x0018, 0xH140): "dermal_nevus",
    (0x0018, 0xH141): "blue_nevus",
    (0x0018, 0xH142): "spitz_nevus",
    (0x0018, 0xH143): "halo_nevus",
    (0x0018, 0xH144): "recurrent_nevus",
    (0x0018, 0xH145): "nail_changes",
    (0x0018, 0xH146): "mucosal_lesion",
    (0x0018, 0xH147): "acral_lesion",
    (0x0018, 0xH148): "nail_matrix_lesion",
    (0x0018, 0xH149): "hidradenitis_sinus",
}

DERMATOLOGY_IMAGING_TAGS = {
    (0x0020, 0x0010): "series_number",
    (0x0020, 0x0011): "instance_number",
    (0x0020, 0x0032): "image_position_patient",
    (0x0020, 0x0037): "image_orientation_patient",
    (0x0020, 0x0050): "location",
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
    (0x0018, 0xH201): "dermatoscopy",
    (0x0018, 0xH202): "polarized_dermoscopy",
    (0x0018, 0xH203): "non_polarized_dermoscopy",
    (0x0018, 0xH204): "contact_dermoscopy",
    (0x0018, 0xH205): "digital_dermoscopy",
    (0x0018, 0xH206): "total_body_photography",
    (0x0018, 0xH207): "sequential_digital_imaging",
    (0x0018, 0xH208): "computer_aided_diagnosis",
    (0x0018, 0xH209): "ai_melanoma_detection",
    (0x0018, 0xH210): "machine_learning_derm",
    (0x0018, 0xH211): "confocal_microscopy",
    (0x0018, 0xH212): "reflectance_confocal",
    (0x0018, 0xH213): "optical_coherence_tomo",
    (0x0018, 0xH214): "multispectral_imaging",
    (0x0018, 0xH215): "fluorescence_imaging",
    (0x0018, 0xH216): "wood_lamp_exam",
    (0x0018, 0xH217): "uv_photography",
    (0x0018, 0xH218): "trichoscopy",
    (0x0018, 0xH219): "capillaroscopy",
    (0x0018, 0xH220): "onychoscopy",
    (0x0018, 0xH221): "video_dermoscopy",
    (0x0018, 0xH222): "high_frequency_ultrasound",
    (0x0018, 0xH223): "skin_ultrasound",
    (0x0018, 0xH224): "high_res_ultrasound",
    (0x0018, 0xH225): "doppler_ultrasound",
    (0x0018, 0xH226): "ct_skin_lesion",
    (0x0018, 0xH227): "mri_soft_tissue",
    (0x0018, 0xH228): "pet_ct_melanoma",
    (0x0018, 0xH229): "sentinel_lymph_node",
    (0x0018, 0xH230): "lymphoscintigraphy",
    (0x0018, 0xH231): "spect_ct_lymph",
    (0x0018, 0xH232): "ulcers_assessment",
    (0x0018, 0xH233): "wound_measurement",
    (0x0018, 0xH234): "3d_photogrammetry",
    (0x0018, 0xH235): "structured_light_3d",
    (0x0018, 0xH236): "stereotactic_biopsy",
    (0x0018, 0xH237): "excision_mapping",
    (0x0018, 0xH238): "mohs_surgery_mapping",
    (0x0018, 0xH239): "wide_local_excision",
    (0x0018, 0xH240): "lymph_node_biopsy",
    (0x0018, 0xH241): "fine_needle_aspiration",
    (0x0018, 0xH242): "skin_biopsy_protocol",
    (0x0018, 0xH243): "punch_biopsy",
    (0x0018, 0xH244): "shave_biopsy",
    (0x0018, 0xH245): "excisional_biopsy",
    (0x0018, 0xH246): "incisional_biopsy",
    (0x0018, 0xH247): "dermatoscopic_biopsy",
    (0x0018, 0xH248): "immunofluorescence",
    (0x0018, 0xH249): "histopathology_derm",
}

DERMATOLOGY_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xH301): "melanoma_surveillance",
    (0x0018, 0xH302): "screening_dermoscopy",
    (0x0018, 0xH303): "risk_assessment",
    (0x0018, 0xH304): "fair_skin_risk",
    (0x0018, 0xH305): "nevus_count",
    (0x0018, 0xH306): "atypical_nevi",
    (0x0018, 0xH307): "family_history",
    (0x0018, 0xH308): "genetic_counseling",
    (0x0018, 0xH309): "cdkn2a_testing",
    (0x0018, 0xH310): "treatment_planning",
    (0x0018, 0xH311): "wide_local_excision",
    (0x0018, 0xH312): "margins_lesion",
    (0x0018, 0xH313): "sentinel_lymph_node_biopsy",
    (0x0018, 0xH314): "completion_lymphadenectomy",
    (0x0018, 0xH315): "adjuvant_therapy",
    (0x0018, 0xH316): "immunotherapy_derm",
    (0x0018, 0xH317): "targeted_therapy",
    (0x0018, 0xH318): "braf_inhibitor",
    (0x0018, 0xH319): "mek_inhibitor",
    (0x0018, 0xH320): "mohs_micrographic",
    (0x0018, 0xH321): "staged_excision",
    (0x0018, 0xH322): "curettage_electrodesiccation",
    (0x0018, 0xH323): "cryotherapy",
    (0x0018, 0xH324): "photodynamic_therapy",
    (0x0018, 0xH325): "topical_therapy",
    (0x0018, 0xH326): "laser_therapy",
    (0x0018, 0xH327): "excimer_laser",
    (0x0018, 0xH328): "biologic_therapy_derm",
    (0x0018, 0xH329): "anti_tnf_derm",
    (0x0018, 0xH330): "il12_23_inhibitor",
    (0x0018, 0xH331): "il17_inhibitor",
    (0x0018, 0xH332): "il23_inhibitor",
    (0x0018, 0xH333): "jaki_derm",
    (0x0018, 0xH334): "phototherapy",
    (0x0018, 0xH335): "nbuvb_therapy",
    (0x0018, 0xH336): "puva_therapy",
    (0x0018, 0xH337): "excimer_laser_therapy",
    (0x0018, 0xH338): "systemic_therapy_derm",
    (0x0018, 0xH339): "retinoid_therapy",
    (0x0018, 0xH340): "immunosuppressive_therapy",
    (0x0018, 0xH341): "steroid_therapy",
    (0x0018, 0xH342): "wound_care_protocol",
    (0x0018, 0xH343): "compression_therapy",
    (0x0018, 0xH344): "negative_pressure_therapy",
    (0x0018, 0xH345): "skin_graft_planning",
    (0x0018, 0xH346): "flap_reconstruction",
    (0x0018, 0xH347): "reconstructive_surgery",
    (0x0018, 0xH348): "scar_management",
    (0x0018, 0xH349): "laser_scar_revision",
    (0x0018, 0xH350): "cosmetic_procedures",
}

DERMATOLOGY_OUTCOMES_TAGS = {
    (0x0018, 0xH401): "melanoma_survival",
    (0x0018, 0xH402): "disease_free_survival_melanoma",
    (0x0018, 0xH403): "recurrence_melanoma",
    (0x0018, 0xH404): "sentinel_node_positive",
    (0x0018, 0xH405): "lymph_node_involvement",
    (0x0018, 0xH406): "distant_metastasis",
    (0x0018, 0xH407): "treatment_response_derm",
    (0x0018, 0xH408): "complete_response_derm",
    (0x0018, 0xH409): "partial_response_derm",
    (0x0018, 0xH410): "stable_disease_derm",
    (0x0018, 0xH411): "progressive_disease_derm",
    (0x0018, 0xH412): "treatment_toxicity_derm",
    (0x0018, 0xH413): "immune_related_ae",
    (0x0018, 0xH414): "dermatologic_ae",
    (0x0018, 0xH415): "skin_toxicity",
    (0x0018, 0xH416): "rash_derm",
    (0x0018, 0xH417): "pruritus_derm",
    (0x0018, 0xH418): "psoriasis_clearance",
    (0x0018, 0xH419): "pasi_75_response",
    (0x0018, 0xH420): "pasi_90_response",
    (0x0018, 0xH421): "pasl_100_response",
    (0x0018, 0xH422): "easi_75_response",
    (0x0018, 0xH423): "scorad_50",
    (0x0018, 0xH424): "iga_clear",
    (0x0018, 0xH425): "quality_of_life_derm",
    (0x0018, 0xH426): "dlqi_score",
    (0x0018, 0xH427): "skindex_score",
    (0x0018, 0xH428): "cdlqi_score",
    (0x0018, 0xH429): "psychological_impact",
    (0x0018, 0xH430): "body_image_concern",
    (0x0018, 0xH431): "social_impact",
    (0x0018, 0xH432): "work_impact",
    (0x0018, 0xH433): "cosmetic_outcome",
    (0x0018, 0xH434): "scar_quality",
    (0x0018, 0xH435): "patient_satisfaction",
    (0x0018, 0xH436): "adherence_therapy",
    (0x0018, 0xH437): "topical_adherence",
    (0x0018, 0xH438): "phototherapy_adherence",
    (0x0018, 0xH439): "follow_up_compliance",
    (0x0018, 0xH440): "sun_protection_behavior",
    (0x0018, 0xH441): "screening_adherence",
    (0x0018, 0xH442): "self_examination",
    (0x0018, 0xH443): "photoprotection",
    (0x0018, 0xH444): "sunscreen_use",
    (0x0018, 0xH445): "sun_exposure_habits",
    (0x0018, 0xH446): "tanning_bed_use",
    (0x0018, 0xH447): "vitamin_d_level",
    (0x0018, 0xH448): "skin_cancer_prevention",
    (0x0018, 0xH449): "health_education",
    (0x0018, 0xH450): "patient_education_derm",
}

TOTAL_TAGS_LXXIV = {}

TOTAL_TAGS_LXXIV.update(DERMATOLOGY_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXIV.update(DERMATOLOGY_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXIV.update(DERMATOLOGY_IMAGING_TAGS)
TOTAL_TAGS_LXXIV.update(DERMATOLOGY_PROTOCOLS)
TOTAL_TAGS_LXXIV.update(DERMATOLOGY_OUTCOMES_TAGS)


def _extract_tags_lxxiv(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXIV.items()}
    for tag, name in tag_names.items():
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


def _is_dermatology_imaging_file(file_path: str) -> bool:
    derm_indicators = [
        'dermatology', 'dermatologic', 'skin', 'melanoma', 'dermoscopy',
        'dermatoscopy', 'skin_cancer', 'psoriasis', 'eczema', 'acne',
        'lesion', 'nevus', 'biopsy', 'mohs', 'cutaneous', 'dermal',
        'lupus', 'scleroderma', 'hidradenitis', 'trichoscopy'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in derm_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxiv(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxiv_detected": False,
        "fields_extracted": 0,
        "extension_lxxiv_type": "dermatology_imaging",
        "extension_lxxiv_version": "2.0.0",
        "dermatology_patient_parameters": {},
        "dermatology_pathology": {},
        "dermatology_imaging": {},
        "dermatology_protocols": {},
        "dermatology_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_dermatology_imaging_file(file_path):
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

        result["extension_lxxiv_detected"] = True

        derm_data = _extract_tags_lxxiv(ds)

        patient_params_set = set(DERMATOLOGY_PATIENT_PARAMETERS.keys())
        pathology_set = set(DERMATOLOGY_PATHOLOGY_TAGS.keys())
        imaging_set = set(DERMATOLOGY_IMAGING_TAGS.keys())
        protocols_set = set(DERMATOLOGY_PROTOCOLS.keys())
        outcomes_set = set(DERMATOLOGY_OUTCOMES_TAGS.keys())

        for tag, value in derm_data.items():
            if tag in patient_params_set:
                result["dermatology_patient_parameters"][tag] = value
            elif tag in pathology_set:
                result["dermatology_pathology"][tag] = value
            elif tag in imaging_set:
                result["dermatology_imaging"][tag] = value
            elif tag in protocols_set:
                result["dermatology_protocols"][tag] = value
            elif tag in outcomes_set:
                result["dermatology_outcomes"][tag] = value

        result["fields_extracted"] = len(derm_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxiv_field_count() -> int:
    return len(TOTAL_TAGS_LXXIV)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxiv_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxiv_description() -> str:
    return (
        "Dermatology Imaging II metadata extraction. Provides comprehensive coverage of "
        "skin disorders, melanoma, inflammatory skin conditions, "
        "dermatology-specific imaging protocols, and dermatology outcomes assessment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxiv_modalities() -> List[str]:
    return ["US", "CT", "MR", "CR", "DR", "PT", "NM"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxiv_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxiv_category() -> str:
    return "Dermatology Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxiv_keywords() -> List[str]:
    return [
        "dermatology", "skin", "melanoma", "dermoscopy", "skin cancer",
        "psoriasis", "eczema", "acne", "lesion", "nevus",
        "biopsy", "Mohs surgery", "cutaneous", "lupus", "scleroderma",
        "hidradenitis", "trichoscopy", "total body photography"
    ]
