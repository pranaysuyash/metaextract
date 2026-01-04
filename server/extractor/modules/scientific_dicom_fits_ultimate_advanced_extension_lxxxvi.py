"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXXVI - Women's Imaging II

This module provides comprehensive extraction of Women's Imaging parameters
including breast imaging, gynecological imaging, obstetric imaging, and
women's health-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXVI_AVAILABLE = True

WOMENS_IMAGING_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0xL001): "womens_imaging_assessment_date",
    (0x0010, 0xL002): "breast_diagnosis",
    (0x0010, 0xL003): "breast_cancer_indicator",
    (0x0010, 0xL004): "dcis_indicator",
    (0x0010, 0xL005): "invasive_ductal_carcinoma",
    (0x0010, 0xL006): "invasive_lobular",
    (0x0010, 0xL007): "estrogen_receptor",
    (0x0010, 0xL008): "progesterone_receptor",
    (0x0010, 0xL009): "her2_status",
    (0x0010, 0xL010): "triple_negative",
    (0x0010, 0xL011): "ki67_index",
    (0x0010, 0xL012): "oncotype_dx",
    (0x0010, 0xL013): "mammaprint",
    (0x0010, 0xL014): "breast_density",
    (0x0010, 0xL015): "dense_breast",
    (0x0010, 0xL016): "heterogeneously_dense",
    (0x0010, 0xL017): "scattered_density",
    (0x0010, 0xL018): "almost entirely fatty",
    (0x0010, 0xL019): "fibrocystic_change",
    (0x0010, 0xL020): "fibroadenoma",
    (0x0010, 0xL021): "cystic_change",
    (0x0010, 0xL022): "papilloma",
    (0x0010, 0xL023): "radial_scar",
    (0x0010, 0xL024): "gynecological_diagnosis",
    (0x0010, 0xL025): "uterine_fibroid",
    (0x0010, 0xL026): "endometriosis",
    (0x0010, 0xL027): "polycystic_ovary",
    (0x0010, 0xL028): "ovarian_cyst",
    (0x0010, 0xL029): "ovarian_cancer",
    (0x0010, 0xL030): "uterine_cancer",
    (0x0010, 0xL031): "endometrial_cancer",
    (0x0010, 0xL032): "cervical_cancer",
    (0x0010, 0xL033): "vaginal_cancer",
    (0x0010, 0xL034): "vulvar_cancer",
    (0x0010, 0xL035): "pelvic_mass",
    (0x0010, 0xL036): "adenomyosis",
    (0x0010, 0xL037): "endometrial_polyp",
    (0x0010, 0xL038): "endometrial_hyperplasia",
    (0x0010, 0xL039): "obstetric_history",
    (0x0010, 0xL040): "gravidity",
    (0x0010, 0xL041): "parity",
    (0x0010, 0xL042): "last_menstrual_period",
    (0x0010, 0xL043): "estimated_due_date",
    (0x0010, 0xL044): "gestational_age_weeks",
    (0x0010, 0xL045): "trimester",
    (0x0010, 0xL046): "high_risk_pregnancy",
    (0x0010, 0xL047): "gestational_diabetes",
    (0x0010, 0xL048): "preeclampsia",
    (0x0010, 0xL049): "placenta_previa",
    (0x0010, 0xL050): "placental_abruption",
    (0x0010, 0xL051): "fetal_anomaly",
    (0x0010, 0xL052): "intrauterine_growth",
    (0x0010, 0xL053): "fetal_position",
    (0x0010, 0xL054): "amniotic_fluid",
    (0x0010, 0xL055): "multiple_gestation",
    (0x0010, 0xL056): "twins",
    (0x0010, 0xL057): "triplets",
    (0x0010, 0xL058): "ivf_pregnancy",
    (0x0010, 0xL059): "breast_implant",
}

WOMENS_IMAGING_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xL101): "mass_breast",
    (0x0018, 0xL102): "mass_margin",
    (0x0018, 0xL103): "mass_shape",
    (0x0018, 0xL104): "mass_density",
    (0x0018, 0xL105): "calcification_breast",
    (0x0018, 0xL106): "benign_calcification",
    (0x0018, 0xL107): "suspicious_calcification",
    (0x0018, 0xL108): "amorphous_calcification",
    (0x0018, 0xL109): "heterogeneous_calcification",
    (0x0018, 0xL110): "fine_linear_calcification",
    (0x0018, 0xL111): "ductal_carcinoma_in_situ",
    (0x0018, 0xL112): "architectural_distortion",
    (0x0018, 0xL113): "asymmetry_breast",
    (0x0018, 0xL114): "global_asymmetry",
    (0x0018, 0xL115): "focal_asymmetry",
    (0x0018, 0xL116): "developing_asymmetry",
    (0x0018, 0xL117): "skin_changes",
    (0x0018, 0xL118): "skin_thickening",
    (0x0018, 0xL119): "skin_retraction",
    (0x0018, 0xL120): "nipple_changes",
    (0x0018, 0xL121): "nipple_retraction",
    (0x0018, 0xL122): "axillary_lymph_nodes",
    (0x0018, 0xL123): " intramammary_lymph",
    (0x0018, 0xL124): "uterine_size",
    (0x0018, 0xL125): "uterine_shape",
    (0x0018, 0xL126): "endometrial_thickness",
    (0x0018, 0xL127): "myometrium_heterogeneity",
    (0x0018, 0xL128): "fibroid_location",
    (0x0018, 0xL129): "fibroid_size",
    (0x0018, 0xL130): "submucosal_fibroid",
    (0x0018, 0xL131): "intramural_fibroid",
    (0x0018, 0xL132): "subserosal_fibroid",
    (0x0018, 0xL133): "ovarian_mass",
    (0x0018, 0xL134): "ovarian_cyst_character",
    (0x0018, 0xL135): "simple_cyst_ovary",
    (0x0018, 0xL136): "complex_cyst_ovary",
    (0x0018, 0xL137): "solid_mass_ovary",
    (0x0018, 0xL138): "papillary_projection",
    (0x0018, 0xL139): "septation_ovary",
    (0x0018, 0xL140): "free_fluid_pelvis",
    (0x0018, 0xL141): "adnexal_mass",
    (0x0018, 0xL142): "hydrosalpinx",
    (0x0018, 0xL143): "pelvic_endometriosis",
    (0x0018, 0xL144): "deep_infiltrating",
    (0x0018, 0xL145): "rectovaginal_nodule",
    (0x0018, 0xL146): "uterosacral_nodule",
    (0x0018, 0xL147): "bladder_nodule",
    (0x0018, 0xL148): "rectal_nodule",
    (0x0018, 0xL149): "fetal_anomaly_detail",
}

WOMENS_IMAGING_TAGS = {
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
    (0x0018, 0xL201): "screening_mammogram",
    (0x0018, 0xL202): "diagnostic_mammogram",
    (0x0018, 0xL203): "tomosynthesis",
    (0x0018, 0xL204): "digital_breast_tomo",
    (0x0018, 0xL205): "contrast_enhanced_mammo",
    (0x0018, 0xL206): "cesm_breast",
    (0x0018, 0xL207): "automated_breast_ultrasound",
    (0x0018, 0xL208): "hand_held_ultrasound",
    (0x0018, 0xL209): "elastography_breast",
    (0x0018, 0xL210): "mri_breast_protocol",
    (0x0018, 0xL211): "dynamic_contrast_breast",
    (0x0018, 0xL212): "diffusion_breast",
    (0x0018, 0xL213): "spectroscopic_breast",
    (0x0018, 0xL214): "pet_ct_breast",
    (0x0018, 0xL215): "lymphoscintigraphy",
    (0x0018, 0xL216): "sentinel_node_mapping",
    (0x0018, 0xL217): "spect_lymph",
    (0x0018, 0xL218): "transvaginal_ultrasound",
    (0x0018, 0xL219): "pelvic_ultrasound",
    (0x0018, 0xL220): "endometrial_thickness_measure",
    (0x0018, 0xL221): "sonohysterography",
    (0x0018, 0xL222): "hysterosalpingography",
    (0x0018, 0xL223): "mri_pelvis_women",
    (0x0018, 0xL224): "diffusion_pelvis",
    (0x0018, 0xL225): "dynamic_contrast_pelvis",
    (0x0018, 0xL226): "ct_pelvis_women",
    (0x0018, 0xL227): "pet_ct_gynecology",
    (0x0018, 0xL228): "obstetric_ultrasound",
    (0x0018, 0xL229): "first_trimester_scan",
    (0x0018, 0xL230): "anatomy_scan",
    (0x0018, 0xL231): "growth_scan",
    (0x0018, 0xL232): "biophysical_profile",
    (0x0018, 0xL233): "doppler_umbilical",
    (0x0018, 0xL234): "doppler_fetal",
    (0x0018, 0xL235): "middle_cerebral_artery",
    (0x0018, 0xL236): "ductus_venosus",
    (0x0018, 0xL237): "fetal_echocardiography",
    (0x0018, 0xL238): "fetal_mri",
    (0x0018, 0xL239): "fetal_brain_mri",
    (0x0018, 0xL240): "fetal_body_mri",
    (0x0018, 0xL241): "placental_mri",
    (0x0018, 0xL242): "amniocentesis_guided",
    (0x0018, 0xL243): "cvs_guided",
    (0x0018, 0xL244): "cordocentesis",
    (0x0018, 0xL245): "fetoscopic_procedures",
    (0x0018, 0xL246): "twin_transfusion",
    (0x0018, 0xL247): "selective_reduction",
    (0x0018, 0xL248): "laser_ablation_twin",
    (0x0018, 0xL249): "intrauterine_surgery",
}

WOMENS_IMAGING_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xL301): "screening_protocol",
    (0x0018, 0xL302): "annual_mammogram",
    (0x0018, 0xL303): "biennial_mammogram",
    (0x0018, 0xL304): "supplemental_screening",
    (0x0018, 0xL305): "high_risk_screening",
    (0x0018, 0xL306): "mri_screening",
    (0x0018, 0xL307): "ultrasound_screening",
    (0x0018, 0xL308): "assessment_protocol",
    (0x0018, 0xL309): "birads_classification",
    (0x0018, 0xL310): "birads_0",
    (0x0018, 0xL311): "birads_1",
    (0x0018, 0xL312): "birads_2",
    (0x0018, 0xL313): "birads_3",
    (0x0018, 0xL314): "birads_4",
    (0x0018, 0xL315): "birads_5",
    (0x0018, 0xL316): "birads_6",
    (0x0018, 0xL317): "biopsy_protocol",
    (0x0018, 0xL318): "stereotactic_biopsy",
    (0x0018, 0xL319): "ultrasound_biopsy",
    (0x0018, 0xL320): "mri_biopsy",
    (0x0018, 0xL321): "vacuum_assisted",
    (0x0018, 0xL322): "core_needle",
    (0x0018, 0xL323): "excisional_biopsy",
    (0x0018, 0xL324): "lumpectomy_planning",
    (0x0018, 0xL325): "mastectomy_planning",
    (0x0018, 0xL326): "reconstruction_planning",
    (0x0018, 0xL327): "implant_planning",
    (0x0018, 0xL328): "flap_reconstruction",
    (0x0018, 0xL329): "lymph_node_assessment",
    (0x0018, 0xL330): "axillary_dissection",
    (0x0018, 0xL331): "sentinel_node_biopsy",
    (0x0018, 0xL332): "treatment_planning",
    (0x0018, 0xL333): "radiation_therapy_breast",
    (0x0018, 0xL334): "boost_radiation",
    (0x0018, 0xL335): "partial_breast",
    (0x0018, 0xL336): "whole_breast",
    (0x0018, 0xL337): "apbi_therapy",
    (0x0018, 0xL338): "gynecologic_surgery",
    (0x0018, 0xL339): "hysterectomy_planning",
    (0x0018, 0xL340): "myomectomy_planning",
    (0x0018, 0xL341): "oophorectomy_planning",
    (0x0018, 0xL342): "endometrial_ablation",
    (0x0018, 0xL343): "uterine_sparing",
    (0x0018, 0xL344): "obstetric_procedures",
    (0x0018, 0xL345): "version_procedure",
    (0x0018, 0xL346): "external cephalic",
    (0x0018, 0xL347): "cerclage_placement",
    (0x0018, 0xL348): "amnioreduction",
    (0x0018, 0xL349): "fetoscopic_surgery",
    (0x0018, 0xL350): "prenatal_intervention",
}

WOMENS_IMAGING_OUTCOMES_TAGS = {
    (0x0018, 0xL401): "cancer_survival_women",
    (0x0018, 0xL402): "breast_cancer_survival",
    (0x0018, 0xL403): "disease_free_breast",
    (0x0018, 0xL404): "local_recurrence",
    (0x0018, 0xL405): "regional_recurrence",
    (0x0018, 0xL406): "distant_recurrence",
    (0x0018, 0xL407): "treatment_response",
    (0x0018, 0xL408): "pathologic_response",
    (0x0018, 0xL409): "complete_response",
    (0x0018, 0xL410): "partial_response",
    (0x0018, 0xL411): "cosmetic_outcome",
    (0x0018, 0xL412): "cosmetic_score",
    (0x0018, 0xL413): "symmetry_breast",
    (0x0018, 0xL414): "reconstruction_outcome",
    (0x0018, 0xL415): "implant_complication",
    (0x0018, 0xL416): "capsular_contracture",
    (0x0018, 0xL417): "lymphedema_arm",
    (0x0018, 0xL418): "arm_swelling",
    (0x0018, 0xL419): "range_of_motion",
    (0x0018, 0xL420): "pain_syndrome",
    (0x0018, 0xL421): "chronic_pain",
    (0x0018, 0xL422): "gynecologic_outcome",
    (0x0018, 0xL423): "fertility_outcome",
    (0x0018, 0xL424): "pregnancy_outcome",
    (0x0018, 0xL425): "live_birth_rate",
    (0x0018, 0xL426): "miscarriage_rate",
    (0x0018, 0xL427): "preterm_birth",
    (0x0018, 0xL428): "term_birth",
    (0x0018, 0xL429): "birth_weight_outcome",
    (0x0018, 0xL430): "apgar_outcome",
    (0x0018, 0xL431): "congenital_anomaly_rate",
    (0x0018, 0xL432): "perinatal_mortality",
    (0x0018, 0xL433): "maternal_mortality",
    (0x0018, 0xL434): "obstetric_complication",
    (0x0018, 0xL435): "hemorrhage_ob",
    (0x0018, 0xL436): "infection_ob",
    (0x0018, 0xL437): "thromboembolism_ob",
    (0x0018, 0xL438): "quality_of_life_women",
    (0x0018, 0xL439): "breast_qol",
    (0x0018, 0xL440): "sexual_health",
    (0x0018, 0xL441): "body_image",
    (0x0018, 0xL442): "psychological_impact",
    (0x0018, 0xL443): "depression_screening",
    (0x0018, 0xL444): "anxiety_screening",
    (0x0018, 0xL445): "support_services",
    (0x0018, 0xL446): "support_groups",
    (0x0018, 0xL447): "counseling_women",
    (0x0018, 0xL448): "genetic_counseling",
    (0x0018, 0xL449): "brca_testing",
    (0x0018, 0xL450): "survivorship_care",
}

TOTAL_TAGS_LXXXVI = {}

TOTAL_TAGS_LXXXVI.update(WOMENS_IMAGING_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXXVI.update(WOMENS_IMAGING_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXXVI.update(WOMENS_IMAGING_TAGS)
TOTAL_TAGS_LXXXVI.update(WOMENS_IMAGING_PROTOCOLS)
TOTAL_TAGS_LXXXVI.update(WOMENS_IMAGING_OUTCOMES_TAGS)


def _extract_tags_lxxxvi(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXXVI.items()}
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


def _is_womens_imaging_file(file_path: str) -> bool:
    women_indicators = [
        'womens', 'women', 'breast', 'mammogram', 'mammography',
        'obstetric', 'ob', 'gynecologic', 'gyn', 'pelvic',
        'uterine', 'ovarian', 'cervical', 'endometrial', 'prenatal',
        'pregnancy', 'fetal', 'birth', 'maternal', 'fetal'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in women_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxxvi_detected": False,
        "fields_extracted": 0,
        "extension_lxxxvi_type": "womens_imaging",
        "extension_lxxxvi_version": "2.0.0",
        "womens_patient_parameters": {},
        "womens_pathology": {},
        "womens_imaging": {},
        "womens_protocols": {},
        "womens_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_womens_imaging_file(file_path):
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

        result["extension_lxxxvi_detected"] = True

        women_data = _extract_tags_lxxxvi(ds)

        patient_params_set = set(WOMENS_IMAGING_PATIENT_PARAMETERS.keys())
        pathology_set = set(WOMENS_IMAGING_PATHOLOGY_TAGS.keys())
        imaging_set = set(WOMENS_IMAGING_TAGS.keys())
        protocols_set = set(WOMENS_IMAGING_PROTOCOLS.keys())
        outcomes_set = set(WOMENS_IMAGING_OUTCOMES_TAGS.keys())

        for tag, value in women_data.items():
            if tag in patient_params_set:
                result["womens_patient_parameters"][tag] = value
            elif tag in pathology_set:
                result["womens_pathology"][tag] = value
            elif tag in imaging_set:
                result["womens_imaging"][tag] = value
            elif tag in protocols_set:
                result["womens_protocols"][tag] = value
            elif tag in outcomes_set:
                result["womens_outcomes"][tag] = value

        result["fields_extracted"] = len(women_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_field_count() -> int:
    return len(TOTAL_TAGS_LXXXVI)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_description() -> str:
    return (
        "Women's Imaging II metadata extraction. Provides comprehensive coverage of "
        "breast imaging, gynecological imaging, obstetric imaging, "
        "women's health-specific imaging protocols, and women's health outcomes."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_modalities() -> List[str]:
    return ["US", "CT", "MR", "MG", "XA", "PT", "NM", "CR", "DR"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_category() -> str:
    return "Women's Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_keywords() -> List[str]:
    return [
        "women's imaging", "breast", "mammography", "obstetrics",
        "gynecology", "uterine", "ovarian", "cervical", "pregnancy",
        "fetal imaging", "prenatal", "maternal health", "pelvic MRI",
        "breast cancer", "endometriosis", "PCOS"
    ]
