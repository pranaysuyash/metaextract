"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXXII - Neurology Imaging II

This module provides comprehensive extraction of Neurology Imaging parameters
including brain disorders, stroke, neurodegenerative diseases, and
neurology-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXII_AVAILABLE = True

NEUROLOGY_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0xC001): "neurology_assessment_date",
    (0x0010, 0xC002): "neurological_diagnosis",
    (0x0010, 0xC003): "stroke_indicator",
    (0x0010, 0xC004): "ischemic_stroke",
    (0x0010, 0xC005): "hemorrhagic_stroke",
    (0x0010, 0xC006): "intracerebral_hemorrhage",
    (0x0010, 0xC007): "subarachnoid_hemorrhage",
    (0x0010, 0xC008): "subdural_hemorrhage",
    (0x0010, 0xC009): "epidural_hemorrhage",
    (0x0010, 0xC010): "transient_ischemic_attack",
    (0x0010, 0xC011): "stroke_location",
    (0x0010, 0xC012): "nihss_score",
    (0x0010, 0xC013): "modified_rankin_scale",
    (0x0010, 0xC014): "bartel_index",
    (0x0010, 0xC015): "gcs_score",
    (0x0010, 0xC016): "dementia_indicator",
    (0x0010, 0xC017): "alzheimers_disease",
    (0x0010, 0xC018): "vascular_dementia",
    (0x0010, 0xC019): "lewy_body_dementia",
    (0x0010, 0xC020): "frontotemporal_dementia",
    (0x0010, 0xC021): "mild_cognitive_impairment",
    (0x0010, 0xC022): "mmse_score",
    (0x0010, 0xC023): "moca_score",
    (0x0010, 0xC024): "parkinsons_disease",
    (0x0010, 0xC025): "parkinsonism",
    (0x0010, 0xC026): "progressive_supranuclear_palsy",
    (0x0010, 0xC027): "multiple_system_atrophy",
    (0x0010, 0xC028): "corticobasal_degeneration",
    (0x0010, 0xC029): "huntingtons_disease",
    (0x0010, 0xC030): "motor_neuron_disease",
    (0x0010, 0xC031): "als_indicator",
    (0x0010, 0xC032): "multiple_sclerosis",
    (0x0010, 0xC033): "ms_phenotype",
    (0x0010, 0xC034): "relapsing_remitting_ms",
    (0x0010, 0xC035): "secondary_progressive_ms",
    (0x0010, 0xC036): "primary_progressive_ms",
    (0x0010, 0xC037): "edss_score",
    (0x0010, 0xC038): "epilepsy_indicator",
    (0x0010, 0xC039): "seizure_type",
    (0x0010, 0xC040): "generalized_seizure",
    (0x0010, 0xC041): "focal_seizure",
    (0x0010, 0xC042): "status_epilepticus",
    (0x0010, 0xC043): "brain_tumor_indicator",
    (0x0010, 0xC044): "glioma_indicator",
    (0x0010, 0xC045): "meningioma_indicator",
    (0x0010, 0xC046): "metastasis_brain",
    (0x0010, 0xC047): "pituitary_adenoma",
    (0x0010, 0xC048): "acoustic_neuroma",
    (0x0010, 0xC049): "trigeminal_neuralgia",
    (0x0010, 0xC050): "hemifacial_spasm",
    (0x0010, 0xC051): "myasthenia_gravis",
    (0x0010, 0xC052): "guillain_barre",
    (0x0010, 0xC053): "chronic_inflammatory_demyelinating",
    (0x0010, 0xC054): "peripheral_neuropathy",
    (0x0010, 0xC055): "mononeuropathy",
    (0x0010, 0xC056): "radiculopathy",
    (0x0010, 0xC057): "plexopathy",
    (0x0010, 0xC058): "neuromuscular_junction",
    (0x0010, 0xC059): "muscle_disorder",
}

NEURO_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xC101): "infarct_core",
    (0x0018, 0xC102): "penumbra_zone",
    (0x0018, 0xC103): "diffusion_restriction",
    (0x0018, 0xC104): "apparent_diffusion_coefficient",
    (0x0018, 0xC105): "fluid_attenuated_inversion_recovery",
    (0x0018, 0xC106): "flair_hyperintensity",
    (0x0018, 0xC107): "t2_hyperintensity",
    (0x0018, 0xC108): "t1_hypointensity",
    (0x0018, 0xC109): "microbleeds",
    (0x0018, 0xC110): "white_matter_hyperintensity",
    (0x0018, 0xC111): "leukoaraiosis",
    (0x0018, 0xC112): "lacunar_infarct",
    (0x0018, 0xC113): "territorial_infarction",
    (0x0018, 0xC114): "watershed_infarction",
    (0x0018, 0xC115): "intraparenchymal_hemorrhage",
    (0x0018, 0xC116): "hemorrhage_volume",
    (0x0018, 0xC117): "intraventricular_extension",
    (0x0018, 0xC118): "subarachnoid_blood",
    (0x0018, 0xC119): "vasospasm_indicator",
    (0x0018, 0xC120): "aneurysm_presence",
    (0x0018, 0xC121): "aneurysm_size",
    (0x0018, 0xC122): "aneurysm_location",
    (0x0018, 0xC123): "ruptured_aneurysm",
    (0x0018, 0xC124): "avm_indicator",
    (0x0018, 0xC125): "arteriovenous_malformation",
    (0x0018, 0xC126): "cavernoma_indicator",
    (0x0018, 0xC127): "brain_tumor_location",
    (0x0018, 0xC128): "tumor_size_neuro",
    (0x0018, 0xC129): "tumor_enhancement",
    (0x0018, 0xC130): "peritumoral_edema",
    (0x0018, 0xC131): "mass_effect",
    (0x0018, 0xC132): "midline_shift",
    (0x0018, 0xC133): "herniation_syndrome",
    (0x0018, 0xC134): "uncal_herniation",
    (0x0018, 0xC135): "tonsillar_herniation",
    (0x0018, 0xC136): "hydrocephalus",
    (0x0018, 0xC137): "ventriculomegaly",
    (0x0018, 0xC138): "cortical_atrophy",
    (0x0018, 0xC139): "hippocampal_atrophy",
    (0x0018, 0xC140): "ventricular_enlargement",
    (0x0018, 0xC141): "cerebral_atrophy",
    (0x0018, 0xC142): "cerebellar_atrophy",
    (0x0018, 0xC143): "brainstem_atrophy",
    (0x0018, 0xC144): "ms_plaque",
    (0x0018, 0xC145): "ms_location",
    (0x0018, 0xC146): "ms_enhancement",
    (0x0018, 0xC147): "dawson_fingers",
    (0x0018, 0xC148): "corpus_callosum_lesion",
    (0x0018, 0xC149): "posterior_fossa_ms",
}

NEURO_IMAGING_TAGS = {
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
    (0x0018, 0xC201): "brain_ct_protocol",
    (0x0018, 0xC202): "non_contrast_ct_brain",
    (0x0018, 0xC203): "contrast_ct_brain",
    (0x0018, 0xC204): "ct_perfusion",
    (0x0018, 0xC205): "cerebral_blood_flow",
    (0x0018, 0xC206): "cerebral_blood_volume",
    (0x0018, 0xC207): "mean_transit_time",
    (0x0018, 0xC208): "time_to_peak",
    (0x0018, 0xC209): "ct_angiography_head",
    (0x0018, 0xC210): "cta_circle_willis",
    (0x0018, 0xC211): "cta_neck",
    (0x0018, 0xC212): "brain_mri_protocol",
    (0x0018, 0xC213): "t1_weighted_brain",
    (0x0018, 0xC214): "t2_weighted_brain",
    (0x0018, 0xC215): "flair_brain",
    (0x0018, 0xC216): "diffusion_weighted_imaging",
    (0x0018, 0xC217): "adc_mapping",
    (0x0018, 0xC218): "gradient_recalled_echo",
    (0x0018, 0xC219): "susceptibility_weighted",
    (0x0018, 0xC220): "swi_sequence",
    (0x0018, 0xC221): "perfusion_weighted_imaging",
    (0x0018, 0xC222): "pwi_brain",
    (0x0018, 0xC223): "arterial_spin_labeling",
    (0x0018, 0xC224): "magnetic_resonance_angiography",
    (0x0018, 0xC225): "time_of_flight_mra",
    (0x0018, 0xC226): "contrast_enhanced_mra",
    (0x0018, 0xC227): "spectroscopy_neuro",
    (0x0018, 0xC228): "proton_spectroscopy",
    (0x0018, 0xC229): "choline_peak",
    (0x0018, 0xC230): "n_acetylaspartate",
    (0x0018, 0xC231): "lactate_peak",
    (0x0018, 0xC232): "neuronavigation",
    (0x0018, 0xC233): "functional_mri",
    (0x0018, 0xC234): "task_based_fmri",
    (0x0018, 0xC235): "resting_state_fmri",
    (0x0018, 0xC236): "diffusion_tensor_imaging",
    (0x0018, 0xC237): "dti_sequence",
    (0x0018, 0xC238): "fractional_anisotropy",
    (0x0018, 0xC239): "mean_diffusivity",
    (0x0018, 0xC240): "tractography",
    (0x0018, 0xC241): "corticospinal_tract",
    (0x0018, 0xC242): "optic_radiation",
    (0x0018, 0xC243): "arcuate_fasciculus",
    (0x0018, 0xC244): "voxel_based_morphometry",
    (0x0018, 0xC245): "hippocampal_volumetry",
    (0x0018, 0xC246): "brain_volumetry",
    (0x0018, 0xC247): "thalamic_volumetry",
    (0x0018, 0xC248): "putamen_volumetry",
    (0x0018, 0xC249): "caudate_volumetry",
}

NEURO_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xC301): "acute_stroke_protocol",
    (0x0018, 0xC302): "dwiASPECTS",
    (0x0018, 0xC303): "pcASPECTS",
    (0x0018, 0xC304): "target_mismatch_profile",
    (0x0018, 0xC305): "core_penumbra_ratio",
    (0x0018, 0xC306): "thrombolysis_decision",
    (0x0018, 0xC307): "tenecteplase_dosing",
    (0x0018, 0xC308): "alteplase_dosing",
    (0x0018, 0xC309): "endovascular_planning",
    (0x0018, 0xC310): "mechanical_thrombectomy",
    (0x0018, 0xC311): "stent_retriever",
    (0x0018, 0xC312): "aspiration_catheter",
    (0x0018, 0xC313): "tici_score",
    (0x0018, 0xC314): "tici_2b",
    (0x0018, 0xC315): "tici_3",
    (0x0018, 0xC316): "brain_tumor_protocol",
    (0x0018, 0xC317): "perfusion_imaging_neuro",
    (0x0018, 0xC318): "mr_spectroscopy_tumor",
    (0x0018, 0xC319): "advanced_mr_tumor",
    (0x0018, 0xC320): "pituitary_protocol",
    (0x0018, 0xC321): "sellar_region_mri",
    (0x0018, 0xC322): "cavernous_sinus_mri",
    (0x0018, 0xC323): "temporal_lobe_protocol",
    (0x0018, 0xC324): "hippocampal_protocol",
    (0x0018, 0xC325): "epilepsy_protocol",
    (0x0018, 0xC326): "orbital_mri",
    (0x0018, 0xC327): "optic_nerve_mri",
    (0x0018, 0xC328): "cranial_nerve_mri",
    (0x0018, 0xC329): "posterior_fossa_protocol",
    (0x0018, 0xC330): "cerebellar_protocol",
    (0x0018, 0xC331): "brainstem_protocol",
    (0x0018, 0xC332): "spine_protocol",
    (0x0018, 0xC333): "cervical_spine_mri",
    (0x0018, 0xC334): "thoracic_spine_mri",
    (0x0018, 0xC335): "lumbar_spine_mri",
    (0x0018, 0xC336): "myelography",
    (0x0018, 0xC337): "ct_myelogram",
    (0x0018, 0xC338): "nerve_conduction",
    (0x0018, 0xC339): "electromyography",
    (0x0018, 0xC340): "evoked_potentials",
    (0x0018, 0xC341): "visual_evoked_potential",
    (0x0018, 0xC342): "brainstem_auditory",
    (0x0018, 0xC343): "somatosensory",
    (0x0018, 0xC344): "neurosurgery_planning",
    (0x0018, 0xC345): "tumor_resection_planning",
    (0x0018, 0xC346): "biopsy_planning",
    (0x0018, 0xC347): "stereotactic_planning",
    (0x0018, 0xC348): "radiosurgery_planning",
    (0x0018, 0xC349): "gamma_knife_planning",
    (0x0018, 0xC350): "cyberknife_planning",
}

NEURO_OUTCOMES_TAGS = {
    (0x0018, 0xC401): "neurological_survival",
    (0x0018, 0xC402): "stroke_outcome",
    (0x0018, 0xC403): "modified_rankin_outcome",
    (0x0018, 0xC404): "functional_independence",
    (0x0018, 0xC405): "hemorrhage_expansion",
    (0x0018, 0xC406): "recanalization_rate",
    (0x0018, 0xC407): "reperfusion_status",
    (0x0018, 0xC408): "symptomatic_ich",
    (0x0018, 0xC409): "mortality_stroke",
    (0x0018, 0xC410): "dementia_progression",
    (0x0018, 0xC411): "cognitive_decline",
    (0x0018, 0xC412): "conversion_mci_dementia",
    (0x0018, 0xC413): "brain_atrophy_rate",
    (0x0018, 0xC414): "hippocampal_atrophy_rate",
    (0x0018, 0xC415): "pd_progression",
    (0x0018, 0xC416): "unified_parkinson_rating",
    (0x0018, 0xC417): "hoehn_yahr_stage",
    (0x0018, 0xC418): "motor_complications",
    (0x0018, 0xC419): "dyskinesia_presence",
    (0x0018, 0xC420): "motor_fluctuations",
    (0x0018, 0xC421): "ms_relapse_rate",
    (0x0018, 0xC422): "ms_progression",
    (0x0018, 0xC423): "edss_progression",
    (0x0018, 0xC424): "brain_volume_loss_ms",
    (0x0018, 0xC425): "lesion_burden_ms",
    (0x0018, 0xC426): "new_t2_lesions",
    (0x0018, 0xC427): "gadolinium_enhancing",
    (0x0018, 0xC428): "seizure_frequency",
    (0x0018, 0xC429): "seizure_control",
    (0x0018, 0xC430): "seizure_freedom",
    (0x0018, 0xC431): "status_epilepticus_outcome",
    (0x0018, 0xC432): "tumor_response",
    (0x0018, 0xC433): "rano_response",
    (0x0018, 0xC434): "pseudoprogression",
    (0x0018, 0xC435): "pseudoresponse",
    (0x0018, 0xC436): "radionecrosis",
    (0x0018, 0xC437): "treatment_related_necrosis",
    (0x0018, 0xC438): "progression_free_survival",
    (0x0018, 0xC439): "overall_survival_neuro",
    (0x0018, 0xC440): "neurological_rehabilitation",
    (0x0018, 0xC441): "speech_therapy_outcome",
    (0x0018, 0xC442): "physical_therapy_outcome",
    (0x0018, 0xC443): "occupational_therapy_outcome",
    (0x0018, 0xC444): "speech_recovery",
    (0x0018, 0xC445): "aphasia_recovery",
    (0x0018, 0xC446): "motor_recovery",
    (0x0018, 0xC447): "sensory_recovery",
    (0x0018, 0xC448): "visual_field_recovery",
    (0x0018, 0xC449): "balance_recovery",
    (0x0018, 0xC450): "gait_recovery",
}

TOTAL_TAGS_LXXXII = {}

TOTAL_TAGS_LXXXII.update(NEUROLOGY_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXXII.update(NEURO_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXXII.update(NEURO_IMAGING_TAGS)
TOTAL_TAGS_LXXXII.update(NEURO_PROTOCOLS)
TOTAL_TAGS_LXXXII.update(NEURO_OUTCOMES_TAGS)


def _extract_tags_lxxxii(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXXII.items()}
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


def _is_neurology_imaging_file(file_path: str) -> bool:
    neurology_indicators = [
        'neurology', 'neurological', 'brain', 'stroke', 'cerebral',
        'dementia', 'alzheimer', 'parkinson', 'multiple_sclerosis', 'ms',
        'epilepsy', 'seizure', 'brain_tumor', 'glioma', 'meningioma',
        'neuroimaging', 'mri_brain', 'ct_brain', 'spine', 'neuroradiology'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in neurology_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxxii_detected": False,
        "fields_extracted": 0,
        "extension_lxxxii_type": "neurology_imaging",
        "extension_lxxxii_version": "2.0.0",
        "neurology_patient_parameters": {},
        "neuro_pathology": {},
        "neuro_imaging": {},
        "neuro_protocols": {},
        "neuro_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_neurology_imaging_file(file_path):
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

        result["extension_lxxxii_detected"] = True

        neuro_data = _extract_tags_lxxxii(ds)

        patient_params_set = set(NEUROLOGY_PATIENT_PARAMETERS.keys())
        pathology_set = set(NEURO_PATHOLOGY_TAGS.keys())
        imaging_set = set(NEURO_IMAGING_TAGS.keys())
        protocols_set = set(NEURO_PROTOCOLS.keys())
        outcomes_set = set(NEURO_OUTCOMES_TAGS.keys())

        for tag, value in neuro_data.items():
            if tag in patient_params_set:
                result["neurology_patient_parameters"][tag] = value
            elif tag in pathology_set:
                result["neuro_pathology"][tag] = value
            elif tag in imaging_set:
                result["neuro_imaging"][tag] = value
            elif tag in protocols_set:
                result["neuro_protocols"][tag] = value
            elif tag in outcomes_set:
                result["neuro_outcomes"][tag] = value

        result["fields_extracted"] = len(neuro_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_field_count() -> int:
    return len(TOTAL_TAGS_LXXXII)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_description() -> str:
    return (
        "Neurology Imaging II metadata extraction. Provides comprehensive coverage of "
        "brain disorders, stroke, neurodegenerative diseases, "
        "neurology-specific imaging protocols, and neurological outcomes assessment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "XA", "ES"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_category() -> str:
    return "Neurology Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_keywords() -> List[str]:
    return [
        "neurology", "brain", "stroke", "dementia", "Alzheimer's",
        "Parkinson's", "multiple sclerosis", "epilepsy", "seizure",
        "brain tumor", "glioma", "neuroimaging", "MRI brain", "CT brain",
        "neuroradiology", "spine imaging"
    ]


# Aliases for smoke test compatibility
def extract_medical_visualization(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxii."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxii(file_path)

def get_medical_visualization_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_field_count()

def get_medical_visualization_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_version()

def get_medical_visualization_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_description()

def get_medical_visualization_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_supported_formats()

def get_medical_visualization_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_modalities()
