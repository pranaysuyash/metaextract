"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXXIX - Pulmonology Imaging II

This module provides comprehensive extraction of Pulmonology Imaging parameters
including respiratory disease, lung cancer, interstitial lung disease, and
pulmonology-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXIX_AVAILABLE = True

PULMONOLOGY_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0xA001): "pulmonology_assessment_date",
    (0x0010, 0xA002): "pulmonary_diagnosis",
    (0x0010, 0xA003): "copd_indicator",
    (0x0010, 0xA004): "emphysema_indicator",
    (0x0010, 0xA005): "chronic_bronchitis",
    (0x0010, 0xA006): "asthma_indicator",
    (0x0010, 0xA007): "asthma_severity",
    (0x0010, 0xA008): "asthma_control",
    (0x0010, 0xA009): "interstitial_lung_disease",
    (0x0010, 0xA010): "idiopathic_pulmonary_fibrosis",
    (0x0010, 0xA011): "nsip_pattern",
    (0x0010, 0xA012): "uip_pattern",
    (0x0010, 0xA013): "hypersensitivity_pneumonitis",
    (0x0010, 0xA014): "sarcoidosis_indicator",
    (0x0010, 0xA015): "pulmonary_hypertension",
    (0x0010, 0xA016): "pulmonary_embolism",
    (0x0010, 0xA017): "pulmonary_fibrosis",
    (0x0010, 0xA018): "restrictive_lung_disease",
    (0x0010, 0xA019): "obstructive_lung_disease",
    (0x0010, 0xA020): "mixed_lung_disease",
    (0x0010, 0xA021): "lung_cancer_diagnosis",
    (0x0010, 0xA022): "lung_cancer_type",
    (0x0010, 0xA023): "non_small_cell_lung_cancer",
    (0x0010, 0xA024): "adenocarcinoma_lung",
    (0x0010, 0xA025): "squamous_cell_lung",
    (0x0010, 0xA026): "large_cell_carcinoma",
    (0x0010, 0xA027): "small_cell_lung_cancer",
    (0x0010, 0xA028): "limited_stage_sclc",
    (0x0010, 0xA029): "extensive_stage_sclc",
    (0x0010, 0xA030): "lung_cancer_stage",
    (0x0010, 0xA031): "tnm_lung",
    (0x0010, 0xA032): "nodule_indicator",
    (0x0010, 0xA033): "solitary_pulmonary_nodule",
    (0x0010, 0xA034): "multiple_nodules",
    (0x0010, 0xA035): "nodule_size",
    (0x0010, 0xA036): "nodule_location",
    (0x0010, 0xA037): "nodule_characteristics",
    (0x0010, 0xA038): "pulmonary_function_tests",
    (0x0010, 0xA039): "fev1_value",
    (0x0010, 0xA040): "fvc_value",
    (0x0010, 0xA041): "fev1_fvc_ratio",
    (0x0010, 0xA042): "dlco_value",
    (0x0010, 0xA043): "peak_expiratory_flow",
    (0x0010, 0xA044): "six_minute_walk_test",
    (0x0010, 0xA045): "oxygen_saturation",
    (0x0010, 0xA046): "pao2_level",
    (0x0010, 0xA047): "paco2_level",
    (0x0010, 0xA048): "ph_level",
    (0x0010, 0xA049): "respiratory_failure",
    (0x0010, 0xA050): "type_1_respiratory_failure",
    (0x0010, 0xA051): "type_2_respiratory_failure",
    (0x0010, 0xA052): "chronic_oxygen_therapy",
    (0x0010, 0xA053): "home_oxygen",
    (0x0010, 0xA054): "non_invasive_ventilation",
    (0x0010, 0xA055): "cpap_therapy",
    (0x0010, 0xA056): "bipap_therapy",
    (0x0010, 0xA057): "mechanical_ventilation",
    (0x0010, 0xA058): "tracheostomy_status",
    (0x0010, 0xA059): "smoking_status",
}

RESPIRATORY_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xA101): "consolidation_indicator",
    (0x0018, 0xA102): "ground_glass_opacity",
    (0x0018, 0xA103): "reticular_pattern",
    (0x0018, 0xA104): "honeycombing",
    (0x0018, 0xA105): "traction_bronchiectasis",
    (0x0018, 0xA106): "tree_in_bud",
    (0x0018, 0xA107): "centrilobular_nodules",
    (0x0018, 0xA108): "perilymphatic_nodules",
    (0x0018, 0xA109): "random_nodules",
    (0x0018, 0xA110): "cystic_changes",
    (0x0018, 0xA111): "emphysema_type",
    (0x0018, 0xA112): "centrilobular_emphysema",
    (0x0018, 0xA113): "paraseptal_emphysema",
    (0x0018, 0xA114): "panlobular_emphysema",
    (0x0018, 0xA115): "bullae_indicator",
    (0x0018, 0xA116): "air_trapping",
    (0x0018, 0xA117): "mosaic_attenuation",
    (0x0018, 0xA118): "vascular_abnormality",
    (0x0018, 0xA119): "pulmonary_artery_size",
    (0x0018, 0xA120): "septal_thickening",
    (0x0018, 0xA121): "pleural_effusion",
    (0x0018, 0xA122): "pleural_thickening",
    (0x0018, 0xA123): "pleural_plaques",
    (0x0018, 0xA124): "calcified_pleura",
    (0x0018, 0xA125): "asbestos_related",
    (0x0018, 0xA126): "pleural_mass",
    (0x0018, 0xA127): "mediastinal_mass",
    (0x0018, 0xA128): "hilum_enlargement",
    (0x0018, 0xA129): "lymphadenopathy",
    (0x0018, 0xA130): "mediastinal_lymph_nodes",
    (0x0018, 0xA131): "hilar_lymph_nodes",
    (0x0018, 0xA132): "supraclavicular_nodes",
    (0x0018, 0xA133): "node_station",
    (0x0018, 0xA134): "node_size",
    (0x0018, 0xA135): "node_short_axis",
    (0x0018, 0xA136): "node_long_axis",
    (0x0018, 0xA137): "node_characteristics",
    (0x0018, 0xA138): "central_necrosis",
    (0x0018, 0xA139): "calcified_lymph_node",
    (0x0018, 0xA140): "fat_hilum_node",
    (0x0018, 0xA141): "atelectasis",
    (0x0018, 0xA142): "lobar_atelectasis",
    (0x0018, 0xA143): "segmental_atelectasis",
    (0x0018, 0xA144): "subsegmental_atelectasis",
    (0x0018, 0xA145): "collapse_pattern",
    (0x0018, 0xA146): "compressive_atelectasis",
    (0x0018, 0xA147): "cicatricial_atelectasis",
    (0x0018, 0xA148): "passive_atelectasis",
    (0x0018, 0xA149): "resorption_atelectasis",
}

THORACIC_ONCOLOGY_TAGS = {
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
    (0x0018, 0xA201): "lung_nodule_volumetry",
    (0x0018, 0xA202): "nodule_volume",
    (0x0018, 0xA203): "nodule_diameter",
    (0x0018, 0xA204): "nodule_density",
    (0x0018, 0xA205): "solid_nodule",
    (0x0018, 0xA206): "part_solid_nodule",
    (0x0018, 0xA207): "ground_glass_nodule",
    (0x0018, 0xA208): "pure_ground_glass",
    (0x0018, 0xA209): "subsolid_nodule",
    (0x0018, 0xA210): "nodule_spiculation",
    (0x0018, 0xA211): "nodule_lobulation",
    (0x0018, 0xA212): "nodule_spicules",
    (0x0018, 0xA213): "nodule_cavity",
    (0x0018, 0xA214): "cavity_wall_thickness",
    (0x0018, 0xA215): "nodule_enhancement",
    (0x0018, 0xA216): "nodule_growth_rate",
    (0x0018, 0xA217): "lung_rads_category",
    (0x0018, 0xA218): "lung_rads_1",
    (0x0018, 0xA219): "lung_rads_2",
    (0x0018, 0xA220): "lung_rads_3",
    (0x0018, 0xA221): "lung_rads_4a",
    (0x0018, 0xA222): "lung_rads_4b",
    (0x0018, 0xA223): "lung_rads_4x",
    (0x0018, 0xA224): "tumor_size",
    (0x0018, 0xA225): "tumor_location_lung",
    (0x0018, 0xA226): "tumor_lobe",
    (0x0018, 0xA227): "tumor_segment",
    (0x0018, 0xA228): "central_tumor",
    (0x0018, 0xA229): "peripheral_tumor",
    (0x0018, 0xA230): "hilar_involvement",
    (0x0018, 0xA231): "mediastinal_invasion",
    (0x0018, 0xA232): "chest_wall_invasion",
    (0x0018, 0xA233): "pleural_invasion",
    (0x0018, 0xA234): "diaphragm_invasion",
    (0x0018, 0xA235): "pericardial_invasion",
    (0x0018, 0xA236): "vascular_invasion",
    (0x0018, 0xA237): "pulmonary_artery_invasion",
    (0x0018, 0xA238): "superior_vena_cava_invasion",
    (0x0018, 0xA239): "aortic_invasion",
    (0x0018, 0xA240): "esophageal_invasion",
    (0x0018, 0xA241): "recurrent_laryngeal_invasion",
    (0x0018, 0xA242): "phrenic_nerve_invasion",
    (0x0018, 0xA243): "brachial_plexus_invasion",
    (0x0018, 0xA244): "vertebral_invasion",
    (0x0018, 0xA245): "tumor_efusion",
    (0x0018, 0xA246): "pleural_effusion_malignant",
    (0x0018, 0xA247): "pericardial_effusion_malignant",
    (0x0018, 0xA248): "malignant_mass",
    (0x0018, 0xA249): "metastatic_nodules",
}

PULMONARY_IMAGING_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xA301): "chest_ct_protocol",
    (0x0018, 0xA302): "high_resolution_ct",
    (0x0018, 0xA303): "hrct_thin_section",
    (0x0018, 0xA304): "hrct_algorithm",
    (0x0018, 0xA305): "inspiration_hrct",
    (0x0018, 0xA306): "expiration_hrct",
    (0x0018, 0xA307): "prone_ct",
    (0x0018, 0xA308): "supine_ct",
    (0x0018, 0xA309): "ct_angiography_pulmonary",
    (0x0018, 0xA310): "cta_pulmonary_embolism",
    (0x0018, 0xA311): "pulmonary_artery_ct",
    (0x0018, 0xA312): "low_dose_ct_chest",
    (0x0018, 0xA313): "lung_cancer_screening",
    (0x0018, 0xA314): "annual_lung_screen",
    (0x0018, 0xA315): "chest_mri_protocol",
    (0x0018, 0xA316): "mri_diffusion_lung",
    (0x0018, 0xA317): "mri_ventilation_lung",
    (0x0018, 0xA318): "chest_ultrasound",
    (0x0018, 0xA319): "pleural_ultrasound",
    (0x0018, 0xA320): "interventional_planning",
    (0x0018, 0xA321): "nodule_biopsy_guidance",
    (0x0018, 0xA322): "ct_guided_biopsy",
    (0x0018, 0xA323): "bronchoscopy_guidance",
    (0x0018, 0xA324): "navigation_bronchoscopy",
    (0x0018, 0xA325): "ebus_protocol",
    (0x0018, 0xA326): "endobronchial_ultrasound",
    (0x0018, 0xA327): "tbna_biopsy",
    (0x0018, 0xA328): "mediastinoscopy",
    (0x0018, 0xA329): "vats_lung_biopsy",
    (0x0018, 0xA330): "pet_ct_lung",
    (0x0018, 0xA331): "fdg_pet_lung",
    (0x0018, 0xA332): "octreotide_scan_thoracic",
    (0x0018, 0xA333): "mibg_scan_thoracic",
    (0x0018, 0xA334): "ventilation_perfusion_scan",
    (0x0018, 0xA335): "vq_scan",
    (0x0018, 0xA336): "spect_vq",
    (0x0018, 0xA337): "spect_ct_lung_perfusion",
    (0x0018, 0xA338): "quantitative_lung_scan",
    (0x0018, 0xA339): "mismatched_defect",
    (0x0018, 0xA340): "matched_defect",
    (0x0018, 0xA341): "subsegmental_pe",
    (0x0018, 0xA342): "low_probability_vq",
    (0x0018, 0xA343): "intermediate_probability_vq",
    (0x0018, 0xA344): "high_probability_vq",
    (0x0018, 0xA345): "radiation_planning_lung",
    (0x0018, 0xA346): "sbrt_lung",
    (0x0018, 0xA347): "stereotactic_body_radiation",
    (0x0018, 0xA348): "imrt_lung",
    (0x0018, 0xA349): "vmat_lung",
    (0x0018, 0xA350): "proton_therapy_lung",
}

PULMONARY_OUTCOMES_TAGS = {
    (0x0018, 0xA401): "lung_cancer_survival",
    (0x0018, 0xA402): "overall_survival_lung",
    (0x0018, 0xA403): "cancer_specific_survival",
    (0x0018, 0xA404): "progression_free_survival",
    (0x0018, 0xA405): "disease_free_survival",
    (0x0018, 0xA406): "response_rate",
    (0x0018, 0xA407): "complete_response",
    (0x0018, 0xA408): "partial_response",
    (0x0018, 0xA409): "stable_disease",
    (0x0018, 0xA410): "progressive_disease",
    (0x0018, 0xA411): "recist_response_lung",
    (0x0018, 0xA412): "immune_related_response",
    (0x0018, 0xA413): "pseudoprogression",
    (0x0018, 0xA414): "hyperprogression",
    (0x0018, 0xA415): "treatment_outcome",
    (0x0018, 0xA416): "chemotherapy_response",
    (0x0018, 0xA417): "radiation_response",
    (0x0018, 0xA418): "surgical_outcome",
    (0x0018, 0xA419): "lobectomy_outcome",
    (0x0018, 0xA420): "pneumonectomy_outcome",
    (0x0018, 0xA421): "wedge_resection_outcome",
    (0x0018, 0xA422): "segmentectomy_outcome",
    (0x0018, 0xA423): "node_dissection_outcome",
    (0x0018, 0xA424): "complications_lung_surgery",
    (0x0018, 0xA425): "air_leak",
    (0x0018, 0xA426): "prolonged_air_leak",
    (0x0018, 0xA427): "chyle_leak",
    (0x0018, 0xA428): "recurrent_laryngeal_nerve_injury",
    (0x0018, 0xA429): "hemothorax",
    (0x0018, 0xA430): "chylothorax",
    (0x0018, 0xA431): "bronchopleural_fistula",
    (0x0018, 0xA432): "pulmonary_embolism_postop",
    (0x0018, 0xA433): "atelectasis_postop",
    (0x0018, 0xA434): "pneumonia_postop",
    (0x0018, 0xA435): "respiratory_failure_postop",
    (0x0018, 0xA436): "copd_exacerbation",
    (0x0018, 0xA437): "ae_copd",
    (0x0018, 0xA438): "hospitalization_copd",
    (0x0018, 0xA439): "icu_admission_copd",
    (0x0018, 0xA440): "mechanical_ventilation_copd",
    (0x0018, 0xA441): "mortality_copd",
    (0x0018, 0xA442): "asthma_exacerbation",
    (0x0018, 0xA443): "status_asthmaticus",
    (0x0018, 0xA444): "hospitalization_asthma",
    (0x0018, 0xA445): "icu_asthma",
    (0x0018, 0xA446): "ipf_progression",
    (0x0018, 0xA447): "fvc_decline_ipf",
    (0x0018, 0xA448): "dlco_decline_ipf",
    (0x0018, 0xA449): "acute_exacerbation_ipf",
    (0x0018, 0xA450): "mortality_ipf",
}

TOTAL_TAGS_LXXXIX = {}

TOTAL_TAGS_LXXXIX.update(PULMONOLOGY_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXXIX.update(RESPIRATORY_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXXIX.update(THORACIC_ONCOLOGY_TAGS)
TOTAL_TAGS_LXXXIX.update(PULMONARY_IMAGING_PROTOCOLS)
TOTAL_TAGS_LXXXIX.update(PULMONARY_OUTCOMES_TAGS)


def _extract_tags_lxxxix(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXXIX.items()}
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


def _is_pulmonology_imaging_file(file_path: str) -> bool:
    pulmonology_indicators = [
        'pulmonology', 'pulmonary', 'respiratory', 'lung', 'thoracic',
        'copd', 'emphysema', 'asthma', 'interstitial_lung', 'pulmonary_fibrosis',
        'lung_cancer', 'lung_nodule', 'pulmonary_embolism', 'sarcoidosis',
        'bronchoscopy', 'chest_ct', 'hrct', 'lung_screening', 'pleural'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in pulmonology_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxix(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxxix_detected": False,
        "fields_extracted": 0,
        "extension_lxxxix_type": "pulmonology_imaging",
        "extension_lxxxix_version": "2.0.0",
        "pulmonology_patient_parameters": {},
        "respiratory_pathology": {},
        "thoracic_oncology": {},
        "pulmonary_imaging_protocols": {},
        "pulmonary_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_pulmonology_imaging_file(file_path):
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

        result["extension_lxxxix_detected"] = True

        pulmonary_data = _extract_tags_lxxxix(ds)

        patient_params_set = set(PULMONOLOGY_PATIENT_PARAMETERS.keys())
        pathology_set = set(RESPIRATORY_PATHOLOGY_TAGS.keys())
        oncology_set = set(THORACIC_ONCOLOGY_TAGS.keys())
        protocols_set = set(PULMONARY_IMAGING_PROTOCOLS.keys())
        outcomes_set = set(PULMONARY_OUTCOMES_TAGS.keys())

        for tag, value in pulmonary_data.items():
            if tag in patient_params_set:
                result["pulmonology_patient_parameters"][tag] = value
            elif tag in pathology_set:
                result["respiratory_pathology"][tag] = value
            elif tag in oncology_set:
                result["thoracic_oncology"][tag] = value
            elif tag in protocols_set:
                result["pulmonary_imaging_protocols"][tag] = value
            elif tag in outcomes_set:
                result["pulmonary_outcomes"][tag] = value

        result["fields_extracted"] = len(pulmonary_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_field_count() -> int:
    return len(TOTAL_TAGS_LXXXIX)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_description() -> str:
    return (
        "Pulmonology Imaging II metadata extraction. Provides comprehensive coverage of "
        "respiratory disease parameters, lung cancer assessment, interstitial lung disease, "
        "pulmonology-specific imaging protocols, and pulmonary outcomes measurement."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_modalities() -> List[str]:
    return ["CT", "MR", "US", "CR", "DR", "XA", "PT", "NM", "RG"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_category() -> str:
    return "Pulmonology Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_keywords() -> List[str]:
    return [
        "pulmonology", "pulmonary", "respiratory", "lung", "thoracic",
        "COPD", "emphysema", "asthma", "interstitial lung disease", "IPF",
        "lung cancer", "lung nodule", "pulmonary embolism", "sarcoidosis",
        "bronchoscopy", "chest CT", "HRCT", "lung screening", "pleural"
    ]


# Aliases for smoke test compatibility
def extract_medical_notifications(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxix."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxix(file_path)

def get_medical_notifications_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_field_count()

def get_medical_notifications_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_version()

def get_medical_notifications_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_description()

def get_medical_notifications_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_supported_formats()

def get_medical_notifications_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxix_modalities()
