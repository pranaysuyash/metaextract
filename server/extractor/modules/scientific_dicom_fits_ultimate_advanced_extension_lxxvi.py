"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXVI - ENT Imaging II

This module provides comprehensive extraction of ENT Imaging parameters
including otolaryngology, head and neck imaging, sinus disorders, and
ENT-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXVI_AVAILABLE = True

ENT_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x1001): "ent_assessment_date",
    (0x0010, 0xJ002): "ent_diagnosis",
    (0x0010, 0xJ003): "sinusitis_indicator",
    (0x0010, 0xJ004): "acute_sinusitis",
    (0x0010, 0xJ005): "chronic_sinusitis",
    (0x0010, 0xJ006): "nasal_polyposis",
    (0x0010, 0xJ007): "allergic_fungal_sinusitis",
    (0x0010, 0xJ008): "samter_triad",
    (0x0010, 0xJ009): "septal_deviation",
    (0x0010, 0xJ010): "turbinate_hypertrophy",
    (0x0010, 0xJ011): "concha_bullosa",
    (0x0010, 0xJ012): "adenoid_hypertrophy",
    (0x0010, 0xJ013): "tonsillar_hypertrophy",
    (0x0010, 0xJ014): "obstructive_sleep_apnea",
    (0x0010, 0xJ015): "osa_severity",
    (0x0010, 0xJ016): "ahi_index",
    (0x0010, 0xJ017): "apnea_hypopnea_index",
    (0x0010, 0xJ018): "snoring_severity",
    (0x0010, 0xJ019): "laryngeal_diagnosis",
    (0x0010, 0xJ020): "vocal_cord_paralysis",
    (0x0010, 0xJ021): "laryngeal_cancer",
    (0x0010, 0xJ022): "laryngeal_leukoplakia",
    (0x0010, 0xJ023): "reinke_edema",
    (0x0010, 0xJ024): "nodules_vocal_cord",
    (0x0010, 0xJ025): "polyps_vocal_cord",
    (0x0010, 0xJ026): "granuloma_larynx",
    (0x0010, 0xJ027): "hearing_loss_indicator",
    (0x0010, 0xJ028): "conductive_hl",
    (0x0010, 0xJ029): "sensorineural_hl",
    (0x0010, 0xJ030): "mixed_hl",
    (0x0010, 0xJ031): "pTA_threshold",
    (0x0010, 0xJ032): "speech_frequencies",
    (0x0010, 0xJ033): "otitis_media",
    (0x0010, 0xJ034): "chronic_otitis_media",
    (0x0010, 0xJ035): "cholesteatoma",
    (0x0010, 0xJ036): "tympanic_membrane_perforation",
    (0x0010, 0xJ037): "otosclerosis",
    (0x0010, 0xJ038): "meniere_disease",
    (0x0010, 0xJ039): "benign_paroxysmal_positional",
    (0x0010, 0xJ040): "vestibular_neuronitis",
    (0x0010, 0xJ041): "acoustic_neuroma",
    (0x0010, 0xJ042): "vestibular_schwannoma",
    (0x0010, 0xJ043): "head_neck_cancer",
    (0x0010, 0xJ044): "oral_cavity_cancer",
    (0x0010, 0xJ045): "oropharyngeal_cancer",
    (0x0010, 0xJ046): "hypopharyngeal_cancer",
    (0x0010, 0xJ047): "nasopharyngeal_cancer",
    (0x0010, 0xJ048): "thyroid_cancer",
    (0x0010, 0xJ049): "salivary_gland_tumor",
    (0x0010, 0xJ050): "parotid_tumor",
    (0x0010, 0xJ051): "submandibular_tumor",
    (0x0010, 0xJ052): "lymphoma_head_neck",
    (0x0010, 0xJ053): "thyroiditis",
    (0x0010, 0xJ054): "goiter_indicator",
    (0x0010, 0xJ055): "thyroid_nodule",
    (0x0010, 0xJ056): "hoarseness_indicator",
    (0x0010, 0xJ057): "dysphagia_indicator",
    (0x0010, 0xJ058): "dysphonia_indicator",
    (0x0010, 0xJ059): "globus_sensation",
}

ENT_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xJ101): "mucosal_thickening_sinus",
    (0x0018, 0xJ102): "fluid_level_sinus",
    (0x0018, 0xJ103): "opacification_sinus",
    (0x0018, 0xJ104): "polypoid_mass_sinus",
    (0x0018, 0xJ105): "bone_thinning",
    (0x0018, 0xJ106): "bone_erosion_sinus",
    (0x0018, 0xJ107): "sinus_obliteration",
    (0x0018, 0xJ108): "ostiomeatal_unit",
    (0x0018, 0xJ109): "nasal_obstruction",
    (0x0018, 0xJ110): "septal_spur",
    (0x0018, 0xJ111): "nasal_polyp_size",
    (0x0018, 0xJ112): "polyps_nasal",
    (0x0018, 0xJ113): "choanal_atresia",
    (0x0018, 0xJ114): "cranial_fossa",
    (0x0018, 0xJ115): "intracranial_extension",
    (0x0018, 0xJ116): "orbital_extension",
    (0x0018, 0xJ117): "laryngeal_lesion",
    (0x0018, 0xJ118): "vocal_fold_mass",
    (0x0018, 0xJ119): "vocal_fold_immobility",
    (0x0018, 0xJ120): "airway_narrowing",
    (0x0018, 0xJ121): "subglottic_stenosis",
    (0x0018, 0xJ122): "tracheal_stenosis",
    (0x0018, 0xJ123): "retropharyngeal_space",
    (0x0018, 0xJ124): "parapharyngeal_space",
    (0x0018, 0xJ125): "prevertebral_space",
    (0x0018, 0xJ126): "masticator_space",
    (0x0018, 0xJ127): "parotid_space",
    (0x0018, 0xJ128): "carotid_space",
    (0x0018, 0xJ129): "lymph_node_level",
    (0x0018, 0xJ130): "level_1_ln",
    (0x0018, 0xJ131): "level_2_ln",
    (0x0018, 0xJ132): "level_3_ln",
    (0x0018, 0xJ133): "level_4_ln",
    (0x0018, 0xJ134): "level_5_ln",
    (0x0018, 0xJ135): "level_6_ln",
    (0x0018, 0xJ136): "retropharyngeal_ln",
    (0x0018, 0xJ137): "supraclavicular_ln",
    (0x0018, 0xJ138): "node_size_ent",
    (0x0018, 0xJ139): "node_necrosis",
    (0x0018, 0xJ140): "extracapsular_spread",
    (0x0018, 0xJ141): "middle_ear_opacification",
    (0x0018, 0xJ142): "ossicular_erosion",
    (0x0018, 0xJ143): "facial_nerve_canal",
    (0x0018, 0xJ144): "semicircular_canals",
    (0x0018, 0xJ145): "cochlea_ent",
    (0x0018, 0xJ146): "internal_acoustic_meatus",
    (0x0018, 0xJ147): "mass_pons",
    (0x0018, 0xJ148): "cerebellopontine_angle",
    (0x0018, 0xJ149): "thyroid_nodule_neck",
}

ENT_IMAGING_TAGS = {
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
    (0x0018, 0xJ201): "ct_sinus_protocol",
    (0x0018, 0xJ202): "ct_paranasal_sinus",
    (0x0018, 0xJ203): "coronal_sinus_ct",
    (0x0018, 0xJ204): "sagittal_sinus_ct",
    (0x0018, 0xJ205): "sinus_window",
    (0x0018, 0xJ206): "bone_window_sinus",
    (0x0018, 0xJ207): "ct_temporal_bone",
    (0x0018, 0xJ208): "petrous_temporal",
    (0x0018, 0xJ209): "mastoid_ct",
    (0x0018, 0xJ210): "middle_ear_ct",
    (0x0018, 0xJ211): "inner_ear_ct",
    (0x0018, 0xJ212): "ct_neck_protocol",
    (0x0018, 0xJ213): "contrast_neck_ct",
    (0x0018, 0xJ214): "non_contrast_neck_ct",
    (0x0018, 0xJ215): "mri_head_neck",
    (0x0018, 0xJ216): "mri_sinus_protocol",
    (0x0018, 0xJ217): "mri_temporal_bone",
    (0x0018, 0xJ218): "diffusion_head_neck",
    (0x0018, 0xJ219): "dwi_head_neck",
    (0x0018, 0xJ220): "fat_suppressed_head_neck",
    (0x0018, 0xJ221): "post_contrast_head_neck",
    (0x0018, 0xJ222): "pet_ct_head_neck",
    (0x0018, 0xJ223): "fdg_pet_neck",
    (0x0018, 0xJ224): "thyroid_pet_ct",
    (0x0018, 0xJ225): "oct_neck",
    (0x0018, 0xJ226): "ultrasound_neck",
    (0x0018, 0xJ227): "thyroid_ultrasound",
    (0x0018, 0xJ228): "parathyroid_ultrasound",
    (0x0018, 0xJ229): "salivary_gland_us",
    (0x0018, 0xJ230): "lymph_node_us",
    (0x0018, 0xJ231): "fine_needle_aspiration",
    (0x0018, 0xJ232): "us_guided_biopsy",
    (0x0018, 0xJ233): "ct_guided_biopsy",
    (0x0018, 0xJ234): "endoscopic_ultrasound",
    (0x0018, 0xJ235): "eus_ent",
    (0x0018, 0xJ236): "laryngoscopy_imaging",
    (0x0018, 0xJ237): "stroboscopy",
    (0x0018, 0xJ238): "videostroboscopy",
    (0x0018, 0xJ239): "nasal_endoscopy",
    (0x0018, 0xJ240): "otoneurological_test",
    (0x0018, 0xJ241): "audiometry",
    (0x0018, 0xJ242): "pure_tone_audiometry",
    (0x0018, 0xJ243): "speech_audiometry",
    (0x0018, 0xJ244): "tympanometry",
    (0x0018, 0xJ245): "acoustic_reflexes",
    (0x0018, 0xJ246): "vestibular_testing",
    (0x0018, 0xJ247): "electronystagmography",
    (0x0018, 0xJ248): "videonystagmography",
    (0x0018, 0xJ249): "vemp_testing",
}

ENT_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xJ301): "sinus_surgery_planning",
    (0x0018, 0xJ302): "functional_endoscopic",
    (0x0018, 0xJ303): "fess_planning",
    (0x0018, 0xJ304): "septoplasty_planning",
    (0x0018, 0xJ305): "turbinoplasty",
    (0x0018, 0xJ306): "polypectomy_planning",
    (0x0018, 0xJ307): "image_guidance",
    (0x0018, 0xJ308): "navigation_surgery",
    (0x0018, 0xJ309): "intraoperative_ct",
    (0x0018, 0xJ310): "tumor_resection_planning",
    (0x0018, 0xJ311): "neck_dissection",
    (0x0018, 0xJ312): "selective_neck_dissection",
    (0x0018, 0xJ313): "modified_radical",
    (0x0018, 0xJ314): "radical_neck_dissection",
    (0x0018, 0xJ315): "thyroidectomy_planning",
    (0x0018, 0xJ316): "total_thyroidectomy",
    (0x0018, 0xJ317): "hemi_thyroidectomy",
    (0x0018, 0xJ318): "lobectomy_neck",
    (0x0018, 0xJ319): "parathyroid_planning",
    (0x0018, 0xJ320): "salivary_gland_surgery",
    (0x0018, 0xJ321): "parotidectomy",
    (0x0018, 0xJ322): "submandibular_gland",
    (0x0018, 0xJ323): "laryngeal_surgery",
    (0x0018, 0xJ324): "cordectomy",
    (0x0018, 0xJ325): "partial_laryngectomy",
    (0x0018, 0xJ326): "total_laryngectomy",
    (0x0018, 0xJ327): "reconstruction_planning",
    (0x0018, 0xJ328): "flap_reconstruction",
    (0x0018, 0xJ329): "free_flap_planning",
    (0x0018, 0xJ330): "pedicled_flap",
    (0x0018, 0xJ331): "tracheostomy_planning",
    (0x0018, 0xJ332): "airway_management",
    (0x0018, 0xJ333): "sleep_surgery",
    (0x0018, 0xJ334): "uvulopalatopharyngoplasty",
    (0x0018, 0xJ335): "hyoid_suspension",
    (0x0018, 0xJ336): "maxillomandibular",
    (0x0018, 0xJ337): "ent_implant_planning",
    (0x0018, 0xJ338): "cochlear_implant",
    (0x0018, 0xJ339): "bone_anchored_hearing",
    (0x0018, 0xJ340): "stapedectomy_planning",
    (0x0018, 0xJ341): "tympanoplasty",
    (0x0018, 0xJ342): "myringotomy",
    (0x0018, 0xJ343): "ventilation_tube",
    (0x0018, 0xJ344): "mastoidectomy",
    (0x0018, 0xJ345): "canal_wall_up",
    (0x0018, 0xJ346): "canal_wall_down",
    (0x0018, 0xJ347): "radical_mastoidectomy",
    (0x0018, 0xJ348): "ossiculoplasty",
    (0x0018, 0xJ349): "stapes_surgery",
    (0x0018, 0xJ350): "ear_reconstruction",
}

ENT_OUTCOMES_TAGS = {
    (0x0018, 0xJ401): "cancer_survival_ent",
    (0x0018, 0xJ402): "local_control_ent",
    (0x0018, 0xJ403): "regional_control",
    (0x0018, 0xJ404): "distant_control",
    (0x0018, 0xJ405): "recurrence_ent",
    (0x0018, 0xJ406): "treatment_response_ent",
    (0x0018, 0xJ407): "complete_response_ent",
    (0x0018, 0xJ408): "resection_margins",
    (0x0018, 0xJ409): "positive_margins",
    (0x0018, 0xJ410): "close_margins",
    (0x0018, 0xJ411): "negative_margins",
    (0x0018, 0xJ412): "functional_outcome_ent",
    (0x0018, 0xJ413): "swallowing_function",
    (0x0018, 0xJ414): "speech_function",
    (0x0018, 0xJ415): "voice_quality",
    (0x0018, 0xJ416): "voice_handicap_index",
    (0x0018, 0xJ417): "breathing_function",
    (0x0018, 0xJ418): "airway_patency",
    (0x0018, 0xJ419): "deglutition",
    (0x0018, 0xJ420): "feeding_ability",
    (0x0018, 0xJ421): "gastrostomy_dependence",
    (0x0018, 0xJ422): "tracheostomy_dependence",
    (0x0018, 0xJ423): "hearing_outcome",
    (0x0018, 0xJ424): "audiometric_improvement",
    (0x0018, 0xJ425): "speech_perception",
    (0x0018, 0xJ426): "balance_outcome",
    (0x0018, 0xJ427): "vertigo_resolution",
    (0x0018, 0xJ428): "dizziness_improvement",
    (0x0018, 0xJ429): "sinus_symptom_score",
    (0x0018, 0xJ430): "snot_22_score",
    (0x0018, 0xJ431): "sino_nasal_outcome",
    (0x0018, 0xJ432): "nasal_obstruction_score",
    (0x0018, 0xJ433): "olfaction_score",
    (0x0018, 0xJ434): "sleep_quality_ent",
    (0x0018, 0xJ435): "apnea_outcome",
    (0x0018, 0xJ436): "ahi_improvement",
    (0x0018, 0xJ437): "oxygen_saturation",
    (0x0018, 0xJ438): "quality_of_life_ent",
    (0x0018, 0xJ439): "hqo_laryngectomy",
    (0x0018, 0xJ440): "eortc_hn35",
    (0x0018, 0xJ441): "swallowing_qol",
    (0x0018, 0xJ442): "cosmetic_outcome",
    (0x0018, 0xJ443): "facial_nerve_function",
    (0x0018, 0xJ444): "shoulder_function",
    (0x0018, 0xJ445): "complication_ent",
    (0x0018, 0xJ446): "fistula_formation",
    (0x0018, 0xJ447): "chyle_leak",
    (0x0018, 0xJ448): "bleeding_ent",
    (0x0018, 0xJ449): "infection_ent",
    (0x0018, 0xJ450): "adherence_ent",
}

TOTAL_TAGS_LXXVI = {}

TOTAL_TAGS_LXXVI.update(ENT_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXVI.update(ENT_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXVI.update(ENT_IMAGING_TAGS)
TOTAL_TAGS_LXXVI.update(ENT_PROTOCOLS)
TOTAL_TAGS_LXXVI.update(ENT_OUTCOMES_TAGS)


def _extract_tags_lxxvi(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXVI.items()}
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


def _is_ent_imaging_file(file_path: str) -> bool:
    ent_indicators = [
        'ent', 'otorhinolaryngology', 'ear', 'nose', 'throat',
        'sinus', 'sinusitis', 'laryngeal', 'larynx', 'vocal',
        'hearing', 'audiology', 'neck', 'thyroid', 'salivary',
        'nasal', 'pharyngeal', 'tonsil', 'adenoid', 'sleep_apnea',
        'head_neck_cancer', 'cochlear', 'otology', 'rhinology'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in ent_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxvi(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxvi_detected": False,
        "fields_extracted": 0,
        "extension_lxxvi_type": "ent_imaging",
        "extension_lxxvi_version": "2.0.0",
        "ent_patient_parameters": {},
        "ent_pathology": {},
        "ent_imaging": {},
        "ent_protocols": {},
        "ent_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_ent_imaging_file(file_path):
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

        result["extension_lxxvi_detected"] = True

        ent_data = _extract_tags_lxxvi(ds)

        patient_params_set = set(ENT_PATIENT_PARAMETERS.keys())
        pathology_set = set(ENT_PATHOLOGY_TAGS.keys())
        imaging_set = set(ENT_IMAGING_TAGS.keys())
        protocols_set = set(ENT_PROTOCOLS.keys())
        outcomes_set = set(ENT_OUTCOMES_TAGS.keys())

        for tag, value in ent_data.items():
            if tag in patient_params_set:
                result["ent_patient_parameters"][tag] = value
            elif tag in pathology_set:
                result["ent_pathology"][tag] = value
            elif tag in imaging_set:
                result["ent_imaging"][tag] = value
            elif tag in protocols_set:
                result["ent_protocols"][tag] = value
            elif tag in outcomes_set:
                result["ent_outcomes"][tag] = value

        result["fields_extracted"] = len(ent_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxvi_field_count() -> int:
    return len(TOTAL_TAGS_LXXVI)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxvi_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxvi_description() -> str:
    return (
        "ENT Imaging II metadata extraction. Provides comprehensive coverage of "
        "otolaryngology, head and neck imaging, sinus disorders, hearing loss, "
        "ENT-specific imaging protocols, and ENT outcomes assessment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxvi_modalities() -> List[str]:
    return ["CT", "MR", "US", "PT", "NM", "XA", "CR", "DR"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxvi_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxvi_category() -> str:
    return "ENT Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxvi_keywords() -> List[str]:
    return [
        "ENT", "otorhinolaryngology", "ear", "nose", "throat",
        "sinus", "sinusitis", "larynx", "vocal cords", "hearing",
        "neck", "thyroid", "salivary glands", "sleep apnea",
        "head and neck cancer", "cochlear implant", "otology",
        "rhinology", "laryngology", "Audiology"
    ]
