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
    (0x0010, 0x1001): "womens_imaging_assessment_date",
    (0x0010, 0x1002): "breast_diagnosis",
    (0x0010, 0x1003): "breast_cancer_indicator",
    (0x0010, 0x1004): "dcis_indicator",
    (0x0010, 0x1005): "invasive_ductal_carcinoma",
    (0x0010, 0x1006): "invasive_lobular",
    (0x0010, 0x1007): "estrogen_receptor",
    (0x0010, 0x1008): "progesterone_receptor",
    (0x0010, 0x1009): "her2_status",
    (0x0010, 0x1010): "triple_negative",
    (0x0010, 0x1011): "ki67_index",
    (0x0010, 0x1012): "oncotype_dx",
    (0x0010, 0x1013): "mammaprint",
    (0x0010, 0x1014): "breast_density",
    (0x0010, 0x1015): "dense_breast",
    (0x0010, 0x1016): "heterogeneously_dense",
    (0x0010, 0x1017): "scattered_density",
    (0x0010, 0x1018): "almost entirely fatty",
    (0x0010, 0x1019): "fibrocystic_change",
    (0x0010, 0x1020): "fibroadenoma",
    (0x0010, 0x1021): "cystic_change",
    (0x0010, 0x1022): "papilloma",
    (0x0010, 0x1023): "radial_scar",
    (0x0010, 0x1024): "gynecological_diagnosis",
    (0x0010, 0x1025): "uterine_fibroid",
    (0x0010, 0x1026): "endometriosis",
    (0x0010, 0x1027): "polycystic_ovary",
    (0x0010, 0x1028): "ovarian_cyst",
    (0x0010, 0x1029): "ovarian_cancer",
    (0x0010, 0x1030): "uterine_cancer",
    (0x0010, 0x1031): "endometrial_cancer",
    (0x0010, 0x1032): "cervical_cancer",
    (0x0010, 0x1033): "vaginal_cancer",
    (0x0010, 0x1034): "vulvar_cancer",
    (0x0010, 0x1035): "pelvic_mass",
    (0x0010, 0x1036): "adenomyosis",
    (0x0010, 0x1037): "endometrial_polyp",
    (0x0010, 0x1038): "endometrial_hyperplasia",
    (0x0010, 0x1039): "obstetric_history",
    (0x0010, 0x1040): "gravidity",
    (0x0010, 0x1041): "parity",
    (0x0010, 0x1042): "last_menstrual_period",
    (0x0010, 0x1043): "estimated_due_date",
    (0x0010, 0x1044): "gestational_age_weeks",
    (0x0010, 0x1045): "trimester",
    (0x0010, 0x1046): "high_risk_pregnancy",
    (0x0010, 0x1047): "gestational_diabetes",
    (0x0010, 0x1048): "preeclampsia",
    (0x0010, 0x1049): "placenta_previa",
    (0x0010, 0x1050): "placental_abruption",
    (0x0010, 0x1051): "fetal_anomaly",
    (0x0010, 0x1052): "intrauterine_growth",
    (0x0010, 0x1053): "fetal_position",
    (0x0010, 0x1054): "amniotic_fluid",
    (0x0010, 0x1055): "multiple_gestation",
    (0x0010, 0x1056): "twins",
    (0x0010, 0x1057): "triplets",
    (0x0010, 0x1058): "ivf_pregnancy",
    (0x0010, 0x1059): "breast_implant",
}

WOMENS_IMAGING_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x1101): "mass_breast",
    (0x0018, 0x1102): "mass_margin",
    (0x0018, 0x1103): "mass_shape",
    (0x0018, 0x1104): "mass_density",
    (0x0018, 0x1105): "calcification_breast",
    (0x0018, 0x1106): "benign_calcification",
    (0x0018, 0x1107): "suspicious_calcification",
    (0x0018, 0x1108): "amorphous_calcification",
    (0x0018, 0x1109): "heterogeneous_calcification",
    (0x0018, 0x1110): "fine_linear_calcification",
    (0x0018, 0x1111): "ductal_carcinoma_in_situ",
    (0x0018, 0x1112): "architectural_distortion",
    (0x0018, 0x1113): "asymmetry_breast",
    (0x0018, 0x1114): "global_asymmetry",
    (0x0018, 0x1115): "focal_asymmetry",
    (0x0018, 0x1116): "developing_asymmetry",
    (0x0018, 0x1117): "skin_changes",
    (0x0018, 0x1118): "skin_thickening",
    (0x0018, 0x1119): "skin_retraction",
    (0x0018, 0x1120): "nipple_changes",
    (0x0018, 0x1121): "nipple_retraction",
    (0x0018, 0x1122): "axillary_lymph_nodes",
    (0x0018, 0x1123): " intramammary_lymph",
    (0x0018, 0x1124): "uterine_size",
    (0x0018, 0x1125): "uterine_shape",
    (0x0018, 0x1126): "endometrial_thickness",
    (0x0018, 0x1127): "myometrium_heterogeneity",
    (0x0018, 0x1128): "fibroid_location",
    (0x0018, 0x1129): "fibroid_size",
    (0x0018, 0x1130): "submucosal_fibroid",
    (0x0018, 0x1131): "intramural_fibroid",
    (0x0018, 0x1132): "subserosal_fibroid",
    (0x0018, 0x1133): "ovarian_mass",
    (0x0018, 0x1134): "ovarian_cyst_character",
    (0x0018, 0x1135): "simple_cyst_ovary",
    (0x0018, 0x1136): "complex_cyst_ovary",
    (0x0018, 0x1137): "solid_mass_ovary",
    (0x0018, 0x1138): "papillary_projection",
    (0x0018, 0x1139): "septation_ovary",
    (0x0018, 0x1140): "free_fluid_pelvis",
    (0x0018, 0x1141): "adnexal_mass",
    (0x0018, 0x1142): "hydrosalpinx",
    (0x0018, 0x1143): "pelvic_endometriosis",
    (0x0018, 0x1144): "deep_infiltrating",
    (0x0018, 0x1145): "rectovaginal_nodule",
    (0x0018, 0x1146): "uterosacral_nodule",
    (0x0018, 0x1147): "bladder_nodule",
    (0x0018, 0x1148): "rectal_nodule",
    (0x0018, 0x1149): "fetal_anomaly_detail",
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
    (0x0018, 0x1201): "screening_mammogram",
    (0x0018, 0x1202): "diagnostic_mammogram",
    (0x0018, 0x1203): "tomosynthesis",
    (0x0018, 0x1204): "digital_breast_tomo",
    (0x0018, 0x1205): "contrast_enhanced_mammo",
    (0x0018, 0x1206): "cesm_breast",
    (0x0018, 0x1207): "automated_breast_ultrasound",
    (0x0018, 0x1208): "hand_held_ultrasound",
    (0x0018, 0x1209): "elastography_breast",
    (0x0018, 0x1210): "mri_breast_protocol",
    (0x0018, 0x1211): "dynamic_contrast_breast",
    (0x0018, 0x1212): "diffusion_breast",
    (0x0018, 0x1213): "spectroscopic_breast",
    (0x0018, 0x1214): "pet_ct_breast",
    (0x0018, 0x1215): "lymphoscintigraphy",
    (0x0018, 0x1216): "sentinel_node_mapping",
    (0x0018, 0x1217): "spect_lymph",
    (0x0018, 0x1218): "transvaginal_ultrasound",
    (0x0018, 0x1219): "pelvic_ultrasound",
    (0x0018, 0x1220): "endometrial_thickness_measure",
    (0x0018, 0x1221): "sonohysterography",
    (0x0018, 0x1222): "hysterosalpingography",
    (0x0018, 0x1223): "mri_pelvis_women",
    (0x0018, 0x1224): "diffusion_pelvis",
    (0x0018, 0x1225): "dynamic_contrast_pelvis",
    (0x0018, 0x1226): "ct_pelvis_women",
    (0x0018, 0x1227): "pet_ct_gynecology",
    (0x0018, 0x1228): "obstetric_ultrasound",
    (0x0018, 0x1229): "first_trimester_scan",
    (0x0018, 0x1230): "anatomy_scan",
    (0x0018, 0x1231): "growth_scan",
    (0x0018, 0x1232): "biophysical_profile",
    (0x0018, 0x1233): "doppler_umbilical",
    (0x0018, 0x1234): "doppler_fetal",
    (0x0018, 0x1235): "middle_cerebral_artery",
    (0x0018, 0x1236): "ductus_venosus",
    (0x0018, 0x1237): "fetal_echocardiography",
    (0x0018, 0x1238): "fetal_mri",
    (0x0018, 0x1239): "fetal_brain_mri",
    (0x0018, 0x1240): "fetal_body_mri",
    (0x0018, 0x1241): "placental_mri",
    (0x0018, 0x1242): "amniocentesis_guided",
    (0x0018, 0x1243): "cvs_guided",
    (0x0018, 0x1244): "cordocentesis",
    (0x0018, 0x1245): "fetoscopic_procedures",
    (0x0018, 0x1246): "twin_transfusion",
    (0x0018, 0x1247): "selective_reduction",
    (0x0018, 0x1248): "laser_ablation_twin",
    (0x0018, 0x1249): "intrauterine_surgery",
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
    (0x0018, 0x1301): "screening_protocol",
    (0x0018, 0x1302): "annual_mammogram",
    (0x0018, 0x1303): "biennial_mammogram",
    (0x0018, 0x1304): "supplemental_screening",
    (0x0018, 0x1305): "high_risk_screening",
    (0x0018, 0x1306): "mri_screening",
    (0x0018, 0x1307): "ultrasound_screening",
    (0x0018, 0x1308): "assessment_protocol",
    (0x0018, 0x1309): "birads_classification",
    (0x0018, 0x1310): "birads_0",
    (0x0018, 0x1311): "birads_1",
    (0x0018, 0x1312): "birads_2",
    (0x0018, 0x1313): "birads_3",
    (0x0018, 0x1314): "birads_4",
    (0x0018, 0x1315): "birads_5",
    (0x0018, 0x1316): "birads_6",
    (0x0018, 0x1317): "biopsy_protocol",
    (0x0018, 0x1318): "stereotactic_biopsy",
    (0x0018, 0x1319): "ultrasound_biopsy",
    (0x0018, 0x1320): "mri_biopsy",
    (0x0018, 0x1321): "vacuum_assisted",
    (0x0018, 0x1322): "core_needle",
    (0x0018, 0x1323): "excisional_biopsy",
    (0x0018, 0x1324): "lumpectomy_planning",
    (0x0018, 0x1325): "mastectomy_planning",
    (0x0018, 0x1326): "reconstruction_planning",
    (0x0018, 0x1327): "implant_planning",
    (0x0018, 0x1328): "flap_reconstruction",
    (0x0018, 0x1329): "lymph_node_assessment",
    (0x0018, 0x1330): "axillary_dissection",
    (0x0018, 0x1331): "sentinel_node_biopsy",
    (0x0018, 0x1332): "treatment_planning",
    (0x0018, 0x1333): "radiation_therapy_breast",
    (0x0018, 0x1334): "boost_radiation",
    (0x0018, 0x1335): "partial_breast",
    (0x0018, 0x1336): "whole_breast",
    (0x0018, 0x1337): "apbi_therapy",
    (0x0018, 0x1338): "gynecologic_surgery",
    (0x0018, 0x1339): "hysterectomy_planning",
    (0x0018, 0x1340): "myomectomy_planning",
    (0x0018, 0x1341): "oophorectomy_planning",
    (0x0018, 0x1342): "endometrial_ablation",
    (0x0018, 0x1343): "uterine_sparing",
    (0x0018, 0x1344): "obstetric_procedures",
    (0x0018, 0x1345): "version_procedure",
    (0x0018, 0x1346): "external cephalic",
    (0x0018, 0x1347): "cerclage_placement",
    (0x0018, 0x1348): "amnioreduction",
    (0x0018, 0x1349): "fetoscopic_surgery",
    (0x0018, 0x1350): "prenatal_intervention",
}

WOMENS_IMAGING_OUTCOMES_TAGS = {
    (0x0018, 0x1401): "cancer_survival_women",
    (0x0018, 0x1402): "breast_cancer_survival",
    (0x0018, 0x1403): "disease_free_breast",
    (0x0018, 0x1404): "local_recurrence",
    (0x0018, 0x1405): "regional_recurrence",
    (0x0018, 0x1406): "distant_recurrence",
    (0x0018, 0x1407): "treatment_response",
    (0x0018, 0x1408): "pathologic_response",
    (0x0018, 0x1409): "complete_response",
    (0x0018, 0x1410): "partial_response",
    (0x0018, 0x1411): "cosmetic_outcome",
    (0x0018, 0x1412): "cosmetic_score",
    (0x0018, 0x1413): "symmetry_breast",
    (0x0018, 0x1414): "reconstruction_outcome",
    (0x0018, 0x1415): "implant_complication",
    (0x0018, 0x1416): "capsular_contracture",
    (0x0018, 0x1417): "lymphedema_arm",
    (0x0018, 0x1418): "arm_swelling",
    (0x0018, 0x1419): "range_of_motion",
    (0x0018, 0x1420): "pain_syndrome",
    (0x0018, 0x1421): "chronic_pain",
    (0x0018, 0x1422): "gynecologic_outcome",
    (0x0018, 0x1423): "fertility_outcome",
    (0x0018, 0x1424): "pregnancy_outcome",
    (0x0018, 0x1425): "live_birth_rate",
    (0x0018, 0x1426): "miscarriage_rate",
    (0x0018, 0x1427): "preterm_birth",
    (0x0018, 0x1428): "term_birth",
    (0x0018, 0x1429): "birth_weight_outcome",
    (0x0018, 0x1430): "apgar_outcome",
    (0x0018, 0x1431): "congenital_anomaly_rate",
    (0x0018, 0x1432): "perinatal_mortality",
    (0x0018, 0x1433): "maternal_mortality",
    (0x0018, 0x1434): "obstetric_complication",
    (0x0018, 0x1435): "hemorrhage_ob",
    (0x0018, 0x1436): "infection_ob",
    (0x0018, 0x1437): "thromboembolism_ob",
    (0x0018, 0x1438): "quality_of_life_women",
    (0x0018, 0x1439): "breast_qol",
    (0x0018, 0x1440): "sexual_health",
    (0x0018, 0x1441): "body_image",
    (0x0018, 0x1442): "psychological_impact",
    (0x0018, 0x1443): "depression_screening",
    (0x0018, 0x1444): "anxiety_screening",
    (0x0018, 0x1445): "support_services",
    (0x0018, 0x1446): "support_groups",
    (0x0018, 0x1447): "counseling_women",
    (0x0018, 0x1448): "genetic_counseling",
    (0x0018, 0x1449): "brca_testing",
    (0x0018, 0x1450): "survivorship_care",
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


# Aliases for smoke test compatibility
def extract_medical_monitoring(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi(file_path)

def get_medical_monitoring_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_field_count()

def get_medical_monitoring_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_version()

def get_medical_monitoring_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_description()

def get_medical_monitoring_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_supported_formats()

def get_medical_monitoring_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvi_modalities()
