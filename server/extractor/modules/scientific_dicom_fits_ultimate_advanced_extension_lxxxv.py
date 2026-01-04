"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXXV - Pediatric Imaging II

This module provides comprehensive extraction of Pediatric Imaging parameters
including developmental disorders, congenital anomalies, pediatric oncology, and
pediatric-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXV_AVAILABLE = True

PEDIATRIC_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x8010): "pediatric_assessment_date",
    (0x0010, 0x8011): "age_in_months",
    (0x0010, 0x8012): "gestational_age",
    (0x0010, 0x8013): "birth_weight",
    (0x0010, 0x8014): "apgar_score",
    (0x0010, 0x8015): "developmental_milestone",
    (0x0010, 0x8016): "growth_percentile",
    (0x0010, 0x8017): "weight_percentile",
    (0x0010, 0x8018): "height_percentile",
    (0x0010, 0x8019): "head_circumference",
    (0x0010, 0x8020): "bmi_percentile",
    (0x0010, 0x8021): "failure_to_thrive",
    (0x0010, 0x8022): "congenital_anomaly",
    (0x0010, 0x8023): "chromosomal_abnormality",
    (0x0010, 0x8024): "trisomy_21",
    (0x0010, 0x8025): "trisomy_18",
    (0x0010, 0x8026): "trisomy_13",
    (0x0010, 0x8027): "turner_syndrome",
    (0x0010, 0x8028): "klinefelter_syndrome",
    (0x0010, 0x8029): "cystic_fibrosis",
    (0x0010, 0x8030): "congenital_heart_disease",
    (0x0010, 0x8031): "ventricular_septal_defect",
    (0x0010, 0x8032): "atrial_septal_defect",
    (0x0010, 0x8033): "tetralogy_of_fallot",
    (0x0010, 0x8034): "hypoplastic_left_heart",
    (0x0010, 0x8035): "pediatric_oncology",
    (0x0010, 0x8036): "acute_lymphoblastic_leukemia",
    (0x0010, 0x8037): "acute_myeloid_leukemia",
    (0x0010, 0x8029): "neuroblastoma",
    (0x0010, 0x8040): "wilmstumor",
    (0x0010, 0x8041): "rhabdomyosarcoma",
    (0x0010, 0x8042): "ewing_sarcoma",
    (0x0010, 0x8043): "osteosarcoma_pediatric",
    (0x0010, 0x8044): "brain_tumor_pediatric",
    (0x0010, 0x8045): "medulloblastoma",
    (0x0010, 0x8046): "astrocytoma_pediatric",
    (0x0010, 0x8047): "craniopharyngioma",
    (0x0010, 0x8048): "pediatric_lymphoma",
    (0x0010, 0x8049): "infection_pediatric",
    (0x0010, 0x8050): "sepsis_pediatric",
    (0x0010, 0x8051): "meningitis_pediatric",
    (0x0010, 0x8052): "pneumonia_pediatric",
    (0x0010, 0x8053): "gastroenteritis",
    (0x0010, 0x8054): "appendicitis_pediatric",
    (0x0010, 0x8055): "intussusception",
    (0x0010, 0x8056): "pyloric_stenosis",
    (0x0010, 0x8057): "hirschsprung_disease",
    (0x0010, 0x8058): "malrotation",
    (0x0010, 0x8059): "trauma_pediatric",
    (0x0010, 0x8060): "non_accidental_trauma",
    (0x0010, 0x8061): "child_abuse",
    (0x0010, 0x8062): "bone_fracture_pediatric",
    (0x0010, 0x8063): "head_injury_pediatric",
    (0x0010, 0x8064): "skeletal_dysplasia",
    (0x0010, 0x8065): "achondroplasia",
    (0x0010, 0x8066): "osteogenesis_imperfecta",
    (0x0010, 0x8067): "metabolic_bone_disease",
    (0x0010, 0x8068): "rickets_pediatric",
    (0x0010, 0x8069): "scoliosis_pediatric",
}

PEDIATRIC_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x8101): "bone_age_assessment",
    (0x0018, 0x8102): "bone_age_deviation",
    (0x0018, 0x8103): "greulich_pyle_pediatric",
    (0x0018, 0x8104): "tanner_whitehouse",
    (0x0018, 0x8105): "RUS_score",
    (0x0018, 0x8106): "carpal_score",
    (0x0018, 0x8107): "growth_plate_status",
    (0x0018, 0x8108): "physeal_closure",
    (0x0018, 0x8109): "epiphyseal_plate",
    (0x0018, 0x8110): "congenital_malformation",
    (0x0018, 0x8111): "dysraphism",
    (0x0018, 0x8112): "spina_bifida",
    (0x0018, 0x8113): "encephalocele",
    (0x0018, 0x8114): "hydrocephalus",
    (0x0018, 0x8115): "ventriculomegaly",
    (0x0018, 0x8116): "corpus_callosum_agenesis",
    (0x0018, 0x8117): "chiari_malformation",
    (0x0018, 0x8118): "dandy_walker",
    (0x0018, 0x8119): "cystic_malformation",
    (0x0018, 0x8120): "cardiac_shunt",
    (0x0018, 0x8121): "left_to_right_shunt",
    (0x0018, 0x8122): "right_to_left_shunt",
    (0x0018, 0x8123): "obstructive_lesion",
    (0x0018, 0x8124): "regurgitant_lesion",
    (0x0018, 0x8125): "tumor_markers_pediatric",
    (0x0018, 0x8126): "afp_level_pediatric",
    (0x0018, 0x8127): "hcg_level_pediatric",
    (0x0018, 0x8128): "ldh_level_pediatric",
    (0x0018, 0x8129): "vanillylmandelic_acid",
    (0x0018, 0x8130): "homovanillic_acid",
    (0x0018, 0x8131): "mass_effect_pediatric",
    (0x0018, 0x8132): "midline_shift_pediatric",
    (0x0018, 0x8133): "hydrocephalus_pediatric",
    (0x0018, 0x8134): "peritumoral_edema_pediatric",
    (0x0018, 0x8135): "metastasis_pediatric",
    (0x0018, 0x8136): "leptomeningeal_disease",
    (0x0018, 0x8137): "intussusception_target",
    (0x0018, 0x8138): "bowel_wall_thickening",
    (0x0018, 0x8139): "free_air_pediatric",
    (0x0018, 0x8140): "appendiceal_diameter",
    (0x0018, 0x8141): "appendiceal_wall",
    (0x0018, 0x8142): "periappendiceal_fluid",
    (0x0018, 0x8143): "phlegmon_pediatric",
    (0x0018, 0x8144): "abscess_pediatric",
    (0x0018, 0x8145): "pneumoperitoneum",
    (0x0018, 0x8146): "meconium_ileus",
    (0x0018, 0x8147): "meconium_plug",
    (0x0018, 0x8148): "hirschsprung_transition",
    (0x0018, 0x8149): "fracture_pattern_pediatric",
}

PEDIATRIC_IMAGING_TAGS = {
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
    (0x0018, 0x8201): "neonatal_brain_mri",
    (0x0018, 0x8202): "diffusion_tensor_infant",
    (0x0018, 0x8203): "functional_infant_mri",
    (0x0018, 0x8204): "spectroscopy_infant",
    (0x0018, 0x8205): "cranial_ultrasound",
    (0x0018, 0x8206): "anterior_fontanelle",
    (0x0018, 0x8207): "posterior_fontanelle",
    (0x0018, 0x8208): "temporal_window",
    (0x0018, 0x8209): "hip_ultrasound",
    (0x0018, 0x8210): "graf_method",
    (0x0018, 0x8211): "alpha_angle",
    (0x0018, 0x8212): "beta_angle",
    (0x0018, 0x8213): "pediatric_ct_protocol",
    (0x0018, 0x8214): "low_dose_pediatric",
    (0x0018, 0x8215): "weight_based_protocol",
    (0x0018, 0x8216): "age_adjusted_ct",
    (0x0018, 0x8217): "pediatric_mri_protocol",
    (0x0018, 0x8218): "sedation_mri",
    (0x0018, 0x8219): "feed_and_wrap",
    (0x0018, 0x8220): "play_therapy_mri",
    (0x0018, 0x8221): "motion_reduction",
    (0x0018, 0x8222): "fast_imaging_pediatric",
    (0x0018, 0x8223): "pet_ct_pediatric",
    (0x0018, 0x8224): "mibg_pediatric",
    (0x0018, 0x8225): "octreotide_pediatric",
    (0x0018, 0x8226): "bone_scan_pediatric",
    (0x0018, 0x8227): "gallium_pediatric",
    (0x0018, 0x8228): "ultrasound_pediatric",
    (0x0018, 0x8229): "contrast_enhanced_ultrasound",
    (0x0018, 0x8230): "fluoroscopy_pediatric",
    (0x0018, 0x8231): "upper_gi_series",
    (0x0018, 0x8232): "lower_gi_series",
    (0x0018, 0x8233): "voiding_cystourethrogram",
    (0x0018, 0x8234): "micturating_cytogram",
    (0x0018, 0x8235): "contrast_enema",
    (0x0018, 0x8236): "barium_swallow",
    (0x0018, 0x8237): "video_fluoroscopy",
    (0x0018, 0x8238): "swallowing_study",
    (0x0018, 0x8239): "interventional_pediatric",
    (0x0018, 0x8240): "biopsy_pediatric",
    (0x0018, 0x8241): "drainage_pediatric",
    (0x0018, 0x8242): "line_placement",
    (0x0018, 0x8243): "port_placement",
    (0x0018, 0x8244): "gastrostomy_tube",
    (0x0018, 0x8245): "jejunostomy_tube",
    (0x0018, 0x8246): "radiotherapy_pediatric",
    (0x0018, 0x8247): "proton_therapy_pediatric",
    (0x0018, 0x8248): "brachytherapy_pediatric",
    (0x0018, 0x8249): "stereotactic_pediatric",
}

PEDIATRIC_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x8301): "screening_protocol",
    (0x0018, 0x8302): "prenatal_screening",
    (0x0018, 0x8303): "prenatal_ultrasound",
    (0x0018, 0x8304): "fetal_mri",
    (0x0018, 0x8305): "newborn_screening",
    (0x0018, 0x8306): "metabolic_screening",
    (0x0018, 0x8307): "hip_screening",
    (0x0018, 0x8308): "hearing_screening",
    (0x0018, 0x8309): "vision_screening",
    (0x0018, 0x8310): "cancer_screening",
    (0x0018, 0x8311): "surveillance_imaging",
    (0x0018, 0x8312): "response_assessment",
    (0x0018, 0x8313): "treatment_planning",
    (0x0018, 0x8314): "chemotherapy_protocol",
    (0x0018, 0x8315): "radiation_planning",
    (0x0018, 0x8316): "surgery_planning",
    (0x0018, 0x8317): "transplant_planning",
    (0x0018, 0x8318): "stem_cell_transplant",
    (0x0018, 0x8319): "bone_marrow_transplant",
    (0x0018, 0x8320): "radiation_therapy",
    (0x0018, 0x8321): "target_volume_pediatric",
    (0x0018, 0x8322): "organ_sparing",
    (0x0018, 0x8323): "growth_consideration",
    (0x0018, 0x8324): "late_effects",
    (0x0018, 0x8325): "cardiac_sparing",
    (0x0018, 0x8326): "pulmonary_sparing",
    (0x0018, 0x8327): "renal_sparing",
    (0x0018, 0x8328): "hormonal_sparing",
    (0x0018, 0x8329): "fertility_preservation",
    (0x0018, 0x8330): "gamete_preservation",
    (0x0018, 0x8331): "tissue_preservation",
    (0x0018, 0x8332): "growth_hormone_therapy",
    (0x0018, 0x8333): "endocrine_replacement",
    (0x0018, 0x8334): "transition_care",
    (0x0018, 0x8335): "adolescent_medicine",
    (0x0018, 0x8336): "family_centered_care",
    (0x0018, 0x8337): "play_therapy",
    (0x0018, 0x8338): "child_life_specialist",
    (0x0018, 0x8339): "distraction_techniques",
    (0x0018, 0x8340): "virtual_reality",
    (0x0018, 0x8341): "simulation_training",
    (0x0018, 0x8342): "parental_involvement",
    (0x0018, 0x8343): "informed_consent_pediatric",
    (0x0018, 0x8344): "assent_pediatric",
    (0x0018, 0x8345): "ethical_considerations",
    (0x0018, 0x8346): "research_protocols",
    (0x0018, 0x8347): "clinical_trials",
    (0x0018, 0x8348): "long_term_followup",
    (0x0018, 0x8349): "survivorship_care",
    (0x0018, 0x8350): "late_monitoring",
}

PEDIATRIC_OUTCOMES_TAGS = {
    (0x0018, 0x8401): "survival_pediatric",
    (0x0018, 0x8402): "event_free_survival",
    (0x0018, 0x8403): "disease_free_survival",
    (0x0018, 0x8404): "overall_survival_pediatric",
    (0x0018, 0x8405): "treatment_response_ped",
    (0x0018, 0x8406): "complete_remission",
    (0x0018, 0x8407): "partial_remission",
    (0x0018, 0x8408): "relapse_pediatric",
    (0x0018, 0x8409): "refractory_disease",
    (0x0018, 0x8410): "toxicity_grade_pediatric",
    (0x0018, 0x8411): "hematologic_toxicity",
    (0x0018, 0x8412): "non_hematologic_toxicity",
    (0x0018, 0x8413): "organ_toxicity",
    (0x0018, 0x8414): "cardiotoxicity_pediatric",
    (0x0018, 0x8415): "nephrotoxicity_pediatric",
    (0x0018, 0x8416): "neurotoxicity_pediatric",
    (0x0018, 0x8417): "ototoxicity_pediatric",
    (0x0018, 0x8418): "growth_deficiency",
    (0x0018, 0x8419): "growth_hormone_deficiency",
    (0x0018, 0x8420): "pubertal_delay",
    (0x0018, 0x8421): "cognitive_outcome",
    (0x0018, 0x8422): "neurocognitive",
    (0x0018, 0x8423): "learning_disability",
    (0x0018, 0x8424): "developmental_delay",
    (0x0018, 0x8425): "functional_status",
    (0x0018, 0x8426): "activities_daily_living",
    (0x0018, 0x8427): "mobility_pediatric",
    (0x0018, 0x8428): "quality_of_life_ped",
    (0x0018, 0x8429): "peds_qol",
    (0x0018, 0x8430): "child_health_qol",
    (0x0018, 0x8431): "family_impact",
    (0x0018, 0x8432): "parent_stress",
    (0x0018, 0x8433): "sibling_outcome",
    (0x0018, 0x8434): "school_performance",
    (0x0018, 0x8435): "social_outcome",
    (0x0018, 0x8436): "peer_relationships",
    (0x0018, 0x8437): "transition_adulthood",
    (0x0018, 0x8438): "independent_living",
    (0x0018, 0x8439): "employment_pediatric",
    (0x0018, 0x8440): "fertility_outcome",
    (0x0018, 0x8441): "reproductive_health",
    (0x0018, 0x8442): "second_malignancy",
    (0x0018, 0x8443): "late_mortality",
    (0x0018, 0x8444): "cause_of_death",
    (0x0018, 0x8445): "palliative_care",
    (0x0018, 0x8446): "end_of_life",
    (0x0018, 0x8447): "bereavement_support",
    (0x0018, 0x8448): "psychosocial_support",
    (0x0018, 0x8449): "support_services",
    (0x0018, 0x8450): "follow_up_adherence",
}

TOTAL_TAGS_LXXXV = {}

TOTAL_TAGS_LXXXV.update(PEDIATRIC_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXXV.update(PEDIATRIC_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXXV.update(PEDIATRIC_IMAGING_TAGS)
TOTAL_TAGS_LXXXV.update(PEDIATRIC_PROTOCOLS)
TOTAL_TAGS_LXXXV.update(PEDIATRIC_OUTCOMES_TAGS)


def _extract_tags_lxxxv(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXXV.items()}
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


def _is_pediatric_imaging_file(file_path: str) -> bool:
    ped_indicators = [
        'pediatric', 'pediatrics', 'child', 'children', 'infant',
        'neonatal', 'newborn', 'adolescent', 'teenager', 'fetal',
        'prenatal', 'congenital', 'developmental', 'bone_age',
        'pediatric_oncology', 'childhood_cancer', 'peds'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in ped_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxv(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxxv_detected": False,
        "fields_extracted": 0,
        "extension_lxxxv_type": "pediatric_imaging",
        "extension_lxxxv_version": "2.0.0",
        "pediatric_patient_parameters": {},
        "pediatric_pathology": {},
        "pediatric_imaging": {},
        "pediatric_protocols": {},
        "pediatric_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_pediatric_imaging_file(file_path):
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

        result["extension_lxxxv_detected"] = True

        ped_data = _extract_tags_lxxxv(ds)

        patient_params_set = set(PEDIATRIC_PATIENT_PARAMETERS.keys())
        pathology_set = set(PEDIATRIC_PATHOLOGY_TAGS.keys())
        imaging_set = set(PEDIATRIC_IMAGING_TAGS.keys())
        protocols_set = set(PEDIATRIC_PROTOCOLS.keys())
        outcomes_set = set(PEDIATRIC_OUTCOMES_TAGS.keys())

        for tag, value in ped_data.items():
            if tag in patient_params_set:
                result["pediatric_patient_parameters"][tag] = value
            elif tag in pathology_set:
                result["pediatric_pathology"][tag] = value
            elif tag in imaging_set:
                result["pediatric_imaging"][tag] = value
            elif tag in protocols_set:
                result["pediatric_protocols"][tag] = value
            elif tag in outcomes_set:
                result["pediatric_outcomes"][tag] = value

        result["fields_extracted"] = len(ped_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxv_field_count() -> int:
    return len(TOTAL_TAGS_LXXXV)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxv_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxv_description() -> str:
    return (
        "Pediatric Imaging II metadata extraction. Provides comprehensive coverage of "
        "developmental disorders, congenital anomalies, pediatric oncology, "
        "pediatric-specific imaging protocols, and pediatric outcomes assessment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxv_modalities() -> List[str]:
    return ["US", "CT", "MR", "CR", "DR", "XA", "PT", "NM", "RG"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxv_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxv_category() -> str:
    return "Pediatric Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxv_keywords() -> List[str]:
    return [
        "pediatric", "children", "infant", "newborn", "neonatal",
        "adolescent", "fetal", "congenital", "developmental",
        "bone age", "pediatric oncology", "childhood cancer",
        "congenital anomalies", "prenatal imaging", "pediatric MRI"
    ]
