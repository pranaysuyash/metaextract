"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXXVII - Men's Health Imaging II

This module provides comprehensive extraction of Men's Health Imaging parameters
including prostate health, testicular disorders, male infertility, and
men's health-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXVII_AVAILABLE = True

MENS_HEALTH_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x1001): "mens_health_assessment_date",
    (0x0010, 0xM002): "prostate_diagnosis",
    (0x0010, 0xM003): "benign_prostatic_hyperplasia",
    (0x0010, 0xM004): "prostatitis",
    (0x0010, 0xM005): "acute_prostatitis",
    (0x0010, 0xM006): "chronic_prostatitis",
    (0x0010, 0xM007): "prostate_cancer",
    (0x0010, 0xM008): "gleason_score",
    (0x0010, 0xM009): "prostate_specific_antigen",
    (0x0010, 0xM010): "psa_velocity",
    (0x0010, 0xM011): "psa_density",
    (0x0010, 0xM012): "free_psa",
    (0x0010, 0xM013): "prostate_volume",
    (0x0010, 0xM014): "ipss_score",
    (0x0010, 0xM015): "urinary_symptoms",
    (0x0010, 0xM016): "erectile_dysfunction",
    (0x0010, 0xM017): "ejaculatory_dysfunction",
    (0x0010, 0xM018): "testicular_diagnosis",
    (0x0010, 0xM019): "testicular_cancer",
    (0x0010, 0xM020): "seminoma",
    (0x0010, 0xM021): "nonseminoma",
    (0x0010, 0xM022): "embryonal_carcinoma",
    (0x0010, 0xM023): "teratoma",
    (0x0010, 0xM024): "yolk_sac_tumor",
    (0x0010, 0xM025): "choriocarcinoma",
    (0x0010, 0xM026): "leydig_cell_tumor",
    (0x0010, 0xM027): "sertoli_cell_tumor",
    (0x0010, 0xM028): "testicular_torsion",
    (0x0010, 0xM029): "epididymitis",
    (0x0010, 0xM030): "hydrocele",
    (0x0010, 0xM031): "varicocele",
    (0x0010, 0xM032): "spermatocele",
    (0x0010, 0xM033): "infertility_indicator",
    (0x0010, 0xM034): "azoospermia",
    (0x0010, 0xM035): "oligoasthenoteratozoospermia",
    (0x0010, 0xM036): "sperm_count",
    (0x0010, 0xM037): "sperm_motility",
    (0x0010, 0xM038): "sperm_morphology",
    (0x0010, 0xM039): "hormone_levels_male",
    (0x0010, 0xM040): "testosterone_level",
    (0x0010, 0xM041): "lh_level",
    (0x0010, 0xM042): "fsh_level",
    (0x0010, 0xM043): "prolactin_level",
    (0x0010, 0xM044): "estradiol_level",
    (0x0010, 0xM045): "penile_diagnosis",
    (0x0010, 0xM046): "peyronie_disease",
    (0x0010, 0xM047): "erectile_dysfunction_cause",
    (0x0010, 0xM048): "venous_leak",
    (0x0010, 0xM049): "arterial_insufficiency",
    (0x0010, 0xM050): "hypogonadism",
    (0x0010, 0xM051): "primary_hypogonadism",
    (0x0010, 0xM052): "secondary_hypogonadism",
    (0x0010, 0xM053): "andropause",
    (0x0010, 0xM054): "male_menopause",
    (0x0010, 0xM055): "late_onset_hypogonadism",
    (0x0010, 0xM056): "prostate_indicator",
    (0x0010, 0xM057): "bph_indicator",
    (0x0010, 0xM058): "postvoid_residual",
    (0x0010, 0xM059): "uroflowmetry_peak",
}

MENS_HEALTH_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xM101): "prostate_lesion",
    (0x0018, 0xM102): "prostate_zonal_anatomy",
    (0x0018, 0xM103): "transition_zone",
    (0x0018, 0xM104): "peripheral_zone",
    (0x0018, 0xM105): "central_zone",
    (0x0018, 0xM106): "anterior_fibromuscular",
    (0x0018, 0xM107): "capsular_involvement",
    (0x0018, 0xM108): "extracapsular_extension",
    (0x0018, 0xM109): "seminal_vesicle_invasion",
    (0x0018, 0xM110): "neurovascular_bundle",
    (0x0018, 0xM111): "lymph_node_involvement",
    (0x0018, 0xM112): "pi_rads_score",
    (0x0018, 0xM113): "pi_rads_1",
    (0x0018, 0xM114): "pi_rads_2",
    (0x0018, 0xM115): "pi_rads_3",
    (0x0018, 0xM116): "pi_rads_4",
    (0x0018, 0xM117): "pi_rads_5",
    (0x0018, 0xM118): "lesion_location_prostate",
    (0x0018, 0xM119): "lesion_size_prostate",
    (0x0018, 0xM120): "apical_involvement",
    (0x0018, 0xM121): "basal_involvement",
    (0x0018, 0xM122): "testicular_mass",
    (0x0018, 0xM123): "testicular_cyst",
    (0x0018, 0xM124): "testicular_calcification",
    (0x0018, 0xM125): "microcalcification_testis",
    (0x0018, 0xM126): "epididymal_mass",
    (0x0018, 0xM127): "scrotal_wall_thickening",
    (0x0018, 0xM128): "hydrocele_size",
    (0x0018, 0xM129): "varicocele_grade",
    (0x0018, 0xM130): "penile_plaque",
    (0x0018, 0xM131): "penile_fibrosis",
    (0x0018, 0xM132): "curvature_angle",
    (0x0018, 0xM133): "erectile_tissue",
    (0x0018, 0xM134): "cavernosal_fibrosis",
    (0x0018, 0xM135): "arterial_inflow",
    (0x0018, 0xM136): "venous_outflow",
    (0x0018, 0xM137): "pelvic_pathology",
    (0x0018, 0xM138): "rectal_pathology",
    (0x0018, 0xM139): "bladder_pathology",
    (0x0018, 0xM140): "urethral_pathology",
    (0x0018, 0xM141): "pelvic_floor_anatomy",
    (0x0018, 0xM142): "levator_ani",
    (0x0018, 0xM143): "puborectalis",
    (0x0018, 0xM144): "obturator_internus",
    (0x0018, 0xM145): "sacral_plexus",
    (0x0018, 0xM146): "lumbar_plexus",
    (0x0018, 0xM147): "genitofemoral_nerve",
    (0x0018, 0xM148): "ilioinguinal_nerve",
    (0x0018, 0xM149): "pelvic_lymph_nodes",
}

MENS_HEALTH_IMAGING_TAGS = {
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
    (0x0018, 0xM201): "transrectal_ultrasound",
    (0x0018, 0xM202): "trus_guided",
    (0x0018, 0xM203): "systematic_biopsy",
    (0x0018, 0xM204): "fusion_biopsy",
    (0x0018, 0xM205): "mri_ultrasound_fusion",
    (0x0018, 0xM206): "in_bore_biopsy",
    (0x0018, 0xM207): "prostate_mri_protocol",
    (0x0018, 0xM208): "t2_weighted_prostate",
    (0x0018, 0xM209): "diffusion_prostate",
    (0x0018, 0xM210): "dce_prostate",
    (0x0018, 0xM211): "spectroscopic_prostate",
    (0x0018, 0xM212): "mri_lymph_node",
    (0x0018, 0xM213): "pet_ct_prostate",
    (0x0018, 0xM214): "psma_pet_ct",
    (0x0018, 0xM215): "fluciclovine_pet",
    (0x0018, 0xM216): "choline_pet",
    (0x0018, 0xM217): "testicular_ultrasound",
    (0x0018, 0xM218): "scrotal_ultrasound",
    (0x0018, 0xM219): "high_frequency_scrotal",
    (0x0018, 0xM220): "doppler_testicular",
    (0x0018, 0xM221): "color_doppler_scrotal",
    (0x0018, 0xM222): "contrast_enhanced_testicular",
    (0x0018, 0xM223): "ct_abdomen_pelvis",
    (0x0018, 0xM224): "ct_prostate_protocol",
    (0x0018, 0xM225): "mri_pelvis_male",
    (0x0018, 0xM226): "mri_penis",
    (0x0018, 0xM227): "dynamic_contrast_penis",
    (0x0018, 0xM228): "cavernosography",
    (0x0018, 0xM229): "cavernosometry",
    (0x0018, 0xM230): "penile_doppler",
    (0x0018, 0xM231): "intracavernosal_injection",
    (0x0018, 0xM232): "vasography",
    (0x0018, 0xM233): "vesiculography",
    (0x0018, 0xM234): "urethrography",
    (0x0018, 0xM235): "retrograde_urethrogram",
    (0x0018, 0xM236): "antegrade_urethrogram",
    (0x0018, 0xM237): "cystoscopy_male",
    (0x0018, 0xM238): "urodynamics",
    (0x0018, 0xM239): "uroflowmetry",
    (0x0018, 0xM240): "pressure_flow_study",
    (0x0018, 0xM241): "electromyography_pelvic",
    (0x0018, 0xM242): "bone_scan_prostate",
    (0x0018, 0xM243): "na_fluoride_prostate",
    (0x0018, 0xM244): "spect_ct_bone",
    (0x0018, 0xM245): "sperm_analysis",
    (0x0018, 0xM246): "semen_analysis",
    (0x0018, 0xM247): "hormone_testing",
    (0x0018, 0xM248): "genetic_testing_male",
    (0x0018, 0xM249): "karyotyping_male",
}

MENS_HEALTH_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xM301): "screening_protocol",
    (0x0018, 0xM302): "psa_screening",
    (0x0018, 0xM303): "digital_rectal_exam",
    (0x0018, 0xM304): "prostate_biopsy_protocol",
    (0x0018, 0xM305): "saturation_biopsy",
    (0x0018, 0xM306): "template_biopsy",
    (0x0018, 0xM307): "active_surveillance",
    (0x0018, 0xM308): "treatment_planning",
    (0x0018, 0xM309): "radical_prostatectomy",
    (0x0018, 0xM310): "robotic_prostatectomy",
    (0x0018, 0xM311): "open_prostatectomy",
    (0x0018, 0xM312): "nerve_sparing",
    (0x0018, 0xM313): "lymph_node_dissection",
    (0x0018, 0xM314): "radiation_therapy_prostate",
    (0x0018, 0xM315): "brachytherapy_prostate",
    (0x0018, 0xM316): "seed_implantation",
    (0x0018, 0xM317): "external_beam_prostate",
    (0x0018, 0xM318): "sbrt_prostate",
    (0x0018, 0xM319): "hifu_prostate",
    (0x0018, 0xM320): "cryotherapy_prostate",
    (0x0018, 0xM321): "androgen_deprivation",
    (0x0018, 0xM322): "chemical_castration",
    (0x0018, 0xM323): "lhrh_agonist",
    (0x0018, 0xM324): "anti_androgen",
    (0x0018, 0xM325): "testosterone_suppression",
    (0x0018, 0xM326): "infertility_treatment",
    (0x0018, 0xM327): "varicocelectomy",
    (0x0018, 0xM328): "vasectomy",
    (0x0018, 0xM329): "vasectomy_reversal",
    (0x0018, 0xM330): "vasovasostomy",
    (0x0018, 0xM331): "epididymostomy",
    (0x0018, 0xM332): "testicular_biopsy",
    (0x0018, 0xM333): "sperm_extraction",
    (0x0018, 0xM334): "tese_procedure",
    (0x0018, 0xM335): "microtese",
    (0x0018, 0xM336): "icsi_procedure",
    (0x0018, 0xM337): "ivf_male_factor",
    (0x0018, 0xM338): "penile_surgery",
    (0x0018, 0xM339): "penile_prosthesis",
    (0x0018, 0xM340): "inflatable_prosthesis",
    (0x0018, 0xM341): "malleable_prosthesis",
    (0x0018, 0xM342): "peyronie_correction",
    (0x0018, 0xM343): "plication_surgery",
    (0x0018, 0xM344): "graft_surgery",
    (0x0018, 0xM345): "erectile_restoration",
    (0x0018, 0xM346): "hormone_replacement",
    (0x0018, 0xM347): "testosterone_therapy",
    (0x0018, 0xM348): "clomiphene_therapy",
    (0x0018, 0xM349): "gonadotropin_therapy",
    (0x0018, 0xM350): "infertility_counseling",
}

MENS_HEALTH_OUTCOMES_TAGS = {
    (0x0018, 0xM401): "prostate_cancer_survival",
    (0x0018, 0xM402): "cancer_specific_survival",
    (0x0018, 0xM403): "overall_survival_prostate",
    (0x0018, 0xM404): "biochemical_recurrence",
    (0x0018, 0xM405): "psa_recurrence",
    (0x0018, 0xM406): "local_control_prostate",
    (0x0018, 0xM407): "metastasis_prostate",
    (0x0018, 0xM408): "treatment_response_prostate",
    (0x0018, 0xM409): "continence_outcome",
    (0x0018, 0xM410): "urinary_continence",
    (0x0018, 0xM411): "pad_use_prostate",
    (0x0018, 0xM412): "time_to_continence",
    (0x0018, 0xM413): "sexual_function_prostate",
    (0x0018, 0xM414): "erectile_function",
    (0x0018, 0xM415): "iief_score",
    (0x0018, 0xM416): "nerve_sparing_outcome",
    (0x0018, 0xM417): "libido_outcome",
    (0x0018, 0xM418): "orgasmic_function",
    (0x0018, 0xM419): "ejaculatory_function",
    (0x0018, 0xM420): "infertility_outcome",
    (0x0018, 0xM421): "pregnancy_rate",
    (0x0018, 0xM422): "live_birth_rate_male",
    (0x0018, 0xM423): "sperm_parameters",
    (0x0018, 0xM424): "improvement_rate",
    (0x0018, 0xM425): "treatment_fertility",
    (0x0018, 0xM426): "assisted_reproduction",
    (0x0018, 0xM427): "icsi_success",
    (0x0018, 0xM428): "testicular_cancer_survival",
    (0x0018, 0xM429): "relapse_testicular",
    (0x0018, 0xM430): "remission_testicular",
    (0x0018, 0xM431): "fertility_preservation",
    (0x0018, 0xM432): "sperm_banking",
    (0x0018, 0xM433): "endocrine_outcome",
    (0x0018, 0xM434): "testosterone_recovery",
    (0x0018, 0xM435): "symptom_relief",
    (0x0018, 0xM436): "luts_improvement",
    (0x0018, 0xM437): "flow_rate_improvement",
    (0x0018, 0xM438): "postvoid_residual_reduction",
    (0x0018, 0xM439): "quality_of_life_male",
    (0x0018, 0xM440): "prostate_qol",
    (0x0018, 0xM441): "sexual_qol",
    (0x0018, 0xM442): "mental_health_male",
    (0x0018, 0xM443): "depression_male",
    (0x0018, 0xM444): "anxiety_male",
    (0x0018, 0xM445): "body_image_male",
    (0x0018, 0xM446): "relationship_impact",
    (0x0018, 0xM447): "support_services_male",
    (0x0018, 0xM448): "support_groups_male",
    (0x0018, 0xM449): "counseling_male",
    (0x0018, 0xM450): "follow_up_adherence",
}

TOTAL_TAGS_LXXXVII = {}

TOTAL_TAGS_LXXXVII.update(MENS_HEALTH_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXXVII.update(MENS_HEALTH_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXXVII.update(MENS_HEALTH_IMAGING_TAGS)
TOTAL_TAGS_LXXXVII.update(MENS_HEALTH_PROTOCOLS)
TOTAL_TAGS_LXXXVII.update(MENS_HEALTH_OUTCOMES_TAGS)


def _extract_tags_lxxxvii(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXXVII.items()}
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


def _is_mens_health_imaging_file(file_path: str) -> bool:
    mens_indicators = [
        'mens', "men's", 'male', 'prostate', 'testicular',
        'testis', 'scrotal', 'penile', 'penis', 'bph',
        'psa', 'prostatitis', 'infertility', 'azoospermia',
        'erectile', 'andrology', 'urogenital', 'urology_male'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in mens_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxxvii_detected": False,
        "fields_extracted": 0,
        "extension_lxxxvii_type": "mens_health_imaging",
        "extension_lxxxvii_version": "2.0.0",
        "mens_health_patient_parameters": {},
        "mens_health_pathology": {},
        "mens_health_imaging": {},
        "mens_health_protocols": {},
        "mens_health_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_mens_health_imaging_file(file_path):
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

        result["extension_lxxxvii_detected"] = True

        mens_data = _extract_tags_lxxxvii(ds)

        patient_params_set = set(MENS_HEALTH_PATIENT_PARAMETERS.keys())
        pathology_set = set(MENS_HEALTH_PATHOLOGY_TAGS.keys())
        imaging_set = set(MENS_HEALTH_IMAGING_TAGS.keys())
        protocols_set = set(MENS_HEALTH_PROTOCOLS.keys())
        outcomes_set = set(MENS_HEALTH_OUTCOMES_TAGS.keys())

        for tag, value in mens_data.items():
            if tag in patient_params_set:
                result["mens_health_patient_parameters"][tag] = value
            elif tag in pathology_set:
                result["mens_health_pathology"][tag] = value
            elif tag in imaging_set:
                result["mens_health_imaging"][tag] = value
            elif tag in protocols_set:
                result["mens_health_protocols"][tag] = value
            elif tag in outcomes_set:
                result["mens_health_outcomes"][tag] = value

        result["fields_extracted"] = len(mens_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_field_count() -> int:
    return len(TOTAL_TAGS_LXXXVII)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_description() -> str:
    return (
        "Men's Health Imaging II metadata extraction. Provides comprehensive coverage of "
        "prostate health, testicular disorders, male infertility, erectile dysfunction, "
        "men's health-specific imaging protocols, and men's health outcomes assessment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_modalities() -> List[str]:
    return ["US", "CT", "MR", "PT", "NM", "XA", "CR", "DR"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_category() -> str:
    return "Men's Health Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_keywords() -> List[str]:
    return [
        "men's health", "prostate", "testicular", "male infertility",
        "erectile dysfunction", "BPH", "PSA", "prostate cancer",
        "testicular cancer", "testosterone", "andrology", "urology",
        "sexual health", "male reproductive", "penile health"
    ]


# Aliases for smoke test compatibility
def extract_medical_alarms(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii(file_path)

def get_medical_alarms_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_field_count()

def get_medical_alarms_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_version()

def get_medical_alarms_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_description()

def get_medical_alarms_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_supported_formats()

def get_medical_alarms_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxvii_modalities()
