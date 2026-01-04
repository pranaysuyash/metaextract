"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXXI - Cardiology Imaging II

This module provides comprehensive extraction of Cardiology Imaging parameters
including cardiac function, coronary artery disease, heart failure, and
cardiology-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXI_AVAILABLE = True

CARDIAC_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0xB001): "cardiology_assessment_date",
    (0x0010, 0xB002): "cardiac_diagnosis",
    (0x0010, 0xB003): "coronary_artery_disease",
    (0x0010, 0xB004): "myocardial_infarction",
    (0x0010, 0xB005): "stemi_indicator",
    (0x0010, 0xB006): "nstemi_indicator",
    (0x0010, 0xB007): "unstable_angina",
    (0x0010, 0xB008): "heart_failure_indicator",
    (0x0010, 0xB009): "hf_phenotype",
    (0x0010, 0xB010): "hfperef_indicator",
    (0x0010, 0xB011): "hfpef_indicator",
    (0x0010, 0xB012): "nyha_class",
    (0x0010, 0xB013): "acc_stage",
    (0x0010, 0xB014): "left_ventricular_ejection_fraction",
    (0x0010, 0xB015): "lv_ef_measured",
    (0x0010, 0xB016): "right_ventricular_function",
    (0x0010, 0xB017): "rv_function_indicator",
    (0x0010, 0xB018): "valvular_heart_disease",
    (0x0010, 0xB019): "aortic_stenosis",
    (0x0010, 0xB020): "mitral_regurgitation",
    (0x0010, 0xB021): "mitral_stenosis",
    (0x0010, 0xB022): "tricuspid_regurgitation",
    (0x0010, 0xB023): "pulmonary_stenosis",
    (0x0010, 0xB024): "valve_prosthesis",
    (0x0010, 0xB025): "aortic_valve_replacement",
    (0x0010, 0xB026): "mitral_valve_replacement",
    (0x0010, 0xB027): "valve_repair",
    (0x0010, 0xB028): "atrial_fibrillation",
    (0x0010, 0xB029): "aflutter_indicator",
    (0x0010, 0xB030): "supraventricular_tachycardia",
    (0x0010, 0xB031): "ventricular_tachycardia",
    (0x0010, 0xB032): "ventricular_fibrillation",
    (0x0010, 0xB033): "bradycardia_indicator",
    (0x0010, 0xB034): "heart_block",
    (0x0010, 0xB035): "sick sinus_syndrome",
    (0x0010, 0xB036): "pacemaker_status",
    (0x0010, 0xB037): "icd_status",
    (0x0010, 0xB038): "cardiac_resynchronization",
    (0x0010, 0xB039): "blood_pressure_systolic",
    (0x0010, 0xB040): "blood_pressure_diastolic",
    (0x0010, 0xB041): "heart_rate",
    (0x0010, 0xB042): "bnp_level",
    (0x0010, 0xB043): "nt_probnp_level",
    (0x0010, 0xB044): "troponin_i_level",
    (0x0010, 0xB045): "troponin_t_level",
    (0x0010, 0xB046): "ck_mb_level",
    (0x0010, 0xB047): "lipid_panel",
    (0x0010, 0xB048): "ldl_cholesterol",
    (0x0010, 0xB049): "hdl_cholesterol",
    (0x0010, 0xB050): "total_cholesterol",
    (0x0010, 0xB051): "triglycerides",
    (0x0010, 0xB052): "diabetes_mellitus",
    (0x0010, 0xB053): "hypertension_indicator",
    (0x0010, 0xB054): "hyperlipidemia",
    (0x0010, 0xB055): "smoking_status",
    (0x0010, 0xB056): "pack_years",
    (0x0010, 0xB057): "family_history_cad",
    (0x0010, 0xB058): "prior_cabg",
    (0x0010, 0xB059): "prior_pci",
}

CARDIAC_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xB101): "myocardial_ischemia",
    (0x0018, 0xB102): "myocardial_infarction_size",
    (0x0018, 0xB103): "infarct_location",
    (0x0018, 0xB104): "infarct_territory",
    (0x0018, 0xB105): "late_gadolinium_enhancement",
    (0x0018, 0xB106): "lge_pattern",
    (0x0018, 0xB107): "subendocardial_infarction",
    (0x0018, 0xB108): "transmural_infarction",
    (0x0018, 0xB109): "microvascular_obstruction",
    (0x0018, 0xB110): "intramyocardial_hemorrhage",
    (0x0018, 0xB111): "wall_motion_abnormality",
    (0x0018, 0xB112): "hypokinesia",
    (0x0018, 0xB113): "akinesia",
    (0x0018, 0xB114): "dyskinesia",
    (0x0018, 0xB115): "aneurysm_formation",
    (0x0018, 0xB116): "left_ventricular_thrombus",
    (0x0018, 0xB117): "right_ventricular_infarction",
    (0x0018, 0xB118): "coronary_artery_stenosis",
    (0x0018, 0xB119): "lms_stenosis",
    (0x0018, 0xB120): "lad_stenosis",
    (0x0018, 0xB121): "lcx_stenosis",
    (0x0018, 0xB122): "rca_stenosis",
    (0x0018, 0xB123): "coronary_occlusion",
    (0x0018, 0xB124): "coronary_calcification",
    (0x0018, 0xB125): "coronary_ calcium_score",
    (0x0018, 0xB126): "agatston_score",
    (0x0018, 0xB127): "plaque_characterization",
    (0x0018, 0xB128): "calcified_plaque",
    (0x0018, 0xB129): "non_calcified_plaque",
    (0x0018, 0xB130): "mixed_plaque",
    (0x0018, 0xB131): "positive_remodeling",
    (0x0018, 0xB132): "low_attenuation_plaque",
    (0x0018, 0xB133): "napkin_ring_sign",
    (0x0018, 0xB134): "valve_calcification",
    (0x0018, 0xB135): "aortic_valve_area",
    (0x0018, 0xB136): "mitral_valve_area",
    (0x0018, 0xB137): "pressure_gradient_valve",
    (0x0018, 0xB138): "valve_regurgitation_severity",
    (0x0018, 0xB139): "valve_stenosis_severity",
    (0x0018, 0xB140): "pericardial_effusion",
    (0x0018, 0xB141): "pericardial_thickening",
    (0x0018, 0xB142): "constrictive_pericarditis",
    (0x0018, 0xB143): "cardiac_tamponade",
    (0x0018, 0xB144): "aortic_dissection",
    (0x0018, 0xB145): "aortic_aneurysm",
    (0x0018, 0xB146): "aortic_arch_atheroma",
    (0x0018, 0xB147): "pulmonary_hypertension_ct",
    (0x0018, 0xB148): "pulmonary_artery_diameter",
    (0x0018, 0xB149): "right_heart_strain",
}

CARDIAC_IMAGING_TAGS = {
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
    (0x0018, 0xB201): "cardiac_ct_protocol",
    (0x0018, 0xB202): "coronary_ct_angiography",
    (0x0018, 0xB203): "ct_fractional_flow_reserve",
    (0x0018, 0xB204): "ct_ffr_value",
    (0x0018, 0xB205): "stress_ct_perfusion",
    (0x0018, 0xB206): "cardiac_mri_protocol",
    (0x0018, 0xB207): "cine_mri_heart",
    (0x0018, 0xB208): "late_enhancement_mri",
    (0x0018, 0xB209): "stress_perfusion_mri",
    (0x0018, 0xB210): "t1_mapping_mri",
    (0x0018, 0xB211): "t2_mapping_mri",
    (0x0018, 0xB212): "extracellular_volume_mri",
    (0x0018, 0xB213): "t2_star_mri",
    (0x0018, 0xB214): "four_chamber_view",
    (0x0018, 0xB215): "two_chamber_view",
    (0x0018, 0xB216): "short_axis_view",
    (0x0018, 0xB217): "long_axis_view",
    (0x0018, 0xB218): "echocardiogram_protocol",
    (0x0018, 0xB219): "tte_exam",
    (0x0018, 0xB220): "ttee_exam",
    (0x0018, 0xB221): "stress_echocardiogram",
    (0x0018, 0xB222): "dobutamine_stress_echo",
    (0x0018, 0xB223): "exercise_stress_echo",
    (0x0018, 0xB224): "nuclear_cardiology",
    (0x0018, 0xB225): "spect_mpi",
    (0x0018, 0xB226): "stress_spect",
    (0x0018, 0xB227): "rest_spect",
    (0x0018, 0xB228): "pet_cardiac",
    (0x0018, 0xB229): "fdg_cardiac",
    (0x0018, 0xB230): "rubidium_pet",
    (0x0018, 0xB231): "ammonia_pet",
    (0x0018, 0xB232): "cardiac_reserve",
    (0x0018, 0xB233): "coronary_angiography",
    (0x0018, 0xB234): "left_main_angiogram",
    (0x0018, 0xB235): "right_coronary_angiogram",
    (0x0018, 0xB236): "ventriculogram",
    (0x0018, 0xB237): "aortogram",
    (0x0018, 0xB238): "hemodynamic_data",
    (0x0018, 0xB239): "cardiac_output",
    (0x0018, 0xB240): "cardiac_index",
    (0x0018, 0xB241): "systemic_vascular_resistance",
    (0x0018, 0xB242): "pulmonary_capillary_wedge_pressure",
    (0x0018, 0xB243): "central_venous_pressure",
    (0x0018, 0xB244): "pulmonary_artery_pressure",
    (0x0018, 0xB245): "qrs_duration",
    (0x0018, 0xB246): "qt_interval",
    (0x0018, 0xB247): "pr_interval",
    (0x0018, 0xB248): "electrophysiology_study",
    (0x0018, 0xB249): "ablation_procedure",
}

CARDIAC_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xB301): "ecg_gating",
    (0x0018, 0xB302): "prospective_gating",
    (0x0018, 0xB303): "retrospective_gating",
    (0x0018, 0xB304): "retrospective_gating",
    (0x0018, 0xB305): "phase_based_gating",
    (0x0018, 0xB306): "beat_average_ct",
    (0x0018, 0xB307): "helical_acquisition",
    (0x0018, 0xB308): "axial_acquisition",
    (0x0018, 0xB309): "temporal_resolution",
    (0x0018, 0xB310): "spatial_resolution",
    (0x0018, 0xB311): "contrast_protocol_cardiac",
    (0x0018, 0xB312): "iodinated_contrast_cardiac",
    (0x0018, 0xB313): "beta_blocker_premedication",
    (0x0018, 0xB314): "nitroglycerin_admin",
    (0x0018, 0xB315): "adenosine_stress",
    (0x0018, 0xB316): "regadenoson_stress",
    (0x0018, 0xB317): "dipyridamole_stress",
    (0x0018, 0xB318): "dobutamine_stress",
    (0x0018, 0xB319): "pci_planning",
    (0x0018, 0xB320): "stent_planning",
    (0x0018, 0xB321): "bifurcation_stenting",
    (0x0018, 0xB322): "left_main_intervention",
    (0x0018, 0xB323): "chronic_total_occlusion",
    (0x0018, 0xB324): "cto_revascularization",
    (0x0018, 0xB325): "cabg_planning",
    (0x0018, 0xB326): "graft_planning",
    (0x0018, 0xB327): "arterial_graft",
    (0x0018, 0xB328): "venous_graft",
    (0x0018, 0xB329): "valve_replacement_planning",
    (0x0018, 0xB330): "tavr_planning",
    (0x0018, 0xB331): "tavi_planning",
    (0x0018, 0xB332): "surgical_avr_planning",
    (0x0018, 0xB333): "mitral_intervention",
    (0x0018, 0xB334): "mitraclip_planning",
    (0x0018, 0xB335): "pacemaker_lead_placement",
    (0x0018, 0xB336): "icd_lead_placement",
    (0x0018, 0xB337): "crt_planning",
    (0x0018, 0xB338): "lv_lead_position",
    (0x0018, 0xB339): "atrial_septal_defect_closure",
    (0x0018, 0xB340): "ventricular_septal_defect_closure",
    (0x0018, 0xB341): "pfo_closure",
    (0x0018, 0xB342): "laac_planning",
    (0x0018, 0xB343): "left_atrial_appendage",
    (0x0018, 0xB344): "watchman_device",
    (0x0018, 0xB345): "aortic_aneurysm_repair",
    (0x0018, 0xB346): "tevar_planning",
    (0x0018, 0xB347): "evar_planning",
    (0x0018, 0xB348): "congenital_heart_disease",
    (0x0018, 0xB349): "shunt_assessment",
    (0x0018, 0xB350): "Qp_Qs_ratio",
}

CARDIAC_OUTCOMES_TAGS = {
    (0x0018, 0xB401): "cardiac_survival",
    (0x0018, 0xB402): "cardiovascular_mortality",
    (0x0018, 0xB403): "sudden_cardiac_death",
    (0x0018, 0xB404): "heart_failure_hospitalization",
    (0x0018, 0xB405): "myocardial_infarction_outcome",
    (0x0018, 0xB406): "revascularization_outcome",
    (0x0018, 0xB407): "stent_thrombosis",
    (0x0018, 0xB408): "in_stent_restenosis",
    (0x0018, 0xB409): "graft_patency",
    (0x0018, 0xB410): "graft_failure",
    (0x0018, 0xB411): "valve_durability",
    (0x0018, 0xB412): "structural_valve_deterioration",
    (0x0018, 0xB413): "valve_thrombosis",
    (0x0018, 0xB414): "valve_endocarditis",
    (0x0018, 0xB415): "stroke_cardiac",
    (0x0018, 0xB416): "bleeding_complication",
    (0x0018, 0xB417): "contrast_induced_nephropathy",
    (0x0018, 0xB418): "radiation_dose_cardiac",
    (0x0018, 0xB419): "procedure_time",
    (0x0018, 0xB420): "fluoroscopy_time",
    (0x0018, 0xB421): "contrast_volume",
    (0x0018, 0xB422): "nyha_improvement",
    (0x0018, 0xB423): "ef_improvement",
    (0x0018, 0xB424): "reverse_remodeling",
    (0x0018, 0xB425): "exercise_capacity",
    (0x0018, 0xB426): "six_minute_walk_cardiac",
    (0x0018, 0xB427): "cardiopulmonary_exercise_test",
    (0x0018, 0xB428): "vo2_max",
    (0x0018, 0xB429): "quality_of_life_cardiac",
    (0x0018, 0xB430): "seattle_angina_questionnaire",
    (0x0018, 0xB431): "kansas_city_cardiomyopathy",
    (0x0018, 0xB432): "mlwhf_questionnaire",
    (0x0018, 0xB433): "medication_adherence_cardiac",
    (0x0018, 0xB434): "beta_blocker_tolerance",
    (0x0018, 0xB435): "ace_inhibitor_tolerance",
    (0x0018, 0xB436): "statin_intolerance",
    (0x0018, 0xB437): "anticoagulation_management",
    (0x0018, 0xB438): "warfarin_management",
    (0x0018, 0xB439): "doac_management",
    (0x0018, 0xB440): "arrhythmia_recurrence",
    (0x0018, 0xB441): "af_recurrence",
    (0x0018, 0xB442): "vt_inducibility",
    (0x0018, 0xB443): "icd_appropriate_therapy",
    (0x0018, 0xB444): "icd_shock",
    (0x0018, 0xB445): "crt_response",
    (0x0018, 0xB446): "super_response_crt",
    (0x0018, 0xB447): "non_response_crt",
    (0x0018, 0xB448): "cardiac_rehabilitation",
    (0x0018, 0xB449): "preventive_therapy",
    (0x0018, 0xB450): "secondary_prevention",
}

TOTAL_TAGS_LXXXI = {}

TOTAL_TAGS_LXXXI.update(CARDIAC_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXXI.update(CARDIAC_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXXI.update(CARDIAC_IMAGING_TAGS)
TOTAL_TAGS_LXXXI.update(CARDIAC_PROTOCOLS)
TOTAL_TAGS_LXXXI.update(CARDIAC_OUTCOMES_TAGS)


def _extract_tags_lxxxi(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXXI.items()}
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


def _is_cardiology_imaging_file(file_path: str) -> bool:
    cardiology_indicators = [
        'cardiology', 'cardiac', 'heart', 'coronary', 'myocardial',
        'cardiac', 'aortic', 'valve', 'echocardiogram', 'ecg', 'ekg',
        'angiography', 'stent', 'cabg', 'pci', 'tavr', 'tavi',
        'heart_failure', 'cardiomyopathy', 'arrhythmia', 'atrial_fibrillation',
        'pacemaker', 'icd', 'crt', 'spect', 'pet_cardiac', 'cardiac_mri'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in cardiology_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxi(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxxi_detected": False,
        "fields_extracted": 0,
        "extension_lxxxi_type": "cardiology_imaging",
        "extension_lxxxi_version": "2.0.0",
        "cardiac_patient_parameters": {},
        "cardiac_pathology": {},
        "cardiac_imaging": {},
        "cardiac_protocols": {},
        "cardiac_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_cardiology_imaging_file(file_path):
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

        result["extension_lxxxi_detected"] = True

        cardiac_data = _extract_tags_lxxxi(ds)

        patient_params_set = set(CARDIAC_PATIENT_PARAMETERS.keys())
        pathology_set = set(CARDIAC_PATHOLOGY_TAGS.keys())
        imaging_set = set(CARDIAC_IMAGING_TAGS.keys())
        protocols_set = set(CARDIAC_PROTOCOLS.keys())
        outcomes_set = set(CARDIAC_OUTCOMES_TAGS.keys())

        for tag, value in cardiac_data.items():
            if tag in patient_params_set:
                result["cardiac_patient_parameters"][tag] = value
            elif tag in pathology_set:
                result["cardiac_pathology"][tag] = value
            elif tag in imaging_set:
                result["cardiac_imaging"][tag] = value
            elif tag in protocols_set:
                result["cardiac_protocols"][tag] = value
            elif tag in outcomes_set:
                result["cardiac_outcomes"][tag] = value

        result["fields_extracted"] = len(cardiac_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxi_field_count() -> int:
    return len(TOTAL_TAGS_LXXXI)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxi_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxi_description() -> str:
    return (
        "Cardiology Imaging II metadata extraction. Provides comprehensive coverage of "
        "cardiac function parameters, coronary artery disease, heart failure, "
        "cardiology-specific imaging protocols, and cardiac outcomes assessment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxi_modalities() -> List[str]:
    return ["CT", "MR", "US", "XA", "PT", "NM", "ES", "DX", "CR"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxi_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxi_category() -> str:
    return "Cardiology Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxi_keywords() -> List[str]:
    return [
        "cardiology", "cardiac", "heart", "coronary", "myocardial",
        "infarction", "heart failure", "valvular heart disease",
        "echocardiogram", "coronary CT angiography", "cardiac MRI",
        "pacemaker", "ICD", "CRT", "arrhythmia", "atrial fibrillation"
    ]
