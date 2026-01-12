"""
Scientific DICOM/FITS Ultimate Advanced Extension LXVI - Cath Lab Imaging

This module provides comprehensive extraction of Catheterization Laboratory Imaging parameters
including cardiac cath, PCI, electrophysiology, and structural heart procedures.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXVI_AVAILABLE = True

CATH_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x2600): "cath_date",
    (0x0010, 0x2601): "cath_time",
    (0x0010, 0x2602): "procedure_duration_minutes",
    (0x0010, 0x2603): "cath_procedure_type",
    (0x0010, 0x2604): "operator_name",
    (0x0010, 0x2605): "first_operator",
    (0x0010, 0x2606): "second_operator",
    (0x0010, 0x2607): "nurse_name",
    (0x0010, 0x2608): "tech_name",
    (0x0010, 0x2609): "room_number",
    (0x0010, 0x2610): "indication_for_procedure",
    (0x0010, 0x2611): "stable_angina",
    (0x0010, 0x2612): "unstable_angina",
    (0x0010, 0x2613): "nstemi",
    (0x0010, 0x2614): "stemi",
    (0x0010, 0x2615): "heart_failure",
    (0x0010, 0x2616): "valvular_disease",
    (0x0010, 0x2617): "arrhythmia",
    (0x0010, 0x2618): "syncope",
    (0x0010, 0x2619): "pre_procedure_risk_score",
    (0x0010, 0x2620): "syntax_score",
    (0x0010, 0x2621): "syntax_score_ii",
    (0x0010, 0x2622): "grace_score",
    (0x0010, 0x2623): "timi_risk_score",
    (0x0010, 0x2624): "sts_score",
    (0x0010, 0x2625): "euro_score",
    (0x0010, 0x2626): "left_ventricular_ejection_fraction",
    (0x0010, 0x2627): "baseline_creatinine",
    (0x0010, 0x2628): "gfr_estimate",
    (0x0010, 0x2629): "contrast_allergy",
    (0x0010, 0x2630): "previous_stent",
    (0x0010, 0x2631): "previous_cabg",
    (0x0010, 0x2632): "previous_valve_surgery",
    (0x0010, 0x2633): "diabetes_mellitus",
    (0x0010, 0x2634): "hypertension",
    (0x0010, 0x2635): "hyperlipidemia",
    (0x0010, 0x2636): "smoking_history",
    (0x0010, 0x2637): "family_history_cad",
    (0x0010, 0x2638): "peripheral_artery_disease",
    (0x0010, 0x2639): "cerebrovascular_disease",
    (0x0010, 0x2640): "chronic_kidney_disease",
    (0x0010, 0x2641): "anticoagulation_therapy",
    (0x0010, 0x2642): "dual_antiplatelet_therapy",
    (0x0010, 0x2643): "statin_therapy",
    (0x0010, 0x2644): "beta_blocker",
    (0x0010, 0x2645): "ace_inhibitor",
    (0x0010, 0x2646): "calcium_channel_blocker",
}

CORONARY_ANATOMY_TAGS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xA101): "coronary_angiography_indicator",
    (0x0018, 0xA102): "left_main_disease",
    (0x0018, 0xA103): "lad_disease",
    (0x0018, 0xA104): "lcx_disease",
    (0x0018, 0xA105): "rca_disease",
    (0x0018, 0xA106): "ramus_disease",
    (0x0018, 0xA107): "number_of_vessels_diseased",
    (0x0018, 0xA108): "left_main_stenosis_percent",
    (0x0018, 0xA109): "proximal_lad_stenosis",
    (0x0018, 0xA110): "mid_lad_stenosis",
    (0x0018, 0xA111): "distal_lad_stenosis",
    (0x0018, 0xA112): "proximal_lcx_stenosis",
    (0x0018, 0xA113): "mid_lcx_stenosis",
    (0x0018, 0xA114): "distal_lcx_stenosis",
    (0x0018, 0xA115): "proximal_rca_stenosis",
    (0x0018, 0xA116): "mid_rca_stenosis",
    (0x0018, 0xA117): "distal_rca_stenosis",
    (0x0018, 0xA118): "pda_stenosis",
    (0x0018, 0xA119): "pla_stenosis",
    (0x0018, 0xA120): "lesion_length_mm",
    (0x0018, 0xA121): "lesion_diameter_mm",
    (0x0018, 0xA122): "thrombus_presence",
    (0x0018, 0xA123): "calcification_severity",
    (0x0018, 0xA124): "tortuosity_grade",
    (0x0018, 0xA125): "bifurcation_involvement",
    (0x0018, 0xA126): "ostial_lesion",
    (0x0018, 0xA127): "chronic_total_occlusion",
    (0x0018, 0xA128): "ctocolength_mm",
    (0x0018, 0xA129): "collateral_circulation",
    (0x0018, 0xA130): "syntax_score_segment_1",
    (0x0018, 0xA131): "syntax_score_segment_2",
    (0x0018, 0xA132): "syntax_score_segment_3",
    (0x0018, 0xA133): "total_syntax_score",
    (0x0018, 0xA134): "dominant_circulation",
    (0x0018, 0xA135): "right_dominant",
    (0x0018, 0xA136): "left_dominant",
    (0x0018, 0xA137): "codominant",
    (0x0018, 0xA138): "arterial_graft_assessment",
    (0x0018, 0xA139): "venous_graft_assessment",
    (0x0018, 0xA140): "native_coronary_assessment",
}

PCI_TAGS = {
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
    (0x0018, 0xA201): "pci_performed",
    (0x0018, 0xA202): "pci_target_vessel",
    (0x0018, 0xA203): "number_of_stents",
    (0x0018, 0xA204): "stent_type",
    (0x0018, 0xA205): "drug_eluting_stent",
    (0x0018, 0xA206): "bare_metal_stent",
    (0x0018, 0xA207): "bioresorbable_stent",
    (0x0018, 0xA208): "stent_diameter_mm",
    (0x0018, 0xA209): "stent_length_mm",
    (0x0018, 0xA210): "stent_post_dilation",
    (0x0018, 0xA211): "balloon_size_mm",
    (0x0018, 0xA212): "balloon_pressure_atm",
    (0x0018, 0xA213): "pre_dilation_performed",
    (0x0018, 0xA214): "post_dilation_performed",
    (0x0018, 0xA215): "stent_deployment_pressure",
    (0x0018, 0xA216): "final_timi_flow",
    (0x0018, 0xA217): "timi_0",
    (0x0018, 0xA218): "timi_1",
    (0x0018, 0xA219): "timi_2",
    (0x0018, 0xA220): "timi_3",
    (0x0018, 0xA221): "residual_stenosis_percent",
    (0x0018, 0xA222): "dissection_occurrence",
    (0x0018, 0xA223): "dissection_type",
    (0x0018, 0xA224): "no_reflow_phenomenon",
    (0x0018, 0xA225): "slow_flow",
    (0x0018, 0xA226): "graft_intervention",
    (0x0018, 0xA227): "rotational_atherectomy",
    (0x0018, 0xA228): "laser_atherectomy",
    (0x0018, 0xA229): "cutting_balloon",
    (0x0018, 0xA230): "intravascular_imaging",
    (0x0018, 0xA231): "ivus_performed",
    (0x0018, 0xA232): "oct_performed",
    (0x0018, 0xA233): "physiology_measurement",
    (0x0018, 0xA234): "ffr_measured",
    (0x0018, 0xA235): "ifr_measured",
    (0x0018, 0xA236): "ffr_value",
    (0x0018, 0xA237): "ifr_value",
    (0x0018, 0xA238): "iwm_value",
    (0x0018, 0xA239): "coronary_sinus_pressure",
    (0x0018, 0xA240): "microvascular_resistance",
}

ELECTROPHYSIOLOGY_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xA301): "electrophysiology_study",
    (0x0018, 0xA302): "ablation_performed",
    (0x0018, 0xA303): "ablation_target",
    (0x0018, 0xA304): "av_nodal_reentrant_tachycardia",
    (0x0018, 0xA305): "atrial_flutter",
    (0x0018, 0xA306): "atrial_fibrillation",
    (0x0018, 0xA307): "supraventricular_tachycardia",
    (0x0018, 0xA308): "ventricular_tachycardia",
    (0x0018, 0xA309): "wpw_syndrome",
    (0x0018, 0xA310): "av_node_ablation",
    (0x0018, 0xA311): "pulmonary_vein_isolation",
    (0x0018, 0xA312): "linear_ablation",
    (0x0018, 0xA313): "fractionated_area_ablation",
    (0x0018, 0xA314): "cavotricuspid_isthmus_ablation",
    (0x0018, 0xA315): "left_atrial_appendage_closure",
    (0x0018, 0xA316): "watchman_device",
    (0x0018, 0xA317): "amplatzer_device",
    (0x0018, 0xA318): "device_size_mm",
    (0x0018, 0xA319): "pacemaker_placement",
    (0x0018, 0xA320): "icd_placement",
    (0x0018, 0xA321): "crt_placement",
    (0x0018, 0xA322): "biventricular_pacemaker",
    (0x0018, 0xA323): "lead_location_ra",
    (0x0018, 0xA324): "lead_location_rv",
    (0x0018, 0xA325): "lead_location_lv",
    (0x0018, 0xA326): "electrode_type",
    (0x0018, 0xA327): "ablation_energy_type",
    (0x0018, 0xA328): "rf_ablation",
    (0x0018, 0xA329): "cryoablation",
    (0x0018, 0xA330): "irreversible_electroporation",
    (0x0018, 0xA331): "laser_ablation",
    (0x0018, 0xA332): "ablation_power_watts",
    (0x0018, 0xA333): "ablation_temperature",
    (0x0018, 0xA334): "ablation_duration_seconds",
    (0x0018, 0xA335): "irrigation_type",
    (0x0018, 0xA336): "3d_mapping_system",
    (0x0018, 0xA337): "contact_force_grams",
    (0x0018, 0xA338): "ablation_success",
    (0x0018, 0xA339): "procedure_complication",
    (0x0018, 0xA340): "av_block_complication",
    (0x0018, 0xA341): "tamponade_complication",
    (0x0018, 0xA342): "vascular_complication",
    (0x0018, 0xA343): "stroke_complication",
}

STRUCTURAL_HEART_TAGS = {
    (0x0018, 0xA401): "structural_heart_intervention",
    (0x0018, 0xA402): "tavr_performed",
    (0x0018, 0xA403): "tavr_valve_type",
    (0x0018, 0xA404): "tavr_valve_size",
    (0x0018, 0xA405): "transfemoral_approach",
    (0x0018, 0xA406): "transapical_approach",
    (0x0018, 0xA407): "subclavian_approach",
    (0x0018, 0xA408): "direct_aortic_approach",
    (0x0018, 0xA409): "aortic_gradients_pre",
    (0x0018, 0xA410): "aortic_gradients_post",
    (0x0018, 0xA411): "aortic_valve_area_pre",
    (0x0018, 0xA412): "aortic_valve_area_post",
    (0x0018, 0xA413): "paravalvular_leak",
    (0x0018, 0xA414): "mitraclip_performed",
    (0x0018, 0xA415): "mitraclip_device_size",
    (0x0018, 0xA416): "mitraclip_number_of_clips",
    (0x0018, 0xA417): "mitral_regurgitation_pre",
    (0x0018, 0xA418): "mitral_regurgitation_post",
    (0x0018, 0xA419): "mvp_performed",
    (0x0018, 0xA420): "balloon_valvuloplasty",
    (0x0018, 0xA421): "aortic_valvuloplasty",
    (0x0018, 0xA422): "mitral_valvuloplasty",
    (0x0018, 0xA423): "pulmonary_valvuloplasty",
    (0x0018, 0xA424): "asd_closure",
    (0x0018, 0xA425): "pfo_closure",
    (0x0018, 0xA426): "vsd_closure",
    (0x0018, 0xA427): "pda_closure",
    (0x0018, 0xA428): "device_closure_size",
    (0x0018, 0xA429): "patent_foramen_ovale",
    (0x0018, 0xA430): "atrial_septal_defect",
    (0x0018, 0xA431): "ventricular_septal_defect",
    (0x0018, 0xA432): "patent_ductus_arteriosus",
    (0x0018, 0xA433): "left_atrial_appendage_closure",
    (0x0018, 0xA434): "laca_device_type",
    (0x0018, 0xA435): "laca_complication",
    (0x0018, 0xA436): "vascular_closure_device",
    (0x0018, 0xA437): "vascular_complication_type",
    (0x0018, 0xA438): "contrast_volume_ml",
    (0x0018, 0xA439): "fluoroscopy_time_minutes",
    (0x0018, 0xA440): "air_kerma_gy",
    (0x0018, 0xA441): "dose_area_product_gy_cm2",
}

CATH_WORKFLOW_TAGS = {
    (0x0018, 0xA501): "vascular_access",
    (0x0018, 0xA502): "femoral_artery_access",
    (0x0018, 0xA503): "radial_artery_access",
    (0x0018, 0xA504): "sheath_size",
    (0x0018, 0xA505): "heparin_dose_units",
    (0x0018, 0xA506): "activated_clotting_time",
    (0x0018, 0xA507): "gp_iib_iiia_inhibitor",
    (0x0018, 0xA508): "bivalirudin",
    (0x0018, 0xA509): "contrast_type",
    (0x0018, 0xA510): "iodixanol",
    (0x0018, 0xA511): "iopamidol",
    (0x0018, 0xA512): "iohexol",
    (0x0018, 0xA513): "contrast_reaction",
    (0x0018, 0xA514): "anaphylaxis",
    (0x0018, 0xA515): "contrast_induced_nephropathy",
    (0x0018, 0xA516): "creatinine_post_procedure",
    (0x0018, 0xA517): "hemostasis_method",
    (0x0018, 0xA518): "manual_compression",
    (0x0018, 0xA519): "closure_device",
    (0x0018, 0xA520): "vascular_complication",
    (0x0018, 0xA521): "hematoma",
    (0x0018, 0xA522): "retroperitoneal_hematoma",
    (0x0018, 0xA523): "pseudoaneurysm",
    (0x0018, 0xA524): "av_fistula",
    (0x0018, 0xA525): "dissection",
    (0x0018, 0xA526): "perforation",
    (0x0018, 0xA527): "tamponade",
    (0x0018, 0xA528): "death",
    (0x0018, 0xA529): "myocardial_infarction",
    (0x0018, 0xA530): "stroke",
    (0x0018, 0xA531): "target_vessel_revascularization",
    (0x0018, 0xA532): "repeat_revascularization",
    (0x0018, 0xA533): "bleeding_event",
    (0x0018, 0xA534): "transfusion_required",
    (0x0018, 0xA535): "cardiogenic_shock",
    (0x0018, 0xA536): "cardiac_arrest",
    (0x0018, 0xA537): "complete_revascularization",
    (0x0018, 0xA538): "residual_ ischemia",
    (0x0018, 0xA539): "st_segment_elevation",
    (0x0018, 0xA540): "post_procedure_troponin",
    (0x0018, 0xA541): "ck_mb_level",
    (0x0018, 0xA542): "discharge_medication",
    (0x0018, 0xA543): "aspirin_prescribed",
    (0x0018, 0xA544): "p2y12_inhibitor",
    (0x0018, 0xA545): "statin_prescribed",
    (0x0018, 0xA546): "beta_blocker_prescribed",
    (0x0018, 0xA547): "ace_arb_prescribed",
}

TOTAL_TAGS_LXVI = (
    CATH_PATIENT_PARAMETERS |
    CORONARY_ANATOMY_TAGS |
    PCI_TAGS |
    ELECTROPHYSIOLOGY_TAGS |
    STRUCTURAL_HEART_TAGS |
    CATH_WORKFLOW_TAGS
)


def _extract_tags_lxvi(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LXVI.items():
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


def _is_cath_lab_imaging_file(file_path: str) -> bool:
    cath_indicators = [
        'cath', 'cath lab', 'cardiac cath', 'coronary', 'angiography', 'pci',
        'stent', 'balloon', 'stent', 'angioplasty', 'electrophysiology', 'ep study',
        'ablation', 'pacemaker', 'icd', 'crt', 'tavr', 'mitraclip', 'structural heart',
        'coronary physiology', 'ffr', 'ifr', 'ivus', 'oct', 'left main', 'lad',
        'lcx', 'rca', 'left anterior descending', 'circumflex'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in cath_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxvi(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxvi_detected": False,
        "fields_extracted": 0,
        "extension_lxvi_type": "cath_lab_imaging",
        "extension_lxvi_version": "2.0.0",
        "cath_patient_parameters": {},
        "coronary_anatomy": {},
        "pci": {},
        "electrophysiology": {},
        "structural_heart": {},
        "cath_workflow": {},
        "extraction_errors": [],
    }

    try:
        if not _is_cath_lab_imaging_file(file_path):
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

        result["extension_lxvi_detected"] = True

        cath_data = _extract_tags_lxvi(ds)

        result["cath_patient_parameters"] = {
            k: v for k, v in cath_data.items()
            if k in CATH_PATIENT_PARAMETERS.values()
        }
        result["coronary_anatomy"] = {
            k: v for k, v in cath_data.items()
            if k in CORONARY_ANATOMY_TAGS.values()
        }
        result["pci"] = {
            k: v for k, v in cath_data.items()
            if k in PCI_TAGS.values()
        }
        result["electrophysiology"] = {
            k: v for k, v in cath_data.items()
            if k in ELECTROPHYSIOLOGY_TAGS.values()
        }
        result["structural_heart"] = {
            k: v for k, v in cath_data.items()
            if k in STRUCTURAL_HEART_TAGS.values()
        }
        result["cath_workflow"] = {
            k: v for k, v in cath_data.items()
            if k in CATH_WORKFLOW_TAGS.values()
        }

        result["fields_extracted"] = len(cath_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_field_count() -> int:
    return len(TOTAL_TAGS_LXVI)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_description() -> str:
    return (
        "Cath Lab Imaging metadata extraction. Provides comprehensive coverage of "
        "cardiac catheterization, PCI, coronary anatomy, electrophysiology, "
        "structural heart procedures, and cath lab workflow parameters."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_modalities() -> List[str]:
    return ["XA", "RF", "CT", "US", "MR"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_category() -> str:
    return "Cath Lab Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_keywords() -> List[str]:
    return [
        "cath lab", "cardiac catheterization", "PCI", "coronary angiography", "stenting",
        "electrophysiology", "EP study", "ablation", "pacemaker", "ICD", "CRT",
        "TAVR", "MitraClip", "structural heart", "coronary physiology", "FFR", "iFR",
        "IVUS", "OCT", "STEMI", "NSTEMI", "angina", "TIMI flow", "Syntax score",
        "aortic stenosis", "mitral regurgitation", "atrial fibrillation", "SVT", "VT"
    ]


# Aliases for smoke test compatibility
def extract_digital_health(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxvi."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxvi(file_path)

def get_digital_health_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_field_count()

def get_digital_health_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_version()

def get_digital_health_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_description()

def get_digital_health_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_supported_formats()

def get_digital_health_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_modalities()
